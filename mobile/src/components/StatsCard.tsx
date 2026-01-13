import React, {useEffect, useState} from 'react';
import {View, Text, StyleSheet, TouchableOpacity, ActivityIndicator} from 'react-native';
import {format} from 'date-fns';
import {useTaskStore} from '../stores/taskStore';
import {useHabitStore} from '../stores/habitStore';
import {getDailyStats} from '../services/api';
import {DailyStats} from '../types';
import {useTheme, Spacing, FontSizes} from '../utils/theme';

interface StatsCardProps {
  date: string;
  onPress?: () => void;
}

export const StatsCard = ({date, onPress}: StatsCardProps) => {
  const theme = useTheme();
  const {tasks} = useTaskStore();
  const {habits} = useHabitStore();

  const [stats, setStats] = useState<DailyStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, [date, tasks, habits]);

  const loadStats = async () => {
    try {
      const data = await getDailyStats(date);
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
      // Calculate stats locally as fallback
      calculateLocalStats();
    } finally {
      setIsLoading(false);
    }
  };

  const calculateLocalStats = () => {
    const completedTasks = tasks.filter(t => t.status === 'DONE').length;
    const totalTasks = tasks.length;
    const completionRate =
      totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    const activeStreaks = habits.filter(h => h.current_streak > 0).length;

    setStats({
      date,
      total_tasks: totalTasks,
      completed_tasks: completedTasks,
      skipped_tasks: tasks.filter(t => t.status === 'SKIPPED').length,
      completion_rate: completionRate,
      active_streaks: activeStreaks,
    });
  };

  const styles = createStyles(theme);

  if (isLoading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="small" color={theme.primary} />
      </View>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={onPress}
      activeOpacity={onPress ? 0.7 : 1}
      disabled={!onPress}>
      <View style={styles.header}>
        <Text style={styles.title}>Today's Progress</Text>
        {onPress && <Text style={styles.viewMore}>View Details ›</Text>}
      </View>

      <View style={styles.statsGrid}>
        {/* Completion Rate */}
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{stats.completion_rate}%</Text>
          <Text style={styles.statLabel}>Completion</Text>
        </View>

        {/* Active Streaks */}
        <View style={styles.statItem}>
          <Text style={styles.statValue}>
            {stats.active_streaks} 🔥
          </Text>
          <Text style={styles.statLabel}>Active Streaks</Text>
        </View>

        {/* Completed Tasks */}
        <View style={styles.statItem}>
          <Text style={styles.statValue}>
            {stats.completed_tasks}/{stats.total_tasks}
          </Text>
          <Text style={styles.statLabel}>Tasks Done</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const createStyles = (theme: any) =>
  StyleSheet.create({
    container: {
      backgroundColor: theme.surface,
      borderRadius: 12,
      padding: Spacing.md,
      marginBottom: Spacing.lg,
      borderWidth: 1,
      borderColor: theme.border,
      shadowColor: '#000',
      shadowOffset: {width: 0, height: 2},
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: Spacing.md,
    },
    title: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: theme.text,
    },
    viewMore: {
      fontSize: FontSizes.sm,
      color: theme.primary,
    },
    statsGrid: {
      flexDirection: 'row',
      justifyContent: 'space-between',
    },
    statItem: {
      flex: 1,
      alignItems: 'center',
    },
    statValue: {
      fontSize: FontSizes.xl,
      fontWeight: 'bold',
      color: theme.primary,
      marginBottom: 4,
    },
    statLabel: {
      fontSize: FontSizes.xs,
      color: theme.textSecondary,
      textAlign: 'center',
    },
  });
