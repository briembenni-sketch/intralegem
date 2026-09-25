import numpy as np, sys
from scipy import ndimage as nd
from PIL import Image
rng = np.random.default_rng(7)
OUT = sys.argv[1]; W, H = int(sys.argv[2]), int(sys.argv[3]); MASK = sys.argv[4]; LOGO_Y = float(sys.argv[5]); BRASS = sys.argv[6] if len(sys.argv) > 6 else None

def fbm(h, w, beta, seed):
    r = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fx**2 + fy**2); f[0, 0] = 1
    spec = (r.normal(size=f.shape) + 1j*r.normal(size=f.shape)) / f**(beta/2)
    spec[0, 0] = 0
    n = np.fft.irfft2(spec, s=(h, w))
    return (n - n.mean()) / n.std()

def norm01(a): return (a - a.min()) / (a.max() - a.min())

# ---------------- Wall height field (lime plaster, trowelled) ----------------
big   = fbm(H, W, 3.2, 1)                     # broad undulation
mid   = fbm(H, W, 2.2, 2)                     # mottling
fine  = nd.gaussian_filter(rng.normal(size=(H, W)), 0.8)
fine /= fine.std()
# trowel strokes: anisotropic noise at a few orientations, blended by low-freq masks
strokes = np.zeros((H, W))
for i, ang in enumerate([18, -24, 62]):
    pad = int(0.35*max(H, W))
    n = rng.normal(size=(H+2*pad, W+2*pad)).astype(np.float32)
    n = nd.rotate(n, ang, reshape=False, order=1)
    n = nd.gaussian_filter(n, (1.6, 26))
    n = nd.rotate(n, -ang, reshape=False, order=1)[pad:pad+H, pad:pad+W]
    n /= n.std()
    m = norm01(nd.gaussian_filter(fbm(H, W, 3.5, 10+i), 2))
    strokes += n * m**2
strokes /= strokes.std()
# pits / pores
pits = np.zeros((H, W)); idx = rng.integers(0, H*W, 9000)
pits.flat[idx] = rng.uniform(0.5, 1.6, idx.size)
pits = nd.gaussian_filter(pits, 1.3); pits /= pits.max()
# ridges where trowel edges dragged
ridge = np.abs(nd.gaussian_filter(fbm(H, W, 1.6, 21), 1.2)); ridge = np.clip(1.6 - ridge, 0, None)**3
ridge = nd.gaussian_filter(ridge, 0.9); ridge /= ridge.std()

hw = 7.0*big + 1.8*mid + 1.6*strokes + 0.5*fine - 1.5*pits + 0.2*ridge

# ---------------- Logo ----------------
logo = np.asarray(Image.open(MASK).convert('L'), dtype=np.float32) / 255
lh, lw = logo.shape
M = np.zeros((H, W), np.float32)
ox, oy = (W - lw)//2, int(H*LOGO_Y - lh/2)
M[oy:oy+lh, ox:ox+lw] = logo
B = np.zeros((H, W), np.float32)
if BRASS:
    bl = np.asarray(Image.open(BRASS).convert('L'), dtype=np.float32) / 255
    B[oy:oy+lh, ox:ox+lw] = bl
inside = M > 0.5
edt = nd.distance_transform_edt(inside)
BEV = 2.4
bevel = np.clip(edt/BEV, 0, 1); bevel = np.sin(bevel*np.pi/2)
bevel = nd.gaussian_filter(bevel, 0.6) * (M)
letter_grain = nd.gaussian_filter(rng.normal(size=(H, W)), 0.6) * 0.28 + nd.gaussian_filter(rng.normal(size=(H, W)), 2.0)*0.2
hl = 3.0*bevel + letter_grain*M

# ---------------- Lighting ----------------
def normals(h, k):
    gy, gx = np.gradient(h)
    n = np.dstack([-gx*k, -gy*k, np.ones_like(h)])
    return n / np.linalg.norm(n, axis=2, keepdims=True)
Nw = normals(hw, 0.085)
Nl = normals(hl, 0.9)
Ldir = np.array([0.62, -0.50, 0.60]); Ldir /= np.linalg.norm(Ldir)   # sun from upper-right, grazing
V = np.array([0, 0, 1.0])
Hv = (Ldir + V); Hv /= np.linalg.norm(Hv)

