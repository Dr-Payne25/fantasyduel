import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import LeagueDashboard from './components/League/LeagueDashboard';
import DraftRoom from './components/Draft/DraftRoom';
import Login from './components/Auth/Login';
import SignUp from './components/Auth/SignUp';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import MyLeagues from './components/League/MyLeagues';
import NavBar from './components/Navigation/NavBar';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { api } from './services/api';

function HomePage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [leagueName, setLeagueName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [error, setError] = useState<string | null>(null);

  const createLeague = async () => {
    if (!user) return;
    
    try {
      const result = await api.createLeague(leagueName, user.username, user.email);
      setInviteCode(result.invite_code);
    } catch (error) {
      console.error('Error creating league:', error);
    }
  };

  const joinLeague = async () => {
    if (!user) return;
    
    try {
      setError(null);
      await api.joinLeague(joinCode, user.username, user.email);
      navigate(`/league/${joinCode}`);
    } catch (error: any) {
      console.error('Error joining league:', error);
      setError(error.message || 'Failed to join league');
    }
  };

  return (
    <div className="min-h-screen bg-sleeper-darker">
      <NavBar />
      
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h1 className="text-5xl font-bold text-sleeper-primary mb-2">FantasyDuel</h1>
        <p className="text-xl text-gray-400 mb-12">Unique 1v1 draft mechanics for fantasy football</p>
        
        {user ? (
          <>
            {/* My Leagues Section */}
            <div className="mb-12">
              <MyLeagues />
            </div>
            
            {/* Create/Join Section */}
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-sleeper-dark rounded-lg p-8">
              <h2 className="text-2xl font-semibold mb-6">Create New League</h2>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="League Name"
                  className="w-full px-4 py-3 bg-sleeper-gray rounded border border-gray-700 focus:border-sleeper-primary focus:outline-none"
                  value={leagueName}
                  onChange={(e) => setLeagueName(e.target.value)}
                />
                <div className="text-sm text-gray-400">
                  Commissioner: {user.username} ({user.email})
                </div>
                <button
                  onClick={createLeague}
                  className="w-full py-3 bg-sleeper-primary hover:bg-blue-600 rounded font-semibold transition"
                  disabled={!leagueName}
                >
                  Create League
                </button>
              {inviteCode && (
                <div className="mt-4 p-4 bg-green-900/20 border border-green-700 rounded">
                  <p className="text-sm text-gray-400">League created! Share this code:</p>
                  <p className="text-lg font-mono text-green-400">{inviteCode}</p>
                  <Link
                    to={`/league/${inviteCode}`}
                    className="mt-2 inline-block text-sm text-sleeper-primary hover:underline"
                  >
                    Go to League →
                  </Link>
                </div>
              )}
            </div>
          </div>
          
            <div className="bg-sleeper-dark rounded-lg p-8">
              <h2 className="text-2xl font-semibold mb-6">Join Existing League</h2>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="League Invite Code"
                  className="w-full px-4 py-3 bg-sleeper-gray rounded border border-gray-700 focus:border-sleeper-primary focus:outline-none"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value)}
                />
                <div className="text-sm text-gray-400">
                  Joining as: {user.username} ({user.email})
                </div>
                <button 
                  onClick={joinLeague}
                  className="w-full py-3 bg-sleeper-secondary hover:bg-pink-600 rounded font-semibold transition"
                  disabled={!joinCode}
                >
                  Join League
                </button>
                {error && (
                  <div className="mt-4 p-4 bg-red-900/20 border border-red-700 rounded">
                    <p className="text-sm text-red-400">{error}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
          </>
        ) : (
          <div className="bg-sleeper-dark rounded-lg p-8 text-center">
            <h2 className="text-2xl font-semibold mb-4">Welcome to FantasyDuel</h2>
            <p className="text-gray-400 mb-6">Sign in or create an account to start playing</p>
            <div className="flex gap-4 justify-center">
              <Link
                to="/login"
                className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded font-semibold transition"
              >
                Login
              </Link>
              <Link
                to="/signup"
                className="px-6 py-3 bg-sleeper-primary hover:bg-blue-600 rounded font-semibold transition"
              >
                Create Account
              </Link>
            </div>
          </div>
        )}
        
        <div className="mt-12 text-center">
          <h3 className="text-xl font-semibold mb-4">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-6 text-sm text-gray-400">
            <div className="bg-sleeper-dark rounded-lg p-6">
              <div className="text-3xl mb-3">🏈</div>
              <h4 className="font-semibold text-white mb-2">1. Create League</h4>
              <p>Start a 12-person league and invite your friends</p>
            </div>
            <div className="bg-sleeper-dark rounded-lg p-6">
              <div className="text-3xl mb-3">👥</div>
              <h4 className="font-semibold text-white mb-2">2. Pair Up</h4>
              <p>Players are randomly paired for 6 simultaneous 1v1 drafts</p>
            </div>
            <div className="bg-sleeper-dark rounded-lg p-6">
              <div className="text-3xl mb-3">🎯</div>
              <h4 className="font-semibold text-white mb-2">3. Draft & Play</h4>
              <p>Each pair drafts from an equal-value player pool, then compete in the season</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route 
            path="/league/:leagueId" 
            element={
              <ProtectedRoute>
                <LeagueDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/draft/:draftId" 
            element={
              <ProtectedRoute>
                <DraftRoom />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;