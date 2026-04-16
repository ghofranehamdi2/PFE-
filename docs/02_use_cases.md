# 02 - Analyse Détaillée des Cas d'Utilisation

## 1. Cas d'Utilisation Global (Macro)

Ce diagramme présente les interactions de haut niveau entre les acteurs et le système.

```puml
@startuml
left to right direction
actor "Utilisateur" as U
actor "Assistant IA" as AI
actor "Hardware (Pi)" as HW
actor "Application Mobile" as APP

rectangle "Système Smart Focus & Life Assistant" {
  (Gérer les Sessions) as UC1
  (Suivi Temps Réel Vision) as UC2
  (Retours & Alertes) as UC3
  (Interaction Assistant RAG) as UC4
  (Analyse de l'Historique) as UC5
}

U -- UC1
U -- UC4
U -- UC5

UC1 ..> UC2 : <<include>>
UC2 ..> UC3 : <<include>>

UC3 -- HW
UC4 -- AI
UC5 -- APP
@enduml
```

## 2. Cas d'Utilisation : Module pi_client (Foyer de Vision)

C'est ici que se concentre la logique de capture et d'analyse locale sur le Raspberry Pi.

```puml
@startuml
left to right direction
actor "Utilisateur" as U
actor "Caméra" as Cam
actor "Écran du Boîtier" as SCR

rectangle "Module pi_client" {
  (Capturer Vidéo) as capture
  (Analyser Posture) as post
  (Analyser Fatigue) as fatigue
  (Analyser Stress/Attention) as att
  (Vérifier Seuils) as decision
  (Envoyer au Backend) as transmit
  (Alerter sur l'Écran) as alert_scr
  (Alerter Hardware) as alert_hw
}

capture -- Cam
Cam -- U

capture ..> post : <<include>>
capture ..> fatigue : <<include>>
capture ..> att : <<include>>

post ..> decision : <<include>>
fatigue ..> decision : <<include>>
att ..> decision : <<include>>

decision ..> alert_scr : <<extend>>
decision ..> alert_hw : <<extend>>
decision ..> transmit : <<include>>

alert_scr -- SCR
@enduml
```

## 3. Cas d'Utilisation : Module Assistant IA (RAG)

Interaction entre l'utilisateur via l'application mobile, ses documents et l'IA.

```puml
@startuml
left to right direction
actor "Utilisateur" as U
actor "LLM / OpenAI" as LLM
actor "Application Mobile" as APP

rectangle "Module Assistant IA" {
  (Importer PDF via App) as upload
  (Poser une Question via App) as ask
  (Générer Planning d'Étude) as plan
  (Adapter Planning aux Scores) as adapt
}

U -- APP
APP -- upload
APP -- ask
APP -- plan

upload ..> ask : <<precedes>>
plan ..> adapt : <<include>>
ask -- LLM
plan -- LLM
@enduml
```
