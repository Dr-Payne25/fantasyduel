// Mock API responses
export const mockLeague = {
  id: 'test-league-id',
  name: 'Test League',
  status: 'draft_ready',
  commissioner_id: 'test-user-id',
  created_at: '2025-01-01T00:00:00Z',
  settings: {
    roster_spots: {
      QB: 1, RB: 2, WR: 2, TE: 1, FLEX: 1, K: 1, DEF: 1, BENCH: 6
    },
    scoring: 'PPR'
  }
};

export const mockLeagueUser = {
  id: 1,
  league_id: 'test-league-id',
  user_id: 'test-user-id',
  email: 'test@example.com',
  display_name: 'Test User',
  pair_id: 1
};

export const mockDraftPair = {
  id: 1,
  league_id: 'test-league-id',
  pool_number: 0,
  draft_order: 0
};

export const mockDraft = {
  id: 'test-draft-id',
  pair_id: 1,
  status: 'active',
  current_picker_id: 'test-user-id',
  pick_timer_seconds: 90,
  started_at: '2025-01-01T00:00:00Z',
  completed_at: null
};

export const mockPlayer = {
  id: 'player-1',
  sleeper_id: 'sleeper-1',
  first_name: 'Test',
  last_name: 'Player',
  full_name: 'Test Player',
  team: 'KC',
  position: 'QB',
  fantasy_positions: ['QB'],
  age: 25,
  composite_rank: 1.0,
  pool_assignment: 0
};

export const mockDraftPick = {
  id: 1,
  draft_id: 'test-draft-id',
  pick_number: 1,
  user_id: 'test-user-id',
  player_id: 'player-1',
  picked_at: '2025-01-01T00:01:00Z',
  player: mockPlayer
};

// Mock WebSocket
export class MockWebSocket {
  url: string;
  readyState: number = 0;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate connection
    setTimeout(() => {
      this.readyState = 1;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 0);
  }

  send(data: string) {
    // Mock implementation
  }

  close() {
    this.readyState = 3;
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }

  // Helper to simulate receiving a message
  receiveMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }));
    }
  }
}