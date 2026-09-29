# Intra Legem

Vefsíða Intra Legem slf. — sýniseintak.

- `index.html` — öll síðan (HTML, CSS og JS í einni skrá), íslenska og enska.
- `assets/` — myndir.

Opnaðu `index.html` í vafra til að skoða.

## Merki og veggmynd

- `assets/brand/source/intra-legem-logo-original.svg` — upprunalegt logo stofunnar (frá Intra Legem).
- `assets/brand/` — útgáfur unnar úr því, með texta breytt í ferla (óháð letri):
  `logo-full.svg` (heild), `logo-full-green.svg`, `logo-badge.svg` (rammi), `logo-horizontal.svg` (haus),
  `mark.svg` / `mark-current.svg` (favicon og lítil notkun). Litir: grænn `#243B30`, messing `#9A7C39`.
- `assets/office-{wide,mobile}.{webp,jpg}` — skrifstofan með skiltinu, teiknuð í Blender.
- `assets/fonts/` — Fraunces og Schibsted Grotesk, hýst á síðunni sjálfri.
- `tools/brand/` — `logo_real.py` (logo → SVG-útgáfur, Gelasio í stað Georgia),
  `office.py` (3D-skrifstofa: `pip install bpy`, `python3 office.py út.png 2400 1200 wide 160`).
