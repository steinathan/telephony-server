from fastapi import WebSocket
from streaming_providers.base import BaseStreamingProvider
from streaming_providers.models import StreamingProviderConfig
import os

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.utils.events_manager import EventsManager


class PipecatStreamingConfig(StreamingProviderConfig):
    type: str = "streaming_provider_pipecat"
    deepgram_api_key: str | None = None
    llm_model: str | None = "gpt-4o"
    openai_api_key: str | None = None
    elevenlabs_api_key: str | None = None


class PipecatStreamingProvider(BaseStreamingProvider):
    def __init__(
        self,
        websocket: WebSocket,
        provider_config: PipecatStreamingConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ):
        super().__init__(websocket, provider_config, config_manager, events_manager)

        self.provider_config = provider_config
        self.llm_model = provider_config.llm_model or "gpt-4o"
        self.openai_api_key = (
            provider_config.openai_api_key or os.environ["OPENAI_COMPATIBLE_API_KEY"]
        )
        self.deepgram_api_key = (
            provider_config.deepgram_api_key or os.environ["DEEPGRAM_API_KEY"]
        )
        self.elevenlabs_api_key = (
            provider_config.elevenlabs_api_key or os.environ["ELEVENLABS_API_KEY"]
        )

    async def start(self):
        transport = FastAPIWebsocketTransport(
            websocket=self.websocket,
            params=FastAPIWebsocketParams(
                audio_out_enabled=True,
                add_wav_header=False,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                vad_audio_passthrough=True,
                serializer=TwilioFrameSerializer(stream_sid),
            ),
        )

        llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY", ""))

        tts = CartesiaTTSService(
            api_key=os.getenv("CARTESIA_API_KEY", ""),
            voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British Lady
        )

        messages = [
            {
                "role": "system",
                "content": "You are a helpful LLM in an audio call. Your goal is to demonstrate your capabilities in a succinct way. Your output will be converted to audio so don't include special characters in your answers. Respond to what the user said in a creative and helpful way.",
            },
        ]

        context = OpenAILLMContext(messages)  # type: ignore
        context_aggregator = llm.create_context_aggregator(context)

        pipeline = Pipeline(
            [
                transport.input(),  # Websocket input from client
                stt,  # Speech-To-Text
                context_aggregator.user(),
                llm,  # LLM
                tts,  # Text-To-Speech
                transport.output(),  # Websocket output to client
                context_aggregator.assistant(),
            ]
        )

        task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            # Kick off the conversation.
            messages.append(
                {"role": "system", "content": "Please introduce yourself to the user."}
            )
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            await task.cancel()

        self.runner = PipelineRunner(handle_sigint=False)

        await self.runner.run(task)

    async def stop(self):
        if self.runner is not None:
            await self.runner.cancel()
