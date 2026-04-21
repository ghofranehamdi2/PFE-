from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from app.api import deps
from app.crud import crud
from app.schemas import schemas
from app.models import models

router = APIRouter()

@router.post("/", response_model=schemas.WorkSession)
def create_session(
    payload: schemas.WorkSessionCreate,
    db: Session = Depends(deps.get_db)
):
    """Initializes a new session (called by CV client)."""
    db_session = db.query(models.WorkSession).filter(models.WorkSession.id == payload.id).first()
    if db_session:
        return db_session
    
    db_session = models.WorkSession(
        id=payload.id,
        start_time=payload.start_time or datetime.utcnow(),
        metadata_json=payload.metadata_json
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/", response_model=List[schemas.WorkSession])
def list_sessions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    return db.query(models.WorkSession).offset(skip).limit(limit).all()

@router.get("/{session_id}/latest")
def get_latest_snapshot(
    session_id: str,
    db: Session = Depends(deps.get_db)
):
    return db.query(models.Snapshot).filter(models.Snapshot.session_id == session_id).order_by(models.Snapshot.timestamp.desc()).first()


@router.post("/{session_id}/finalize", response_model=schemas.WorkSession)
def finalize_session(
    session_id: str,
    summary: Dict[str, Any] = Body(...),
    db: Session = Depends(deps.get_db),
):
    """Close a session and persist the final summary in metadata_json."""
    db_session = db.query(models.WorkSession).filter(models.WorkSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    merged_metadata = dict(db_session.metadata_json or {})
    merged_metadata.update(dict(summary or {}))

    db_session.metadata_json = merged_metadata
    flag_modified(db_session, "metadata_json")
    db_session.end_time = datetime.utcnow()
    db_session.is_active = False

    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session
