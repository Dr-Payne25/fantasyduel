from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class League(Base):
    __tablename__ = "leagues"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    commissioner_id = Column(String, nullable=False)
    status = Column(String, default="setup")
    settings = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    draft_start_time = Column(DateTime(timezone=True))

    users = relationship("LeagueUser", back_populates="league")
    draft_pairs = relationship("DraftPair", back_populates="league")


class LeagueUser(Base):
    __tablename__ = "league_users"

    id = Column(Integer, primary_key=True)
    league_id = Column(String, ForeignKey("leagues.id"))
    user_id = Column(String, ForeignKey("users.id"))
    email = Column(String)  # Keep for backward compatibility
    display_name = Column(String, nullable=False)
    pair_id = Column(Integer, ForeignKey("draft_pairs.id"))

    league = relationship("League", back_populates="users")
    pair = relationship("DraftPair", back_populates="users")
    user = relationship("User")


class DraftPair(Base):
    __tablename__ = "draft_pairs"

    id = Column(Integer, primary_key=True)
    league_id = Column(String, ForeignKey("leagues.id"))
    pool_number = Column(Integer, nullable=False)
    draft_order = Column(Integer)

    league = relationship("League", back_populates="draft_pairs")
    users = relationship("LeagueUser", back_populates="pair")
    draft = relationship("Draft", uselist=False, back_populates="pair")
