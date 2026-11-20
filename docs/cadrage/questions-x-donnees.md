# Tableau questions × données précises

Ce document relie chaque question de [`Analyse de la commande.md`](../../Analyse%20de%20la%20commande.md) (partie 1) aux **champs précis** des jeux décrits dans [`Fiche d'identite des donnees.md`](../../Fiche%20d'identite%20des%20donnees.md), aux **croisements ou corrélations** à faire, puis aux jeux du [défi data.gouv « Prévenir et détecter les feux de forêt »](https://defis.data.gouv.fr/defis/prevenir-et-detecter-les-feux-de-foret) qui seraient plus pertinents.

Il prépare la future base agrégée (« super BDD ») : clés de jointure, grains et sources à ajouter.

**Identifiants des questions** : C1 à C15 pour les questions communes, M1 à M4 pour Mariam, D1 et D2 pour Dris, E1 à E6 pour Esli, T1 à T6 pour Théo. La numérotation suit l'ordre de la partie 1.

**Abréviations des sources**

| Code | Jeu de données | Statut |
| ---- | -------------- | ------ |
| MDF | Météo des forêts (Météo-France) : API et archives `data/raw/archives/mdf_2024..2026.csv.gz` | Fiche |
| ISDIS | Interventions réalisées par les services d'incendie et de secours (DGSCGC, data.gouv) | Fiche |
| SNSDIS | Statistiques nationales des SDIS (rapports PDF annuels DGSCGC) | Fiche |
| AROME | Paquets AROME 0,01° (Météo-France, GRIB2) | Fiche |
| BDIFF | Base de données sur les incendies de forêt en France (IGN / ministère de l'Agriculture) | Défi |
| IFM-C | Indice Forêt Météo (FWI) maillé : Copernicus Early Warning Data Store et EFFIS | Défi |
| FIRMS | NASA FIRMS : points chauds détectés par satellite | Défi |
| ERA5 | Copernicus Climate Data Store : réanalyses météo historiques | Défi |
| OCCSOL | BD Forêt V2, Corine Land Cover, OCS-GE, Forêts publiques | Défi |
| ADMIN | Admin Express : communes, départements, codes INSEE | Défi |
| RISQ | Carroyage DFCI 2 km, obligations légales de débroussaillement (OLD), GASPAR, PPRIF | Défi |
| ACCES | BD TOPO, ROUTE 500, OpenStreetMap, points de rencontre des secours, MNS LiDAR HD | Défi |
| FREQ | Trafic moyen journalier annuel (réseau national) et liste des festivals en France | Défi |
| DOC | Stratégie nationale DFCI, PPFCI / PDPFCI | Défi |

---

## 1. Inventaire des champs disponibles (jeux de la fiche)

| Jeu | Grain | Champs utiles | Période disponible | Clé de jointure |
| --- | ----- | ------------- | ------------------ | --------------- |
| MDF | Département × jour d'émission (juin à septembre) | `date` (horodatage d'émission UTC), `num_dep`, `nom_dep` (2024, 2026) ou `dep_nom` (2025), `niveau_j1`, `niveau_j2` (1 faible, 2 modéré, 3 élevé, 4 très élevé) | 2024 à 2026 dans nos archives ; dispositif public depuis 2023 | `num_dep` + date (J1 = lendemain de l'émission) |
| ISDIS | Département × année | `Année`, `Zone`, `Région`, `Numéro`, `Département`, `Catégorie A` (catégorie du SDIS : A, B ou C), **`Feux de végétations`**, `Autres feux`, `Incendies`, `Secours à personne`, `Fausses alertes`, `Total interventions` | 2008 à 2024 (un CSV par année) | `Numéro` (code département) + `Année` |
| SNSDIS | SDIS × année (extraction depuis PDF) | Effectifs (sapeurs-pompiers professionnels, volontaires, militaires), personnels administratifs, centres d'incendie et de secours, engins, interventions, budget (dépenses de fonctionnement et d'investissement, coût par habitant) | Éditions 2014 à 2025 | Département + année |
| AROME | Maille de 0,01° (≈ 1,3 km) × heure | Température à 2 m, humidité relative, vent à 10 m (vitesse, direction, rafales), précipitations | Prévisions récentes uniquement : pas d'archive | Latitude et longitude → commune (ADMIN) + date et heure |

**Points de vigilance relevés sur les fichiers**

- Les archives MDF n'ont pas le même format selon l'année : séparateur `,` (2024, 2025) ou `;` (2026), colonne `nom_dep` ou `dep_nom`, code `1` ou `01`. À harmoniser avant toute jointure.
- La date MDF est la date d'**émission** (vers 17 h locales). Le niveau J1 vaut pour le lendemain : il faut décaler d'un jour avant de croiser avec la date d'un feu.
- ISDIS ne donne que des **comptes annuels par département**. Il n'y a ni date, ni commune, ni cause. La rubrique `Feux de végétations` ne distingue pas la forêt des autres végétations.
- AROME n'a pas d'historique : il ne permet aucune analyse rétrospective.

**Champs BDIFF relevés sur le portail** (fiche incendie) : numéro de fiche, `Année`, commune (code INSEE et nom), département, date et heure de première alerte, surface parcourue (ha) et sa répartition (forêt ; maquis et garrigues ; autres surfaces naturelles hors forêt ; surfaces agricoles ; autres surfaces), précision des surfaces, `Nature` (cause : involontaire travaux, involontaire particulier, malveillance, accidentelle, naturelle, ou non renseignée), décès ou bâtiments touchés. Couverture : France entière, 2006 à 2025, grain commune.

---

## 2. Tableau principal : une question par ligne

Couverture : **Totale** si les jeux de la fiche suffisent ; **Partielle** s'ils répondent en partie ; **Aucune** si la réponse dépend d'un entretien ou d'un document interne du SDMIS.

### 2.1. Questions communes

| ID | Question | Données disponibles (jeu → champs précis) | Croisement / corrélation à faire | Couverture | Données du défi plus pertinentes ou complémentaires | Reste à demander au SDMIS |
| -- | -------- | ----------------------------------------- | -------------------------------- | ---------- | -------------------------------------------------- | ------------------------- |
| C1 | Quel est le seuil actuel de déclenchement du dispositif renforcé ? | MDF → `niveau_j1`, `niveau_j2` du `num_dep = 69` : distribution des niveaux, mais pas le seuil. | Une fois le seuil connu : compter les jours MDF du 69 au niveau du seuil ou au-dessus, par saison. | Aucune | DOC → stratégie nationale DFCI ; PDPFCI ou arrêté préfectoral du Rhône s'il existe. | Valeur du seuil, variation par zone, historique 2020 à 2026. |
| C2 | Comment ce seuil a-t-il été fixé ? | MDF → `niveau_j1` (69) ; documentation `presentation_mdf.pdf`. | Analyse rétrospective MDF × BDIFF : nombre de feux par niveau de danger, pour juger si le seuil est cohérent. | Aucune | DOC → stratégie nationale ; BDIFF pour la vérification rétrospective. | Note de décision, retours d'expérience. |
| C3 | Quels autres critères sont pris en compte pour déclencher le dispositif renforcé ? | AROME → rafales, humidité relative, précipitations ; MDF → `niveau_j2` (persistance du danger). | Repérer les jours où le vent ou la sécheresse dépassent un seuil alors que le niveau MDF reste bas. | Partielle | IFM-C → composantes de l'IFM (sécheresse profonde, propagation) ; FREQ → festivals (affluence) ; FIRMS → feux en cours à proximité. | Liste des critères non météo (événements, disponibilité des moyens). |
| C4 | Qui prend la décision de déclencher le dispositif renforcé ? | Aucune. | Aucun. | Aucune | DOC → PDPFCI (répartition des rôles préfet et SDIS). | Organigramme et délégations de décision. |
| C5 | Quelles zones du Rhône sont les plus exposées aux départs de feu ? | ISDIS → `Feux de végétations` (69, par an) : niveau département seulement. AROME → zones météo défavorables, sans historique. | BDIFF : nombre de feux et surface parcourue par commune (code INSEE), rapportés à la surface boisée (OCCSOL) → densité de feux par km² de forêt. Agrégation possible à la maille DFCI 2 km. | Partielle | **BDIFF** (feux par commune) ; OCCSOL (surface de forêt par commune) ; FIRMS (détections ponctuelles) ; RISQ (communes à risque dans GASPAR, OLD, carroyage DFCI) ; ADMIN (référentiel des communes). | Interventions « feux de végétation » géolocalisées, plus complètes que BDIFF. |
| C6 | Quelles zones du Rhône faut-il prioriser, en tenant compte de la fréquence des incendies, des dommages et des difficultés d'intervention ? | ISDIS → `Feux de végétations` (département seulement). | Score par commune ou maille DFCI : fréquence (BDIFF, nombre de feux) + dommages (BDIFF, surface et décès ou bâtiments touchés) + enjeux (OLD, interface forêt-habitat) + difficulté d'accès (distance aux routes et aux casernes, pente). | Partielle | **BDIFF** ; RISQ (OLD, carroyage DFCI, PPRIF) ; ACCES (routes, casernes dans la BD TOPO, points de rencontre des secours, relief) ; OCCSOL. | Délais d'intervention par zone, zones difficiles connues des équipes. |
| C7 | Quel indice est utilisé pour évaluer le danger de feu ? | MDF → indice de danger intégré de Météo-France, publié en 4 niveaux (`presentation_mdf.pdf`). | Aucun. | Partielle | IFM-C → IFM brut, base de l'indice intégré. | L'indice interne du SDMIS diffère-t-il de la Météo des forêts ? |
| C8 | Comment cet indice est-il calculé ? | `presentation_mdf.pdf` : IFM + sécheresse de la végétation + surface des massifs et interfaces forêt-habitat + zones sensibles (climatologie sur 30 ans). Formule non publiée. AROME → variables d'entrée. | Recalculer l'IFM à partir d'AROME ou d'ERA5, puis comparer aux niveaux MDF du 69. | Partielle | IFM-C (système canadien, formules publiques, composantes détaillées) ; ERA5 (variables historiques). | Règles de passage de l'IFM aux 4 niveaux. |
| C9 | Que représentent les différents niveaux de cet indice ? | MDF → `niveau_j1`, `niveau_j2` : 1 faible (vert), 2 modéré (jaune), 3 élevé (orange), 4 très élevé (rouge). | Aucun. | Totale | IFM-C (classes de danger EFFIS) pour comparaison. | Correspondance entre niveaux et actions du SDMIS. |
| C10 | Quelles variables entrent dans la composition de cet indice ? | AROME → température, humidité relative, vent, précipitations (variables de l'IFM). La sécheresse de la végétation (relevés ONF) n'est pas disponible. | Corrélation entre chaque variable AROME (agrégée au 69) et le niveau MDF du jour. | Partielle | IFM-C (composantes) ; ERA5 (mêmes variables en historique) ; OCCSOL (massifs forestiers) ; RISQ / OLD (proxy des interfaces forêt-habitat). | Variables propres au SDMIS, s'il y en a. |
| C11 | Quelles actions sont déclenchées lors d'un renforcement (patrouilles, guet, prépositionnement, etc.) ? | Aucune. | Aucun. | Aucune | DOC (PDPFCI : mesures types) ; RISQ (carroyage DFCI : zones de patrouille) ; ACCES (points de rencontre des secours). | Actions prévues et réalisées par dispositif. |
| C12 | Quels moyens humains et matériels sont disponibles ? | SNSDIS → effectifs (professionnels, volontaires), centres, engins du SDMIS 69 (annuel). | Charge : ISDIS `Feux de végétations` ÷ effectifs SNSDIS, par année. | Partielle | ACCES → localisation des casernes (BD TOPO). | Disponibilités par centre et par jour en saison. |
| C13 | Quels moyens financiers sont disponibles ? | SNSDIS → budget du SDIS 69 (fonctionnement, investissement, coût par habitant). | Aucun. | Partielle | Aucune. | Crédits 2025 et 2026 affectables au dispositif. |
| C14 | Disposez-vous d'historiques localisés des départs de feu, des interventions et des niveaux de l'indice ? | MDF 2024 à 2026 (département) ; ISDIS 2008 à 2024 (département × année). Aucun n'est localisé finement. | Inventaire des sources : ce tableau. | Partielle | **BDIFF** (2006 à 2025, commune) ; FIRMS (point GPS) ; IFM-C (historique maillé). | Historique des interventions géolocalisées. |
| C15 | Peut-on suivre l'évolution des départs de feu, des interventions et des niveaux de l'indice au fil des saisons ? | MDF → série quotidienne du 69, juin à septembre 2024 à 2026. ISDIS → série annuelle `Feux de végétations` et `Incendies`, 2008 à 2024. | Par saison : nombre de jours au niveau 3 ou plus (MDF) face au nombre de feux de végétation (ISDIS) puis de feux BDIFF. | Partielle | **BDIFF** (série quotidienne) ; IFM-C (niveaux avant 2024). | Changements de méthode de collecte. |

### 2.2. Questions individuelles — Mariam

| ID | Question | Données disponibles (jeu → champs précis) | Croisement / corrélation à faire | Couverture | Données du défi plus pertinentes ou complémentaires | Reste à demander au SDMIS |
| -- | -------- | ----------------------------------------- | -------------------------------- | ---------- | -------------------------------------------------- | ------------------------- |
| M1 | Quelles sont les principales causes des départs de feu dans le Rhône (origine humaine, foudre, etc.) ? | Aucune : ISDIS ne donne pas la cause. | Répartition des feux BDIFF du 69 par `Nature`, comparée à la région et à la France. | Aucune | **BDIFF** → `Nature`. Attention : beaucoup de causes ne sont pas renseignées. | Causes établies par les enquêtes. |
| M2 | Dans quelle mesure les causes des départs de feu échappent-elles à l'indice de danger ? | MDF → `niveau_j1` du 69. | BDIFF (`Nature`, date d'alerte) × MDF (niveau du jour) : part des feux de chaque cause survenus par danger faible. Les feux BDIFF hors période MDF (octobre à mai) échappent aussi à l'indice. | Partielle | **BDIFF** ; IFM-C (danger hors saison). | Aucun. |
| M3 | Quel est le taux de faux positifs de l'indicateur, et combien de journées à danger élevé n'ont pas connu de départ de feu ? | MDF → `niveau_j1` du 69 (décalé au lendemain). | Jointure par jour MDF × BDIFF (dép. 69, date d'alerte). Taux = jours au niveau du seuil ou au-dessus sans feu ÷ jours au niveau du seuil ou au-dessus. Seuil testé : 3 tant que le seuil SDMIS est inconnu. | Partielle | **BDIFF** ; IFM-C pour étendre la période avant 2024. | Seuil officiel et définition retenue du taux. |
| M4 | Quel est le taux de faux négatifs de l'indicateur, et combien de départs de feu ont eu lieu lors de journées à danger faible ? | MDF → `niveau_j1` du 69. | Même jointure. Taux = jours avec au moins un feu et niveau sous le seuil ÷ jours avec au moins un feu. Compter aussi le nombre de feux, distinct du nombre de jours. | Partielle | **BDIFF** ; IFM-C. | Aucun. |

### 2.3. Questions individuelles — Dris

| ID | Question | Données disponibles (jeu → champs précis) | Croisement / corrélation à faire | Couverture | Données du défi plus pertinentes ou complémentaires | Reste à demander au SDMIS |
| -- | -------- | ----------------------------------------- | -------------------------------- | ---------- | -------------------------------------------------- | ------------------------- |
| D1 | Existe-t-il un référentiel ou un *thésaurus* décrivant les variables, les catégories et les niveaux utilisés pour construire l'indice ? | `presentation_mdf.pdf` (niveaux, couleurs, composantes) ; pas de thésaurus officiel. | Construire notre propre référentiel dans le glossaire. | Partielle | IFM-C (documentation EFFIS du système canadien de l'IFM). | Référentiel interne, s'il existe. |
| D2 | Pour les zones du Rhône les plus exposées, peut-on consulter conjointement l'historique des niveaux de danger et celui des départs de feu ? | MDF → niveau du 69 (un seul niveau pour tout le département). | BDIFF (commune, date) × MDF (69, date) : pour chaque commune exposée, liste des feux avec le niveau du jour. Mieux : IFM-C maillé ↔ maille DFCI ↔ communes BDIFF, ce qui donne un niveau propre à chaque zone. | Partielle | **BDIFF** ; IFM-C ; RISQ (carroyage DFCI). | Zonage utilisé par le SDMIS. |

### 2.4. Questions individuelles — Esli

| ID | Question | Données disponibles (jeu → champs précis) | Croisement / corrélation à faire | Couverture | Données du défi plus pertinentes ou complémentaires | Reste à demander au SDMIS |
| -- | -------- | ----------------------------------------- | -------------------------------- | ---------- | -------------------------------------------------- | ------------------------- |
| E1 | Comment l'indicateur se comporte-t-il dans les autres départements d'Auvergne-Rhône-Alpes et à l'échelle nationale, en comparant des territoires aux caractéristiques similaires ? | MDF → 96 départements ; ISDIS → `Feux de végétations` et `Région` pour tous les départements ; SNSDIS et ISDIS → catégorie du SDIS (A, B, C). | Par département : nombre de jours au niveau 3 ou plus face au nombre de feux. Regrouper les départements comparables (catégorie SDIS, taux de boisement, relief). AURA : 01, 03, 07, 15, 26, 38, 42, 43, 63, 69, 73, 74. | Partielle | **BDIFF** national ; OCCSOL (taux de boisement) ; ACCES (relief, MNS) ; ADMIN (population) ; données changement climatique (climat). | Aucun. |
| E2 | Comment les niveaux de danger ont-ils évolué au fil des saisons (séries temporelles) ? | MDF → `niveau_j1` du 69, 2024 à 2026 (3 saisons). | Par saison : nombre de jours par niveau, date du premier jour au niveau 3, durée de la saison à risque. | Partielle | IFM-C (série longue, avant 2023) ; archives Météo des forêts 2023. | Aucun. |
| E3 | Comment les départs de feu ont-ils évolué au fil des saisons (séries temporelles) ? | ISDIS → `Feux de végétations` du 69, 2008 à 2024 (annuel, toute végétation). | Série annuelle ISDIS comparée à la série quotidienne BDIFF agrégée par mois ou par saison. | Partielle | **BDIFF** (série quotidienne 2006 à 2025) ; FIRMS. | Aucun. |
| E4 | Comment les moyens mobilisés ont-ils évolué au fil des saisons (séries temporelles) ? | SNSDIS → effectifs, engins, interventions du SDIS 69 (annuel, 2014 à 2025) ; ISDIS → `Incendies`, `Total interventions`. | Évolution annuelle des effectifs face au volume d'interventions incendie. Attention : ce sont des moyens disponibles, pas des moyens mobilisés. | Partielle | Aucune. | Registre des moyens mobilisés par jour et par dispositif. |
| E5 | Quel budget peut être consacré au dispositif renforcé ? | SNSDIS → budget global du SDIS 69. | Aucun. | Partielle | Aucune. | Budget 2026 et 2027 affecté au dispositif. |
| E6 | Quel est le coût estimé de chaque ressource ou action mobilisée ? | SNSDIS → dépenses, effectifs, engins ; ISDIS → `Total interventions`. | Estimations : coût moyen par sapeur-pompier = dépenses de personnel ÷ effectifs ; coût moyen par intervention = dépenses ÷ `Total interventions`. | Partielle | Aucune. | Coûts unitaires réels (patrouille, guet, engin par jour). |

### 2.5. Questions individuelles — Théo

| ID | Question | Données disponibles (jeu → champs précis) | Croisement / corrélation à faire | Couverture | Données du défi plus pertinentes ou complémentaires | Reste à demander au SDMIS |
| -- | -------- | ----------------------------------------- | -------------------------------- | ---------- | -------------------------------------------------- | ------------------------- |
| T1 | Combien de temps le dispositif renforcé peut-il rester déployé ? | MDF → `niveau_j1` du 69. | Durée des épisodes de jours consécutifs au niveau du seuil ou au-dessus : durée pendant laquelle le dispositif aurait dû tenir. | Partielle | IFM-C (épisodes plus anciens). | Durées maximales et roulements prévus. |
| T2 | Quelles contraintes limitent la durée du déploiement du dispositif renforcé ? | SNSDIS → part des volontaires dans les effectifs ; ISDIS → `Secours à personne`, `Total interventions` (concurrence des autres missions). | Charge estivale hors feux face aux effectifs disponibles. | Partielle | Aucune. | Contraintes réelles : repos, disponibilité des volontaires, budget. |
| T3 | Le besoin porte-t-il uniquement sur la prévention et l'anticipation des départs de feu, ou également sur la gestion opérationnelle d'un incendie en cours ? | Aucune. | Aucun. | Aucune | Aucune. | Question de cadrage pour l'entretien. |
| T4 | Comment anticipez-vous aujourd'hui l'évolution d'un incendie une fois qu'il s'est déclaré ? | AROME → vent horaire (direction, rafales), humidité relative, maille de 1,3 km : moteurs de la propagation. | Associer la position d'un feu aux prévisions de vent AROME et au combustible environnant. | Partielle | IFM-C (indice de propagation) ; EFFIS (cartes de combustibles) ; OCCSOL (essences de la BD Forêt) ; ACCES (relief, pente) ; FIRMS (détections successives d'un même feu). | Procédures et outils actuels de prévision de la propagation. |
| T5 | Comment prenez-vous en compte les départs de feu d'origine humaine ? | Aucune. | Part des feux d'origine humaine dans BDIFF (`Nature`) et proximité de ces feux avec le bâti. | Aucune | **BDIFF** ; RISQ (OLD) ; OCCSOL (OCS-GE : bâti et interfaces). | Mesures actuelles (prévention, information). |
| T6 | Comment anticipez-vous les départs de feu d'origine humaine ? | Aucune. | Feux d'origine humaine (BDIFF) × jour de la semaine et heure d'alerte × événements (festivals) × trafic routier proche × proximité du bâti. | Aucune | **BDIFF** ; FREQ (festivals, trafic) ; ACCES (routes) ; hors défi : calendrier scolaire et jours fériés (data.gouv). | Règles d'anticipation actuelles. |

---

## 3. Croisements clés pour la future base agrégée

| Croisement | Clé de jointure | Grain obtenu | Questions servies | Point de vigilance |
| ---------- | --------------- | ------------ | ----------------- | ------------------ |
| MDF × BDIFF | Département + date (J1 décalé d'un jour) | Département × jour | C2, C15, M2, M3, M4, D2, T1 | MDF ne couvre que juin à septembre ; un seul niveau pour tout le département. |
| BDIFF × ADMIN | Code INSEE de la commune | Commune | C5, C6, D2, E1 | Fusions de communes : utiliser le millésime ADMIN correspondant. |
| BDIFF × OCCSOL | Commune ou maille DFCI (jointure spatiale) | Commune ou maille 2 km | C5, C6, E1, T5 | Millésimes différents de l'occupation du sol. |
| IFM-C / AROME / ERA5 × ADMIN ou RISQ | Latitude et longitude → commune ou maille DFCI | Maille × jour | C8, C10, D2, E2, T4 | Résolutions différentes (1,3 km pour AROME, environ 8 à 25 km pour IFM-C et ERA5). |
| ISDIS × SNSDIS | Code département + année | Département × année | C12, E4, E6, T2 | Grain annuel ; SNSDIS est en PDF, donc extraction manuelle ou semi-automatique. |
| ISDIS × BDIFF | Code département + année | Département × année | C15, E3 | « Feux de végétations » (ISDIS) n'équivaut pas à « feux de forêt » (BDIFF). Comparer les tendances, pas les volumes. |

**Dimensions communes à prévoir** : temps (jour, saison, année), géographie (commune → maille DFCI → département → région), niveau de danger (1 à 4), cause (référentiel BDIFF).

---

## 4. Matrice sources × questions (contrôle de minimisation)

Chaque source doit servir au moins une question ; chaque question doit avoir au moins une source ou un entretien.

| Source | Questions couvertes | Verdict |
| ------ | ------------------- | ------- |
| MDF | C1, C2, C3, C7, C8, C9, C10, C15, M2, M3, M4, D1, D2, E1, E2, T1 | À garder (indice cible). |
| ISDIS | C5, C6, C12, C14, C15, E1, E3, E4, E6, T2 | À garder (seule série longue des interventions). |
| SNSDIS | C12, C13, E1, E4, E5, E6, T2 | À garder (seule source sur les moyens). |
| AROME | C3, C5, C8, C10, T4 | À garder, mais seulement pour le temps réel ; pas d'historique. |
| BDIFF | C2, C5, C6, C14, C15, M1, M2, M3, M4, D2, E1, E3, T5, T6 | **À ajouter en priorité.** |
| IFM-C | C3, C7, C8, C9, C10, C14, C15, M2, M3, M4, D1, D2, E2, T1, T4 | À ajouter. |
| OCCSOL | C5, C6, C10, E1, T4, T5 | À ajouter (BD Forêt V2 ou OCS-GE en priorité). |
| ADMIN | C5, E1 et toutes les jointures communales | À ajouter (référentiel). |
| RISQ | C5, C6, C10, C11, D2, T5 | À ajouter (carroyage DFCI comme zonage commun). |
| ACCES | C6, C11, C12, E1, T4, T6 | À ajouter, en ne gardant que les couches utiles (routes, casernes, relief). |
| ERA5 | C8, C10 | Optionnel : seulement si l'on recalcule l'IFM. |
| FIRMS | C3, C5, C14, E3, T4 | Optionnel : complète BDIFF pour la localisation. |
| FREQ | C3, T6 | Optionnel. |
| DOC | C1, C2, C4, C11 | Documentaire (pas d'intégration dans la base). |
| Entretien SDMIS | C1 à C4, C11 à C13, E4 à E6, T1 à T4 | Indispensable pour les questions de gouvernance. |

**Sources du défi écartées** : ARPEGE (moins précis qu'AROME), Pyronear (images de détection, hors périmètre des questions), Sentinel-1, BD ORTHO, EuroGlobalMap, Geofla (remplacé par Admin Express), parcelles agricoles, réserves biologiques, artificialisation des sols, données naturalistes de l'ONF. Aucune question ne les nécessite.

---

## 5. Synthèse : sources du défi à ajouter en priorité

| Priorité | Source | Ce qu'elle débloque |
| -------- | ------ | ------------------- |
| 1 | BDIFF | Départs de feu datés et localisés à la commune, avec cause et surface. Rend possibles le calcul des faux positifs et faux négatifs (M3, M4), la cartographie des zones exposées (C5, C6), l'analyse des causes (M1, M2, T5, T6) et les séries temporelles (C15, E3). |
| 2 | IFM-C (Copernicus EWDS / EFFIS) | Historique du danger avant 2024 et à une maille plus fine que le département (D2, E2, C8, C10). |
| 3 | OCCSOL (BD Forêt V2, OCS-GE) | Surface boisée et interfaces forêt-habitat, pour normaliser l'exposition (C5, C6, E1). |
| 4 | ADMIN | Référentiel des communes et clé de toutes les jointures. |
| 5 | RISQ (carroyage DFCI, OLD, GASPAR) | Zonage commun aux feux et au danger ; enjeux humains (C6, D2, T5). |
| 6 | ACCES (BD TOPO, points de rencontre) | Difficulté d'intervention (C6) et facteurs de propagation (T4). |
| 7 | ERA5, FIRMS, FREQ | Compléments optionnels selon les analyses retenues. |

**Questions sans donnée ouverte possible** : C1, C2, C4, C11, T3. La réponse viendra de l'entretien avec le SDMIS. Pour C13 et E5, le SNSDIS ne donne que le budget global : le montant affecté au dispositif reste à demander.
