"""Download the chosen sources into .cache/.

    python3 pipeline/sources.py [name ...]

fetch.py is reconnaissance — it asks data.govt.nz what exists. This is the
ingest: it pulls the sources that were actually chosen, and Docs/SOURCES.md
records why each one and on what licence.

Everything lands in .cache/, which is gitignored. What gets committed is the
canonical JSON that emit.py builds from it, so the site builds from the
repository alone (HANDOFF §3).

One source is not here and cannot be: Waikato Regional Council's flow API sits
behind Incapsula, which rejects any client that is not a browser. Those four
stations are in emit.py as a dated snapshot with their provenance. See
Docs/SOURCES.md §1.4 — and note that verify.py cross-checks them against REC2's
catchment areas, so the snapshot is guarded rather than merely trusted.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
UA = {"User-Agent": "enviro-analysis/0.1 (personal project)"}

REC2 = "https://services3.arcgis.com/fp1tibNcN9mbExhG/arcgis/rest/services/REC2_Layers/FeatureServer/0/query"
OVERPASS = "https://overpass-api.de/api/interpreter"

# LAWA's Waikato/Northland monitoring file. LAWA serves it from Google Sheets;
# the id is published on https://www.lawa.org.nz/download-data. Pinned here
# rather than scraped so a page redesign cannot silently change what we ingest.
LAWA_SHEET_ID = "1dm6S4SxWJtFtQnrtIkgvUCb6Mefzvf_K"

# REC2 boxes. Split because the network above Taupō needs low stream orders to
# reach Ruapehu, and pulling every order across the whole catchment would be
# tens of thousands of reaches for no gain.
REC2_BOXES = [
    ("waikato", "StreamOrde>=6", "174.4,-39.1,176.6,-37.0"),
    ("upper", "StreamOrde>=4", "175.3,-39.6,176.3,-38.6"),
    ("ruapehu", "1=1", "175.40,-39.45,175.85,-39.05"),
]

OVERPASS_QUERIES = {
    "taupo": """[out:json][timeout:180];
(relation["natural"="water"]["name"~"Taupo|Taupō",i](-39.05,175.65,-38.35,176.20););
out body geom;""",
    "features": """[out:json][timeout:240];
(way["waterway"="dam"](-38.85,175.0,-37.2,176.2);
 node["place"~"^(city|town)$"](-39.35,174.6,-37.2,176.2););
out center tags;""",
}


def _get(url: str, dest: pathlib.Path, data: bytes | None = None, tries: int = 4) -> pathlib.Path:
    """Overpass is a shared free service and answers 504 when it is busy, so a
    single failure means "try later", not "the data is gone"."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers=UA, data=data)
            with urllib.request.urlopen(req, timeout=300) as r:
                dest.write_bytes(r.read())
            break
        except Exception as e:  # noqa: BLE001
            if attempt == tries:
                raise
            wait = 15 * attempt
            print(f"  {type(e).__name__}: {e} — retrying in {wait}s ({attempt}/{tries - 1})")
            time.sleep(wait)
    print(f"  {dest.relative_to(ROOT)}  {dest.stat().st_size:,} bytes")
    return dest


def lawa() -> None:
    _get(f"https://docs.google.com/spreadsheets/d/{LAWA_SHEET_ID}/export?format=xlsx",
         CACHE / "lawa" / "river-wq-ni3.xlsx")


def rec2() -> None:
    fields = "HydroID,nzsegment,LENGTHDOWN,StreamOrde,NextDownID,upElev,downElev,CUM_AREA"
    for name, where, box in REC2_BOXES:
        out, offset = [], 0
        while True:
            q = urllib.parse.urlencode({
                "where": where, "geometry": box, "geometryType": "esriGeometryEnvelope",
                "inSR": "4326", "spatialRel": "esriSpatialRelIntersects", "outFields": fields,
                "returnGeometry": "true", "outSR": "4326",
                "resultRecordCount": 2000, "resultOffset": offset, "f": "json"})
            with urllib.request.urlopen(urllib.request.Request(f"{REC2}?{q}", headers=UA), timeout=300) as r:
                page = json.load(r).get("features", [])
            out += page
            if len(page) < 2000:
                break
            offset += 2000
        dest = CACHE / "rec2" / f"{name}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(out))
        print(f"  {dest.relative_to(ROOT)}  {len(out)} reaches")


def osm() -> None:
    for name, query in OVERPASS_QUERIES.items():
        _get(OVERPASS, CACHE / "osm" / f"{name}.json", data=query.encode())


# ── The journey ──────────────────────────────────────────────────────────────

# The Waikato River as OpenStreetMap maps it. The map tiles the journey is drawn
# on are built from these same ways, so a boat that follows them sits on the
# river the reader sees — REC2's line traces the same river from a different
# survey and drifts off the drawn water by tens of metres at street zoom.
# Fetched from the main OSM API rather than Overpass: one relation is one
# request there, and Overpass answered 504 three times running when this was
# first built.
OSM_RIVER_RELATION = 2751038

