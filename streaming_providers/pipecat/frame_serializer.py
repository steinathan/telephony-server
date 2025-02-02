#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import base64
import json

from pydantic import BaseModel

from pipecat.audio.utils import pcm_to_ulaw, ulaw_to_pcm
from pipecat.frames.frames import (
    AudioRawFrame,
    Frame,
    InputAudioRawFrame,
    InputDTMFFrame,
    KeypadEntry,
    StartInterruptionFrame,
)
from pipecat.serializers.base_serializer import FrameSerializer, FrameSerializerType

from telephony.server.output_devices.abstract_output_device import AbstractOutputDevice
from telephony.server.output_devices.audio_chunk import AudioChunk
from telephony.server.worker import InterruptibleEvent


class TwilioFrameSerializer(FrameSerializer):
    class InputParams(BaseModel):
        twilio_sample_rate: int = 8000
        sample_rate: int = 16000

    def __init__(
        self,
        stream_sid: str,
        device: AbstractOutputDevice,
        params: InputParams = InputParams(),
    ):
        self._stream_sid = stream_sid
        self._params = params
        self.device = device

    @property
    def type(self) -> FrameSerializerType:
        return FrameSerializerType.TEXT

    # send ai message
    def serialize(self, frame: Frame) -> str | bytes | None:
        if isinstance(frame, AudioRawFrame):
            data = frame.audio

            serialized_data = pcm_to_ulaw(
                data, frame.sample_rate, self._params.twilio_sample_rate
            )
            payload = base64.b64encode(serialized_data).decode("utf-8")
            answer = {
                "event": "media",
                "streamSid": self._stream_sid,
                "media": {"payload": payload},
            }

            # self.device.consume_nonblocking(InterruptibleEvent(AudioChunk(data=data)))

            return json.dumps(answer)

        if isinstance(frame, StartInterruptionFrame):
            answer = {"event": "clear", "streamSid": self._stream_sid}
            return json.dumps(answer)


    # send human message
    def deserialize(self, data: str | bytes) -> Frame | None:
        message = json.loads(data)

        if message["event"] == "media":
            payload_base64 = message["media"]["payload"]
            payload = base64.b64decode(payload_base64)

            deserialized_data = ulaw_to_pcm(
                payload, self._params.twilio_sample_rate, self._params.sample_rate
            )
            audio_frame = InputAudioRawFrame(
                audio=deserialized_data, num_channels=1, sample_rate=self._params.sample_rate
            )
            return audio_frame
        elif message["event"] == "dtmf":
            digit = message.get("dtmf", {}).get("digit")

            try:
                return InputDTMFFrame(KeypadEntry(digit))
            except ValueError as e:
                # Handle case where string doesn't match any enum value
                return None
        else:
            return None

