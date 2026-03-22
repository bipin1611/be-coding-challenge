import time
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.config import settings
from src.logger import get_logger
from src.routers.auth import router as auth_router

logger = get_logger(__name__)

app = FastAPI(
    title="Backend Coding Challenge",
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(auth_router)

# {ip: [timestamp, ...]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    now = time.time()
    window_start = now - settings.rate_limit_window

    timestamps = _rate_limit_store[ip]
    # Drop timestamps outside the window
    timestamps[:] = [t for t in timestamps if t > window_start]

    if len(timestamps) >= settings.rate_limit_requests:
        logger.warning("Rate limit exceeded | ip=%s", ip)
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})

    timestamps.append(now)
    return await call_next(request)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("HTTP error | method=%s path=%s status=%d detail=%s",
                   request.method, request.url.path, exc.status_code, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error | method=%s path=%s error=%s",
                 request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/health")
async def health_check():
    logger.debug("Health check requested")
    return {"status": "ok"}
