from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Player

engine = create_engine("sqlite:///./fantasyduel.db")
Session = sessionmaker(bind=engine)
db = Session()

print("🏈 TOP 5 PLAYERS BY POSITION FOR DRAFT\n")
print("=" * 60)

positions = ["QB", "RB", "WR", "TE", "K", "DEF"]

for position in positions:
    print(f"\n{position}s:")
    print("-" * 40)

    # Get top 5 players for this position
    top_players = (
        db.query(Player)
        .filter(Player.position == position)
        .order_by(Player.composite_rank)
        .limit(5)
        .all()
    )

    for i, player in enumerate(top_players, 1):
        # Format team and age info
        team_info = f"({player.team})" if player.team else "(FA)"
        age_info = f"Age {player.age}" if player.age else ""

        # Build the info string
        info_parts = [team_info]
        if age_info:
            info_parts.append(age_info)
        info_str = " - ".join(info_parts)

        print(
            f"{i}. {player.full_name:25} {info_str:20} Overall Rank: {player.composite_rank:.1f}"
        )

print("\n" + "=" * 60)
print("Note: Rankings are based on composite scores from multiple sources")

db.close()
