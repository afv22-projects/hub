from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from enums import ConsumableCategory
from models.pantry import Consumable
from schemas.pantry import ConsumableCreate, ConsumableSchema, ConsumableUpdate

router = APIRouter(prefix="/consumables")


@router.get("/categories", response_model=list[str])
def get_categories():
    return [category.value for category in ConsumableCategory]


@router.get("/{id}", response_model=ConsumableSchema)
def get_consumable(id: int, db: Session = Depends(get_db)):
    db_consumable = db.get(Consumable, id)
    if not db_consumable:
        raise HTTPException(404, f"Consumable not found (id: {id})")
    return db_consumable


@router.patch("/{id}", response_model=ConsumableSchema)
def update_consumable(
    id: int, consumable: ConsumableUpdate, db: Session = Depends(get_db)
):
    db_consumable = db.get(Consumable, id)
    if not db_consumable:
        raise HTTPException(404, f"Consumable not found (id: {id})")

    if consumable.name is not None:
        db_consumable.name = consumable.name
    if consumable.needed is not None:
        db_consumable.needed = consumable.needed
    if consumable.category is not None:
        db_consumable.category = consumable.category

    try:
        db.commit()
        return db_consumable
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Consumable with name '{consumable.name}' already exists",
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumable(id: int, db: Session = Depends(get_db)):
    db_consumable = db.get(Consumable, id)
    if not db_consumable:
        raise HTTPException(404, f"Consumable not found (id: {id})")

    db.delete(db_consumable)
    db.commit()


@router.get("", response_model=list[ConsumableSchema])
def get_consumables(db: Session = Depends(get_db)):
    return db.query(Consumable).all()


@router.post("", response_model=ConsumableSchema)
def create_consumable(consumable: ConsumableCreate, db: Session = Depends(get_db)):
    db_consumable = Consumable(
        name=consumable.name,
        needed=consumable.needed,
        category=consumable.category,
    )
    db.add(db_consumable)

    try:
        db.commit()
        db.refresh(db_consumable)
        return db_consumable
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Consumable with name '{consumable.name}' already exists",
        )
