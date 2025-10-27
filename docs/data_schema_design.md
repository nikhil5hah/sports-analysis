# Squash Analytics Data Schema Design

## Overview
Comprehensive data schema for Wear OS + Mobile + Backend + Streamlit squash analytics system.

---

## 1. Core Entities

### User
```json
{
  "user_id": "uuid",
  "email": "string",
  "name": "string",
  "created_at": "timestamp",
  "profile": {
    "max_heart_rate": "int (optional, for better zone calculation)",
    "age": "int",
    "skill_level": "string (beginner/intermediate/advanced)",
    "watch_hand": "string (left/right)"
  }
}
```

### Session (Match/Training)
```json
{
  "session_id": "uuid",
  "user_id": "uuid",
  "session_type": "string (match/training)",
  "sport": "string (squash)",
  "start_time": "timestamp",
  "end_time": "timestamp",
  "duration_seconds": "int",

  "metadata": {
    "watch_position": "string (playing_hand/non_playing_hand)",
    "location": "string (optional)",
    "opponent_id": "uuid (optional for matches)",
    "venue": "string (optional)"
  },

  "summary": {
    "final_score": {
      "me": "int",
      "opponent": "int"
    },
    "total_points": "int",
    "total_rallies": "int",
    "total_games": "int",
    "avg_hr": "float",
    "max_hr": "float",
    "calories_burned": "float (optional)"
  },

  "sync_status": {
    "watch_to_backend": "string (synced/pending/failed)",
    "last_synced_at": "timestamp"
  }
}
```

### Point (Score Event)
```json
{
  "point_id": "uuid",
  "session_id": "uuid",
  "point_number": "int (sequential within session)",
  "game_number": "int",
  "timestamp": "timestamp",

  "score_before": {
    "me": "int",
    "opponent": "int"
  },
  "score_after": {
    "me": "int",
    "opponent": "int"
  },

  "winner": "string (me/opponent)",

  "hr_at_point_end": "float",
  "rally_duration_seconds": "float (estimated or detected)",

  "notes": "string (optional - for manual annotations)"
}
```

### HeartRateData (Continuous Stream)
```json
{
  "hr_id": "uuid",
  "session_id": "uuid",
  "timestamp": "timestamp",
  "heart_rate": "float",
  "hr_zone": "int (0-5, calculated)",
  "confidence": "float (0-1, sensor confidence)"
}
```

**Storage Strategy**:
- Store as time-series (optimized for queries)
- Option 1: PostgreSQL with TimescaleDB extension
- Option 2: InfluxDB for time-series
- Option 3: Store as compressed arrays in PostgreSQL (JSON/binary)

### SensorData (Raw Background Collection)
```json
{
  "sensor_id": "uuid",
  "session_id": "uuid",
  "timestamp": "timestamp",

  "accelerometer": {
    "x": "float",
    "y": "float",
    "z": "float"
  },

  "gyroscope": {
    "x": "float",
    "y": "float",
    "z": "float"
  },

  "gps": {
    "latitude": "float (optional)",
    "longitude": "float (optional)",
    "accuracy": "float (optional)"
  }
}
```

**Storage Strategy**:
- Store in batches (not individual records)
- Compressed format (protobuf or msgpack)
- Could use S3/cloud storage for cold storage after analysis

### GeneratedInsights (HR + Score Correlation)
```json
{
  "insight_id": "uuid",
  "session_id": "uuid",
  "user_id": "uuid",
  "generated_at": "timestamp",
  "insight_type": "string (performance/recovery/momentum/trend)",

  "metrics": {
    "avg_hr_on_won_points": "float",
    "avg_hr_on_lost_points": "float",
    "hr_difference": "float",

    "optimal_hr_zone": {
      "zone": "int (3/4/5)",
      "win_percentage": "float",
      "points_in_zone": "int"
    },

    "hr_recovery_avg_seconds": "float",
    "recovery_to_target_hr": "float (e.g., 120 bpm)",

    "performance_by_game": [
      {
        "game_number": "int",
        "avg_hr": "float",
        "points_won": "int",
        "points_lost": "int",
        "fatigue_indicator": "float (0-1)"
      }
    ],

    "momentum_analysis": [
      {
        "streak_type": "string (winning/losing)",
        "streak_length": "int",
        "avg_hr_during_streak": "float",
        "hr_trend": "string (increasing/stable/decreasing)"
      }
    ]
  },

  "recommendations": [
    "string (AI-generated insights)"
  ],

  "algorithm_version": "string (for versioning insights)"
}
```

---

## 2. Aggregated Historical Data

