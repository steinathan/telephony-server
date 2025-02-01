from typing import Any, Literal
from pydantic import BaseModel as Pydantic1BaseModel


PhoneCallDirection = Literal["inbound", "outbound"]

class BaseModel(Pydantic1BaseModel):
    pass 



# Adapted from https://github.com/pydantic/pydantic/discussions/3091
class TypedModel(BaseModel):
    _subtypes_: list[tuple[Any, Any]] = []

    def __init_subclass__(cls, type=None):  # type: ignore
        cls._subtypes_.append((type, cls))

    @classmethod
    def get_cls(_cls, type):
        for t, cls in _cls._subtypes_:
            if t == type:
                return cls
        raise ValueError(f"Unknown type {type}")

    @classmethod
    def get_type(_cls, cls_name):
        for t, cls in _cls._subtypes_:
            if cls.__name__ == cls_name:
                return t
        raise ValueError(f"Unknown class {cls_name}")

    @classmethod
    def parse_obj(cls, obj):
        data_type = obj.get("type")
        if data_type is None:
            raise ValueError(f"type is required for {cls.__name__}")

        sub = cls.get_cls(data_type)
        if sub is None:
            raise ValueError(f"Unknown type {data_type}")
        return sub(**obj)

    def _iter(self, **kwargs):
        yield "type", self.get_type(self.__class__.__name__)
        yield from super()._iter(**kwargs)

    @property
    def type(self):
        return self.get_type(self.__class__.__name__)
