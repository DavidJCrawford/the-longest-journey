import type { APIRoute } from 'astro';
import { iconPng } from '@lib/icon-png';

export const GET: APIRoute = () =>
  new Response(iconPng(32), { headers: { 'Content-Type': 'image/png' } });