# window light: lit region below a diagonal edge, with a mullion; soft penumbra + slight edge wobble
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
wob = nd.gaussian_filter(fbm(H, W, 2.8, 33), 3) * 6
edge = (yy - ((LOGO_Y - 0.48)*H + 0.02*H + 0.075*W + (W - xx)*0.34)) + wob            # diagonal: dark top-left wedge
sun = 1/(1+np.exp(-edge/26))
edge2 = ((xx*0.9 + yy*0.55) - 0.82*W) + wob              # second soft falloff far right-bottom -> window frame
sun *= 1 - 0.9/(1+np.exp(-(edge2 - 520)/60))
mull = np.abs((xx*0.88 - yy*0.47) - 0.60*W) + wob*0.5   # thin mullion bar crossing lit area
sun *= 1 - 0.85*np.exp(-(np.clip(mull-26, 0, None)/16)**2) * (mull < 200)
sun = nd.gaussian_filter(sun, 2)

# cast shadow of standoff letters (depth ~ 22 px)
DEPTH = 34.0
dx, dy = -Ldir[0]/Ldir[2]*DEPTH, -Ldir[1]/Ldir[2]*DEPTH
sh_near = nd.shift(M, (dy*0.35, dx*0.35), order=1)
sh_far  = nd.shift(M, (dy, dx), order=1)
cast = np.maximum(nd.gaussian_filter(sh_near, 2.2)*0.55, nd.gaussian_filter(sh_far, 7.5)*0.88)
cast = np.clip(cast, 0, 1) * (1 - M)          # shadow only on wall
ao = nd.gaussian_filter(M, 14) * 0.5 + nd.gaussian_filter(M, 4)*0.35

def lin(c): c = np.array(c)/255; return c**2.2
alb_wall = lin([222, 210, 190])
mott = norm01(nd.gaussian_filter(mid, 6))[..., None]
alb = alb_wall * (0.9 + 0.16*mott) * (1 - 0.1*norm01(pits)[..., None])
alb_let = lin([28, 27, 26]) * (1 + 0.25*letter_grain[..., None])
alb_let = alb_let*(1 - B[..., None]) + lin([182, 142, 72]) * (1 + 0.12*letter_grain[..., None]) * B[..., None]

SUN = np.array([1.00, 0.88, 0.72]) * 2.75
SKY = np.array([0.74, 0.66, 0.58]) * 0.36

ndl_w = np.clip((Nw*Ldir).sum(2), 0, 1)
wall = alb * (SKY*(1 - ao[..., None]) * (0.75 + 0.25*Nw[..., 2:3]) +
              SUN * (ndl_w * sun * (1 - cast))[..., None])
ndl_l = np.clip((Nl*Ldir).sum(2), 0, 1)
spec = np.clip((Nl*Hv).sum(2), 0, 1)**40 * (0.35 + 1.6*B)
letter = alb_let * (SKY*1.1 + SUN*(ndl_l*sun)[..., None]) + (spec*sun)[..., None]*SUN*0.12
img = wall*(1 - M[..., None]) + letter*M[..., None]

# bounce light from the lit area into the shadow wedge (warm fill)
bounce = nd.gaussian_filter(sun, 180)[..., None] * np.array([1.0, 0.86, 0.7]) * 0.1
img = img + alb*bounce*(1-M[..., None])

# ---------------- Camera ----------------
img = img * 0.9
img = 1 - np.exp(-img*1.25)                    # filmic-ish shoulder
vig = 1 - 0.32*(((xx-W*0.5)/(W*0.62))**2 + ((yy-H*0.5)/(H*0.7))**2)
img *= np.clip(vig, 0, 1)[..., None]
img = img ** (1/2.2)
img = nd.gaussian_filter(img, (0.55, 0.55, 0))
img += rng.normal(size=(H, W, 1)) * 0.012   # grain
out = np.clip(img*255, 0, 255).astype(np.uint8)
Image.fromarray(out).save(OUT, quality=88, subsampling=0)
Image.fromarray(out).resize((W//2, H//2), Image.LANCZOS).save(OUT.rsplit('.',1)[0]+'-small.png')
print('done', OUT)
