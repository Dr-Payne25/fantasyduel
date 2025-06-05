import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../AuthContext';
import { api } from '../../services/api';

// Unmock the AuthContext for this test file
jest.unmock('../AuthContext');

// Mock the API module
jest.mock('../../services/api', () => ({
  api: {
    setAuthToken: jest.fn(),
    login: jest.fn(),
    register: jest.fn(),
    getCurrentUser: jest.fn(),
    refreshToken: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReset();
    localStorageMock.setItem.mockReset();
    localStorageMock.removeItem.mockReset();
    localStorageMock.clear.mockReset();
  });

  it('throws error when useAuth is used outside AuthProvider', () => {
    const { result } = renderHook(() => {
      try {
        return useAuth();
      } catch (error) {
        return error;
      }
    });

    expect(result.current).toEqual(
      new Error('useAuth must be used within an AuthProvider')
    );
  });

  it('initializes with loading state', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    // Initially should be loading
    expect(result.current.user).toBe(null);

    // Wait for loading to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });

  it('checks for existing session on mount', async () => {
    const mockUser = {
      id: 'test-user',
      email: 'test@example.com',
      username: 'testuser',
      is_active: true,
      is_verified: true,
      theme: 'dark',
      notification_preferences: 'all',
    };

    localStorageMock.getItem.mockReturnValue('test-access-token');
    (api.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(api.setAuthToken).toHaveBeenCalledWith('test-access-token');
    expect(api.getCurrentUser).toHaveBeenCalled();
    expect(result.current.user).toEqual(mockUser);
  });

  it('removes expired token on mount', async () => {
    localStorageMock.getItem.mockReturnValue('expired-token');
    (api.getCurrentUser as jest.Mock).mockRejectedValue(new Error('Token expired'));

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    expect(api.setAuthToken).toHaveBeenCalledWith(null);
    expect(result.current.user).toBe(null);
  });

  it('handles login successfully', async () => {
    const mockTokenResponse = {
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token',
      token_type: 'bearer',
    };
    const mockUser = {
      id: 'test-user',
      email: 'test@example.com',
      username: 'testuser',
      is_active: true,
      is_verified: true,
      theme: 'dark',
      notification_preferences: 'all',
    };

    (api.login as jest.Mock).mockResolvedValue(mockTokenResponse);
    (api.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('testuser', 'password123');
    });

    expect(api.login).toHaveBeenCalledWith('testuser', 'password123');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'new-access-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'new-refresh-token');
    expect(api.setAuthToken).toHaveBeenCalledWith('new-access-token');
    expect(api.getCurrentUser).toHaveBeenCalled();
    expect(result.current.user).toEqual(mockUser);
  });

  it('handles registration and auto-login', async () => {
    const mockNewUser = {
      id: 'new-user',
      email: 'new@example.com',
      username: 'newuser',
    };
    const mockTokenResponse = {
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token',
      token_type: 'bearer',
    };
    const mockUser = {
      id: 'new-user',
      email: 'new@example.com',
      username: 'newuser',
      is_active: true,
      is_verified: true,
      theme: 'dark',
      notification_preferences: 'all',
    };

    (api.register as jest.Mock).mockResolvedValue(mockNewUser);
    (api.login as jest.Mock).mockResolvedValue(mockTokenResponse);
    (api.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.register('new@example.com', 'newuser', 'password123');
    });

    expect(api.register).toHaveBeenCalledWith('new@example.com', 'newuser', 'password123');
    expect(api.login).toHaveBeenCalledWith('newuser', 'password123');
    expect(result.current.user).toEqual(mockUser);
  });

  it('handles logout', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.logout();
    });

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    expect(api.setAuthToken).toHaveBeenCalledWith(null);
    expect(result.current.user).toBe(null);
  });

  it('handles token refresh', async () => {
    const mockTokenResponse = {
      access_token: 'refreshed-access-token',
      refresh_token: 'refreshed-refresh-token',
      token_type: 'bearer',
    };

    localStorageMock.getItem.mockReturnValue('old-refresh-token');
    (api.refreshToken as jest.Mock).mockResolvedValue(mockTokenResponse);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.refreshToken();
    });

    expect(api.refreshToken).toHaveBeenCalledWith('old-refresh-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'refreshed-access-token');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'refreshed-refresh-token');
    expect(api.setAuthToken).toHaveBeenCalledWith('refreshed-access-token');
  });

  it('throws error when no refresh token available', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await expect(result.current.refreshToken()).rejects.toThrow('No refresh token available');
  });

});
