import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Player
from app.services.sleeper_api import sleeper_api

engine = create_engine("sqlite:///./fantasyduel.db")
Session = sessionmaker(bind=engine)


async def fix_player_rankings():
    db = Session()

    try:
        print("Fetching current NFL players from Sleeper API...")
        players_data = await sleeper_api.get_all_players()

        # Define realistic 2024 fantasy rankings for top players by name
        TOP_PLAYERS_2024 = {
            # QBs
            "Josh Allen": 1,
            "Jalen Hurts": 2,
            "Lamar Jackson": 3,
            "Patrick Mahomes": 4,
            "Justin Herbert": 5,
            "Joe Burrow": 6,
            "Dak Prescott": 7,
            "Tua Tagovailoa": 8,
            "Trevor Lawrence": 9,
            "Kyler Murray": 10,
            # RBs
            "Christian McCaffrey": 1,
            "Austin Ekeler": 2,
            "Jonathan Taylor": 3,
            "Saquon Barkley": 4,
            "Tony Pollard": 5,
            "Josh Jacobs": 6,
            "Derrick Henry": 7,
            "Bijan Robinson": 8,
            "Nick Chubb": 9,
            "Najee Harris": 10,
            # WRs
            "Justin Jefferson": 1,
            "Ja'Marr Chase": 2,
            "CeeDee Lamb": 3,
            "Tyreek Hill": 4,
            "A.J. Brown": 5,
            "Davante Adams": 6,
            "Stefon Diggs": 7,
            "Jaylen Waddle": 8,
            "DeVonta Smith": 9,
            "Chris Olave": 10,
            # TEs
            "Travis Kelce": 1,
            "Mark Andrews": 2,
            "T.J. Hockenson": 3,
            "Dallas Goedert": 4,
            "George Kittle": 5,
            "Kyle Pitts": 6,
            "Darren Waller": 7,
            "Cole Kmet": 8,
            "Evan Engram": 9,
            "Pat Freiermuth": 10,
        }

        # Add team defenses
        TEAM_DEFENSES = {
            "SF": ("49ers", 1),
            "DAL": ("Cowboys", 2),
            "BUF": ("Bills", 3),
            "BAL": ("Ravens", 4),
            "PIT": ("Steelers", 5),
            "NE": ("Patriots", 6),
            "PHI": ("Eagles", 7),
            "NYJ": ("Jets", 8),
            "KC": ("Chiefs", 9),
            "MIA": ("Dolphins", 10),
            "CLE": ("Browns", 11),
            "LAR": ("Rams", 12),
            "TB": ("Buccaneers", 13),
            "NO": ("Saints", 14),
            "GB": ("Packers", 15),
            "DEN": ("Broncos", 16),
            "IND": ("Colts", 17),
            "CIN": ("Bengals", 18),
            "TEN": ("Titans", 19),
            "MIN": ("Vikings", 20),
            "WAS": ("Commanders", 21),
            "JAX": ("Jaguars", 22),
            "SEA": ("Seahawks", 23),
            "CAR": ("Panthers", 24),
            "CHI": ("Bears", 25),
            "LAC": ("Chargers", 26),
            "NYG": ("Giants", 27),
            "ATL": ("Falcons", 28),
            "DET": ("Lions", 29),
            "ARI": ("Cardinals", 30),
            "LV": ("Raiders", 31),
            "HOU": ("Texans", 32),
        }

        # First, clear existing players
        print("Clearing existing players...")
        db.query(Player).delete()

        # Counter for active NFL players
        active_count = 0
        position_count = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "K": 0, "DEF": 0}

        print("Adding active NFL players...")
        for sleeper_id, player_data in players_data.items():
            if not player_data.get("active") or player_data.get("status") not in [
                "Active",
                "Inactive",
                "Injured Reserve",
            ]:
                continue

            position = player_data.get("position")
            if position not in ["QB", "RB", "WR", "TE", "K", "DEF"]:
                continue

            # Skip if no valid name
            full_name = player_data.get("full_name", "")
            if not full_name or full_name.strip() == "":
                continue

            # Generate realistic rankings
            player_name = full_name
            if player_name in TOP_PLAYERS_2024:
                base_rank = TOP_PLAYERS_2024[player_name]
            else:
                # Use position count to generate sequential rankings
                base_rank = position_count[position] + 15

            # Add some variance for different platforms
            sleeper_rank = base_rank
            espn_rank = base_rank + (active_count % 3) - 1
            yahoo_rank = base_rank + (active_count % 5) - 2

            # Calculate composite rank
            composite = (sleeper_rank + espn_rank + yahoo_rank) / 3.0

            # Apply position weight
            position_weight = {
                "QB": 1.0,
                "RB": 0.9,
                "WR": 0.9,
                "TE": 1.1,
                "K": 2.0,  # Kickers drafted later
                "DEF": 1.8,  # Defenses drafted later
            }.get(position, 1.0)

            composite = composite * position_weight

            player = Player(
                id=f"player-{sleeper_id}",
                sleeper_id=sleeper_id,
                first_name=player_data.get("first_name", ""),
                last_name=player_data.get("last_name", ""),
                full_name=full_name,
                team=player_data.get("team", ""),
                position=position,
                fantasy_positions=player_data.get("fantasy_positions", []),
                age=player_data.get("age"),
                status=player_data.get("status", ""),
                sleeper_rank=sleeper_rank,
                espn_rank=espn_rank,
                yahoo_rank=yahoo_rank,
                composite_rank=composite,
                metadata_json=player_data,
            )

            db.add(player)
            active_count += 1
            position_count[position] += 1

            if active_count % 100 == 0:
                print(f"  Added {active_count} players...")

        db.commit()
        print(f"\n✅ Added {active_count} active NFL players")
        print(f"Position breakdown: {position_count}")

        # Add team defenses
        print("\nAdding team defenses...")
        for team_code, (team_name, rank) in TEAM_DEFENSES.items():
            defense_id = f"def-{team_code}"

            # Add variance
            sleeper_rank = rank
            espn_rank = rank + (rank % 3) - 1
            yahoo_rank = rank + (rank % 2)
            composite = (sleeper_rank + espn_rank + yahoo_rank) / 3.0 * 1.8

            player = Player(
                id=defense_id,
                sleeper_id=defense_id,
                first_name=team_name,
                last_name="DEF",
                full_name=f"{team_name} DEF",
                team=team_code,
                position="DEF",
                fantasy_positions=["DEF"],
                status="active",
                sleeper_rank=sleeper_rank,
                espn_rank=espn_rank,
                yahoo_rank=yahoo_rank,
                composite_rank=composite,
            )
            db.add(player)

        db.commit()
        print(f"✅ Added {len(TEAM_DEFENSES)} team defenses")

        # Now run pool division
        print("\nDividing players into pools...")
        from app.services.pool_division import PoolDivisionService

        all_players = db.query(Player).all()
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

        pool_service = PoolDivisionService()
        pools, pool_values = pool_service.divide_players_into_pools(players_dict)

        # Update player pool assignments
        for pool_idx, pool_players in pools.items():
            for player_data in pool_players:
                player = db.query(Player).filter_by(id=player_data["id"]).first()
                if player:
                    player.pool_assignment = pool_idx
                    # Keep the composite rank we calculated, not the pool service one
                    # player.composite_rank = player_data["composite_value"]

        db.commit()
        print(f"✅ Divided players into {len(pools)} pools")

        # Show top players
        print("\nTop Players by Position:")
        for position in ["QB", "RB", "WR", "TE", "K", "DEF"]:
            print(f"\n{position}:")
            top_players = (
                db.query(Player)
                .filter(Player.position == position)
                .order_by(Player.composite_rank)
                .limit(5)
                .all()
            )

            for i, p in enumerate(top_players):
                print(
                    f"  {i+1}. {p.full_name[:25]:25} ({p.team}) - Rank: {p.composite_rank:.1f}"
                )

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        await sleeper_api.close()


if __name__ == "__main__":
    asyncio.run(fix_player_rankings())
