'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { Task, Goal, Habit } from '@/types';

export default function DashboardPage() {
  const { user, loading: authLoading, logout } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    try {
      const [tasksRes, goalsRes, habitsRes] = await Promise.all([
        api.get('/api/tasks?limit=5'),
        api.get('/api/goals?limit=5'),
        api.get('/api/habits?limit=5'),
      ]);

      setTasks(tasksRes.data.tasks || []);
      setGoals(goalsRes.data || []);
      setHabits(habitsRes.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Personal Process Tracker
              </h1>
              <p className="text-sm text-gray-600">
                Welcome back, {user?.username}!
              </p>
            </div>
            <div className="flex gap-4 items-center">
              <nav className="flex gap-2">
                <button
                  onClick={() => router.push('/tasks')}
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Tasks
                </button>
                <button
                  onClick={() => router.push('/goals')}
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Goals
                </button>
                <button
                  onClick={() => router.push('/habits')}
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Habits
                </button>
                <button
                  onClick={() => router.push('/analytics')}
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Analytics
                </button>
                <button
                  onClick={() => router.push('/sleep')}
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Sleep
                </button>
                <button
                  onClick={() => router.push('/notes')}
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Notes
                </button>
                <button
                  onClick={() => router.push('/retrospective')}
                  className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Retrospective
                </button>
              </nav>
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Tasks Card */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Recent Tasks
              </h2>
              <span className="text-2xl">📝</span>
            </div>
            {tasks.length === 0 ? (
              <p className="text-gray-500 text-sm">No tasks yet</p>
            ) : (
              <ul className="space-y-3">
                {tasks.slice(0, 5).map((task) => (
                  <li
                    key={task.id}
                    className="flex items-start space-x-2 text-sm"
                  >
                    <span
                      className={`mt-0.5 ${
                        task.status === 'DONE'
                          ? 'text-green-500'
                          : task.status === 'SKIPPED'
                          ? 'text-gray-400'
                          : 'text-blue-500'
                      }`}
                    >
                      {task.status === 'DONE' ? '✓' : '○'}
                    </span>
                    <span
                      className={
                        task.status === 'DONE'
                          ? 'line-through text-gray-500'
                          : 'text-gray-900'
                      }
                    >
                      {task.title}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Goals Card */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Goals</h2>
              <span className="text-2xl">🎯</span>
            </div>
            {goals.length === 0 ? (
              <p className="text-gray-500 text-sm">No goals yet</p>
            ) : (
              <ul className="space-y-3">
                {goals.slice(0, 5).map((goal) => {
                  const progressPercentage = (goal.current_count / goal.target_count) * 100;
                  const progressColor = 
                    progressPercentage >= 100 ? 'bg-green-600' :
                    progressPercentage >= 75 ? 'bg-blue-600' :
                    'bg-orange-600';
                  
                  return (
                    <li key={goal.id} className="text-sm">
                      <div className="flex justify-between items-center mb-1">
                        <button
                          onClick={() => router.push(`/goals/${goal.id}`)}
                          className="text-gray-900 font-medium hover:text-blue-600 transition-colors"
                        >
                          {goal.title}
                        </button>
                        <span className="text-xs text-gray-500">
                          {goal.current_count}/{goal.target_count}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`${progressColor} h-2 rounded-full transition-all`}
                          style={{
                            width: `${Math.min(progressPercentage, 100)}%`,
                          }}
                        ></div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* Habits Tracker Card - Motivational */}
          <div className="bg-white rounded-xl shadow-sm p-6 lg:col-span-3">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">🔥 Habit Tracker</h2>
              <button
                onClick={() => router.push('/habits')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                View All →
              </button>
            </div>
            {habits.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 text-sm mb-4">No habits tracked yet</p>
                <button
                  onClick={() => router.push('/habits')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Start Your First Habit
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {habits.map((habit) => {
                  const getMotivationalMessage = (streak: number, name: string) => {
                    if (streak === 0) return `Start "${name}" today! 💪`;
                    if (streak === 1) return `Great start! Keep going! 🌟`;
                    if (streak < 7) return `${streak} days strong! Don't break the chain! 🔗`;
                    if (streak < 21) return `${streak} days! You're building a habit! 🚀`;
                    if (streak < 30) return `${streak} days! Almost a month! 🎯`;
                    if (streak < 100) return `${streak} days! You're unstoppable! 💎`;
                    return `${streak} days! Legendary streak! 👑`;
                  };

                  return (
                    <div
                      key={habit.id}
                      className="bg-gradient-to-br from-orange-50 to-red-50 rounded-lg p-4 border-2 border-orange-200 hover:border-orange-300 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 mb-1">{habit.name}</h3>
                          <p className="text-xs text-gray-600 italic">
                            {getMotivationalMessage(habit.current_streak, habit.name)}
                          </p>
                        </div>
                        <div className="text-3xl font-bold text-orange-600">
                          {habit.current_streak}
                          <span className="text-2xl">🔥</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-600">
                        <span>Best: {habit.longest_streak} days 🏆</span>
                        <span className="px-2 py-1 bg-white rounded-full text-orange-600 font-medium">
                          {habit.frequency}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-sm p-6 text-white">
            <div className="text-3xl font-bold">{tasks.length}</div>
            <div className="text-blue-100 mt-1">Total Tasks</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-sm p-6 text-white">
            <div className="text-3xl font-bold">{goals.length}</div>
            <div className="text-green-100 mt-1">Active Goals</div>
          </div>
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-sm p-6 text-white">
            <div className="text-3xl font-bold">{habits.length}</div>
            <div className="text-orange-100 mt-1">Tracked Habits</div>
          </div>
        </div>
      </main>
    </div>
  );
}
