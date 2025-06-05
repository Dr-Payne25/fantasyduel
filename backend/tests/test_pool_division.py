"""
Test pool division service
"""

import pytest
from app.services.pool_division import PoolDivisionService


class TestPoolDivisionService:
    """Test the pool division algorithm"""

    @pytest.fixture
    def sample_player_data(self):
        """Create sample player data for testing"""
        players = []
        positions = ["QB", "RB", "WR", "TE", "K", "DEF"]

        # Create more players than minimum requirements
        # QB: 30, RB: 70, WR: 70, TE: 30, K: 20, DEF: 20 (240 total)
        player_counts = {"QB": 30, "RB": 70, "WR": 70, "TE": 30, "K": 20, "DEF": 20}

        rank = 1
        for position, count in player_counts.items():
            for i in range(count):
                player = {
                    "id": f"{position}_{i}",
                    "position": position,
                    "sleeper_rank": rank,
                    "espn_rank": rank + 5,
                    "yahoo_rank": rank - 3,
                }
                players.append(player)
                rank += 1

        return players

    @pytest.mark.unit
    def test_pool_division_creates_six_pools(self, sample_player_data):
        """Test that exactly 6 pools are created"""
        service = PoolDivisionService(num_pools=6)
        pools, _ = service.divide_players_into_pools(sample_player_data)

        assert len(pools) == 6
        assert all(pool_idx in pools for pool_idx in range(6))

    @pytest.mark.unit
    def test_pool_division_distributes_all_players(self, sample_player_data):
        """Test that all players are distributed to pools"""
        service = PoolDivisionService()
        pools, _ = service.divide_players_into_pools(sample_player_data)

        total_players = sum(len(pool) for pool in pools.values())
        assert total_players == len(sample_player_data)

        # Verify each player appears exactly once
        player_ids = set()
        for pool in pools.values():
            for player in pool:
                assert player["id"] not in player_ids
                player_ids.add(player["id"])

    @pytest.mark.unit
    def test_pool_division_position_requirements(self, sample_player_data):
        """Test that each pool meets position requirements"""
        service = PoolDivisionService()
        pools, _ = service.divide_players_into_pools(sample_player_data)

        for pool_idx, players in pools.items():
            position_counts = {}
            for player in players:
                pos = player["position"]
                position_counts[pos] = position_counts.get(pos, 0) + 1

            # Check minimum requirements
            assert position_counts.get("QB", 0) >= 4
            assert position_counts.get("RB", 0) >= 10
            assert position_counts.get("WR", 0) >= 10
            assert position_counts.get("TE", 0) >= 4
            assert position_counts.get("K", 0) >= 2
            assert position_counts.get("DEF", 0) >= 2

    @pytest.mark.unit
    def test_pool_division_value_balance(self, sample_player_data):
        """Test that pools are balanced in value"""
        service = PoolDivisionService()
        pools, pool_values = service.divide_players_into_pools(sample_player_data)

        # Calculate average value
        avg_value = sum(pool_values.values()) / len(pool_values)

        # Check that no pool deviates more than 5% from average
        for pool_idx, value in pool_values.items():
            deviation = abs(value - avg_value) / avg_value
            assert (
                deviation <= 0.05
            ), f"Pool {pool_idx} value deviation: {deviation:.2%}"

    @pytest.mark.unit
    def test_pool_division_snake_draft(self, sample_player_data):
        """Test that snake draft order is used for fairness"""
        service = PoolDivisionService()
        pools, _ = service.divide_players_into_pools(sample_player_data)

        # Check QBs (first position) - should follow snake pattern
        qb_by_pool = {i: [] for i in range(6)}
        for pool_idx, players in pools.items():
            for player in players:
                if player["position"] == "QB":
                    qb_by_pool[pool_idx].append(player)

        # Each pool should have QBs
        assert all(len(qbs) > 0 for qbs in qb_by_pool.values())

    @pytest.mark.unit
    def test_calculate_player_value(self):
        """Test player value calculation"""
        service = PoolDivisionService()

        # Test with all rankings
        player1 = {
            "position": "QB",
            "sleeper_rank": 10,
            "espn_rank": 12,
            "yahoo_rank": 8,
        }
        value1 = service.calculate_player_value(player1)
        avg_rank = (10 + 12 + 8) / 3  # 10
        expected = avg_rank * 1.2  # QB multiplier
        assert value1 == expected

        # Test with missing rankings
        player2 = {
            "position": "RB",
            "sleeper_rank": 20,
            "espn_rank": None,
            "yahoo_rank": None,
        }
        value2 = service.calculate_player_value(player2)
        assert value2 == 20.0  # Only sleeper rank, RB multiplier is 1.0

        # Test with no rankings
        player3 = {"position": "WR"}
        value3 = service.calculate_player_value(player3)
        assert value3 == 999.0  # Default value

    @pytest.mark.unit
    def test_validate_pool_balance(self, sample_player_data):
        """Test pool balance validation"""
        service = PoolDivisionService()
        pools, pool_values = service.divide_players_into_pools(sample_player_data)

        validation = service.validate_pool_balance(pools, pool_values)

        assert validation["balanced"] is True
        assert len(validation["pool_stats"]) == 6
        assert len(validation["warnings"]) == 0

        # Check pool stats
        for pool_idx, stats in validation["pool_stats"].items():
            assert "total_players" in stats
            assert "total_value" in stats
            assert "value_deviation" in stats
            assert "positions" in stats
