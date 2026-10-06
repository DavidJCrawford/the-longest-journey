# HANDOFF — The Longest Journey

Written 2026-09-18, at the end of the session that scaffolded the project, and
updated the same day once the data was settled. **Updated again 2026-10-06**,
after the visual layer was rebuilt on F1 Analysis's design. Read
[SPEC.md](SPEC.md) first, then [SOURCES.md](SOURCES.md), which is the record of
what was adopted and why.

§0 is where this is up to. §4 is what the two sibling projects paid to learn and
you should not pay again — and one of those lessons has already been paid for a
third time here, so it is worth believing.

---

## 0. Where this is up to

**The data is settled and the first page is built.** SPEC §3.2's five questions
are answered in SOURCES.md; SPEC §3.3 was researched from the legislation itself
before a word of prose was written.

What the answers turned out to be:

- **20 monitoring sites** on the mainstem, **13 with the full suite, monthly,
  January 2004 to December 2024.** LAWA publishes them and the file was released
  9 February 2026 — the spec's belief that the record stopped in 2017 was an
  artefact of checking reachability rather than contents.
- **The spine works.** NIWA's REC2 carries `LENGTHDOWN` and `NextDownID`, so the
  mainstem is *walked* rather than drawn: 443.8 km from a reach at 2,600 m on
  Ruapehu to the sea. Every site snaps within 160 m of it.
- **The premise holds, hard.** Taupō to Tuakau: total nitrogen ×10, oxidised
  nitrogen ×205, phosphorus ×14, *E. coli* ×45, clarity 7.5 m → 0.65 m.
- **The river is 338 km from the lake outlet, not 425.** The conventional figure
  measures from Ruapehu, through the Tongariro and the length of Lake Taupō.
  SPEC §2 and `scope.ts` were corrected.

`make data` reproduces everything except the four flow figures, which cannot be
fetched — SOURCES.md §1.4 says why, and it is not worth rediscovering.

**`verify.py` runs 395 checks and they pass.** The one that matters most is in
§4 below.

### What is built

```
pipeline/xlsx.py        minimal .xlsx reader — LAWA publishes Excel, and the
                        no-dependencies rule means zipfile + xml.etree
pipeline/geo.py         the spine: walk, stitch, snap, simplify
pipeline/journey.py     the boat's path, who lives along it, the three reaches
pipeline/sources.py     download the chosen sources -> .cache/
pipeline/emit.py        -> site/data/{river,stations,measures,landmarks,journey}.json
pipeline/verify.py      443 checks, all against facts it did not produce
site/src/lib/mapstyle.ts             OSM in the F1 instrument palette
site/src/lib/clarity.ts              the nutrients-against-clarity series
site/src/lib/water.ts                clarity -> the colour of the water
site/src/lib/chapters.ts             the places passed, each claim sourced
site/src/components/ClarityChart.astro the chart, revealed as the boat goes
site/src/pages/index.astro           landing, after F1's
site/src/pages/journey/index.astro   F1's replay, as a map
site/src/pages/sources/index.astro   sources, method, limits — after F1's credits
```

**Two pages and a colophon, on F1 Analysis's design.** The landing page is F1's
landing; the journey is F1's race replay with the circuit replaced by a web map
and the running order replaced by a ledger. SPEC §4 has the shape.

**The argument is nutrients against clarity** (2026-10-06; it was people against
nitrogen until then — SPEC §4). Nitrogen ×10 and phosphorus ×14 from the Taupō
gates to Tuakau; clarity 7.47 m at Reids Farm to 0.65 m. Of the 5.8 m lost by the
Narrows above Hamilton, 5.5 m is gone by Karāpiro. The colour of the water on the
map and in the chart is keyed to clarity, not measured (lib/water.ts) — the one
thing drawn between sites. E. coli was shown until 2026-10-06, when the owner
asked for it to come off the site; the data is still emitted (measures.json,
journey.json reach changes). SOURCES.md §1.10 records what the brief claimed that
the data does not support, and what the site says instead.

The owner has lived beside the river in central Hamilton all their life; the
clear upper river against the green-brown water through the city is the thing
they want seen. The data supports it — say it with the data's numbers.

