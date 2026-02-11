from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models.second_thought import Justification as JustificationModel
from schemas.second_thought import (
    JustificationCreate,
    Justification as JustificationSchema,
)

router = APIRouter(prefix="/second-thought")


@router.get("/logs/", response_model=list[JustificationSchema])
def get_logs(db: Session = Depends(get_db)):
    return db.query(JustificationModel).all()


@router.post("/log/")
def post_log(justification: JustificationCreate, db: Session = Depends(get_db)):
    db_justification = JustificationModel(
        ts=datetime.now(),
        domain=justification.domain,
        url=justification.url,
        reason=justification.reason,
        duration=justification.duration,
    )
    db.add(db_justification)
    db.commit()
