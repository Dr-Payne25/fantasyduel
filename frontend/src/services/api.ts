const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Player {
  id: string;
  sleeper_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  team: string;
  position: string;
  fantasy_positions: string[];
  age: number;
  composite_rank: number;
  pool_assignment: number;
}

export interface League {
  id: string;
  name: string;
  status: string;
  commissioner_id: string;
  created_at: string;
  settings: {
    roster_spots: Record<string, number>;
    scoring: string;
  };
}

export interface LeagueUser {
  id: number;
  league_id: string;
  user_id: string;
  email: string;
  display_name: string;
  pair_id: number;
}

export interface DraftPair {
  id: number;
  league_id: string;
  pool_number: number;
  draft_order: number;
}

export interface Draft {
  id: string;
  pair_id: number;
  status: string;
  current_picker_id: string;
  pick_timer_seconds: number;
  started_at: string;
  completed_at: string | null;
}

export interface DraftPick {
  id: number;
  draft_id: string;
  pick_number: number;
  user_id: string;
  player_id: string;
  picked_at: string;
  player?: Player;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  theme: string;
  notification_preferences: string;
}

class API {
  private authToken: string | null = null;

  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    // Merge with any headers from options
    if (options?.headers) {
      Object.assign(headers, options.headers);
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Player endpoints
  async getPlayers(position?: string, pool?: number): Promise<Player[]> {
    const params = new URLSearchParams();
    if (position) params.append('position', position);
    if (pool !== undefined) params.append('pool', pool.toString());

    return this.request<Player[]>(`/api/players?${params}`);
  }

  async getPoolPlayers(poolNumber: number): Promise<{ pool: number; total_players: number; players: Player[] }> {
    return this.request(`/api/players/pools/${poolNumber}`);
  }

  // League endpoints
  async createLeague(name: string, commissionerName: string, email: string) {
    return this.request<{
      league: League;
      invite_code: string;
    }>('/api/leagues/create', {
      method: 'POST',
      body: JSON.stringify({
        name,
        commissioner_name: commissionerName,
        commissioner_email: email,
      }),
    });
  }

  async joinLeague(leagueId: string, userName: string, email: string) {
    return this.request<{
      message: string;
      user: LeagueUser;
    }>('/api/leagues/join', {
      method: 'POST',
      body: JSON.stringify({
        league_id: leagueId,
        user_name: userName,
        email,
      }),
    });
  }

  async getLeagues() {
    return this.request<League[]>('/api/leagues');
  }

  async getMyLeagues() {
    return this.request<Array<{
      league: League;
      user_count: number;
      my_pair_id: number | null;
      active_draft: { id: string; status: string } | null;
      is_commissioner: boolean;
    }>>('/api/leagues/my-leagues');
  }

  async getLeague(leagueId: string) {
    return this.request<{
      league: League;
      users: LeagueUser[];
      pairs: DraftPair[];
      drafts: Record<number, { id: string; status: string; started_at: string | null }>;
      user_count: number;
    }>(`/api/leagues/${leagueId}`);
  }

  async createDraftPairs(leagueId: string) {
    return this.request(`/api/leagues/${leagueId}/create-pairs`, {
      method: 'POST',
    });
  }

  // Draft endpoints
  async startDraft(pairId: number) {
    return this.request<{
      draft: Draft;
      users: Array<{ id: string; name: string }>;
      pool_number: number;
    }>('/api/drafts/start', {
      method: 'POST',
      body: JSON.stringify({ pair_id: pairId }),
    });
  }

  async makePick(draftId: string, userId: string, playerId: string) {
    return this.request('/api/drafts/pick', {
      method: 'POST',
      body: JSON.stringify({
        draft_id: draftId,
        user_id: userId,
        player_id: playerId,
      }),
    });
  }

  async getDraft(draftId: string) {
    return this.request<{
      draft: Draft;
      users: LeagueUser[];
      picks: DraftPick[];
      available_players: Player[];
      current_picker: string;
    }>(`/api/drafts/${draftId}`);
  }

  async getDraftRosters(draftId: string) {
    return this.request(`/api/drafts/${draftId}/rosters`);
  }

  // Auth endpoints
  async register(email: string, username: string, password: string): Promise<User> {
    return this.request<User>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    });
  }

  async login(username: string, password: string): Promise<AuthTokens> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Login failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/auth/me');
  }

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    return this.request<AuthTokens>('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async logout(): Promise<void> {
    await this.request('/api/auth/logout', {
      method: 'POST',
    });
  }
}

export const api = new API();
