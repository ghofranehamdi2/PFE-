# 📐 Diagrammes de Séquence – Smart Focus & Life Assistant

**Version** : 1.0  
**Date** : 18 Février 2026  
**Phase** : Conception  

---

## 1. 🔐 Module Authentification

### 1.1 Inscription (UC1)

```mermaid
sequenceDiagram
    actor User as 👤 Utilisateur
    participant App as 📱 App Flutter
    participant API as ⚙️ Backend FastAPI
    participant DB as 🗄️ PostgreSQL

    User->>App: Saisir email, mot de passe, nom
    App->>App: Valider les champs (format email, mdp fort)
    App->>API: POST /auth/register {email, password, full_name}
    API->>DB: SELECT * FROM users WHERE email = ?
    
    alt Email déjà utilisé
        DB-->>API: Utilisateur trouvé
        API-->>App: 409 Conflict "Email déjà utilisé"
        App-->>User: Afficher erreur
    else Email disponible
        DB-->>API: Aucun résultat
        API->>API: Hasher le mot de passe (bcrypt)
        API->>DB: INSERT INTO users (email, password_hash, full_name)
        DB-->>API: User créé (id)
        API->>DB: INSERT INTO user_profiles (user_id, defaults)
        DB-->>API: Profil créé
        API->>API: Générer JWT (access + refresh)
        API-->>App: 201 Created {user, access_token, refresh_token}
        App->>App: Stocker token (Hive)
        App-->>User: Rediriger vers Dashboard
    end
```

### 1.2 Connexion (UC2)

```mermaid
sequenceDiagram
    actor User as 👤 Utilisateur
    participant App as 📱 App Flutter
    participant API as ⚙️ Backend FastAPI
    participant DB as 🗄️ PostgreSQL
    participant Redis as 🔴 Redis Cache

    User->>App: Saisir email et mot de passe
    App->>API: POST /auth/login {email, password}
    API->>DB: SELECT * FROM users WHERE email = ?
    
    alt Utilisateur non trouvé
        DB-->>API: Aucun résultat
        API-->>App: 401 Unauthorized
        App-->>User: "Email ou mot de passe incorrect"
    else Utilisateur trouvé
        DB-->>API: User (id, password_hash)
        API->>API: Vérifier bcrypt(password, hash)
        
        alt Mot de passe incorrect
            API-->>App: 401 Unauthorized
            App-->>User: "Email ou mot de passe incorrect"
        else Mot de passe correct
            API->>DB: UPDATE users SET last_login = NOW()
            API->>API: Générer JWT (access + refresh)
            API->>Redis: Stocker session active
            API-->>App: 200 OK {user, access_token, refresh_token}
            App->>App: Stocker token localement (Hive)
            App-->>User: Rediriger vers Dashboard
        end
    end
```
