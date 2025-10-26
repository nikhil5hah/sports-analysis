# Sports Performance Analysis Platform

A comprehensive, AI-driven sports performance analysis platform that starts with squash and extends to tennis, badminton, table tennis, and padel. Integrate with smart fitness trackers to get actionable insights for athletes and coaches.

## 🎯 Project Vision

Build a modular, extensible platform that:
- Provides comprehensive performance analysis for racket sports
- Integrates with smart fitness trackers (Garmin, Pixel Watch, etc.)
- Delivers AI-driven insights from historical data
- Supports multiple sports with consistent framework
- Offers native mobile apps and web dashboards

## 🚀 Current Status: MVP Complete ✅

**Phase 1 (Weeks 1-4)**: Foundation & MVP ✅
- Modular metrics framework
- 10+ squash-specific metrics
- Data ingestion (GPX/FIT files)
- Streamlit interface
- Accelerometer/gyroscope support

## 📚 Documentation

**Start here**: [AI Context](./AI_CONTEXT.md) - Complete project overview for AI agents and new developers

**Planning & Design**:
- [Project Plan](./PROJECT_PLAN.md) - 40-week development roadmap
- [Architecture](./ARCHITECTURE.md) - System design and structure

**For Contributors**:
- [Contributing](./CONTRIBUTING.md) - How to add features
- [Quick Start](./QUICK_START.md) - Getting started guide

## ✨ Key Features

### 📊 Metrics Analyzed
- **Warm-up & Cool-down duration** (MM:SS format)
- **Number of games and rallies**
- **Total playing time** (accounting for both players)
- **Longest rally length** (doubled for both players)
- **Rest periods between games**
- **Shot detection** using accelerometer data
- **Performance deterioration points**

### 🎯 Session Context
- **Hand position**: Playing hand vs non-playing hand
- **Session type**: Training vs match
- **Sport-specific**: Different algorithms per sport

### 🔧 Technical Features
- **Modular architecture**: Easy to add new sports or metrics
- **Confidence scoring**: Know how reliable each metric is
- **Data quality assessment**: Automatic validation
- **Historical tracking**: Compare across sessions
- **Export capabilities**: PDF, CSV, Excel

## 📦 Installation

```bash
git clone https://github.com/your-username/sports-analysis.git
cd sports-analysis
pip install -r requirements.txt
```

## 🚀 Quick Start

```bash
# Option 1: Using the run script
python3 run.py

# Option 2: Direct Streamlit
streamlit run frontend/streamlit/app.py
```

Upload your GPX (Strava) or FIT (fitness tracker) files to get started!

## 📁 Project Structure

```
sports-analysis/
├── core/                              # Framework files
│   ├── metrics_framework.py          # Base framework
│   ├── modular_analysis.py          # Analysis orchestrator
│   └── __init__.py
│
├── sports/                            # Sport-specific modules
│   └── squash/
│       └── detectors/
│           ├── event_detection.py    # Event detection
│           ├── performance_analysis.py # Performance analysis
│           ├── additional_metrics.py  # Additional detectors
│           └── __init__.py
│
├── data/                              # Data processing
│   ├── ingestion/
│   │   ├── data_ingestion.py        # GPX/FIT import
│   │   └── __init__.py
│   └── processing/
│       └── sample_squash_session.gpx
│
├── frontend/                           # User interfaces
│   └── streamlit/
│       ├── app.py                    # Streamlit app
│       └── __init__.py
│
├── tests/                              # Test files
│   ├── test_mvp.py
│   └── sample_squash_session.gpx
│
├── run.py                              # Main entry point
├── PROJECT_PLAN.md                     # Detailed roadmap
├── ARCHITECTURE.md                     # System design
├── CONTRIBUTING.md                     # Contribution guide
├── QUICK_START.md                      # Getting started
├── LICENSE                              # MIT License
└── README.md                           # This file
```

## 🗺️ Development Roadmap

### ✅ Phase 1 (Weeks 1-4): Foundation - COMPLETE
- Modular framework established
- Squash metrics implemented
- Streamlit MVP ready

### 📅 Phase 2 (Weeks 5-8): Production Readiness
- Algorithm refinement with real data
- Session storage and persistence
- Historical tracking

### 🎾 Phase 3 (Weeks 9-14): Multi-Sport Expansion
- Tennis support
- Badminton support
- Table tennis support
- Padel support

### 🤖 Phase 4 (Weeks 15-22): AI Integration
- Pattern recognition
- Predictive analytics
- Personalized insights
- Training load analysis

### 📱 Phase 5 (Weeks 23-32): Mobile Apps
- iOS native app
- Android native app
- Real-time analysis

### 🌐 Phase 6 (Weeks 33-40): Platform Expansion
- Web dashboard
- Team/coach features
- Social features
- Public API

## 🎯 Current Metrics (Squash)

### Time-Based Metrics
- Warm-up duration (MM:SS)
- Cool-down duration (MM:SS)
- Total session duration
- Total playing time
- Rest between games

### Count-Based Metrics
- Number of games
- Number of rallies
- Rallies per game
- Shots detected

### Intensity Metrics
- Average heart rate
- Maximum heart rate
- Heart rate zones
- Performance deterioration

## 🔮 Future Sports

- 🎾 **Tennis**: Set/game detection, point tracking
- 🏸 **Badminton**: Fast rally analysis, shuttlecock exchanges
- 🏓 **Table Tennis**: Ultra-fast rally detection
- 🎾 **Padel**: Four-player dynamics, wall shots

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- How to add new sports
- How to add new metrics
- Coding standards
- Testing requirements

### High-Priority Contributions
- Tennis detection algorithms
- Badminton detection algorithms
- Table tennis detection algorithms
- Algorithm accuracy improvements

## 📊 Data Sources

### Currently Supported
- **GPX files**: Strava exports
- **FIT files**: Native fitness tracker format
- **Fields**: Heart rate, cadence, speed, GPS, accelerometer, gyroscope

### Future Integrations
- Garmin API
- Apple HealthKit
- Google Fit API
- Polar Flow API
- Suunto Movescount

## 💡 Key Design Principles

1. **Modularity**: Sports and metrics are independent modules
2. **Consistency**: Unified framework across all sports
3. **Extensibility**: Easy to add new sports or metrics
4. **Data-Driven**: All insights based on actual sensor data
5. **Privacy-First**: Local processing, user-controlled data

## 📈 Success Metrics

- Algorithm accuracy: >90% for core metrics
- Processing time: <5 seconds per session
- Mobile battery impact: <5% per session
- User satisfaction: 4.5+ star rating

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with dedication to helping athletes understand and improve their performance through data-driven insights.

---

**Ready to analyze your squash performance? Run `streamlit run app.py` and upload your data!** 🏓
