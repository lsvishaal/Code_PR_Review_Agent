"""Main FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.app.api.review import router as review_router
from src.app.core import get_logger, get_settings, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger = setup_logging()
    settings = get_settings()
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    yield
    # Shutdown
    logger.info("application_shutdown")


# Create FastAPI app
app = FastAPI(
    title="CodeReview Agent",
    description="Automated GitHub PR Review Agent with Multi-Agent LLM System",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
settings = get_settings()
if settings.enable_metrics:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(review_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CodeReview Agent API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger = get_logger(__name__)
    logger.debug("health_check_requested")
    return {
        "status": "healthy",
        "service": "pr-review-agent",
    }


@app.get("/version")
async def version():
    """Version information."""
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
    }
