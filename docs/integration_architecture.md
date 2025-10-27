# Integration Architecture
## Complete System Integration for Squash Analytics Platform

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         COMPLETE SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Pixel Watch │────────▶│  Mobile App  │────────▶│   Backend    │
│   (Wear OS)  │  BLE/   │   (Phone)    │  HTTPS  │ (FastAPI +   │
│              │  WiFi   │              │         │  Supabase)   │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                         │
       │ During match:          │ Post-match:            │ Analysis:
       │ - HR monitoring        │ - View history         │ - Insight gen
       │ - Score tracking       │ - Charts               │ - Rally detect
       │ - Sensor collection    │ - Sync trigger         │ - HR correlation
       │                        │                         │
       └────────────────────────┴─────────────────────────┘
                                 │
                    ┌────────────▼───────────┐
                    │   Streamlit Dashboard  │
                    │   (Deep Analysis)      │
                    └────────────────────────┘
```

---

## 2. Data Flow Scenarios

### 2.1 Scenario: Start New Match

```
1. USER: Opens Wear OS app, taps "Start Match"
   ↓
2. WEAR OS:
   - Creates session (UUID, start time)
   - Stores in local SQLite
   - Starts HR monitoring service (continuous)
   - Starts sensor collection service (background, 10Hz)
   - Displays match UI
   ↓
3. WATCH SCREEN SHOWS:
   - Current HR: 132 bpm (Zone 4 - Hard)
   - Score: 0 - 0 (Game 1)
   - Buttons: [Me] [Them]
   - Timer: 0:00
   ↓
4. USER PLAYS: Every second, watch stores:
   - HR data point → local DB
   - Sensor data (batched every 10 seconds) → local DB
   ↓
5. USER: Taps "Me" button after winning a point
   ↓
6. WEAR OS:
   - Records point in local DB:
     * timestamp, winner="me", score_after=(1,0), hr_at_point_end=145
   - Updates UI: Score: 1 - 0
   - Vibrates briefly (haptic feedback)
   ↓
7. MATCH CONTINUES...
   ↓
8. USER: Taps "End Match" after final point
   ↓
9. WEAR OS:
   - Stops HR/sensor collection
   - Updates session end_time, final_score
   - Marks session sync_status = "pending"
   - Shows summary: "Match saved. Sync when connected."
   ↓
10. WATCH: Attempts sync when WiFi/phone connected
    - Checks if phone companion app is available
    - If yes → transfers data to phone
    - If no → waits for next sync opportunity
```

### 2.2 Scenario: Sync to Backend

```
TRIGGER: Watch connects to phone (BLE/WiFi)

1. WEAR OS Sync Service:
   - Queries local DB for pending sessions
   - Compresses HR data (downsample to 1Hz if needed)
   - Compresses sensor data (msgpack format)
   - Packages as FIT file OR JSON payload
   ↓
2. TRANSFER TO PHONE:
   - Via Wear Data Layer API (BLE/WiFi)
   - Transfer: ~5-10 MB per 1-hour session
   - Progress shown on watch: "Syncing 45%..."
   ↓
3. PHONE RECEIVES:
   - Mobile app background service receives data
   - Stores temporarily in phone storage
   - Displays notification: "New match ready to sync"
   ↓
4. PHONE → BACKEND (when WiFi available):
   POST /api/sessions/{session_id}/upload/fit
   - Uploads FIT file or JSON data
   - Backend responds: {"status": "processing", "job_id": "..."}
   ↓
5. BACKEND PROCESSING:
   - DataIngestionService: Parses FIT file, extracts HR/sensor data
   - Stores in PostgreSQL (sessions, points, hr_data, sensor_data tables)
   - Triggers Celery job: generate_insights_task(session_id)
   ↓
6. BACKGROUND INSIGHT GENERATION:
   - InsightGenerator: Runs metrics framework (rally detection, etc.)
   - PerformanceAnalyzer: Correlates HR with point outcomes
   - Stores insights in DB
   - Updates session.sync_status = "analyzed"
   ↓
