# 📟 Logique Hardware & Client IoT – Smart Focus & Life Assistant

**Version** : 1.0  
**Date** : 08 Mars 2026  
**Description** : Détail du fonctionnement du client IoT (Raspberry Pi/ESP32-CAM) et intégration des capteurs.

---

## 1. Architecture Logicielle du Client (`pi_client`)

Le client est écrit en Python et gère l'orchestration des capteurs et de la caméra.

```mermaid
graph TB
    subgraph MAIN["Main Loop (main_cv.py)"]
        CORE["Loop 30 FPS"]
        CALIB["Calibration Initiale"]
    end

    subgraph SENSORS["📡 Couche Capteurs"]
        CAM["📷 Caméra (OpenCV)"]
        AUDIO["🎙 Micro (AudioDetector)"]
        SIM["⚖️ Capteurs Simulés\n(Pression/Pouls)"]
    end

    subgraph COMM["🔌 Communication"]
        HTTP["API REST (Auth/Session)"]
        WS["WebSocket (Real-time events)"]
    end

    CAM --> MAIN
    AUDIO --> MAIN
    SIM --> MAIN
    MAIN --> HTTP
    MAIN --> WS
```

---

## 2. Intégration des Capteurs

- **Caméra** : Flux MJPEG redimensionné localement.
- **Audio** : Détection de l'activité vocale (VAD) pour identifier les distractions sociales ou les périodes de communication.
- **Capteurs de santé (Simulés)** : Données de pression (présence au bureau) et cardio (simulé pour le prototype PFE).

---

## 3. Flux de Données Hardware → Backend

```mermaid
sequenceDiagram
    participant HW as Raspberry Pi / ESP32
    participant API as FastAPI Backend

    HW->>API: POST /auth/login
    API-->>HW: JWT Token
    HW->>API: POST /focus/session/start
    API-->>HW: session_id

    loop Boucle de Session
        HW->>HW: Capture & Analyse Locale
        alt Toutes les 30 frames
            HW->>API: POST /focus/event {type: "concentration", score: XX}
        end
    end

    HW->>API: POST /focus/session/stop
```

---

## 4. Gestion des Erreurs & Robustesse

1. **Auto-reconnexion** : En cas de perte de WiFi, le client tente de se reconnecter à l'API sans arrêter la session locale.
2. **Fallback Mode** : Si la caméra n'est pas détectée, le client peut passer en mode "Sensors Only".
3. **Logging** : Logs locaux pour le débogage hardware.
