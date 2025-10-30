# Squash Analytics Mobile App

React Native mobile application for tracking squash performance with smartwatch integration.

## Phase 1 - Setup and Authentication (COMPLETE)

This is the initial phase with authentication functionality built and tested.

## Features Implemented

- User registration with validation
- User login with JWT token authentication
- Secure token storage using AsyncStorage
- Auto-login on app restart
- Clean, modern UI with iOS-style design
- Error handling and user feedback

## Project Structure

```
mobile/
├── App.js                          # Main app entry point
├── src/
│   ├── api/
│   │   └── client.js              # API client with auth endpoints
│   ├── screens/
│   │   ├── LoginScreen.js         # Login screen
│   │   ├── RegisterScreen.js      # Registration screen
│   │   └── HomeScreen.js          # Home screen (placeholder)
│   ├── navigation/
│   │   └── AppNavigator.js        # Navigation with auth flow
│   └── utils/
└── package.json
```

## Prerequisites

1. Node.js and npm installed
2. Expo Go app on your iOS/Android device
   - iOS: Download from App Store
   - Android: Download from Play Store
3. Backend API running at `http://192.168.1.35:8000`

## Installation

All dependencies are already installed. If you need to reinstall:

```bash
cd mobile
npm install
```

## Running the App

### Option 1: Using Expo Go (Easiest)

1. Start the Expo development server:
```bash
npm start
```

2. Scan the QR code:
   - iOS: Use Camera app to scan QR code
   - Android: Use Expo Go app to scan QR code

3. The app will load on your device

### Option 2: iOS Simulator (Mac only)

```bash
npm run ios
```

### Option 3: Android Emulator

```bash
npm run android
```

## Testing Authentication

### Test User Credentials

The backend has a test user already created:
- Email: `test@squash.com`
- Password: `test123`

### Testing Steps

1. **Launch the app** - You'll see the Login screen

2. **Quick test login** - Tap "Use test account" button to auto-fill credentials

3. **Login** - Tap "Login" button
   - Should successfully authenticate
   - Navigate to Home screen
   - Display welcome message with user info

4. **Test persistence** - Close and reopen the app
   - Should automatically log you back in (no login screen)
   - Token is persisted in AsyncStorage

5. **Test logout** - Tap "Logout" button
   - Should clear token and return to Login screen

6. **Test registration** - Tap "Sign up" link
   - Fill in new user details
   - Should register and auto-login
   - Navigate to Home screen

7. **Test validation** - Try invalid inputs
   - Empty fields
   - Invalid email format
   - Password mismatch
   - Short password (< 6 chars)

## API Configuration

The app connects to the backend at:
```
http://192.168.1.35:8000
```

To change this, edit `src/api/client.js`:
```javascript
const API_BASE_URL = 'http://YOUR_IP:8000';
```

## Backend Endpoints Used

- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login (returns JWT token)
- `GET /api/auth/me` - Get current user info

## Features Breakdown

### API Client (`src/api/client.js`)

- Axios instance with interceptors
- Automatic token injection in requests
- Token storage in AsyncStorage
- Error handling and retry logic
- Auto-logout on 401 (token expired)

### Login Screen (`src/screens/LoginScreen.js`)

- Email and password inputs
- Form validation
- Loading states
- "Use test account" quick fill button
- Navigation to Register screen

### Register Screen (`src/screens/RegisterScreen.js`)

- Name, email, password, confirm password inputs
- Client-side validation:
  - Email format validation
  - Password length (min 6 chars)
  - Password confirmation match
- Auto-login after successful registration

### Home Screen (`src/screens/HomeScreen.js`)

- Welcome message with user info
- Success indicator (Phase 1 complete)
- Next steps information
- Logout functionality

### Navigation (`src/navigation/AppNavigator.js`)

- Auth check on app startup
- Conditional rendering (Auth stack vs Main stack)
- Auto-login if valid token exists
- Loading screen during auth check

## Troubleshooting

### Cannot connect to backend

1. Verify backend is running:
```bash
curl http://192.168.1.35:8000/health
```

2. Ensure phone and computer are on same WiFi network

3. Check firewall settings (backend port 8000 must be accessible)

4. Try using ngrok for testing:
```bash
ngrok http 8000
# Update API_BASE_URL in src/api/client.js with ngrok URL
```

### Expo server won't start

1. Kill any existing Metro processes:
```bash
pkill -f "expo"
pkill -f "metro"
```

2. Clear Expo cache:
```bash
npx expo start --clear
```

### App won't load on device

1. Make sure Expo Go is updated to latest version
2. Try shaking device and selecting "Reload"
3. Check console for error messages

## Next Steps (Phase 2)

Phase 2 will add Session Management:

- Create new session screen
- Session list view
- Active session screen with timer
- Session details view
- Integration with backend session endpoints

See `docs/MOBILE_APP_PLAN.md` for full roadmap.

## Development Notes

### State Management

Currently using simple React state with callbacks. For Phase 2+, consider:
- React Context for global state
- Redux/MobX for complex state
- React Query for server state

### Styling

Using React Native StyleSheet with:
- Consistent color scheme
- iOS-style components
- Responsive layouts

### Security

- Passwords never stored locally
- JWT tokens stored in encrypted AsyncStorage
- Auto-logout on token expiration
- HTTPS recommended for production

## Built With

- **React Native** - Mobile framework
- **Expo** - Development platform
- **React Navigation** - Navigation library
- **Axios** - HTTP client
- **AsyncStorage** - Local storage

## Testing Checklist

- [x] User can register with new account
- [x] User can login with credentials
- [x] Invalid credentials show error
- [x] Token persists after app restart
- [x] User can logout
- [x] Form validation works
- [x] Loading states display correctly
- [x] Error messages are user-friendly

## Resources

- [React Native Docs](https://reactnative.dev)
- [Expo Docs](https://docs.expo.dev)
- [React Navigation](https://reactnavigation.org)
- [Backend API Docs](../docs/API.md)
- [Mobile App Plan](../docs/MOBILE_APP_PLAN.md)

---

**Status**: Phase 1 Complete - Authentication working end-to-end
**Last Updated**: October 30, 2024
