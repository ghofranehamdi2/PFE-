# Diagramme de Séquence Global - Smart Focus Assistant

## Scénario 1 : Session de Focus Complète (Capture + Alerte + Feedback)

```mermaid
sequenceDiagram
    participant U as 👤 Utilisateur
    participant MA as 📱 Mobile App
    participant API as 🔗 Backend API
    participant VO as 🎯 Vision Orchestrator
    participant DB as 🗄️ Database
    participant DA as 🧠 Decision AI
    participant PI as 🤖 Pi Client
    participant LD as 📺 Local Display
    participant HW as ⚙️ Hardware

    autonumber

    U->>MA: Démarre session
    MA->>API: POST /sessions/start
    API->>DB: Créer Session
    DB-->>API: Session{id}
    API-->>MA: {"session_id": 123}
    
    Note over PI: Capture en continu
    PI->>PI: Capturer frame vidéo
    PI->>VO: Analyser frame
    VO->>VO: Calcul scores (P,F,S,A)
    VO-->>PI: Metric{posture:0.4, fatigue:0.85}
    
    PI->>API: POST /metrics/record
    API->>DB: Enregistrer Metric
    API->>DA: Évaluer scores
    
    alt Fatigue > 0.8
        DA->>DA: Générer alerte FATIGUE_HIGH
        DA-->>API: Event{type, priority}
        API->>DB: Enregistrer Event
        API-->>PI: Alerte JSON
        
        PI->>LD: Afficher alerte rouge
        LD-->>U: 🔴 FATIGUE!
        PI->>HW: Trigger vibration
        HW-->>U: 📳 Vibration feedback
        
        PI->>API: POST /recommendation/adapt
        API->>DA: Contexte session + scores
        DA-->>API: "Faites une pause!"
        API-->>PI: Recommendation
        PI->>LD: Afficher recommandation
        
        MA->>MA: Refresh temps réel
        MA-->>U: Affichage alerte + recommandation
    end
    
    Note over MA: Utilisateur pause
    U->>MA: Termine session + Chat
    MA->>API: POST /ai/chat
    API->>API: Chercher contexte (RAG)
    API->>API: Injecter metrics (fatigue=0.85)
    API->>API: Query LLM avec contexte
    API-->>MA: Réponse personnalisée
    MA-->>U: Affichage réponse IA

    U->>MA: Peut retourner au focus
```

---

## Scénario 2 : Importation Document & Génération Planning RAG

```mermaid
sequenceDiagram
    participant U as 👤 Utilisateur
    participant MA as 📱 Mobile App
    participant API as 🔗 Backend API
    participant EMB as 🧮 Embedder
    participant VS as 🎯 Vector Store
    participant RAG as 📚 RAG Engine
    participant LLM as 🧠 LLM/API
    participant DB as 🗄️ Database

    autonumber

    U->>MA: Importe PDF cours
    MA->>API: POST /documents/upload
    API->>API: Parse PDF → chunks
    API->>EMB: Créer embeddings
    EMB-->>API: vectors[]
    
    API->>VS: Stocker chunks + embeddings
    VS-->>API: ACK
    
    API->>DB: Enregistrer métadonnée doc
    DB-->>API: Document{id}
    
    Note over MA: Utilisateur revient après session
    U->>MA: "Aide-moi avec mon planning"
    MA->>API: POST /ai/generate-plan
    API->>DB: Récupérer historique sessions
    API->>RAG: Récupérer stats (fatigue avg, etc)
    
    RAG->>VS: Recherche docs pertinents
    VS-->>RAG: [chunks pertinents]
    
    RAG->>RAG: Créer prompt enrichi:
    Note right of RAG: Prompt = <br/>Contexte user + <br/>Docs + <br/>Stats fatigue + <br/>Question
    
    RAG->>LLM: Envoyer prompt
    LLM-->>RAG: Planning détaillé
    
    RAG-->>API: StudyPlan{sessions[], timing}
    API->>DB: Enregistrer planning
    API-->>MA: JSON planning
    
    MA-->>U: Afficher planning adapté

    Note over MA: Adapt planning selon condition user
    U->>API: Utilisateur lance session
    API->>DB: User fatigue_avg > threshold
    API->>RAG: Adapter durée session
    RAG->>LLM: "Sessions courtes"
    LLM-->>RAG: Planning ajusté
```

---

## Scénario 3 : Interaction Chat Temps Réel En Session

```mermaid
sequenceDiagram
    participant U as 👤 Utilisateur
    participant MA as 📱 Mobile App
    participant PI as 🤖 Pi Client
    participant API as 🔗 Backend API
    participant VO as 🎯 Vision
    participant DB as 🗄️ Database
    participant RAG as 📚 RAG Engine
    participant LLM as 🧠 LLM

    autonumber
    
    rect rgb(200, 150, 255)
        Note over PI,MA: Session active en parallèle
        PI->>PI: Capture continue
        PI->>VO: Analyse metrics
        VO-->>PI: Scores (P,F,S,A)
        PI->>API: POST /metrics (async)
    end

    U->>MA: Pose question en chat
    MA->>API: POST /ai/chat (avec session_id)
    
    par Récupération contexte
        API->>DB: Récupérer last metrics
        API->>VS: Recherche docs
    and Injection du contexte
        API->>API: Formatter contexte:
        Note right of API: {<br/>question,<br/>metrics_recent,<br/>docs_relevant,<br/>historique<br/>}
    end
    
    API->>LLM: POST prompt enrichi
    LLM-->>API: Streaming réponse
    
    API-->>MA: Réponse personnalisée
    MA-->>U: Affichage chat
    
    Note over MA,U: Décision utilisateur basée sur réponse IA

    alt Utilisateur suit conseil pause
        U->>MA: Clique "Pauser"
        MA->>API: PATCH /sessions/{id}/pause
        API->>DB: session.status = paused
        PI->>PI: Arrêter vision
    else Utilisateur continue
        U->>MA: Continue étude
        Note over PI: Vision reprend
    end
```

---

## Scénario 4 : Consultation Historique & Statistiques

```mermaid
sequenceDiagram
    participant U as 👤 Utilisateur
    participant MA as 📱 Mobile App
    participant API as 🔗 Backend API
    participant DB as 🗄️ Database
    participant DA as 📊 Analytics

    autonumber

    U->>MA: Clique "Statistiques"
    MA->>API: GET /users/{id}/statistics?period=month
    
    API->>DB: Query sessions last 30 days
    DB-->>API: Sessions[]
    
    API->>DB: Query all metrics for sessions
    DB-->>API: Metrics[]
    
    API->>DA: Calculer agrégats
    DA->>DA: avg(posture), max(fatigue)<br/>trends, anomalies
    DA-->>API: AggregatedData
    
    API-->>MA: JSON statistiques
    MA->>MA: Afficher graphiques
    MA-->>U: Visualisation complète
    
    rect rgb(200, 220, 255)
        Note over U: Dashboard affiche<br/>- Focus moyen/jour<br/>- Fatigue trends<br/>- Sessions réussies<br/>- Alertes top
    end
```

---

## Notes Importantes

- **Asynchrone** : Les envois de metrics sont POST asynchrones (ne bloquent pas l'app)
- **Real-time** : Vision continue indépendamment du chat
- **Contextualisé** : LLM reçoit toujours context(user, docs, metrics)
- **Adaptatif** : Recommandations évoluent avec les scores
