from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import schemas
from app.models import models
from datetime import datetime

router = APIRouter()

@router.post("/snapshots", status_code=201)
def create_snapshot(
    payload: schemas.SnapshotCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Handles point-in-time snapshots from the CV client.
    Stores numerical scores for dashboarding and the full raw JSON for backup.
    """
    # 1. Ensure session exists
    session = db.query(models.WorkSession).filter(models.WorkSession.id == payload.session_id).first()
    if not session:
        # Auto-create session if not exists (useful for Edge robustness)
        session = models.WorkSession(id=payload.session_id, is_active=True)
        db.add(session)
        db.commit()
    
    # 2. Create Snapshot
    db_snapshot = models.Snapshot(
        session_id=payload.session_id,
        work_mode=payload.work_mode,
        attention_score=payload.scores.get("attention_score", 0),
        posture_score=payload.scores.get("posture_score", 0),
        vigilance_score=payload.scores.get("vigilance_score", 0),
        stress_risk_score=payload.scores.get("stress_risk_score", 0),
        global_focus_score=payload.scores.get("focus_score_global", 0),
        raw_payload_json=payload.model_dump()
    )
    
    db.add(db_snapshot)
    db.commit()
    return {"status": "ok", "id": db_snapshot.id}

@router.post("/events", status_code=201)
def create_event(
    payload: schemas.EventCreate,
    db: Session = Depends(deps.get_db)
):
    """Handles discrete events (alerts, mode changes)."""
    db_event = models.Event(
        session_id=payload.session_id,
        event_type=payload.event_type,
        level=payload.level,
        description=payload.description,
        raw_payload_json=payload.metadata
    )
    db.add(db_event)
    db.commit()
    return {"status": "ok", "id": db_event.id}
