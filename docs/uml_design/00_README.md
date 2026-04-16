# 🎨 UML Design - Smart Focus Assistant

**Conception UML complète du projet Smart Focus Assistant** – Architecture globale et diagrammes détaillés par module.

---

## 📂 Structure

```
📁 uml_design/
├─ 📄 INDEX.md                           ← 👈 LIRE D'ABORD (Table des matières)
├─ 📊 01_cas_utilisation_global.md       (8 cas d'utilisation + 4 acteurs)
├─ 📐 02_diagramme_classe_global.md      (30+ classes, 4 couches)
├─ 🔄 03_diagramme_sequence_global.md    (4 scénarios complets)
├─ 📷 04_module_pi_client.md             (Vision analysis)
├─ 🔗 05_module_backend.md               (FastAPI + Decision + AI)
├─ 📱 06_module_mobile_app.md            (Flutter UI)
├─ 🧠 07_module_ia_rag.md                (LLM + Vector Store)
├─ 🗄️ 08_module_database.md              (PostgreSQL ERD)
└─ 📋 README.md                          (Ce fichier)
```

---

## 🎯 Démarrage Rapide

### Lecteur Impatient (5 min)
1. Lire [INDEX.md](INDEX.md) – Vue d'ensemble
2. Voir [Diagramme Classes Global](02_diagramme_classe_global.md) – Architecture générale

