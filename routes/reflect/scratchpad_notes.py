import time
import uuid

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from db.reflect import DBScratchpadNote
from schemas.reflect import (
    ScratchpadNote,
    ScratchpadNoteCreate,
    ScratchpadNotePromote,
)

router = APIRouter(prefix="/scratchpad-notes")


@router.post("", response_model=dict)
def create_scratchpad_note(note: ScratchpadNoteCreate, db: Session = Depends(get_db)):
    note_id = str(uuid.uuid4())
    db_note = DBScratchpadNote(
        id=note_id,
        text=note.text,
        created_at=int(time.time() * 1000),  # milliseconds
        promoted_to_goal_id=None,
    )
    db.add(db_note)
    db.commit()
    return {"id": note_id}


@router.get("", response_model=list[ScratchpadNote])
def get_scratchpad_notes(
    include_promoted: bool = Query(False), db: Session = Depends(get_db)
):
    query = db.query(DBScratchpadNote)

    if not include_promoted:
        query = query.filter(DBScratchpadNote.promoted_to_goal_id.is_(None))

    return query.order_by(DBScratchpadNote.created_at.desc()).all()


@router.patch("/{note_id}/promote", response_model=dict)
def promote_scratchpad_note(
    note_id: str, promotion: ScratchpadNotePromote, db: Session = Depends(get_db)
):
    db_note = db.get(DBScratchpadNote, note_id)
    if not db_note:
        raise HTTPException(404, f"Scratchpad note not found (id: {note_id})")

    db_note.promoted_to_goal_id = promotion.goal_id
    db.commit()
    return {"updated": 1}


@router.delete("/{note_id}", response_model=dict)
def delete_scratchpad_note(note_id: str, db: Session = Depends(get_db)):
    db_note = db.get(DBScratchpadNote, note_id)
    if not db_note:
        raise HTTPException(404, f"Scratchpad note not found (id: {note_id})")

    db.delete(db_note)
    db.commit()
    return {"success": True}