**MapLibre GL 6 and OpenFreeMap tiles.** The tiles are fetched at runtime — the
one thing that is (SOURCES.md §1.8). three.js is gone.

**Weight:** the journey is about 450 KB gzipped plus tiles — 274 KB of it MapLibre
and 141 KB its worker. The landing page does not load the map library and is
under 20 KB.

### What is not built

- **Flow above Hamilton, and load.** SOURCES.md §3.
- **Turbidity.** Measured at every site but in NTU at the council's and FNU at
  NIWA's. Different instruments; excluded rather than quietly mixed.

---

## 1. What exists

```
Makefile                  fetch / sources / emit / verify / data / build / links
pipeline/fetch.py         reconnaissance — asks data.govt.nz what exists
pipeline/sources.py       ingest — LAWA, REC2, OSM, the river, Stats NZ, places
pipeline/journey.py       the journey: path, settlements, reaches
pipeline/emit.py          -> site/data/, canonical JSON, committed
pipeline/verify.py        443 checks against facts it did not produce
pipeline/check_site.py    carried over intact, follows every internal link
site/src/styles/          tokens.css + base.css, inherited unchanged
site/src/layouts/Base.astro  F1's masthead; `chrome={false}` for the journey
.github/workflows/        deploy.yml — Pages, ignores Docs/** and *.md
```

**Two ingest steps, not one.** `make fetch` asks the catalogue what exists and
caches the answers; `make sources` downloads what SOURCES.md says was chosen.
They are separate because the first is for deciding and the second is for
building, and conflating them made it too easy to re-browse instead of re-read.

`verify.py` returns 0 *only* while `site/data/` is empty. It is no longer in
that state, so every check has to pass.

**Live** at https://davidjcrawford.github.io/the-longest-journey/, from
`DavidJCrawford/the-longest-journey`. The repository's name is the base path:
the Pages workflow passes it in as `BASE_PATH`, and `astro.config.mjs` falls back
to the same value so a local build matches. Rename one, rename both.

## 2. What to do next, in order

**1. Watch one full journey in a real browser.** It was verified here by seeking
to points along the river and by stepping its logic, not by sitting through all
seven minutes from Ruapehu (halved in pace and extended to the source on
2026-10-06; `PACE` in the journey page): the browser pane this was built in stops painting whenever it
is not on screen, and MapLibre stops with it. Watch for the pace (`speedAt` in
the journey page) and the zoom schedule (`zoomAt`), which are the edit.

**2. Flow above Hamilton, and load.** SOURCES.md §3. The comparison is in
concentration, and the sources page says so; load in tonnes would show the lower
reach carrying more than its concentration rise suggests.

**3. If the tile dependency ever bites,** the way out is a Protomaps extract of
the corridor served from the repository (SOURCES.md §1.8).

## 3. Conventions carried over

- **Comments say why, not what.** This is what made the siblings' handoffs
  writable, and it is the single highest-leverage habit in either repo.
- **Commit the emitted data with the code.** The site builds from the repository
  alone; CI never fetches from anybody.
- **Canonical JSON** — sorted keys, tight separators. A no-op rebuild is
  byte-identical, so `git status` after `make emit` tells you whether the source
  moved.
- **The pipeline has no dependencies.** Python standard library only. (PIL is
  used in the siblings for one-off image work, never in a build step.)
- **Every link goes through one helper.** `u()` here; the siblings add a second
  for their per-entity URLs. Bypassing it is how you get 544 dead links.
- **Design tokens are inherited unchanged** from F1 via NFL. Add project
  colours as new `--enviro-*` tokens rather than editing the palette.
- **Pushing `main` deploys.** The workflow ignores `Docs/**` and `*.md`, so
  documentation commits do not rebuild the site.

## 4. Lessons from the siblings, and why each one is here

These were expensive twice. Assume they apply.

**Verify what the data holds before designing around it.** NFL Analysis: betting
lines turned out to be published only two weeks ahead, so 224 of 272 games had
none — which killed a home-page design in twenty minutes that would otherwise
have been built and thrown away. The equivalent question here is SPEC §3.2.

