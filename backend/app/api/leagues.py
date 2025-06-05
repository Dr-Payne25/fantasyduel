import random
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import DraftPair, League, LeagueUser, User

router = APIRouter()


@router.get("/my-leagues")
async def get_my_leagues(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get all leagues the current user is in"""
    # Get all league memberships for the user
    league_users = db.query(LeagueUser).filter_by(user_id=current_user.id).all()

    # Get the league details for each membership
    user_leagues = []
    for lu in league_users:
        league = db.query(League).filter_by(id=lu.league_id).first()
        if league:
            # Get user count for each league
            user_count = db.query(LeagueUser).filter_by(league_id=league.id).count()

            # Check if user has an active draft
            from app.models import Draft

            active_draft = None
            if lu.pair_id:
                draft = (
                    db.query(Draft)
                    .filter_by(pair_id=lu.pair_id, status="active")
                    .first()
                )
                if draft:
                    active_draft = {"id": draft.id, "status": draft.status}

            user_leagues.append(
                {
                    "league": league,
                    "user_count": user_count,
                    "my_pair_id": lu.pair_id,
                    "active_draft": active_draft,
                    "is_commissioner": league.commissioner_id == current_user.id,
                }
            )

    return user_leagues


class CreateLeagueRequest(BaseModel):
    name: str
    commissioner_name: str
    commissioner_email: str


class JoinLeagueRequest(BaseModel):
    league_id: str
    user_name: str
    email: str


@router.post("/create")
async def create_league(
    request: CreateLeagueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new league"""
    league = League(
        id=str(uuid.uuid4()),
        name=request.name,
        commissioner_id=current_user.id,
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
    )
    db.add(league)

    commissioner = LeagueUser(
        league_id=league.id,
        user_id=current_user.id,
        email=current_user.email,
        display_name=request.commissioner_name or current_user.username,
    )
    db.add(commissioner)

    db.commit()
    return {"league": league, "invite_code": league.id}


@router.post("/join")
async def join_league(
    request: JoinLeagueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Join an existing league"""
    league = db.query(League).filter_by(id=request.league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    # Check if current user is already in the league
    existing_user = (
        db.query(LeagueUser)
        .filter_by(league_id=league.id, user_id=current_user.id)
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="You are already in this league")

    current_users = db.query(LeagueUser).filter_by(league_id=league.id).count()
    if current_users >= 12:
        raise HTTPException(status_code=400, detail="League is full")

    user = LeagueUser(
        league_id=league.id,
        user_id=current_user.id,
        email=current_user.email,
        display_name=request.user_name or current_user.username,
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
        raise HTTPException(
            status_code=400,
            detail=f"League needs exactly 12 users, currently has {len(users)}",
        )

    existing_pairs = db.query(DraftPair).filter_by(league_id=league_id).count()
    if existing_pairs > 0:
        raise HTTPException(status_code=400, detail="Draft pairs already created")

    random.shuffle(users)

    pairs_created = []
    for i in range(6):
        pair = DraftPair(league_id=league_id, pool_number=i, draft_order=i)
        db.add(pair)
        db.flush()

        users[i * 2].pair_id = pair.id
        users[i * 2 + 1].pair_id = pair.id

        pairs_created.append(
            {
                "pair_id": pair.id,
                "pool_number": i,
                "users": [users[i * 2].display_name, users[i * 2 + 1].display_name],
            }
        )

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

    # Get drafts for each pair
    from app.models import Draft

    drafts = {}
    for pair in pairs:
        draft = db.query(Draft).filter_by(pair_id=pair.id).first()
        if draft:
            drafts[pair.id] = {
                "id": draft.id,
                "status": draft.status,
                "started_at": (
                    draft.started_at.isoformat() if draft.started_at else None
                ),
            }

    return {
        "league": league,
        "users": users,
        "pairs": pairs,
        "drafts": drafts,
        "user_count": len(users),
    }
