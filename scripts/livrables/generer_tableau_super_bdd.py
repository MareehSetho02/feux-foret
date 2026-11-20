"""Génère le tableau de visualisation de la super BDD à partir de « docs/sources/indicateurs-x-donnees.md »."""
import re
import sys

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

SRC, OUT = sys.argv[1], sys.argv[2]
md = open(SRC, encoding="utf-8").read().splitlines()

# ---------------------------------------------------------------- parsing
def clean(t):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    return t.replace("**", "").replace("`", "").strip()

def first_url(t):
    m = re.search(r"\]\((https?://[^)]+)\)", t)
    return m.group(1) if m else None

def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]

def section(start, end):
    i = next(k for k, l in enumerate(md) if l.startswith(start))
    j = next((k for k, l in enumerate(md) if k > i and l.startswith(end)), len(md))
    return md[i:j]

def table_rows(lines, header_start):
    out, on = [], False
    for l in lines:
        if l.startswith(header_start):
            on = True
            continue
        if on:
            if not l.startswith("|"):
                if out:
                    on = False
                continue
            if l.startswith("| --") or l.startswith("| -"):
                continue
            out.append(cells(l))
    return out

# Catalogue
cat = []
for sec in ("### 1.1.", "### 1.2."):
    for r in table_rows(section(sec, "###" if sec == "### 1.1." else "---"), "| Code |"):
        code = clean(r[0]).replace(" (ex-CLIM)", "")
        cat.append(dict(code=code, nom=clean(r[1]), prod=clean(r[2]), lien=first_url(r[3]),
                        lien_txt=clean(r[3]), defi=clean(r[4]), format=clean(r[5]),
                        grain=clean(r[6]), periode=clean(r[7]), cle=clean(r[8])))

# Verdicts §4
verdict = {}
for r in table_rows(section("## 4.", "## 5."), "| Source |"):
    names = re.sub(r"\((HD|ex-CLIM)\)", "", clean(r[0]))
    for n in names.split(","):
        verdict[n.strip()] = (clean(r[2]), clean(r[1]))

# Indicateurs (§2.1 à 2.6.2)
PARTIES = {"1": "1. Départs de feu et déclenchements",
           "2": "2. Ressources et états de mobilisation",
           "3": "3. Facteurs naturels",
           "4": "4. Facteurs humains",
           "5": "5. Moyens et efficience du déploiement"}
ind = {}
for l in section("### 2.1.", "#### 2.6.3."):
    if re.match(r"\| P\d\.\d \|", l):
        r = cells(l)
        if len(r) >= 8 and r[0] not in ind:
            ind[r[0]] = dict(nom=clean(r[1]), couv=clean(r[4]), ecart=clean(r[7]))
ids = sorted(ind, key=lambda x: (int(x[1]), int(x[3])))
assert len(ids) == 28, ids

# Demandes §6
dem_rows = [[clean(c) for c in r] for r in table_rows(section("## 6.", "zzz"), "| Indicateur |")]
demande = {}
for r in dem_rows:
    for i in r[0].split(","):
        demande.setdefault(i.strip(), []).append(r[1])

# Liaison §3
lia = [[clean(c) for c in r] for r in table_rows(section("## 3.", "## 4."), "| ID | Source |")]

# ---------------------------------------------------------------- styles
F = "Arial"
H_FILL = PatternFill("solid", fgColor="1F3864")
H_FONT = Font(name=F, bold=True, color="FFFFFF", size=10)
BODY = Font(name=F, size=10)
BOLD = Font(name=F, size=10, bold=True)
TITLE = Font(name=F, size=14, bold=True, color="1F3864")
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FILLS = {"retenu": "C6EFCE", "écarté": "E7E6E6", "conditionnel": "FFEB9C",
         "paramètre": "DDEBF7", "à demander": "F8CBAD"}

wb = Workbook()

def sheet(title, headers, widths):
    ws = wb.create_sheet(title)
    for j, (h, w) in enumerate(zip(headers, widths), 1):
        c = ws.cell(row=1, column=j, value=h)
        c.font, c.fill, c.alignment, c.border = H_FONT, H_FILL, CENTER, BORDER
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "B2"
    ws.row_dimensions[1].height = 30
    return ws

def put(ws, r, j, v, font=BODY, align=WRAP):
    c = ws.cell(row=r, column=j, value=v)
    c.font, c.alignment, c.border = font, align, BORDER
    return c

def statut_colors(ws, rng):
    first = rng.split(":")[0]
    for k, col in FILLS.items():
        ws.conditional_formatting.add(
            rng, CellIsRule(operator="equal", formula=[f'"{k}"'], fill=PatternFill("solid", fgColor=col)))

