# Indicateurs SDIS 33 × données publiques

Ce document associe chaque **donnée idéale** de `data/Donnees_ideales_SDIS33.pdf` aux **données publiques précises** qui permettent de la calculer, en indiquant la **base d'origine**. Il prépare le tableau de visualisation de la future base agrégée (« super BDD »), puis son UML.

**Problématique** : quel seuil d'un indice de risque, calculé par zone à partir de facteurs naturels et humains, permettrait au SDIS 33 de déclencher son dispositif renforcé à l'été 2027 de façon efficiente, tout en limitant les fausses alertes ?

**Grain cible** : une ligne par **carreau DFCI de 2 km** et par **jour**.
**Emprise** : Gironde (33). Les Landes (40) et le Lot-et-Garonne (47) servent à la comparaison au sein du massif landais.

**Ordre de priorité des sources** : d'abord les 39 jeux du [défi data.gouv « Prévenir et détecter les feux de forêt »](https://defis.data.gouv.fr/defis/prevenir-et-detecter-les-feux-de-foret) (colonne Défi = **oui**), puis des sources publiques hors défi (Défi = **HD**), ajoutées seulement quand elles comblent un vide.

**Légende de la couverture**

| Couverture | Sens |
| ---------- | ---- |
| Directe | La donnée publique existe telle quelle, au grain voulu ou à un grain proche. |
| Calculée | Elle se dérive par croisement ou par calcul à partir de jeux publics. |
| Proxy | Seule une approximation publique existe, et l'écart à l'idéal est important. |
| Absente | Aucune source publique : donnée interne au SDIS 33 ou à la préfecture, à demander. |

Les mentions « à vérifier » signalent un champ ou une source dont l'existence ou l'intitulé exact n'a pas encore été confirmé au téléchargement.

**Révision du 20/11/2026** : les corrections de la revue critique (`Revue Indicateurs x donnees SDIS33.md`) sont reportées ici. Elles portent principalement sur :
- CLIM, requalifié en réanalyse SIM2 et devenu source principale ;
- les seuils MDF testés (2 et 3), le niveau 4 n'ayant jamais été atteint dans les trois départements ;
- le double grain : facteurs au carreau, évaluation du seuil à la commune × jour ;
- les sources écartées : BLITZ, GASPAR, R500, CLC, S1, FEST ;
- la fusion de P4.7 dans P4.1 et le reclassement de P2.6 en Proxy ;
- la colonne « Statut » de la table de liaison.

**Vérifications du 20/11/2026 (après-midi)** :
- **BDIFF** : export CSV des départements 33, 40 et 47 de 2006 à 2025, enregistré dans `data/raw/bdiff/bdiff_33_40_47_2006_2025.csv` (5 948 feux), avec ses définitions (`bdiff_definitions.pdf`).
- **SIM2** : en-tête lu sur `QUOT_SIM2_2025`, plus la notice des paramètres.
- **BD TOPO et BD Forêt** : attributs lus sur le service WFS de la Géoplateforme IGN (`data.geopf.fr`).

Les mentions « à vérifier » correspondantes sont levées ci-dessous.

---

## 1. Catalogue des sources

### 1.1. Sources du défi

