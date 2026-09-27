# Intra Legem

Vefsíða Intra Legem slf. — sýniseintak.

- `index.html` — öll síðan (HTML, CSS og JS í einni skrá), íslenska og enska.
- `assets/` — myndir.

Opnaðu `index.html` í vafra til að skoða.

## Merki og veggmynd

- `assets/brand/` — merki Intra Legem (IL-skjöldur + orðmerki) í SVG: `logo-stacked.svg`, `logo-horizontal.svg`, `mark.svg`.
- `assets/office-{wide,mobile}.{webp,jpg}` — skrifstofa Intra Legem teiknuð í Blender (merkið á veggnum, skrifborð, bókahillur, sól inn um glugga).
- `assets/fonts/` — Fraunces (fyrirsagnir, sama letur og í merkinu) og Schibsted Grotesk (meginmál), hýst á síðunni sjálfri.
- `tools/brand/` — skriftur sem búa til merkið og veggmyndina
  (`logo.py` → SVG; `office.py` → 3D-skrifstofa í Blender/Cycles: `pip install bpy`, `python3 office.py út.png 2400 1200 wide 160`; eldri 2D-veggur: `render.py`).
  Letur: Fraunces (SOFT) og Gelasio Italic frá Google Fonts.
