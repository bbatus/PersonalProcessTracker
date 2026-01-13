import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ScrollView,
  Switch,
  Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import NetInfo from '@react-native-community/netinfo';
import {useAuthStore} from '../stores/authStore';
import {useHabitStore} from '../stores/habitStore';
import * as storage from '../services/storage';
import * as notificationManager from '../services/notificationManager';
import {useTheme, Spacing, FontSizes, BorderRadius} from '../utils/theme';

interface SettingsScreenProps {
  navigation: any;
}

export const SettingsScreen = ({navigation}: SettingsScreenProps) => {
  const theme = useTheme();
  const {user, logout} = useAuthStore();
  const {habits} = useHabitStore();

  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [offlineModeEnabled, setOfflineModeEnabled] = useState(true);
  const [isOnline, setIsOnline] = useState(true);
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null);
  const [reminderTime, setReminderTime] = useState(new Date());
  const [showTimePicker, setShowTimePicker] = useState(false);

  useEffect(() => {
    loadSettings();
    checkConnection();

    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(state.isConnected ?? false);
    });

    return () => unsubscribe();
  }, []);

  const loadSettings = async () => {
    const notifPref = await storage.getNotificationPreference();
    const offlinePref = await storage.getOfflineMode();
    const lastSync = await storage.getLastSyncTimestamp();
    const savedTime = await storage.getReminderTime();

    setNotificationsEnabled(notifPref);
    setOfflineModeEnabled(offlinePref);
    setLastSyncTime(lastSync);

    if (savedTime) {
      const time = new Date();
      time.setHours(savedTime.hour, savedTime.minute, 0, 0);
      setReminderTime(time);
    }
  };

  const checkConnection = async () => {
    const state = await NetInfo.fetch();
    setIsOnline(state.isConnected ?? false);
  };

  const handleNotificationToggle = async (value: boolean) => {
    if (value) {
      // Request permissions if enabling
      const granted = await notificationManager.requestPermissions();
      if (!granted) {
        Alert.alert(
          'Permission Denied',
          'Please enable notifications in your device settings.',
        );
        return;
      }

      // Schedule reminders
      await notificationManager.scheduleAllHabitReminders(habits);
    } else {
      // Cancel all reminders if disabling
      await notificationManager.cancelAllReminders();
    }

    setNotificationsEnabled(value);
    await storage.setNotificationPreference(value);
  };

  const handleTimeChange = (event: any, selectedDate?: Date) => {
    setShowTimePicker(Platform.OS === 'ios');

    if (selectedDate) {
      setReminderTime(selectedDate);
      updateReminderTime(selectedDate);
    }
  };

  const updateReminderTime = async (time: Date) => {
    const hour = time.getHours();
    const minute = time.getMinutes();

    await notificationManager.updateReminderTime(hour, minute, habits);

    Alert.alert(
      'Reminder Time Updated',
      `You will receive reminders at ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`,
    );
  };

  const handleOfflineModeToggle = async (value: boolean) => {
    setOfflineModeEnabled(value);
    await storage.setOfflineMode(value);
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout? All offline data will be cleared.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await logout();
          },
        },
      ],
    );
  };

  const getLastSyncText = () => {
    if (!lastSyncTime) return 'Never';

    const syncDate = new Date(lastSyncTime);
    const now = new Date();
    const diffMinutes = Math.floor(
      (now.getTime() - syncDate.getTime()) / 60000,
    );

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minutes ago`;

    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} days ago`;
  };

  const styles = createStyles(theme);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* User Profile Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Profile</Text>
          <View style={styles.card}>
            <View style={styles.row}>
              <Text style={styles.label}>Username</Text>
              <Text style={styles.value}>{user?.username || 'N/A'}</Text>
            </View>
            <View style={styles.divider} />
            <View style={styles.row}>
              <Text style={styles.label}>Email</Text>
              <Text style={styles.value}>{user?.email || 'N/A'}</Text>
            </View>
          </View>
        </View>

        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          <View style={styles.card}>
            <View style={styles.row}>
              <View style={styles.rowLeft}>
                <Text style={styles.label}>Enable Notifications</Text>
                <Text style={styles.description}>
                  Receive daily reminders for habits
                </Text>
              </View>
              <Switch
                value={notificationsEnabled}
                onValueChange={handleNotificationToggle}
                trackColor={{false: theme.border, true: theme.primary}}
              />
            </View>

            {notificationsEnabled && (
              <>
                <View style={styles.divider} />
                <TouchableOpacity
                  style={styles.row}
                  onPress={() => setShowTimePicker(true)}>
                  <Text style={styles.label}>Reminder Time</Text>
                  <Text style={styles.value}>
                    {reminderTime.getHours().toString().padStart(2, '0')}:
                    {reminderTime.getMinutes().toString().padStart(2, '0')}
                  </Text>
                </TouchableOpacity>

                {showTimePicker && (
                  <DateTimePicker
                    value={reminderTime}
                    mode="time"
                    display="spinner"
                    onChange={handleTimeChange}
                  />
                )}
              </>
            )}
          </View>
        </View>

        {/* Offline Mode Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Offline Mode</Text>
          <View style={styles.card}>
            <View style={styles.row}>
              <View style={styles.rowLeft}>
                <Text style={styles.label}>Enable Offline Mode</Text>
                <Text style={styles.description}>
                  Cache data for offline access
                </Text>
              </View>
              <Switch
                value={offlineModeEnabled}
                onValueChange={handleOfflineModeToggle}
                trackColor={{false: theme.border, true: theme.primary}}
              />
            </View>
          </View>
        </View>

        {/* App Info Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>App Info</Text>
          <View style={styles.card}>
            <View style={styles.row}>
              <Text style={styles.label}>Version</Text>
              <Text style={styles.value}>1.0.0</Text>
            </View>
            <View style={styles.divider} />
            <View style={styles.row}>
              <Text style={styles.label}>Connection Status</Text>
              <View style={styles.statusBadge}>
                <View
                  style={[
                    styles.statusDot,
                    {backgroundColor: isOnline ? '#4CAF50' : '#F44336'},
                  ]}
                />
                <Text style={styles.value}>
                  {isOnline ? 'Connected' : 'Offline'}
                </Text>
              </View>
            </View>
            <View style={styles.divider} />
            <View style={styles.row}>
              <Text style={styles.label}>Last Sync</Text>
              <Text style={styles.value}>{getLastSyncText()}</Text>
            </View>
          </View>
        </View>

        {/* Logout Button */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const createStyles = (theme: any) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.background,
    },
    content: {
      padding: Spacing.lg,
    },
    section: {
      marginBottom: Spacing.xl,
    },
    sectionTitle: {
      fontSize: FontSizes.lg,
      fontWeight: '600',
      color: theme.text,
      marginBottom: Spacing.md,
    },
    card: {
      backgroundColor: theme.card,
      borderRadius: BorderRadius.md,
      padding: Spacing.md,
    },
    row: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: Spacing.xs,
    },
    rowLeft: {
      flex: 1,
      marginRight: Spacing.md,
    },
    label: {
      fontSize: FontSizes.md,
      fontWeight: '500',
      color: theme.text,
      marginBottom: 2,
    },
    description: {
      fontSize: FontSizes.sm,
      color: theme.textSecondary,
    },
    value: {
      fontSize: FontSizes.md,
      color: theme.textSecondary,
    },
    divider: {
      height: 1,
      backgroundColor: theme.border,
      marginVertical: Spacing.sm,
    },
    statusBadge: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    statusDot: {
      width: 8,
      height: 8,
      borderRadius: 4,
      marginRight: Spacing.xs,
    },
    logoutButton: {
      backgroundColor: theme.error,
      borderRadius: BorderRadius.md,
      padding: Spacing.md,
      alignItems: 'center',
      marginTop: Spacing.xl,
    },
    logoutText: {
      color: '#FFFFFF',
      fontSize: FontSizes.md,
      fontWeight: '600',
    },
  });
