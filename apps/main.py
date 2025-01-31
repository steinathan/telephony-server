# Standard library imports
import os
import sys

from dotenv import load_dotenv

# Third-party imports
from fastapi import FastAPI
from loguru import logger
from pyngrok import ngrok

from telephony.config_manager.redis_config_manager import RedisConfigManager
from telephony.models.telephony import TwilioConfig
from telephony.server.server import TelephonyServer, TwilioInboundCallConfig


load_dotenv()


app = FastAPI()

config_manager = RedisConfigManager()

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    streaming_provider_config=None,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/twilio/inbound_call",
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),
        ),
    ],
)

app.include_router(telephony_server.get_router())