7. MOBILE APP POLLS:
   GET /api/sessions/{session_id}/insights
   - Receives insights when ready
   - Shows notification: "Match analysis ready!"
   - User opens app to view insights
```

### 2.3 Scenario: View Insights on Mobile

```
1. USER: Opens mobile app
   ↓
2. MOBILE APP:
   GET /api/sessions?limit=20
   - Fetches recent sessions
   - Displays list: "Match vs John - Jan 15 (3-1 Win)"
   ↓
3. USER: Taps on session
   ↓
4. MOBILE APP FETCHES:
   GET /api/sessions/{session_id}
   GET /api/sessions/{session_id}/insights
   GET /api/sessions/{session_id}/charts/hr-over-time
   GET /api/sessions/{session_id}/charts/point-by-point
   ↓
5. SCREEN DISPLAYS:
   ┌─────────────────────────────────────┐
   │ Match vs John - Jan 15              │
   │ Final Score: 3 - 1                  │
   │ Duration: 82 minutes                │
   ├─────────────────────────────────────┤
   │ 📊 KEY INSIGHTS                     │
   │                                     │
   │ ✓ Won points at avg HR: 152 bpm    │
   │ ✗ Lost points at avg HR: 158 bpm   │
   │ → You perform better when HR is    │
   │   in Zone 4 (145-155 bpm)          │
   │                                     │
   │ ✓ HR recovery: 18 bpm/min (Good)   │
   │ ✗ Game 4 fatigue detected          │
   │   (HR +12 bpm vs Game 1)           │
   ├─────────────────────────────────────┤
   │ 📈 CHARTS                           │
   │ [HR Over Time Graph]                │
   │ [Point-by-Point Breakdown]          │
   │ [HR Zone Distribution Pie Chart]    │
   └─────────────────────────────────────┘
   ↓
6. USER: Taps "Detailed Analysis"
   ↓
7. MOBILE APP: Opens Streamlit deep-link
   → https://your-streamlit-app.com/?session={session_id}
   ↓
8. STREAMLIT DASHBOARD:
   - Fetches full session data from backend
   - Displays advanced visualizations
   - Shows rally-by-rally breakdown
   - Comparison with historical sessions
```

---

## 3. Tech Stack Summary

### 3.1 Wear OS (Pixel Watch 3)
```
Language: Kotlin
UI: Jetpack Compose for Wear OS
Database: Room (SQLite)
Services:
  - Health Services API (HR monitoring)
  - Sensor Manager (accelerometer, gyroscope)
  - Work Manager (background sync)
Key Libraries:
  - androidx.health:health-services-client
  - androidx.room:room-ktx
  - androidx.work:work-runtime-ktx
```

### 3.2 Mobile App (Companion)
```
Option 1: React Native (recommended for cross-platform)
  - Pros: Single codebase for iOS + Android
  - Cons: Wear OS sync requires native modules

Option 2: Native Android (Kotlin)
  - Pros: Best Wear OS integration
  - Cons: iOS requires separate Swift app

Option 3: Flutter
  - Pros: Beautiful UI, single codebase
  - Cons: Limited Wear OS libraries

RECOMMENDATION: React Native + native module for Wear sync
```

### 3.3 Backend
```
Framework: FastAPI (Python)
Database: Supabase (PostgreSQL + TimescaleDB)
Storage: Supabase Storage / S3
Background Jobs: Celery + Redis
Auth: Supabase Auth (JWT)
Hosting: Railway / Fly.io (MVP), AWS/GCP (production)
```

### 3.4 Streamlit Dashboard
```
Current: Python + Streamlit
Keep for: Deep analysis, power users
Access: Web link from mobile app
Reuses: ALL existing analysis code (core/, data/, sports/)
```

---

## 4. API Communication Patterns

### 4.1 REST API Endpoints (FastAPI)

```python
# Authentication
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh-token

