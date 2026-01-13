import React, {useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import {format, addDays, subDays, isToday, differenceInDays} from 'date-fns';
import {useTaskStore} from '../stores/taskStore';
import {useHabitStore} from '../stores/habitStore';
import {TaskCard} from '../components/TaskCard';
import {HabitCard} from '../components/HabitCard';
import {StatsCard} from '../components/StatsCard';
import {OfflineIndicator} from '../components/OfflineIndicator';
import {useTheme, Spacing, FontSizes} from '../utils/theme';
import {
  GestureHandlerRootView,
  GestureDetector,
  Gesture,
} from 'react-native-gesture-handler';

interface DailyViewScreenProps {
  navigation: any;
}

export const DailyViewScreen = ({navigation}: DailyViewScreenProps) => {
  const theme = useTheme();
  const {
    loadTasks,
    selectedDate,
    setSelectedDate,
    tasks,
    pendingTasks,
    doneTasks,
    skippedTasks,
  } = useTaskStore();
  const {loadHabits, habits, todayCompletions} = useHabitStore();

  const [refreshing, setRefreshing] = React.useState(false);

  useEffect(() => {
    // Load data on mount
    loadTasks(selectedDate);
    loadHabits();
  }, [selectedDate]);

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([loadTasks(selectedDate), loadHabits()]);
    setRefreshing(false);
  };

  const goToPreviousDay = () => {
    const newDate = format(subDays(new Date(selectedDate), 1), 'yyyy-MM-dd');
    setSelectedDate(newDate);
  };

  const goToNextDay = () => {
    const newDate = format(addDays(new Date(selectedDate), 1), 'yyyy-MM-dd');
    setSelectedDate(newDate);
  };

  const goToToday = () => {
    const today = format(new Date(), 'yyyy-MM-dd');
    setSelectedDate(today);
  };

  const getRelativeDateText = () => {
    const today = new Date();
    const selected = new Date(selectedDate);
    const diff = differenceInDays(selected, today);

    if (diff === 0) return 'Today';
    if (diff === -1) return 'Yesterday';
    if (diff === 1) return 'Tomorrow';
    if (diff < 0) return `${Math.abs(diff)} days ago`;
    return `In ${diff} days`;
  };

  // Swipe gesture
  const swipeGesture = Gesture.Pan()
    .onEnd(event => {
      if (event.translationX > 100) {
        // Swipe right - previous day
        goToPreviousDay();
      } else if (event.translationX < -100) {
        // Swipe left - next day
        goToNextDay();
      }
    });

  const completions = todayCompletions();

  const styles = createStyles(theme);

  return (
    <GestureHandlerRootView style={styles.wrapper}>
      <GestureDetector gesture={swipeGesture}>
        <View style={styles.wrapper}>
          {/* Offline Indicator */}
          <OfflineIndicator />

          {/* Today Button - Show when not viewing today */}
          {!isToday(new Date(selectedDate)) && (
            <TouchableOpacity style={styles.todayButton} onPress={goToToday}>
              <Text style={styles.todayButtonText}>Today</Text>
            </TouchableOpacity>
          )}

          <ScrollView
            style={styles.container}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }>
            <View style={styles.content}>
              <View style={styles.dateHeader}>
                <TouchableOpacity
                  onPress={goToPreviousDay}
                  style={styles.dateArrow}>
                  <Text style={styles.dateArrowText}>‹</Text>
                </TouchableOpacity>

                <View style={styles.dateInfo}>
                  <Text style={styles.title}>{getRelativeDateText()}</Text>
                  <Text style={styles.date}>
                    {format(new Date(selectedDate), 'EEEE, MMMM d')}
                  </Text>
                </View>

                <TouchableOpacity onPress={goToNextDay} style={styles.dateArrow}>
                  <Text style={styles.dateArrowText}>›</Text>
                </TouchableOpacity>
              </View>

              {/* Stats Card */}
              <StatsCard date={selectedDate} />

        {/* Tasks Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Tasks ({pendingTasks().length} pending)
          </Text>

          {/* Pending Tasks */}
          {pendingTasks().map(task => (
            <TaskCard key={task.id} task={task} />
          ))}

          {/* Done Tasks */}
          {doneTasks().length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>
                Done ({doneTasks().length})
              </Text>
              {doneTasks().map(task => (
                <TaskCard key={task.id} task={task} />
              ))}
            </>
          )}

          {/* Skipped Tasks */}
          {skippedTasks().length > 0 && (
            <>
              <Text style={styles.subsectionTitle}>
                Skipped ({skippedTasks().length})
              </Text>
              {skippedTasks().map(task => (
                <TaskCard key={task.id} task={task} />
              ))}
            </>
          )}

          {tasks.length === 0 && (
            <Text style={styles.emptyText}>No tasks for today</Text>
          )}
        </View>

        {/* Habits Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            Habits ({completions.size}/{habits.length} completed)
          </Text>

          {habits.map(habit => (
            <HabitCard
              key={habit.id}
              habit={habit}
              isCompletedToday={completions.has(habit.id)}
              onPress={() => navigation.navigate('HabitDetail', {habit})}
            />
          ))}

          {habits.length === 0 && (
            <Text style={styles.emptyText}>No habits yet</Text>
          )}
        </View>
      </View>
    </ScrollView>

          {/* Floating Add Button */}
          <TouchableOpacity
            style={styles.fab}
            onPress={() => navigation.navigate('TaskForm')}
            activeOpacity={0.8}>
            <Text style={styles.fabIcon}>+</Text>
          </TouchableOpacity>
        </View>
      </GestureDetector>
    </GestureHandlerRootView>
  );
};

