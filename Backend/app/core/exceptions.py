"""
Custom Exception Classes and Global Handlers.

Defines a hierarchy of application-specific exceptions and FastAPI
exception handlers that return consistent, structured error responses
with request_id for tracing.

Exception Hierarchy:
    AppException (base)
    ├── NotFoundError        (404)
    ├── ValidationError      (400)
    ├── AuthenticationError  (401)
    ├── AuthorizationError   (403)
    ├── ConflictError        (409)
    ├── RateLimitError       (429)
    └── ClassifierError      (503)
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ── Base Exception ───────────────────────────────────────────

class AppException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: dict | list | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


# ── Specific Exceptions ─────────────────────────────────────

class NotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str, identifier: str | None = None):
        msg = f"{resource} not found" if not identifier else f"{resource} '{identifier}' not found"
        super().__init__(message=msg, code="NOT_FOUND", status_code=404)


class ValidationError(AppException):
    """Client sent invalid data (400)."""

    def __init__(self, message: str, details: dict | list | None = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=400, details=details)


class AuthenticationError(AppException):
    """Not authenticated or invalid credentials (401)."""

    def __init__(self, message: str = "Invalid or missing credentials"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR", status_code=401)


class AuthorizationError(AppException):
    """Authenticated but insufficient permissions (403)."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="AUTHORIZATION_ERROR", status_code=403)


class ConflictError(AppException):
    """Resource already exists or state conflict (409)."""

    def __init__(self, message: str):
        super().__init__(message=message, code="CONFLICT", status_code=409)


class RateLimitError(AppException):
    """Too many requests (429)."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message=message, code="RATE_LIMITED", status_code=429)


class ClassifierError(AppException):
    """AI model inference failed (503)."""

    def __init__(self, message: str = "Symptom classification service unavailable"):
        super().__init__(message=message, code="CLASSIFIER_ERROR", status_code=503)


# ── Exception Handlers ──────────────────────────────────────

def _build_error_response(request: Request, exc: AppException) -> JSONResponse:
    """Build a consistent error response with request tracing."""
    request_id = getattr(request.state, "request_id", None)

    body = {
        "status": "error",
        "error": {
            "code": exc.code,
            "message": exc.message,
        },
        "meta": {
            "request_id": request_id,
        },
    }

    if exc.details:
        body["error"]["details"] = exc.details

    return JSONResponse(status_code=exc.status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "AppException: %s (code=%s, status=%d)",
            exc.message,
            exc.code,
            exc.status_code,
        )
        return _build_error_response(request, exc)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error("Unhandled exception: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
                "meta": {
                    "request_id": request_id,
                },
            },
        )
