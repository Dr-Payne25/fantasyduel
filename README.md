# FantasyDuel

A unique fantasy football app with 1v1 draft mechanics where 12 players are split into 6 pairs, each drafting from equally-valued player pools.

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Initialize Player Data
1. Start the backend server
2. Sync players: `curl -X POST http://localhost:8000/api/players/sync`
3. Divide into pools: `curl -X POST http://localhost:8000/api/players/divide-pools`

## Features
- Automatic player pool division into 6 equal-value groups
- Real-time 1v1 drafting with WebSocket support
- Sleeper-inspired modern UI
- Fair and balanced draft experience

## API Endpoints
- `POST /api/players/sync` - Sync players from Sleeper API
- `POST /api/players/divide-pools` - Create 6 equal pools
- `POST /api/leagues/create` - Create a new league
- `POST /api/drafts/start` - Start a 1v1 draft
- `WS /ws/{draft_id}` - WebSocket for live draft updates