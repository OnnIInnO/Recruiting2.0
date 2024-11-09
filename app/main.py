from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import webhooks
from app.api.routes import router, seed_router
from app.config import get_settings
from app.core.logging import setup_logging
from app.middleware.error_handling import (
    error_handler,
    validation_exception_handler,
    database_exception_handler,
)

from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    # Add any other startup logic (like initializing resources)
    yield
    # Shutdown
    # Add any cleanup logic here


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Next generation recruitment platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.middleware("http")(error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)

# Routes
app.include_router(router, prefix="/api/v1")
app.include_router(seed_router, prefix="/admin")
app.include_router(webhooks.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
    )
