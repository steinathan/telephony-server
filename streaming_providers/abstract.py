from abc import ABC, abstractmethod

from fastapi import WebSocket

from streaming_providers.base import BaseStreamingProvider
from streaming_providers.models import StreamingProviderConfig
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.utils.events_manager import EventsManager


class AbstractStreamingProviderFactory(ABC):
    @abstractmethod
    def create_streaming_provider(
        self,
        websocket: WebSocket,
        streaming_provider_config: StreamingProviderConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ) -> BaseStreamingProvider:
        pass
