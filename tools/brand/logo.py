"""Intra Legem crest logo (from the firm's existing site) -> outlined SVG lockups."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import re, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
F_R, F_I, F_IL = 'fr-r-s30.ttf', 'fr-i-w0.ttf', 'gelasio-i.ttf'
_fonts = {}
def font(f):
    if f not in _fonts: _fonts[f] = TTFont(f)
    return _fonts[f]

def text_path(f, text, size, x, y, tracking=0):
    ft = font(f); gs = ft.getGlyphSet(); cmap = ft.getBestCmap(); sc = size/ft['head'].unitsPerEm
    pen = SVGPathPen(gs); cx = x
    for ch in text:
        g = cmap[ord(ch)]; gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, cx, y))); cx += gs[g].width*sc + tracking
    return pen.getCommands(), cx - x - tracking

def ink_bounds(f, text, size):
    ft = font(f); gs = ft.getGlyphSet(); cmap = ft.getBestCmap(); sc = size/ft['head'].unitsPerEm
    bp = BoundsPen(gs); cx = 0
    for ch in text:
        g = cmap[ord(ch)]; gs[g].draw(TransformPen(bp, (1, 0, 0, 1, cx, 0))); cx += gs[g].width
    x0, y0, x1, y1 = bp.bounds
    return x0*sc, y0*sc, x1*sc, y1*sc

def frame(o, i):  # square ring as even-odd path
    return f'M{o[0]} {o[0]}H{o[1]}V{o[1]}H{o[0]}Z M{i[0]} {i[0]}V{i[1]}H{i[1]}V{i[0]}Z'

def crest(ox=0, oy=0, s=1.0):
    """Crest in a 200x200 box (matches the original SVG): double frame, brass corner triangles, italic IL."""
    x0, _, x1, _ = ink_bounds(F_IL, 'IL', 100)
    dIL, _ = text_path(F_IL, 'IL', 100, 100 - (x0 + x1)/2, 132)
    body = frame((17, 183), (23, 177)) + frame((30.5, 169.5), (33.5, 166.5)) + dIL
    tris = 'M38 38H52L45 52Z M162 38H148L155 52Z M38 162H52L45 148Z M162 162H148L155 148Z'
    t = f'translate({ox} {oy}) scale({s})'
    return (f'<path fill-rule="evenodd" fill="currentColor" transform="{t}" d="{body}"/>'
            f'<path class="brass" fill="#9A7C39" transform="{t}" d="{tris}"/>')

def wordmark(x, y, size):
    d1, w1 = text_path(F_R, 'Intra ', size, x, y)
    d2, w2 = text_path(F_I, 'Legem', size, x + w1, y)
    return d1 + d2, w1 + w2

def svg(W, H, body, pad=0):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}" '
         f'fill="currentColor">{body}</svg>')
    return re.sub(r'-?\d+\.\d{3,}', lambda m: ('%.2f' % float(m.group())).rstrip('0').rstrip('.'), s)

# stacked: crest above wordmark (signage)
WS = 80
_, ww = wordmark(0, 0, WS)
cs = 1.15; ch = 200*cs
W = max(ww, ch); gap = 30
dW, _ = wordmark((W-ww)/2, ch + gap + WS*0.72, WS)
H = ch + gap + WS*0.72 + WS*0.08
open(f'{OUT}/logo-stacked.svg', 'w').write(svg(W, H, crest((W-ch)/2, 0, cs) + f'<path d="{dW}"/>', 2))

# horizontal: crest left, wordmark right (nav/footer), matches the original site header
S = 22; cs2 = 0.2
dH, wh = wordmark(40 + 12, 20 + S*0.36, S)
open(f'{OUT}/logo-horizontal.svg', 'w').write(svg(52 + wh, 40, crest(0, 0, cs2) + f'<path d="{dH}"/>', 1))
open(f'{OUT}/mark.svg', 'w').write(svg(200, 200, crest(), 0))
print('ok', W, H)
