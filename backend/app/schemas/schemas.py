from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# --- VISION / MONITORING SCHEMAS ---

class SnapshotCreate(BaseModel):
    session_id: str
    timestamp: str # ISO format
    work_mode: str
    scores: dict
    presence: dict
    instant_observations: dict
    short_window_inference: dict
    consolidated_states: dict
    reliability: dict
    temporal_context: dict
    alert: dict
    events: List[Any] = []

class EventCreate(BaseModel):
    session_id: str
    timestamp: str
    event_type: str
    level: str
    description: str
    metadata: Optional[dict] = {}

class WorkSessionCreate(BaseModel):
    id: str # UUID from client
    start_time: Optional[datetime] = None
    metadata_json: Optional[dict] = None

class Event(BaseModel):
    id: int
    session_id: str
    timestamp: datetime
    event_type: str
    level: str
    description: str

    class Config:
        from_attributes = True

class WorkSession(BaseModel):
    id: str
    user_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool
    metadata_json: Optional[dict] = None

    class Config:
        from_attributes = True

# Settings Schemas
class SettingsBase(BaseModel):
    focus_duration: int
    break_duration: int

class SettingsUpdate(BaseModel):
    focus_duration: Optional[int] = None
    break_duration: Optional[int] = None

class Settings(SettingsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
