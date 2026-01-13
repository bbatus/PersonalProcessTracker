import AsyncStorage from '@react-native-async-storage/async-storage';
import {Task, Habit} from '../types';
import {CACHE_TTL} from '../config';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

/**
 * Generic cache set with TTL support
 */
export const set = async <T>(key: string, value: T, ttl?: number): Promise<void> => {
  const entry: CacheEntry<T> = {
    data: value,
    timestamp: Date.now(),
    ttl: ttl || 0,
  };
  await AsyncStorage.setItem(key, JSON.stringify(entry));
};

/**
 * Generic cache get with TTL checking
 */
export const get = async <T>(key: string): Promise<T | null> => {
  const raw = await AsyncStorage.getItem(key);
  if (!raw) {
    return null;
  }

  try {
    const entry: CacheEntry<T> = JSON.parse(raw);

    // Check if expired
    if (entry.ttl > 0) {
      const age = Date.now() - entry.timestamp;
      if (age > entry.ttl) {
        // Expired, remove and return null
        await AsyncStorage.removeItem(key);
        return null;
      }
    }

    return entry.data;
  } catch (error) {
    console.error('Cache parse error:', error);
    await AsyncStorage.removeItem(key);
    return null;
  }
};

/**
 * Remove item from cache
 */
export const remove = async (key: string): Promise<void> => {
  await AsyncStorage.removeItem(key);
};

/**
 * Clear all cache
 */
export const clear = async (): Promise<void> => {
  await AsyncStorage.clear();
};

// ============================================================================
// Task-specific cache methods
// ============================================================================

export const cacheTasks = async (date: string, tasks: Task[]): Promise<void> => {
  const key = `tasks:${date}`;
  await set(key, tasks, CACHE_TTL.TASKS);
};

export const getCachedTasks = async (date: string): Promise<Task[] | null> => {
  const key = `tasks:${date}`;
  return await get<Task[]>(key);
};

// ============================================================================
// Habit-specific cache methods
// ============================================================================

export const cacheHabits = async (habits: Habit[]): Promise<void> => {
  const key = 'habits:all';
  await set(key, habits, CACHE_TTL.HABITS);
};

export const getCachedHabits = async (): Promise<Habit[] | null> => {
  const key = 'habits:all';
  return await get<Habit[]>(key);
};

// ============================================================================
// Stats cache methods
// ============================================================================

export const cacheStats = async (date: string, stats: any): Promise<void> => {
  const key = `stats:${date}`;
  await set(key, stats, CACHE_TTL.STATS);
};

export const getCachedStats = async (date: string): Promise<any | null> => {
  const key = `stats:${date}`;
  return await get(key);
};
