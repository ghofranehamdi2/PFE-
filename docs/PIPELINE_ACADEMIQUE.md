# Pipeline Complet d'Analyse de Concentration Vidéo
## Vision + Score System - Rapport PFE

---

## 1. Introduction Générale

Ce système implémente une architecture modulaire en **5 niveaux** pour transformer un flux vidéo temps réel (30 FPS) en décisions intelligentes de focus, fatigue et distraction. Chaque niveau construit sur les observations précédentes avec une progressivité croissante de la stabilité temporelle et de la contextualisation.

### Flux Général

```
Flux Vidéo (30 FPS) → L1 Analyzers → L2 Scores → L3 States → L4 Global State → L5 Alerts → JSON Output
```

---

## 2. Niveau 1 : Analyzers (L1) - Observations Instantanées

### Architecture Générale

Quatre analyseurs indépendants extraient des caractéristiques faciales et posturales via **MediaPipe** et **YOLO**, opérant en parallèle sur chaque frame sans état persistant.

### 2.1 AttentionAnalyzer

**Objectif** : Extraire l'orientation du regard et les signaux de communication.

**Entrées** :
- Frame RGB capturée par la caméra
- Calibration optionnelle (60 frames initiaux)

**Sorties** :
| Métrique | Type | Plage | Description |
|----------|------|-------|-------------|
| `yaw` | float | [-90, +90]° | Rotation horizontale tête (négatif=gauche) |
| `pitch` | float | [-90, +90]° | Rotation verticale tête (négatif=haut) |
| `MAR` | float | [0, 0.5] | Mouth Aspect Ratio (0=fermée, 0.5=grande ouverture) |
| `face_present` | bool | {0, 1} | Visage détecté dans le frame |
| `num_faces` | int | [0, 3+] | Nombre de visages (indicateur social) |

**Méthode** :
1. Détection faciale : MediaPipe FaceMesh (468 landmarks)
2. Extraction 6 points clés : nez, menton, coins yeux, commisures lèvres
3. Résolution PnP (Perspective-n-Point) via `cv2.solvePnP()` pour angles 3D
4. **Calibration** : Médiane (yaw, pitch) sur 60 frames; base utilisée pour normalisation relative

**Éq. MAR** :
$$\text{MAR} = \frac{\|P_{top} - P_{bottom}\|_{vertical} + \|P_{top} - P_{bottom}\|_{vertical2}}{2 \times \|P_{left} - P_{right}\|_{horizontal}}$$

---

### 2.2 FatigueAnalyzer

**Objectif** : Quantifier l'état de fatigue et de vigilance oculaire.

**Entrées** :
- Frame RGB
- `yaw` optionnel (depuis AttentionAnalyzer) pour correction adaptive

**Sorties** :
| Métrique | Type | Plage | Description |
|----------|------|-------|-------------|
| `fatigue_score` | float | [0, 100] | Score synthétique fatigue |
| `yawn_frequency_per_min` | float | [0, ∞) | Nombre yawns par minute (détecté) |
| `eye_closed_ratio` (PERCLOS) | float | [0, 1] | Ratio temps yeux fermés (fenêtre 60s) |
| `is_calibrated` | bool | {0, 1} | État calibration |

**Calcul Principal** :

1. **Eye Aspect Ratio (EAR)** : Mesure l'ouverture des yeux
   $$\text{EAR} = \frac{\|P_{vert1} - P_{vert2}\| + \|P_{vert3} - P_{vert4}\|}{2 \times \|P_{horiz1} - P_{horiz2}\|}$$
   - Seuil nominal : 0.21 (calibré individuellement)
   
2. **Compensation Yaw** : Quand tête tourne, EAR diminue mécaniquement
   $$\text{EAR}_{adjusted} = \text{EAR} \times \left(1 - 0.18 \times \frac{|\text{yaw}| - 12°}{23°}\right)$$
   - Évite faux positifs fatigue en profil

3. **PERCLOS (Percentage Eye Closure)** : % temps yeux fermés (fenêtre 60s)
   $$\text{PERCLOS} = \frac{\text{frames\_eye\_closed}}{\text{total\_frames}} \times 100$$

4. **Yawn Detection** : Détecte bâillements soutenu
   - Seuil : MAR > (base_MAR + 0.35)
   - Durée minimale : 22 frames (~0.7s)
   - Fréquence sur fenêtre 120s

5. **Fusion Score Fatigue** (voir L2)

**Calibration** : Médiane EAR sur 60 frames; seuil = base_ear × 0.75

---

### 2.3 PostureAnalyzer

**Objectif** : Évaluer la qualité posturale et détecter comportements problématiques.

**Entrées** :
- Frame RGB
- Calibration posture (60 frames)

