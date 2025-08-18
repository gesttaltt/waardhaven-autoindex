from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .routers import (
    root,
    auth,
    index,
    benchmark,
    tasks,
    diagnostics,
    manual_refresh,
    strategy,
    background,
    news,
)
from .core.config import settings
import time
from typing import Dict
from collections import defaultdict
import logging
import os

# Import models to ensure they're registered with SQLAlchemy

logger = logging.getLogger(__name__)
app = FastAPI(title="Waardhaven Autoindex API", version="0.1.0")


# Run migrations on startup
@app.on_event("startup")
async def startup_event():
    """Run database migrations and other startup tasks."""
    try:
        from .utils.run_migrations import run_all_migrations

        logger.info("Running database migrations on startup...")
        if run_all_migrations():
            logger.info("Database migrations completed successfully")
        else:
            logger.warning("Some database migrations failed - check logs")
    except Exception as e:
        logger.error(f"Failed to run startup migrations: {e}")
        # Don't fail startup on migration errors in production
        if settings.DEBUG:
            raise


# CORS - Secure configuration
# Determine allowed origins based on environment
if os.getenv("RENDER", None):  # Running on Render
    allowed_origins = [
        "https://waardhaven-web-frontend.onrender.com",  # Actual production frontend URL
        "https://www.waardhaven-web-frontend.onrender.com",  # www variant
        "https://waardhaven-web.onrender.com",  # Legacy URL (keep for compatibility)
        "https://waardhaven-autoindex.onrender.com",  # Alternative domain
    ]
    # Add custom domain if configured
    if custom_domain := os.getenv("FRONTEND_URL"):
        allowed_origins.append(custom_domain)
        # Also add www variant of custom domain
        if not custom_domain.startswith("www."):
            allowed_origins.append(custom_domain.replace("https://", "https://www."))
else:  # Local development
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Only add HSTS in production
        if os.getenv("RENDER"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


app.add_middleware(SecurityHeadersMiddleware)


# Simple Rate Limiting
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host

        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)

        now = time.time()

        # Clean old entries
        self.clients[client_ip] = [
            timestamp
            for timestamp in self.clients[client_ip]
            if timestamp > now - self.period
        ]

        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        # Record this request
        self.clients[client_ip].append(now)

        response = await call_next(request)
        return response


# Add rate limiting (100 requests per minute)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# CORS Debug Middleware (only in debug mode or when CORS_DEBUG is set)
if settings.DEBUG or os.getenv("CORS_DEBUG"):

    @app.middleware("http")
    async def cors_debug_middleware(request: Request, call_next):
        """Log CORS-related information for debugging"""
        origin = request.headers.get("origin")
        if origin:
            logger.info(f"CORS Debug - Request from origin: {origin}")
            logger.info(f"CORS Debug - Method: {request.method}")
            logger.info(f"CORS Debug - Path: {request.url.path}")
            logger.info(f"CORS Debug - Allowed origins: {allowed_origins}")

        response = await call_next(request)

        # Log response CORS headers
        if origin:
            cors_header = response.headers.get("access-control-allow-origin")
            logger.info(f"CORS Debug - Response Allow-Origin: {cors_header}")

        return response


# Routers
app.include_router(root.router, tags=["root"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(index.router, prefix="/api/v1/index", tags=["index"])
app.include_router(benchmark.router, prefix="/api/v1/benchmark", tags=["benchmark"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(
    diagnostics.router, prefix="/api/v1/diagnostics", tags=["diagnostics"]
)
app.include_router(manual_refresh.router, prefix="/api/v1/manual", tags=["manual"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["strategy"])
app.include_router(background.router, prefix="/api/v1/background", tags=["background"])
app.include_router(news.router, prefix="/api/v1", tags=["news"])
