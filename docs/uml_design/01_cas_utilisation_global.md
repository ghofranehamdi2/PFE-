# Diagramme de Cas d'Utilisation Global - Smart Focus Assistant

## Vue Globale du Système

```mermaid
graph TB
    subgraph Acteurs
        U["👤 Utilisateur"]
        PI["🤖 Raspberry Pi"]
        LLM["🧠 Moteur IA/LLM"]
        EMAIL["📧 Système Notification"]
    end

    subgraph "Système Smart Focus Assistant"
        CU1["Démarrer une Session"]
        CU2["Analyser Vision en Temps Réel"]
        CU3["Recevoir Alertes & Feedback"]
        CU4["Consulter Statistiques"]
        CU5["Interagir avec Assistant IA"]
        CU6["Générer Planning d'Étude"]
        CU7["Importer Documents"]
        CU8["Adapter Recommandations"]
    end

    subgraph "Systèmes Externes"
        VisionEngine["Moteur Vision<br/>YOLOv8"]
        VectorDB["Vector Store<br/>ChromaDB"]
        PostgreSQL["Base de Données<br/>PostgreSQL"]
        HardwareFeedback["Feedback Matériel<br/>LED/Vibration"]
    end

    U -->|Démarrer| CU1
    U -->|Consulter| CU4
    U -->|Poser questions| CU5
    U -->|Importer docs| CU7
    
    PI -->|Capturer| CU2
    PI -.->|Déclenche| CU3
    
    CU1 -->|include| CU2
    CU2 -->|include| CU3
    CU2 -->|include| CU8
    
    CU3 -->|extend| HardwareFeedback
    CU3 -->|extend| EMAIL
    
    CU4 -.->|consult| PostgreSQL
    CU5 -.->|use| LLM
    CU5 -.->|retrieve| VectorDB
    CU5 -.->|use| CU8
    
    CU6 -.->|generate from| CU4
    CU6 --> CU8
    
    CU7 -.->|store| VectorDB
    CU7 -.->|persist| PostgreSQL
    
    CU8 -->|adapt scores| CU5

    style CU1 fill:#e1f5ff
    style CU2 fill:#fff3e0
    style CU3 fill:#fce4ec
    style CU5 fill:#f3e5f5
    style CU6 fill:#e0f2f1
    style CU8 fill:#fff9c4
```

## Description des Cas d'Utilisation

| Cas d'Utilisation | Description | Acteurs | Préconditions |
|-------------------|-------------|---------|---------------|
| **Démarrer une Session** | L'utilisateur lance une session de focus/étude | Utilisateur | L'utilisateur est connecté |
| **Analyser Vision en Temps Réel** | Le pi_client capture et analyse posture, fatigue, stress, attention | Pi, Backend | Session active |
| **Recevoir Alertes & Feedback** | Les alertes sont affichées sur l'écran du Pi et l'app mobile | Système, Utilisateur | Seuil dépassé |
| **Consulter Statistiques** | L'utilisateur visualise l'historique et statistiques sessionnelles | Utilisateur, BD | Sessions enregistrées |
| **Interagir avec Assistant IA** | Chat avec le moteur RAG pour aide à l'étude | Utilisateur, LLM, Vector DB | Documents importés |
| **Générer Planning d'Étude** | IA génère un planning personnalisé basé sur stats | LLM, BD | Données suffisantes |
| **Importer Documents** | Utilisateur importe PDFs/ressources pour le RAG | Utilisateur, Vector DB | Authenticité du fichier |
| **Adapter Recommandations** | Recommandations adaptées selon scores en temps réel | Système, LLM | Scores disponibles |

---

## Relations entre Cas d'Utilisation

- **Include (→)** : Relation de composition obligatoire
- **Extend (⇢)** : Relation optionnelle avec conditions
- **Précédence (⋯→)** : Ordre d'exécution logique
