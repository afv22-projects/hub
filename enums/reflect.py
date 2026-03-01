from enum import Enum


class GoalPriority(str, Enum):
    """Priority levels for goals."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class GoalStatus(str, Enum):
    """Status values for goals."""

    ACTIVE = "active"
    COMPLETED = "completed"
    PIVOTED = "pivoted"
    ARCHIVED = "archived"


class TrackingStatus(str, Enum):
    """Tracking status for weekly check-ins."""

    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OFF_TRACK = "off_track"


class GoalOutcome(str, Enum):
    """Outcome values for goal month outcomes."""

    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    PIVOTED = "pivoted"


class HistoryOperation(int, Enum):
    CREATE = 0
    UPDATE = 1
    DELETE = 2
