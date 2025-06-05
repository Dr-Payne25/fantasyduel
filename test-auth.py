#!/usr/bin/env python3
"""Test authentication endpoints"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_auth():
    # Test registration
    print("Testing registration...")
    register_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "testpass123"
    }
    
    resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if resp.status_code == 200:
        print("✓ Registration successful")
        user = resp.json()
        print(f"  User ID: {user['id']}")
        print(f"  Email: {user['email']}")
    else:
        print(f"✗ Registration failed: {resp.status_code}")
        print(f"  {resp.text}")
    
    # Test login
    print("\nTesting login...")
    login_data = {
        "username": "testuser2",
        "password": "testpass123"
    }
    
    # OAuth2PasswordRequestForm expects form data
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,  # Use data instead of json for form encoding
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if resp.status_code == 200:
        print("✓ Login successful")
        token_data = resp.json()
        print(f"  Access token: {token_data['access_token'][:20]}...")
        print(f"  Refresh token: {token_data['refresh_token'][:20]}...")
        print(f"  Token type: {token_data['token_type']}")
        
        # Test authenticated endpoint
        print("\nTesting authenticated endpoint...")
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if resp.status_code == 200:
            print("✓ Get user info successful")
            user_info = resp.json()
            print(f"  Username: {user_info['username']}")
            print(f"  Email: {user_info['email']}")
            print(f"  Verified: {user_info['is_verified']}")
        else:
            print(f"✗ Get user info failed: {resp.status_code}")
            print(f"  {resp.text}")
    else:
        print(f"✗ Login failed: {resp.status_code}")
        print(f"  {resp.text}")

if __name__ == "__main__":
    test_auth()