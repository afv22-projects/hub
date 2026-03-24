from fastapi import APIRouter, Depends, HTTPException, status

from mdorm import MDorm
from hub.pantry import get_db
from hub.pantry.models import Consumable

router = APIRouter(prefix="/consumables")


@router.get("/{name}", response_model=Consumable)
def get_consumable(name: str, db: MDorm = Depends(get_db)):
    consumable = db.get_or_none(Consumable, name)
    if not consumable:
        raise HTTPException(404, f"Consumable not found (name: {name})")
    return consumable


@router.put("/{name}", status_code=status.HTTP_200_OK)
def update_consumable(name: str, consumable: Consumable, db: MDorm = Depends(get_db)):
    try:
        db.update(consumable)
    except FileNotFoundError:
        raise HTTPException(404, f"Consumable not found (name: {name})")


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumable(name: str, db: MDorm = Depends(get_db)):
    try:
        db.delete(Consumable, name)
    except FileNotFoundError:
        raise HTTPException(404, f"Consumable not found (name: {name})")


@router.get("", response_model=list[Consumable])
def get_consumables(db: MDorm = Depends(get_db)):
    return db.query(Consumable)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_consumable(consumable: Consumable, db: MDorm = Depends(get_db)):
    try:
        db.create(consumable)
    except FileExistsError:
        raise HTTPException(
            409, f"Consumable already exists (name: {consumable.title})"
        )
