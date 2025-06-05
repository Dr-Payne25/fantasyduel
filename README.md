# FantasyDuel 🏈

A unique fantasy football app with 1v1 draft mechanics where 12 players are split into 6 pairs, each drafting from equally-valued player pools.

## Recent Updates (December 2024)

- ✅ Full authentication system with JWT tokens
- ✅ Navigation improvements with user dashboard
- ✅ Comprehensive test suites (Backend: 81% coverage, Frontend: 39 tests)
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Pre-commit hooks for code quality

## Quick Start

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Git Workflow

We use a feature branch workflow to keep `main` stable:

### Branches

- **main**: Production-ready code only
- **dev**: Active development branch
- **feature/***: Individual feature branches

### Development Process

1. **Start new work**

   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**

   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

3. **Push feature branch**

   ```bash
   git push origin feature/your-feature-name
   ```

4. **Merge to dev** (via pull request or locally)

   ```bash
   git checkout dev
   git merge feature/your-feature-name
   git push origin dev
   ```

5. **Deploy to main** (when dev is stable)

   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```

### Branch Protection Rules (Recommended)

- Protect `main` branch
- Require pull request reviews
- Run tests before merging

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

## Tech Stack

- **Backend**: FastAPI (Python) with SQLite
- **Frontend**: React with TypeScript and Tailwind CSS
- **Data Source**: Sleeper API
- **Real-time**: WebSockets
