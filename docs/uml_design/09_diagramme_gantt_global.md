# Diagramme de Gantt Global

## Objectif
Ce diagramme représente le planning global du projet Smart Focus & Life Assistant en cohérence avec le plan Scrum du dossier documentation.

## Diagramme de Gantt (Mermaid)

```mermaid
gantt
    title Smart Focus & Life Assistant - Planning Global
    dateFormat  YYYY-MM-DD
    axisFormat  %d/%m
    excludes    weekends

    section Sprint 0 - Conception
    Architecture, UML, API, DB          :done, s0, 2026-02-03, 7d

    section Sprint 1 - Fondations Backend
    Setup FastAPI + Auth JWT            :done, s1a, 2026-02-10, 5d
    Modeles SQLAlchemy + migrations     :done, s1b, 2026-02-17, 5d
    Client API edge de base             :done, s1c, 2026-02-17, 5d

    section Sprint 2 - Vision MVP Edge
    Pipeline capture multi-thread       :done, s2a, 2026-02-24, 5d
    Detection posture/fatigue           :done, s2b, 2026-03-03, 5d
    Ingestion metriques backend         :done, s2c, 2026-03-03, 5d

    section Sprint 3 - Mobile v1
    Dashboard mobile + historique       :active, s3a, 2026-03-10, 6d
    Alertes en temps reel               :active, s3b, 2026-03-17, 4d
    Integration stress/attention edge   :active, s3c, 2026-03-17, 4d

    section Sprint 4 - Assistant IA RAG
    Parsing documents + indexation      :s4a, 2026-03-24, 5d
    Integration LLM + endpoint chat     :s4b, 2026-03-31, 5d
    Generation planning personnalise    :s4c, 2026-03-31, 5d

    section Sprint 5 - Adaptation UX
    Personnalisation des seuils         :s5a, 2026-04-07, 4d
    Synchronisation config edge         :s5b, 2026-04-07, 4d
    Tests integration transverses       :s5c, 2026-04-14, 4d

    section Sprint 6 - Stabilisation
    Correctifs et optimisation          :s6a, 2026-04-21, 4d
    Validation finale et demo           :s6b, 2026-04-28, 3d
```

## Jalons

| Jalon | Date cible | Critere de validation |
|---|---|---|
| M1 - Base technique stable | 2026-02-21 | API auth + DB operationnels |
| M2 - Boucle edge complete | 2026-03-07 | Capture, scoring, alertes, sync |
| M3 - Mobile v1 fonctionnel | 2026-03-21 | Dashboard et historique consultables |
| M4 - IA RAG exploitable | 2026-04-04 | Chat contextualise + planning genere |
| M5 - Integration complete | 2026-04-18 | Flux end-to-end valide |
| M6 - Version demo | 2026-04-30 | Stabilisation et scenario de demo valide |

## Notes

- Les dates sont proposees pour une vue globale et peuvent etre ajustees selon les contraintes académiques.
- Le sprint en cours est marque active.
- Le diagramme est compatible avec les renderers Mermaid de VS Code et GitHub.
