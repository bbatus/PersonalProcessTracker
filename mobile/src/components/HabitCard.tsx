import React from 'react';
import {View, Text, StyleSheet, TouchableOpacity} from 'react-native';
import {Habit} from '../types';
import {useHabitStore} from '../stores/habitStore';
import {useTheme, Spacing, FontSizes, BorderRadius} from '../utils/theme';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

interface HabitCardProps {
  habit: Habit;
  isCompletedToday: boolean;
  onPress?: () => void;
}

export const HabitCard: React.FC<HabitCardProps> = ({
  habit,
  isCompletedToday,
  onPress,
}) => {
  const theme = useTheme();
  const {logCompletion} = useHabitStore();

  const handleTap = async () => {
    if (!isCompletedToday) {
      ReactNativeHapticFeedback.trigger('impactLight');
      await logCompletion(habit.id);
    } else if (onPress) {
      // If already completed, navigate to detail view
      onPress();
    }
  };

  const getStreakDisplay = () => {
    if (habit.current_streak > 3) {
      return `🔥 ${habit.current_streak}`;
    }
    return habit.current_streak.toString();
  };

  const styles = createStyles(theme);

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={handleTap}
      activeOpacity={0.7}>
      <View style={styles.content}>
        {/* Completion Indicator */}
        <View style={styles.indicator}>
          {isCompletedToday ? (
            <View style={[styles.checkmark, {backgroundColor: theme.success}]}>
              <Text style={styles.checkmarkText}>✓</Text>
            </View>
          ) : (
            <View style={[styles.circle, {borderColor: theme.border}]} />
          )}
        </View>

        {/* Habit Info */}
        <View style={styles.info}>
          <Text style={styles.name}>{habit.name}</Text>
          {habit.description && (
            <Text style={styles.description}>{habit.description}</Text>
          )}
        </View>

        {/* Streak */}
        <View style={styles.streak}>
          <Text style={styles.streakNumber}>{getStreakDisplay()}</Text>
          <Text style={styles.streakLabel}>day streak</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const createStyles = (theme: any) =>
  StyleSheet.create({
    container: {
      backgroundColor: theme.card,
      borderRadius: BorderRadius.md,
      marginBottom: Spacing.sm,
    },
    content: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: Spacing.md,
    },
    indicator: {
      marginRight: Spacing.md,
    },
    checkmark: {
      width: 28,
      height: 28,
      borderRadius: 14,
      justifyContent: 'center',
      alignItems: 'center',
    },
    checkmarkText: {
      color: '#FFFFFF',
      fontSize: FontSizes.md,
      fontWeight: 'bold',
    },
    circle: {
      width: 28,
      height: 28,
      borderRadius: 14,
      borderWidth: 2,
    },
    info: {
      flex: 1,
    },
    name: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: theme.text,
      marginBottom: Spacing.xs,
    },
    description: {
      fontSize: FontSizes.sm,
      color: theme.textSecondary,
    },
    streak: {
      alignItems: 'center',
      marginLeft: Spacing.md,
    },
    streakNumber: {
      fontSize: FontSizes.lg,
      fontWeight: 'bold',
      color: theme.primary,
    },
    streakLabel: {
      fontSize: FontSizes.xs,
      color: theme.textSecondary,
    },
  });
