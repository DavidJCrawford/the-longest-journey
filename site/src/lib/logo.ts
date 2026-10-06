/** The mark: a circle of the river's water, clear blue to brown.
 *
 *  Its gradient is the journey chart's clarity band, squeezed into a circle:
 *  the same colour at each monitoring site (lib/water.ts), in the same order,
 *  spaced as the sites are spaced down the river. So the mark is the data, not
 *  a picture of it, and it changes if the data does.
 *
 *  Used by the header (components/Logo.astro), the SVG favicon, and the PNG
 *  icons for browsers and home screens that do not take an SVG.
 */
import { measures } from './data';
import { waterColour } from './water';

export interface Stop { at: number; colour: string }

export function logoStops(): Stop[] {
  const cl = measures().find((m) => m.key === 'clarity')!.points;
  const a = cl[0].km, b = cl[cl.length - 1].km;
  return cl.map((p) => ({ at: (p.km - a) / (b - a), colour: waterColour(p.median) }));
}

/** The circle as a standalone SVG document, for the favicon. */
export function logoSvg(): string {
  const stops = logoStops().map((s) => `<stop offset="${s.at.toFixed(4)}" stop-color="${s.colour}"/>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">`
    + `<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0">${stops}</linearGradient></defs>`
    + `<circle cx="32" cy="32" r="32" fill="url(#g)"/></svg>`;
}
