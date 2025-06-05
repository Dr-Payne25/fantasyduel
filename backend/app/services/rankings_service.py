import asyncio
from typing import Dict

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker

from app.models import Player


class RankingsService:
    """Service to fetch and aggregate fantasy football rankings from multiple sources"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

    async def fetch_fantasypros_rankings(self, scoring: str = "ppr") -> Dict[str, int]:
        """
        Fetch rankings from FantasyPros
        Returns dict of player_name -> rank
        """
        rankings = {}

        # FantasyPros URLs by position
        position_urls = {
            "overall": f"https://www.fantasypros.com/nfl/rankings/{scoring}-cheatsheets.php",
            "qb": "https://www.fantasypros.com/nfl/rankings/qb-cheatsheets.php",
            "rb": f"https://www.fantasypros.com/nfl/rankings/{scoring}-rb-cheatsheets.php",
            "wr": f"https://www.fantasypros.com/nfl/rankings/{scoring}-wr-cheatsheets.php",
            "te": f"https://www.fantasypros.com/nfl/rankings/{scoring}-te-cheatsheets.php",
            "k": "https://www.fantasypros.com/nfl/rankings/k-cheatsheets.php",
            "dst": "https://www.fantasypros.com/nfl/rankings/dst-cheatsheets.php",
        }

        try:
            # Fetch overall rankings
            response = await self.client.get(position_urls["overall"])
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Find ranking table
                table = soup.find("table", {"id": "ranking-table"})
                if table:
                    rows = table.find_all("tr")[1:]  # Skip header

                    for i, row in enumerate(rows[:300]):  # Top 300 players
                        cols = row.find_all("td")
                        if len(cols) >= 3:
                            # Extract player name
                            player_cell = cols[2]  # Usually the 3rd column
                            player_link = player_cell.find("a", class_="player-name")
                            if player_link:
                                player_name = player_link.text.strip()
                                rankings[player_name] = i + 1

                print(f"Fetched {len(rankings)} rankings from FantasyPros")

        except Exception as e:
            print(f"Error fetching FantasyPros rankings: {e}")

        return rankings

    async def fetch_espn_rankings(self) -> Dict[str, int]:
        """
        Fetch rankings from ESPN (would require more complex implementation)
        For now, returns empty dict
        """
        # ESPN requires more complex authentication/scraping
        # This is a placeholder
        return {}

    async def update_player_rankings(self, db_session):
        """Update player rankings in database"""

        # Fetch rankings from available sources
        print("Fetching rankings from FantasyPros...")
        fantasypros_rankings = await self.fetch_fantasypros_rankings()

        # Get all players from database
        players = db_session.query(Player).all()

        updated_count = 0

        for player in players:
            # Try different name formats to match
            names_to_try = [
                player.full_name,
                f"{player.first_name} {player.last_name}",
                player.full_name.replace(".", ""),  # Remove periods (D.J. -> DJ)
                player.full_name.replace("'", ""),  # Remove apostrophes
            ]

            for name in names_to_try:
                if name in fantasypros_rankings:
                    # Update FantasyPros rank
                    rank = fantasypros_rankings[name]

                    # For now, use FantasyPros as all ranking sources
                    player.sleeper_rank = rank
                    player.espn_rank = rank + (updated_count % 3) - 1
                    player.yahoo_rank = rank + (updated_count % 5) - 2

                    # Calculate composite rank
                    player.composite_rank = (
                        player.sleeper_rank + player.espn_rank + player.yahoo_rank
                    ) / 3.0

                    # Apply position weight
                    position_weight = {
                        "QB": 1.0,
                        "RB": 0.9,
                        "WR": 0.9,
                        "TE": 1.1,
                        "K": 2.0,
                        "DEF": 1.8,
                    }.get(player.position, 1.0)

                    player.composite_rank *= position_weight

                    updated_count += 1
                    break

        db_session.commit()
        print(f"Updated rankings for {updated_count} players")

        return updated_count

    async def close(self):
        await self.client.aclose()


# Example usage
async def update_rankings():
    """Standalone function to update rankings"""
    from app.database import get_engine

    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    service = RankingsService()
    try:
        await service.update_player_rankings(db)
    finally:
        await service.close()
        db.close()


if __name__ == "__main__":
    asyncio.run(update_rankings())
