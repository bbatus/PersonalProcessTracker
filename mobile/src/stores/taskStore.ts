import {create} from 'zustand';
import {format} from 'date-fns';
import {Task, CreateTaskDTO, TaskStatus} from '../types';
import * as api from '../services/api';
import * as cache from '../services/cache';
import * as syncManager from '../services/syncManager';

interface TaskState {
  tasks: Task[];
  selectedDate: string;
  isLoading: boolean;
  error: string | null;

  // Actions
  loadTasks: (date: string) => Promise<void>;
  createTask: (task: CreateTaskDTO) => Promise<void>;
  markDone: (taskId: string) => Promise<void>;
  markSkipped: (taskId: string) => Promise<void>;
  postponeTask: (taskId: string) => Promise<void>;
  setSelectedDate: (date: string) => void;

  // Computed
  pendingTasks: () => Task[];
  doneTasks: () => Task[];
  skippedTasks: () => Task[];
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  selectedDate: format(new Date(), 'yyyy-MM-dd'),
  isLoading: false,
  error: null,

  /**
   * Load tasks for a specific date (cache-first)
   */
  loadTasks: async (date: string) => {
    set({isLoading: true, error: null, selectedDate: date});

    try {
      // Try cache first
      const cachedTasks = cache.getCachedTasks(date);
      if (cachedTasks) {
        set({tasks: cachedTasks, isLoading: false});
      }

      // Fetch from API in background
      const tasks = await api.getTasks(date);

      // Update cache
      cache.cacheTasks(date, tasks);

      // Update state
      set({tasks, isLoading: false});
    } catch (error: any) {
      console.error('Load tasks error:', error);

      // If we have cached data, keep showing it
      const cachedTasks = cache.getCachedTasks(date);
      if (cachedTasks) {
        set({
          tasks: cachedTasks,
          isLoading: false,
          error: 'Using cached data. Unable to refresh.',
        });
      } else {
        set({
          isLoading: false,
          error: error.message || 'Failed to load tasks',
        });
      }
    }
  },

  /**
   * Create a new task
   */
  createTask: async (taskDTO: CreateTaskDTO) => {
    set({isLoading: true, error: null});

    try {
      const newTask = await api.createTask(taskDTO);

      // Add to current tasks if same date
      const {tasks, selectedDate} = get();
      if (newTask.scheduled_date === selectedDate) {
        set({tasks: [...tasks, newTask], isLoading: false});

        // Update cache
        cache.cacheTasks(selectedDate, [...tasks, newTask]);
      } else {
        set({isLoading: false});
      }
    } catch (error: any) {
      console.error('Create task error:', error);

      // Check if offline
      const isOnline = await syncManager.isOnline();
      if (!isOnline) {
        // Queue for later sync
        await syncManager.queueAction({
          id: `task_create_${Date.now()}`,
          type: 'TASK_CREATE',
          payload: taskDTO,
          timestamp: Date.now(),
          retryCount: 0,
        });

        set({
          isLoading: false,
          error: 'Task queued. Will sync when online.',
        });
      } else {
        set({
          isLoading: false,
          error: error.message || 'Failed to create task',
        });
      }
    }
  },

  /**
   * Mark task as done (optimistic update)
   */
  markDone: async (taskId: string) => {
    const {tasks, selectedDate} = get();
    const task = tasks.find(t => t.id === taskId);

    if (!task) {
      return;
    }

    // Optimistic update
    const updatedTask = {...task, status: 'DONE' as TaskStatus, completed_at: new Date().toISOString()};
    const updatedTasks = tasks.map(t => (t.id === taskId ? updatedTask : t));

    set({tasks: updatedTasks});
    cache.cacheTasks(selectedDate, updatedTasks);

    try {
      // Call API
      await api.updateTaskStatus(taskId, 'DONE');
    } catch (error: any) {
      console.error('Mark done error:', error);

      // Revert on failure
      set({tasks, error: 'Failed to update task'});
      cache.cacheTasks(selectedDate, tasks);

      // Check if offline and queue
      const isOnline = await syncManager.isOnline();
      if (!isOnline) {
        await syncManager.queueAction({
          id: `task_update_${taskId}_${Date.now()}`,
          type: 'TASK_UPDATE',
          payload: {id: taskId, status: 'DONE'},
          timestamp: Date.now(),
          retryCount: 0,
        });

        // Keep optimistic update
        set({tasks: updatedTasks, error: 'Queued for sync'});
      }
    }
  },

  /**
   * Mark task as skipped (optimistic update)
   */
  markSkipped: async (taskId: string) => {
    const {tasks, selectedDate} = get();
    const task = tasks.find(t => t.id === taskId);

    if (!task) {
      return;
    }

    // Optimistic update
    const updatedTask = {...task, status: 'SKIPPED' as TaskStatus};
    const updatedTasks = tasks.map(t => (t.id === taskId ? updatedTask : t));

    set({tasks: updatedTasks});
    cache.cacheTasks(selectedDate, updatedTasks);

    try {
      await api.updateTaskStatus(taskId, 'SKIPPED');
    } catch (error: any) {
      console.error('Mark skipped error:', error);

      // Revert on failure
      set({tasks, error: 'Failed to update task'});
      cache.cacheTasks(selectedDate, tasks);

      // Check if offline and queue
      const isOnline = await syncManager.isOnline();
      if (!isOnline) {
        await syncManager.queueAction({
          id: `task_update_${taskId}_${Date.now()}`,
          type: 'TASK_UPDATE',
          payload: {id: taskId, status: 'SKIPPED'},
          timestamp: Date.now(),
          retryCount: 0,
        });

        set({tasks: updatedTasks, error: 'Queued for sync'});
      }
    }
  },

  /**
   * Postpone task to tomorrow (optimistic update)
   */
  postponeTask: async (taskId: string) => {
    const {tasks, selectedDate} = get();
    const task = tasks.find(t => t.id === taskId);

    if (!task) {
      return;
    }

    // Remove from current view immediately
    const updatedTasks = tasks.filter(t => t.id !== taskId);
    set({tasks: updatedTasks});
    cache.cacheTasks(selectedDate, updatedTasks);

    try {
      await api.postponeTask(taskId);
    } catch (error: any) {
      console.error('Postpone task error:', error);

      // Revert on failure
      set({tasks, error: 'Failed to postpone task'});
      cache.cacheTasks(selectedDate, tasks);
    }
  },

  /**
   * Set selected date
   */
  setSelectedDate: (date: string) => {
    set({selectedDate: date});
  },

  /**
   * Get pending tasks
   */
  pendingTasks: () => {
    return get().tasks.filter(t => t.status === 'PENDING');
  },

  /**
   * Get done tasks
   */
  doneTasks: () => {
    return get().tasks.filter(t => t.status === 'DONE');
  },

  /**
   * Get skipped tasks
   */
  skippedTasks: () => {
    return get().tasks.filter(t => t.status === 'SKIPPED');
  },
}));
