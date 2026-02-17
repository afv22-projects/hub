from fastapi import FastAPI

from .goals import router as goals_router
from .scratchpad_notes import router as scratchpad_notes_router
from .weekly_check_ins import router as weekly_check_ins_router

app = FastAPI(title="Reflect API")

app.include_router(goals_router)
app.include_router(weekly_check_ins_router)
app.include_router(scratchpad_notes_router)
