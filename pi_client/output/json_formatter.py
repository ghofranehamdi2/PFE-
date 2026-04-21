import time

from engine.models import CVOutputPayload


class JSONFormatter:
    """Formats two outputs:

    1) Full snapshot payload for the existing backend schema (SnapshotCreate)
    2) Clean, minimal JSON frames for real application usage
    """

    @staticmethod
    def format_snapshot(payload: CVOutputPayload, scores: dict, *, clean_frame: dict | None = None) -> dict:
        """Backend-compatible snapshot payload.

        Keep the current rich schema (Levels 1–4 + scores) so the backend can
        store both numeric fields and a full raw JSON backup.

        We also embed the clean frame + numeric metrics inside `scores` so the
        backend will persist them (SnapshotCreate.scores is a free-form dict).
        """
        data = payload.model_dump()
        data["work_mode"] = payload.consolidated_states.work_mode
        
        # Explicit exposure of sub-states for backend convenience
        data["sub_states"] = {
            "fatigue": payload.consolidated_states.fatigue_state,
            "posture": payload.consolidated_states.posture_state,
            "social": payload.consolidated_states.social_state,
            "phone": payload.consolidated_states.phone_state
        }

        enriched_scores = dict(scores or {})
        if getattr(payload, "metrics", None):
            enriched_scores["metrics"] = payload.metrics
        if clean_frame is not None:
            enriched_scores["clean_frame"] = clean_frame

        data["scores"] = enriched_scores
        data["message_type"] = "snapshot"
        return data

    @staticmethod
    def _map_work_mode_to_state(work_mode: str) -> str:
        wm = (work_mode or "").lower()
        if wm == "focused_reading":
            return "reading"
        if wm == "focused_writing":
            return "writing"
        if wm == "thinking":
            return "thinking"
        if wm == "self_explaining":
            return "focused" # Or maybe "focused"? User said talking alone is okay.
        if wm in ("phone_distraction", "social_distraction", "brief_off_task"):
            return "distracted"
        return "focused"

    @staticmethod
    def format_clean_frame(payload: CVOutputPayload, scores: dict) -> dict:
        """Minimal per-interval frame JSON requested by the user."""
        metrics = getattr(payload, "metrics", None) or {}

        state = JSONFormatter._map_work_mode_to_state(payload.consolidated_states.work_mode)
        confidence = float(getattr(payload.reliability, "work_mode_confidence", 0.0) or 0.0)

        posture_score = float(metrics.get("posture_score", scores.get("posture_score", 0.0)) or 0.0)
        fatigue_score = float(metrics.get("fatigue_score", 0.0) or 0.0)
        attention_score = float(scores.get("attention_score", 0.0) or 0.0)

        # Conservative distraction score: use whichever is higher (discrete vs. risk)
        discrete_distraction = float(scores.get("distraction_score", 0.0) or 0.0)
        distraction_risk = float(metrics.get("distraction_risk", 0.0) or 0.0)
        distraction_score = max(discrete_distraction, distraction_risk)

        phone_detected = bool(payload.instant_observations.phone_detected) or (
            payload.consolidated_states.phone_state != "not_detected"
        )

        return {
            "timestamp": payload.timestamp,
            "state": state,
            "sub_states": {
                "fatigue": payload.consolidated_states.fatigue_state,
                "posture": payload.consolidated_states.posture_state,
            },
            "scores": {
                "attention": round(attention_score, 1),
                "posture": round(posture_score, 1),
                "fatigue": round(fatigue_score, 1),
                "distraction": round(distraction_score, 1)
            },
            "confidence": round(max(0.0, min(1.0, confidence)), 2),
            "phone_detected": phone_detected,
            "alert": payload.alert.model_dump() if payload.alert.should_alert else None,
            "events": payload.events or []
        }

    @staticmethod
    def format_event(
        *,
        session_id: str,
        event_type: str,
        level: str,
        description: str,
        metadata: dict | None = None,
    ) -> dict:
        return {
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "message_type": "event",
            "event_type": event_type,
            "level": level,
            "description": description,
            "metadata": metadata or {},
        }
