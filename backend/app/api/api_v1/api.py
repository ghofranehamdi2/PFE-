from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, sessions, events, settings, vision

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(vision.router, prefix="/vision", tags=["vision"])
