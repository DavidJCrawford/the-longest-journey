import type { APIRoute } from 'astro';
import { iconPng } from '@lib/icon-png';

/* iOS fills a transparent icon with black, so the circle sits on the site's
   paper colour with a margin, the way home-screen icons are drawn. */
export const GET: APIRoute = () =>
  new Response(iconPng(180, 22, [248, 248, 248]), { headers: { 'Content-Type': 'image/png' } });
