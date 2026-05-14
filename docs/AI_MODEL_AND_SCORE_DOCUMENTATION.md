**Documentation complète du modèle AI et du score de vision**

Résumé
-------
- **But :** Détecter des objets/événements dans le flux vidéo et calculer un `vision_score` (score de qualité/pertinence) par détection.
- **Modèle principal :** YOLOv8 (poids fournis : [yolov8n.pt](yolov8n.pt)).
- **Scripts clés :** [pi_client/main_cv.py](pi_client/main_cv.py), [backups/cv_model_20260416_143037/main_cv.py](backups/cv_model_20260416_143037/main_cv.py), [scan_cameras.py](scan_cameras.py).
- **API / Backend :** point d'entrée principal [backend/app/main.py](backend/app/main.py).
- **Documentation projet AI existante :** [docs/06_ai_modules.md](docs/06_ai_modules.md).

1) Architecture du modèle
-------------------------
- **Type :** Détection d'objets en temps réel (You Only Look Once style) — YOLOv8n (nano) pour faible latence.
- **Poids fournis :** `yolov8n.pt` (quantité, taille et date dans le dépôt).
- **Pipeline général :** acquisition -> prétraitement -> inférence (YOLOv8) -> post-traitement -> calcul du `vision_score` -> envoi au backend.

2) Données & Entraînement
-------------------------
- **Sources de données :** vidéos/images recueillies par clients PI et dataset d'entraînement (voir dossiers `pi_client/output` et backups).
- **Annotations :** format COCO / YOLO (boîtes englobantes, classes). Vérifier les scripts d'entraînement si disponibles.
- **Augmentations courantes :** flips, crops, variations de luminosité, bruit.
- **Hyperparamètres (exemple recommandé) :** learning rate 0.01→0.001, batch 16, epochs 50–200 selon convergence.

3) Entrée et prétraitement
--------------------------
- **Entrées attendues :** image RGB (BGR selon OpenCV conversion), résolution recommandée 640×640 pour YOLOv8n.
- **Prétraitement standard :**
  - conversion couleur BGR→RGB (si OpenCV),
  - redimensionnement en maintenant ratio (letterbox) jusqu'à la taille d'entrée du modèle,
  - normalisation pixels → [0,1] ou centré selon export du modèle,
  - conversion en tenseur et batch dimension.

4) Sorties et post-traitement
-----------------------------
- **Sorties typiques YOLOv8 :** pour chaque détection → `[x1, y1, x2, y2, confidence, class_id]`.
- **NMS (suppression de non-maxima) :** appliquer NMS sur IoU threshold (ex. 0.45) pour filtrer doublons.
- **Filtrage par confiance :** garder détections `confidence >= conf_threshold` (ex. 0.25 par défaut).

5) Définition et calcul du `vision_score`
----------------------------------------
Le `vision_score` est un score unique (0–100) représentant la qualité et la confiance d'une détection. Il combine :
- **Confiance du modèle** ($C$) — la probabilité de la détection (0–1).
- **Taille relative de la boîte** ($A$) — surface de la boîte normalisée par la surface de l'image (0–1).
- **Poids de classe** ($W_c$) — importance relative d'une classe (ex : personne > véhicule), valeur >0.
- **Pénalité d'occlusion / flou** ($P_{occ}$) — facteur de réduction (0–1) si l'objet est partiellement masqué ou flou.

Formule générale :
$$
S = 100 \times \mathrm{clip}\left( \alpha\,C + \beta\,A + \gamma\,W_c - \delta\,(1-P_{occ}),\,0,\,1 \right)
$$
où $\alpha,\beta,\gamma,\delta$ sont des poids relatifs (somme indicative ≈1). Exemple de valeurs par défaut :
- $\alpha=0.5$ (confiance)
- $\beta=0.25$ (taille)
- $\gamma=0.2$ (poids de classe)
- $\delta=0.15$ (pénalité occlusion)

Explication des composants :
- $C$ : la `confidence` fournie par YOLOv8.
- $A = \dfrac{(x2-x1)\times(y2-y1)}{W_{img}\times H_{img}}$ (surface normalisée).
- $W_c$ : table de poids configurable (ex. personne=1.0, animal=0.8, voiture=0.9). Stocker la table dans config.
- $P_{occ}$ : heuristique entre 0 et 1. Calcul possible : détecter overlap avec autres boîtes (fort overlap → possible occlusion) ou estimer flou via variance du Laplacien.