**Sorties** :
| Métrique | Type | Plage | Description |
|----------|------|-------|-------------|
| `posture_score` | float | [0, 100] | Score global posture (100=bonne) |
| `bad_posture_confirmed` | bool | {0, 1} | Mauvaise posture persistent > 2.5s |
| `hand_near_face` | bool | {0, 1} | Main détectée près visage |
| `hands_on_knees` | bool | {0, 1} | Mains sur genoux (effondrement) |
| `tilt_score` | float | [0, 1] | Score tilt/inclination tête |

**Modèle** : MediaPipe Pose (17 joints: nez, yeux, oreilles, épaules, coudes, poignets, hanches, genoux, chevilles)

**Calcul Posture** :
$$\text{posture\_score} = 100 - \left(\text{slouch}\_\text{penalty} + \text{tilt}\_\text{penalty} + \text{fwd\_head}\_\text{penalty}\right)$$

Où pénalités ∈ [0, 100] selon déviation vs calibration:
- **Slouch** : Incurvation colonne (~0.8× pénalité)
- **Tilt** : Inclinaison tête latérale (~2.0× pénalité)
- **Forward Head** : Tête penchée avant (~1.5× pénalité)
- **Lean** : Inclinaison latérale corps (~1.2× pénalité)

**Détection Comportements** :
- Hands on knees: `|wrist_y - hip_y| < 0.08` ET `|wrist_x - hip_x| < 0.10`
- Hand near face: `norm(wrist - nose) / shoulder_width < 0.20`

---

### 2.4 PhoneDetector

**Objectif** : Détecter présence téléphone en main.

**Entrées** :
- Frame RGB
- (Exécuté tous les 8 frames pour performance)

**Sorties** :
| Métrique | Type | Plage | Description |
|----------|------|-------|-------------|
| `phone_found` | bool | {0, 1} | Téléphone détecté |
| `confidence` | float | [0, 1] | Confiance YOLO |

**Modèle** : YOLOv8n (nano, optimisé edge)

---

## 3. Niveau 2 : Score Manager (L2) - Lissage & Fusion Faible

### 3.1 Evidence Generation

Les observations brutes L1 deviennent des **signaux d'évidence** normalisés [0, 1] :

| Signal | Calcul | Condition |
|--------|--------|-----------|
| `reading_ev` | 0.6 | pitch < -20° (tête vers le bas) |
| `writing_ev` | 0.5 + hand_weight | pitch < -20° ET mains proches |
| `thinking_ev` | 0.5 | yaw ∉ [-18°, 18°] (regard détourné) |
| `speech_ev` | min(1, MAR / 0.08) | MAR > 0.05 (parole) |
| `phone_ev` | 0.8 | phone_detected = True |
| `social_ev` | 1.0 | num_faces ≥ 2 |
| `distracted_ev` | 0.4 à 0.7 | looking_away > 2s à 4s |

### 3.2 Fatigue Fusion (Multi-modal)

$$\text{fatigue\_unified} = w_1 \times \text{EAR\_score} + w_2 \times \text{yawn\_signal} + w_3 \times \text{posture\_signal} + w_4 \times \text{behavior\_signal}$$

Où :
- $w_1 = 0.50$ : Eye metrics (EAR + PERCLOS + slow blinks)
- $w_2 = 0.20$ : Yawning frequency
- $w_3 = 0.15$ : Postural fatigue (slouch while motionless)
- $w_4 = 0.15$ : Behavioral signals (hands on knees, immobility)

**Détails** :
- `EAR_score` = (1 - EAR / base_EAR) × 100 + PERCLOS × 2
- `yawn_signal` = min(1.0, freq_yawns_per_min / 2.0) × 100
- `posture_signal` = max(0, 100 - posture_score) × 0.8
- `behavior_signal` = (hands_on_knees × 60) + (face_absent × 20)

### 3.3 Temporal Smoothing

Chaque signal passe par un buffer de lissage :

**Médiane Mobile** (75 frames ≈ 2.5s à 30 FPS) :
$$m_t = \text{median}(\text{buffer}_t)$$

**EMA (Exponential Moving Average)** :
$$\text{signal}_t = \alpha \times m_t + (1 - \alpha) \times \text{signal}_{t-1}$$

Où :
- $\alpha = 0.15$ pour signaux généraux (reading, writing, etc.)
- $\alpha = 0.08$ pour fatigue (plus conservateur)
- $\alpha = 0.10$ pour posture

**Phone** : Buffer ultra-rapide (6 frames) avec percentile 90

---

## 4. Niveau 3 : State Manager (L3) - États Stables avec Hysteresis

### 4.1 Hysteresis Manager

Empêche oscillations d'états en appliquant des **délais d'entrée/sortie asymétriques** :

