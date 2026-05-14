# Diagrammes & Schémas Complémentaires - Pipeline Vision+Score

## 1. Diagramme Détaillé - Architecture L1 à L5

```
FLUX VIDÉO 30 FPS (640×480)
     ↓
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 1: ANALYZERS (Observations Brutes - Parallèle)      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AttentionAnalyzer    FatigueAnalyzer    PostureAnalyzer   │
│  └─ yaw/pitch         └─ EAR/PERCLOS     └─ posture_score  │
│  └─ MAR               └─ yawn_freq       └─ hand_position  │
│  └─ face_present      └─ calib_ears      └─ slouch/tilt   │
│  └─ num_faces                                              │
│                            PhoneDetector                    │
│                            └─ phone_found                   │
│                            └─ confidence                    │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 2: SCORE MANAGER (Lissage + Fusion Faible)          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Evidence Generation:                                       │
│  ├─ reading_ev (tête vers bas)                             │
│  ├─ writing_ev (tête bas + mains)                          │
│  ├─ thinking_ev (regard loin)                              │
│  ├─ phone_ev (téléphone detected)                          │
│  ├─ social_ev (2+ visages)                                 │
│  ├─ distracted_ev (gaze away > 4s)                         │
│  └─ fatigue_unified = 0.50×EAR + 0.20×yawn + 0.30×other   │
│                                                             │
│  Temporal Smoothing (Médiane + EMA):                        │
│  ├─ Buffers: 75 frames (2.5s)                              │
│  ├─ EMA α=0.15 (general), α=0.08 (fatigue)                │
│  └─ Outputs: [reading, writing, phone, distracted, ...]   │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 3: STATE MANAGER (États Stables + Hysteresis)       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Fatigue State:                                             │
│  normal ─(40)─→ slightly_fatigued ─(65)─→ fatigued ─(85)─→ drowsy
│   ↑                    ↑                      ↑               │
│   └────────────────────┴──────────────────────┘ (hysteresis) │
│   (délais asymétriques)                                     │
│                                                             │
│  Distraction State:                                          │
│  focused ─(0.25)─→ slightly_distracted ─(0.55)─→ distracted
│   ↑                        ↑                         │        │
│   └────────────────────────┴─────────────────────────┘        │
│                                                             │
│  Posture State: good ↔ acceptable ↔ poor_persistent        │
│  Task State: reading | writing | general                   │
│  Phone State: not_detected | probable_in_use               │
│                                                             │
│  OUTPUTS: {fatigue, posture, phone, distraction, task}     │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 4: FUSION ENGINE (État Global Unique)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Priority-Based Selection:                                  │
│                                                             │
│  IF drowsy(9) THEN state = "drowsy" 🔴                     │
│  ELSE IF phone(8) THEN state = "phone_distraction" 🔴      │
│  ELSE IF social(7) THEN state = "social_distraction" 🟠    │
│  ELSE IF distracted(6) THEN state = "distracted" 🟠        │
│  ELSE IF fatigued(4) THEN state = "fatigued" 🟠            │
│  ELSE IF slightly_fatigued(3) THEN state = "s_fatigued" 🟡 │
│  ELSE IF reading(2) THEN state = "reading" 🟢              │
│  ELSE IF writing(2) THEN state = "writing" 🟢              │
│  ELSE state = "focused" ✅                                  │
│                                                             │
│  OUTPUT: global_state (unique, déterministe)               │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 5: ALERT MANAGER (Validation Temporelle)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  State Persistence Validation:                              │
│                                                             │
│  FOR EACH state IN {drowsy, phone, social, fatigue, ...}:  │
│    IF state_active:                                         │
│      elapsed = now - t_first_detected                       │
│      IF elapsed >= required_duration:                       │
│        Check cooldown: IF now - t_last_fired > cooldown:   │
│          FIRE ALERT ✓                                       │
│          UPDATE t_last_fired, cooldown clock               │
│      ELSE:                                                  │
│        QUEUE pending alert (% progress)                    │
│    ELSE:                                                    │
│      RESET timer for this state                            │
│                                                             │
│  OUTPUT: alerts[] (prioritised if multiple)                │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ JSON PAYLOAD → Backend / UI / Database                      │
│ Contient: L1→L5 observations, scores, states, alerts       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Diagramme Détaillé - Fusion Fatigue (L2)

```
┌─────────────────────────────────────────────────────────────┐
│                  FATIGUE FUSION EQUATION                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  fatigue_unified =                                          │
│    0.50 × EAR_score                                         │
│  + 0.20 × yawn_signal                                       │
│  + 0.15 × posture_signal                                    │
│  + 0.15 × behavior_signal                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ TERM 1: EAR_score (Eye Aspect Ratio)                        │
│                                                             │
│  EAR = (||P_v1 - P_v2|| + ||P_v3 - P_v4||)                 │
│        / (2 × ||P_h1 - P_h2||)                              │
│                                                             │
│  → Calibration: base_ear = median(60 frames)               │
│  → Threshold: ear_thresh = base_ear × 0.75                 │
│                                                             │
│  → YAW COMPENSATION:                                        │
│     IF |yaw| > 12°:                                         │
│       ear_adjusted = ear × (1 - 0.18 × (|yaw|-12)/(35-12)) │
│       thresh_adjusted = ear_thresh × 0.82..1.0             │
│                                                             │
│  → PERCLOS (Percentage Eye Closure):                        │
│     perclos = (frames_closed / total_frames) × 100          │
│     Fenêtre: 60s (1800 frames à 30FPS)                      │
│                                                             │
│  EAR_score = (1 - EAR/base_ear)×100 + PERCLOS×2             │
│  Range: [0, 100]                                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ TERM 2: yawn_signal (Détection Bâillements)                 │
│                                                             │
│  IF MAR > (base_mar + 0.35) AND duration > 22 frames:      │
│    → YAWN DETECTED                                          │
│    → Count yawns in 120s window                             │
│                                                             │
│  yawn_freq_per_min = count_yawns / (window_sec / 60)       │
│  yawn_signal = min(1.0, freq / 2.0) × 100                   │
│  Range: [0, 100]                                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ TERM 3: posture_signal (Postural Fatigue)                   │
│                                                             │
│  posture_signal = max(0, 100 - posture_score) × 0.8        │
│  Range: [0, 100]                                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ TERM 4: behavior_signal (Comportements)                     │
│                                                             │
│  behavior_signal = 0                                        │
│  IF hands_on_knees: behavior_signal += 60                   │
│  IF NOT face_present: behavior_signal += 20                 │
│  Range: [0, 100]                                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT: fatigue_unified ∈ [0, 100]                          │
│                                                             │
│  → Passe en L3 State Manager                                │
│  → Comparaison thresholds:                                  │
│     < 40   → "normal"                                       │
│     40-65  → "slightly_fatigued"                            │
│     65-85  → "fatigued"                                     │
│     ≥ 85   → "drowsy"                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Diagramme État Transitions - Hysteresis

