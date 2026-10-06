# SOURCES — what has been adopted, and on what terms

Written 2026-09-18, answering SPEC §3.2. **Contents were read, not just
reachability.** Every figure below was computed from the files themselves; the
commands are in `pipeline/`.

Licence is recorded here as each source is adopted, per SPEC §3.2 (5). A source
is not adopted until it has a row in §1 with a licence that has been read.

---

## 1. Adopted

### 1.1 LAWA — river water quality monitoring data (**primary**)

| | |
| --- | --- |
| **Publisher** | Land, Air, Water Aotearoa (LAWA), on behalf of partner agencies |
| **File** | *River water quality monitoring data: North Island (2004–2024) 3 of 3* — Northland and Waikato |
| **Published** | 9 February 2026. Data collated from agency databases July–September 2025 |
| **Covers** | 2004-01-06 – 2024-12-12 |
| **Licence** | **CC BY 4.0**, stated in the file's own *Dataset Notices* sheet |
| **Attribution required** | *"Data sourced from LAWA (Land, Air, Water Aotearoa) and Waikato Regional Council, available under the Creative Commons Attribution 4.0 International Licence"*, with links to <https://www.lawa.org.nz/> and the licence |
| **Agency for our sites** | Waikato Regional Council (19 sites), NIWA / Earth Sciences New Zealand (1 site) |
| **Format** | `.xlsx`, 27 MB, one 313,000-row sheet. Readable with `zipfile` + `xml.etree` — no dependency needed |

The file is served from Google Sheets. `export?format=xlsx` on the document id
returns it; the id is listed on <https://www.lawa.org.nz/download-data>.

**Caveat carried from the publisher:** LAWA notes that contracted laboratories
and lab methods change over time, and that quality codes are a mix of agency
internal codes and NEMS. Both are relevant to a 21-year series.

### 1.2 NIWA REC2 — river network geometry (**the spine**) — LICENCE PROBLEM

| | |
| --- | --- |
| **Publisher** | NIWA / Earth Sciences New Zealand |
| **Layer** | River Environment Classification (REC2), *River Lines* |
| **Endpoint** | `services3.arcgis.com/fp1tibNcN9mbExhG/.../REC2_Layers/FeatureServer/0` — answers anonymously, returns WGS84 geometry |
| **Licence** | **CC BY-NC 4.0** — *NonCommercial*. `copyrightText` on the layer is "NIWA, Taihoro Nukurangi, 2018" |

Carries `LENGTHDOWN` (metres to the sea), `NextDownID` (network topology),
`StreamOrde`, `CUM_AREA`. That is the distance-downstream axis SPEC §3.2 (2)
asks for, already computed by the publisher, rather than a projection this
project would have to invent and defend.

**Adopted 2026-09-18 with the NonCommercial term accepted**, this being a
personal, non-commercial site. Recorded here because it is a real constraint
and the next person will need to know it: **this project cannot be
commercialised while REC2 is in it**, and the credits page must say BY-NC
rather than BY for this source alone. Two of the catalogue's records for the
same layer disagree — one says CC BY-NC 4.0, one says nothing — so BY-NC is
taken as the binding one. If the licence ever has to go, the replacements are
LINZ NZ River Centrelines (CC BY 4.0, free API key) or OpenStreetMap (ODbL),
and both would mean deriving distance downstream by hand.

### 1.3 OpenStreetMap — lake outline, dams, towns

| | |
| --- | --- |
| **Licence** | **ODbL 1.0.** Attribution required, and share-alike on the *database*. The map is a Produced Work, so the site itself is not infected — but a derived dataset would be |
| **Attribution** | © OpenStreetMap contributors, on the page |
| **Fetched** | Overpass API, no key. It answers 504 and 429 under load, so `sources.py` retries |

Taken because the openly-licensed alternatives were worse: LINZ's lake polygons
are CC BY 4.0 but behind an API key, and NIWA's coastline is **CC BY-NC-SA** —
the ShareAlike would reach the whole project.

**Checked, not trusted:** the stitched Lake Taupō outline encloses 613 km²
against a published ~616. `verify.py` tests it on every build. Seven of the
eight dams are named in OSM; Waipapa is mapped but unnamed and is identified by
position, which `verify.py` guards by checking all eight come out in the
published downstream order.

### 1.4 Waikato Regional Council — flow (**a dated snapshot, not a feed**)

| | |
| --- | --- |
| **Source** | Envirohub, `/api/v1/enviromap/stations` |
| **Read** | 2026-09-18 |
| **Holds** | Four mainstem gauges. Mean flow, record high and low with dates, catchment area, record start — from 1957, 1963, 1965 and 1975 |

**This one cannot be automated and the reason is recorded here so nobody wastes
an afternoon on it.** The endpoint is behind Incapsula, which rejects every
non-browser client; `curl` gets a challenge page, not JSON. The figures are
therefore committed in `emit.py` as a snapshot with its date.

