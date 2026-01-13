'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { Task, Category } from '@/types';

export default function NotesPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchNotes();
    }
  }, [user]);

  const fetchNotes = async () => {
    try {
      // Fetch all tasks with notes (we'll filter on frontend)
      const [tasksRes, categoriesRes] = await Promise.all([
        api.get('/api/tasks?limit=500'),
        api.get('/api/categories'),
      ]);

      // Filter tasks that have notes
      const tasksWithNotes = (tasksRes.data.tasks || []).filter(
        (task: Task) => task.notes && task.notes.trim().length > 0
      );

      // Sort by date descending (most recent first)
      tasksWithNotes.sort((a: Task, b: Task) => 
        b.scheduled_date.localeCompare(a.scheduled_date)
      );

      setTasks(tasksWithNotes);
      setCategories(categoriesRes.data || []);
    } catch (error) {
      console.error('Error fetching notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewInCalendar = (task: Task) => {
    // Navigate to tasks page with the date
    router.push(`/tasks?date=${task.scheduled_date}`);
  };

  const filteredTasks = tasks.filter(task => {
    const query = searchQuery.toLowerCase();
    return (
      task.title.toLowerCase().includes(query) ||
      (task.notes && task.notes.toLowerCase().includes(query)) ||
      (task.description && task.description.toLowerCase().includes(query))
    );
  });

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
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
              <h1 className="text-2xl font-bold text-gray-900">Task Notes</h1>
              <p className="text-sm text-gray-600 mt-1">
                View all your task notes and feedback
              </p>
            </div>
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
        {/* Search Bar */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search notes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Stats */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">{tasks.length}</p>
              <p className="text-sm text-gray-600">Total Notes</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">
                {tasks.filter(t => t.status === 'DONE').length}
              </p>
              <p className="text-sm text-gray-600">Completed Tasks</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">
                {tasks.filter(t => t.habit_id).length}
              </p>
              <p className="text-sm text-gray-600">Habit Notes</p>
            </div>
          </div>
        </div>

        {/* Notes List */}
        {filteredTasks.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {searchQuery ? 'No notes found' : 'No notes yet'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchQuery 
                ? 'Try a different search term'
                : 'Start adding notes to your tasks to see them here'
              }
            </p>
            {!searchQuery && (
              <button
                onClick={() => router.push('/tasks')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Go to Tasks
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredTasks.map(task => {
              const category = categories.find(c => c.id === task.category_id);
              const isHabitTask = !!task.habit_id;
              const taskDate = new Date(task.scheduled_date + 'T12:00:00');
              
              return (
                <div
                  key={task.id}
                  className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {isHabitTask && <span className="text-purple-600">🔄</span>}
                        <h3 className={`text-lg font-semibold ${
                          task.status === 'DONE' ? 'text-green-700' : 'text-gray-900'
                        }`}>
                          {task.title}
                          {task.status === 'DONE' && ' ✓'}
                        </h3>
                        {category && (
                          <span 
                            className="px-2 py-0.5 text-xs rounded-full text-white"
                            style={{ backgroundColor: category.color }}
                          >
                            {category.name}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>📅 {taskDate.toLocaleDateString('en-US', { 
                          weekday: 'short',
                          month: 'short', 
                          day: 'numeric',
                          year: 'numeric'
                        })}</span>
                        {task.estimated_duration && (
                          <span>⏱️ {task.estimated_duration} min</span>
                        )}
                        <span className={`px-2 py-0.5 rounded-full text-xs ${
                          task.status === 'DONE' ? 'bg-green-100 text-green-700' :
                          task.status === 'SKIPPED' ? 'bg-gray-100 text-gray-700' :
                          'bg-blue-100 text-blue-700'
                        }`}>
                          {task.status}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleViewInCalendar(task)}
                      className="px-4 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                    >
                      View in Calendar →
                    </button>
                  </div>

                  {task.description && (
                    <p className="text-sm text-gray-600 mb-3 italic">
                      {task.description}
                    </p>
                  )}

                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                    <p className="text-xs font-semibold text-yellow-800 mb-2">📝 Notes:</p>
                    <p className="text-sm text-yellow-900 whitespace-pre-wrap">
                      {task.notes}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
