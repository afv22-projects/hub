from fastapi import FastAPI, Depends

from mdorm import MDorm
from .consumables import router as consumables_router
from .groceries import router as groceries_router
from .ingredients import router as ingredients_router
from .recipes import router as recipes_router
from hub.pantry import get_db

app = FastAPI(title="Pantry API")


@app.post("/sync")
def sync(db: MDorm = Depends(get_db)):
    db.sync()


app.include_router(consumables_router)
app.include_router(groceries_router)
app.include_router(ingredients_router)
app.include_router(recipes_router)
