# AI Context - Sports Performance Analysis Platform

**Last Updated**: Current session  
**Purpose**: Comprehensive context for AI assistants working on this project  

---

## Project Overview

**Sports Performance Analysis Platform** - A modular, extensible framework for analyzing racket sports performance using fitness tracker data. Currently focuses on squash with plans to expand to tennis, badminton, table tennis, and padel.

**Key Value**: Analyze GPX/FIT files from fitness trackers to extract meaningful performance metrics like warm-up duration, rally counts, heart rate zones, and more.

---

## Current System Status

### ✅ Working Well
- Data ingestion (GPX/FIT files)
- Modular framework architecture
- Zone-based metrics (total playing time, total rest time, avg playing HR, avg rest HR)
- Streamlit UI with improved 3-column layout
- Session breakdown and HR zone distribution charts
- Heart rate chart and session phases timeline
- Game detection (number of games) - high confidence
- Rest between games - high confidence
- Warm-up detection - working with proper time caps
- Total session duration

### ⚠️ Needs Improvement
- **Cool-down Detection**: Often returns 0 (many players skip it)
- **Session Phases Timeline**: Currently divides session into equal segments, needs better HR analysis

### ❌ Not Working / No Data
- **Shot Detection**: Requires accelerometer data (not available in current dataset)

---

## Architecture

```
sports-analysis/
├── core/                         # Core framework (reusable)
│   ├── metrics_framework.py      # Base detector classes, HR zones
│   └── modular_analysis.py       # Analysis orchestrator
├── sports/squash/detectors/      # Sport-specific modules
│   ├── event_detection.py        # Event detection algorithms
│   ├── performance_analysis.py   # Performance metrics
│   └── additional_metrics.py     # Additional detectors
├── data/ingestion/               # Data processing
│   └── data_ingestion.py         # GPX/FIT file import
├── frontend/streamlit/           # User interface
│   └── app.py                    # Streamlit application
├── docs/                         # Documentation
│   ├── metrics_definitions.md    # Complete metric definitions
│   ├── quick_start.md            # Getting started guide
│   ├── architecture.md           # System design
│   └── planning/                 # Planning docs
└── tests/                        # Test files
```

---

## Core Components

### BaseMetricDetector (`core/metrics_framework.py`)
Abstract base class for all metric detectors:
- `detect()` - Main detection method
- `get_required_data_fields()` - Required data fields
- `validate_data()` - Data validation
- `get_confidence_score()` - Confidence calculation
- Algorithm version tracking

### MetricResult
Standardized result format:
- `metric_name`: String identifier
- `value`: Detected value (Any type)
- `confidence`: Float (0.0-1.0)
- `metadata`: Dict with additional info
- `data_points`: List of (start, end) tuples
- `algorithm_version`: String version

### Heart Rate Zones
Calculated for all data points based on max HR:
- **Zone 1**: 50-60% max HR (Rest)
- **Zone 2**: 60-70% max HR (Light Activity)
- **Zone 3**: 70-80% max HR (Aerobic)
- **Zone 4**: 80-90% max HR (Hard)
- **Zone 5**: 90-100% max HR (Maximum)

---

## Current Metrics (13 Total)

| # | Metric | Status | Data Source | Confidence |
|---|--------|--------|-------------|------------|
| 1 | Warm-up Length | ✅ | Heart Rate | 0.35-0.65 |
| 2 | Cool-down Length | ⚠️ | Heart Rate | Often 0 |
| 3 | Number of Games | ✅ | Heart Rate | ~1.0 |
| 4 | Number of Rallies | ✅ **Improved** | Heart Rate | ~0.79-1.0 |
| 5 | Total Session Duration | ✅ | Timestamps | 1.0 |
| 6 | Total Playing Time | ✅ | HR Zones | 0.3-0.5 |
| 7 | Total Rest Time | ✅ | HR Zones | 0.4-0.5 |
| 8 | Longest Rally Length | ✅ | Heart Rate | Capped at 120s |
| 9 | Rallies Per Game | ✅ **Improved** | Calculated | Now ~12 per game |
| 10 | Rest Between Games | ✅ | Heart Rate | ~1.0 |
| 11 | Shots Detected | ❌ | Accelerometer | No data |
| 12 | Avg Playing HR | ✅ | HR Zones | 0.7-0.8 |
| 13 | Avg Rest HR | ✅ | HR Zones | 0.2-0.3 |

