from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud
from app.schemas import schemas
from app.models import models

router = APIRouter()

@router.get("/", response_model=schemas.Settings)
def read_settings(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    return current_user.settings

@router.put("/", response_model=schemas.Settings)
def update_settings(
    *,
    db: Session = Depends(deps.get_db),
    settings_in: schemas.SettingsUpdate,
    current_user: models.User = Depends(deps.get_current_user)
):
    db_obj = current_user.settings
    obj_data = settings_in.dict(exclude_unset=True)
    for field in obj_data:
        setattr(db_obj, field, obj_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
