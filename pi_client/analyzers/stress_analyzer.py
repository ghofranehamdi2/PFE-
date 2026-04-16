import mediapipe as mp
import cv2
import numpy as np
from collections import deque

# Key stable landmarks for jitter (head micro-movements)
KEY_IDS = [1, 152, 33, 263, 61, 291]

# Facial expression landmarks
INNER_BROW_LEFT   = 107
INNER_BROW_RIGHT  = 336
LEFT_EYE_OUTER    = 33
RIGHT_EYE_OUTER   = 263
LIP_TOP_INNER     = 13
LIP_BOTTOM_INNER  = 14
LIP_LEFT_CORNER   = 61
LIP_RIGHT_CORNER  = 291
NOSE_TIP          = 1
LEFT_EYE_TOP      = 159   
LEFT_EYE_BOTTOM   = 145   
RIGHT_EYE_TOP     = 386
RIGHT_EYE_BOTTOM  = 374

class StressAnalyzer:
    """
    Level 1 Analyzer: Extracts purely instantaneous observations for Stress.
    Computes facial grimace and jitter. Jitter uses a small smoothing to reject noise, 
    but the true states are derived in L2/L3.
    """
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # ── Calibration ───────────────────────────────────────────────────────
        self.is_calibrated = False
        self._cal_jitters       = []
        self._cal_brow_dists    = []
        self._cal_lip_seps      = []
        self._cal_lip_corner_ys = []
        self._cal_eye_openings  = []
        self.base_noise         = 0.0015
        self.base_brow_dist     = 0.10   
        self.base_lip_sep       = 0.03   
        self.base_lip_corner_y  = 0.0    
        self.base_eye_opening   = 0.04   
        self.CAL_FRAMES         = 60

        # Jitter points buffer for instantaneous velocity
        self._prev_points = None
        self._head_scale  = 1.0

    @staticmethod
    def _inter_eye(lm) -> float:
        le = np.array([lm[LEFT_EYE_OUTER].x, lm[LEFT_EYE_OUTER].y])
        re = np.array([lm[RIGHT_EYE_OUTER].x, lm[RIGHT_EYE_OUTER].y])
        return float(np.linalg.norm(re - le)) + 1e-6

    @staticmethod
    def _brow_distance(lm, scale: float) -> float:
        lb = np.array([lm[INNER_BROW_LEFT].x, lm[INNER_BROW_LEFT].y])
        rb = np.array([lm[INNER_BROW_RIGHT].x, lm[INNER_BROW_RIGHT].y])
        return float(np.linalg.norm(rb - lb)) / scale

    @staticmethod
    def _lip_separation(lm, scale: float) -> float:
        top = np.array([lm[LIP_TOP_INNER].x, lm[LIP_TOP_INNER].y])
        bot = np.array([lm[LIP_BOTTOM_INNER].x, lm[LIP_BOTTOM_INNER].y])
        return float(np.linalg.norm(top - bot)) / scale

    @staticmethod
    def _lip_corner_offset(lm, scale: float) -> float:
        center_y = (lm[LIP_TOP_INNER].y + lm[LIP_BOTTOM_INNER].y) / 2.0
        corner_y = (lm[LIP_LEFT_CORNER].y + lm[LIP_RIGHT_CORNER].y) / 2.0
        return float(corner_y - center_y) / scale

    @staticmethod
    def _eye_opening(lm, scale: float) -> float:
        l_gap = abs(lm[LEFT_EYE_TOP].y - lm[LEFT_EYE_BOTTOM].y)
        r_gap = abs(lm[RIGHT_EYE_TOP].y - lm[RIGHT_EYE_BOTTOM].y)
        return float((l_gap + r_gap) / 2.0) / scale

    def calibrate(self, jitter: float, brow_d: float, lip_s: float, lip_co: float, eye_o: float) -> bool:
        self._cal_jitters.append(jitter)
        self._cal_brow_dists.append(brow_d)
        self._cal_lip_seps.append(lip_s)
        self._cal_lip_corner_ys.append(lip_co)
        self._cal_eye_openings.append(eye_o)
        if len(self._cal_jitters) >= self.CAL_FRAMES:
            self.base_noise        = float(np.percentile(self._cal_jitters, 90))
            self.base_brow_dist    = float(np.median(self._cal_brow_dists))
            self.base_lip_sep      = float(np.median(self._cal_lip_seps))
            self.base_lip_corner_y = float(np.median(self._cal_lip_corner_ys))
            self.base_eye_opening  = float(np.median(self._cal_eye_openings))
            self.is_calibrated = True
            print(f"[Stress L1] Calibrated noise={self.base_noise:.4f} brow={self.base_brow_dist:.3f}")
            return True
        return False

    def analyze(self, image, calibrating: bool = False) -> dict:
        rgb    = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)

        if not result.multi_face_landmarks:
            return {
                "raw_jitter": 0.0,
                "brow_d": 0.0,
                "lip_s": 0.0,
                "lip_co": 0.0,
                "eye_o": 0.0,
                "grimace_raw": 0.0,
                "stress_score": 0.0,
                "is_calibrated": self.is_calibrated
            }

        lm = result.multi_face_landmarks[0].landmark
        self._head_scale = self._inter_eye(lm)

        brow_d = self._brow_distance(lm, self._head_scale)
        lip_s  = self._lip_separation(lm, self._head_scale)
        lip_co = self._lip_corner_offset(lm, self._head_scale)
        eye_o  = self._eye_opening(lm, self._head_scale)

        pts = np.array([[lm[i].x, lm[i].y] for i in KEY_IDS], dtype=np.float64)
        pts_n = pts / self._head_scale

        if self._prev_points is None:
            self._prev_points = pts_n
            raw_jitter = 0.0
        else:
            velocity = np.linalg.norm(pts_n - self._prev_points, axis=1)
            raw_jitter = float(np.min(velocity))  # Meilleure discrimination
            self._prev_points = pts_n

        if calibrating:
            self.calibrate(raw_jitter, brow_d, lip_s, lip_co, eye_o)
            return {"calibrating": True, "progress": len(self._cal_jitters) / self.CAL_FRAMES}

        # Calculate a single grimace instantaneous score component here to avoid sending all baselines
        # IMPROVED: Lowered triggers for better sensitivity
        brow_ratio = brow_d / (self.base_brow_dist + 1e-6)
        brow_score = min(100.0, max(0.0, (1.0 - brow_ratio) * 350.0))  # SENSITIVE (was 200)

        lip_ratio = lip_s / (self.base_lip_sep + 1e-6)
        lip_press_score = min(100.0, max(0.0, (1.0 - lip_ratio) * 200.0))  # SENSITIVE (was 150)

        # Frown detection (mouth corners down)
        corner_drop = max(0.0, lip_co - self.base_lip_corner_y)
        frown_score = min(100.0, corner_drop * 4500.0) # SENSITIVE (was 3000)

        eye_ratio = eye_o / (self.base_eye_opening + 1e-6)
        squint_score = min(100.0, max(0.0, (1.0 - eye_ratio) * 300.0)) # SENSITIVE (was 150)

        # Use max() for parts of the grimace to catch the strongest signal
        grimace_raw = (0.40 * brow_score + 0.15 * lip_press_score + 0.15 * frown_score + 0.30 * squint_score)
        grimace_raw = max(grimace_raw, brow_score * 0.7, squint_score * 0.7)

        # IMPROVED: Calcul du stress score (0-100)
        jitter_score = min(100.0, max(0.0, (raw_jitter / (self.base_noise + 1e-6) - 1.0) * 50.0))
        
        # Combinaison pour stress robuste
        stress_score = (0.60 * grimace_raw + 0.40 * jitter_score)
        stress_score = min(100.0, max(0.0, stress_score))

        return {
            "raw_jitter": round(raw_jitter, 6),
            "grimace_raw": round(grimace_raw, 2),
            "stress_score": round(stress_score, 2),
            "brow_d": round(brow_d, 4),
            "lip_s": round(lip_s, 4),
            "eye_o": round(eye_o, 4),
            "base_noise": self.base_noise,
            "is_calibrated": self.is_calibrated
        }
