"""
FastAPI Application Factory.

Creates and configures the FastAPI application instance with
middleware, exception handlers, and route registration.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging
from app.middleware.rate_limiter import setup_rate_limiting
from app.middleware.request_id import RequestIDMiddleware, request_id_filter
from app.routers import auth, health, history, symptoms


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Initialize structured JSON logging before anything else
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="AI-powered symptom analysis with BART zero-shot classification",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    _configure_middleware(app)
    register_exception_handlers(app)
    setup_rate_limiting(app)
    _register_routers(app)

    return app


def _configure_middleware(app: FastAPI) -> None:
    """Register all middleware on the application."""

    # Request ID — must be first so all subsequent middleware/logs have it
    app.add_middleware(RequestIDMiddleware)

    # Attach the request_id filter to root logger
    logging.getLogger().addFilter(request_id_filter)

    # CORS — origins configured from environment
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_routers(app: FastAPI) -> None:
    """Register all API routers on the application."""

    app.include_router(health.router)
    app.include_router(symptoms.router)
    app.include_router(auth.router)
    app.include_router(history.router)

    @app.get("/", tags=["root"])
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }


# Application instance — used by uvicorn
app = create_app()
