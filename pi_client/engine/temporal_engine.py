"""TemporalEngine - 4-layer engine with stability-first decisions.

Constraints (per user request):
- Do NOT change the detection models (pose/gaze/phone). Only logic & outputs.

Goals:
- Decisions are not frame-by-frame (30–60 frame smoothing)
- Conservative state changes (duration + dwell time)
- Alerts are de-duplicated (no per-frame spam)
"""

from __future__ import annotations

import time
from collections import deque
from statistics import median
import numpy as np

from config.cv_config import config
from engine.alert_manager import AlertManager
from engine.models import (
    AlertStatus,
    CVOutputPayload,
    ConsolidatedStates,
    InstantObservations,
    PresenceInfo,
    Reliability,
    ShortWindowInference,
    TemporalContext,
)


def _clamp01(x: float) -> float:
    return 0.0 if x <= 0.0 else 1.0 if x >= 1.0 else float(x)


class TemporalEngine:
    """Temporal smoothing + decision engine (L2/L3) + alert policy (L4)."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._start_time = time.time()
        self.alert_manager = AlertManager()

        # Target FPS is used only to convert seconds→frames.
        self.fps = float(config.TARGET_FPS)

        def frames(sec: float) -> int:
            return max(1, int(sec * self.fps))

        self._smooth_len = frames(config.SMOOTHING_WINDOW_SECONDS)

        # L2 smoothed evidences (0..1)
        self._signals: dict[str, float] = {
            k: 0.0 for k in ["reading", "writing", "thinking", "speech", "social", "phone", "distracted"]
        }
        # Standard buffer (30 frames) for most signals
        self._ev_buf: dict[str, deque[float]] = {
            k: deque(maxlen=self._smooth_len) for k in self._signals.keys() if k != "phone"
        }
        # ULTRA-FAST buffer for phone to ensure it's "credible"
        self._ev_buf["phone"] = deque(maxlen=max(6, int(self.fps * 0.4))) # 0.4s window

        # L3 stable work_mode state
        self.work_mode = "focused"
        self._candidate_work = "focused"
        self._candidate_start = 0.0
        self._state_start = time.time()

        # Sub-states (fatigue / stress / posture)
        self.fatigue_state = "normal"
        self.stress_state = "normal"
        self._ema_fatigue = 0.0
        self._ema_stress = 0.0
        self._ema_posture = 100.0

        self._fat_candidate = "normal"
        self._fat_candidate_start = 0.0

        self._stress_candidate = "normal"
        self._stress_candidate_start = 0.0

        self._buf_microsleep = deque(maxlen=frames(3.0))

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _push_evidence(self, key: str, value: float):
        buf = self._ev_buf[key]
        buf.append(_clamp01(value))
        
        if key == "phone":
            # Very aggressive for phone: if it's there even briefly, we want to know
            m = float(np.percentile(buf, 90)) if buf else 0.0
            a = 0.65  # Ultra fast EMA for phone
        else:
            # Consistent stable median filtering for others
            m = float(np.median(buf)) if buf else 0.0
            a = 0.15
            
        self._signals[key] = a * m + (1.0 - a) * self._signals[key]

    @staticmethod
    def _head_direction(yaw: float, pitch: float) -> str:
        if yaw > config.YAW_DISTRACT_THRESH_DEG:
            return "right"
        if yaw < -config.YAW_DISTRACT_THRESH_DEG:
            return "left"
        if pitch > config.PITCH_UP_THRESH_DEG:
            return "up"
        if pitch < -config.PITCH_DOWN_THRESH_DEG:
            return "down"
        return "frontal"

    def _update_substate(self, *, now: float, name: str, new_state: str, current_state: str, hold_sec: float, cand_state: str, cand_start: float) -> tuple[str, str, float]:
        if new_state == current_state:
            return current_state, new_state, 0.0

        if new_state != cand_state:
            return current_state, new_state, now

        if (now - cand_start) >= hold_sec:
            return new_state, new_state, 0.0

        return current_state, cand_state, cand_start

    # ---------------------------------------------------------------------
    # Main
    # ---------------------------------------------------------------------
    def process(self, att: dict, fat: dict, stress: dict, pos: dict, phone: dict) -> CVOutputPayload:
        now = time.time()
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        events: list[str] = []

        # ==================================================================
        # LEVEL 1: Map observations (no model changes)
        # ==================================================================
        face_present = bool(att.get("face_present", False))
        num_faces = int(att.get("num_faces", 0) or 0)
        yaw = float(att.get("yaw", 0.0) or 0.0)
        pitch = float(att.get("pitch", 0.0) or 0.0)
        mar = float(att.get("mar", 0.0) or 0.0)

        eye_closed = bool(fat.get("eye_closed", False))
        fatigue_score_l1 = float(fat.get("fatigue_score", 0.0) or 0.0)
        microsleep_l1 = bool(fat.get("microsleep", False))

        grimace = float(stress.get("grimace_raw", 0.0) or 0.0)
        jitter = float(stress.get("raw_jitter", 0.0) or 0.0)

        phone_found = bool(phone.get("phone_found", False))
        phone_conf = float(phone.get("confidence", 0.0) or 0.0)

        slouch = float(pos.get("slouch_score", 1.0) or 1.0)
        tilt = float(pos.get("tilt_score", 1.0) or 1.0)
        fwd = float(pos.get("fwd_score", 1.0) or 1.0)
        hand_face = bool(pos.get("hand_near_face", False))
        posture_score_l1 = pos.get("posture_score")
        inclination_axis = pos.get("inclination_axis", "neutral") or "neutral"
        bad_posture_flag = bool(pos.get("bad_posture_confirmed", False))

        if posture_score_l1 is not None:
            raw_posture = max(0.0, min(100.0, float(posture_score_l1)))
        else:
            penalty = (1.0 - slouch) * 60 + (1.0 - tilt) * 20 + (1.0 - fwd) * 20
            if hand_face:
                penalty += 15
            raw_posture = max(0.0, 100.0 - penalty)

        head_dir = self._head_direction(yaw, pitch)
        gaze_zone = "away" if head_dir in ("right", "left", "up") else ("desk" if head_dir == "down" else "screen")
        eyes_state = "closed" if eye_closed else ("squinting" if grimace > 50 else "open")

        posture_inst = "good" if raw_posture >= 82 else ("bad" if raw_posture < config.SCORE_POSTURE_BAD else "warning")
        if inclination_axis != "neutral" and raw_posture < 90:
            posture_inst = "warning"
        if bad_posture_flag and raw_posture < 85:
            posture_inst = "bad"

        inst_obs = InstantObservations(
            head_direction=head_dir,
            gaze_zone=gaze_zone,
            eyes_state=eyes_state,
            posture_state=posture_inst,
            phone_detected=phone_found,
            face_tension_level="high" if grimace > 70 else ("moderate" if grimace > 40 else "low"),
            agitation_level="high" if jitter > 0.02 else ("moderate" if jitter > 0.01 else "low"),
        )

        presence = PresenceInfo(
            main_person_present=face_present,
            person_count=num_faces,
            face_detected=face_present,
        )

        # If face is missing, keep the last stable decision (avoid flicker/false positives)
        if not face_present:
            cons_states = ConsolidatedStates(
                work_mode=self.work_mode,
                fatigue_state=self.fatigue_state,
                stress_state=self.stress_state,
                posture_state="acceptable",
                reasoning_indices=["face_missing"],
            )
            stable_dur = now - self._state_start
            return CVOutputPayload(
                session_id=self.session_id,
                timestamp=timestamp,
                presence=presence,
                instant_observations=inst_obs,
                short_window_inference=ShortWindowInference(),
                consolidated_states=cons_states,
                reliability=Reliability(work_mode_confidence=0.1, attention_confidence=0.5, fatigue_confidence=0.5, stress_confidence=0.5),
                temporal_context=TemporalContext(observed_for_sec=round(now - self._start_time, 2), stable_state_for_sec=round(stable_dur, 2)),
                alert=AlertStatus(),
                metrics={
                    "fatigue_score": round(self._ema_fatigue, 1),
                    "stress_score": round(self._ema_stress, 1),
                    "posture_score": round(self._ema_posture, 1),
                    "distraction_risk": 0.0,
                },
                events=[],
            )

        # ==================================================================
        # LEVEL 2: Evidence extraction + 30–60 frame smoothing
        # ==================================================================

        # Reading (looking down can be reading; do not treat as distraction)
        reading_ev = 0.0
        if head_dir == "down":
            reading_ev += config.WEIGHT_READING_PITCH_DOWN
        if abs(yaw) < config.YAW_READING_THRESH_DEG:
            reading_ev += config.WEIGHT_READING_YAW_CENTER
        if inst_obs.agitation_level == "low":
            reading_ev += config.WEIGHT_READING_STABILITY
        self._push_evidence("reading", min(1.0, reading_ev))

        # Writing
        writing_ev = 0.0
        if head_dir == "down":
            writing_ev += config.WEIGHT_WRITING_PITCH_DOWN
        if bool(pos.get("hands_on_knees", False)):
            writing_ev += config.WEIGHT_WRITING_HANDS_NEAR
        self._push_evidence("writing", min(1.0, writing_ev))

        # Thinking (looking away can be thinking; calm+stable increases it)
        thinking_ev = 0.0
        if head_dir in ("up", "left", "right"):
            thinking_ev += config.WEIGHT_THINKING_YAW_AWAY
        if inst_obs.face_tension_level == "low" and inst_obs.agitation_level == "low":
            thinking_ev += config.WEIGHT_THINKING_CALM
        self._push_evidence("thinking", min(1.0, thinking_ev))

        # Speech (self-explaining is not distraction)
        speech_allowed = (
            not phone_found
            and not microsleep_l1
            and fatigue_score_l1 < config.SCORE_FATIGUE_WARNING
            and inst_obs.agitation_level != "high"
        )
        speech_ev = 0.0
        if speech_allowed and mar > config.LIP_MAR_SPEECH_THRESH:
            speech_ev += config.WEIGHT_SPEECH_MAR_ACTIVE
        if speech_allowed and mar > config.SPEECH_MAR_STRONG_THRESH:
            speech_ev += 0.15
        if speech_allowed and num_faces == 1 and head_dir == "frontal":
            speech_ev += config.WEIGHT_SPEECH_SINGLE_PRES
        if speech_allowed and abs(jitter) <= config.SPEECH_MAX_JITTER:
            speech_ev += 0.10
        self._push_evidence("speech", min(1.0, speech_ev))

        # Phone evidence
        phone_ev = 0.0
        if phone_found:
            phone_ev += config.WEIGHT_PHONE_DETECTED + max(0.0, phone_conf * 0.4)
            if head_dir == "down" or hand_face:
                phone_ev += config.WEIGHT_PHONE_GAZE_MATCH
        self._push_evidence("phone", min(1.0, phone_ev))

        # Social evidence
        social_ev = (1.0 if num_faces >= 2 else 0.0) * 0.7 + (0.3 if bool(att.get("gaze_toward_person", False)) else 0.0)
        self._push_evidence("social", min(1.0, social_ev))

        # Off-task / distraction evidence (conservative):
        # - Looking away alone is often "thinking" (highly conservative).
        # - Looking down is mostly "reading" or "writing".
        # - Only increase distraction if away/down + agitation + NO other strong hypothesis.
        distracted_ev = 0.0
        away = head_dir in ("left", "right", "up")
        down = head_dir == "down"

        if (away or down) and not phone_found and num_faces < 2:
            # Base distraction logic: higher if agitated, lower if calm.
            base = 0.40 if inst_obs.agitation_level != "low" else 0.15
            
            # Stronger suppression from other signals (thinking, speech, reading, writing)
            suppress = (
                0.7 * self._signals["thinking"] + 
                0.8 * self._signals["speech"] + 
                0.8 * self._signals["reading"] + 
                0.8 * self._signals["writing"]
            )
            distracted_ev = max(0.0, base * (1.0 - min(0.95, suppress)))
        
        # If phone is found, that's a separate signal handled in Level 3.
        self._push_evidence("distracted", distracted_ev)

        # ==================================================================
        # LEVEL 3: Stable work_mode (duration + dwell time)
        # ==================================================================

        # Candidate thresholds (stability-first)
        thresholds = {
            "phone_distraction": 0.75,
            "social_distraction": 0.75,
            "focused_reading": 0.65,
            "focused_writing": 0.65,
            "self_explaining": 0.85,
            "thinking": 0.65,
            "brief_off_task": 0.80,
        }

        # Priority overrides (to avoid under-reacting on clear cases)
        if self._signals["phone"] >= 0.65:
            chosen = ("phone_distraction", self._signals["phone"], config.TRANSITION_DELAY_PHONE)
        elif self._signals["social"] >= 0.65:
            chosen = ("social_distraction", self._signals["social"], config.TRANSITION_DELAY_SOCIAL)
        else:
            candidates = [
                ("focused_reading", self._signals["reading"], config.TRANSITION_DELAY_READING),
                ("focused_writing", self._signals["writing"], config.TRANSITION_DELAY_WRITING),
                ("self_explaining", self._signals["speech"], config.SELF_EXPLAIN_DELAY),
                ("thinking", self._signals["thinking"], config.TRANSITION_DELAY_THINKING),
                ("brief_off_task", self._signals["distracted"], config.TRANSITION_DELAY_DISTRACTED),
            ]
            # Only consider candidates that clear their thresholds.
            viable = [c for c in candidates if c[1] >= thresholds.get(c[0], 0.0)]
            if viable:
                chosen = max(viable, key=lambda x: x[1])
            else:
                chosen = ("focused", 0.0, config.TRANSITION_DELAY_FOCUSED)

        best_mode, best_signal, best_delay = chosen

        # Conservative dwell: don't bounce rapidly between states.
        dwell_ok = (now - self._state_start) >= config.MIN_STATE_DWELL_SECONDS
        if not dwell_ok and best_mode not in ("phone_distraction", "social_distraction"):
            best_mode, best_signal, best_delay = self.work_mode, 1.0, config.TRANSITION_DELAY_FOCUSED

        if best_mode != self.work_mode:
            if best_mode != self._candidate_work:
                self._candidate_work = best_mode
                self._candidate_start = now
            elif (now - self._candidate_start) >= best_delay:
                prev = self.work_mode
                self.work_mode = best_mode
                self._state_start = now
                
                # Production events logic
                focus_modes = {"focused", "reading", "writing", "thinking", "focused_reading", "focused_writing", "self_explaining"}
                prev_is_focus = prev in focus_modes
                curr_is_focus = best_mode in focus_modes
                
                if prev_is_focus and not curr_is_focus:
                    events.append({"type": "FOCUS_LOST", "timestamp": timestamp})
                elif not prev_is_focus and curr_is_focus:
                    events.append({"type": "FOCUS_RECOVERED", "timestamp": timestamp})

                if best_mode == "phone_distraction":
                    events.append({"type": "PHONE_DETECTED", "timestamp": timestamp})

                events.append({
                    "type": "MODE_CHANGE",
                    "description": f"Transition from {prev} to {best_mode}",
                    "from_mode": prev,
                    "to_mode": best_mode,
                    "timestamp": timestamp
                })
        else:
            self._candidate_work = best_mode
            self._candidate_start = 0.0

        # ==================================================================
        # Sub-states (fatigue / stress / posture) - conservative holds
        # ==================================================================

        # Fatigue score (EMA) + microsleep confirmation
        self._buf_microsleep.append(1 if microsleep_l1 else 0)
        microsleep_confirmed = (len(self._buf_microsleep) > 0 and (sum(self._buf_microsleep) / len(self._buf_microsleep)) > 0.92)
        fat_sig = float(fatigue_score_l1)
        if microsleep_confirmed:
            fat_sig = max(fat_sig, 92.0)

        self._ema_fatigue = (config.EMA_ALPHA_FATIGUE * fat_sig) + ((1.0 - config.EMA_ALPHA_FATIGUE) * self._ema_fatigue)

        new_fat = "normal"
        if self._ema_fatigue >= config.SCORE_FATIGUE_HIGH:
            new_fat = "fatigue_high"
        elif self._ema_fatigue >= config.SCORE_FATIGUE_WARNING:
            new_fat = "fatigue_warning"

        fat_hold = 1.0 if new_fat == "fatigue_high" else 2.5 if new_fat == "fatigue_warning" else 1.5
        self.fatigue_state, self._fat_candidate, self._fat_candidate_start = self._update_substate(
            now=now,
            name="fatigue",
            new_state=new_fat,
            current_state=self.fatigue_state,
            hold_sec=fat_hold,
            cand_state=self._fat_candidate,
            cand_start=self._fat_candidate_start,
        )

        # Stress score (EMA), avoid instant escalation
        HIGH_JITTER_THRESHOLD = 0.010
        if fatigue_score_l1 >= config.SCORE_FATIGUE_WARNING:
            jitter_weight = 0.05
            grimace_weight = 1.0  # Entirely grimace if fatigued
        elif jitter > HIGH_JITTER_THRESHOLD:
            jitter_weight = 0.35
            grimace_weight = 0.80 # Stronger on grimace
        else:
            jitter_weight = 0.15
            grimace_weight = 1.0  # Almost entirely grimace

        stress_sig = grimace_weight * grimace + jitter_weight * jitter * config.STRESS_JITTER_SCALE
        if eye_closed:
            stress_sig *= 0.85
        if fatigue_score_l1 >= config.SCORE_FATIGUE_WARNING or microsleep_l1:
            stress_sig *= 0.80  # Less damping than before

        self._ema_stress = (config.EMA_ALPHA_STRESS_TOTAL * stress_sig) + ((1.0 - config.EMA_ALPHA_STRESS_TOTAL) * self._ema_stress)

        new_stress = "normal"
        if self._ema_stress >= config.SCORE_STRESS_ELEVATED:
            new_stress = "stress_elevated"
        elif self._ema_stress >= config.SCORE_STRESS_SUSPECTED:
            new_stress = "stress_suspected"

        stress_hold = 4.0 if new_stress == "stress_elevated" else 3.0 if new_stress == "stress_suspected" else 2.0
        self.stress_state, self._stress_candidate, self._stress_candidate_start = self._update_substate(
            now=now,
            name="stress",
            new_state=new_stress,
            current_state=self.stress_state,
            hold_sec=stress_hold,
            cand_state=self._stress_candidate,
            cand_start=self._stress_candidate_start,
        )

        # Posture (EMA)
        self._ema_posture = (config.EMA_ALPHA_POSTURE * raw_posture) + ((1.0 - config.EMA_ALPHA_POSTURE) * self._ema_posture)
        if self._ema_posture >= 78:
            pos_consolidated = "good"
        elif (self._ema_posture < config.SCORE_POSTURE_BAD and (bad_posture_flag or raw_posture < 60)):
            pos_consolidated = "poor_persistent"
        else:
            pos_consolidated = "acceptable"

        # ==================================================================
        # Final consolidated states
        # ==================================================================

        reasons: list[str] = []
        if head_dir == "down":
            reasons.append("head_down")
        if phone_found:
            reasons.append("phone_detected")

        cons_states = ConsolidatedStates(
            work_mode=self.work_mode,
            attention_state=(
                "distracted" if self.work_mode in ("phone_distraction", "social_distraction")
                else "slightly_distracted" if self.work_mode == "brief_off_task"
                else "focused"
            ),
            fatigue_state=self.fatigue_state,
            stress_state=self.stress_state,
            social_state=(
                "active_interaction" if self._signals["social"] > 0.7
                else "other_person_present" if num_faces >= 2
                else "alone"
            ),
            phone_state=(
                "probable_in_use"
                if phone_found and (self._signals["phone"] > 0.55 or head_dir == "down" or hand_face or phone_conf > 0.35)
                else "detected_not_used" if phone_found
                else "not_detected"
            ),
            posture_state=pos_consolidated,
            reasoning_indices=reasons,
        )

        # Confidence from separation between top candidates
        mode_scores = [
            ("phone", self._signals["phone"]),
            ("social", self._signals["social"]),
            ("reading", self._signals["reading"]),
            ("writing", self._signals["writing"]),
            ("speech", self._signals["speech"]),
            ("thinking", self._signals["thinking"]),
            ("distracted", self._signals["distracted"]),
        ]
        mode_scores.sort(key=lambda x: x[1], reverse=True)
        top = mode_scores[0][1] if mode_scores else 0.0
        second = mode_scores[1][1] if len(mode_scores) > 1 else 0.0
        margin = max(0.0, top - second)
        work_conf = max(0.1, min(0.95, 0.2 + 0.6 * top + 0.6 * margin))

        stable_dur = now - self._state_start
        alert_status = self.alert_manager.evaluate(cons_states)
        if alert_status.should_alert:
            events.append({
                "type": "ALERT",
                "level": alert_status.level,
                "reason": alert_status.reason,
                "timestamp": timestamp
            })

        distraction_risk = max(self._signals["phone"], self._signals["social"], self._signals["distracted"])

        short_win = ShortWindowInference(
            possible_reading=self._signals["reading"] > 0.7,
            possible_writing=self._signals["writing"] > 0.7,
            possible_thinking=self._signals["thinking"] > 0.65,
            possible_self_explaining=self._signals["speech"] > 0.85,
            possible_social_interaction=self._signals["social"] > 0.65,
            possible_phone_distraction=self._signals["phone"] > 0.65,
            possible_fatigue=self._ema_fatigue > config.SCORE_FATIGUE_WARNING,
            possible_stress=self._ema_stress > config.SCORE_STRESS_SUSPECTED,
        )

        return CVOutputPayload(
            session_id=self.session_id,
            timestamp=timestamp,
            presence=presence,
            instant_observations=inst_obs,
            short_window_inference=short_win,
            consolidated_states=cons_states,
            reliability=Reliability(
                work_mode_confidence=round(work_conf, 2),
                attention_confidence=0.90,
                fatigue_confidence=0.85,
                stress_confidence=0.80,
            ),
            temporal_context=TemporalContext(
                observed_for_sec=round(now - self._start_time, 2),
                stable_state_for_sec=round(stable_dur, 2),
            ),
            alert=alert_status,
            metrics={
                "fatigue_score": round(self._ema_fatigue, 1),
                "stress_score": round(self._ema_stress, 1),
                "posture_score": round(self._ema_posture, 1),
                "distraction_risk": round(distraction_risk * 100.0, 1),
            },
            events=events,
        )
