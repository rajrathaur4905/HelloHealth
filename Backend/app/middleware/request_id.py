"""
Request ID Middleware.

Assigns a unique UUID to every incoming HTTP request and attaches it to:
  1. request.state.request_id  — accessible in route handlers
  2. X-Request-ID response header — returned to the client
  3. Log context — via a logging filter for automatic inclusion

This enables end-to-end request tracing: a client can send a request,
receive the X-Request-ID header, and use it to find all related logs.
"""

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDFilter(logging.Filter):
    """Logging filter that injects request_id into every log record.

    When no request is active, request_id defaults to None.
    """

    _current_request_id: str | None = None

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = self._current_request_id  # type: ignore[attr-defined]
        return True


# Singleton filter instance — shared across the middleware and logger
request_id_filter = RequestIDFilter()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a UUID to each request for tracing."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Use client-provided ID if present, otherwise generate one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Make it available to route handlers via request.state
        request.state.request_id = request_id

        # Make it available to all loggers via the shared filter
        request_id_filter._current_request_id = request_id

        # Process the request
        response = await call_next(request)

        # Echo the ID back to the client in response headers
        response.headers["X-Request-ID"] = request_id

        # Clear the filter after request completes
        request_id_filter._current_request_id = None

        return response
