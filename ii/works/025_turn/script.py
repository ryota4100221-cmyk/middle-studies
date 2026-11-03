# =============================================================
# MIDDLE STUDIES II — 雛形（2026-09-23）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
#
# 🔴 これは「インフラ」の雛形であって、見た目の雛形ではない。
#    第1期の雛形（白床・3色・85mm・キャプション・4灯）は**持ち込まない**。
#    LOOK（色・地・光・レンズ・判型）は毎回ここで決め直し、works.json の look に同じ値を書く。
#    下の LOOK の値は動作確認用の仮置き。**そのまま出すと check.py look で前作と比べられる**。
#
# 残してあるのは、どの見た目でも要るものだけ：
#   出力モード／判型から解像度を出す計算／Cycles+GPU+デノイズ／毎フレームキーのループ／
#   面取り（bmesh・clamp の罠つき）／glb 書き出し
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK（毎回決める）
# II 025 TURN — 挽く木。基準：Time & Style「Pepper mill」製品写真（白の無限背景紙・上前方の大きな柔光・木2種）
LOOK = dict(
    aspect=(8, 5),
    lens=100,
    fstop=5.6,
    view="Standard",
    look="None",
    exposure=-2.93,
    bg=hex_to_linear("#EDECEA")[:3] if False else None,
)
FPS = 24

def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


def hex_to_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    return m


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.12), shape='RECTANGLE', sy=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.shape, ld.size = energy, color, shape, size
    if sy:
        ld.size_y = sy
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L

# ------------------------------------------------------------- 舞台：白の無限背景紙
R, W, D, H, Y0 = 2.4, 10.0, 4.0, 4.0, 0.25
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 48 * math.pi / 2 for i in range(1, 49)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + Y0, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me"); me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
PAPER = hex_to_linear("#EDEDEE")
sweep.data.materials.append(principled("paper", PAPER, rough=0.85))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.9, 0.9, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