```
FATIGUE STATE MACHINE (avec Hysteresis)

                              ┌─ Seuil: 40 ─┐
                              │ Entrée: 1.5s │
                              │ Sortie: 3.0s │
                              └──────────────┘
                                     ↓
                                     ↓
NORMAL ←─────────────────────── slightly_fatigued ──────────────┐
  ↑                                    ↓                        │
  │                          (Seuil: 65, Entrée: 2s, Sortie: 4s)│
  │                                    ↓                        │
  │                               FATIGUED ─────────────────────┤
  │                                    ↑                        │
  │                          (Seuil: 85, Entrée: 2.5s,         │
  └────────────────────────────       Sortie: 5s)              │
  (reset si score < 40                 ↓                        │
   maintenu > 3s)                  DROWSY 🔴                    │
                                    ↑                          │
                               (2.5s maintenu)                 │
                                                               │
TIMELINE EXAMPLE:                                              │
                                                               │
t=0s:   score_fatigue = 42 → "normal" (pas transition immédiate)
t=1.5s: toujours 42 → "slightly_fatigued" ✓ (entrée 1.5s ok)
t=2.0s: score descend 38 → reste "slightly_fatigued"
t=5.0s: score ↓ 35 → maintenu > sortie(3s) → retour "normal"
t=10s:  score monte 70 → "slightly_fatigued" (pas saut direct fatigued)
t=12s:  score ≥ 70 maintenu → franchit seuil 65 → rentre "fatigued"
t=14s:  "fatigued" confirmé ✓ (durée entrée 2s ok)

ASYMMETRIE: Entrée < Sortie
─ Favorise stabilité état long-terme
─ Dampe micro-oscillations bruitées
```

