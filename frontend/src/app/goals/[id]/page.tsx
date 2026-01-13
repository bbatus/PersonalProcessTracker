'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { GoalWithTasks, Category } from '@/types';

export default function GoalDetailPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const goalId = params.id as string;

  const [goalData, setGoalData] = useState<GoalWithTasks | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user && goalId) {
      fetchGoalData();
      fetchCategories();
    }
  }, [user, goalId]);

  const fetchGoalData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/api/goals/${goalId}/tasks`);
      setGoalData(response.data);
    } catch (err: any) {
      console.error('Error fetching goal data:', err);
      setError(err.response?.data?.detail || 'Failed to load goal');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/api/categories');
      setCategories(response.data || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleStatusChange = async (taskId: string, action: 'done' | 'skip' | 'reopen') => {
    try {
      await api.patch(`/api/tasks/${taskId}/${action}`);
      await fetchGoalData(); // Refresh to see updated progress
    } catch (error) {
      console.error(`Error ${action} task:`, error);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await api.delete(`/api/tasks/${taskId}`);
      await fetchGoalData(); // Refresh after delete
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const handleCreateTask = () => {
    // Navigate to tasks page with goal pre-selected
    router.push(`/tasks?goal_id=${goalId}`);
  };

  const handleEditTask = (taskId: string) => {
    // Navigate to tasks page with task to edit
    router.push(`/tasks?edit=${taskId}`);
  };

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !goalData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-sm p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="text-red-600 text-5xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Goal Not Found</h2>
            <p className="text-gray-600 mb-6">{error || 'The goal you are looking for does not exist.'}</p>
            <button
              onClick={() => router.push('/goals')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Back to Goals
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { goal, tasks, stats } = goalData;
  const progressPercentage = stats.progress_percentage;
  const progressColor = 
    progressPercentage >= 100 ? 'bg-green-600' :
    progressPercentage >= 75 ? 'bg-blue-600' :
    'bg-orange-600';

  const getDaysRemaining = () => {
    const end = new Date(goal.end_date);
    const now = new Date();
    const diff = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const daysRemaining = getDaysRemaining();
  const isNearDeadline = daysRemaining <= 5 && daysRemaining > 0;
  const isPastDeadline = daysRemaining < 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <button
              onClick={() => router.push('/goals')}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Goals
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              Dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Goal Info Card */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{goal.title}</h1>
              <span className="inline-block px-3 py-1 text-sm rounded-full bg-blue-100 text-blue-800">
                {goal.period}
              </span>
            </div>
          </div>

          {goal.description && (
            <p className="text-gray-600 mb-6">{goal.description}</p>
          )}

          {/* Progress Section */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-lg font-semibold text-gray-900">Progress</span>
              <span className="text-2xl font-bold text-gray-900">
                {goal.current_count} / {goal.target_count}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
              <div
                className={`${progressColor} h-4 rounded-full transition-all duration-300`}
                style={{ width: `${Math.min(progressPercentage, 100)}%` }}
              ></div>
            </div>
            <div className="text-sm text-gray-600">
              {progressPercentage.toFixed(1)}% complete
            </div>
          </div>

          {/* Timeline */}
          <div className="border-t pt-4">
            <div className="text-sm text-gray-600 mb-2">
              {isPastDeadline ? (
                <span className="text-red-600 font-medium">
                  ⚠️ Deadline passed {Math.abs(daysRemaining)} days ago
                </span>
              ) : isNearDeadline ? (
                <span className="text-orange-600 font-medium">
                  ⏰ {daysRemaining} days remaining
                </span>
              ) : (
                <span>
                  📅 {daysRemaining} days remaining
                </span>
              )}
            </div>
            <div className="text-xs text-gray-500">
              {new Date(goal.start_date).toLocaleDateString()} → {new Date(goal.end_date).toLocaleDateString()}
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-600 mb-1">Total Tasks</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-600 mb-1">Completed</div>
            <div className="text-3xl font-bold text-green-600">{stats.completed}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-600 mb-1">Pending</div>
            <div className="text-3xl font-bold text-orange-600">{stats.pending}</div>
          </div>
        </div>

        {/* Tasks Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Tasks</h2>
            <button
              onClick={handleCreateTask}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              + New Task
            </button>
          </div>

          {tasks.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-5xl mb-4">📝</div>
              <p className="text-gray-500 mb-4">No tasks linked to this goal yet</p>
              <button
                onClick={handleCreateTask}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Create First Task
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map(task => {
                const category = categories.find(c => c.id === task.category_id);
                const isHabitTask = !!task.habit_id;
                
                return (
                  <div
                    key={task.id}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      task.status === 'DONE' ? 'bg-green-50 border-green-200' :
                      task.status === 'SKIPPED' ? 'bg-gray-50 border-gray-200' :
                      'bg-white border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Checkbox */}
                      <button
                        onClick={() => {
                          if (task.status === 'DONE') {
                            handleStatusChange(task.id, 'reopen');
                          } else {
                            handleStatusChange(task.id, 'done');
                          }
                        }}
                        className={`mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                          task.status === 'DONE' 
                            ? 'bg-green-500 border-green-500' 
                            : 'border-gray-300 hover:border-blue-500'
                        }`}
                      >
                        {task.status === 'DONE' && (
                          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </button>

                      {/* Task Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          {isHabitTask && <span className="text-purple-600">🔄</span>}
                          <h3 className={`font-semibold text-gray-900 ${task.status === 'DONE' ? 'line-through' : ''}`}>
                            {task.title}
                          </h3>
                          {category && (
                            <span 
                              className="px-2 py-0.5 text-xs rounded-full text-white"
                              style={{ backgroundColor: category.color }}
                            >
                              {category.name}
                            </span>
                          )}
                          <span className="text-xs text-gray-500">
                            📅 {new Date(task.scheduled_date).toLocaleDateString()}
                          </span>
                        </div>
                        {task.description && (
                          <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                        )}
                        {task.notes && (
                          <div className="mt-2 p-2 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                            <p className="text-xs font-semibold text-yellow-800 mb-1">📝 Notes:</p>
                            <p className="text-sm text-yellow-900 whitespace-pre-wrap">{task.notes}</p>
                          </div>
                        )}
                        {task.estimated_duration && (
                          <p className="text-xs text-gray-500 mt-1">⏱️ {task.estimated_duration} min</p>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleEditTask(task.id)}
                          className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Edit"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        {task.status === 'PENDING' && (
                          <button
                            onClick={() => handleStatusChange(task.id, 'skip')}
                            className="p-2 text-gray-400 hover:text-yellow-600 transition-colors"
                            title="Skip"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                            </svg>
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                          title="Delete"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