# ------------------------------------------------------------- 木の材質（挽物：成長輪を斜めに切った面）
def wood(name, early, late, rings, off, tilt, pore_dark, rough, warp=0.0025, seed=0.0, bump_k=0.08,
         vscale=420.0, vasp=22.0, vwidth=0.05, vdark=0.55, hf=0.0006, vtint=(0.93, 0.86), irr=0.0, band=(0.18, 0.62, 0.9), jag=0.0, jag_scale=400.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (off[0], off[1], 0)
    mp.inputs["Rotation"].default_value = (tilt[0], tilt[1], 0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    # 輪のゆらぎ（低周波ノイズで輪をうねらせる）
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14.0
    nz.inputs["Detail"].default_value = 3.0; nz.noise_dimensions = '4D'
    nz.inputs["W"].default_value = seed
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    sub = N.new("ShaderNodeVectorMath"); sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = (0.5, 0.5, 0.5)
    L.new(nz.outputs["Color"], sub.inputs[0])
    sc = N.new("ShaderNodeVectorMath"); sc.operation = 'SCALE'
    sc.inputs["Scale"].default_value = warp
    L.new(sub.outputs[0], sc.inputs[0])
    add = N.new("ShaderNodeVectorMath"); add.operation = 'ADD'
    L.new(mp.outputs[0], add.inputs[0]); L.new(sc.outputs[0], add.inputs[1])
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(add.outputs[0], sep.inputs[0])
    # d = sqrt(x^2+y^2)
    x2 = N.new("ShaderNodeMath"); x2.operation = 'MULTIPLY'
    L.new(sep.outputs[0], x2.inputs[0]); L.new(sep.outputs[0], x2.inputs[1])
    y2 = N.new("ShaderNodeMath"); y2.operation = 'MULTIPLY'
    L.new(sep.outputs[1], y2.inputs[0]); L.new(sep.outputs[1], y2.inputs[1])
    s2 = N.new("ShaderNodeMath"); s2.operation = 'ADD'
    L.new(x2.outputs[0], s2.inputs[0]); L.new(y2.outputs[0], s2.inputs[1])
    d = N.new("ShaderNodeMath"); d.operation = 'SQRT'; L.new(s2.outputs[0], d.inputs[0])
    # 輪の幅を不揃いに：d に低周波ノイズを足してから倍率
    nz2 = N.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 3.0
    nz2.inputs["Detail"].default_value = 1.0
    L.new(tc.outputs["Object"], nz2.inputs["Vector"])
    j = N.new("ShaderNodeMath"); j.operation = 'MULTIPLY_ADD'
    L.new(nz2.outputs["Fac"], j.inputs[0]); j.inputs[1].default_value = 0.004
    L.new(d.outputs[0], j.inputs[2])
    nz3 = N.new("ShaderNodeTexNoise"); nz3.inputs["Scale"].default_value = 90.0
    nz3.inputs["Detail"].default_value = 4.0
    L.new(tc.outputs["Object"], nz3.inputs["Vector"])
    j2 = N.new("ShaderNodeMath"); j2.operation = 'MULTIPLY_ADD'
    L.new(nz3.outputs["Fac"], j2.inputs[0]); j2.inputs[1].default_value = hf
    L.new(j.outputs[0], j2.inputs[2])
    j = j2
    rr = N.new("ShaderNodeMath"); rr.operation = 'MULTIPLY'; rr.inputs[1].default_value = rings
    L.new(j.outputs[0], rr.inputs[0])
    # 輪の間隔を不揃いに：輪の番号そのものに1次元ノイズを足す
    n1 = N.new("ShaderNodeTexNoise"); n1.noise_dimensions = '1D'
    n1.inputs["Scale"].default_value = 0.22; n1.inputs["Detail"].default_value = 2.0
    L.new(rr.outputs[0], n1.inputs["W"])
    n1m = N.new("ShaderNodeMath"); n1m.operation = 'MULTIPLY_ADD'
    L.new(n1.outputs["Fac"], n1m.inputs[0]); n1m.inputs[1].default_value = irr
    L.new(rr.outputs[0], n1m.inputs[2])
    # 輪を導管で千切る：縦に引き伸ばした高周波ノイズを輪の番号に足す（ウェンジの「破線の輪」）
    mpj = N.new("ShaderNodeMapping"); mpj.inputs["Scale"].default_value = (1.0, 1.0, 0.12)
    L.new(add.outputs[0], mpj.inputs["Vector"])
    nj = N.new("ShaderNodeTexNoise"); nj.inputs["Scale"].default_value = jag_scale
    nj.inputs["Detail"].default_value = 3.0
    L.new(mpj.outputs[0], nj.inputs["Vector"])
    njm = N.new("ShaderNodeMath"); njm.operation = 'MULTIPLY_ADD'
    L.new(nj.outputs["Fac"], njm.inputs[0]); njm.inputs[1].default_value = jag
    L.new(n1m.outputs[0], njm.inputs[2])
    fr = N.new("ShaderNodeMath"); fr.operation = 'FRACT'; L.new(njm.outputs[0], fr.inputs[0])
    ramp = N.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position = 0.0; e[0].color = late
    e[1].position = band[0]; e[1].color = early
    e3 = e.new(band[1]); e3.color = early
    e4 = e.new(band[2]); e4.color = late
    L.new(fr.outputs[0], ramp.inputs["Fac"])
    # 導管（縦に引き伸ばした細かいノイズ）
    mp2 = N.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (1.0, 1.0, 0.04)
    L.new(add.outputs[0], mp2.inputs["Vector"])
    pn = N.new("ShaderNodeTexNoise"); pn.inputs["Scale"].default_value = 1400.0
    pn.inputs["Detail"].default_value = 2.0
    L.new(mp2.outputs[0], pn.inputs["Vector"])
    pr = N.new("ShaderNodeMapRange"); pr.inputs["From Min"].default_value = 0.55
    pr.inputs["From Max"].default_value = 0.75
    L.new(pn.outputs["Fac"], pr.inputs["Value"])
    mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    L.new(pr.outputs[0], mix.inputs[0])   # Factor
    mix.inputs[0].default_value = 0.0
    L.new(ramp.outputs["Color"], mix.inputs[6])
    mix.inputs[7].default_value = (pore_dark, pore_dark * 0.95, pore_dark * 0.9, 1)
    fm = N.new("ShaderNodeMath"); fm.operation = 'MULTIPLY'; fm.inputs[1].default_value = 0.6
    L.new(pr.outputs[0], fm.inputs[0]); L.new(fm.outputs[0], mix.inputs[0])
    # 導管線：縦に引き伸ばした Voronoi の境界（#106）
    mp3 = N.new("ShaderNodeMapping"); mp3.inputs["Scale"].default_value = (1.0, 1.0, 1.0 / vasp)
    L.new(add.outputs[0], mp3.inputs["Vector"])
    vo = N.new("ShaderNodeTexVoronoi"); vo.feature = 'DISTANCE_TO_EDGE'
    vo.inputs["Scale"].default_value = vscale
    L.new(mp3.outputs[0], vo.inputs["Vector"])
    vr = N.new("ShaderNodeMapRange"); vr.inputs["From Min"].default_value = 0.0
    vr.inputs["From Max"].default_value = vwidth
    vr.inputs["To Min"].default_value = 1.0; vr.inputs["To Max"].default_value = 0.0
    L.new(vo.outputs["Distance"], vr.inputs["Value"])
    mix2 = N.new("ShaderNodeMix"); mix2.data_type = 'RGBA'; mix2.blend_type = 'MULTIPLY'
    L.new(vr.outputs[0], mix2.inputs[0])
    L.new(mix.outputs[2], mix2.inputs[6])
    mix2.inputs[7].default_value = (vdark, vdark * vtint[0], vdark * vtint[1], 1)
    L.new(mix2.outputs[2], p.inputs["Base Color"])
    hb = N.new("ShaderNodeMath"); hb.operation = 'ADD'
    L.new(vr.outputs[0], hb.inputs[0]); L.new(pr.outputs[0], hb.inputs[1])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = 0.55
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = bump_k
    bump.inputs["Distance"].default_value = 0.0002
    L.new(hb.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs[0], p.inputs["Normal"])
    return m

ASH = wood("ash", hex_to_linear("#D9C6A4"), hex_to_linear("#A57C50"), rings=1400,
           off=(0.075, 0.02), tilt=(0.0, 0.05), pore_dark=0.62, rough=0.36, seed=1.3, vscale=950, vasp=40, vwidth=0.04, vdark=0.80, vtint=(0.84, 0.70), irr=5.0, band=(0.05, 0.74, 0.90))
WENGE = wood("wenge", hex_to_linear("#160E0A"), hex_to_linear("#7A4835"), rings=4200,
             off=(0.16, -0.05), tilt=(0.008, -0.012), pore_dark=0.42, rough=0.48, seed=7.1, warp=0.006, vscale=620, vasp=9, vwidth=0.12, vdark=0.40, jag=1.6, jag_scale=900, irr=5.0, bump_k=0.22, band=(0.06, 0.62, 0.72), hf=0.0012)
STEEL = principled("steel", hex_to_linear("#C9CBCC"), rough=0.22, metal=1.0)

# ------------------------------------------------------------- 被写体：挽物のミル2本（造形は自作）
SEG = 160


def catmull(pts, n_per=16):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n_per):
            t = k / n_per
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t * t
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t ** 3) for c in (0, 1)))
    out.append(pts[-1])
    return out


