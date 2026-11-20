# Revue critique : « Indicateurs x donnees SDIS33.md »

Revue du 20/11/2026, selon trois axes : **faisabilité** (téléchargement, volume, effort, passage au grain carreau DFCI × jour), **fiabilité** (qualité, millésime, licence, noms de champs) et **pertinence** (utilité pour le seuil de déclenchement 2027 et la limitation des fausses alertes).

**Légende de l'état de vérification** : ✅ vérifié en direct pendant cette revue ; ☑️ vérifié lors de la session précédente ; ❓ toujours non vérifié ; ❌ faux ou à corriger.

---

## 0. Synthèse

Le document est solide sur la structure (catalogue, couverture, table de liaison, demandes au SDIS). Quatre constats changent toutefois la méthode et doivent être intégrés avant de construire la base.

| # | Constat | Gravité | Conséquence |
| - | ------- | ------- | ----------- |
| 1 | En Gironde, la Météo des forêts n'a **jamais atteint le niveau 4** sur 2024 à 2026, et le niveau 3 seulement 19 jours sur 371. ✅ | Bloquant | Le seuil « 4 » ne déclenche jamais, et le niveau MDF seul n'offre que 2 seuils utiles (≥ 2, ≥ 3). Le seuil doit porter sur un **indice continu**, pas sur le niveau MDF. |
| 2 | Le jeu codé **CLIM** n'est pas un jeu de projections : le lien pointe vers **« Données changement climatique – SIM quotidienne »** (réanalyse Safran-Isba, maille 8 km, quotidienne, 1958 à aujourd'hui, Licence Ouverte). ✅ | Bloquant (erreur) | Il a été écarté à tort. C'est la meilleure source du défi pour allonger l'historique météo à une maille 8 km, bien plus fine qu'EWDS (≈ 25 à 31 km). |
| 3 | La BDIFF publique ne localise les feux qu'à la **commune** : la fiche publique ne montre ni carreau DFCI, ni coordonnées, ni origine de l'alerte. ✅ | Majeur | La répartition au prorata de la forêt crée des « fractions de feu » par carreau : on ne peut pas compter des fausses alertes sur des fractions. Il faut **évaluer le seuil à la commune × jour** (ou au secteur), et garder le carreau pour les facteurs. |
| 4 | Plusieurs couches « état actuel » (BD TOPO, OSM, OLD, BD Forêt) sont appliquées à 20 ans de feux, alors que les incendies de 2022 ont fortement modifié le combustible en Gironde. | Majeur | Risque d'anachronisme et de fuite d'information : il faut dater chaque couche et masquer les surfaces brûlées (EFFIS). |

