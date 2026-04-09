from fastapi import FastAPI

from .consumables import router as consumables_router
from .groceries import router as groceries_router
from .ingredients import router as ingredients_router
from .recipes import router as recipes_router
from .mcp import app as mcp_app

app = FastAPI(title="Pantry API")

app.include_router(consumables_router)
app.include_router(groceries_router)
app.include_router(ingredients_router)
app.include_router(recipes_router)

app.mount("/", mcp_app)