# ---------------------------------------------------------------- Lisez-moi
ws = wb.active
ws.title = "Lisez-moi"
ws.column_dimensions["A"].width = 26
ws.column_dimensions["B"].width = 110
lines = [
    ("Super BDD feux de forêt – SDIS 33", None, TITLE),
    ("Problématique", "Quel seuil d'un indice de risque, calculé par zone à partir de facteurs naturels et humains, permettrait au SDIS 33 de déclencher son dispositif renforcé à l'été 2027 de façon efficiente, tout en limitant les fausses alertes ?", None),
    ("Source du classeur", "Généré à partir de « docs/sources/indicateurs-x-donnees.md » (révision du 20/11/2026, après vérifications). En cas d'écart, le document Markdown fait foi.", None),
    ("Grains", "Facteurs au carreau DFCI de 2 km (dimension carreau) ; évaluation du seuil (feux, déclenchements, fausses alertes) à la commune × jour. Emprise : Gironde (33), plus Landes (40) et Lot-et-Garonne (47) pour comparer.", None),
    ("", None, None),
    ("Onglets", None, BOLD),
    ("Synthèse", "Compteurs et graphique : couverture des indicateurs par partie, liaisons par statut, sources par verdict. Tout est calculé par formules.", None),
    ("Indicateurs", "Les 28 données idéales : couverture, nombre de sources retenues (formule), état (direct ou calculé, proxy ou simulé, non alimenté, fusionné) et demande au SDIS 33.", None),
    ("Sources", "Catalogue des sources (défi et HD) avec verdict et nombre d'indicateurs alimentés (formule).", None),
    ("Liaison", "Table de liaison indicateur × source (format long), à filtrer. C'est la table de base des associations de l'UML.", None),
    ("Matrice", "Vue croisée indicateur × source, calculée à partir de l'onglet Liaison : P, C ou X si la liaison est retenue ou conditionnelle, « é » si elle est écartée.", None),
    ("Variables BDD", "Dictionnaire des variables de la super BDD, rangées par classe de l'UML (« docs/modelisation/uml-super-bdd.md »), avec indicateur, source et statut.", None),
    ("Demandes", "Données à demander au SDIS 33 et aux partenaires, classées « écarté » : hors modèle tant qu'elles ne sont pas fournies.", None),
    ("", None, None),
    ("Légende", None, BOLD),
    ("Rôle", "P = source principale ; C = complément ; X = proxy.", None),
    ("Statut", "retenu (vert) = à charger ; conditionnel (jaune) = chargé si une condition est remplie ; écarté (gris) = gardé pour la traçabilité ; paramètre (bleu) = hypothèse saisie à la main ; à demander (orange) = donnée non publique.", None),
    ("Défi", "oui = jeu du défi data.gouv « Prévenir et détecter les feux de forêt » ; HD = hors défi.", None),
    ("Mise à jour", "Modifier la colonne Statut de l'onglet Liaison : la Matrice, les compteurs des onglets Indicateurs et Sources et la Synthèse se recalculent.", None),
]
for i, (a, b, font) in enumerate(lines, 1):
    ca = ws.cell(row=i, column=1, value=a)
    ca.font = font or BOLD
    ca.alignment = WRAP
    if b:
        cb = ws.cell(row=i, column=2, value=b)
        cb.font, cb.alignment = BODY, WRAP

# ---------------------------------------------------------------- Indicateurs
wi = sheet("Indicateurs",
           ["ID", "Partie", "Donnée idéale", "Couverture", "Sources retenues", "Sources écartées",
            "Variables BDD", "État", "Écart à l'idéal", "Demande au SDIS 33 ou aux partenaires"],
           [7, 26, 40, 26, 11, 11, 11, 24, 50, 50])
n_ind = len(ids)
for k, i in enumerate(ids, 2):
    d = ind[i]
    put(wi, k, 1, i, BOLD)
    put(wi, k, 2, PARTIES[i[1]])
    put(wi, k, 3, d["nom"])
    put(wi, k, 4, d["couv"])
    put(wi, k, 5, f'=COUNTIFS(Liaison!$A:$A,$A{k},Liaison!$H:$H,"retenu")', align=CENTER)
    put(wi, k, 6, f'=COUNTIFS(Liaison!$A:$A,$A{k},Liaison!$H:$H,"écarté")', align=CENTER)
    put(wi, k, 7, f'=COUNTIF(\'Variables BDD\'!$G:$G,"*"&$A{k}&"*")', align=CENTER)
    put(wi, k, 8, f'=IF(ISNUMBER(SEARCH("fusionné",D{k})),"fusionné",IF(E{k}=0,"non alimenté",'
                  f'IF(OR(LEFT(D{k},7)="Directe",LEFT(D{k},8)="Calculée"),"direct ou calculé","proxy ou simulé")))')
    put(wi, k, 9, d["ecart"])
    put(wi, k, 10, " ; ".join(demande.get(i, [])) or "—")
