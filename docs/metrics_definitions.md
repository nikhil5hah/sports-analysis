# Squash Metrics - Definitions & Technical Specifications

**Last Updated**: Current as of latest drop-based rally detection (v3.2)  
**Purpose**: Complete technical reference for all squash performance metrics  

---

## Metrics Overview

| # | Metric | Current Status | Data Source | Version |
|---|--------|----------------|-------------|---------|
| 1 | Warm-up Length | ✅ Working | Heart Rate | v1.4 |
| 2 | Cool-down Length | ⚠️ Needs Improvement | Heart Rate | v1.0 |
| 3 | Number of Games | ✅ Working | Heart Rate | v1.0 |
| 4 | Number of Rallies | ✅ **Working** - Recently improved | Heart Rate | v3.2 |
| 5 | Total Session Duration | ✅ Working | Timestamps | v1.0 |
| 6 | Total Playing Time | ✅ Working | Heart Rate (Zones) | v2.0 |
| 7 | Total Rest Time | ✅ Working | Heart Rate (Zones) | v1.0 |
| 8 | Longest Rally Length | ✅ **Working** - Capped at 120s | Heart Rate | v1.0 |
| 9 | Rallies Per Game | ✅ **Working** - Now improved | Calculated | v1.0 |
| 10 | Rest Between Games | ✅ Working | Heart Rate | v1.0 |
| 11 | Shots Detected | ❌ No Data Available | Accelerometer | v1.0 |
| 12 | Avg Playing HR | ✅ Working | Heart Rate (Zones) | v1.0 |
| 13 | Avg Rest HR | ✅ Working | Heart Rate (Zones) | v1.0 |

**Status Legend:**
- ✅ Working well with good confidence
- ⚠️ Works but needs improvement or has reliability issues
- ❌ Not working or no data available
- **WIP** Work in Progress - currently unreliable

---

## Metric Definitions

### 1. Warm-up Length ⏱️

**Definition**: Duration of the initial warm-up period at the start of a squash session.

**Data Source**: Heart rate data from chest strap or watch sensor.

**Current Logic** (v1.4):
1. Identifies initial HR spike in first 10 minutes
2. Calculates baseline HR from first stable period
3. Detects sustained HR elevation above baseline
4. Caps duration between 2-5 minutes
5. Uses actual sampling rate to convert data points to time

**Formula**: 
```
warmup_duration = min(max(detected_period, 2_min), 5_min)
```

**Status**: ✅ Working - Confidence typically 0.35-0.65

**Future Improvements**:
- Consider movement patterns (if accelerometer available)
- Validate against session start patterns
- Account for different warm-up styles

---

### 2. Cool-down Length ❄️

**Definition**: Duration of the cool-down period at the end of a squash session.

**Data Source**: Heart rate data from chest strap or watch sensor.

**Current Logic** (v1.0):
1. Analyzes last 20% of session
2. Identifies decreasing HR pattern
3. Calculates duration based on HR drop rate

**Formula**: 
```
cool_down_period = last 20% of session where HR decreases continuously
```

**Status**: ⚠️ Often returns 0 - many players skip cool-down

**Known Issues**:
- Many players skip cool-down entirely
- 20% threshold is arbitrary
- May confuse natural HR drop with intentional cool-down
- Requires distinct decreasing pattern

**Future Improvements**:
- Reduce to last 5-10 minutes only
- Return 0 if no clear decreasing pattern (expected behavior)
- Zone-based approach (detect Zone 1/2 in last portion)
- Consider accepting 0 as valid result

---

### 3. Number of Games 🎮

**Definition**: Total count of complete games played during the session.

**Data Source**: Heart rate data from chest strap or watch sensor.

**Current Logic** (v1.0):
1. Identifies rest periods > 2 minutes in duration
2. Counts distinct rest periods
3. Adds 1 (assuming rest between games, not after last game)

**Formula**: 
```
games = count(rest_periods > 2_min) + 1
```

**Status**: ✅ Working - High confidence (~1.0)

**Future Improvements**:
- Cross-reference with rally detection
- Account for training scenarios with structured games

---

### 4. Number of Rallies 🏸

**Definition**: Total count of rally periods where active play occurred.

**Data Source**: Heart rate data from chest strap or watch sensor.

**Current Logic** (v3.2 - drop-based detection):
1. Smoothes HR data with 10-second rolling average
2. Tracks peak HR in last 15 seconds for each data point
3. Detects when HR drops by 1+ bpm from recent peak
4. Creates rally boundary when drop is sustained for 1+ seconds
5. Skips warm-up period (first ~5 minutes)
6. Creates rally segments from boundaries
7. Filters rallies: duration between 2-120 seconds
8. Applies minimum 2-second duration filter

