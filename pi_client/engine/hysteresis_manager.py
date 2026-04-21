import time
from typing import Dict, Any

class HysteresisState:
    """
    Handles asymmetric state transitions (Enter vs Exit delays).
    Ensures a state is only entered after enter_sec, and only exited after exit_sec.
    """
    
    def __init__(self, initial_state: str, enter_sec: float, exit_sec: float):
        self.current_state = initial_state
        self.default_state = initial_state
        self.enter_sec = enter_sec
        self.exit_sec = exit_sec
        
        self._candidate_state: str = initial_state
        self._candidate_start_time: float = 0.0

    def update(self, now: float, observed_state: str) -> str:
        # If observed match current, reset any pending candidate
        if observed_state == self.current_state:
            self._candidate_state = observed_state
            self._candidate_start_time = 0.0
            return self.current_state

        # If observed state changed from the current candidate, start new timer
        if observed_state != self._candidate_state:
            self._candidate_state = observed_state
            self._candidate_start_time = now
            return self.current_state

        # We have a stable candidate different from current. Check duration.
        elapsed = now - self._candidate_start_time
        
        # Asymmetric thresholds
        # If we are in 'default' and going to 'something else' -> use enter_sec
        # If we are in 'something else' and going to 'default' -> use exit_sec
        threshold = self.exit_sec if observed_state == self.default_state else self.enter_sec
        
        if elapsed >= threshold:
            self.current_state = observed_state
            self._candidate_start_time = 0.0
            
        return self.current_state

class HysteresisManager:
    """
    Manages a collection of HysteresisState objects for various behavioral factors.
    """
    
    def __init__(self):
        self.factors: Dict[str, HysteresisState] = {
            "fatigue": HysteresisState("normal", enter_sec=2.5, exit_sec=6.0),
            "posture": HysteresisState("good", enter_sec=3.0, exit_sec=10.0),
            "phone": HysteresisState("not_detected", enter_sec=2.0, exit_sec=5.0),
            "distraction": HysteresisState("focused", enter_sec=3.0, exit_sec=5.0)
        }

    def process(self, now: float, observations: Dict[str, str]) -> Dict[str, str]:
        results = {}
        for key, state_obj in self.factors.items():
            obs = observations.get(key, state_obj.default_state)
            results[key] = state_obj.update(now, obs)
        return results
