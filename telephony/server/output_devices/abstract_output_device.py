from abc import abstractmethod

from fastapi import WebSocket

import telephony
from telephony.models.audio import AudioEncoding
from telephony.server.output_devices.audio_chunk import AudioChunk
from telephony.server.worker import AsyncWorker, InterruptibleEvent


class AbstractOutputDevice(AsyncWorker[InterruptibleEvent[AudioChunk]]):

    telephony_stream_id: str
    ws: WebSocket | None = None

    def __init__(self, sampling_rate: int, audio_encoding: AudioEncoding):
        super().__init__()
        self.sampling_rate = sampling_rate
        self.audio_encoding = audio_encoding

    def set_streaming_id(self, streaming_id):
        self.telephony_stream_id = streaming_id
