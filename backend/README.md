# Squash Analytics Backend

FastAPI backend for squash performance analytics.

## Architecture

**Reuses existing code:**
- `core/metrics_framework.py` - All detectors (rally, game, warmup, etc.)
- `data/ingestion/data_ingestion.py` - FIT file parsing
- `sports/squash/detectors/` - Event detection

**New components:**
- FastAPI REST API
- PostgreSQL database (via Supabase)
- Celery background jobs
- HR + Score correlation analytics

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Supabase

1. Go to https://supabase.com and create a new project
2. Get your credentials:
   - Project URL: `https://xxx.supabase.co`
   - Anon key: Public API key
   - Service key: Secret service role key

3. Create `.env` file:

```bash
cp .env.example .env
# Edit .env and add your Supabase credentials
```

### 3. Run Database Migrations

The database tables will be created automatically on first run.

### 4. Start the Server

```bash
python app.py
```

Or with uvicorn:

```bash
uvicorn app:app --reload --port 8000
```

Server will start at: http://localhost:8000

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# You should see:
# {"status": "healthy", "database": "connected", "redis": "connected"}
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app.py                    # FastAPI entry point
├── config.py                 # Configuration
├── models/                   # Database models (SQLAlchemy)
│   ├── database.py          # Database connection
│   ├── user.py
│   ├── session.py
│   ├── point.py
│   ├── heart_rate_data.py
│   ├── gps_data.py          # ✅ NEW
│   ├── spo2_data.py         # ✅ NEW
│   ├── temperature_data.py  # ✅ NEW
│   ├── activity_data.py     # ✅ NEW
│   ├── sensor_data.py
│   └── insight.py
├── api/                      # API routes ✅ COMPLETE
│   ├── dependencies.py      # JWT auth dependency
│   ├── schemas.py           # Pydantic validation schemas
│   ├── auth.py              # Authentication endpoints
│   ├── sessions.py          # Session CRUD
│   ├── points.py            # Point recording
│   ├── heart_rate.py        # Heart rate upload
│   ├── gps.py               # GPS/location upload
│   ├── spo2.py              # SpO2 upload
│   ├── temperature.py       # Temperature upload
│   ├── activity.py          # Activity metrics upload
│   ├── sensor_data.py       # Sensor batch upload
│   └── insights.py          # Insights generation
├── services/                 # Business logic (reuses existing code)
│   ├── data_ingestion_service.py
│   └── insight_generator.py
└── workers/                  # Celery tasks (future)
```

## Development Workflow

### ✅ Completed Features:

1. **API Routes** - All REST endpoints implemented
   - ✅ Authentication (register, login, JWT)
   - ✅ Sessions CRUD
   - ✅ Points recording
   - ✅ Heart rate data upload
   - ✅ GPS/location data upload
   - ✅ SpO2 data upload
   - ✅ Temperature data upload
   - ✅ Activity metrics upload
   - ✅ Sensor data batches (accelerometer/gyroscope)
   - ✅ Insights generation and retrieval

2. **Next Phase** - Mobile App Development
   - Build iOS/Android app
   - Integrate smartwatch APIs
   - Real-time data streaming

3. **Future Enhancements**
   - Background job processing (Celery)
   - Deploy to Railway/Render
   - Advanced analytics and ML models

## Database Schema

See `docs/data_schema_design.md` for complete schema.

**Key tables:**
- `users` - User accounts
- `sessions` - Match/training sessions
- `points` - Individual points scored
- `heart_rate_data` - Time-series HR data
- `gps_data` - GPS/location tracking (lat/long, altitude, speed, bearing)
- `spo2_data` - Blood oxygen saturation readings
- `temperature_data` - Skin temperature measurements
- `activity_data` - Activity metrics (steps, calories, distance, floors)
- `sensor_data_batches` - Accelerometer/gyroscope (for ML)
- `insights` - Generated analytics

**Time-series data pattern:**
All sensor data tables use composite primary keys `(time, session_id)` for efficient querying and storage of high-frequency sensor readings.

## Environment Variables

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Database (alternative to Supabase)
DATABASE_URL=postgresql://user:pass@localhost/squash_analytics

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32

# CORS (for mobile app)
CORS_ORIGINS=http://localhost:3000,http://localhost:19006
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Deployment

### Railway (Recommended for MVP)

1. Create Railway account: https://railway.app
2. Connect GitHub repo
3. Add environment variables in Railway dashboard
4. Deploy!

Railway will automatically:
- Detect Python app
- Install dependencies
- Run database migrations
- Provide HTTPS URL

### Alternative: Fly.io, Render, Heroku

All work similarly. See deployment docs.

## Status

✅ **Backend API is complete and operational!**

All endpoints are implemented and tested. Server runs at `http://localhost:8000` with interactive API docs at `/docs`.

**Next Phase:** Build mobile app (iOS/Android) with smartwatch integration. See `../docs/MOBILE_APP_PLAN.md` for implementation guide.
