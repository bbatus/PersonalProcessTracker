import apiClient from './apiClient';
import {
  Task,
  CreateTaskDTO,
  TaskStatus,
  Habit,
  HabitLog,
  StreakInfo,
  AuthResult,
  DailyStats,
  WeeklyStats,
  User,
  Category,
} from '../types';

// ============================================================================
// Task API Methods
// ============================================================================

export const getTasks = async (date: string): Promise<Task[]> => {
  const response = await apiClient.get<Task[]>('/api/tasks', {
    params: {scheduled_date: date},
  });
  return response.data;
};

export const createTask = async (task: CreateTaskDTO): Promise<Task> => {
  const response = await apiClient.post<Task>('/api/tasks', task);
  return response.data;
};

export const updateTaskStatus = async (
  id: string,
  status: TaskStatus,
): Promise<Task> => {
  let endpoint = '';
  switch (status) {
    case 'DONE':
      endpoint = `/api/tasks/${id}/done`;
      break;
    case 'SKIPPED':
      endpoint = `/api/tasks/${id}/skip`;
      break;
    default:
      throw new Error(`Invalid status: ${status}`);
  }

  const response = await apiClient.patch<Task>(endpoint);
  return response.data;
};

export const postponeTask = async (id: string): Promise<Task> => {
  const response = await apiClient.patch<Task>(`/api/tasks/${id}/postpone`);
  return response.data;
};

export const deleteTask = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/tasks/${id}`);
};

// ============================================================================
// Habit API Methods
// ============================================================================

export const getHabits = async (): Promise<Habit[]> => {
  const response = await apiClient.get<Habit[]>('/api/habits');
  return response.data;
};

export const logHabitCompletion = async (
  habitId: string,
  date: string,
): Promise<HabitLog> => {
  const response = await apiClient.post<HabitLog>(`/api/habits/${habitId}/log`, {
    completed_date: date,
  });
  return response.data;
};

export const getHabitStreak = async (habitId: string): Promise<StreakInfo> => {
  const response = await apiClient.get<StreakInfo>(`/api/habits/${habitId}/streak`);
  return response.data;
};

// ============================================================================
// Auth API Methods
// ============================================================================

export const login = async (
  username: string,
  password: string,
): Promise<AuthResult> => {
  try {
    const response = await apiClient.post<{access_token: string; user: User}>(
      '/api/auth/login',
      {username, password},
    );

    return {
      success: true,
      token: response.data.access_token,
      user: response.data.user,
    };
  } catch (error: any) {
    // Handle specific error cases
    if (error.response?.status === 401) {
      return {
        success: false,
        error: 'Invalid username or password',
      };
    }

    if (error.response?.status === 403) {
      return {
        success: false,
        error: 'Account locked. Please try again later.',
      };
    }

    if (error.message.includes('internet connection')) {
      return {
        success: false,
        error: 'Unable to connect. Please check your internet connection.',
      };
    }

    return {
      success: false,
      error: 'Login failed. Please try again.',
    };
  }
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>('/api/auth/me');
  return response.data;
};

// ============================================================================
// Stats API Methods
// ============================================================================

export const getDailyStats = async (date: string): Promise<DailyStats> => {
  const response = await apiClient.get<DailyStats>('/api/analytics/daily', {
    params: {date},
  });
  return response.data;
};

export const getWeeklyStats = async (): Promise<WeeklyStats> => {
  const response = await apiClient.get<WeeklyStats>('/api/analytics/weekly');
  return response.data;
};

// ============================================================================
// Category API Methods
// ============================================================================

export const getCategories = async (): Promise<Category[]> => {
  const response = await apiClient.get<Category[]>('/api/categories');
  return response.data;
};
