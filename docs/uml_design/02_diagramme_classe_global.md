# Diagramme de Classe Global

## Objectif
Ce diagramme représente la structure logique globale du système, en alignement avec les modules réels: pi_client, backend, mobile et composant IA/RAG.

## Diagramme UML (Mermaid)

```mermaid
classDiagram

    class Utilisateur {
        +int id
        +string email
        +string hashed_password
        +datetime created_at
    }

    class SessionFocus {
        +int id
        +int user_id
        +datetime start_time
        +datetime end_time
        +string status
    }

    class MetriqueVision {
        +int id
        +int session_id
        +float posture_score
        +float fatigue_score
        +float stress_score
        +float attention_score
        +datetime timestamp
    }

    class EvenementAlerte {
        +int id
        +int session_id
        +string type
        +string priority
        +json metadata
        +datetime timestamp
    }

    class PiClient {
        +start_loop()
        +capture_frame()
        +analyze_frame()
        +send_metrics()
        +handle_local_alert()
    }

    class VisionPipeline {
        +compute_scores(frame)
        +merge_scores()
    }

    class PostureAnalyzer {
        +analyze(frame)
    }

    class FatigueAnalyzer {
        +analyze(frame)
    }

    class StressAnalyzer {
        +analyze(frame)
    }

    class AttentionAnalyzer {
        +analyze(frame)
    }

    class DecisionEngine {
        +evaluate_thresholds(metrics)
        +create_alert(metrics)
    }

    class LocalFeedbackController {
        +display_alert(message)
        +led_feedback(level)
        +vibration_feedback(level)
    }

    class FastAPIApp {
        +start_session(payload)
        +ingest_metrics(payload)
        +create_event(payload)
        +get_dashboard(user_id)
    }

    class SessionService {
        +create_session(user)
        +close_session(session)
    }

    class MetricsService {
        +save_metrics(metrics)
        +aggregate_metrics(session)
    }

    class AlertService {
        +save_event(event)
        +notify_clients(event)
    }

    class AIService {
        +chat(question, context)
        +generate_plan(user_context)
    }

    class RAGService {
        +index_document(doc)
        +retrieve_context(question)
    }

    class LLMProvider {
        +complete(prompt)
    }

    class Repository {
        +save(entity)
        +find_by_id(id)
        +find_all(filters)
    }

    class Database {
        +connect()
        +transaction()
    }

    class VectorStore {
        +upsert_embeddings(chunks)
        +search_similar(query)
    }

    class MobileApp {
        +show_realtime_dashboard()
        +show_history()
        +chat_with_ai()
        +show_study_plan()
    }

    Utilisateur "1" --> "*" SessionFocus : possede
    SessionFocus "1" --> "*" MetriqueVision : contient
    SessionFocus "1" --> "*" EvenementAlerte : declenche

    PiClient --> VisionPipeline : utilise
    VisionPipeline --> PostureAnalyzer : compose
    VisionPipeline --> FatigueAnalyzer : compose
    VisionPipeline --> StressAnalyzer : compose
    VisionPipeline --> AttentionAnalyzer : compose
    PiClient --> DecisionEngine : utilise
    PiClient --> LocalFeedbackController : controle

    PiClient --> FastAPIApp : envoie API
    MobileApp --> FastAPIApp : consomme API

    FastAPIApp --> SessionService : delegue
    FastAPIApp --> MetricsService : delegue
    FastAPIApp --> AlertService : delegue
    FastAPIApp --> AIService : delegue

    SessionService --> Repository : utilise
    MetricsService --> Repository : utilise
    AlertService --> Repository : utilise
    Repository --> Database : persiste

    AIService --> RAGService : utilise
    AIService --> LLMProvider : utilise
    RAGService --> VectorStore : interroge
```

## Couches UML Globales

| Couche | Eléments |
|---|---|
| Présentation | MobileApp, PiClient, LocalFeedbackController |
| Métier | VisionPipeline, DecisionEngine, SessionService, MetricsService, AlertService, AIService |
| Accès Données | Repository, Database, VectorStore |
| Domaine | Utilisateur, SessionFocus, MetriqueVision, EvenementAlerte |

## Flux Principal Résumé

1. PiClient capture le flux vidéo.
2. VisionPipeline calcule les scores via les analyzers spécialisés.
3. DecisionEngine détermine alertes et priorités.
4. FastAPIApp persiste les données via les services et repositories.
5. MobileApp visualise historique et temps réel.
6. AIService enrichit la recommandation via RAGService et LLMProvider.
