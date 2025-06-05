import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../test-utils/test-utils';
import { useNavigate } from 'react-router-dom';
import SignUp from '../SignUp';

jest.mock('react-router-dom');

describe('SignUp Component', () => {
  const mockNavigate = jest.fn();
  const mockRegister = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useNavigate as jest.Mock).mockReturnValue(mockNavigate);
  });

  it('renders signup form', () => {
    render(<SignUp />);

    expect(screen.getByText('Create your account')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('cooluser123')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('At least 8 characters')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Confirm your password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('validates password match', async () => {
    render(<SignUp />);

    const passwordInput = screen.getByPlaceholderText('At least 8 characters');
    const confirmInput = screen.getByPlaceholderText('Confirm your password');
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(screen.getByPlaceholderText('you@example.com'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('cooluser123'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmInput, { target: { value: 'password456' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    });
  });

  it('validates password length', async () => {
    render(<SignUp />);

    const passwordInput = screen.getByPlaceholderText('At least 8 characters');
    const confirmInput = screen.getByPlaceholderText('Confirm your password');
    const submitButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(screen.getByPlaceholderText('you@example.com'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('cooluser123'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(passwordInput, { target: { value: 'short' } });
    fireEvent.change(confirmInput, { target: { value: 'short' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters long')).toBeInTheDocument();
    });
  });

  it('handles successful registration', async () => {
    mockRegister.mockResolvedValueOnce(undefined);

    render(<SignUp />, {
      authValue: {
        user: null,
        loading: false,
        login: jest.fn(),
        register: mockRegister,
        logout: jest.fn(),
        refreshToken: jest.fn(),
      },
    });

    fireEvent.change(screen.getByPlaceholderText('you@example.com'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('cooluser123'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(screen.getByPlaceholderText('At least 8 characters'), {
      target: { value: 'password123' }
    });
    fireEvent.change(screen.getByPlaceholderText('Confirm your password'), {
      target: { value: 'password123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith('test@example.com', 'testuser', 'password123');
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('displays error message on registration failure', async () => {
    mockRegister.mockRejectedValueOnce(new Error('Username already taken'));

    render(<SignUp />, {
      authValue: {
        user: null,
        loading: false,
        login: jest.fn(),
        register: mockRegister,
        logout: jest.fn(),
        refreshToken: jest.fn(),
      },
    });

    fireEvent.change(screen.getByPlaceholderText('you@example.com'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('cooluser123'), {
      target: { value: 'existinguser' }
    });
    fireEvent.change(screen.getByPlaceholderText('At least 8 characters'), {
      target: { value: 'password123' }
    });
    fireEvent.change(screen.getByPlaceholderText('Confirm your password'), {
      target: { value: 'password123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(screen.getByText('Username already taken')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  it('links to login page', () => {
    render(<SignUp />);

    const loginLink = screen.getByText(/sign in to your existing account/i);
    expect(loginLink).toHaveAttribute('href', '/login');
  });
});