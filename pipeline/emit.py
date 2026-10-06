"""Build the canonical JSON the site draws from.

    python3 pipeline/emit.py

Reads .cache/ (see sources.py) and writes site/data/. Output is canonical —
sorted keys, tight separators — so a rebuild that changes nothing is
byte-identical and `git status` after `make emit` tells you whether a publisher
moved (HANDOFF §3).

What comes out:

  river.json       the spine: one simplified polyline from the headwater on
                   Ruapehu to the sea, plus the lake outline and the coastline
                   box the map needs
  stations.json    every measuring point placed on the spine by distance
                   downstream, with its record
  measures.json    the per-site medians, per indicator, that the site reads
  landmarks.json   dams, towns and DOC places on the same axis
  journey.json     the path the boat follows, who lives along it, and how the
                   water changes reach by reach — see journey.py

Nothing here interpolates. A value exists at a site or it does not, and the gaps
between sites are left as gaps — HANDOFF §4, and the single most likely mistake
this project could make.
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import geo  # noqa: E402
import journey  # noqa: E402
import xlsx  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
DATA = ROOT / "site" / "data"

# Ruapehu's summit, for identifying the headwater reach. The highest reach that
# drains to the Taupō gates starts 1.7 km from here at 2,600 m.
RUAPEHU = (-39.2812, 175.5641)
# The Taupō control gates: where the river leaves the lake, and where the
# monitoring record begins.
TAUPO_GATES = (-38.68106, 176.06993)

# Simplification tolerance for the emitted line. 25 m is well below anything a
# reader can see at the zoom this map uses and takes the spine from 4,567
# vertices to a fraction of that. Stated rather than accidental (HANDOFF §5).
SIMPLIFY_M = 25.0

# The indicators worth placing on a distance axis. pH and ammoniacal nitrogen
# are measured at the same sites and are deliberately not here: both are flat
# from Taupō to Tuakau, so drawing them as a downstream trend would invent a
# story the data does not tell. SPEC §3.2 (3).
INDICATORS = {
    "Total nitrogen": ("total_nitrogen", "mg/L", "down"),
    "Total oxidised nitrogen": ("oxidised_nitrogen", "mg/L", "down"),
    "Total phosphorus": ("total_phosphorus", "mg/L", "down"),
    "Dissolved reactive phosphorus": ("reactive_phosphorus", "mg/L", "down"),
    "E.coli": ("e_coli", "per 100 mL", "down"),
    "Clarity (BDISC)": ("clarity", "m", "up"),
}
# Turbidity is measured at every site but in two units — NTU at the council
# sites and FNU at NIWA's. They are different instruments and not
# interchangeable, so it is excluded rather than quietly mixed. SPEC §3.2 (3).

# Waikato Regional Council flow gauges, read from their Envirohub API on
# 2026-09-18. Recorded here rather than fetched because the API is behind
# Incapsula and refuses non-browser clients (sources.py docstring). These are
# long-record statistics — the shortest record starts in 1975 — so a snapshot is
# the right shape for them. verify.py checks the catchment areas against REC2.
FLOW_ASOF = "2026-09-18"
FLOW = [
    {"station": "Hamilton Traffic Br", "lat": -37.792226, "lon": 175.291189,
     "mean_cumecs": 256.14, "catchment_km2": 8334.00, "record_from": "1975-12-22",
     "highest": [790.72, "1998-07-15"], "lowest": [137.84, "2016-12-28"]},
    {"station": "Ngaruawahia Cableway", "lat": -37.65273083671382, "lon": 175.1459045385919,
     "mean_cumecs": 337.02, "catchment_km2": 11545.63, "record_from": "1957-05-18",
     "highest": [1599.32, "1998-07-13"], "lowest": [136.32, "1961-04-10"]},
    {"station": "Rangiriri Br", "lat": -37.432141, "lon": 175.129277,
     "mean_cumecs": 361.10, "catchment_km2": 12371.93, "record_from": "1965-04-01",
     "highest": [1489.10, "1998-07-16"], "lowest": [126.53, "1973-05-04"]},
    {"station": "Mercer Br", "lat": -37.281276, "lon": 175.0467,
     "mean_cumecs": 400.91, "catchment_km2": 13874.11, "record_from": "1963-06-14",
     "highest": [1534.87, "1998-07-16"], "lowest": [134.04, "2015-04-07"]},
]

# DOC places on or beside the river, with the page each one has. Every URL was
# taken from DOC's own sitemap.xml and checked for a 200 on 2026-09-18 — see
# Docs/SOURCES.md. offset_note says how far from the water it is, because a
# reader should not be sent to a reserve 5 km away without being told.
DOC_PLACES = [
    ("Tongariro National Park", -39.2812, 175.5641,
     "/parks-and-recreation/places-to-go/central-north-island/places/tongariro-national-park/"),
    ("Taupō and the lake", -38.7860, 175.9200,
     "/parks-and-recreation/places-to-go/central-north-island/places/taupo-area/"),
    ("Huka Falls — Te Taheke Hukahuka", -38.6494, 176.0900,
     "/parks-and-recreation/places-to-go/central-north-island/places/taupo-area/things-to-do/huka-falls-lookout-walk/"),
    ("Aratiatia Rapids", -38.6157, 176.1423,
     "/parks-and-recreation/places-to-go/central-north-island/places/taupo-area/things-to-do/aratiatia-rapids-lookout-walk/"),
    ("Hakarimata Scenic Reserve", -37.6600, 175.1300,
     "/parks-and-recreation/places-to-go/waikato/places/hakarimata-scenic-reserve/"),
    ("Whangamarino Wetland", -37.3500, 175.1050,
     "/parks-and-recreation/places-to-go/waikato/places/whangamarino-wetland/"),
]

# The eight dams. Seven are named in OSM; Waipapa is mapped but unnamed, so it
# is identified by position — it sits beside the Waipapa tailrace sampling site.
DAM_NAMES = {"Aratiatia Dam", "Ōhakuri Dam", "Ātiamuri Dam", "Whakamaru Dam",
             "Maraetai Dam", "Arapuni Dam", "Karāpiro Dam"}
WAIPAPA_DAM = (-38.29218, 175.68355)


def canonical(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    print(f"  {path.relative_to(ROOT)}  {path.stat().st_size:,} bytes")


def load_rec2() -> dict:
    by = {}
    for name in ("waikato", "upper", "ruapehu"):
        for f in json.loads((CACHE / "rec2" / f"{name}.json").read_text()):
            by[f["attributes"]["HydroID"]] = f
    return by


def build_spine(by: dict):
    """Ruapehu headwater -> the sea, as one chain."""
    gate_reach = min(by.values(), key=lambda f: min(
        geo.haversine(p, [TAUPO_GATES[1], TAUPO_GATES[0]]) for p in f["geometry"]["paths"][0]))
    gate_id = gate_reach["attributes"]["HydroID"]

    # Which reaches reach the gates? Only those can be Waikato headwaters.
    drains, memo = {}, {}
    sys.setrecursionlimit(30000)

    def reaches_gate(hid: int) -> bool:
        if hid == gate_id:
            return True
        if hid in memo:
            return memo[hid]
        memo[hid] = False  # cycle guard
        f = by.get(hid)
        memo[hid] = False if f is None else reaches_gate(f["attributes"]["NextDownID"])
        return memo[hid]

    for hid in list(by):
        drains[hid] = reaches_gate(hid)
    # The headwater is the highest reach that drains to the gates.
    head = max((f for hid, f in by.items() if drains[hid]), key=lambda f: f["attributes"]["upElev"])

    upper = geo.walk_downstream(by, head["attributes"]["HydroID"])
    upper = upper[: next(i for i, f in enumerate(upper) if f["attributes"]["HydroID"] == gate_id)]
    lower = geo.walk_downstream(by, gate_id)
    chain = upper + lower
    line = geo.stitch(chain)
    return chain, geo.Spine(line, geo.cumulative(line)), head, lower[0]


def lake_ring() -> list[list[float]]:
    rel = json.loads((CACHE / "osm" / "taupo.json").read_text())["elements"][0]
    segs = [[[p["lon"], p["lat"]] for p in m["geometry"]]
            for m in rel["members"] if m.get("role") == "outer" and m.get("geometry")]
    ring = segs.pop(0)
    while segs:
        best = None
        for i, s in enumerate(segs):
            for rev in (False, True):
                t = s[::-1] if rev else s
                d = geo.haversine(ring[-1], t[0])
                if best is None or d < best[0]:
                    best = (d, i, rev)
        _, i, rev = best
        s = segs.pop(i)
        ring += (s[::-1] if rev else s)[1:]
    return ring


def main() -> int:
    if not (CACHE / "rec2").exists():
        print("  nothing cached — run `make sources` first")
        return 1

    by = load_rec2()
    chain, spine, head, gate = build_spine(by)
    gate_km = (spine.length_m - gate["attributes"]["LENGTHDOWN"]) / 1000
    print(f"  spine {spine.length_m / 1000:.2f} km, {len(spine.line)} vertices, gates at {gate_km:.1f} km")

    # ---- measurements -------------------------------------------------------
    z = zipfile.ZipFile(CACHE / "lawa" / "river-wq-ni3.xlsx")
    ss = xlsx.shared_strings(z)
    it = xlsx.rows(z, "xl/worksheets/sheet2.xml", ss)
    next(it)  # header
    sites: dict[str, dict] = {}
    obs: dict[tuple[str, str], list[float]] = collections.defaultdict(list)
    censored: collections.Counter = collections.Counter()
    for r in it:
        if len(r) < 18 or r[0] != "waikato":
            continue
        name = r[4]
        if not name.lower().startswith(("waikato river at", "waikato at")):
            continue
        s = sites.setdefault(name, {"site": name, "lawa_id": r[3], "agency": r[1],
                                    "lat": float(r[6]), "lon": float(r[7]),
                                    "samples": 0, "first": None, "last": None})
        s["samples"] += 1
        d = xlsx.excel_date(r[12])
        if d:
            s["first"] = d if s["first"] is None or d < s["first"] else s["first"]
            s["last"] = d if s["last"] is None or d > s["last"] else s["last"]
        if r[11] in INDICATORS:
            if r[15] == "<":
                censored[r[11]] += 1
            try:
                obs[(name, r[11])].append(float(r[16]))
            except ValueError:
                pass

    stations = []
    for name, s in sites.items():
        off, m = spine.snap(s["lat"], s["lon"])
        stations.append({**s, "km": round(m / 1000, 3), "offset_m": round(off, 1)})
    stations.sort(key=lambda s: s["km"])

    measures = []
    for name, (key, unit, better) in ((k, v) for k, v in INDICATORS.items()):
        pts = []
        for st in stations:
            vals = obs.get((st["site"], name))
            if not vals:
                continue
            pts.append({"km": st["km"], "site": st["site"], "n": len(vals),
                        "median": round(statistics.median(vals), 4),
                        "p25": round(statistics.quantiles(vals, n=4)[0], 4) if len(vals) > 3 else None,
                        "p75": round(statistics.quantiles(vals, n=4)[2], 4) if len(vals) > 3 else None})
        measures.append({"key": key, "label": name, "unit": unit,
                         "direction": better, "censored": censored.get(name, 0), "points": pts})

    # ---- landmarks ----------------------------------------------------------
    feats = json.loads((CACHE / "osm" / "features.json").read_text())["elements"]
    dams = []
    for e in feats:
        t = e.get("tags", {})
        c = e.get("center") or {}
        lat, lon = e.get("lat") or c.get("lat"), e.get("lon") or c.get("lon")
        if not lat or t.get("waterway") != "dam":
            continue
        nm = t.get("name")
        if nm in DAM_NAMES:
            dams.append((nm, lat, lon))
        elif abs(lat - WAIPAPA_DAM[0]) < 1e-3 and abs(lon - WAIPAPA_DAM[1]) < 1e-3:
            dams.append(("Waipapa Dam", lat, lon))
    out_dams = []
    for nm, lat, lon in dams:
        off, m = spine.snap(lat, lon)
        out_dams.append({"name": nm, "km": round(m / 1000, 3), "offset_m": round(off, 1),
                         "lat": lat, "lon": lon})
    out_dams.sort(key=lambda d: d["km"])

    towns = []
    for e in feats:
        t = e.get("tags", {})
        if t.get("place") not in ("city", "town"):
            continue
        lat, lon = e.get("lat"), e.get("lon")
        if lat is None:
            continue
        off, m = spine.snap(lat, lon)
        if off > 3000:  # a town 3 km from the water is not a town on this river
            continue
        towns.append({"name": t.get("name"), "km": round(m / 1000, 3), "offset_m": round(off, 1),
                      "population": int(t["population"]) if t.get("population", "").isdigit() else None,
                      "lat": lat, "lon": lon})
    towns.sort(key=lambda t: t["km"])

    flow = []
    for f in FLOW:
        off, m = spine.snap(f["lat"], f["lon"])
        flow.append({**f, "km": round(m / 1000, 3), "offset_m": round(off, 1)})
    flow.sort(key=lambda f: f["km"])

    doc = []
    for nm, lat, lon, path in DOC_PLACES:
        off, m = spine.snap(lat, lon)
        doc.append({"name": nm, "km": round(m / 1000, 3), "offset_km": round(off / 1000, 2),
                    "url": "https://www.doc.govt.nz" + path})
    doc.sort(key=lambda d: d["km"])

    # ---- write --------------------------------------------------------------
    # The mainstem reach by reach: distance, the catchment feeding it, and the
    # elevation it falls through. REC2's own numbers, carried unchanged — which
    # is what lets verify.py test them against Waikato Regional Council's.
    profile = []
    for f in chain:
        a = f["attributes"]
        profile.append({"km": round((spine.length_m / 1000) - a["LENGTHDOWN"] / 1000, 3),
                        "catchment_km2": round(a["CUM_AREA"] / 1e6, 2),
                        "elev_m": round(a["downElev"], 1)})
    profile.sort(key=lambda p: p["km"])

    # Simplify, then recover the real distance downstream at each surviving
    # vertex. The map animates a boat along this line, and it has to move at the
    # river's actual pace: SVG path length is not kilometres, because the
    # projection stretches and the simplification removes bends unevenly.
    simplified = geo.simplify(spine.line, SIMPLIFY_M)
    kept = {(round(x, 7), round(y, 7)) for x, y in simplified}
    line_km = [round(c / 1000, 3) for p, c in zip(spine.line, spine.cum)
               if (round(p[0], 7), round(p[1], 7)) in kept]
    if len(line_km) != len(simplified):
        # Two vertices at the same rounded position would break the pairing.
        raise SystemExit(f"vertex/distance mismatch: {len(simplified)} vs {len(line_km)}")
    ring = lake_ring()
    canonical(DATA / "river.json", {
        "length_km": round(spine.length_m / 1000, 3),
        "rec2_lengthdown_km": round(chain[0]["attributes"]["LENGTHDOWN"] / 1000, 3),
        "source_elevation_m": head["attributes"]["upElev"],
        "gates_km": round(gate_km, 3),
        "simplify_tolerance_m": SIMPLIFY_M,
        "vertices_full": len(spine.line),
        "line": [[round(x, 5), round(y, 5)] for x, y in simplified],
        "line_km": line_km,
        "lake_taupo": [[round(x, 5), round(y, 5)] for x, y in geo.simplify(ring, SIMPLIFY_M)],
        "catchment_km2": round(chain[-1]["attributes"]["CUM_AREA"] / 1e6, 1),
        "profile": profile,
    })
    canonical(DATA / "stations.json", stations)
    canonical(DATA / "journey.json", journey.build(spine, spine.line, measures, stations, ring, RUAPEHU))
    canonical(DATA / "measures.json", measures)
    canonical(DATA / "landmarks.json", {"dams": out_dams, "towns": towns,
                                        "flow": flow, "flow_asof": FLOW_ASOF, "doc": doc})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
