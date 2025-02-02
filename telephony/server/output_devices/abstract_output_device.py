from fastapi import WebSocket


class AbstractOutputDevice:
    def __init__(self):
        self.telephony_stream_id: str | None = None
        self.ws: WebSocket | None = None

    def set_streaming_id(self, streaming_id):
        self.telephony_stream_id = streaming_id

    def set_ws(self, ws):
        self.ws = ws
