from pydantic import BaseModel, ConfigDict

from enums import ConsumableCategory


class ConsumableBase(BaseModel):
    name: str
    needed: bool
    category: ConsumableCategory


class ConsumableCreate(ConsumableBase): ...


class ConsumableUpdate(BaseModel):
    name: str | None = None
    needed: bool | None = None
    category: ConsumableCategory | None = None


class ConsumableSchema(ConsumableBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
