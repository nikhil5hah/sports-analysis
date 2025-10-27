# Component Reuse Mapping
## Existing Streamlit Code → New System Architecture

---

## 1. Data Ingestion Module

### `data/ingestion/data_ingestion.py`

#### REUSABLE: FitnessDataImporter Class (Lines 19-162)

**Current Usage**: Import GPX/FIT files in Streamlit
**New Usage**: Backend ingestion service

```python
# BEFORE (Streamlit)
importer = FitnessDataImporter()
df = importer.import_fit_file('temp_file.fit')

# AFTER (Backend Service)
# backend/services/data_ingestion_service.py
class DataIngestionService:
    def __init__(self):
        self.importer = FitnessDataImporter()  # REUSE existing class

    def process_watch_upload(self, fit_file_path: str, session_id: str) -> Dict:
        """Process FIT file uploaded from Pixel Watch 3"""
        df = self.importer.import_fit_file(fit_file_path)
        df = self.importer.preprocess_data(df)

        # Extract data into database format
        hr_data = self._extract_hr_data(df, session_id)
        sensor_data = self._extract_sensor_data(df, session_id)

        return {
            'hr_data': hr_data,
            'sensor_data': sensor_data,
            'session_summary': self._build_session_summary(df)
        }
```

**What to Extract**:
- ✓ Lines 57-126: FIT file parsing (accelerometer, gyroscope, HR)
- ✓ Lines 127-154: Preprocessing (interpolation, time diffs)
- ✓ Lines 156-161: Session context setting

**What to Modify**:
- Change: File input → Stream/Buffer input (for real-time processing)
- Add: Batch processing for large uploads
- Add: Validation for Pixel Watch 3 specific fields

---

## 2. Metrics Framework

### `core/metrics_framework.py`

#### REUSABLE: All Detector Classes

**Current Usage**: Run analysis on uploaded data
**New Usage**: Backend insight generation service

```python
# BACKEND SERVICE: backend/services/insight_generator.py
from core.metrics_framework import (
    MetricsFramework,
    RallyDetector,
    GameDetector,
    calculate_hr_zones
)

class InsightGenerator:
    def __init__(self):
        self.framework = MetricsFramework()
        self.framework.register_detector(RallyDetector())
        self.framework.register_detector(GameDetector())
        # ... register other detectors

    def generate_session_insights(self, session_id: str) -> Dict:
        """Generate insights from stored session data"""
        # Fetch HR + point data from database
        df = self._fetch_session_dataframe(session_id)

        # Run existing analysis
        results = self.framework.detect_all_metrics(df)

        # Enhance with score correlation
        insights = self._correlate_hr_with_scores(results, session_id)

        return insights
```

**Direct Reuse Components**:
1. **HR Zone Calculator** (lines 18-72)
   - Use in: Real-time watch app (show current zone)
   - Use in: Backend (calculate zones for all points)
   - Use in: Mobile app (display zone distribution)

2. **RallyDetector** (lines 497-831)
   - Backend: Detect rallies from full session
   - Could adapt for: Real-time rally detection on watch (simplified version)

3. **GameDetector** (lines 383-495)
   - Backend: Identify game boundaries from rest periods
   - Use in: Mobile app to display game-by-game breakdown

4. **MetricResult** dataclass (lines 83-91)
   - Backend: Standard format for insight storage
   - API: Response format for insight endpoints

**What to Extract for Wear OS** (Kotlin/Java versions needed):
```kotlin
// wear/src/main/kotlin/utils/HRZoneCalculator.kt
// Port of calculate_hr_zones() from Python
object HRZoneCalculator {
    fun calculateZone(heartRate: Float, maxHR: Float): Int {
        val pct = (heartRate / maxHR) * 100
        return when {
            pct < 50 -> 0
            pct < 60 -> 1
            pct < 70 -> 2
            pct < 80 -> 3
            pct < 90 -> 4
            else -> 5
        }
    }
}
```

---

## 3. Event Detection

### `sports/squash/detectors/event_detection.py`

#### REUSABLE: EventDetector Class (Lines 21-304)

**Current Usage**: Batch analysis of completed sessions
**New Usage**: Backend post-processing service

```python
# backend/services/event_processor.py
from sports.squash.detectors.event_detection import EventDetector

class EventProcessorService:
    def __init__(self):
        self.detector = EventDetector()  # REUSE existing

    def process_session_events(self, session_id: str) -> Dict:
        """Run event detection after session completes"""
        df = self._fetch_session_dataframe(session_id)

        # Detect warm-up/cool-down
        warmup = self.detector.detect_warm_up(df)
        cooldown = self.detector.detect_cool_down(df)

        # Detect rallies (cross-reference with manual point scoring)
        rallies = self.detector.detect_rallies(df)

        # Store detected events
        self._store_detected_events(session_id, {
            'warmup': warmup,
            'rallies': rallies,
            'cooldown': cooldown
        })

        return {...}
```

**Do NOT Reuse for Real-Time**:
- Warm-up detection (lines 29-73): Needs full session
- Rally detection (lines 75-140): Needs lookback analysis

**Could Simplify for Real-Time**:
- Create simplified version for watch: "Currently in rally" indicator
- Use current HR vs baseline (simple threshold)

---

## 4. Streamlit App Logic

### `app.py` and `frontend/streamlit/app.py`

#### SECTIONS TO MIGRATE:

