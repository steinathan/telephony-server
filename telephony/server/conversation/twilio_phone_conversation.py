import json
from enum import Enum
from typing import Optional

from fastapi import WebSocket
from loguru import logger

from streaming_providers.base import BaseStreamingProvider
from telephony.clients.twilio_client import TwilioClient
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.models.events import PhoneCallConnectedEvent
from telephony.models.telephony import TwilioConfig
from telephony.server.conversation.abstract_phone_conversation import (
    AbstractPhoneConversation,
)
from telephony.server.output_devices.abstract_output_device import AbstractOutputDevice
from telephony.utils.events_manager import EventsManager
from telephony.models.telephony import PhoneCallDirection


class TwilioPhoneConversationWebsocketAction(Enum):
    CLOSE_WEBSOCKET = 1


class TwilioPhoneConversation(AbstractPhoneConversation):  # noqa: F821
    telephony_provider = "twilio"

    def __init__(
        self,
        streaming_provider: BaseStreamingProvider,
        direction: PhoneCallDirection,
        from_phone: str,
        to_phone: str,
        base_url: str,
        config_manager: BaseConfigManager,
        twilio_sid: str,
        conversation_id: str,
        device: AbstractOutputDevice,
        twilio_config: TwilioConfig,
        events_manager: Optional[EventsManager] = None,
        record_call: bool = False,
    ):


        super().__init__(
            streaming_provider=streaming_provider,
            direction=direction,
            from_phone=from_phone,
            to_phone=to_phone,
            base_url=base_url,
            config_manager=config_manager,
            output_device=device,
            conversation_id=conversation_id,
            events_manager=events_manager,
        )
        self.twilio_config = twilio_config 
        self.telephony_client = TwilioClient(
            base_url=self.base_url, maybe_twilio_config=self.twilio_config
        )
        self.twilio_sid = twilio_sid


    async def attach_ws_and_start(self, ws: WebSocket):
        super().attach_ws(ws)

        await self._wait_for_twilio_start(ws)

        self.events_manager.publish_event(
            PhoneCallConnectedEvent(
                conversation_id=self.conversation_id,
                to_phone_number=self.to_phone,
                from_phone_number=self.from_phone,
            )
        )

        await self.start_until_completed()
        await self.terminate()

    async def _wait_for_twilio_start(self, ws: WebSocket):
        while True:
            message = await ws.receive_text()
            if not message:
                continue
            data = json.loads(message)
            if data["event"] == "start":
                logger.debug(f"Media WS: Received event '{data['event']}': {message}")
                self.output_device.set_ws(ws)
                self.output_device.set_streaming_id(data["start"]["streamSid"])
                break