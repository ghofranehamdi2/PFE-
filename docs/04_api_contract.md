# 04 - Contrat API (FastAPI)

## URL de Base : `http://<ip-serveur>:8000/api/v1`

| Méthode | Endpoint | Description | 
| --- | --- | --- |
| POST | `/auth/login` | Retourne un jeton JWT pour l'utilisateur/appareil. |
| POST | `/sessions/start` | Commence une nouvelle session de focus. Retourne `session_id`. |
| POST | `/sessions/{id}/metrics` | Télécharge les scores de métriques bruts (0..1). |
| POST | `/sessions/{id}/events` | Enregistre des événements spécifiques (ex: `POSTURE_BAD`). |
| POST | `/sessions/{id}/end` | Finalise la session et calcule le résumé. |
| GET | `/device/config` | Récupère les seuils et paramètres pour le Pi. |
| POST | `/ai/chat` | Interaction avec le chatbot IA (RAG). |
| GET | `/stats/summary` | Données de résumé pour l'application mobile. |

## Exemples

### 1. Téléchargement des Métriques
**POST** `/sessions/101/metrics`
```json
{
  "timestamp": "2026-03-03T23:30:00Z",
  "posture_score": 0.85,
  "fatigue_score": 0.12,
  "stress_score": 0.05,
  "attention_score": 0.95
}
```

### 2. Enregistrement d'Événement
**POST** `/sessions/101/events`
```json
{
  "event_type": "FATIGUE_HIGH",
  "priority": "MEDIUM",
  "metadata": {
    "eye_closure": 0.8,
    "blink_rate": 2
  }
}
```
