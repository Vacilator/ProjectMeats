import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Simple test component to verify our testing infrastructure
const TestComponent = () => (
  <div>
    <h1>ProjectMeats Test Component</h1>
    <p>Testing infrastructure is working</p>
  </div>
);

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      {component}
    </MemoryRouter>
  );
};

describe('Frontend Testing Infrastructure', () => {
  test('basic React component renders correctly', () => {
    render(<TestComponent />);
    expect(screen.getByText(/ProjectMeats Test Component/i)).toBeInTheDocument();
    expect(screen.getByText(/Testing infrastructure is working/i)).toBeInTheDocument();
  });

  test('router wrapper works correctly', () => {
    renderWithRouter(<TestComponent />);
    expect(screen.getByText(/ProjectMeats Test Component/i)).toBeInTheDocument();
  });

  test('Jest configuration handles TypeScript correctly', () => {
    const testValue: string = 'TypeScript test';
    expect(testValue).toBe('TypeScript test');
  });

  test('testing library matchers are available', () => {
    render(<TestComponent />);
    const heading = screen.getByRole('heading');
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveTextContent('ProjectMeats Test Component');
  });

  test('async testing capabilities work', async () => {
    render(<TestComponent />);
    const element = await screen.findByText(/Testing infrastructure is working/i);
    expect(element).toBeInTheDocument();
  });
});