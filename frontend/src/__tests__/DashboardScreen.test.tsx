import { render, screen } from '@testing-library/react';

// Simple utility function tests to verify our testing infrastructure
describe('Testing Infrastructure Verification', () => {
  test('basic DOM rendering works', () => {
    const testElement = document.createElement('div');
    testElement.textContent = 'Frontend testing infrastructure is working';
    document.body.appendChild(testElement);
    
    expect(testElement).toBeInTheDocument();
    expect(testElement).toHaveTextContent('Frontend testing infrastructure is working');
    
    document.body.removeChild(testElement);
  });

  test('Jest configuration is working correctly', () => {
    // Test TypeScript support
    const testConfig: { name: string; version: number } = {
      name: 'ProjectMeats Testing',
      version: 1
    };
    
    expect(testConfig.name).toBe('ProjectMeats Testing');
    expect(testConfig.version).toBe(1);
  });

  test('React Testing Library is configured correctly', () => {
    const TestComponent = () => <div data-testid="test">Test Component</div>;
    render(<TestComponent />);
    
    expect(screen.getByTestId('test')).toBeInTheDocument();
    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });

  test('async testing capabilities are available', async () => {
    const AsyncComponent = () => {
      return <div>Async Test Component</div>;
    };
    
    render(<AsyncComponent />);
    const element = await screen.findByText('Async Test Component');
    expect(element).toBeInTheDocument();
  });

  test('mock functions work correctly', () => {
    const mockFn = jest.fn();
    mockFn('test argument');
    
    expect(mockFn).toHaveBeenCalledWith('test argument');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });
});