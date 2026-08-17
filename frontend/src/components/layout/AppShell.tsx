import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { authApi } from '../../api/auth';
import { NotificationInbox } from '../NotificationInbox';
import { 
  LayoutDashboard, 
  FileText, 
  PlusCircle, 
  LogOut,
  MapPin,
  Menu,
  X,
  Activity,
  Bell,
  User,
  HelpCircle
} from 'lucide-react';
import { Button } from '../ui/Button';

export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user, clearAuth } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
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

  const navItems = user?.role === 'authority' || user?.role === 'admin' ? [
    { label: 'Operations Console', href: '/authority', icon: Activity },
    { label: 'Predictive Intelligence', href: '/dashboard', icon: LayoutDashboard },
  ] : [
    { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { label: 'Report a Problem', href: '/complaints/new', icon: PlusCircle },
    { label: 'My Complaints', href: '/complaints', icon: FileText },
    { label: 'Notifications', href: '/notifications', icon: Bell },
    { label: 'Profile', href: '/profile', icon: User },
    { label: 'Help', href: '/help', icon: HelpCircle },
  ];

  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="md:hidden bg-white shadow-sm border-b flex justify-between items-center p-4">
        <a href="/" className="text-xl font-bold text-civic-700 flex items-center gap-2">
          <MapPin className="h-6 w-6" /> CivicPulse
        </a>
        <div className="flex items-center gap-4">
          <NotificationInbox onSelectComplaint={(id) => { window.location.href = `/complaints/${id}`; }} />
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="h-6 w-6 text-gray-600" /> : <Menu className="h-6 w-6 text-gray-600" />}
          </button>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r shadow-sm transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="h-full flex flex-col">
          <div className="p-6 border-b hidden md:block">
            <a href="/" className="text-2xl font-bold text-civic-700 flex items-center gap-2">
              <MapPin className="h-7 w-7" /> CivicPulse
            </a>
          </div>
          
          <div className="p-4 border-b bg-gray-50">
            <p className="font-semibold text-gray-900 truncate">{user?.display_name}</p>
            <p className="text-xs text-gray-500 uppercase font-medium mt-1 tracking-wider">{user?.role}</p>
          </div>

          <nav className="flex-1 overflow-y-auto py-4">
            <ul className="space-y-1 px-3">
              {navItems.map((item) => {
                const isActive = path === item.href || path.startsWith(item.href + '/');
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <a
                      href={item.href}
                      className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive 
                          ? 'bg-civic-50 text-civic-700' 
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <Icon className={`h-5 w-5 ${isActive ? 'text-civic-600' : 'text-gray-400'}`} />
                      {item.label}
                    </a>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="p-4 border-t">
            <div className="hidden md:flex justify-between items-center mb-4">
              <NotificationInbox onSelectComplaint={(id) => { window.location.href = `/complaints/${id}`; }} />
            </div>
            <Button variant="ghost" className="w-full justify-start text-gray-600 hover:text-red-600 hover:bg-red-50" onClick={handleLogout}>
              <LogOut className="h-5 w-5 mr-3" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-gray-50">
          <div className="mx-auto max-w-6xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
