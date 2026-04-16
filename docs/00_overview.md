# 00 - Présentation du Projet : Smart Focus & Life Assistant

## Résumé
Smart Focus & Life Assistant est un système intégré IoT et IA conçu pour améliorer la productivité et le bien-être lors des activités quotidiennes. En utilisant la vision par ordinateur et divers capteurs, le système surveille l'état de l'utilisateur (posture, fatigue, stress et attention) et fournit des retours en temps réel tout en agrégeant les données pour une analyse à long terme sur une **application mobile**.

## Objectifs du Système
- **Productivité** : Minimiser les distractions et maintenir la concentration pendant les sessions de travail/étude.
- **Bien-être** : Prévenir la fatigue physique (posture) et l'épuisement mental (fatigue/stress).
- **Intelligence** : Fournir des conseils personnalisés et une planification via un assistant IA basé sur le RAG (accessible via l'application).

## Responsabilités
### Responsable Hardware & Vision par Ordinateur (Moi)
- **Module** : `pi_client`
- **Périmètre** : Intégration matérielle, algorithmes de CV (posture, fatigue, stress, attention), moteur de décision local (alertes sur **écran du boîtier** et hardware), communication IoT-Backend.

### Responsable Backend & IA (Binôme)
- **Module** : `backend`, `application_mobile`
- **Périmètre** : Développement FastAPI, conception de la base de données, implémentation RAG/LLM, application mobile Streamlit/Flutter, orchestration API.

## Hypothèses
1. **Connectivité** : Le Raspberry Pi dispose d'une connexion Wi-Fi stable au réseau local où le backend est hébergé.
2. **Matériel** : Un Raspberry Pi 4/5 est utilisé pour une puissance de traitement CV suffisante.
3. **Stockage** : SQLite est utilisé pour le prototypage (comme vu dans `sql_app.db`), avec une migration potentielle vers PostgreSQL pour la production.
4. **IA** : Le traitement LLM (RAG) est géré par le serveur backend (via l'API OpenAI ou un Ollama local).
5. **Confidentialité** : Tout le traitement CV est effectué localement sur le Pi ; seuls les scores et les événements sont envoyés au backend.
