import time
import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from enums import GoalStatus
from models.reflect import Goal as GoalModel, WeeklyCheckIn as WeeklyCheckInModel
from schemas.reflect import GoalCreate, GoalSchema, GoalUpdate

router = APIRouter(prefix="/goals")


@router.post("", response_model=dict)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    goal_id = str(uuid.uuid4())
    db_goal = GoalModel(
        id=goal_id,
        title=goal.title,
        priority=goal.priority,
        exit_criteria=goal.exit_criteria,
        action_plan=goal.action_plan,
        status=GoalStatus.ACTIVE,
        created_at=int(time.time() * 1000),  # milliseconds
        month_created=goal.month_created,
    )
    db.add(db_goal)
    db.commit()
    return {"id": goal_id}


@router.get("/{goal_id}", response_model=GoalSchema)
def get_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = db.get(GoalModel, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")
    return db_goal


@router.patch("/{goal_id}", response_model=dict)
def update_goal(goal_id: str, updates: GoalUpdate, db: Session = Depends(get_db)):
    db_goal = db.get(GoalModel, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")

    if updates.title is not None:
        db_goal.title = updates.title
    if updates.priority is not None:
        db_goal.priority = updates.priority
    if updates.exit_criteria is not None:
        db_goal.exit_criteria = updates.exit_criteria
    if updates.action_plan is not None:
        db_goal.action_plan = updates.action_plan
    if updates.status is not None:
        db_goal.status = updates.status

    db.commit()
    return {"updated": 1}


@router.delete("/{goal_id}", response_model=dict)
def delete_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = db.get(GoalModel, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")

    db.delete(db_goal)
    db.commit()
    return {"success": True}


@router.get("", response_model=list[GoalSchema])
def get_goals(
    status: Literal["active", "inactive"] | None = Query(None),
    sort: Literal["priority"] | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GoalModel)

    if status == "active":
        query = query.filter(GoalModel.status == GoalStatus.ACTIVE)
    elif status == "inactive":
        query = query.filter(GoalModel.status != GoalStatus.ACTIVE)

    if sort == "priority":
        query = query.order_by(GoalModel.priority)

    return query.all()


@router.get("/weekly-checkin/{week_of}", response_model=list[GoalSchema])
def get_goals_for_weekly_checkin(week_of: str, db: Session = Depends(get_db)):
    active_goals_query = db.query(GoalModel).filter(
        GoalModel.status == GoalStatus.ACTIVE
    )

    goals_with_checkins_query = (
        db.query(GoalModel)
        .join(WeeklyCheckInModel)
        .filter(WeeklyCheckInModel.week_of == week_of)
    )

    active_goal_ids = {goal.id for goal in active_goals_query.all()}
    goals_with_checkin_ids = {goal.id for goal in goals_with_checkins_query.all()}
    all_goal_ids = active_goal_ids | goals_with_checkin_ids

    goals = (
        db.query(GoalModel)
        .filter(GoalModel.id.in_(all_goal_ids))
        .order_by(GoalModel.priority)
        .all()
    )

    return goals
