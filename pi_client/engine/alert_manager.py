import time

from config.cv_config import config
from engine.models import ConsolidatedStates, AlertStatus


class AlertManager:
    """Level 4: conservative alert policy with de-duplication.

    Goals:
    - No per-frame alert spam
    - Alerts only after temporal confirmation (per-condition timers)
    - Prefer "no alert" over false positives
    """

    def __init__(self):
        self._since: dict[str, float] = {}
        self._last_fired: dict[str, float] = {}

    def _track(self, key: str, active: bool, now: float) -> float | None:
        """Returns how long the condition has been continuously active (seconds)."""
        if not active:
            self._since.pop(key, None)
            return None
        if key not in self._since:
            self._since[key] = now
        return now - self._since[key]

    def _can_fire(self, key: str, now: float) -> bool:
        last = self._last_fired.get(key)
        return last is None or (now - last) >= config.ALERT_COOLDOWN_SECONDS

    def evaluate(self, state: ConsolidatedStates) -> AlertStatus:
        now = time.time()

        # Global cooldown check (don't fired any alert if another was just fired)
        last_global = max(self._last_fired.values()) if self._last_fired else 0.0
        if (now - last_global) < 3.0: # Minimum 3s between any two alerts
            return AlertStatus(should_alert=False, level="none", reason=None)

        # Priority order (highest first)
        checks: list[tuple[str, bool, float, str, str]] = [
            (
                "fatigue_high",
                state.fatigue_state == "fatigue_high",
                2.5, # Slightly longer threshold
                "high",
                "Fatigue critique détectée.",
            ),
            (
                "fatigue_warning",
                state.fatigue_state == "fatigue_warning",
                config.ALERT_DELAY_FATIGUE,
                "medium",
                "Signes de fatigue persistants.",
            ),
            (
                "phone_distraction",
                state.work_mode == "phone_distraction",
                config.ALERT_DELAY_PHONE,
                "high",
                "Utilisation du téléphone détectée.",
            ),
            (
                "social_distraction",
                state.work_mode == "social_distraction",
                config.ALERT_DELAY_SOCIAL,
                "medium",
                "Interaction sociale prolongée.",
            ),
            (
                "off_task",
                state.work_mode == "brief_off_task",
                config.ALERT_DELAY_DISTRACTED,
                "low",
                "Attention relâchée.",
            ),
            (
                "posture",
                state.posture_state == "poor_persistent",
                config.ALERT_DELAY_POSTURE,
                "low",
                "Posture à corriger.",
            ),
            (
                "stress_elevated",
                state.stress_state == "stress_elevated",
                config.ALERT_DELAY_STRESS,
                "high",
                "Niveau de stress élevé.",
            ),
        ]

        for key, active, delay, level, reason in checks:
            active_for = self._track(key, active, now)
            if active_for is None:
                continue
            if active_for >= delay and self._can_fire(key, now):
                self._last_fired[key] = now
                return AlertStatus(should_alert=True, level=level, reason=reason)

        return AlertStatus(should_alert=False, level="none", reason=None)
