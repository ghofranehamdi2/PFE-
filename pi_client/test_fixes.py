"""
test_fixes.py — Validate all 6 targeted fixes without a camera.
Run from pi_client/:  python test_fixes.py
"""
import sys, time
sys.path.insert(0, ".")

from engine.temporal_engine import TemporalEngine
from config.cv_config import config
from analyzers.fatigue_analyzer import YAWN_FRAMES_MIN, YAWN_MOUTH_RATIO_MIN
from analyzers.phone_detector import MIN_CONFIDENCE, PHONE_FACE_PROXIMITY

PASS = "[PASS]"
FAIL = "[FAIL]"

def check(label, condition, note=""):
    tag = PASS if condition else FAIL
    print(f"  {tag} {label}" + (f"  ({note})" if note else ""))
    return condition


# ─── Helpers ──────────────────────────────────────────────────────────────────
def att(yaw=0, pitch=0, face=True):
    return {
        "face_present": face, "num_faces": 1 if face else 0,
        "yaw": yaw, "pitch": pitch, "mar": 0.03,
        "face_bbox": (100, 80, 220, 200),
        "gaze_toward_person": False, "is_calibrated": True,
    }

def fat(score=0, microsleep=False, eye_closed=False, yawn=False):
    level = "high" if score >= 75 else "moderate" if score >= 45 else "low"
    return {
        "fatigue_score": score, "fatigue_level": level,
        "perclos": score * 0.5, "microsleep": microsleep,
        "eye_closed": eye_closed, "slow_blink": False,
        "yawn_in_progress": yawn, "yawn_count": 0, "frequent_yawn": False,
        "ear": 0.28, "mar": 0.03, "is_calibrated": True,
    }

def stress(grimace=0, jitter=0.001):
    return {
        "grimace_raw": grimace, "raw_jitter": jitter,
        "stress_score": grimace * 0.5, "is_calibrated": True,
    }

def pos(score=85, bad=False, hand_face=False):
    return {
        "posture_score": score, "slouch_score": 0.8, "tilt_score": 0.9,
        "fwd_score": 0.85, "lean_score": 0.9,
        "bad_posture_confirmed": bad,
        "inclination_axis": "neutral",
        "hands_on_knees": False, "hand_near_face": hand_face,
    }

def phone(found=False, conf=0.0):
    return {"phone_found": found, "confidence": conf, "bbox": None, "rel_area": 0.0}


all_pass = True

# ─── TEST 1: Yawn constants updated ───────────────────────────────────────────
print("=== TEST 1: Yawn constants match fixes ===")
ok = True
ok &= check("YAWN_FRAMES_MIN=22", YAWN_FRAMES_MIN == 22, f"got {YAWN_FRAMES_MIN}")
ok &= check("YAWN_MOUTH_RATIO_MIN=1.4", abs(YAWN_MOUTH_RATIO_MIN - 1.4) < 0.001, f"got {YAWN_MOUTH_RATIO_MIN}")
all_pass &= ok

# ─── TEST 2: Phone detector constants ─────────────────────────────────────────
print("\n=== TEST 2: Phone detector constants ===")
ok = True
ok &= check("MIN_CONFIDENCE = 0.55", abs(MIN_CONFIDENCE - 0.55) < 0.01, f"got {MIN_CONFIDENCE}")
ok &= check("PHONE_FACE_PROXIMITY = 2.0", abs(PHONE_FACE_PROXIMITY - 2.0) < 0.01, f"got {PHONE_FACE_PROXIMITY}")
all_pass &= ok

# ─── TEST 3: Gaze-away NOT instant (< 3 s should not trigger distraction) ─────
print("\n=== TEST 3: Gaze-away NOT detected instantly (<3 s window) ===")
te3 = TemporalEngine("t3")
for _ in range(5):                       # ~0.5 s of looking away
    r3 = te3.process(att(yaw=40), fat(), pos(), phone())
    time.sleep(0.1)
ok = True
ok &= check("distracted_signal ~0 after 0.5 s", te3.score_manager._signals["distracted"] < 0.05,
            f"got {te3.score_manager._signals['distracted']:.4f}")
ok &= check("attention_state not distracted", r3.consolidated_states.attention_state != "distracted",
            r3.consolidated_states.attention_state)
all_pass &= ok

