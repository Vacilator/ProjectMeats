/**
 * Authentication service for ProjectMeats frontend.
 * 
 * Handles user authentication, login, logout, signup, and session management.
 */
import axios, { InternalAxiosRequestConfig, AxiosError } from 'axios';
import { UserProfile } from '../types';

// Configure API base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance for auth requests
const authClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for session authentication
});

// Add CSRF token interceptor
authClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get CSRF token from cookies for non-GET requests
    if (config.method && config.method.toLowerCase() !== 'get') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
          config.headers = config.headers || {};
          config.headers['X-CSRFToken'] = value;
          break;
        }
      }
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Types for authentication
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  department?: string;
  job_title?: string;
}

export interface AuthResponse {
  message: string;
  user: UserProfile;
}

export interface AuthStatus {
  authenticated: boolean;
  user: UserProfile | null;
}

/**
 * Authentication service class
 */
export class AuthService {
  /**
   * Login user with username and password
   */
  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await authClient.post('/auth/login/', credentials);
    return response.data;
  }

  /**
   * Logout current user
   */
  static async logout(): Promise<{ message: string }> {
    const response = await authClient.post('/auth/logout/');
    return response.data;
  }

  /**
   * Register new user
   */
  static async signup(userData: SignupData): Promise<AuthResponse> {
    const response = await authClient.post('/auth/signup/', userData);
    return response.data;
  }

  /**
   * Get current authentication status
   */
  static async getAuthStatus(): Promise<AuthStatus> {
    try {
      const response = await authClient.get('/auth/status/');
      return response.data;
    } catch (error) {
      return {
        authenticated: false,
        user: null
      };
    }
  }

  /**
   * Get current user profile (requires authentication)
   */
  static async getCurrentUserProfile(): Promise<UserProfile> {
    const response = await authClient.get('/user-profiles/me/');
    return response.data;
  }
}

export default AuthService;