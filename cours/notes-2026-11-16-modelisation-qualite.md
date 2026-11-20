# Bloc « Qualité et modélisation des données » — Séance d'introduction

*Transcription remise en forme — 16 novembre 2026*

> Note : la transcription automatique d'origine contenait beaucoup d'erreurs de reconnaissance. Les termes techniques ont été corrigés (ex. « Datahops » → DataOps, « médalium » → architecture Médaillon, « basilles électorielles » → bases vectorielles, « protéger » → Protégé). Les passages inaudibles ou incompréhensibles ont été résumés ou signalés par *[passage inaudible]*.

---

## 1. Contexte : ce qui a été fait l'an dernier

- L'an dernier, le projet portait sur l'**analyse de données issues d'articles** (scraping d'articles, développement de pipelines, découverte de différents types de bases de données).
- Cette partie était surtout **technique** : construction d'un pipeline de données de bout en bout.
- Cette année, il faudra **refaire un pipeline**, mais on y passera **peu de temps** : les notebooks et le code de l'an dernier sont disponibles et une grande partie peut être réutilisée.
- L'accent sera mis sur la **modélisation** et la **qualité des données**.

---

## 2. Organisation du bloc : 4 cours

| # | Cours | Contenu |
|---|-------|---------|
| 1 | **Modélisation des données** (Marine + l'intervenant) | Rechercher et mobiliser des sources de données, constituer un modèle interne, évaluer la pertinence, gérer les données manquantes, données personnelles et **RGPD** |
| 2 | **Indicateurs de qualité** | Définir des indicateurs pour s'assurer que les décisions prises sont rationnelles par rapport aux objectifs |
| 3 | **Visualisation / outils décisionnels** | Construire des tableaux de bord une fois le pipeline en place, pour mettre l'information à disposition des décideurs |
| 4 | **Présentation** (1 journée) | Non technique : présenter ses travaux à des publics intéressés (ex. ceux qui possèdent les données traitées) |

### Calendrier
- **Cette semaine** : cours sur les indicateurs de qualité.
- Le cours **modélisation & qualité** est découpé en **2 sessions** (nouveauté par rapport aux années précédentes) :
  - **Session 1 (cette semaine — aujourd'hui, demain matin, mercredi matin)** : spécification, compréhension de ce que sont les données.
  - **Session 2 (début décembre)** : partie plus technique sur la qualité des données, approfondissement **RGPD / données personnelles**, et **présentation des modèles** réalisés.
- Les dates exactes seront communiquées plus tard.

---

## 3. Évaluation

- **Au moins 2 notes** :
  1. Une note sur le **cours lui-même** (modalités encore ouvertes).
  2. Une note sur le **bloc**, construite à partir des **barèmes du RNCP**.
- Objectif de la notation RNCP : s'entraîner à voir comment l'évaluation se passe en fin d'année.
  - Le RNCP liste un ensemble de **compétences**.
  - Pour chaque compétence, le jury estime si elle est **acquise**, **en cours d'acquisition** ou **non acquise** (pas de note à proprement parler).
  - Il y a beaucoup de compétences : il faut **construire le projet en gardant cette grille en tête**.
- Le document de déroulé du bloc sera **partagé** (accès à la plateforme de l'école en cours de régularisation).

---

## 4. Format du cours

- Peu de cours magistral, plutôt des **petites interventions**.
- Des **QCM non notés** seront mis à disposition sur la plateforme pour inciter à lire la documentation et repérer les points importants.
- Le temps est court et il y a beaucoup de choses à couvrir.

---

## 5. Cadre méthodologique : DataOps

### Rappel : DevOps
- Méthodologie visant à **rapprocher les développeurs et les équipes d'exploitation** (infrastructure, système, réseau) pour supprimer la fracture entre ces deux mondes.

### DataOps
- Même logique, appliquée au **monde des données**.
- Constat : en tant que développeurs, on a tendance à :
  1. Ignorer la **mise en œuvre pratique** du logiciel qu'on développe ;
  2. Négliger l'**utilisabilité des données** pour des utilisateurs non informaticiens (marketing, SAV, communication…).
- Il faut **servir les données dans de bonnes conditions** à ces utilisateurs.
- **Self-service BI** : outils comme **Kibana**, **Grafana**, **Superset** permettant aux utilisateurs finaux de faire leurs propres requêtes, analyses et graphiques, sans passer par les équipes data.

### Place de la modélisation dans DataOps
- Collecter les données depuis des sources, les rendre **interopérables**, les **normaliser** et les **nettoyer** pour les rendre accessibles.
- **Architecture Médaillon** (vue l'an dernier) : raffinage progressif des données en 3 étapes — **Bronze → Silver → Gold** — jusqu'à ce qu'elles soient suffisamment propres pour être utilisées.
- L'aspect **documentation** sera très important.

---

## 6. Modélisation orientée graphe et ontologies

- Quand on pense modélisation, on pense d'abord **SQL / tables**. L'intervenant souhaite aussi montrer une **modélisation de type graphe**.
- **Graphes de connaissances** : ensembles de **concepts métier** repérés lors de l'analyse de la problématique, reliés par des **relations sémantiques**.
  - Exemple : la relation « *être le père de* » — X est le père de Y, Y est le père de Z… Cette relation s'applique (en première approximation) à des êtres humains.
- Ce type de modélisation permet de construire des **ontologies**.
  - Historiquement liées au **web sémantique** / **web de données** (hors périmètre du cours).
  - Elles reviennent aujourd'hui dans les **bases de données graphes**.
- **Pourquoi ce retour ?** La popularité des **RAG** (Retrieval-Augmented Generation) avec les LLM :
  - L'architecture RAG classique repose sur des **bases vectorielles**.
  - De plus en plus d'articles montrent des bases vectorielles **remplacées ou augmentées par des bases graphes** (**GraphRAG**), qui apportent davantage de **concepts et de contexte**.
- **Outil** : l'éditeur d'ontologies **Protégé**, à explorer pour la prochaine fois (pistes données mercredi en fin de matinée).

---

## 7. Le projet

### Attendus
- Un **pipeline de données complet** ; **libre choix des outils** (côté de l'intervenant, à confirmer avec Marine).
- **Modéliser un entrepôt de données** (cœur du projet).
- Prévoir aussi la partie **amont** : récupération des sources, éventuellement des **connecteurs** (pas le cœur du périmètre, mais intéressant).
- Une chaîne de **raffinage** des données (Bronze / Silver / Gold).
- Une partie **tableau de bord**.

### Sujet (éléments donnés à l'oral)
- Le sujet concerne les **incendies / les pompiers**.
- Il ne s'agit pas de réactivité immédiate (temps réel), mais plutôt de **planification à moyen terme** (horizon de quelques mois). *[Échange question/réponse partiellement inaudible.]*

### Déroulé de la séance
1. **Première partie de l'après-midi** : vous recevez un **texte court** énonçant la problématique, **sans les sources**.
   - Comprendre ce que dit le texte.
   - Recenser les **questions analytiques** : toutes les questions que vous aimeriez poser, par exemple, à des pompiers.
   - **Repérer ce que vous ne savez pas** — c'est souvent ainsi que démarrent les projets.
2. **Synthèse** collective.
3. **Deuxième partie** : distribution des **sources de données**. Vous êtes aussi **libres d'utiliser d'autres sources** existantes.

### Logistique
- 10–15 minutes pour former les groupes et régler les aspects logistiques avant de commencer.

---

## À retenir / à faire

- [ ] Récupérer les notebooks et le code du projet de l'an dernier
- [ ] Se renseigner sur **DataOps** et l'**architecture Médaillon**
- [ ] Installer et explorer **Protégé** (éditeur d'ontologies)
- [ ] Former les groupes
- [ ] Lire le texte du sujet et lister les **questions analytiques**
- [ ] Garder en tête la **grille de compétences RNCP** en construisant le projet
