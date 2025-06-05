import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import LeagueDashboard from './components/League/LeagueDashboard';
import DraftRoom from './components/Draft/DraftRoom';
import { api } from './services/api';

function HomePage() {
  const navigate = useNavigate();
  const [leagueName, setLeagueName] = useState('');
  const [commissionerName, setCommissionerName] = useState('');
  const [email, setEmail] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [joinName, setJoinName] = useState('');
  const [joinEmail, setJoinEmail] = useState('');

  // Set a simple user ID in localStorage for demo purposes
  useEffect(() => {
    if (!localStorage.getItem('userId')) {
      localStorage.setItem('userId', `user-${Date.now()}`);
    }
  }, []);

  const createLeague = async () => {
    try {
      const result = await api.createLeague(leagueName, commissionerName, email);
      setInviteCode(result.invite_code);
      // Store user info for demo
      localStorage.setItem('userId', result.league.commissioner_id);
      localStorage.setItem('userName', commissionerName);
    } catch (error) {
      console.error('Error creating league:', error);
    }
  };

  const joinLeague = async () => {
    try {
      const result = await api.joinLeague(joinCode, joinName, joinEmail);
      // Store user info for demo
      localStorage.setItem('userId', result.user.user_id);
      localStorage.setItem('userName', joinName);
      navigate(`/league/${joinCode}`);
    } catch (error) {
      console.error('Error joining league:', error);
    }
  };

  return (
    <div className="min-h-screen bg-sleeper-darker">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h1 className="text-5xl font-bold text-sleeper-primary mb-2">FantasyDuel</h1>
        <p className="text-xl text-gray-400 mb-12">Unique 1v1 draft mechanics for fantasy football</p>
        
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
              <input
                type="text"
                placeholder="Your Name"
                className="w-full px-4 py-3 bg-sleeper-gray rounded border border-gray-700 focus:border-sleeper-primary focus:outline-none"
                value={commissionerName}
                onChange={(e) => setCommissionerName(e.target.value)}
              />
              <input
                type="email"
                placeholder="Email"
                className="w-full px-4 py-3 bg-sleeper-gray rounded border border-gray-700 focus:border-sleeper-primary focus:outline-none"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <button
                onClick={createLeague}
                className="w-full py-3 bg-sleeper-primary hover:bg-blue-600 rounded font-semibold transition"
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
              <input
                type="text"
                placeholder="Your Name"
                className="w-full px-4 py-3 bg-sleeper-gray rounded border border-gray-700 focus:border-sleeper-primary focus:outline-none"
                value={joinName}
                onChange={(e) => setJoinName(e.target.value)}
              />
              <input
                type="email"
                placeholder="Email"
                className="w-full px-4 py-3 bg-sleeper-gray rounded border border-gray-700 focus:border-sleeper-primary focus:outline-none"
                value={joinEmail}
                onChange={(e) => setJoinEmail(e.target.value)}
              />
              <button 
                onClick={joinLeague}
                className="w-full py-3 bg-sleeper-secondary hover:bg-pink-600 rounded font-semibold transition"
              >
                Join League
              </button>
            </div>
          </div>
        </div>
        
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
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/league/:leagueId" element={<LeagueDashboard />} />
        <Route path="/draft/:draftId" element={<DraftRoom />} />
      </Routes>
    </Router>
  );
}

export default App;