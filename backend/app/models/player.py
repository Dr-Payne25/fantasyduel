from app.database import Base
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func


class Player(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True)
    sleeper_id = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    full_name = Column(String)
    team = Column(String)
    position = Column(String, index=True)
    fantasy_positions = Column(JSON)
    age = Column(Integer)
    status = Column(String)

    composite_rank = Column(Float)
    sleeper_rank = Column(Integer)
    espn_rank = Column(Integer)
    yahoo_rank = Column(Integer)

    pool_assignment = Column(Integer, index=True)

    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