# Sessions
POST   /api/sessions                    # Create new session
GET    /api/sessions                    # List sessions (paginated)
GET    /api/sessions/{id}               # Get session details
PUT    /api/sessions/{id}               # Update session
DELETE /api/sessions/{id}               # Delete session

# Data Upload
POST   /api/sessions/{id}/upload/fit    # Upload FIT file
POST   /api/sessions/{id}/hr-data       # Bulk HR data
POST   /api/sessions/{id}/sensor-data   # Bulk sensor data

# Points
POST   /api/sessions/{id}/points        # Record point
GET    /api/sessions/{id}/points        # List points
PUT    /api/sessions/{id}/points/{pid}  # Update point
DELETE /api/sessions/{id}/points/{pid}  # Delete point

# Insights & Analytics
GET    /api/sessions/{id}/insights      # Get insights
POST   /api/sessions/{id}/insights/regenerate

# Charts (Optimized for mobile rendering)
GET    /api/sessions/{id}/charts/hr-over-time
GET    /api/sessions/{id}/charts/zone-distribution
GET    /api/sessions/{id}/charts/point-by-point

# User Statistics
GET    /api/users/{uid}/statistics      # Aggregated stats
GET    /api/users/{uid}/trends          # Performance trends
```

### 4.2 Real-time Updates (Optional - Phase 2)

```python
# WebSocket for live match tracking
WS     /ws/sessions/{id}/live

# Mobile app can show live updates during match
# - Real-time HR monitoring
# - Live score updates
# - Watch connection status
```

---

## 5. Data Synchronization Strategy

### 5.1 Sync Priorities

**Priority 1: Critical Match Data**
- Points scored (timestamp, winner, score)
- Session metadata (start/end time, final score)
- Size: ~1 KB per match
- Upload: Immediately when WiFi available

**Priority 2: Heart Rate Data**
- 1 Hz downsampled (from original 1Hz continuous)
- Size: ~70 KB per hour
- Upload: Within 24 hours

**Priority 3: Sensor Data**
- 10 Hz accelerometer/gyroscope
- Size: ~5-8 MB per hour (compressed)
- Upload: When charging + WiFi
- Purpose: Future ML training

### 5.2 Conflict Resolution

```
Scenario: User manually edits score on mobile app
         But watch has different score stored locally

Resolution Strategy:
1. Backend is source of truth
2. Watch syncs → backend validates
3. If conflict detected:
   - Show user both versions
   - Let user choose correct one
   - Store conflict resolution preference
```

### 5.3 Offline Support

**Watch (Always Offline-First)**
- Store everything locally
- Show "pending sync" indicator
- Retry sync every 15 minutes when connected

**Mobile App**
- Cache last 30 days of sessions
- Allow viewing cached sessions offline
- Show "Last synced: 2 hours ago"

**Backend**
- Idempotent API endpoints (can replay requests)
- Deduplicate data by timestamp + session_id

---

## 6. HR + Score Correlation Logic

### 6.1 Key Insights to Generate

```python
# backend/services/performance_analyzer.py

class PerformanceAnalyzer:
    def generate_insights(self, session_id: str) -> Dict:
        """
        Generate HR + Score insights
        Answers questions like:
        - What HR zone do I perform best in?
        - Do I lose points when HR is too high?
        - How does fatigue affect performance?
        """

        insights = {}

        # 1. Avg HR on Won vs Lost Points
        insights['hr_by_outcome'] = self._analyze_hr_by_outcome(session_id)
        # Result: "Won points: 152 bpm, Lost points: 158 bpm"
        # Insight: "You win more points when HR is 145-155 bpm (Zone 4)"

        # 2. Optimal HR Zone
        insights['optimal_zone'] = self._find_optimal_zone(session_id)
        # Result: Zone 4 = 65% win rate, Zone 5 = 45% win rate
        # Insight: "Stay in Zone 4 for best performance"

        # 3. HR Recovery Between Points
        insights['recovery'] = self._analyze_recovery(session_id)
        # Result: "Avg recovery: 18 bpm/min"
        # Insight: "Good recovery rate. You're fit!"

        # 4. Performance by Game (Fatigue Analysis)
        insights['fatigue'] = self._analyze_fatigue(session_id)
        # Result: Game 1 avg HR = 148, Game 4 avg HR = 160
        # Insight: "Performance declined in Game 4 due to fatigue"

        # 5. Momentum Analysis
        insights['momentum'] = self._analyze_momentum(session_id)
        # Result: During 5-point winning streak, HR increased from 145→158
        # Insight: "Your HR rises when building momentum"

        return insights
