import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../test-utils/test-utils';
import { useNavigate } from 'react-router-dom';
import Login from '../Login';

jest.mock('react-router-dom');

describe('Login Component', () => {
  const mockNavigate = jest.fn();
  const mockLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);
  });

  it('renders login form', () => {
    render(<Login />);

    expect(screen.getByText('Sign in to FantasyDuel')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Username or email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/create a new account/i)).toBeInTheDocument();
  });

  it('handles form submission with valid credentials', async () => {
    mockLogin.mockResolvedValueOnce(undefined);

    render(<Login />, {
      authValue: {
        user: null,
        loading: false,
        login: mockLogin,
        register: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
      },
    });

    const usernameInput = screen.getByPlaceholderText('Username or email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123');
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('displays error message on login failure', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));

    render(<Login />, {
      authValue: {
        user: null,
        loading: false,
        login: mockLogin,
        register: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
      },
    });

    const usernameInput = screen.getByPlaceholderText('Username or email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  it('disables submit button while loading', async () => {
    mockLogin.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<Login />, {
      authValue: {
        user: null,
        loading: false,
        login: mockLogin,
        register: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn(),
      },
    });

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(screen.getByPlaceholderText('Username or email'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' }
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText('Signing in...')).toBeInTheDocument();
    });
  });

  it('links to signup page', () => {
    render(<Login />);

    const signupLink = screen.getByText(/create a new account/i);
    expect(signupLink).toHaveAttribute('href', '/signup');
  });
});