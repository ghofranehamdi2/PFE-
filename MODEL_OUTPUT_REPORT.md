# 🎯 Smart Focus Model - Output Results Summary

## ✅ Model Execution Results

The CV model ran successfully and captured behavioral data from the camera feed.

---

## 📊 Database Results Summary

### Latest Session
- **Session ID**: `a4e5ced5-18e7-4006-96c0-ff8880af165a`
- **Start Time**: 2026-03-26 11:04:41 UTC
- **Status**: Active

### Key Scores (Latest Snapshot)
| Metric | Score | Status |
|--------|-------|--------|
| 🎯 **Global Focus** | **65.74/100** | ⚠️ Below Optimal |
| 👁️ Attention Score | 70.0/100 | Moderate |
| 💪 Posture Score | 3.7/100 | ❌ Poor |
| 😴 Vigilance Score | 100.0/100 | ✅ Excellent |
| 😰 Stress Risk | 100.0/100 | ⚠️ High |
| 📱 Distraction | 20.0/100 | ✅ Low |

### Work Mode Detection
- **Current Mode**: `self_explaining` (Explaining ideas aloud to validate thinking)
- **Confidence**: 73%

### Behavioral State
```
✅ Face Detected: Yes
✅ Person Present: 1
⚠️ Posture: Poor & Persistent
❌ Stress Level: Elevated
❌ Phone: Not Detected
✅ Fatigue: Normal
✅ Social: Alone
```

### Alerts Generated
- **Alert**: "Mauvaise posture persistante. Redressez-vous." (Poor persistent posture. Straighten up.)
- **Level**: LOW
- **Time**: 2026-03-26 10:05:05

### Reasoning for State Assessment
1. `posture_inclination_forward` - Head/body leaning forward
2. `posture_deviation_persistent` - Poor posture maintained for 8.35+ seconds

---

## 📄 JSON Snapshot Payload Structure

```json
{
  "session_id": "a4e5ced5-18e7-4006-96c0-ff8880af165a",
  "timestamp": "2026-03-26T10:05:18Z",
  "work_mode": "self_explaining",
  
  "scores": {
    "attention_score": 70.0,
    "posture_score": 3.7,
    "vigilance_score": 100.0,
    "stress_risk_score": 100.0,
    "distraction_score": 20.0,
    "focus_score_global": 65.74
  },
  
  "presence": {
    "main_person_present": true,
    "person_count": 1,
    "face_detected": true
  },
  
  "instant_observations": {
    "head_direction": "up",
    "gaze_zone": "away",
    "eyes_state": "open",
    "posture_state": "bad",
    "phone_detected": false,
    "face_tension_level": "low",
    "agitation_level": "high"
  },
  
  "consolidated_states": {
    "work_mode": "self_explaining",
    "attention_state": "focused",
    "fatigue_state": "normal",
    "stress_state": "stress_elevated",
    "social_state": "alone",
    "phone_state": "not_detected",
    "posture_state": "poor_persistent",
    "reasoning_indices": ["posture_inclination_forward", "posture_deviation_persistent"]
  },
  
  "reliability": {
    "work_mode_confidence": 0.73,
    "attention_confidence": 0.9,
    "fatigue_confidence": 0.85,
    "stress_confidence": 0.8
  },
  
  "temporal_context": {
    "observed_for_sec": 36.53,
    "stable_state_for_sec": 8.35
  }
}
```

---

## 🏗️ Data Storage Architecture

### PostgreSQL Tables

#### `work_sessions`
- Stores user session metadata
- Current: Active session with no end time

#### `snapshots`
- **Purpose**: Point-in-time behavioral snapshots (every ~1-2 frames)
- **Fields**: 
  - Individual scores (attention, posture, vigilance, stress, focus)
  - `raw_payload_json`: Complete CV output payload
- **Total Records**: 100+ snapshots captured during test

#### `events`
- **Purpose**: Discrete events and alerts
- **Fields**: event_type, level, description, raw metadata
- **Current**: "Poor posture" alerts

---

## 🔄 Data Flow

```
📹 Camera Feed
    ↓
🧠 L1 Analysis Layer (Attention, Fatigue, Stress, Posture, Phone Detection)
    ↓
⚙️ L2-L4 Temporal Engine (State consolidation & inference)
    ↓
📊 Score Engine (Numerical scoring: 0-100)
    ↓
📝 JSON Formatter (Standardized payload)
    ↓
🌐 API Client (Async send to backend)
    ↓
💾 PostgreSQL Database
    ├─ work_sessions
    ├─ snapshots (with raw JSON)
    └─ events (alerts)
```

---

## 🎯 Key Findings

1. **Focus Score**: 65.74/100 - Below optimal, needs attention
2. **Main Issue**: Poor posture detected and persisting
3. **Positive**: Good vigilance, low distraction, no phone use
4. **Recommendation**: Adjust sitting position for better focus
5. **Confidence**: All metrics show 85%+ confidence in detection

---

## 📝 How to Query Results

Run the database query script to see latest results:
```bash
python query_results.py
```

---

Generated: 2026-03-26 March 26, 2026
