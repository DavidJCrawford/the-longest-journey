/** The mark as a PNG, for browsers and home screens that will not take an SVG
 *  icon. Drawn here rather than shipped as a file so it comes from the same
 *  data as everything else (lib/logo.ts). Build-time only: it uses node:zlib.
 */
import { deflateSync } from 'node:zlib';
import { logoStops } from './logo';

const CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();
const crc32 = (b: Uint8Array) => {
  let c = 0xffffffff;
  for (const x of b) c = CRC[(c ^ x) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};
const chunk = (type: string, data: Uint8Array) => {
  const out = new Uint8Array(12 + data.length);
  const dv = new DataView(out.buffer);
  dv.setUint32(0, data.length);
  out.set(new TextEncoder().encode(type), 4);
  out.set(data, 8);
  dv.setUint32(8 + data.length, crc32(out.subarray(4, 8 + data.length)));
  return out;
};

/** A size×size RGBA PNG of the circle, inset by `pad` pixels on a background
 *  (transparent unless given), antialiased by 4×4 supersampling. */
export function iconPng(size: number, pad = 0, background?: [number, number, number]): ArrayBuffer {
  const stops = logoStops().map((s) => ({
    at: s.at, rgb: [1, 3, 5].map((i) => parseInt(s.colour.slice(i, i + 2), 16)),
  }));
  const colourAt = (t: number) => {
    if (t <= stops[0].at) return stops[0].rgb;
    for (let i = 1; i < stops.length; i++) if (t <= stops[i].at) {
      const a = stops[i - 1], b = stops[i], u = (t - a.at) / (b.at - a.at);
      return a.rgb.map((v, j) => v + (b.rgb[j] - v) * u);
    }
    return stops[stops.length - 1].rgb;
  };
  const r = size / 2 - pad, c = size / 2, SS = 4;
  const raw = new Uint8Array(size * (size * 4 + 1));
  for (let y = 0; y < size; y++) {
    raw[y * (size * 4 + 1)] = 0;
    for (let x = 0; x < size; x++) {
      let cover = 0;
      for (let sy = 0; sy < SS; sy++) for (let sx = 0; sx < SS; sx++) {
        const px = x + (sx + 0.5) / SS - c, py = y + (sy + 0.5) / SS - c;
        if (px * px + py * py <= r * r) cover++;
      }
      const a = cover / (SS * SS);
      const [cr, cg, cb] = colourAt((x + 0.5 - (c - r)) / (2 * r));
      const o = y * (size * 4 + 1) + 1 + x * 4;
      if (background) {
        raw[o] = Math.round(background[0] + (cr - background[0]) * a);
        raw[o + 1] = Math.round(background[1] + (cg - background[1]) * a);
        raw[o + 2] = Math.round(background[2] + (cb - background[2]) * a);
        raw[o + 3] = 255;
      } else {
        raw[o] = Math.round(cr); raw[o + 1] = Math.round(cg); raw[o + 2] = Math.round(cb);
        raw[o + 3] = Math.round(a * 255);
      }
    }
  }
  const ihdr = new Uint8Array(13);
  const dv = new DataView(ihdr.buffer);
  dv.setUint32(0, size); dv.setUint32(4, size);
  ihdr.set([8, 6, 0, 0, 0], 8);
  const sig = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]);
  const parts = [sig, chunk('IHDR', ihdr), chunk('IDAT', new Uint8Array(deflateSync(raw))), chunk('IEND', new Uint8Array())];
  const out = new Uint8Array(parts.reduce((n, p) => n + p.length, 0));
  let off = 0;
  for (const p of parts) { out.set(p, off); off += p.length; }
  return out.buffer;
}
