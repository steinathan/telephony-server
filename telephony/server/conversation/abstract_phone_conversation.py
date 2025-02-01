from abc import abstractmethod
from typing import Generic, Literal, Optional, TypeVar, Union

from fastapi import WebSocket
from loguru import logger

from streaming_providers.base import BaseStreamingProvider
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.models.events import PhoneCallEndedEvent
from telephony.server.output_devices.abstract_output_device import AbstractOutputDevice
from telephony.server.output_devices.pilvo_output_device import PlivoOutputDevice
from telephony.server.output_devices.twilio_output_device import TwilioOutputDevice
from telephony.server.worker import AbstractWorker
from telephony.utils.events_manager import EventsManager

from telephony.models.model import PhoneCallDirection

TelephonyOutputDeviceType = TypeVar(
    "TelephonyOutputDeviceType",
    bound=Union[TwilioOutputDevice, PlivoOutputDevice],
)

OutputDeviceType = TypeVar("OutputDeviceType", bound=AbstractOutputDevice)

LOW_INTERRUPT_SENSITIVITY_THRESHOLD = 0.9

TelephonyProvider = Literal["twilio", "vonage", "plivo"]


class AudioPipeline(AbstractWorker[bytes], Generic[OutputDeviceType]):
    output_device: OutputDeviceType
    events_manager: EventsManager
    id: str

    def receive_audio(self, chunk: bytes):
        self.consume_nonblocking(chunk)

    @abstractmethod
    def is_active(self):
        raise NotImplementedError


class AbstractPhoneConversation(AudioPipeline[TelephonyOutputDeviceType]):
    telephony_provider: TelephonyProvider

    def __init__(
        self,
        streaming_provider: BaseStreamingProvider,
        direction: PhoneCallDirection,
        from_phone: str,
        to_phone: str,
        base_url: str,
        output_device: TelephonyOutputDeviceType,
        config_manager: BaseConfigManager,
        conversation_id: Optional[str] = None,
        events_manager: Optional[EventsManager] = None,
    ):
        self.streaming_provider = streaming_provider
        conversation_id = conversation_id
        # ctx_conversation_id.set(conversation_id)

        self.direction = direction
        self.from_phone = from_phone
        self.to_phone = to_phone
        self.base_url = base_url
        self.output_device = output_device
        super().__init__(
            # output_device,
            # transcriber_factory.create_transcriber(transcriber_config),
            # agent_factory.create_agent(agent_config),
            # synthesizer_factory.create_synthesizer(synthesizer_config),
            # conversation_id=conversation_id,
            # events_manager=events_manager,
            # speed_coefficient=speed_coefficient,
        )
        self.config_manager = config_manager

    def attach_ws(self, ws: WebSocket):
        logger.debug("Trying to attach WS to outbound call")
        self.output_device.ws = ws
        logger.debug("Attached WS to outbound call")

    @abstractmethod
    async def attach_ws_and_start(self, ws: WebSocket):
        pass
    
    async def start(self):
        await self.streaming_provider.start()

    async def terminate(self):
        self.events_manager.publish_event(PhoneCallEndedEvent(conversation_id=self.id))
        await super().terminate()
