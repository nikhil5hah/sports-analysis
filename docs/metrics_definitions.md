# Squash Metrics - Working Definitions & Status

**Last Updated**: Current as of latest zone-based implementation  
**Purpose**: Single source of truth for all squash metrics  

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
| 6b | Total Rest Time | ✅ Working | Heart Rate (Zones) | v1.0 |
| 7 | Longest Rally Length | ⚠️ **WIP** - Unreliable | Heart Rate | Fixed |
| 8 | Rallies Per Game | ⚠️ **WIP** - Low accuracy | Calculated | v1.0 |
| 9 | Rest Between Games | ✅ Working | Heart Rate | v1.0 |
| 10 | Shots Detected | ❌ No Data Available | Accelerometer | v1.0 |
| 11 | Avg Playing HR | ✅ Working | Heart Rate (Zones) | v1.0 |
| 12 | Avg Rest HR | ✅ Working | Heart Rate (Zones) | v1.0 |

**Key to Status:**
- ✅ = Working well with good confidence
- ⚠️ = Works but needs improvement or has reliability issues
- ❌ = Not working or no data available
- **WIP** = Work in Progress - currently unreliable

---

## Metrics Requiring Improvement

### 4. Number of Rallies 🏸 **[WIP]**

**Current Status**: ⚠️ Low accuracy - detecting only 11 rallies (should be 50-150)

**Current Logic** (v1.4):
- Counts HR elevation periods (15% above baseline)
- Splits long periods at local HR minima
- Duration range: 5-180 seconds

**Issues**:
- Too conservative threshold (only 11 detected vs expected 50-150)
- Long periods being skipped (>180s)
- May merge multiple rallies together

**Next Steps**:
- Implement zone-based transition detection
- Lower threshold or use zone transitions
- Better splitting algorithm

---

### 7. Longest Rally Length 🏆 **[WIP]**

**Current Status**: ⚠️ Unreliable

**Current Logic** (Fixed):
- Maximum rally duration capped at 60 seconds
- Multiplied by 2 (for both players)

**Issues**:
- Depends entirely on rally detection quality
- Cap is arbitrary
- May show unrealistic values if detection is wrong

**Next Steps**:
- Implement zone-based longest continuous period in Zone 3/4/5
- Remove dependency on rally detection
- More accurate direct measurement

---

### 8. Rallies Per Game 📊 **[WIP]**

**Current Status**: ⚠️ Low accuracy (depends on #3 and #4)

**Current Logic** (v1.0):
- Simple division: Number of Rallies / Number of Games

**Issues**:
- Inherits issues from rally detection
- Shows 2.2 rallies/game (unrealistic - should be 10-20)

**Next Steps**:
- Fix rally detection first
- Then this metric will automatically improve

---

### 2. Cool-down Length ❄️

**Current Status**: ⚠️ Often returns 0

**Current Logic** (v1.0):
- Last 20% of session where HR is decreasing

**Issues**:
- Many players skip cool-down
- 20% threshold is arbitrary
- Confuses natural HR drop with cool-down

**Next Steps**:
- Look at last 5-10 minutes only
- Return 0 if no clear pattern
- Zone-based approach

---

## UI Layout for Key Insights

### Column 1: Timings ⏱️
- Total Session Duration
- Warm-up Time
- Total Playing Time
- Total Rest Time (now formatted correctly)
- Total Cool-down Time
- Longest Rally Length **[WIP]**
- Avg Rest Between Games

### Column 2: Games & Rallies 🎾
- Total Number of Games
- Total Number of Rallies **[WIP]**
- Avg Rallies Per Game **[WIP]**
- Total Number of Shots
- Avg Shots Per Rally

### Column 3: Heart Rate ❤️
- Avg Heart Rate
- Max Heart Rate
- Avg Playing Heart Rate
- Avg Rest Heart Rate

---

## Visualizations

### Charts
1. **Session Breakdown** - Pie chart showing time distribution (warm-up, playing, rest, cool-down)
2. **HR Zone Distribution** - Pie chart showing time in each HR zone
3. **Heart Rate Over Time** - Simple line chart
4. **Session Phases Timeline** - **[WIP]** Timeline showing phases (needs improvement)

### Known Issues with Session Phases Timeline
- Currently divides session into equal segments
- Should analyze HR patterns to detect actual phase boundaries
- Needs better game/rest period detection

---

## Priority for Improvements

1. **Fix Rally Detection** (#4) - Most important, affects multiple metrics
2. **Improve Session Phases Timeline** - Better HR analysis needed
3. **Fix Longest Rally** (#7) - Switch to zone-based approach
4. **Improve Cool-down Detection** (#2) - Better pattern matching

---

## Zone-Based Metrics (Working Well)

- **Total Playing Time** (Zone 3, 4, 5) ✅
- **Total Rest Time** (Zone 1, 2) ✅
- **Avg Playing Heart Rate** (Zone 3, 4, 5) ✅
- **Avg Rest Heart Rate** (Zone 1, 2) ✅

These zone-based metrics are reliable and working well!
