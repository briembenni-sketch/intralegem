"""Law-office hero render (Blender/Cycles via the `bpy` module).

A plaster back wall with the Intra Legem crest mounted as stand-off letters,
a walnut desk with a banker's lamp, built-in bookshelves, and late sun through
a side window that throws the mullion shadows across the sign.

    python3 office.py OUT.png WIDTH HEIGHT [wide|tall] [SAMPLES]
"""
import sys, math, random
import bpy, bmesh, addon_utils
from mathutils import Vector

OUT = sys.argv[1]
W, H = int(sys.argv[2]), int(sys.argv[3])
SHOT = sys.argv[4] if len(sys.argv) > 4 else 'wide'
SAMPLES = int(sys.argv[5]) if len(sys.argv) > 5 else 128
LOGO_SVG = sys.argv[6] if len(sys.argv) > 6 else '/home/user/intralegem/assets/brand/logo-stacked.svg'
random.seed(4)

addon_utils.enable('io_curve_svg', default_set=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_curve_svg', default_set=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- materials
def mat(name, color, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat: b.inputs['Coat Weight'].default_value = coat
    return m, m.node_tree, b

def link(nt, a, b): nt.links.new(a, b)

def plaster():
    m, nt, b = mat('Plaster', (0.70, 0.62, 0.52), 0.92)
    N = nt.nodes
    tc = N.new('ShaderNodeTexCoord')
    # mottled lime-wash colour
    mott = N.new('ShaderNodeTexNoise'); mott.inputs['Scale'].default_value = 1.6; mott.inputs['Detail'].default_value = 6
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.60, 0.52, 0.42, 1); ramp.color_ramp.elements[1].color = (0.74, 0.66, 0.55, 1)
    link(nt, tc.outputs['Object'], mott.inputs['Vector']); link(nt, mott.outputs['Fac'], ramp.inputs['Fac'])
    link(nt, ramp.outputs['Color'], b.inputs['Base Color'])
    # trowel strokes: stretched noise + fine grain
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (9, 1.2, 9); mp.inputs['Rotation'].default_value = (0.3, 0.5, 0.35)
    link(nt, tc.outputs['Object'], mp.inputs['Vector'])
    st = N.new('ShaderNodeTexNoise'); st.inputs['Scale'].default_value = 3.0; st.inputs['Detail'].default_value = 10; st.inputs['Roughness'].default_value = 0.62
    link(nt, mp.outputs['Vector'], st.inputs['Vector'])
    gr = N.new('ShaderNodeTexNoise'); gr.inputs['Scale'].default_value = 260; gr.inputs['Detail'].default_value = 4
    link(nt, tc.outputs['Object'], gr.inputs['Vector'])
    mix = N.new('ShaderNodeMath'); mix.operation = 'MULTIPLY_ADD'; mix.inputs[1].default_value = 0.55
    link(nt, gr.outputs['Fac'], mix.inputs[0]); link(nt, st.outputs['Fac'], mix.inputs[2])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.55; bump.inputs['Distance'].default_value = 0.004
    link(nt, mix.outputs['Value'], bump.inputs['Height']); link(nt, bump.outputs['Normal'], b.inputs['Normal'])
    return m

def wood(name, c1, c2, scale=(1, 14, 1), rough=0.38, coat=0.25):
    m, nt, b = mat(name, c1, rough, coat=coat)
    N = nt.nodes
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = scale
    link(nt, tc.outputs['Object'], mp.inputs['Vector'])
    wv = N.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 3.0; wv.inputs['Distortion'].default_value = 3.5; wv.inputs['Detail'].default_value = 8; wv.inputs['Detail Roughness'].default_value = 0.7
    link(nt, mp.outputs['Vector'], wv.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    link(nt, wv.outputs['Fac'], ramp.inputs['Fac']); link(nt, ramp.outputs['Color'], b.inputs['Base Color'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08
    link(nt, wv.outputs['Fac'], bump.inputs['Height']); link(nt, bump.outputs['Normal'], b.inputs['Normal'])
    return m

def floor_mat():
    m, nt, b = mat('Oak', (0.30, 0.19, 0.11), 0.42, coat=0.15)
    N = nt.nodes
    tc = N.new('ShaderNodeTexCoord')
    br = N.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.004; br.inputs['Brick Width'].default_value = 1.6; br.inputs['Row Height'].default_value = 0.18
    br.offset = 0.37; br.squash = 1.0
    br.inputs['Color1'].default_value = (0.36, 0.23, 0.13, 1); br.inputs['Color2'].default_value = (0.27, 0.16, 0.09, 1)
    br.inputs['Mortar'].default_value = (0.08, 0.05, 0.03, 1)
    link(nt, tc.outputs['Object'], br.inputs['Vector'])
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 20, 1)
    link(nt, tc.outputs['Object'], mp.inputs['Vector'])
    gn = N.new('ShaderNodeTexNoise'); gn.inputs['Scale'].default_value = 6; gn.inputs['Detail'].default_value = 8
    link(nt, mp.outputs['Vector'], gn.inputs['Vector'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 0.35
    link(nt, br.outputs['Color'], mx.inputs['A']); link(nt, gn.outputs['Color'], mx.inputs['B'])
    link(nt, mx.outputs['Result'], b.inputs['Base Color'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25
    link(nt, br.outputs['Fac'], bump.inputs['Height']); link(nt, bump.outputs['Normal'], b.inputs['Normal'])
    return m

def rug_mat():
    m, nt, b = mat('Rug', (0.20, 0.17, 0.14), 0.95)
    N = nt.nodes
    tc = N.new('ShaderNodeTexCoord')
    n = N.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 90; n.inputs['Detail'].default_value = 3
    link(nt, tc.outputs['Object'], n.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.13, 0.11, 0.09, 1); ramp.color_ramp.elements[1].color = (0.27, 0.23, 0.19, 1)
    link(nt, n.outputs['Fac'], ramp.inputs['Fac']); link(nt, ramp.outputs['Color'], b.inputs['Base Color'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.4
    link(nt, n.outputs['Fac'], bump.inputs['Height']); link(nt, bump.outputs['Normal'], b.inputs['Normal'])
    return m

M_PLASTER = plaster()
M_WALNUT = wood('Walnut', (0.10, 0.05, 0.028), (0.21, 0.11, 0.06), scale=(0.9, 28, 28))
M_SHELF = wood('ShelfWalnut', (0.09, 0.045, 0.025), (0.18, 0.095, 0.05), scale=(28, 28, 0.9))
M_FLOOR = floor_mat()
M_RUG = rug_mat()
M_BLACK, nt, b = mat('LogoBlack', (0.01, 0.0095, 0.009), 0.68)
bn = nt.nodes.new('ShaderNodeTexNoise'); bn.inputs['Scale'].default_value = 900
bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.12
link(nt, bn.outputs['Fac'], bp.inputs['Height']); link(nt, bp.outputs['Normal'], b.inputs['Normal'])
M_BRASS = mat('Brass', (0.80, 0.60, 0.30), 0.26, metal=1.0)[0]
M_LEATHER = mat('Leather', (0.045, 0.028, 0.02), 0.42)[0]
M_BLOTTER = mat('Blotter', (0.07, 0.045, 0.03), 0.5)[0]
m_glass, nt, b = mat('GreenGlass', (0.02, 0.22, 0.10), 0.12)
b.inputs['Transmission Weight'].default_value = 0.35
M_GLASS = m_glass
m_bulb, nt, b = mat('Bulb', (1, 0.8, 0.55), 0.5)
b.inputs['Emission Color'].default_value = (1.0, 0.78, 0.5, 1); b.inputs['Emission Strength'].default_value = 12
M_BULB = m_bulb
M_PAPER = mat('Paper', (0.82, 0.79, 0.72), 0.8)[0]
M_CERAMIC = mat('Ceramic', (0.66, 0.60, 0.52), 0.35)[0]
BOOK_COLORS = [(0.16, 0.035, 0.03), (0.035, 0.05, 0.09), (0.04, 0.07, 0.05), (0.26, 0.17, 0.09), (0.03, 0.028, 0.025),
               (0.40, 0.32, 0.22), (0.11, 0.045, 0.03), (0.46, 0.41, 0.33), (0.07, 0.06, 0.055), (0.20, 0.10, 0.05)]
M_BOOKS = [mat(f'Book{i}', c, random.uniform(0.45, 0.7))[0] for i, c in enumerate(BOOK_COLORS)]
M_GILT = mat('Gilt', (0.75, 0.56, 0.26), 0.35, metal=1.0)[0]

# ---------------------------------------------------------------- geometry helpers
def box(name, x0, x1, y0, y1, z0, z1, m, bevel=0.0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 if v.co.x < 0 else x1
        v.co.y = y0 if v.co.y < 0 else y1
        v.co.z = z0 if v.co.z < 0 else z1
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    if bevel:
        md = ob.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = 3; md.limit_method = 'ANGLE'
    for p in me.polygons: p.use_smooth = bool(bevel)
    return ob

def cyl(name, x, y, z0, z1, r, m, verts=48, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
    ob = bpy.context.active_object; ob.name = name; ob.data.materials.append(m)
    if rot: ob.rotation_euler = rot
    bpy.ops.object.shade_smooth()
    return ob

# ---------------------------------------------------------------- room
WALL_Y = 0.0
box('Floor', -5, 5, -8, 0.3, -0.05, 0.0, M_FLOOR)
box('BackWall', -5, 5, WALL_Y, 0.3, 0, 3.3, M_PLASTER)
box('Ceiling', -5, 5, -8, 0.3, 3.3, 3.45, M_PLASTER)
box('RightWall', 3.2, 3.45, -8, 0.3, 0, 3.3, M_PLASTER)
box('Skirting', -5, 5, -0.018, 0.0, 0, 0.12, M_PLASTER)
# left wall with a tall window (y -3.3 .. -0.35, z 0.45 .. 3.15)
LX0, LX1 = -3.45, -3.2
box('LeftWallA', LX0, LX1, -8, -4.5, 0, 3.3, M_PLASTER)
box('LeftWallB', LX0, LX1, -0.35, 0.3, 0, 3.3, M_PLASTER)
box('Sill', LX0, LX1, -4.5, -0.35, 0, 0.45, M_PLASTER)
box('Header', LX0, LX1, -4.5, -0.35, 3.15, 3.3, M_PLASTER)
for yy in (-3.4, -2.35, -1.3):
    box('Mullion', LX0 + 0.08, LX1 - 0.08, yy - 0.035, yy + 0.035, 0.45, 3.15, M_SHELF)
box('Transom', LX0 + 0.08, LX1 - 0.08, -4.5, -0.35, 2.38, 2.44, M_SHELF)

# rug
box('Rug', -1.7, 1.7, -3.2, -0.25, 0.0, 0.012, M_RUG, bevel=0.004)

# ---------------------------------------------------------------- the sign
before = set(bpy.data.objects)
bpy.ops.import_curve.svg(filepath=LOGO_SVG)
curves = [o for o in bpy.data.objects if o not in before]
SIGN_W = 1.3
xs = [o.dimensions.x for o in curves]
raw_w = max(xs)
s = SIGN_W / raw_w
for o in curves:
    cu = o.data
    cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = 0.0075 / s; cu.bevel_depth = 0.0009 / s; cu.bevel_resolution = 2
    o.scale = (s, s, s)
    o.rotation_euler = (math.radians(90), 0, 0)
    is_brass = any(mm and 'SVGMat' in mm.name for mm in cu.materials)
    cu.materials.clear(); cu.materials.append(M_BRASS if is_brass else M_BLACK)
bpy.context.view_layer.update()
mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
for o in curves:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mins = Vector(map(min, mins, w)); maxs = Vector(map(max, maxs, w))
SIGN_Z = 1.78
off = Vector((-(mins.x + maxs.x) / 2, (WALL_Y - 0.009) - maxs.y, SIGN_Z - mins.z))
for o in curves: o.location += off

# ---------------------------------------------------------------- desk
DY0, DY1 = -1.95, -1.05          # desk depth span (front edge faces camera at DY0)
box('DeskTop', -1.1, 1.1, DY0, DY1, 0.715, 0.765, M_WALNUT, bevel=0.006)
box('DeskEndL', -1.06, -1.0, DY0 + 0.03, DY1 - 0.03, 0, 0.715, M_WALNUT, bevel=0.003)
box('DeskEndR', 1.0, 1.06, DY0 + 0.03, DY1 - 0.03, 0, 0.715, M_WALNUT, bevel=0.003)
box('DeskFront', -1.0, 1.0, DY0 + 0.05, DY0 + 0.08, 0.16, 0.715, M_WALNUT, bevel=0.002)
box('Blotter', -0.42, 0.42, -1.8, -1.28, 0.765, 0.771, M_BLOTTER, bevel=0.003)
box('Papers', -0.2, 0.12, -1.72, -1.42, 0.771, 0.776, M_PAPER)
pen = cyl('Pen', 0.22, -1.55, 0.777, 0.777 + 0.14, 0.0055, M_BLACK, 24, rot=(0, math.radians(90), math.radians(-18)))
pen.location = (0.25, -1.56, 0.781)
# book stack
bz = 0.765
for i, (w_, d_, h_, rot) in enumerate([(0.30, 0.22, 0.045, 6), (0.27, 0.2, 0.038, -3), (0.24, 0.17, 0.05, 11)]):
    ob = box(f'DeskBook{i}', -w_ / 2, w_ / 2, -d_ / 2, d_ / 2, 0, h_, M_BOOKS[[0, 1, 4][i]], bevel=0.003)
    ob.location = (0.72, -1.38, bz); ob.rotation_euler = (0, 0, math.radians(rot)); bz += h_
# banker's lamp
LX, LY = -0.72, -1.36
cyl('LampBase', LX, LY, 0.765, 0.785, 0.085, M_BRASS)
cyl('LampStem', LX, LY, 0.785, 1.12, 0.009, M_BRASS)
shade = cyl('LampShade', LX, LY - 0.07, 0, 0.36, 0.075, M_GLASS, 64, rot=(0, math.radians(90), 0))
shade.location = (LX, LY - 0.07, 1.14)
# cut the shade to a half-cylinder (keep upper half) with a boolean box
cutter = box('ShadeCut', LX - 0.3, LX + 0.3, LY - 0.3, LY + 0.3, 1.14 - 0.2, 1.135, M_GLASS)
bm_ = shade.modifiers.new('cut', 'BOOLEAN'); bm_.object = cutter; bm_.operation = 'DIFFERENCE'
sol = shade.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 0.004
cutter.hide_render = True; cutter.hide_viewport = True
bulb = cyl('Bulb', LX, LY - 0.07, 0, 0.26, 0.018, M_BULB, 24, rot=(0, math.radians(90), 0)); bulb.location = (LX, LY - 0.07, 1.125)

# ---------------------------------------------------------------- chair (high-back leather, behind the desk)
CY = -0.62
cb = box('ChairBack', -0.33, 0.33, -0.07, 0.07, -0.44, 0.44, M_LEATHER, bevel=0.07)
cb.location = (0, CY, 1.06); cb.rotation_euler = (math.radians(-9), 0, 0)
cb.modifiers['bev'].segments = 6
box('ChairSeat', -0.32, 0.32, CY - 0.55, CY, 0.44, 0.56, M_LEATHER, bevel=0.04)
for sx in (-0.36, 0.36):
    box('ChairArm', sx - 0.04, sx + 0.04, CY - 0.5, CY + 0.02, 0.56, 0.72, M_LEATHER, bevel=0.03)

# ---------------------------------------------------------------- built-in bookshelves
def shelf_unit(x0, x1):
    y0, y1 = -0.46, WALL_Y
    t = 0.04
    box('ShelfSideL', x0, x0 + t, y0, y1, 0, 3.3, M_SHELF, bevel=0.003)
    box('ShelfSideR', x1 - t, x1, y0, y1, 0, 3.3, M_SHELF, bevel=0.003)
    box('ShelfCrown', x0 - 0.02, x1 + 0.02, y0 - 0.03, y1, 3.12, 3.3, M_SHELF, bevel=0.004)
    box('ShelfBack', x0, x1, y1 - 0.015, y1, 0, 3.3, M_SHELF)
    # lower cabinet with two panelled doors
    box('Cabinet', x0 + t, x1 - t, y0 + 0.02, y1, 0, 0.86, M_SHELF)
    box('CabTop', x0 - 0.01, x1 + 0.01, y0 - 0.02, y1, 0.86, 0.9, M_SHELF, bevel=0.004)
    mid = (x0 + x1) / 2
    for a, b_ in ((x0 + t + 0.02, mid - 0.006), (mid + 0.006, x1 - t - 0.02)):
        box('Door', a, b_, y0 - 0.0, y0 + 0.02, 0.08, 0.84, M_SHELF, bevel=0.003)
        box('DoorPanel', a + 0.06, b_ - 0.06, y0 - 0.012, y0, 0.16, 0.76, M_SHELF, bevel=0.006)
        cyl('Knob', b_ - 0.04 if a < mid else a + 0.04, y0 - 0.02, 0, 0.001, 0.012, M_BRASS).location.z = 0.6
    levels = [0.9, 1.34, 1.78, 2.22, 2.66, 3.12]
    for z in levels[1:-1]:
        box('Shelf', x0 + t, x1 - t, y0 + 0.02, y1 - 0.015, z - 0.035, z, M_SHELF, bevel=0.003)
    for i in range(len(levels) - 1):
        z = levels[i]; top = levels[i + 1] - 0.035
        x = x0 + t + 0.012; end = x1 - t - 0.012
        gap_at = random.uniform(x + 0.2, end - 0.35) if random.random() < 0.6 else None
        while x < end - 0.02:
            if gap_at and x > gap_at:
                if random.random() < 0.5:
                    cyl('Vase', x + 0.08, y0 + 0.22, z, z + random.uniform(0.18, 0.28), 0.06, M_CERAMIC)
                    x += 0.2
                else:
                    hz = z
                    for k in range(random.randint(2, 4)):
                        hh = random.uniform(0.03, 0.05)
                        box('LyingBook', x, x + random.uniform(0.2, 0.25), y0 + 0.08, y0 + 0.33, hz, hz + hh, random.choice(M_BOOKS), bevel=0.002); hz += hh
                    x += 0.28
                gap_at = None; continue
            bw = random.uniform(0.024, 0.06)
            bh = min(top - z - 0.012, random.uniform(0.24, 0.36))
            bd = random.uniform(0.22, 0.3)
            if x + bw > end: break
            fy = y1 - 0.02 - bd
            m_ = random.choice(M_BOOKS)
            ob = box('Book', x, x + bw, fy, y1 - 0.02, z, z + bh, m_, bevel=0.0015)
            if random.random() < 0.45:     # gilt bands on the spine (law reports)
                for bz_ in (z + bh - 0.035, z + bh - 0.06, z + 0.03):
                    box('Gilt', x + 0.002, x + bw - 0.002, fy - 0.0012, fy, bz_, bz_ + 0.004, M_GILT)
            x += bw + random.uniform(0.0, 0.003)

shelf_unit(-3.2, -1.8)
shelf_unit(1.8, 3.2)

# ---------------------------------------------------------------- lighting
sun_d = Vector((0.70, 0.62, -0.17)).normalized()          # direction the light travels
bpy.ops.object.light_add(type='SUN', location=(-6, -4, 5))
sun = bpy.context.active_object
sun.data.energy = 8.0; sun.data.angle = math.radians(0.8); sun.data.color = (1.0, 0.88, 0.74)
sun.rotation_euler = (-sun_d).to_track_quat('Z', 'Y').to_euler()

bpy.ops.object.light_add(type='AREA', location=(0.3, -5.2, 3.1))
fill = bpy.context.active_object
fill.data.shape = 'RECTANGLE'; fill.data.size = 4.0; fill.data.size_y = 1.5
fill.data.energy = 70; fill.data.color = (1.0, 0.93, 0.85)
fill.rotation_euler = (math.radians(58), 0, 0)

world = bpy.data.worlds.new('World'); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.62, 0.66, 0.74, 1); bg.inputs['Strength'].default_value = 0.12

# ---------------------------------------------------------------- camera
bpy.ops.object.camera_add()
cam = bpy.context.active_object; scene.camera = cam
cam.data.sensor_width = 36
if SHOT == 'detail':
    cam.location = (-0.55, -3.05, 1.2); cam.data.lens = 36
    tgt = Vector((-0.12, -0.2, 1.72))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
elif SHOT == 'tall':
    cam.location = (0.0, -4.6, 1.35); cam.data.lens = 30; cam.data.shift_y = 0.02; cam.data.shift_x = 0.0
    cam.rotation_euler = (math.radians(90), 0, 0)
else:
    cam.location = (0.0, -5.4, 1.3); cam.data.lens = 32; cam.data.shift_y = 0.085
    cam.rotation_euler = (math.radians(90), 0, 0)
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = abs(cam.location.y) - 0.03; cam.data.dof.aperture_fstop = 5.6
if SHOT == 'detail': cam.data.dof.focus_distance = 1.75; cam.data.dof.aperture_fstop = 2.8

# ---------------------------------------------------------------- render
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = SAMPLES
scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = 0.015
scene.cycles.use_denoising = True
try: scene.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
scene.cycles.max_bounces = 8; scene.cycles.diffuse_bounces = 4; scene.cycles.glossy_bounces = 4; scene.cycles.transmission_bounces = 6
scene.render.resolution_x = W; scene.render.resolution_y = H; scene.render.resolution_percentage = 100
scene.render.film_transparent = False
for vt, lk in (('AgX', 'AgX - Medium High Contrast'), ('AgX', 'Medium High Contrast'), ('Filmic', 'Medium High Contrast')):
    try:
        scene.view_settings.view_transform = vt; scene.view_settings.look = lk; break
    except Exception:
        continue
scene.view_settings.exposure = 0.3
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print('rendered', OUT)