last_i = n_ind + 1
wi.auto_filter.ref = f"A1:J{last_i}"
for val, col in (("direct ou calculé", FILLS["retenu"]), ("proxy ou simulé", FILLS["conditionnel"]),
                 ("non alimenté", FILLS["à demander"]), ("fusionné", FILLS["écarté"])):
    wi.conditional_formatting.add(f"H2:H{last_i}", CellIsRule(operator="equal", formula=[f'"{val}"'], fill=PatternFill("solid", fgColor=col)))

# ---------------------------------------------------------------- Sources
wsrc = sheet("Sources",
             ["Code", "Jeu de données", "Producteur", "Défi", "Format", "Grain natif", "Période",
              "Clé de jointure", "Lien", "Verdict", "Indicateurs alimentés (retenus)", "Liaisons conditionnelles", "Liaisons écartées"],
             [11, 45, 22, 6, 22, 35, 30, 28, 30, 45, 13, 13, 11])
for k, s in enumerate(cat, 2):
    put(wsrc, k, 1, s["code"], BOLD)
    put(wsrc, k, 2, s["nom"])
    put(wsrc, k, 3, s["prod"])
    put(wsrc, k, 4, s["defi"], align=CENTER)
    put(wsrc, k, 5, s["format"])
    put(wsrc, k, 6, s["grain"])
    put(wsrc, k, 7, s["periode"])
    put(wsrc, k, 8, s["cle"])
    c = put(wsrc, k, 9, s["lien_txt"])
    if s["lien"]:
        c.hyperlink = s["lien"]
        c.font = Font(name=F, size=10, color="0563C1", underline="single")
    v = verdict.get(s["code"])
    put(wsrc, k, 10, v[0] if v else "—")
    put(wsrc, k, 11, f'=COUNTIFS(Liaison!$D:$D,$A{k},Liaison!$H:$H,"retenu")', align=CENTER)
    put(wsrc, k, 12, f'=COUNTIFS(Liaison!$D:$D,$A{k},Liaison!$H:$H,"conditionnel")', align=CENTER)
    put(wsrc, k, 13, f'=COUNTIFS(Liaison!$D:$D,$A{k},Liaison!$H:$H,"écarté")', align=CENTER)
last_s = len(cat) + 1
wsrc.auto_filter.ref = f"A1:M{last_s}"
for pref, col in (("Prioritaire", FILLS["retenu"]), ("Écarté", FILLS["écarté"]), ("Conditionnel", FILLS["conditionnel"])):
    wsrc.conditional_formatting.add(f"J2:J{last_s}", FormulaRule(formula=[f'LEFT($J2,{len(pref)})="{pref}"'], fill=PatternFill("solid", fgColor=col)))

# ---------------------------------------------------------------- Liaison
wl = sheet("Liaison", ["ID", "Partie", "Donnée idéale", "Source", "Défi", "Rôle", "Champs utilisés", "Statut", "Clé"],
           [7, 8, 40, 11, 7, 6, 60, 13, 16])
for k, r in enumerate(lia, 2):
    i, src, role, champs, statut = r
    put(wl, k, 1, i, BOLD)
    put(wl, k, 2, f'="P"&MID(A{k},2,1)', align=CENTER)
    put(wl, k, 3, f'=IFERROR(INDEX(Indicateurs!$C:$C,MATCH(A{k},Indicateurs!$A:$A,0)),"")')
    put(wl, k, 4, src, BOLD)
    put(wl, k, 5, f'=IFERROR(INDEX(Sources!$D:$D,MATCH(D{k},Sources!$A:$A,0)),"?")', align=CENTER)
    put(wl, k, 6, role, align=CENTER)
    put(wl, k, 7, champs)
    put(wl, k, 8, statut, align=CENTER)
    put(wl, k, 9, f'=A{k}&"|"&D{k}')
last_l = len(lia) + 1
wl.auto_filter.ref = f"A1:I{last_l}"
statut_colors(wl, f"H2:H{last_l}")

# ---------------------------------------------------------------- Matrice
order = [s["code"] for s in cat]
used = []
for r in lia:
    if r[1] not in used:
        used.append(r[1])
