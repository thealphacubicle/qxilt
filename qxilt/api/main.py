"""FastAPI application for Qxilt."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from qxilt.api.routes_reputation import router as reputation_router
from qxilt.api.routes_reviews import router as reviews_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context - no-op for now; Supabase client is created on demand."""
    yield


async def catch_all_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log and return 500 with error detail for debugging."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


app = FastAPI(
    title="Qxilt",
    description="Reputation engine for AI agents",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(Exception, catch_all_exception_handler)
app.include_router(reviews_router)
app.include_router(reputation_router)
