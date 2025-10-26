# Squash Performance Analysis MVP - Quick Start Guide

## 🚀 Getting Started

Your squash performance analysis MVP is ready! Here's how to use it:

### 1. Run the Application

```bash
cd /Users/nikhilshah/Projects/sports-analysis
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 2. Using Your Own Data

#### Option A: Strava Export (Recommended)
1. Go to your Strava activity
2. Click the "..." menu → "Export GPX"
3. Upload the GPX file in the Streamlit app
4. Configure your session settings:
   - **Watch Position**: Was it on your playing hand or non-playing hand?
   - **Session Type**: Training or match?

#### Option B: Direct FIT File
1. Export FIT file directly from your Pixel Watch 3
2. Upload the FIT file in the Streamlit app
3. Configure session settings

### 3. Sample Data Testing

If you want to test the app first:
1. Click "Generate Sample Data" in the app
2. This creates a realistic 45-minute squash session with:
   - 5-minute warm-up
   - Multiple rallies and rest periods
   - Performance deterioration in the final 10 minutes

## 📊 What You'll See

### Session Overview
- **Duration**: Total session time
- **Average Heart Rate**: Overall intensity
- **Max Heart Rate**: Peak intensity
- **Total Rallies**: Number of rally periods detected

### Key Insights
- **Performance Deterioration**: When your performance started declining
- **Warm-up Duration**: How long your warm-up lasted
- **Recovery Patterns**: How well you recovered between rallies

### Visualizations
- **Heart Rate Over Time**: With warm-up and deterioration points marked
- **Intensity Zones**: Time spent in different heart rate zones
- **Rally Analysis**: Duration and intensity trends over time
- **Performance Trends**: Overall performance score and trends

## 🔧 Technical Details

### Algorithms Used

#### Event Detection
- **Warm-up Detection**: Identifies gradual HR increase with low variability
- **Rally Detection**: Finds periods of elevated heart rate and movement
- **Shot Detection**: Different algorithms for playing vs non-playing hand
- **Rest Period Detection**: Identifies recovery periods between rallies

#### Performance Analysis
- **Deterioration Detection**: Uses HR drift, rally performance, and recovery rates
- **Intensity Zones**: Calculates time in recovery, aerobic, threshold, and anaerobic zones
- **Recovery Analysis**: Measures recovery rates and consistency
- **Performance Scoring**: Overall score based on multiple metrics

### Hand Position Impact
- **Playing Hand**: Detects shots using cadence spikes and movement patterns
- **Non-Playing Hand**: Uses movement variability and sudden changes

### Session Type Impact
- **Training**: Focuses on technique and endurance patterns
- **Match**: Emphasizes intensity and competitive performance

## 🎯 Key Features

✅ **Automatic Event Detection**: No manual input needed for rallies, shots, rest periods
✅ **Performance Deterioration**: Identifies when you start to fatigue
✅ **Heart Rate Zone Analysis**: Shows training intensity distribution
✅ **Recovery Analysis**: Measures how well you recover between efforts
✅ **Visual Dashboard**: Clear, easy-to-understand charts and metrics
✅ **Multiple Data Sources**: Supports GPX (Strava) and FIT files
✅ **Hand Position Awareness**: Different algorithms for different watch positions

## 🔮 Future Enhancements

This MVP provides the foundation for:
- **Multi-sport Support**: Expand to tennis, badminton, etc.
- **Mobile App**: Native iOS/Android app
- **Real-time Analysis**: Live performance monitoring
- **Coaching Integration**: Share insights with coaches
- **Historical Tracking**: Compare sessions over time
- **Advanced Metrics**: Shot accuracy, court coverage, etc.

## 🐛 Troubleshooting

### Common Issues
1. **No rallies detected**: Check if heart rate data is present and session is long enough
2. **Incorrect warm-up detection**: Ensure you have a gradual HR increase at the start
3. **File upload errors**: Make sure file is GPX or FIT format

### Data Requirements
- **Minimum session length**: 10 minutes
- **Required data**: Heart rate (essential), cadence (helpful)
- **Data frequency**: 1-second intervals work best

## 📈 Understanding Your Results

### Performance Deterioration
- **Early deterioration** (< 20 minutes): May indicate insufficient warm-up or fitness level
- **Late deterioration** (> 30 minutes): Normal for longer sessions
- **No deterioration**: Excellent endurance or low-intensity session

### Heart Rate Zones
- **Recovery** (50-60% max): Active recovery, warm-up/cool-down
- **Aerobic** (60-70% max): Base fitness, endurance building
- **Threshold** (70-85% max): Lactate threshold, sustainable high intensity
- **Anaerobic** (85-100% max): Maximum effort, short bursts

### Rally Analysis
- **Consistent duration**: Good pacing and technique
- **Decreasing duration**: Possible fatigue or tactical changes
- **High intensity**: Competitive match or high-intensity training

---

**Ready to analyze your squash performance? Run `streamlit run app.py` and upload your data!** 🏓
