"""The journey: the path the boat follows, and what it passes.

Six pieces of line, joined end to end:

  1. From the river's true head — REC2's first vertex, on the ice on Ruapehu's
     eastern slopes, 2,600 m up — to where OpenStreetMap's first mapped stream
     begins, about a kilometre and a half below, as one smooth curve. Nothing is
     mapped on the ice, and REC2's own line there is a grid trace that steps
     at 45° and then jogs 90° sideways to meet the stream.
  2. OpenStreetMap's streams from there to Lake Taupō: the Mangatoetoenui
     Stream, then the Tongariro River. Chosen as the chain of OSM waterways that
     runs along REC2's line, so the boat is on water the map draws.
  3. Across the lake, from the Tongariro's mouth to the outlet, on one smooth
     curve that leaves the Tongariro and meets the Waikato in the direction each
     is flowing, and keeps clear of Motutaiko Island and the shore.
  4. OpenStreetMap's Waikato River, from the outlet to where its centreline
     stops at the head of the estuary.
  5. REC2's mainstem for the last few kilometres to the coast, where OSM maps
     the estuary only as water — smoothed, because REC2 is traced from a
     terrain grid and runs in steps.
  6. A short run out to sea.

Every vertex is then placed on the REC2 spine by distance downstream, so the
boat's kilometre is the same kilometre every measurement on the site is filed
under. The two surveys trace the same river, and verify.py checks they agree
on its length.
"""
from __future__ import annotations

import heapq
import json
import math
import pathlib

import geo

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"

#: Off Taupō township, where the journey used to begin
#: (openstreetmap.org/#map=16/-38.70350/176.06333): used to find which end of
#: OSM's Waikato is the outlet.
LAKE_VIA = (176.06333, -38.70350)

#: What the lake crossing must keep clear of, in metres: the shore, away from
#: the two ends where it has to touch it, and Motutaiko Island.
LAKE_SHORE_M = 700.0
LAKE_ISLAND_M = 1500.0

#: Smoothing for REC2's estuary tail. REC2 is traced from a terrain grid and its
#: line runs in steps tens of metres across; a Gaussian of this width takes the
#: steps out without moving the line off the water of an estuary 1-2 km wide.
TAIL_SIGMA_M = 150.0

#: Within this distance of the channel a settlement counts as living on the
#: river. Fourteen of the eighteen candidates sit within 1.2 km and are not in
#: question. The rule does do work at its edge, and the page says so: Tuakau is
#: in at 2.95 km and Pōkeno, 7,380 people, is out at 3.20. Counting Pōkeno would
#: move the lower Waikato from 10% of the river's people to 12% — it changes no
#: conclusion, which is the test a threshold like this has to pass.
ON_RIVER_KM = 3.0

#: How far past the mouth the journey carries on, in kilometres.
OFFSHORE_KM = 7.0

#: Simplification of the emitted path. Fine enough that the boat stays inside
#: the drawn water at the closest zoom the journey uses.
SIMPLIFY_M = 12.0

#: Where the river divides into the three reaches the ledger compares, by the
#: monitoring site at each boundary. Measured points, so each reach's change
#: in the water is a difference of two measurements and nothing in between.
REACHES = [
    ("Upper Waikato", "Taupō to Karāpiro",
     "Waikato River at Taupo Control Gates", "Waikato River at Karapiro Tailrace"),
    ("Cambridge and Hamilton", "Karāpiro to Horotiu",
     "Waikato River at Karapiro Tailrace", "Waikato River at Horotiu Br"),
    ("Lower Waikato", "Horotiu to Tuakau",
     "Waikato River at Horotiu Br", "Waikato River at Tuakau Br"),
]


