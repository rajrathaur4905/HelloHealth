"""
Structured JSON Logging Configuration.

Sets up Python's logging module to output JSON-formatted log lines.
Each log entry includes timestamp, level, message, module, and
an optional request_id for tracing requests across the system.

Usage:
    from app.core.logging_config import setup_logging
    import logging

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("User registered", extra={"user_id": "abc-123"})
"""

import json
import logging
import sys
from datetime import datetime, timezone

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON objects.

    Output example:
    {"timestamp": "2026-05-17T01:45:00Z", "level": "INFO",
     "message": "Symptom query processed", "module": "symptoms",
     "request_id": "550e8400-e29b-41d4-a716-446655440000"}
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        # Attach request_id if available (set by RequestIDMiddleware)
        request_id = getattr(record, "request_id", None)
        if request_id:
            log_data["request_id"] = request_id

        # Attach any extra fields passed via extra={...}
        for key in ("user_id", "school_id", "duration_ms", "status_code"):
            value = getattr(record, key, None)
            if value is not None:
                log_data[key] = value

        # Include exception traceback if present
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


def setup_logging() -> None:
    """Configure the root logger with JSON output to stdout."""

    # Remove any existing handlers to avoid duplicate logs
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # JSON handler writing to stdout (captured by Docker/cloud logging)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Quiet down noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
