# Mobile App Development Plan

## Overview

This document outlines the plan for building iOS/Android mobile apps with smartwatch integration for the Squash Analytics platform.

## Architecture

```
┌──────────────────────────────────────┐
│  Mobile App (React Native/Flutter)   │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  UI Layer                      │ │
│  │  - Login/Registration          │ │
│  │  - Session Management          │ │
│  │  - Live Session View           │ │
│  │  - Analytics Dashboard         │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Business Logic                │ │
│  │  - API Client                  │ │
│  │  - State Management            │ │
│  │  - Data Buffering              │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Smartwatch Integration        │ │
│  │  - HealthKit (iOS)             │ │
│  │  - Google Fit / Health         │ │
│  │    Connect (Android)           │ │
│  └────────────────────────────────┘ │
└──────────┬───────────────────────────┘
           │ HTTP/REST
           ↓
┌──────────────────────────────────────┐
│  Backend API (localhost:8000)        │
│  - Authentication                    │
│  - Session Management                │
│  - Sensor Data Storage               │
└──────────────────────────────────────┘
```

## Technology Stack Options

### Option 1: React Native ⭐ RECOMMENDED
**Pros:**
- Single codebase for iOS + Android
- Large community and ecosystem
- JavaScript/TypeScript (familiar)
- Expo for rapid development
- Good smartwatch library support

**Cons:**
- Bridge performance overhead for high-frequency sensor data
- Requires native modules for some watch features

**Key Libraries:**
- `react-native-health` - HealthKit integration
- `react-native-google-fit` - Google Fit integration
- `@react-native-async-storage/async-storage` - Local storage
- `axios` - API calls
- `react-navigation` - Navigation
- `react-native-charts-wrapper` - Visualizations

### Option 2: Flutter
**Pros:**
- Excellent performance
- Beautiful UI with Material Design
- Single codebase
- Growing ecosystem

**Cons:**
- Dart language (less familiar)
- Smaller community than React Native
- Smartwatch integration requires more custom work

### Option 3: Native Development (Swift + Kotlin)
**Pros:**
- Best performance
- Full platform access
- Native smartwatch APIs

**Cons:**
- Two separate codebases
- 2x development time
- More maintenance

## Recommended Approach: React Native with Expo

### Phase 1: Setup and Authentication (Week 1)

**1.1 Project Setup**
```bash
# Install Expo CLI
npm install -g expo-cli

# Create new project
expo init squash-analytics-mobile
cd squash-analytics-mobile

# Install dependencies
npm install axios react-navigation @react-native-async-storage/async-storage
```

