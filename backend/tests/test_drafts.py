"""
Test draft endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import League, LeagueUser, DraftPair, Draft, DraftPick, Player, User
import uuid


class TestDraftEndpoints:
    """Test draft API endpoints"""
    
    @pytest.fixture
    def draft_setup(self, db: Session, test_league: League, sample_players: list[Player]):
        """Set up a league with pairs ready for drafting"""
        # Create 2 users for a pair
        users = []
        for i in range(2):
            user = User(
                id=str(uuid.uuid4()),
                email=f"draftuser{i}@example.com",
                username=f"draftuser{i}",
                password_hash="dummy",
                is_active=True
            )
            db.add(user)
            users.append(user)
        
        # Create draft pair
        pair = DraftPair(
            league_id=test_league.id,
            pool_number=0,
            draft_order=0
        )
        db.add(pair)
        db.flush()
        
        # Add users to league and pair
        for user in users:
            league_user = LeagueUser(
                league_id=test_league.id,
                user_id=user.id,
                email=user.email,
                display_name=user.username,
                pair_id=pair.id
            )
            db.add(league_user)
        
        db.commit()
        return {"pair": pair, "users": users, "players": sample_players}
    
    @pytest.mark.unit
    def test_start_draft(self, client: TestClient, db: Session, draft_setup, auth_headers: dict):
        """Test starting a draft for a pair"""
        pair = draft_setup["pair"]
        
        response = client.post(
            "/api/drafts/start",
            json={"pair_id": pair.id},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "draft" in data
        assert data["draft"]["pair_id"] == pair.id
        assert data["draft"]["status"] == "active"
        assert data["pool_number"] == 0
        assert len(data["users"]) == 2
        
        # Verify draft was created in database
        draft = db.query(Draft).filter_by(pair_id=pair.id).first()
        assert draft is not None
        assert draft.status == "active"
    
    @pytest.mark.unit
    def test_start_duplicate_draft(self, client: TestClient, db: Session, draft_setup, auth_headers: dict):
        """Test starting a draft when one already exists"""
        pair = draft_setup["pair"]
        
        # Start first draft
        client.post("/api/drafts/start", json={"pair_id": pair.id}, headers=auth_headers)
        
        # Try to start another
        response = client.post(
            "/api/drafts/start",
            json={"pair_id": pair.id},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Draft already exists" in response.json()["detail"]
    
    @pytest.mark.unit
    def test_make_pick(self, client: TestClient, db: Session, draft_setup, auth_headers: dict):
        """Test making a draft pick"""
        pair = draft_setup["pair"]
        users = draft_setup["users"]
        players = draft_setup["players"]
        
        # Start draft
        start_resp = client.post(
            "/api/drafts/start",
            json={"pair_id": pair.id},
            headers=auth_headers
        )
        draft_id = start_resp.json()["draft"]["id"]
        current_picker = start_resp.json()["draft"]["current_picker_id"]
        
        # Get a player from pool 0
        player = next(p for p in players if p.pool_assignment == 0)
        
        response = client.post(
            "/api/drafts/pick",
            json={
                "draft_id": draft_id,
                "user_id": current_picker,
                "player_id": player.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Check the response structure (pick and player might be empty dicts)
        assert "pick" in data
        assert "player" in data
        assert data["next_picker"] != current_picker  # Turn should switch
        assert data["draft_status"] == "active"
        
        # Verify pick was saved
        pick = db.query(DraftPick).filter_by(
            draft_id=draft_id,
            player_id=player.id
        ).first()
        assert pick is not None
        assert pick.user_id == current_picker
    
    @pytest.mark.unit
    def test_pick_wrong_turn(self, client: TestClient, db: Session, draft_setup, auth_headers: dict):
        """Test making a pick when it's not your turn"""
        pair = draft_setup["pair"]
        users = draft_setup["users"]
        players = draft_setup["players"]
        
        # Start draft
        start_resp = client.post(
            "/api/drafts/start",
            json={"pair_id": pair.id},
            headers=auth_headers
        )
        draft_id = start_resp.json()["draft"]["id"]
        current_picker = start_resp.json()["draft"]["current_picker_id"]
        
        # Try to pick as the wrong user
        wrong_user = next(u.id for u in users if u.id != current_picker)
        player = next(p for p in players if p.pool_assignment == 0)
        
        response = client.post(
            "/api/drafts/pick",
            json={
                "draft_id": draft_id,
                "user_id": wrong_user,
                "player_id": player.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Not your turn" in response.json()["detail"]
    
    @pytest.mark.unit
    def test_pick_wrong_pool(self, client: TestClient, db: Session, draft_setup, auth_headers: dict):
        """Test picking a player from wrong pool"""
        pair = draft_setup["pair"]
        players = draft_setup["players"]
        
        # Start draft
        start_resp = client.post(
            "/api/drafts/start",
            json={"pair_id": pair.id},
            headers=auth_headers
        )
        draft_id = start_resp.json()["draft"]["id"]
        current_picker = start_resp.json()["draft"]["current_picker_id"]
        
        # Get a player from wrong pool
        wrong_pool_player = next(p for p in players if p.pool_assignment != 0)
        
        response = client.post(
            "/api/drafts/pick",
            json={
                "draft_id": draft_id,
                "user_id": current_picker,
                "player_id": wrong_pool_player.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "not available in your pool" in response.json()["detail"]
    
    @pytest.mark.unit
    def test_get_draft(self, client: TestClient, db: Session, draft_setup, auth_headers: dict):
        """Test getting draft details"""
        pair = draft_setup["pair"]
        
        # Start draft
        start_resp = client.post(
            "/api/drafts/start",
            json={"pair_id": pair.id},
            headers=auth_headers
        )
        draft_id = start_resp.json()["draft"]["id"]
        
        response = client.get(f"/api/drafts/{draft_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["draft"]["id"] == draft_id
        assert len(data["users"]) == 2
        assert len(data["picks"]) == 0
        assert len(data["available_players"]) > 0
        
        # All available players should be from pool 0
        for player in data["available_players"]:
            assert player["pool_assignment"] == 0
    
    @pytest.mark.integration
    def test_complete_draft_flow(self, client: TestClient, db: Session, draft_setup, auth_headers: dict):
        """Test a complete draft with multiple picks"""
        pair = draft_setup["pair"]
        users = draft_setup["users"]
        players = [p for p in draft_setup["players"] if p.pool_assignment == 0]
        
        # Start draft
        start_resp = client.post(
            "/api/drafts/start",
            json={"pair_id": pair.id},
            headers=auth_headers
        )
        draft_id = start_resp.json()["draft"]["id"]
        
        # Make several picks alternating between users
        for i in range(6):  # 3 picks each
            # Get current state
            draft_resp = client.get(f"/api/drafts/{draft_id}")
            current_picker = draft_resp.json()["current_picker"]
            available = draft_resp.json()["available_players"]
            
            # Pick first available player
            pick_resp = client.post(
                "/api/drafts/pick",
                json={
                    "draft_id": draft_id,
                    "user_id": current_picker,
                    "player_id": available[0]["id"]
                },
                headers=auth_headers
            )
            assert pick_resp.status_code == 200
        
        # Verify final state
        final_resp = client.get(f"/api/drafts/{draft_id}")
        assert len(final_resp.json()["picks"]) == 6
        
        # Each user should have 3 picks
        picks_by_user = {}
        for pick in final_resp.json()["picks"]:
            user_id = pick["user_id"]
            picks_by_user[user_id] = picks_by_user.get(user_id, 0) + 1
        
        assert all(count == 3 for count in picks_by_user.values())