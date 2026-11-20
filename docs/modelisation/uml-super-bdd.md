# UML de la super BDD : entrepôt feux de forêt SDIS 33

Ce document décrit **comment la base est constituée** : quelles tables elle contient, d'où vient chacune, avec quelles clés, et comment elles se relient. Emprise : Gironde (33), Landes (40) et Lot-et-Garonne (47).

Il s'appuie sur [`indicateurs-x-donnees.md`](../sources/indicateurs-x-donnees.md) (sources et statuts). Les diagrammes sont écrits en Mermaid : ils s'affichent dans GitHub, GitLab, VS Code (aperçu Markdown) ou sur [mermaid.live](https://mermaid.live).

---

## 1. Choix de modélisation

| Choix | Décision | Raison |
| ----- | -------- | ------ |
| Zone de référence | **Carreau DFCI de 2 km** (table `Carreau`) | Carroyage opérationnel des feux de forêt ; les données géographiques y sont agrégées une seule fois. |
| Rattachement des feux | **Commune** (table `Feu`, clé `code_insee`) | La BDIFF localise chaque feu à la commune, sans coordonnées. |
| Lien carreau ↔ commune | Table d'association `CarreauCommune` (surface et surface boisée de l'intersection) | Un carreau couvre plusieurs communes et inversement. |
| Météo | Stockée à sa **maille d'origine** (`MeteoMailleJour` pour SIM2, `EwdsCelluleJour` pour EWDS), reliée au carreau par une clé | Pas de duplication : environ 170 mailles SIM2 de 8 km couvrent la Gironde, contre environ 2 700 carreaux. |
| Météo des forêts | Table `NiveauMDF` au grain **département × date de validité × échéance** | Le niveau est publié par département ; J1 et J2 sont deux lignes. |
| Données qui changent dans le temps | Statiques dans `Carreau` et `Commune` ; datées dans `CarreauSaison`, `CarreauMois` et `CommuneSaison` | Évite de répéter les données statiques chaque jour. |
| Communes fusionnées | Table `PassageCommune` (table de passage du COG INSEE) | Les codes INSEE historiques de la BDIFF sont ramenés à un millésime unique. |
| Données non publiques | **Écartées du modèle** | Les données à demander au SDIS 33 et à Météo-France (interventions géolocalisées, impacts de foudre, disponibilité des moyens…) sont classées « écarté » dans [`indicateurs-x-donnees.md`](../sources/indicateurs-x-donnees.md). |

### Place dans l'architecture Médaillon

| Couche | Contenu | Exemples |
| ------ | ------- | -------- |
| **Bronze** | Fichiers bruts téléchargés, sans modification | `data/raw/bdiff/bdiff_33_40_47_2006_2025.csv`, `mdf_2024..2026.csv.gz`, `QUOT_SIM2_<année>.csv.gz`, couches IGN, fichiers INSEE |
| **Silver** | Une table propre par source, typée, avec des clés harmonisées (code INSEE ramené au COG, `num_dep` sur 2 caractères, dates locales, surfaces en m²) | `Feu`, `DetectionSatellite`, `MeteoMailleJour`, `EwdsCelluleJour`, `NiveauMDF`, `SiteSecours`, `StatistiqueSDIS`, référentiels |
| **Gold** | Tables dérivées, calculées à partir de la couche Silver | `Carreau` (attributs agrégés), `CommuneJour`, `CarreauSaison`, `CarreauMois`, `CommuneSaison`, `TempsAcces` |

---

## 2. Vue d'ensemble

Les classes sont regroupées en quatre paquets. Les attributs sont détaillés dans les diagrammes suivants.

