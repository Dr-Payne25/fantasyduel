from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import League, LeagueUser, DraftPair
from pydantic import BaseModel
import uuid
import random

router = APIRouter()

class CreateLeagueRequest(BaseModel):
    name: str
    commissioner_name: str
    commissioner_email: str

class JoinLeagueRequest(BaseModel):
    league_id: str
    user_name: str
    email: str

@router.post("/create")
async def create_league(request: CreateLeagueRequest, db: Session = Depends(get_db)):
    """Create a new league"""
    league = League(
        id=str(uuid.uuid4()),
        name=request.name,
        commissioner_id=str(uuid.uuid4()),
        settings={
            "roster_spots": {
                "QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DEF": 1, "BENCH": 6
            },
            "scoring": "PPR"
        }
    )
    db.add(league)
    
    commissioner = LeagueUser(
        league_id=league.id,
        user_id=league.commissioner_id,
        email=request.commissioner_email,
        display_name=request.commissioner_name
    )
    db.add(commissioner)
    
    db.commit()
    return {"league": league, "invite_code": league.id}

@router.post("/join")
async def join_league(request: JoinLeagueRequest, db: Session = Depends(get_db)):
    """Join an existing league"""
    league = db.query(League).filter_by(id=request.league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    current_users = db.query(LeagueUser).filter_by(league_id=league.id).count()
    if current_users >= 12:
        raise HTTPException(status_code=400, detail="League is full")
    
    user = LeagueUser(
        league_id=league.id,
        user_id=str(uuid.uuid4()),
        email=request.email,
        display_name=request.user_name
    )
    db.add(user)
    db.commit()
    
    return {"message": "Successfully joined league", "user": user}

@router.post("/{league_id}/create-pairs")
async def create_draft_pairs(league_id: str, db: Session = Depends(get_db)):
    """Create draft pairs for the league"""
    league = db.query(League).filter_by(id=league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    users = db.query(LeagueUser).filter_by(league_id=league_id).all()
    if len(users) != 12:
        raise HTTPException(status_code=400, detail=f"League needs exactly 12 users, currently has {len(users)}")
    
    existing_pairs = db.query(DraftPair).filter_by(league_id=league_id).count()
    if existing_pairs > 0:
        raise HTTPException(status_code=400, detail="Draft pairs already created")
    
    random.shuffle(users)
    
    pairs_created = []
    for i in range(6):
        pair = DraftPair(
            league_id=league_id,
            pool_number=i,
            draft_order=i
        )
        db.add(pair)
        db.flush()
        
        users[i * 2].pair_id = pair.id
        users[i * 2 + 1].pair_id = pair.id
        
        pairs_created.append({
            "pair_id": pair.id,
            "pool_number": i,
            "users": [users[i * 2].display_name, users[i * 2 + 1].display_name]
        })
    
    league.status = "draft_ready"
    db.commit()
    
    return {"message": "Draft pairs created", "pairs": pairs_created}

@router.get("/{league_id}")
async def get_league(league_id: str, db: Session = Depends(get_db)):
    """Get league details"""
    league = db.query(League).filter_by(id=league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    users = db.query(LeagueUser).filter_by(league_id=league_id).all()
    pairs = db.query(DraftPair).filter_by(league_id=league_id).all()
    
    return {
        "league": league,
        "users": users,
        "pairs": pairs,
        "user_count": len(users)
    }