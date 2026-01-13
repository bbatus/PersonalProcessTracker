import {create} from 'zustand';
import {format} from 'date-fns';
import {Habit, HabitLog} from '../types';
import * as api from '../services/api';
import * as cache from '../services/cache';
import * as syncManager from '../services/syncManager';
import * as notificationManager from '../services/notificationManager';

interface HabitState {
  habits: Habit[];
  habitLogs: Map<string, HabitLog[]>; // habitId -> logs
  isLoading: boolean;
  error: string | null;

  // Actions
  loadHabits: () => Promise<void>;
  logCompletion: (habitId: string) => Promise<void>;
  getHabitLogs: (habitId: string) => Promise<void>;

  // Computed
  todayCompletions: () => Set<string>;
  activeStreaks: () => number;
}

export const useHabitStore = create<HabitState>((set, get) => ({
  habits: [],
  habitLogs: new Map(),
  isLoading: false,
  error: null,

  /**
   * Load all habits (cache-first)
   */
  loadHabits: async () => {
    set({isLoading: true, error: null});

    try {
      // Try cache first
      const cachedHabits = cache.getCachedHabits();
      if (cachedHabits) {
        set({habits: cachedHabits, isLoading: false});
      }

      // Fetch from API in background
      const habits = await api.getHabits();

      // Update cache
      cache.cacheHabits(habits);

      // Update state
      set({habits, isLoading: false});

      // Schedule notifications for all habits
      await notificationManager.scheduleAllHabitReminders(habits);
    } catch (error: any) {
      console.error('Load habits error:', error);

      // If we have cached data, keep showing it
      const cachedHabits = cache.getCachedHabits();
      if (cachedHabits) {
        set({
          habits: cachedHabits,
          isLoading: false,
          error: 'Using cached data. Unable to refresh.',
        });
      } else {
        set({
          isLoading: false,
          error: error.message || 'Failed to load habits',
        });
      }
    }
  },

  /**
   * Log habit completion for today (optimistic update)
   */
  logCompletion: async (habitId: string) => {
    const {habits} = get();
    const habit = habits.find(h => h.id === habitId);

    if (!habit) {
      return;
    }

    const today = format(new Date(), 'yyyy-MM-dd');

    // Optimistic update - increment streak
    const updatedHabit = {
      ...habit,
      current_streak: habit.current_streak + 1,
      longest_streak: Math.max(habit.longest_streak, habit.current_streak + 1),
    };

    const updatedHabits = habits.map(h => (h.id === habitId ? updatedHabit : h));

    set({habits: updatedHabits});
    cache.cacheHabits(updatedHabits);

    try {
      // Call API
      await api.logHabitCompletion(habitId, today);

      // Fetch updated streak info
      const streakInfo = await api.getHabitStreak(habitId);

      // Update with actual streak from server
      const finalHabit = {
        ...habit,
        current_streak: streakInfo.current_streak,
        longest_streak: streakInfo.longest_streak,
      };

      const finalHabits = habits.map(h => (h.id === habitId ? finalHabit : h));

      set({habits: finalHabits});
      cache.cacheHabits(finalHabits);

      // Cancel today's reminder since habit is completed
      await notificationManager.cancelHabitReminder(habitId);
    } catch (error: any) {
      console.error('Log completion error:', error);

      // Revert on failure
      set({habits, error: 'Failed to log completion'});
      cache.cacheHabits(habits);

      // Check if offline and queue
      const isOnline = await syncManager.isOnline();
      if (!isOnline) {
        await syncManager.queueAction({
          id: `habit_log_${habitId}_${Date.now()}`,
          type: 'HABIT_LOG',
          payload: {habitId, date: today},
          timestamp: Date.now(),
          retryCount: 0,
        });

        // Keep optimistic update
        set({habits: updatedHabits, error: 'Queued for sync'});
      }
    }
  },

  /**
   * Get habit logs for a specific habit
   */
  getHabitLogs: async (habitId: string) => {
    try {
      const streakInfo = await api.getHabitStreak(habitId);

      // Store logs in map (we'll use last_7_days for now)
      const {habitLogs} = get();
      const logs: HabitLog[] = [];

      // Convert last_7_days boolean array to logs
      const today = new Date();
      streakInfo.last_7_days.forEach((completed, index) => {
        if (completed) {
          const date = new Date(today);
          date.setDate(date.getDate() - (6 - index));

          logs.push({
            id: `${habitId}_${format(date, 'yyyy-MM-dd')}`,
            habit_id: habitId,
            completed_date: format(date, 'yyyy-MM-dd'),
            completed_at: date.toISOString(),
          });
        }
      });

      habitLogs.set(habitId, logs);
      set({habitLogs: new Map(habitLogs)});
    } catch (error: any) {
      console.error('Get habit logs error:', error);
      set({error: error.message || 'Failed to load habit logs'});
    }
  },

  /**
   * Get set of habit IDs completed today
   */
  todayCompletions: () => {
    const {habitLogs} = get();
    const today = format(new Date(), 'yyyy-MM-dd');
    const completions = new Set<string>();

    habitLogs.forEach((logs, habitId) => {
      const completedToday = logs.some(log => log.completed_date === today);
      if (completedToday) {
        completions.add(habitId);
      }
    });

    return completions;
  },

  /**
   * Get count of active streaks (streak > 0)
   */
  activeStreaks: () => {
    const {habits} = get();
    return habits.filter(h => h.current_streak > 0).length;
  },
}));
