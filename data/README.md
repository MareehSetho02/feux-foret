# Données

Les données brutes sont stockées dans `data/raw/`. Ce dossier **n'est pas versionné** (voir `.gitignore`) : chaque membre le reconstitue à partir des sources ci-dessous. Ce fichier sert de registre de provenance. Le catalogue complet des sources du projet se trouve au § 1 de [`docs/sources/indicateurs-x-donnees.md`](../docs/sources/indicateurs-x-donnees.md).

| Chemin local | Source | Producteur | Obtention | Remarques |
| --- | --- | --- | --- | --- |
| `raw/bdiff/bdiff_33_40_47_2006_2025.csv` | [BDIFF](https://bdiff.agriculture.gouv.fr/incendies) | Ministère de l'Agriculture, IGN | Export CSV du portail, filtré sur les départements 33, 40 et 47 et la période 2006 à 2025 | Séparateur `;`, 3 lignes de métadonnées avant l'en-tête, surfaces en m² |
| `raw/bdiff/bdiff_definitions.pdf` | [BDIFF](https://bdiff.agriculture.gouv.fr/incendies) | Ministère de l'Agriculture, IGN | Téléchargé avec l'export | Définitions des champs |
| `raw/archives/mdf_2024.csv.gz` … `mdf_2026.csv.gz` | [Archives de la Météo des forêts](https://www.data.gouv.fr/datasets/archives-de-la-meteo-des-forets) | Météo-France | Téléchargement manuel sur data.gouv.fr | Une ligne par département, jour d'émission et échéance |
| `raw/archives/presentation_mdf.pdf` | [Archives de la Météo des forêts](https://www.data.gouv.fr/datasets/archives-de-la-meteo-des-forets) | Météo-France | Téléchargement manuel sur data.gouv.fr | Notice des archives |
| `raw/AAAAMMJJ-HHMM/` | [API Météo des forêts](https://portail-api.meteofrance.fr/web/fr/api/DonneesPubliquesMeteoForets) | Météo-France | `python3 scripts/extract/meteo_forets_api.py` | Un dossier par appel ; `_requetes.json` journalise chaque requête. Hors saison (octobre à mai), l'API renvoie 404 |

Les référentiels légers qu'on pourra versionner (par exemple le Code officiel géographique de l'Insee) iront dans `data/reference/`.
