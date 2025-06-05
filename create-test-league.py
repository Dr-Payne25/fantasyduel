#!/usr/bin/env python3
"""
Create a fully populated test league for FantasyDuel development.
This script creates a league, adds 12 test users, creates draft pairs,
and optionally starts a draft.
"""

import requests
import json
import time
import sys
from datetime import datetime

API_URL = "http://localhost:8000"

# Test users with realistic names
TEST_USERS = [
    {"name": "Alex Commissioner", "email": "alex@test.com"},
    {"name": "Blake Richardson", "email": "blake@test.com"},
    {"name": "Casey Thompson", "email": "casey@test.com"},
    {"name": "Drew Mitchell", "email": "drew@test.com"},
    {"name": "Emma Watson", "email": "emma@test.com"},
    {"name": "Felix Rodriguez", "email": "felix@test.com"},
    {"name": "Grace Chen", "email": "grace@test.com"},
    {"name": "Henry Davis", "email": "henry@test.com"},
    {"name": "Iris Johnson", "email": "iris@test.com"},
    {"name": "Jake Williams", "email": "jake@test.com"},
    {"name": "Kelly Brown", "email": "kelly@test.com"},
    {"name": "Liam O'Brien", "email": "liam@test.com"},
]

def create_league():
    """Create a new test league"""
    print("🏈 Creating test league...")
    
    league_data = {
        "name": f"Test League {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "commissioner_name": TEST_USERS[0]["name"],
        "commissioner_email": TEST_USERS[0]["email"]
    }
    
    response = requests.post(f"{API_URL}/api/leagues/create", json=league_data)
    if response.status_code != 200:
        print(f"❌ Failed to create league: {response.text}")
        sys.exit(1)
    
    result = response.json()
    league_id = result["invite_code"]
    print(f"✅ League created with ID: {league_id}")
    return league_id

def add_users(league_id):
    """Add remaining 11 users to the league"""
    print("\n👥 Adding users to league...")
    
    # Skip first user (commissioner)
    for i, user in enumerate(TEST_USERS[1:], 2):
        response = requests.post(
            f"{API_URL}/api/leagues/join",
            json={
                "league_id": league_id,
                "user_name": user["name"],
                "email": user["email"]
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Added user {i}/12: {user['name']}")
        else:
            print(f"❌ Failed to add {user['name']}: {response.text}")
            return False
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    return True

def create_draft_pairs(league_id):
    """Create draft pairs for the league"""
    print("\n🎲 Creating draft pairs...")
    
    response = requests.post(f"{API_URL}/api/leagues/{league_id}/create-pairs")
    if response.status_code != 200:
        print(f"❌ Failed to create pairs: {response.text}")
        return False
    
    result = response.json()
    print("✅ Draft pairs created:")
    for pair in result["pairs"]:
        print(f"   Pool {pair['pool_number']}: {pair['users'][0]} vs {pair['users'][1]}")
    
    return result["pairs"]

def get_league_info(league_id):
    """Get and display league information"""
    response = requests.get(f"{API_URL}/api/leagues/{league_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get league info: {response.text}")
        return None
    
    return response.json()

def save_test_data(league_id, league_info):
    """Save test league data for future use"""
    test_data = {
        "league_id": league_id,
        "created_at": datetime.now().isoformat(),
        "users": [
            {
                "user_id": user["user_id"],
                "name": user["display_name"],
                "email": user["email"],
                "pair_id": user["pair_id"]
            }
            for user in league_info["users"]
        ],
        "pairs": [
            {
                "pair_id": pair["id"],
                "pool_number": pair["pool_number"],
                "users": [
                    u["display_name"] for u in league_info["users"] if u["pair_id"] == pair["id"]
                ]
            }
            for pair in league_info["pairs"]
        ]
    }
    
    with open("test-league-data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\n💾 Test data saved to test-league-data.json")
    return test_data

def print_summary(league_id, test_data):
    """Print a summary of the test league"""
    print("\n" + "="*60)
    print("🎉 TEST LEAGUE CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📋 League ID: {league_id}")
    print(f"🔗 League URL: http://localhost:3000/league/{league_id}")
    print(f"\n👥 Users:")
    for user in test_data["users"]:
        pair_info = next((p for p in test_data["pairs"] if p["pair_id"] == user["pair_id"]), None)
        pool = f"Pool {pair_info['pool_number']}" if pair_info else "No pair"
        print(f"   - {user['name']} ({user['email']}) - {pool}")
    
    print(f"\n🎯 Draft Pairs:")
    for pair in test_data["pairs"]:
        print(f"   Pool {pair['pool_number']}: {' vs '.join(pair['users'])}")
    
    print("\n📝 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print(f"2. Go to the league: http://localhost:3000/league/{league_id}")
    print("3. Click 'Start Draft' on any pair to test drafting")
    print("\n💡 Tip: Use different browser windows/incognito to simulate different users")

def main():
    """Main function to create test league"""
    print("🚀 FantasyDuel Test League Creator")
    print("==================================\n")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code != 200:
            print("❌ API is not running. Please start the backend first:")
            print("   cd backend && source venv/bin/activate && python main.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at http://localhost:8000")
        print("   Please start the backend first:")
        print("   cd backend && source venv/bin/activate && python main.py")
        sys.exit(1)
    
    # Create league
    league_id = create_league()
    
    # Add users
    if not add_users(league_id):
        print("❌ Failed to add all users")
        sys.exit(1)
    
    # Create draft pairs
    pairs = create_draft_pairs(league_id)
    if not pairs:
        print("❌ Failed to create draft pairs")
        sys.exit(1)
    
    # Get league info and save test data
    league_info = get_league_info(league_id)
    if league_info:
        test_data = save_test_data(league_id, league_info)
        print_summary(league_id, test_data)
    
    print("\n✅ Test league setup complete!")

if __name__ == "__main__":
    main()