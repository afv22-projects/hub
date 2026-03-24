import os
from pathlib import Path
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

load_dotenv()

from hub.logging_config import (
    init_logging,
    get_uvicorn_log_config,
    set_request_id,
)
from hub.reflect.db import init_db as init_reflect_db
from hub.reflect.routes import app as reflect_app
from hub.pantry import init_db as init_mdorm
from hub.pantry.routes import app as pantry_app

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")
DB_URI = os.environ.get("DB_URI", "sqlite:///data/app.db")
PANTRY_MODELS_DIR = os.environ.get("PANTRY_MODELS_DIR", "data/pantry")
PANTRY_DB_URI = os.environ.get("PANTRY_DB_URI", "sqlite:///:memory:")

init_logging(LOG_LEVEL)
init_reflect_db(DB_URI)
init_mdorm(Path(PANTRY_MODELS_DIR), PANTRY_DB_URI)

app = FastAPI(title="Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = set_request_id()
    start_time = time.perf_counter()

    logger.debug(f"{request.method} {request.url.path}")

    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    log_msg = f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)"
    if response.status_code >= 500:
        logger.error(log_msg)
    elif response.status_code >= 400:
        logger.warning(log_msg)
    else:
        logger.debug(log_msg)

    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def get_root():
    return {"msg": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.mount("/reflect", reflect_app)
app.mount("/pantry-v2", pantry_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3001,
        log_config=get_uvicorn_log_config(),
        access_log=False,  # Middleware handles access logging
    )