```

### 6.2 Example Insight Calculation

```python
def _analyze_hr_by_outcome(self, session_id: str) -> Dict:
    """Calculate average HR during won vs lost points"""

    # Fetch all points for this session
    points = db.query(Point).filter_by(session_id=session_id).all()

    won_hrs = []
    lost_hrs = []

    for point in points:
        # Get HR data in 5-second window before point
        hr_window = db.query(HeartRateData).filter(
            HeartRateData.session_id == session_id,
            HeartRateData.timestamp >= point.timestamp - timedelta(seconds=5),
            HeartRateData.timestamp <= point.timestamp
        ).all()

        if not hr_window:
            continue

        avg_hr = sum(d.heart_rate for d in hr_window) / len(hr_window)

        if point.winner == 'me':
            won_hrs.append(avg_hr)
        else:
            lost_hrs.append(avg_hr)

    return {
        'avg_hr_won': np.mean(won_hrs) if won_hrs else 0,
        'avg_hr_lost': np.mean(lost_hrs) if lost_hrs else 0,
        'difference': np.mean(won_hrs) - np.mean(lost_hrs) if won_hrs and lost_hrs else 0,
        'sample_size': {'won': len(won_hrs), 'lost': len(lost_hrs)}
    }
```

---

## 7. Deployment & DevOps

### 7.1 Development Environment

```yaml
# docker-compose.yml (for local development)
version: '3.8'
services:
  postgres:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: squash_analytics
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn app:app --reload --host 0.0.0.0
    volumes:
      - ./backend:/app
      - ./core:/app/core      # Mount existing code
      - ./data:/app/data
      - ./sports:/app/sports
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  celery_worker:
    build: ./backend
    command: celery -A workers.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
      - ./core:/app/core
      - ./data:/app/data
      - ./sports:/app/sports
    depends_on:
      - postgres
      - redis

  streamlit:
    build: ./frontend/streamlit
    command: streamlit run app.py
    volumes:
      - ./frontend/streamlit:/app
    ports:
      - "8501:8501"
