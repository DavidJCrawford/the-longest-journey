"""The spine: the river's line, and how anything gets a place on it.

SPEC §2 makes distance downstream the organising axis, so this is the one piece
everything else depends on. HANDOFF §2 says to do it early and to make it the
first thing verify.py checks.

The line is not drawn by hand. NIWA's REC2 river network already carries
LENGTHDOWN — metres from each reach to the sea — and NextDownID, which says
which reach each one flows into. Walking NextDownID from a headwater to
LENGTHDOWN = 0 produces the mainstem as a chain, in order, without anyone
deciding by eye which channel is the main one.

Distances here are geodesic (haversine on a sphere). REC2's own LENGTHDOWN is
planar, computed in NZTM. That they disagree by ~0.15% over 443 km is the point
rather than a problem: two quantities from different methods agreeing that
closely is evidence the chain is right, and verify.py tests exactly that.
"""
from __future__ import annotations

import math

R_EARTH = 6371008.8  # IUGG mean radius, metres


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Metres between two [lon, lat] points."""
    la1, lo1 = math.radians(a[1]), math.radians(a[0])
    la2, lo2 = math.radians(b[1]), math.radians(b[0])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))


def walk_downstream(by_hydro_id: dict, start_id: int) -> list:
    """Follow NextDownID from start_id to the sea. Guards against cycles: REC2
    is meant to be acyclic, and if it ever is not, this must stop rather than
    spin."""
    chain, cur, seen = [], by_hydro_id.get(start_id), set()
    while cur is not None:
        hid = cur["attributes"]["HydroID"]
        if hid in seen:
            raise ValueError(f"cycle in REC2 network at HydroID {hid}")
        seen.add(hid)
        chain.append(cur)
        cur = by_hydro_id.get(cur["attributes"]["NextDownID"])
    return chain


def stitch(chain: list) -> list[list[float]]:
    """Concatenate a chain of reaches into one ordered polyline.

    Reach geometry does not arrive with a consistent direction, so each reach is
    flipped if its far end is nearer the line so far than its near end."""
    line: list[list[float]] = []
    for i, f in enumerate(chain):
        pts = list(f["geometry"]["paths"][0])
        if not line:
            nxt = chain[i + 1]["geometry"]["paths"][0] if i + 1 < len(chain) else None
            if nxt is not None and min(haversine(pts[0], nxt[0]), haversine(pts[0], nxt[-1])) < min(
                haversine(pts[-1], nxt[0]), haversine(pts[-1], nxt[-1])
            ):
                pts = pts[::-1]
            line = pts
            continue
        if haversine(line[-1], pts[0]) > haversine(line[-1], pts[-1]):
            pts = pts[::-1]
        # Reaches usually share their join vertex exactly; drop the duplicate
        # when they do, keep both when they do not, so no length is invented.
        line += pts[1:] if haversine(line[-1], pts[0]) < 1 else pts
    return line


def cumulative(line: list[list[float]]) -> list[float]:
    cum = [0.0]
    for i in range(1, len(line)):
        cum.append(cum[-1] + haversine(line[i - 1], line[i]))
    return cum


class Spine:
    """The river as one measured line, and the projection onto it."""

    def __init__(self, line: list[list[float]], cum: list[float]):
        self.line = line
        self.cum = cum

    @property
    def length_m(self) -> float:
        return self.cum[-1]

    def _xy(self, lon: float, lat: float, lat0: float) -> tuple[float, float]:
        # Local equirectangular projection. Over the few hundred metres between
        # a monitoring site and the channel this is exact enough that the error
        # is far below the offsets we actually see (all under 160 m).
        return (math.radians(lon) * math.cos(math.radians(lat0)) * R_EARTH, math.radians(lat) * R_EARTH)

    def snap(self, lat: float, lon: float) -> tuple[float, float]:
        """-> (metres from the line, metres downstream along it).

        The offset is returned, not discarded, because it is the evidence that a
        point belongs on this river at all. A site 5 km from the line is not a
        site on the Waikato, and verify.py refuses one."""
        px, py = self._xy(lon, lat, lat)
        best = (float("inf"), 0, 0.0)
        for i in range(len(self.line) - 1):
            ax, ay = self._xy(self.line[i][0], self.line[i][1], lat)
            bx, by = self._xy(self.line[i + 1][0], self.line[i + 1][1], lat)
            dx, dy = bx - ax, by - ay
            l2 = dx * dx + dy * dy
            t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
            d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d < best[0]:
                best = (d, i, t)
        d, i, t = best
        return d, self.cum[i] + t * (self.cum[i + 1] - self.cum[i])


def simplify(line: list[list[float]], tolerance_m: float) -> list[list[float]]:
    """Ramer-Douglas-Peucker.

    HANDOFF §5 warns that a river's line at full resolution is large and that
    the simplification has to be deliberate and stated rather than accidental.
    The tolerance is a parameter and the emitted data records it."""
    if len(line) < 3:
        return line
    keep = [False] * len(line)
    keep[0] = keep[-1] = True
    stack = [(0, len(line) - 1)]
    while stack:
        lo, hi = stack.pop()
        if hi <= lo + 1:
            continue
        ax, ay = line[lo]
        bx, by = line[hi]
        lat0 = (ay + by) / 2
        k = math.cos(math.radians(lat0))
        dx, dy = (bx - ax) * k, by - ay
        l2 = dx * dx + dy * dy
        far_i, far_d = -1, -1.0
        for i in range(lo + 1, hi):
            px, py = (line[i][0] - ax) * k, line[i][1] - ay
            t = 0.0 if l2 == 0 else max(0.0, min(1.0, (px * dx + py * dy) / l2))
            d = math.hypot(px - t * dx, py - t * dy) * math.radians(1) * R_EARTH
            if d > far_d:
                far_i, far_d = i, d
        if far_d > tolerance_m:
            keep[far_i] = True
            stack += [(lo, far_i), (far_i, hi)]
    return [p for p, k in zip(line, keep) if k]