# Every settlement within reach of the river that Stats NZ publishes a place
# summary for, by its Stats NZ slug. Which of them count as "on the river" is
# decided in emit.py by distance, not here — this is the list of candidates,
# including the ones the rule turns out to exclude.
SETTLEMENTS = {
    "taupo": "Taupō", "wairakei-village": "Wairākei Village", "atiamuri": "Ātiamuri",
    "whakamaru": "Whakamaru", "mangakino": "Mangakino", "arapuni": "Arapuni",
    "cambridge": "Cambridge", "hamilton": "Hamilton", "horotiu": "Horotiu",
    "te-kowhai": "Te Kōwhai", "ngaruawahia": "Ngāruawāhia", "taupiri": "Taupiri",
    "huntly": "Huntly", "te-kauwhata": "Te Kauwhata", "meremere": "Meremere",
    "pokeno": "Pōkeno", "tuakau": "Tuakau", "port-waikato": "Port Waikato",
}


def osm_river() -> None:
    _get(f"https://api.openstreetmap.org/api/0.6/relation/{OSM_RIVER_RELATION}/full.json",
         CACHE / "osm" / "river.json")


# Above the lake. The journey starts at the river's true head on Ruapehu, and
# from there to Lake Taupō it follows OpenStreetMap's streams — every waterway
# in a box around REC2's upper mainstem, plus the Tongariro River relation in
# full — and journey.py picks the chain of them that runs along REC2's line.
# The box is all streams, not just named ones: the first few kilometres off the
# mountain are mapped as unnamed stream ways.
OSM_TONGARIRO_RELATION = 18122690
UPPER_QUERY = f"""[out:json][timeout:180];
(way["waterway"~"^(river|stream|canal)$"](-39.29,175.56,-38.92,175.85);
 relation({OSM_TONGARIRO_RELATION}); way(r);)->.all;
way.all;
out geom tags;"""


def osm_upper() -> None:
    _get(OVERPASS, CACHE / "osm" / "upper.json", data=UPPER_QUERY.encode())


def statsnz() -> None:
    """Stats NZ estimated resident population, per settlement.

    Read from the place summaries Stats NZ publishes, which are server-rendered
    and carry their figures in the page's own data block. The first `numbers`
    block under the first topic is the place; `vs_numbers` is New Zealand, and
    is skipped. Estimated resident population rather than the census count,
    because it is Stats NZ's own best measure of who usually lives somewhere and
    it is two years more current."""
    import re
    out = {}
    for slug, name in SETTLEMENTS.items():
        url = f"https://tools.summaries.stats.govt.nz/places/UR/{slug}"
        html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode()
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        topics = json.loads(m.group(1))["props"]["pageProps"]["place"] if m else []
        if not topics:
            raise RuntimeError(f"no place data for {slug}")
        erp: dict[str, float] = {}

        def walk(o):
            if isinstance(o, dict):
                for n in o.get("numbers") or []:
                    if n.get("variable1_code") == "ERP" and n.get("variable2_code") is None:
                        erp.setdefault(n["period"], n["value"])
                for k, v in o.items():
                    if k != "vs_numbers":
                        walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(topics[0])
        year = max(erp)
        out[slug] = {"name": name, "code": topics[0].get("classification_code"),
                     "erp": erp[year], "erp_year": year, "url": url}
        print(f"  {name:<18} {erp[year]:>8,.0f}  (ERP {year})")
        time.sleep(0.5)
    dest = CACHE / "statsnz" / "settlements.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1))


def places() -> None:
    """Where each settlement is, from Nominatim — one request a second, as its
    usage policy asks, cached so it is asked once."""
    out = {}
    for slug, name in SETTLEMENTS.items():
        q = urllib.parse.urlencode({"q": f"{name}, Waikato, New Zealand", "format": "jsonv2", "limit": 1})
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            f"https://nominatim.openstreetmap.org/search?{q}", headers=UA), timeout=60))
        if not r:
            raise RuntimeError(f"Nominatim found no {name}")
        out[slug] = {"name": name, "lat": float(r[0]["lat"]), "lon": float(r[0]["lon"]),
                     "osm": f"{r[0]['osm_type']}/{r[0]['osm_id']}"}
        time.sleep(1.1)
    dest = CACHE / "osm" / "places.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"  {dest.relative_to(ROOT)}  {len(out)} places")


SOURCES = {"lawa": lawa, "rec2": rec2, "osm": osm, "river": osm_river, "upper": osm_upper,
           "statsnz": statsnz, "places": places}


def main() -> int:
    wanted = sys.argv[1:] or list(SOURCES)
    for name in wanted:
        fn = SOURCES.get(name)
        if fn is None:
            print(f"  unknown source {name!r} — one of {', '.join(SOURCES)}")
            return 2
        print(f"{name}:")
        try:
            fn()
        except Exception as e:  # noqa: BLE001 — report and continue, as fetch.py does
            print(f"  FAILED: {e}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
