/** A smooth curve through the monitoring sites that never overshoots them.
 *
 *  The water changes along the whole length between two sites, not at the
 *  sites, so the chart draws each measure as a curve rather than steps (the
 *  owner's call, 2026-10-06). The curve is monotone cubic interpolation — the
 *  same rule as d3's curveMonotoneX: between two readings it only ever moves
 *  from one towards the other, so it can never show a peak or a dip that no
 *  site measured. Every number printed in the panel is still a site's reading.
 *
 *  No imports, so the chart (on the server) and the panel's moving dots (in the
 *  browser) use exactly the same curve.
 */
export type Pt = [number, number];

const sign = (v: number) => (v < 0 ? -1 : 1);

/** Tangents at each point. */
export function slopes(p: Pt[]): number[] {
  const n = p.length;
  if (n < 2) return p.map(() => 0);
  const h = (i: number) => p[i + 1][0] - p[i][0];
  const s = (i: number) => (p[i + 1][1] - p[i][1]) / h(i);
  const m = new Array<number>(n);
  for (let i = 1; i < n - 1; i++) {
    const s0 = s(i - 1), s1 = s(i), h0 = h(i - 1), h1 = h(i);
    const q = (s0 * h1 + s1 * h0) / (h0 + h1);
    m[i] = (sign(s0) + sign(s1)) * Math.min(Math.abs(s0), Math.abs(s1), 0.5 * Math.abs(q)) || 0;
  }
  // Ends: the one-sided estimate, held to the same no-overshoot rule.
  m[0] = n > 2 ? (3 * s(0) - m[1]) / 2 : s(0);
  m[n - 1] = n > 2 ? (3 * s(n - 2) - m[n - 2]) / 2 : s(n - 2);
  if (sign(m[0]) !== sign(s(0))) m[0] = 0;
  if (sign(m[n - 1]) !== sign(s(n - 2))) m[n - 1] = 0;
  return m;
}

/** The curve's value at x; held flat beyond the first and last points. */
export function valueAt(p: Pt[], m: number[], x: number): number {
  if (x <= p[0][0]) return p[0][1];
  if (x >= p[p.length - 1][0]) return p[p.length - 1][1];
  let i = 0;
  while (p[i + 1][0] < x) i++;
  const [x0, y0] = p[i], [x1, y1] = p[i + 1];
  const h = x1 - x0, t = (x - x0) / h, t2 = t * t, t3 = t2 * t;
  return (2 * t3 - 3 * t2 + 1) * y0 + (t3 - 2 * t2 + t) * h * m[i]
    + (-2 * t3 + 3 * t2) * y1 + (t3 - t2) * h * m[i + 1];
}

/** The curve as SVG cubic segments, given the chart's own x and y scales.
 *  Each Hermite piece is exactly one Bézier: the handles sit a third of the
 *  way along, on the tangents. Starts with M unless `join` is set. */
export function pathD(p: Pt[], m: number[], X: (x: number) => number, Y: (y: number) => number,
                      join = false): string {
  const f = (v: number) => v.toFixed(1);
  let d = `${join ? 'L' : 'M'}${f(X(p[0][0]))} ${f(Y(p[0][1]))}`;
  for (let i = 0; i < p.length - 1; i++) {
    const [x0, y0] = p[i], [x1, y1] = p[i + 1];
    const h = (x1 - x0) / 3;
    d += `C${f(X(x0 + h))} ${f(Y(y0 + m[i] * h))} ${f(X(x1 - h))} ${f(Y(y1 - m[i + 1] * h))} ${f(X(x1))} ${f(Y(y1))}`;
  }
  return d;
}
