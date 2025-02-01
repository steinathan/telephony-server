from enum import Enum
from typing import Any, Dict, Literal, Optional, Union
from streaming_providers.models import StreamingProviderConfig
from telephony.models.model import BaseModel, TypedModel


class TelephonyProviderConfig(BaseModel):
    record: bool = False


class TwilioConfig(TelephonyProviderConfig):
    account_sid: str
    auth_token: str
    extra_params: Optional[Dict[str, Any]] = {}
    account_supports_any_caller_id: bool = True


class PlivoConfig(TelephonyProviderConfig):
    auth_id: str
    auth_token: str
    extra_params: Optional[Dict[str, Any]] = {}


class VonageConfig(TelephonyProviderConfig):
    api_key: str
    api_secret: str
    application_id: str
    private_key: str


class CallEntity(BaseModel):
    phone_number: str


class CreateInboundCall(BaseModel):
    recipient: CallEntity
    caller: CallEntity
    vonage_uuid: Optional[str] = None
    twilio_sid: Optional[str] = None
    conversation_id: Optional[str] = None
    twilio_config: Optional[TwilioConfig] = None
    vonage_config: Optional[VonageConfig] = None
    plivo_config: Optional[PlivoConfig] = None


class EndOutboundCall(BaseModel):
    call_id: str
    vonage_config: Optional[VonageConfig] = None
    twilio_config: Optional[TwilioConfig] = None
    plivo_config: Optional[PlivoConfig] = None


class CreateOutboundCall(BaseModel):
    recipient: CallEntity
    caller: CallEntity
    conversation_id: Optional[str] = None
    vonage_config: Optional[VonageConfig] = None
    twilio_config: Optional[TwilioConfig] = None
    plivo_config: Optional[PlivoConfig] = None
    # TODO add IVR/etc.


class DialIntoZoomCall(BaseModel):
    recipient: CallEntity
    caller: CallEntity
    zoom_meeting_id: str
    zoom_meeting_password: Optional[str]
    conversation_id: Optional[str] = None
    vonage_config: Optional[VonageConfig] = None
    twilio_config: Optional[TwilioConfig] = None
    plivo_config: Optional[PlivoConfig] = None


class CallConfigType(str, Enum):
    BASE = "call_config_base"
    TWILIO = "call_config_twilio"
    VONAGE = "call_config_vonage"
    PLIVO = "call_config_plivo"


PhoneCallDirection = Literal["inbound", "outbound"]


class BaseCallConfig(TypedModel, type=CallConfigType.BASE.value):  
    model_config = {"extra": "allow"}
    streaming_provider_config: StreamingProviderConfig
    from_phone: str
    to_phone: str
    sentry_tags: Dict[str, str] = {}
    conference: bool = False
    telephony_params: Optional[Dict[str, str]] = None
    direction: PhoneCallDirection


class TwilioCallConfig(BaseCallConfig, type=CallConfigType.TWILIO.value):  
    twilio_config: TwilioConfig
    twilio_sid: str


class VonageCallConfig(BaseCallConfig, type=CallConfigType.VONAGE.value):  # type: ignore
    vonage_config: VonageConfig
    vonage_uuid: str
    output_to_speaker: bool = False


class PlivoCallConfig(BaseCallConfig, type=CallConfigType.PLIVO.value):  # type: ignore
    plivo_config: PlivoConfig
    plivo_uuid: str


TelephonyConfig = Union[TwilioConfig, VonageConfig, PlivoConfig]
