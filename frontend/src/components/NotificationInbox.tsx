import React, { useState, useEffect, useRef } from 'react';
import { notificationsApi } from '../api/notifications';
import type { NotificationItem, NotificationPreferences } from '../api/notifications';
import { Bell, Settings, Inbox, Circle } from 'lucide-react';

interface NotificationInboxProps {
  onSelectComplaint?: (complaintId: string) => void;
}

export const NotificationInbox: React.FC<NotificationInboxProps> = ({ onSelectComplaint }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Preferences State
  const [showPrefs, setShowPrefs] = useState(false);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [savingPrefs, setSavingPrefs] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchUnreadCount = async () => {
    try {
      const count = await notificationsApi.getUnreadCount();
      setUnreadCount(count);
    } catch {
      // Quiet fail for badge polling
    }
  };

  const fetchNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const items = await notificationsApi.getNotifications(unreadOnly);
      setNotifications(items);
    } catch (err: any) {
      setError(err.message || 'Failed to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPreferences = async () => {
    try {
      const prefs = await notificationsApi.getPreferences();
      setPreferences(prefs);
    } catch (err: any) {
      console.error('Failed to fetch preferences', err);
    }
  };

  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000); // 30s poll
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen, unreadOnly]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setShowPrefs(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkAsRead = async (item: NotificationItem) => {
    if (!item.read) {
      try {
        await notificationsApi.markAsRead(item.id);
        setNotifications((prev) =>
          prev.map((n) => (n.id === item.id ? { ...n, read: true, read_at: new Date().toISOString() } : n))
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
      } catch (err) {
        console.error('Failed to mark read', err);
      }
    }
    if (item.complaint_id && onSelectComplaint) {
      onSelectComplaint(item.complaint_id);
      setIsOpen(false);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true, read_at: new Date().toISOString() })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all read', err);
    }
  };

  const handleTogglePref = async (key: keyof NotificationPreferences) => {
    if (!preferences) return;
    const updatedValue = !preferences[key];
    setSavingPrefs(true);
    try {
      const updated = await notificationsApi.updatePreferences({ [key]: updatedValue });
      setPreferences(updated);
    } catch (err) {
      console.error('Failed to update preferences', err);
    } finally {
      setSavingPrefs(false);
    }
  };

  return (
    <div className="relative z-50" ref={dropdownRef}>
      {/* Notification Bell Button */}
      <button
        onClick={() => {
          setIsOpen(!isOpen);
          if (!showPrefs && !preferences) fetchPreferences();
        }}
        className={`relative p-2 rounded-full transition-colors flex items-center justify-center ${
          isOpen ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
        }`}
        title="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-white text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1 border-2 border-slate-900">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel Dropdown */}
      {isOpen && (
        <div className="absolute right-0 top-12 w-80 sm:w-96 bg-white border border-slate-200 rounded-xl shadow-xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-top-4 duration-200 origin-top-right">
          
          {/* Header */}
          <div className="px-4 py-3 border-b border-slate-100 flex justify-between items-center bg-slate-50">
            <div className="flex items-center gap-2">
              <h4 className="m-0 text-slate-900 text-sm font-semibold">
                {showPrefs ? 'Notification Settings' : 'Notifications'}
              </h4>
              {!showPrefs && unreadCount > 0 && (
                <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-bold">
                  {unreadCount} new
                </span>
              )}
            </div>
            <button
              onClick={() => setShowPrefs(!showPrefs)}
              className="text-slate-400 hover:text-slate-700 transition-colors"
              title="Settings"
            >
              {showPrefs ? <Inbox className="h-4 w-4" /> : <Settings className="h-4 w-4" />}
            </button>
          </div>

          {/* Body Content */}
          {showPrefs ? (
            /* Preferences Panel */
            <div className="p-4 bg-white text-sm">
              <p className="text-slate-500 mb-4 text-xs">
                Configure how you want to receive updates about your reported issues.
              </p>
              {preferences ? (
                <div className="flex flex-col gap-4">
                  <label className="flex justify-between items-center cursor-pointer group">
                    <span className="text-slate-700 font-medium group-hover:text-slate-900">In-App Notifications</span>
                    <input
                      type="checkbox"
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer"
                      checked={preferences.in_app_enabled}
                      onChange={() => handleTogglePref('in_app_enabled')}
                      disabled={savingPrefs}
                    />
                  </label>
                  <label className="flex justify-between items-center cursor-pointer group">
                    <span className="text-slate-700 font-medium group-hover:text-slate-900">Email Notifications</span>
                    <input
                      type="checkbox"
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer"
                      checked={preferences.email_enabled}
                      onChange={() => handleTogglePref('email_enabled')}
                      disabled={savingPrefs}
                    />
                  </label>
                  <label className="flex justify-between items-center cursor-pointer group">
                    <span className="text-slate-700 font-medium group-hover:text-slate-900">SMS Notifications</span>
                    <input
                      type="checkbox"
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer"
                      checked={preferences.sms_enabled}
                      onChange={() => handleTogglePref('sms_enabled')}
                      disabled={savingPrefs}
                    />
                  </label>
                  <label className="flex justify-between items-center cursor-pointer group">
                    <span className="text-slate-700 font-medium group-hover:text-slate-900">Push Notifications</span>
                    <input
                      type="checkbox"
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer"
                      checked={preferences.push_enabled}
                      onChange={() => handleTogglePref('push_enabled')}
                      disabled={savingPrefs}
                    />
                  </label>
                </div>
              ) : (
                <p className="text-slate-400 text-center py-4">Loading preferences...</p>
              )}
            </div>
          ) : (
            /* Notifications Inbox List */
            <>
              {/* Filter bar */}
              <div className="px-4 py-2 border-b border-slate-100 flex justify-between items-center text-xs bg-white">
                <div className="flex gap-4">
                  <button
                    onClick={() => setUnreadOnly(false)}
                    className={`transition-colors ${!unreadOnly ? 'text-blue-600 font-semibold' : 'text-slate-500 hover:text-slate-800'}`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => setUnreadOnly(true)}
                    className={`transition-colors ${unreadOnly ? 'text-blue-600 font-semibold' : 'text-slate-500 hover:text-slate-800'}`}
                  >
                    Unread
                  </button>
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
                  >
                    Mark all as read
                  </button>
                )}
              </div>

              {/* List */}
              <div className="flex-1 overflow-y-auto max-h-[360px] bg-white divide-y divide-slate-50">
                {loading ? (
                  <div className="p-8 text-center text-slate-400 text-sm flex flex-col items-center">
                    <div className="w-5 h-5 border-2 border-slate-200 border-t-blue-500 rounded-full animate-spin mb-2"></div>
                    Loading...
                  </div>
                ) : error ? (
                  <div className="p-6 text-center text-red-500 text-sm">
                    {error}
                  </div>
                ) : notifications.length === 0 ? (
                  <div className="p-8 text-center text-slate-400 flex flex-col items-center justify-center">
                    <Bell className="h-8 w-8 mb-2 opacity-20" />
                    <span className="text-sm">No notifications yet.</span>
                  </div>
                ) : (
                  notifications.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => handleMarkAsRead(item)}
                      className={`p-4 cursor-pointer transition-colors flex gap-3 items-start ${
                        item.read ? 'bg-white hover:bg-slate-50' : 'bg-blue-50/50 hover:bg-blue-50'
                      }`}
                    >
                      {/* Read status dot */}
                      <div className="mt-1 flex-shrink-0">
                        {item.read ? (
                          <Circle className="h-2 w-2 text-transparent" />
                        ) : (
                          <div className="h-2 w-2 bg-blue-500 rounded-full" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm mb-1 ${item.read ? 'text-slate-600 font-medium' : 'text-slate-900 font-semibold'}`}>
                          {item.title}
                        </p>
                        <p className="text-xs text-slate-500 leading-relaxed line-clamp-2 mb-1">
                          {item.body}
                        </p>
                        <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">
                          {new Date(item.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};
