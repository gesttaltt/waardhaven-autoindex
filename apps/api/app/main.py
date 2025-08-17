from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, index, broker, benchmark, tasks, diagnostics, manual_refresh, strategy
from .core.config import settings

# Import models to ensure they're registered with SQLAlchemy
from . import models

app = FastAPI(title="Waardhaven Autoindex API", version="0.1.0")

# CORS - Configure allowed origins based on environment
import os
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
# In production, should be: https://waardhaven-web.onrender.com

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if os.getenv("NODE_ENV") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(index.router, prefix="/api/v1/index", tags=["index"])
app.include_router(benchmark.router, prefix="/api/v1/benchmark", tags=["benchmark"])
app.include_router(broker.router, prefix="/api/v1/broker", tags=["broker"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(diagnostics.router, prefix="/api/v1/diagnostics", tags=["diagnostics"])
app.include_router(manual_refresh.router, prefix="/api/v1/manual", tags=["manual"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["strategy"])
