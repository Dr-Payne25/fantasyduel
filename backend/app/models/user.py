from app.database import Base
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Settings
    notification_preferences = Column(String, default="all")  # all, important, none
    theme = Column(String, default="dark")

    # OAuth fields (for future)
    oauth_provider = Column(String)  # google, github, etc
    oauth_id = Column(String)
