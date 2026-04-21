# Conception UML Globale

## Portee
Ce document consolide la conception UML globale du projet Smart Focus & Life Assistant.
Il relie les besoins fonctionnels, les structures logiques, les interactions et la planification.

## Livrables UML Globaux

1. Diagramme de cas d'utilisation global.
2. Diagramme de classes global.
3. Diagramme de sequence global.
4. Diagramme de Gantt global.

## Architecture de Reference

Le systeme est compose de 4 blocs:

- Edge IoT: Raspberry Pi et moteur de vision locale.
- Backend: API FastAPI, services metier, persistance.
- IA/RAG: indexation documentaire, retrieval, generation.
- Mobile: consultation temps reel, historique, chat et planning.

## Traceabilite UML

| Besoin metier | Cas d'utilisation | Classes principales | Flux sequence associe |
|---|---|---|---|
| Suivre la concentration en session | Demarrer session, analyser flux | PiClient, VisionPipeline, MetriqueVision, DecisionEngine | Session focus complete |
| Alerter en temps reel | Declencher alerte locale | EvenementAlerte, AlertService, LocalFeedbackController | Session focus complete |
| Consulter les donnees | Consulter statistiques | SessionService, MetricsService, Repository | Historique et stats |
| Aider l'utilisateur via IA | Poser question IA | AIService, RAGService, LLMProvider, VectorStore | Chat temps reel |
| Produire un planning adapte | Generer planning d'etude | AIService, SessionFocus, MetriqueVision | Import doc + planning |

## Decisions de Conception

1. Separation claire entre analyse edge et orchestration backend.
2. Persistance relationnelle pour sessions/metriques/evenements.
3. Couche vectorielle dediee au retrieval documentaire.
4. Services metier centres sur des responsabilites uniques.
5. Adaptation intelligente basee sur metriques recentes et contexte historique.

## Regles de Coherence UML

1. Tout cas d'utilisation critique doit etre relie a au moins un flux sequence.
2. Toute classe de service doit avoir une dependance explicite vers la persistance ou un provider externe.
3. Les entites metier ne doivent pas contenir de logique d'infrastructure.
4. Les interactions IA doivent passer par AIService pour centraliser la gouvernance des prompts.

## Roadmap d'Evolution UML

1. Ajouter un diagramme de composants executable par module.
2. Completer un diagramme d'etats pour la session focus.
3. Ajouter un diagramme de deploiement cible (local + cloud).
4. Integrer une matrice risques/mitigations reliee aux cas d'utilisation critiques.

## References

- Voir 01_cas_utilisation_global.md pour la vue metier.
- Voir 02_diagramme_classe_global.md pour la structure objet.
- Voir 03_diagramme_sequence_global.md pour les interactions runtime.
- Voir 09_diagramme_gantt_global.md pour la planification projet.
