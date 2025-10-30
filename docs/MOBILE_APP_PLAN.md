# Mobile App Development Plan

## Overview

This document outlines the plan for building iOS/Android mobile apps with smartwatch integration for the Squash Analytics platform.

## Dual-Mode Scoring Concept 🎯

### Core Innovation: Player Mode + Referee Mode

The app supports **two complementary scoring modes**, making it suitable for both casual play and competitive/coached matches:

#### 1. Player Mode (Watch-Controlled Scoring)
- **Use Case**: Casual play, solo practice, unsupervised matches
- **How it Works**:
  - Player wears Apple Watch during the match
  - Quick-tap buttons on watch face: Me | Let | Opponent
  - Watch collects heart rate data simultaneously
  - Score syncs to phone in real-time via WatchConnectivity
  - All data flows to backend for post-match analysis

**Benefits**:
- Hands-free scoring during play
- No need for separate person to track score
- Continuous biometric data collection
- Minimal interruption to gameplay

#### 2. Referee Mode (Phone-Controlled Scoring)
- **Use Case**: Competitive matches, coached sessions, tournaments
- **How it Works**:
  - Referee/coach uses phone app to track score (already built in Phase 4!)
  - Better UX with larger screen for spectators
  - More accurate scoring with dedicated person
  - Can add notes and observations during play
  - Player still wears watch for biometric data

**Benefits**:
- Higher accuracy for important matches
- Enables coaching insights during play
- Better for tournament/league play
- Referee can focus solely on score tracking

#### 3. Hybrid Mode
- Player wears watch collecting biometrics
- Referee uses phone for score (authoritative)
- Watch score buttons disabled or in "view-only" mode
- Best of both worlds: accurate scoring + full sensor data

### Technical Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                    Dual-Mode Architecture                    │
└─────────────────────────────────────────────────────────────┘

PLAYER MODE:
┌──────────────┐         ┌──────────────┐         ┌──────────┐
│ Apple Watch  │ Watch   │  iPhone App  │  REST   │ Backend  │
│ - Score UI   │ Conn.   │ - Display    │  API    │ - Store  │
│ - HR sensor  │────────▶│ - Sync       │────────▶│ - Analyze│
│ - Haptics    │         │ - Backup UI  │         │          │
└──────────────┘         └──────────────┘         └──────────┘
    PRIMARY                  SECONDARY              DATABASE

REFEREE MODE:
┌──────────────┐         ┌──────────────┐         ┌──────────┐
│ Apple Watch  │ Watch   │  iPhone App  │  REST   │ Backend  │
│ - HR sensor  │ Conn.   │ - Score UI   │  API    │ - Store  │
│ - (disabled) │────────▶│ - Timer      │────────▶│ - Analyze│
│              │         │ - Notes      │         │          │
└──────────────┘         └──────────────┘         └──────────┘
   BIOMETRICS               PRIMARY                DATABASE

HYBRID MODE:
┌──────────────┐         ┌──────────────┐         ┌──────────┐
│ Apple Watch  │ Watch   │  iPhone App  │  REST   │ Backend  │
│ - HR sensor  │ Conn.   │ - Score UI   │  API    │ - Store  │
│ - View score │────────▶│ - Timer      │────────▶│ - Analyze│
│ - Vibrate    │         │ (Referee)    │         │          │
└──────────────┘         └──────────────┘         └──────────┘
  BIOMETRICS +          AUTHORITATIVE             DATABASE
   READ-ONLY              SCORING
```

### Data Flow

Both modes collect the same data for post-match analysis:
- Point-by-point scores (who won each point)
- Game-by-game results (e.g., "11-4 11-3 4-11 12-9")
- Heart rate at each point
- Match duration and timestamps
- Let counts
- Player notes/observations (referee mode only)

### Mode Selection UI

**Session Creation Screen Enhancement**:
```
┌─────────────────────────────────────┐
│ Create Match Session                │
├─────────────────────────────────────┤
│ Sport: [Squash ▼]                   │
│ Scoring: [American (PARS) ▼]        │
│                                     │
│ ┌─ Scoring Mode ─────────────────┐ │
│ │ ○ Player Mode                   │ │
│ │   I'll wear the watch & score   │ │
│ │                                 │ │
│ │ ● Referee Mode                  │ │
│ │   Someone else tracks score     │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Start Match]                       │
└─────────────────────────────────────┘
```

### Implementation Priority

**Already Built** (Phase 4):
- ✅ Phone-based scoring UI (Referee Mode core)
- ✅ Point recording and game management
- ✅ Final score calculation
- ✅ Backend API for points

**To Build** (Phase 6 - Apple Watch App):
- [ ] Apple Watch companion app
- [ ] Watch face score buttons
- [ ] WatchConnectivity integration
- [ ] Mode selector in session creation
- [ ] Conflict resolution (if both try to score)
- [ ] Haptic feedback on watch

**Future Enhancements**:
- [ ] Multi-referee support (scorer + umpire)
- [ ] Voice control for hands-free scoring
- [ ] Automatic score detection via AI (advanced)

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

### Phase 3: Smartwatch Integration (Week 3-4) 🚧 **MULTI-PLATFORM**

This phase supports multiple smartwatch platforms with unified data collection.

#### Platform Support Matrix

| Platform | Watch | Phone App | Integration Library | Development Priority |
|----------|-------|-----------|-------------------|---------------------|
| **Android** | Pixel Watch 3, Galaxy Watch | React Native (Android) | `react-native-health-connect` | **PRIMARY** ⭐ |
| **iOS** | Apple Watch | React Native (iOS) | `react-native-health` | Secondary |
| **Samsung** | Galaxy Watch (Wear OS) | React Native (Android) | Same as Pixel Watch | Tertiary |

**Why Pixel Watch 3 First**:
- Modern Wear OS 4.0
- Health Connect API (unified, standardized)
- Excellent development tools
- Developer's actual test device

**3.1 Android - Health Connect Integration (Pixel Watch 3)**

Install Health Connect library:
```bash
npm install react-native-health-connect
```

Request permissions (AndroidManifest.xml):
```xml
<uses-permission android:name="android.permission.health.READ_HEART_RATE" />
<uses-permission android:name="android.permission.health.WRITE_HEART_RATE" />
<uses-permission android:name="android.permission.health.READ_DISTANCE" />
<uses-permission android:name="android.permission.health.READ_STEPS" />
<uses-permission android:name="android.permission.health.READ_CALORIES_BURNED" />
```

Request permissions in code:
```javascript
import HealthConnect from 'react-native-health-connect';

