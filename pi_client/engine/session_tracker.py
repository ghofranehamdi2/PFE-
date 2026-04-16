from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def _parse_ts(ts: str) -> datetime:
    # Expected: 2026-04-16T12:34:56Z
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        # Best-effort fallback
        return datetime.now(tz=timezone.utc)


@dataclass
class SessionTracker:
    """Accumulates clean per-interval frames into a session summary."""

    session_id: str
    _start_ts: datetime | None = None
    _last_ts: datetime | None = None

    _sum_attention: float = 0.0
    _sum_posture: float = 0.0
    _sum_fatigue: float = 0.0
    _sum_distraction: float = 0.0
    _n: int = 0

    _distracted_seconds: float = 0.0
    _reading_seconds: float = 0.0
    _posture_good_seconds: float = 0.0
    _total_seconds: float = 0.0

    _max_fatigue: float = 0.0

    def add_frame(self, frame: dict):
        ts = _parse_ts(str(frame.get("timestamp", "")))
        scores = frame.get("scores", {})
        state = str(frame.get("state", "")).lower()

        if self._start_ts is None:
            self._start_ts = ts
            self._last_ts = ts

        # Duration accumulation (time between samples)
        if self._last_ts is not None:
            dt = (ts - self._last_ts).total_seconds()
            if 0.0 <= dt <= 10.0:
                self._total_seconds += dt
                if state == "distracted":
                    self._distracted_seconds += dt
                if state == "reading":
                    self._reading_seconds += dt
                if float(scores.get("posture", 0.0)) >= 70.0:
                    self._posture_good_seconds += dt
        self._last_ts = ts

        # Numeric accumulation
        self._n += 1
        self._sum_attention += float(scores.get("attention", 0.0))
        self._sum_posture += float(scores.get("posture", 0.0))
        self._sum_fatigue += float(scores.get("fatigue", 0.0))
        self._sum_distraction += float(scores.get("distraction", 0.0))
        self._max_fatigue = max(self._max_fatigue, float(scores.get("fatigue", 0.0)))

    def finalize(self) -> dict:
        avg = lambda s: (s / self._n) if self._n else 0.0

        avg_attention = avg(self._sum_attention)
        avg_posture = avg(self._sum_posture)
        avg_fatigue = avg(self._sum_fatigue)
        avg_distraction = avg(self._sum_distraction)

        duration = float(self._total_seconds)
        distraction_ratio = (self._distracted_seconds / duration) if duration > 0 else 0.0
        focus_ratio = 1.0 - distraction_ratio
        
        # Conservative fatigue level
        fatigue_index = max(avg_fatigue, self._max_fatigue * 0.80)
        if fatigue_index >= 75.0:
            fatigue_level = "high"
        elif fatigue_index >= 45.0:
            fatigue_level = "moderate"
        else:
            fatigue_level = "low"

        # Final score calculation (0-100)
        inv_fatigue = 100.0 - max(0.0, min(100.0, avg_fatigue))
        inv_distraction = 100.0 - max(0.0, min(100.0, avg_distraction))

        final_score = (
            0.40 * avg_attention +
            0.20 * avg_posture +
            0.20 * inv_fatigue +
            0.20 * inv_distraction
        )
        final_score = max(0.0, min(100.0, float(final_score)))

        return {
            "session_duration": round(duration, 2),
            "focus_time_ratio": round(focus_ratio, 4),
            "distraction_time_ratio": round(distraction_ratio, 4),
            "reading_time": round(float(self._reading_seconds), 2),
            "posture_quality_score": round((self._posture_good_seconds / duration * 100) if duration > 0 else 0.0, 2),
            "fatigue_level": fatigue_level,
            "final_score": round(final_score, 2),
            "breakdown": {
                "attention_score": round(avg_attention, 2),
                "posture_score": round(avg_posture, 2),
                "fatigue_score": round(avg_fatigue, 2),
                "distraction_score": round(avg_distraction, 2)
            }
        }
