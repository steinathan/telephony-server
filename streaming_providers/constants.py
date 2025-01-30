from enum import Enum


class StreamingProviderType(str, Enum):
    JAY = "streaming_provider_jay"
    PIPECAT = "streaming_provider_pipecat"
