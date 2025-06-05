#!/usr/bin/env python3
"""
Set up a complete test league with players, users, and draft data
"""
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.auth.utils import get_password_hash  # noqa: E402
from app.database import Base  # noqa: E402
from app.models import Draft, DraftPair, League, LeagueUser, Player, User  # noqa: E402
from app.services.pool_division import PoolDivisionService  # noqa: E402
from app.services.sleeper_api import sleeper_api  # noqa: E402


async def setup_test_league():
    """Create a complete test league with all data"""
    # Create database session
    engine = create_engine("sqlite:///./fantasyduel.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("🏈 Setting up FantasyDuel test league...")

        # Step 1: Create test users
        print("\n1️⃣ Creating test users...")
        users = []

        # Create admin user first
        admin_existing = db.query(User).filter_by(username="admin").first()
        if not admin_existing:
            admin_user = User(
                id="admin-user",
                email="admin@fantasyduel.com",
                username="admin",
                password_hash=get_password_hash("admin123"),
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(admin_user)
            users.append(admin_user)
            print("  ✅ Created admin user")
        else:
            users.append(admin_existing)
            print("  ℹ️  Admin user already exists")

        for i in range(1, 12):  # 11 more users to make 12 total
            username = f"testuser{i}"
            existing = db.query(User).filter_by(username=username).first()

            if not existing:
                user = User(
                    id=f"user-{i}",
                    email=f"testuser{i}@example.com",
                    username=username,
                    password_hash=get_password_hash("password123"),
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(user)
                users.append(user)
                print(f"  ✅ Created {username}")
            else:
                users.append(existing)
                print(f"  ℹ️  User {username} already exists")

        db.commit()

        # Step 2: Sync players from Sleeper API
        print("\n2️⃣ Syncing players from Sleeper API...")
        try:
            players_data = await sleeper_api.get_all_players()

            positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
            active_count = 0

            for sleeper_id, player_data in players_data.items():
                if (
                    player_data.get("active")
                    and player_data.get("position") in positions
                ):
                    existing = db.query(Player).filter_by(sleeper_id=sleeper_id).first()

                    if not existing:
                        # Generate realistic fantasy rankings
                        base_rank = active_count + 1
                        sleeper_rank = base_rank + (active_count % 5) - 2
                        espn_rank = base_rank + (active_count % 7) - 3
                        yahoo_rank = base_rank + (active_count % 3) - 1

                        player = Player(
                            id=f"player-{sleeper_id}",
                            sleeper_id=sleeper_id,
                            first_name=player_data.get("first_name", ""),
                            last_name=player_data.get("last_name", ""),
                            full_name=player_data.get("full_name", ""),
                            team=player_data.get("team", ""),
                            position=player_data.get("position", ""),
                            fantasy_positions=player_data.get("fantasy_positions", []),
                            age=player_data.get("age"),
                            status=player_data.get("status", ""),
                            sleeper_rank=sleeper_rank,
                            espn_rank=espn_rank,
                            yahoo_rank=yahoo_rank,
                            metadata_json=player_data,
                        )
                        db.add(player)
                        active_count += 1

            db.commit()
            print(f"  ✅ Synced {active_count} active players")

        except Exception as e:
            print(f"  ❌ Error syncing players: {e}")
            print("  ℹ️  Creating sample players instead...")

            # Create sample players if API fails
            sample_players = [
                ("Patrick Mahomes", "QB", "KC"),
                ("Josh Allen", "QB", "BUF"),
                ("Christian McCaffrey", "RB", "SF"),
                ("Austin Ekeler", "RB", "LAC"),
                ("Tyreek Hill", "WR", "MIA"),
                ("Stefon Diggs", "WR", "BUF"),
                ("Travis Kelce", "TE", "KC"),
                ("Mark Andrews", "TE", "BAL"),
                ("Justin Tucker", "K", "BAL"),
                ("Harrison Butker", "K", "KC"),
                ("49ers", "DEF", "SF"),
                ("Bills", "DEF", "BUF"),
            ]

            for i, (name, pos, team) in enumerate(
                sample_players * 20
            ):  # Create enough players
                # Generate varied rankings based on player index and position
                base_rank = i + 1
                sleeper_rank = base_rank + (i % 5) - 2
                espn_rank = base_rank + (i % 7) - 3
                yahoo_rank = base_rank + (i % 3) - 1

                player = Player(
                    id=f"sample-player-{i}",
                    sleeper_id=f"sample-{i}",
                    full_name=f"{name} {i//len(sample_players)}",
                    first_name=name.split()[0],
                    last_name=name.split()[-1] if len(name.split()) > 1 else "",
                    team=team,
                    position=pos,
                    fantasy_positions=[pos],
                    status="active",
                    sleeper_rank=sleeper_rank,
                    espn_rank=espn_rank,
                    yahoo_rank=yahoo_rank,
                )
                db.add(player)
            db.commit()

        # Step 3: Divide players into pools
        print("\n3️⃣ Dividing players into pools...")
        all_players = db.query(Player).filter(Player.position.in_(positions)).all()

        # Prepare player data for pool division
        players_dict = []
        for player in all_players:
            players_dict.append(
                {
                    "id": player.id,
                    "position": player.position,
                    "sleeper_rank": player.sleeper_rank or 999,
                    "espn_rank": player.espn_rank or 999,
                    "yahoo_rank": player.yahoo_rank or 999,
                }
            )

        # Divide into pools
        pool_service = PoolDivisionService()
        pools, pool_values = pool_service.divide_players_into_pools(players_dict)

        # Update player pool assignments
        for pool_idx, pool_players in pools.items():
            for player_data in pool_players:
                player = db.query(Player).filter_by(id=player_data["id"]).first()
                if player:
                    player.pool_assignment = pool_idx
                    player.composite_rank = player_data["composite_value"]

        db.commit()
        print(f"  ✅ Divided players into {len(pools)} pools")

        # Step 4: Create test league
        print("\n4️⃣ Creating test league...")
        test_league = db.query(League).filter_by(name="Test League 2025").first()

        if not test_league:
            test_league = League(
                id="test-league-2025",
                name="Test League 2025",
                commissioner_id=users[0].id,
                status="draft_ready",
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
                created_at=datetime.now(timezone.utc),
            )
            db.add(test_league)
            print("  ✅ Created Test League 2025")
        else:
            print("  ℹ️  Test League 2025 already exists")

        # Step 5: Add users to league
        print("\n5️⃣ Adding users to league...")
        for user in users:
            existing = (
                db.query(LeagueUser)
                .filter_by(league_id=test_league.id, user_id=user.id)
                .first()
            )

            if not existing:
                league_user = LeagueUser(
                    league_id=test_league.id,
                    user_id=user.id,
                    email=user.email,
                    display_name=user.username,
                )
                db.add(league_user)

        db.commit()

        # Step 6: Create draft pairs
        print("\n6️⃣ Creating draft pairs...")
        existing_pairs = db.query(DraftPair).filter_by(league_id=test_league.id).count()

        if existing_pairs == 0:
            league_users = (
                db.query(LeagueUser).filter_by(league_id=test_league.id).all()
            )

            for i in range(6):  # 6 pairs for 12 users
                pair = DraftPair(league_id=test_league.id, pool_number=i, draft_order=i)
                db.add(pair)
                db.flush()

                # Assign users to pairs
                league_users[i * 2].pair_id = pair.id
                league_users[i * 2 + 1].pair_id = pair.id

                print(
                    f"  ✅ Created Pair {i+1}: {league_users[i*2].display_name} & {league_users[i*2+1].display_name}"
                )

            test_league.status = "draft_ready"
            db.commit()
        else:
            print("  ℹ️  Draft pairs already exist")

        # Step 7: Create a sample draft for the first pair
        print("\n7️⃣ Creating sample draft for first pair...")
        first_pair = (
            db.query(DraftPair)
            .filter_by(league_id=test_league.id, pool_number=0)
            .first()
        )

        if first_pair:
            existing_draft = db.query(Draft).filter_by(pair_id=first_pair.id).first()

            if not existing_draft:
                pair_users = db.query(LeagueUser).filter_by(pair_id=first_pair.id).all()

                draft = Draft(
                    id="test-draft-1",
                    pair_id=first_pair.id,
                    status="active",
                    current_picker_id=pair_users[0].user_id,
                    started_at=datetime.now(timezone.utc),
                )
                db.add(draft)
                db.commit()
                print(
                    f"  ✅ Created active draft for {pair_users[0].display_name} vs {pair_users[1].display_name}"
                )
            else:
                print("  ℹ️  Draft already exists for first pair")

        print("\n✅ Test league setup complete!")
        print("\n📊 Summary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Players: {db.query(Player).count()}")
        print(f"  - League: {test_league.name}")
        print(
            f"  - Draft Pairs: {db.query(DraftPair).filter_by(league_id=test_league.id).count()}"
        )
        print(
            f"  - Active Drafts: {db.query(Draft).filter_by(status='active').count()}"
        )

        print("\n🔑 Login credentials:")
        print("  Admin: username: admin, password: admin123")
        print("  Test users: testuser1-11, password: password123")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        await sleeper_api.close()


if __name__ == "__main__":
    asyncio.run(setup_test_league())