RS = 0.86

def lathe(name, prof, mat, loc):
    """prof: (r, z) を下から上へ。r=0 の端は閉じる"""
    verts, faces = [], []
    rings = []
    for (r, z) in prof:
        if r < 1e-6:
            verts.append((0, 0, z)); rings.append([len(verts) - 1])
            continue
        idx = []
        for s in range(SEG):
            a = 2 * math.pi * s / SEG
            verts.append((RS * r * math.cos(a), RS * r * math.sin(a), z)); idx.append(len(verts) - 1)
        rings.append(idx)
    for A, B in zip(rings[:-1], rings[1:]):
        if len(A) == 1 and len(B) > 1:
            for s in range(SEG):
                faces.append((A[0], B[(s + 1) % SEG], B[s]))
        elif len(B) == 1 and len(A) > 1:
            for s in range(SEG):
                faces.append((A[s], A[(s + 1) % SEG], B[0]))
        else:
            for s in range(SEG):
                faces.append((A[s], A[(s + 1) % SEG], B[(s + 1) % SEG], B[s]))
    me = bpy.data.meshes.new(name + "_me"); me.from_pydata(verts, [], faces); me.update()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.location = loc
    ob.data.materials.append(mat)
    return ob


def mill(prefix, H, mat, loc, rot):
    """胴（樽形・下から4割が最大径）＋継ぎ目の溝＋頭（すぼまってから小さく張る肩・平たい丸頭）"""
    k = H / 0.25
    zg = 0.178 * k                      # 継ぎ目の高さ
    body_ctrl = [(0.0205, 0.0), (0.0228, 0.03 * k), (0.0238, 0.075 * k), (0.0226, 0.125 * k), (0.0198, zg)]
    sm = catmull(body_ctrl, 18)
    rb = 0.0016                         # 足の丸め
    prof = [(0.0, 0.0)] + [(sm[0][0] - rb + rb * math.sin(t), rb - rb * math.cos(t))
                            for t in [i / 8 * math.pi / 2 for i in range(9)]]
    prof += [(r, z) for (r, z) in sm[1:] if z > rb + 1e-4]
    gw, gd = 0.0006, 0.0007            # 溝（上下の部品の隙間）
    prof_body = prof[:-1] + [(0.0198 - 0.0002, zg - 0.0003), (0.0198 - gd, zg - gw * 0.2), (0.0, zg - gw * 0.2)]
    head_ctrl = [(0.0198, zg), (0.0186, zg + 0.018 * k), (0.0178, zg + 0.034 * k), (0.0196, zg + 0.050 * k),
                 (0.0200, zg + 0.056 * k)]
    hs = catmull(head_ctrl, 14)
    top = zg + 0.056 * k
    dome = [(0.0200 * math.cos(t) , top + 0.007 * math.sin(t)) for t in [i / 16 * math.pi / 2 for i in range(1, 15)]]
    prof_head = [(0.0, zg + gw * 0.2), (0.0198 - gd, zg + gw * 0.2), (0.0198 - 0.0002, zg + 0.0003)] + hs[1:] + dome
    prof_head += [(0.0048, top + 0.0068)]
    b = lathe(prefix + "_body", prof_body, mat, loc)
    h = lathe(prefix + "_head", prof_head, mat, loc)
    nut = lathe(prefix + "_nut", [(0.0, top + 0.0062), (0.0042, top + 0.0062), (0.0044, top + 0.0080),
                                  (0.0040, top + 0.0098), (0.0028, top + 0.0108), (0.0, top + 0.0110)], STEEL, loc)
    nut.parent = h; nut.location = (0, 0, 0)
    b.rotation_euler = (0, 0, rot); h.rotation_euler = (0, 0, rot)
    return b, h, nut, top + 0.011