```mermaid
classDiagram
    direction LR
    namespace Referentiels {
        class Departement
        class Commune
        class PassageCommune
        class Carreau
        class CarreauCommune
        class MailleSIM2
        class CelluleEWDS
        class Jour
        class RefCause
    }
    namespace Observations {
        class Feu
        class DetectionSatellite
        class MeteoMailleJour
        class EwdsCelluleJour
        class NiveauMDF
    }
    namespace Derivees {
        class CommuneJour
        class CarreauSaison
        class CarreauMois
        class CommuneSaison
        class TempsAcces
    }
    namespace Moyens {
        class SiteSecours
        class StatistiqueSDIS
        class BaremeSPV
        class PrixCarburant
    }

    Departement "1" --> "*" Commune
    Departement "1" --> "*" Carreau
    Commune "1" --> "*" CarreauCommune
    Carreau "1" --> "*" CarreauCommune
    Carreau "*" --> "1" MailleSIM2
    Carreau "*" --> "1" CelluleEWDS
    Commune "1" --> "*" Feu
    RefCause "1" --> "*" Feu
    Feu "0..1" <-- "*" DetectionSatellite
    MailleSIM2 "1" --> "*" MeteoMailleJour
    CelluleEWDS "1" --> "*" EwdsCelluleJour
    Departement "1" --> "*" NiveauMDF
    Commune "1" --> "*" CommuneJour
    Jour "1" --> "*" CommuneJour
    Carreau "1" --> "*" CarreauSaison
    Carreau "1" --> "*" CarreauMois
    Commune "1" --> "*" CommuneSaison
    Carreau "1" --> "*" TempsAcces
    SiteSecours "1" --> "*" TempsAcces
    Carreau "1" --> "*" SiteSecours
    Departement "1" --> "*" StatistiqueSDIS
```

---

## 3. Référentiels et observations (couche Silver)

```mermaid
classDiagram
    direction TB
    class Departement {
        +num_dep : texte [PK]
        +nom : texte
    }
    class Commune {
        +code_insee : texte [PK]
        +nom : texte
        +num_dep : texte [FK]
        +surface_ha : réel
        +surface_foret_ha : réel
        +geom : polygone
    }
    class PassageCommune {
        +code_insee_historique : texte [PK]
        +annee_cog : entier [PK]
        +code_insee : texte [FK]
    }
    class Carreau {
        +id_carreau : texte [PK]
        +num_dep : texte [FK]
        +id_maille_sim2 : texte [FK]
        +id_cellule_ewds : texte [FK]
        +geom : polygone
        +surface_foret_ha : réel
        +part_tfv_type : réel
        +hauteur_vegetation_moy : réel «conditionnel»
        +pente_moy : réel
        +pente_max : réel
        +part_expo_sud : réel
        +nb_batiments_interface : entier
        +lisiere_habitee_km : réel
        +lineaire_routes_km : réel
        +lineaire_vf_km : réel
        +lineaire_elec_km : réel
        +trafic_pondere : réel
        +pop_residente : entier
        +capacite_touristique : entier
        +nb_parkings_foret : entier
        +km_sentiers : réel
        +presence_plage_camping : booléen
        +densite_pistes : réel
        +densite_pistes_dfci : réel
        +dist_point_eau_m : réel
    }
    class CarreauCommune {
        +id_carreau : texte [PK, FK]
        +code_insee : texte [PK, FK]
        +surface_ha : réel
        +surface_foret_ha : réel
        +poids_foret : réel
    }
    class MailleSIM2 {
        +id_maille : texte [PK]
        +lambx_hm : entier
        +lamby_hm : entier
        +geom : polygone
    }
    class CelluleEWDS {
        +id_cellule : texte [PK]
        +lat : réel
        +lon : réel
    }
    class Jour {
        +date : date [PK]
        +annee : entier
        +mois : entier
        +saison : entier
        +est_saison_feux : booléen
    }
    class RefCause {
        +nature : texte [PK]
        +cause_groupe : texte
    }
    class Feu {
        +id_feu : texte [PK]
        +code_insee : texte [FK]
        +date : date [FK]
        +date_heure_alerte : horodatage
        +surface_m2 : réel
        +surface_foret_m2 : réel
        +surface_autres_m2 : réel
        +precision_surfaces : texte
        +nature : texte [FK]
    }
    class DetectionSatellite {
        +id_detection : texte [PK]
        +source : FIRMS ou EFFIS
        +date : date [FK]
        +geom : point ou polygone
        +frp : réel
        +confiance : texte
        +id_feu : texte [FK, 0..1]
    }
    class MeteoMailleJour {
        +id_maille : texte [PK, FK]
        +date : date [PK, FK]
        +preliq_mm : réel
        +tsup_h : réel
        +hu : réel
        +ff : réel
        +swi : réel
        +sswi_10j : réel
        +ifm : réel «calculé»
    }
    class EwdsCelluleJour {
        +id_cellule : texte [PK, FK]
        +date : date [PK, FK]
        +fwinx : réel
        +ffmcode : réel
        +dufmcode : réel
        +drtcode : réel
        +infsinx : réel
        +fbupinx : réel
    }
    class NiveauMDF {
        +num_dep : texte [PK, FK]
        +date_validite : date [PK, FK]
        +echeance : J1 ou J2 [PK]
        +date_emission : horodatage
        +niveau : entier 1 à 4
    }

    Departement "1" --> "*" Commune : regroupe
    Departement "1" --> "*" Carreau : contient
    PassageCommune "*" --> "1" Commune : ramène au COG
    Commune "1" --> "*" CarreauCommune
    Carreau "1" --> "*" CarreauCommune
    Carreau "*" --> "1" MailleSIM2 : centroïde dans
    Carreau "*" --> "1" CelluleEWDS : centroïde dans
    Commune "1" --> "*" Feu : localise
    Jour "1" --> "*" Feu : date d'alerte
    RefCause "1" --> "*" Feu : cause
    Feu "0..1" <-- "*" DetectionSatellite : appariée à
    MailleSIM2 "1" --> "*" MeteoMailleJour
    Jour "1" --> "*" MeteoMailleJour
    CelluleEWDS "1" --> "*" EwdsCelluleJour
    Jour "1" --> "*" EwdsCelluleJour
    Departement "1" --> "*" NiveauMDF
    Jour "1" --> "*" NiveauMDF : date de validité
```

