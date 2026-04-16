# 🧠 Guide Technique : Vision par Ordinateur (Smart Focus)

Ce document explique les algorithmes, les bibliothèques et les concepts mathématiques utilisés dans le module de vision du projet **Smart Focus**.

## 🛠 Bibliothèques Utilisées
1. **OpenCV (cv2)** : Gestion des flux vidéo, dessin des overlays (superpositions) et traitement d'image de base.
2. **MediaPipe** : Framework développé par Google pour le suivi des repères faciaux (FaceMesh) et corporels (Pose) en temps réel.
3. **NumPy** : Calculs mathématiques sur les tableaux de coordonnées (distances euclidiennes, moyennes).

---

## 1. Détection de la Fatigue (Fatigue Analyzer)

Le système utilise principalement deux métriques : **EAR** et **PERCLOS**.

### A. EAR (Eye Aspect Ratio)
L'EAR mesure le rapport entre la hauteur et la largeur de l'œil. 
- **Calcul** : On utilise 6 points de repère par œil. 
  - $EAR = \frac{||P_2 - P_6|| + ||P_3 - P_5||}{2 \times ||P_1 - P_4||}$
- **Interprétation** : 
  - Yeux ouverts : EAR élevé (~0.25 - 0.35).
  - Yeux fermés : EAR chute brusquement (~0.15 - 0.20).

### B. PERCLOS (Percentage of Eye Closure)
C'est l'indicateur le plus fiable utilisé dans l'industrie automobile.
- Il mesure le **pourcentage de temps** où les yeux sont fermés (EAR sous le seuil) sur une fenêtre temporelle (ex: 1 minute).
- Un PERCLOS élevé déclenche l'alerte de fatigue.

### C. MAR (Mouth Aspect Ratio)
Similaire au EAR mais pour la bouche. Si le ratio dépasse un certain seuil pendant quelques secondes, un **bâillement** est détecté.

---

## 2. Analyse de la Posture (Posture Analyzer)

Utilise les points de repère de **MediaPipe Pose**.

### A. Alignement des Épaules
On compare la coordonnée $Y$ de l'épaule gauche et de l'épaule droite.
- Une différence importante indique une mauvaise inclinaison latérale.

### B. Affaissement (Slouching)
On mesure la **distance verticale** entre le milieu des épaules et le nez.
- Lorsque l'utilisateur s'affaisse, sa tête descend vers le bureau, réduisant cette distance.
- **Calibration** : Le système enregistre votre position "droite" au démarrage pour définir une référence personnalisée.

---

## 3. Analyse de l'Attention (Attention Analyzer)

### A. Head Pose Estimation (Yaw & Pitch)
- **Yaw (Lacet)** : Rotation de la tête à gauche ou à droite. Calculé par la position relative du nez par rapport aux coins des yeux.
- **Pitch (Tangage)** : Regard vers le haut ou vers le bas.
- Si le Yaw ou le Pitch dépasse les seuils calibrés, le système considère l'utilisateur comme **distrait**.

---

## 4. Proxy de Stress (Stress Analyzer)

### A. Agitation (Jitter)
Comme nous n'avons pas accès à des capteurs physiologiques (ECG/EEG), nous utilisons le **Jitter visuel**.
- On suit les micro-mouvements des points clés du visage (nez, yeux).
- On calcule la variance des positions sur une fenêtre de 30 frames.
- Une forte agitation (mouvements saccadés/nerveux) est interprétée comme un niveau de stress élevé ou une frustration.

---

## 🚀 Étape de Calibration (INDISPENSABLE)

Au lancement, le système effectue une phase de **5 secondes** :
1. **Baseline EAR** : Capture votre EAR "naturel" (yeux ouverts normalement).
2. **Posture Référence** : Enregistre votre hauteur d'assise idéale.
3. **Regard Centre** : Définit l'angle de votre écran.

**Pourquoi ?** Car chaque morphologie et chaque installation de caméra est différente. La calibration assure que le système ne donne pas de "faux positifs".