---

## Zone-Based Metrics (Production Ready)

These are the most reliable metrics in the system:

1. **Total Playing Time** - Sum of time in Zone 3, 4, or 5
2. **Total Rest Time** - Sum of time in Zone 1 or 2 (excluding warm-up/cool-down)
3. **Avg Playing Heart Rate** - Mean HR during Zone 3, 4, or 5
4. **Avg Rest Heart Rate** - Mean HR during Zone 1 or 2

**Why They Work**: Direct measurement from HR zones eliminates guesswork about activity patterns.

---

## Recent Major Improvements

### UI Overhaul
- 3-column layout for key insights (Timings, Games/Rallies, Heart Rate)
- Two side-by-side pie charts (Session Breakdown, HR Zone Distribution)
- Separate charts for HR over time and session phases
- WIP labels on unreliable metrics
- Improved metric display with expandable details

### Zone-Based Implementation
- Introduced HR zone calculator
- Rewrote playing time and rest time detectors to use zones
- Added avg playing HR and avg rest HR detectors
- Added `PHYSIOLOGICAL` metric type to framework

### Documentation
- Comprehensive metrics definitions document
- Simplified quick start guide
- Organized documentation structure
- All UI/visualization references removed from technical docs

---

## Known Issues & WIP Items

### Rally Detection (Recently Improved ✅)
**Problem Solved**: Now detecting 60+ rallies for 81-minute sessions (previously only ~6-28)

**Current Solution** (v3.2 - drop-based detection):
1. Detects HR drops of 1+ bpm from recent peak (15-second lookback)
2. Drop must be sustained for 1+ seconds
3. Filters rallies: duration between 2-120 seconds
4. Skips warm-up period (first ~5 minutes)
5. Results: 60-70 rallies for typical 81-minute session

**Algorithm Details**:
- Uses 10-second rolling average for smoothing
- Tracks peak HR in last 15 seconds
- Identifies when HR drops below peak by 1+ bpm
- Creates rally boundaries when drop is sustained
- Minimum rally duration: 2 seconds

**Status**: ✅ Working - Detecting 60+ rallies with high confidence

### Longest Rally (Fixed ✅)
**Problem Solved**: Was showing unrealistic durations (7+ minutes)

**Current Solution**:
- Removed "multiply by 2" assumption
- Filters out rallies longer than 120 seconds (likely merged rallies)
- Returns actual longest rally duration within realistic bounds
- Typical range: 5-90 seconds, max reasonable: 120 seconds
- Average ~30 seconds

**Status**: ✅ Working - Returns realistic longest rally duration

### Cool-down (Often 0)
**Why**: Many players skip cool-down, which is valid
**Future**: Consider accepting 0 as expected result, or improve pattern detection

---

## Data Format

**Current Dataset**:
- 81.3 minutes of squash session
- 2543 data points
- Heart rate data available
- No accelerometer data (requires sensor configuration)

**Expected Data**:
- Heart rate: Essential
- Timestamps: Essential
- Accelerometer (X, Y, Z): Optional but needed for shot detection
- Cadence, GPS: Optional

---

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run frontend/streamlit/app.py

# Or use the runner
python3 run.py
```

App runs at: `http://localhost:8501` (or available port)

---

## Key Files to Modify

### For Metric Improvements
- `core/metrics_framework.py` - Rally detection, warm-up, cool-down
- `sports/squash/detectors/additional_metrics.py` - Longest rally, rallies per game

### For UI Improvements
- `frontend/streamlit/app.py` - All UI components

### For Documentation
- `docs/metrics_definitions.md` - Complete metric specs
- `AI_CONTEXT.md` - This file (update after each session)

---

## Development Guidelines

1. **Respect Modularity**: Don't break separation between core and sport-specific code
2. **Version Tracking**: Always increment algorithm version when changing logic
3. **Confidence Scoring**: Return meaningful confidence scores (0.0-1.0)
4. **Handle Missing Data**: Gracefully handle missing data fields
5. **Test Thoroughly**: Use existing test files and real data
6. **Document Changes**: Update relevant MD files with significant changes
7. **Zone-Based First**: Prefer zone-based approaches when possible

