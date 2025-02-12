from enum import Enum
from typing import Optional

from telephony.models.model import BaseModel



class Sender(str, Enum):
    HUMAN = "human"
    BOT = "bot"
    ACTION_WORKER = "action_worker"
    VECTOR_DB = "vector_db"
    CONFERENCE = "conference"


class EventType(str, Enum):
    TRANSCRIPT = "event_transcript"
    TRANSCRIPT_COMPLETE = "event_transcript_complete"
    PHONE_CALL_CONNECTED = "event_phone_call_connected"
    PHONE_CALL_ENDED = "event_phone_call_ended"
    PHONE_CALL_DID_NOT_CONNECT = "event_phone_call_did_not_connect"
    RECORDING = "event_recording"
    ACTION = "event_action"


class Event(BaseModel):
    type: str = "event"
    conversation_id: str


class PhoneCallConnectedEvent(Event):
    event_type: EventType = EventType.PHONE_CALL_CONNECTED
    to_phone_number: str
    from_phone_number: str


class PhoneCallEndedEvent(Event):
    event_type: EventType = EventType.PHONE_CALL_ENDED
    conversation_minutes: float = 0


class PhoneCallDidNotConnectEvent(Event):
    event_type: EventType = EventType.PHONE_CALL_DID_NOT_CONNECT
    telephony_status: str


class RecordingEvent(Event):
    event_type: EventType = EventType.RECORDING
    recording_url: str


class ActionEvent(Event):
    event_type: EventType = EventType.ACTION
    action_input: Optional[dict] = None
    action_output: Optional[dict] = None
