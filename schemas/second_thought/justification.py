from datetime import datetime
from pydantic import BaseModel


class JustificationBase(BaseModel):
    domain: str
    url: str
    reason: str
    duration: int


class JustificationCreate(JustificationBase): ...


class Justification(JustificationBase):
    ts: datetime

    class Config:
        from_attributes = True
