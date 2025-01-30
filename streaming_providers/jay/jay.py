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
    agent_id: str
    deepgram_api_key: str | None = None
    llm_model: str | None = "gpt-4o"
    openai_api_key: str | None = None
    elevenlabs_api_key: str | None = None


class JayStreamingProvider(BaseStreamingProvider):
    def __init__(self, provider_config: JayStreamingConfig):
        self.provider_config = provider_config
        self.llm_model = provider_config.llm_model or "gpt-4o"        
        self.openai_api_key = provider_config.openai_api_key or os.environ["OPENAI_COMPATIBLE_API_KEY"]
        self.deepgram_api_key = provider_config.deepgram_api_key or os.environ["DEEPGRAM_API_KEY"]
        self.elevenlabs_api_key = provider_config.elevenlabs_api_key or os.environ["ELEVENLABS_API_KEY"]

    async def configure_session(self, input: ConfigureSessionInput):
        return SessionConfig(
            initial_messages=[],
            vad=VAD.Silero(),
            stt=STT.Deepgram(api_key=self.deepgram_api_key),
            tts=TTS.ElevenLabs(api_key=self.elevenlabs_api_key),
        )

    async def llm_response_handler(self, input: LLMResponseHandlerInput):
        client = AsyncOpenAI(api_key=self.openai_api_key)
        messages = input["messages"]
        completion = await client.chat.completions.create(
            model=self.llm_model,
            messages=messages, # type: ignore
            stream=True,
        ) # type: ignore
        return completion

    async def start(self):
        agent = Agent(
            id=self.provider_config.agent_id,
            configure_session=self.configure_session,
            llm_response_handler=self.llm_response_handler,
        )
        # agent.start() # I'm not sure if this is the right way to start the agent, but I'm trying to make it work.

    async def stop(self):
        pass
