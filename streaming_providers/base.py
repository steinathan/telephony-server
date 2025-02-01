from abc import ABC, abstractmethod

from fastapi import WebSocket

from streaming_providers.models import StreamingProviderConfig
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.utils.events_manager import EventsManager


class BaseStreamingProvider(ABC):
    def __init__(
        self,
        websocket: WebSocket,
        streaming_provider_config: StreamingProviderConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ):
        self.websocket = websocket
        self.streaming_provider_config = streaming_provider_config
        self.config_manager = config_manager
        self.events_manager = events_manager

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
