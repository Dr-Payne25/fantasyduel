import React from 'react';
import { DraftPick, LeagueUser, Player } from '../../services/api';

interface DraftBoardProps {
  picks: DraftPick[];
  users: LeagueUser[];
  availablePlayers: Player[];
  draftedPlayers: Player[];
}

export default function DraftBoard({ picks, users, availablePlayers, draftedPlayers }: DraftBoardProps) {
  const sortedPicks = [...picks].sort((a, b) => b.pick_number - a.pick_number);

  // Combine all players for lookup
  const allPlayers = [...availablePlayers, ...draftedPlayers];

  // Position color mapping
  const getPositionColor = (position: string) => {
    switch (position) {
      case 'QB':
        return 'bg-red-500/20 border-red-500/50 text-red-400';
      case 'RB':
        return 'bg-green-500/20 border-green-500/50 text-green-400';
      case 'WR':
        return 'bg-blue-500/20 border-blue-500/50 text-blue-400';
      case 'TE':
        return 'bg-orange-500/20 border-orange-500/50 text-orange-400';
      case 'K':
        return 'bg-purple-500/20 border-purple-500/50 text-purple-400';
      case 'DEF':
        return 'bg-gray-500/20 border-gray-500/50 text-gray-400';
      default:
        return 'bg-gray-500/20 border-gray-500/50 text-gray-400';
    }
  };

  // Get current user ID (same logic as in DraftRoom)
  const currentUserId = (() => {
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromUrl = urlParams.get('userId');
    return userIdFromUrl || localStorage.getItem('userId') || '';
  })();

  return (
    <div>
      {/* Header */}
      <div className="px-4 py-2 border-b border-gray-800 text-xs text-gray-500 font-semibold uppercase tracking-wider">
        Recent Picks
      </div>

      {/* Picks List */}
      <div className="p-2">
        {sortedPicks.map((pick, index) => {
          const user = users.find(u => u.user_id === pick.user_id);
          const player = allPlayers.find(p => p.id === pick.player_id);
          const isMyPick = pick.user_id === currentUserId;

          return (
            <div
              key={pick.id}
              className={`px-3 py-2 rounded-lg mb-1 transition-all ${
                index === 0 ? 'bg-sleeper-primary/10' : ''
              } hover:bg-gray-800/50`}
            >
              {/* Pick Header */}
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">
                    #{pick.pick_number}
                  </span>
                  <span className={`text-xs font-semibold ${
                    isMyPick ? 'text-sleeper-primary' : 'text-gray-400'
                  }`}>
                    {user?.display_name}
                  </span>
                </div>
                <span className="text-xs text-gray-600">
                  {new Date(pick.picked_at).toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit'
                  })}
                </span>
              </div>

              {/* Player Info */}
              {player && (
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${
                    player.position === 'QB' ? 'bg-red-900/50 text-red-400' :
                    player.position === 'RB' ? 'bg-green-900/50 text-green-400' :
                    player.position === 'WR' ? 'bg-blue-900/50 text-blue-400' :
                    player.position === 'TE' ? 'bg-orange-900/50 text-orange-400' :
                    player.position === 'K' ? 'bg-purple-900/50 text-purple-400' :
                    'bg-gray-700 text-gray-400'
                  }`}>
                    {player.position}
                  </span>
                  <span className="font-semibold text-sm">
                    {player.full_name}
                  </span>
                  <span className="text-xs text-gray-500">
                    {player.team || 'FA'}
                  </span>
                </div>
              )}
            </div>
          );
        })}

        {picks.length === 0 && (
          <div className="text-center text-gray-600 py-8">
            <div className="mb-2">
              <svg className="w-12 h-12 mx-auto text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div className="text-sm font-medium">No picks yet</div>
            <div className="text-xs text-gray-600 mt-1">Draft starting soon</div>
          </div>
        )}
      </div>
    </div>
  );
}
