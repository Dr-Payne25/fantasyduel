import React, { useState, useMemo } from 'react';
import { Player } from '../../services/api';

interface PlayerListProps {
  players: Player[];
  onSelectPlayer: (player: Player) => void;
  selectedPlayer: Player | null;
  canSelect: boolean;
}

export default function PlayerList({ players, onSelectPlayer, selectedPlayer, canSelect }: PlayerListProps) {
  const [positionFilter, setPositionFilter] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPlayers = useMemo(() => {
    return players
      .filter(player => {
        const matchesPosition = positionFilter === 'ALL' || player.position === positionFilter;
        const matchesSearch = player.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             player.team?.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesPosition && matchesSearch;
      })
      .sort((a, b) => (a.composite_rank || 999) - (b.composite_rank || 999));
  }, [players, positionFilter, searchTerm]);

  const positions = ['ALL', 'QB', 'RB', 'WR', 'TE', 'K', 'DEF'];

  return (
    <div className="h-full flex flex-col">
      {/* Filters - Sleeper Style */}
      <div className="bg-sleeper-dark border-b border-gray-800">
        <div className="p-3">
          <div className="flex gap-3 mb-3">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search players..."
                className="w-full px-3 py-2 pl-9 bg-gray-800 rounded-lg text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-sleeper-primary/50"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <svg className="w-4 h-4 absolute left-3 top-2.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <div className="flex gap-1.5 overflow-x-auto">
            {positions.map(pos => (
              <button
                key={pos}
                onClick={() => setPositionFilter(pos)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                  positionFilter === pos
                    ? 'bg-sleeper-primary text-white'
                    : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {pos}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Player List - Sleeper Style */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-3 py-2 text-xs text-gray-500 font-semibold uppercase tracking-wider">
          Available Players ({filteredPlayers.length})
        </div>

        <div className="px-2">
          {filteredPlayers.map((player, index) => (
            <div
              key={player.id}
              onClick={() => canSelect && onSelectPlayer(player)}
              className={`mb-1 rounded-lg transition-all ${
                selectedPlayer?.id === player.id
                  ? 'bg-sleeper-primary/20 ring-2 ring-sleeper-primary'
                  : canSelect
                  ? 'hover:bg-gray-800/50 cursor-pointer'
                  : 'opacity-50 cursor-not-allowed'
              }`}
            >
              <div className="p-3">
                <div className="flex items-center gap-3">
                  {/* Rank */}
                  <div className="flex-shrink-0 text-center">
                    <div className="text-sm font-bold text-white">
                      {index + 1}
                    </div>
                    <div className="text-xs text-gray-600">
                      ADP
                    </div>
                  </div>

                  {/* Player Avatar Placeholder */}
                  <div className="flex-shrink-0 w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center">
                    <span className={`text-xs font-bold ${
                      player.position === 'QB' ? 'text-red-400' :
                      player.position === 'RB' ? 'text-green-400' :
                      player.position === 'WR' ? 'text-blue-400' :
                      player.position === 'TE' ? 'text-orange-400' :
                      player.position === 'K' ? 'text-purple-400' :
                      'text-gray-400'
                    }`}>
                      {player.position}
                    </span>
                  </div>

                  {/* Player Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-white truncate">
                        {player.full_name}
                      </span>
                      {selectedPlayer?.id === player.id && (
                        <svg className="w-4 h-4 text-sleeper-primary flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className={`font-bold ${
                        player.position === 'QB' ? 'text-red-400' :
                        player.position === 'RB' ? 'text-green-400' :
                        player.position === 'WR' ? 'text-blue-400' :
                        player.position === 'TE' ? 'text-orange-400' :
                        player.position === 'K' ? 'text-purple-400' :
                        'text-gray-400'
                      }`}>
                        {player.position}
                      </span>
                      <span>{player.team || 'FA'}</span>
                      {player.age && <span>Age {player.age}</span>}
                    </div>
                  </div>

                  {/* Stats/Rank */}
                  <div className="flex-shrink-0 text-right">
                    <div className="text-sm font-bold text-sleeper-primary">
                      #{Math.round(player.composite_rank)}
                    </div>
                    <div className="text-xs text-gray-600">
                      Rank
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredPlayers.length === 0 && (
          <div className="text-center py-8">
            <div className="text-gray-600 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="text-sm text-gray-500">No players found</div>
            <div className="text-xs text-gray-600 mt-1">Try adjusting your filters</div>
          </div>
        )}
      </div>
    </div>
  );
}
