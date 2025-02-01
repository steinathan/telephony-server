from pydantic import BaseModel

from telephony.models.model import TypedModel


class BaseMessage(BaseModel):
    type: str = "base_message"
    message: str


class StreamingProviderConfig(TypedModel, type="streaming_provider_base"):
    prompt_premble: BaseMessage
    greeting_message: BaseMessage | None = None
