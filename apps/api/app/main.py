from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .routers import auth, index, benchmark, tasks, diagnostics, manual_refresh, strategy
from .core.config import settings
import time
from typing import Dict
from collections import defaultdict
import asyncio

# Import models to ensure they're registered with SQLAlchemy
from . import models

app = FastAPI(title="Waardhaven Autoindex API", version="0.1.0")

# CORS - Secure configuration
import os

# Determine allowed origins based on environment
if os.getenv("RENDER", None):  # Running on Render
    allowed_origins = [
        "https://waardhaven-web.onrender.com",  # Production frontend
        "https://waardhaven-autoindex.onrender.com",  # Alternative domain
    ]
    # Add custom domain if configured
    if custom_domain := os.getenv("FRONTEND_URL"):
        allowed_origins.append(custom_domain)
else:  # Local development
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
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
            timestamp for timestamp in self.clients[client_ip]
            if timestamp > now - self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Record this request
        self.clients[client_ip].append(now)
        
        response = await call_next(request)
        return response

# Add rate limiting (100 requests per minute)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

@app.get("/health")
def health():
    return {"status": "ok"}

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(index.router, prefix="/api/v1/index", tags=["index"])
app.include_router(benchmark.router, prefix="/api/v1/benchmark", tags=["benchmark"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(diagnostics.router, prefix="/api/v1/diagnostics", tags=["diagnostics"])
app.include_router(manual_refresh.router, prefix="/api/v1/manual", tags=["manual"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["strategy"])
