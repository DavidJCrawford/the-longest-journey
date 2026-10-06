"""Check the emitted JSON against facts it did not produce.

    python3 pipeline/verify.py

HANDOFF §4: not a schema check. Every test here compares the output against
something the emitter had no hand in — a second publisher's number, a published
figure, a physical bound, an ordering that must hold.

The strongest of them is the catchment cross-check. Waikato Regional Council
states a catchment area for each of its four flow gauges; NIWA's REC2 carries a
cumulative catchment area for every reach. Two organisations, different methods,
no shared working. If the spine were wrong, or a gauge snapped to the wrong
place on it, those numbers would not agree — and they agree to 0.04%.

verify.py returns 0 while site/data/ is empty, so the skeleton stays buildable.
The moment anything is emitted, every check below has to pass.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import geo  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "site" / "data"
CACHE = ROOT / ".cache"

# Published figures, from sources independent of anything this pipeline builds.
LAKE_TAUPO_KM2 = 616.0        # the area Lake Taupō is conventionally given as
WAIKATO_CATCHMENT_KM2 = 14260  # the catchment area conventionally published
# The eight dams, in the order the river meets them. Not derived — this is the
# published order, and the spine has to reproduce it.
DAM_ORDER = ["Aratiatia Dam", "Ōhakuri Dam", "Ātiamuri Dam", "Whakamaru Dam",
             "Maraetai Dam", "Waipapa Dam", "Arapuni Dam", "Karāpiro Dam"]
# The period LAWA states the file covers. A sample outside it means either the
# file changed or the date decoding is wrong.
PERIOD = ("2004-01-01", "2024-12-31")
# What the instruments can actually report. A negative concentration or a
# Secchi clarity deeper than the river is a bug, not a measurement.
BOUNDS = {"total_nitrogen": (0, 100), "oxidised_nitrogen": (0, 100),
          "total_phosphorus": (0, 50), "reactive_phosphorus": (0, 50),
          "e_coli": (0, 1_000_000), "clarity": (0, 30)}

checks = 0
failures: list[str] = []


def check(ok: bool, msg: str) -> None:
    global checks
    checks += 1
    if not ok:
        failures.append(msg)


def main() -> int:
    files = sorted(DATA.rglob("*.json")) if DATA.exists() else []
    if not files:
        print("  nothing emitted yet — nothing to verify (see Docs/HANDOFF.md §2)")
        return 0

    river = json.loads((DATA / "river.json").read_text())
    stations = json.loads((DATA / "stations.json").read_text())
    measures = json.loads((DATA / "measures.json").read_text())
    marks = json.loads((DATA / "landmarks.json").read_text())

    # 1. Our geodesic length against NIWA's own planar LENGTHDOWN.
    d = abs(river["length_km"] - river["rec2_lengthdown_km"]) / river["rec2_lengthdown_km"]
    check(d < 0.005, f"spine length {river['length_km']} km disagrees with REC2 "
                     f"LENGTHDOWN {river['rec2_lengthdown_km']} km by {d:.2%}")

    # 2. The spine is the axis: everything placed on it must be ordered by it.
    for name, seq in (("stations", stations), ("dams", marks["dams"]),
                      ("towns", marks["towns"]), ("flow", marks["flow"])):
        kms = [x["km"] for x in seq]
        check(kms == sorted(kms), f"{name} are not in distance order")
        check(all(0 <= k <= river["length_km"] for k in kms),
              f"a {name[:-1]} sits off the end of the river")

    # 3. Everything placed on the river must actually be on it.
    for s in stations:
        check(s["offset_m"] < 200, f"{s['site']} is {s['offset_m']} m from the channel")
    for f in marks["flow"]:
        check(f["offset_m"] < 200, f"{f['station']} is {f['offset_m']} m from the channel")

    # 4. Cross-publisher: WRC's catchment areas against NIWA's REC2. The
    #    strongest check here — see the module docstring.
    prof = river["profile"]
    for f in marks["flow"]:
        near = min(prof, key=lambda p: abs(p["km"] - f["km"]))
        rel = abs(near["catchment_km2"] - f["catchment_km2"]) / f["catchment_km2"]
        check(rel < 0.02, f"{f['station']}: WRC says {f['catchment_km2']} km2, "
                          f"REC2 says {near['catchment_km2']:.0f} km2 ({rel:.2%})")

    # 4b. The catchment can only grow downstream — water does not leave it.
    areas = [p["catchment_km2"] for p in prof]
    check(all(areas[i] <= areas[i + 1] + 0.01 for i in range(len(areas) - 1)),
          "catchment area decreases somewhere downstream, so the chain leaves the mainstem")

    # 5. Lake Taupō's area, from the emitted outline, against the published figure.
    ring = river["lake_taupo"]
    lat0 = sum(p[1] for p in ring) / len(ring)
    k = math.cos(math.radians(lat0)) * geo.R_EARTH
    xy = [(math.radians(x) * k, math.radians(y) * geo.R_EARTH) for x, y in ring]
    area = abs(sum(xy[i][0] * xy[i + 1][1] - xy[i + 1][0] * xy[i][1]
                   for i in range(len(xy) - 1)) / 2) / 1e6
    check(abs(area - LAKE_TAUPO_KM2) / LAKE_TAUPO_KM2 < 0.05,
          f"Lake Taupō outline encloses {area:.0f} km2, published {LAKE_TAUPO_KM2} km2")

    # 6. The catchment the river drains, against the published figure.
    check(abs(river["catchment_km2"] - WAIKATO_CATCHMENT_KM2) / WAIKATO_CATCHMENT_KM2 < 0.05,
          f"catchment {river['catchment_km2']} km2 vs published {WAIKATO_CATCHMENT_KM2} km2")

    # 7. The dams, in the order the published record says the river meets them.
    check([d["name"] for d in marks["dams"]] == DAM_ORDER,
          f"dam order is {[d['name'] for d in marks['dams']]}")

    # 8. Measurements inside what the instrument can report.
    for m in measures:
        lo, hi = BOUNDS[m["key"]]
        for p in m["points"]:
            for stat in ("median", "p25", "p75"):
                v = p.get(stat)
                check(v is None or lo <= v <= hi,
                      f"{m['key']} {stat} {v} at {p['site']} is outside [{lo}, {hi}]")
            check(p["n"] > 0, f"{m['key']} at {p['site']} has no samples")

    # 9. Every sample date inside the period LAWA says the file covers.
    for s in stations:
        check(s["first"] >= PERIOD[0] and s["last"] <= PERIOD[1],
              f"{s['site']} spans {s['first']}..{s['last']}, outside {PERIOD}")

    # 10. The gates must sit between the source and the sea, and the lake above them.
    check(0 < river["gates_km"] < river["length_km"], "the Taupō gates are not on the river")
    check(all(s["km"] >= river["gates_km"] - 1 for s in stations),
          "a water-quality site sits above the Taupō gates — none should")

    # ── The journey ──────────────────────────────────────────────────────────
    jp = DATA / "journey.json"
    if jp.exists():
        j = json.loads(jp.read_text())
        line = j["line"]

        # 11. It starts at the river's true head: REC2's first vertex, on
        #     Ruapehu, within two kilometres of the summit.
        check(geo.haversine(line[0][:2], river["line"][0]) < 5 and line[0][2] == 0,
              f"journey starts at {line[0]}, not at REC2's head {river['line'][0]}")
        check(geo.haversine(line[0][:2], j["summit"]) < 2000,
              f"the head is {geo.haversine(line[0][:2], j['summit']):.0f} m from the summit")

        # 12. The boat never sails upstream.
        kms = [v[2] for v in line]
        check(all(kms[i] <= kms[i + 1] for i in range(len(kms) - 1)), "journey kilometres run backwards")

        # 13. Two surveys, one river. OSM's path, measured by its own vertices,
        #     against the REC2 kilometres every vertex was filed under.
        to_coast = [v for v in line if v[2] <= j["coast_km"]]
        L = sum(geo.haversine(to_coast[i], to_coast[i + 1]) for i in range(len(to_coast) - 1)) / 1000
        span = to_coast[-1][2] - to_coast[0][2]
        # The sources page states "to within 1%", so that is the bound.
        check(abs(L - span) / span < 0.01,
              f"journey path is {L:.1f} km but spans {span:.1f} km of the REC2 axis")

        # 14. And it is the same river, not a tributary the stitch wandered into:
        #     every sampled vertex of OSM's line lies close to REC2's line.
        rline = river["line"]
        def nearest_m(pt):
            best = float("inf")
            for i in range(0, len(rline) - 1):
                a, b = rline[i], rline[i + 1]
                k = math.cos(math.radians(pt[1]))
                ax, ay, bx, by = a[0] * k, a[1], b[0] * k, b[1]
                px, py = pt[0] * k, pt[1]
                dx, dy = bx - ax, by - ay
                l2 = dx * dx + dy * dy
                t = 0 if l2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / l2))
                d = math.hypot(px - ax - t * dx, py - ay - t * dy) * math.radians(1) * geo.R_EARTH
                best = min(best, d)
            return best
        #     The lake crossing is left out: REC2 crosses Taupō in a few straight
        #     segments, and the journey's curve round Motutaiko is not meant to
        #     follow them. Above the lake this tests the streams the search
        #     chose; below it, the Waikato.
        lk0, lk1 = j["lake_crossing_km"]
        river_part = [v for v in line if 3 < v[2] <= j["osm_end_km"] and not lk0 < v[2] < lk1]
        worst = max(nearest_m(v) for v in river_part[::12])
        check(worst < 600, f"OSM's river strays {worst:.0f} m from REC2's — the path left the mainstem")

        # 14b. The lake crossing stays on the lake.
        ring = river["lake_taupo"]
        def inside(pt):
            x, y, c = pt[0], pt[1], False
            for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
                if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                    c = not c
            return c
        crossing = [v for v in line if lk0 + 0.5 < v[2] < lk1 - 0.5]
        check(crossing and all(inside(v) for v in crossing), "the lake crossing runs onto land")
        check([n for _, _, n in j["upper_names"]][:2] == ["Mangatoetoenui Stream", "Tongariro River"],
              f"above the lake the path follows {j['upper_names']}, not the Mangatoetoenui and the Tongariro")

        # 15. Who lives on the river: the rule, applied as stated, and the sums.
        for st in j["settlements"]:
            check(st["population"] > 0, f"{st['name']} has no population")
            check(st["on_river"] == (st["offset_km"] <= j["on_river_km"]),
                  f"{st['name']} is {st['offset_km']} km off but on_river={st['on_river']}")
        on = [st for st in j["settlements"] if st["on_river"]]
        check(sum(st["population"] for st in on) == j["people_on_river"], "people on the river do not sum")
        check(sum(r["people"] for r in j["reaches"]) == j["people_on_river"],
              "the reaches do not account for everyone on the river, or count someone twice")

        # 16. The reaches meet end to end and run downstream.
        rs = j["reaches"]
        check(all(rs[i]["to_site"] == rs[i + 1]["from_site"] for i in range(len(rs) - 1)),
              "reaches do not meet at a shared site")
        check(all(r["from_km"] < r["to_km"] for r in rs), "a reach runs upstream")

        # 17. Stats NZ's figure for Hamilton, against the city's own 2023 census
        #     count from the same publisher — an estimate a long way from its
        #     census would mean the wrong place was read.
        ham = next(st for st in j["settlements"] if st["slug"] == "hamilton")
        check(170_000 < ham["population"] < 215_000, f"Hamilton read as {ham['population']}")

    print(f"  {checks} checks")
    for f in failures:
        print(f"  FAIL  {f}")
    if failures:
        print(f"  {len(failures)} failed")
        return 1
    print("  all passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
