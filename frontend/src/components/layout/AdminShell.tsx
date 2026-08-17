import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { authApi } from '../../api/auth';
import { 
  ShieldAlert, 
  Users, 
  Building2, 
  Map, 
  Lock,
  ClipboardList,
  BrainCircuit,
  Network,
  FolderKanban,
  Building,
  Handshake,
  CheckCircle,
  BarChart3,
  MapPin,
  LineChart,
  Bell,
  FileText,
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { Button } from '../ui/Button';

export const AdminShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, clearAuth } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const path = window.location.pathname;

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
    } finally {
      clearAuth();
      window.location.href = '/';
    }
  };

  const navSections = [
    {
      title: 'ADMINISTRATION',
      items: [
        { label: 'Command Center', href: '/admin', icon: ShieldAlert },
        { label: 'Authorities', href: '/admin/authorities', icon: Users },
        { label: 'Departments', href: '/admin/departments', icon: Building2 },
        { label: 'Wards & Zones', href: '/admin/wards', icon: Map },
        { label: 'Roles & Permissions', href: '/admin/permissions', icon: Lock },
      ]
    },
    {
      title: 'CIVIC OPERATIONS',
      items: [
        { label: 'Complaints', href: '/admin/complaints', icon: ClipboardList },
        { label: 'Civic Intelligence', href: '/admin/intelligence', icon: BrainCircuit },
        { label: 'Problem Clusters', href: '/admin/clusters', icon: Network },
        { label: 'Civic Projects', href: '/admin/projects', icon: FolderKanban },
        { label: 'Organizations', href: '/admin/organizations', icon: Building },
        { label: 'Resource Matching', href: '/admin/matching', icon: Handshake },
        { label: 'Outcome Verification', href: '/admin/outcomes', icon: CheckCircle },
      ]
    },
    {
      title: 'ANALYTICS',
      items: [
        { label: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
        { label: 'Hotspots', href: '/admin/hotspots', icon: MapPin },
        { label: 'Predictive Intelligence', href: '/admin/predictions', icon: LineChart },
      ]
    },
    {
      title: 'SYSTEM',
      items: [
        { label: 'Notifications', href: '/admin/notifications', icon: Bell },
        { label: 'Audit Logs', href: '/admin/audit', icon: FileText },
        { label: 'System Configuration', href: '/admin/settings', icon: Settings },
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="md:hidden bg-slate-900 shadow-sm border-b flex justify-between items-center p-4">
        <a href="/admin" className="text-xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="h-6 w-6" /> CivicPulse X
        </a>
        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          {mobileMenuOpen ? <X className="h-6 w-6 text-white" /> : <Menu className="h-6 w-6 text-white" />}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-slate-300 transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0 flex flex-col
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="p-6 hidden md:block border-b border-slate-800">
          <a href="/admin" className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="h-7 w-7 text-indigo-400" /> CivicPulse X
          </a>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          {navSections.map((section) => (
            <div key={section.title} className="mb-6">
              <h3 className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                {section.title}
              </h3>
              <ul className="space-y-1">
                {section.items.map((item) => {
                  const isActive = path === item.href;
                  const Icon = item.icon;
                  return (
                    <li key={item.href}>
                      <a
                        href={item.href}
                        className={`flex items-center gap-3 px-6 py-2 text-sm font-medium transition-colors ${
                          isActive 
                            ? 'bg-slate-800 text-white border-l-4 border-indigo-500' 
                            : 'hover:bg-slate-800 hover:text-white border-l-4 border-transparent'
                        }`}
                      >
                        <Icon className={`h-5 w-5 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                        {item.label}
                      </a>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-950">
          <p className="font-semibold text-white truncate px-2">{user?.display_name}</p>
          <p className="text-xs text-indigo-400 uppercase font-medium mt-1 mb-4 tracking-wider px-2">{user?.role?.replace(/_/g, ' ')}</p>
          <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-white hover:bg-slate-800" onClick={handleLogout}>
            <LogOut className="h-5 w-5 mr-3" />
            Sign Out
          </Button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden bg-slate-50">
        <header className="bg-slate-900 border-b border-slate-800 text-white px-8 py-5 flex justify-between items-center hidden md:flex shadow-md">
          <div>
            <h1 className="text-2xl font-bold">Authority Operations Command</h1>
            <p className="text-sm text-slate-400 mt-1">Centralized civic operations, authority management, problem intelligence and resource coordination.</p>
          </div>
          <div>
            <span className="bg-indigo-900 text-indigo-200 border border-indigo-700 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">
              Global System View
            </span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