---

## Mobile App Development (TRacket)

### Completed Phases
- ✅ **Phase 1**: Authentication (Login/Register screens, JWT, auto-login)
- ✅ **Phase 2**: Session Management (Create, List, Details, Active tracking)
- ✅ **Phase 4**: Score Tracking (Point-by-point scoring, game management, final scores)
- ⚠️ **Phase 5**: Analytics Dashboard (partially complete - AnalyticsScreen exists)

### Technology Stack
- React Native + Expo
- Running on http://localhost:8081 (web)
- Backend API at http://192.168.1.35:8000
- AsyncStorage for JWT tokens

### Current Mobile App Issue (CRITICAL - UNRESOLVED)
**Problem**: Android app fails to load on Pixel phone via Expo Go
**Error**: `java.lang.string cannot be cast to java.lang.Boolean`

**Troubleshooting Attempts (All Failed)**:
1. Removed `newArchEnabled` and `edgeToEdgeEnabled` from app.json
2. Cleared all caches (Expo Go, Metro, .expo, node_modules)
3. Removed `cursor: 'pointer'` web-specific CSS properties
4. Multiple server restarts with cache clearing
5. Reinstalled Expo Go app

**Status**:
- ❌ Android testing blocked
- ✅ Web version works correctly
- ✅ Logo integration complete (TRacket branding)

**Next Steps**:
1. Check for other web-specific CSS properties
2. Examine full error stack trace
3. Try development build instead of Expo Go
4. Consider downgrading react-native-screens

### Mobile App File Structure
```
mobile/
├── App.js
├── app.json (updated - removed problematic configs)
├── assets/
│   └── logo.png (added)
├── src/
│   ├── api/
│   │   └── client.js (auth, sessions, points)
│   ├── screens/
│   │   ├── LoginScreen.js (with logo)
│   │   ├── RegisterScreen.js
│   │   ├── HomeScreen.js (with logo)
│   │   ├── SessionCreateScreen.js
│   │   ├── SessionListScreen.js
│   │   ├── ActiveSessionScreen.js (with score tracking)
│   │   ├── SessionDetailsScreen.js (with scores)
│   │   └── AnalyticsScreen.js
│   └── navigation/
│       └── AppNavigator.js
```

## Recent Session Summary

**Last Session Focus**: Android troubleshooting + Mobile app branding

**Changes Made**:
- ❌ Attempted to fix Android Expo Go error (multiple approaches, still unresolved)
- ✅ Integrated Logo.png into mobile app (LoginScreen, HomeScreen)
- ✅ Updated branding from "Tracket" to "TRacket" throughout app
- ✅ Removed web-specific CSS properties from all screen files

**Current State**:
- ✅ Backend API fully functional (all phases complete)
- ✅ Mobile app Phases 1,2,4 complete on web
- ❌ Mobile app blocked on Android (Expo Go error)
- ✅ Documentation up to date
- ✅ Streamlit analytics dashboard working
- ⚠️ Rally detection still needs improvement (in analytics engine)

---

## Next Steps for Future AI Sessions

### High Priority
1. ✅ **Fix Rally Detection** - Implemented drop-based detection (v3.2) - detecting 60+ rallies
2. ✅ **Fix Longest Rally** - Capped at 120s, removed x2 multiplier
3. **Improve Session Phases Timeline** - Analyze HR patterns instead of equal segments

### Medium Priority
4. Improve cool-down detection or accept 0 as valid
5. Add metadata to zone-based metrics (zone distribution breakdowns)

### Low Priority
6. Shot detection (requires accelerometer data)
7. Refine game detection with additional indicators

---

## Important Notes

- Zone-based metrics (#6, #7, #12, #13) are production-ready
- Rally-related metrics (#4, #8, #9) are marked with **[WIP]** labels in UI
- Cool-down returning 0 may be correct (many players skip it)
- Shot detection requires accelerometer data not currently available
- All working metrics have good confidence scores
- UI clearly indicates which metrics are reliable vs WIP

---

**For detailed metric definitions, logic, and formulas, see:** `docs/metrics_definitions.md`  
**For architecture details, see:** `docs/architecture.md`  
**For getting started, see:** `docs/quick_start.md`