| Code | Jeu de données | Producteur | Lien | Défi | Format | Grain natif | Période | Clé de jointure |
| ---- | -------------- | ---------- | ---- | ---- | ------ | ----------- | ------- | --------------- |
| BDIFF | Base de données sur les incendies de forêt en France | Ministère de l'Agriculture, IGN | [bdiff.agriculture.gouv.fr](https://bdiff.agriculture.gouv.fr/incendies) | oui | CSV (export du portail, `/incendies/zip` ; séparateur `;`, 3 lignes de métadonnées avant l'en-tête, 24 colonnes, **surfaces en m²**) ; local : `data/raw/bdiff/` | 1 feu **de forêt** (feu qui démarre ou se propage en forêt ou en terres boisées : les autres feux de végétation sont exclus), localisé à la commune. Ni carreau DFCI, ni coordonnées, ni origine de l'alerte, ni degré de connaissance de la cause dans l'export. | 2006 à 2025 (2026 pas encore publié). 33 : 3 555 feux, dont 2 323 de juin à septembre ; 40 : 1 905 ; 47 : 488 | `Code INSEE` + `Date de première alerte` (AAAA-MM-JJ hh:mm:ss) |
| ISDIS | Interventions réalisées par les services d'incendie et de secours | Ministère de l'Intérieur (DGSCGC) | [data.gouv](https://www.data.gouv.fr/fr/datasets/interventions-realisees-par-les-services-d-incendie-et-de-secours/) | oui | CSV (un fichier par an) | Département × année | 2008 à 2024 | `Numéro` (département) + `Année` |
| FIRMS | NASA FIRMS : points chauds détectés par satellite (MODIS, VIIRS) | NASA | [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov/) | oui | CSV, SHP | 1 détection : point (375 m à 1 km) ; VIIRS : 2 passages par jour (vers 1 h 30 et 13 h 30), petits feux le plus souvent non détectés | 2000 (MODIS), 2012 (VIIRS) à aujourd'hui | Latitude et longitude + `acq_date` |
| EFFIS | European Forest Fire Information System : surfaces brûlées, carte des combustibles, prévisions de danger | Commission européenne (JRC) | [EFFIS](https://forest-fire.emergency.copernicus.eu/applications/data-and-services) | oui | SHP, GeoTIFF | Feu d'au moins 30 ha environ (contour) ; raster de combustibles | 2000 à aujourd'hui | Géométrie + date |
| EWDS | Indices de danger feu historiques, Copernicus EMS (jeu `cems-fire-historical-v1`) : indices canadiens (FWI et composantes), plus des indices américains et australiens ; **pas d'IFM Météo-France** | Copernicus (ECMWF) | [ewds.climate.copernicus.eu](https://ewds.climate.copernicus.eu/datasets/cems-fire-historical-v1) | oui | NetCDF, GRIB2 ; licence CC-BY | Grille interpolée de 0,25° (grille native N320 ≈ 31 km) × jour | 1940 à aujourd'hui (réanalyse ERA5) | Latitude et longitude + date |
| MDF | Météo des forêts : archives et API | Météo-France | [Archives data.gouv](https://www.data.gouv.fr/datasets/archives-de-la-meteo-des-forets) ; [API](https://portail-api.meteofrance.fr/web/fr/api/DonneesPubliquesMeteoForets) ; local : `data/raw/archives/mdf_2024..2026.csv.gz` | oui | CSV.gz, JSON | Département × jour d'émission (vers 17 h) × échéance (J1 = lendemain, J2 = surlendemain) | Juin à septembre 2024 et 2025 ; 28 mai au 5 octobre 2026. **Niveau 4 jamais atteint en 33, 40 et 47** | `num_dep` + `date` (+1 jour pour J1) |
| AROME | Paquets AROME 0,01° | Météo-France | [data.gouv](https://www.data.gouv.fr/datasets/paquets-arome-resolution-0-01deg) | oui | GRIB2 | Maille d'environ 1,3 km × heure | Prévisions récentes, sans archive | Latitude et longitude + heure |
| ARPEGE | Paquets ARPEGE 0,1° | Météo-France | [data.gouv](https://www.data.gouv.fr/datasets/paquets-arpege-resolution-0-1deg) | oui | GRIB2 | Maille d'environ 11 km × heure | Prévisions récentes, sans archive | Latitude et longitude + heure |
| ERA5 | Copernicus Climate Data Store : réanalyse ERA5 | Copernicus (ECMWF) | [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/) | oui | NetCDF, GRIB | Maille de 0,25° × heure | 1940 à aujourd'hui | Latitude et longitude + heure |
| SIM2 (ex-CLIM) | Données changement climatique – **SIM quotidienne** : réanalyse Safran-Isba. Champs vérifiés : `PRELIQ`, `PRENEI` (pluie, neige), `T` (température moyenne), `TINF_H`, `TSUP_H` (minimum et maximum des températures horaires), `FF` (vent moyen), `HU` (humidité relative moyenne), `Q`, `ETP`, `EVAP`, `SWI` (humidité des sols), `SSWI_10J` (sécheresse des sols sur 10 jours), etc. | Météo-France | [meteo.data.gouv.fr](https://meteo.data.gouv.fr/datasets/6569b27598256cc583c917a7) ; [data.gouv](https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne) ; [notice des paramètres](https://static.data.gouv.fr/resources/donnees-changement-climatique-sim-quotidienne/20260331-150448/sim-quotidienne-parametres-20260331.pdf) | oui | CSV.gz, séparateur `;` (un fichier `QUOT_SIM2_<année>` par an, 85 à 492 Mo) ; Licence Ouverte 2.0 | Maille de 0,072° (≈ 8 km, 8 981 mailles fixes) × jour ; moyennes de 00 à 00 UTC, cumuls de pluie de 06 à 06 UTC | 1958 à aujourd'hui | `LAMBX`, `LAMBY` (Lambert II étendu, en hectomètres, à reprojeter en Lambert 93 ; pas de numéro de maille dans le fichier) + `DATE` (AAAAMMJJ) |
| SNSDIS | Statistiques nationales des SDIS (rapports annuels) | DGSCGC | Publication officielle de la DGSCGC (ministère de l'Intérieur, lien exact à confirmer) ; miroir : [ressourcesdupompier.com](https://www.ressourcesdupompier.com/etudes-statistiques/) | oui | PDF | SDIS × année | Éditions 2014 à 2025 | Département + année |
| PYRO | Images de départs de feux, SDIS 2024 (Pyronear) | Pyronear | [data.gouv](https://www.data.gouv.fr/datasets/images-de-departs-de-feux-sdis-2024) | oui | Images annotées | 1 image | 2024 | Aucune (pas de géolocalisation exploitable) |
| DOC | Stratégie nationale DFCI ; PPFCI et PDPFCI ; PPRIF | Ministère de l'Agriculture, préfectures | [Stratégie nationale](https://observatoire.foret.gouv.fr/themes/la-strategie-francaise-de-lutte-contre-les-feux-de-foret) | oui | PDF, arrêtés | Document | Version en vigueur | Aucune (documentaire) |
| BDTOPO | BD TOPO® v3 ; attributs vérifiés sur le WFS `BDTOPO_V3:*`. `troncon_de_route` porte des **attributs DFCI** (`piste_dfci`, `gabarit_dfci`, `categorie_dfci`, `vitesse_moyenne_dfci`…), renseignés dans les Landes (≈ 104 000 tronçons) et le Lot-et-Garonne (≈ 15 000), mais **presque pas en Gironde (91 tronçons sur ≈ 382 000)**. | IGN | [data.gouv](https://www.data.gouv.fr/datasets/bd-topo-r/) | oui | GPKG, SHP, WFS | Objet vectoriel (bâtiment, tronçon…) | Millésimes trimestriels | Géométrie ; code INSEE (`insee_commune`, `insee_commune_gauche`/`_droite`) |
| BDORTHO | BD ORTHO® | IGN | [data.gouv](https://www.data.gouv.fr/datasets/bd-ortho-r/) | oui | JPEG2000 | Pixel de 20 cm | Millésimes tous les 3 ans environ | Géométrie |
| LIDAR | MNS LiDAR HD (modèle numérique de surface) | IGN | [data.gouv](https://www.data.gouv.fr/datasets/mns-lidar-hd) | oui | GeoTIFF | Pixel de 50 cm | Acquisitions 2021 à aujourd'hui | Géométrie |
| FORPUB | Forêts publiques (diffusion publique) | ONF | [data.gouv](https://www.data.gouv.fr/datasets/forets-publiques-diffusion-publique) | oui | WFS | Forêt ou parcelle publique | État actuel | Géométrie |
| BDFORET | BD Forêt® V2 (nomenclature de 32 postes) ; champs vérifiés : `id`, `code_tfv`, `tfv`, `tfv_g11`, `essence` | IGN | [data.gouv](https://www.data.gouv.fr/datasets/bd-foret-r) ; WFS `LANDCOVER.FORESTINVENTORY.V2:formation_vegetale` | oui | SHP, WFS | Polygone d'au moins 0,5 ha | Éditions : 33 du 10/05/2017 ; 40 et 47 du 01/10/2018 : **antérieures aux feux de 2022**. Le masque forêt par IA de l'IGN (`IGNF_MASQUE-FORET.2021-2023`) date aussi de 2021 en Gironde. | Géométrie |
| CLC | Corine Land Cover | SDES, Copernicus | [data.gouv](https://www.data.gouv.fr/datasets/corine-land-cover-occupation-des-sols-en-france/) | oui | SHP, GPKG | Polygone d'au moins 25 ha | 1990, 2000, 2006, 2012, 2018 | Géométrie |
| RPG | Registre parcellaire graphique (parcelles agricoles) | IGN, ASP | [data.gouv](https://www.data.gouv.fr/datasets/rpg) | oui | GPKG, SHP | Parcelle ou îlot × année | 2007 à aujourd'hui | Géométrie + année |
| RESBIO | Réserves biologiques | ONF | [data.gouv](https://www.data.gouv.fr/datasets/reserves-biologiques-diffusion-publique-1) | oui | WFS | Réserve | État actuel | Géométrie |
| ARTIF | Artificialisation des sols | Mon diagnostic artificialisation (Cerema) | [data.gouv](https://www.data.gouv.fr/datasets/artificialisation-des-sols-donnees-par-region-departement-scot-commune-et-epci) | oui | GPKG, CSV | Commune × période | 2016 à 2022 (OCS GE), fichiers fonciers depuis 2009 | Code INSEE |
| ONFNAT | Données naturalistes de l'ONF | ONF | [data.gouv](https://www.data.gouv.fr/datasets/donnees-naturalistes-de-l-onf-0) | oui | CSV, WFS | Observation | Variable | Géométrie |
| OCSGE | OCS GE (occupation du sol à grande échelle) | IGN | [data.gouv](https://www.data.gouv.fr/datasets/ocs-ge) | oui | GPKG | Polygone (couverture × usage) | 2 millésimes par département | Géométrie |
| DFCI | Carroyage DFCI 2 km | IGN, DFCI | [data.gouv](https://www.data.gouv.fr/datasets/carroyage-dfci-2-km/) (`CARRO_DFCI_2x2_L93.7z`) | oui | SHP (Lambert 93) | Carreau de 2 km × 2 km | Stable | Identifiant à 6 caractères (ex. `KD42F7`) |
| PRS | Points de rencontre des secours et couverture téléphonique | ONF | [data.gouv](https://www.data.gouv.fr/datasets/points-de-rencontre-des-secours-et-couverture-telephonique-1) | oui | WFS | Point | État actuel | Géométrie |
| ADMIN | Admin Express (communes, EPCI, départements) | IGN | [data.gouv](https://www.data.gouv.fr/datasets/admin-express/) | oui | SHP, GPKG | Commune | 2017 à aujourd'hui (millésimes) | Code INSEE |
| GEOFLA | GEOFLA® (limites administratives anciennes) | IGN | [data.gouv](https://www.data.gouv.fr/datasets/geofla-r/) | oui | SHP | Commune | 1997 à 2016 | Code INSEE |
| OSM | OpenStreetMap France métropolitaine | OpenStreetMap | [data.gouv](https://www.data.gouv.fr/datasets/donnees-openstreetmap-integrales-de-france-metropolitaine/) | oui | PBF | Objet (nœud, chemin) avec tags | État actuel | Géométrie |
| EGM | EuroGlobalMap 1/1 000 000 | EuroGeographics | [data.gouv](https://www.data.gouv.fr/datasets/euroglobalmap-donnees-topographiques-au-1-1-000-000-couvrant-45-pays-et-territoires-en-europe/) | oui | SHP | Objet à petite échelle | Annuel | Géométrie |
| S1 | Copernicus Sentinel-1A (radar) | ESA, Copernicus | [data.gouv](https://www.data.gouv.fr/datasets/copernicus-satellite-sentinel-1a/) | oui | SAFE, GeoTIFF | Pixel de 10 m × passage (6 à 12 jours) | 2014 à aujourd'hui | Géométrie + date |
| TMJA | Trafic moyen journalier annuel sur le réseau routier national | Ministère de la Transition écologique | [data.gouv](https://www.data.gouv.fr/datasets/trafic-moyen-journalier-annuel-sur-le-reseau-routier-national/) | oui | CSV, SHP | Section de route nationale ou d'autoroute × année | 2019 à 2024 environ | `route` + `prD`/`prF` ; coordonnées `xD`, `yD`, `xF`, `yF` |
| R500 | ROUTE 500® | IGN | [data.gouv](https://www.data.gouv.fr/datasets/route-500/) | oui | SHP | Tronçon du réseau principal | Dernier millésime (produit dérivé de la BD TOPO) | Géométrie |
| OLD | Obligations légales de débroussaillement : jeu « Débroussaillement », zonage informatif (massifs concernés + tampon de 200 m), 45 départements | IGN, ministère de l'Agriculture | [data.gouv](https://www.data.gouv.fr/datasets/debroussaillement) ; [georisques.gouv.fr](https://www.georisques.gouv.fr/donnees/bases-de-donnees/obligations-legales-de-debroussaillement) | oui | SHP, GPKG (versions allégée et complète) | Zone soumise aux OLD | Mise à jour du 08/04/2026 | Géométrie ; numéro de département |
| GASPAR | Base GASPAR (risques et procédures par commune) | Ministère de la Transition écologique | [data.gouv](https://www.data.gouv.fr/datasets/base-nationale-de-gestion-assistee-des-procedures-administratives-relatives-aux-risques-gaspar/) | oui | CSV (`gaspar.zip`) ; Licence Ouverte | Commune × risque ou procédure | Mise à jour continue | Code INSEE (`cod_commune`, à vérifier) |
| FEST | Liste des festivals en France | Ministère de la Culture | [data.gouv](https://www.data.gouv.fr/datasets/liste-des-festivals-en-france) | oui | CSV, GPKG | 1 festival | Référence 2019 | `Code Insee commune` ; `Géocodage xy` |

### 1.2. Sources hors défi (HD)

| Code | Jeu de données | Producteur | Lien | Défi | Format | Grain natif | Période | Clé de jointure |
| ---- | -------------- | ---------- | ---- | ---- | ------ | ----------- | ------- | --------------- |
| BDALTI | BD ALTI® 25 m (MNT), avec en complément le MNT LiDAR HD | IGN | [geoservices.ign.fr/bdalti](https://geoservices.ign.fr/bdalti) | HD | ASC, GeoTIFF | Pixel de 25 m | Stable | Géométrie |
| FILO | Filosofi, données carroyées à 200 m (population et ménages) | INSEE | [insee.fr](https://www.insee.fr/fr/statistiques?debut=0&theme=0&categorie=10&geo=0) (rubrique « Données carroyées ») | HD | CSV, GPKG | Carreau de 200 m | Millésimes 2015, 2017, 2019 | Identifiant du carreau ; géométrie |
| TOUR | Capacité des communes en hébergement touristique (hôtels, campings, autres hébergements collectifs) | INSEE | [insee.fr](https://www.insee.fr/fr/statistiques/2021703) | HD | CSV | Commune × année | Annuel | Code INSEE |
| RP | Recensement de la population : logements (dont résidences secondaires) | INSEE | [insee.fr](https://www.insee.fr/fr/statistiques) (base « Logement ») | HD | CSV | Commune × année | Annuel (millésimes glissants) | Code INSEE |
| BALANCES | Balances comptables des établissements publics locaux (dont le SDIS 33) | DGFiP | [data.gouv](https://www.data.gouv.fr/datasets/balances-comptables-des-etablissements-publics-locaux-depuis-2010/) (lien vérifié) | HD | CSV | Établissement × compte × exercice | 2010 à aujourd'hui | SIREN du SDIS + exercice |
| CARBU | Prix des carburants en France | Ministère de l'Économie | [data.gouv](https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane/) | HD | XML, CSV | Station × relevé | Historique annuel disponible | Code postal ; coordonnées |
| SPV | Barèmes réglementaires : indemnité horaire des sapeurs-pompiers volontaires | Légifrance (arrêté ministériel) | [legifrance.gouv.fr](https://www.legifrance.gouv.fr/) | HD | Texte | Grade × année | Révisions successives | Grade |
| SUFOSAT | Suivi des coupes rases en France métropolitaine, plus d'une fois par mois, à partir de Sentinel-1 (Morin et al., 2024, IEEE JSTARS ; rappel 81 %, précision 99 %) | Recherche publique | Aucune plateforme de diffusion publique trouvée ; l'article est sous licence CC BY-NC-ND, les cartes ne sont pas diffusées. **Écarté** (à demander aux auteurs du CESBIO ou de GlobEO si besoin) | HD | Raster ou vecteur | Pixel ou polygone × date | 2018 à aujourd'hui (à vérifier) | Géométrie + date |
| BLITZ | Blitzortung : impacts de foudre détectés par un réseau collaboratif. **Écarté** : données brutes réservées aux participants du réseau, usage commercial interdit, usage pour l'analyse de risque et l'alerte exclu (archive limaps.org) | Blitzortung.org | [blitzortung.org](https://www.blitzortung.org/en/compendium.php) | HD | JSON | 1 impact : point et heure | Archives réservées | Latitude et longitude + heure |
| COG | Code officiel géographique : table de passage annuelle des communes (fusions de communes) | INSEE | [insee.fr : tables de passage des communes](https://www.insee.fr/fr/information/7671867) (table de passage annuelle, géographies 2003 à 2026) | HD | CSV | Commune × millésime | 2003 à aujourd'hui | Code INSEE |

---

## 2. Correspondance par indicateur

Les sections 2.1 à 2.5 ne gardent que les indicateurs couverts de façon **directe** ou **calculée**. Tous les indicateurs **absents** ou couverts seulement par un **proxy** sont regroupés en 2.6, avec leur identifiant d'origine.

### 2.1. Partie 1. Départs de feu et déclenchements

| ID | Indicateur idéal | Données retenues → champs précis | Sources | Couverture | Grain et période réels | Calcul vers DFCI × jour | Écart à l'idéal, à demander au SDIS 33 |
| -- | ---------------- | -------------------------------- | ------- | ---------- | ---------------------- | ----------------------- | -------------------------------------- |
| P1.1 | Départs de feu exhaustifs, y compris les très petits | **BDIFF** : `Année`, numéro de fiche, commune (code INSEE et nom), département, **date et heure de première alerte**, **`Surface parcourue (m2)`** et sa répartition (forêt ; maquis et garrigues ; autres surfaces naturelles hors forêt ; agricoles ; autres ; terres boisées ; non boisées), `Précision des surfaces` (vide pour 81 % des feux girondins). `Type de peuplement` est vide pour tous les feux girondins. **FIRMS** : `latitude`, `longitude`, `acq_date`, `acq_time`, `confidence`, `frp`. **EFFIS** : contours des surfaces brûlées avec dates (feux d'au moins 30 ha environ). | BDIFF (principale), FIRMS, EFFIS | Directe à la commune ; Proxy au carreau | 1 feu × commune, 2006 à 2025, départements 33, 40 et 47 ; pas de point GPS ni de type de végétation fin. **Feux de forêt seulement** (les autres feux de végétation sont exclus). Gironde, juin à septembre : environ 116 feux par saison (de 23 en 2021 à 300 en 2006 ; 25 en 2024, 102 en 2025), dont la moitié sous 0,1 ha et 81 % sous 1 ha (sur l'année). | **Double grain** : l'évaluation du seuil (feux, fausses alertes) se fait à la **commune × jour** ; la répartition au prorata de la surface boisée (BDFORET) sert seulement de carte de densité par carreau, car elle produit des fractions de feu. Grands feux : appariement FIRMS ou EFFIS ↔ BDIFF avec une règle explicite (commune + 2 km, écart ≤ 24 h). Date = date de première alerte. | Point GPS d'éclosion, heure d'éclosion, type de végétation, **et les feux de végétation hors forêt** : extraction des interventions « feux de forêt et de végétation » du SDIS 33 (système de gestion opérationnelle). |

Déplacés en 2.6 : P1.2, P1.3.

### 2.2. Partie 2. Ressources du dispositif renforcé et états de mobilisation

Aucun indicateur de la partie 2 n'est couvert de façon directe ou calculée.

Déplacés en 2.6 : P2.1, P2.2, P2.3, P2.4, P2.5, P2.6.

### 2.3. Partie 3. Facteurs naturels

| ID | Indicateur idéal | Données retenues → champs précis | Sources | Couverture | Grain et période réels | Calcul vers DFCI × jour | Écart à l'idéal, à demander au SDIS 33 |
| -- | ---------------- | -------------------------------- | ------- | ---------- | ---------------------- | ----------------------- | -------------------------------------- |
| P3.1 | Niveau Météo des forêts, échéances J1 et J2 | **MDF** : `date` (émission, UTC), `num_dep`, `nom_dep` ou `dep_nom`, **`niveau_j1`**, **`niveau_j2`** (1 faible à 4 très élevé). Indice continu et historique : IFM calculé à partir de **SIM2** (précipitations, température, humidité, vent : `PRELIQ`, `TSUP_H`, `HU`, `FF` ; `SWI` et `SSWI_10J` pour la sécheresse des sols). Contrôle : **EWDS** : `fire_weather_index`, `fine_fuel_moisture_code`, `duff_moisture_code`, `drought_code`, `initial_fire_spread_index`, `build_up_index` (noms de requête vérifiés ; noms courts NetCDF selon la base de paramètres ECMWF : `fwinx`, `ffmcode`, `dufmcode`, `drtcode`, `infsinx`, `fbupinx`). | MDF (principale), SIM2, EWDS | Directe (2024 à 2026) ; Calculée (indice continu, depuis 1958) | MDF : département × jour, 2024 à 2026 (33, 40, 47) ; SIM2 : maille de 8 km × jour depuis 1958 ; EWDS : 0,25° × jour depuis 1940 | Date de validité = date d'émission + 1 jour (J1) ou + 2 jours (J2). Chaque carreau DFCI hérite du niveau de son département. SIM2 et EWDS : valeur de la maille qui contient le centroïde du carreau. L'IFM tiré de SIM2 est approché (valeurs journalières au lieu des valeurs de midi). | Harmoniser les archives (séparateur `,` ou `;`, `nom_dep` ou `dep_nom`, `1` ou `01`). Archive 2023 : à demander à Météo-France. Le niveau MDF intègre déjà, à l'échelle du département, la surface forestière, l'interface forêt-habitat et les zones sensibles : ne pas recompter ces facteurs entre départements. |
| P3.2 | Type de combustible : essences, sous-bois, biomasse, coupes récentes | **BDFORET** V2 : `CODE_TFV`, `TFV` (type de formation végétale, 32 postes), `TFV_G11`, `ESSENCE` (vérifiés, en minuscules sur le WFS). **EFFIS** : surfaces brûlées datées, pour masquer le combustible disparu (feux de 2022 notamment). **OCSGE** : couverture (`code_cs`) et usage (`code_us`). **FORPUB** : forêts publiques. Hauteur de végétation (proxy de la biomasse) = **LIDAR** MNS − MNT **BDALTI**, seulement sous forme agrégée (rééchantillonnage à 25 m ou produit de hauteur de canopée). Coupes récentes : non retenues (SUFOSAT sans accès public, S1 trop lourd). | BDFORET (principale), EFFIS, OCSGE, FORPUB, LIDAR, BDALTI (HD), SUFOSAT (HD) | Directe (essences) ; Calculée (biomasse, coupes) | Polygone d'au moins 0,5 ha ; édition 2017 en Gironde, 2018 dans les Landes et le Lot-et-Garonne : antérieure à 2022 | Par carreau : part de surface par type de formation végétale (pin maritime, feuillus, landes…) après masquage des surfaces brûlées, `annees_depuis_dernier_feu`, hauteur moyenne de végétation, surface coupée au cours des 12 derniers mois. | Mise à jour des coupes rases et des chablis (CRPF, DFCI Aquitaine). |
| P3.3 | Relief : pente, exposition au soleil | **BDALTI** 25 m : altitude, d'où l'on tire la **pente** et l'**exposition**. En complément, MNT LiDAR HD (HD) et MNS **LIDAR** (défi). | BDALTI (HD, principale), LIDAR | Calculée | Pixel de 25 m, stable | Par carreau : pente moyenne et maximale, part de surface exposée au sud ou au sud-ouest. Poids attendu faible : la Gironde est plane, hormis les dunes littorales et l'Entre-deux-Mers. | Aucun. |

Déplacés en 2.6 : P3.4.

### 2.4. Partie 4. Facteurs humains

| ID | Indicateur idéal | Données retenues → champs précis | Sources | Couverture | Grain et période réels | Calcul vers DFCI × jour | Écart à l'idéal, à demander au SDIS 33 |
| -- | ---------------- | -------------------------------- | ------- | ---------- | ---------------------- | ----------------------- | -------------------------------------- |
| P4.1 | Interface forêt-habitat : bâtiments à moins de 200 m d'un massif (intègre P4.7) | **BDTOPO**, classe `BATIMENT` : géométrie, `nature`, `usage_1`. **BDFORET** : polygones de forêt. **OLD** : zonage informatif (massifs + tampon de 200 m), qui peut servir directement de tampon. Évolution : **ARTIF** (surface artificialisée par commune et par période), **OCSGE** (deux millésimes). | BDTOPO (principale), BDFORET, OLD, ARTIF, OCSGE | Calculée | Bâtiment ; ARTIF : commune, 2009 à 2022 | Tampon de 200 m autour des forêts (ou zonage OLD), puis, par carreau : nombre de bâtiments (`nb_batiments_interface`) et longueur de lisière habitée. Tendance sur 10 ans à partir d'ARTIF et d'OCSGE. Variable utile à l'intérieur du département seulement : le niveau MDF en tient déjà compte entre départements. | Résultats des contrôles OLD (voir P4.7). |
| P4.5 | Infrastructures sources de départs, avec leur trafic | **BDTOPO** : `TRONCON_DE_ROUTE` (`nature`, `importance`), `TRONCON_DE_VOIE_FERREE`, `LIGNE_ELECTRIQUE` (`voltage`, `gestionnaire`) (vérifiés). **OSM** (`highway=*`, `railway=*`, `power=line`). Trafic : **TMJA**. | BDTOPO (principale), OSM, TMJA | Directe (infrastructures) ; Proxy (trafic) | Tronçon, état actuel | Par carreau : linéaire de routes par classe d'importance, de voies ferrées et de lignes électriques en forêt ; trafic pondéré (TMJA ne couvre que le réseau national, surtout autoroutier en Gironde). | Trafic ferroviaire (SNCF Réseau) et lignes électriques en forêt (RTE, Enedis), si besoin. |
| P4.9 | Antécédents de malveillance | **BDIFF** : feux où `Nature` vaut malveillance, avec la commune et la date de première alerte. | BDIFF | Calculée | Commune × année, 2006 à 2025 | Par commune (carreau seulement en carte de densité, comme en P1.1) : nombre de feux de malveillance sur les 5, 10 et 20 saisons **strictement antérieures** à la saison évaluée, pour éviter que la variable « voie » la cible. | Zones de récidive connues des enquêteurs. |

Déplacés en 2.6 : P4.2, P4.3, P4.4, P4.6, P4.7, P4.8.

### 2.5. Partie 5. Moyens et efficience du déploiement

| ID | Indicateur idéal | Données retenues → champs précis | Sources | Couverture | Grain et période réels | Calcul vers DFCI × jour | Écart à l'idéal, à demander au SDIS 33 |
| -- | ---------------- | -------------------------------- | ------- | ---------- | ---------------------- | ----------------------- | -------------------------------------- |
| P5.1 | Implantation des centres de secours, des engins feux de forêt et des postes de guet ou caméras | **BDTOPO**, classe `ZONE_D_ACTIVITE_OU_D_INTERET` : `categorie` = « Administratif ou militaire », `nature` = « Caserne de pompiers » (vérifié : 74 objets en Gironde, à comparer au nombre de centres du SDIS 33). **OSM** : `amenity=fire_station`, `man_made=tower` + `tower:type=observation`, caméras éventuelles (`man_made=surveillance`). **PRS** : points de rencontre des secours. Nombre de centres et d'engins : **SNSDIS**. | BDTOPO (principale), OSM, PRS, SNSDIS | Directe (centres) ; Proxy (engins, guet, caméras) | Point, état actuel (33, 40, 47) | Table « site » géolocalisée ; carreau du site. | Liste des engins feux de forêt par centre, emplacement des vigies et des caméras, état 2027. |
| P5.3 | Temps d'accès à chaque zone depuis les centres de secours | Graphe routier **BDTOPO** `TRONCON_DE_ROUTE` (`nature`, `vitesse_moyenne_vl`, `acces_vehicule_leger` : vérifiés), ou **OSM** en secours ; casernes (P5.1) ; centroïdes des carreaux **DFCI**. | BDTOPO (principale), OSM, DFCI | Calculée | Carreau × centre, état actuel | Temps de trajet du centre le plus proche jusqu'au centroïde de chaque carreau (isochrones). | Délais réels constatés et vitesses des engins feux de forêt. |

Déplacés en 2.6 : P5.2, P5.4, P5.5, P5.6.

### 2.6. Absent et Proxy

#### 2.6.1. Absentes

Aucune source publique ne fournit la donnée. Le proxy éventuel est indiqué, mais il reste très éloigné de l'idéal.

| ID | Indicateur idéal | Données retenues → champs précis | Sources | Couverture | Grain et période réels | Calcul vers DFCI × jour | Écart à l'idéal, à demander au SDIS 33 |
| -- | ---------------- | -------------------------------- | ------- | ---------- | ---------------------- | ----------------------- | -------------------------------------- |
| P1.3 | Registre des déclenchements du dispositif renforcé | Aucune donnée publique. Reconstitution théorique : jours où **MDF** `niveau_j1` (Gironde) atteint le seuil testé (2 ou 3 ; le niveau 4 n'a jamais été atteint en 2024 à 2026), ou jours où l'indice continu (IFM tiré de **SIM2**, combiné aux facteurs de zone) dépasse chaque valeur d'une grille de seuils. Règles DOC pour le seuil actuel. | MDF, SIM2, DOC | Absente (proxy MDF et SIM2) | MDF : département × jour, 2024 à 2026 (19 jours au niveau 3 en Gironde). **Recouvrement avec la BDIFF : 2024 et 2025 seulement** (la BDIFF 2026 n'est pas publiée), soit 127 feux d'été en Gironde répartis sur 75 jours ; SIM2 : maille × jour depuis 1958 | Niveau MDF : tous les carreaux de la Gironde héritent du déclenchement théorique du département. Indice continu : déclenchement par commune × jour. | Registre réel : date, zone, niveau qui a motivé le déclenchement, moyens engagés, pour toutes les saisons passées. |
| P2.2 | États de mobilisation de chaque ressource et passages d'un état à l'autre | Aucune donnée publique. Le vocabulaire des états peut venir de DOC (ordre d'opérations, guides de doctrine nationaux). | DOC | Absente | Aucun | Table de référence « type de ressource × état ». | Délai de passage, préavis, durées minimale et maximale, repos obligatoire, par état. |
| P2.5 | Journal d'activité des patrouilles et du guet | Aucune donnée publique. | Aucune | Absente | Aucun | Sans objet. | Traces GPS des patrouilles, postes de guet × heure, fumées signalées, feux naissants traités. |
| P5.6 | Chronologie de chaque intervention | **BDIFF** : date et heure de première alerte et surface finale uniquement. **ISDIS** : `Feux de végétations` par an. | BDIFF, ISDIS | Absente (proxy très partiel) | Feu × commune ; département × année | Sans objet. | Horodatages alerte → départ → arrivée → feu fixé, et moyens engagés, sur au moins 10 ans. |

#### 2.6.2. Proxy

Seule une approximation publique existe.

| ID | Indicateur idéal | Données retenues → champs précis | Sources | Couverture | Grain et période réels | Calcul vers DFCI × jour | Écart à l'idéal, à demander au SDIS 33 |
| -- | ---------------- | -------------------------------- | ------- | ---------- | ---------------------- | ----------------------- | -------------------------------------- |
| P1.2 | Cause de chaque feu, avec un degré de certitude | **BDIFF** : `Nature` (involontaire travaux, involontaire particulier, malveillance, accidentelle, naturelle, non renseignée). Le champ « Précision de la donnée » indique la fiabilité de la saisie, pas la certitude de la cause (vide pour 99,7 % des feux girondins). La BDIFF interne contient un **degré de connaissance de la Nature** (Inconnu, Probable, Certaine), une « Source de l'enquête » et l'intervention de la cellule RCCI : **absents de l'export public** (vérifié). | BDIFF | Proxy | 1 feu, 2006 à 2025. Gironde, juin à septembre : Nature vide pour 61 % des feux ; parmi les causes connues, naturelle 50 %, accidentelle 22 %, malveillance 12 %, travaux 9 %, particulier 8 % | Hériter de la cause dans la table des feux ; regrouper en « naturelle » ou « humaine ». | Degré de certitude de la cause et causes détaillées : résultats des enquêtes (RCCI, gendarmerie, DFCI). |
| P2.1 | Catalogue des ressources du dispositif renforcé | Types de moyens décrits dans le **PDPFCI** de Gironde et la stratégie nationale (DOC) ; caméras de détection (**PYRO**, à titre d'exemple de ressource) ; vigies et tours de guet dans **OSM** (`man_made=tower` + `tower:type=observation`) ; nombre d'engins du SDIS 33 dans **SNSDIS**. | DOC, OSM, PYRO, SNSDIS | Proxy | Liste qualitative ; SNSDIS par SDIS × année | Table de référence « type de ressource », sans grain spatial ; rayon de couverture saisi à la main. | Catalogue 2027 : zone couverte, personnels et engins requis, délai d'intervention, conditions d'emploi. |
| P2.3 | Coût de chaque ressource selon son état de mobilisation | **SPV** : indemnité horaire de base par grade ; **CARBU** : prix du gazole ; **SNSDIS** : dépenses de personnel et coût par habitant du SDIS 33 ; **BALANCES** : comptes de charges du SDIS 33 (carburant, indemnités…). | SPV (HD), CARBU (HD), SNSDIS, BALANCES (HD) | Proxy | Barèmes nationaux par année ; comptes annuels | Table « type de ressource × état × coût unitaire », alimentée par des hypothèses documentées. | Coûts réels 2026 et tarifs 2027 : heure de garde, heure de vol, exploitation d'une caméra, coût fixe d'activation. |
| P2.4 | Doctrine d'engagement actuelle | **PDPFCI** de Gironde ; règlement interdépartemental de protection de la forêt contre l'incendie (33, 40, 47) ; stratégie nationale DFCI. | DOC | Proxy | Documentaire | Table « niveau de danger × zone → ressources et état prévus », saisie à partir des documents. | Ordre d'opérations feux de forêt et plan de prépositionnement du SDIS 33. |
| P2.6 | Bilan de performance de chaque ressource | **BDIFF** : part des feux éteints sous 1 ha (surface parcourue). Le délai entre la détection **FIRMS** et la première alerte est abandonné : 2 passages par jour seulement, petits feux invisibles. | BDIFF | Proxy | Feu × saison, 2006 à 2025 | Agrégé par saison et par commune ; aucune attribution à une ressource possible. | Feux détectés par ressource, délai entre détection et alerte, fausses détections, coût par feu détecté. |
| P3.4 | Impacts de foudre | **BDIFF** : feux où `Nature` vaut naturelle. La densité de foudre ERA5 est **absente** du catalogue « ERA5 single levels » du CDS (aucune des 262 variables ne porte sur la foudre ; vérifié) : ERA5 est écarté pour P3.4. BLITZ est écarté aussi (conditions d'usage). Aucune source publique ne donne donc les impacts de foudre. | BDIFF | Proxy | Feu × commune | Par commune et par période : nombre de feux d'origine naturelle. | Impacts de foudre géolocalisés (Météorage, via Météo-France ou le SDIS 33). |
| P4.2 | Présence humaine réelle : résidents et population saisonnière | **FILO** : `Ind` (individus) par carreau de 200 m. **TOUR** : chambres d'hôtel, emplacements de camping, lits des autres hébergements collectifs par commune. **RP** : résidences secondaires par commune. **FEST** : `Période principale de déroulement du festival`, `Code Insee commune`. | FILO (HD), TOUR (HD), RP (HD), FEST | Proxy | Carreau ou commune × année ; aucune donnée journalière | Population estivale par carreau = résidents + capacité touristique de la commune × taux d'occupation supposé, répartie sur le bâti. Facteur saisonnier mensuel (juillet, août). | Données de téléphonie mobile (Flux Vision, non publiques) ou estimations de l'office de tourisme. |
| P4.3 | Fréquentation des massifs | **OSM** : `amenity=parking`, `highway=path`, `highway=track`, `natural=beach`, `tourism=camp_site`, `tourism=picnic_site`. **FORPUB** : forêts publiques ouvertes au public. **FEST**. | OSM, FORPUB, FEST | Proxy | Objet, état actuel ; aucune série journalière | Par carreau : nombre de parkings forestiers, longueur de sentiers, présence de plage ou de camping. | Comptages de fréquentation (ONF, éco-compteurs, Département). |
| P4.4 | Déplacements en période estivale | **TMJA** : `route`, `TMJA`, `ratio_PL`, `anneeMesureTrafic`, coordonnées des sections (`xD`, `yD`, `xF`, `yF`). Comptages du réseau départemental de Gironde : non publiés en open data (vérifié sur data.gouv) ; seulement des moyennes annuelles par section dans l'atlas des trafics de la DREAL Nouvelle-Aquitaine (PDF). | TMJA | Proxy | Section du réseau national × année ; aucune donnée journalière ni estivale | Par carreau : somme de TMJA × longueur des sections traversées. | Comptages journaliers estivaux (DIR Atlantique, Département de la Gironde). |
| P4.6 | Activités à risque | **RPG** : `CODE_CULTU`, `CODE_GROUP` (céréales à paille, d'où une période de moisson en juillet), géométrie de la parcelle. Travaux forestiers : coupes détectées sur **S1** ou **SUFOSAT**. | RPG (principale), S1, SUFOSAT (HD) | Proxy | Parcelle × année ; aucune date de chantier | Par carreau et par jour : surface de céréales près des forêts × indicateur de période de moisson ; surface en coupe récente. | Chantiers forestiers déclarés (DFCI, CRPF, préfecture) et dates de moisson. |
| P4.7 | Respect des obligations de débroussaillement autour des habitations | **OLD** : zonage informatif (massifs + tampon de 200 m). **BDTOPO** : bâtiments situés dans ces zones. GASPAR retiré (grain communal, redondant). | OLD, BDTOPO | Proxy (exposition seulement, pas le respect) ; **fusionné dans P4.1** | Zone OLD, état 2026 | Même géométrie que l'interface forêt-habitat : la variable est calculée une seule fois, en P4.1 (`nb_batiments_interface`). | Résultats des contrôles OLD (communes, DDTM 33). |
| P4.8 | Mesures de restriction en vigueur | Règlement interdépartemental et arrêté permanent de Gironde (**DOC**) : règles d'accès aux massifs et d'emploi du feu, liées au niveau de danger. Reconstitution : règles appliquées à **MDF** `niveau_j1`. | DOC, MDF | Proxy | Département × jour, 2024 à 2026 | Chaque carreau hérite de la restriction théorique du jour. | Historique des arrêtés préfectoraux temporaires de restriction (préfecture de la Gironde). |
| P5.2 | Disponibilité réelle des personnels et des engins | **SNSDIS** : effectifs (sapeurs-pompiers professionnels et volontaires) et engins du SDIS 33, par an. **ISDIS** : `Total interventions`, `Secours à personne` (charge concurrente). | SNSDIS, ISDIS | Proxy | SDIS × année | Aucune déclinaison journalière possible. | Disponibilité par centre et par jour ou par heure, sur au moins 5 ans. |
| P5.4 | Réseau d'accès et de défense : pistes DFCI, points d'eau | **OSM** : `highway=track`, tags DFCI éventuels, `emergency=fire_hydrant`, `emergency=water_tank`, `emergency=suction_point`. **BDTOPO** : `TRONCON_DE_ROUTE` avec ses attributs DFCI (`piste_dfci`, `gabarit_dfci`, `categorie_dfci`, `vitesse_moyenne_dfci`, `impasse_dfci`, `aire_de_retournement_dfci`…), ou à défaut `nature` = « Route empierrée » ou « Chemin » ; `RESERVOIR`, `PLAN_D_EAU`. **DFCI** : carroyage de référence. | BDTOPO, OSM, DFCI | Proxy en Gironde (91 tronçons DFCI sur ≈ 382 000) ; Directe dans les Landes et le Lot-et-Garonne (attributs DFCI renseignés) | Tronçon ou point, état actuel | Par carreau : densité de pistes (km/km²), nombre de points d'eau, distance au point d'eau le plus proche. | Atlas DFCI de Gironde (pistes classées, points d'eau, gabarits), absent de la BD TOPO alors que les Landes y sont renseignées : DFCI Aquitaine ou SDIS 33. Attention à l'asymétrie entre départements dans les comparaisons. |
| P5.5 | Enveloppe budgétaire du dispositif renforcé | **SNSDIS** : budget du SDIS 33 (fonctionnement, investissement, coût par habitant). **BALANCES** : comptes de charges du SDIS 33 par exercice. | SNSDIS, BALANCES (HD) | Proxy | SDIS × année | Table « saison » : budget global, sans part propre au dispositif. | Enveloppe 2027 et dépenses réelles des saisons passées pour le dispositif renforcé. |

#### 2.6.3. Composantes proxy d'indicateurs restés en 2.1 à 2.5

Ces indicateurs sont couverts directement pour l'essentiel, mais une partie de la donnée ne l'est que par un proxy.

| ID | Composante en proxy | Sources du proxy | Limite | À demander |
| -- | ------------------- | ---------------- | ------ | ---------- |
| P3.1 | Niveau de danger avant 2024 (hors archives Météo des forêts) | SIM2 (IFM calculé à 8 km, `SWI`) ; EWDS (FWI et composantes) en contrôle | IFM approché (valeurs journalières), sans l'expertise humaine ni les relevés de végétation de l'ONF qui fondent le niveau MDF ; correspondance IFM → niveau à caler sur toute la France (≈ 35 000 jours-départements en 2024 à 2026, dont 129 au niveau 4) | Archive Météo des forêts 2023 (Météo-France) |
| P4.5 | Trafic sur les infrastructures | TMJA (`TMJA`, `ratio_PL`) | Réseau national seulement, moyenne annuelle ; comptages départementaux non publiés en open data | Comptages départementaux (Département de la Gironde) et ferroviaires |
| P5.1 | Engins feux de forêt, postes de guet et caméras | OSM (`man_made=tower`, `tower:type=observation`, `man_made=surveillance`), SNSDIS (nombre d'engins) | Postes de guet incomplets dans OSM ; engins seulement comptés, sans localisation | Liste des engins par centre, vigies et caméras (SDIS 33) |

#### 2.6.4. Proxys sélectionnés

Ce sont les proxys à intégrer dès maintenant dans la base. Ils ont été retenus selon trois critères :
- ils distinguent les zones entre elles (grain plus fin que le département) ou allongent l'historique ;
- ils servent directement au calcul du seuil, des fausses alertes ou du coût d'un déclenchement ;
- ils sont peu coûteux à produire.

Chaque proxy sélectionné devient une variable de la base, nommée dans la colonne « Variable produite ».

| ID | Proxy retenu | Sources et champs | Pourquoi le garder | Variable produite (grain) | Limite à garder en tête |
| -- | ------------ | ----------------- | ------------------ | ------------------------- | ----------------------- |
| P1.2 | Cause déclarée du feu | BDIFF : `Nature` | Seul moyen public de séparer les feux d'origine naturelle et humaine, et d'expliquer les feux partis par indice bas. | `cause_feu` (feu), `part_feux_humains` (carreau × période) | Beaucoup de causes non renseignées ; pas de degré de certitude. |
| P1.3 | Déclenchements théoriques | MDF : `niveau_j1` ; seuils testés 2 et 3 (le niveau 4 n'a jamais été atteint en Gironde) ; grille de seuils sur l'indice continu (SIM2 + facteurs de zone) ; règles DOC | Indispensable pour compter les fausses alertes et les feux hors dispositif selon chaque seuil testé : c'est le cœur de la problématique. | `declenchement_theorique` (département × jour × seuil MDF ; commune × jour × seuil d'indice) | Simulation : ne remplace pas le registre réel du SDIS 33. Le niveau MDF seul ne permet que 2 seuils et ne distingue aucune zone. |
| P2.3 | Coûts unitaires de référence | SPV : indemnité horaire par grade ; CARBU : prix du gazole | Permet de chiffrer un déclenchement et de vérifier que le seuil reste finançable. | Table de **paramètres** `cout_ressource_etat`, avec scénarios bas, central et haut | Hypothèses, pas données mesurées : à remplacer par les coûts réels du SDIS 33. |
| P2.4 | Doctrine d'engagement | DOC : PDPFCI de Gironde, règlement interdépartemental | Point de départ pour proposer la gradation « niveau × zone → ressource et état ». | Table de référence `niveau_x_ressource` | À valider et à compléter avec le SDIS 33. |
| P2.6 | Part des feux éteints au stade naissant | BDIFF : surface parcourue | Seul indicateur public d'efficacité de l'attaque, comparable d'une saison à l'autre. | `part_feux_moins_1ha` (commune × saison ; 81 % en Gironde sur 2006 à 2025) | Aucune attribution à une ressource. |
| P3.1 | Danger météo avant 2024 | SIM2 : `PRELIQ`, `TSUP_H`, `HU`, `FF`, `SWI`, `SSWI_10J` ; EWDS : FWI en contrôle | Fait passer l'historique de 3 à 20 saisons (et plus), à une maille de 8 km, ce qui permet de caler le seuil sur assez de feux. | `ifm` (maille de 8 km × jour, ramenée au carreau), `swi` (maille × jour) | Ce n'est pas la Météo des forêts : établir une correspondance IFM → niveaux sur 2024 à 2026, calée sur toute la France. |
| P3.4 | Foudre | BDIFF : `Nature` = naturelle ; ERA5 : densité de flashs absente du catalogue (écarté) | Seule cause naturelle de départ, absente de la Météo des forêts, et **première cause connue en été** en Gironde et dans les Landes. | `nb_feux_naturels` (commune × période ; en Gironde, 447 feux naturels de juin à septembre sur 2006 à 2025, soit 19 % des feux et la moitié des causes connues ; 37 % des feux d'été dans les Landes) ; aucune variable de densité de foudre publique | ERA5 est modélisé ; BLITZ est exclu par ses conditions d'usage. |
| P4.2 | Population résidente et touristique | FILO : `Ind` ; TOUR : chambres, emplacements, lits ; RP : résidences secondaires | Principal facteur humain qui varie d'une zone à l'autre, en particulier sur le littoral. | `pop_residente`, `capacite_touristique` (carreau), `pop_estivale_estimee` (carreau × mois) | Pas de donnée journalière ; taux d'occupation supposé. |
| P4.3 | Points d'entrée du public en forêt | OSM : `amenity=parking`, `highway=path`, `natural=beach`, `tourism=camp_site`, `tourism=picnic_site` | Mesure l'exposition directe des massifs aux visiteurs, au grain du carreau, sans coût. | `nb_parkings_foret`, `km_sentiers`, `presence_plage_camping` (carreau) | Indique un potentiel de fréquentation, pas la fréquentation réelle ; complétude d'OSM variable. |
| P4.5 | Trafic des axes en forêt | TMJA : `TMJA`, `ratio_PL` | Pondère le linéaire de routes par leur fréquentation : beaucoup de départs ont lieu en bord de voie. | `trafic_pondere` (carreau) | Apport faible : réseau national seulement, surtout autoroutier (axes clôturés) ; les routes départementales forestières restent sans trafic. Les comptages du réseau départemental ne sont pas publiés en open data : à demander au Département de la Gironde, qui exploite des stations de comptage permanentes. |
| P5.4 | Pistes et points d'eau | OSM : `highway=track`, `emergency=fire_hydrant`, `emergency=water_tank`, `emergency=suction_point` ; BDTOPO : `RESERVOIR` | Mesure la difficulté d'attaque d'une zone, au grain du carreau. | `densite_pistes`, `densite_pistes_dfci` (40, 47), `dist_point_eau` (carreau) | En Gironde, pistes DFCI non distinguées des autres chemins (attributs DFCI vides dans la BD TOPO) ; points d'eau incomplets. |
| P5.5 | Budget global du SDIS 33 | SNSDIS : budget de fonctionnement | Ordre de grandeur pour borner le nombre de déclenchements finançables. | `budget_sdis` (année), utilisé comme **paramètre** | Budget global : aucune part propre au dispositif renforcé. |

**Partie 2 (efficience)** : avec des données publiques seulement, le coût ne peut être qu'un **paramètre de scénario** (coût d'une journée de déclenchement, testé en sensibilité). La problématique se traite alors ainsi : « quel seuil minimise les fausses alertes sous une contrainte de détection des feux, pour un coût journalier donné ? ».

**Proxys écartés**

| ID | Proxy écarté | Raison |
| -- | ------------ | ------ |
| P2.1 | Catalogue des ressources tiré de DOC, OSM et PYRO | Trop incomplet pour être utile : à demander directement au SDIS 33. |
| P2.2 | Vocabulaire des états de mobilisation tiré de DOC | Ne donne ni délais ni durées : à demander au SDIS 33. |
| P4.4 | Déplacements estivaux par TMJA | Doublon de P4.5 (mêmes données, réseau national et moyenne annuelle). |
| P4.6 | Activités à risque par RPG, S1 ou SUFOSAT | Aucune date de chantier ni de moisson ; S1 demande un traitement d'images lourd. **Décision prise sur l'export BDIFF** : les feux « Involontaire (travaux) » ne représentent que 3,4 % des feux girondins de juin à septembre (9 % des causes connues), sous le seuil d'environ 15 % fixé pour réintégrer le RPG. P4.6 reste écarté. |
| P4.7 | Exposition aux obligations de débroussaillement (OLD, GASPAR) | Même géométrie que l'interface forêt-habitat (massifs + 200 m) : fusionné dans P4.1 pour éviter la colinéarité. GASPAR est retiré (grain communal, redondant). |
| P4.8 | Restrictions reconstituées à partir de MDF | Fonction directe du niveau MDF : variable redondante avec P3.1. |
| P5.1 | Engins et guet à partir d'OSM et de SNSDIS | Le proxy apporte peu ; garder seulement les casernes (BD TOPO), qui sont en couverture directe. |
| P5.2 | Disponibilité à partir de SNSDIS et ISDIS | Grain annuel, sans lien avec la décision quotidienne. |
| P5.6 | Chronologie des interventions à partir de BDIFF et ISDIS | Seule l'heure d'alerte est connue : impossible de mesurer l'effet du renforcement sur l'attaque. |
| P2.6 (partie) | Délai entre la détection FIRMS et l'alerte BDIFF | Deux passages satellite par jour, petits feux invisibles : délai sans signification. |

---

## 3. Table de liaison indicateur × source (format long)

Une ligne par couple indicateur × source. C'est la table à charger telle quelle dans le tableur de visualisation : elle servira ensuite de base aux associations de l'UML.

**Rôle** : P = source principale ; C = complément ; X = proxy.

**Statut** : retenu = à charger dans la base ; écarté = gardé pour la traçabilité, non chargé ; conditionnel = chargé seulement si une condition est remplie (agrégation préalable pour LIDAR) ; à vérifier = existence ou accès non confirmé. Pour la visualisation, filtrer sur `Statut` ≠ écarté.

| ID | Source | Rôle | Champs utilisés | Statut |
| -- | ------ | ---- | --------------- | ------ |
| P1.1 | BDIFF | P | Code INSEE, Date de première alerte, Surface parcourue (m2) et surfaces par type | retenu |
| P1.1 | FIRMS | C | latitude, longitude, acq_date, acq_time, confidence, frp | retenu |
| P1.1 | EFFIS | C | contours des surfaces brûlées, dates | retenu |
| P1.1 | BDFORET | C | polygones de forêt (répartition commune → carreau) | retenu |
| P1.2 | BDIFF | X | Nature ; degré de connaissance (à vérifier dans l'export) | retenu |
| P1.3 | MDF | X | num_dep, date, niveau_j1 (seuils 2 et 3) | retenu |
| P1.3 | SIM2 | X | IFM calculé (grille de seuils sur l'indice continu) | retenu |
| P1.3 | DOC | X | seuil de déclenchement prévu | retenu |
| P2.1 | DOC | X | types de moyens | écarté |
| P2.1 | OSM | X | man_made=tower, tower:type=observation | écarté |
| P2.1 | PYRO | X | caméras (exemple de ressource) | écarté |
| P2.1 | SNSDIS | X | nombre d'engins | écarté |
| P2.2 | DOC | X | vocabulaire des états | écarté |
| P2.3 | SPV | X | indemnité horaire par grade | retenu |
| P2.3 | CARBU | X | prix du gazole | retenu |
| P2.3 | SNSDIS | X | dépenses de personnel | retenu |
| P2.3 | BALANCES | X | comptes de charges | retenu |
| P2.4 | DOC | X | PDPFCI, règlement interdépartemental | retenu |
| P2.6 | BDIFF | X | surface parcourue → part des feux sous 1 ha | retenu |
| P2.6 | FIRMS | C | acq_date, acq_time | écarté |
| P3.1 | MDF | P | date, num_dep, niveau_j1, niveau_j2 | retenu |
| P3.1 | SIM2 | X | précipitations, température, humidité, vent, SWI (noms à vérifier) → IFM | retenu |
| P3.1 | EWDS | X | fwinx, ffmcode, dufmcode, drtcode, infsinx, fbupinx (contrôle) | retenu |
| P3.1 | EFFIS | X | classes de danger | écarté |
| P3.2 | BDFORET | P | CODE_TFV, TFV, TFV_G11, ESSENCE | retenu |
| P3.2 | EFFIS | C | surfaces brûlées datées (masque du combustible) | retenu |
| P3.2 | OCSGE | C | code_cs, code_us | retenu |
| P3.2 | CLC | C | code_18 | écarté |
| P3.2 | FORPUB | C | forêts publiques | retenu |
| P3.2 | LIDAR | C | MNS (hauteur de végétation) | conditionnel |
| P3.2 | BDALTI | C | MNT (hauteur de végétation) | retenu |
| P3.2 | S1 | C | changements radar (coupes) | écarté |
| P3.2 | SUFOSAT | C | alertes de coupe | écarté |
| P3.3 | BDALTI | P | altitude → pente, exposition | retenu |
| P3.3 | LIDAR | C | MNS | conditionnel |
| P3.4 | ERA5 | X | densité de flashs de foudre (absente du catalogue) | écarté |
| P3.4 | BDIFF | X | Nature = naturelle | retenu |
| P3.4 | BLITZ | X | impacts (point, heure) | écarté |
| P4.1 | BDTOPO | P | BATIMENT (géométrie, nature, usage_1) | retenu |
| P4.1 | BDFORET | P | polygones de forêt | retenu |
| P4.1 | OLD | C | zonage informatif (massifs + 200 m) | retenu |
| P4.1 | ARTIF | C | surface artificialisée par période | retenu |
| P4.1 | OCSGE | C | deux millésimes | retenu |
| P4.2 | FILO | X | Ind | retenu |
| P4.2 | TOUR | X | chambres, emplacements, lits | retenu |
| P4.2 | RP | X | résidences secondaires | retenu |
| P4.2 | FEST | C | période de déroulement, code INSEE | écarté |
| P4.3 | OSM | X | parking, path, track, beach, camp_site, picnic_site | retenu |
| P4.3 | FORPUB | X | forêts publiques | retenu |
| P4.3 | FEST | C | festivals | écarté |
| P4.4 | TMJA | X | route, TMJA, ratio_PL, anneeMesureTrafic, coordonnées | écarté |
| P4.5 | BDTOPO | P | TRONCON_DE_ROUTE, TRONCON_DE_VOIE_FERREE, LIGNE_ELECTRIQUE | retenu |
| P4.5 | R500 | C | tronçons principaux | écarté |
| P4.5 | OSM | C | highway, railway, power=line | retenu |
| P4.5 | TMJA | C | TMJA | retenu |
| P4.6 | RPG | X | CODE_CULTU, CODE_GROUP | écarté |
| P4.6 | S1 | X | changements radar (coupes) | écarté |
| P4.6 | SUFOSAT | X | alertes de coupe | écarté |
| P4.7 | OLD | X | zones soumises | écarté |
| P4.7 | GASPAR | C | cod_commune, lib_risque_long | écarté |
| P4.7 | BDTOPO | C | BATIMENT | écarté |
| P4.8 | DOC | X | règles liées au niveau de danger | écarté |
| P4.8 | MDF | X | niveau_j1 | écarté |
| P4.9 | BDIFF | P | Nature = malveillance, code INSEE, date (saisons antérieures) | retenu |
| P5.1 | BDTOPO | P | ZONE_D_ACTIVITE_OU_D_INTERET (nature = Caserne de pompiers) | retenu |
| P5.1 | OSM | C | amenity=fire_station, man_made=tower | retenu |
| P5.1 | PRS | C | points de rencontre des secours | retenu |
| P5.1 | SNSDIS | X | nombre de centres et d'engins | retenu |
| P5.2 | SNSDIS | X | effectifs, engins | écarté |
| P5.2 | ISDIS | X | Total interventions, Secours à personne | écarté |
| P5.3 | BDTOPO | P | TRONCON_DE_ROUTE (nature, vitesse_moyenne_vl, acces_vehicule_leger) | retenu |
| P5.3 | R500 | C | graphe routier | écarté |
| P5.3 | OSM | C | graphe routier | retenu |
| P5.3 | DFCI | P | centroïdes des carreaux | retenu |
| P5.4 | OSM | X | highway=track, emergency=* | retenu |
| P5.4 | BDTOPO | P | TRONCON_DE_ROUTE (piste_dfci, gabarit_dfci, categorie_dfci… ; vides en Gironde), RESERVOIR, PLAN_D_EAU | retenu |
| P5.4 | DFCI | C | carroyage | retenu |
| P5.5 | SNSDIS | X | budget du SDIS 33 | retenu |
| P5.5 | BALANCES | X | comptes de charges | retenu |
| P5.6 | BDIFF | X | date d'alerte, surface | écarté |
| P5.6 | ISDIS | X | Feux de végétations | écarté |

**Indicateurs sans aucune source publique** : P2.5 (journal des patrouilles et du guet). P2.2 n'a qu'un vocabulaire documentaire.

---

## 4. Contrôle source → indicateurs

Chaque source du catalogue doit servir au moins un indicateur ou une jointure.

| Source | Indicateurs servis | Verdict |
| ------ | ------------------ | ------- |
| BDIFF | P1.1, P1.2, P2.6, P3.4, P4.9 | Prioritaire : seule base historique des feux (feux de forêt seulement, localisés à la commune) ; export enregistré dans `data/raw/bdiff/` |
| MDF | P1.3, P3.1 | Prioritaire : niveau officiel, mais 3 saisons et aucun niveau 4 en Gironde |
| SIM2 (ex-CLIM) | P1.3, P3.1 | Prioritaire : indice continu à 8 km depuis 1958 |
| BDFORET | P1.1, P3.2, P4.1 | Prioritaire, à masquer par les surfaces brûlées |
| BDTOPO | P4.1, P4.5, P5.1, P5.3, P5.4 | Prioritaire (attributs vérifiés ; attributs DFCI vides en Gironde) |
| DFCI | P5.3, P5.4 et toutes les agrégations | Prioritaire : référentiel de zone |
| ADMIN, COG (HD) | Toutes les jointures communales | Prioritaire : référentiel communes et départements, avec table de passage des communes fusionnées |
| EFFIS | P1.1, P3.2 | À garder : grands feux et masque du combustible brûlé |
| EWDS | P3.1 | À garder en contrôle de SIM2 |
| FIRMS | P1.1 | À garder pour les grands feux seulement |
| BDALTI (HD) | P3.2, P3.3 | À garder (coût faible, poids attendu faible) |
| OSM | P4.3, P4.5, P5.1, P5.3, P5.4 | À garder, en filtrant les tags utiles |
| OCSGE | P3.2, P4.1 | À garder (millésimes de la Gironde à vérifier) |
| OLD | P4.1 | À garder, comme tampon de l'interface forêt-habitat |
| TMJA | P4.5 | À garder, apport faible (réseau national) |
| FILO, TOUR, RP (HD) | P4.2 | À garder : seules sources sur la population |
| DOC | P1.3, P2.4 | Documentaire : règles à saisir à la main |
| SNSDIS | P5.5 (et P2.1, P5.1, P5.2 écartés) | Optionnel : paramètre budgétaire |
| BALANCES, SPV, CARBU (HD) | P2.3, P5.5 | Optionnel : hypothèses de coût (paramètres) |
| RPG | P4.6 (écarté) | Écarté : les causes « travaux » ne font que 3,4 % des feux d'été en Gironde |
| LIDAR | P3.2, P3.3 | Conditionnel : seulement sous forme agrégée (volume) |
| ARTIF | P4.1 | Optionnel |
| FORPUB | P3.2, P4.3 | Optionnel |
| PRS | P5.1 | Optionnel |
| ISDIS | P5.2, P5.6 (écartés) | Optionnel : grain département × année, sans usage pour un seuil quotidien |
| PYRO | P2.1 (écarté) | Optionnel : illustratif |
| ERA5 | Aucun | Écarté : aucune variable de foudre dans « ERA5 single levels » |
| SUFOSAT (HD) | Aucun | Écarté : aucune diffusion publique des cartes |
| GASPAR | Aucun (P4.7 fusionné) | Écarté : grain communal, redondant avec OLD et la BD Forêt |
| BLITZ (HD) | Aucun | Écarté : conditions d'usage (participants seulement, analyse de risque exclue) |
| R500 | Aucun | Écarté : doublon simplifié de la BD TOPO |
| CLC | Aucun | Écarté : doublon grossier (25 ha) d'OCS GE et de la BD Forêt |
| S1 | Aucun | Écarté : traitement d'images trop lourd |
| FEST | Aucun | Écarté : référence 2019, sans dates exactes |
| AROME, ARPEGE | Aucun indicateur historique | Écarté de la base historique ; utile seulement pour un calcul opérationnel en 2027 (prévision) |
| BDORTHO, EGM, GEOFLA, RESBIO, ONFNAT | Aucun indicateur | Écartés (GEOFLA remplacé par la table de passage du COG) |

---

## 5. Clés de jointure et référentiels communs

| Référentiel | Clé | Source | Usage |
| ----------- | --- | ------ | ----- |
| Zone | Identifiant du carreau DFCI (6 caractères) | DFCI | Grain des facteurs (dimension `carreau`) et des variables dynamiques par carreau |
| Commune | Code INSEE ramené au millésime de référence par la table de passage du COG | ADMIN, COG | **Grain d'évaluation du seuil** (commune × jour) ; rattacher BDIFF, TOUR, RP, ARTIF aux carreaux, par intersection spatiale commune × carreau |
| Maille SIM2 | `LAMBX`, `LAMBY` (Lambert II étendu, hm), à reprojeter en Lambert 93 ; identifiant de maille à créer | SIM2 | Rattacher l'IFM et le `SWI` aux carreaux (maille contenant le centroïde) |
| Département | `num_dep` sur 2 caractères (`33`, `40`, `47`) | ADMIN, MDF | Rattacher MDF, SNSDIS |
| Date | Date calendaire locale (Europe/Paris) | Toutes | MDF : date de validité = date d'émission + 1 jour (J1) ou + 2 jours (J2) ; BDIFF : date de première alerte ; FIRMS : `acq_date` (UTC, à convertir) |
| Saison | Année + période (juin à septembre ; 28 mai au 5 octobre pour la MDF 2026) | Calculé | Agrégations annuelles, budget, performance ; fenêtres strictement antérieures pour les antécédents |
| Niveau de danger | 1 faible, 2 modéré, 3 élevé, 4 très élevé | MDF | Seuils testés : 2 et 3 (niveau 4 jamais atteint en 33, 40 et 47) |
| Cause | Nomenclature `Nature` de BDIFF | BDIFF | Séparer facteurs naturels et humains |
| Type de ressource et état | Codes internes à créer | DOC, puis SDIS 33 | Partie 2 |

**Passage commune → carreau** : un feu BDIFF est localisé à la commune. La répartition sur les carreaux de la commune au prorata de leur surface boisée (BDFORET) produit des fractions de feu : elle sert seulement de carte de densité. **Les feux et les fausses alertes se comptent à la commune × jour** ; les facteurs calculés au carreau y sont agrégés (moyenne pondérée par la surface boisée). Les grands feux détectés par FIRMS ou EFFIS sont appariés aux fiches BDIFF par une règle explicite (commune + 2 km, écart ≤ 24 h).

**Passage département → carreau** : MDF et SNSDIS donnent une valeur par département, que chaque carreau du département reçoit telle quelle. La différence entre zones vient donc des autres facteurs (parties 3 et 4) et de l'indice continu SIM2.

**Rareté de l'événement** : en Gironde, environ 116 feux de forêt par saison (juin à septembre) pour environ 535 communes × 122 jours ≈ 65 000 communes-jours, soit un taux d'environ 0,2 % (et d'environ 0,03 % au carreau-jour). Les métriques doivent être adaptées à ce déséquilibre.

**Volume et schéma** : environ 6 300 carreaux (33, 40, 47) × 122 jours × 20 saisons ≈ 15 millions de lignes. C'est faisable en Parquet ou DuckDB avec un schéma en étoile : une table de faits `carreau_jour` limitée aux variables dynamiques (météo, MDF, déclenchement), des dimensions `carreau`, `commune`, `departement` et `jour` pour les variables statiques, et une table d'évaluation `commune_jour` (feux, déclenchements, fausses alertes).

**Millésimes des couches statiques** : BD TOPO, OSM et OLD (état 2026) et la BD Forêt (antérieure à 2022) sont appliquées à 20 ans de feux. Il faut documenter le millésime de chaque couche, masquer le combustible brûlé (EFFIS) et prendre le millésime FILO le plus proche de la saison.

---

## 6. Données à demander au SDIS 33 et aux partenaires

Ces données ne sont **pas intégrées à la base** pour l'instant : elles sont classées « écarté » (hors modèle) tant qu'elles ne sont pas fournies.

| Indicateur | Donnée à demander | Interlocuteur pressenti | Statut |
| ---------- | ----------------- | ----------------------- | ------ |
| P1.1 | **Priorité 1** : interventions « feux de forêt » géolocalisées (carreau DFCI ou coordonnées), avec l'heure d'éclosion et d'alerte. C'est la donnée qui permet d'évaluer le seuil au grain carreau. | SDIS 33 (système de gestion opérationnelle) | écarté |
| P1.2 | Causes établies et degré de certitude (le degré de connaissance de la BDIFF interne, s'il n'est pas dans l'export public) | Cellules RCCI, gendarmerie, DFCI, gestionnaires de la BDIFF | écarté |
| P1.3 | Registre des déclenchements du dispositif renforcé, et seuil actuellement appliqué | SDIS 33 | écarté |
| P2.1, P2.2 | Catalogue des ressources et états de mobilisation 2027 | SDIS 33 | écarté |
| P2.3 | Coûts unitaires par ressource et par état | SDIS 33 (service financier) | écarté |
| P2.4 | Ordre d'opérations feux de forêt et plan de prépositionnement | SDIS 33 | écarté |
| P2.5 | Journal des patrouilles et du guet | SDIS 33, DFCI | écarté |
| P2.6 | Bilan de détection par ressource | SDIS 33 | écarté |
| P3.1 | Archive Météo des forêts 2023 | Météo-France | écarté |
| P3.4 | **Priorité 2** : impacts de foudre géolocalisés (la foudre est la première cause connue des feux d'été en Gironde) | Météo-France (Météorage) | écarté |
| P4.2, P4.3, P4.4 | Fréquentation et trafic estival journaliers | Département de la Gironde, ONF, offices de tourisme | écarté |
| P4.6 | Chantiers forestiers et agricoles déclarés (faible priorité : 3,4 % des feux d'été) | DDTM 33, CRPF | écarté |
| P4.7 | Résultats des contrôles OLD | Communes, DDTM 33 | écarté |
| P4.8 | Historique des arrêtés de restriction | Préfecture de la Gironde | écarté |
| P5.1, P5.2 | Engins feux de forêt par centre ; disponibilité journalière | SDIS 33 | écarté |
| P5.4 | Atlas DFCI de Gironde (pistes, points d'eau), absent de la BD TOPO | DFCI Aquitaine, SDIS 33 | écarté |
| P5.5 | Enveloppe budgétaire du dispositif renforcé | SDIS 33 | écarté |
| P5.6 | Chronologie des interventions | SDIS 33 | écarté |
