# Modèle de Vision (CV) : Choix de Fiabilité et Architecture Temporelle

Ce document documente l'architecture du modèle CV "Smart Focus" V3. L'objectif de cette version est de corriger les faux positifs naïfs (ex: grimace = stress, lecture = distraction) en appliquant une approche temporelle robuste et modulaire à 4 niveaux.

## Architecture à 4 Niveaux

Le traitement vidéo n'est plus un simple mapping "Image -> Décision", mais suit un tunnel de consolidation :

### 1. Niveau 1 : Observations Instantanées (Les Analyseurs)
Les scripts dans `analyzers/` (`attention_analyzer.py`, `fatigue_analyzer.py`, etc.) ont été purgés de toute logique décisionnelle ou d'états persistants majeurs.
- Ils extraient l'état *physique* de la frame : le *yaw* de la tête, le *pitch*, le niveau d'ouverture de la bouche (*MAR*), la présence de téléphones, un score brut de grimace (basé sur 4 métriques de tension faciale), et le *jitter* (agitation).
- **Rôle** : Fournir une photographie objective du comportement (ex: "La tête est baissée, les lèvres sont pincées"). Aucune alerte n'est déclenchée ici.

### 2. Niveau 2 : Hypothèses Faibles (Fenêtres Courtes)
Géré par le `TemporalEngine`, ce niveau bufferise les observations du Niveau 1 (généralement sur 1 à 3 secondes) pour en tirer des hypothèses booléennes comportementales stables afin d'éliminer le bruit :
- `possible_reading` : regard vers le bas depuis > 0.7s avec tête de niveau
- `possible_thinking` : regard hors écran sans tension ni agitation
- `possible_self_explaining` : lèvres en mouvement avec une seule personne dans le champ
- `possible_phone_distraction` : téléphone clairement détecté + regard baissé
- `possible_fatigue` / `possible_stress` : moyennes lissées (EMA) dépassant un seuil de base.

### 3. Niveau 3 : États Consolidés (Fenêtres Longues & Hystérésis)
Toujours dans le `TemporalEngine`, ce niveau applique des *Timers de Transition* stricts (anti-flapping). Une hypothèse du Niveau 2 doit persister sans interruption pour modifier l'état consolidé final.
- Exemple : Pour passer de `focused` à `social_distraction`, l'utilisateur doit fixer une seconde personne présente pendant au moins 3 secondes continues.
- Une transition vers `phone_distraction` requiert 2 secondes continues d'attention vers le téléphone.
- Les états comme `focused_writing` et `self_explaining` sont légitimés de façon mutuellement exclusive selon la posture, le regard et la voix.

### 4. Niveau 4 : Politique d'Alerte (Alert Manager)
Géré par `AlertManager`. Avoir un état négatif (ex: `phone_distraction`) *ne déclenche pas une alerte immédiatement*. Le système attend que cet état "mauvais" s'éternise :
- `phone_distraction` : toléré 4 secondes avant alerte "haute".
- `stress_elevated` : toléré 15 secondes (pour s'assurer qu'il ne s'agit pas d'un moment de frustration passagère lié à un exercice difficile) avant alerte "haute".
- Les comportements studieux (`focused_reading`, `self_explaining`, `thinking`) ne provoquent *jamais* d'alerte, même s'ils s'éloignent de la pose académique standard "face écran".

---

## Centralisation via `cv_config.py`
Toutes ces constantes de temps et de tolérance sont regroupées dans `pi_client/config/cv_config.py` pour un ajustage fin (tuning).

---

## Exemples de Sorties JSON

Les simulations ci-dessous démontrent que la pipeline V3 filtre correctement les observations brutes en états métier cohérents.

### Cas 1 : Lecture Concentrée (Regard baissé pur)
L'utilisateur baisse la tête vers son bureau.
- **Niveau 1** : `head_direction="down"`, `gaze_zone="desk"`.
- **Niveau 2** : `possible_reading=True`, `possible_writing=True`.
- **Niveau 3** : Le moteur reconnaît la posture et passe en `work_mode="focused_writing"`.
- **Niveau 4** : `should_alert=False` car ce comportement est reconnu comme productif.

### Cas 2 : Auto-Explication (Parler seul)
L'utilisateur parle à voix haute pour résoudre un exercice.
- **Niveau 1** : Lèvres en mouvement (`mar` élevé) en l'absence de deuxième visage.
- **Niveau 2** : `possible_self_explaining=True`.
- **Niveau 3** : L'état passe en `self_explaining` plutôt qu'en 'distraction sociale'. L'attention reste `focused`.
- **Niveau 4** : `should_alert=False`.

### Cas 3 : Distraction Bref (Rupture d'attention ponctuelle)
L'utilisateur regarde par la fenêtre 1 ou 2 secondes.
- **Niveau 1** : `head_direction="right"`, `gaze_zone="away"`.
- **Niveau 2** : `possible_thinking=True` car l'utilisateur est calme (pas de stress, pas de téléphone).
- **Niveau 3** : Le système passe en mode `thinking`. (S'il bougeait la tête sans arrêt, il deviendrait `brief_off_task`).
- **Niveau 4** : `should_alert=False`. L'attention humaine respire.

### Cas 4 : Distraction par Téléphone (Alerte justifiée)
L'utilisateur regarde le téléphone posé sur le bureau.
- **Niveau 1** : `head_direction="down"`, `phone_detected=True`.
- **Niveau 2** : `possible_phone_distraction=True`.
- **Niveau 3** : Le mode se verrouille sur `phone_distraction` (+ de 2 secondes).
- **Niveau 4** : Après la tolérance de délai prévue dans l'AlertManager, `should_alert=True`, `level="high"`, avec la raison "Distraction par téléphone".

---

## Limites et Améliorations Futures
- **Occultation du WebCam** : Si les mains masquent le visage lors d'un "réfléchissement profond", le modèle passe en `USER_ABSENT` s'il ne gère pas de mémoire faciale au-delà de 0.5s.
- **Stress Cognitif vs. Stress Émotionnel** : Le clignement nerveux et les grimaces peuvent signifier une forte charge cognitive pertinente pour le flux de travail, qui ne devrait pas être traitée comme de la "détresse" à alerter, mais comme un effort accru. Le tuning fin sur des cas réels aidera à peaufiner ces seuils.
- **Audio manquant** : L'`attention_analyzer` utilise le MAR (mouvement des lèvres) comme proxy proxy de la parole. L'ajout d'une analyse audio courte rendrait le diagnostic `self_explaining` infaillible.
