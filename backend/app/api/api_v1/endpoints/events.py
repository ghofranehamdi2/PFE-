from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud
from app.schemas import schemas
from app.models import models

router = APIRouter()

@router.post("/ingest", response_model=schemas.Event)
def ingest_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: schemas.EventCreate,
    current_user: models.User = Depends(deps.get_current_user)
):
    active_session = crud.session.get_active(db, user_id=current_user.id)
    if not active_session:
        # Auto-start a session if none exists? (Optional decision)
        active_session = crud.session.create(db, user_id=current_user.id)
    
    return crud.event.create(db, obj_in=event_in, session_id=active_session.id)
