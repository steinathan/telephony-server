
from abc import ABC, abstractmethod

from streaming_providers.base import BaseStreamingProvider
from streaming_providers.models import StreamingProviderConfig




class AbstractStreamingProviderFactory(ABC):
    @abstractmethod
    def create_agent(self, streaming_provider_config: StreamingProviderConfig) -> BaseStreamingProvider:
        pass

