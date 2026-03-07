from typing import Literal

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from db.reflect import DBGoal
from enums import GoalStatus
from schemas.reflect import (
    Goal,
    GoalCreate,
    GoalUpdate,
    HistoryEntry,
)

router = APIRouter(prefix="/goals")


@router.get("/{goal_id}/history", response_model=list[HistoryEntry])
def get_goal_history(goal_id: str, db: Session = Depends(get_db)):
    db_goal = db.get(DBGoal, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")

    return db_goal.get_history()


@router.get("/{goal_id}", response_model=Goal)
def get_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = db.get(DBGoal, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")
    return db_goal


@router.patch("/{goal_id}", response_model=dict)
def update_goal(goal_id: str, updates: GoalUpdate, db: Session = Depends(get_db)):
    db_goal = db.get(DBGoal, goal_id)
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
    db_goal = db.get(DBGoal, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")

    db.delete(db_goal)
    db.commit()
    return {"success": True}


@router.post("", response_model=dict)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    db_goal = DBGoal(
        title=goal.title,
        priority=goal.priority,
        exit_criteria=goal.exit_criteria,
        action_plan=goal.action_plan,
        status=GoalStatus.ACTIVE,
        month_created=goal.month_created,
    )
    db.add(db_goal)
    db.commit()
    return {"id": db_goal.id}


@router.get("", response_model=list[Goal])
def get_goals(
    status: Literal["active", "inactive"] | None = Query(None),
    sort: Literal["priority"] | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(DBGoal)

    if status == "active":
        query = query.filter(DBGoal.status == GoalStatus.ACTIVE)
    elif status == "inactive":
        query = query.filter(DBGoal.status != GoalStatus.ACTIVE)

    if sort == "priority":
        query = query.order_by(DBGoal.priority)

    return query.all()
