# Backend Architecture Design
## Squash Analytics Backend System

---

## 1. Technology Stack Recommendation

### Backend Framework: **FastAPI** (Python)
**Why:**
- ✅ Native Python → Reuse 100% of existing code
- ✅ Async support → Handle multiple uploads/sync
- ✅ Auto-generated OpenAPI docs
- ✅ Fast development, high performance
- ✅ Built-in validation (Pydantic)

**Alternative**: Flask (simpler but less modern)

### Database: **Supabase** (PostgreSQL + Real-time)
**Why:**
- ✅ PostgreSQL backend → Full SQL power
- ✅ Built-in auth, storage, real-time subscriptions
- ✅ REST + GraphQL APIs auto-generated
- ✅ Good free tier for MVP
- ✅ Easy to self-host later

**Alternative**: Railway + PostgreSQL, AWS RDS

### Storage: **Supabase Storage** or **S3**
**For:** Large FIT files, exported data

### Background Jobs: **Celery** + **Redis**
**For:** Async processing (insight generation, rally detection)

### Deployment: **Railway** or **Fly.io**
**Why:** Easy Python deployment, affordable, good DX

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Wear OS     │  Mobile App  │  Streamlit   │  Web (Future) │
│  (Watch)     │  (Phone)     │  (Analysis)  │               │
└──────┬───────┴──────┬───────┴──────┬───────┴───────┬───────┘
       │              │              │               │
       └──────────────┼──────────────┴───────────────┘
                      │
       ┌──────────────▼──────────────┐
       │     API GATEWAY (FastAPI)   │
       │  - Authentication           │
       │  - Rate limiting            │
       │  - Request validation       │
       └──────────────┬──────────────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
   ┌───▼────┐   ┌────▼─────┐   ┌───▼────┐
   │ Session│   │Ingestion │   │Insights│
   │ Service│   │ Service  │   │Service │
   └───┬────┘   └────┬─────┘   └───┬────┘
       │             │              │
       └─────────────┼──────────────┘
                     │
       ┌─────────────▼──────────────┐
       │     BACKGROUND WORKERS     │
       │  (Celery + Redis Queue)    │
       │  - Rally detection         │
       │  - Insight generation      │
       │  - Data aggregation        │
       └─────────────┬──────────────┘
                     │
       ┌─────────────▼──────────────┐
       │    DATABASE (Supabase)     │
       │  - PostgreSQL (relational) │
       │  - TimescaleDB (time-series│
       │  - JSONB (flexible schema) │
       └────────────────────────────┘
```

---

## 3. API Endpoints Design

### 3.1 Authentication

```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh-token
POST /api/auth/logout
```

**Using Supabase Auth** (recommended):
- Email/password
- OAuth (Google, Apple) - for future
- JWT tokens

### 3.2 Session Management

```python
# POST /api/sessions
# Create new session (from Wear OS or manual)
{
  "session_type": "match",  # or "training"
  "start_time": "2025-01-15T10:00:00Z",
  "metadata": {
    "watch_position": "playing_hand",
    "location": "Local Squash Club"
  }
}
# Response: { "session_id": "uuid", "upload_url": "..." }

# PUT /api/sessions/{session_id}
# Update session (end time, final score)
{
  "end_time": "2025-01-15T11:30:00Z",
  "summary": {
    "final_score": {"me": 3, "opponent": 1}
  }
}

# GET /api/sessions
# List user's sessions
# Query params: ?limit=20&offset=0&session_type=match&start_date=2025-01-01

# GET /api/sessions/{session_id}
# Get detailed session data
# Response: Full session object with summary, metrics, insights

# DELETE /api/sessions/{session_id}
# Delete session (soft delete)
```

### 3.3 Data Upload

```python
# POST /api/sessions/{session_id}/upload/fit
# Upload FIT file (from watch export or phone)
# Content-Type: multipart/form-data
# Body: file=<binary FIT data>
# Response: { "status": "processing", "job_id": "..." }

# GET /api/sessions/{session_id}/upload/status
# Check processing status
# Response: { "status": "completed", "progress": 100 }

# POST /api/sessions/{session_id}/hr-data (bulk)
# Bulk upload heart rate data
{
  "data": [
    {"timestamp": "...", "heart_rate": 145, "confidence": 0.95},
    ...
  ]
}

# POST /api/sessions/{session_id}/sensor-data (bulk)
# Bulk upload accelerometer/gyroscope data (compressed)
{
  "start_time": "...",
  "sample_rate_hz": 10,
  "accelerometer": {
    "x": [0.1, 0.2, ...],  # array of values
    "y": [...],
    "z": [...]
  },
  "gyroscope": { ... }
}
```

### 3.4 Point Tracking (Score Recording)

```python
# POST /api/sessions/{session_id}/points
# Record a point (from Wear OS button press)
{
  "timestamp": "2025-01-15T10:15:23Z",
  "winner": "me",  # or "opponent"
  "score_after": {"me": 3, "opponent": 2},
  "game_number": 1,
  "hr_at_point_end": 152.5  # optional, watch can send
}
# Response: { "point_id": "uuid", "point_number": 5 }

# GET /api/sessions/{session_id}/points
# Get all points for a session

# PUT /api/sessions/{session_id}/points/{point_id}
# Update a point (e.g., correct score)

# DELETE /api/sessions/{session_id}/points/{point_id}
# Delete a point
```

### 3.5 Insights & Analytics

```python
# GET /api/sessions/{session_id}/insights
# Get generated insights for session
# Response: GeneratedInsights object (see data_schema_design.md)

# POST /api/sessions/{session_id}/insights/regenerate
# Trigger insight regeneration (if algorithm improved)
# Response: { "job_id": "..." }

# GET /api/users/{user_id}/statistics
# Get aggregated user statistics
# Query params: ?period=monthly&start_date=2025-01-01

# GET /api/users/{user_id}/trends
# Get performance trends over time
# Response: { "performance": [...], "fitness": [...] }
```

### 3.6 Visualization Data

```python
# GET /api/sessions/{session_id}/charts/hr-over-time
# Get HR data formatted for charting
{
  "timestamps": [...],
  "heart_rates": [...],
  "zones": [...],
  "annotations": [
    {"type": "warmup", "start": "...", "end": "..."},
    {"type": "game_break", "start": "...", "end": "..."}
  ]
}

# GET /api/sessions/{session_id}/charts/zone-distribution
# Get time spent in each HR zone
{
  "zone_1": 120,  # seconds
  "zone_2": 240,
  ...
}

# GET /api/sessions/{session_id}/charts/point-by-point
# Get point-by-point breakdown with HR correlation
[
  {
    "point_number": 1,
    "winner": "me",
    "avg_hr": 145,
    "rally_duration": 23.5
  },
  ...
]
```

---

## 4. Service Layer Architecture

### 4.1 Service Structure

```python
# backend/
├── app.py                    # FastAPI app entry point
├── config.py                 # Configuration
├── models/                   # Database models (SQLAlchemy)
│   ├── user.py
│   ├── session.py
│   ├── point.py
│   ├── heart_rate_data.py
│   └── sensor_data.py
├── schemas/                  # Pydantic schemas (API validation)
│   ├── session_schemas.py
│   ├── point_schemas.py
│   └── insight_schemas.py
├── api/                      # API routes
│   ├── auth.py
│   ├── sessions.py
│   ├── points.py
│   ├── insights.py
│   └── users.py
├── services/                 # Business logic (REUSE EXISTING CODE HERE)
│   ├── data_ingestion_service.py    # Uses data_ingestion.py
│   ├── insight_generator.py         # Uses metrics_framework.py
│   ├── event_processor.py           # Uses event_detection.py
│   ├── performance_analyzer.py      # NEW: HR + Score correlation
│   └── statistics_service.py        # Aggregations
├── workers/                  # Celery tasks
│   ├── celery_app.py
│   ├── tasks.py              # Background job definitions
│   └── rally_detection_task.py
├── utils/                    # Utilities
│   ├── auth.py
│   └── database.py
└── tests/                    # Tests
    └── ...

# REUSE EXISTING MODULES (add to Python path)
# Keep these as-is, import into services
├── core/                     # ✅ NO CHANGES NEEDED
│   ├── metrics_framework.py
│   └── modular_analysis.py
├── data/                     # ✅ NO CHANGES NEEDED
│   └── ingestion/
│       └── data_ingestion.py
└── sports/                   # ✅ NO CHANGES NEEDED
    └── squash/
        └── detectors/
```

### 4.2 Example Service Implementation

```python
# backend/services/data_ingestion_service.py
from data.ingestion.data_ingestion import FitnessDataImporter
from models.session import Session
from models.heart_rate_data import HeartRateData
import pandas as pd

class DataIngestionService:
    def __init__(self, db_session):
        self.db = db_session
        self.importer = FitnessDataImporter()  # REUSE existing

    async def process_fit_upload(self, session_id: str, fit_file_path: str):
        """Process uploaded FIT file and store in database"""

        # REUSE existing import logic
        df = self.importer.import_fit_file(fit_file_path)
        df = self.importer.preprocess_data(df)

        # Store HR data in bulk
        hr_records = []
        for idx, row in df.iterrows():
            hr_records.append(HeartRateData(
                session_id=session_id,
                timestamp=row['timestamp'],
                heart_rate=row.get('heart_rate'),
                hr_zone=self._calculate_zone(row.get('heart_rate'))
            ))

        self.db.bulk_insert_mappings(HeartRateData, hr_records)

        # Store sensor data (if available)
        if 'accelerometer_x' in df.columns:
            await self._store_sensor_data(session_id, df)

        # Update session summary
        await self._update_session_summary(session_id, df)

        # Trigger background job for insight generation
        from workers.tasks import generate_insights_task
        generate_insights_task.delay(session_id)

        return {"status": "success", "data_points": len(df)}
```

```python
# backend/services/insight_generator.py
from core.metrics_framework import MetricsFramework, RallyDetector, GameDetector
from models.session import Session
from models.insight import Insight

class InsightGenerator:
    def __init__(self, db_session):
        self.db = db_session
        self.framework = MetricsFramework()
        self.framework.register_detector(RallyDetector())
        self.framework.register_detector(GameDetector())
        # ... register other detectors

    async def generate_insights(self, session_id: str):
        """Generate insights using existing metrics framework"""

        # Fetch data from database as DataFrame (format expected by framework)
        df = await self._fetch_session_dataframe(session_id)

        # REUSE existing analysis
        results = self.framework.detect_all_metrics(df)

        # Enhance with score correlation (NEW logic)
        hr_score_insights = await self._analyze_hr_vs_scores(session_id, results)

        # Store insights
        insight = Insight(
            session_id=session_id,
            metrics=self._serialize_metric_results(results),
            hr_score_correlation=hr_score_insights,
            algorithm_version="1.0"
        )
        self.db.add(insight)
        self.db.commit()

        return insight

    async def _analyze_hr_vs_scores(self, session_id: str, metric_results):
        """NEW: Correlate HR with point outcomes"""
        # Fetch points from database
        points = self.db.query(Point).filter_by(session_id=session_id).all()

        won_points_hr = []
        lost_points_hr = []

        for point in points:
            # Get HR in 5-second window before point
            hr_data = self.db.query(HeartRateData).filter(
                HeartRateData.session_id == session_id,
                HeartRateData.timestamp >= point.timestamp - timedelta(seconds=5),
                HeartRateData.timestamp <= point.timestamp
            ).all()

            avg_hr = sum(d.heart_rate for d in hr_data) / len(hr_data) if hr_data else 0

            if point.winner == 'me':
                won_points_hr.append(avg_hr)
            else:
                lost_points_hr.append(avg_hr)

        return {
            'avg_hr_on_won_points': sum(won_points_hr) / len(won_points_hr) if won_points_hr else 0,
            'avg_hr_on_lost_points': sum(lost_points_hr) / len(lost_points_hr) if lost_points_hr else 0,
            'hr_difference': (sum(won_points_hr) / len(won_points_hr) if won_points_hr else 0) -
                           (sum(lost_points_hr) / len(lost_points_hr) if lost_points_hr else 0)
        }
```

---

## 5. Background Job Processing

### 5.1 Celery Task Examples

```python
# backend/workers/tasks.py
from celery import Celery
from services.insight_generator import InsightGenerator
from services.event_processor import EventProcessor

celery_app = Celery('squash_analytics', broker='redis://localhost:6379/0')

@celery_app.task
def generate_insights_task(session_id: str):
    """Background task to generate insights after data upload"""
    generator = InsightGenerator(db_session)
    insights = generator.generate_insights(session_id)
    return {"session_id": session_id, "insights_generated": True}

@celery_app.task
def detect_rallies_task(session_id: str):
    """Background task for rally detection (computationally expensive)"""
    processor = EventProcessor(db_session)
    rallies = processor.detect_rallies(session_id)
    return {"session_id": session_id, "rallies_detected": len(rallies)}

@celery_app.task
def aggregate_user_statistics(user_id: str, period: str):
    """Nightly job to aggregate user statistics"""
    stats_service = StatisticsService(db_session)
    stats = stats_service.calculate_statistics(user_id, period)
    return stats
```

### 5.2 Job Workflow

```
1. User uploads FIT file
   ↓
2. API stores file, creates processing job
   ↓
3. Celery worker picks up job
   ↓
4. DataIngestionService processes file
   ↓
5. Triggers insight generation job
   ↓
6. InsightGenerator runs metrics framework
   ↓
7. Stores results in database
   ↓
8. Mobile app polls or receives webhook
```

---

## 6. Database Models (SQLAlchemy)

### 6.1 Core Models

```python
# backend/models/session.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Session(Base):
    __tablename__ = 'sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    session_type = Column(String(20), nullable=False)  # match/training
    sport = Column(String(50), default='squash')

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    metadata_ = Column('metadata', JSON)  # watch_position, location, etc.
    summary = Column(JSON)  # final_score, total_points, etc.
    sync_status = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    points = relationship("Point", back_populates="session")
    hr_data = relationship("HeartRateData", back_populates="session")
    insights = relationship("Insight", back_populates="session")
```

```python
# backend/models/heart_rate_data.py
from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class HeartRateData(Base):
    __tablename__ = 'heart_rate_data'

    # TimescaleDB hypertable - partitioned by time
    time = Column(DateTime(timezone=True), primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id'), primary_key=True)

    heart_rate = Column(Float, nullable=False)
    hr_zone = Column(Integer)
    confidence = Column(Float)

    # Relationships
    session = relationship("Session", back_populates="hr_data")
```

---

## 7. Authentication & Security

### 7.1 Supabase Auth Integration

```python
# backend/utils/auth.py
from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token with Supabase"""
    token = credentials.credentials

    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Usage in API routes
@app.get("/api/sessions")
async def list_sessions(user = Depends(get_current_user)):
    user_id = user.id
    # ... fetch sessions for user
```

### 7.2 Data Access Control

- **Row-Level Security**: Use Supabase RLS policies
- **User can only access their own data**
- **Admin role** for future features

---

## 8. Deployment Strategy

### Phase 1: MVP (Railway/Fly.io)

```yaml
# Railway deployment (automatic from Git)
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT"
  }
}
```

### Phase 2: Production (Docker + K8s)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy existing codebase modules
COPY core/ ./core/
COPY data/ ./data/
COPY sports/ ./sports/

# Copy backend code
COPY backend/ ./backend/

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 9. Next Steps

See next document: `wear_os_setup.md` for:
- Wear OS project structure
- Pixel Watch 3 sensor APIs
- Local storage and sync strategy
- Button press handling for score tracking