That is acceptable only because they are long-record statistics — a mean over
fifty years does not move — and because they are *guarded*: `verify.py` checks
each station's catchment area against REC2's, and the two publishers agree to
**0.04%**. If a station were ever moved, mistyped or misplaced on the spine,
that check fails.

No licence is stated on the endpoint. The figures used are four means and four
record extremes, attributed on the page.

### 1.5 Department of Conservation — place pages

*Not used on the site since the 2026-10-06 redesign; the entries remain in
`landmarks.json` for any page that wants them back.*

Six links, taken from DOC's own `sitemap.xml` rather than guessed, each checked
for a 200 on 2026-09-18 and each placed on the spine so the distance from the
river can be stated. Links only; no DOC content is reproduced.

### 1.6 Stats NZ — who lives on the river

| | |
| --- | --- |
| **Publisher** | Stats NZ, *Place and ethnic group summaries* |
| **Measure** | Estimated resident population, June 2025 — Stats NZ's own best measure of who usually lives somewhere, and two years more current than the 2023 census count |
| **Licence** | **CC BY 4.0** |
| **Read** | 2026-10-06, by `sources.py statsnz`, from the data block each server-rendered page carries |

Eighteen settlements are read. Which count as *on the river* is decided by
distance from the channel in `journey.py`: within 3 km. Fourteen are within
1.2 km and not in question; **the line does matter at its edge** — Tuakau is in
at 2.95 km and Pōkeno, 7,380 people, out at 3.20. Counting Pōkeno moves the
lower Waikato from 10% of the river's people to 12% and changes no conclusion.
The sources page states this rather than leaving it to be found.

Checked: Hamilton reads 192,100, and its 2023 census count on the same page is
174,741 — an estimate a long way from its census would mean the wrong place had
been read, and `verify.py` bounds it.

### 1.7 OpenStreetMap — the river the journey follows, and where the towns are