A_body, A_head, A_nut, A_top = mill("ash", 0.25, ASH, (-0.050, 0.0, 0.0), 0.4)
B_body, B_head, B_nut, B_top = mill("wenge", 0.25, WENGE, (0.052, 0.012, 0.0), 2.1)
parts = [A_body, A_head, A_nut, B_body, B_head, B_nut]

# ------------------------------------------------------------- 光：上前方の大きな柔光1つ＋正面の起こし＋地を白く起こす
key = area("key", (-1.2, -2.0, 1.8), 1.6, 400, (1.0, 1.0, 1.0), target=(0, 0, 0.12))
fill = area("fill", (0.9, -2.2, 0.5), 1.2, 55, (0.98, 0.99, 1.0), target=(0, 0, 0.12))
wall = area("wall", (0.0, 0.0, 2.2), 3.0, 230, (1, 1, 1), target=(0, 1.0, 0.25))
BLACK = principled("black", (0.003, 0.003, 0.003, 1), rough=0.9)
flags = []
for nm, x, ang in ():
    fm = bpy.data.meshes.new(nm + "_me")
    fm.from_pydata([(0, -0.14, 0.02), (0, 0.14, 0.02), (0, 0.14, 0.34), (0, -0.14, 0.34)], [], [(0, 1, 2, 3)])
    fl = bpy.data.objects.new(nm, fm); scene.collection.objects.link(fl)
    fl.location = (x, 0.0, 0.0); fl.rotation_euler = (0, 0, math.radians(ang))
    fl.data.materials.append(BLACK)
    fl.visible_camera = False; fl.visible_shadow = False
    fl.visible_glossy = True
    flags.append(fl)
for L in (key, fill, wall):
    L.visible_camera = False
key_light = key
KEY_HOME = tuple(key.location)

# 壁の起こしは被写体に当てない（ライトリンク）：当てると全方向から起きて胴の丸みが消える
recv = bpy.data.collections.new("mills_recv")
for o in (A_body, A_head, B_body, B_head):
    recv.objects.link(o)
wall.light_linking.receiver_collection = recv
for co in recv.collection_objects:
    co.light_linking.link_state = 'EXCLUDE'

# 床だけを洗う光（ライトリンクで背景紙だけに当てる）：床の奥の継ぎ目の灰の帯を白へ飛ばす。真上からなので足元に小さな影が溜まる
floorwash = area("floorwash", (0.0, 0.1, 1.4), 2.6, 45, (1, 1, 1), target=(0, 0.7, 0.0), sy=1.6)
floorwash.visible_camera = False
fw_recv = bpy.data.collections.new("sweep_recv"); fw_recv.objects.link(sweep)
floorwash.light_linking.receiver_collection = fw_recv

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
cd.clip_start = 0.01
scene.camera = cam


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def orbit(center, radius, height, deg):
    r = math.radians(deg)
    return Vector((center[0] + radius * math.sin(r), center[1] - radius * math.cos(r), height))