**Autres corrections à faire** : écarter **Blitzortung** (conditions d'usage incompatibles) ; fusionner **OLD** avec P4.1 (même géométrie : massifs + tampon de 200 m) ; retirer **GASPAR** (redondant) ; corriger la période MDF 2026 ; préciser que l'IFM français n'est publié nulle part tel quel ; reclasser **P2.6** en Proxy.

**Verdict sur la partie 2 (efficience)** : traitable avec des données publiques **seulement si le coût devient un paramètre de scénario** (coût d'une journée de déclenchement, saisi comme hypothèse et testé en sensibilité), et non une donnée mesurée. La problématique se reformule alors ainsi : « quel seuil minimise les fausses alertes sous une contrainte de détection des feux, pour un coût journalier donné ? ».

---

## 1. Constats structurants

### 1.1. Météo des forêts : trop peu de niveaux observés pour caler un seuil

Comptage sur les archives locales `data/raw/archives/mdf_2024..2026.csv.gz` (niveau J1, jours d'émission) :

| Saison | Dép. | Niveau 1 | Niveau 2 | Niveau 3 | Niveau 4 | Jours |
| ------ | ---- | -------- | -------- | -------- | -------- | ----- |
| 2024 | 33 | 106 | 13 | 1 | 0 | 120 |
| 2025 | 33 | 79 | 37 | 4 | 0 | 120 |
| 2026 | 33 | 56 | 61 | 14 | 0 | 131 |
| 2024 à 2026 | 40 | 292 | 73 | 6 | 0 | 371 |
| 2024 à 2026 | 47 | 260 | 93 | 18 | 0 | 371 |

Niveau 4, toute la France : 1 jour-département en 2024, 29 en 2025, 99 en 2026.

**Conséquences**
- Le seuil « 3 puis 4 » de P1.3 est à remplacer par « 2 puis 3 » ; le seuil 4 ne peut pas être testé sur l'historique girondin.
- Avec 3 valeurs possibles et un seul niveau par département et par jour, le niveau MDF **ne distingue aucune zone** et donne au mieux 2 seuils. La finesse doit venir d'un **indice continu** : IFM (ou FWI) calculé à 8 km à partir de SIM2, combiné aux facteurs de zone.
- La correspondance « IFM → niveau MDF » (prévue en 2.6.4) ne peut pas être calée sur la Gironde seule (19 jours au niveau 3, aucun au niveau 4). Il faut la caler **sur toute la France** : 96 départements × 3 saisons, soit environ 35 000 jours-départements, dont 129 au niveau 4.
- La période 2026 couvre en réalité du **28 mai au 5 octobre** (131 jours), et non « juin à septembre ». ❌ à corriger dans le catalogue.
- L'échéance est confirmée par `presentation_mdf.pdf` : la carte est émise à 17 h, J1 = lendemain et J2 = surlendemain. Les horodatages (`14:50Z`, `16:00Z` en 2024) sont cohérents avec ce rythme. ✅
- **Double comptage** : selon la même présentation, le niveau MDF tient déjà compte, **à l'échelle du département**, de la surface des massifs, des interfaces forêt-habitat et de la climatologie des « zones sensibles ». P4.1 reste utile **à l'intérieur** du département, mais il ne faut pas l'utiliser pour comparer des départements entre eux.
- La MDF repose sur un « indice de danger intégré » et sur une expertise humaine (relevés de sécheresse de l'ONF) : ce n'est **pas** une fonction de l'IFM seul. Il faut l'écrire dans la limite de P3.1.

### 1.2. CLIM = SIM2 quotidienne : à réintégrer en source principale de la météo historique

Métadonnées data.gouv du jeu `6569b27598256cc583c917a7` ✅ :
- **titre** : « Données changement climatique – SIM quotidienne » ;
- **modèle** : Safran-Isba, maille de 0,072° (environ 8 km, 8 981 mailles fixes en métropole) ;
- **période** : 1958 à aujourd'hui (fichiers `QUOT_SIM2_<année>` et `QUOT_SIM2_latest`) ;
- **format** : CSV compressé, de 85 à 492 Mo par fichier ;
- **mise à jour** : quotidienne sur 60 jours glissants ;
- **licence** : Licence Ouverte 2.0.

| Axe | Avis |
| --- | ---- |
| Faisabilité | Bonne. Pour 20 saisons, environ 20 fichiers à filtrer sur les mailles de la Gironde, des Landes et du Lot-et-Garonne (quelques centaines de mailles). Champs attendus : précipitations, température, humidité, vent, indice d'humidité des sols `SWI_Q`. Les noms exacts sont à confirmer sur l'en-tête au téléchargement ❓. |
| Fiabilité | Réanalyse de référence de Météo-France, celle qui alimente leurs propres indicateurs de sécheresse. Limite : SIM fournit des valeurs **journalières**, alors que l'IFM utilise la température, l'humidité et le vent de **midi** ; le calcul de l'IFM à partir de SIM2 est donc une approximation à documenter. |
| Pertinence | Très forte : historique long, maille 8 fois plus fine qu'EWDS, même chaîne de données que la MDF, et `SWI` comme indicateur de sécheresse des sols. |

**Recommandation** : SIM2 devient la source principale de P3.1 pour la période antérieure à 2024 ; EWDS reste un contrôle (FWI prêt à l'emploi). Requalifier CLIM ainsi : « SIM2, défi = oui ». Les vraies projections (DRIAS) restent hors sujet.

### 1.3. Localisation des feux et calcul des fausses alertes

| Point | Constat | Recommandation |
| ----- | ------- | -------------- |
| Champs publics de la BDIFF | La fiche publique ✅ contient : commune (INSEE et nom), date et heure de première alerte, surface parcourue et sa répartition (forêt ; maquis et garrigues ; autres surfaces naturelles ; agricoles ; autres), précision des surfaces, Nature, décès ou bâtiments touchés. **Aucun** carreau DFCI, aucune coordonnée, aucune origine de l'alerte. | Le contenu exact de l'export CSV (`/incendies/zip`) reste à confirmer au premier téléchargement ❓, notamment l'unité des surfaces (ha ou m²). |
| Degré de certitude de la cause | Un support de formation BDIFF (ENASIS, 2025) décrit un **degré de connaissance de la Nature** (Inconnu, Probable, Certaine), un champ « Source de l'enquête » et un indicateur d'intervention de la cellule RCCI. Ces champs ne figurent pas sur la fiche publique. | P1.2 : vérifier si l'export les contient. Sinon, les demander : ils correspondent exactement à la donnée idéale. |
| Répartition commune → carreau | Elle produit des valeurs fractionnaires (0,3 feu dans un carreau). Or une fausse alerte se compte comme un événement binaire (zone déclenchée, aucun départ). | **Deux grains** : les facteurs au carreau (dimension `carreau`), **l'évaluation du seuil à la commune × jour** (agrégation des carreaux par commune, pondérée par la forêt). Garder la répartition au prorata seulement comme carte de densité. |
| FIRMS pour placer exactement les feux | VIIRS ne passe que deux fois par jour (vers 1 h 30 et 13 h 30) : il manque les feux brefs et petits, c'est-à-dire la grande majorité des feux girondins éteints sous 1 ha. On y trouve aussi de fausses détections (sites industriels, brûlages agricoles), et l'appariement avec la BDIFF est lui-même incertain. | Utiliser FIRMS seulement pour les grands feux, avec une règle d'appariement explicite (distance ≤ commune + 2 km, |Δt| ≤ 24 h). Ne pas le présenter comme une « localisation exacte ». |
| Communes fusionnées | BDIFF utilise le code INSEE en vigueur l'année du feu ; plusieurs communes nouvelles ont été créées depuis 2016 en Gironde. | Ajouter la **table de passage annuelle du COG INSEE** (HD) plutôt que GEOFLA. |

**Demande prioritaire au SDIS 33** : l'extraction des interventions « feux de forêt » géolocalisées (le carroyage DFCI est le référentiel opérationnel en Aquitaine). C'est la donnée qui débloque l'évaluation au grain carreau.

### 1.4. Volume et faisabilité du grain carreau × jour

| Élément | Estimation |
| ------- | ---------- |
| Carreaux de 2 km | 33 : ≈ 2 700 ; 40 : ≈ 2 300 ; 47 : ≈ 1 350 ; total ≈ 6 300 (plus les carreaux de bordure) |
| Jours par saison | ≈ 122 (juin à septembre) |
| Lignes, 20 saisons | ≈ 15 millions |
| Lignes, 3 saisons MDF | ≈ 2,3 millions |

C'est faisable en Parquet ou DuckDB, à condition de **ne pas répéter les variables statiques chaque jour** : schéma en étoile avec une table de faits `carreau_jour` limitée aux variables dynamiques (météo, MDF, déclenchement, feux) et des dimensions `carreau`, `commune`, `departement` et `jour`. La cible est très déséquilibrée (presque toutes les lignes sans feu) : prévoir des métriques adaptées (rappel, précision, taux de fausses alertes par saison) plutôt que l'exactitude.

### 1.5. Anachronismes et fuites d'information

| Couche | Problème | Correction |
| ------ | -------- | ---------- |
| BD Forêt V2 (2007 à 2018 selon le département) | Antérieure aux grands feux de 2022 en Gironde (Landiras, La Teste-de-Buch) : le combustible a disparu ou changé sur des dizaines de milliers d'hectares. | Masquer les surfaces brûlées EFFIS après leur date ; ajouter une variable `annees_depuis_dernier_feu`. |
| BD TOPO, OSM, OLD (état 2026) | Appliqués à des feux de 2006. | Documenter le millésime de chaque couche. Pour l'évolution du bâti, utiliser les deux millésimes OCS GE et ARTIF. |
| Antécédents de malveillance (P4.9) | Si l'on compte les feux de l'année évaluée, la variable « voit » la cible. | Fenêtres **strictement antérieures** à la saison évaluée (n − 1 à n − 5, etc.). |
| Population FILO (2015, 2017, 2019) | Millésimes fixes. | Prendre le millésime le plus proche de la saison. |

---

## 2. Revue du catalogue, source par source

Colonnes : F = faisabilité, R = fiabilité, P = pertinence (de ++ à −).

| Code | F | R | P | Vérif. | Avis et corrections |
| ---- | -- | -- | -- | ------ | ------------------- |
| BDIFF | ++ | + | ++ | ✅ fiche, ❓ export | Source cible indispensable. Localisation à la commune seulement (voir 1.3). Vérifier dans l'export : degré de connaissance de la Nature, unité des surfaces, part de « Nature » non renseignée en Gironde. |
| ISDIS | ++ | + | − | ☑️ | Grain département × année : sans usage pour un seuil quotidien. À rétrograder en « optionnel ». |
| FIRMS | + | + | + | — | Utile pour les grands feux et pour contrôler la BDIFF ; pas pour localiser les petits feux (voir 1.3). |
| EFFIS | + | ++ | + | — | Surtout utile pour **masquer le combustible brûlé** (surfaces brûlées datées). La carte européenne des combustibles est trop grossière face à la BD Forêt. |
| EWDS | ++ | ++ | + | ✅ | Jeu « cems-fire-historical-v1 », 1940 à aujourd'hui, quotidien, grille interpolée à 0,25° (grille native N320 ≈ 31 km), licence CC-BY. Indices canadiens (FWI, FFMC, DMC, DC, ISI, BUI) plus des indices américains et australiens ; **aucun IFM Météo-France**. Les noms `fwi`, `ffmc`… sont des libellés, pas les noms courts NetCDF (❓). Rôle : contrôle, derrière SIM2. |
| MDF | ++ | ++ | ++ | ✅ | Voir 1.1 : période 2026 à corriger ; 3 saisons seulement ; jamais de niveau 4 en Gironde. |
| AROME, ARPEGE | − | ++ | − | — | D'accord pour les écarter de la base historique. |
| ERA5 | + | − | − | ✅ partiel | Le paramètre de densité de foudre (`litoti` et ses moyennes horaires) existe dans l'IFS **depuis le cycle 45r1** ; ERA5 tourne sur un cycle antérieur (41r2). Sa présence dans le catalogue ERA5 du CDS reste ❓, et c'est de toute façon une **paramétrisation** (CAPE, hydrométéores), pas une observation. À écarter, sauf confirmation dans le CDS. |
| CLIM | ++ | ++ | ++ | ✅ | ❌ Mal identifié : c'est SIM2 quotidienne (voir 1.2). À passer en **source principale**. |
| SNSDIS | + | + | − | — | Le lien pointe vers un site tiers (ressourcesdupompier.com) : préférer la publication officielle de la DGSCGC (ministère de l'Intérieur). Grain annuel. |
| PYRO | + | + | − | — | D'accord : seulement illustratif. |
| DOC | − | ++ | ++ | — | Saisie manuelle. Indispensable pour P1.3 et P2.4 (règles du règlement interdépartemental et du PDPFCI). |
| BDTOPO | + | ++ | ++ | ❓ | Noms à confirmer sur le descriptif de contenu v3.4 (lien IGN redirigé vers cartes.gouv.fr) : `ZONE_D_ACTIVITE_OU_D_INTERET.nature = "Caserne de pompiers"`, `TRONCON_DE_ROUTE.vitesse_moyenne_vl`, `acces_vehicule_leger`, `LIGNE_ELECTRIQUE.voltage`, `RESERVOIR`. Ces champs existent bien dans la BD TOPO v3 à notre connaissance, mais ils n'ont pas été relus à la source. |
| BDORTHO | − | ++ | − | — | D'accord pour l'écarter. |
| LIDAR | −− | ++ | + | — | Un MNS à 50 cm sur environ 25 000 km² représente une centaine de milliards de pixels. Ne garder la hauteur de végétation que sous forme agrégée (produit de hauteur de canopée déjà calculé, ou rééchantillonnage à 25 m) ; sinon, l'écarter. |
| FORPUB | ++ | ++ | − | — | Faible apport pour le seuil. Optionnel. |
| BDFORET | ++ | + | ++ | ✅ partiel | V2 élaborée de 2007 à 2018, nomenclature de 32 postes, Licence Ouverte. Millésime de la Gironde ❓ (carte des millésimes sur data.gouv) ; noms `CODE_TFV`, `TFV`, `TFV_G11`, `ESSENCE` ❓ (descriptif IGN déplacé). Antérieure aux feux de 2022 (voir 1.5). |
| CLC | ++ | − | − | — | Doublon grossier (25 ha) d'OCS GE et de la BD Forêt. À écarter. |
| RPG | ++ | ++ | + | ✅ | ✅ `CODE_CULTU` (3 caractères) et `CODE_GROUP` (2 caractères) confirmés sur le RPG 2022 ; `ID_PARCEL`, `SURF_PARC`, `CULTURE_D1`, `CULTURE_D2` aussi. Licence Ouverte. Attention : avant 2015, il s'agit d'îlots et non de parcelles. |
| RESBIO, ONFNAT, EGM, BDORTHO | — | — | − | — | D'accord pour les écarter. |
| ARTIF | ++ | + | + | ☑️ | Utile pour la tendance de l'interface forêt-habitat. |
| OCSGE | + | ++ | + | ❓ | Millésimes de la Gironde à confirmer. |
| DFCI | ++ | ++ | ++ | ☑️ | Référentiel de zone. Vérifier que l'emprise du fichier national couvre bien les trois départements. |
| PRS | ++ | + | − | ☑️ | Peu utile pour le seuil. |
| ADMIN, GEOFLA | ++ | ++ | ++ | — | Remplacer GEOFLA par la **table de passage du COG INSEE** pour les communes fusionnées. |
| OSM | + | − | + | — | Complétude variable, et pas d'historique sans outil dédié. Correct pour les parkings, sentiers et points d'eau. |
| S1 | −− | + | − | — | D'accord : trop lourd. |
| TMJA | ++ | ++ | − | ☑️ | En Gironde, le réseau national est surtout autoroutier (axes clôturés). Il ne dit presque rien des routes départementales forestières. Chercher les comptages du Département de la Gironde (HD, ❓). |
| R500 | ++ | + | − | — | Doublon simplifié de la BD TOPO : à écarter. |
| OLD | ++ | + | − | ✅ | Le jeu national est « Débroussaillement » (IGN, data.gouv, mis à jour le 08/04/2026, 45 départements). C'est un **zonage informatif** : massifs concernés + tampon de 200 m, soit presque la même géométrie que P4.1. À **fusionner avec P4.1**. Le producteur cité (Géorisques) est à corriger. |
| GASPAR | ++ | + | −− | ✅ partiel | Fichier `gaspar.zip`, Licence Ouverte. Noms de colonnes ❓ (documentation indisponible). Grain communal et binaire : redondant avec OLD et la BD Forêt. À **retirer**. |
| FEST | ++ | − | − | ☑️ | Référence 2019, sans dates exactes. À écarter, ou garder seulement pour mémoire. |
| BDALTI (HD) | ++ | ++ | − | — | Gironde globalement plane (plateau landais), sauf les dunes littorales et l'Entre-deux-Mers : le relief pèsera peu. Le garder, car il coûte peu. |
| FILO, TOUR, RP (HD) | ++ | + | + | ❓ liens | FILO : carreaux de moins de 11 ménages regroupés (secret statistique). Vérifier s'il existe un millésime plus récent que 2019. |
| BALANCES, SPV, CARBU (HD) | + | + | − | ☑️ partiel | Servent seulement à poser des hypothèses de coût (voir partie 2). |
| SUFOSAT (HD) | − | + | − | ✅ partiel | Existe : suivi des coupes rases à l'échelle de la France, plus d'une fois par mois, à partir de Sentinel-1 (Mermoz et al., 2024, IEEE JSTARS). **Plateforme d'accès et licence introuvables** ❓. À garder en option, seulement si P4.6 est réintégré. |
| BLITZ (HD) | −− | − | − | ✅ | ❌ À **écarter** : données brutes réservées aux participants du réseau, usage commercial interdit, et l'archive limaps.org exclut explicitement l'usage pour l'**analyse de risque** et les systèmes d'alerte. |
| SIM2 | ++ | ++ | ++ | ✅ | Nouveau nom de CLIM (voir 1.2). |
| COG INSEE (à ajouter, HD) | ++ | ++ | + | — | Table de passage annuelle des communes. |

---

## 3. Revue indicateur par indicateur

| ID | Couverture déclarée | Couverture jugée | Avis (faisabilité, fiabilité, pertinence) | Action |
| -- | ------------------- | ---------------- | ----------------------------------------- | ------ |
| P1.1 | Directe (commune) | Directe à la commune, Proxy au carreau | Cible indispensable ; grain communal seulement. | Évaluer le seuil à la commune × jour ; demander la géolocalisation au SDIS. |
| P1.2 | Proxy | Proxy, peut-être Directe | Un degré de connaissance (Inconnu, Probable, Certaine) existe dans la BDIFF interne. | Vérifier l'export ; sinon le demander. |
| P1.3 | Absente (proxy MDF) | Absente | Le cœur de la problématique, mais les seuils sont mal choisis. | Seuils testés : 2 et 3 sur le niveau MDF, **et** une grille de seuils sur l'indice continu. |
| P2.1, P2.2, P2.5 | Proxy, Absente | Absente | D'accord. | Demande au SDIS. |
| P2.3, P5.5 | Proxy | Hypothèse | Ne pas les présenter comme des données. | Table de paramètres avec scénarios bas, central et haut. |
| P2.4 | Proxy | Proxy | Utile et réaliste (saisie documentaire). | Garder. |
| P2.6 | Calculée (partielle) | **Proxy** | Délai FIRMS → alerte sans valeur : 2 passages par jour, petits feux invisibles. Seule « part des feux sous 1 ha » est calculable. | Reclasser en Proxy ; ne garder que `part_feux_moins_1ha` par saison. |
| P3.1 | Directe (2024 à 2026), Proxy avant | Directe (MDF), Calculée (SIM2) | Voir 1.1 et 1.2. | SIM2 en principale avant 2024 ; correspondance IFM → niveau calée sur toute la France. |
| P3.2 | Directe, Calculée | Directe (BD Forêt), à dater | Essences : bonne donnée. Biomasse LiDAR et coupes S1 : trop lourd. | BD Forêt + masque des surfaces brûlées EFFIS ; LiDAR seulement en agrégé. |
| P3.3 | Calculée | Calculée | Simple, mais pèse peu en Gironde. | Garder une pente moyenne seulement. |
| P3.4 | Proxy | Proxy faible | BLITZ interdit ; densité de foudre ERA5 incertaine et modélisée. | Garder seulement `nb_feux_naturels` (BDIFF). |
| P4.1 | Calculée | Calculée | Bon facteur intra-départemental. | Fusionner avec OLD (P4.7). |
| P4.2 | Proxy | Proxy | Principal facteur humain du littoral. | Garder ; facteur saisonnier mensuel documenté. |
| P4.3 | Proxy | Proxy | Coût nul, intérêt réel. | Garder. |
| P4.4 | Proxy | Proxy | D'accord pour l'écarter (doublon de P4.5). | — |
| P4.5 | Directe, Proxy | Directe (linéaire), Proxy faible (trafic) | Le linéaire de routes en forêt suffit ; TMJA apporte peu en Gironde. | Garder le linéaire ; le trafic seulement si les comptages départementaux existent. |
| P4.6 | Proxy (écarté) | Proxy | Le RPG (céréales près des forêts × calendrier de moisson) coûte peu. | Décider sur les chiffres : réintégrer si la part « Involontaire (travaux) » de la BDIFF girondine dépasse ≈ 15 %. |
| P4.7 | Proxy | Proxy, redondant | Même zonage que P4.1. | Fusionner avec P4.1 ; retirer GASPAR. |
| P4.8 | Proxy (écarté) | Proxy | D'accord : fonction déterministe du niveau MDF. | — |
| P4.9 | Calculée | Calculée, à la commune | Risque de fuite. | Fenêtres antérieures ; grain commune. |
| P5.1 | Directe, Proxy | Directe (casernes) | Noms BD TOPO ❓. | Garder les casernes. |
| P5.2, P5.6 | Proxy, Absente | Absente | D'accord pour les écarter. | Demande au SDIS. |
| P5.3 | Calculée | Calculée | Isochrones faisables (BD TOPO, avec `vitesse_moyenne_vl` ❓). Valeur statique par carreau. | Garder ; un seul graphe (BD TOPO), sans R500. |
| P5.4 | Proxy | Proxy | Pistes DFCI non identifiées dans OSM ni (à confirmer) dans la BD TOPO. | Garder ; demander l'atlas DFCI. |

---

## 4. Avis sur les proxys retenus et écartés (§2.6.4)

| ID | Choix du document | Avis | Justification |
| -- | ----------------- | ---- | ------------- |
| P1.2 | Retenu | ✅ D'accord | Corriger la limite : un degré de connaissance existe peut-être dans l'export. |
| P1.3 | Retenu | ⚠️ D'accord, seuils à changer | Seuils 2 et 3, plus une grille de seuils sur l'indice continu. |
| P2.3 | Retenu | ⚠️ Comme paramètre | Table de scénarios, pas variable mesurée. |
| P2.4 | Retenu | ✅ D'accord | — |
| P3.1 | Retenu (EWDS) | ⚠️ Changer de source | SIM2 (8 km) en principale, EWDS en contrôle. |
| P3.4 | Retenu | ⚠️ Réduire | Garder `nb_feux_naturels` ; retirer BLITZ ; `densite_foudre` seulement si confirmée dans le CDS. |
| P4.2 | Retenu | ✅ D'accord | — |
| P4.3 | Retenu | ✅ D'accord | — |
| P4.5 | Retenu | ⚠️ Faible | Le trafic TMJA ne couvre presque pas les routes forestières. |
| P4.7 | Retenu | ❌ Fusionner | Même géométrie que P4.1 : risque de colinéarité. |
| P5.4 | Retenu | ✅ D'accord | — |
| P5.5 | Retenu | ⚠️ Comme paramètre | Ordre de grandeur. |
| P2.1, P2.2, P4.4, P4.8, P5.1, P5.2, P5.6 | Écartés | ✅ D'accord | — |
| P4.6 | Écarté | ⚠️ Décision à fonder sur les chiffres | Vérifier d'abord la part des causes « travaux » dans la BDIFF. |

---

## 5. Corrections à reporter dans « Indicateurs x donnees SDIS33.md »

| § | Correction |
| - | ---------- |
| 1.1, CLIM | Renommer en SIM2 : « Données changement climatique – SIM quotidienne », maille 8 km × jour, 1958 à aujourd'hui, CSV.gz, Licence Ouverte. Statut : principale. |
| 1.1, MDF | Période 2026 : 28 mai au 5 octobre. Ajouter : « jamais de niveau 4 en 33, 40 et 47 sur 2024 à 2026 ». |
| 1.1, EWDS | Grille 0,25° interpolée (native ≈ 31 km) ; licence CC-BY ; indices canadiens, sans IFM français ; noms courts NetCDF à confirmer. |
| 1.1, ERA5 | Densité de foudre : paramètre IFS du cycle 45r1, présence dans ERA5 non confirmée. |
| 1.1, SNSDIS | Remplacer le lien tiers par la publication officielle de la DGSCGC. |
| 1.1, OLD | Producteur et jeu : « Débroussaillement » (IGN, data.gouv), zonage informatif (massifs + 200 m), 45 départements. |
| 1.2, BLITZ | Passer en « écarté » (conditions d'usage). |
| 1.2, SUFOSAT | Existence confirmée (Mermoz et al., 2024) ; accès et licence inconnus. |
| 1.2 | Ajouter COG INSEE (table de passage des communes). |
| 2.1, P1.1 | Préciser « Directe à la commune, Proxy au carreau » et le double grain d'évaluation. |
| 2.2, P2.6 | Reclasser en Proxy. |
| 2.6.4, P1.3 | Seuils testés : 2 et 3 (niveau MDF) et une grille sur l'indice continu. |
| 2.6.4, P3.1 | Source : SIM2 en principale, EWDS en contrôle ; correspondance calée sur toute la France. |
| 2.6.4, P4.7 | Fusionner avec P4.1 ; retirer GASPAR. |
| 3 | Ajouter une colonne **Statut** (retenu, écarté, à vérifier) : sinon, les lignes des proxys écartés (P4.4, P4.8, P5.2…) se chargeront comme si elles étaient actives. |
| 4 | GASPAR, BLITZ, R500, CLC : passer en « écarté » ; CLIM (SIM2) : « prioritaire ». |
| 5 | Commune : la clé devient « code INSEE + table de passage COG » ; ajouter le grain d'évaluation commune × jour. |

---

## 6. Reste à vérifier (à faire au premier téléchargement)

| Élément | Comment le vérifier |
| ------- | ------------------- |
| En-tête de l'export CSV de la BDIFF (degré de connaissance, unité des surfaces) | Export Gironde depuis le portail (`/incendies/zip`) |
| Part des causes non renseignées et part « Involontaire (travaux) » en Gironde | Même export |
| Noms des variables SIM2 | En-tête d'un fichier `QUOT_SIM2_<année>` |
| Noms d'attributs BD TOPO v3.4 | Descriptif de contenu sur cartes.gouv.fr (ancien lien IGN redirigé) |
| Millésime de la BD Forêt V2 pour 33, 40 et 47 ; noms des champs | Carte des millésimes sur data.gouv ; descriptif IGN |
| Colonnes de GASPAR | Seulement si GASPAR est conservé |
| Densité de foudre dans ERA5 | Liste des variables « ERA5 single levels » du CDS |
| Liens INSEE (FILO, TOUR, RP) ; millésime FILO après 2019 | insee.fr |
| Comptages routiers du Département de la Gironde | Portail open data du Département |

---

## Sources consultées pendant la revue

- Archives locales `data/raw/archives/mdf_2024..2026.csv.gz` et `presentation_mdf.pdf`
- [Portail BDIFF](https://bdiff.agriculture.gouv.fr/incendies) et une fiche publique ([2025-421](https://bdiff.agriculture.gouv.fr/incendie/2025/421))
- [Support de formation BDIFF, ENASIS 2025](https://enasis.fr/pluginfile.php/99998/mod_folder/content/0/S%C3%A9minaires%20et%20journ%C3%A9es%20OPEN%20-%20pr%C3%A9sentations/2025%20-%20S%C3%A9minaire%20G%C3%A9rer%20le%20risque%20incendie%20de%20for%C3%AAt%20en%20inter%20service%2013%20et%2014%20novembre%202025/Ressources%20pr%C3%A9sent%C3%A9es%20en%20ateliers/Atelier%208%20-%20BDIFF.pdf)
- [data.gouv : SIM quotidienne (jeu 6569b275…)](https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne) et [documentation Météo-France des données climatologiques](https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/621510657/Donn+es+climatologiques)
- [EWDS : cems-fire-historical-v1](https://ewds.climate.copernicus.eu/datasets/cems-fire-historical-v1)
- [ECMWF : paramètres de densité de foudre (IFS 45r1)](https://confluence.ecmwf.int/x/yMFaBg)
- [Blitzortung : compendium](https://www.blitzortung.org/en/compendium.php) et [limaps.org](https://www.limaps.org)
- [SUFOSAT : FORMSpoT (arXiv), citant Mermoz et al. 2024](https://arxiv.org/html/2512.17021v1)
- [RPG 2022 : couche PARCELLES_GRAPHIQUES](https://services.arcgis.com/d3voDfTFbHOCRwVR/ArcGIS/rest/services/RPG_2022/FeatureServer/16)
- [data.gouv : Débroussaillement (OLD)](https://www.data.gouv.fr/datasets/debroussaillement)
- [data.gouv : BD Forêt](https://www.data.gouv.fr/datasets/bd-foret-r) ; [data.gouv : GASPAR](https://www.data.gouv.fr/datasets/base-nationale-de-gestion-assistee-des-procedures-administratives-relatives-aux-risques-gaspar/)

---

## 7. Addendum : vérifications faites le 20/11/2026 (après-midi)

| Élément | Résultat | Conséquence |
| ------- | -------- | ----------- |
| Export CSV de la BDIFF (33, 40, 47, 2006 à 2025) | ✅ Enregistré dans `data/raw/bdiff/`. 24 colonnes, séparateur `;`, 3 lignes de métadonnées, **surfaces en m²**. Ni carreau DFCI, ni coordonnées, ni origine de l'alerte, ni degré de connaissance de la cause. **Feux de forêt seulement.** 5 948 feux, dont 3 555 en Gironde (2 323 de juin à septembre). | P1.2 reste Proxy. La demande de géolocalisation au SDIS 33 doit couvrir aussi les feux de végétation hors forêt. |
| Causes en Gironde (juin à septembre) | Nature vide : 61 %. Parmi les causes connues : naturelle 50 %, accidentelle 22 %, malveillance 12 %, travaux 9 %, particulier 8 %. | **P3.4 (foudre) devient pertinent** : première cause connue en été. Météorage passe en priorité 2. **P4.6 reste écarté** : travaux = 3,4 % des feux d'été. |
| Volume d'événements | Environ 116 feux par saison en Gironde (25 en 2024, 102 en 2025) ; la moitié sous 0,1 ha. BDIFF 2026 non publiée. | Recouvrement MDF × BDIFF limité à 2024 et 2025 : 127 feux sur 75 jours. Il ne suffit pas pour caler un seuil sur le niveau MDF : l'historique long de SIM2 est indispensable. |
| SIM2 | ✅ En-tête lu : `LAMBX;LAMBY;DATE;PRENEI;PRELIQ;T;FF;Q;DLI;SSI;HU;EVAP;ETP;PE;SWI;SSWI_10J;…;TINF_H;TSUP_H`. Coordonnées en Lambert II étendu (hm) ; pas de numéro de maille. | Identifiant de maille à créer ; IFM approché avec `TSUP_H`, `HU`, `FF` (valeurs journalières) et `PRELIQ`. |
| BD TOPO | ✅ Attributs vérifiés sur le WFS de la Géoplateforme : `vitesse_moyenne_vl`, `acces_vehicule_leger`, `voltage`, `usage_1`, `nature` = « Caserne de pompiers » (74 objets en Gironde). `troncon_de_route` porte des attributs DFCI : environ 104 000 tronçons dans les Landes, 15 000 dans le Lot-et-Garonne, **91 en Gironde**. | P5.4 : Directe dans les Landes et le Lot-et-Garonne, Proxy en Gironde. Asymétrie à garder en tête dans les comparaisons ; l'atlas DFCI de Gironde reste à demander. |
| BD Forêt V2 | ✅ Champs `id`, `code_tfv`, `tfv`, `tfv_g11`, `essence`. Éditions : Gironde du 10/05/2017 ; Landes et Lot-et-Garonne du 01/10/2018. Le masque forêt par IA de l'IGN date de 2021 en Gironde. | Aucune couche forestière IGN ne reflète les feux de 2022 : le masquage par les surfaces brûlées EFFIS reste nécessaire. |

**Points restants, vérifiés ensuite** :

| Élément | Résultat | Conséquence |
| ------- | -------- | ----------- |
| Densité de foudre dans ERA5 | ✅ Absente : aucune des 262 variables de « ERA5 single levels » (catalogue du CDS) ne porte sur la foudre. | ERA5 écarté. Aucune source publique d'impacts de foudre : la demande à Météo-France (Météorage) devient la seule voie. |
| Noms des variables EWDS | ✅ Noms de requête : `fire_weather_index`, `fine_fuel_moisture_code`, `duff_moisture_code`, `drought_code`, `initial_fire_spread_index`, `build_up_index`… Noms courts NetCDF (base de paramètres ECMWF) : `fwinx`, `ffmcode`, `dufmcode`, `drtcode`, `infsinx`, `fbupinx`. | Levé. |
| SUFOSAT | Article de Morin et al. (2024), sous licence CC BY-NC-ND ; aucune plateforme de diffusion des cartes trouvée. | Écarté ; à demander aux auteurs si besoin. |
| Comptages routiers du Département | Aucun jeu en open data (recherche data.gouv sans résultat). Le Département exploite des stations de comptage permanentes ; l'atlas des trafics de la DREAL Nouvelle-Aquitaine (PDF) donne des moyennes annuelles. | À demander au Département de la Gironde. |
| Table de passage des communes | ✅ [insee.fr/fr/information/7671867](https://www.insee.fr/fr/information/7671867) : table annuelle, géographies 2003 à 2026. | Levé. |