cols = [c for c in order if c in used] + [c for c in used if c not in order]
wm = sheet("Matrice", ["ID", "Donnée idéale"] + cols, [7, 38] + [6.5] * len(cols))
wm.row_dimensions[1].height = 70
for j in range(3, 3 + len(cols)):
    wm.cell(row=1, column=j).alignment = Alignment(text_rotation=90, horizontal="center", vertical="bottom")
for k, i in enumerate(ids, 2):
    put(wm, k, 1, i, BOLD)
    put(wm, k, 2, f"=INDEX(Indicateurs!$C:$C,MATCH($A{k},Indicateurs!$A:$A,0))")
    for j, src in enumerate(cols, 3):
        col = get_column_letter(j)
        key = f'$A{k}&"|"&{col}$1'
        f = (f'=IFERROR(IF(INDEX(Liaison!$H$2:$H${last_l},MATCH({key},Liaison!$I$2:$I${last_l},0))="écarté","é",'
             f'INDEX(Liaison!$F$2:$F${last_l},MATCH({key},Liaison!$I$2:$I${last_l},0))),"")')
        put(wm, k, j, f, align=CENTER)
last_m = n_ind + 1
rng = f"C2:{get_column_letter(2 + len(cols))}{last_m}"
for v, col in (("P", "548235"), ("C", "A9D08E"), ("X", "FFD966"), ("é", "E7E6E6")):
    wm.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{v}"'], fill=PatternFill("solid", fgColor=col)))
put(wm, last_m + 2, 1, "Légende", BOLD)
put(wm, last_m + 2, 2, "P = principale ; C = complément ; X = proxy (liaison retenue ou conditionnelle) ; é = liaison écartée ; vide = pas de liaison.")
put(wm, last_m + 3, 2, "Sources retenues par colonne →", BOLD)
for j, src in enumerate(cols, 3):
    col = get_column_letter(j)
    put(wm, last_m + 3, j, f'=COUNTIF({col}2:{col}{last_m},"P")+COUNTIF({col}2:{col}{last_m},"C")+COUNTIF({col}2:{col}{last_m},"X")', BOLD, CENTER)

