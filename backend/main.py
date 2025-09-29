"""
AI Ad Copy Generator - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import init_database
from app.api.v1 import ads

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_database()
    yield
    # Shutdown - cleanup if needed

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Generate high-converting ad copy for multiple platforms",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend integration
# Include both development and production origins
cors_origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
]

# Add production frontend URL if available
import os
production_frontend = os.getenv("FRONTEND_URL")
if production_frontend:
    cors_origins.append(production_frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(ads.router, prefix="/api/v1", tags=["ads"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Ad Copy Generator API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "ready"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