const permissions = [
  { accessType: 'read', recordType: 'HeartRate' },
  { accessType: 'read', recordType: 'Steps' },
  { accessType: 'read', recordType: 'Distance' },
  { accessType: 'read', recordType: 'TotalCaloriesBurned' },
];

await HealthConnect.requestPermission(permissions);
```

**3.2 iOS - HealthKit Integration (Apple Watch)**

Install HealthKit library:
```bash
npm install react-native-health
cd ios && pod install
```

Request permissions (Info.plist):
```xml
<key>NSHealthShareUsageDescription</key>
<string>We need access to your heart rate during matches</string>
<key>NSHealthUpdateUsageDescription</key>
<string>We save your match data to Health</string>
```

Request permissions in code:
```javascript
import AppleHealthKit from 'react-native-health';

const permissions = {
  permissions: {
    read: ['HeartRate', 'ActiveEnergyBurned', 'DistanceWalkingRunning'],
    write: ['Workout']
  }
};

AppleHealthKit.initHealthKit(permissions, (err) => {
  // Start monitoring
});
```

**3.3 Wear OS Companion App (Kotlin) - For Pixel Watch & Galaxy Watch**

Simple scoring interface on watch:
```kotlin
// ScoreActivity.kt
class ScoreActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_score)

        // Me button
        findViewById<Button>(R.id.btnMe).setOnClickListener {
            recordPoint("me")
            WKInterfaceDevice.current().play(.click) // Haptic
        }

        // Let button
        findViewById<Button>(R.id.btnLet).setOnClickListener {
            recordPoint("let")
        }

        // Opponent button
        findViewById<Button>(R.id.btnOpponent).setOnClickListener {
            recordPoint("opponent")
        }
    }

    private fun recordPoint(winner: String) {
        // Send to phone via Health Connect
        sendDataToPhone(winner)
    }
}
```

**3.4 WatchOS Companion App (Swift) - For Apple Watch**

```swift
// ScoreInterfaceController.swift
import WatchKit
import WatchConnectivity

class ScoreInterfaceController: WKInterfaceController {
    let session = WCSession.default

    @IBAction func meButtonTapped() {
        recordPoint(winner: "me")
    }

    @IBAction func letButtonTapped() {
        recordPoint(winner: "let")
    }

    @IBAction func opponentButtonTapped() {
        recordPoint(winner: "opponent")
    }

    func recordPoint(winner: String) {
        // Send to iPhone
        let message = ["action": "recordPoint", "winner": winner]
        session.sendMessage(message, replyHandler: nil)

        // Haptic feedback
        WKInterfaceDevice.current().play(.click)
    }
}
```

**3.5 Data Streaming Architecture**

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

**3.6 Buffering Strategy**
- Collect sensor readings in memory
- Upload in batches every 30 seconds
- Handle network failures gracefully
- Retry failed uploads when connection restored

**3.7 Development Roadmap for Smartwatch Integration**

**Priority 1: Pixel Watch 3 (Android/Wear OS)** - Week 4, Days 1-3
- Install `react-native-health-connect` library
- Request Health Connect permissions
- Build heart rate monitoring on phone
- Create basic Wear OS app with 3 buttons (Me/Let/Opponent)
- Test data sync: Watch → Phone → Backend
- Test end-to-end scoring from watch

**Priority 2: Apple Watch (iOS/WatchOS)** - Week 4, Days 4-5
- Install `react-native-health` library
- Request HealthKit permissions
- Build heart rate monitoring on phone
- Create WatchOS companion app
- Implement WatchConnectivity sync
- Test end-to-end flow

**Priority 3: Optimization** - Week 5
- Battery optimization (reduce sampling rate)
- Offline mode (queue data when no connection)
- Background sync
- Error recovery and retry logic

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
