from fastapi import FastAPI

from .consumables import router as consumables_router
from .ingredients import router as ingredients_router
from .recipes import router as recipes_router

app = FastAPI(title="Pantry API")

app.include_router(consumables_router)
app.include_router(recipes_router)
app.include_router(ingredients_router)
