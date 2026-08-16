/*
 * CivicPulse AI — Auth Context.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { authApi } from '../api/auth';
import type { User } from '../api/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  refreshUser: () => Promise<void>;
  clearAuth: () => void;
  setUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refreshUser = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (err: any) {
      if (err.status !== 401) {
        // Only log/surface unexpected errors. 401 is normal for unauthenticated.
        setError(err.message || 'Failed to verify identity');
      }
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const clearAuth = () => {
    setUser(null);
  };

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        refreshUser,
        clearAuth,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
