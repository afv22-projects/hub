from fastapi import FastAPI

from .consumables import router as consumables_router
from .ingredients import router as ingredients_router
from .recipes import router as recipes_router
from .mcp.recipes import mcp as recipes_mcp

mcp_app = recipes_mcp.http_app(path="/mcp")

app = FastAPI(title="Pantry V2 API")

app.include_router(consumables_router)
app.include_router(ingredients_router)
app.include_router(recipes_router)

app.mount("/", mcp_app)
