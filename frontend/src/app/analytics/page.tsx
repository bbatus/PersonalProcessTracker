'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DailyAnalytics {
  date: string;
  total_tasks: number;
  completed_tasks: number;
  skipped_tasks: number;
  completion_rate: number;
}

interface MonthlyAnalytics {
  total_tasks: number;
  completed_tasks: number;
  skipped_tasks: number;
  completion_rate: number;
  category_breakdown: Array<{
    category_name: string;
    total: number;
    completed: number;
    completion_rate: number;
  }>;
}

interface TaskInsights {
  most_completed: Array<{ title: string; count: number }>;
  most_skipped: Array<{ title: string; count: number }>;
}

export default function AnalyticsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<'week' | 'month'>('week');
  const [weeklyData, setWeeklyData] = useState<DailyAnalytics[]>([]);
  const [monthlyData, setMonthlyData] = useState<MonthlyAnalytics | null>(null);
  const [insights, setInsights] = useState<TaskInsights | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchAnalytics();
    }
  }, [user, period]);

  const fetchAnalytics = async () => {
    try {
      const [weeklyRes, monthlyRes, insightsRes] = await Promise.all([
        api.get('/api/analytics/weekly'),
        api.get('/api/analytics/monthly'),
        api.get('/api/analytics/insights'),
      ]);

      setWeeklyData(weeklyRes.data.daily_analytics || []);
      setMonthlyData(monthlyRes.data);
      setInsights(insightsRes.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
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
        {/* Summary Cards */}
        {monthlyData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Total Tasks</div>
              <div className="text-3xl font-bold text-gray-900">{monthlyData.total_tasks}</div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Completed</div>
              <div className="text-3xl font-bold text-green-600">{monthlyData.completed_tasks}</div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Skipped</div>
              <div className="text-3xl font-bold text-orange-600">{monthlyData.skipped_tasks}</div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="text-sm text-gray-600 mb-1">Completion Rate</div>
              <div className="text-3xl font-bold text-blue-600">
                {monthlyData.completion_rate.toFixed(0)}%
              </div>
            </div>
          </div>
        )}

        {/* Weekly Trend Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Weekly Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="completed_tasks" stroke="#10B981" name="Completed" strokeWidth={2} />
              <Line type="monotone" dataKey="skipped_tasks" stroke="#F59E0B" name="Skipped" strokeWidth={2} />
              <Line type="monotone" dataKey="total_tasks" stroke="#3B82F6" name="Total" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Completion Rate Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Daily Completion Rate</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="completion_rate" fill="#3B82F6" name="Completion Rate %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Category Breakdown */}
          {monthlyData && monthlyData.category_breakdown.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Category Breakdown</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={monthlyData.category_breakdown}
                    dataKey="total"
                    nameKey="category_name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {monthlyData.category_breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {monthlyData.category_breakdown.map((cat, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="text-gray-600">{cat.category_name}</span>
                    <span className="font-medium text-gray-900">
                      {cat.completed}/{cat.total} ({cat.completion_rate.toFixed(0)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Task Insights */}
          {insights && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Task Insights</h2>
              
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Most Completed Tasks</h3>
                {insights.most_completed.length === 0 ? (
                  <p className="text-sm text-gray-500">No data yet</p>
                ) : (
                  <div className="space-y-2">
                    {insights.most_completed.map((task, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-900">{task.title}</span>
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                          {task.count}x
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Most Skipped Tasks</h3>
                {insights.most_skipped.length === 0 ? (
                  <p className="text-sm text-gray-500">No data yet</p>
                ) : (
                  <div className="space-y-2">
                    {insights.most_skipped.map((task, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-900">{task.title}</span>
                        <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full font-medium">
                          {task.count}x
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
