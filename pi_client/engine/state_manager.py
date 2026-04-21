import time
from config.cv_config import config
from engine.hysteresis_manager import HysteresisManager

class StateManager:
    """
    Level 3: Sub-state Computation.
    Refactored to include persistent hysteresis with asymmetric entry/exit logic.
    """
    
    def __init__(self):
        self.hysteresis = HysteresisManager()
        self.current_states = {
            "fatigue": "normal",
            "posture": "good",
            "phone": "not_detected",
            "distraction": "focused"
        }

    def compute_sub_states(self, now: float, smoothed_scores: dict, raw_flags: dict) -> dict[str, str]:
        """
        Determines the stable sub-states using hysteresis to prevent abrupt transitions.
        """
        
        # 1. Determine Target Sub-states (Raw Observations for hysteresis)
        
        # Fatigue target
        ema_fat = smoothed_scores["ema_fatigue"]
        if ema_fat >= config.SCORE_FATIGUE_HIGH:
            target_fat = "fatigue_high"
        elif ema_fat >= config.SCORE_FATIGUE_WARNING:
            target_fat = "fatigue_warning"
        else:
            target_fat = "normal"
            
        # Posture target
        ema_pos = smoothed_scores["ema_posture"]
        bad_flag = raw_flags.get("bad_posture_confirmed", False)
        raw_pos = raw_flags.get("posture_raw", 100.0)
        if ema_pos >= 78:
            target_pos = "good"
        elif ema_pos < config.SCORE_POSTURE_BAD and (bad_flag or raw_pos < 60):
            target_pos = "poor_persistent"
        else:
            target_pos = "acceptable"
            
        # Phone target
        phone_sig = smoothed_scores["phone"]
        target_phone = "probable_in_use" if phone_sig > 0.45 else "not_detected"
        
        # Distraction target
        dist_sig = smoothed_scores["distracted"]
        target_dist = "distraction" if dist_sig > 0.35 else "focused"

        # 2. Apply Hysteresis (Enter vs Exit delays)
        observations = {
            "fatigue": target_fat,
            "posture": target_pos,
            "phone": target_phone,
            "distraction": target_dist
        }
        
        self.current_states = self.hysteresis.process(now, observations)
        
        return self.current_states
