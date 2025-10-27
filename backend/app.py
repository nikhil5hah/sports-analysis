"""
FastAPI Application Entry Point
"""
import sys
from pathlib import Path

# Add parent directory to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.models.database import init_db

# Import API routers (we'll create these next)
# from backend.api import auth, sessions, points, insights, users

app = FastAPI(
    title="Squash Analytics API",
    description="Backend for squash performance analytics",
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Squash Analytics API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "redis": "connected"      # TODO: Add actual Redis check
    }


# Include API routers (we'll add these next)
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
# app.include_router(points.router, prefix="/api/points", tags=["Points"])
# app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
# app.include_router(users.router, prefix="/api/users", tags=["Users"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
