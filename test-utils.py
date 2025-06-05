#!/usr/bin/env python3
"""
Utility functions for testing FantasyDuel
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

def start_draft(pair_id):
    """Start a draft for a specific pair"""
    response = requests.post(
        f"{API_URL}/api/drafts/start",
        json={"pair_id": pair_id}
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Draft started!")
        print(f"   Draft ID: {result['draft']['id']}")
        print(f"   Pool: {result['pool_number']}")
        print(f"   Users: {', '.join([u['name'] for u in result['users']])}")
        print(f"   URL: http://localhost:3000/draft/{result['draft']['id']}")
        return result['draft']['id']
    else:
        print(f"❌ Failed to start draft: {response.text}")
        return None

def make_pick(draft_id, user_id, player_id):
    """Make a pick in a draft"""
    response = requests.post(
        f"{API_URL}/api/drafts/pick",
        json={
            "draft_id": draft_id,
            "user_id": user_id,
            "player_id": player_id
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Pick made: {result['player']['full_name']} ({result['player']['position']})")
        return result
    else:
        print(f"❌ Failed to make pick: {response.text}")
        return None

def get_available_players(draft_id, position=None):
    """Get available players in a draft"""
    response = requests.get(f"{API_URL}/api/drafts/{draft_id}")
    if response.status_code == 200:
        result = response.json()
        players = result['available_players']

        if position:
            players = [p for p in players if p['position'] == position]

        # Sort by composite rank
        players.sort(key=lambda x: x.get('composite_rank', 999))

        return players[:10]  # Return top 10
    else:
        print(f"❌ Failed to get draft info: {response.text}")
        return []

def show_league_status(league_id):
    """Show current league status"""
    response = requests.get(f"{API_URL}/api/leagues/{league_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 League Status: {data['league']['name']}")
        print(f"   Status: {data['league']['status']}")
        print(f"   Users: {data['user_count']}/12")

        if data['pairs']:
            print("\n🎯 Draft Pairs:")
            for pair in data['pairs']:
                users = [u for u in data['users'] if u['pair_id'] == pair['id']]
                user_names = [u['display_name'] for u in users]
                print(f"   Pool {pair['pool_number']}: {' vs '.join(user_names)}")
                print(f"      Pair ID: {pair['id']}")
    else:
        print(f"❌ Failed to get league status: {response.text}")

def load_test_data():
    """Load saved test league data"""
    try:
        with open("test-league-data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No test league data found. Run create-test-league.py first!")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test-utils.py status <league_id>")
        print("  python test-utils.py start-draft <pair_id>")
        print("  python test-utils.py players <draft_id> [position]")
        print("  python test-utils.py pick <draft_id> <user_id> <player_id>")
        print("  python test-utils.py load  # Load saved test data")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status" and len(sys.argv) >= 3:
        show_league_status(sys.argv[2])

    elif command == "start-draft" and len(sys.argv) >= 3:
        start_draft(int(sys.argv[2]))

    elif command == "players" and len(sys.argv) >= 3:
        position = sys.argv[3] if len(sys.argv) >= 4 else None
        players = get_available_players(sys.argv[2], position)
        print(f"\n🏈 Top Available Players" + (f" ({position})" if position else ""))
        for i, p in enumerate(players, 1):
            print(f"{i:2d}. {p['full_name']:20s} {p['position']:3s} {p['team'] or 'FA':3s} Rank: {p.get('composite_rank', 999):.1f}")

    elif command == "pick" and len(sys.argv) >= 5:
        make_pick(sys.argv[2], sys.argv[3], sys.argv[4])

    elif command == "load":
        data = load_test_data()
        if data:
            print(f"\n📋 Test League: {data['league_id']}")
            print(f"   Created: {data['created_at']}")
            print(f"   URL: http://localhost:3000/league/{data['league_id']}")
            print("\n👥 Users:")
            for user in data['users']:
                print(f"   {user['name']} (ID: {user['user_id']})")

    else:
        print("❌ Invalid command or missing arguments")
