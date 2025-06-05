"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import User, League, Player
from app.auth.utils import get_password_hash
from main import app
import uuid


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with the test database"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("testpass123"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get authentication headers for a test user"""
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "testpass123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_league(db: Session, test_user: User) -> League:
    """Create a test league"""
    league = League(
        id=str(uuid.uuid4()),
        name="Test League",
        commissioner_id=test_user.id,
        status="setup",
        settings={
            "roster_spots": {
                "QB": 1,
                "RB": 2,
                "WR": 2,
                "TE": 1,
                "FLEX": 1,
                "K": 1,
                "DEF": 1,
                "BENCH": 6,
            },
            "scoring": "PPR",
        },
    )
    db.add(league)
    db.commit()
    db.refresh(league)
    return league


@pytest.fixture
def sample_players(db: Session) -> list[Player]:
    """Create sample players for testing"""
    positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
    players = []

    for i, position in enumerate(positions * 10):  # 60 players total
        player = Player(
            id=str(uuid.uuid4()),
            sleeper_id=f"sleeper_{i}",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            full_name=f"First{i} Last{i}",
            team=f"TM{i % 32}",
            position=position,
            fantasy_positions=[position],
            age=20 + (i % 15),
            status="active",
            composite_rank=float(i + 1),
            pool_assignment=i % 6,
        )
        players.append(player)
        db.add(player)

    db.commit()
    return players


# Event loop configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
