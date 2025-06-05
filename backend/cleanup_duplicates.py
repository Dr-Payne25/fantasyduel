#!/usr/bin/env python3
"""
Clean up duplicate users in leagues
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import func  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models.league import LeagueUser  # noqa: E402


def cleanup_duplicate_league_users():
    db = SessionLocal()

    try:
        # Find all duplicates (same user_id and league_id)
        duplicates = (
            db.query(
                LeagueUser.league_id,
                LeagueUser.user_id,
                func.count(LeagueUser.id).label("count"),
            )
            .group_by(LeagueUser.league_id, LeagueUser.user_id)
            .having(func.count(LeagueUser.id) > 1)
            .all()
        )

        print(f"Found {len(duplicates)} cases of duplicate users in leagues")

        for league_id, user_id, count in duplicates:
            print(f"\nLeague {league_id} has {count} entries for user {user_id}")

            # Get all entries for this user in this league
            entries = db.query(LeagueUser).filter_by(
                league_id=league_id, user_id=user_id
            ).order_by(LeagueUser.id).all()

            # Keep the first entry, delete the rest
            for entry in entries[1:]:
                print(
                    f"  - Removing duplicate entry: {entry.display_name} "
                    f"(ID: {entry.id})"
                )
                db.delete(entry)

        db.commit()
        print("\n✅ Cleanup completed successfully!")

        # Show current league counts
        print("\n📊 Current league member counts:")
        from app.models.league import League  # noqa: E402

        leagues = db.query(League).all()
        for league in leagues:
            user_count = db.query(LeagueUser).filter_by(league_id=league.id).count()
            print(f"  - {league.name}: {user_count} members")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_duplicate_league_users()
