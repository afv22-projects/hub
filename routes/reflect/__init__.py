from fastapi import APIRouter

from .goals import router as goals_router
from .scratchpad_notes import router as scratchpad_notes_router
from .weekly_check_ins import router as weekly_check_ins_router

router = APIRouter(prefix="/reflect")

router.include_router(goals_router)
router.include_router(weekly_check_ins_router)
router.include_router(scratchpad_notes_router)
