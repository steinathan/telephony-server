import base64
import json
from typing import Optional

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from telephony.constants.constants import DEFAULT_AUDIO_ENCODING, DEFAULT_CHUNK_SIZE, DEFAULT_SAMPLING_RATE, MULAW_SILENCE_BYTE
from telephony.server.output_devices.blocking_speaker_output import BlockingSpeakerOutput
from telephony.server.output_devices.rate_limit_interruptions_output_device import RateLimitInterruptionsOutputDevice



class PlivoOutputDevice(RateLimitInterruptionsOutputDevice):
    def __init__(
        self,
        ws: Optional[WebSocket] = None,
        output_to_speaker: bool = False,
    ):
        super().__init__(sampling_rate=DEFAULT_SAMPLING_RATE, audio_encoding=DEFAULT_AUDIO_ENCODING)
        self.ws = ws
        self.output_to_speaker = output_to_speaker
        if output_to_speaker:
            self.output_speaker = BlockingSpeakerOutput.from_default_device(
                sampling_rate=DEFAULT_SAMPLING_RATE, blocksize=DEFAULT_CHUNK_SIZE // 2
            )

    async def pipe_to_plivo(self, chunk: bytes):
        assert self.ws is not None, "ws is not attached"

        encode = base64.b64encode(chunk).decode("utf-8")
        data = {
            "event": "playAudio",
            "media": {"contentType": "audio/x-mulaw", "sampleRate": 8000, "payload": encode},
        }
        data = json.dumps(data)
        await self.ws.send_text(data)

    async def play(self, chunk: bytes):
        if self.output_to_speaker:
            self.output_speaker.consume_nonblocking(chunk) # type: ignore

        for i in range(0, len(chunk), DEFAULT_CHUNK_SIZE):
            subchunk = chunk[i : i + DEFAULT_CHUNK_SIZE]
            if len(subchunk) % 2 == 1:
                subchunk += MULAW_SILENCE_BYTE
            if self.ws and self.ws.application_state != WebSocketState.DISCONNECTED:
                await self.pipe_to_plivo(subchunk)