Relation [2751038](https://www.openstreetmap.org/relation/2751038), *Waikato
River*, fetched from the main OSM API (Overpass returned 504 three times running).
Eighteen ways: fourteen `main_stream` and four untagged — the spillways at
Ātiamuri and Maraetai, which are the only connection across those dams. Its
centreline stops at the head of the estuary; REC2 carries the last 14 km,
smoothed with a 150 m Gaussian because REC2's line runs in grid steps.

Above the lake (2026-10-06, when the journey was extended to the source): every
`waterway` of class river, stream or canal in a box around REC2's upper mainstem,
plus relation [18122690](https://www.openstreetmap.org/relation/18122690),
*Tongariro River*, from Overpass. `journey.py` picks the chain of them that runs
along REC2's line by a shortest-path search weighted by distance from REC2 — it
comes out as the Mangatoetoenui Stream, then the Tongariro. OSM's mapped stream
starts about 1.6 km below REC2's head on the ice; that first stretch is one
smooth curve from REC2's head to the stream, because REC2's line there is a grid
trace that steps at 45° and jogs 90° to meet it. Across Lake Taupō the journey takes a curve clear of Motutaiko Island
rather than REC2's straight segments.

The map tiles are built from these same ways, which is why the journey follows
OSM rather than REC2: REC2 traces the same river from the LINZ topographic survey
and sits tens of metres off the drawn water at street zoom. The two are checked
against each other every build — the path's length agrees with REC2's to 0.7%,
and no sampled vertex off the lake strays more than 600 m from REC2's line.

Settlement positions from Nominatim, one request a second as its policy asks.
**Licence: ODbL.**

### 1.7b The journey's passages

Each stop lists its own sources under its passage (`site/src/lib/chapters.ts`),
checked against the source text on 2026-10-06: NZHistory (Tongariro gift,
Rangiriri, 2010 rowing world championships), Te Ara (Lake Taupō, Ngāruawāhia),
Waikato Regional Council (Variation 5; TR 2015/13; TR 2018/44; the Kirikiriroa
kūmara story, quoting Wiremu Puke of Ngaati Wairere), the Parliamentary
Commissioner for the Environment (2013 land-use report: forest-to-dairy north of
Taupō, the 17-fold figure, groundwater lag at Taupō), Mercury (control gates),
Living Heritage (Huka Falls), Love Taupō (Aratiatia releases), NIWA (elver
transfer at Karāpiro), DOC (Whangamarino, matuku-hūrepo and the October 2024
fire, Māui dolphin), Ngā Taonga (Tūrangawaewae Regatta), legislation.govt.nz
(2010 River Settlement Act and Te Ture Whaimana; 1995 Raupatu Settlement Act;
River Iwi Act 2010), Watercare. Te Ara and WRC refuse non-browser fetches; they
were read in a browser.

### 1.8 OpenFreeMap — the map tiles (**runtime**)

OpenMapTiles-schema vector tiles of OpenStreetMap, from
[openfreemap.org](https://openfreemap.org): no key, no registration, no request
limit. Restyled from scratch in `site/src/lib/mapstyle.ts`.

**This is the site's one runtime dependency on somebody else's server**, and it
breaks the rule that the site builds from the repository alone — the pages still
build, but the journey's map is blank if OpenFreeMap is down. Accepted as the
cost of a real street map at every zoom from 8 to 16. The way out, if it is ever
needed, is a Protomaps PMTiles extract of the corridor, served from this
repository: a one-off extraction step and some tens of megabytes.

### 1.9 Attributed statements

| Statement | Source | Used where |
| --- | --- | --- |
| 61% of the river's nitrogen from land use, mainly pastoral farming; 6% from town and industrial wastewater; 33% background | Bill Vant, WRC senior water scientist, quoted by [RNZ](https://shorthand.radionz.co.nz/the-dirty-truth-about-the-waikato-river/) | Landing, journey, sources |
| Up to 225 million litres a day drawn near Tuakau for Auckland | [Watercare, 14 July 2021](https://www.watercare.co.nz/home/about-us/latest-news-and-media/new-water-treatment-plant-near-tuakau-about-to-go-live) | Landing, journey |

The WRC figure could not be confirmed from WRC's own pages, which now put every
non-browser client — and on the day this was written, the browser too — behind a
bot check that this project does not try to get past. It is attributed to the
person and the outlet that published it.

### 1.10 Consulted, not used: the "handful of farmers" question

The brief for the 2026-10-06 redesign described the river as degraded by "a
handful of wealthy elite farm owners". The site does not say that, and the
reason is recorded here so it is a decision rather than an omission:

- **The data cannot see who.** Monitoring shows where the water changes. The 61%
  is a figure for land use across the catchment.
- **"A handful" is contradicted.** DairyNZ and LIC, *New Zealand Dairy Statistics
  2023-24*: 3,022 dairy herds in the Waikato region, 1.08 million cows — and that
  is dairy alone, before sheep and beef. Not every one of those drains to this
  river, but the order of magnitude is thousands, not a handful.

The site says instead that land use, mainly pastoral farming, is the source of
most of the nitrogen and towns of very little, which is sourced, and which is
the same point.

## 2. Read and rejected, with the reason

| Source | Why not |
| --- | --- |
| MfE *River water quality, raw observations, 2013–2017* | Superseded. LAWA's file is the same measurements, more current, and downloadable. MfE's resources are Koordinates portal pages, not files |
| MfE *…state / trends, 2016–2020* and *1991–2020* | Per-site summary statistics, not a series. CC BY 4.0. Useful later as an **independent check** on medians this project computes — which is exactly what `verify.py` wants |
| MfE *…modelled / predicted* (all) | Modelled, not measured. SPEC §2 and HANDOFF §5 both rule this out |
| Waikato Regional Council *Rivers and streams: monitoring and reporting* | Licence "other, check with agency". The six resource URLs are aggregate indicator spreadsheets, last updated 2014–2016, and at least one now 404s |
| LAWA *River water quality state and trend results* (30 Oct 2025) | CC BY 4.0, keep in reserve. Same check role as the MfE state/trend files |
| NIWA Hydro Web Portal | Flow. Requires an account; the API answers 401 anonymously and the terms are the platform vendor's. Not usable |
| MfE *Natural river flow statistics, predicted for all river reaches* | Modelled, and explicitly **natural** flow — it excludes dams. On the most heavily dammed river in the country that is not a simplification, it is the wrong number |
| LAWA `waterquantityservice` internal API | Undocumented, needs zone ids discovered by crawling, and is not covered by the CC BY 4.0 that the published downloads carry |
| NIWA *Coastline* | **CC BY-NC-SA 4.0.** ShareAlike would reach the whole project |
| LINZ *NZ Lake Polygons (Topo 1:50k)* | CC BY 4.0 and the cleanest licence available, but needs an API key. Reconsider if OSM's ODbL ever becomes a problem |

## 3. Not yet investigated

- **Flow above Hamilton.** All four gauges are on the lower river. The hydro
  chain's flows are operated rather than natural and no open measured record was
  found. This is stated on the page rather than filled in.
- **Load, rather than concentration.** Concentration × discharge would give
  tonnes per year, which is the number that says what the river delivers to the
  sea. It needs flow at the same places as the chemistry, and there is none
  above Hamilton.
- **Waikato River Authority Report Card** — grades the whole catchment C+ across
  eight taura. A different shape from this (one grade, no distance axis), but
  worth reading before adding anything evaluative here.

---

## 4. Attribution and trademarks

HANDOFF §5 applies. No logos have been taken from anybody, and none should be
without checking separately from the data licence — the LAWA and council marks
are trademarks that CC BY 4.0 does not cover, and an iwi emblem is a more
serious question again.
