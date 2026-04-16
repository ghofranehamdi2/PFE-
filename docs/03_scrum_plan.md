# 03 - Plan Scrum & Implémentation

## Sprint 0 : Conception (1 Semaine)
**Objectif** : Finaliser la conception et la configuration de l'environnement.
- **Livrables** : Architecture, UML, Contrat API, Schéma BD.
- **Assignation** : Tous (Moi + Binôme).

## Sprint 1 : Fondations (Backend & Auth)
**Objectif** : API accessible et stockage de base.
- **Tâches (Binôme)** : 
  - Boilerplate FastAPI.
  - Authentification JWT.
  - Implémentation du schéma DB (SQLAlchemy).
- **Tâches (Moi)** : 
  - Verrouillage de l'environnement `pi_client`.
  - Client API de base (Flux de connexion).

## Sprint 2 : MVP Vision & Logique Edge
**Objectif** : Pipeline fonctionnel de la capture à l'alerte.
- **Tâches (Moi)** :
  - Affinement des algorithmes de Posture & Fatigue.
  - Moteur de décision (Seuils locaux).
  - Pipeline de capture multi-threadé.
- **Tâches (Binôme)** :
  - Endpoints d'ingestion de métriques.
  - Système de journalisation d'événements.

## Sprint 3 : Application Mobile (v1)
**Objectif** : L'utilisateur peut voir ses données sur son smartphone.
- **Tâches (Binôme)** :
  - Structure de l'application mobile (Streamlit/Flutter).
  - Visualisation des données (Matplotlib/Plotly).
  - Vue historique des sessions.
- **Tâches (Moi)** : 
  - Intégration des analyseurs de Stress & Attention.
  - Affichage des alertes sur l'**écran du boîtier**.

## Sprint 4 : Assistant Intelligent (RAG)
**Objectif** : Chatbot avec contexte.
- **Tâches (Binôme)** :
  - Configuration de la Vector DB (Chroma/FAISS).
  - Parseur de fichiers PDF/Markdown.
  - Intégration LLM (OpenAI/Ollama).
- **Tâches (Moi)** : 
  - Affinement des retours matériels (modèles de LED).

## Sprint 5 : Planification Proactive & UX
**Objectif** : Le système s'adapte à l'utilisateur.
- **Tâches (Binôme)** :
  - Logique de génération de planning.
  - API de paramètres utilisateur (Personnalisation des seuils).
- **Tâches (Moi)** :
  - Synchronisation de la configuration côté Edge.
  - Tests d'intégration finaux.

## Sprint 6 : Polissage & Extension
**Objectif** : Prêt pour la démonstration.
- **Tâches** : Corrections de bugs, optimisation du déploiement, rapport final.
