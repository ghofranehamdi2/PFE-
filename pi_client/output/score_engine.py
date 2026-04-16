from engine.models import ConsolidatedStates

class ScoreEngine:
    """
    Translates discrete behavioral states into numerical scores (0-100).
    Pure logic layer - no temporal context or vision processing here.
    """
    
    def __init__(self):
        # Configuration for weights and base values
        self.weights = {
            "attention": 0.5,
            "posture": 0.2,
            "vigilance": 0.3
        }

    def compute_all(self, states: ConsolidatedStates, raw_posture_score: float = None) -> dict:
        """Computes all scores and the global focus score."""
        
        attention_score = self._get_attention_score(states.work_mode)
        posture_score = raw_posture_score if raw_posture_score is not None else self._get_posture_score(states.posture_state)
        vigilance_score = self._get_vigilance_score(states.fatigue_state)
        stress_risk = self._get_stress_risk(states.stress_state)
        distraction = self._get_distraction_score(states.work_mode)
        phone_risk = self._get_phone_risk(states.work_mode)
        
        # Weighted Global Focus Score - IMPROVED
        # Si téléphone détecté, ça réduit significativement le score
        focus_penalty = 0.0
        if "phone" in states.work_mode.lower():
            focus_penalty = 0.35  # 35% pénalité si téléphone en main
        
        global_focus = (
            (attention_score * self.weights["attention"]) +
            (posture_score * self.weights["posture"]) +
            (vigilance_score * self.weights["vigilance"])
        ) * (1.0 - focus_penalty)
        
        # Session score calculation
        session_score = self._compute_session_score(
            attention_score, posture_score, vigilance_score, stress_risk, phone_risk
        )
        
        return {
            "attention_score": round(attention_score, 2),
            "posture_score": round(posture_score, 2),
            "vigilance_score": round(vigilance_score, 2),
            "stress_risk_score": round(stress_risk, 2),
            "distraction_score": round(distraction, 2),
            "phone_risk_score": round(phone_risk, 2),
            "focus_score_global": round(max(0, global_focus), 2),
            "session_score": round(session_score, 2)
        }

    def _get_attention_score(self, work_mode: str) -> float:
        mapping = {
            "focused": 100.0,
            "focused_reading": 100.0,
            "focused_writing": 100.0,
            "thinking": 85.0,
            # Talking alone can be self-explaining (still on-task).
            "self_explaining": 90.0,
            "brief_off_task": 30.0,
            "phone_distraction": 0.0,
            "social_distraction": 0.0
        }
        return mapping.get(work_mode, 50.0)

    def _get_posture_score(self, posture_state: str) -> float:
        mapping = {
            "good": 100.0,
            "acceptable": 60.0,
            "poor_persistent": 0.0
        }
        return mapping.get(posture_state, 50.0)

    def _get_vigilance_score(self, fatigue_state: str) -> float:
        mapping = {
            "normal": 100.0,
            "fatigue_warning": 50.0,
            "fatigue_high": 0.0
        }
        return mapping.get(fatigue_state, 50.0)

    def _get_stress_risk(self, stress_state: str) -> float:
        mapping = {
            "normal": 0.0,
            "stress_suspected": 50.0,
            "stress_elevated": 100.0
        }
        return mapping.get(stress_state, 20.0)

    def _get_distraction_score(self, work_mode: str) -> float:
        mapping = {
            "focused": 0.0,
            "focused_reading": 0.0,
            "focused_writing": 0.0,
            # Looking away can be thinking; do not mark it as distraction by default.
            "thinking": 10.0,
            "self_explaining": 5.0,
            "brief_off_task": 50.0,
            "social_distraction": 80.0,
            "phone_distraction": 100.0
        }
        return mapping.get(work_mode, 10.0)

    def _get_phone_risk(self, work_mode: str) -> float:
        """ADDED: Calcule le risque téléphone (0-100)"""
        if "phone" in work_mode.lower():
            return 100.0
        elif "distraction" in work_mode.lower():
            return 50.0
        else:
            return 0.0

    def _compute_session_score(self, attention: float, posture: float, 
                               vigilance: float, stress: float, phone_risk: float) -> float:
        """ADDED: Calcule le score de session global (0-100)"""
        # Weights: attention is dominant (60%), posture (15%), vigilance (15%), stress/phone (10%)
        base_score = (
            (attention * 0.60) +
            (posture * 0.15) +
            (vigilance * 0.15)
        )
        
        # Penalties for risk factors
        stress_penalty = (stress / 100.0) * 10.0  # Max 10 points de pénalité
        phone_penalty = (phone_risk / 100.0) * 15.0  # Max 15 points
        
        session_score = base_score - stress_penalty - phone_penalty
        return max(0.0, min(100.0, session_score))