# ---------------------------------------------------------------- Variables BDD
VARS = [
    # table, type, variable, description, type de donnée, grain, indicateur(s), source(s), statut
    ("feu", "Événement", "id_feu", "Identifiant BDIFF (Année-Numéro)", "texte", "1 feu", "P1.1", "BDIFF", "retenu"),
    ("feu", "Événement", "code_insee", "Commune du feu, ramenée au COG de référence", "texte", "1 feu", "P1.1", "BDIFF, COG", "retenu"),
    ("feu", "Événement", "date_alerte", "Date et heure de première alerte (heure locale)", "date-heure", "1 feu", "P1.1", "BDIFF", "retenu"),
    ("feu", "Événement", "surface_m2", "Surface parcourue totale et par type (forêt, autres…)", "nombre", "1 feu", "P1.1, P2.6", "BDIFF", "retenu"),
    ("feu", "Événement", "nature", "Cause déclarée (5 valeurs + vide)", "texte (réf. cause)", "1 feu", "P1.2, P3.4, P4.9", "BDIFF", "retenu"),
    ("feu", "Événement", "cause_groupe", "Naturelle, humaine ou inconnue", "texte", "1 feu", "P1.2", "BDIFF", "retenu"),
    ("feu", "Événement", "id_detection_satellite", "Appariement FIRMS ou EFFIS pour les grands feux (commune + 2 km, ≤ 24 h)", "texte", "1 feu", "P1.1", "FIRMS, EFFIS", "retenu"),
    ("commune_jour", "Fait (évaluation)", "nb_feux", "Nombre de feux de forêt alertés ce jour", "entier", "commune × jour", "P1.1", "BDIFF", "retenu"),
    ("commune_jour", "Fait (évaluation)", "surface_brulee_m2", "Surface parcourue par les feux du jour", "nombre", "commune × jour", "P1.1", "BDIFF", "retenu"),
    ("commune_jour", "Fait (évaluation)", "indice_risque", "Indice continu agrégé à la commune (IFM + facteurs de zone)", "nombre", "commune × jour", "P1.3, P3.1", "SIM2 + dimensions", "retenu"),
    ("commune_jour", "Fait (évaluation)", "declenchement_theorique", "Déclenchement simulé pour chaque seuil testé", "booléen × seuil", "commune × jour × seuil", "P1.3", "calculé", "retenu"),
    ("commune_jour", "Fait (évaluation)", "fausse_alerte", "Déclenchement sans départ de feu", "booléen × seuil", "commune × jour × seuil", "P1.3", "calculé", "retenu"),
    ("carreau_jour", "Fait", "ifm", "Indice forêt météo approché (TSUP_H, HU, FF, PRELIQ)", "nombre", "carreau × jour", "P3.1", "SIM2", "retenu"),
    ("carreau_jour", "Fait", "swi", "Indice d'humidité des sols (SWI) et SSWI_10J", "nombre", "carreau × jour", "P3.1", "SIM2", "retenu"),
    ("carreau_jour", "Fait", "fwi_ewds", "FWI EWDS (fwinx), en contrôle", "nombre", "carreau × jour", "P3.1", "EWDS", "retenu"),
    ("departement_jour", "Fait", "niveau_mdf_j1", "Niveau Météo des forêts pour le lendemain (1 à 4)", "entier", "département × jour", "P3.1, P1.3", "MDF", "retenu"),
    ("departement_jour", "Fait", "niveau_mdf_j2", "Niveau Météo des forêts pour le surlendemain", "entier", "département × jour", "P3.1", "MDF", "retenu"),
    ("departement_jour", "Fait", "declenchement_mdf", "Déclenchement théorique sur le niveau MDF (seuils 2 et 3), appliqué aux communes du département", "booléen × seuil", "commune × jour × seuil", "P1.3", "MDF, DOC", "retenu"),
    ("carreau", "Dimension", "id_carreau", "Identifiant DFCI à 6 caractères", "texte", "carreau", "P5.3, P5.4", "DFCI", "retenu"),
    ("carreau", "Dimension", "num_dep", "Département du carreau", "texte", "carreau", "—", "ADMIN", "retenu"),
    ("carreau", "Dimension", "id_maille_sim2", "Maille SIM2 contenant le centroïde (LAMBX, LAMBY reprojetés)", "texte", "carreau", "P3.1", "SIM2", "retenu"),
    ("carreau", "Dimension", "surface_foret_ha", "Surface boisée (BD Forêt, après masque des surfaces brûlées)", "nombre", "carreau", "P3.2", "BDFORET, EFFIS", "retenu"),
    ("carreau", "Dimension", "part_tfv_*", "Part de surface par type de formation végétale (pin maritime, feuillus, landes…)", "pourcentage", "carreau", "P3.2", "BDFORET, OCSGE", "retenu"),
    ("carreau", "Dimension", "hauteur_vegetation_moy", "Hauteur moyenne de végétation (MNS − MNT, agrégée)", "nombre", "carreau", "P3.2", "LIDAR, BDALTI", "conditionnel"),
    ("carreau", "Dimension", "pente_moy, pente_max", "Pente moyenne et maximale", "nombre", "carreau", "P3.3", "BDALTI", "retenu"),
    ("carreau", "Dimension", "part_expo_sud", "Part de surface exposée au sud ou au sud-ouest", "pourcentage", "carreau", "P3.3", "BDALTI", "retenu"),
    ("carreau", "Dimension", "nb_batiments_interface", "Bâtiments à moins de 200 m d'un massif (zonage OLD)", "entier", "carreau", "P4.1, P4.7", "BDTOPO, BDFORET, OLD", "retenu"),
    ("carreau", "Dimension", "lisiere_habitee_km", "Longueur de lisière habitée", "nombre", "carreau", "P4.1", "BDTOPO, BDFORET", "retenu"),
    ("carreau", "Dimension", "lineaire_routes_km", "Linéaire de routes en forêt par classe d'importance", "nombre", "carreau", "P4.5", "BDTOPO", "retenu"),
    ("carreau", "Dimension", "lineaire_vf_km, lineaire_elec_km", "Linéaire de voies ferrées et de lignes électriques en forêt", "nombre", "carreau", "P4.5", "BDTOPO", "retenu"),
    ("carreau", "Dimension", "trafic_pondere", "Somme TMJA × longueur des sections (réseau national)", "nombre", "carreau", "P4.5", "TMJA", "retenu"),
    ("carreau", "Dimension", "pop_residente", "Population résidente (carreaux de 200 m)", "entier", "carreau", "P4.2", "FILO", "retenu"),
    ("carreau", "Dimension", "capacite_touristique", "Lits touristiques et résidences secondaires, répartis sur le bâti", "entier", "carreau", "P4.2", "TOUR, RP", "retenu"),
    ("carreau", "Dimension", "nb_parkings_foret, km_sentiers", "Points d'entrée du public en forêt", "nombre", "carreau", "P4.3", "OSM", "retenu"),
    ("carreau", "Dimension", "presence_plage_camping", "Plage, camping ou aire de pique-nique dans le carreau", "booléen", "carreau", "P4.3", "OSM", "retenu"),
    ("carreau", "Dimension", "temps_acces_min", "Temps de trajet depuis la caserne la plus proche", "nombre", "carreau", "P5.3", "BDTOPO, DFCI", "retenu"),
    ("carreau", "Dimension", "densite_pistes, densite_pistes_dfci", "Densité de pistes (DFCI distinguées dans les Landes et le Lot-et-Garonne)", "nombre", "carreau", "P5.4", "BDTOPO, OSM", "retenu"),
    ("carreau", "Dimension", "dist_point_eau", "Distance au point d'eau le plus proche", "nombre", "carreau", "P5.4", "OSM, BDTOPO", "retenu"),
    ("carreau_saison", "Dimension datée", "annees_depuis_dernier_feu", "Années depuis le dernier passage du feu (surfaces brûlées)", "entier", "carreau × saison", "P3.2", "EFFIS", "retenu"),
    ("carreau_mois", "Dimension datée", "pop_estivale_estimee", "Résidents + capacité touristique × taux d'occupation supposé", "nombre", "carreau × mois", "P4.2", "FILO, TOUR, RP", "paramètre"),
    ("commune", "Dimension", "code_insee", "Code INSEE de référence (table de passage COG)", "texte", "commune", "—", "ADMIN, COG", "retenu"),
    ("commune", "Dimension", "surface_foret_ha", "Surface boisée de la commune (pondération carreau → commune)", "nombre", "commune", "P1.1", "BDFORET", "retenu"),
    ("commune_saison", "Dimension datée", "nb_feux_malveillance_5_10_20", "Feux de malveillance sur les saisons strictement antérieures", "entier", "commune × saison", "P4.9", "BDIFF", "retenu"),
    ("commune_saison", "Dimension datée", "nb_feux_naturels", "Feux d'origine naturelle (saisons antérieures)", "entier", "commune × saison", "P3.4", "BDIFF", "retenu"),
    ("commune_saison", "Dimension datée", "part_feux_humains", "Part des feux d'origine humaine parmi les causes connues", "pourcentage", "commune × saison", "P1.2", "BDIFF", "retenu"),
    ("commune_saison", "Dimension datée", "part_feux_moins_1ha", "Part des feux éteints sous 1 ha", "pourcentage", "commune × saison", "P2.6", "BDIFF", "retenu"),
    ("site_secours", "Dimension", "id_site, type, geometrie", "Casernes de pompiers (BD TOPO), points de rencontre", "point", "site", "P5.1", "BDTOPO, PRS", "retenu"),
    ("departement_annee", "Dimension datée", "budget_sdis", "Budget de fonctionnement du SDIS (ordre de grandeur)", "nombre (€)", "département × année", "P5.5", "SNSDIS, BALANCES", "paramètre"),
    ("ref_cout_ressource_etat", "Référence", "cout_unitaire", "Coût horaire ou journalier par type de ressource et état (scénarios bas, central, haut)", "nombre (€)", "ressource × état × scénario", "P2.3", "SPV, CARBU", "paramètre"),
    ("ref_niveau_x_ressource", "Référence", "ressource_prevue", "Gradation niveau de danger × zone → ressource et état", "texte", "niveau × zone", "P2.4", "DOC", "paramètre"),
    ("ref_cause", "Référence", "nature, cause_groupe", "Nomenclature des causes BDIFF", "texte", "cause", "P1.2", "BDIFF", "retenu"),
    ("ref_seuil", "Référence", "seuil, type_indice", "Seuils testés (MDF 2 et 3 ; grille sur l'indice continu)", "nombre", "seuil", "P1.3", "calculé", "retenu"),
    ("(à demander)", "Non public", "registre_declenchements", "Registre réel des déclenchements du dispositif renforcé", "—", "zone × jour", "P1.3", "SDIS 33", "à demander"),
    ("(à demander)", "Non public", "feux_geolocalises", "Interventions feux de forêt et de végétation géolocalisées", "—", "1 feu", "P1.1", "SDIS 33", "à demander"),
    ("(à demander)", "Non public", "impacts_foudre", "Impacts de foudre géolocalisés", "—", "1 impact", "P3.4", "Météo-France (Météorage)", "à demander"),
    ("(à demander)", "Non public", "catalogue_ressources, etats", "Ressources du dispositif renforcé, états de mobilisation, coûts réels", "—", "ressource × état", "P2.1, P2.2, P2.3", "SDIS 33", "à demander"),
    ("(à demander)", "Non public", "disponibilite_moyens", "Disponibilité des personnels et engins par centre", "—", "centre × jour", "P5.2", "SDIS 33", "à demander"),
    ("(à demander)", "Non public", "journal_patrouilles", "Journal d'activité des patrouilles et du guet", "—", "patrouille × heure", "P2.5", "SDIS 33, DFCI", "à demander"),
    ("(à demander)", "Non public", "chronologie_interventions", "Alerte, départ, arrivée, feu fixé, moyens engagés", "—", "1 intervention", "P5.6", "SDIS 33", "à demander"),
]

