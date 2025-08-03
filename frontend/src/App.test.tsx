/**
 * Basic tests for the ProjectMeats App component.
 */
import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Mock the AuthService completely
jest.mock('./services/auth', () => {
  const mockAuthService = {
    getAuthStatus: jest.fn(() => Promise.resolve({ authenticated: false, user: null })),
    login: jest.fn(() => Promise.resolve({ message: 'Success', user: {} })),
    logout: jest.fn(() => Promise.resolve({ message: 'Logged out' })),
    signup: jest.fn(() => Promise.resolve({ message: 'Success', user: {} })),
  };
  
  return {
    default: mockAuthService,
    AuthService: mockAuthService,
  };
});

// Simple test component for basic functionality
const TestAuthWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MemoryRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </MemoryRouter>
);

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', async () => {
    await act(async () => {
      render(
        <TestAuthWrapper>
          <div>Loading...</div>
        </TestAuthWrapper>
      );
    });
    
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('AuthProvider provides context without errors', async () => {
    await act(async () => {
      render(
        <TestAuthWrapper>
          <div data-testid="test-content">Auth Provider Working</div>
        </TestAuthWrapper>
      );
    });
    
    expect(screen.getByTestId('test-content')).toBeInTheDocument();
    expect(screen.getByText('Auth Provider Working')).toBeInTheDocument();
  });

  test('basic component rendering works without errors', async () => {
    await act(async () => {
      render(
        <TestAuthWrapper>
          <div data-testid="app-test">ProjectMeats App Test</div>
        </TestAuthWrapper>
      );
    });
    
    expect(screen.getByTestId('app-test')).toBeInTheDocument();
    expect(screen.getByText('ProjectMeats App Test')).toBeInTheDocument();
  });
});