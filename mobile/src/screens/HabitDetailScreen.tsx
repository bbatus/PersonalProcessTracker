import React, {useEffect, useState} from 'react';
import {View, Text, StyleSheet, ScrollView, ActivityIndicator} from 'react-native';
import {format, subDays} from 'date-fns';
import {useHabitStore} from '../stores/habitStore';
import {Habit, StreakInfo} from '../types';
import {getHabitStreak} from '../services/api';
import {useTheme, Spacing, FontSizes} from '../utils/theme';

interface HabitDetailScreenProps {
  route: any;
}

export const HabitDetailScreen = ({route}: HabitDetailScreenProps) => {
  const theme = useTheme();
  const {habit}: {habit: Habit} = route.params;
  const {todayCompletions} = useHabitStore();

  const [streakInfo, setStreakInfo] = useState<StreakInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStreakInfo();
  }, []);

  const loadStreakInfo = async () => {
    try {
      const data = await getHabitStreak(habit.id);
      setStreakInfo(data);
    } catch (error) {
      console.error('Failed to load streak info:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const isCompletedToday = todayCompletions().has(habit.id);
  const showAtRiskWarning = !isCompletedToday && habit.current_streak > 0;

  const styles = createStyles(theme);

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Habit Name */}
        <Text style={styles.habitName}>{habit.name}</Text>
        {habit.description && (
          <Text style={styles.habitDescription}>{habit.description}</Text>
        )}

        {/* At-Risk Warning */}
        {showAtRiskWarning && (
          <View style={styles.warningBanner}>
            <Text style={styles.warningIcon}>⚠️</Text>
            <View style={styles.warningTextContainer}>
              <Text style={styles.warningTitle}>Streak at risk!</Text>
              <Text style={styles.warningText}>
                Complete this habit today to maintain your {habit.current_streak}-day streak
              </Text>
            </View>
          </View>
        )}

        {/* Streak Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {habit.current_streak}
              {habit.current_streak > 3 && ' 🔥'}
            </Text>
            <Text style={styles.statLabel}>Current Streak</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statValue}>{habit.longest_streak}</Text>
            <Text style={styles.statLabel}>Longest Streak</Text>
          </View>
        </View>

        {/* Weekly Calendar */}
        <View style={styles.calendarSection}>
          <Text style={styles.sectionTitle}>Last 7 Days</Text>
          <View style={styles.calendar}>
            {streakInfo?.last_7_days.map((completed, index) => {
              const date = subDays(new Date(), 6 - index);
              const isToday = index === 6;

              return (
                <View key={index} style={styles.calendarDay}>
                  <Text style={styles.dayLabel}>
                    {format(date, 'EEE')}
                  </Text>
                  <View
                    style={[
                      styles.dayCircle,
                      completed && styles.dayCircleCompleted,
                      isToday && styles.dayCircleToday,
                    ]}>
                    {completed && <Text style={styles.checkmark}>✓</Text>}
                  </View>
                  <Text style={styles.dayDate}>{format(date, 'd')}</Text>
                </View>
              );
            })}
          </View>
        </View>

        {/* Completion Status */}
        <View style={styles.statusSection}>
          <Text style={styles.sectionTitle}>Today's Status</Text>
          <View
            style={[
              styles.statusCard,
              isCompletedToday
                ? styles.statusCardCompleted
                : styles.statusCardPending,
            ]}>
            <Text style={styles.statusIcon}>
              {isCompletedToday ? '✓' : '○'}
            </Text>
            <Text style={styles.statusText}>
              {isCompletedToday ? 'Completed' : 'Not completed yet'}
            </Text>
          </View>
        </View>
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
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: theme.background,
    },
    content: {
      padding: Spacing.lg,
    },
    habitName: {
      fontSize: FontSizes.xxl,
      fontWeight: 'bold',
      color: theme.text,
      marginBottom: Spacing.sm,
    },
    habitDescription: {
      fontSize: FontSizes.md,
      color: theme.textSecondary,
      marginBottom: Spacing.lg,
    },
    warningBanner: {
      flexDirection: 'row',
      backgroundColor: '#FFF3CD',
      borderRadius: 8,
      padding: Spacing.md,
      marginBottom: Spacing.lg,
      borderLeftWidth: 4,
      borderLeftColor: '#FF9800',
    },
    warningIcon: {
      fontSize: 24,
      marginRight: Spacing.sm,
    },
    warningTextContainer: {
      flex: 1,
    },
    warningTitle: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: '#856404',
      marginBottom: 4,
    },
    warningText: {
      fontSize: FontSizes.sm,
      color: '#856404',
    },
    statsContainer: {
      flexDirection: 'row',
      gap: Spacing.md,
      marginBottom: Spacing.xl,
    },
    statCard: {
      flex: 1,
      backgroundColor: theme.surface,
      borderRadius: 12,
      padding: Spacing.lg,
      alignItems: 'center',
      borderWidth: 1,
      borderColor: theme.border,
    },
    statValue: {
      fontSize: 32,
      fontWeight: 'bold',
      color: theme.primary,
      marginBottom: Spacing.xs,
    },
    statLabel: {
      fontSize: FontSizes.sm,
      color: theme.textSecondary,
      textAlign: 'center',
    },
    calendarSection: {
      marginBottom: Spacing.xl,
    },
    sectionTitle: {
      fontSize: FontSizes.lg,
      fontWeight: '600',
      color: theme.text,
      marginBottom: Spacing.md,
    },
    calendar: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      backgroundColor: theme.surface,
      borderRadius: 12,
      padding: Spacing.md,
      borderWidth: 1,
      borderColor: theme.border,
    },
    calendarDay: {
      alignItems: 'center',
      flex: 1,
    },
    dayLabel: {
      fontSize: FontSizes.xs,
      color: theme.textSecondary,
      marginBottom: Spacing.xs,
    },
    dayCircle: {
      width: 36,
      height: 36,
      borderRadius: 18,
      borderWidth: 2,
      borderColor: theme.border,
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: Spacing.xs,
    },
    dayCircleCompleted: {
      backgroundColor: theme.primary,
      borderColor: theme.primary,
    },
    dayCircleToday: {
      borderColor: theme.primary,
      borderWidth: 3,
    },
    checkmark: {
      color: '#fff',
      fontSize: 20,
      fontWeight: 'bold',
    },
    dayDate: {
      fontSize: FontSizes.xs,
      color: theme.textSecondary,
    },
    statusSection: {
      marginBottom: Spacing.xl,
    },
    statusCard: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: Spacing.md,
      borderRadius: 8,
      borderWidth: 1,
    },
    statusCardCompleted: {
      backgroundColor: '#E8F5E9',
      borderColor: '#4CAF50',
    },
    statusCardPending: {
      backgroundColor: theme.surface,
      borderColor: theme.border,
    },
    statusIcon: {
      fontSize: 24,
      marginRight: Spacing.sm,
    },
    statusText: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: theme.text,
    },
  });
