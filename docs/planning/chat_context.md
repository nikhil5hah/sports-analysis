# Sports Performance Analysis Platform - Context for AI Assistant

## Project Overview

Building a modular sports performance analysis platform starting with squash. The app analyzes fitness tracker data (GPX/FIT files) to detect performance metrics like warm-up length, number of rallies, longest rally, shots, etc.

## Current Status

### Working
- ✅ Data ingestion (GPX/FIT files from fitness trackers)
- ✅ Modular framework architecture  
- ✅ Basic metric detection (some metrics work, others need improvement)
- ✅ Streamlit UI with visualizations
- ✅ Pie chart showing session breakdown
- ✅ Natural time formatting (e.g., "5 mins 30 secs")
- ✅ Confidence scores as percentages

### Issues to Fix
- ⚠️ **Warm-up Detection**: Still showing 16.22 minutes (should be 3-5 mins)
- ⚠️ **Rally Detection**: Only detecting 16 rallies (should be much more, e.g., 50-150)
- ⚠️ **Longest Rally**: 24.38 minutes × 2 = 48.76 minutes (IMPOSSIBLE! Should be 10-60 seconds)
- ⚠️ **Rallies per Game**: 3.2 (way too low, should be 15-30)
- ⚠️ **Pie Chart**: Shows 100% rest (playing time not detected properly)
- ⚠️ **Timestamp Error**: "Addition/subtraction of integers and integer-arrays with Timestamp is no longer supported"

## User Requirements for Metrics

### 1. Warm-up (Priority: HIGH)
**Current**: ~16 minutes  
**Target**: 3-5 minutes  
**Logic**:
- Look for HR spike (20+ bpm increase from baseline)
- HR should stabilize within first 5 minutes
- HR during warm-up should NOT exceed 160 bpm
- Should detect: spike → stabilization pattern

### 2. Number of Rallies (Priority: HIGH)
**Current**: 16 rallies  
**Target**: 50-150 rallies for 81-minute session  
**Logic**:
- Use HR spikes in elevated HR windows to detect rallies
- Each rally: localized elevated HR window
- Duration: 5-180 seconds per rally
- Should detect: elevated HR above baseline (25% increase)
- Group consecutive elevated periods with gap detection

### 3. Longest Rally Length (Priority: HIGH)
**Current**: 24.38 mins × 2 = 48.76 mins (impossible!)  
**Target**: 10-60 seconds × 2 = 20 secs to 2 mins total  
**Logic**:
- From detected rallies, find maximum duration
- Validate: rally must be 5-180 seconds realistic
- Multiply by 2 to account for both players
- Should cap at realistic maximum (60-90 seconds × 2 = 2-3 mins)

### 4. Rallies per Game (Priority: MEDIUM)
**Current**: 3.2  
**Target**: 15-30 rallies per game  
**Logic**:
- English scoring: up to 9 points per serve (≈20-30 rallies/game)
- American scoring: point per rally (≈15-20 rallies/game)
- Range: 11-50 rallies per game, focus on 15-30
- Formula: total_rallies / number_of_games
- Depends on rally detection being accurate first

### 5. Shots Detected (Priority: LOW)
**Current**: 0 (no accelerometer data available)  
**Target**: N/A without accelerometer data  
**Logic**:
- Requires accelerometer data (X, Y, Z axes) from FIT files
- Current FIT files only have heart_rate data
- Should gracefully handle missing data
- Provide guidance to enable accelerometer in fitness tracker settings

## Technical Architecture

```
sports-analysis/
├── core/
│   ├── metrics_framework.py          # Base detector classes
│   └── modular_analysis.py          # Analysis orchestrator
├── sports/squash/detectors/
│   ├── event_detection.py            # Original event detectors
│   ├── performance_analysis.py       # Performance metrics
│   └── additional_metrics.py        # Additional detectors
├── data/ingestion/
│   └── data_ingestion.py            # GPX/FIT import
├── frontend/streamlit/
│   └── app.py                       # Streamlit UI
└── tests/
    └── test_mvp.py                  # Tests
```

## Key Files

### Main Files:
- **`core/metrics_framework.py`**: Contains `WarmUpDetector` and `RallyDetector` classes - these need fixing
- **`sports/squash/detectors/additional_metrics.py`**: Contains `LongestRallyDetector`, `RalliesPerGameDetector`, etc.
- **`frontend/streamlit/app.py`**: Streamlit UI with pie chart and visualizations

