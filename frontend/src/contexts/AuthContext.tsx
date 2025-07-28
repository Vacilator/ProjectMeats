/**
 * Authentication context for ProjectMeats.
 * 
 * Provides authentication state management and user session handling
 * throughout the React application.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile } from '../types';
import AuthService, { LoginCredentials, SignupData } from '../services/auth';

// Authentication context type
interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  signup: (userData: SignupData) => Promise<boolean>;
  clearError: () => void;
  checkAuthStatus: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Authentication provider props
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication provider component
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = user !== null;

  /**
   * Clear any error messages
   */
  const clearError = () => {
    setError(null);
  };

  /**
   * Check authentication status on app load
   */
  const checkAuthStatus = async () => {
    try {
      setIsLoading(true);
      const authStatus = await AuthService.getAuthStatus();
      
      if (authStatus.authenticated && authStatus.user) {
        setUser(authStatus.user);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error('Error checking auth status:', err);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Login user
   */
  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await AuthService.login(credentials);
      setUser(response.user);
      
      return true;
    } catch (err: any) {
      console.error('Login error:', err);
      const errorMessage = err.response?.data?.error || 'Login failed. Please try again.';
      setError(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logout user
   */
  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true);
      await AuthService.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      setError(null);
      setIsLoading(false);
    }
  };

  /**
   * Sign up new user
   */
  const signup = async (userData: SignupData): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await AuthService.signup(userData);
      setUser(response.user);
      
      return true;
    } catch (err: any) {
      console.error('Signup error:', err);
      const errorMessage = err.response?.data?.error || 
                           err.response?.data?.message || 
                           'Signup failed. Please try again.';
      setError(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    signup,
    clearError,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Hook to use authentication context
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;