### UserStatistics (Long-term Trends)
```json
{
  "user_id": "uuid",
  "period": "string (all_time/yearly/monthly/weekly)",
  "start_date": "date",
  "end_date": "date",

  "sessions": {
    "total_sessions": "int",
    "total_matches": "int",
    "total_training": "int",
    "total_duration_minutes": "float"
  },

  "performance": {
    "matches_won": "int",
    "matches_lost": "int",
    "win_rate": "float",
    "avg_points_per_match": "float"
  },

  "fitness": {
    "avg_hr": "float",
    "max_hr": "float",
    "avg_recovery_time_seconds": "float",
    "fitness_trend": "string (improving/stable/declining)"
  },

  "trends": {
    "performance_by_hr_zone": {
      "zone_3": {"win_rate": "float"},
      "zone_4": {"win_rate": "float"},
      "zone_5": {"win_rate": "float"}
    }
  }
}
```

---

## 3. Data Flow & Collection Strategy

### Wear OS → Local Storage (During Match)
```
Watch collects:
- HR: Continuous (1Hz)
- Score: On button press (Me/Them)
- Sensors: Background (10Hz for accel/gyro)

Storage:
- SQLite on watch (local buffer)
- Periodic sync to phone when connected
- Sync to backend when on WiFi
```

### Phone → Backend (After Match)
```
Compression:
- HR data: Downsample to 1 point per second
- Sensor data: Store in batches (10s chunks)
- Points: Individual records (small dataset)

Upload:
- Incremental sync (only new data)
- Retry logic for failed uploads
- Background sync when charging
```

### Backend → Insights Generation
```
Immediate (Real-time):
- Session summary
- Basic HR zones
- Point-by-point stats

Delayed (Batch Processing):
- Rally detection (requires full session)
- Advanced insights (HR + Score correlation)
- Historical trends (runs nightly)
```

---

## 4. Comparison with Existing Streamlit Schema

### What's Already Defined (Can Reuse)

From `core/metrics_framework.py` and `modular_analysis.py`:

```python
# Existing MetricResult - REUSE THIS
{
    'metric_name': str,
    'value': Any,
    'confidence': float,
    'metadata': Dict,
    'data_points': List[Tuple[int, int]],
    'algorithm_version': str
}

# Existing session analysis output - ADAPT THIS
{
    'session_summary': {
        'total_duration_minutes': float,
        'metrics_detected': int,
        'available_data_fields': List[str]
    },
    'metrics': Dict[str, MetricResult],
    'data_quality': Dict,
    'recommendations': List[str]
}
```

**Recommendation**:
- Use `MetricResult` as the format for `GeneratedInsights.metrics`
- Map existing metrics to new schema fields
- Keep algorithm versioning for ML improvements

---

## 5. Database Technology Recommendations

### Option 1: PostgreSQL (Recommended for MVP)
**Pros:**
- Handles all data types (relational + JSON + time-series with TimescaleDB)
- Mature ecosystem (ORMs, migrations, backups)
- JSONB for flexible schema evolution
- Can scale vertically initially

**Schema Example:**
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    session_type VARCHAR(20),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,
    metadata JSONB,
    summary JSONB,
    sync_status JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE points (
    point_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    point_number INTEGER,
    game_number INTEGER,
    timestamp TIMESTAMPTZ,
    score_before JSONB,
    score_after JSONB,
    winner VARCHAR(20),
    hr_at_point_end FLOAT,
    rally_duration_seconds FLOAT,
    notes TEXT
);

-- TimescaleDB hypertable for efficient time-series storage
CREATE TABLE heart_rate_data (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID,
    heart_rate FLOAT,
    hr_zone INTEGER,
    confidence FLOAT
);
SELECT create_hypertable('heart_rate_data', 'time');

-- Compressed storage for sensor data
CREATE TABLE sensor_data_batches (
    batch_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    sample_rate_hz FLOAT,
    data BYTEA -- msgpack compressed
);
```

### Option 2: Firebase/Firestore (Fastest to MVP)
**Pros:**
- Zero backend setup
- Real-time sync built-in
- Mobile SDKs ready
- Good for MVP

**Cons:**
- Limited complex queries
- Cost scales with reads
- Less control over data

### Option 3: Supabase (PostgreSQL + Firebase DX)
**Pros:**
- PostgreSQL backend (full SQL power)
- Firebase-like real-time APIs
- Built-in auth
- Good balance of power + ease

**Recommendation for MVP**: **Supabase** or **PostgreSQL + TimescaleDB**

---

## 6. Data Retention & Privacy

### Hot Storage (Active Analysis)
- Last 3 months: Full resolution (all sensors, 1Hz HR)
- Immediate access for mobile app

### Warm Storage (Historical)
- 3 months - 2 years: Downsampled (0.2Hz HR, no raw sensors)
- Available for trend analysis

### Cold Storage (Archive)
- 2+ years: Summary only (session metrics, no raw data)
- S3/cloud storage, can be retrieved for research

### Privacy
- User owns all data
- Export feature (GDPR compliance)
- Delete account = delete all data
- No sharing without explicit consent

---

## Next Steps

1. ✅ Schema designed
2. Choose backend tech (Supabase recommended)
3. Create database migrations
4. Build API layer (REST or GraphQL)
5. Integrate with Wear OS sync
6. Migrate existing Streamlit analysis to use backend data
