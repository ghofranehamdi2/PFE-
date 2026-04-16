# 🗄️ Schéma Base de Données PostgreSQL (ERD) – Smart Focus & Life Assistant

**Version** : 1.0  
**Date** : 01 Mars 2026  
**Phase** : Conception  
**SGBD** : PostgreSQL 15+  

---

## 1. ERD Global (Mermaid)

```mermaid
erDiagram

    %% ── UTILISATEURS ──────────────────────────────────────
    users {
        SERIAL      id              PK
        VARCHAR255  email           UK  "NOT NULL"
        VARCHAR255  hashed_password     "NOT NULL"
        VARCHAR100  full_name           "NOT NULL"
        VARCHAR20   role                "DEFAULT student"
        TIMESTAMP   created_at          "DEFAULT now()"
        TIMESTAMP   last_login
        BOOLEAN     is_active           "DEFAULT true"
    }

    user_profiles {
        SERIAL      id              PK
        INT         user_id         FK  "NOT NULL"
        INT         daily_focus_goal    "DEFAULT 120 (min)"
        VARCHAR50   preferred_schedule  "morning|afternoon|evening"
        BOOLEAN     notif_enabled       "DEFAULT true"
        JSONB       notif_preferences
        TIMESTAMP   updated_at          "DEFAULT now()"
    }

    esp32_devices {
        SERIAL      id              PK
        INT         user_id         FK  "NOT NULL"
        VARCHAR50   device_id           "UNIQUE"
        VARCHAR20   firmware_version
        VARCHAR20   status              "online|offline|pairing"
        TIMESTAMP   last_seen
        INET        ip_address
    }
```
(Note: ERD partially shown for brevity in this tool call, full content based on user snippet)
