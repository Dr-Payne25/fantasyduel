import { api } from '../api';

// Mock fetch globally
global.fetch = jest.fn();

describe('API Service - Authentication', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset auth token
    api.setAuthToken(null);
  });

  describe('setAuthToken', () => {
    it('stores auth token for use in requests', async () => {
      api.setAuthToken('test-token');
      
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'test' }),
      });

      await api.getLeagues();

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/leagues',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      );
    });

    it('removes auth token when set to null', async () => {
      api.setAuthToken('test-token');
      api.setAuthToken(null);
      
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'test' }),
      });

      await api.getLeagues();

      const headers = (global.fetch as jest.Mock).mock.calls[0][1].headers;
      expect(headers['Authorization']).toBeUndefined();
    });
  });

  describe('register', () => {
    it('registers a new user', async () => {
      const mockUser = {
        id: 'new-user',
        email: 'new@example.com',
        username: 'newuser',
        is_active: true,
        is_verified: false,
        theme: 'dark',
        notification_preferences: 'all',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const result = await api.register('new@example.com', 'newuser', 'password123');

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/register',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            email: 'new@example.com',
            username: 'newuser',
            password: 'password123',
          }),
        })
      );
      expect(result).toEqual(mockUser);
    });

    it('throws error on registration failure', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Username already exists' }),
      });

      await expect(
        api.register('existing@example.com', 'existinguser', 'password123')
      ).rejects.toThrow('Username already exists');
    });
  });

  describe('login', () => {
    it('logs in a user and returns tokens', async () => {
      const mockTokenResponse = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTokenResponse,
      });

      const result = await api.login('testuser', 'password123');

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/x-www-form-urlencoded',
          }),
          body: expect.any(URLSearchParams),
        })
      );
      
      const callArgs = (global.fetch as jest.Mock).mock.calls[0];
      expect(callArgs[1].body.toString()).toBe('username=testuser&password=password123');
      expect(result).toEqual(mockTokenResponse);
    });

    it('throws error on login failure', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      await expect(api.login('testuser', 'wrongpassword')).rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('logs out the user', async () => {
      api.setAuthToken('test-token');

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logged out successfully' }),
      });

      await api.logout();

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/logout',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      );
    });
  });

  describe('getCurrentUser', () => {
    it('fetches current user info', async () => {
      const mockUser = {
        id: 'test-user',
        email: 'test@example.com',
        username: 'testuser',
        is_active: true,
        is_verified: true,
        theme: 'dark',
        notification_preferences: 'all',
      };

      api.setAuthToken('test-token');

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const result = await api.getCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/me',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      );
      expect(result).toEqual(mockUser);
    });

    it('throws error when not authenticated', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Not authenticated' }),
      });

      await expect(api.getCurrentUser()).rejects.toThrow('Not authenticated');
    });
  });

  describe('refreshToken', () => {
    it('refreshes access token', async () => {
      const mockTokenResponse = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        token_type: 'bearer',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTokenResponse,
      });

      const result = await api.refreshToken('old-refresh-token');

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/refresh',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({ refresh_token: 'old-refresh-token' }),
        })
      );
      expect(result).toEqual(mockTokenResponse);
    });

    it('throws error on invalid refresh token', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid refresh token' }),
      });

      await expect(api.refreshToken('invalid-token')).rejects.toThrow('Invalid refresh token');
    });
  });

  describe('error handling', () => {
    it('handles network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(api.login('testuser', 'password')).rejects.toThrow('Network error');
    });

    it('handles non-JSON error responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => { throw new Error('Invalid JSON'); },
        text: async () => 'Internal Server Error',
      });

      await expect(api.login('testuser', 'password')).rejects.toThrow('Login failed');
    });
  });
});