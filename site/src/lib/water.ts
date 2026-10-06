/** The colour of the water, from how far you can see into it.
 *
 *  Nobody in the monitoring record measures the river's colour, so the colour
 *  drawn here is not a measurement. It is keyed to one that is — black-disc
 *  clarity, in metres — along a ramp that follows what changes the clarity:
 *  the clear blue water leaving Taupō; green as algae grow through the hydro
 *  lakes, which Waikato Regional Council puts at about half the loss of clarity
 *  between the gates and Ngāruawāhia; brown below, where it finds suspended
 *  silt about twice as important as algae (Vant, WRC TR 2015/13).
 *
 *  Used by the server-rendered chart and the map script alike, so the two
 *  always agree on what colour a metre of clarity is.
 */

/** Clarity in metres → colour. Stops in descending clarity. */
const RAMP: [number, [number, number, number]][] = [
  [8.0, [46, 155, 240]],   // Taupō blue
  [4.5, [35, 181, 196]],   // still clear, turning teal
  [2.2, [70, 181, 138]],   // the hydro lakes: green
  [1.6, [143, 176, 78]],   // Hamilton: green going olive
  [1.0, [179, 154, 72]],   // khaki
  [0.6, [168, 118, 62]],   // the lower river: brown
];

const hex = (c: number[]) => '#' + c.map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');

/** Interpolated in log-clarity, because the eye reads a drop from 2 m to 1 m
 *  as about as large as one from 8 m to 4 m. */
export function waterColour(clarity: number): string {
  const c = Math.max(RAMP[RAMP.length - 1][0], Math.min(RAMP[0][0], clarity));
  for (let i = 1; i < RAMP.length; i++) {
    const [a, ca] = RAMP[i - 1], [b, cb] = RAMP[i];
    if (c >= b) {
      const t = (Math.log(a) - Math.log(c)) / (Math.log(a) - Math.log(b));
      return hex(ca.map((v, j) => v + (cb[j] - v) * t));
    }
  }
  return hex(RAMP[RAMP.length - 1][1]);
}

/** The ramp's stops, for a legend. */
export const RAMP_STOPS = RAMP.map(([m, c]) => ({ m, colour: hex(c) }));

/** Clarity as written on the page: to the centimetre under two metres, where
 *  the readings that matter differ by centimetres; to the decimetre above. */
export const metres = (v: number) => `${v.toFixed(v < 2 ? 2 : 1)} m`;
