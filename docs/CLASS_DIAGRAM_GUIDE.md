# 📊 Diagramme de Classe - Vision + Score Pipeline

## 📥 Comment Ouvrir le Diagramme

**Fichier** : `docs/vision_score_class_diagram.drawio`

### Option 1 : Draw.io Web (Recommandé)
1. Allez sur [draw.io](https://draw.io)
2. **File** → **Open from** → **Device**
3. Sélectionnez `vision_score_class_diagram.drawio`
4. Diagramme s'ouvre avec toutes les fonctionnalités (edit, export, etc.)

### Option 2 : VS Code
- Installez extension **Draw.io Integration** (hediet.vscode-drawio)
- Clic droit sur `.drawio` → **Open with Draw.io**

### Option 3 : Exporter en Image
**Dans Draw.io** :
- **File** → **Export as** → **PNG** / **SVG** / **PDF**
- ✅ Format prêt pour rapport

---

## 🎨 Structure du Diagramme

Le diagramme montre l'architecture complète **UML Class Diagram** organisée en **6 sections** :

### **Sections Couleur (Code de couleur)**

| Couleur | Niveau | Classes | Rôle |
|---------|--------|---------|------|
| 🟢 Vert | **L1** | AttentionAnalyzer, FatigueAnalyzer, PostureAnalyzer, PhoneDetector | Observations brutes instantanées |
| 🟣 Violet | **L2** | ScoreManager | Lissage + fusion faible |
| 🟡 Orange | **L3** | HysteresisManager, StateManager | États stables + damping oscillations |
| 🔴 Rouge | **L4** | FusionEngine | État global unique prioritaire |
| 🔴 Rouge | **L5** | AlertManager | Validation temporelle + cooldown |
| 🟤 Marron | **Orch** | TemporalEngine | Orchestration L1→L5 |
| 🟦 Cyan | **Main** | SmartFocusPipelineV3 | Entry point + gestion caméra |
| 🔵 Bleu | **Model** | CVOutputPayload | Format sortie JSON |

---

## 🔗 Relations & Fluxes

### Hiérarchie d'Appels

```
SmartFocusPipelineV3 (main)
  ↓
TemporalEngine (orchestration)
  ├─→ [attaque L1 Analyzers]
  ├─→ ScoreManager (L2)
  ├─→ StateManager (L3)
  │    ├─ HysteresisManager (damping)
  ├─→ FusionEngine (L4)
  ├─→ AlertManager (L5)
  └─→ [crée] CVOutputPayload
```

### Types de Relations (Légende Diagramme)

| Symbole | Signification |
|---------|---------------|
| `─→ (trait continu)` | Appel direct / dépendance forte |
| `┆→ (tiret)` | Utilisation / composition |
| `uses` | Label relation |
| `creates` | Instanciation objet |

---

## 📦 Détail par Classe

### **L1 - Analyzers** (4 classes indépendantes)

#### AttentionAnalyzer
- **Attributs** :
  - `face_mesh` : MediaPipe FaceMesh detector
  - `base_yaw`, `base_pitch` : Calibration individuelle
  - `_cam_matrix`, `_dist_coeffs` : Paramètres PnP
  
- **Méthodes** :
  - `analyze(image)` : Détecte yaw/pitch/MAR/num_faces
  - `_head_pose()` : Résolution PnP → angles 3D
  - `calibrate()` : Baseline 60 frames

#### FatigueAnalyzer
- **Attributs** :
  - `base_ear` : Eye Aspect Ratio baseline
  - `ear_threshold` : Seuil fermeture yeux (calibré)
  - `_perclos_window` : Buffer 60s
  - `_yawn_counter` : Comptage bâillements
  
- **Méthodes** :
  - `analyze(image, yaw)` : Retourne EAR, PERCLOS, yawn_freq
  - `_yaw_compensated_threshold()` : Corrige EAR selon rotation tête
  - `_detect_yawning()` : Détecte bâillements (MAR > seuil + durée)

#### PostureAnalyzer
- **Attributs** :
  - `pose` : MediaPipe Pose (17 joints)
  - `base_vdist`, `base_shoulder_width` : Calibration posture
  - `_bad_history` : Buffer mauvaise posture (2.5s)
  
- **Méthodes** :
  - `analyze(image)` : Calcul posture_score (0-100)
  - `_check_hands_on_knees()` : Détecte effondrement
  - `_check_hand_near_face()` : Main près visage
  - `_compute_posture_score()` : Slouch + Tilt + Forward head

#### PhoneDetector
- **Attributs** :
  - `model` : YOLOv8n (léger, edge-friendly)
  - `confidence_threshold` : Seuil confiance
  - `skip_frames` : Exécuté 1 fois / 8 frames (perf)
  
- **Méthodes** :
  - `analyze(image)` : Détecte téléphone
  - `_detect_phone_yolo()` : Appel modèle YOLO

---

### **L2 - ScoreManager**

**Responsabilité** : Convertir L1 en signaux lissés [0, 1]

- **Attributs** :
  - `_signals` : Dict signaux (reading, writing, phone, distracted, etc.)
  - `_buffers` : Deques médiane mobile (75 frames = 2.5s)
  - `ema_fatigue`, `ema_posture` : Exponential Moving Average
  
- **Méthodes** :
  - `compute_scores(raw_data)` : Génère evidences + lissage
  - `_push_signal(key, value)` : Ajoute au buffer + EMA
  - `_push_ema()` : Calcul EMA (α=0.15 ou α=0.08 fatigue)

**Flux** :
```
L1 {yaw, pitch, EAR, ...}
  ↓
Evidence Generation {reading_ev=0.6, phone_ev=0.8, ...}
  ↓
Median Filter (75 frames)
  ↓
EMA (α dépend signal)
  ↓
L2 Output {reading: 0.65, phone: 0.8, ema_fatigue: 38.5, ...}
```

---

### **L3 - StateManager + HysteresisManager**

#### HysteresisManager
**Responsabilité** : Damper oscillations via délais asymétriques entrée/sortie

- **Attributs** :
  - `_timers` : Tracking quand état entre
  - `_validated_states` : State = validé si durée ≥ seuil
  - `_delays` : Dict {state: (delay_enter, delay_exit)}
  
- **Méthodes** :
  - `process(now, observations)` : Applique hysteresis
  - `_check_entry()` : now - t_first_entry ≥ delay_enter ?
  - `_check_exit()` : now - t_enter ≥ delay_exit ?

#### StateManager
**Responsabilité** : Mapper scores → états discrets

- **Attributs** :
  - `hysteresis` : Instance HysteresisManager
  - `current_states` : Dict {fatigue, distraction, posture, phone, task}
  
- **Méthodes** :
  - `compute_sub_states(now, scores, flags)` : Retourne 5 sub-états
  - `_compute_fatigue_target()` : Détermine cible (normal/slightly/fatigued/drowsy)
  - `_compute_distraction_target()` : focused/slightly/distracted
  - `_compute_posture_target()` : good/acceptable/poor

**Exemple Hysteresis** :
```
Fatigue: normal ←→ slightly_fatigued ←→ fatigued ←→ drowsy
Délais entrée: 1.5s    2.0s     2.5s
Délais sortie: 3.0s    4.0s     5.0s

Entrée < Sortie → dampe oscillation court-terme
```

---

### **L4 - FusionEngine**

**Responsabilité** : Fusionner 5 sub-états en UN état global déterministe

- **Attributs** :
  - `PRIORITY_MAP` : dict priorités (drowsy=9, ..., focused=0)
  
- **Méthodes** :
  - `compute_global_state(sub_states, scores)` : max_priority(sub_states)
  - `_get_priority(state)` : Lookup priorité

**Hiérarchie Priorité** :
```
drowsy (9) > phone (8) > social (7) > distracted (6)
> slightly_distracted (5) > fatigued (4)
> slightly_fatigued (3) > reading/writing (2)
> posture (1) > focused (0)
```

**Garantie** : Déterministe, pas ambiguïté multi-conditions.

---

### **L5 - AlertManager**

**Responsabilité** : Valider états + cooldown avant alerte

- **Attributs** :
  - `_persistence_timers` : Quand état 1ère fois vu
  - `_last_fired_times` : Dernier tir alerte par type
  - `alert_configs` : Config [{key, condition, val_duration, cooldown, level, message}]
  
- **Méthodes** :
  - `evaluate(state)` → AlertStatus : Décide si alerte
  - `_update_persistence()` : Valide durée ≥ required
  - `_is_on_cooldown()` : Vérifie cooldown

**Cycle Alerte** :
```
State = "fatigued" depuis 22s+
  ├─ elapsed ≥ required_duration (22s) ? ✓
  ├─ cooldown expiré ? ✓
  └─ 🚨 FIRE ALERT
     └─ t_last_fired = now
     └─ cooldown = 120s (prochaine ≥ t+120s)
```

---

### **Orchestration - TemporalEngine**

**Responsabilité** : Pipeline L1→L5 complet, orchestration

- **Attributs** :
  - `session_id` : UUID session
  - `score_manager` : L2
  - `state_manager` : L3
  - `fusion_engine` : L4
  - `alert_manager` : L5
  - `_gaze_away_start` : Tracking distraction 
  
- **Méthodes** :
  - `process(att, fat, pos, phone)` → CVOutputPayload : Pipeline complet
  - `_head_direction()` : Détermine direction tête (left/right/up/down/frontal)
  - `_compute_raw_evidence()` : Génère evidences brutes L2
  - `_apply_distraction_logic()` : Gaze away > 4s = distraction

**Flux Processus** :
```
att = L1.attention.analyze(frame)
fat = L1.fatigue.analyze(frame, att.yaw)
pos = L1.posture.analyze(frame)
phone = L1.phone.analyze(frame)
  ↓
evidence = {reading_ev, phone_ev, fatigue_unified, ...}
  ↓
L2_scores = score_manager.compute_scores(evidence)
  ↓
L3_states = state_manager.compute_sub_states(now, L2_scores)
  ↓
L4_state = fusion_engine.compute_global_state(L3_states)
  ↓
L5_alerts = alert_manager.evaluate(consolidated_state)
  ↓
payload = CVOutputPayload(timestamp, L1-L5)
```

---

### **Main - SmartFocusPipelineV3**

**Responsabilité** : Gestion caméra, boucle principal, output backend

- **Attributs** :
  - `attention`, `fatigue`, `posture`, `phone` : 4 L1 Analyzers
  - `engine` : TemporalEngine (orchestration)
  - `cap` : cv2.VideoCapture (caméra)
  - `send_to_backend` : Flag envoi HTTP
  
- **Méthodes** :
  - `run(duration)` : Boucle principal (30 FPS)
  - `_calibrate()` : Calibration 3 secondes tous analyzers
  - `_process_frame(frame)` : Appel engine.process()
  - `_send_to_backend(payload)` : HTTP POST JSON

---

### **Data Model - CVOutputPayload**

**Responsabilité** : Structure JSON sortie complète

- **Attributs** :
  - `timestamp` : ISO 8601 (UTC)
  - `session_id` : UUID
  - `frame_index` : Numéro frame
  - `l1_observations` : {yaw, pitch, EAR, PERCLOS, fatigue_score, ...}
  - `l2_scores` : {reading, writing, phone, distracted, ema_fatigue, ...}
  - `l3_substates` : {fatigue, distraction, posture, phone, task}
  - `l4_global_state` : str (unique, prioritaire)
  - `l5_alerts` : list[] (validés alertes)

**Format JSON** :
```json
{
  "timestamp": "2025-05-11T14:23:45Z",
  "l1_observations": {...},
  "l2_scores": {...},
  "l3_substates": {...},
  "l4_global_state": "reading",
  "l5_alerts": [
    {"type": "fatigue_warning", "level": "medium", "message": "..."}
  ]
}
```

---

## 📐 Design Patterns Utilisés

| Pattern | Classe | Bénéfice |
|---------|--------|----------|
| **Cascade** | L1→L2→L3→L4→L5 | Séparation responsabilités, testable |
| **Composition** | TemporalEngine contient managers | Orchestration centralisée |
| **Strategy** | Analyzers indépendants | Plug&play, extension facile |
| **State Machine** | HysteresisManager | Damping oscillations |
| **Priority Queue** | FusionEngine PRIORITY_MAP | Déterminisme |
| **Observer** | AlertManager listeners | Notification événements |

---

## 🔄 Interaction Exemple

### Scénario : Utilisateur Lit + Montre Fatigue (t=0 à 40s)

```
t=0-5s CALIBRATION
├─ SmartFocus.run() → _calibrate()
├─ Analyzer.calibrate(image) × 60 frames
└─ Baseline établis (yaw=-1.2, pitch=0.5, EAR=0.30, etc.)

t=5-10s READING STABLE
├─ frame → TemporalEngine.process(L1_data)
├─ L1: {pitch=-25, EAR=0.28, PERCLOS=2%, posture=85}
├─ L2: {reading_ev=0.6, ema_fatigue=12}
├─ L3: {fatigue="normal", task="reading"}
├─ L4: "reading"
├─ L5: (aucune alerte)
└─ Output: CVOutputPayload(...)

t=15-25s FATIGUE BUILDING
├─ L1: {EAR↓=0.23, PERCLOS↑=12%, 2 yawns}
├─ L2: {ema_fatigue↑=35}
├─ L3: {fatigue="slightly_fatigued"} ← enter +1.5s
├─ L4: "slightly_fatigued" (prior 3 > reading prior 2)
├─ L5: Alert PENDING (elapsed 17/22s)
└─ Progress bar 77%

t=35-40s CRITICAL
├─ L1: {EAR=0.22, PERCLOS=22%, 4 yawns}
├─ L2: {ema_fatigue=68} ← ≥65 threshold
├─ L3: {fatigue="fatigued"} ← enter +2s
├─ L4: "fatigued"
├─ L5: Alert PENDING (elapsed 5/22s)
└─ Progress: 23%

t=40+ ALERTE !
├─ L5: elapsed ≥ 22s ✓
├─ L5: cooldown expired ✓
├─ 🚨 AlertManager.evaluate() → AlertStatus
├─ Message: "Attention : Signes de fatigue détectés"
├─ Level: MEDIUM (🟠)
├─ cooldown: 120s (next alert ≥ t=162s)
└─ Alert sent to backend
```

---

## 🎓 Utilisation dans Rapport PFE

### Comment Intégrer le Diagramme

1. **Ouvrir** le fichier `.drawio` dans Draw.io
2. **Export** en PNG/SVG haute résolution
3. **Insérer** dans rapport section **Architecture**

### Légende à Ajouter

```
"Diagramme 1: Architecture Classe Complete Vision+Score

Les 6 couches du système:
- L1 (Vert): 4 Analyzers independants (AttentionAnalyzer, FatigueAnalyzer, 
  PostureAnalyzer, PhoneDetector) extraient observables brutes
- L2 (Violet): ScoreManager lisse signals via median + EMA (2.5s buffer)
- L3 (Orange): StateManager + HysteresisManager créent états stables
  avec transitions asymétriques (damping oscillations)
- L4 (Rouge): FusionEngine fusionne 5 sub-états en UN état global
  selon hiérarchie prioritaire stricte
- L5 (Rouge): AlertManager valide états avec durée minimum +
  cooldown anti-spam
- Orchestration (Marron): TemporalEngine coordonne L1-L5 + JSON output
- Main (Cyan): SmartFocusPipelineV3 gère caméra + boucle principal"
```

---

## 💾 Fichier à Modifier

Si vous trouvez erreurs / omissions :
1. Ouvrir Draw.io
2. Open → `vision_score_class_diagram.drawio`
3. Éditer + sauvegarder
4. Re-export PNG pour rapport

---

**Prêt pour rapport académique PFE** ✅

Fichier generé : `docs/vision_score_class_diagram.drawio`
Format: Draw.io XML (éditable, exportable PNG/SVG/PDF)
