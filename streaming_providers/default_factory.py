from streaming_providers.abstract import AbstractStreamingProviderFactory
from streaming_providers.base import BaseStreamingProvider
from streaming_providers.jay.jay import JayStreamingConfig, JayStreamingProvider
from streaming_providers.models import StreamingProviderConfig
from streaming_providers.pipecat.pipecat import (
    PipecatStreamingConfig,
    PipecatStreamingProvider,
)
from telephony.config_manager.base_config_manager import BaseConfigManager
from telephony.utils.events_manager import EventsManager


class DefaultStreamingProviderFactory(AbstractStreamingProviderFactory):
    def create_streaming_provider(
        self,
        streaming_provider_config: StreamingProviderConfig,
        config_manager: BaseConfigManager,
        events_manager: EventsManager | None = None,
    ) -> BaseStreamingProvider:
        if isinstance(streaming_provider_config, JayStreamingConfig):
            return JayStreamingProvider(provider_config=streaming_provider_config)

        if isinstance(streaming_provider_config, PipecatStreamingConfig):
            return PipecatStreamingProvider(
                provider_config=streaming_provider_config,
                config_manager=config_manager,
                events_manager=events_manager,
            )
        raise Exception("Invalid streaming config", streaming_provider_config.type)
