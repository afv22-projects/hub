from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from hub.db import get_db
from hub.db.pantry import DBConsumable
from hub.enums import ConsumableCategory
from hub.schemas.pantry import Consumable, ConsumableCreate, ConsumableUpdate

router = APIRouter(prefix="/consumables")


@router.get("/{id}", response_model=Consumable)
def get_consumable(id: str, db: Session = Depends(get_db)):
    db_consumable = db.get(DBConsumable, id)
    if not db_consumable:
        raise HTTPException(404, f"Consumable not found (id: {id})")
    return db_consumable


@router.patch("/{id}", response_model=Consumable)
def update_consumable(
    id: str, consumable: ConsumableUpdate, db: Session = Depends(get_db)
):
    db_consumable = db.get(DBConsumable, id)
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
def delete_consumable(id: str, db: Session = Depends(get_db)):
    db_consumable = db.get(DBConsumable, id)
    if not db_consumable:
        raise HTTPException(404, f"Consumable not found (id: {id})")

    db.delete(db_consumable)
    db.commit()


@router.get("", response_model=list[Consumable])
def get_consumables(db: Session = Depends(get_db)):
    return db.query(DBConsumable).all()


@router.post("", response_model=Consumable)
def create_consumable(consumable: ConsumableCreate, db: Session = Depends(get_db)):
    db_consumable = DBConsumable(
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


@router.put("", response_model=Consumable)
def upsert_ingredient(consumable: ConsumableCreate, db: Session = Depends(get_db)):
    consumable.name = consumable.name.lower()
    db_consumable = (
        db.query(DBConsumable).filter(DBConsumable.name == consumable.name).first()
    )

    if db_consumable:
        db_consumable.needed = consumable.needed
        if consumable.category != ConsumableCategory.OTHER:
            db_consumable.category = consumable.category
    else:
        db_consumable = DBConsumable(
            name=consumable.name,
            needed=consumable.needed,
            category=consumable.category,
        )
        db.add(db_consumable)

    db.commit()
    db.refresh(db_consumable)
    return db_consumable