# Alignement sur les classes de « docs/modelisation/uml-super-bdd.md »
CLASSE = {"feu": "Feu", "commune_jour": "CommuneJour", "carreau": "Carreau", "carreau_saison": "CarreauSaison",
          "carreau_mois": "CarreauMois", "commune": "Commune", "commune_saison": "CommuneSaison",
          "site_secours": "SiteSecours", "departement_annee": "BudgetSDIS", "ref_cout_ressource_etat": "CoutRessourceEtat",
          "ref_niveau_x_ressource": "DoctrineNiveau", "ref_cause": "RefCause", "ref_seuil": "Seuil",
          "departement_jour": "NiveauMDF", "carreau_jour": "MeteoMailleJour"}
PAR_VARIABLE = {"id_detection_satellite": "DetectionSatellite", "fwi_ewds": "EwdsCelluleJour",
                "declenchement_theorique": "DeclenchementSimule", "fausse_alerte": "DeclenchementSimule",
                "declenchement_mdf": "DeclenchementSimule", "temps_acces_min": "TempsAcces",
                "registre_declenchements": "RegistreDeclenchement", "feux_geolocalises": "InterventionSDIS",
                "impacts_foudre": "ImpactFoudre", "catalogue_ressources, etats": "TypeRessource, EtatMobilisation",
                "disponibilite_moyens": "DisponibiliteMoyens", "journal_patrouilles": "(hors modèle)",
                "chronologie_interventions": "InterventionSDIS"}
