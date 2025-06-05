import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api, League, LeagueUser, DraftPair } from '../../services/api';
import NavBar from '../Navigation/NavBar';

export default function LeagueDashboard() {
  const { leagueId } = useParams<{ leagueId: string }>();
  const navigate = useNavigate();
  const [league, setLeague] = useState<League | null>(null);
  const [users, setUsers] = useState<LeagueUser[]>([]);
  const [pairs, setPairs] = useState<DraftPair[]>([]);
  const [drafts, setDrafts] = useState<Record<number, { id: string; status: string; started_at: string | null }>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadLeague = useCallback(async () => {
    try {
      const data = await api.getLeague(leagueId!);
      setLeague(data.league);
      setUsers(data.users);
      setPairs(data.pairs);
      setDrafts(data.drafts || {});
    } catch (err) {
      setError('Failed to load league');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [leagueId]);

  useEffect(() => {
    if (leagueId) {
      loadLeague();
    }
  }, [leagueId, loadLeague]);

  const createPairs = async () => {
    try {
      await api.createDraftPairs(leagueId!);
      await loadLeague();
    } catch (err) {
      setError('Failed to create pairs');
      console.error(err);
    }
  };

  const startDraft = async (pairId: number) => {
    try {
      const result = await api.startDraft(pairId);
      console.log('Start draft result:', result);
      if (result.draft && result.draft.id) {
        navigate(`/draft/${result.draft.id}`);
      } else {
        setError('Invalid draft response - no draft ID');
        console.error('Invalid draft response:', result);
      }
    } catch (err: any) {
      if (err.message.includes('400')) {
        setError('Draft already exists for this pair. Refreshing...');
        setTimeout(() => loadLeague(), 1000);
      } else {
        setError('Failed to start draft');
      }
      console.error('Start draft error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-sleeper-darker">
        <NavBar />
        <div className="flex items-center justify-center h-96">
          <div className="text-xl">Loading league...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-sleeper-darker">
        <NavBar />
        <div className="flex items-center justify-center h-96">
          <div className="text-red-500">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sleeper-darker">
      <NavBar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-sleeper-primary mb-2">{league?.name}</h1>
          <p className="text-gray-400">League ID: {leagueId}</p>
        </div>

        {/* Users Section */}
        <div className="bg-sleeper-dark rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">League Members ({users.length}/12)</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {users.map((user) => (
              <div key={user.id} className="bg-sleeper-gray rounded p-4">
                <p className="font-semibold">{user.display_name}</p>
                <p className="text-sm text-gray-400">{user.email}</p>
                {user.pair_id && <p className="text-sm text-sleeper-primary">Pair {pairs.find(p => p.id === user.pair_id)?.pool_number! + 1}</p>}
              </div>
            ))}
          </div>
          
          {users.length < 12 && (
            <div className="mt-4 p-4 bg-blue-900/20 border border-blue-700 rounded">
              <p className="text-sm">Waiting for {12 - users.length} more players to join</p>
              <p className="text-xs text-gray-400 mt-1">Share this code: {leagueId}</p>
            </div>
          )}
        </div>

        {/* Draft Pairs Section */}
        {users.length === 12 && (
          <div className="bg-sleeper-dark rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold">Draft Pairs</h2>
              {pairs.length === 0 && (
                <button
                  onClick={createPairs}
                  className="px-4 py-2 bg-sleeper-primary hover:bg-blue-600 rounded font-semibold transition"
                >
                  Create Draft Pairs
                </button>
              )}
            </div>
            
            {pairs.length > 0 && (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pairs.map((pair) => {
                  const pairUsers = users.filter(u => u.pair_id === pair.id);
                  return (
                    <div key={pair.id} className="bg-sleeper-gray rounded p-4">
                      <h3 className="font-semibold mb-2">Pool {pair.pool_number + 1}</h3>
                      <div className="space-y-1 mb-3">
                        {pairUsers.map(u => (
                          <p key={u.id} className="text-sm">{u.display_name}</p>
                        ))}
                      </div>
                      {drafts[pair.id] ? (
                        <button
                          onClick={() => navigate(`/draft/${drafts[pair.id].id}`)}
                          className="w-full py-2 bg-sleeper-primary hover:bg-blue-600 rounded text-sm font-semibold transition"
                        >
                          {drafts[pair.id].status === 'completed' ? 'View Draft' : 'Continue Draft'}
                        </button>
                      ) : (
                        <button
                          onClick={() => startDraft(pair.id)}
                          className="w-full py-2 bg-sleeper-secondary hover:bg-pink-600 rounded text-sm font-semibold transition"
                        >
                          Start Draft
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}