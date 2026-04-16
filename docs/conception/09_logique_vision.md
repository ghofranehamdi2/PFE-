# 🧠 Logique du Module Vision – Smart Focus & Life Assistant

**Version** : 1.0  
**Date** : 08 Mars 2026  
**Description** : Détail du pipeline d'analyse d'images et du moteur de concentration.

---

## 1. Pipeline de Traitement Vision

Le traitement est optimisé pour s'exécuter sur un client (type Raspberry Pi) en temps réel.

```mermaid
graph TD
    START["📹 Capture Frame\n(OpenCV VideoCapture)"]
    RESIZE["✂️ Redimensionnement\n(320x240 pour l'IA)"]
    
    subgraph ANALYZERS["🔍 Analyseurs IA"]
        POSTURE["🧍 PostureAnalyzer\n(Angles & Inclinaison)"]
        FATIGUE["😴 FatigueAnalyzer\n(EAR - Eye Aspect Ratio)"]
        ATTENTION["👀 AttentionAnalyzer\n(Pose de tête Yaw/Pitch)"]
        STRESS["😰 StressAnalyzer\n(Agitation/Mouvement)"]
    end
    
    ENGINE["🧠 ConcentrationEngine\n(Logique floue / Heuristiques)"]
    API["🌐 Async API Client\n(Service de push)"]
    
    START --> RESIZE
    RESIZE --> POSTURE
    RESIZE --> FATIGUE
    RESIZE --> ATTENTION
    RESIZE --> STRESS
    
    POSTURE --> ENGINE
    FATIGUE --> ENGINE
    ATTENTION --> ENGINE
    STRESS --> ENGINE
    
    ENGINE -->|Score & État| API
```

---

## 2. Logique du Moteur de Concentration

Le `ConcentrationEngine` agrège les scores des différents analyseurs pour déterminer l'état de l'utilisateur :

- **États détectés** : `focused`, `distracted`, `fatigued`, `talking`.
- **Calcul du score** : Moyenne pondérée tenant compte de la présence du visage, de l'EAR (fatigue) et de l'orientation du regard.
- **Temporisation** : Utilisation de buffers pour éviter les changements d'état trop fréquents (anti-flickering).

```mermaid
stateDiagram-v2
    [*] --> FOCUSED
    FOCUSED --> DISTRACTED : Regard absent > 2s
    DISTRACTED --> FOCUSED : Regard présent
    FOCUSED --> FATIGUED : EAR bas > 3s
    FATIGUED --> FOCUSED : EAR normal
    FOCUSED --> TALKING : Audio détecté
    TALKING --> FOCUSED : Silence
```

---

## 3. Optimisations Techniques

1. **Frame Skipping** : Capture à 30 FPS mais analyse IA toutes les 3 frames (`FRAME_SKIP=3`) pour économiser le CPU.
2. **Multi-threading** : Les appels réseau vers le backend FastAPI sont effectués dans des threads séparés pour ne pas bloquer la boucle de capture.
3. **Calibration Dynamique** : Phase de 5 secondes au démarrage pour définir la posture "normale" de l'utilisateur.
