"""
FastAPI Application Factory.

Creates and configures the FastAPI application instance with
middleware, exception handlers, and route registration.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging_config import setup_logging
from app.middleware.request_id import RequestIDMiddleware, request_id_filter


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

    # Routers will be registered here as they are built:
    # app.include_router(health.router)      — Phase 1
    # app.include_router(symptoms.router)    — Phase 2
    # app.include_router(auth.router)        — Phase 3
    # app.include_router(history.router)     — Phase 4

    @app.get("/", tags=["root"])
    async def root():
        return {
            "name": "HelloHealth API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
        }


# Application instance — used by uvicorn
app = create_app()
