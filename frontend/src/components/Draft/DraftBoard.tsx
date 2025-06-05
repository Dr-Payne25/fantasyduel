import React from 'react';
import { DraftPick, LeagueUser } from '../../services/api';

interface DraftBoardProps {
  picks: DraftPick[];
  users: LeagueUser[];
}

export default function DraftBoard({ picks, users }: DraftBoardProps) {
  const sortedPicks = [...picks].sort((a, b) => b.pick_number - a.pick_number);

  return (
    <div className="p-4">
      <div className="space-y-2">
        {sortedPicks.map(pick => {
          const user = users.find(u => u.user_id === pick.user_id);
          return (
            <div key={pick.id} className="bg-sleeper-gray rounded p-3">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs text-gray-400">Pick #{pick.pick_number}</span>
                <span className="text-xs text-gray-400">{user?.display_name}</span>
              </div>
              <div className="font-semibold">
                {pick.player?.full_name || 'Loading...'}
              </div>
              <div className="text-sm text-gray-400">
                {pick.player?.position} - {pick.player?.team || 'FA'}
              </div>
            </div>
          );
        })}

        {picks.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            No picks made yet
          </div>
        )}
      </div>
    </div>
  );
}