def _stitch(river: dict, start: tuple[float, float]) -> list[list[float]]:
    """Chain the relation's ways into one line, from the end nearest the start.

    The relation's members are not in order, and at three dams the main stream
    is interrupted by a spillway mapped as a separate, untagged way. So: follow
    endpoints, prefer a `main_stream` way when two would connect, and accept a
    spillway when it is the only way across."""
    nodes = {e["id"]: [e["lon"], e["lat"]] for e in river["elements"] if e["type"] == "node"}
    ways = {e["id"]: e for e in river["elements"] if e["type"] == "way"}
    rel = next(e for e in river["elements"] if e["type"] == "relation")
    pieces = [{"pts": [nodes[n] for n in ways[m["ref"]]["nodes"]], "main": m["role"] == "main_stream"}
              for m in rel["members"] if m["type"] == "way"]

    first = min(pieces, key=lambda p: min(geo.haversine(p["pts"][0], start), geo.haversine(p["pts"][-1], start)))
    line = first["pts"] if geo.haversine(first["pts"][0], start) <= geo.haversine(first["pts"][-1], start) \
        else first["pts"][::-1]
    pieces.remove(first)
    while pieces:
        tail = line[-1]
        near = []
        for p in pieces:
            for rev in (False, True):
                head = p["pts"][-1] if rev else p["pts"][0]
                d = geo.haversine(tail, head)
                if d < 80:
                    near.append((not p["main"], d, p, rev))
        if not near:
            break
        _, _, p, rev = min(near, key=lambda t: (t[0], t[1]))
        pts = p["pts"][::-1] if rev else p["pts"]
        line += pts[1:] if geo.haversine(tail, pts[0]) < 1 else pts
        pieces.remove(p)
    return line


def _metric(lat0: float):
    """Local equirectangular metres, accurate to well under 1% over the few tens
    of kilometres any one of these helpers works across."""
    kx = math.cos(math.radians(lat0)) * math.radians(1) * geo.R_EARTH
    ky = math.radians(1) * geo.R_EARTH
    return (lambda p: (p[0] * kx, p[1] * ky)), (lambda q: (q[0] / kx, q[1] / ky))


def _dist_to_line(P: tuple[float, float], seg: list[tuple[float, float]]) -> float:
    best = float("inf")
    for (ax, ay), (bx, by) in zip(seg, seg[1:]):
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((P[0] - ax) * dx + (P[1] - ay) * dy) / l2))
        best = min(best, math.hypot(P[0] - ax - t * dx, P[1] - ay - t * dy))
    return best


