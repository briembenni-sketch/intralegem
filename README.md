# Intra Legem

Vefsíða Intra Legem slf. — sýniseintak.

- `index.html` — öll síðan (HTML, CSS og JS í einni skrá), íslenska og enska.
- `assets/` — myndir.

Opnaðu `index.html` í vafra til að skoða.

## Merki og veggmynd

- `assets/brand/` — merki Intra Legem (IL-skjöldur + orðmerki) í SVG: `logo-stacked.svg`, `logo-horizontal.svg`, `mark.svg`.
- `assets/wall-{wide,tall}-{sun,shade}.webp` — merkið á múrvegg, í sól og skugga. Síðan blandar lögunum saman með CSS-grímu svo sólargeislinn færist yfir vegginn.
- `assets/fonts/` — Fraunces (fyrirsagnir, sama letur og í merkinu) og Schibsted Grotesk (meginmál), hýst á síðunni sjálfri.
- `tools/brand/` — skriftur sem búa til merkið og veggmyndina
  (`logo.py` → SVG, `rastermask.js` → maski, `render.py` → mynd; 6. viðfang = messingmaski, `SUN_MODE=full|none` fyrir sól/skugga-lög).
  Letur: Fraunces (SOFT) og Gelasio Italic frá Google Fonts.
