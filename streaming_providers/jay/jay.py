import os
from openai import AsyncOpenAI
from jay_ai import (
    VAD,
    STT,
    TTS,
    ConfigureSessionInput,
    SessionConfig,
    LLMResponseHandlerInput,
    Agent,
)
from streaming_providers.base import BaseStreamingProvider
from streaming_providers.models import StreamingProviderConfig


# I have no idea what I'm doing, but I'm trying to make this work.
# so i should create a factory function that returns the agent
# but since Jay is expected to be ran in a different way, I'm not sure how to do that.

class JayStreamingConfig(StreamingProviderConfig):
    type: str = "streaming_provider_jay"


class JayStreamingProvider(BaseStreamingProvider):
    def __init__(self, provider_config: JayStreamingConfig):
        self.provider_config = provider_config

    async def configure_session(self, input: ConfigureSessionInput):
        return SessionConfig(
            initial_messages=[],
            vad=VAD.Silero(),
            stt=STT.Deepgram(api_key=os.environ["DEEPGRAM_API_KEY"]),
            tts=TTS.ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"]),
        )

    async def llm_response_handler(self, input: LLMResponseHandlerInput):
        client = AsyncOpenAI(api_key=os.environ["OPENAI_COMPATIBLE_API_KEY"])
        messages = input["messages"]
        completion = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
        )
        return completion

    async def start(self):
        agent = Agent(
            id="cm6icplb10002lskeiw824cfd",
            configure_session=self.configure_session,
            llm_response_handler=self.llm_response_handler,
        )
        # agent.start() # I'm not sure if this is the right way to start the agent, but I'm trying to make it work.

    async def stop(self):
        pass
