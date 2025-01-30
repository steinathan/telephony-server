
from streaming_providers.abstract import AbstractStreamingProviderFactory
from streaming_providers.base import BaseStreamingProvider
from streaming_providers.jay.jay import  JayStreamingConfig, JayStreamingProvider
from streaming_providers.models import StreamingProviderConfig


class DefaultStreamingProviderFactory(AbstractStreamingProviderFactory):
    def create_agent(self, streaming_provider_config: StreamingProviderConfig) -> BaseStreamingProvider:
        if isinstance(streaming_provider_config, JayStreamingConfig):
            return JayStreamingProvider(provider_config=streaming_provider_config)
        raise Exception("Invalid streaming config", streaming_provider_config.type)
