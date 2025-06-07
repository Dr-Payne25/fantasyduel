#!/usr/bin/env python3
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Login as admin
print("1. Logging in as admin...")
login_data = {"username": "admin", "password": "admin123"}
response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data, timeout=10)
if response.status_code == 200:
    auth_data = response.json()
    token = auth_data["access_token"]
    print(f"   ✓ Logged in successfully. Token: {token[:20]}...")

    # Set up headers with auth
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Get leagues
    print("\n2. Getting leagues...")
    response = requests.get(
        f"{BASE_URL}/api/leagues/my-leagues", headers=headers, timeout=10
    )
    if response.status_code == 200:
        leagues = response.json()
        print(f"   ✓ Found {len(leagues)} leagues")
        if leagues:
            league = leagues[0]
            print(f"   - League: {league['name']} (ID: {league['id']})")

            # Get drafts for league
            print(f"\n3. Getting drafts for league {league['id']}...")
            response = requests.get(
                f"{BASE_URL}/api/leagues/{league['id']}/drafts",
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                drafts_data = response.json()
                drafts = drafts_data.get("drafts", [])
                print(f"   ✓ Found {len(drafts)} drafts")

                # Find in_progress draft
                active_draft = None
                for draft in drafts:
                    if draft["status"] == "in_progress":
                        active_draft = draft
                        break

                if active_draft:
                    print(
                        f"   - Active draft: {active_draft['id']} (Status: {active_draft['status']})"
                    )
                    print(
                        f"   - Current picker: {active_draft.get('current_picker_id')}"
                    )

                    # Access draft room
                    print(f"\n4. Accessing draft room {active_draft['id']}...")
                    response = requests.get(
                        f"{BASE_URL}/api/drafts/{active_draft['id']}",
                        headers=headers,
                        timeout=10,
                    )
                    if response.status_code == 200:
                        draft_data = response.json()
                        print("   ✓ Draft room loaded successfully")
                        print(f"   - Users in draft: {len(draft_data['users'])}")
                        print(
                            f"   - Available players: {len(draft_data['available_players'])}"
                        )
                        print(f"   - Picks made: {len(draft_data['picks'])}")

                        print("\n5. WebSocket connection info:")
                        print(f"   - Draft ID for WebSocket: {active_draft['id']}")
                        print(
                            f"   - WebSocket URL: ws://localhost:8000/ws/{active_draft['id']}"
                        )
                    else:
                        print(
                            f"   ✗ Failed to access draft room: {response.status_code}"
                        )
                else:
                    print("   ! No active drafts found")
            else:
                print(f"   ✗ Failed to get drafts: {response.status_code}")
    else:
        print(f"   ✗ Failed to get leagues: {response.status_code}")
else:
    print(f"   ✗ Login failed: {response.status_code}")
    print(f"   Error: {response.text}")
