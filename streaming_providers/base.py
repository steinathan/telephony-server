from abc import ABC, abstractmethod

from fastapi import WebSocket

from streaming_providers.models import StreamingProviderConfig
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.models.telephony import BaseCallConfig
from telephony.server.output_devices.abstract_output_device import AbstractOutputDevice
from telephony.utils.events_manager import EventsManager


class BaseStreamingProvider(ABC):
    def __init__(
        self,
        websocket: WebSocket,
        call_config: BaseCallConfig,
        device: AbstractOutputDevice,
        streaming_provider_config: StreamingProviderConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ):
        self.websocket = websocket
        self.streaming_provider_config = streaming_provider_config
        self.config_manager = config_manager
        self.events_manager = events_manager
        self.device = device
        self.call_config = call_config

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