**Règles d'alimentation**

| Classe | Source (Bronze) | Règle |
| ------ | --------------- | ----- |
| `Feu` | BDIFF | Code INSEE ramené au COG de référence par `PassageCommune` ; surfaces en m² ; heure d'alerte en heure locale. |
| `DetectionSatellite` | FIRMS, EFFIS | `id_feu` renseigné seulement pour les grands feux : même commune (+ 2 km), écart ≤ 24 h. |
| `MeteoMailleJour` | SIM2 | `LAMBX`, `LAMBY` (Lambert II étendu, hm) reprojetés pour créer `id_maille` ; `ifm` calculé à partir de `TSUP_H`, `HU`, `FF` et `PRELIQ` (approximation de l'IFM de midi). |
| `EwdsCelluleJour` | EWDS | Indices canadiens tels que publiés (noms courts NetCDF). |
| `NiveauMDF` | Archives MDF | Séparateur `,` ou `;`, `nom_dep` ou `dep_nom`, `1` ou `01` harmonisés ; `date_validite` = date d'émission + 1 (J1) ou + 2 (J2). |
| `Carreau` | DFCI, BD Forêt, BD TOPO, OSM, FILO, TOUR, RP, TMJA, BD ALTI, OLD | Agrégations spatiales par carreau ; surfaces boisées masquées par les surfaces brûlées EFFIS. |
| `CarreauCommune` | DFCI × ADMIN Express × BD Forêt | Intersection carreau × commune ; `poids_foret` = part de la forêt de la commune située dans le carreau. |
| `PassageCommune` | COG INSEE | Table de passage annuelle des communes (géographies 2003 à 2026). |

---

## 4. Tables dérivées (couche Gold)

```mermaid
classDiagram
    direction LR
    class CommuneJour {
        +code_insee : texte [PK, FK]
        +date : date [PK, FK]
        +nb_feux : entier
        +surface_brulee_m2 : réel
        +nb_feux_naturels : entier
        +niveau_mdf_j1 : entier
        +niveau_mdf_j2 : entier
        +ifm_pondere : réel
        +swi_pondere : réel
    }
    class CarreauSaison {
        +id_carreau : texte [PK, FK]
        +saison : entier [PK]
        +annees_depuis_dernier_feu : entier
        +surface_foret_active_ha : réel
    }
    class CarreauMois {
        +id_carreau : texte [PK, FK]
        +annee : entier [PK]
        +mois : entier [PK]
        +pop_estivale_estimee : réel «estimé»
    }
    class CommuneSaison {
        +code_insee : texte [PK, FK]
        +saison : entier [PK]
        +nb_feux_malveillance_5 : entier
        +nb_feux_malveillance_10 : entier
        +nb_feux_malveillance_20 : entier
        +nb_feux_naturels_anterieurs : entier
        +part_feux_humains : réel
        +part_feux_moins_1ha : réel
    }
    class TempsAcces {
        +id_carreau : texte [PK, FK]
        +id_site : texte [PK, FK]
        +temps_min : réel
    }
    class Commune
    class Carreau
    class Jour
    class SiteSecours

    Commune "1" --> "*" CommuneJour
    Jour "1" --> "*" CommuneJour
    Carreau "1" --> "*" CarreauSaison
    Carreau "1" --> "*" CarreauMois
    Commune "1" --> "*" CommuneSaison
    Carreau "1" --> "*" TempsAcces
    SiteSecours "1" --> "*" TempsAcces
```

**Règles de calcul**

| Attribut | Calcul |
| -------- | ------ |
| `CommuneJour.nb_feux`, `surface_brulee_m2`, `nb_feux_naturels` | Agrégation de `Feu` par commune et date d'alerte. |
| `CommuneJour.niveau_mdf_j1`, `niveau_mdf_j2` | `NiveauMDF` du département de la commune, à la date du jour. |
| `CommuneJour.ifm_pondere`, `swi_pondere` | Moyenne de `MeteoMailleJour` sur les carreaux de la commune, pondérée par `CarreauCommune.poids_foret`. |
| `CarreauSaison.annees_depuis_dernier_feu`, `surface_foret_active_ha` | Surfaces brûlées EFFIS datées, croisées avec la BD Forêt. |
| `CarreauMois.pop_estivale_estimee` | Résidents (FILO) + capacité touristique (TOUR, RP) × taux d'occupation supposé, répartis sur le bâti. |
| `CommuneSaison.*` | Comptages de `Feu` par commune sur les saisons antérieures à `saison` (5, 10 et 20 saisons). |
| `TempsAcces.temps_min` | Temps de trajet sur le graphe routier BD TOPO, du site de secours au centroïde du carreau. |

---

## 5. Moyens de secours (sources publiques)

```mermaid
classDiagram
    direction LR
    class SiteSecours {
        +id_site : texte [PK]
        +type : texte
        +nom : texte
        +id_carreau : texte [FK]
        +geom : point
    }
    class StatistiqueSDIS {
        +num_dep : texte [PK, FK]
        +annee : entier [PK]
        +nb_centres : entier
        +effectif_spp : entier
        +effectif_spv : entier
        +nb_engins : entier
        +budget_fonctionnement : réel
    }
    class BaremeSPV {
        +grade : texte [PK]
        +date_effet : date [PK]
        +indemnite_horaire : réel
    }
    class PrixCarburant {
        +num_dep : texte [PK, FK]
        +date : date [PK]
        +prix_gazole_moyen : réel
    }
    class Departement
    class Carreau

    Carreau "1" --> "*" SiteSecours : héberge
    Departement "1" --> "*" StatistiqueSDIS
    Departement "1" --> "*" PrixCarburant
```

**Sources**

| Classe | Source | Remarque |
| ------ | ------ | -------- |
| `SiteSecours` | BD TOPO (`nature` = « Caserne de pompiers »), OSM, points de rencontre ONF (PRS) | 74 casernes BD TOPO en Gironde. |
| `StatistiqueSDIS` | SNSDIS, balances comptables DGFiP | Grain département × année. |
| `BaremeSPV` | Arrêté des indemnités horaires des sapeurs-pompiers volontaires (Légifrance) | Une ligne par grade et par révision. |
| `PrixCarburant` | Prix des carburants (flux et historiques annuels) | Moyenne journalière du gazole par département. |

---

## 6. Volumes attendus (Gironde, Landes, Lot-et-Garonne)

| Classe | Grain | Ordre de grandeur |
| ------ | ----- | ----------------- |
| `Carreau` | carreau | ≈ 6 300 |
| `Commune` | commune | ≈ 1 200 (≈ 535 en Gironde) |
| `CarreauCommune` | carreau × commune | ≈ 15 000 |
| `Feu` | feu | 5 948 (2006 à 2025) |
| `MeteoMailleJour` | maille × jour | ≈ 400 mailles × 365 j × 20 ans ≈ 3 millions |
| `NiveauMDF` | département × jour × échéance | ≈ 2 200 (3 départements, 2024 à 2026) |
| `CommuneJour` | commune × jour de saison | ≈ 1 200 × 122 × 20 ≈ 3 millions |
| `SiteSecours` | site | quelques centaines |
