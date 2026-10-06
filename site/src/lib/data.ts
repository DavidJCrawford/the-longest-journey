/** Read the emitted data at build time.
 *
 *  site/data/ is committed (HANDOFF §3), so this is a filesystem read during the
 *  build and nothing is fetched at runtime. __DATA_DIR__ is injected by
 *  astro.config.mjs because import.meta.url inside src/lib points at the bundled
 *  chunk after build, not at this file.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

declare const __DATA_DIR__: string;

const read = <T>(name: string): T => JSON.parse(readFileSync(join(__DATA_DIR__, name), 'utf8')) as T;

/** A [lon, lat] pair. */
export type Point = [number, number];

export interface River {
  length_km: number;
  rec2_lengthdown_km: number;
  source_elevation_m: number;
  gates_km: number;
  simplify_tolerance_m: number;
  vertices_full: number;
  line: Point[];
  /** Real distance downstream, in km, at each vertex of `line`. */
  line_km: number[];
  lake_taupo: Point[];
  catchment_km2: number;
  profile: { km: number; catchment_km2: number; elev_m: number }[];
}

export interface Station {
  site: string; lawa_id: string; agency: string;
  lat: number; lon: number; samples: number;
  first: string; last: string; km: number; offset_m: number;
}

export interface Measure {
  key: string; label: string; unit: string;
  direction: 'up' | 'down'; censored: number;
  points: { km: number; site: string; n: number; median: number; p25: number | null; p75: number | null }[];
}

export interface Landmarks {
  dams: { name: string; km: number; offset_m: number; lat: number; lon: number }[];
  towns: { name: string; km: number; offset_m: number; population: number | null; lat: number; lon: number }[];
  flow: {
    station: string; km: number; offset_m: number; lat: number; lon: number;
    mean_cumecs: number; catchment_km2: number; record_from: string;
    highest: [number, string]; lowest: [number, string];
  }[];
  flow_asof: string;
  doc: { name: string; km: number; offset_km: number; url: string }[];
}

export const river = (): River => read<River>('river.json');
export const stations = (): Station[] => read<Station[]>('stations.json');
export const measures = (): Measure[] => read<Measure[]>('measures.json');
export const landmarks = (): Landmarks => read<Landmarks>('landmarks.json');

export interface Settlement {
  slug: string; name: string; population: number; year: string;
  km: number; offset_km: number; on_river: boolean;
  lat: number; lon: number; url: string;
}

export interface Reach {
  name: string; span: string; from_site: string; to_site: string;
  from_km: number; to_km: number; people: number;
  /** Median at the reach's first and last site, per measure. */
  change: Record<'total_nitrogen' | 'e_coli' | 'total_phosphorus' | 'clarity', [number | null, number | null]>;
}

export interface Journey {
  /** The river's true head on Ruapehu, where the journey starts. */
  start: [number, number];
  /** Ruapehu's summit, [lon, lat]. */
  summit: [number, number];
  /** OSM's names for the water above the lake, as [from km, to km, name]. */
  upper_names: [number, number, string][];
  /** Where the journey is crossing Lake Taupō, in km. */
  lake_crossing_km: [number, number];
  /** [lon, lat, km downstream] per vertex. */
  line: [number, number, number][];
  simplify_tolerance_m: number;
  osm_relation: number; osm_tongariro_relation: number; osm_end_km: number; coast_km: number; offshore_km: number;
  on_river_km: number;
  settlements: Settlement[];
  people_on_river: number;
  reaches: Reach[];
}

export const journey = (): Journey => read<Journey>('journey.json');
