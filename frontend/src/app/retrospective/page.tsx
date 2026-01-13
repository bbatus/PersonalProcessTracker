'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';

interface Retrospective {
  id: string;
  user_id: string;
  month: string;
  what_went_well: string;
  what_to_improve: string;
  lessons_learned: string;
  goals_next_month: string;
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  average_mood: number;
  created_at: string;
  updated_at: string;
}

export default function RetrospectivePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [retrospectives, setRetrospectives] = useState<Retrospective[]>([]);
  const [selectedMonth, setSelectedMonth] = useState(
    new Date().toISOString().slice(0, 7) // YYYY-MM format
  );
  const [currentRetro, setCurrentRetro] = useState<Retrospective | null>(null);
  const [mood, setMood] = useState(5);

  const [formData, setFormData] = useState({
    what_went_well: '',
    what_to_improve: '',
    lessons_learned: '',
    goals_next_month: '',
  });

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user, selectedMonth]);

  const fetchData = async () => {
    try {
      const [retroRes, listRes] = await Promise.all([
        api.get(`/api/retrospectives/${selectedMonth}`).catch(() => ({ data: null })),
        api.get('/api/retrospectives'),
      ]);

      setCurrentRetro(retroRes.data);
      setRetrospectives(listRes.data || []);

      if (retroRes.data) {
        setFormData({
          what_went_well: retroRes.data.what_went_well || '',
          what_to_improve: retroRes.data.what_to_improve || '',
          lessons_learned: retroRes.data.lessons_learned || '',
          goals_next_month: retroRes.data.goals_next_month || '',
        });
      } else {
        setFormData({
          what_went_well: '',
          what_to_improve: '',
          lessons_learned: '',
          goals_next_month: '',
        });
      }
    } catch (error) {
      console.error('Error fetching retrospectives:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/retrospectives', {
        month: selectedMonth,
        ...formData,
      });
      fetchData();
      alert('Retrospective saved successfully!');
    } catch (error) {
      console.error('Error saving retrospective:', error);
      alert('Failed to save retrospective');
    }
  };

  const handleLogMood = async () => {
    try {
      await api.post('/api/retrospectives/mood', {
        date: new Date().toISOString().split('T')[0],
        mood_score: mood,
      });
      alert('Mood logged successfully!');
    } catch (error) {
      console.error('Error logging mood:', error);
      alert('Failed to log mood');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Monthly Retrospective</h1>
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Month Selector */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Month
              </label>
              <input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Statistics */}
            {currentRetro && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Monthly Statistics</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Total Tasks</div>
                    <div className="text-2xl font-bold text-gray-900">{currentRetro.total_tasks}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Completed</div>
                    <div className="text-2xl font-bold text-green-600">{currentRetro.completed_tasks}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Completion Rate</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {currentRetro.completion_rate.toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Avg Mood</div>
                    <div className="text-2xl font-bold text-purple-600">
                      {currentRetro.average_mood ? currentRetro.average_mood.toFixed(1) : 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Retrospective Form */}
            <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What went well? 🎉
                </label>
                <textarea
                  value={formData.what_went_well}
                  onChange={(e) => setFormData({ ...formData, what_went_well: e.target.value })}
                  rows={4}
                  placeholder="Celebrate your wins and positive moments..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What could be improved? 🔧
                </label>
                <textarea
                  value={formData.what_to_improve}
                  onChange={(e) => setFormData({ ...formData, what_to_improve: e.target.value })}
                  rows={4}
                  placeholder="Areas for growth and improvement..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lessons learned 📚
                </label>
                <textarea
                  value={formData.lessons_learned}
                  onChange={(e) => setFormData({ ...formData, lessons_learned: e.target.value })}
                  rows={4}
                  placeholder="Key insights and takeaways..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Goals for next month 🎯
                </label>
                <textarea
                  value={formData.goals_next_month}
                  onChange={(e) => setFormData({ ...formData, goals_next_month: e.target.value })}
                  rows={4}
                  placeholder="What do you want to achieve next month?..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <button
                type="submit"
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Save Retrospective
              </button>
            </form>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Mood Logger */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Log Today's Mood</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    How are you feeling? (1-10)
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={mood}
                    onChange={(e) => setMood(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>😢 1</span>
                    <span className="text-2xl">{mood}</span>
                    <span>😄 10</span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleLogMood}
                  className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Log Mood
                </button>
              </div>
            </div>

            {/* Past Retrospectives */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Past Retrospectives</h2>
              {retrospectives.length === 0 ? (
                <p className="text-sm text-gray-500">No retrospectives yet</p>
              ) : (
                <div className="space-y-2">
                  {retrospectives.slice(0, 6).map((retro) => (
                    <button
                      key={retro.id}
                      onClick={() => setSelectedMonth(retro.month)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        retro.month === selectedMonth
                          ? 'bg-blue-100 text-blue-900'
                          : 'hover:bg-gray-100 text-gray-700'
                      }`}
                    >
                      <div className="font-medium">{retro.month}</div>
                      <div className="text-xs text-gray-500">
                        {retro.completion_rate.toFixed(0)}% completion
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
