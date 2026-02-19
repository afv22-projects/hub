import logging
import sys
import uuid
from contextvars import ContextVar
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import Record

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


FILTERED_MESSAGES = {
    "Invalid HTTP request received.",
}


class InterceptHandler(logging.Handler):
    """Intercept standard logging and route to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        msg = record.getMessage()
        if msg in FILTERED_MESSAGES:
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, msg)


def get_request_id() -> str | None:
    return request_id_ctx.get()


def set_request_id(request_id: str | None = None) -> str:
    rid = request_id or str(uuid.uuid4())[:8]
    request_id_ctx.set(rid)
    return rid


def _patcher(record: "Record") -> None:
    record["extra"]["request_id"] = get_request_id() or "-"


FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "[{extra[request_id]}] "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def init_logging(log_level: str) -> None:
    logger.remove()
    logger.configure(patcher=_patcher)

    logger.add(
        sys.stderr,
        format=FORMAT,
        level=log_level,
        colorize=True,
    )

    logger.info(f"Logging configured with level: {log_level}")


def get_uvicorn_log_config() -> dict:
    """Return uvicorn logging config that routes through loguru."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "default": {
                "()": InterceptHandler,
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
