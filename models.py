from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from database import Base
from datetime import datetime, timezone

class DBUser (Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)          #first parameter is fixed e.g. datatype, others are priority wise
    name = Column(String)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    hashed_password = Column(String)
    role = Column (String, default="user")
    bio = Column (String, nullable=True)
    avatar_filename = Column (String, nullable=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token_fingerprint = Column(String, unique=True, index=True)
    revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))