### Data Available:
- Currently: Only `heart_rate` data from FIT files
- Future: Need `accelerometer_x`, `accelerometer_y`, `accelerometer_z` for shot detection
- Session: 81.3 minutes, 2543 data points

## Recent Changes Made

1. **Warm-up detection**: Attempted to implement HR spike + stabilization but still getting 16 minutes
2. **Rally detection**: Lowered threshold from 30% to 25%, increased max duration to 180 seconds
3. **Added logging**: Added debug logs to see rally detection parameters
4. **Time formatting**: Changed to natural format (e.g., "5 mins 30 secs")
5. **Confidence**: Displayed as percentages
6. **Pie chart**: Added session breakdown visualization

## Current Detection Logic

### WarmUpDetector (core/metrics_framework.py, lines 98-208):
```python
# Current logic:
1. Calculate baseline HR (first 10 points)
2. Find first HR spike (>20 bpm increase from baseline)
3. Look for stabilization (HR within 10 bpm range after spike)
4. Constrain to 2-5 minutes
5. HR must be < 160 bpm during warm-up
```

**Problem**: Still calculating 16 minutes. Need to ensure logic limits to first 5 minutes hardcoded.

### RallyDetector (core/metrics_framework.py, lines 460-560):
```python
# Current logic:
1. Calculate baseline HR (20th percentile, excluding warm-up)
2. Rally threshold: baseline + 25% of (max - baseline)
3. Find periods above threshold
4. Group consecutive periods
5. Validate: rally must be 5-180 seconds
```

**Problem**: Only detecting 16 rallies. Need better threshold calibration or different approach.

## Immediate Tasks

### 1. Fix Warm-up Detection ⭐⭐⭐
- Limit search to first 5 minutes (300 seconds) hardcoded
- Detect HR spike (>20 bpm from baseline) within first 300 seconds
- Find stabilization within 60 seconds after spike
- Ensure HR < 160 bpm
- Default: 5 minutes if no pattern found
- Min: 2 minutes, Max: 5 minutes

### 2. Fix Rally Detection ⭐⭐⭐
- Lower threshold further or use different approach
- Consider using HR variability (std dev) in addition to absolute values
- May need to use accelerometer patterns if available
- Goal: Detect 50-150 rallies in 81-minute session
- Each rally: 5-60 seconds duration

### 3. Fix Longest Rally ⭐⭐
- Add validation: max rally duration 60 seconds × 2 = 120 seconds (2 mins)
- If rally > 60 seconds, it's likely multiple rallies merged
- Need better segmentation of long HR elevated periods

### 4. Fix Rallies per Game ⭐
- Depends on rally detection being accurate
- Formula: num_rallies / num_games
- Add validation: should be 15-30 range

### 5. Handle Shots Gracefully ⭐
- Currently requires accelerometer data (not available)
- Either: Remove metric, or provide guidance on enabling accelerometer
- Option: Use HR spikes as shot proxy (less accurate)

## Test Data

```
Session Duration: 81.3 minutes (2543 data points)
Available Data: heart_rate only
Heart Rate Range: [baseline ~80-90 bpm, max ~170-180 bpm]
```

## How to Run

```bash
cd /Users/nikhilshah/Projects/sports-analysis
python3 -m streamlit run frontend/streamlit/app.py
```

## Git Status

- All changes committed locally (WIP commits)
- NOT pushed to GitHub yet (user requested to wait until finalized)
- Ready for new AI assistant to continue improvements

## Next Steps for AI Assistant

1. Review the current detection algorithms in `core/metrics_framework.py`
2. Debug why warm-up is still detecting 16 minutes (should be 3-5 mins)
3. Debug why only 16 rallies detected (should be 50-150)
4. Fix longest rally calculation (currently 24 mins = impossible)
5. Test with the actual FIT file data
6. Ensure pie chart shows proper breakdown (playing time vs rest)

## Key Insights

- The timestamp arithmetic error suggests there are issues with how indices are being used in duration calculations
- The pie chart showing 100% rest suggests playing time is not being calculated properly
- Warm-up detection logic looks correct but not being applied/executed correctly
- Rally detection threshold (25%) might still be too high, or there's an issue with the grouping logic

