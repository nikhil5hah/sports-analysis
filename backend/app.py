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

# Import API routers
from backend.api import auth, sessions, points, heart_rate, sensor_data, insights, gps, spo2, temperature, activity

app = FastAPI(
    title="Squash Analytics API",
    description="Backend for squash performance analytics",
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
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


# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(points.router, prefix="/api", tags=["Points"])
app.include_router(heart_rate.router, prefix="/api", tags=["Heart Rate"])
app.include_router(sensor_data.router, prefix="/api", tags=["Sensor Data"])
app.include_router(insights.router, prefix="/api", tags=["Insights"])
app.include_router(gps.router, prefix="/api", tags=["GPS"])
app.include_router(spo2.router, prefix="/api", tags=["SpO2"])
app.include_router(temperature.router, prefix="/api", tags=["Temperature"])
app.include_router(activity.router, prefix="/api", tags=["Activity"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
