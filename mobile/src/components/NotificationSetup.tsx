import React, {useEffect, useState} from 'react';
import {View, Text, StyleSheet, TouchableOpacity, Alert} from 'react-native';
import * as notificationManager from '../services/notificationManager';
import {useTheme, Spacing, FontSizes} from '../utils/theme';

interface NotificationSetupProps {
  onComplete?: () => void;
}

export const NotificationSetup: React.FC<NotificationSetupProps> = ({
  onComplete,
}) => {
  const theme = useTheme();
  const [hasPermission, setHasPermission] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkPermissions();
  }, []);

  const checkPermissions = async () => {
    const permission = await notificationManager.checkPermissions();
    setHasPermission(permission);
    setIsChecking(false);
  };

  const requestPermissions = async () => {
    const granted = await notificationManager.requestPermissions();
    setHasPermission(granted);

    if (granted) {
      Alert.alert(
        'Notifications Enabled',
        'You will receive daily reminders for your habits.',
        [{text: 'OK', onPress: onComplete}],
      );
    } else {
      Alert.alert(
        'Notifications Disabled',
        'You can enable notifications later in Settings.',
        [{text: 'OK', onPress: onComplete}],
      );
    }
  };

  const styles = createStyles(theme);

  if (isChecking) {
    return null;
  }

  if (hasPermission) {
    return null;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.icon}>🔔</Text>
      <Text style={styles.title}>Enable Notifications</Text>
      <Text style={styles.description}>
        Get daily reminders to complete your habits and stay on track with your
        goals.
      </Text>

      <TouchableOpacity style={styles.button} onPress={requestPermissions}>
        <Text style={styles.buttonText}>Enable Notifications</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.skipButton} onPress={onComplete}>
        <Text style={styles.skipButtonText}>Maybe Later</Text>
      </TouchableOpacity>
    </View>
  );
};

const createStyles = (theme: any) =>
  StyleSheet.create({
    container: {
      padding: Spacing.xl,
      alignItems: 'center',
    },
    icon: {
      fontSize: 64,
      marginBottom: Spacing.lg,
    },
    title: {
      fontSize: FontSizes.xl,
      fontWeight: 'bold',
      color: theme.text,
      marginBottom: Spacing.md,
      textAlign: 'center',
    },
    description: {
      fontSize: FontSizes.md,
      color: theme.textSecondary,
      textAlign: 'center',
      marginBottom: Spacing.xl,
      lineHeight: 22,
    },
    button: {
      backgroundColor: theme.primary,
      paddingHorizontal: Spacing.xl,
      paddingVertical: Spacing.md,
      borderRadius: 8,
      marginBottom: Spacing.md,
      width: '100%',
      alignItems: 'center',
    },
    buttonText: {
      color: '#fff',
      fontSize: FontSizes.md,
      fontWeight: '600',
    },
    skipButton: {
      paddingVertical: Spacing.sm,
    },
    skipButtonText: {
      color: theme.textSecondary,
      fontSize: FontSizes.md,
    },
  });
