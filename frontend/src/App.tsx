import { useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { MyComplaints } from './components/MyComplaints';
import { ComplaintForm } from './components/ComplaintForm';
import { ComplaintDetail } from './components/ComplaintDetail';
import { Dashboard } from './components/Dashboard';
import { AuthorityDashboard } from './components/AuthorityDashboard';
import { AuthForm } from './components/AuthForm';
import { PredictiveIntelligence } from './components/PredictiveIntelligence';
import { CivicOpportunities } from './components/CivicOpportunities';
import { Organizations } from './components/Organizations';
import { Profile } from './components/Profile';
import { Help } from './components/Help';
import { NotificationsPage } from './components/NotificationsPage';
import { AppShell } from './components/layout/AppShell';
import { AdminShell } from './components/layout/AdminShell';
import { AdminRoutes } from './components/admin/AdminRoutes';
import type { UserRole } from './api/auth';

function App() {
  const { isAuthenticated, user } = useAuth();
  const path = window.location.pathname;

  const renderContent = () => {
    if (!isAuthenticated) {
      return <AuthForm />;
    }

    const authorityRoles: UserRole[] = [
      'authority', 'admin', 'super_admin', 'municipal_admin',
      'department_head', 'ward_supervisor', 'authority_officer', 'field_inspector'
    ];
    
    const isAuthority = authorityRoles.includes(user?.role as UserRole);
    const isSuperAdmin = user?.role === 'super_admin' || user?.role === 'municipal_admin';

    // ----------------------------------------------------
    // Admin Shell Routes (Strictly for Super Admin / Municipal Admin)
    // ----------------------------------------------------
    if (isSuperAdmin && path.startsWith('/admin')) {
      return <ProtectedRoute allowedRoles={['super_admin', 'municipal_admin']}><AdminRoutes path={path} /></ProtectedRoute>;
    }

    // ----------------------------------------------------
    // Authority / Citizen Routes (Uses standard AppShell)
    // ----------------------------------------------------
    if (path === '/authority' || (path === '/dashboard' && isAuthority && !isSuperAdmin)) {
      return <ProtectedRoute allowedRoles={authorityRoles}><AuthorityDashboard /></ProtectedRoute>;
    }
    if (path === '/dashboard') {
      return <ProtectedRoute allowedRoles={['citizen']}><Dashboard /></ProtectedRoute>;
    }
    if (path === '/complaints/new') {
      return <ProtectedRoute allowedRoles={['citizen']}><ComplaintForm /></ProtectedRoute>;
    }
    if (path === '/complaints') {
      return <ProtectedRoute allowedRoles={['citizen']}><MyComplaints /></ProtectedRoute>;
    }
    if (path.startsWith('/complaints/')) {
      const id = path.split('/')[2];
      return <ProtectedRoute allowedRoles={['citizen']}><ComplaintDetail complaintId={id} /></ProtectedRoute>;
    }
    if (path === '/intelligence') {
      return <ProtectedRoute allowedRoles={['citizen', ...authorityRoles]}><PredictiveIntelligence /></ProtectedRoute>;
    }
    if (path === '/opportunities') {
      return <ProtectedRoute allowedRoles={['citizen', ...authorityRoles]}><CivicOpportunities /></ProtectedRoute>;
    }
    if (path === '/organizations') {
      return <ProtectedRoute allowedRoles={['citizen', ...authorityRoles]}><Organizations /></ProtectedRoute>;
    }
    if (path === '/profile') {
      return <ProtectedRoute allowedRoles={['citizen']}><Profile /></ProtectedRoute>;
    }
    if (path === '/help') {
      return <ProtectedRoute allowedRoles={['citizen']}><Help /></ProtectedRoute>;
    }
    if (path === '/notifications') {
      return <ProtectedRoute allowedRoles={['citizen', ...authorityRoles]}><NotificationsPage /></ProtectedRoute>;
    }

    // Default authenticated view
    if (isSuperAdmin && !path.startsWith('/admin')) {
        window.location.href = '/admin';
        return null;
    }
    if (isAuthority && !isSuperAdmin) {
       window.location.href = '/authority';
       return null;
    }
    window.location.href = '/dashboard';
    return null;
  };

  if (user && (user.role === 'super_admin' || user.role === 'municipal_admin') && path.startsWith('/admin')) {
    return (
      <AdminShell>
        {renderContent()}
      </AdminShell>
    );
  }

  return (
    <AppShell>
      {renderContent()}
    </AppShell>
  );
}

export default App;
