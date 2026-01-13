import React, {useEffect} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {ActivityIndicator, View} from 'react-native';
import {useAuthStore} from '../stores/authStore';
import {LoginScreen} from '../screens/LoginScreen';
import {DailyViewScreen} from '../screens/DailyViewScreen';
import {SettingsScreen} from '../screens/SettingsScreen';
import {TaskFormScreen} from '../screens/TaskFormScreen';
import {HabitDetailScreen} from '../screens/HabitDetailScreen';

const Stack = createNativeStackNavigator();

export const AppNavigator = () => {
  const {token, isLoading, checkAuth} = useAuthStore();

  useEffect(() => {
    // Check authentication on app launch
    checkAuth();
  }, []);

  // Show loading screen while checking auth
  if (isLoading) {
    return (
      <View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {token ? (
        // Authenticated - Main App Stack
        <Stack.Navigator>
          <Stack.Screen
            name="DailyView"
            component={DailyViewScreen}
            options={{
              title: 'Today',
              headerLargeTitle: true,
            }}
          />
          <Stack.Screen
            name="TaskForm"
            component={TaskFormScreen}
            options={{
              title: 'New Task',
              presentation: 'modal',
            }}
          />
          <Stack.Screen
            name="HabitDetail"
            component={HabitDetailScreen}
            options={{
              title: 'Habit Details',
            }}
          />
          <Stack.Screen
            name="Settings"
            component={SettingsScreen}
            options={{
              title: 'Settings',
              presentation: 'modal',
            }}
          />
        </Stack.Navigator>
      ) : (
        // Not Authenticated - Auth Stack
        <Stack.Navigator screenOptions={{headerShown: false}}>
          <Stack.Screen name="Login" component={LoginScreen} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
};
