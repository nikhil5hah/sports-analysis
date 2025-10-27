# Multi-Sport Support Architecture

## Overview

This platform is designed to support multiple racket sports:
- 🎾 **Squash** (primary, MVP)
- 🎾 **Tennis** (future)
- 🏸 **Badminton** (future)
- 🏓 **Table Tennis** (future)
- 🎾 **Padel** (future)

---

## Database Design (Sport-Agnostic)

### Session Model
```python
class Session:
    sport = Column(String(50), default="squash")  # ✅ Sport type
    scoring_system = Column(String(20))            # ✅ Sport-specific
    # ... rest is generic
```

**Supported sports:**
- `squash` - american or english scoring
- `tennis` - traditional or no-ad scoring
- `badminton` - rally point system
- `table_tennis` - rally point system
- `padel` - same as tennis

### Point Model
```python
class Point:
    # Generic fields work for all sports
    winner = Column(String(20))  # "me" or "opponent"
    score_before = Column(Integer)
    score_after = Column(Integer)
```

**This works for all racket sports!**

---

## Sport-Specific Differences

### Scoring Systems

**Squash:**
- American: Point-a-rally to 11 (win by 2)
- English: Point only on serve to 9 (or 10 if 8-8)

**Tennis:**
- Traditional: 15-30-40-game, with deuces
- No-ad: First to 4 points (deuce = next point wins)

**Badminton:**
- Rally point to 21 (win by 2, cap at 30)

**Table Tennis:**
- Rally point to 11 (win by 2)

**Padel:**
- Same as tennis

### Court/Table Differences

**Squash:** Indoor court, front wall
**Tennis:** Outdoor/indoor court, net
**Badminton:** Indoor court, high net
**Table Tennis:** Indoor table, low net
**Padel:** Enclosed court with walls

### Metric Differences

| Metric | Squash | Tennis | Badminton | Table Tennis | Padel |
|--------|--------|--------|-----------|--------------|-------|
| Rally Detection | ✅ HR + Sensors | ✅ HR + Sensors | ✅ HR + Sensors | ✅ Sensors only | ✅ HR + Sensors |
| Shot Detection | ✅ Accelerometer | ✅ Accelerometer | ✅ Accelerometer | ✅ Accelerometer | ✅ Accelerometer |
| Serve Detection | Maybe | ✅ Important | ✅ Important | ✅ Important | ✅ Important |
| Spin Detection | Low priority | ✅ High priority | ✅ Medium | ✅ High priority | ✅ Medium |
| Court Position | N/A (small court) | ✅ GPS | Maybe GPS | N/A | Maybe GPS |

---

## Code Architecture for Multi-Sport

### Current Structure (Squash-focused)
```
sports/
└── squash/
    └── detectors/
        ├── event_detection.py
        ├── performance_analysis.py
        └── additional_metrics.py
```

### Multi-Sport Structure (Planned)
```
sports/
├── base/                        # Shared base classes
│   ├── base_detector.py         # Generic detector
│   └── base_metrics.py          # Common metrics
├── squash/
│   └── detectors/
│       ├── rally_detector.py
│       ├── shot_detector.py
│       └── squash_metrics.py
├── tennis/
│   └── detectors/
│       ├── rally_detector.py    # Tennis-specific
│       ├── serve_detector.py    # Different from squash
│       └── tennis_metrics.py
├── badminton/
│   └── detectors/
│       └── ...
└── ...
```

### Backend Service Layer
```python
# backend/services/sport_factory.py
class SportFactory:
    @staticmethod
    def get_detector(sport: str, detector_type: str):
        if sport == "squash":
            from sports.squash.detectors import SquashRallyDetector
            return SquashRallyDetector()
        elif sport == "tennis":
            from sports.tennis.detectors import TennisRallyDetector
            return TennisRallyDetector()
        # ...
```

---

## Wear OS Multi-Sport Support

### Sport Selection UI
```kotlin
// User selects sport before starting session
@Composable
fun SportSelectionScreen() {
    // Dropdown or cards
    // - Squash
    // - Tennis
    // - Badminton
    // - Table Tennis
    // - Padel
}
```

### Sport-Specific Configuration
```kotlin
data class SportConfig(
    val sport: String,
    val scoringSystem: String,
    val maxPointsPerGame: Int,
    val useServeTracking: Boolean,
    val hrRelevance: String  // high/medium/low
)

val sportConfigs = mapOf(
    "squash" to SportConfig(
        sport = "squash",
        scoringSystem = "american",  // or "english"
        maxPointsPerGame = 11,
        useServeTracking = false,     // Not critical
        hrRelevance = "high"          // HR very important
    ),
    "tennis" to SportConfig(
        sport = "tennis",
        scoringSystem = "traditional",
        maxPointsPerGame = 4,  // 4 points = 1 game
        useServeTracking = true,      // Critical for tennis
        hrRelevance = "medium"        // Longer rallies, varied
    ),
    "table_tennis" to SportConfig(
        sport = "table_tennis",
        scoringSystem = "rally_point",
        maxPointsPerGame = 11,
        useServeTracking = true,
        hrRelevance = "low"           // HR less variable
    )
)
```

---

## Mobile App Multi-Sport Support

### Session List
```
My Sessions
├── 🎾 Squash vs John - Jan 15 (3-1 Win)
├── 🎾 Tennis vs Sarah - Jan 14 (6-4, 6-3 Win)
├── 🏸 Badminton vs Mike - Jan 13 (21-18, 18-21, 21-19 Win)
└── ...
```

### Sport-Specific Insights

**Squash:**
- Optimal HR zone
- Rally intensity
- Wall shot detection

**Tennis:**
- Serve speed (future with radar)
- Forehand vs backhand ratio
- Court coverage (GPS)

**Badminton:**
- Smash detection
- Jump frequency
- Shuttle speed estimation

---

## Implementation Phases

### Phase 1: Squash Only (MVP) ✅
- Build complete system for squash
- Validate architecture
- Collect data

### Phase 2: Add Tennis (Month 3-4)
- Create `sports/tennis/` module
- Adapt existing detectors for tennis
- Add serve tracking
- Tennis-specific scoring UI

### Phase 3: Add Badminton (Month 5-6)
- Create `sports/badminton/` module
- Focus on jump detection
- Smash intensity metrics

### Phase 4: Table Tennis & Padel (Month 7+)
- Faster rally detection needed
- Less HR variance
- More shot type variety

---

## Benefits of Multi-Sport Architecture

### For Users:
- ✅ One app for all racket sports
- ✅ Cross-sport fitness comparison
- ✅ Unified match history

### For Development:
- ✅ Shared codebase (HR monitoring, sync, etc.)
- ✅ Reusable ML models (rally detection concepts transfer)
- ✅ Faster feature development (build once, adapt for each sport)

### For Business:
- ✅ Larger addressable market
- ✅ Network effects (players often play multiple sports)
- ✅ Unique positioning ("Strava for racket sports")

---

## Next Steps

1. **Complete Squash MVP** (validate architecture)
2. **Identify tennis players** in network for beta testing
3. **Adapt detectors** for tennis (6-8 weeks)
4. **Expand to other sports** based on user demand

---

**The architecture is already multi-sport ready!** 🎉

Just need to:
- Create sport-specific detector modules
- Add sport selection in UI
- Adapt scoring logic per sport