const createStyles = (theme: any) =>
  StyleSheet.create({
    wrapper: {
      flex: 1,
      backgroundColor: theme.background,
    },
    container: {
      flex: 1,
    },
    content: {
      padding: Spacing.lg,
    },
    dateHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: Spacing.lg,
    },
    dateInfo: {
      flex: 1,
      alignItems: 'center',
    },
    dateArrow: {
      width: 44,
      height: 44,
      justifyContent: 'center',
      alignItems: 'center',
    },
    dateArrowText: {
      fontSize: 32,
      color: theme.primary,
      fontWeight: '300',
    },
    title: {
      fontSize: FontSizes.xxl,
      fontWeight: 'bold',
      color: theme.text,
    },
    date: {
      fontSize: FontSizes.md,
      color: theme.textSecondary,
    },
    todayButton: {
      position: 'absolute',
      top: 10,
      right: Spacing.lg,
      backgroundColor: theme.primary,
      paddingHorizontal: Spacing.md,
      paddingVertical: Spacing.sm,
      borderRadius: 20,
      zIndex: 10,
      shadowColor: '#000',
      shadowOffset: {width: 0, height: 2},
      shadowOpacity: 0.2,
      shadowRadius: 4,
      elevation: 4,
    },
    todayButtonText: {
      color: '#fff',
      fontSize: FontSizes.sm,
      fontWeight: '600',
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
    subsectionTitle: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: theme.textSecondary,
      marginTop: Spacing.md,
      marginBottom: Spacing.sm,
    },
    emptyText: {
      fontSize: FontSizes.md,
      color: theme.textSecondary,
      textAlign: 'center',
      marginTop: Spacing.md,
    },
    fab: {
      position: 'absolute',
      right: Spacing.lg,
      bottom: Spacing.xl,
      width: 56,
      height: 56,
      borderRadius: 28,
      backgroundColor: theme.primary,
      justifyContent: 'center',
      alignItems: 'center',
      shadowColor: '#000',
      shadowOffset: {width: 0, height: 4},
      shadowOpacity: 0.3,
      shadowRadius: 8,
      elevation: 8,
    },
    fabIcon: {
      fontSize: 32,
      color: '#fff',
      fontWeight: '300',
      marginTop: -2,
    },
  });
