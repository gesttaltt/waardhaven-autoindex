"""
Root endpoint router for API information and health checks.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Waardhaven Autoindex API",
        "version": "0.1.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/api/v1/auth",
            "index": "/api/v1/index",
            "benchmark": "/api/v1/benchmark",
            "strategy": "/api/v1/strategy",
            "diagnostics": "/api/v1/diagnostics",
            "tasks": "/api/v1/tasks",
            "manual": "/api/v1/manual"
        }
    }

@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "api"}

@router.get("/api")
async def api_info():
    """API version information."""
    return {
        "version": "v1",
        "base_path": "/api/v1",
        "documentation": "/docs"
    }