from typing import Dict, Optional
import typing

from loguru import logger

from telephony.clients.abstract import AbstractTelephonyClient
from telephony.clients.twilio_client import TwilioClient
from telephony.config_manager.base_config_manager import (
    BaseCallConfig,
    BaseConfigManager,
)
from telephony.models.telephony import TwilioCallConfig, TwilioConfig
from telephony.models.telephony import TelephonyConfig


class OutboundCall:
    def __init__(
        self,
        base_url: str,
        to_phone: str,
        from_phone: str,
        config_manager: BaseConfigManager,
        conversation_id: str,
        telephony_config: TelephonyConfig,
        telephony_params: Optional[Dict[str, str]] = None,
        sentry_tags: Dict[str, str] = {},
        digits: Optional[
            str
        ] = None,  # Keys to press when the call connects, see send_digits https://www.twilio.com/docs/voice/api/call-resource#create-a-call-resource
    ):
        self.base_url = base_url
        self.to_phone = to_phone
        self.from_phone = from_phone
        self.config_manager = config_manager
        self.conversation_id = conversation_id
        self.telephony_config = telephony_config
        self.telephony_params = telephony_params or {}
        self.telephony_client = self.create_telephony_client()
        self.sentry_tags = sentry_tags
        self.digits = digits

    def create_telephony_client(self) -> AbstractTelephonyClient:
        if isinstance(self.telephony_config, TwilioConfig):
            return TwilioClient(
                base_url=self.base_url, maybe_twilio_config=self.telephony_config
            )
        else:
            raise ValueError("Unsupported telephony configuration")

    async def start(self):
        logger.debug("Starting outbound call")
        self.telephony_id = await self.telephony_client.create_call(
            conversation_id=self.conversation_id,
            to_phone=self.to_phone,
            from_phone=self.from_phone,
            record=self.telephony_client.get_telephony_config().record,  # note twilio does not use this
            telephony_params=self.telephony_params,
            digits=self.digits,
        )
        if isinstance(self.telephony_client, TwilioClient):
            call_config = TwilioCallConfig(
                twilio_config=self.telephony_client.twilio_config,
                twilio_sid=self.telephony_id,
                from_phone=self.from_phone,
                to_phone=self.to_phone,
                sentry_tags=self.sentry_tags,
                telephony_params=self.telephony_params,
                direction="outbound",
            )
        else:
            raise ValueError("Unknown telephony client")
        await self.config_manager.save_config(
            conversation_id=self.conversation_id,
            config=typing.cast(BaseCallConfig, call_config),
        )

    async def end(self):
        return await self.telephony_client.end_call(self.telephony_id)