**Formula**: 
```
hr_smooth = rolling_average(hr, window=10s)
recent_peak = max(hr_smooth[i-15:i])
drop = recent_peak - hr_smooth[i]
boundary = when(drop >= 1bpm for >= 1second)
rallies = segments_from_boundaries
filtered = rallies where 2s <= duration <= 120s
```

**Status**: ✅ **Working** - Detecting 60-70 rallies for 81-minute sessions (high confidence ~0.79-1.0)

**Algorithm Evolution**:
- v1.4: Percentage-based threshold (too conservative)
- v2.0-2.3: Zone-based and spike-based approaches (still too conservative)
- v3.0-3.2: Drop-based detection with increasing sensitivity
  - v3.0: 5 bpm drop, 3-20s sustained → 3 rallies
  - v3.1: 2 bpm drop, 3s sustained → 51 rallies
  - v3.2: 1 bpm drop, 1s sustained → 60-70 rallies

**Key Insight**: Rally boundaries are marked by HR drops (player walking to serve) rather than HR spikes.

---

### 5. Total Session Duration ⏱️

**Definition**: Total elapsed time from session start to session end.

**Data Source**: Timestamp data from sensor recording.

**Current Logic** (v1.0):
1. Gets first timestamp from data
2. Gets last timestamp from data
3. Calculates difference in minutes

**Formula**: 
```
duration = (last_timestamp - first_timestamp).total_seconds() / 60
```

**Status**: ✅ Working - Perfect confidence (1.0)

**Future Improvements**: None needed

---

### 6. Total Playing Time ⚡

**Definition**: Total time spent actively playing (excluding warm-up, rest, and cool-down).

**Data Source**: Heart rate zones calculated from heart rate data.

**Current Logic** (v2.0 - Zone-based):
1. Estimates max HR: `220 - age` or `observed_max * 1.05`
2. Calculates HR zone for each data point:
   - Zone 1: 50-60% max HR (rest)
   - Zone 2: 60-70% max HR (light activity)
   - Zone 3: 70-80% max HR (aerobic)
   - Zone 4: 80-90% max HR (hard)
   - Zone 5: 90-100% max HR (maximum)
3. Sums time where HR is in Zone 3, 4, or 5 (active play)

**Formula**: 
```
for each data_point:
    zone = calculate_zone(hr, max_hr)
    
total_playing_time = sum(time_delta where zone in [3, 4, 5])
```

**Status**: ✅ Working - Confidence typically 0.3-0.5

**Future Improvements**:
- Account for warm-up and cool-down zones
- Add metadata: zone distribution breakdown
- Consider sport-specific zone definitions

---

### 7. Total Rest Time 😴

**Definition**: Total time spent resting between points, games, or during breaks.

**Data Source**: Heart rate zones calculated from heart rate data.

**Current Logic** (v1.0 - Zone-based):
1. Uses same zone calculation as Total Playing Time
2. Sums time where HR is in Zone 1 or 2 (rest zones)
3. Excludes warm-up and cool-down periods

**Formula**: 
```
total_rest_time = sum(time_delta where zone in [1, 2] AND not in warmup/cooldown)
```

**Status**: ✅ Working - Confidence typically 0.4-0.5

**Future Improvements**:
- Better warm-up/cool-down exclusion logic
- Distinguish between rest and active recovery (Zone 2 vs Zone 1)

---

### 8. Longest Rally Length 🏆

**Definition**: Duration of the longest continuous rally in the session.

**Data Source**: Heart rate data (relies on rally detection).

**Current Logic** (v1.0 - Capped):
1. Gets all detected rallies from rally detection
2. Filters out rallies longer than 120 seconds (likely merged rallies)
3. Finds maximum duration among filtered rallies
4. Returns actual duration (no multiplication)

**Formula**: 
```
filtered_rallies = [r for r in rallies if duration <= 120s]
longest_rally = max(filtered_rallies, key=duration)
```

**Status**: ✅ **Working** - Realistic values with 120s cap

**Known Characteristics**:
- Typical range: 5-90 seconds
- Average: ~30 seconds
- Maximum reasonable: 120 seconds (2 minutes)
- Longer rallies are likely multiple rallies merged together and are filtered out

**Rationale**:
- Rallies longer than 2 minutes are unrealistic for squash and indicate detection issues
- The cap filters out merged rallies that would skew the metric
- Actual rally duration is returned without arbitrary multipliers

---

### 9. Rallies Per Game 📊 **[WIP]**

**Definition**: Average number of rallies per game.

**Data Source**: Calculated from Number of Rallies and Number of Games.

**Current Logic** (v1.0):
1. Gets total rallies detected
2. Gets number of games
3. Calculates average: rallies / games

**Formula**: 
```
rallies_per_game = number_of_rallies / number_of_games
```

**Status**: ✅ **Working** - Now showing ~12 rallies per game (expected 10-20)

**Status Note**:
- Automatically improved once rally detection was fixed
- Now shows realistic values: ~12 rallies per game

