import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Draft, DraftPair, DraftPick, LeagueUser, Player
from app.schemas import DraftBase, DraftPickBase, LeagueUserBase, PlayerBase

router = APIRouter()


class StartDraftRequest(BaseModel):
    pair_id: int


class MakePickRequest(BaseModel):
    draft_id: str
    user_id: str
    player_id: str


@router.post("/start")
async def start_draft(request: StartDraftRequest, db: Session = Depends(get_db)):
    """Start a draft for a pair"""
    pair = db.query(DraftPair).filter_by(id=request.pair_id).first()
    if not pair:
        raise HTTPException(status_code=404, detail="Draft pair not found")

    existing_draft = db.query(Draft).filter_by(pair_id=pair.id).first()
    if existing_draft:
        raise HTTPException(
            status_code=400, detail="Draft already exists for this pair"
        )

    users = db.query(LeagueUser).filter_by(pair_id=pair.id).all()
    if len(users) != 2:
        raise HTTPException(status_code=400, detail="Pair must have exactly 2 users")

    draft = Draft(
        id=str(uuid.uuid4()),
        pair_id=pair.id,
        status="active",
        current_picker_id=users[0].user_id,
        started_at=datetime.now(timezone.utc),
    )
    db.add(draft)
    db.commit()

    return {
        "draft": {
            "id": draft.id,
            "pair_id": draft.pair_id,
            "status": draft.status,
            "current_picker_id": draft.current_picker_id,
            "started_at": (draft.started_at.isoformat() if draft.started_at else None),
        },
        "users": [{"id": u.user_id, "name": u.display_name} for u in users],
        "pool_number": pair.pool_number,
    }


@router.post("/pick")
async def make_pick(request: MakePickRequest, db: Session = Depends(get_db)):
    """Make a draft pick"""
    draft = db.query(Draft).filter_by(id=request.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if draft.status != "active":
        raise HTTPException(status_code=400, detail="Draft is not active")

    if draft.current_picker_id != request.user_id:
        raise HTTPException(status_code=400, detail="Not your turn to pick")

    player = db.query(Player).filter_by(id=request.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    pair = db.query(DraftPair).filter_by(id=draft.pair_id).first()
    if player.pool_assignment != pair.pool_number:
        raise HTTPException(status_code=400, detail="Player not available in your pool")

    already_picked = (
        db.query(DraftPick).filter_by(draft_id=draft.id, player_id=player.id).first()
    )
    if already_picked:
        raise HTTPException(status_code=400, detail="Player already drafted")

    pick_number = db.query(DraftPick).filter_by(draft_id=draft.id).count() + 1

    pick = DraftPick(
        draft_id=draft.id,
        pick_number=pick_number,
        user_id=request.user_id,
        player_id=player.id,
    )
    db.add(pick)

    users = db.query(LeagueUser).filter_by(pair_id=draft.pair_id).all()
    other_user = next(u for u in users if u.user_id != request.user_id)
    draft.current_picker_id = other_user.user_id

    total_picks = pick_number
    max_picks = 30
    if total_picks >= max_picks:
        draft.status = "completed"
        draft.completed_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "pick": pick,
        "player": player,
        "next_picker": (draft.current_picker_id if draft.status == "active" else None),
        "draft_status": draft.status,
    }


@router.get("/{draft_id}")
async def get_draft(draft_id: str, db: Session = Depends(get_db)):
    """Get draft details with all picks"""
    draft = db.query(Draft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    picks = (
        db.query(DraftPick)
        .filter_by(draft_id=draft_id)
        .order_by(DraftPick.pick_number)
        .all()
    )
    pair = db.query(DraftPair).filter_by(id=draft.pair_id).first()
    users = db.query(LeagueUser).filter_by(pair_id=pair.id).all()

    # Get available players - handle empty picks list
    picked_player_ids = [p.player_id for p in picks] if picks else []
    if picked_player_ids:
        available_players = (
            db.query(Player)
            .filter(
                Player.pool_assignment == pair.pool_number,
                ~Player.id.in_(picked_player_ids),
            )
            .order_by(Player.composite_rank)
            .all()
        )
    else:
        available_players = (
            db.query(Player)
            .filter(Player.pool_assignment == pair.pool_number)
            .order_by(Player.composite_rank)
            .all()
        )

    return {
        "draft": DraftBase.model_validate(draft).model_dump(),
        "users": [LeagueUserBase.model_validate(u).model_dump() for u in users],
        "picks": [DraftPickBase.model_validate(p).model_dump() for p in picks],
        "available_players": [
            PlayerBase.model_validate(p).model_dump() for p in available_players
        ],
        "current_picker": draft.current_picker_id,
    }


@router.get("/{draft_id}/rosters")
async def get_draft_rosters(draft_id: str, db: Session = Depends(get_db)):
    """Get rosters for both users in the draft"""
    draft = db.query(Draft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    picks = db.query(DraftPick).filter_by(draft_id=draft_id).all()
    users = db.query(LeagueUser).filter_by(pair_id=draft.pair_id).all()

    rosters = {}
    for user in users:
        user_picks = [p for p in picks if p.user_id == user.user_id]
        rosters[user.user_id] = {
            "user": user,
            "picks": user_picks,
            "roster": {"QB": [], "RB": [], "WR": [], "TE": [], "K": [], "DEF": []},
        }

        for pick in user_picks:
            player = db.query(Player).filter_by(id=pick.player_id).first()
            if player and player.position in rosters[user.user_id]["roster"]:
                rosters[user.user_id]["roster"][player.position].append(player)

    return rosters