def _inside(pt, ring) -> bool:
    x, y = pt
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def _upper(upper: dict, rec2: list[list[float]]) -> tuple[list[list[float]], list[str | None]]:
    """OpenStreetMap's streams from Ruapehu to the lake, along REC2's line.

    Every OSM waterway in the box becomes a graph; each segment costs its
    length, multiplied up the further it lies from REC2's mainstem. The cheapest
    route from the lake back up the mountain is then the chain of mapped
    streams that REC2's line traces — the Mangatoetoenui, then the Tongariro —
    and not a tributary that happens to be near. It is searched from the lake
    end because the mapped streams nearest REC2's head, on the ice, belong to
    other catchments; the start is the reachable stream nearest that head.

    Returns the path and the OSM name at each vertex, for the place readout."""
    to_m, _ = _metric(-39.1)
    # The guide line at 25 m — finer only slows the search.
    R = [to_m(p) for p in geo.simplify(rec2, 25.0)]
    key = lambda p: (round(p[0], 7), round(p[1], 7))
    graph: dict = {}
    names: dict = {}
    for w in upper["elements"]:
        g = [key((n["lon"], n["lat"])) for n in w["geometry"]]
        for n in g:
            names.setdefault(n, w.get("tags", {}).get("name"))
        for a, b in zip(g, g[1:]):
            A, B = to_m(a), to_m(b)
            off = _dist_to_line(((A[0] + B[0]) / 2, (A[1] + B[1]) / 2), R)
            cost = math.hypot(B[0] - A[0], B[1] - A[1]) * (1 + (off / 150) ** 2)
            graph.setdefault(a, []).append((b, cost))
            graph.setdefault(b, []).append((a, cost))
    entry, head = rec2[-1], rec2[0]
    t = min(graph, key=lambda n: geo.haversine(n, entry))
    dist, prev, pq = {t: 0.0}, {}, [(0.0, t)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, c in graph[u]:
            if d + c < dist.get(v, float("inf")):
                dist[v], prev[v] = d + c, u
                heapq.heappush(pq, (d + c, v))
    s = min(dist, key=lambda n: geo.haversine(n, head))
    path = [s]
    while path[-1] != t:
        path.append(prev[path[-1]])
    return [list(p) for p in path], [names.get(p) for p in path]


def _heading(pts: list[list[float]], to_m, back: bool, over_m: float = 600.0) -> tuple[float, float]:
    """Unit direction of travel over the last (back) or first ~over_m of a line,
    so one wiggle cannot set it."""
    M = [to_m(p) for p in (pts[::-1] if back else pts)]
    acc, b = 0.0, M[-1]
    for a, b in zip(M, M[1:]):
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        if acc >= over_m:
            break
    dx, dy = (M[0][0] - b[0], M[0][1] - b[1]) if back else (b[0] - M[0][0], b[1] - M[0][1])
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def _cubic(P0, t0, P3, t3, a: float, b: float, step_m: float) -> list[tuple[float, float]]:
    """A cubic from P0 leaving along t0 to P3 arriving along t3, in metres."""
    P1 = (P0[0] + t0[0] * a, P0[1] + t0[1] * a)
    P2 = (P3[0] - t3[0] * b, P3[1] - t3[1] * b)
    n = max(2, int(math.hypot(P3[0] - P0[0], P3[1] - P0[1]) / step_m))
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * P0[0] + 3 * u * u * t * P1[0] + 3 * u * t * t * P2[0] + t ** 3 * P3[0],
                    u ** 3 * P0[1] + 3 * u * u * t * P1[1] + 3 * u * t * t * P2[1] + t ** 3 * P3[1]))
    return out


def _lead_in(rec2_head: list[list[float]], streams: list[list[float]]) -> list[list[float]]:
    """From the source to the first mapped stream: leaving the source the way
    REC2's line runs overall, arriving the way the stream flows."""
    to_m, to_ll = _metric(rec2_head[0][1])
    P0, P3 = to_m(rec2_head[0]), to_m(streams[0])
    chord = math.hypot(P3[0] - P0[0], P3[1] - P0[1])
    t0 = _heading(rec2_head, to_m, back=False, over_m=chord * 0.6)
    t3 = _heading(streams, to_m, back=False)
    return [list(to_ll(q)) for q in _cubic(P0, t0, P3, t3, chord / 3, chord / 3, 25.0)]


