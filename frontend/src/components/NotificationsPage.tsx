import React, { useState, useEffect } from 'react';
import { notificationsApi } from '../api/notifications';
import type { NotificationItem } from '../api/notifications';
import { Bell, Check, Circle, ExternalLink } from 'lucide-react';
import { Button } from './ui/Button';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  useEffect(() => {
    loadNotifications();
  }, [filter]);

  const loadNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const items = await notificationsApi.getNotifications(filter === 'unread');
      setNotifications(items);
    } catch (err: any) {
      setError(err.message || 'Failed to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (item: NotificationItem) => {
    if (!item.read) {
      try {
        await notificationsApi.markAsRead(item.id);
        setNotifications((prev) =>
          prev.map((n) => (n.id === item.id ? { ...n, read: true, read_at: new Date().toISOString() } : n))
        );
      } catch (err) {
        console.error('Failed to mark read', err);
      }
    }
    if (item.complaint_id) {
      window.location.href = `/complaints/${item.complaint_id}`;
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true, read_at: new Date().toISOString() })));
    } catch (err) {
      console.error('Failed to mark all read', err);
    }
  };

  if (loading && notifications.length === 0) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-slate-500 space-y-4">
        <div className="w-8 h-8 border-4 border-slate-200 border-t-civic-600 rounded-full animate-spin"></div>
        <p className="text-sm font-medium">Loading notifications...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 animate-in fade-in">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <Bell className="h-8 w-8 text-civic-600" />
            Notifications
          </h1>
          <p className="text-slate-500 mt-1">Updates on your reported civic issues.</p>
        </div>
        <div className="flex gap-2 bg-slate-100 p-1 rounded-lg">
          <button 
            onClick={() => setFilter('all')} 
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${filter === 'all' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600 hover:text-slate-900'}`}
          >
            All
          </button>
          <button 
            onClick={() => setFilter('unread')} 
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${filter === 'unread' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Unread
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
          <span className="text-sm font-medium text-slate-600">
            {notifications.filter(n => !n.read).length} unread
          </span>
          {notifications.some(n => !n.read) && (
            <Button variant="ghost" size="sm" onClick={handleMarkAllRead} className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50">
              <Check className="h-4 w-4 mr-2" /> Mark all as read
            </Button>
          )}
        </div>

        {error ? (
           <div className="p-8 text-center text-red-500">
             {error}
           </div>
        ) : notifications.length === 0 ? (
          <div className="py-20 text-center flex flex-col items-center justify-center">
            <Bell className="h-16 w-16 text-slate-200 mb-4" />
            <h3 className="text-lg font-bold text-slate-700">YOU'RE ALL CAUGHT UP</h3>
            <p className="text-slate-500 mt-2">No new notifications at this time.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {notifications.map((item) => (
              <div 
                key={item.id}
                onClick={() => handleMarkAsRead(item)}
                className={`p-6 cursor-pointer transition-colors flex gap-4 items-start ${item.read ? 'bg-white hover:bg-slate-50' : 'bg-indigo-50/30 hover:bg-indigo-50/50'}`}
              >
                <div className="mt-1 flex-shrink-0">
                  {item.read ? (
                    <Circle className="h-3 w-3 text-slate-300" />
                  ) : (
                    <div className="h-3 w-3 bg-indigo-600 rounded-full shadow-[0_0_0_4px_rgba(79,70,229,0.1)]" />
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className={`text-base mb-1 ${item.read ? 'text-slate-700 font-medium' : 'text-slate-900 font-bold'}`}>
                    {item.title}
                  </p>
                  <p className="text-sm text-slate-600 leading-relaxed mb-3 max-w-3xl">
                    {item.body}
                  </p>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-slate-400 font-medium tracking-wider uppercase">
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                    {item.complaint_id && (
                      <span className="text-xs text-indigo-600 font-medium flex items-center gap-1 group-hover:underline">
                        View Report <ExternalLink className="h-3 w-3" />
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
