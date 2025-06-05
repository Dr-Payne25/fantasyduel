import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

interface UserLeague {
  league: {
    id: string;
    name: string;
    status: string;
  };
  user_count: number;
  my_pair_id: number | null;
  active_draft: { id: string; status: string } | null;
  is_commissioner: boolean;
}

export default function MyLeagues() {
  const navigate = useNavigate();
  const [leagues, setLeagues] = useState<UserLeague[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMyLeagues();
  }, []);

  const fetchMyLeagues = async () => {
    try {
      setLoading(true);
      const myLeagues = await api.getMyLeagues();
      setLeagues(myLeagues);
    } catch (err) {
      console.error('Error fetching leagues:', err);
      setError('Failed to load your leagues');
    } finally {
      setLoading(false);
    }
  };

  const handleLeagueClick = (leagueId: string, activeDraft: UserLeague['active_draft']) => {
    if (activeDraft) {
      // If there's an active draft, go directly to it
      navigate(`/draft/${activeDraft.id}`);
    } else {
      // Otherwise go to league page
      navigate(`/league/${leagueId}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sleeper-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 text-center py-4">
        {error}
      </div>
    );
  }

  if (leagues.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-400 mb-4">You're not in any leagues yet.</p>
        <p className="text-sm text-gray-500">Create a new league or join an existing one below.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-white mb-4">My Leagues</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {leagues.map(({ league, user_count, active_draft, is_commissioner }) => (
          <div
            key={league.id}
            onClick={() => handleLeagueClick(league.id, active_draft)}
            className="bg-sleeper-dark p-4 rounded-lg border border-gray-800 hover:border-sleeper-primary cursor-pointer transition-all"
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-medium text-white">{league.name}</h3>
              {is_commissioner && (
                <span className="text-xs bg-sleeper-primary px-2 py-1 rounded">Commissioner</span>
              )}
            </div>

            <div className="text-sm text-gray-400 space-y-1">
              <p>{user_count}/12 members</p>
              <p className="capitalize">Status: {league.status.replace('_', ' ')}</p>

              {active_draft && (
                <div className="mt-2 pt-2 border-t border-gray-700">
                  <p className="text-sleeper-primary font-medium">
                    Active Draft - Click to Enter
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
