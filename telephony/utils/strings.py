from cuid2 import Cuid

from telephony.models.audio import AudioEncoding

PER_CHUNK_ALLOWANCE_SECONDS = 0.01



def get_chunk_size_per_second(audio_encoding: AudioEncoding, sampling_rate: int) -> int:
    if audio_encoding == AudioEncoding.LINEAR16:
        return sampling_rate * 2
    elif audio_encoding == AudioEncoding.MULAW:
        return sampling_rate
    else:
        raise Exception("Unsupported audio encoding")


def create_conversation_id(direction: str):
    CUID_GENERATOR: Cuid = Cuid(length=5)

    return f"{direction}_{CUID_GENERATOR.generate()}"
