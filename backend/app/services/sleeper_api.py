import httpx
from typing import List, Dict, Optional
from app.config import get_settings
import asyncio
from datetime import datetime

settings = get_settings()


class SleeperAPI:
    def __init__(self):
        self.base_url = settings.sleeper_api_base
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_all_players(self) -> Dict[str, Dict]:
        """Fetch all NFL players from Sleeper API"""
        url = f"{self.base_url}/players/nfl"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_trending_players(
        self, sport: str = "nfl", type: str = "add", hours: int = 24, limit: int = 100
    ) -> List[Dict]:
        """Get trending players based on adds/drops"""
        url = f"{self.base_url}/players/{sport}/trending/{type}"
        params = {"lookback_hours": hours, "limit": limit}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_projections(
        self, season: int, week: int, positions: Optional[List[str]] = None
    ) -> Dict:
        """Get player projections for a specific week"""
        # Note: Sleeper doesn't provide projections via API, this is a placeholder
        # You'd need to integrate with another source or use historical data
        return {}

    async def close(self):
        await self.client.aclose()


sleeper_api = SleeperAPI()