**Never draw across a gap.** Where the data does not say what happened between
two points, do not interpolate a line through it and let it look like a
measurement. NFL's replay *places* the ball rather than tweening it whenever the
record does not connect two positions, and says why on the page. A river profile
drawn as a smooth curve through eleven sampling sites is exactly this mistake,
and it is the most likely mistake this project will make.

**Find something the output can be checked against, and check it every build.**
Not a schema check — something the emitter did not have a hand in. NFL's
`verify.py` runs 78,429 such checks and has caught three real bugs.

Here the one that earns its keep is the **catchment cross-check**. Waikato
Regional Council publishes a catchment area for each of its four flow gauges;
NIWA's REC2 carries a cumulative catchment area for every reach of the river.
Two organisations, different methods, no shared working — and they agree to
**0.04%** at all four. That single number validates the spine, the walk down the
network, and the snapping, all at once, and it is the reason the flow snapshot
in `emit.py` is safe to commit by hand.

Its companions: the geodesic length agrees with REC2's own planar LENGTHDOWN to
0.15%; the stitched Lake Taupō outline encloses 613 km² against a published 616;
and the eight dams come out of the walk in the published downstream order.

**Say what is missing, on the page.** Both siblings carry a credits page that
states what the data cannot show, and NFL's replay says in words that it has no
player tracking. An environmental site has a stronger version of this duty: a
gap in monitoring is not the same as clean water, and the difference must be
visible.

**A cached download is a snapshot.** Re-fetch before concluding anything is
missing. This one was paid for again here: the spec recorded that the river data
stopped in 2017, and it stopped in 2017 only because reachability had been
checked and contents had not. LAWA publishes to December 2024 and released the
file in February 2026. **Reachability is not contents**, and the difference was
nearly the whole project.

**Two things may look continuous and only one of them be.** On the map the
river's *width* is drawn from catchment area, which REC2 records for every reach
— genuinely continuous, so a continuous taper says nothing the data does not.
Its *colour* is drawn from water quality, which exists at thirteen points across
338 km, so it appears only as marks at those points and the channel between them
is one flat colour. An early version had a gradient running the length of the
river; it looked far better and was inventing values for twenty-five kilometres
out of every twenty-six.

**A custom shader has to end the way three's own materials end.** A hand-written
fragment shader that just assigns `gl_FragColor` is writing display-ready values
into a linear buffer. Rendering straight to the canvas that happens to look
right, so it survived until an EffectComposer was added — and then OutputPass
encoded the water a second time and turned the river pale grey while the grass
beside it, a stock material, stayed correct. Add `<tonemapping_fragment>` and
`<colorspace_fragment>` at the end. Do **not** add the matching `_pars_` chunks:
the renderer already injects those function definitions into every fragment
shader it compiles, and redefining them fails the compile — which shows up as
the water silently not drawing, not as an error anywhere a reader would see.

And when that is fixed, every source colour will look too bright, because they
were picked against the broken pipeline. They are linear-referred: they are
meant to look too dark written down.

**The camera's angle and whether you can see the boat are different knobs.**
Height sets the pitch; how far back the camera sits decides whether the boat is
in frame at all. With the camera eleven units behind the boat and thirteen above
it, the boat sat fifty-one degrees below the horizontal while the frame reached
thirty-six — rendering perfectly, just below the bottom edge. And a fixed rig
does not survive a portrait screen: the fov is vertical, so on a phone the boat
filled a third of the width. The rig pulls back as the aspect narrows.

**Mixed geometry will not merge.** `mergeGeometries` refuses any disagreement in
the attribute set or in whether the parts are indexed, and three's primitives
disagree on both counts — icosahedrons arrive without an index, cylinders and
spheres with one. Fixing the mismatches one at a time kept finding another;
rebuilding each part with exactly position, normal and slot ended it.

**Check the brief against the data, not only the data against itself.** The
2026-10-06 brief made five claims about the river. The data supports the central
one — Hamilton holds most of the river's people and adds essentially none of its
nitrogen — and contradicts three others: the steepest nitrogen rise is upstream
of Hamilton, not below it; Hamilton does double the E. coli; and "a handful of
farmers" is three thousand dairy herds. Building the brief as written would have
meant choosing nitrogen and quietly dropping E. coli. The site showed both until
the owner removed E. coli on 2026-10-06, as an explicit editorial decision rather
than a quiet one; SOURCES.md §1.10 says why the attribution is worded as it is.

