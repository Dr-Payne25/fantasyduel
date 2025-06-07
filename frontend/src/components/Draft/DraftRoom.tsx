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
  const [draftedPlayers, setDraftedPlayers] = useState<Player[]>([]);
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
      setAvailablePlayers(prev => {
        const pickedPlayer = prev.find(p => p.id === message.pick.player_id);
        if (pickedPlayer) {
          setDraftedPlayers(drafted => [...drafted, pickedPlayer]);
        }
        return prev.filter(p => p.id !== message.pick.player_id);
      });
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
      setDraftedPlayers(data.drafted_players || []);
    } catch (err) {
      console.error('Failed to load draft:', err);
    } finally {
      setLoading(false);
    }
  }, [draftId]);

  // Separate effect for initial load
  useEffect(() => {
    if (draftId) {
      console.log('[DraftRoom] Loading draft data for draftId:', draftId);
      loadDraft();
    }
  }, [draftId, loadDraft]);

  // Separate effect for WebSocket connection
  useEffect(() => {
    if (draftId) {
      console.log('[DraftRoom] Connecting WebSocket for draftId:', draftId);
      wsService.connect(draftId);

      const unsubscribe = wsService.addMessageHandler(handleWebSocketMessage);
      return () => {
        console.log('[DraftRoom] Cleaning up - unsubscribing and disconnecting WebSocket');
        unsubscribe();
        wsService.disconnect();
      };
    }
  }, [draftId, handleWebSocketMessage]);

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

  // Get the current user's display name
  const myUser = users.find(u => u.user_id === currentUserId);
  const otherUser = users.find(u => u.user_id !== currentUserId);
  const myPickCount = picks.filter(p => p.user_id === currentUserId).length;
  const otherPickCount = picks.filter(p => p.user_id === otherUser?.user_id).length;

  return (
    <div className="min-h-screen bg-sleeper-darker">
      <NavBar />

      {/* Draft Info Header - Sleeper Style */}
      <div className="bg-sleeper-dark border-b border-gray-800">
        <div className="px-4 py-2">
          <div className="flex items-center justify-between">
            {/* Left: Draft Info */}
            <div className="flex items-center gap-4">
              <div>
                <h1 className="text-lg font-bold">Draft Room</h1>
                <p className="text-xs text-gray-500">Pool {draft?.pair_id || ''}</p>
              </div>

              {/* Turn Indicator */}
              <div className="flex items-center gap-3">
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
                  draft?.current_picker_id === myUser?.user_id
                    ? 'bg-sleeper-primary text-white'
                    : 'bg-gray-800 text-gray-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    draft?.current_picker_id === myUser?.user_id
                      ? 'bg-white animate-pulse'
                      : 'bg-gray-600'
                  }`} />
                  <span className="text-sm font-medium">{myUser?.display_name || 'You'}</span>
                </div>

                <span className="text-gray-600 text-sm">vs</span>

                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
                  draft?.current_picker_id === otherUser?.user_id
                    ? 'bg-sleeper-primary text-white'
                    : 'bg-gray-800 text-gray-400'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    draft?.current_picker_id === otherUser?.user_id
                      ? 'bg-white animate-pulse'
                      : 'bg-gray-600'
                  }`} />
                  <span className="text-sm font-medium">{otherUser?.display_name || 'Opponent'}</span>
                </div>
              </div>
            </div>

            {/* Right: Pick Info & Timer */}
            <div className="flex items-center gap-6">
              {/* Pick Counter */}
              <div className="text-center">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Pick</p>
                <p className="text-2xl font-bold">{picks.length + 1}</p>
              </div>

              {/* Timer (placeholder for now) */}
              <div className="text-center">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Time</p>
                <p className="text-2xl font-bold tabular-nums">1:30</p>
              </div>

              {/* Draft Button - Always visible but disabled when not your turn */}
              <button
                onClick={makePick}
                disabled={!isMyTurn || !selectedPlayer}
                className={`px-6 py-2.5 rounded-full font-bold transition-all ${
                  isMyTurn && selectedPlayer
                    ? 'bg-sleeper-primary hover:bg-blue-600 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                    : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                }`}
              >
                DRAFT
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex" style={{ height: 'calc(100vh - 73px - 56px)' }}>
        {/* Left Panel - Draft Board & Rosters */}
        <div className="w-80 bg-sleeper-dark border-r border-gray-800 flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-gray-800">
            <button className="flex-1 px-4 py-3 text-sm font-semibold border-b-2 border-sleeper-primary">
              Draft Board
            </button>
            <button className="flex-1 px-4 py-3 text-sm font-semibold text-gray-500 hover:text-white">
              Rosters
            </button>
          </div>

          {/* Draft Board Content */}
          <div className="flex-1 overflow-y-auto">
            <DraftBoard
              picks={picks}
              users={users}
              availablePlayers={availablePlayers}
              draftedPlayers={draftedPlayers}
            />
          </div>
        </div>

        {/* Center - Available Players */}
        <div className="flex-1 bg-sleeper-darker flex flex-col overflow-hidden">
          {/* Selected Player Banner */}
          {selectedPlayer && (
            <div className={`bg-sleeper-dark border-b ${
              isMyTurn ? 'border-sleeper-primary/50' : 'border-gray-800'
            }`}>
              <div className="px-6 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Player Avatar Placeholder */}
                    <div className="w-16 h-16 bg-gray-800 rounded-lg flex items-center justify-center">
                      <span className="text-2xl font-bold text-gray-600">
                        {selectedPlayer.position}
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="text-xl font-bold">{selectedPlayer.full_name}</h3>
                        <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                          selectedPlayer.position === 'QB' ? 'bg-red-900 text-red-300' :
                          selectedPlayer.position === 'RB' ? 'bg-green-900 text-green-300' :
                          selectedPlayer.position === 'WR' ? 'bg-blue-900 text-blue-300' :
                          selectedPlayer.position === 'TE' ? 'bg-orange-900 text-orange-300' :
                          selectedPlayer.position === 'K' ? 'bg-purple-900 text-purple-300' :
                          'bg-gray-700 text-gray-300'
                        }`}>
                          {selectedPlayer.position}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span>{selectedPlayer.team || 'FA'}</span>
                        <span>Age {selectedPlayer.age}</span>
                        <span className="text-sleeper-primary font-semibold">
                          Rank #{Math.round(selectedPlayer.composite_rank)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {!isMyTurn && (
                    <div className="text-sm text-gray-500">
                      Not your turn
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Player List */}
          <div className="flex-1 overflow-hidden">
            <PlayerList
              players={availablePlayers}
              onSelectPlayer={setSelectedPlayer}
              selectedPlayer={selectedPlayer}
              canSelect={isMyTurn}
            />
          </div>
        </div>

        {/* Right Panel - Rosters (Sleeper Style) */}
        <div className="w-96 bg-sleeper-dark border-l border-gray-800 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <h2 className="font-bold">Team Rosters</h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-6">
              {users.map(user => {
                const isCurrentUser = user.user_id === currentUserId;
                const userPicks = picks.filter(p => p.user_id === user.user_id);
                const allPlayers = [...availablePlayers, ...draftedPlayers];

                return (
                  <div key={user.user_id} className="space-y-3">
                    {/* User Header */}
                    <div className={`flex items-center justify-between px-3 py-2 rounded-lg ${
                      isCurrentUser ? 'bg-sleeper-primary/20' : 'bg-gray-800'
                    }`}>
                      <span className="font-bold">
                        {user.display_name}
                        {isCurrentUser && <span className="text-sm text-gray-400 ml-2">(You)</span>}
                      </span>
                      <span className="text-sm text-gray-400">
                        {userPicks.length} / 8 picks
                      </span>
                    </div>

                    {/* Roster Grid */}
                    <div className="grid grid-cols-2 gap-2">
                      {['QB', 'RB', 'WR', 'TE', 'K', 'DEF'].map(position => {
                        const positionPicks = userPicks.filter(pick => {
                          const player = allPlayers.find(pl => pl.id === pick.player_id);
                          return player?.position === position;
                        });

                        const requirements = { QB: 1, RB: 2, WR: 2, TE: 1, K: 1, DEF: 1 };
                        const slots = requirements[position as keyof typeof requirements] || 0;

                        return Array.from({ length: slots }, (_, i) => {
                          const pick = positionPicks[i];
                          const player = pick ? allPlayers.find(p => p.id === pick.player_id) : null;

                          return (
                            <div
                              key={`${position}-${i}`}
                              className={`bg-gray-800 rounded-lg p-2.5 ${
                                player ? 'border border-gray-700' : 'border border-dashed border-gray-700'
                              }`}
                            >
                              <div className="text-xs font-bold text-gray-400 mb-1">{position}</div>
                              {player ? (
                                <div>
                                  <div className="text-sm font-semibold truncate">
                                    {player.full_name}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    {player.team || 'FA'}
                                  </div>
                                </div>
                              ) : (
                                <div className="text-xs text-gray-600 italic">Empty</div>
                              )}
                            </div>
                          );
                        });
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
