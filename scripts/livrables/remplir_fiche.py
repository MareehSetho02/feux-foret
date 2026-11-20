"""Remplit « Fiche d'identite des donnees.docx » pour la Météo des forêts (Météo-France).

Édite directement le XML du docx (pas de dépendance python-docx).
Usage : python3 scripts/remplir_fiche.py <docx_source> <docx_sortie>
"""
from __future__ import annotations

import re
import sys
import zipfile
from xml.sax.saxutils import escape

HEADER = ("Jeu de données : Météo des forêts – Météo-France (API DPMeteoForets v1 + archives data.gouv)"
          "    Rédigé par : Théo Saminadin    Date : 17/11/2026")

# Tableau 1 : colonne « Valeur / Observations » (une entrée par catégorie)
SYNTHESE = [
    ["API temps réel : émission quotidienne à 17h (heure locale), de juin à septembre (saison 2026 : 28/05 → 05/10), "
     "avec réémission possible en journée. Rétention de 5 jours, sans archive. Hors saison (test du 17/11/2026), tous les endpoints renvoient 404.",
     "Archives data.gouv : 1 CSV par an depuis 2024 (11 520 / 11 520 / 12 576 lignes). Pas de SLA."],
    ["Archives complètes : 96 départements chaque jour, 0 jour manquant, 0 valeur vide sur 2024-2026.",
     "Points de vigilance : le schéma change selon les années (séparateur, nom de colonne, code département « 1 » ou « 01 », heure d'émission), "
     "une seule émission par jour est conservée, et J1 est révisé par rapport au J2 de la veille dans 3 à 12 % des cas."],
    ["Pas de donnée personnelle (niveaux agrégés au département). Licence Ouverte Etalab 2.0 + licence d'utilisation de l'API Météo-France : "
     "citer Météo-France et la date de mise à jour, ne pas altérer les données. Clé API personnelle, à ne pas partager.",
     "Conservation côté source : 5 jours (API), archive annuelle pérenne (data.gouv)."],
    ["Amont : observations et prévisions météo (pluie, humidité, température, vent) → Indice Forêt Météo (IFM) + sécheresse de la végétation "
     "(ONF) → Indice de danger intégré, croisé avec les massifs et interfaces forêt-habitat, puis expertise des prévisionnistes.",
     "Aval : meteofrance.com, appli mobile, médias ; pour nous : historique du Rhône (69) et calibration du seuil du dispositif renforcé."],
    ["Q3 (quel indice et quels niveaux), Q1 (seuil de déclenchement à partir du niveau J1/J2 du 69), Q5 (historique de l'indice depuis 2024).",
     "Après croisement avec l'historique des départs de feu : taux de faux positifs/négatifs (Mariam Q2) et comparaison entre départements (Esli Q1-Q2)."],
]

API = [
    "API Météo des forêts temps réel (DPMeteoForets v1, portail-api.meteofrance.fr)",
    # Fraîcheur
    ["Dernière émission : 05/10/2026 (fin de saison).", "Test du 17/11/2026 : 404 « no matching blob » sur les 6 requêtes (clé valide, hors saison)."],
    ["Quotidienne à 17h (heure locale), de juin à septembre.", "Réémission ponctuelle dans la journée si la situation l'exige."],
    ["Par émission : 96 départements × 2 échéances (J1, J2).", "CSV/JSON de quelques Ko + 3 PNG nationaux.", "Rétention : 5 jours."],
    ["Aucun SLA : disponibilité non garantie (licence §D).", "Quotas par seconde, minute et jour. Accès par clé API."],
    # Qualité
    ["Pas d'archive : seule la dernière émission est disponible.", "Hexagone + Corse uniquement (pas l'outre-mer)."],
    ["Même contenu que les archives.", "Format CSV ou JSON au choix.", "Codes département énumérés sans zéro (1…95, 2A, 2B)."],
    ["Hors saison : 404 ou liste vide (JSON « [] », CSV avec l'en-tête seul)."],
    # Gouvernance
    ["Aucune donnée personnelle (niveaux agrégés au département).", "Sensibilité faible. La clé API est un secret (.env, non versionné)."],
    ["Licence Ouverte Etalab 2.0 + licence d'utilisation de l'API Météo-France."],
    ["Citer Météo-France et la date de mise à jour.", "Ne pas altérer ni dénaturer les données.", "Clé API non partageable, quotas à respecter."],
    ["Source : 5 jours.", "Projet : archiver chaque appel (data/raw/) pour constituer notre propre historique."],
    # Lineage
    ["Observations et prévisions météo (pluie, humidité, température, vent).", "IFM + sécheresse de la végétation (ONF).",
     "Massifs forestiers et interfaces forêt-habitat (ONF).", "Expertise des prévisionnistes."],
    ["Météo-France : IFM + sécheresse → Indice de danger intégré → agrégation au département → 4 niveaux (1 faible … 4 très élevé).",
     "Projet : filtre sur le 69, horodatage de l'appel."],
    ["meteofrance.com, appli mobile, médias.", "Projet : suivi quotidien du niveau J1/J2 du Rhône pour décider du renforcement."],
    # Besoin
    ["Q3 : quel indice et quels niveaux ?", "Q1 : déclencher le dispositif renforcé à partir du niveau J1/J2 du 69 ?"],
]