**Section 1: Session Processing (Lines 141-187)**
```python
# CURRENT: Upload → Process → Display
def process_uploaded_file(uploaded_file, hand_position, session_type):
    importer = FitnessDataImporter()
    analyzer = ModularAnalysisEngine()

    df = importer.import_fit_file('temp_file.fit')
    df = importer.preprocess_data(df)

    analyzer.set_session_context(hand_position, session_type)
    analysis = analyzer.analyze_session(df)

    return {'raw_data': df, 'analysis': analysis}

# NEW: Backend API
# POST /api/sessions/upload
# - Accepts FIT file from mobile/watch
# - Returns session_id
# - Triggers async processing

# NEW: Mobile App
# - Calls backend API
# - Shows processing status
# - Fetches completed analysis
```

**Section 2: Visualization Logic (Lines 247-467)**

These visualizations should move to:
1. **Backend API**: Return chart-ready data structures
2. **Mobile App**: Render charts using native libraries (MPAndroidChart, etc.)
3. **Streamlit**: Keep for deep analysis tool

Example:
```python
# BACKEND API RESPONSE
GET /api/sessions/{session_id}/visualizations
{
    "hr_over_time": {
        "timestamps": [...],
        "heart_rates": [...],
        "zones": [...]
    },
    "zone_distribution": {
        "zone_1": 120,  # seconds
        "zone_2": 240,
        ...
    }
}

# Mobile app renders this data natively
# Streamlit continues to use create_heart_rate_chart() for advanced analysis
```

---

## 5. Key Insights to HR+Score Correlation

### NEW FUNCTIONALITY (Not in existing code)

**What User Wants**: Correlate HR with point outcomes

**Implementation Plan**:

```python
# backend/services/performance_analyzer.py
class PerformanceAnalyzer:
    """New service to correlate HR with match outcomes"""

    def analyze_hr_vs_performance(self, session_id: str) -> Dict:
        """
        Correlate HR zones with won/lost points
        """
        # Fetch points from database
        points = self._fetch_points(session_id)
        hr_data = self._fetch_hr_data(session_id)

        won_points_hr = []
        lost_points_hr = []

        for point in points:
            # Get HR during rally (5 seconds before point end)
            rally_hr = self._get_hr_window(
                hr_data,
                point.timestamp - 5,
                point.timestamp
            )

            if point.winner == 'me':
                won_points_hr.append(rally_hr.mean())
            else:
                lost_points_hr.append(rally_hr.mean())

        return {
            'avg_hr_on_won_points': np.mean(won_points_hr),
            'avg_hr_on_lost_points': np.mean(lost_points_hr),
            'hr_difference': np.mean(won_points_hr) - np.mean(lost_points_hr),
            'optimal_zone': self._find_optimal_zone(points, hr_data)
        }

    def _find_optimal_zone(self, points, hr_data):
        """Find which HR zone has best win rate"""
        zone_performance = {1: [], 2: [], 3: [], 4: [], 5: []}

        for point in points:
            zone = self._get_zone_at_point(hr_data, point.timestamp)
            zone_performance[zone].append(1 if point.winner == 'me' else 0)

        # Calculate win rate per zone
        zone_win_rates = {
            zone: np.mean(outcomes) if outcomes else 0
            for zone, outcomes in zone_performance.items()
        }

        return max(zone_win_rates.items(), key=lambda x: x[1])
```

**This is NEW logic** that combines:
- Existing HR zone calculations (from `metrics_framework.py`)
- New point-level data (from Wear OS button presses)
- Statistical analysis (new code)

---

## 6. Component Migration Summary

### Keep in Python (Backend)
✅ **Entire `core/` module**
- `metrics_framework.py` → Insight generation service
- `modular_analysis.py` → Session analysis orchestrator

✅ **Entire `data/ingestion/` module**
- `data_ingestion.py` → File upload processing service

✅ **Entire `sports/squash/detectors/` module**
- `event_detection.py` → Event detection service
- `performance_analysis.py` → Performance analytics
- `additional_metrics.py` → Advanced metrics

### Port to Kotlin (Wear OS)
🔄 **Simplified versions only**
- HR zone calculation (real-time on watch)
- Basic session timer
- Point counter

### Rewrite for Mobile (Kotlin/Swift/Flutter)
🆕 **New mobile-specific code**
- Match history list
- Session detail view
- Charts and visualizations (native libraries)
- Settings and profile management

### Keep in Streamlit (Analysis Tool)
✅ **Current app.py** - For deep dive analysis
- Power users who want advanced metrics
- Research and algorithm development
- Detailed session comparisons

---

## 7. Migration Priority (Recommended Order)

### Phase 1: Backend Setup ⭐ START HERE
1. Create FastAPI/Flask backend
2. Set up database (PostgreSQL/Supabase)
3. Migrate `FitnessDataImporter` → API endpoint `/upload`
4. Migrate `MetricsFramework` → Background job

### Phase 2: Wear OS MVP
1. Create Wear OS project (Jetpack Compose)
2. Implement HR monitoring
3. Implement score buttons (Me/Them)
4. Local SQLite storage
5. Sync to phone/backend

### Phase 3: Mobile Companion
1. Create mobile app (React Native/Flutter/Native)
2. List sessions from backend
3. Display basic metrics
4. Show HR charts

### Phase 4: Advanced Features
1. Correlate HR with scores (new backend logic)
2. Generate insights and recommendations
3. Historical trends and progress tracking
4. Export and sharing features

### Phase 5: ML Pipeline (50-100 sessions)
1. Collect raw sensor data
2. Train rally detection model
3. Train shot detection model
4. Improve insights with ML

---

## Next Document

See `backend_architecture.md` for:
- API endpoint design
- Database schema implementation
- Service layer architecture
- Authentication and sync strategy