```

### 7.2 Production Deployment

```
┌──────────────────────────────────────────┐
│  WEAR OS APP                             │
│  - Google Play Store (production)        │
│  - Internal testing (beta)               │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  MOBILE APP                              │
│  - iOS: TestFlight → App Store          │
│  - Android: Play Store Internal Track    │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  BACKEND (Railway/Fly.io)                │
│  - FastAPI (uvicorn)                     │
│  - Celery workers (separate service)    │
│  - Redis (managed)                       │
│  - Monitoring: Sentry                    │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  DATABASE (Supabase)                     │
│  - PostgreSQL + TimescaleDB              │
│  - Automatic backups                     │
│  - Row-level security                    │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  STREAMLIT (Streamlit Cloud)             │
│  - Deployed from GitHub                  │
│  - Auto-deploys on push to main          │
└──────────────────────────────────────────┘
```

---

## 8. Phased Implementation Plan

### Phase 1: MVP (4-6 weeks)
**Goal**: Basic working system

✅ **Week 1-2: Backend Setup**
- Set up Supabase database
- Create FastAPI backend
- Implement session + point endpoints
- Deploy to Railway

✅ **Week 3-4: Wear OS App**
- Create basic Wear OS project
- Implement HR monitoring
- Add score buttons (Me/Them)
- Local storage (SQLite)

✅ **Week 5-6: Mobile App**
- Create React Native app
- List sessions
- Display basic metrics
- Trigger sync from watch

**Milestone**: User can record a match on watch, sync to phone, view on mobile

---

### Phase 2: Insights (2-3 weeks)
**Goal**: Generate HR + Score insights

✅ **Week 7-8: Insight Generation**
- Migrate existing metrics framework to backend
- Implement HR + Score correlation
- Create insight endpoints
- Display insights in mobile app

✅ **Week 9: Mobile UI Polish**
- Add charts (HR over time, zone distribution)
- Point-by-point breakdown
- Session comparison

**Milestone**: User gets meaningful insights after each match

---

### Phase 3: Advanced Features (3-4 weeks)
**Goal**: Rich analytics and ML preparation

✅ **Week 10-11: Sensor Data Collection**
- Background sensor collection on watch
- Compress and upload to backend
- Store for future ML training

✅ **Week 12: Historical Trends**
- Aggregate user statistics
- Performance trends over time
- Progress tracking

✅ **Week 13: Streamlit Integration**
- Link from mobile app to Streamlit
- Deep-dive analysis
- Session comparison tool

**Milestone**: Complete end-to-end system with advanced analytics

---

### Phase 4: ML & Optimization (Ongoing)
**Goal**: After 50-100 sessions collected

✅ **ML Pipeline**
- Train rally detection model (sensor data)
- Train shot detection model
- Improve insight algorithms

✅ **Optimizations**
- Real-time match tracking (WebSocket)
- Voice commands on watch
- Social features (share matches)

---

## 9. Success Metrics

### Technical Metrics
- ✓ Sync success rate: >95%
- ✓ Insight generation time: <30 seconds
- ✓ Mobile app crash rate: <1%
- ✓ API response time: <200ms (p95)

### User Metrics
- ✓ Sessions per user per week: >2
- ✓ Insight views per session: >80%
- ✓ User retention (30-day): >60%

---

## 10. Next Steps for You

### Immediate Actions:
1. **Review all documents** (data_schema, component_mapping, backend_architecture, wear_os_setup, this doc)
2. **Choose tech stack** (confirm choices or adjust)
3. **Set up development environment**:
   - Create Supabase project
   - Set up Railway account
   - Install Android Studio

### Development Path:
1. Start with **Backend** (Week 1-2)
   - Fastest to get working
   - Reuses 100% of existing Python code
   - Can test with Postman/curl

2. Then **Wear OS** (Week 3-4)
   - Core functionality
   - Most unique/valuable part

3. Then **Mobile App** (Week 5-6)
   - Ties everything together
   - User-facing experience

### Questions to Consider:
- **Mobile app platform**: React Native, Native Android, or Flutter?
- **Backend hosting**: Railway (easier) or AWS (more control)?
- **Auth**: Supabase Auth (faster) or custom (more flexible)?
- **Real-time**: WebSocket for live match tracking? (Phase 2+)

---

## Appendix: File Structure of Complete Project

```
squash-analytics/
├── backend/                     # NEW - FastAPI backend
│   ├── app.py
│   ├── api/
│   ├── services/                # Wraps existing code
│   ├── models/
│   └── workers/
├── mobile/                      # NEW - Mobile app
│   ├── ios/
│   ├── android/
│   └── src/
├── wear/                        # NEW - Wear OS app
│   └── app/
├── core/                        # EXISTING - Keep as-is
│   ├── metrics_framework.py
│   └── modular_analysis.py
├── data/                        # EXISTING - Keep as-is
│   └── ingestion/
│       └── data_ingestion.py
├── sports/                      # EXISTING - Keep as-is
│   └── squash/
│       └── detectors/
├── frontend/streamlit/          # EXISTING - Keep for analysis
│   └── app.py
├── docs/                        # ENHANCED - New docs added
│   ├── data_schema_design.md
│   ├── component_reuse_mapping.md
│   ├── backend_architecture.md
│   ├── wear_os_setup.md
│   └── integration_architecture.md
└── README.md
```

---

**END OF INTEGRATION ARCHITECTURE**

You now have a complete blueprint to build your squash analytics system!
