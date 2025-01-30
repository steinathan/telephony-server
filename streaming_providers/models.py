from pydantic import BaseModel


class StreamingProviderConfig(BaseModel):  
    type: str = "streaming_provider_base"
