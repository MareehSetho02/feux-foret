# Feux de forêt : entrepôt de données pour le SDIS 33

Projet du bloc « Qualité et modélisation des données » (HETIC, M2). L'objectif est de construire un entrepôt de données sur les feux de forêt pour le SDIS de la Gironde (33), organisé en couches Bronze, Silver et Gold. Il doit aider à fixer le seuil de déclenchement du dispositif renforcé pour l'été 2027. Les Landes (40) et le Lot-et-Garonne (47) servent de points de comparaison au sein du massif landais.

## Structure du dépôt

```
README.md
livrables/            Rendus datés (ajoutés par leurs branches docs/…)
docs/
  cadrage/            Analyse de la commande, questions × données
  sources/            Indicateurs × données (catalogue des sources au § 1), revue critique, fiches d'identité
  modelisation/       UML de la super BDD, règles d'alignement
cours/                Supports et notes de cours (noms d'origine conservés)
data/                 Provenance des données (README) ; raw/ non versionné
scripts/
  extract/            Extraction depuis les API et portails
  transform/          Nettoyage et alignement (à venir)
  livrables/          Génération des tableaux et fiches
.github/              Modèle de pull request
```

## Ordre de lecture

1. [`docs/cadrage/analyse-commande.md`](docs/cadrage/analyse-commande.md) : les questions du SDIS.
2. [`docs/cadrage/questions-x-donnees.md`](docs/cadrage/questions-x-donnees.md) : chaque question reliée aux champs des jeux de données.
3. [`docs/sources/indicateurs-x-donnees.md`](docs/sources/indicateurs-x-donnees.md) : le catalogue des sources et la correspondance entre indicateurs et données publiques.
4. [`docs/sources/revue-indicateurs.md`](docs/sources/revue-indicateurs.md) : la revue critique du document précédent.

## Installation

Python 3.12 ou plus récent.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner MF_API_KEY
```

Le fichier `.env` contient une clé d'API : il ne doit jamais être commité.

## Scripts

| Commande | Rôle |
| --- | --- |
| `python3 scripts/extract/meteo_forets_api.py [--dep 33]` | Interroge l'API Météo des forêts. Les résultats sont écrits dans `data/raw/AAAAMMJJ-HHMM/`. |
| `python3 scripts/livrables/generer_tableau_super_bdd.py docs/sources/indicateurs-x-donnees.md livrables/tableau-super-bdd-sdis33.xlsx` | Génère le classeur de visualisation de la super BDD. |
| `python3 scripts/livrables/remplir_fiche.py <docx_source> <docx_sortie>` | Remplit la fiche d'identité Word pour la Météo des forêts. |

La provenance des fichiers de `data/raw/` est décrite dans [`data/README.md`](data/README.md).

## Conventions

**Fichiers** : noms en minuscules, avec des tirets, sans espaces ni accents. Pour déplacer un fichier, utiliser `git mv` afin de garder son historique. Les supports de `cours/` gardent leur nom d'origine.

**Branches** : `type/sujet-court`, par exemple `docs/uml-super-bdd`. On crée une branche par livrable ou par partie, à partir de `main`. Elle vit peu de temps et elle est supprimée après le merge.

**Commits** : [Conventional Commits](https://www.conventionalcommits.org/fr/), rédigés en français, au format `type(scope): description à l'impératif` (72 caractères au plus). Un commit contient un seul changement logique.
- Types : `docs`, `feat`, `fix`, `data`, `refactor`, `chore`.
- Scopes : `cadrage`, `sources`, `uml`, `alignement`, `extract`, `transform`, `livrables`.

**Pull requests** : vers `main`, avec un titre au format des commits. Chaque PR est relue par un autre membre de l'équipe, puis fusionnée en « Squash and merge ». Le modèle [`.github/pull_request_template.md`](.github/pull_request_template.md) contient la checklist. Après chaque rendu, on pose un tag (par exemple `livrable-2026-11-20`).