$$\text{transition}(t) = \begin{cases}
\text{enter state if } (now - t_{last\_exit}) \geq \text{delay\_enter} \\
\text{exit state if } (now - t_{last\_enter}) \geq \text{delay\_exit}
\end{cases}$$

### 4.2 Sub-States Computation

#### **Fatigue State** (4 niveaux progressifs)

| État | Condition (EMA fatigue) | Délai Entrée | Délai Sortie |
|------|---------------------------|--------------|--------------|
| `normal` | < 40 | — | — |
| `slightly_fatigued` | [40, 65) | 1.5s | 3.0s |
| `fatigued` | [65, 85) | 2.0s | 4.0s |
| `drowsy` | ≥ 85 | 2.5s | 5.0s |

#### **Distraction State** (3 niveaux)

| État | Condition (score distracted) | Délai Entrée | Délai Sortie |
|------|-------------------------------|--------------|--------------|
| `focused` | < 0.25 | — | — |
| `slightly_distracted` | [0.25, 0.55) | 1.5s | 2.5s |
| `distracted` | ≥ 0.55 | 2.5s | 3.5s |

#### **Posture State**

| État | Condition (EMA posture) |
|------|--------------------------|
| `good` | ≥ 78 |
| `acceptable` | (30, 78) |
| `poor_persistent` | < 30 ET bad_posture_confirmed |

#### **Task State** (Reconnaissance contexte tâche)

| État | Condition |
|------|-----------|
| `reading` | reading_score > 0.45 ET reading > writing |
| `writing` | writing_score > 0.45 |
| `general` | défaut |

---

## 5. Niveau 4 : Fusion Engine (L4) - État Global Unique

### 5.1 Priority-Based Fusion

Les sub-états sont fusionnés en **UN SEUL état global** selon une **hiérarchie stricte de priorités** :

$$\text{GlobalState} = \arg\max_{\text{state}} \{ \text{Priority}(\text{state}) : \text{state active} \}$$

### 5.2 Hiérarchie de Priorités

| Rang | État | Priorité | Description |
|------|------|----------|-------------|
| 1 | `drowsy` | 9 | Microsleep imminent (CRITIQUE) |
| 2 | `phone_distraction` | 8 | Téléphone détecté (supprime self_explaining) |
| 3 | `social_distraction` | 7 | 2+ visages détectés |
| 4 | `distracted` | 6 | Regard détourné > 4s soutenu |
| 5 | `slightly_distracted` | 5 | Regard détourné 2-4s |
| 6 | `fatigued` | 4 | Fatigue avérée (65-85) |
| 7 | `slightly_fatigued` | 3 | Premiers signes (40-65) |
| 8 | `reading` | 2 | Tâche productive (tête bas) |
| 9 | `writing` | 2 | Tâche productive (tête bas + mains) |
| 10 | `posture_issue` | 1 | Mauvaise posture persistante |
| 11 | `focused` | 0 | État par défaut (sain) |

### 5.3 Exemple d'Application

Scénario : Utilisateur lit mais croise les mains sur les genoux
- Sub-états actifs : `reading` (2), `slightly_fatigued` (3), `acceptable_posture` (0)
- Fusion : **max(2, 3, 0) = 3** → État global = `slightly_fatigued` ⚠️

Scénario : Utilisateur sommeille + téléphone en main
- Sub-états actifs : `drowsy` (9), `phone_distraction` (8)
- Fusion : **max(9, 8) = 9** → État global = `drowsy` 🔴 (ALERTE IMMÉDIATE)

---

## 6. Niveau 5 : Alert Manager (L5) - Validation Temporelle

### 6.1 Persistence Validation

Chaque état global candidate doit être maintenu pendant une **durée minimale** avant génération d'alerte :

$$\text{validated}(t) = \begin{cases}
\text{False} & \text{si état inactif} \\
\text{True} & \text{si } (now - t_{first\_detected}) \geq \text{required\_duration} \\
\text{False} & \text{sinon}
\end{cases}$$

### 6.2 Configuration Alertes

| État | Val. Durée | Cooldown | Niveau | Message |
|------|-----------|----------|--------|---------|
| **drowsy** | 2.5s | 300s | 🔴 HIGH | Faites une pause immédiatement |
| **phone_distraction** | 5.0s | 5s | 🔴 HIGH | Attention : Utilisation du téléphone détectée |
| **social_distraction** | 8.0s | 5s | 🟠 MEDIUM | Note : Interaction sociale prolongée |
| **fatigued** | 22.0s | 120s | 🟠 MEDIUM | Attention : Signes de fatigue détectés |
| **distracted** | 12.0s | 5s | 🟠 MEDIUM | Rappel : Restez concentré sur votre tâche |
| **posture_issue** | 20.0s | 5s | 🟡 LOW | Améliorez votre posture |

### 6.3 Cooldown Management

