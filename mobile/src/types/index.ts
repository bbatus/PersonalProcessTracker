// Task types
export type TaskStatus = 'PENDING' | 'DONE' | 'SKIPPED';

export interface Task {
  id: string;
  title: string;
  description?: string;
  scheduled_date: string; // YYYY-MM-DD
  status: TaskStatus;
  category: Category;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskDTO {
  title: string;
  description?: string;
  scheduled_date: string;
  category_id: string;
}

// Habit types
export type HabitFrequency = 'DAILY';

export interface Habit {
  id: string;
  name: string;
  description?: string;
  frequency: HabitFrequency;
  current_streak: number;
  longest_streak: number;
  created_at: string;
}

export interface HabitLog {
  id: string;
  habit_id: string;
  completed_date: string; // YYYY-MM-DD
  completed_at: string; // ISO timestamp
}

export interface StreakInfo {
  current_streak: number;
  longest_streak: number;
  last_7_days: boolean[]; // [true, false, true, ...]
}

// Category types
export interface Category {
  id: string;
  name: string;
  color: string; // hex color
}

// Stats types
export interface DailyStats {
  date: string;
  total_tasks: number;
  completed_tasks: number;
  skipped_tasks: number;
  completion_rate: number;
  active_streaks: number;
}

export interface WeeklyStats {
  week_start: string;
  week_end: string;
  total_completed: number;
  daily_breakdown: DailyStats[];
}

// Auth types
export interface User {
  id: string;
  username: string;
  email: string;
}

export interface AuthResult {
  success: boolean;
  token?: string;
  user?: User;
  error?: string;
}

// Sync types
export type QueuedActionType = 'TASK_UPDATE' | 'HABIT_LOG' | 'TASK_CREATE';

export interface QueuedAction {
  id: string;
  type: QueuedActionType;
  payload: any;
  timestamp: number;
  retryCount: number;
}

export interface SyncResult {
  success: boolean;
  syncedCount: number;
  failedCount: number;
  errors: string[];
}