### Lecteur Standard (20 min)
1. [Cas d'Utilisation](01_cas_utilisation_global.md) – Comprendre les besoins
2. [Diagrammes Classes](02_diagramme_classe_global.md) – Architecture
3. [Diagrammes Séquence](03_diagramme_sequence_global.md) – Flux clés

### Développeur Détaillé (1h)
→ Lire tous les fichiers en ordre numérique

---

## 📊 Contenu Résumé

| # | Fichier | Type | Contenu |
|---|---------|------|---------|
| 01 | Cas d'Utilisation | Use Case | 8 CU, 4 acteurs, relations |
| 02 | Classes Global | Class | 30+ classes, 4 couches, dépendances |
| 03 | Séquence Global | Sequence | 4 scénarios : Focus, Planning, Chat, Stats |
| 04 | Pi_Client | Architecture | Vision + Hardware + API |
| 05 | Backend | Architecture | FastAPI + Orchestration + AI |
| 06 | Mobile | Architecture | Flutter + State + Services |
| 07 | IA/RAG | Architecture | LLM + Vector DB + Context |
| 08 | Database | ERD | PostgreSQL + Repositories |

---

## 🔍 Recherche Rapide

### Je veux comprendre...

**"Comment fonctionne une session complète ?"**  
→ [Diagramme Séquence Scénario 1](03_diagramme_sequence_global.md#scénario-1--session-de-focus-complète-capture--alerte--feedback)

**"Quelles classes existent dans le système ?"**  
→ [Diagramme Classes Global](02_diagramme_classe_global.md)

**"Comment marche la vision (Pi_Client) ?"**  
→ [Module Pi_Client](04_module_pi_client.md) + Boucle principale

**"Où sont stockées les données ?"**  
→ [Module Database ERD](08_module_database.md)

**"Comment fonctionne le RAG/IA ?"**  
→ [Module IA/RAG Flux](07_module_ia_rag.md)

**"Comment l'app mobile affiche les données ?"**  
→ [Module Mobile - Écrans & State](06_module_mobile_app.md)

**"Quels sont les endpoints API ?"**  
→ [Module Backend - APIServer](05_module_backend.md#diagramme-de-classes---module-backend-fastapi)

---

## 🎓 Lectures Recommandées par Rôle

### 👨‍💻 Développeur Backend
1. [Cas d'Utilisation](01_cas_utilisation_global.md)
2. [Backend Module](05_module_backend.md) ⭐⭐⭐
3. [Database Module](08_module_database.md) ⭐⭐⭐
4. [IA/RAG Module](07_module_ia_rag.md) ⭐⭐
5. [Classes Global](02_diagramme_classe_global.md)

### 🎨 Développeur Mobile
1. [Cas d'Utilisation](01_cas_utilisation_global.md)
2. [Mobile Module](06_module_mobile_app.md) ⭐⭐⭐
3. [Backend Endpoints](05_module_backend.md#diagramme-de-classes---module-backend-fastapi) ⭐⭐
4. [Classes Global](02_diagramme_classe_global.md)

### 📷 Ingénieur Vision/IA
1. [Pi_Client Module](04_module_pi_client.md) ⭐⭐⭐
2. [IA/RAG Module](07_module_ia_rag.md) ⭐⭐⭐
3. [Backend - Decision Orchestrator](05_module_backend.md)
4. [Séquence - Adaptation](03_diagramme_sequence_global.md#scénario-3--interaction-chat-temps-réel-en-session)

### 🗄️ DBA / Ingénieur Données
1. [Database Module](08_module_database.md) ⭐⭐⭐
2. [Model Entities](02_diagramme_classe_global.md#--modèle-objet-complet-du-système) ⭐⭐
3. [Classes Global](02_diagramme_classe_global.md)

### 🧠 Architecte Logiciel
1. [Toute documentation dans l'ordre]
2. [INDEX.md](INDEX.md) avec relations
3. [Diagramme Classes Global](02_diagramme_classe_global.md)

---

## 💡 Points Clés du Design

### Architecture
- ✅ **4 couches** : Présentation → Métier → Persistance → Modèle
- ✅ **Asynchrone** : Métriques traitées en arrière-plan
- ✅ **Real-time** : WebSocket pour updates temps réel
- ✅ **RAG Context** : LLM enrichi avec docs + métriques

### Pattern
- ✅ **Repository Pattern** : Accès données abstrait
- ✅ **Provider Pattern** : State Flutter
- ✅ **Service Layer** : Logique métier centralisée
- ✅ **MVC** : Model-View-Controller frontend

### Performance
- 📊 **Vision** : 30 FPS, < 100ms latence
- 📊 **API** : Rate limiting, async processing
- 📊 **Database** : Indexation optimisée, transactions
- 📊 **IA/RAG** : Retrieval < 1s, LLM < 5s

---

## 📌 Conventions UML

### Visualisation
```
[Classe]
├─ Attributs (-)
├─ Méthodes (+)
└─ Relations (→, ←, ⬍, ◆)

(CaseUtilisation)
├─ Include (→)
├─ Extend (⇢)
└─ Précédence (⋯)

Séquence
├─ Flux normal (→)
├─ Réponse (←)
└─ Appel auto (⟲)
```

### Symboles
- `👤` Acteur
- `🔗` Système/Service
- `📊` Données
- `*` Multiplicité 0..*
- `1` Multiplicité 1..1

---

## 🔗 Fichiers Liés du Projet

```
docs/
├─ INDEX.md (Ce fichier de navigation) ← Vous êtes ici
├─ 01_architecture.md (Composants 3D)
├─ 02_use_cases.md (Puml format)
├─ 04_api_contract.md (Endpoints)
├─ 05_database_design.md (Schéma)
├─ 06_ai_modules.md (RAG pipeline)
└─ uml_design/
    └─ [8 fichiers détaillés]
```

---

## ✨ Highlights du Design

### 🎯 Unity de Conception
Tous les diagrammes couvrent le même projet, avec :
- **Cohérence** entre modules
- **Traçabilité** CU → Classes → Séquences
- **Complétude** from capture to display

### 🔄 Traceability
```
Cas d'Utilisation
  ↓
Classes impliquées
  ↓
Séquence d'exécution
  ↓
Repository/Service appelés
```

### 🚀 Prêt pour développement
Tous les diagrammes sont **orientés implémentation** :
- Classes nomées et structurées
- Méthodes et signatures claires
- Flux d'exécution détaillé
- Database relationships complètes

---

## 🤝 Questions Fréquentes

**Q: Par où commencer ?**  
R: [INDEX.md](INDEX.md), puis votre rôle en haut.

**Q: Où voir comment les modules interagissent ?**  
R: [Diagramme Classe Global](02_diagramme_classe_global.md) ou [INDEX.md - Relations](INDEX.md#-relations-inter-modules)

**Q: Comment implémenter le backend ?**  
R: [Backend Module](05_module_backend.md) + [Database Module](08_module_database.md)

**Q: C'est quoi le flux complet d'une métrique ?**  
R: [Séquence Scénario 1](03_diagramme_sequence_global.md#scénario-1--session-de-focus-complète-capture--alerte--feedback)

**Q: Tous les diagrammes sont à jour ?**  
R: ✅ Avril 2026 - Version 1.0

---

## 🎁 Bonus

### Diagrammes En Format Mermaid
Tous les diagrammes utilisent **Mermaid.js** – Vous pouvez :
- Copier-coller dans [mermaid.live](https://mermaid.live)
- Modifier et exporter SVG/PNG
- Intégrer dans des wikis/documents

### Comment Exporter
1. Ouvrir le fichier markdown
2. Copier bloc `\`\`\`mermaid ... \`\`\``
3. Sur [mermaid.live](https://mermaid.live)
4. Exporter en image

---

## 📞 Support et Clarifications

Pour questions ou clarifications sur les diagrammes :
1. Vérifier [INDEX.md](INDEX.md) - Vue d'ensemble
2. Chercher le module concerné
3. Lire la description et légende
4. Consulter le fichier source markdown

---

**Créé** : Avril 2026  
**Version** : 1.0 Complète  
**Status** : ✅ Prêt Production  
**Format** : Markdown + Mermaid  

---

**👉 [Commençons par INDEX.md →](INDEX.md)**
