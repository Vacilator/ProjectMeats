/**
 * Basic tests for the ProjectMeats App component.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

test('renders ProjectMeats title', () => {
  render(<App />);
  const titleElement = screen.getByText(/ProjectMeats/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders main navigation', () => {
  render(<App />);
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
  expect(screen.getByText(/Suppliers/i)).toBeInTheDocument();
  expect(screen.getByText(/Customers/i)).toBeInTheDocument();
});

test('renders sales management subtitle', () => {
  render(<App />);
  const subtitleElement = screen.getByText(/Sales Management/i);
  expect(subtitleElement).toBeInTheDocument();
});