**MapLibre 6 needs its worker bundled.** It finds the worker relative to its own
module with a name built at runtime, so Vite cannot see it and does not emit it,
and once MapLibre is folded into the page bundle the file is not there. The map
never loads and says only "Worker failed to load". Import it as
`maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url`, set `worker.format: 'es'`
in the Vite config, and pass the URL to `setWorkerUrl`. MapLibre 6 also has no
default export. And pin the current major: 5.x carries a critical sanitiser
advisory, which is how this came up.

**A MapLibre expression may use `zoom` only at the top.** Nested inside a
multiplication, the layer fails validation and is dropped with nothing on the
page to say so — the population discs, the point of the closing frame, simply
were not there. Repeat the data term at each stop of a top-level interpolate.

**`npm audit fix --omit=dev` removes the dev dependencies.** Pagefind and the type
checker went with it; the build failed with exit 127 and the check hung.

**Carrying a river's last bearing out to sea can run up the beach.** The Waikato
runs north behind the Port Waikato spit before it reaches the Tasman, so the
first offshore leg went seven kilometres along the sand. The coast runs
north–south; the sea is west; the line now turns.

**Frame the moving thing, don't centre it.** A centred boat loses half the view
to river already passed, and the panel hides more. With north fixed up, the boat
is set back from the middle of the visible map opposite its (eased) heading, by
MapLibre's camera `padding`, so the view is mostly river to come.

