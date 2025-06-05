from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Player

engine = create_engine("sqlite:///./fantasyduel.db")
Session = sessionmaker(bind=engine)
db = Session()

# Get sample players from each position
print("Sample Player Rankings:\n")

for position in ["QB", "RB", "WR", "TE", "K", "DEF"]:
    print(f"\n{position}s:")
    players = (
        db.query(Player)
        .filter(
            Player.position == position,
            Player.pool_assignment == 0,  # Pool 0 for this draft
        )
        .order_by(Player.composite_rank)
        .limit(10)
        .all()
    )

    for i, player in enumerate(players):
        print(
            f"{i+1}. {player.full_name[:25]:25} - Composite: {player.composite_rank:6.1f}, "
            f"Sleeper: {player.sleeper_rank or 999:3d}, "
            f"ESPN: {player.espn_rank or 999:3d}, "
            f"Yahoo: {player.yahoo_rank or 999:3d}"
        )

# Check for issues
print("\n\nChecking for ranking issues:")
# Check for null composite ranks
null_composite = db.query(Player).filter(Player.composite_rank.is_(None)).count()
print(f"Players with NULL composite rank: {null_composite}")

# Check for unrealistic rankings
weird_ranks = (
    db.query(Player)
    .filter((Player.composite_rank < 1) | (Player.composite_rank > 500))
    .count()
)
print(f"Players with weird composite ranks (<1 or >500): {weird_ranks}")

db.close()
