import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';

// Mock user for testing
export const mockUser = {
  id: 'test-user-id',
  email: 'test@example.com',
  username: 'testuser',
  is_active: true,
  is_verified: true,
  theme: 'dark',
  notification_preferences: 'all',
  created_at: '2025-01-01T00:00:00Z'
};

// Mock auth context
export const mockAuthContext = {
  user: mockUser,
  loading: false,
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
  refreshToken: jest.fn(),
};

interface AllTheProvidersProps {
  children: React.ReactNode;
  authValue?: any;
}

// Custom provider that wraps components with all necessary providers
const AllTheProviders: React.FC<AllTheProvidersProps> = ({ children, authValue }) => {
  return (
    <BrowserRouter>
      <AuthProvider value={authValue || mockAuthContext}>
        {children}
      </AuthProvider>
    </BrowserRouter>
  );
};

// Custom render method that includes providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & { authValue?: any }
) => {
  const { authValue, ...renderOptions } = options || {};
  
  return render(ui, {
    wrapper: ({ children }) => (
      <AllTheProviders authValue={authValue}>{children}</AllTheProviders>
    ),
    ...renderOptions,
  });
};

// Re-export everything
export * from '@testing-library/react';

// Override render method
export { customRender as render };