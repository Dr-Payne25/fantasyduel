#!/usr/bin/env python3
"""
Create demo data for testing
"""
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.auth.utils import get_password_hash  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.league import League, LeagueUser  # noqa: E402
from app.models.user import User  # noqa: E402


def create_demo_data():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            # Create admin user
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@fantasyduel.com",
                username="admin",
                password_hash=get_password_hash("admin123"),
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(admin)
            print("✅ Created admin user - Username: admin, Password: admin123")
        else:
            print("ℹ️  Admin user already exists - Username: admin")

        # Check if demo league exists
        demo_league = db.query(League).filter(League.name == "Demo League 2025").first()

        if not demo_league:
            # Create demo league
            demo_league = League(
                id=str(uuid.uuid4()),
                name="Demo League 2025",
                commissioner_id=admin.id,
                status="setup",
                created_at=datetime.now(timezone.utc),
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
            db.add(demo_league)

            # Add admin as league user
            league_user = LeagueUser(
                league_id=demo_league.id,
                user_id=admin.id,
                email=admin.email,
                display_name=admin.username,
            )
            db.add(league_user)

            print(f"✅ Created demo league - Name: Demo League 2025, " f"ID: {demo_league.id}")
        else:
            print(f"ℹ️  Demo league already exists - Name: {demo_league.name}, " f"ID: {demo_league.id}")

        # Create additional test users if needed
        test_users = []
        for i in range(1, 10):
            username = f"player{i}"
            user = db.query(User).filter(User.username == username).first()

            if not user:
                user = User(
                    id=str(uuid.uuid4()),
                    email=f"player{i}@fantasyduel.com",
                    username=username,
                    password_hash=get_password_hash("password123"),
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(user)
                test_users.append(user)
                print(f"✅ Created test user - Username: {username}, " f"Password: password123")

        db.commit()

        # Add test users to demo league if created
        if test_users and demo_league:
            for i, user in enumerate(test_users):
                league_user = LeagueUser(
                    league_id=demo_league.id,
                    user_id=user.id,
                    email=user.email,
                    display_name=f"Player {i+1}",
                )
                db.add(league_user)
            db.commit()
            print(f"✅ Added {len(test_users)} test users to demo league")

        print("\n📋 Summary:")
        print("=" * 50)
        print("Admin Account:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email: admin@fantasyduel.com")
        print("\nTest Accounts (player1-player9):")
        print("  Password: password123")
        print(f"\nDemo League ID: {demo_league.id}")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_data()
