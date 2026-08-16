/*
 * CivicPulse AI — Protected Route Foundation.
 */

import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import type { UserRole } from '../api/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

/**
 * Foundation for protecting routes.
 * If user is not authenticated, could redirect to login (placeholder here).
 * If user does not have allowed role, could show unauthorized.
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <div className="p-4">Loading application state...</div>;
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="p-4 text-red-600 bg-red-50 rounded">
        <h2>Authentication Required</h2>
        <p>Please log in to access this page.</p>
        {/* Real implementation would use react-router-dom <Navigate to="/login" /> */}
      </div>
    );
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="p-4 text-orange-600 bg-orange-50 rounded">
        <h2>Access Denied</h2>
        <p>You do not have the required permissions to view this content.</p>
      </div>
    );
  }

  return <>{children}</>;
};
