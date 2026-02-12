from pydantic import BaseModel, ConfigDict


class ScratchpadNoteBase(BaseModel):
    text: str


class ScratchpadNoteCreate(ScratchpadNoteBase): ...


class ScratchpadNotePromote(BaseModel):
    goal_id: str


class ScratchpadNoteSchema(ScratchpadNoteBase):
    id: str
    created_at: int
    promoted_to_goal_id: str | None

    model_config = ConfigDict(from_attributes=True)
