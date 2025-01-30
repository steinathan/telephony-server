from enum import Enum
from typing import Literal, Optional

from telephony.models.model import BaseModel

class CallConfigType(str, Enum):
    BASE = "call_config_base"
    TWILIO = "call_config_twilio"
    VONAGE = "call_config_vonage"
    PLIVO = "call_config_plivo"

PhoneCallDirection = Literal["inbound", "outbound"]

class BaseCallConfig(BaseModel):  # type: ignore
    from_phone: str
    to_phone: str
    sentry_tags: dict[str, str] = {}
    conference: bool = False
    telephony_params: Optional[dict[str, str]] = None
    direction: PhoneCallDirection

    @staticmethod
    def default_transcriber_config():
        raise NotImplementedError

    @staticmethod
    def default_synthesizer_config():
        raise NotImplementedError



class BaseConfigManager:
    async def save_config(self, conversation_id: str, config: BaseCallConfig):
        raise NotImplementedError

    async def get_config(self, conversation_id) -> Optional[BaseCallConfig]:
        raise NotImplementedError

    async def delete_config(self, conversation_id):
        raise NotImplementedError
