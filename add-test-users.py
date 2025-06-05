#!/usr/bin/env python3
import requests
import sys

if len(sys.argv) != 2:
    print("Usage: python add-test-users.py <league_id>")
    sys.exit(1)

league_id = sys.argv[1]
api_url = "http://localhost:8000"

test_users = [
    {"name": "Alice Johnson", "email": "alice@test.com"},
    {"name": "Bob Smith", "email": "bob@test.com"},
    {"name": "Charlie Brown", "email": "charlie@test.com"},
    {"name": "Diana Prince", "email": "diana@test.com"},
    {"name": "Ethan Hunt", "email": "ethan@test.com"},
    {"name": "Fiona Green", "email": "fiona@test.com"},
    {"name": "George Wilson", "email": "george@test.com"},
    {"name": "Hannah Montana", "email": "hannah@test.com"},
    {"name": "Ian Malcolm", "email": "ian@test.com"},
    {"name": "Julia Roberts", "email": "julia@test.com"},
    {"name": "Kevin Hart", "email": "kevin@test.com"},
]

print(f"Adding test users to league {league_id}...")

for i, user in enumerate(test_users, 1):
    try:
        response = requests.post(
            f"{api_url}/api/leagues/join",
            json={
                "league_id": league_id,
                "user_name": user["name"],
                "email": user["email"]
            }
        )
        if response.status_code == 200:
            print(f"✓ Added user {i}/11: {user['name']}")
        else:
            print(f"✗ Failed to add {user['name']}: {response.text}")
    except Exception as e:
        print(f"✗ Error adding {user['name']}: {e}")

print("\nDone! Check your league at http://localhost:3000/league/" + league_id)