def _crossing(inflow: list[list[float]], outflow: list[list[float]], ring: list[list[float]],
              island: list[list[float]], step_m: float = 200.0) -> list[list[float]]:
    """Across Lake Taupō, as one cubic curve.

    It starts at the Tongariro's mouth heading the way the Tongariro is flowing
    and ends at the outlet heading the way the Waikato leaves, so there is no
    corner at either end. The two handle lengths are searched for the gentlest
    curve that stays on the lake, LAKE_SHORE_M off the shore away from its two
    ends and LAKE_ISLAND_M off Motutaiko."""
    to_m, to_ll = _metric((inflow[-1][1] + outflow[0][1]) / 2)
    P0, P3 = to_m(inflow[-1]), to_m(outflow[0])

    tin, tout = _heading(inflow, to_m, back=True), _heading(outflow, to_m, back=False)
    # The shore at 100 m is plenty for a 700 m clearance, and fast to test.
    shore = [to_m(p) for p in geo.simplify(ring, 100.0)]
    isl = [to_m(p) for p in island]
    chord = math.hypot(P3[0] - P0[0], P3[1] - P0[1])

    def curve(a, b):
        return _cubic(P0, tin, P3, tout, a, b, step_m)

    def turning(pts):
        # The sharpest turn per kilometre anywhere along it.
        worst = 0.0
        for a, b, c in zip(pts, pts[1:], pts[2:]):
            h1 = math.atan2(b[1] - a[1], b[0] - a[0])
            h2 = math.atan2(c[1] - b[1], c[0] - b[0])
            worst = max(worst, abs((h2 - h1 + math.pi) % (2 * math.pi) - math.pi) / (step_m / 1000))
        return worst

    best = None
    for a in range(1000, int(chord * 0.9), 1000):
        for b in range(1000, int(chord * 0.9), 1000):
            pts = curve(a, b)
            ends = 2000.0
            inner = [q for q in pts if math.hypot(q[0] - P0[0], q[1] - P0[1]) > ends
                     and math.hypot(q[0] - P3[0], q[1] - P3[1]) > ends]
            ll = [to_ll(q) for q in inner]
            if not all(_inside(q, ring) for q in ll):
                continue
            if min(_dist_to_line(q, shore + shore[:1]) for q in inner[::3]) < LAKE_SHORE_M:
                continue
            if min(math.hypot(q[0] - c[0], q[1] - c[1]) for q in inner for c in isl) < LAKE_ISLAND_M:
                continue
            score = turning(pts)
            if best is None or score < best[0]:
                best = (score, pts)
    if best is None:
        raise SystemExit("no smooth lake crossing stays on the lake — loosen LAKE_SHORE_M or LAKE_ISLAND_M")
    return [list(to_ll(q)) for q in best[1]]