TGT = Vector((0.0, 0.0, 0.128))
HERO_CAM = Vector((0.0, -1.82, 0.33))
SHOTS = [
    dict(sec=3.0,   # 回り込み：真上寄りから2本の頭（天面と金具）を見下ろして弧を描く
         cam=lambda t: (orbit(Vector((0.0, 0.006, 0.0)), 0.42, 0.78, -70 + 55 * ease(t)), Vector((0.0, 0.006, 0.22)),
                        85, 4.0, None)),
    dict(sec=3.0,   # マクロ：タモの継ぎ目→頭をなめる。頭がひねられて木目が回る。ピントは表面（軸から半径ぶん手前）
         cam=lambda t: (lerp((-0.17, -0.30, 0.150), (-0.13, -0.31, 0.205), ease(t)),
                        lerp((-0.050, 0, 0.160), (-0.050, 0, 0.200), ease(t)), 135, 4.0,
                        (lerp((-0.050, 0, 0.160), (-0.050, 0, 0.200), ease(t)) - lerp((-0.17, -0.30, 0.150), (-0.13, -0.31, 0.205), ease(t))).length - 0.017)),
    dict(sec=2.6,   # スライド：低い位置で手前を横に滑る（足元と接地の影）
         cam=lambda t: (lerp((0.16, -0.62, 0.035), (-0.10, -0.60, 0.045), ease(t)), lerp((0.06, 0.0, 0.05), (-0.04, 0.0, 0.06), ease(t)),
                        85, 2.8, None)),
    dict(sec=3.4,   # 決め：遠くから押し込んで hero で止まる
         cam=lambda t: (lerp(HERO_CAM + Vector((0.10, -0.55, 0.06)), HERO_CAM, ease_out(min(1.0, t / 0.62))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    A_head.rotation_euler = (0, 0, 0.4 + (math.radians(-70) * ease(t) if i == 1 else 0))
    B_head.rotation_euler = (0, 0, 2.1)
    A_body.rotation_euler = (0, 0, 0.4); B_body.rotation_euler = (0, 0, 2.1)


def light_path(i, t):
    key_light.location = KEY_HOME


for i, sh in enumerate(SHOTS):
    for k in range(sh["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh["frames"] - 1)
        T = (f - 1) / max(1, N_FRAMES - 1)
        loc, tgt, lens, fstop, focus = sh["cam"](t)
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cd.lens = lens
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus if focus else (Vector(tgt) - Vector(loc)).length
        for path in ("location", "rotation_euler"):
            cam.keyframe_insert(path, frame=f)
        cd.keyframe_insert("lens", frame=f)
        cd.dof.keyframe_insert("aperture_fstop", frame=f)
        cd.dof.keyframe_insert("focus_distance", frame=f)
        pose(i, t, T)
        for o in parts:
            o.keyframe_insert("rotation_euler", frame=f)
            o.keyframe_insert("location", frame=f)
        light_path(i, t)
        key_light.keyframe_insert("location", frame=f)

# ------------------------------------------------------------- レンダー設定
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.view_settings.view_transform = LOOK["view"]
try:
    scene.view_settings.look = LOOK["look"]
except TypeError:
    print(">> look not available:", LOOK["look"])
scene.view_settings.exposure = LOOK["exposure"]
scene.frame_start, scene.frame_end = 1, N_FRAMES
scene.render.fps = FPS
scene.render.film_transparent = False


def still(path, long_side, samples, frame=STILL_FRAME):
    scene.frame_set(frame)
    scene.render.resolution_x, scene.render.resolution_y = res(long_side)
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


if "test" in modes:
    still(os.path.join(OUT, "_test.png"), 720, 48)
    print(">> test done")

if "testhero" in modes:
    still(os.path.join(OUT, "_testhero.png"), 1600, 128)
    print(">> testhero done")

if "shots" in modes:    # 各カットの頭・中・終わり（ii/scripts/contact.py で1枚に並べる）
    for i, sh in enumerate(SHOTS):
        for j, frac in enumerate((0.0, 0.5, 1.0)):
            fr = shot_start[i] + round(frac * (sh["frames"] - 1))
            still(os.path.join(OUT, "_shot_%d_%d.png" % (i, j)), 480, 24, fr)
    print(">> shots done")

if "still" in modes:
    still(os.path.join(OUT, "hero.png"), 2560, 256)
    print(">> hero done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = res(int(os.environ.get("II_ANIM_LONG", "1080")))  # II_ANIM_LONG は試験用
    scene.cycles.samples = int(os.environ.get("II_ANIM_SAMPLES", "24"))
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> anim done")

# glb は最後（マテリアルを書き換える作品があるため）
if "glb" in modes:
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
