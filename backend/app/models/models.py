from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Enum, JSON
from sqlalchemy.orm import relationship
import datetime
import enum
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)

    sessions = relationship("WorkSession", back_populates="user")
    settings = relationship("Settings", back_populates="user", uselist=False)

class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(String, primary_key=True, index=True) # UUID from client
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    metadata_json = Column(JSON, nullable=True)

    user = relationship("User", back_populates="sessions")
    snapshots = relationship("Snapshot", back_populates="session", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")

class Snapshot(Base):
    """Point-in-time state of the user (Levels 1-4 + Scores)."""
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("work_sessions.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Primary fields for quick indexing/dashboarding
    work_mode = Column(String)
    attention_score = Column(Float)
    posture_score = Column(Float)
    vigilance_score = Column(Float)
    stress_risk_score = Column(Float)
    global_focus_score = Column(Float)
    
    # Full rich data
    raw_payload_json = Column(JSON)

    session = relationship("WorkSession", back_populates="snapshots")

class Event(Base):
    """Significant discrete behavioral events or alerts."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("work_sessions.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    event_type = Column(String) # 'alert', 'task_change', 'manual_tag'
    level = Column(String) # 'info', 'warning', 'critical'
    description = Column(String)
    
    raw_payload_json = Column(JSON, nullable=True)

    session = relationship("WorkSession", back_populates="events")

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    focus_duration = Column(Integer, default=25) 
    break_duration = Column(Integer, default=5)
    
    user = relationship("User", back_populates="settings")
