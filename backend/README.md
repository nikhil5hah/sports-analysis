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
│   ├── user.py
│   ├── session.py
│   ├── point.py
│   ├── heart_rate_data.py
│   ├── sensor_data.py
│   └── insight.py
├── services/                 # Business logic (reuses existing code)
│   ├── data_ingestion_service.py
│   └── insight_generator.py
├── api/                      # API routes (TODO: next step)
├── schemas/                  # Pydantic schemas (TODO)
└── workers/                  # Celery tasks (TODO)
```

## Development Workflow

### Next Steps (We'll build together):

1. **API Routes** - Create REST endpoints
   - Sessions CRUD
   - Points recording
   - Insights retrieval

2. **Background Jobs** - Celery tasks
   - Async insight generation
   - Data processing

3. **Deploy to Railway**
   - One-click deployment
   - Automatic HTTPS

## Database Schema

See `docs/data_schema_design.md` for complete schema.

**Key tables:**
- `users` - User accounts
- `sessions` - Match/training sessions
- `points` - Individual points scored
- `heart_rate_data` - Time-series HR data
- `sensor_data_batches` - Accelerometer/gyroscope (for ML)
- `insights` - Generated analytics

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

## Next: Build API Routes

Ready to add the API endpoints! Let me know and I'll create:
- `api/sessions.py` - Session CRUD
- `api/points.py` - Point recording
- `api/insights.py` - Get insights
- `schemas/` - Pydantic models for validation
