/** Nutrients against clarity, down the river.
 *
 *  Three series along the same kilometres:
 *
 *    nitrogen    — median total nitrogen at each site, as a multiple of the
 *                  first site's, the Taupō control gates.
 *    phosphorus  — the same for total phosphorus.
 *    clarity     — median black-disc clarity at each site, in metres.
 *
 *  These are the site readings. The chart draws them as smooth curves through
 *  the sites (lib/curve.ts, the owner's call on 2026-10-06), because the water
 *  changes along each stretch rather than at the station that measures it; the
 *  curve never overshoots a reading, and every figure printed in the panel is
 *  still one site's reading.
 *
 *  What the pairing shows is that the two move together along the river, not
 *  that one causes the other site by site. The mechanism is published and is
 *  named on the page: nutrients feed the algae (WRC TR 2018/44 finds the river's
 *  algae nutrient-limited), algae account for about half the lost clarity
 *  between the gates and Ngāruawāhia, and below it silt matters about twice as
 *  much as algae (WRC TR 2015/13).
 */
import type { Journey, Measure } from './data';

type Step = [number, number][];

export interface ClaritySeries {
  x0: number; x1: number;
  nitrogen: Step;
  phosphorus: Step;
  clarity: Step;
  /** The last site with a measurement; past it the chart draws nothing. */
  lastKm: number;
  /** Where Hamilton's centre falls on the river, for the chart's marker. */
  hamiltonKm: number;
  reaches: {
    name: string; span: string; from: number; to: number;
    n: [number, number]; p: [number, number]; c: [number, number];
  }[];
  base: { n: number; p: number; c: number; site: string; cSite: string };
  top: { n: number; p: number; c: number; site: string };
}

export function claritySeries(J: Journey, M: Measure[]): ClaritySeries {
  /* The chart is of the measured river, so it starts where the lake crossing
     ends, just above the outlet — not up on Ruapehu, where nothing is sampled
     and the first hundred kilometres would be an empty quarter of the chart. */
  const x0 = J.lake_crossing_km[1];
  const x1 = J.coast_km;
  const pts = (key: string) => M.find((m) => m.key === key)!.points;
  const tn = pts('total_nitrogen'), tp = pts('total_phosphorus'), cl = pts('clarity');

  const nBase = tn[0].median, pBase = tp[0].median;
  const nitrogen: Step = tn.map((p) => [p.km, p.median / nBase]);
  const phosphorus: Step = tp.map((p) => [p.km, p.median / pBase]);
  const clarity: Step = cl.map((p) => [p.km, p.median]);

  /* The control gates have no clarity record; the first one is Reids Farm,
     900 m below. A reach starting at the gates takes its clarity from there. */
  const cAt = (km: number) => {
    let v = cl[0].median;
    for (const p of cl) { if (p.km <= km + 1e-9) v = p.median; else break; }
    return v;
  };
  const reaches = J.reaches.map((r, i) => ({
    name: r.name, span: r.span,
    from: i === 0 ? x0 : r.from_km,
    to: i === J.reaches.length - 1 ? x1 : r.to_km,
    n: r.change.total_nitrogen as [number, number],
    p: r.change.total_phosphorus as [number, number],
    c: [cAt(r.from_km), cAt(r.to_km)] as [number, number],
  }));

  const last = tn[tn.length - 1];
  return {
    x0, x1, nitrogen, phosphorus, clarity,
    lastKm: Math.max(last.km, cl[cl.length - 1].km),
    hamiltonKm: J.settlements.find((s) => s.slug === 'hamilton')!.km,
    reaches,
    base: { n: nBase, p: pBase, c: cl[0].median, site: tn[0].site, cSite: cl[0].site },
    top: { n: last.median, p: tp[tp.length - 1].median, c: cl[cl.length - 1].median, site: last.site },
  };
}
