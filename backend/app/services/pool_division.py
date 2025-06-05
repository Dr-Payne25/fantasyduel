from typing import List, Dict, Tuple
from collections import defaultdict
import random
from app.models import Player

class PoolDivisionService:
    def __init__(self, num_pools: int = 6):
        self.num_pools = num_pools
        self.positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
        self.position_requirements = {
            "QB": 4,
            "RB": 10,
            "WR": 10,
            "TE": 4,
            "K": 2,
            "DEF": 2
        }
    
    def calculate_player_value(self, player: Dict) -> float:
        """Calculate composite value for a player based on multiple rankings"""
        rank_sources = []
        
        if player.get("sleeper_rank"):
            rank_sources.append(player["sleeper_rank"])
        if player.get("espn_rank"):
            rank_sources.append(player["espn_rank"])
        if player.get("yahoo_rank"):
            rank_sources.append(player["yahoo_rank"])
        
        if not rank_sources:
            return 999.0
        
        avg_rank = sum(rank_sources) / len(rank_sources)
        
        position_multiplier = {
            "QB": 1.2,
            "RB": 1.0,
            "WR": 1.0,
            "TE": 0.9,
            "K": 0.5,
            "DEF": 0.6
        }.get(player.get("position", ""), 0.8)
        
        return avg_rank * position_multiplier
    
    def divide_players_into_pools(self, players: List[Dict]) -> Dict[int, List[Dict]]:
        """Divide players into equal-value pools using a snake draft approach"""
        players_by_position = defaultdict(list)
        
        for player in players:
            if player.get("position") in self.positions:
                player["composite_value"] = self.calculate_player_value(player)
                players_by_position[player["position"]].append(player)
        
        for position in players_by_position:
            players_by_position[position].sort(key=lambda x: x["composite_value"])
        
        pools = {i: [] for i in range(self.num_pools)}
        pool_values = {i: 0.0 for i in range(self.num_pools)}
        
        for position, requirements in self.position_requirements.items():
            position_players = players_by_position.get(position, [])
            players_per_pool = requirements
            
            for tier in range(players_per_pool):
                tier_players = position_players[tier * self.num_pools:(tier + 1) * self.num_pools]
                
                if tier % 2 == 0:
                    pool_order = list(range(self.num_pools))
                else:
                    pool_order = list(range(self.num_pools - 1, -1, -1))
                
                for i, pool_idx in enumerate(pool_order):
                    if i < len(tier_players):
                        player = tier_players[i]
                        player["pool_assignment"] = pool_idx
                        pools[pool_idx].append(player)
                        pool_values[pool_idx] += player["composite_value"]
        
        remaining_players = []
        for position, position_players in players_by_position.items():
            required_count = self.position_requirements.get(position, 0) * self.num_pools
            if len(position_players) > required_count:
                remaining_players.extend(position_players[required_count:])
        
        remaining_players.sort(key=lambda x: x["composite_value"])
        pool_order = sorted(range(self.num_pools), key=lambda x: pool_values[x])
        
        for i, player in enumerate(remaining_players):
            pool_idx = pool_order[i % self.num_pools]
            player["pool_assignment"] = pool_idx
            pools[pool_idx].append(player)
            pool_values[pool_idx] += player["composite_value"]
        
        return pools, pool_values
    
    def validate_pool_balance(self, pools: Dict[int, List[Dict]], pool_values: Dict[int, float]) -> Dict:
        """Validate that pools are balanced in value and position distribution"""
        validation_results = {
            "balanced": True,
            "pool_stats": {},
            "warnings": []
        }
        
        avg_value = sum(pool_values.values()) / len(pool_values)
        max_deviation = avg_value * 0.05
        
        for pool_idx, players in pools.items():
            pool_positions = defaultdict(int)
            for player in players:
                pool_positions[player.get("position", "UNKNOWN")] += 1
            
            pool_value = pool_values[pool_idx]
            deviation = abs(pool_value - avg_value)
            
            validation_results["pool_stats"][pool_idx] = {
                "total_players": len(players),
                "total_value": pool_value,
                "value_deviation": deviation,
                "positions": dict(pool_positions)
            }
            
            if deviation > max_deviation:
                validation_results["balanced"] = False
                validation_results["warnings"].append(
                    f"Pool {pool_idx} value deviation too high: {deviation:.2f}"
                )
            
            for position, required in self.position_requirements.items():
                if pool_positions.get(position, 0) < required:
                    validation_results["warnings"].append(
                        f"Pool {pool_idx} has insufficient {position}s: {pool_positions.get(position, 0)}/{required}"
                    )
        
        return validation_results