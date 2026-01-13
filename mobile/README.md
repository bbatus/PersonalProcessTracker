# Personal Process Tracker - iOS Mobile App

React Native iOS mobile application for personal task and habit tracking with offline support.

## Features

- ✅ **Task Management**: Create, complete, skip, and postpone daily tasks
- 🔥 **Habit Tracking**: Track daily habits with streak counting
- 📊 **Daily Stats**: View completion rates and active streaks
- 📅 **Date Navigation**: Swipe between days or jump to specific dates
- 🔒 **Secure Authentication**: Token-based auth with Keychain storage
- 📴 **Offline Support**: Full offline functionality with automatic sync
- 🌙 **Dark Mode**: Native iOS dark mode support
- 📳 **Haptic Feedback**: Native iOS haptic feedback for actions
- 🔔 **Push Notifications**: Daily habit reminders (coming soon)

## Tech Stack

- **React Native** 0.76.6
- **TypeScript** 5.0.4
- **Zustand** - State management
- **React Navigation** - Navigation
- **Axios** - API client
- **MMKV** - Fast key-value storage
- **Keychain** - Secure token storage
- **date-fns** - Date utilities

## Prerequisites

- **macOS** (required for iOS development)
- **Xcode** 15+ with Command Line Tools
- **Node.js** 18+
- **CocoaPods** (for iOS dependencies)
- **Apple ID** (for device testing)

## Installation

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Install iOS Dependencies

```bash
cd ios
pod install
cd ..
```

### 3. Configure Environment

Create `.env` file in the `mobile` directory:

```bash
API_URL=http://your-backend-url:8000
```

For local development with backend running on your Mac:
```bash
# Find your Mac's local IP address
ifconfig | grep "inet " | grep -v 127.0.0.1

# Use that IP in .env
API_URL=http://192.168.1.XXX:8000
```

## Running the App

### Development Mode (Simulator)

```bash
npm run ios
```

This will:
1. Start the Metro bundler
2. Build the app
3. Launch iOS Simulator
4. Install and run the app

### Running on Physical Device

#### Option 1: Free Apple ID (7-day expiration)

1. Open `mobile/ios/PersonalProcessTracker.xcworkspace` in Xcode
2. Select your iPhone from the device dropdown
3. Go to **Signing & Capabilities** tab
4. Select your Apple ID team
5. Click **Run** (▶️) button

**Note**: Apps signed with free Apple ID expire after 7 days and need to be rebuilt.

#### Option 2: Paid Apple Developer Account ($99/year)

1. Enroll in [Apple Developer Program](https://developer.apple.com/programs/)
2. Create App ID in Apple Developer Portal
3. Create provisioning profile
4. Configure signing in Xcode with your team
5. Build and run on device

The app will remain installed until you manually delete it.

## Building for Distribution

### TestFlight (Beta Testing)

1. Archive the app in Xcode:
   - Product → Archive
2. Upload to App Store Connect
3. Add to TestFlight
4. Invite testers via email

### App Store Release

1. Complete App Store Connect setup
2. Submit for review
3. Once approved, release to App Store

## Project Structure

```
mobile/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── TaskCard.tsx
│   │   ├── HabitCard.tsx
│   │   ├── StatsCard.tsx
│   │   └── OfflineIndicator.tsx
│   ├── screens/         # Screen components
│   │   ├── LoginScreen.tsx
│   │   ├── DailyViewScreen.tsx
│   │   ├── TaskFormScreen.tsx
│   │   ├── HabitDetailScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── stores/          # Zustand state management
│   │   ├── authStore.ts
│   │   ├── taskStore.ts
│   │   └── habitStore.ts
│   ├── services/        # API and storage services
│   │   ├── apiClient.ts
│   │   ├── api.ts
│   │   ├── keychain.ts
│   │   ├── cache.ts
│   │   ├── storage.ts
│   │   └── syncManager.ts
│   ├── navigation/      # Navigation configuration
│   │   └── AppNavigator.tsx
│   ├── utils/           # Utilities
│   │   └── theme.ts
│   └── types/           # TypeScript types
│       └── index.ts
├── ios/                 # iOS native code
├── package.json
└── tsconfig.json
```

## Key Features Implementation

### Authentication
- Secure token storage in iOS Keychain
- Automatic login on app launch
- Token refresh on API calls

### Offline Support
- MMKV cache for fast data access
- Action queue for offline operations
- Automatic sync when connection restored
- Exponential backoff for retries

### Task Management
- Optimistic UI updates
- Cache-first loading strategy
- Swipe gestures for actions
- Date navigation with swipe

### Habit Tracking
- Daily completion logging
- Streak calculation
- Weekly calendar view
- At-risk warnings

## Troubleshooting

### Metro Bundler Issues

```bash
# Clear Metro cache
npm start -- --reset-cache

# Clear watchman
watchman watch-del-all
```

### iOS Build Issues

```bash
# Clean build folder
cd ios
xcodebuild clean
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# Reinstall pods
pod deintegrate
pod install
```

### Network Connection Issues

- Ensure backend is running and accessible
- Check firewall settings
- Verify API_URL in .env file
- For physical device, use Mac's local IP (not localhost)

### Code Signing Issues

- Verify Apple ID is signed in to Xcode
- Check provisioning profile is valid
- Ensure bundle identifier is unique
- For free account, rebuild every 7 days

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- TaskCard.test.tsx
```

## Performance

- App size: ~50MB
- Launch time: <2s
- 60fps animations
- Optimized list rendering with FlatList
- Image caching with react-native-fast-image

## Security

- ✅ HTTPS-only API calls
- ✅ Token stored in iOS Keychain
- ✅ SSL certificate validation
- ✅ Background content blur
- ✅ No sensitive data in logs

## Future Enhancements

- [ ] Push notifications for habit reminders
- [ ] Widgets for quick task view
- [ ] Siri shortcuts integration
- [ ] Apple Watch companion app
- [ ] iCloud sync
- [ ] Share extension for quick task creation

## License

Private - For personal use only

## Support

For issues or questions, contact the development team.
