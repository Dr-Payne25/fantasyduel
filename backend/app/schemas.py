from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Player schemas
class PlayerBase(BaseModel):
    id: str
    sleeper_id: str
    first_name: str
    last_name: str
    full_name: str
    team: Optional[str]
    position: str
    fantasy_positions: List[str]
    age: Optional[int]
    status: str
    composite_rank: Optional[float]
    pool_assignment: Optional[int]
    
    class Config:
        from_attributes = True

# League schemas
class LeagueUserBase(BaseModel):
    id: int
    league_id: str
    user_id: str
    email: str
    display_name: str
    pair_id: Optional[int]
    
    class Config:
        from_attributes = True

# Draft schemas
class DraftBase(BaseModel):
    id: str
    pair_id: int
    status: str
    current_picker_id: str
    pick_timer_seconds: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DraftPickBase(BaseModel):
    id: int
    draft_id: str
    pick_number: int
    user_id: str
    player_id: str
    picked_at: datetime
    player: Optional[PlayerBase] = None
    
    class Config:
        from_attributes = True