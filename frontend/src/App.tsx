import { useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { MyComplaints } from './components/MyComplaints';
import { ComplaintForm } from './components/ComplaintForm';
import { ComplaintDetail } from './components/ComplaintDetail';
import { Dashboard } from './components/Dashboard';
import { AuthorityDashboard } from './components/AuthorityDashboard';
import { AuthForm } from './components/AuthForm';
import { PredictiveIntelligence } from './components/PredictiveIntelligence';
import { AppShell } from './components/layout/AppShell';

function App() {
  const { isAuthenticated, user } = useAuth();
  const path = window.location.pathname;

  const renderContent = () => {
    if (!isAuthenticated) {
      return <AuthForm />;
    }

    if (path === '/authority' || (path === '/dashboard' && (user?.role === 'authority' || user?.role === 'admin'))) {
      return <ProtectedRoute allowedRoles={['authority', 'admin']}><AuthorityDashboard /></ProtectedRoute>;
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
      return <ProtectedRoute allowedRoles={['citizen', 'authority', 'admin']}><PredictiveIntelligence /></ProtectedRoute>;
    }

    // Default authenticated view
    if (user?.role === 'authority' || user?.role === 'admin') {
       window.location.href = '/authority';
       return null;
    }
    window.location.href = '/dashboard';
    return null;
  };

  return (
    <AppShell>
      {renderContent()}
    </AppShell>
  );
}

export default App;
