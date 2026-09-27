"""Database models: student accounts and their reading session history."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("ReadingSession", back_populates="user")


class ReadingSession(Base):
    __tablename__ = "reading_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_text = Column(Text, nullable=False)
    wpm = Column(Float)
    accuracy = Column(Float)
    risk_score = Column(Float)
    risk_band = Column(String)
    next_exercise = Column(String)
    error_rates_json = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="sessions")