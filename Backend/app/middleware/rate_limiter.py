"""
Rate Limiter Middleware.

Uses SlowAPI to provide rate limiting for API endpoints.
Configured with limits from the environment variables.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings

# Create a rate limiter instance based on client IP
limiter = Limiter(key_func=get_remote_address)

def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return a consistent JSON response for rate limit errors."""
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "error": {
                "code": "RATE_LIMITED",
                "message": f"Rate limit exceeded: {exc.detail}"
            },
            "meta": {
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

def setup_rate_limiting(app):
    """Wire the rate limiter and custom exception handler into the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
