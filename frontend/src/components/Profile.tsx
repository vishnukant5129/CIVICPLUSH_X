import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { User, Mail, Shield } from 'lucide-react';

export const Profile: React.FC = () => {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-3xl mx-auto py-8 animate-in fade-in">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">My Profile</h1>
      <p className="text-slate-500 mb-8">Manage your account information and preferences.</p>

      <Card className="shadow-sm border-0 rounded-xl mb-6">
        <CardHeader className="border-b border-slate-100 pb-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <User className="h-5 w-5 text-indigo-500" /> Account Details
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-sm font-medium text-slate-500">Full Name</div>
              <div className="md:col-span-2 text-slate-900 font-medium">{user.display_name}</div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-sm font-medium text-slate-500 flex items-center gap-1">
                <Mail className="h-4 w-4" /> Email Address
              </div>
              <div className="md:col-span-2 text-slate-900">{user.email}</div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-sm font-medium text-slate-500 flex items-center gap-1">
                <Shield className="h-4 w-4" /> Account Type
              </div>
              <div className="md:col-span-2 text-slate-900 capitalize">
                {user.role.replace(/_/g, ' ')}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card className="shadow-sm border-0 rounded-xl">
        <CardHeader className="border-b border-slate-100 pb-4">
          <CardTitle className="text-lg">Account Settings</CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <p className="text-sm text-slate-500 mb-4">
            Your account is managed via Google OAuth. To update your password or profile picture, please visit your Google Account settings.
          </p>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
            <p className="text-sm font-medium text-slate-700">Notification Preferences</p>
            <p className="text-xs text-slate-500 mt-1 mb-3">Choose how you receive updates about your complaints.</p>
            <label className="flex items-center gap-2 cursor-not-allowed opacity-70">
              <input type="checkbox" checked disabled className="rounded text-indigo-600 focus:ring-indigo-500" />
              <span className="text-sm">In-app notifications (Required)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer mt-2">
              <input type="checkbox" defaultChecked className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
              <span className="text-sm text-slate-700">Email notifications for major status changes</span>
            </label>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
