from pydantic import BaseModel, ConfigDict

from hub.reflect.enums import TrackingStatus


class WeeklyCheckInBase(BaseModel):
    goal_id: str
    week_of: str  # ISO date (Monday)
    tracking_status: TrackingStatus
    reflection_note: str
    strategy_adjustment: str


class WeeklyCheckInCreate(WeeklyCheckInBase): ...


class WeeklyCheckInUpdate(BaseModel):
    tracking_status: TrackingStatus | None = None
    reflection_note: str | None = None
    strategy_adjustment: str | None = None


class WeeklyCheckIn(WeeklyCheckInBase):
    id: str
    created_at: int

    model_config = ConfigDict(from_attributes=True)
