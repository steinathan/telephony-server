import os

from dotenv import load_dotenv

from fastapi import FastAPI

from streaming_providers.models import BaseMessage
from streaming_providers.pipecat.pipecat import PipecatStreamingConfig
from telephony.config_manager.redis_config_manager import RedisConfigManager
from telephony.models.telephony import TwilioConfig
from telephony.server.server import TelephonyServer, TwilioInboundCallConfig


load_dotenv()


app = FastAPI()


BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=RedisConfigManager(),
    streaming_provider_config=PipecatStreamingConfig(
        deepgram_api_key=os.environ["DEEPGRAM_API_KEY"],
        openai_api_key=os.environ["OPENAI_API_KEY"],
        elevenlabs_api_key=os.environ["ELEVENLABS_API_KEY"],
        llm_model="gpt-4o-mini",
        greeting_message=BaseMessage(
            message="Hello, I'm Navi, your assistant. How can I help you today?"
        ),
        prompt_premble=BaseMessage(message="you are a friendly assistant"),
    ),
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/twilio/inbound_call",
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
                record=True,
            ),
        ),
    ],
)

app.include_router(telephony_server.get_router())
