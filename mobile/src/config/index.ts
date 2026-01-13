import Config from 'react-native-config';

export const API_URL = Config.API_URL || 'http://localhost:8000';
export const ENV = Config.ENV || 'development';

export const CACHE_TTL = {
  TASKS: 5 * 60 * 1000, // 5 minutes
  HABITS: 60 * 60 * 1000, // 1 hour
  STATS: 5 * 60 * 1000, // 5 minutes
};

export const SYNC_CONFIG = {
  MAX_RETRIES: 3,
  BASE_DELAY: 1000, // 1 second
  MAX_DELAY: 30000, // 30 seconds
};

export const KEYCHAIN_SERVICE = 'com.personalprocesstracker.auth';

export const STORAGE_KEYS = {
  ACTION_QUEUE: 'action_queue',
  NOTIFICATION_TIME: 'notification_time',
  OFFLINE_MODE: 'offline_mode',
  LAST_SYNC: 'last_sync',
};
