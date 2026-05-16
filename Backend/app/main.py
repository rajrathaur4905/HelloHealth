"""
FastAPI Application Factory.

Creates and configures the FastAPI application instance with
middleware, exception handlers, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="HelloHealth API",
        description="AI-powered symptom analysis with BART zero-shot classification",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    _configure_middleware(app)
    _register_routers(app)

    return app


def _configure_middleware(app: FastAPI) -> None:
    """Register all middleware on the application."""

    # CORS — will be configured from environment in Phase 1
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
