from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Player
from app.services.sleeper_api import sleeper_api
from app.services.pool_division import PoolDivisionService
import uuid

router = APIRouter()

@router.post("/sync")
async def sync_players(db: Session = Depends(get_db)):
    """Sync all players from Sleeper API"""
    try:
        players_data = await sleeper_api.get_all_players()
        
        active_players = []
        for sleeper_id, player_data in players_data.items():
            if player_data.get("active") and player_data.get("position") in ["QB", "RB", "WR", "TE", "K", "DEF"]:
                player = Player(
                    id=str(uuid.uuid4()),
                    sleeper_id=sleeper_id,
                    first_name=player_data.get("first_name", ""),
                    last_name=player_data.get("last_name", ""),
                    full_name=player_data.get("full_name", ""),
                    team=player_data.get("team", ""),
                    position=player_data.get("position", ""),
                    fantasy_positions=player_data.get("fantasy_positions", []),
                    age=player_data.get("age"),
                    status=player_data.get("status", ""),
                    metadata_json=player_data
                )
                
                existing = db.query(Player).filter_by(sleeper_id=sleeper_id).first()
                if existing:
                    for key, value in player.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing, key, value)
                else:
                    db.add(player)
                    active_players.append(player)
        
        db.commit()
        return {"message": f"Synced {len(active_players)} players"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/divide-pools")
async def divide_player_pools(db: Session = Depends(get_db)):
    """Divide all players into 6 equal-value pools"""
    players = db.query(Player).filter(Player.position.in_(["QB", "RB", "WR", "TE", "K", "DEF"])).all()
    
    if len(players) < 192:
        raise HTTPException(status_code=400, detail="Not enough players to create pools")
    
    players_dict = []
    for player in players:
        players_dict.append({
            "id": player.id,
            "position": player.position,
            "sleeper_rank": player.sleeper_rank or 999,
            "espn_rank": player.espn_rank or 999,
            "yahoo_rank": player.yahoo_rank or 999
        })
    
    pool_service = PoolDivisionService()
    pools, pool_values = pool_service.divide_players_into_pools(players_dict)
    validation = pool_service.validate_pool_balance(pools, pool_values)
    
    for pool_idx, pool_players in pools.items():
        for player_data in pool_players:
            player = db.query(Player).filter_by(id=player_data["id"]).first()
            if player:
                player.pool_assignment = pool_idx
                player.composite_rank = player_data["composite_value"]
    
    db.commit()
    
    return {
        "pools_created": len(pools),
        "validation": validation,
        "pool_sizes": {idx: len(players) for idx, players in pools.items()}
    }

@router.get("/")
async def get_players(
    position: Optional[str] = None,
    pool: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get players with optional filters"""
    query = db.query(Player)
    
    if position:
        query = query.filter(Player.position == position)
    if pool is not None:
        query = query.filter(Player.pool_assignment == pool)
    
    players = query.order_by(Player.composite_rank).limit(limit).all()
    return players

@router.get("/pools/{pool_number}")
async def get_pool_players(pool_number: int, db: Session = Depends(get_db)):
    """Get all players in a specific pool"""
    players = db.query(Player).filter(Player.pool_assignment == pool_number).order_by(Player.position, Player.composite_rank).all()
    
    if not players:
        raise HTTPException(status_code=404, detail=f"Pool {pool_number} not found")
    
    return {
        "pool": pool_number,
        "total_players": len(players),
        "players": players
    }