def _smooth(pts: list[list[float]], sigma_m: float, step_m: float = 20.0) -> list[list[float]]:
    """Resample at step_m and run a Gaussian along the line. Both ends are held
    exactly where they were, fading the smoothing in over three sigmas, so the
    smoothed piece still meets what comes before and after it."""
    to_m, to_ll = _metric(pts[0][1])
    P = [to_m(p) for p in pts]
    cum = [0.0]
    for a, b in zip(P, P[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    n = max(2, int(cum[-1] / step_m))
    res, j = [], 0
    for i in range(n + 1):
        d = cum[-1] * i / n
        while j < len(cum) - 2 and cum[j + 1] < d:
            j += 1
        seg = cum[j + 1] - cum[j]
        t = 0.0 if seg == 0 else (d - cum[j]) / seg
        res.append((P[j][0] + (P[j + 1][0] - P[j][0]) * t, P[j][1] + (P[j + 1][1] - P[j][1]) * t))
    s = sigma_m / (cum[-1] / n)
    w = int(3 * s)
    kern = [math.exp(-0.5 * (k / s) ** 2) for k in range(-w, w + 1)]
    out = []
    for i in range(len(res)):
        sx = sy = sw = 0.0
        for k in range(-w, w + 1):
            if 0 <= i + k < len(res):
                g = kern[k + w]
                sx += res[i + k][0] * g
                sy += res[i + k][1] * g
                sw += g
        blend = min(1.0, i / w, (len(res) - 1 - i) / w) if w else 1.0
        x = res[i][0] + (sx / sw - res[i][0]) * blend
        y = res[i][1] + (sy / sw - res[i][1]) * blend
        out.append(list(to_ll((x, y))))
    return out


def _rdp_keep(pts: list[list[float]], tol_m: float) -> list[bool]:
    """Ramer-Douglas-Peucker returning which vertices to keep, so the kilometre
    attached to each surviving vertex travels with it."""
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        lo, hi = stack.pop()
        if hi <= lo + 1:
            continue
        ax, ay = pts[lo]
        bx, by = pts[hi]
        k = math.cos(math.radians((ay + by) / 2))
        dx, dy = (bx - ax) * k, by - ay
        l2 = dx * dx + dy * dy
        far, fd = -1, -1.0
        for i in range(lo + 1, hi):
            px, py = (pts[i][0] - ax) * k, pts[i][1] - ay
            t = 0.0 if l2 == 0 else max(0.0, min(1.0, (px * dx + py * dy) / l2))
            d = math.hypot(px - t * dx, py - t * dy) * math.radians(1) * geo.R_EARTH
            if d > fd:
                far, fd = i, d
        if fd > tol_m:
            keep[far] = True
            stack += [(lo, far), (far, hi)]
    return keep


def build(spine: geo.Spine, rec2_line: list[list[float]], measures: list[dict],
          stations: list[dict], lake: list[list[float]], summit: tuple[float, float]) -> dict:
    river = json.loads((CACHE / "osm" / "river.json").read_text())
    upper_osm = json.loads((CACHE / "osm" / "upper.json").read_text())

    # REC2 down to where it enters the lake: the line the upper streams follow.
    entry = next(i for i, p in enumerate(rec2_line) if _inside(p, lake))
    streams, stream_names = _upper(upper_osm, rec2_line[: entry + 1])

    # 1: from the true head down to the first mapped stream.
    _, m_stream = spine.snap(streams[0][1], streams[0][0])
    head = _lead_in([list(p) for p, c in zip(rec2_line, spine.cum) if c <= m_stream], streams)[:-1]
    names: list[str | None] = [None] * len(head)
    # 2: the streams. 3: across the lake. 4: OSM's Waikato.
    osm = _stitch(river, LAKE_VIA)
    taupo = json.loads((CACHE / "osm" / "taupo.json").read_text())["elements"][0]
    island = [[g["lon"], g["lat"]] for m in taupo["members"] if m["role"] == "inner" for g in m["geometry"]]
    lake_leg = _crossing(streams, osm, lake, island)[1:-1]
    path = head + streams + lake_leg + osm
    names += stream_names + ["Lake Taupō"] * len(lake_leg) + [None] * len(osm)

    # Every vertex onto the spine. Snapping is forced to be monotonic: where the
    # two surveys disagree about which side of a tight bend a vertex belongs to,
    # the kilometre may not run backwards.
    kms: list[float] = []
    for lon, lat in path:
        _, m = spine.snap(lat, lon)
        kms.append(max(m / 1000, kms[-1] if kms else 0.0))
    lake_from = kms[len(head) + len(streams) - 1]
    lake_to = kms[len(head) + len(streams) + len(lake_leg) - 1]

    # 5: REC2 from where OSM's centreline stops, to the coast — smoothed, from
    # the last OSM vertex so the join is smooth too. Kilometres travel with the
    # resampled points in proportion along the piece, which is how REC2 files
    # them.
    osm_end_km = kms[-1]
    tail = [path[-1]] + [[lon, lat] for (lon, lat), c in zip(rec2_line, spine.cum) if c / 1000 > osm_end_km + 0.2]
    coast_km = spine.length_m / 1000
    smooth = _smooth(tail, TAIL_SIGMA_M)[1:]
    for i, pt in enumerate(smooth, 1):
        path.append(pt)
        kms.append(osm_end_km + (coast_km - osm_end_km) * i / len(smooth))
        names.append(None)

    # Then out to sea.
    #
    # Not on the river's last bearing. At Port Waikato the Waikato runs north
    # behind the sand spit before it reaches the Tasman, so carrying that
    # bearing on sent the boat up the beach, parallel to the coast, for seven
    # kilometres. The coast here runs north–south and the sea is west, so the
    # line turns from the river's heading to due west across the first two
    # kilometres and then runs straight offshore.
    tail = [p for p, k in zip(path, kms) if k >= coast_km - 2.0]
    a, b = tail[0], tail[-1]
    kx = math.cos(math.radians(b[1]))
    start_bearing = math.degrees(math.atan2((b[0] - a[0]) * kx, b[1] - a[1]))
    turn = ((270 - start_bearing + 540) % 360) - 180
    deg_per_km = 1 / 111.32
    x, y = b
    STEP = 0.5
    for i in range(1, int(OFFSHORE_KM / STEP) + 1):
        d = i * STEP
        brg = math.radians(start_bearing + turn * min(1.0, d / 2.0))
        x += math.sin(brg) * STEP * deg_per_km / kx
        y += math.cos(brg) * STEP * deg_per_km
        path.append([x, y])
        kms.append(coast_km + d)
        names.append(None)

    keep = _rdp_keep(path, SIMPLIFY_M)
    line = [[round(p[0], 6), round(p[1], 6), round(k, 3)] for p, k, kk in zip(path, kms, keep) if kk]

    # What the readout calls the water above the lake: OSM's own names for the
    # streams, as runs of kilometres. A junction vertex can carry a tributary's
    # name for one point; runs shorter than 300 m are folded into their
    # neighbours so the readout does not flicker.
    runs: list[list] = []
    for nm, k in zip(names, kms):
        if k > lake_to:
            break
        if runs and runs[-1][2] == nm:
            runs[-1][1] = k
        else:
            runs.append([k, k, nm])
    runs = [r for r in runs if r[2] and r[1] - r[0] >= 0.3]
    merged: list[list] = []
    for a, b, nm in runs:
        if merged and merged[-1][2] == nm:
            merged[-1][1] = b
        else:
            merged.append([a, b, nm])
    upper_names = [[round(a, 3), round(b, 3), nm] for a, b, nm in merged]

    # ── who lives on it ──────────────────────────────────────────────────────
    stats = json.loads((CACHE / "statsnz" / "settlements.json").read_text())
    where = json.loads((CACHE / "osm" / "places.json").read_text())
    settlements = []
    for slug, s in stats.items():
        p = where[slug]
        off, m = spine.snap(p["lat"], p["lon"])
        settlements.append({
            "slug": slug, "name": s["name"], "population": int(s["erp"]), "year": s["erp_year"],
            "km": round(m / 1000, 3), "offset_km": round(off / 1000, 2),
            "on_river": off / 1000 <= ON_RIVER_KM, "lat": p["lat"], "lon": p["lon"], "url": s["url"],
        })
    settlements.sort(key=lambda s: s["km"])
    people = sum(s["population"] for s in settlements if s["on_river"])

    # ── what changes in the water, reach by reach ────────────────────────────
    def value(key: str, site: str) -> float | None:
        m = next((x for x in measures if x["key"] == key), None)
        p = next((x for x in m["points"] if x["site"] == site), None) if m else None
        return p["median"] if p else None

    site_km = {s["site"]: s["km"] for s in stations}
    reaches = []
    for name, span, a_site, b_site in REACHES:
        lo, hi = site_km[a_site], site_km[b_site]
        last = name == REACHES[-1][0]
        reaches.append({
            "name": name, "span": span, "from_site": a_site, "to_site": b_site,
            "from_km": lo, "to_km": hi,
            # The last reach takes in everyone to the sea, not just to Tuakau:
            # Port Waikato lives on the river too, and its people would
            # otherwise fall out of every reach.
            "people": sum(s["population"] for s in settlements
                          if s["on_river"] and (lo <= s["km"] or name == REACHES[0][0])
                          and (s["km"] < hi or last)),
            "change": {k: [value(k, a_site), value(k, b_site)]
                       for k in ("total_nitrogen", "e_coli", "total_phosphorus", "clarity")},
        })

    return {
        "start": line[0][:2], "summit": [summit[1], summit[0]],
        "line": line, "simplify_tolerance_m": SIMPLIFY_M,
        "osm_relation": 2751038, "osm_tongariro_relation": 18122690,
        "upper_names": upper_names,
        "lake_crossing_km": [round(lake_from, 3), round(lake_to, 3)],
        "osm_end_km": round(osm_end_km, 3), "tail_sigma_m": TAIL_SIGMA_M,
        "coast_km": round(coast_km, 3), "offshore_km": OFFSHORE_KM,
        "on_river_km": ON_RIVER_KM, "settlements": settlements, "people_on_river": people,
        "reaches": reaches,
    }
