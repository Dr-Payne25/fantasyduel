import React from 'react';
import { render, screen } from '../../../test-utils/test-utils';
import { Navigate } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';

jest.mock('react-router-dom');

const mockUseLocation = jest.fn();
beforeEach(() => {
  const ReactRouterDom = require('react-router-dom');
  ReactRouterDom.useLocation = mockUseLocation;
  mockUseLocation.mockReturnValue({ pathname: '/protected' });
});

describe('ProtectedRoute Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading spinner when auth is loading', () => {
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      {
        authValue: {
          user: null,
          loading: true,
          login: jest.fn(),
          register: jest.fn(),
          logout: jest.fn(),
          refreshToken: jest.fn(),
        },
      }
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('renders children when user is authenticated', () => {
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      {
        authValue: {
          user: {
            id: 'test-user',
            email: 'test@example.com',
            username: 'testuser',
            is_active: true,
            is_verified: true,
            theme: 'dark',
            notification_preferences: 'all',
            created_at: '2025-01-01T00:00:00Z',
          },
          loading: false,
          login: jest.fn(),
          register: jest.fn(),
          logout: jest.fn(),
          refreshToken: jest.fn(),
        },
      }
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(Navigate).not.toHaveBeenCalled();
  });

  it('redirects to login when user is not authenticated', () => {
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      {
        authValue: {
          user: null,
          loading: false,
          login: jest.fn(),
          register: jest.fn(),
          logout: jest.fn(),
          refreshToken: jest.fn(),
        },
      }
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    expect(Navigate).toHaveBeenCalledWith(
      { to: '/login', state: { from: { pathname: '/protected' } }, replace: true },
      undefined
    );
  });
});
