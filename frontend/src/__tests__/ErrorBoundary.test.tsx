import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary from '../components/ErrorBoundary';

// Component that throws an error for testing
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error for ErrorBoundary');
  }
  return <div>No error occurred</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error for these tests since we're testing error scenarios
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  test('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('No error occurred')).toBeInTheDocument();
  });

  test('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText(/We're sorry, but something unexpected happened/)).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('shows retry functionality', async () => {
    const user = userEvent.setup();
    
    // Create a component that can toggle error state
    const TestComponent = () => {
      const [shouldThrow, setShouldThrow] = React.useState(true);
      
      return (
        <div>
          <button onClick={() => setShouldThrow(!shouldThrow)}>
            Toggle Error
          </button>
          <ErrorBoundary>
            <ThrowError shouldThrow={shouldThrow} />
          </ErrorBoundary>
        </div>
      );
    };

    render(<TestComponent />);
    
    // Initially should show error
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    
    // Click retry button
    const retryButton = screen.getByText('Try Again');
    await user.click(retryButton);
    
    // Error boundary should reset and show the error again (since shouldThrow is still true)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  test('renders custom fallback when provided', () => {
    const customFallback = <div>Custom error message</div>;
    
    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Custom error message')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });

  test('has proper accessibility attributes', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    const errorContainer = screen.getByRole('alert');
    expect(errorContainer).toBeInTheDocument();
    expect(errorContainer).toHaveAttribute('aria-live', 'assertive');
    
    const retryButton = screen.getByRole('button', { name: /retry loading the component/i });
    expect(retryButton).toBeInTheDocument();
  });

  test('logs error to console in development', () => {
    const mockConsoleError = jest.fn();
    console.error = mockConsoleError;
    
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(mockConsoleError).toHaveBeenCalledWith(
      expect.stringContaining('🚨 ErrorBoundary caught an error:'),
      expect.any(Error)
    );
  });
});