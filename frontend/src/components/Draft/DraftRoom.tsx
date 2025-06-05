import React, { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { api, Draft, DraftPick, Player, LeagueUser } from '../../services/api';
import { wsService } from '../../services/websocket';
import PlayerList from './PlayerList';
import DraftBoard from './DraftBoard';
import NavBar from '../Navigation/NavBar';

export default function DraftRoom() {
  const { draftId } = useParams<{ draftId: string }>();
  const [draft, setDraft] = useState<Draft | null>(null);
  const [users, setUsers] = useState<LeagueUser[]>([]);
  const [picks, setPicks] = useState<DraftPick[]>([]);
  const [availablePlayers, setAvailablePlayers] = useState<Player[]>([]);
  const [currentUserId] = useState(() => {
    // Get user ID from localStorage or URL params for testing
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromUrl = urlParams.get('userId');
    return userIdFromUrl || localStorage.getItem('userId') || '';
  });
  const [loading, setLoading] = useState(true);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  const handleWebSocketMessage = useCallback((message: any) => {
    if (message.type === 'pick_made') {
      setPicks(prev => [...prev, message.pick]);
      setAvailablePlayers(prev => prev.filter(p => p.id !== message.pick.player_id));
      setDraft(prev => prev ? { ...prev, current_picker_id: message.next_picker } : null);
    }
  }, []);

  const loadDraft = useCallback(async () => {
    try {
      const data = await api.getDraft(draftId!);
      setDraft(data.draft);
      setUsers(data.users);
      setPicks(data.picks);
      setAvailablePlayers(data.available_players);
    } catch (err) {
      console.error('Failed to load draft:', err);
    } finally {
      setLoading(false);
    }
  }, [draftId]);

  useEffect(() => {
    if (draftId) {
      loadDraft();
      wsService.connect(draftId);

      const unsubscribe = wsService.addMessageHandler(handleWebSocketMessage);
      return () => {
        unsubscribe();
        wsService.disconnect();
      };
    }
  }, [draftId, handleWebSocketMessage, loadDraft]);

  const makePick = async () => {
    if (!selectedPlayer || !currentUserId || draft?.current_picker_id !== currentUserId) return;

    try {
      await api.makePick(draftId!, currentUserId, selectedPlayer.id);
      setSelectedPlayer(null);
    } catch (err) {
      console.error('Failed to make pick:', err);
    }
  };

  const isMyTurn = draft?.current_picker_id === currentUserId;
  const currentUser = users.find(u => u.user_id === draft?.current_picker_id);

  if (loading) {
    return (
      <div className="min-h-screen bg-sleeper-darker">
        <NavBar />
        <div className="flex items-center justify-center h-96">
          <div className="text-xl">Loading draft...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sleeper-darker">
      <NavBar />
      <div className="flex" style={{ height: 'calc(100vh - 73px)' }}>
        {/* Left Panel - Draft Board */}
        <div className="w-96 bg-sleeper-dark border-r border-gray-800 overflow-y-auto">
          <div className="p-4 border-b border-gray-800">
            <h2 className="text-xl font-bold mb-2">Draft Board</h2>
            <div className="text-sm text-gray-400">
              Pick #{picks.length + 1} - {currentUser?.display_name}'s turn
              {isMyTurn && <span className="text-sleeper-primary ml-2">(Your pick!)</span>}
            </div>
          </div>
          <DraftBoard picks={picks} users={users} />
        </div>

        {/* Center - Available Players */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4 border-b border-gray-800 bg-sleeper-dark sticky top-0 z-10">
            <h2 className="text-xl font-bold mb-2">Available Players</h2>
            {selectedPlayer && isMyTurn && (
              <div className="flex items-center gap-4 mt-2">
                <div className="flex-1 bg-sleeper-gray rounded p-3">
                  <span className="font-semibold">{selectedPlayer.full_name}</span>
                  <span className="text-sm text-gray-400 ml-2">
                    {selectedPlayer.position} - {selectedPlayer.team}
                  </span>
                </div>
                <button
                  onClick={makePick}
                  className="px-6 py-2 bg-sleeper-primary hover:bg-blue-600 rounded font-semibold transition"
                >
                  Draft Player
                </button>
              </div>
            )}
          </div>
          <PlayerList
            players={availablePlayers}
            onSelectPlayer={setSelectedPlayer}
            selectedPlayer={selectedPlayer}
            canSelect={isMyTurn}
          />
        </div>

        {/* Right Panel - My Roster */}
        <div className="w-80 bg-sleeper-dark border-l border-gray-800 overflow-y-auto">
          <div className="p-4 border-b border-gray-800">
            <h2 className="text-xl font-bold">My Roster</h2>
          </div>
          <div className="p-4">
            {['QB', 'RB', 'WR', 'TE', 'K', 'DEF'].map(position => {
              const myPicks = picks.filter(
                p => p.user_id === currentUserId &&
                availablePlayers.find(pl => pl.id === p.player_id)?.position === position
              );
              return (
                <div key={position} className="mb-4">
                  <h3 className="font-semibold text-sm text-gray-400 mb-2">{position}</h3>
                  <div className="space-y-1">
                    {myPicks.length === 0 ? (
                      <p className="text-sm text-gray-600">Empty</p>
                    ) : (
                      myPicks.map(pick => {
                        const player = availablePlayers.find(p => p.id === pick.player_id);
                        return player ? (
                          <div key={pick.id} className="text-sm bg-sleeper-gray rounded p-2">
                            {player.full_name} - {player.team}
                          </div>
                        ) : null;
                      })
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
