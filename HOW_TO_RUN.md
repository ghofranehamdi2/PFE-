# Guide d'utilisation : Relancer le Smart Focus Assistant

Ce guide explique comment lancer manuellement le projet à partir d'un terminal Windows.

## Prérequis
- PostgreSQL doit être lancé localement sur votre PC.
- Les ports 8000 (Backend) et le flux caméra doivent être disponibles.

---

## Étape 1 : Lancer le Backend (Serveur API)

Ouvrez un **premier terminal** et exécutez ces commandes :

```powershell
# Aller dans le dossier du projet
cd d:\PFE\backend

# Activer l'environnement virtuel et lancer le serveur
.\backend_venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Laissez ce terminal ouvert pour voir les requêtes arriver.*


---

## Étape 2 : Lancer le Modèle CV (Pipeline Vision)

Ouvrez un **deuxième terminal** et exécutez ces commandes :

```powershell 
# Aller dans le dossier du projet
cd d:\PFE\pi_client

# Activer l'environnement virtuel et lancer le script
.\vision_venv\Scripts\activate
python main_cv.py
``` 

### Touches Clavier
- **`q`** : Pour quitter proprement le modèle et fermer la fenêtre caméra.

---

## Architecture et Optimisations
- **Base de données** : PostgreSQL (`smart_focus` sur `127.0.0.1:5432`).
- **Fluidité Vidéo** : Optimisé pour une latence minimale via l'analyse asynchrone et le saut d'images (frame skipping). 
