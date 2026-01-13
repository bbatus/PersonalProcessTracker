import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import {QueuedAction, SyncResult} from '../types';
import {STORAGE_KEYS, SYNC_CONFIG} from '../config';
import * as api from './api';
import {setLastSync} from './storage';

/**
 * Sync Manager - Handles offline action queue and background sync
 */

// ============================================================================
// Action Queue Management
// ============================================================================

export const queueAction = async (action: QueuedAction): Promise<void> => {
  try {
    const queue = await getQueuedActions();
    queue.push(action);
    await AsyncStorage.setItem(STORAGE_KEYS.ACTION_QUEUE, JSON.stringify(queue));
  } catch (error) {
    console.error('Failed to queue action:', error);
    throw new Error('Failed to queue offline action');
  }
};

export const getQueuedActions = async (): Promise<QueuedAction[]> => {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEYS.ACTION_QUEUE);
    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    console.error('Failed to get queued actions:', error);
    return [];
  }
};

const removeAction = async (id: string): Promise<void> => {
  const queue = await getQueuedActions();
  const filtered = queue.filter(action => action.id !== id);
  await AsyncStorage.setItem(STORAGE_KEYS.ACTION_QUEUE, JSON.stringify(filtered));
};

export const clearQueue = async (): Promise<void> => {
  await AsyncStorage.removeItem(STORAGE_KEYS.ACTION_QUEUE);
};

// ============================================================================
// Network State Monitoring
// ============================================================================

export const isOnline = async (): Promise<boolean> => {
  const state = await NetInfo.fetch();
  return state.isConnected === true && state.isInternetReachable === true;
};

export const onNetworkChange = (callback: (isConnected: boolean) => void): void => {
  NetInfo.addEventListener(state => {
    const connected = state.isConnected === true && state.isInternetReachable === true;
    callback(connected);
  });
};

// ============================================================================
// Sync Logic
// ============================================================================

export const sync = async (): Promise<SyncResult> => {
  const queue = await getQueuedActions();

  if (queue.length === 0) {
    return {
      success: true,
      syncedCount: 0,
      failedCount: 0,
      errors: [],
    };
  }

  let syncedCount = 0;
  let failedCount = 0;
  const errors: string[] = [];

  // Process actions sequentially
  for (const action of queue) {
    try {
      await processAction(action);
      await removeAction(action.id);
      syncedCount++;
    } catch (error: any) {
      console.error(`Failed to sync action ${action.id}:`, error);

      // Increment retry count
      action.retryCount++;

      if (action.retryCount >= SYNC_CONFIG.MAX_RETRIES) {
        // Max retries reached, remove from queue
        await removeAction(action.id);
        failedCount++;
        errors.push(`Action ${action.type} failed after ${SYNC_CONFIG.MAX_RETRIES} retries`);
      } else {
        // Update retry count in queue
        const queue = await getQueuedActions();
        const updated = queue.map(a => (a.id === action.id ? action : a));
        await AsyncStorage.setItem(STORAGE_KEYS.ACTION_QUEUE, JSON.stringify(updated));
        failedCount++;
        errors.push(`Action ${action.type} failed, will retry`);
      }
    }
  }

  // Update last sync timestamp
  await setLastSync(Date.now());

  return {
    success: failedCount === 0,
    syncedCount,
    failedCount,
    errors,
  };
};

/**
 * Process a single queued action
 */
const processAction = async (action: QueuedAction): Promise<void> => {
  switch (action.type) {
    case 'TASK_UPDATE':
      await api.updateTaskStatus(action.payload.id, action.payload.status);
      break;

    case 'TASK_CREATE':
      await api.createTask(action.payload);
      break;

    case 'HABIT_LOG':
      await api.logHabitCompletion(action.payload.habitId, action.payload.date);
      break;

    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
};

// ============================================================================
// Exponential Backoff for Retries
// ============================================================================

export const calculateBackoffDelay = (retryCount: number): number => {
  // 2^retryCount seconds, capped at MAX_DELAY
  const delay = Math.pow(2, retryCount) * SYNC_CONFIG.BASE_DELAY;
  return Math.min(delay, SYNC_CONFIG.MAX_DELAY);
};

/**
 * Schedule a retry with exponential backoff
 */
export const scheduleRetry = (retryCount: number, callback: () => void): void => {
  const delay = calculateBackoffDelay(retryCount);
  console.log(`Scheduling retry in ${delay}ms`);
  setTimeout(callback, delay);
};

// ============================================================================
// Auto-sync on Network Reconnection
// ============================================================================

let autoSyncEnabled = false;

export const startAutoSync = (): void => {
  if (autoSyncEnabled) {
    return;
  }

  autoSyncEnabled = true;

  onNetworkChange(async isConnected => {
    if (isConnected) {
      console.log('Network reconnected, starting sync...');
      const result = await sync();
      console.log('Sync result:', result);
    }
  });
};

export const stopAutoSync = (): void => {
  autoSyncEnabled = false;
};
