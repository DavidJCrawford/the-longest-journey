# SPEC — The Longest Journey

**A static, editorial site that makes complex environmental data usable: the
Waikato River from Taupō to the sea at Port Waikato, and how the water changes
on the way down.**

- **Status:** data settled 2026-09-18; the visual layer rebuilt 2026-10-06 on
  F1 Analysis's design — a landing page and a journey page that is F1's race
  replay turned into a map. See §4 and §6.
- **Sibling projects:** [NFL Analysis](https://github.com/DavidJCrawford/nfl-analysis)
  and [F1 Analysis](https://github.com/DavidJCrawford/f1-analysis), whose design
  system, build shape and hard-won lessons this inherits. See
  [HANDOFF.md](HANDOFF.md) §4 — those lessons are not optional reading, and the
  first of them is the reason §3 exists.
- **Deployment target:** GitHub Pages, personal account, at
  [davidjcrawford.github.io/the-longest-journey](https://davidjcrawford.github.io/the-longest-journey/),
  from [DavidJCrawford/the-longest-journey](https://github.com/DavidJCrawford/the-longest-journey).
- **Aesthetic reference:** [impeccable.style](https://impeccable.style), via the
  siblings — calm, editorial, typographically led. Decoration reads as wrong.

---

## 1. The promise

One sentence, to accept and reject every feature:

> **The river, end to end, and what the water is carrying at each point of it.**

The reader should come away understanding two things they did not before: that
the river matters, and that it is not the same river at Taupō as it is at Port
Waikato. A feature that serves neither does not belong.

## 2. Scope

**The Waikato River, source to sea.** New Zealand's longest. **338 km** from
Lake Taupō's outlet to the Tasman at Port Waikato — *not* the 425 km usually
quoted, which is measured from the headwaters on Ruapehu and includes the
Tongariro and the length of Lake Taupō. Checked 2026-09-18 against REC2; see
Docs/SOURCES.md. `site/src/lib/scope.ts` holds the
subject as a single constant, as the siblings hold a season, so a second
catchment later is one entry rather than a search.

The organising axis is **distance downstream**. That is the spine of the thing:
every measurement has a place on it, the reader moves along it, and the story —
water that changes as it travels — is only legible against it. If a dataset
cannot be placed on that axis, it is decoration.

**Not** a general environmental dashboard. Not every river in the Waikato
region. Not air, soil or climate, unless they explain something about the water.

## 3. Data — NOT YET ESTABLISHED

**This section is the project.** The sibling projects both learned the same
lesson the expensive way and it is written at the top of both handoffs: *verify
what the data holds before designing around it.* On NFL Analysis, twenty minutes
of counting killed a home-page design before it was drawn. Here the exposure is
larger, because unlike nflverse there is no single publisher.

### 3.1 What has been found so far

**Superseded on 2026-09-18 — the contents have now been read. See
[SOURCES.md](SOURCES.md), which is the record, and note that the line below
about MfE stopping in 2017 was a reconnaissance artefact: MfE publishes to 2020
and LAWA publishes to December 2024.** The table is kept as written because it
is a fair picture of what reachability alone tells you.

Reconnaissance only, on 2026-09-18. **Reachability was checked; contents were
not.** Treat every line below as a lead, not a fact.

| Source | Status | Holds |
| --- | --- | --- |
| `catalogue.data.govt.nz` | **CKAN API, answers queries** | The index. 208 datasets match "waikato river", 194 match "waikato river water quality" |
| Ministry for the Environment | listed, CSV + GPKG | *River water quality, raw observations, 2013–2017*; *state, 2013–2017*; *predicted, 2009–13* |
| Waikato Regional Council | listed, CSV + XLSX | *Coasts: monitoring and reporting*, *Groundwater: monitoring and reporting* |
| Co-Lab | listed, GeoJSON + CSV + ArcGIS REST | *Waikato River Catchment*, *Catchment Area*, *Biodiversity Inventory — Waikato River Corridor* |
| LAWA (`lawa.org.nz`) | site up; no public API found | The canonical NZ water-quality portal, aggregating regional council monitoring |
| NIWA hydro web portal | site up; access terms unknown | River flow and level |

`make fetch` caches the catalogue records for these queries into
`.cache/catalogue/`. Read those before choosing anything.

### 3.2 What must be established before anything is designed

In order. Each is cheap and each can kill a design.

1. **Is there a time series of measurements at identified sites on the Waikato
   River itself** — not modelled, not regional averages — and how many sites,
   how far apart, over what period? The whole premise is change *along* the
   river. If the sites are sparse or clustered, the premise needs rethinking,
   not the drawing.
2. **Can each site be placed on the river by distance downstream?** Coordinates
   are not enough on their own; they have to be projected onto the river's line.
   The catchment geometry above may give that line, or it may need deriving.
3. **Which measures, and are they comparable along the length?** Nitrogen,
   phosphorus, *E. coli*, clarity, turbidity, temperature are the usual set.
   Some are meaningful as a trend downstream and some are not.
4. **How current is it?** MfE's headline river datasets above end in 2017. A
   site about a living river that stops eight years ago is a different site, and
   it may be that the councils publish more recent data than the ministry does.
5. **Licence, per source.** The siblings both carry a credits page because
   attribution is a condition and not a courtesy. NZ government data is usually
   CC BY 4.0, which is generous — but *usually* is not a licence, and it must be
   checked per dataset and written down.

### 3.3 Something this subject has that a dataset will not tell you

The Waikato River is not only an environmental subject. It has statutory
standing and deep significance to Waikato-Tainui and other iwi, and there is a
co-management settlement and a vision-and-strategy document that governs it.
**This has not been researched and nothing here should be asserted about it
until it has been.** It is flagged in the spec rather than left to be discovered
because a site whose stated aim is "understand how important this river is",
built only from nitrogen concentrations, would be telling a fraction of the
story and would not know it.

## 4. Information architecture — SETTLED 2026-10-06

Two pages and a colophon, in F1 Analysis's shape.

- **The landing page** is F1's: eyebrow, a thin display title, a lead, one pill
  button into the thing worth doing, the numbers on a hairline, three-up, and
  nothing under that (cut 2026-10-06 at the owner's request). What the data
  cannot say lives on the sources page.
- **The journey** is F1's race replay turned into a map. A full-screen dark
  instrument: thin bar above with the clock-style readout, a stage, thin bar
  below with the controls. The stage is a web map laid out as any web map is —
  full bleed, no chrome — but not one you drive: there is play and there is
  pause. A boat follows the river from its true head on Ruapehu (2026-10-06;
  it started on Lake Taupō off the township until then) to Port Waikato and out
  to sea. North is always up (2026-10-06); the camera sets the
  boat back from the middle, opposite the way it is heading, so the view is of
  the river to come, and at the end pulls back to the whole river.
- **The ledger** sits over the right of the map as a persistent panel: the
  kilometre; nitrogen and phosphorus as multiples of Taupō's, and clarity in
  metres, all from the last site passed and named; the chart revealed as the
  boat goes; and each reach's verdict as it is left behind.
- **The stops** (2026-10-06). The journey brakes to rest at each chapter's
  place and its whole passage fades in as a card in the middle of the screen;
  "Continue the journey" fades it out as the boat pulls away. The first card,
  Ruapehu, is read while the boat is already moving off the mountain under a
  lighter scrim; if it is still up when the boat reaches the Lake Taupō stop,
  it turns into that card in place and the boat stops there. An Autoplay box, remembered per browser, makes every card
  after it close itself after ten seconds, with a countdown along its foot.

**The comparison is nutrients against clarity** (2026-10-06, replacing people
against nitrogen). Above a surface line, nitrogen and phosphorus rise; below it,
the water you can see into closes in, coloured by its clarity. The link is
WRC's, and is said as theirs: the river's algae are nutrient-limited (TR
2018/44), algae take about half the clarity lost between the gates and
Ngāruawāhia, and below it silt takes about twice as much as algae (TR 2015/13).
The sites show the two moving together; they do not show one causing the other
site by site, and the page does not say they do. People stay on the map, as gold
discs, and on the landing page. E. coli was taken off the site on 2026-10-06 at
the owner's request.

## 5. Build

Same shape as the siblings, and the pipeline is deliberately dependency-free —
a pipeline that needs a virtualenv is one that stops working.

```bash
make fetch     # sources -> .cache/
make emit      # -> canonical JSON in site/data/
make verify    # check the emitted JSON against facts it did not produce
make data      # all three
make build     # Astro + Pagefind, then check every internal link
```

`emit.py` is not written, and `verify.py` reports that it has nothing to check.
Both are honest about it. `check_site.py` came over intact and already works.

Emitted JSON is **canonical** — sorted keys, tight separators — so a rebuild
that changes nothing is byte-identical and `git status` tells you whether the
source moved. Emitted data is **committed**, so the site builds from the
repository alone and CI never touches a council's server.

## 6. Decisions taken, and what is open

**Taken:**

1. **The subject** — the Waikato River, source to sea, on a distance-downstream
   spine. §2.
2. **The stack** — Astro, static, Python pipeline with no dependencies.
   Inherited and proven twice.

   **Revised again 2026-10-06: three.js is gone and MapLibre GL is in its
   place**, with map tiles fetched at runtime from OpenFreeMap. The note below
   is kept because the reasoning about the rule still holds.

   **Revised 2026-09-18: the site now has one runtime dependency, three.js.**
   This was a decision taken deliberately and against the inherited rule, so it
   is recorded rather than quietly absorbed. The brief was an Animal Crossing
   look — perspective camera, real models, soft shading, depth of field — and
   that is a renderer's job. Build-time SVG was tried first and got a long way,
   but it cannot do perspective, and a flat-shaded axonometric drawing is a
   different thing from a place you travel through.

   What it costs: ~670 KB of JavaScript, and a page that needs WebGL. What the
   rule was protecting — a pipeline that still runs in five years — is untouched,
   because the Python side still has no dependencies at all and the data is
   still committed.
3. **The data comes before the design.** §3.

4. **The look** — F1 Analysis's, unchanged in its tokens: the light editorial
   page for the landing, the dark instrument for the journey. The map is
   OpenStreetMap restyled into the instrument palette with every tile label off
   (`site/src/lib/mapstyle.ts`); the only words on it are the site's. Earlier
   looks — an isometric SVG diorama, then a three.js world after *Animal
   Crossing* — were built and replaced at the owner's direction.

**Open:** whether the river needs a second page; whether flow above Hamilton can
be found at all; and whether load — concentration × discharge, the number that
says what the river delivers to the sea — is reachable without it.
