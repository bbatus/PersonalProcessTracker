import notifee, {
  AndroidImportance,
  AuthorizationStatus,
  TriggerType,
  TimestampTrigger,
} from '@notifee/react-native';
import {Habit} from '../types';
import * as storage from './storage';

/**
 * Notification Manager
 * Handles local notifications for habit reminders
 */

// Default reminder time: 9:00 AM
const DEFAULT_REMINDER_HOUR = 9;
const DEFAULT_REMINDER_MINUTE = 0;

/**
 * Request notification permissions from user
 */
export const requestPermissions = async (): Promise<boolean> => {
  try {
    const settings = await notifee.requestPermission();
    return settings.authorizationStatus === AuthorizationStatus.AUTHORIZED;
  } catch (error) {
    console.error('Failed to request notification permissions:', error);
    return false;
  }
};

/**
 * Check if notifications are enabled
 */
export const checkPermissions = async (): Promise<boolean> => {
  try {
    const settings = await notifee.getNotificationSettings();
    return settings.authorizationStatus === AuthorizationStatus.AUTHORIZED;
  } catch (error) {
    console.error('Failed to check notification permissions:', error);
    return false;
  }
};

/**
 * Create notification channel (Android only, but safe to call on iOS)
 */
const createChannel = async () => {
  try {
    await notifee.createChannel({
      id: 'habit-reminders',
      name: 'Habit Reminders',
      importance: AndroidImportance.HIGH,
      sound: 'default',
    });
  } catch (error) {
    console.error('Failed to create notification channel:', error);
  }
};

/**
 * Get reminder time from storage or use default
 */
const getReminderTime = async (): Promise<{hour: number; minute: number}> => {
  try {
    const reminderTime = await storage.getReminderTime();
    if (reminderTime) {
      return reminderTime;
    }
  } catch (error) {
    console.error('Failed to get reminder time:', error);
  }

  return {
    hour: DEFAULT_REMINDER_HOUR,
    minute: DEFAULT_REMINDER_MINUTE,
  };
};

/**
 * Schedule a daily reminder for a habit
 */
export const scheduleHabitReminder = async (habit: Habit): Promise<void> => {
  try {
    // Check if notifications are enabled
    const hasPermission = await checkPermissions();
    if (!hasPermission) {
      console.log('Notifications not enabled, skipping reminder');
      return;
    }

    // Check if notifications are enabled in settings
    const notificationsEnabled = await storage.getNotificationPreference();
    if (!notificationsEnabled) {
      console.log('Notifications disabled in settings');
      return;
    }

    // Create channel (safe to call on iOS)
    await createChannel();

    // Get reminder time
    const {hour, minute} = await getReminderTime();

    // Calculate next trigger time
    const now = new Date();
    const trigger = new Date();
    trigger.setHours(hour, minute, 0, 0);

    // If time has passed today, schedule for tomorrow
    if (trigger <= now) {
      trigger.setDate(trigger.getDate() + 1);
    }

    const triggerConfig: TimestampTrigger = {
      type: TriggerType.TIMESTAMP,
      timestamp: trigger.getTime(),
      repeatFrequency: 'daily',
    };

    // Create notification
    await notifee.createTriggerNotification(
      {
        id: `habit_${habit.id}`,
        title: '🔥 Habit Reminder',
        body: `Don't forget to complete: ${habit.name}`,
        ios: {
          sound: 'default',
          categoryId: 'habit-reminder',
        },
        android: {
          channelId: 'habit-reminders',
          sound: 'default',
          pressAction: {
            id: 'default',
          },
        },
        data: {
          habitId: habit.id,
          habitName: habit.name,
          type: 'habit-reminder',
        },
      },
      triggerConfig,
    );

    console.log(`Scheduled reminder for habit: ${habit.name} at ${hour}:${minute}`);
  } catch (error) {
    console.error('Failed to schedule habit reminder:', error);
  }
};

/**
 * Cancel a habit reminder
 */
export const cancelHabitReminder = async (habitId: string): Promise<void> => {
  try {
    await notifee.cancelNotification(`habit_${habitId}`);
    console.log(`Cancelled reminder for habit: ${habitId}`);
  } catch (error) {
    console.error('Failed to cancel habit reminder:', error);
  }
};

/**
 * Cancel all habit reminders
 */
export const cancelAllReminders = async (): Promise<void> => {
  try {
    await notifee.cancelAllNotifications();
    console.log('Cancelled all reminders');
  } catch (error) {
    console.error('Failed to cancel all reminders:', error);
  }
};

/**
 * Schedule reminders for all habits
 */
export const scheduleAllHabitReminders = async (
  habits: Habit[],
): Promise<void> => {
  try {
    // Cancel existing reminders first
    await cancelAllReminders();

    // Schedule new reminders
    for (const habit of habits) {
      await scheduleHabitReminder(habit);
    }

    console.log(`Scheduled reminders for ${habits.length} habits`);
  } catch (error) {
    console.error('Failed to schedule all habit reminders:', error);
  }
};

/**
 * Update reminder time and reschedule all habits
 */
export const updateReminderTime = async (
  hour: number,
  minute: number,
  habits: Habit[],
): Promise<void> => {
  try {
    // Save new reminder time
    await storage.setReminderTime({hour, minute});

    // Reschedule all reminders
    await scheduleAllHabitReminders(habits);

    console.log(`Updated reminder time to ${hour}:${minute}`);
  } catch (error) {
    console.error('Failed to update reminder time:', error);
  }
};

/**
 * Initialize notification manager
 * Call this on app startup
 */
export const initializeNotifications = async (): Promise<void> => {
  try {
    // Create channel
    await createChannel();

    // Set up notification categories for iOS
    await notifee.setNotificationCategories([
      {
        id: 'habit-reminder',
        actions: [
          {
            id: 'mark-done',
            title: 'Mark as Done',
          },
          {
            id: 'snooze',
            title: 'Remind me later',
          },
        ],
      },
    ]);

    console.log('Notification manager initialized');
  } catch (error) {
    console.error('Failed to initialize notifications:', error);
  }
};
