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
    return players.filter(player => {
      const matchesPosition = positionFilter === 'ALL' || player.position === positionFilter;
      const matchesSearch = player.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           player.team?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesPosition && matchesSearch;
    });
  }, [players, positionFilter, searchTerm]);

  const positions = ['ALL', 'QB', 'RB', 'WR', 'TE', 'K', 'DEF'];

  return (
    <div>
      {/* Filters */}
      <div className="p-4 bg-sleeper-dark sticky top-16 z-10 border-b border-gray-800">
        <div className="flex gap-4 mb-3">
          <input
            type="text"
            placeholder="Search players..."
            className="flex-1 px-4 py-2 bg-sleeper-gray rounded border border-gray-700 focus:border-sleeper-primary focus:outline-none"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          {positions.map(pos => (
            <button
              key={pos}
              onClick={() => setPositionFilter(pos)}
              className={`px-4 py-2 rounded font-semibold transition ${
                positionFilter === pos
                  ? 'bg-sleeper-primary text-white'
                  : 'bg-sleeper-gray hover:bg-gray-700'
              }`}
            >
              {pos}
            </button>
          ))}
        </div>
      </div>

      {/* Player List */}
      <div className="p-4">
        <div className="space-y-2">
          {filteredPlayers.map(player => (
            <div
              key={player.id}
              onClick={() => canSelect && onSelectPlayer(player)}
              className={`p-3 rounded cursor-pointer transition ${
                selectedPlayer?.id === player.id
                  ? 'bg-sleeper-primary/20 border border-sleeper-primary'
                  : canSelect
                  ? 'bg-sleeper-gray hover:bg-gray-700'
                  : 'bg-sleeper-gray opacity-75 cursor-not-allowed'
              }`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold">{player.full_name}</span>
                  <span className="text-sm text-gray-400 ml-2">
                    {player.position} - {player.team || 'FA'}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold">Rank #{Math.round(player.composite_rank)}</div>
                  {player.age && <div className="text-xs text-gray-400">Age {player.age}</div>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
