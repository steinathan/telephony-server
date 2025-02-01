import base64
import json
import os
from enum import Enum
from typing import Optional

from fastapi import WebSocket
from loguru import logger

from streaming_providers.base import BaseStreamingProvider
from telephony.clients.twilio_client import TwilioClient
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.models.events import PhoneCallConnectedEvent
from telephony.models.telephony import TwilioConfig
from telephony.server.conversation.abstract_phone_conversation import AbstractPhoneConversation
from telephony.server.output_devices.twilio_output_device import ChunkFinishedMarkMessage, TwilioOutputDevice
from telephony.server.state_manager.phone_state_manager import PhoneConversationStateManager
from telephony.utils.events_manager import EventsManager
from telephony.models.telephony import PhoneCallDirection

class TwilioPhoneConversationWebsocketAction(Enum):
    CLOSE_WEBSOCKET = 1


class TwilioPhoneConversationStateManager(PhoneConversationStateManager):
    def __init__(self, conversation: "TwilioPhoneConversation"):
        super().__init__(conversation=conversation)
        self._twilio_phone_conversation = conversation

    def get_twilio_config(self):
        return self._twilio_phone_conversation.twilio_config

    def get_twilio_sid(self):
        return self._twilio_phone_conversation.twilio_sid

    def create_twilio_client(self):
        return TwilioClient(
            base_url=self._twilio_phone_conversation.base_url,
            maybe_twilio_config=self.get_twilio_config(),
        )


class TwilioPhoneConversation(AbstractPhoneConversation[TwilioOutputDevice]):  # noqa: F821
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
        twilio_config: Optional[TwilioConfig] = None,
        conversation_id: Optional[str] = None,
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
            output_device=TwilioOutputDevice(),
            conversation_id=conversation_id,
            events_manager=events_manager,
        )
        self.config_manager = config_manager
        self.twilio_config = twilio_config or TwilioConfig(
            account_sid=os.environ["TWILIO_ACCOUNT_SID"],
            auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        )
        self.telephony_client = TwilioClient(
            base_url=self.base_url, maybe_twilio_config=self.twilio_config
        )
        self.twilio_sid = twilio_sid
        self.record_call = record_call

    def create_state_manager(self) -> TwilioPhoneConversationStateManager:
        return TwilioPhoneConversationStateManager(self)

    async def attach_ws_and_start(self, ws: WebSocket):
        super().attach_ws(ws)

        await self._wait_for_twilio_start(ws)
        await self.start()
        self.events_manager.publish_event(
            PhoneCallConnectedEvent(
                conversation_id=self.id,
                to_phone_number=self.to_phone,
                from_phone_number=self.from_phone,
            )
        )
        while self.is_active():
            message = await ws.receive_text()
            response = await self._handle_ws_message(message)
            if response == TwilioPhoneConversationWebsocketAction.CLOSE_WEBSOCKET:
                break
        await ws.close(code=1000, reason=None)
        await self.terminate()

    async def _wait_for_twilio_start(self, ws: WebSocket):
        assert isinstance(self.output_device, TwilioOutputDevice)
        while True:
            message = await ws.receive_text()
            if not message:
                continue
            data = json.loads(message)
            if data["event"] == "start":
                logger.debug(f"Media WS: Received event '{data['event']}': {message}")
                self.output_device.stream_sid = data["start"]["streamSid"]
                break

    async def _handle_ws_message(self, message) -> Optional[TwilioPhoneConversationWebsocketAction]:
        if message is None:
            return TwilioPhoneConversationWebsocketAction.CLOSE_WEBSOCKET

        data = json.loads(message)
        if data["event"] == "media":
            media = data["media"]
            chunk = base64.b64decode(media["payload"])
            self.receive_audio(chunk)
        if data["event"] == "mark":
            chunk_id = data["mark"]["name"]
            self.output_device.enqueue_mark_message(ChunkFinishedMarkMessage(chunk_id=chunk_id))
        elif data["event"] == "stop":
            logger.debug(f"Media WS: Received event 'stop': {message}")
            logger.debug("Stopping...")
            return TwilioPhoneConversationWebsocketAction.CLOSE_WEBSOCKET
        return None


    def consume_nonblocking(self, item):
        raise NotImplementedError

    def is_active(self):
        raise NotImplementedError

