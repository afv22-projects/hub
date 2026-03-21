from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from hub.db import get_db
from hub.db.reflect import DBGoal, DBWeeklyCheckIn
from hub.enums import GoalStatus
from hub.schemas.reflect import (
    Goal,
    WeeklyCheckIn,
    WeeklyCheckInCreate,
    WeeklyCheckInUpdate,
)

router = APIRouter(prefix="/weekly-checkins")


@router.get("/{week_of}/goals", response_model=list[Goal])
def get_goals_for_week(week_of: str, db: Session = Depends(get_db)):
    active_goals_query = db.query(DBGoal).filter(DBGoal.status == GoalStatus.ACTIVE)

    goals_with_checkins_query = (
        db.query(DBGoal)
        .join(DBWeeklyCheckIn)
        .filter(DBWeeklyCheckIn.week_of == week_of)
    )

    active_goal_ids = {goal.id for goal in active_goals_query.all()}
    goals_with_checkin_ids = {goal.id for goal in goals_with_checkins_query.all()}
    all_goal_ids = active_goal_ids | goals_with_checkin_ids

    return (
        db.query(DBGoal)
        .filter(DBGoal.id.in_(all_goal_ids))
        .order_by(DBGoal.priority)
        .all()
    )


@router.patch("/{checkin_id}", response_model=dict)
def update_weekly_checkin(
    checkin_id: str, updates: WeeklyCheckInUpdate, db: Session = Depends(get_db)
):
    db_checkin = db.get(DBWeeklyCheckIn, checkin_id)
    if not db_checkin:
        raise HTTPException(404, f"Weekly check-in not found (id: {checkin_id})")

    if updates.tracking_status is not None:
        db_checkin.tracking_status = updates.tracking_status
    if updates.reflection_note is not None:
        db_checkin.reflection_note = updates.reflection_note
    if updates.strategy_adjustment is not None:
        db_checkin.strategy_adjustment = updates.strategy_adjustment

    db.commit()
    return {"updated": 1}


@router.post("", response_model=dict)
def create_weekly_checkin(checkin: WeeklyCheckInCreate, db: Session = Depends(get_db)):
    db_checkin = DBWeeklyCheckIn(
        goal_id=checkin.goal_id,
        week_of=checkin.week_of,
        tracking_status=checkin.tracking_status,
        reflection_note=checkin.reflection_note,
        strategy_adjustment=checkin.strategy_adjustment,
    )
    db.add(db_checkin)
    db.commit()
    return {"id": db_checkin.id}


@router.get("", response_model=list[WeeklyCheckIn] | None)
def get_weekly_checkins(
    goal_id: str | None = Query(None),
    week_of: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(DBWeeklyCheckIn)

    if goal_id:
        query = query.filter(DBWeeklyCheckIn.goal_id == goal_id)

    if week_of:
        query = query.filter(DBWeeklyCheckIn.week_of == week_of)

    return query.order_by(DBWeeklyCheckIn.week_of).all()
