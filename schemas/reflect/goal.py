from pydantic import BaseModel, ConfigDict

from enums import GoalPriority, GoalStatus, HistoryOperation


class GoalBase(BaseModel):
    title: str
    priority: GoalPriority
    exit_criteria: str
    action_plan: str


class GoalCreate(GoalBase):
    month_created: str  # "YYYY-MM"


class GoalUpdate(BaseModel):
    title: str | None = None
    priority: GoalPriority | None = None
    exit_criteria: str | None = None
    action_plan: str | None = None
    status: GoalStatus | None = None


class Goal(GoalBase):
    id: str
    status: GoalStatus
    created_at: int
    month_created: str  # "YYYY-MM"

    model_config = ConfigDict(from_attributes=True)


class HistoryEntry(BaseModel):
    timestamp: str  # ISO 8601
    operation: HistoryOperation
    changes: dict[str, str | None]  # field name -> new value
