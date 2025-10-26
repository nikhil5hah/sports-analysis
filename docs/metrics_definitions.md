# Squash Metrics - Definitions & Technical Specifications

**Last Updated**: Current as of latest zone-based implementation  
**Purpose**: Complete technical reference for all squash performance metrics  

---

## Metrics Overview

| # | Metric | Current Status | Data Source | Version |
|---|--------|----------------|-------------|---------|
| 1 | Warm-up Length | ✅ Working | Heart Rate | v1.4 |
| 2 | Cool-down Length | ⚠️ Needs Improvement | Heart Rate | v1.0 |
| 3 | Number of Games | ✅ Working | Heart Rate | v1.0 |
| 4 | Number of Rallies | ⚠️ **WIP** - Low accuracy | Heart Rate | v1.4 |
| 5 | Total Session Duration | ✅ Working | Timestamps | v1.0 |
| 6 | Total Playing Time | ✅ Working | Heart Rate (Zones) | v2.0 |
| 7 | Total Rest Time | ✅ Working | Heart Rate (Zones) | v1.0 |
| 8 | Longest Rally Length | ⚠️ **WIP** - Unreliable | Heart Rate | Fixed |
| 9 | Rallies Per Game | ⚠️ **WIP** - Low accuracy | Calculated | v1.0 |
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

### 4. Number of Rallies 🏸 **[WIP]**

**Definition**: Total count of rally periods where active play occurred.

**Data Source**: Heart rate data from chest strap or watch sensor.

**Current Logic** (v1.4):
1. Calculates baseline HR (average of lower 30% of data)
2. Calculates max HR from observed values
3. Sets threshold at 15% above baseline: `threshold = baseline + 0.15 * (max - baseline)`
4. Identifies continuous periods where HR > threshold
5. Splits long periods at local HR minima
6. Filters rallies: duration between 5-180 seconds
7. Counts valid rallies

**Formula**: 
```
threshold = baseline_hr + 0.15 * (max_hr - baseline_hr)
rally_periods = continuous_segments(hr > threshold)
filtered_rallies = rallies where 5s <= duration <= 180s
```

**Status**: ⚠️ **WIP** - Low accuracy (detecting only ~11 rallies, expected 50-150)

**Known Issues**:
- Threshold too conservative (15% too high)
- Many potential rallies skipped (duration > 180s)
- May merge multiple rallies into one long period
- Baseline calculation may not capture true resting state

**Future Improvements**:
1. **Zone-based approach**: Count transitions into Zone 3/4/5
2. **Dynamic threshold**: Use zone boundaries instead of percentage
3. **Better splitting**: Use HR derivative (rate of change) to detect true pauses
4. **Remove arbitrary duration cap**: Let zone transitions define rallies
5. **Parallel detection**: Use both HR elevation and zone transitions

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

### 8. Longest Rally Length 🏆 **[WIP]**

**Definition**: Duration of the longest continuous rally in the session.

**Data Source**: Heart rate data (currently reliant on rally detection).

**Current Logic** (Fixed - v1.0):
1. Depends on rally detection (metric #4)
2. Finds maximum duration among detected rallies
3. Caps duration at 60 seconds
4. Multiplies by 2 (attempts to account for both players)

**Formula**: 
```
longest_rally = min(max(detected_rallies), 60_seconds) * 2
```

**Status**: ⚠️ **WIP** - Unreliable (depends on rally detection quality)

**Known Issues**:
- Completely depends on rally detection, which is currently unreliable
- Arbitrary 60-second cap
- *2 multiplier is assumption-based, not data-driven
- May show unrealistic values if detection fails

**Future Improvements**:
1. **Direct zone-based measurement**: Find longest continuous period in Zone 3/4/5
2. **Remove dependency**: Don't rely on rally detection
3. **Remove arbitrary cap**: Let data determine max
4. **Return actual duration**: Don't multiply (no evidence for 2x assumption)

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

**Status**: ⚠️ **WIP** - Low accuracy (currently showing ~2.2, expected 10-20)

**Known Issues**:
- Completely dependent on Number of Rallies (#4), which is unreliable
- Shows unrealistic values when rally detection fails

**Future Improvements**:
- Fix rally detection first (#4)
- This metric will automatically improve once rally detection is accurate
- Consider adding confidence threshold (don't calculate if rallies < expected minimum)

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
1. **Fix Rally Detection** (#4) - Most critical, affects multiple dependent metrics
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
