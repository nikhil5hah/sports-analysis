# TRacket Wear OS App

Native Wear OS application for real-time squash match tracking on Pixel Watch 3.

## Overview

The TRacket Wear OS app allows players to track their squash matches directly from their smartwatch, recording points, games, and heart rate data in real-time. All data syncs automatically to the TRacket backend and mobile app.

## Features

- **Real-time Point Tracking**: Record points for you or your opponent with a single tap
- **Let Recording**: Mark replayed points as lets
- **Heart Rate Monitoring**: Continuous HR tracking during matches using Health Services API
- **Score Display**: Live score display optimized for round watch faces
- **Game Management**: Track multiple games within a match
- **Undo Functionality**: Revert the last recorded point
- **Offline Support**: Works without internet connection, syncs when available
- **Auto-sync**: Automatic synchronization with backend server

## Technical Stack

- **Language**: Kotlin
- **UI**: Jetpack Compose for Wear OS
- **Architecture**: MVVM pattern
- **Networking**: Retrofit + OkHttp
- **Health Services**: androidx.health.services.client
- **Minimum SDK**: 30 (Wear OS 3.0)
- **Target SDK**: 36

## Project Structure

```
wear-app-project/
├── app/
│   └── src/
│       └── main/
│           ├── java/com/tracket/wear/
│           │   ├── models/          # Data models
│           │   │   ├── HeartRateData.kt
│           │   │   └── PointData.kt
│           │   ├── presentation/    # UI layer
│           │   │   └── MainActivity.kt
│           │   ├── services/        # Business logic
│           │   │   ├── ApiClient.kt
│           │   │   └── HealthServicesManager.kt
│           │   ├── theme/           # UI theming
│           │   │   └── TracketWatchTheme.kt
│           │   └── ui/              # Composables
│           │       └── ScoreTrackingScreen.kt
│           ├── res/
│           │   ├── values/          # Strings, colors, themes
│           │   └── xml/             # Network security config
│           └── AndroidManifest.xml
└── README.md
```

## Setup Instructions

### Prerequisites

1. **Android Studio** (latest version)
2. **Pixel Watch 3** with developer mode enabled
3. **TRacket Backend** running locally
4. **TRacket Mobile App** with active session

### Development Environment Setup

1. **Clone the repository**:
   ```bash
   cd /path/to/sports-analysis
   ```

2. **Open in Android Studio**:
   - Open `wear-app-project` folder in Android Studio
   - Wait for Gradle sync to complete

3. **Configure Dependencies**:
   All dependencies are defined in `app/build.gradle.kts`:
   - Wear OS Compose libraries
   - Health Services API
   - Retrofit for networking
   - Coroutines for async operations

### Watch Setup

1. **Enable Developer Mode on Pixel Watch**:
   - Go to Settings → System → About
   - Tap "Build number" 7 times
   - Go back to Settings → Developer options
   - Enable "Developer options"
   - Enable "ADB debugging"
   - Enable "Wireless debugging"

2. **Connect Watch via ADB**:
   ```bash
   # Add Android SDK platform-tools to PATH
   export ANDROID_HOME=$HOME/Library/Android/sdk
   export PATH=$PATH:$ANDROID_HOME/platform-tools

   # Pair watch (get pairing code from watch Settings → Developer options → Wireless debugging → Pair new device)
   adb pair <WATCH_IP>:<PAIRING_PORT> <PAIRING_CODE>

   # Connect to watch (get IP from watch Settings → Developer options → Wireless debugging)
   adb connect <WATCH_IP>:<PORT>

   # Verify connection
   adb devices
   ```

### Configuration

Before deploying, update the following in `MainActivity.kt`:

1. **Session ID**: Get from active session on mobile app
   ```kotlin
   sessionId = "YOUR_SESSION_ID_HERE"
   ```

2. **Auth Token**: Get from mobile app active session screen
   ```kotlin
   apiClient.saveAuthToken("YOUR_AUTH_TOKEN_HERE")
   ```

3. **Backend URL** (if needed): Update in `ApiClient.kt`
   ```kotlin
   private val baseUrl = "http://YOUR_IP:8000"
   ```

### Deployment

1. **Select Watch as Target**:
   - In Android Studio, ensure your Pixel Watch is selected in the device dropdown
   - The device should show as `<WATCH_IP>:<PORT>`

2. **Build and Deploy**:
   - Click the green Run button (▶️)
   - Or use: Run → Run 'app'

3. **Grant Permissions**:
   - First launch will request BODY_SENSORS permission
   - Grant permission to enable heart rate monitoring

## Usage

### Starting a Match

1. **Start Session on Mobile App**:
   - Open TRacket mobile app
   - Create and start a new squash session
   - Note the Session ID displayed on screen

2. **Launch Watch App**:
   - The TRacket app should appear in your watch app drawer
   - Open the app - it will auto-connect to the session

### Recording Points