Après une alerte, un **cooldown** est appliqué pour éviter spam :

$$\text{can\_fire}(t) = (now - t_{last\_fired}) > \text{cooldown\_period}$$

Exemple : Si alerte `fatigue_warning` déclenche à t=100s, prochaine alerte fatigue possible seulement après t=220s (cooldown 120s).

---

## 7. Sortie Finale : JSON Payload

Exemple de payload JSON transmis au backend à chaque cycle :

```json
{
  "timestamp": "2025-05-11T14:23:45.123Z",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "frame_index": 1234,
  
  "l1_observations": {
    "face_present": true,
    "num_faces": 1,
    "yaw": -5.2,
    "pitch": -18.5,
    "mar": 0.032,
    "fatigue_score": 42.3,
    "yawn_frequency_per_min": 0.5,
    "eye_closed_ratio_perclos": 18.2,
    "posture_score": 72.0,
    "hand_near_face": false,
    "hands_on_knees": false,
    "phone_found": false,
    "phone_confidence": 0.0
  },
  
  "l2_scores": {
    "reading": 0.65,
    "writing": 0.12,
    "thinking": 0.08,
    "speech": 0.02,
    "phone": 0.0,
    "social": 0.0,
    "distracted": 0.18,
    "ema_fatigue": 38.5,
    "ema_posture": 71.2
  },
  
  "l3_substates": {
    "fatigue": "slightly_fatigued",
    "posture": "acceptable",
    "phone": "not_detected",
    "distraction": "focused",
    "task": "reading"
  },
  
  "l4_global_state": "reading",
  
  "l5_alerts": [
    {
      "type": "fatigue_warning",
      "validated": false,
      "elapsed_duration": 15.2,
      "required_duration": 22.0,
      "level": "medium",
      "message": "Attention : Signes de fatigue détectés."
    }
  ]
}
```

---

## 8. Caractéristiques de Robustesse

| Aspect | Implémentation | Rationale |
|--------|-----------------|-----------|
| **Calibration Individuelle** | 60 frames baseline pour yaw/pitch/EAR/MAR | Adapte à morphologie unique |
| **Compensation Yaw** | EAR relaxé -18% max selon rotation tête | Évite faux positifs profil |
| **Hysteresis Asymétrique** | Entrée < Sortie (ex: 1.5s/3s) | Dampe oscillations, favorise stabilité |
| **Multi-modal Fusion** | 4 métriques indépendantes pour fatigue | Réduit faux positifs par redondance |
| **Smoothing Progressif** | Médiane + EMA en cascade | Élimine bruit temps-réel |
| **Priorité Stricte** | Un seul état global à la fois | Clarté décision, pas ambiguïté |
| **Cooldown Alertes** | Délai min entre alertes mêmes type | Évite spam, respecte bien-être |
| **Ultra-Fast Phone** | Buffer 6 frames pour téléphone | Réaction rapide objet critique |

---

## 9. Architecture Modulation & Extensibilité

Chaque niveau est indépendant et peut être amélioré/remplacé :

- **L1** : Ajouter nouveaux analyzers (emotion, lumière, gestes) sans impact L2+
- **L2** : Ajuster poids fusion, ajouter signaux (posture, stress) sans impact L3+
- **L3** : Modifier seuils états, hysteresis, sans impact L4+
- **L4** : Changer priorités états, fusion logique, sans impact L5+
- **L5** : Adapter délais alertes, cooldowns, messages, sans impact backend

---

## 10. Performance & Constraints

- **FPS Cible** : 30 FPS (≈33 ms par frame)
- **Latence Perception** : ~150 ms (5 frames buffer lissage)
- **Ressources** : Raspberry Pi 4 (4GB RAM) suffisant
- **Bande Mémoire** : ~50-100 MB (buffers, modèles ML compacts)
- **Connectivité** : JSON transmis via HTTP POST, format ~1KB par payload

---

## Références Implémentation

**Fichiers Clés** :
- `pi_client/analyzers/attention_analyzer.py` (L1)
- `pi_client/analyzers/fatigue_analyzer.py` (L1)
- `pi_client/analyzers/posture_analyzer.py` (L1)
- `pi_client/analyzers/phone_detector.py` (L1)
- `pi_client/engine/score_manager.py` (L2)
- `pi_client/engine/state_manager.py` (L3)
- `pi_client/engine/fusion_engine.py` (L4)
- `pi_client/engine/alert_manager.py` (L5)
- `pi_client/engine/temporal_engine.py` (Orchestration)

**Dépendances** :
- MediaPipe 0.10+ (Pose, FaceMesh)
- OpenCV 4.5+
- YOLOv8
- NumPy, déque (stdlib)

---

**Auteur** : Smart Focus - PFE 2025-2026
**Dernière MAJ** : 2025-05-11
