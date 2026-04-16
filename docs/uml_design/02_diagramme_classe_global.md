# Diagramme de Classes Global - Smart Focus Assistant

## Modèle Objet Complet du Système

```mermaid
classDiagram
    %% ============== ENTITÉS MÉTIER ==============
    
    class User {
        -id: int
        -email: string
        -hashedPassword: string
        -createdAt: datetime
        +createSession(): Session
        +getStatistics(): Statistics
        +importDocument(file): void
    }

    class Session {
        -id: int
        -userId: int
        -startTime: datetime
        -endTime: datetime
        -status: string
        -totalFocusTime: duration
        +recordMetrics(metrics): void
        +triggerAlert(event): void
        +getMetrics(): Metric[]
    }

    class Metric {
        -id: int
        -sessionId: int
        -postureScore: float
        -fatigueScore: float
        -stressScore: float
        -attentionScore: float
        -timestamp: datetime
        +validate(): boolean
        +isAnomalous(): boolean
    }

    class Event {
        -id: int
        -sessionId: int
        -type: string
        -priority: string
        -metadata: JSON
        -timestamp: datetime
        +severity(): int
        +getAction(): string
    }

    %% ============== MODULES VISION ==============

    class VisionAnalyzer {
        -enabled: boolean
        -model: string
        +analyzeFrame(frame): Metric
        +detectFatigue(frame): float
        +detectPosture(frame): float
        +detectStress(frame): float
        +detectAttention(frame): float
    }

    class PostureAnalyzer {
        -keypoints: list
        +analyze(frame): float
        +getRecommendation(): string
    }

    class FatigueAnalyzer {
        -eyeClosureThreshold: float
        +analyze(frame): float
        +detectEyeClosure(): boolean
    }

    class StressAttentionAnalyzer {
        -movementThreshold: float
        +analyze(frame): float
        +getHeadMovement(): float
    }

    %% ============== MODULE BACKEND ==============

    class APIServer {
        -host: string
        -port: int
        -database: Database
        +startSession(userId): Session
        +recordMetrics(metrics): void
        +triggerAlert(event): void
        +getHistoricalData(userId): Metric[]
    }

    class DecisionOrchestrator {
        -thresholds: dict
        -aiEngine: AIEngine
        +evaluateMetrics(metrics): Action
        +determineAlert(event): Recommendation
        +adaptRecommendations(metrics, context): string
    }

    class AIEngine {
        -llm: LLM
        -vectorStore: VectorStore
        -ragRetriever: RAGRetriever
        +generateResponse(query, context): string
        +generateStudyPlan(history): StudyPlan
        +scoreRelevance(doc, query): float
    }

    class RAGRetriever {
        -vectorStore: VectorStore
        -chunkSize: int
        +retrieveDocuments(query, topK): Document[]
        +rankDocuments(query, candidates): Document[]
    }

    %% ============== PERSISTANCE ==============

    class Database {
        -connectionString: string
        -pool: ConnectionPool
        +saveSession(session): void
        +saveMetrics(metrics): void
        +getSessionHistory(userId): Session[]
        +queryMetrics(filter): Metric[]
    }

    class VectorStore {
        -client: ChromaDB
        -collections: dict
        +addDocuments(docs, embeddings): void
        +searchSimilar(query, topK): Document[]
        +deleteDocument(docId): void
    }

    class Document {
        -id: string
        -userId: int
        -title: string
        -content: string
        -embedding: vector
        -uploadedAt: datetime
        +getChunks(size): string[]
    }

    %% ============== INTERFACES CLIENT ==============

    class MobileApp {
        -userId: int
        -apiClient: APIClient
        +displayRealTimeMetrics(): void
        +showAlert(event): void
        +chatWithAI(query): string
        +viewStatistics(): void
    }

    class PiClient {
        -cameraManager: CameraManager
        -analyzer: VisionAnalyzer
        -apiClient: APIClient
        -display: LocalDisplay
        +captureAndAnalyze(): void
        +sendMetricsToBackend(metrics): void
        +handleAlert(event): void
        +feedbackHardware(action): void
    }

    class LocalDisplay {
        -screen: Device
        +showAlert(type, severity): void
        +displayMetrics(metric): void
        +clearScreen(): void
    }

    %% ============== RECOMMENDATIONS ==============

    class Recommendation {
        -type: string
        -priority: int
        -content: string
        -basedOnScores: Metric
        +display(): string
        +execute(): void
    }

    class StudyPlan {
        -userId: int
        -generatedAt: datetime
        -sessions: StudySession[]
        +adjustToDifficulty(level): void
        +synchronizeWithMetrics(metric): void
    }

    class StudySession {
        -startTime: time
        -duration: int
        -subject: string
        -difficulty: string
        +canAdjust(newDuration): boolean
    }

    %% ============== ASSOCIATIONS ==============

    User "1" --> "*" Session : owns
    User "1" --> "*" Document : uploads
    
    Session "1" --> "*" Metric : contains
    Session "1" --> "*" Event : triggers
    
    Metric --> VisionAnalyzer : produced by
    VisionAnalyzer --> PostureAnalyzer : uses
    VisionAnalyzer --> FatigueAnalyzer : uses
    VisionAnalyzer --> StressAttentionAnalyzer : uses
    
    APIServer "1" --> "1" Database : uses
    APIServer "1" --> "1" DecisionOrchestrator : uses
    APIServer "1" --> "1" AIEngine : uses
    
    DecisionOrchestrator --> Recommendation : generates
    
    AIEngine "1" --> "1" RAGRetriever : uses
    AIEngine "1" --> "1" VectorStore : queries
    
    VectorStore "1" --> "*" Document : manages
    VectorStore "1" --> "*" RAGRetriever : serves
    
    Database "1" --> "*" Session : stores
    Database "1" --> "*" User : manages
    
    MobileApp --> APIServer : consumes
    PiClient --> APIServer : consumes
    
    PiClient "1" --> "1" VisionAnalyzer : uses
    PiClient "1" --> "1" LocalDisplay : controls
    
    Recommendation --> StudyPlan : suggests
    StudyPlan "1" --> "*" StudySession : contains

    %% ============== STYLES ==============
    style User fill:#e1f5ff
    style Session fill:#e3f2fd
    style Metric fill:#f3e5f5
    style Event fill:#fce4ec
    style VisionAnalyzer fill:#fff3e0
    style PostureAnalyzer fill:#fff9c4
    style APIServer fill:#e0f2f1
    style Database fill:#f1f8e9
    style VectorStore fill:#e8f5e9
    style MobileApp fill:#fbe9e7
    style PiClient fill:#ffe0b2
```

## Hiérarchie et Dépendances

### Couches Identifiées

1. **Couche Présentation** : `MobileApp`, `PiClient`, `LocalDisplay`
2. **Couche Métier** : `APIServer`, `DecisionOrchestrator`, `VisionAnalyzer`, `AIEngine`
3. **Couche Persistance** : `Database`, `VectorStore`, `Document`
4. **Couche Modèle** : `User`, `Session`, `Metric`, `Event`, `Recommendation`

### Flux Principal

```
PiClient (capture) 
  ↓
VisionAnalyzer (analyse)
  ↓
APIServer (traite)
  ↓
DecisionOrchestrator (évalue)
  ↓
AIEngine + RAGRetriever (contexte)
  ↓
Recommendation (affichage mobile & pi)
```
