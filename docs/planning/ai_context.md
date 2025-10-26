# AI Context: Sports Performance Analysis Platform

## 🎯 Project Overview

**Sports Performance Analysis Platform** is a modular, extensible framework for analyzing racket sports performance using fitness tracker data. Currently focuses on squash with plans to expand to tennis, badminton, table tennis, and padel.

## 📊 Current Status

**Phase 1 (MVP) - COMPLETE ✅**
- Modular metrics framework implemented
- 10+ squash-specific metrics
- GPX/FIT file data ingestion
- Streamlit interface for insights
- Accelerometer/gyroscope data extraction

**Next Phase**: Algorithm refinement with real user data

## 🏗️ Architecture

### Directory Structure
```
sports-analysis/
├── core/                      # Core framework (reusable across sports)
│   ├── metrics_framework.py  # Base detector classes
│   └── modular_analysis.py   # Analysis orchestrator
│
├── sports/squash/detectors/   # Sport-specific modules
│   ├── event_detection.py     # Event detection algorithms
│   ├── performance_analysis.py # Performance metrics
│   └── additional_metrics.py  # Additional detectors
│
├── data/ingestion/           # Data processing
│   └── data_ingestion.py     # GPX/FIT file import
│
├── frontend/streamlit/        # User interface
│   └── app.py                # Streamlit application
│
└── tests/                     # Test files
    └── test_mvp.py           # MVP tests
```

### Key Design Patterns

1. **Modular Framework**: Each sport and metric is an independent module
2. **Base Metric Detector**: All detectors inherit from `BaseMetricDetector`
3. **Confidence Scoring**: Every metric returns a confidence score (0.0-1.0)
4. **Context-Aware Analysis**: Hand position and session type affect algorithms

## 🔧 Core Components

### BaseMetricDetector
**Location**: `core/metrics_framework.py`

Abstract base class for all metric detectors with:
- `detect()` - Main detection method (must be implemented)
- `get_required_data_fields()` - Required data fields
- `get_optional_data_fields()` - Optional improvements
- `validate_data()` - Data validation
- `get_confidence_score()` - Confidence calculation
- Algorithm version tracking

### MetricResult
Standardized result format:
- `metric_name`: String identifier
- `value`: Detected value (Any type)
- `confidence`: Float (0.0-1.0)
- `metadata`: Dict with additional info
- `data_points`: List of (start, end) tuples for events
- `algorithm_version`: String version

### Data Flow
1. User uploads GPX/FIT file
2. Data ingestion parses and preprocesses
3. Session context set (hand position, session type)
4. Framework registers all detectors
5. Each detector runs independently
6. Results aggregated with confidence scores
7. Display insights with recommendations

## 📈 Current Metrics (Squash)

### Time-Based Metrics
- Warm-up duration (MM:SS format)
- Cool-down duration  
- Total session duration
- Total playing time
- Rest between games

### Count-Based Metrics
- Number of games
- Number of rallies
- Rallies per game
- Shots detected (via accelerometer)

### Special Calculations
- Longest rally (doubled to account for both players)
- Performance deterioration point
- Heart rate zones distribution

## 🎯 Key Features

### Data Sources
- **GPX files**: Strava exports (heart rate, cadence, GPS)
- **FIT files**: Native format (heart rate, cadence, speed, accelerometer, gyroscope)
- **Future**: Direct tracker APIs (Garmin, Polar, etc.)

### Session Context
- **Hand position**: `playing_hand` or `non_playing_hand`
  - Different algorithms for each position
  - Affects shot detection and movement analysis
- **Session type**: `training` or `match`
  - Different metrics emphasized
  - Training: technique, endurance
  - Match: intensity, competitive performance

### Confirmation Scoring
- Each metric has confidence (0.0-1.0)
- Based on: data completeness, pattern strength, reasonableness
- Allows filtering: Only show metrics with confidence > 0.5
- Helps identify data quality issues

## 🔄 Iteration Workflow

### Adding a New Metric
1. Create detector class inheriting `BaseMetricDetector`
2. Implement required methods
3. Register with framework in `modular_analysis.py`
4. Test with sample data
5. Refine algorithm based on real data

### Adding a New Sport
1. Create `sports/{sport}/detectors/` directory
2. Implement sport-specific detectors
3. Follow squash structure for consistency
4. Register with main framework
5. Add sport-specific tests

### Improving Algorithms
1. Increment `algorithm_version`
2. Update detection logic
3. Test with real data
4. Document improvements
5. Compare old vs new results

## 💡 Key Insights for Working with This Code

### Imports
All imports use full paths:
```python
from core.modular_analysis import ModularAnalysisEngine
from data.ingestion.data_ingestion import FitnessDataImporter
from sports.squash.detectors.event_detection import EventDetector
```

### Running the App
```bash
python3 run.py
# OR
streamlit run frontend/streamlit/app.py
```

### Time Formatting
- Time values shown as MM:SS (e.g., "5:30")
- Integer metrics rounded up (e.g., 1.2 → 2)
- Longest rally doubled for both players

### Data Requirements
- **Minimum**: Timestamp, heart_rate
- **Optimal**: + cadence, accelerometer, gyroscope data
- Handles missing data gracefully with confidence warnings

## 🔮 Future Plans

**Phase 2 (Weeks 5-8)**: Production readiness
- Algorithm refinement with real data
- Session storage and persistence
- Historical tracking

**Phase 3 (Weeks 9-14)**: Multi-sport expansion
- Tennis, badminton, table tennis, padel
- Consistent framework across sports

**Phase 4 (Weeks 15-22)**: AI/ML integration
- Historical pattern recognition
- Predictive analytics
- Personalized insights

**Phase 5 (Weeks 23-32)**: Mobile apps
- iOS/Android native apps
- Real-time analysis during sessions

**Phase 6 (Weeks 33-40)**: Platform expansion
- Web dashboard
- Team/coach features
- Public API

## 📝 Important Files

- **`PROJECT_PLAN.md`**: 40-week detailed roadmap
- **`ARCHITECTURE.md`**: System design and structure
- **`CONTRIBUTING.md`**: How to add new features
- **`README.md`**: Project overview and quick start
- **`QUICK_START.md`**: Detailed getting started guide

## 🤖 AI Assistant Guidelines

When working on this codebase:

1. **Respect modularity**: Don't break the separation between core and sport-specific code
2. **Maintain consistency**: Follow existing patterns when adding features
3. **Version tracking**: Always increment algorithm versions when changing logic
4. **Test thoroughly**: Use test_mvp.py and real data for validation
5. **Document changes**: Update relevant MD files with significant changes
6. **Confidence scoring**: Always return meaningful confidence scores
7. **Data flexibility**: Handle missing data gracefully

## 🔗 Quick Reference

- Main entry: `python3 run.py` or `streamlit run frontend/streamlit/app.py`
- Tests: `python3 tests/test_mvp.py`
- Core framework: `core/metrics_framework.py`
- Analysis engine: `core/modular_analysis.py`
- App UI: `frontend/streamlit/app.py`

