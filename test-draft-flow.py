#!/usr/bin/env python3
"""Test the complete draft flow"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_draft_flow():
    # Load test data
    with open("test-league-data.json", "r") as f:
        test_data = json.load(f)

    league_id = test_data["league_id"]

    # Get league info
    resp = requests.get(f"{BASE_URL}/leagues/{league_id}")
    league_data = resp.json()

    print(f"League: {league_data['league']['name']}")
    print(f"Users: {league_data['user_count']}/12")
    print(f"Pairs: {len(league_data['pairs'])}")
    print(f"Active Drafts: {len(league_data['drafts'])}")

    # Check each draft
    for pair_id, draft_info in league_data['drafts'].items():
        print(f"\nDraft for Pair {pair_id}:")
        print(f"  ID: {draft_info['id']}")
        print(f"  Status: {draft_info['status']}")

        # Get draft details
        draft_resp = requests.get(f"{BASE_URL}/drafts/{draft_info['id']}")
        draft_data = draft_resp.json()

        print(f"  Picks made: {len(draft_data['picks'])}")
        print(f"  Available players: {len(draft_data['available_players'])}")

        # Get the users in this draft
        users = draft_data['users']
        print(f"  Users: {users[0]['display_name']} vs {users[1]['display_name']}")

        # Show current picker
        current_picker = next(u for u in users if u['user_id'] == draft_data['current_picker'])
        print(f"  Current picker: {current_picker['display_name']}")

        # Show top 5 available players
        print(f"  Top 5 available players:")
        for i, player in enumerate(draft_data['available_players'][:5]):
            print(f"    {i+1}. {player['full_name']} ({player['position']}) - {player['team']}")

if __name__ == "__main__":
    test_draft_flow()
