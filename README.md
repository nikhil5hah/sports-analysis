# Sports Performance Analysis Platform

A comprehensive platform for analyzing squash performance with real-time smartwatch data capture, backend API, and analytics dashboard.

## Overview

This platform combines:
- **Backend API** for real-time data collection from smartwatches
- **Mobile app integration** (coming next) for iOS/Android
- **Analytics dashboard** for visualizing performance metrics
- **Smartwatch support** for comprehensive biometric tracking

## Architecture

```
┌─────────────────────┐
│   Mobile App        │  (Next: iOS/Android)
│   + Smartwatch      │
└──────────┬──────────┘
           │ REST API
           ↓
┌─────────────────────┐
│  FastAPI Backend    │  ✅ COMPLETE
│  localhost:8000     │
└──────────┬──────────┘
           │ PostgreSQL
           ↓
┌─────────────────────┐
│  Supabase Database  │  ✅ CONFIGURED
│  (Cloud)            │
└─────────────────────┘
```

## Current Status

### ✅ Backend API (COMPLETE)
Fully functional REST API with comprehensive smartwatch data support:

**Authentication:**
- User registration and login
- JWT token-based authentication

**Session Management:**
- Create/update/delete training sessions and matches
- Track sport type, scoring system, duration
- Real-time session status

**Sensor Data Capture:**
- ❤️ Heart Rate monitoring with HR zones
- 📍 GPS/Location tracking (lat/long, altitude, speed, bearing)
- 🫁 SpO2 (blood oxygen saturation)
- 🌡️ Skin temperature monitoring
- 👟 Activity metrics (steps, calories, distance, active minutes, floors)
- 📱 Accelerometer/Gyroscope data for movement analysis

**Analytics:**
- Point-by-point score tracking
- Automated insight generation
- HR-score correlation analysis

### 🚧 Next Steps: Mobile & Watch Apps
See `docs/MOBILE_APP_PLAN.md` for detailed implementation plan

### 📊 Analytics Dashboard
Streamlit dashboard available for data visualization (can be updated to use new API)

## Quick Start

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the server
python app.py
```

Server runs at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Streamlit Dashboard

```bash
# Run the dashboard
streamlit run frontend/streamlit/app.py
```

Dashboard runs at: `http://localhost:8501`

## API Endpoints

**Authentication:**
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/me` - Get current user

**Sessions:**
- `POST /api/sessions` - Create session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session

**Sensor Data:**
- `POST /api/sessions/{id}/heart-rate` - Upload heart rate data
- `POST /api/sessions/{id}/gps` - Upload GPS/location data
- `POST /api/sessions/{id}/spo2` - Upload blood oxygen data
- `POST /api/sessions/{id}/temperature` - Upload temperature data
- `POST /api/sessions/{id}/activity` - Upload activity metrics
- `POST /api/sessions/{id}/sensor-data` - Upload accelerometer/gyroscope

**Analytics:**
- `POST /api/sessions/{id}/points` - Record match points
- `POST /api/sessions/{id}/insights` - Generate insights
- `GET /api/sessions/{id}/insights` - Get session insights

See `docs/API.md` for complete API documentation.

## Project Structure

```
sports-analysis/
├── backend/                   # FastAPI backend (COMPLETE)
│   ├── app.py                # Application entry point
│   ├── config.py             # Configuration
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── point.py
│   │   ├── heart_rate_data.py
│   │   ├── gps_data.py
│   │   ├── spo2_data.py
│   │   ├── temperature_data.py
│   │   ├── activity_data.py
│   │   ├── sensor_data.py
│   │   └── insight.py
│   └── api/                  # API endpoints
│       ├── auth.py
│       ├── sessions.py
│       ├── points.py
│       ├── heart_rate.py
│       ├── gps.py
│       ├── spo2.py
│       ├── temperature.py
│       ├── activity.py
│       ├── sensor_data.py
│       └── insights.py
├── frontend/streamlit/        # Analytics dashboard
│   └── app.py
├── core/                      # Analysis engine
│   ├── metrics_framework.py
│   └── modular_analysis.py
├── data/ingestion/            # Data processing
│   └── data_ingestion.py
├── sports/squash/             # Sport-specific detectors
│   └── detectors/
└── docs/                      # Documentation
    ├── API.md                # API reference
    └── MOBILE_APP_PLAN.md    # Mobile development guide
```

## Tech Stack

**Backend:**
- FastAPI (REST API)
- SQLAlchemy (ORM)
- PostgreSQL (Supabase)
- JWT authentication
- Pydantic validation

**Frontend:**
- Streamlit (dashboard)
- Plotly (visualizations)

**Mobile (Coming Next):**
- React Native or Flutter
- Apple Watch / Wear OS integration

## Development

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Create user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Visit interactive docs
open http://localhost:8000/docs
```

### Database

The database schema is automatically created on first run. All tables are hosted on Supabase (cloud PostgreSQL).

### Next Development Phase

Ready to build mobile apps! See `docs/MOBILE_APP_PLAN.md` for:
- iOS/Android app architecture
- Smartwatch integration guide
- Step-by-step implementation plan

## Contributing

This is a personal project for squash performance analysis. Contributions welcome!

## License

Non-Commercial License - See LICENSE file
