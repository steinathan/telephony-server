from typing import Literal
from pydantic import BaseModel as Pydantic1BaseModel


PhoneCallDirection = Literal["inbound", "outbound"]

class BaseModel(Pydantic1BaseModel):
    pass 