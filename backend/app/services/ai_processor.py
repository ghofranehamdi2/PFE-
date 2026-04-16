from typing import List, Dict
from app.models.models import EventType, Event

class AIProcessor:
    def process_event(self, event_type: EventType, score: float) -> Dict:
        """
        Decision logic based on event type and score.
        In a real scenario, this would call more complex AI models.
        """
        threshold = 0.7 # Default threshold
        
        if event_type == EventType.POSTURE:
            if score < threshold:
                return {"alert": True, "message": "Mauvaise posture détectée. Redressez-vous.", "priority": "medium"}
        
        elif event_type == EventType.FATIGUE:
            if score < threshold:
                return {"alert": True, "message": "Signes de fatigue détectés. Prenez une pause.", "priority": "high"}
        
        elif event_type == EventType.DISTRACTION:
            if score < threshold:
                return {"alert": True, "message": "Baisse de concentration détectée.", "priority": "low"}
        
        return {"alert": False, "message": "OK"}

ai_processor = AIProcessor()
