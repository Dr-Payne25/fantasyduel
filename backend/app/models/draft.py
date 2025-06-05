from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(String, primary_key=True)
    pair_id = Column(Integer, ForeignKey("draft_pairs.id"))
    status = Column(String, default="not_started")
    current_picker_id = Column(String)
    pick_timer_seconds = Column(Integer, default=90)

    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    pair = relationship("DraftPair", back_populates="draft")
    picks = relationship(
        "DraftPick", back_populates="draft", order_by="DraftPick.pick_number"
    )


class DraftPick(Base):
    __tablename__ = "draft_picks"

    id = Column(Integer, primary_key=True)
    draft_id = Column(String, ForeignKey("drafts.id"))
    pick_number = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False)
    player_id = Column(String, ForeignKey("players.id"))

    picked_at = Column(DateTime(timezone=True), server_default=func.now())

    draft = relationship("Draft", back_populates="picks")
    player = relationship("Player")