**The chart is curves now** (2026-10-06, the owner's call): smooth monotone
curves through the sites (`lib/curve.ts`) replaced the steps, so the chart shows
the water changing along each stretch. They cannot overshoot a reading. This
retires the "never draw across a gap" rule for the chart; numbers printed in the
panel are still always one named site's reading.

**The sources page is sources and method only** (2026-10-06, the owner's call):
the colophon intro, "What this cannot tell you" and "The marks" were removed.
The limits they listed still hold — monitoring shows where the water changes,
not who changed it; nothing is drawn between sites — and the site's wording
should keep respecting them even though they are no longer listed.

**The passages are for readers, not about the site.** The owner's rule
(2026-10-06): nothing about how the site is built or checked, nothing that reads
as machine-written — no "worth pausing on", no "not X but Y", no tidy triplets.
Plain sentences, concrete facts, ecological and cultural substance, each claim
sourced and listed under its passage. Black-disc clarity is a horizontal
sighting distance: say "you can see N metres through the water", never "down".

**Stopping smoothly is one formula.** The boat brakes into each stop at a
constant deceleration: the fastest it may go with d km left is √(2ad), with a
set so that full pace comes to rest in `BRAKE_S` seconds. Below that curve it
sails on; on it, it slows to a halt exactly on the place. Every start eases up
from rest over `ACCEL_S`. The card waits 450 ms after the boat stops so the
camera has settled before it fades in.

**REC2 runs in steps.** It is traced from a terrain grid, so wherever the
journey falls back on it — the estuary tail — the line zig-zags at street zoom.
Smooth it (`TAIL_SIGMA_M`), bridge gaps with a curve whose ends follow the
water on either side (`_lead_in` off the ice, `_crossing` over the lake), and
prefer OSM's own waterways anywhere they exist:
above the lake the journey searches OSM's streams for the chain that follows
REC2, rather than drawing REC2 itself. Search from the lake up — the mapped
streams nearest REC2's head on the ice belong to other catchments.

**"Unmeasured" must not look like "clean".** The last 31 km below Tuakau first
faded to grey, and on the dark map grey reads as near-white: the river seemed to
run clear into Port Waikato, the opposite of the truth, and the owner, who knows
the place, caught it at once. It now keeps Tuakau's colour, in the same line
style as the rest (a dashed version was tried and dropped as too fussy).

**`fitBounds` adds the camera's padding to yours.** With the boat's framing
padding still on the camera, the finale's `fitBounds` asked for more padding than
a phone screen is tall and pulled back to the whole planet. The finale works out
its own zoom from projected bounds and `easeTo`s with explicit padding.

**Separate what a thing *is* from how high the land *is*.** The scene has one
vertical exaggeration, and for a while every height went through it: terrain
elevation, but also how deep the land block was drawn, how tall a conifer was,
how far a dam stood above the water. The exaggeration needed to make a 42 m
terrace visible then also made the upper river — which really does fall 2,240 m
in 106 km — plunge vertically down the screen, and turned every tree into a
spire. Elevation is now converted from metres and exaggerated once, in
`scene.ts`; everything else is specified in kilometres of world space and the
exaggeration never touches it.

**A schematic frame cannot host a true-scale object.** The valley is drawn
narrower than it is, so Lake Taupō placed at its true size and position floated
beside the river like a separate pond. It is now *measured* instead: a ray is
cast either side of the centreline, stopped at the real shore, and those two
distances become the water's half-widths — the same schematic treatment as the
rest of the valley rather than a second, inconsistent one. The river opens into
the lake and closes again, and the shore in cross section is the real shore.

**Check the composition before the detail.** The first attempt laid the river
along the isometric diagonal, where the two horizontal components cancel; 444 km
of river collapsed into a vertical sliver a few pixels wide. The world frame is
now rotated so the river's overall direction is world +x. Related: the whole
river at once does not work at any zoom — a ribbon seventy times longer than it
is broad reads as a worm — which is why the camera opens close, as a game's
does, and the rail says where you are.

**`requestAnimationFrame` is throttled when the page is not being painted.** Not
a bug, but it means a one-frame delay is not a reliable way to start a CSS
transition: a panel that was made visible and then given its `is-open` class on
the next frame simply stayed at opacity zero. Force a reflow instead.

**A figure beside a paragraph is a claim about that paragraph.** The chapter
panels originally chose their numbers by distance — nearest site upstream — and
it went wrong three ways: a chapter at kilometre 143.8 missed the site at 143.83
and showed one 37 km away; the passage about the unmonitored mouth displayed
Tuakau's readings under a sentence saying nobody measures there; and because the
*E. coli* series carries seven Hamilton sites the other measures do not, one
panel drew its nitrogen and its *E. coli* from sites 11 km apart while naming
only the first. Each chapter now names its site, and `noWater` says so where
there is none.

**When something does not add up, search for what actually happened.** Every
anomaly in the NFL data turned out to be real football described accurately.
Assume the data is right and you are wrong, first.

**Check the trivial things.** All of these cost real time:

- **`astro dev` serves stale CSS and stale data.** A scoped rule present in the
  source and in `dist` was simply absent from what the dev server handed the
  browser — three separate times in one day, once costing an hour. **Verify
  against a static server on `site/dist`, not against `astro dev`.**
- **`compressHTML` deletes a newline between text and an inline element**
  instead of collapsing it to a space, so `published by\n<a>NIWA</a>` ships as
  `published byNIWA`. It is invisible in the source. `compressHTML: false` is
  already set here for that reason.
- **An `<img>` in a baseline-aligned flex row sets the row's baseline from its
  own bottom edge**, so a logo beside a wordmark drags the masthead as it grows.
  Give the text `align-items: baseline` and the image `align-self: center`.
- **Astro's template parser cannot read `<=` inside a JSX expression**, nor a
  nested template literal inside an attribute. Both fail as *"svg has no
  corresponding closing tag"* a hundred lines away. Resolve it in frontmatter.
- **Deleting a component leaves dead library exports behind.** Sweep for them —
  and count *in-file* references before deleting, or you will remove a constant
  that looks unused from outside and is reached from within.

## 5. Careful of

- **Third-party marks.** The siblings use club logos and carry an explicit
  statement about trademarks, because a licence over data does not cover a
  trademark. Council and ministry logos are the same question here, and a koru
  or an iwi emblem is a considerably more serious one. Do not reach for either
  casually.
- **Page weight.** NFL's front page needed 32 club marks; at the publisher's
  original size that was 1.7 MB and at a display size 105 KB. Geometry is worse:
  a river's line at full resolution is large, and the simplification has to be
  deliberate and stated rather than accidental.
- **The temptation to model.** This site shows measurements. The moment it draws
  a prediction, it owes the reader a statement about whose model it is and how
  wrong it can be. NFL deleted win probability for exactly this reason: a
  model's number beside a drawing of what actually happened invites the reader
  to trust the wrong one.
