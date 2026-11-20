"""Requêtes sur l'API Météo-France « DonneesPubliquesMeteoForets » (v1).

Doc : https://portail-api.meteofrance.fr/web/fr/api/DonneesPubliquesMeteoForets
Auth : clé d'API (header `apikey`) créée sur le portail, lue dans la variable
d'environnement MF_API_KEY ou dans le fichier .env à la racine du projet.

Usage :
    python3 scripts/meteo_forets_api.py            # tous les endpoints, sortie dans data/raw/
    python3 scripts/meteo_forets_api.py --dep 69   # focus département
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib

import requests

BASE = "https://public-api.meteofrance.fr/public/DPMeteoForets/v1"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw"


def api_key() -> str:
    key = os.environ.get("MF_API_KEY")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("MF_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("MF_API_KEY manquante (variable d'environnement ou fichier .env)")
    return key


def get(session: requests.Session, path: str, params: dict | None = None) -> requests.Response:
    r = session.get(f"{BASE}{path}", params=params, timeout=30)
    print(f"GET {path} {params or ''} -> {r.status_code} {r.headers.get('content-type')} {len(r.content)} o")
    return r


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dep", default="69", help="id département (ex: 69, 2A)")
    args = p.parse_args()

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    out = OUT / stamp
    out.mkdir(parents=True, exist_ok=True)

    s = requests.Session()
    s.headers.update({"apikey": api_key(), "accept": "*/*"})

    calls = [
        ("/carte/encours", None, "tableau-meteo-foret.csv"),
        ("/carte/departement/encours", {"format": "json", "echeance": "J1J2", "id-departement": args.dep}, f"dep{args.dep}_J1J2.json"),
        ("/carte/departement/encours", {"format": "csv", "echeance": "J1J2"}, "tous_dep_J1J2.csv"),
        ("/vignettenationale-J1/encours", None, "carte-meteo-foretJ1.png"),
        ("/vignettenationale-J2/encours", None, "carte-meteo-foretJ2.png"),
        ("/bulletinnational-J1-et-J2/encours", None, "bulletin-J1-J2.png"),
    ]
    log = []
    for path, params, fname in calls:
        r = get(s, path, params)
        entry = {"path": path, "params": params, "status": r.status_code,
                 "content_type": r.headers.get("content-type"), "bytes": len(r.content),
                 "last_modified": r.headers.get("last-modified"), "date": r.headers.get("date")}
        if r.ok:
            (out / fname).write_bytes(r.content)
            entry["file"] = fname
        else:
            entry["body"] = r.text[:500]
        log.append(entry)
    (out / "_requetes.json").write_text(json.dumps(log, ensure_ascii=False, indent=2))
    print(f"Résultats dans {out}")


if __name__ == "__main__":
    main()
