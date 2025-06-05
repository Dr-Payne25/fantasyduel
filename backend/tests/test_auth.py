"""
Test authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.utils import decode_token, verify_password
from app.models import User


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    @pytest.mark.unit
    def test_register_success(self, client: TestClient, db: Session):
        """Test successful user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "id" in data

        # Verify user was created in database
        user = db.query(User).filter_by(email="newuser@example.com").first()
        assert user is not None
        assert verify_password("securepass123", user.password_hash)

    @pytest.mark.unit
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.unit
    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with duplicate username"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "another@example.com",
                "username": test_user.username,
                "password": "password123",
            },
        )

        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    @pytest.mark.unit
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.username, "password": "testpass123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid
        payload = decode_token(data["access_token"])
        assert payload is not None
        assert payload["sub"] == test_user.id
        assert payload["type"] == "access"

    @pytest.mark.unit
    def test_login_with_email(self, client: TestClient, test_user: User):
        """Test login using email instead of username"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "testpass123"},
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.unit
    def test_login_invalid_credentials(self, client: TestClient, test_user: User):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.username, "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @pytest.mark.unit
    def test_get_current_user(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test getting current user info"""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    @pytest.mark.unit
    def test_get_current_user_no_auth(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.unit
    def test_refresh_token(self, client: TestClient, test_user: User):
        """Test refreshing access token"""
        # First login to get tokens
        login_response = client.post(
            "/api/auth/login",
            data={"username": test_user.username, "password": "testpass123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new access token
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify new access token works
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200

    @pytest.mark.unit
    def test_logout(self, client: TestClient, auth_headers: dict):
        """Test logout endpoint"""
        response = client.post("/api/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
