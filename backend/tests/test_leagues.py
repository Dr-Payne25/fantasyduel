"""
Test league endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import DraftPair, League, LeagueUser, User


class TestLeagueEndpoints:
    """Test league API endpoints"""

    @pytest.mark.unit
    def test_create_league(
        self, client: TestClient, db: Session, auth_headers: dict, test_user: User
    ):
        """Test creating a new league"""
        response = client.post(
            "/api/leagues/create",
            json={
                "name": "My Test League",
                "commissioner_name": test_user.username,
                "commissioner_email": test_user.email,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "league" in data
        assert "invite_code" in data

        league = data["league"]
        assert league["name"] == "My Test League"
        assert league["status"] == "setup"
        # Commissioner ID is generated if not authenticated
        assert league["commissioner_id"] is not None

        # Verify league was created in database
        db_league = db.query(League).filter_by(id=data["invite_code"]).first()
        assert db_league is not None

        # Verify commissioner was added as user
        league_user = (
            db.query(LeagueUser)
            .filter_by(league_id=db_league.id, user_id=league["commissioner_id"])
            .first()
        )
        assert league_user is not None
        assert league_user.email == test_user.email

    @pytest.mark.unit
    def test_join_league(
        self,
        client: TestClient,
        db: Session,
        test_league: League,
        auth_headers: dict,
        test_user: User,
    ):
        """Test joining an existing league"""
        # Register and login as new user
        register_resp = client.post(
            "/api/auth/register",
            json={
                "email": "joiner@example.com",
                "username": "joiner",
                "password": "password123",
            },
        )
        assert register_resp.status_code == 200

        login_resp = client.post(
            "/api/auth/login", data={"username": "joiner", "password": "password123"}
        )
        assert login_resp.status_code == 200
        new_auth = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        response = client.post(
            "/api/leagues/join",
            json={
                "league_id": test_league.id,
                "user_name": "joiner",
                "email": "joiner@example.com",
            },
            headers=new_auth,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully joined league"

        # Verify user was added to league
        league_user = (
            db.query(LeagueUser)
            .filter_by(league_id=test_league.id, email="joiner@example.com")
            .first()
        )
        assert league_user is not None

    @pytest.mark.unit
    def test_join_full_league(
        self, client: TestClient, db: Session, test_league: League, auth_headers: dict
    ):
        """Test joining a league that's already full"""
        # Add 12 users to make league full
        for i in range(12):
            user = LeagueUser(
                league_id=test_league.id,
                user_id=f"user-{i}",
                email=f"user{i}@example.com",
                display_name=f"User {i}",
            )
            db.add(user)
        db.commit()

        response = client.post(
            "/api/leagues/join",
            json={
                "league_id": test_league.id,
                "user_name": "latecomer",
                "email": "late@example.com",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "League is full" in response.json()["detail"]

    @pytest.mark.unit
    def test_get_league(
        self, client: TestClient, db: Session, test_league: League, test_user: User
    ):
        """Test getting league details"""
        # Add a user to the league
        league_user = LeagueUser(
            league_id=test_league.id,
            user_id=test_user.id,
            email=test_user.email,
            display_name=test_user.username,
        )
        db.add(league_user)
        db.commit()

        response = client.get(f"/api/leagues/{test_league.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["league"]["id"] == test_league.id
        assert data["league"]["name"] == test_league.name
        assert data["user_count"] == 1
        assert len(data["users"]) == 1
        assert data["users"][0]["email"] == test_user.email

    @pytest.mark.unit
    def test_create_draft_pairs(
        self, client: TestClient, db: Session, test_league: League, auth_headers: dict
    ):
        """Test creating draft pairs for a league"""
        # Add exactly 12 users
        for i in range(12):
            user = LeagueUser(
                league_id=test_league.id,
                user_id=f"user-{i}",
                email=f"user{i}@example.com",
                display_name=f"User {i}",
            )
            db.add(user)
        db.commit()

        response = client.post(
            f"/api/leagues/{test_league.id}/create-pairs", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Draft pairs created"
        assert len(data["pairs"]) == 6

        # Verify pairs were created
        pairs = db.query(DraftPair).filter_by(league_id=test_league.id).all()
        assert len(pairs) == 6

        # Verify each pair has 2 users
        for pair in pairs:
            users = db.query(LeagueUser).filter_by(pair_id=pair.id).all()
            assert len(users) == 2

    @pytest.mark.unit
    def test_create_pairs_wrong_user_count(
        self, client: TestClient, db: Session, test_league: League, auth_headers: dict
    ):
        """Test creating pairs with wrong number of users"""
        # Add only 10 users (not 12)
        for i in range(10):
            user = LeagueUser(
                league_id=test_league.id,
                user_id=f"user-{i}",
                email=f"user{i}@example.com",
                display_name=f"User {i}",
            )
            db.add(user)
        db.commit()

        response = client.post(
            f"/api/leagues/{test_league.id}/create-pairs", headers=auth_headers
        )

        assert response.status_code == 400
        assert "needs exactly 12 users" in response.json()["detail"]
