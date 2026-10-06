/** The site's name, in one place: the masthead, every page title and the
 *  landing page all read it from here. */
export const SITE_NAME = 'The Longest Journey';

/** What this site is about, in one place.
 *
 *  The sibling projects keep their scope here as a single constant — a season,
 *  a championship — so widening it later is one line rather than a search. The
 *  equivalent here is the catchment: everything the site draws is a measurement
 *  taken somewhere in it, and a second river would be a second entry.
 */
export const SUBJECT = {
  /** The river, source to sea. */
  name: 'Waikato River',
  /** Lake Taupō's outlet at Taupō, to the Tasman Sea at Port Waikato. */
  from: 'Taupō',
  to: 'Port Waikato',
  /** Checked 2026-09-18, and the 425 km this used to say was the wrong number
   *  for this river. 425 km is measured from the headwaters on Ruapehu, down
   *  the Tongariro and through Lake Taupō. This site starts at Taupō's outlet,
   *  and from there REC2's network says 338 km to the sea — which a geodesic
   *  sum along the same reaches independently agrees with to 0.15%. See
   *  Docs/SOURCES.md. */
  lengthKm: 338,
  /** The conventional figure, kept because readers will have met it and it is
   *  not wrong — it just measures a longer river than this one. */
  lengthKmFromSourceAboveTaupo: 425,
  region: 'Waikato',
  country: 'New Zealand',
} as const;
