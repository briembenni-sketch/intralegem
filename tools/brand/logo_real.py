"""Outline the firm's supplied logo (assets/brand/source/intra-legem-logo-original.svg)
into font-independent SVGs for the site and the 3D wall render.

The original sets its text in Georgia; we outline with Gelasio (metric-compatible
with Georgia, OFL). Hairline strokes are converted to filled shapes; small-size
variants get heavier rules so they survive at header/favicon sizes.

    python3 logo_real.py FONT_DIR OUT_DIR
"""
import sys, re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FD, OUT = sys.argv[1], sys.argv[2]
F_R, F_I = f'{FD}/gelasio-r.ttf', f'{FD}/gelasio-i.ttf'
GREEN, BRASS = '#243B30', '#9A7C39'
_f = {}
def font(p):
    if p not in _f:
        t = TTFont(p)
        from fontTools.ttLib.removeOverlaps import removeOverlaps
        removeOverlaps(t); _f[p] = t
    return _f[p]

def text(p, s, size, cx, base, track=0.0):
    """Outline s centred on cx (tracking between glyphs, not after the last)."""
    ft = font(p); gs = ft.getGlyphSet(); cm = ft.getBestCmap(); k = size / ft['head'].unitsPerEm
    names = [cm[ord(c)] for c in s]
    adv = [gs[n].width * k for n in names]
    w = sum(adv) + track * (len(s) - 1)
    x = cx - w / 2; pen = SVGPathPen(gs); bp = BoundsPen(gs)
    for n, a in zip(names, adv):
        gs[n].draw(TransformPen(pen, (k, 0, 0, -k, x, base)))
        gs[n].draw(TransformPen(bp, (k, 0, 0, -k, x, base)))
        x += a + track
    return pen.getCommands(), bp.bounds

def ring(x, y, w, h, sw):
    o, i = sw / 2, sw / 2
    return (f'M{x-o} {y-o}H{x+w+o}V{y+h+o}H{x-o}Z'
            f'M{x+i} {y+i}V{y+h-i}H{x+w-i}V{y+i}Z')
def hline(x1, x2, y, sw): return f'M{x1} {y-sw/2}H{x2}V{y+sw/2}H{x1}Z'
def circle(cx, cy, r): return f'M{cx-r} {cy}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0Z'
TRIS = 'M54 36H62L58 44Z M206 36H198L202 44Z M54 148H62L58 140Z M206 148H198L202 148Z'.replace('L202 148Z', 'L202 140Z')

def parts(outer=1.0, inner=0.5, rule=0.5, badge_text=True, sub=True):
    g, b = [], [TRIS]
    g.append(ring(40, 22, 180, 140, outer))
    g.append(ring(48, 30, 164, 124, inner))
    d, _ = text(F_I, 'IL', 62, 130, 108); g.append(d)
    b += [hline(78, 118, 128, rule), circle(130, 128, 1.6), hline(142, 182, 128, rule)]
    if badge_text:
        d, _ = text(F_R, 'INTRA LEGEM', 11, 130, 148, 4); g.append(d)
    if sub:
        d, _ = text(F_R, 'LÖGMANNSSTOFA', 9, 130, 188, 4); g.append(d)
        d, _ = text(F_R, 'LAW FIRM', 7.5, 130, 206, 4.5); b.append(d)
    return ' '.join(g), ' '.join(b)

def rnd(s): return re.sub(r'-?\d+\.\d{3,}', lambda m: ('%.2f' % float(m.group())).rstrip('0').rstrip('.'), s)
def svg(vb, g, b, gfill='currentColor', bfill=BRASS, title='Intra Legem'):
    return rnd(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}">'
               f'<path fill="{gfill}" fill-rule="evenodd" d="{g}"/><path class="brass" fill="{bfill}" d="{b}"/></svg>\n')

# full lockup (as supplied): badge + LÖGMANNSSTOFA / LAW FIRM
g, b = parts()
open(f'{OUT}/logo-full.svg', 'w').write(svg('38 20 184 190', g, b))
open(f'{OUT}/logo-full-green.svg', 'w').write(svg('38 20 184 190', g, b, GREEN))
# badge only (frame with IL + INTRA LEGEM), heavier rules for mid sizes
g, b = parts(1.6, 0.9, 0.8, True, False)
open(f'{OUT}/logo-badge.svg', 'w').write(svg('38 20 184 144', g, b))
# small mark (frame + IL), heavy rules for header/favicon
g, b = parts(3.2, 1.8, 0, False, False)
b = TRIS
open(f'{OUT}/mark.svg', 'w').write(svg('37 19 186 146', g, b, GREEN))
open(f'{OUT}/mark-current.svg', 'w').write(svg('37 19 186 146', g, b))

# horizontal header lockup: small mark + INTRA LEGEM / LÖGMANNSSTOFA
mh = 146; scale = 44 / mh
mg = g  # mark geometry in logo units
dW, bW = text(F_R, 'INTRA LEGEM', 15.5, 0, 0, 4.2)
wW = bW[2] - bW[0]
dS, bS = text(F_R, 'LÖGMANNSSTOFA', 8.2, 0, 0, 3.4)
wS = bS[2] - bS[0]
tx = 186 * scale + 12
dW, _ = text(F_R, 'INTRA LEGEM', 15.5, tx + wW / 2, 22, 4.2)
dS, _ = text(F_R, 'LÖGMANNSSTOFA', 8.2, tx + wS / 2, 36, 3.4)
Wtot = tx + max(wW, wS) + 1
h = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wtot:.1f} 44" role="img" aria-label="Intra Legem">'
     f'<g transform="translate({-37*scale:.3f} {-19*scale:.3f}) scale({scale:.5f})">'
     f'<path fill="currentColor" fill-rule="evenodd" d="{mg}"/><path class="brass" fill="{BRASS}" d="{TRIS}"/></g>'
     f'<path fill="currentColor" d="{dW}"/><path class="brass" fill="{BRASS}" d="{dS}"/></svg>\n')
open(f'{OUT}/logo-horizontal.svg', 'w').write(rnd(h))

# wall-sign sources for Blender: sturdier rules, separate files per material
g, b = parts(2.2, 1.3, 1.1, True, True)
open(f'{OUT}/wall-green.svg', 'w').write(svg('38 20 184 190', g, 'M0 0Z', '#000000', '#000000'))
open(f'{OUT}/wall-brass.svg', 'w').write(svg('38 20 184 190', 'M0 0Z', b, '#000000', '#000000'))
print('ok')
