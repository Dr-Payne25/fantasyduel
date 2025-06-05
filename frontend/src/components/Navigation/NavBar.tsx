import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ChevronDownIcon, HomeIcon, UserCircleIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const canGoBack = location.pathname !== '/';

  return (
    <nav className="bg-sleeper-dark border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            {canGoBack && (
              <button
                onClick={() => navigate(-1)}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition"
                title="Go back"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
            )}

            <Link to="/" className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-sleeper-primary">FantasyDuel</h1>
            </Link>
          </div>

          {user ? (
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded transition"
              >
                <UserCircleIcon className="h-5 w-5" />
                <span>{user.username}</span>
                <ChevronDownIcon className={`h-4 w-4 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-sleeper-dark border border-gray-700 rounded-lg shadow-lg z-50">
                  <div className="px-4 py-3 border-b border-gray-700">
                    <p className="text-sm font-medium text-white">{user.username}</p>
                    <p className="text-xs text-gray-400">{user.email}</p>
                  </div>

                  <div className="py-2">
                    <Link
                      to="/"
                      className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <HomeIcon className="inline h-4 w-4 mr-2" />
                      Home
                    </Link>

                    <button
                      onClick={() => {
                        setDropdownOpen(false);
                        // TODO: Navigate to profile when implemented
                        alert('Profile page coming soon!');
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition"
                    >
                      <UserCircleIcon className="inline h-4 w-4 mr-2" />
                      Profile
                    </button>
                  </div>

                  <div className="border-t border-gray-700 py-2">
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex gap-4">
              <Link
                to="/login"
                className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded transition"
              >
                Login
              </Link>
              <Link
                to="/signup"
                className="px-4 py-2 text-sm bg-sleeper-primary hover:bg-blue-600 rounded transition"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
