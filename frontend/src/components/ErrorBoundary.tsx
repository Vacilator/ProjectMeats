import React, { Component, ErrorInfo, ReactNode } from 'react';
import styled from 'styled-components';
import { colors, typography, spacing, borderRadius } from './DesignSystem';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: ${spacing.xl};
  background-color: ${colors.surface};
  border: 2px solid ${colors.error};
  border-radius: ${borderRadius.lg};
  margin: ${spacing.lg};
`;

const ErrorTitle = styled.h2`
  color: ${colors.error};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.xl};
  font-weight: ${typography.fontWeight.bold};
  margin-bottom: ${spacing.md};
  text-align: center;
`;

const ErrorMessage = styled.p`
  color: ${colors.text.secondary};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.base};
  line-height: ${typography.lineHeight.relaxed};
  text-align: center;
  margin-bottom: ${spacing.lg};
  max-width: 600px;
`;

const RetryButton = styled.button`
  background-color: ${colors.primary[500]};
  color: white;
  border: none;
  border-radius: ${borderRadius.md};
  padding: ${spacing.sm} ${spacing.lg};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.base};
  font-weight: ${typography.fontWeight.medium};
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: ${colors.primary[600]};
  }

  &:focus {
    outline: 2px solid ${colors.primary[300]};
    outline-offset: 2px;
  }
`;

const ErrorDetails = styled.details`
  margin-top: ${spacing.lg};
  max-width: 800px;
  width: 100%;
`;

const ErrorSummary = styled.summary`
  color: ${colors.text.secondary};
  font-family: ${typography.fontFamily.sans};
  font-size: ${typography.fontSize.sm};
  cursor: pointer;
  padding: ${spacing.sm};
  border-radius: ${borderRadius.sm};
  background-color: ${colors.neutral[100]};
  margin-bottom: ${spacing.sm};

  &:hover {
    background-color: ${colors.neutral[200]};
  }
`;

const ErrorStackTrace = styled.pre`
  background-color: ${colors.neutral[50]};
  border: 1px solid ${colors.neutral[300]};
  border-radius: ${borderRadius.sm};
  padding: ${spacing.md};
  font-family: ${typography.fontFamily.mono};
  font-size: ${typography.fontSize.sm};
  line-height: ${typography.lineHeight.normal};
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: ${colors.text.primary};
`;

/**
 * Error Boundary component for graceful error handling in ProjectMeats.
 * 
 * This component catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of the component tree that crashed.
 * 
 * Features:
 * - Professional error UI with retry functionality
 * - Error logging for debugging
 * - Accessible design with proper focus management
 * - Expandable error details for developers
 * - Consistent styling with design system
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Update state with error details
    this.setState({
      error,
      errorInfo,
    });

    // Log error for debugging
    console.error('🚨 ErrorBoundary caught an error:', error);
    console.error('📍 Error info:', errorInfo);

    // In production, you might want to log this to an error reporting service
    // Example: logErrorToService(error, errorInfo);
  }

  handleRetry = () => {
    // Reset error state to retry rendering
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <ErrorContainer role="alert" aria-live="assertive">
          <ErrorTitle>Something went wrong</ErrorTitle>
          <ErrorMessage>
            We're sorry, but something unexpected happened. This might be a temporary issue.
            You can try refreshing the page or contact support if the problem persists.
          </ErrorMessage>
          <RetryButton onClick={this.handleRetry} aria-label="Retry loading the component">
            Try Again
          </RetryButton>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <ErrorDetails>
              <ErrorSummary>
                🔧 Developer Details (click to expand)
              </ErrorSummary>
              <ErrorStackTrace>
                <strong>Error:</strong> {this.state.error.message}
                {'\n\n'}
                <strong>Stack Trace:</strong>
                {'\n'}
                {this.state.error.stack}
                {this.state.errorInfo && (
                  <>
                    {'\n\n'}
                    <strong>Component Stack:</strong>
                    {'\n'}
                    {this.state.errorInfo.componentStack}
                  </>
                )}
              </ErrorStackTrace>
            </ErrorDetails>
          )}
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;