# 🌐 Diagramme des Endpoints API – Smart Focus & Life Assistant

**Version** : 1.0  
**Date** : 01 Mars 2026  
**Base URL** : `http://localhost:8000/api/v1`  
**Framework** : FastAPI + OpenAPI (Swagger auto-généré)

---

## 1. Vue Globale des Endpoints

```mermaid
graph LR
    CLIENT["🖥 Client\n(Flutter / ESP32)"]

    subgraph AUTH_GRP["🔐 /auth"]
        A1["POST /register"]
        A2["POST /login"]
        A3["POST /refresh"]
        A4["POST /logout"]
        A5["GET  /me"]
    end

    subgraph FOCUS_GRP["🎯 /focus"]
        F1["POST /session/start"]
        F2["PATCH /session/{id}/stop"]
        F3["POST /session/{id}/frame"]
        F4["GET  /session/{id}/score"]
        F5["GET  /sessions"]
        F6["GET  /stats"]
    end

    subgraph POSTURE_GRP["🧍 /posture"]
        P1["GET  /stats"]
        P2["GET  /history"]
    end

    subgraph PLANNING_GRP["📅 /planning"]
        PL1["GET  /today"]
        PL2["POST /generate"]
        PL3["GET  /{date}"]
        PL4["POST /sessions"]
        PL5["PATCH /sessions/{id}"]
        PL6["DELETE /sessions/{id}"]
    end

    subgraph CHATBOT_GRP["💬 /chatbot"]
        C1["POST /ask"]
        C2["GET  /conversations"]
        C3["GET  /conversations/{id}"]
        C4["DELETE /conversations/{id}"]
        C5["POST /documents/upload"]
        C6["GET  /documents"]
        C7["DELETE /documents/{id}"]
        C8["POST /quiz/generate"]
        C9["POST /flashcards/generate"]
        C10["GET  /flashcards/review"]
        C11["POST /flashcards/{id}/review"]
    end

    subgraph SLEEP_GRP["🌙 /sleep"]
        S1["POST /log"]
        S2["GET  /stats"]
        S3["GET  /history"]
        S4["PUT  /alarm"]
        S5["GET  /alarm"]
    end

    subgraph DEVICE_GRP["📡 /device"]
        D1["POST /register"]
        D2["GET  /status"]
        D3["POST /command"]
    end

    subgraph WS_GRP["⚡ WebSocket"]
        WS1["WS /ws/realtime"]
    end

    CLIENT --> AUTH_GRP
    CLIENT --> FOCUS_GRP
    CLIENT --> POSTURE_GRP
    CLIENT --> PLANNING_GRP
    CLIENT --> CHATBOT_GRP
    CLIENT --> SLEEP_GRP
    CLIENT --> DEVICE_GRP
    CLIENT <--> WS_GRP
```