- **ME Button** (Green): Tap when you win a point
- **LET Button** (Orange): Tap when a let is played (score doesn't change)
- **OPP Button** (Red): Tap when opponent wins a point
- **UNDO Button** (Gray): Tap to undo the last recorded point
- **Next Button** (Blue): Move to the next game
- **End Button** (Gray): End the match and close the app

### Viewing Data

- **Score**: Displayed prominently in center (ME - OPP)
- **Game Number**: Shown at top (Game 1, Game 2, etc.)
- **Heart Rate**: Live BPM displayed at top with heart icon
- **Sync Status**: Automatic - no indicator needed

### Syncing with Mobile App

Points are automatically sent to the backend. To view on your mobile app:
1. Open the active session screen
2. Tap the "🔄 Refresh Points from Watch" button
3. Score and point history will update

## Architecture Details

### Data Flow

```
Watch UI → ScoreTrackingScreen
  ↓
  Record Point
  ↓
  ApiClient → Backend API
  ↓
  Backend Database
  ↓
  Mobile App (via refresh or auto-poll)
```

### Heart Rate Monitoring

The app uses Health Services API for continuous HR monitoring:
- Measurements taken approximately every 2-3 seconds during activity
- Data buffered in batches of 10 measurements
- Automatic upload to backend when batch is full
- Continues in background while app is in foreground

### Offline Support

The app implements optimistic UI updates:
- Scores update immediately on the watch
- Points are queued for sync if network unavailable
- App continues to function fully offline
- Syncs automatically when connection restored

### Network Security

For local development, HTTP traffic is permitted to specific hosts defined in `network_security_config.xml`:
- 192.168.1.0/24 subnet (local network)
- localhost
- 10.0.2.2 (Android emulator)

**Note**: For production, this should be changed to HTTPS only.

## API Endpoints Used

### POST /api/sessions/{session_id}/points
Records a new point in the match.

**Request Body**:
```json
{
  "winner": "me" | "opponent",
  "score_me_before": 0,
  "score_opponent_before": 0,
  "score_me_after": 1,
  "score_opponent_after": 0,
  "game_number": 1,
  "is_let": "false" | "true"
}
```

### POST /api/sessions/{session_id}/heart-rate
Uploads batch of heart rate measurements.

**Request Body**:
```json
{
  "data_points": [
    {
      "bpm": 145,
      "timestamp": "2025-10-31T16:43:35.220Z"
    }
  ]
}
```

## Troubleshooting

### Watch Not Connecting

1. **Check ADB connection**:
   ```bash
   adb devices
   ```
   - Should show your watch as "device", not "offline" or "unauthorized"

2. **Reconnect wirelessly**:
   ```bash
   adb disconnect  # Disconnect all
   adb connect <WATCH_IP>:<PORT>
   ```

3. **Verify wireless debugging is enabled** on watch

### Points Not Syncing

1. **Check network config**: Ensure backend IP is in `network_security_config.xml`
2. **Check auth token**: Verify token is valid and not expired
3. **Check session ID**: Ensure session exists and is active
4. **View logs**:
   ```bash
   adb -s <WATCH_IP>:<PORT> logcat | grep "TRacket\|okhttp"
   ```

### Heart Rate Not Working

1. **Check permissions**: Go to watch Settings → Apps → TRacket → Permissions
   - BODY_SENSORS should be granted
   - ACTIVITY_RECOGNITION should be granted
   - READ_HEART_RATE should be granted

2. **Verify sensor availability**:
   ```bash
   adb logcat | grep "HealthServices"
   ```

3. **Try restarting the app**

### App Crashes on Launch

1. **Check Gradle sync**: Ensure all dependencies downloaded
2. **Clean and rebuild**:
   - Build → Clean Project
   - Build → Rebuild Project
3. **Check target SDK**: Wear OS 3+ requires SDK 30+

## Known Issues

1. **Manual Refresh Required**: Mobile app requires manual refresh to see watch points
   - **Planned**: Auto-polling every 5 seconds
   - **Workaround**: Tap refresh button

2. **Session ID Hardcoded**: Currently requires updating code with session ID
   - **Planned**: Dynamic session selection from active sessions list
   - **Workaround**: Update MainActivity.kt before each deployment

3. **Auth Token Expiry**: Token expires after 24 hours
   - **Planned**: Token refresh mechanism
   - **Workaround**: Get new token from mobile app and redeploy

## Future Enhancements

### High Priority
- [ ] Auto-refresh on mobile app (polling every 5s)
- [ ] Dynamic session selection on watch
- [ ] Automatic token refresh
- [ ] Better error handling and user feedback

### Medium Priority
- [ ] Watch complications for quick score view
- [ ] Vibration feedback on point recording
- [ ] Score summary at end of game
- [ ] Match statistics view

### Low Priority
- [ ] Multiple sport support (tennis, badminton)
- [ ] Voice commands for hands-free tracking
- [ ] Gesture recognition for point recording
- [ ] Integration with other fitness platforms

## Performance Considerations

- **Battery Impact**: Continuous HR monitoring uses ~5-10% battery per hour
- **Network Usage**: Minimal - only sends small JSON payloads
- **Storage**: App size ~2MB, no local data storage
- **Response Time**: Point recording is instantaneous (< 50ms)

## Security Notes

### Current Implementation (Development)
- HTTP communication allowed for local network
- Auth token stored in SharedPreferences (unencrypted)
- No certificate pinning

### Production Requirements
- Switch to HTTPS only
- Implement encrypted storage for tokens
- Add certificate pinning
- Implement token rotation
- Add request signing

## Contributing

When contributing to the Wear OS app:

1. Follow Kotlin coding conventions
2. Use Jetpack Compose best practices
3. Maintain MVVM architecture
4. Add appropriate logging for debugging
5. Test on actual Pixel Watch hardware
6. Update this README with any new features

## License

See LICENSE file in project root.

## Support

For issues or questions:
- Check troubleshooting section above
- Review logs: `adb logcat | grep "TRacket"`
- Check backend is running: `curl http://192.168.1.35:8000/health`
- Verify mobile app connection

## Version History

### v1.0.0 (2025-10-31)
- Initial release
- Basic point tracking
- Heart rate monitoring
- Offline support
- Manual sync with mobile app
