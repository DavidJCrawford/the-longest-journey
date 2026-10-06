"""Find and cache the source data.

    python3 pipeline/fetch.py [query ...]

New Zealand's environmental data is not one source. Regional councils, the
Ministry for the Environment, NIWA and LAWA all publish, in different shapes,
and most of it is indexed by data.govt.nz — which runs CKAN, so it is queryable
without scraping anything.

This is the reconnaissance step, not the ingest. It records what exists and in
what formats, into .cache/catalogue/, so that choosing the datasets is a reading
job rather than a browsing job. Downloading the chosen ones comes after, and the
shape of that depends on what is chosen — see Docs/HANDOFF.md §2.

No dependencies, as in the sibling projects: a pipeline that needs a virtualenv
is a pipeline that stops working.
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "catalogue"
CKAN = "https://catalogue.data.govt.nz/api/3/action/package_search"
UA = {"User-Agent": "enviro-analysis/0.1 (personal project)"}

# The questions worth asking first. Each is a guess, and the point of caching
# the answers is so the next person can check the guesses instead of repeating
# them.
QUERIES = [
    "waikato river",
    "waikato river water quality",
    "river water quality monitoring sites",
    "river water quality raw observations",
    "waikato regional council monitoring",
    "river environment classification",
]


def search(q: str, rows: int = 50) -> dict:
    url = f"{CKAN}?{urllib.parse.urlencode({'q': q, 'rows': rows})}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def main() -> int:
    queries = sys.argv[1:] or QUERIES
    CACHE.mkdir(parents=True, exist_ok=True)
    for q in queries:
        try:
            payload = search(q)
        except Exception as e:  # noqa: BLE001 — the point is to report, not to raise
            print(f"  {q}: {e}")
            continue
        result = payload.get("result", {})
        dest = CACHE / f"{q.replace(' ', '-')}.json"
        dest.write_text(json.dumps(payload, indent=1, sort_keys=True))
        rows = result.get("results", [])
        print(f"  {q}: {result.get('count', 0)} datasets, {len(rows)} cached")
        for p in rows[:5]:
            org = (p.get("organization") or {}).get("title", "?")
            fmts = sorted({r.get("format", "").upper() for r in p.get("resources", []) if r.get("format")})
            print(f"      {p.get('title', '?')[:62]}")
            print(f"        {org[:40]:<40} {','.join(fmts)[:40]}")
    print(f"\n  catalogue in {CACHE.relative_to(ROOT)} — read it before choosing anything")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
