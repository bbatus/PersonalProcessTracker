/**
 * TypeScript types for the application
 */

export interface User {
  id: string;
  username: string;
  email: string;
  email_verified: boolean;
  avatar_url: string | null;
}

export enum TaskStatus {
  PENDING = 'PENDING',
  DONE = 'DONE',
  SKIPPED = 'SKIPPED',
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  notes: string | null;
  status: TaskStatus;
  scheduled_date: string;
  completed_at: string | null;
  estimated_duration: number | null;
  category_id: string | null;
  habit_id: string | null;
  goal_id: string | null;  // NEW
  goal?: Goal;  // NEW - optional nested goal info
  created_at: string;
  updated_at: string;
}

export enum GoalPeriod {
  DAILY = 'DAILY',
  WEEKLY = 'WEEKLY',
  MONTHLY = 'MONTHLY',
  YEARLY = 'YEARLY',
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  period: GoalPeriod;
  target_count: number;
  current_count: number;
  start_date: string;
  end_date: string;
  category_id: string | null;
  created_at: string;
  updated_at: string;
}

export enum HabitFrequency {
  DAILY = 'DAILY',
  WEEKLY = 'WEEKLY',
}

export interface Habit {
  id: string;
  user_id: string;
  name: string;
  frequency: HabitFrequency;
  target_days: number | null;
  duration_days: number | null;
  start_date: string | null;
  current_streak: number;
  longest_streak: number;
  last_completed: string | null;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: string;
  name: string;
  color: string;
}

export interface DailyAnalytics {
  date: string;
  total_tasks: number;
  completed_tasks: number;
  skipped_tasks: number;
  pending_tasks: number;
  completion_rate: number;
}

export interface WeeklyAnalytics {
  start_date: string;
  end_date: string;
  total_tasks: number;
  completed_tasks: number;
  skipped_tasks: number;
  pending_tasks: number;
  completion_rate: number;
  daily_breakdown: DailyAnalytics[];
}

export interface Retrospective {
  id: string;
  user_id: string;
  month: string;
  success_rate: number | null;
  total_tasks: number | null;
  completed_tasks: number | null;
  what_went_well: string;
  what_went_bad: string;
  what_to_change: string;
  average_mood: number | null;
  created_at: string;
  updated_at: string;
}

export interface SleepLog {
  id: string;
  user_id: string;
  date: string;
  sleep_time: string;
  wake_time: string;
  duration_hours: number;
  quality_score: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface SleepStatistics {
  total_logs: number;
  average_duration: number;
  average_quality: number | null;
  total_sleep_hours: number;
  best_sleep: {
    date: string;
    duration: number;
  } | null;
  worst_sleep: {
    date: string;
    duration: number;
  } | null;
}

export interface GoalWithTasks {
  goal: Goal;
  tasks: Task[];
  stats: {
    total: number;
    completed: number;
    pending: number;
    skipped: number;
    progress_percentage: number;
  };
}
