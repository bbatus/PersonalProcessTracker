import React, {useEffect} from 'react';
import {StatusBar, useColorScheme} from 'react-native';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {AppNavigator} from './src/navigation/AppNavigator';
import * as notificationManager from './src/services/notificationManager';
import notifee, {EventType} from '@notifee/react-native';

function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';

  useEffect(() => {
    // Initialize notifications
    notificationManager.initializeNotifications();

    // Handle notification press (foreground)
    const unsubscribeForeground = notifee.onForegroundEvent(
      async ({type, detail}) => {
        if (type === EventType.PRESS) {
          console.log('Notification pressed (foreground):', detail.notification);
          // Navigate to Daily View - handled by navigation system
        }
      },
    );

    // Handle notification press (background)
    notifee.onBackgroundEvent(async ({type, detail}) => {
      if (type === EventType.PRESS) {
        console.log('Notification pressed (background):', detail.notification);
        // App will open to Daily View automatically
      }
    });

    return () => {
      unsubscribeForeground();
    };
  }, []);

  return (
    <SafeAreaProvider>
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
      <AppNavigator />
    </SafeAreaProvider>
  );
}

export default App;
