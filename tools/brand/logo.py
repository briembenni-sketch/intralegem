from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

def text_path(fontfile, text, size, x, y, tracking=0):
    """Return (svg path d, advance width) for text with baseline at y."""
    f = TTFont(fontfile); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    upm = f['head'].unitsPerEm; sc = size/upm
    pen = SVGPathPen(gs); cx = x
    for ch in text:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (sc,0,0,-sc,cx,y))
        gs[g].draw(tp)
        cx += gs[g].width*sc + tracking
    return pen.getCommands(), cx - x - tracking

def glyph_bounds(fontfile, ch, size):
    f = TTFont(fontfile); gs = f.getGlyphSet(); g = f.getBestCmap()[ord(ch)]
    bp = BoundsPen(gs); gs[g].draw(bp); sc=size/f['head'].unitsPerEm
    return [v*sc for v in bp.bounds]

SER='news-72-400r.ttf'; SANS='geist-500.ttf'

# ---- Mark: 100 x 120 box. Hairline corner brackets (L bottom-left, inverted L top-right) framing a Roman I.
T=3.4; ARM=36; ISZ=132
def mark(ox=0, oy=0, s=1.0, color='currentColor'):
    b = glyph_bounds(SER,'I',ISZ)   # xmin,ymin,xmax,ymax in font units scaled (y up)
    gw = b[2]-b[0]; gh = b[3]-b[1]
    gx = ox + (50 - gw/2 - b[0])*s; base = oy + (60 + gh/2)*s
    dI,_ = text_path(SER,'I',ISZ*s,gx,base)
    r = lambda x0,y0,x1,y1: f'M{ox+x0*s:.2f} {oy+y0*s:.2f}H{ox+x1*s:.2f}V{oy+y1*s:.2f}H{ox+x0*s:.2f}Z'
    d = dI + r(0,120-ARM*1.3,T,120) + r(0,120-T,ARM,120) + r(100-T,0,100,ARM*1.3) + r(100-ARM,0,100,T)
    return f'<path fill="{color}" d="{d}"/>'

def lockup_stacked():
    # mark centred above wordmark, like signage
    word_size=64; tr=15
    dW, wW = text_path(SER,'INTRA LEGEM',word_size,0,0,tr)
    W = wW; MS=1.25; mh=120*MS
    mx = (W-100*MS)/2
    out = mark(mx,0,MS)
    dW, _ = text_path(SER,'INTRA LEGEM',word_size,0,mh+56+word_size*0.68,tr)
    sub=17; dS, wS = text_path(SANS,'LÖGMANNSSTOFA',sub,0,0,sub*0.42)
    dS, _ = text_path(SANS,'LÖGMANNSSTOFA',sub,(W-wS)/2,mh+56+word_size*0.68+46,sub*0.42)
    H = mh+56+word_size*0.68+46+4
    return W, H, out + f'<path fill="currentColor" d="{dW}"/><path fill="currentColor" d="{dS}"/>'

def lockup_horizontal():
    size=30; tr=6
    m = mark(0,0,0.36)
    dW, wW = text_path(SER,'INTRA LEGEM',size,36+18,21.6+size*0.34,tr)
    return 36+18+wW, 43.2, m + f'<path fill="currentColor" d="{dW}"/>'

def svg(W,H,body,pad=0):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {W+2*pad:.1f} {H+2*pad:.1f}" fill="currentColor">{body}</svg>'

import json
W,H,b = lockup_stacked(); open('logo-stacked.svg','w').write(svg(W,H,b,2))
W2,H2,b2 = lockup_horizontal(); open('logo-horizontal.svg','w').write(svg(W2,H2,b2,1))
open('mark.svg','w').write(svg(100,120,mark(),2))
print(W,H,W2,H2)
