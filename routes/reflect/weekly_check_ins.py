import time
import uuid

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from db.reflect import DBWeeklyCheckIn
from schemas.reflect import (
    WeeklyCheckIn,
    WeeklyCheckInCreate,
    WeeklyCheckInUpdate,
)

router = APIRouter(prefix="/weekly-checkins")


@router.post("", response_model=dict)
def create_weekly_checkin(checkin: WeeklyCheckInCreate, db: Session = Depends(get_db)):
    checkin_id = str(uuid.uuid4())
    db_checkin = DBWeeklyCheckIn(
        id=checkin_id,
        goal_id=checkin.goal_id,
        week_of=checkin.week_of,
        tracking_status=checkin.tracking_status,
        reflection_note=checkin.reflection_note,
        strategy_adjustment=checkin.strategy_adjustment,
        created_at=int(time.time() * 1000),  # milliseconds
    )
    db.add(db_checkin)
    db.commit()
    return {"id": checkin_id}


@router.get("", response_model=list[WeeklyCheckIn] | WeeklyCheckIn | None)
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

    if goal_id and week_of:
        return query.first()

    return query.order_by(DBWeeklyCheckIn.week_of).all()


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
