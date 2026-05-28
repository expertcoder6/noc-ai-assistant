# pyrefly: ignore [missing-import]
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from .config import get_settings
from .api import query, health, intents, me, auth

logger = structlog.get_logger()

def create_app() -> FastAPI:
    settings = get_settings()
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer()
        ]
    )
    app = FastAPI(
        title="Network AI Assistant",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:80"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers under /api/v1
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(query.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(intents.router, prefix="/api/v1")
    app.include_router(me.router, prefix="/api/v1")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error("HTTPException", path=request.url.path, detail=exc.detail, status_code=exc.status_code)
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception", path=request.url.path)
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error"})

    @app.get("/404", include_in_schema=False)
    async def not_found():
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Not Found")

    return app

app = create_app()
