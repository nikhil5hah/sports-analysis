# Metric Detection Logic Analysis

## Current Issues
Based on your test data (81.3 minute squash session):
- **Warm-up**: Detects 16.22 mins (should be 3-8 mins) ❌
- **Number of Rallies**: 16 rallies detected (questionable)
- **Longest Rally**: 24.38 mins × 2 = 48.76 mins (IMPOSSIBLE - entire session!)
- **Rallies per Game**: 3.2 (low for squash)
- **Shots Detected**: 0 (no accelerometer data available)

---

## 1. Warm-Up Detection

### Current Logic:
```python
# Steps:
1. Calculate baseline HR (first 10 points): ~80-90 bpm
2. Calculate threshold HR: baseline + 30% of (max - baseline)
3. Search first 600 seconds (10 mins) or 15% of session
4. Find first point where HR crosses threshold
5. Default: 5 minutes if no threshold crossed
6. Constraints: Minimum 3 mins, Maximum 8 mins
```

### Problems:
- **Issue**: Still calculating as ~16 mins because of the percentage-based `max_search_points` calculation
- **Root Cause**: Using `max_search_points = int(len(hr_data) * 0.15)` (1,600+ points = 16+ mins)
- **Fix**: Should only search in first 10 minutes regardless of session length

### Proposed Improvement:
```python
# Better approach:
1. Set fixed search window: first 10 minutes (600 seconds) maximum
2. Look for HR crossing 30% of max range
3. If found: Use that point
4. If not found: Use 5 minutes as reasonable default
5. Validate: Must be 3-8 minutes for realistic warm-up
```

---

## 2. Number of Rallies Detection

### Current Logic:
```python
# Steps:
1. Calculate baseline HR (20th percentile, excluding warm-up if known)
2. Rally threshold: baseline + 30% of (max - baseline)
3. Find consecutive periods above threshold
4. Group consecutive periods (minimum 5 data points = 5 seconds)
5. Count groups = number of rallies
```

### Problems:
- **Issue**: Threshold might be too low, counting non-rally periods
- **Issue**: No validation of rally durations (should be 5-60 seconds)
- **Issue**: Doesn't exclude initial warm-up period from rally count
- **Issue**: Doesn't distinguish between rally and rest periods well

### Proposed Improvement:
```python
# Better approach:
1. Define rally as: HR above baseline + 40% AND lasting 5-90 seconds
2. Must have clear start (HR rising) and end (HR falling)
3. Exclude first 10% of session (warm-up)
4. Exclude last 10% of session (if cool-down detected)
5. Require gap of at least 10 seconds between rallies
```

---

## 3. Longest Rally Length

### Current Logic:
```python
# Steps:
1. Use rallies detected from RallyDetector
2. Find rally with maximum duration
3. Multiply by 2 (account for both players)
```

### Problems:
- **Issue**: Detecting 24.38 mins as longest rally is impossible!
- **Root Cause**: Rally detection is including entire playing periods as single rallies
- **Issue**: No validation (max realistic rally is 2-3 minutes)

### Proposed Improvement:
```python
# Better approach:
1. Validate rally duration (must be 5 seconds to 3 minutes)
2. If rally > 3 minutes, it's likely multiple rallies combined
3. Cap longest rally at realistic maximum (90 seconds * 2 = 3 mins both players)
4. Use rally detection with proper gaps
```

---

## 4. Rallies Per Game

### Current Logic:
```python
# Steps:
1. Count number of rallies (from RallyDetector)
2. Count number of games (from GameDetector)
3. Divide: rallies / games
```

### Problems:
- **Issue**: Getting 3.2 rallies per game (too low for squash)
- **Root Cause**: Not detecting enough rallies (only 16 in 81 minute session)
- **Issue**: Game detection might not be accurate

### Proposed Improvement:
```python
# Better approach:
1. First fix rally detection
2. Expect 5-20 rallies per game for squash
3. If result < 3: Warning about data quality
4. Use rest periods to validate games
```

---

## 5. Shots Detected

### Current Logic:
```python
# Steps:
1. Check for accelerometer data (X, Y, Z axes)
2. Calculate acceleration magnitude
3. Find peaks above threshold
4. Count peaks as shots
```

### Problems:
- **Issue**: No accelerometer data in current FIT files (only heart_rate)
- **Issue**: Algorithm is there but not useable without accelerometer data

### Proposed Improvement:
```python
# Options:
1. Keep algorithm but mark as "requires accelerometer data"
2. Use HR spikes as proxy for shots (less accurate)
3. Remove metric if accelerometer not available
4. Provide guidance on enabling accelerometer in fitness tracker
```

---

## Recommended Fix Order

### Priority 1: Fix Warm-Up Detection ⭐
**Current**: ~16 minutes  
**Target**: 3-8 minutes  
**Fix**: Limit search to first 10 minutes (600 seconds) hardcoded

### Priority 2: Fix Longest Rally ⭐⭐
**Current**: 24.38 mins (impossible!)  
**Target**: 10-180 seconds  
**Fix**: Add validation and proper rally segmentation

### Priority 3: Fix Rally Detection ⭐⭐⭐
**Current**: 16 rallies in 81 mins (too few)  
**Target**: Should be much more  
**Fix**: Improve threshold and grouping logic

### Priority 4: Fix Rallies Per Game
**Depends on**: Rally detection being accurate first

### Priority 5: Shots Detected
**Decision needed**: Keep or remove without accelerometer data

---

## Quick Test Values

Based on a typical 81-minute squash session:
- **Warm-up**: 5-8 minutes ✅
- **Rallies**: 50-150 rallies (lots of short rallies) ✅
- **Longest rally**: 30-60 seconds total (15-30 sec per player) ✅
- **Rallies per game**: 10-30 per game ✅
- **Shots**: N/A without accelerometer

---

## Next Steps

1. **Test warm-up fix** with hardcoded 10-minute limit
2. **Add rally validation** (duration limits)
3. **Improve rally grouping** (proper start/end detection)
4. **Add data quality warnings** for unrealistic values
5. **Handle shots gracefully** when accelerometer data missing

