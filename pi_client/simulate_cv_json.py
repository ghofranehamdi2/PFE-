import json
import time
from unittest.mock import patch
from uuid import uuid4
from engine.temporal_engine import TemporalEngine
from config.cv_config import config

def simulate_real_case(case_name, sequence_steps):
    """
    Simulates a sequence of L1 dict observations and prints the final payload
    by mocking time.time() to properly trigger temporal engine hysteresis.
    """
    print(f"\n======================================")
    print(f"CASE: {case_name}")
    print(f"======================================")
    
    with patch('time.time') as mock_time:
        start_t = 10000.0
        mock_time.return_value = start_t
        engine = TemporalEngine(session_id=str(uuid4()))
        fps = engine.fps
        
        payload = None
        current_t = start_t
        
        # Defaults
        att = {"face_present": True, "num_faces": 1, "yaw": 0.0, "pitch": 0.0, "mar": 0.0, "gaze_toward_person": False}
        fat = {"eye_closed": False, "pitch_proxy": 0.0, "base_mar": 0.0}
        stress = {"raw_jitter": 0.001, "grimace_raw": 0.0}
        pos = {"slouch_score": 0.0, "tilt_score": 0.0, "fwd_score": 0.0, "lean_score": 0.0, "hands_on_knees": False, "hand_near_face": False}
        phone = {"phone_found": False}

        from output.score_engine import ScoreEngine
        from output.json_formatter import JSONFormatter
        
        score_engine = ScoreEngine()
        formatter = JSONFormatter()

        for duration, overrides in sequence_steps:
            # Apply overrides to defaults for this step
            if "att" in overrides: att.update(overrides["att"])
            if "fat" in overrides: fat.update(overrides["fat"])
            if "stress" in overrides: stress.update(overrides["stress"])
            if "pos" in overrides: pos.update(overrides["pos"])
            if "phone" in overrides: phone.update(overrides["phone"])
            
            frames = int(duration * fps)
            for _ in range(frames):
                mock_time.return_value = current_t
                payload = engine.process(att, fat, stress, pos, phone)
                current_t += 1.0 / fps
        
        posture_for_scores = float(getattr(payload, "metrics", {}).get("posture_score", pos.get("posture_score", 70)) or 70.0)
        scores = score_engine.compute_all(payload.consolidated_states, raw_posture_score=posture_for_scores)
        scores["fatigue_score"] = float(getattr(payload, "metrics", {}).get("fatigue_score", 0.0) or 0.0)

        clean_frame = formatter.format_clean_frame(payload, scores)
        final_json = formatter.format_snapshot(payload, scores, clean_frame=clean_frame)

        print(json.dumps(final_json, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    
    # Case 1: Focused Reading (User looks down for 3 seconds)
    simulate_real_case("Focused Reading", [
        (2.0, {}), # 2s normal (to clear any init state if needed)
        (3.0, {"att": {"pitch": -25.0}, "pos": {"hands_on_knees": True}}) # 3s reading/writing
    ])

    # Case 2: Self-Explaining (User alone, speaking for 3 seconds)
    # 2s to clear state
    # 3s to trigger it
    simulate_real_case("Self Explaining", [
        (2.0, {}),
        (3.0, {"att": {"mar": 0.1}}) # Lips moving
    ])

    # Case 3: Brief off-task (User looks away for 1 second, no alert, state is brief_off_task)
    # brief_off_task gets triggered after 2.5s config.STATE_HOLD_DISTRACTED, wait!
    # Ah, let's wait 3.0s to trigger the brief distaction, but NOT the alert (which is 5.0).
    simulate_real_case("Brief Distraction (State changes, but No Alert)", [
        (2.0, {}),
        (3.0, {"att": {"yaw": 30.0}}) # Looks right 
    ])

    # Case 4: Phone usage confirmed (User looks down + phone detected for 7s)
    # config.STATE_HOLD_PHONE is 2.0s
    # config.ALERT_DELAY_PHONE is 4.0s -> 6.0s total needed for alert
    simulate_real_case("Phone Distraction (Alert Fired)", [
        (2.0, {}),
        (7.0, {"att": {"pitch": -25.0}, "phone": {"phone_found": True}})
    ])