TYPE_CLASSE = {"CommuneJour": "Fait (Gold)", "DeclenchementSimule": "Fait (Gold)",
               "Feu": "Observation (Silver)", "DetectionSatellite": "Observation (Silver)",
               "MeteoMailleJour": "Observation (Silver)", "EwdsCelluleJour": "Observation (Silver)",
               "NiveauMDF": "Observation (Silver)", "TempsAcces": "Dimension datée",
               "Seuil": "Paramètre de simulation", "CoutRessourceEtat": "Paramètre (partie 2)",
               "DoctrineNiveau": "Paramètre (partie 2)", "BudgetSDIS": "Paramètre (partie 2)"}
ORDRE = ["Fait (Gold)", "Observation (Silver)", "Dimension", "Dimension datée", "Référence",
         "Paramètre de simulation", "Paramètre (partie 2)", "Non public"]
VARS = [(PAR_VARIABLE.get(v[2], CLASSE.get(v[0], v[0])),) + v[1:] for v in VARS]
# Données à demander : hors modèle (UML) et classées « écarté »
VARS = [v[:8] + ("écarté",) if v[8] == "à demander" else v for v in VARS]
VARS = [(v[0], TYPE_CLASSE.get(v[0], v[1])) + v[2:] for v in VARS]
VARS.sort(key=lambda v: (ORDRE.index(v[1]) if v[1] in ORDRE else len(ORDRE), v[0]))

wv = sheet("Variables BDD", ["Classe UML", "Type de table", "Variable", "Description", "Type de donnée", "Grain",
                             "Indicateur(s)", "Source(s)", "Statut"],
           [22, 16, 30, 55, 15, 22, 15, 24, 13])
for k, v in enumerate(VARS, 2):
    for j, x in enumerate(v, 1):
        put(wv, k, j, x, BOLD if j in (1, 3) else BODY, CENTER if j == 9 else WRAP)
last_v = len(VARS) + 1
wv.auto_filter.ref = f"A1:I{last_v}"
statut_colors(wv, f"I2:I{last_v}")

# ---------------------------------------------------------------- Demandes
wd = sheet("Demandes", ["Indicateur(s)", "Donnée à demander", "Interlocuteur pressenti", "Priorité", "Statut"], [16, 80, 40, 10, 12])
for k, r in enumerate(dem_rows, 2):
    put(wd, k, 1, r[0], BOLD)
    put(wd, k, 2, r[1])
    put(wd, k, 3, r[2])
    put(wd, k, 5, r[3] if len(r) > 3 else "", align=CENTER)
    put(wd, k, 4, f'=IF(ISNUMBER(SEARCH("Priorité 1",B{k})),1,IF(ISNUMBER(SEARCH("Priorité 2",B{k})),2,""))', align=CENTER)
wd.auto_filter.ref = f"A1:E{len(dem_rows) + 1}"
statut_colors(wd, f"E2:E{len(dem_rows) + 1}")

