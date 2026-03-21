from fastapi import FastAPI

from .recipes import router as recipes_router

app = FastAPI(title="Pantry V2 API")

app.include_router(recipes_router)
