from fastapi import WebSocket
from streaming_providers.base import BaseStreamingProvider
from streaming_providers.models import StreamingProviderConfig
import os

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

from streaming_providers.pipecat.frame_serializer import TwilioFrameSerializer
from telephony.config_manager.base_config_manager import (
    BaseCallConfig,
    BaseConfigManager,
)
from telephony.server.output_devices.abstract_output_device import AbstractOutputDevice
from telephony.utils.events_manager import EventsManager


class PipecatStreamingConfig(
    StreamingProviderConfig, type="streaming_provider_pipecat"
):
    deepgram_api_key: str | None = None
    llm_model: str | None = "gpt-4o"
    openai_api_key: str | None = None
    elevenlabs_api_key: str | None = None


class PipecatStreamingProvider(BaseStreamingProvider):
    def __init__(
        self,
        websocket: WebSocket,
        device: AbstractOutputDevice,
        call_config: BaseCallConfig,
        provider_config: PipecatStreamingConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ):
        super().__init__(
            websocket=websocket,
            call_config=call_config,
            device=device,
            streaming_provider_config=provider_config,
            config_manager=config_manager,
            events_manager=events_manager,
        )

        self.call_config = call_config
        self.provider_config = provider_config
        self.config_manager = config_manager
        self.device = device

    async def start(self):
        stream_id = self.device.telephony_stream_id 
        assert stream_id is not None, "Stream ID must be provided"

        transport = FastAPIWebsocketTransport(
            websocket=self.websocket,
            params=FastAPIWebsocketParams(
                audio_out_enabled=True,
                add_wav_header=False,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
                vad_audio_passthrough=True,
                serializer=TwilioFrameSerializer(stream_id, self.device),
            ),
        )

        llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY", ""))

        tts = ElevenLabsTTSService(
            api_key=os.getenv("ELEVENLABS_API_KEY", ""),
            voice_id="21m00Tcm4TlvDq8ikWAM",
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