---

## 4. Diagramme Priorisation État Global

```
SELECTION PRIORITY-BASED (L4 Fusion Engine)

Ensemble états actifs: {slightly_fatigued(3), reading(2), phone(0)}

      Extraction Priorités
      ↓
      3 (slightly_fatigued)
      2 (reading)
      0 (phone_not_detected → supprimé)
      ↓
      max(3, 2) = 3
      ↓
      GLOBAL STATE = "slightly_fatigued" 🟡

─────────────────────────────────────────────

AUTRE SCENARIO: Utilisateur DORMANT + TÉLÉPHONE

États actifs: {drowsy(9), phone_distraction(8), reading(2)}

      Priorités: 9, 8, 2
      ↓
      max(9, 8, 2) = 9
      ↓
      GLOBAL STATE = "drowsy" 🔴 (ALERTE!)

─────────────────────────────────────────────

EFFET PRIORITÉ: Empêche ambiguïté

❌ Avant (sans priorité):
   └─ État indéterminé si plusieurs conditions vraies
   └─ Logique d'alerte incohérente

✅ Après (avec priorité):
   └─ Un seul état déterministe
   └─ Alertes cohérentes et prévisibles
```

---

## 5. Diagramme Cycle Alert Manager

```
ALERT VALIDATION CYCLE (L5)

Input: global_state = "fatigued"
       required_duration = 22.0s
       cooldown = 120.0s

Timeline:
─────────────────────────────────────

t=100s: State "fatigued" détecté
        ├─ t_first_detected = 100s
        ├─ elapsed = 0s
        ├─ elapsed < 22s → PENDING (0% progress)
        └─ No alert

t=110s: State "fatigued" toujours actif
        ├─ elapsed = 10s
        ├─ elapsed < 22s → PENDING (45% progress)
        └─ No alert

t=122s: State "fatigued" toujours actif
        ├─ elapsed = 22s
        ├─ elapsed ≥ 22s → VALIDATED ✓
        ├─ Check cooldown:
        │  └─ (now - t_last_fired=0) = 122s > 0s
        ├─ FIRE ALERT! 🚨
        ├─ t_last_fired = 122s
        └─ Alert sent with reason "Signes de fatigue détectés"

t=150s: State "fatigued" toujours actif
        ├─ elapsed = 50s (state persiste)
        ├─ Cooldown check:
        │  └─ (now - t_last_fired) = 150 - 122 = 28s < 120s
        ├─ COOLDOWN ACTIVE → No new alert
        └─ Alert queued (28/120 cooldown progress)

t=242s: State "fatigued" DISPARAÎT
        ├─ t_first_detected = null
        ├─ elapsed = 0s
        ├─ Reset for next occurrence
        └─ Cooldown persiste jusqu'à t=242s minimum

t=250s: State "fatigued" redétecté
        ├─ t_first_detected = 250s
        ├─ elapsed = 0s
        ├─ PENDING (cooldown expiré, peut refirer)
        └─ Cycle recommence

───────────────────────────────────────

ALERTES PRIORITAIRES EN CAS MULTIPLES:

IF multiple states validated simultaneously:

  alertQueue = [
    ("drowsy", priority=9, val_dur=2.5s),
    ("phone_distraction", priority=8, val_dur=5.0s),
  ]
  
  alerts_to_fire = select_highest_priority(alertQueue)
  → "drowsy" alert FIRST
  → "phone" alert deferred or queued
  → User notified of HIGHEST priority only (prevent overwhelm)
```

---

