import AsyncStorage from '@react-native-async-storage/async-storage';
import {STORAGE_KEYS} from '../config';

/**
 * AsyncStorage wrapper for settings and preferences
 */

// ============================================================================
// Notification settings
// ============================================================================

export const getNotificationTime = async (): Promise<string> => {
  const time = await AsyncStorage.getItem(STORAGE_KEYS.NOTIFICATION_TIME);
  return time || '09:00'; // Default 9:00 AM
};

export const setNotificationTime = async (time: string): Promise<void> => {
  await AsyncStorage.setItem(STORAGE_KEYS.NOTIFICATION_TIME, time);
};

// ============================================================================
// Offline mode preference
// ============================================================================

export const getOfflineMode = async (): Promise<boolean> => {
  const mode = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_MODE);
  return mode === 'true';
};

export const setOfflineMode = async (enabled: boolean): Promise<void> => {
  await AsyncStorage.setItem(STORAGE_KEYS.OFFLINE_MODE, enabled.toString());
};

// ============================================================================
// Last sync timestamp
// ============================================================================

export const getLastSync = async (): Promise<number | null> => {
  const timestamp = await AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC);
  return timestamp ? parseInt(timestamp, 10) : null;
};

export const setLastSync = async (timestamp: number): Promise<void> => {
  await AsyncStorage.setItem(STORAGE_KEYS.LAST_SYNC, timestamp.toString());
};

// ============================================================================
// Per-habit notification preferences
// ============================================================================

export const getHabitNotificationEnabled = async (
  habitId: string,
): Promise<boolean> => {
  const key = `habit_notification:${habitId}`;
  const enabled = await AsyncStorage.getItem(key);
  return enabled !== 'false'; // Default to true
};

export const setHabitNotificationEnabled = async (
  habitId: string,
  enabled: boolean,
): Promise<void> => {
  const key = `habit_notification:${habitId}`;
  await AsyncStorage.setItem(key, enabled.toString());
};

// ============================================================================
// Notification preference
// ============================================================================

export const getNotificationPreference = async (): Promise<boolean> => {
  try {
    const value = await AsyncStorage.getItem('notification_preference');
    return value !== 'false'; // Default to true
  } catch (error) {
    console.error('Failed to get notification preference:', error);
    return true;
  }
};

export const setNotificationPreference = async (
  enabled: boolean,
): Promise<void> => {
  try {
    await AsyncStorage.setItem('notification_preference', enabled.toString());
  } catch (error) {
    console.error('Failed to set notification preference:', error);
  }
};

// ============================================================================
// Last sync timestamp
// ============================================================================

export const getLastSyncTimestamp = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem('last_sync_timestamp');
  } catch (error) {
    console.error('Failed to get last sync timestamp:', error);
    return null;
  }
};

export const setLastSyncTimestamp = async (timestamp: string): Promise<void> => {
  try {
    await AsyncStorage.setItem('last_sync_timestamp', timestamp);
  } catch (error) {
    console.error('Failed to set last sync timestamp:', error);
  }
};

// ============================================================================
// Reminder time
// ============================================================================

export const getReminderTime = async (): Promise<{
  hour: number;
  minute: number;
} | null> => {
  try {
    const value = await AsyncStorage.getItem('reminder_time');
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.error('Failed to get reminder time:', error);
    return null;
  }
};

export const setReminderTime = async (time: {
  hour: number;
  minute: number;
}): Promise<void> => {
  try {
    await AsyncStorage.setItem('reminder_time', JSON.stringify(time));
  } catch (error) {
    console.error('Failed to set reminder time:', error);
  }
};