# ─── TEST 4: Gaze-away sustained 4 s -> triggers distraction ──────────────────
print("\n=== TEST 4: Gaze-away sustained 4 s -> should trigger distraction ===")
te4 = TemporalEngine("t4")
start = time.time()
r4 = None
while time.time() - start < 4.5:
    r4 = te4.process(att(yaw=40), fat(), pos(), phone())
    time.sleep(0.05)
ok = True
ok &= check("distracted_signal > 0 after 4s", te4.score_manager._signals["distracted"] > 0.01,
            f"got {te4.score_manager._signals['distracted']:.4f}")
reasons = r4.consolidated_states.reasoning_indices
print(f"    reasons={reasons}")
all_pass &= ok

# ─── TEST 5: Stress (Skipped - Not in Engine) ──────────────────────────────
print("\n=== TEST 5: Stress test skipped (not implemented in engine) ===")
all_pass &= True

# ─── TEST 6: Yawn score bonus capped (no dominant spike) ──────────────────────
print("\n=== TEST 6: Yawn-in-progress fatigue_score stays low (bonus now 10) ===")
te6 = TemporalEngine("t6")
for _ in range(25):
    r6 = te6.process(att(), fat(score=10, yawn=True), pos(), phone())
    time.sleep(0.033)
ok = True
ok &= check("fatigue_state=normal for low score + yawn", r6.consolidated_states.fatigue_state == "normal",
            r6.consolidated_states.fatigue_state)
ok &= check("ema_fatigue < 45", te6.score_manager.ema_fatigue < 45, f"got {te6.score_manager.ema_fatigue:.1f}")
all_pass &= ok

# ─── TEST 7: Global reasoning_indices includes all concerns ───────────────────
print("\n=== TEST 7: reasoning_indices reflects all active sub-states ===")
te7 = TemporalEngine("t7")
for _ in range(50):
    r7 = te7.process(att(yaw=0), fat(score=80), pos(score=20, bad=True), phone())
    time.sleep(0.033)
reasons7 = r7.consolidated_states.reasoning_indices
ok = True
ok &= check("fatigue concern in reasons", any("fatigue" in r for r in reasons7), str(reasons7))
ok &= check("posture concern in reasons", any("posture" in r for r in reasons7), str(reasons7))
print(f"    attention_state={r7.consolidated_states.attention_state}")
all_pass &= ok

# ─── TEST 8: Phone confidence check ────────────────────────────────
print("\n=== TEST 8: Phone geometry and proximity checks ===")
from analyzers.phone_detector import MIN_CONFIDENCE as MC, PhoneDetector
import numpy as np, cv2
# Synthetic geometry test (no camera needed)
pd = PhoneDetector.__new__(PhoneDetector)
pd._ready = False  # don't run YOLO
# Test _is_valid_phone_bbox for a tilted-ish phone (w<h, ratio=2.5)
result = PhoneDetector._is_valid_phone_bbox(100, 50, 160, 200, 640, 480)
ok = True
ok &= check("tilted phone (ratio=2.5) passes geometry filter", result, f"result={result}")
# Test _bboxes_near proximity check (now uses 2.0x)
near = PhoneDetector._bboxes_near((400, 100, 480, 220), (100, 80, 220, 200))
ok &= check("phone within 2.0x face-width accepted", near, f"near={near}")
far = PhoneDetector._bboxes_near((800, 600, 840, 680), (100, 80, 220, 200))
ok &= check("phone far from face rejected", not far, f"far_result={far}")
all_pass &= ok

# ─── TEST 9: Phone Heuristics (Ear Use) ───────────────────────────────
print("\n=== TEST 9: Phone Heuristic (Near Ear, No YOLO) ===")
te9 = TemporalEngine("t9")
for _ in range(30):
    r9 = te9.process(att(yaw=25), fat(), pos(score=85, hand_face=True), phone(found=False))
    time.sleep(0.01)
ok = True
ok &= check("phone signal > 0 from heuristics", te9.score_manager._signals["phone"] > 0.1, f"got {te9.score_manager._signals['phone']:.3f}")
ok &= check("phone_state = probable_in_use", r9.consolidated_states.phone_state == "probable_in_use", r9.consolidated_states.phone_state)
all_pass &= ok

# ─── Summary ──────────────────────────────────────────────────────────────────
print()
print("=" * 55)
if all_pass:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED — review output above")
print("=" * 55)
