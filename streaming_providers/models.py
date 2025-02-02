from telephony.models.model import TypedModel


class BaseMessage(TypedModel, type="base_message"):
    message: str


class StreamingProviderConfig(TypedModel, type="streaming_provider_base"):
    prompt_premble: BaseMessage
    greeting_message: BaseMessage | None = None