Normalisation et seuils
- Le score $S$ est ramené à 0–100 pour lisibilité dans les rapports.
- Seuils usuels :
  - `score_ok` >= 60 → détection fiable
  - `score_marginal` 40–60 → à vérifier
  - `score_bad` < 40 → faible confiance/qualité

6) Évaluation & métriques
-------------------------
- **Métriques de détection :** mAP@0.5, mAP@[0.5:0.95], précision, rappel.
- **Évaluation du `vision_score` :** corréler $S$ avec détections humaines (ground truth) pour vérifier calibration.
- **Rapports recommandés :** courbe PR, matrice de confusion par classe, distribution des `vision_score` pour TP/FP.

7) Déploiement & inférence
--------------------------
- **Local / edge (Raspberry Pi) :** utiliser version légère (yolov8n), GPU si disponible (NVIDIA Jetson ou inference accélérée), sinon CPU en mode optimisé.
- **Serveur / Backend :** exécuter inférence dans `pi_client` puis pousser événements au backend via API (voir [backend/app/main.py](backend/app/main.py)).
- **Conteneurisation :** vérifier `backend/Dockerfile` et `docker-compose.yml` pour orchestrer services.

Commandes d'exemple (exécution d'un script d'inférence) :
```bash
python pi_client/main_cv.py --source 0 --weights yolov8n.pt --conf 0.25
python backups/cv_model_20260416_143037/main_cv.py --input video.mp4
```

8) API & intégration
---------------------
- **Endpoint de push :** le pipeline standard envoie détection + `vision_score` au backend. Voir [backend/app/main.py](backend/app/main.py) pour l'implémentation du routeur.
- **Payload recommandé JSON :**
```json
{
  "camera_id": "cam01",
  "timestamp": "2026-05-12T12:34:56Z",
  "detections": [
    {
      "class": "person",
      "bbox": [x1,y1,x2,y2],
      "confidence": 0.87,
      "vision_score": 78.4
    }
  ]
}
```

9) Fichiers clés et dépendances
-------------------------------
- Poids modèle : [yolov8n.pt](yolov8n.pt)
- Scripts inférence : [pi_client/main_cv.py](pi_client/main_cv.py), [backups/cv_model_20260416_143037/main_cv.py](backups/cv_model_20260416_143037/main_cv.py)
- Orchestration backend : [docker-compose.yml](docker-compose.yml), [backend/Dockerfile](backend/Dockerfile)
- API backend : [backend/app/main.py](backend/app/main.py)
- Documentation module AI : [docs/06_ai_modules.md](docs/06_ai_modules.md)

10) Limites, biais et maintenance
---------------------------------
- **Biais :** dataset mal équilibré → biais de détection par classe / environnement (luminosité, angle).
- **Robustesse :** performances chutent en faible luminosité, occlusion, fort flou.
- **Maintenance :**
  - ré-entraîner régulièrement avec nouvelles images réelles,
  - recalibrer la table `W_c` et les poids $\alpha,\beta,\gamma,\delta$ selon retours opérateurs,
  - journaliser `vision_score` et erreurs pour monitorer dérive.

11) Annexes & suggestions d'améliorations
-----------------------------------------
- Ajouter un module de calibration automatique qui ajuste les poids du score par apprentissage (régression calibratrice) pour mieux aligner $S$ aux labels humains.
- Envisager quantification / conversion ONNX / TensorRT pour accélérer l'inférence en production.

Contact & suivi
---------------
- Fichiers à consulter pour reprendre le travail : [pi_client/main_cv.py](pi_client/main_cv.py), [backups/cv_model_20260416_143037/main_cv.py](backups/cv_model_20260416_143037/main_cv.py), [backend/app/main.py](backend/app/main.py), [docs/06_ai_modules.md](docs/06_ai_modules.md).

---
Fichier généré automatiquement : adaptez les valeurs de poids et les heuristiques (`P_{occ}`, table `W_c`) en fonction des données réelles et des tests utilisateurs.
