from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
import datetime
import uuid

class CRUDUser:
    def get_by_email(self, db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    def create(self, db: Session, obj_in: schemas.UserCreate):
        db_obj = models.User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Create default settings for new user
        default_settings = models.Settings(user_id=db_obj.id)
        db.add(default_settings)
        db.commit()
        
        return db_obj

class CRUDSession:
    def create(self, db: Session, user_id: int = None, session_id: str = None):
        # Close any existing active sessions if a user_id is provided
        if user_id:
            db.query(models.WorkSession).filter(
                models.WorkSession.user_id == user_id, 
                models.WorkSession.is_active == True
            ).update({"is_active": False, "end_time": datetime.datetime.utcnow()})
        
        real_id = session_id or str(uuid.uuid4())
        db_obj = models.WorkSession(id=real_id, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_active(self, db: Session, user_id: int):
        return db.query(models.WorkSession).filter(
            models.WorkSession.user_id == user_id, 
            models.WorkSession.is_active == True
        ).first()

    def end_session(self, db: Session, session_id: str):
        db_obj = db.query(models.WorkSession).filter(models.WorkSession.id == session_id).first()
        if db_obj:
            db_obj.is_active = False
            db_obj.end_time = datetime.datetime.utcnow()
            db.commit()
            db.refresh(db_obj)
        return db_obj

class CRUDEvent:
    def create(self, db: Session, obj_in: schemas.EventCreate, session_id: str):
        db_obj = models.Event(
            session_id=session_id,
            event_type=obj_in.event_type,
            level=obj_in.level,
            description=obj_in.description,
            raw_payload_json=obj_in.metadata
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser()
session = CRUDSession()
event = CRUDEvent()