---

### 10. Rest Between Games ⏸️

**Definition**: Average duration of rest periods between games.

**Data Source**: Heart rate data from chest strap or watch sensor.

**Current Logic** (v1.0):
1. Identifies rest periods > 2 minutes in duration
2. Calculates average duration of these periods

**Formula**: 
```
rest_periods = periods where hr in Zone 1/2 and duration > 2_min
avg_rest = mean(duration(rest_periods))
```

**Status**: ✅ Working - High confidence (~1.0)

**Future Improvements**:
- Distinguish between game breaks and training breaks
- Consider adding median in addition to average

---

### 11. Shots Detected 🎾

**Definition**: Total count of shots hit during the session.

**Data Source**: Accelerometer data (X, Y, Z axes).

**Current Logic** (v1.0):
1. Requires accelerometer data (x, y, z axes)
2. Detects acceleration spikes
3. Counts distinct spike events

**Formula**: 
```
acceleration_magnitude = sqrt(x² + y² + z²)
shots = count(peaks in acceleration > threshold)
```

**Status**: ❌ No Data Available - Current dataset lacks accelerometer data

**Requirements**:
- Requires accelerometer data from sensor
- Current FIT file contains only heart rate data

**Future Improvements**:
- Need to acquire data with accelerometer
- Implement peak detection algorithm
- Filter out non-shot movements

---

### 12. Average Playing Heart Rate ❤️

**Definition**: Average heart rate during active play periods (excluding rest).

**Data Source**: Heart rate data filtered by HR zones.

**Current Logic** (v1.0):
1. Uses same zone calculation as Total Playing Time
2. Filters HR values where zone is 3, 4, or 5
3. Calculates mean of filtered HR values

**Formula**: 
```
playing_hr_values = [hr for each point where zone in [3, 4, 5]]
avg_playing_hr = mean(playing_hr_values)
```

**Status**: ✅ Working - Confidence typically 0.7-0.8

**Future Improvements**:
- Provide breakdown by zone (avg HR in Zone 3 vs Zone 4 vs Zone 5)
- Time-weighted average (account for duration in each zone)

---

### 13. Average Rest Heart Rate 💚

**Definition**: Average heart rate during rest periods (excluding warm-up and cool-down).

**Data Source**: Heart rate data filtered by HR zones.

**Current Logic** (v1.0):
1. Uses same zone calculation as Total Rest Time
2. Filters HR values where zone is 1 or 2
3. Excludes warm-up and cool-down portions
4. Calculates mean of filtered HR values

**Formula**: 
```
rest_hr_values = [hr for each point where zone in [1, 2] AND not in warmup/cooldown]
avg_rest_hr = mean(rest_hr_values)
```

**Status**: ✅ Working - Confidence typically 0.2-0.3

**Future Improvements**:
- Improve warm-up/cool-down exclusion
- Distinguish Zone 1 (true rest) vs Zone 2 (active recovery)
- Provide both: avg rest HR and avg active recovery HR

---

## Heart Rate Zone Calculation

**Formula Used**:
```python
def calculate_hr_zones(hr_data, max_hr):
    zones = []
    for hr in hr_data:
        if hr < max_hr * 0.5:
            zones.append(0)  # Below Zone 1
        elif hr < max_hr * 0.6:
            zones.append(1)  # Zone 1 (50-60%)
        elif hr < max_hr * 0.7:
            zones.append(2)  # Zone 2 (60-70%)
        elif hr < max_hr * 0.8:
            zones.append(3)  # Zone 3 (70-80%)
        elif hr < max_hr * 0.9:
            zones.append(4)  # Zone 4 (80-90%)
        else:
            zones.append(5)  # Zone 5 (90-100%)
    return zones
```

**Max HR Estimation**:
- If age is provided: `max_hr = 220 - age`
- Otherwise: `max_hr = observed_max_hr * 1.05`

---

## Priority for Future Improvements

### High Priority
1. ✅ **Fix Rally Detection** (#4) - Completed with drop-based approach (v3.2)
2. **Fix Longest Rally** (#8) - Switch to zone-based approach, remove dependency

### Medium Priority
3. **Improve Cool-down Detection** (#2) - Better pattern recognition or accept 0 as valid
4. **Enhance Zone-Based Metrics** (#6, #7, #12, #13) - Add metadata and breakdowns

### Low Priority
5. **Implement Shot Detection** (#11) - Requires accelerometer data
6. **Refine Game Detection** (#3) - Cross-reference multiple indicators

---

## Notes

- Zone-based metrics (#6, #7, #12, #13) are the most reliable and production-ready
- Rally-related metrics (#4, #8, #9) need significant improvement before relying on results
- Cool-down detection (#2) may correctly return 0 for players who skip cool-down
- Metrics without data (shot detection) cannot be implemented until data is available