ARCH = [
    "Archives Météo des forêts (data.gouv.fr, mdf_2024 à mdf_2026.csv.gz)",
    # Fraîcheur
    ["Fichier 2026 mis à jour le 05/10/2026.", "Fichiers 2024 et 2025 republiés en juin 2026."],
    ["data.gouv annonce une mise à jour quotidienne ; en pratique, le fichier de l'année s'enrichit pendant la saison."],
    ["3 fichiers, 5 colonnes.", "2024 : 11 520 lignes (120 j).", "2025 : 11 520 lignes (120 j).", "2026 : 12 576 lignes (131 j).", "≈ 450 Ko/an décompressé."],
    ["Aucun SLA. Fichiers hébergés sur le stockage S3 (OVH) de Météo-France."],
    # Qualité
    ["100 % : 96 départements chaque jour, aucun jour manquant dans la saison.", "Historique disponible seulement depuis 2024."],
    ["Schéma instable : séparateur « , » (2024-25) puis « ; » (2026) ; colonne nom_dep / dep_nom (2025) ; code « 1 » ou « 01 » ; émission à 16:00Z (2024) ou 14:50Z.",
     "Les noms de colonnes de la doc Confluence (Reference_time, dep_code) ne sont pas ceux des fichiers (date, num_dep).",
     "J2 de la veille = J1 du jour : 97 % (2024), 95 % (2025), 88 % (2026).", "Une seule émission conservée par jour."],
    ["Aucune : 0 valeur manquante ou vide sur les 3 ans."],
    # Gouvernance
    ["Aucune donnée personnelle."],
    ["Licence Ouverte v2.0 (Etalab)."],
    ["Citer Météo-France et la date de mise à jour.", "Ne pas altérer les données."],
    ["Archive pérenne, publiée par année depuis 2024.", "Projet : copie locale (data/raw/archives)."],
    # Lineage
    ["Même flux que l'API : l'émission quotidienne de 17h (J1, J2)."],
    ["Météo-France : émission du jour concaténée dans un CSV annuel, compressé en gzip.",
     "Projet : harmoniser séparateur, colonnes et codes ; fusionner 2024-2026 ; filtrer sur le 69."],
    ["Analyse historique ; jointure avec l'historique des départs de feu (SDMIS 69 / BDIFF)."],
    # Besoin
    ["Q5 : historique de l'indice. Rhône, nombre de jours par niveau J1 (1/2/3) : 2024 = 110/10/0 ; 2025 = 91/25/4 ; 2026 = 48/72/11 ; aucun jour au niveau 4.",
     "Q1 : calibrer le seuil.", "Mariam Q2 : faux positifs/négatifs (avec les données feux).", "Esli Q1-Q2 : comparaison entre départements, séries temporelles."],
]


def para(text: str, size: int = 14, bold: bool = False) -> str:
    b = "<w:b/>" if bold else ""
    return (f'<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr>{b}<w:sz w:val="{size}"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def fill_cell(tc: str, lines: list[str] | str, size: int = 14, bold: bool = False) -> str:
    lines = [lines] if isinstance(lines, str) else lines
    body = "".join(para(t, size, bold) for t in lines)
    # Remplace tout le contenu après </w:tcPr> par nos paragraphes
    head, _ = tc.split("</w:tcPr>", 1)
    return f"{head}</w:tcPr>{body}</w:tc>"


def fill_row(tr: str, values: list, size: int = 14) -> str:
    cells = re.findall(r"<w:tc>.*?</w:tc>", tr, re.S)
    assert len(cells) == len(values), (len(cells), len(values))
    out = tr
    for i, (c, v) in enumerate(zip(cells, values)):
        out = out.replace(c, fill_cell(c, v, size, bold=(i == 0)), 1)
    return out


def main(src: str, dst: str) -> None:
    with zipfile.ZipFile(src) as z:
        files = {n: z.read(n) for n in z.namelist()}
    xml = files["word/document.xml"].decode("utf-8")

    xml = re.sub(r"Jeu de données : _+.*?Date : _+/_+/_+", escape(HEADER), xml, count=1)

    tables = re.findall(r"<w:tbl>.*?</w:tbl>", xml, re.S)
    assert len(tables) == 2

    # Tableau 1 : dernière cellule de chaque ligne (hors en-tête)
    t1 = tables[0]
    rows = re.findall(r"<w:tr[ >].*?</w:tr>", t1, re.S)
    new_t1 = t1
    for row, val in zip(rows[1:], SYNTHESE):
        cells = re.findall(r"<w:tc>.*?</w:tc>", row, re.S)
        new_row = row.replace(cells[-1], fill_cell(cells[-1], val, size=16), 1)
        new_t1 = new_t1.replace(row, new_row, 1)

    # Tableau 2 : lignes 3 et 4 (après les 2 lignes d'en-tête)
    t2 = tables[1]
    rows = re.findall(r"<w:tr[ >].*?</w:tr>", t2, re.S)
    new_t2 = t2.replace(rows[2], fill_row(rows[2], API), 1)
    new_t2 = new_t2.replace(rows[3], fill_row(rows[3], ARCH), 1)

    xml = xml.replace(t1, new_t1, 1).replace(t2, new_t2, 1)
    files["word/document.xml"] = xml.encode("utf-8")

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in files.items():
            z.writestr(n, data)
    print(f"Écrit : {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
