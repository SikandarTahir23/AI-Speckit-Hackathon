/**
 * AuthContext - Authentication state management with Better Auth
 * Provides user authentication state across the application
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useSession } from '@site/src/lib/auth-client';

interface User {
  id: string;
  email: string;
  name: string;
  emailVerified: boolean;
  image?: string;
  createdAt: Date;
  updatedAt: Date;
  softwareBackground?: string;
  hardwareBackground?: string;
  pythonFamiliar?: boolean;
  rosFamiliar?: boolean;
  aimlFamiliar?: boolean;
}

interface Session {
  user: User;
  session: {
    id: string;
    userId: string;
    expiresAt: Date;
    token: string;
  };
}

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: Error | null;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  loading: true,
  error: null,
});

export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { data: session, isPending: loading, error } = useSession();

  const value: AuthContextType = {
    user: session?.user || null,
    session: session || null,
    loading,
    error: error || null,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
