'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';
import { Task, Category, Goal } from '@/types';

export default function TasksPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);  // NEW
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [showDayDetail, setShowDayDetail] = useState(false);
  const [detailDate, setDetailDate] = useState<Date | null>(null);
  
  // Current month state
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    notes: '',
    scheduled_date: (() => {
      const today = new Date();
      return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    })(),
    category_id: '',
    goal_id: '',  // NEW
    estimated_duration: 30,
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
  }, [user, currentMonth]);

  // Separate effect for handling URL parameters (only run once)
  useEffect(() => {
    if (!user) return;
    
    const dateParam = searchParams.get('date');
    const goalIdParam = searchParams.get('goal_id');
    const editParam = searchParams.get('edit');
    
    if (dateParam) {
      // Parse the date and open day detail
      const [year, month, day] = dateParam.split('-').map(Number);
      const targetDate = new Date(year, month - 1, day, 12, 0, 0);
      
      // Set current month to the target date's month
      setCurrentMonth(new Date(year, month - 1, 1));
      
      // Open day detail
      setDetailDate(targetDate);
      setShowDayDetail(true);
    }
    
    if (goalIdParam) {
      // Pre-fill goal_id in form
      setFormData(prev => ({ ...prev, goal_id: goalIdParam }));
      setShowForm(true);
    }
    
    if (editParam) {
      // Load task for editing
      const taskToEdit = tasks.find(t => t.id === editParam);
      if (taskToEdit) {
        handleEdit(taskToEdit);
      }
    }
    
    // Remove parameters from URL to prevent reopening
    if (dateParam || goalIdParam || editParam) {
      const newUrl = window.location.pathname;
      window.history.replaceState({}, '', newUrl);
    }
  }, [user, searchParams, tasks]);

  const fetchData = async () => {
    try {
      // Get first and last day of current month (using local timezone)
      const year = currentMonth.getFullYear();
      const month = currentMonth.getMonth();
      
      // Format dates without timezone conversion
      const firstDay = `${year}-${String(month + 1).padStart(2, '0')}-01`;
      const lastDayDate = new Date(year, month + 1, 0);
      const lastDay = `${year}-${String(month + 1).padStart(2, '0')}-${String(lastDayDate.getDate()).padStart(2, '0')}`;

      const [tasksRes, categoriesRes, goalsRes] = await Promise.all([
        api.get(`/api/tasks?start_date=${firstDay}&end_date=${lastDay}&limit=100`),
        api.get('/api/categories'),
        api.get('/api/goals'),  // NEW
      ]);

      setTasks(tasksRes.data.tasks || []);
      setCategories(categoriesRes.data || []);
      setGoals(goalsRes.data || []);  // NEW
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDayOfWeek = new Date(year, month, 1).getDay();
    
    const days = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month - create dates at noon to avoid timezone issues
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day, 12, 0, 0);
      days.push(date);
    }
    
    return days;
  };

  const getTasksForDate = (date: Date) => {
    // Use local date string to avoid timezone issues
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    return tasks.filter(task => task.scheduled_date === dateStr);
  };

  const handlePreviousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const handleDayClick = (date: Date) => {
    // Show day detail panel instead of opening form directly
    setDetailDate(date);
    setShowDayDetail(true);
    
    // Set selected date for potential new task creation
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    setSelectedDate(dateStr);
  };

  const handleNewTaskFromDetail = () => {
    // Open task form with the detail date pre-selected
    if (detailDate) {
      const year = detailDate.getFullYear();
      const month = String(detailDate.getMonth() + 1).padStart(2, '0');
      const day = String(detailDate.getDate()).padStart(2, '0');
      const dateStr = `${year}-${month}-${day}`;
      setFormData({ ...formData, scheduled_date: dateStr });
    }
    setEditingTask(null);
    setShowForm(true);
  };

  const getTaskStats = (date: Date) => {
    const dayTasks = getTasksForDate(date);
    const total = dayTasks.length;
    const completed = dayTasks.filter(t => t.status === 'DONE').length;
    return { total, completed };
  };

  const getStatsColor = (total: number, completed: number) => {
    if (total === 0) return 'text-gray-400';
    if (completed === 0) return 'text-gray-600';
    if (completed === total) return 'text-green-600';
    return 'text-yellow-600';
  };

  const getStatsBgColor = (total: number, completed: number) => {
    if (total === 0) return 'bg-gray-100';
    if (completed === 0) return 'bg-gray-200';
    if (completed === total) return 'bg-green-100';
    return 'bg-yellow-100';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Prepare data - convert empty strings to null for optional UUID fields
      const submitData = {
        ...formData,
        category_id: formData.category_id || null,
        goal_id: formData.goal_id || null,
      };
      
      if (editingTask) {
        await api.put(`/api/tasks/${editingTask.id}`, submitData);
      } else {
        await api.post('/api/tasks', submitData);
      }
      setShowForm(false);
      setEditingTask(null);
      resetForm();
      await fetchData(); // Refresh tasks after save
    } catch (error) {
      console.error('Error saving task:', error);
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      notes: task.notes || '',
      scheduled_date: task.scheduled_date,
      category_id: task.category_id || '',
      goal_id: task.goal_id || '',  // NEW
      estimated_duration: task.estimated_duration || 30,
    });
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await api.delete(`/api/tasks/${id}`);
      await fetchData(); // Refresh tasks after delete
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const handleStatusChange = async (id: string, action: 'done' | 'skip' | 'reopen' | 'postpone') => {
    try {
      await api.patch(`/api/tasks/${id}/${action}`);
      await fetchData(); // Refresh tasks after status change
    } catch (error) {
      console.error(`Error ${action} task:`, error);
    }
  };

  const resetForm = () => {
    const today = new Date();
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    
    setFormData({
      title: '',
      description: '',
      notes: '',
      scheduled_date: selectedDate || todayStr,
      category_id: '',
      goal_id: '',  // NEW
      estimated_duration: 30,
    });
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const days = getDaysInMonth();
  const monthName = currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Tasks Calendar</h1>
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
        {/* Month Navigation */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex items-center justify-between">
            <button
              onClick={handlePreviousMonth}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              ← Previous
            </button>
            <h2 className="text-xl font-bold text-gray-900">{monthName}</h2>
            <button
              onClick={handleNextMonth}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Next →
            </button>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          {/* Day headers */}
          <div className="grid grid-cols-7 gap-2 mb-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="text-center text-sm font-semibold text-gray-600 py-2">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar days */}
          <div className="grid grid-cols-7 gap-2">
            {days.map((date, index) => {
              if (!date) {
                return <div key={`empty-${index}`} className="aspect-square" />;
              }

              const dayTasks = getTasksForDate(date);
              const isCurrentDay = isToday(date);
              const stats = getTaskStats(date);

              return (
                <div
                  key={date.toISOString()}
                  onClick={() => handleDayClick(date)}
                  className={`aspect-square border rounded-lg p-2 cursor-pointer hover:bg-blue-50 transition-colors relative ${
                    isCurrentDay ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  {/* Task Stats Badge - Top Right */}
                  {stats.total > 0 && (
                    <div className={`absolute top-1 right-1 px-1.5 py-0.5 rounded text-xs font-semibold ${getStatsBgColor(stats.total, stats.completed)} ${getStatsColor(stats.total, stats.completed)}`}>
                      {stats.total}/{stats.completed}
                    </div>
                  )}
                  
                  <div className="flex flex-col h-full">
                    <div className={`text-sm font-semibold mb-1 ${
                      isCurrentDay ? 'text-blue-600' : 'text-gray-700'
                    }`}>
                      {date.getDate()}
                    </div>
                    <div className="flex-1 overflow-y-auto space-y-1">
                      {dayTasks.slice(0, 2).map(task => {
                        const category = categories.find(c => c.id === task.category_id);
                        const isHabitTask = !!task.habit_id;
                        return (
                          <div
                            key={task.id}
                            className={`text-xs p-1 rounded truncate ${
                              task.status === 'DONE' ? 'bg-green-100 text-green-800 line-through' :
                              task.status === 'SKIPPED' ? 'bg-gray-100 text-gray-600' :
                              isHabitTask ? 'bg-purple-100 text-purple-800' :
                              'bg-blue-100 text-blue-800'
                            }`}
                            style={category ? { borderLeft: `3px solid ${category.color}` } : {}}
                            title={`${isHabitTask ? '🔄 ' : ''}${task.title}`}
                          >
                            {task.status === 'DONE' && '✓ '}
                            {isHabitTask && '🔄 '}
                            {task.title}
                          </div>
                        );
                      })}
                      {dayTasks.length > 2 && (
                        <div className="text-xs text-gray-500 text-center font-medium">
                          +{dayTasks.length - 2} more
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Day Detail Panel */}
        {showDayDetail && detailDate && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {detailDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                  </h2>
                  <div className="flex items-center gap-2 mt-1">
                    {(() => {
                      const stats = getTaskStats(detailDate);
                      return (
                        <span className={`text-sm font-semibold ${getStatsColor(stats.total, stats.completed)}`}>
                          {stats.completed} of {stats.total} completed
                        </span>
                      );
                    })()}
                  </div>
                </div>
                <button
                  onClick={() => {
                    setShowDayDetail(false);
                    setDetailDate(null);
                  }}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Tasks List */}
              <div className="flex-1 overflow-y-auto px-6 py-4">
                {(() => {
                  const dayTasks = getTasksForDate(detailDate);
                  if (dayTasks.length === 0) {
                    return (
                      <div className="text-center py-12">
                        <p className="text-gray-500 mb-4">No tasks for this day</p>
                        <button
                          onClick={handleNewTaskFromDetail}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          + Add First Task
                        </button>
                      </div>
                    );
                  }

                  return (
                    <div className="space-y-3">
                      {dayTasks.map(task => {
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
                                <div className="flex items-center gap-2 mb-1">
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
                                  <p className="text-xs text-gray-500">⏱️ {task.estimated_duration} min</p>
                                )}
                              </div>

                              {/* Actions */}
                              <div className="flex gap-1">
                                <button
                                  onClick={() => {
                                    handleEdit(task);
                                    setShowDayDetail(false);
                                  }}
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
                                  onClick={() => handleDelete(task.id)}
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
                  );
                })()}
              </div>

              {/* Footer with New Task Button */}
              <div className="px-6 py-4 border-t border-gray-200">
                <button
                  onClick={handleNewTaskFromDetail}
                  className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  + New Task
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Task Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                {editingTask ? 'Edit Task' : 'New Task'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes / Feedback
                    <span className="text-xs text-gray-500 ml-2">(Add notes after completing the task)</span>
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={4}
                    placeholder="e.g., Lesson feedback, key learnings, reflections..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date *
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.scheduled_date}
                    onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">No category</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Goal (Optional)
                  </label>
                  <select
                    value={formData.goal_id}
                    onChange={(e) => setFormData({ ...formData, goal_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">No goal</option>
                    {goals.map((goal) => (
                      <option key={goal.id} value={goal.id}>
                        {goal.title} ({goal.current_count}/{goal.target_count})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.estimated_duration}
                    onChange={(e) => setFormData({ ...formData, estimated_duration: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Status change buttons for editing */}
                {editingTask && (
                  <div className="border-t pt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quick Actions
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {editingTask.status === 'PENDING' && (
                        <>
                          <button
                            type="button"
                            onClick={() => {
                              handleStatusChange(editingTask.id, 'done');
                              setShowForm(false);
                            }}
                            className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
                          >
                            ✓ Mark Done
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              handleStatusChange(editingTask.id, 'skip');
                              setShowForm(false);
                            }}
                            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                          >
                            ⊘ Skip
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              handleStatusChange(editingTask.id, 'postpone');
                              setShowForm(false);
                            }}
                            className="px-3 py-1 text-sm bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200"
                          >
                            → Postpone
                          </button>
                        </>
                      )}
                      {(editingTask.status === 'DONE' || editingTask.status === 'SKIPPED') && (
                        <button
                          type="button"
                          onClick={() => {
                            handleStatusChange(editingTask.id, 'reopen');
                            setShowForm(false);
                          }}
                          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
                        >
                          ↺ Reopen
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => {
                          handleDelete(editingTask.id);
                          setShowForm(false);
                        }}
                        className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                )}

                <div className="flex gap-2 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {editingTask ? 'Update' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingTask(null);
                      resetForm();
                    }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
