from pydantic import BaseModel


class BaseMessage(BaseModel):
    type: str = "base_message"
    message: str


class StreamingProviderConfig(BaseModel):
    type: str = "streaming_provider_base"
    prompt_premble: BaseMessage
    greeting_message: BaseMessage | None = None
