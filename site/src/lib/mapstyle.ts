/** The map, drawn in the F1 Analysis instrument palette.
 *
 *  OpenStreetMap through OpenFreeMap's vector tiles — the OpenMapTiles schema,
 *  no key, no request limit — restyled from scratch so the base map sits back
 *  the way F1's replay stage does: near-black land, water a shade off it, roads
 *  as faint hairlines. The river and the people on it are the only things that
 *  should catch the eye, and both are drawn on top of this by the journey.
 *
 *  Every tile label is off. The only words on the map are the ones the journey
 *  puts there, set in the site's own type, so the reader is never reading a
 *  street name when they should be reading a population.
 *
 *  Colours are the design tokens converted to hex, because MapLibre does not
 *  read OKLCH. The token each one comes from is named beside it.
 */
import type { StyleSpecification } from 'maplibre-gl';

export const C = {
  land: '#171717',          // between --ks-instrument and --ks-instrument-deep
  wood: '#181d19',          // the land, a breath greener
  urban: '#2a2620',         // the land, warmed towards --ks-kinpaku: where people live
  water: '#152f3c',         // oklch(29% 0.04 232)
  waterLine: '#255367',     // oklch(42% 0.06 228): streams and tributaries
  roadMajor: '#3d3d3d',
  roadMinor: '#2b2b2b',
  building: '#292929',
  river: '#4fccd9',         // oklch(78% 0.11 205): the journey's river
  people: '#ffba00',        // --ks-kinpaku
  peopleDeep: '#9f7d45',    // --ks-kinpaku-deep
  text: '#e8e8e8',          // --ks-instrument-text
  muted: '#989898',         // --ks-instrument-muted
  deep: '#0f0f0f',          // --ks-instrument-deep
  rock: '#201f1e',          // the land, a breath lighter: bare volcanic ground
  ice: '#3b4348',           // oklch(37% 0.012 230): Ruapehu's glaciers and snowfields
} as const;

export function mapStyle(): StyleSpecification {
  return {
    version: 8,
    sources: {
      omt: { type: 'vector', url: 'https://tiles.openfreemap.org/planet' },
    },
    layers: [
      { id: 'land', type: 'background', paint: { 'background-color': C.land } },

      { id: 'wood', type: 'fill', source: 'omt', 'source-layer': 'landcover',
        filter: ['in', ['get', 'class'], ['literal', ['wood', 'forest']]],
        paint: { 'fill-color': C.wood } },

      /* The mountain the river starts on. Without these Ruapehu is the same
         near-black as a paddock; with them the bare upper slopes and the ice on
         the summit plateau read as the mountain they are. */
      { id: 'rock', type: 'fill', source: 'omt', 'source-layer': 'landcover',
        filter: ['in', ['get', 'class'], ['literal', ['rock', 'sand']]],
        paint: { 'fill-color': C.rock } },
      { id: 'ice', type: 'fill', source: 'omt', 'source-layer': 'landcover',
        filter: ['==', ['get', 'class'], 'ice'],
        paint: { 'fill-color': C.ice, 'fill-opacity': 0.9 } },

      /* Where people live, warmed towards the colour the people are drawn in.
         Hamilton reads as a gold-tinged footprint before its number appears. */
      { id: 'urban', type: 'fill', source: 'omt', 'source-layer': 'landuse',
        filter: ['in', ['get', 'class'], ['literal', ['residential', 'suburb', 'neighbourhood', 'commercial', 'retail']]],
        paint: { 'fill-color': C.urban, 'fill-opacity': 0.9 } },

      { id: 'water', type: 'fill', source: 'omt', 'source-layer': 'water',
        paint: { 'fill-color': C.water } },

      { id: 'waterway', type: 'line', source: 'omt', 'source-layer': 'waterway',
        paint: {
          'line-color': C.waterLine,
          'line-width': ['interpolate', ['linear'], ['zoom'], 9, 0.4, 14, 1.4, 16, 2.4],
        } },

      { id: 'building', type: 'fill', source: 'omt', 'source-layer': 'building', minzoom: 14,
        paint: { 'fill-color': C.building, 'fill-opacity': 0.8 } },

      { id: 'road-minor', type: 'line', source: 'omt', 'source-layer': 'transportation', minzoom: 12,
        filter: ['in', ['get', 'class'], ['literal', ['minor', 'service', 'tertiary']]],
        layout: { 'line-cap': 'round', 'line-join': 'round' },
        paint: {
          'line-color': C.roadMinor,
          'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.4, 16, 2.2],
        } },

      { id: 'road-major', type: 'line', source: 'omt', 'source-layer': 'transportation', minzoom: 8,
        filter: ['in', ['get', 'class'], ['literal', ['motorway', 'trunk', 'primary', 'secondary']]],
        layout: { 'line-cap': 'round', 'line-join': 'round' },
        paint: {
          'line-color': C.roadMajor,
          'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.5, 13, 1.2, 16, 3.4],
        } },

      { id: 'rail', type: 'line', source: 'omt', 'source-layer': 'transportation', minzoom: 11,
        filter: ['==', ['get', 'class'], 'rail'],
        paint: { 'line-color': C.roadMinor, 'line-width': 0.8, 'line-dasharray': [3, 2] } },
    ],
  };
}