**1.2 API Client Setup**
Create API client that connects to `http://YOUR_LOCAL_IP:8000` (use your Mac's local IP, not localhost)

**1.3 Authentication Screens**
- Login screen
- Registration screen
- JWT token storage
- Auto-login on app restart

**1.4 Testing**
- Test registration flow
- Test login flow
- Verify token persistence

### Phase 2: Session Management (Week 2)

**2.1 Session Creation**
- New session form
  - Sport type (default: Squash)
  - Session type (Match/Training)
  - Scoring system
  - Opponent name (optional)

**2.2 Session List View**
- Display all user sessions
- Filter by date, type, sport
- Tap to view details

**2.3 Active Session View**
- Start/stop session
- Display elapsed time
- Show current heart rate (if available)
- End session button

### Phase 3: Smartwatch Integration (Week 3-4)

**3.1 iOS - HealthKit Integration**

Install health library:
```bash
npm install react-native-health
```

Request permissions:
- Heart Rate
- Active Energy (calories)
- Distance
- Steps
- GPS/Location

Stream real-time heart rate during session.

**3.2 Android - Google Fit Integration**

Install Google Fit library:
```bash
npm install react-native-google-fit
```

Request same permissions as iOS.

**3.3 Data Streaming Architecture**

```javascript
// Pseudo-code for sensor streaming
class SensorStreamManager {
  constructor(apiClient, sessionId) {
    this.apiClient = apiClient;
    this.sessionId = sessionId;
    this.buffer = {
      heartRate: [],
      gps: [],
      activity: []
    };
  }

  // Collect sensor data in memory
  onHeartRateUpdate(hr, timestamp) {
    this.buffer.heartRate.push({ heart_rate: hr, time: timestamp });

    // Upload every 30 seconds or 30 readings
    if (this.buffer.heartRate.length >= 30) {
      this.uploadHeartRate();
    }
  }

  async uploadHeartRate() {
    if (this.buffer.heartRate.length === 0) return;

    const data = { data_points: this.buffer.heartRate };
    await this.apiClient.uploadHeartRate(this.sessionId, data);
    this.buffer.heartRate = [];
  }

  // Similar methods for GPS, SpO2, temperature, activity
}
```

**3.4 Buffering Strategy**
- Collect sensor readings in memory
- Upload in batches every 30 seconds
- Handle network failures gracefully
- Retry failed uploads when connection restored

### Phase 4: Score Tracking (Week 5)

**4.1 Point Recording UI**
- Quick buttons: "Me" / "Opponent"
- Score display
- Let button
- Game/set tracking
- Undo last point

**4.2 API Integration**
- Auto-increment point numbers
- Send current score after each point
- Record heart rate at point completion

### Phase 5: Analytics Dashboard (Week 6)

**5.1 Session Summary**
- Total duration
- Average/max heart rate
- Heart rate zones breakdown
- Total distance, steps, calories
- Score summary (if match)

**5.2 Charts and Visualizations**
- Heart rate over time
- HR zone pie chart
- GPS movement map (if available)
- Point-by-point score progression

**5.3 Insights**
- Request insights from backend
- Display recommendations
- HR-score correlation

### Phase 6: Apple Watch App (Week 7-8)

**6.1 WatchOS App Development**
Create companion Watch app using WatchKit:
- Start/stop session from watch
- Display live heart rate
- Quick score recording with Digital Crown
- Haptic feedback for points

**6.2 Watch-iPhone Communication**
Use Watch Connectivity framework to sync data between watch and phone.

### Phase 7: Testing and Polish (Week 9)

**7.1 Testing**
- Test with real squash session
- Verify all sensor data uploads correctly
- Test offline mode and sync
- Battery usage optimization

**7.2 UI/UX Polish**
- Loading states
- Error messages
- Success feedback
- Smooth animations

## Local Development Setup

### Running Backend Locally for Testing

Your backend needs to be accessible from your phone:

**Option 1: Same WiFi Network**
```bash
# On your Mac, find your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Your IP will be something like: 192.168.1.100
# In mobile app, use: http://192.168.1.100:8000
```

**Option 2: Ngrok (Easier)**
```bash
# Install ngrok
brew install ngrok

# Run backend on port 8000
python backend/app.py

# In another terminal, expose it
ngrok http 8000

# Use the https URL in mobile app (e.g., https://abc123.ngrok.io)
```

## Key Implementation Details

### HealthKit Real-Time Heart Rate (iOS)

```javascript
import AppleHealthKit from 'react-native-health';

// Request permissions
const permissions = {
  permissions: {
    read: [
      AppleHealthKit.Constants.Permissions.HeartRate,
      AppleHealthKit.Constants.Permissions.ActiveEnergyBurned,
      AppleHealthKit.Constants.Permissions.DistanceWalkingRunning,
      AppleHealthKit.Constants.Permissions.StepCount,
    ],
  },
};

AppleHealthKit.initHealthKit(permissions, (err, results) => {
  if (err) {
    console.log('Error initializing HealthKit');
    return;
  }

  // Start heart rate observer
  startHeartRateMonitoring();
});

function startHeartRateMonitoring() {
  // Query heart rate every 5 seconds
  setInterval(() => {
    const options = {
      startDate: new Date(Date.now() - 5000).toISOString(),
      endDate: new Date().toISOString(),
    };

    AppleHealthKit.getHeartRateSamples(options, (err, results) => {
      if (results && results.length > 0) {
        const latestHR = results[results.length - 1];
        onHeartRateUpdate(latestHR.value, latestHR.startDate);
      }
    });
  }, 5000);
}
```

### Google Fit Heart Rate (Android)

```javascript
import GoogleFit, { Scopes } from 'react-native-google-fit';

// Configure permissions
const options = {
  scopes: [
    Scopes.FITNESS_ACTIVITY_READ,
    Scopes.FITNESS_BODY_READ,
    Scopes.FITNESS_LOCATION_READ,
  ],
};

// Initialize
GoogleFit.authorize(options)
  .then(() => {
    startHeartRateMonitoring();
  })
  .catch((err) => {
    console.log('Auth error:', err);
  });

function startHeartRateMonitoring() {
  // Subscribe to heart rate updates
  GoogleFit.subscribeToHeartRate((heartRate) => {
    onHeartRateUpdate(heartRate.value, heartRate.startDate);
  });
}
```

## Deployment

### TestFlight (iOS)
1. Enroll in Apple Developer Program ($99/year)
2. Create app in App Store Connect
3. Build IPA using Expo
4. Upload to TestFlight
5. Invite yourself as tester

### Google Play Internal Testing (Android)
1. Create Google Play Developer account ($25 one-time)
2. Create app in Play Console
3. Build APK/AAB using Expo
4. Upload to Internal Testing
5. Install on your Android device

## Troubleshooting

### Common Issues

**Issue: "Cannot connect to backend"**
- Verify backend is running
- Check your local IP address
- Make sure phone and Mac are on same WiFi
- Try ngrok as alternative

**Issue: "HealthKit permissions denied"**
- Request permissions again
- Check iOS Settings > Privacy > Health
- Ensure Info.plist has usage descriptions

**Issue: "High battery drain"**
- Reduce sensor polling frequency
- Upload data in larger batches
- Use background modes efficiently

## Next Steps After Mobile App

1. **Deploy Backend to Cloud** - Make it accessible anywhere
2. **Advanced Analytics** - ML models, predictions
3. **Social Features** - Compare with friends
4. **Coaching Features** - Training plans, recommendations
5. **Video Integration** - Record and analyze match footage

## Resources

- React Native Health: https://github.com/agencyenterprise/react-native-health
- Google Fit API: https://developers.google.com/fit
- HealthKit Documentation: https://developer.apple.com/documentation/healthkit
- Expo Documentation: https://docs.expo.dev
- React Navigation: https://reactnavigation.org

## Development Timeline Estimate

**Minimum Viable Product (MVP):**
- 6-8 weeks for basic iOS + Android app
- Essential features: auth, sessions, HR tracking, score recording

**Full Featured App:**
- 10-12 weeks including Watch app and advanced features

**Solo Development:** Plan for upper end of estimates
**With Help:** Could be done in 4-6 weeks for MVP

---

**Ready to start?** Begin with Phase 1 (Setup and Authentication) and build iteratively. Test each phase thoroughly before moving to the next.