# ---------------------------------------------------------------- Synthèse
sy = wb.create_sheet("Synthèse", 1)
sy.column_dimensions["A"].width = 42
for c in "BCDE":
    sy.column_dimensions[c].width = 15
sy["A1"] = "Synthèse de la super BDD"
sy["A1"].font = TITLE

def block(r0, title, headers, rows):
    put(sy, r0, 1, title, H_FONT).fill = H_FILL
    for j, h in enumerate(headers, 2):
        c = put(sy, r0, j, h, H_FONT, CENTER)
        c.fill = H_FILL
    for i, (lab, *fs) in enumerate(rows, r0 + 1):
        put(sy, i, 1, lab)
        for j, f in enumerate(fs, 2):
            put(sy, i, j, f, BODY, CENTER)
    return r0 + 1, r0 + len(rows)

def cnt(n, etat):
    return f'=COUNTIFS(Indicateurs!$B$2:$B${last_i},$A{3 + n},Indicateurs!$H$2:$H${last_i},"{etat}")'

p_first, p_last = block(3, "Indicateurs par partie", ["Total", "Direct ou calculé", "Proxy ou simulé", "Non alimenté", "Fusionné"],
                        [(PARTIES[p],
                          f'=COUNTIF(Indicateurs!$B$2:$B${last_i},$A{3 + n})',
                          cnt(n, "direct ou calculé"), cnt(n, "proxy ou simulé"), cnt(n, "non alimenté"), cnt(n, "fusionné"))
                         for n, p in enumerate("12345", 1)])
sy.column_dimensions["F"].width = 15
tot = p_last + 1
put(sy, tot, 1, "Total", BOLD)
for j, col in enumerate("BCDEF", 2):
    put(sy, tot, j, f"=SUM({col}{p_first}:{col}{p_last})", BOLD, CENTER)

s_first, s_last = block(tot + 2, "Liaisons indicateur × source par statut", ["Nombre", "Part"],
                        [(st, f'=COUNTIF(Liaison!$H$2:$H${last_l},"{st}")', None) for st in ("retenu", "conditionnel", "écarté")])
for r in range(s_first, s_last + 1):
    c = put(sy, r, 3, f"=B{r}/SUM($B${s_first}:$B${s_last})", BODY, CENTER)
    c.number_format = "0.0%"

v_first, v_last = block(s_last + 2, "Sources du catalogue par verdict", ["Nombre"],
                        [(lab, f'=COUNTIF(Sources!$J$2:$J${last_s},"{pat}")') for lab, pat in
                         (("Prioritaire", "Prioritaire*"), ("À garder", "À garder*"), ("Optionnel", "Optionnel*"),
                          ("Conditionnel", "Conditionnel*"), ("Documentaire", "Documentaire*"), ("Écarté", "Écarté*"))])
put(sy, v_last + 1, 1, "Sources sans verdict (à classer)")
put(sy, v_last + 1, 2, f'=COUNTA(Sources!$A$2:$A${last_s})-SUM(B{v_first}:B{v_last})', BODY, CENTER)

b_first, b_last = block(v_last + 3, "Variables de la super BDD par statut", ["Nombre"],
                        [(st, f'=COUNTIF(\'Variables BDD\'!$I$2:$I${last_v},"{st}")') for st in ("retenu", "conditionnel", "paramètre", "écarté")])

ch = BarChart()
ch.type = "bar"
ch.grouping = "stacked"
ch.overlap = 100
ch.title = "Couverture des indicateurs par partie"
ch.add_data(Reference(sy, min_col=3, max_col=6, min_row=3, max_row=p_last), titles_from_data=True)
ch.set_categories(Reference(sy, min_col=1, min_row=p_first, max_row=p_last))
ch.y_axis.title = "Nombre d'indicateurs"
ch.height, ch.width = 9, 24
ch.roundedCorners = False
ch.legend.position = "b"
ch.legend.overlay = False
ch.title.overlay = False
ch.y_axis.title.overlay = False
ch.x_axis.delete = False
ch.y_axis.delete = False
ch.y_axis.majorGridlines = None
from openpyxl.chart.shapes import GraphicalProperties
for s, col in zip(ch.series, ("548235", "FFD966", "F4B183", "BFBFBF")):
    s.graphicalProperties = GraphicalProperties(solidFill=col)
sy.add_chart(ch, "H3")

wb.save(OUT)
print(f"{len(ids)} indicateurs, {len(cat)} sources, {len(lia)} liaisons, {len(cols)} colonnes de matrice, {len(VARS)} variables")
missing = [s for s in used if s not in order]
print("sources de la liaison absentes du catalogue :", missing)
print("sources sans verdict :", [s["code"] for s in cat if s["code"] not in verdict])
