from abc import abstractmethod
from typing import Literal, Optional, TypeVar

from fastapi import WebSocket
from loguru import logger

from streaming_providers.base import BaseStreamingProvider
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.models.events import PhoneCallEndedEvent
from telephony.server.output_devices.abstract_output_device import AbstractOutputDevice
from telephony.utils.events_manager import EventsManager

from telephony.models.model import PhoneCallDirection

OutputDeviceType = TypeVar("OutputDeviceType", bound=AbstractOutputDevice)

TelephonyProvider = Literal["twilio", "vonage", "plivo"]


class AbstractPhoneConversation:
    telephony_provider: TelephonyProvider

    def __init__(
        self,
        streaming_provider: BaseStreamingProvider,
        direction: PhoneCallDirection,
        from_phone: str,
        to_phone: str,
        base_url: str,
        conversation_id: str ,
        output_device: AbstractOutputDevice,
        config_manager: BaseConfigManager,
        events_manager: Optional[EventsManager] = None,
    ):
        self.streaming_provider = streaming_provider
        self.conversation_id = conversation_id

        self.events_manager = events_manager or EventsManager()
        self.direction = direction
        self.from_phone = from_phone
        self.to_phone = to_phone
        self.base_url = base_url
        self.output_device = output_device
        self.config_manager = config_manager

    def attach_ws(self, ws: WebSocket):
        logger.debug("Trying to attach WS to outbound call")
        self.output_device.ws = ws
        logger.debug("Attached WS to outbound call")

    @abstractmethod
    async def attach_ws_and_start(self, ws: WebSocket):
        pass

    async def start_until_completed(self):
        await self.streaming_provider.start()

    async def terminate(self):
        logger.warning(f"TODO: Terminating  call: {self.conversation_id}")
        self.events_manager.publish_event(PhoneCallEndedEvent(conversation_id=self.conversation_id))