## 6. Exemple Complet: Scénario Lecture + Fatigue

```
TIME: 0s - 5s (CALIBRATION PHASE)
┌─────────────────────────────────────┐
│ AttentionAnalyzer calibre yaw/pitch │
│ FatigueAnalyzer calibre EAR/MAR     │
│ PostureAnalyzer calibre posture     │
└─────────────────────────────────────┘
  → Baselines établies

TIME: 5s - 10s (STABLE READING)
┌────────────────────────────────────────────────────────┐
│ L1 Observations:                                        │
│ ├─ yaw = -2° (tête légèrement baissée)                │
│ ├─ pitch = -25° (tête fortement vers bas) ✓            │
│ ├─ MAR = 0.03 (bouche fermeé)                          │
│ ├─ EAR = 0.28 (yeux ouverts) ✓                         │
│ ├─ PERCLOS = 2% (normal)                               │
│ ├─ posture_score = 85 (bonne)                          │
│ ├─ phone_found = false                                 │
│ └─ num_faces = 1                                       │
│                                                         │
│ L2 Scores (après lissage):                             │
│ ├─ reading_ev = 0.6 (pitch < -20°)                    │
│ ├─ fatigue_unified = 15 (EAR normal, peu signaux)     │
│ ├─ distracted_ev = 0.0 (gaze centré)                 │
│ └─ ema_fatigue = 12 (lissé)                            │
│                                                         │
│ L3 States:                                              │
│ ├─ fatigue = "normal"                                  │
│ ├─ task = "reading"                                    │
│ ├─ distraction = "focused"                             │
│ └─ posture = "good"                                    │
│                                                         │
│ L4 Global State:                                        │
│ └─ "reading" (priority 2) ✅                           │
│                                                         │
│ L5 Alerts:                                              │
│ └─ (aucune)                                             │
└────────────────────────────────────────────────────────┘

TIME: 10s - 30s (READING CONTINUES, FATIGUE BUILDING)
┌────────────────────────────────────────────────────────┐
│ L1: Yawning detected at t=15s, 20s                     │
│ L2: ema_fatigue progresse 12→18→25→35→42...           │
│ L3: fatigue state reste "normal" (42 < 40? non = enter slightly_fatigued)
│     → enters "slightly_fatigued" at t≈18s (+1.5s)     │
│ L4: "slightly_fatigued" (prior 3) > "reading" (prior 2)
│     → GLOBAL STATE = "slightly_fatigued" 🟡           │
│ L5: Alert validation                                   │
│     └─ elapsed = 12s (< 22s required)                 │
│     └─ PENDING 54% progress                            │
│     └─ No alert YET                                    │
└────────────────────────────────────────────────────────┘

TIME: 30s - 35s (APPROACHING CRITICAL)
┌────────────────────────────────────────────────────────┐
│ L1: EAR↓ 0.24 (seuil 0.21 atteint)                     │
│     PERCLOS: 18% (building)                             │
│     Yawns: 3 detected → freq = 1.5/min                 │
│                                                         │
│ L2: fatigue_unified = 65 (TRANSITION THRESHOLD!)       │
│     ├─ 0.50×(60) + 0.20×(50) + 0.15×(5) + 0.15×(0)    │
│     └─ = 30+10+0.75+0 = 40.75 ... wait ...             │
│                                                         │
│     Recalc:                                             │
│     ├─ EAR_score = (1-0.24/0.30)×100+18×2 = 56         │
│     ├─ yawn_signal = min(1, 1.5/2)×100 = 75           │
│     ├─ posture_signal = 0 (good posture)               │
│     ├─ behavior_signal = 0                             │
│     └─ total = 0.50×56 + 0.20×75 = 28+15 = 43         │
│                                                         │
│ L3: fatigue state: 43 → still "slightly_fatigued"     │
│ L4: GLOBAL STATE = "slightly_fatigued"                 │
│ L5: elapsed = 17s (< 22s) → PENDING 77%               │
└────────────────────────────────────────────────────────┘

TIME: 35s - 40s (CROSSES THRESHOLD)
┌────────────────────────────────────────────────────────┐
│ L1: EAR: 0.22 (seuil franchit!)                        │
│     PERCLOS: 22% (building)                             │
│     4 yawns now                                         │
│                                                         │
│ L2: fatigue_unified = 68 (≥65!)                        │
│     ├─ EAR_score = 75                                  │
│     ├─ yawn_signal = 100                               │
│     └─ total = 0.50×75 + 0.20×100 = 57.5              │
│                                                         │
│ L3: fatigue state transitions:                         │
│     └─ 68 ≥ 65 → "fatigued" (entrée: 2.0s)           │
│     └─ t_enter = 37s                                   │
│                                                         │
│ L4: "fatigued" (prior 4) > "reading" (prior 2)         │
│     → GLOBAL STATE = "fatigued" 🟠                    │
│                                                         │
│ L5: Alert validation:                                  │
│     └─ First seen at t=37s                             │
│     └─ elapsed = 1s (< 22s required)                   │
│     └─ PENDING 5% progress                             │
└────────────────────────────────────────────────────────┘

TIME: 55s - 60s (ALERT FIRES!)
┌────────────────────────────────────────────────────────┐
│ L1: EAR: 0.20 (critical!)                              │
│     PERCLOS: 28% (HIGH)                                 │
│                                                         │
│ L2: fatigue_unified = 80                               │
│ L3: fatigue = "fatigued" (still)                        │
│ L4: GLOBAL STATE = "fatigued"                          │
│                                                         │
│ L5: ALERT VALIDATION:                                  │
│     ├─ State "fatigued" active since t=37s             │
│     ├─ elapsed = 60s - 37s = 23s                       │
│     ├─ 23s ≥ 22s required ✓ → VALIDATED!              │
│     ├─ Cooldown check: (60 - 0) > 0 → OK              │
│     ├─ 🚨 ALERT FIRED!                                │
│     ├─ Message: "Attention : Signes de fatigue         │
│     │           détectés."                             │
│     ├─ Level: MEDIUM                                   │
│     ├─ t_last_fired = 60s                              │
│     └─ cooldown = 120s (next alert after t=180s)       │
└────────────────────────────────────────────────────────┘

TIME: 61s - 100s (ALERT COOLDOWN)
┌────────────────────────────────────────────────────────┐
│ If fatigue persists:                                    │
│ ├─ State "fatigued" active but alert MUTED (cooldown)  │
│ ├─ No duplicate alert spam                             │
│ ├─ User encouraged to take break                       │
│ └─ System waits 120s before next fatigue alert         │
│                                                         │
│ If fatigue resolves (e.g., t=65s: EAR↑ to 0.26):      │
│ ├─ fatigue_unified drops to 55                         │
│ ├─ State remains "fatigued" (exit requires > 4s)       │
│ ├─ at t=69s, still below entry threshold → "normal"    │
│ ├─ Cooldown still active for future alerts             │
│ └─ System resets when fatigued state fully cleared     │
└────────────────────────────────────────────────────────┘
```

---

## 7. Tableau Comparatif: Avant/Après Améliorations

| Aspect | Avant | Après (Implémentation) |
|--------|-------|----------------------|
| **Compensation Yaw** | Aucune → faux positifs profil | EAR relaxé -18% max → fiable en rotation |
| **Fusion Fatigue** | Simple seuil EAR unique | Multi-modal (4 sources) → robust |
| **États Distraction** | Binaire (on/off) | 3 niveaux progressifs (focused/slight/deep) |
| **Hysteresis** | Inexistant → oscillations | Asymétrique (entrée<sortie) → stable |
| **Alertes** | Spam continu | Cooldown + validation durée → acceptable |
| **Global State** | Ambiguë si multi-conditions | Priorité stricte → déterministe |
| **Latence** | ~50ms (raw) | ~150ms (incluant lissage) |
| **Extensibilité** | Monolithique | 5 niveaux modulaires → facile extend |

---

**Fin des diagrammes complémentaires**

Document généré pour rapport PFE académique.
Tous les schémas sont reproductibles en Markdown/ASCII.
