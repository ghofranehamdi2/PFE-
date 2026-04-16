# Smart Focus & Life Assistant (MVP)

Ce projet est un prototype MVP pour un assistant intelligent IoT (Raspberry Pi) et IA conçu pour surveiller la concentration, la posture et le bien-être.

## Architecture

- **Backend**: FastAPI (Python) + SQLAlchemy (SQLite)
- **Client Pi**: Script Python simulant des capteurs (Caméra, Micro)
- **IA**: Couche modulaire intégrée au backend (stubs pour MVP)

## Structure du Projet

```text
/backend         # API FastAPI
/pi_client       # Script Raspberry Pi
docker-compose.yml
README.md
```

## Setup - Backend

1. Aller dans le dossier backend : `cd backend`
2. Créer un environnement virtuel : `python -m venv venv`
3. Activer l'env : `.\venv\Scripts\activate` (Windows)
4. Installer les dépendances : `pip install -r requirements.txt`
5. Lancer le serveur : `uvicorn app.main:app --reload`

L'API sera accessible sur : `http://localhost:8000`
Documentation interactive : `http://localhost:8000/docs`

## Setup - Pi Client

1. Aller dans le dossier client : `cd pi_client`
2. Installer les dépendances : `pip install requests`
3. Lancer le client : `python main.py`

*Note : Le client Pi simule des lectures de capteurs et envoie des données au backend toutes les 5 secondes.*

## Points d'Entrée API (Endpoints)

- `POST /api/v1/auth/login/access-token` : Authentification
- `POST /api/v1/sessions/start` : Démarrer une session de travail
- `POST /api/v1/events/ingest` : Envoyer des données de capteurs (Pi -> Backend)
- `GET /api/v1/settings/` : Récupérer les réglages utilisateur

## Simulation IA

Le module `app/services/ai_processor.py` contient la logique de décision simple pour le MVP :
- Si Score Posture < 0.7 -> Alerte "Mauvaise posture"
- Si Score Fatigue < 0.7 -> Alerte "Fatigue"
