from abc import ABC, abstractmethod

from fastapi import WebSocket
from streaming_providers.base import BaseStreamingProvider
from streaming_providers.models import StreamingProviderConfig
from streaming_providers.pipecat.pipecat import (
    PipecatStreamingConfig,
    PipecatStreamingProvider,
)
from telephony.config_manager.base_config_manager import BaseCallConfig, BaseConfigManager
from telephony.utils.events_manager import EventsManager


class AbstractStreamingProviderFactory(ABC):
    @abstractmethod
    def create_streaming_provider(
        self,
        websocket: WebSocket,
        call_config: BaseCallConfig,
        streaming_provider_config: StreamingProviderConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ) -> BaseStreamingProvider:
        pass

class DefaultStreamingProviderFactory(AbstractStreamingProviderFactory):
    def create_streaming_provider(
        self,
        websocket: WebSocket,
        call_config: BaseCallConfig,
        streaming_provider_config: StreamingProviderConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ) -> BaseStreamingProvider:
        if isinstance(streaming_provider_config, PipecatStreamingConfig):
            return PipecatStreamingProvider(
                websocket=websocket,
                call_config=call_config,
                provider_config=streaming_provider_config,
                config_manager=config_manager,
                events_manager=events_manager,
            )
        raise Exception("Invalid streaming config" + streaming_provider_config.type)
