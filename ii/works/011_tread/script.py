# =============================================================
# MIDDLE STUDIES II 011 — TREAD（踏面）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots
#
# 板目の打放しの階段に、硬い日差しが斜めに差す。段の上に焼付け塗装の卓上ランプを3台
# （橙・クリーム・紺）。ランプの造形は基準から写さず、丸い角の「帽子」形の笠と平たい台座で起こした。
# 実寸（1単位＝1m）で組む（#101：f値で縮尺を払わない）。
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(1, 1),
    lens=70,
    fstop=8.0,
    view="AgX",
    look="AgX - Medium High Contrast",
    exposure=0.55,
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


# ------------------------------------------------------------- 道具
def bevel_bm(bm, width, segments=2, clamp=True, angle=30):
    edges = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(angle)]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=width, segments=segments, profile=0.5,
                        affect='EDGES', clamp_overlap=clamp)


def to_obj(name, bm, mat=None, smooth=True, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.location = loc
    if mat:
        ob.data.materials.append(mat)
    return ob


def box_bm(x0, x1, y0, y1, z0, z1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((x0 if v.co.x < 0 else x1, y0 if v.co.y < 0 else y1, z0 if v.co.z < 0 else z1))
    return bm


def round_profile(pts, r, n=4):
    """(r,z) の折れ線の角を丸める。点に3つ目の値があればその角だけ半径を替える"""
    out = [pts[0][:2]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = Vector(pts[i - 1][:2]), Vector(pts[i][:2]), Vector(pts[i + 1][:2])
        rr = pts[i][2] if len(pts[i]) > 2 else r
        d0, d1 = (p0 - p1), (p2 - p1)
        l = min(rr, d0.length * 0.45, d1.length * 0.45)
        a, b = p1 + d0.normalized() * l, p1 + d1.normalized() * l
        for k in range(n + 1):
            t = k / n
            q = (1 - t) ** 2 * a + 2 * (1 - t) * t * p1 + t * t * b
            out.append((q.x, q.y))
    out.append(pts[-1][:2])
    return out


def lathe(name, prof, seg=160, loc=(0, 0, 0), mat=None):
    bm = bmesh.new()
    rings = []
    for (r, z) in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
                          for k in range(seg)])
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(A) == 1:
                bm.faces.new((A[0], B[k], B[k2]))
            elif len(B) == 1:
                bm.faces.new((A[k], B[0], A[k2]))
            else:
                bm.faces.new((A[k], B[k], B[k2], A[k2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_obj(name, bm, mat, loc=loc)


def sock(node, name, kind='RGBA', out=False):
    """#103：Mix の同名ソケットは型で引く"""
    socks = node.outputs if out else node.inputs
    return next(s for s in socks if s.name == name and s.type == kind)


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, coat_rough=0.03, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = coat_rough
    p.inputs["Specular IOR Level"].default_value = spec
    return m


# ------------------------------------------------------------- 打放しコンクリート（板目の型枠）
BOARD = 0.135      # 型枠の板の幅（m）


def concrete(name, base_hex="#8E8B84", seed=0.0, board_axis='Z'):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    p = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])

    def math_node(op, a, b=None, c=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def noise(scale, detail, rough=0.55, vec=None, stretch=(1, 1, 1), w=0.0, wide=False):
        mp = N.new("ShaderNodeMapping")
        L.new(tc.outputs["Object"] if vec is None else vec, mp.inputs["Vector"])
        mp.inputs["Scale"].default_value = stretch
        mp.inputs["Location"].default_value = (seed * 3.1, seed * 7.7, seed * 1.3)
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = detail
        nz.inputs["Roughness"].default_value = rough
        L.new(mp.outputs[0], nz.inputs["Vector"])
        if not wide:
            return nz.outputs["Fac"]
        mr = N.new("ShaderNodeMapRange"); mr.clamp = True      # ノイズの Fac は 0.35〜0.65 に集まる＝そのままでは斑が見えない
        L.new(nz.outputs["Fac"], mr.inputs["Value"])
        mr.inputs["From Min"].default_value = 0.36; mr.inputs["From Max"].default_value = 0.64
        return mr.outputs[0]

    # 水平な面（踏面・地面）は z が一定なので、板の向きを y に切り替える（z のままだとノイズの等高線が渦になる）
    geo = N.new("ShaderNodeNewGeometry")
    gsep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], gsep.inputs[0])
    horiz = math_node('GREATER_THAN', math_node('ABSOLUTE', gsep.outputs[2]), 0.5)
    mx = N.new("ShaderNodeMix"); mx.data_type = 'FLOAT'
    L.new(horiz, mx.inputs["Factor"])
    L.new(sep.outputs[2], sock(mx, "A", 'VALUE')); L.new(sep.outputs[1], sock(mx, "B", 'VALUE'))
    ax = sock(mx, "Result", 'VALUE', out=True)
    # 板の段：高さ方向を BOARD で割る。継ぎ目は少し波打たせる
    wob = math_node('MULTIPLY', noise(0.7, 2), 0.25)
    zonly = N.new("ShaderNodeCombineXYZ"); L.new(ax, zonly.inputs[2])                # 板の幅を不揃いに（高さ方向だけのノイズ）
    wz = noise(1.2, 1, 0.5, vec=zonly.outputs[0])
    rowf = math_node('ADD', math_node('DIVIDE', ax, BOARD), math_node('ADD', wob, math_node('MULTIPLY', wz, 2.6)))
    row = math_node('FLOOR', rowf)
    wn = N.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = '1D'
    L.new(math_node('ADD', row, seed * 13.0), wn.inputs["W"])
    tone = math_node('SUBTRACT', wn.outputs["Value"], 0.5)                      # 板ごとの色むら ±0.5
    tri = math_node('PINGPONG', rowf, 0.5)                                       # 継ぎ目からの距離 0〜0.5
    seam = N.new("ShaderNodeMapRange"); seam.clamp = True
    L.new(tri, seam.inputs["Value"])
    seam.inputs["From Min"].default_value = 0.0; seam.inputs["From Max"].default_value = 0.03
    seam.inputs["To Min"].default_value = 1.0; seam.inputs["To Max"].default_value = 0.0
    # 木目：横に長く伸ばしたノイズ（板の向きに流す）
    st = (1.0, 1.0, 9) if board_axis == 'Z' else (1.0, 9, 1.0)
    grain = noise(3.0, 5, 0.55, stretch=st)
    grain_c = N.new("ShaderNodeMapRange"); grain_c.clamp = True
    L.new(grain, grain_c.inputs["Value"])
    grain_c.inputs["From Min"].default_value = 0.35; grain_c.inputs["From Max"].default_value = 0.65
    # 大きな斑・細かい砂・気泡
    blot = noise(12.0, 6, 0.6, wide=True)
    sand = noise(70.0, 4, 0.75, wide=True)
    vor = N.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 60.0
    vor.feature = 'F1'
    L.new(tc.outputs["Object"], vor.inputs["Vector"])
    pore = N.new("ShaderNodeMapRange"); pore.clamp = True
    L.new(vor.outputs["Distance"], pore.inputs["Value"])
    pore.inputs["From Min"].default_value = 0.0; pore.inputs["From Max"].default_value = 0.13
    pore.inputs["To Min"].default_value = 1.0; pore.inputs["To Max"].default_value = 0.0

    # 明度 = 1 + 板むら*0.10 + (斑-0.5)*0.35 + (木目-0.5)*0.12 + (砂-0.5)*0.15 − 継ぎ目*0.35 − 気泡*0.3
    val = math_node('MULTIPLY_ADD', tone, 0.22, 1.0)
    val = math_node('MULTIPLY_ADD', math_node('SUBTRACT', blot, 0.5), 0.30, val)
    val = math_node('MULTIPLY_ADD', math_node('SUBTRACT', grain_c.outputs[0], 0.5), 0.16, val)
    val = math_node('MULTIPLY_ADD', math_node('SUBTRACT', sand, 0.5), 0.16, val)
    fade = N.new("ShaderNodeMapRange"); fade.clamp = True                           # 溝の濃さを所々で抜く
    L.new(noise(3.0, 2, 0.5, stretch=(1.0, 1.0, 0.2)), fade.inputs["Value"])
    fade.inputs["From Min"].default_value = 0.4; fade.inputs["From Max"].default_value = 0.6
    fade.inputs["To Min"].default_value = 0.3; fade.inputs["To Max"].default_value = 1.0
    vert = math_node('SUBTRACT', 1.0, horiz)                                          # 型枠の跡は立ち上がりの面だけ
    seam_f = math_node('MULTIPLY', math_node('MULTIPLY', seam.outputs[0], fade.outputs[0]), vert)
    val = math_node('MULTIPLY_ADD', seam_f, -0.08, val)
    val = math_node('MULTIPLY_ADD', pore.outputs[0], -0.45, val)
    # 木目の弧（年輪の写し）：横に伸ばして歪ませた Wave の縞
    wmp = N.new("ShaderNodeMapping"); wmp.inputs["Scale"].default_value = (0.25, 0.25, 1.0) if board_axis == 'Z' else (0.25, 1.0, 0.25)
    wmp.inputs["Location"].default_value = (seed, seed * 2, 0)
    L.new(tc.outputs["Object"], wmp.inputs["Vector"])
    wv = N.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = 'Z' if board_axis == 'Z' else 'Y'
    wv.inputs["Scale"].default_value = 3.0; wv.inputs["Distortion"].default_value = 9.0
    wv.inputs["Detail"].default_value = 3.0; wv.inputs["Detail Scale"].default_value = 1.5
    L.new(wmp.outputs[0], wv.inputs["Vector"])
    ring = N.new("ShaderNodeMapRange"); ring.clamp = True
    L.new(wv.outputs["Fac"], ring.inputs["Value"])
    ring.inputs["From Min"].default_value = 0.75; ring.inputs["From Max"].default_value = 0.95
    val = math_node('MULTIPLY_ADD', ring.outputs[0], -0.08, val)
    # 継ぎ目の上の明るい縁（型枠の板の段差）
    lip = N.new("ShaderNodeMapRange"); lip.clamp = True
    L.new(math_node('FRACT', rowf), lip.inputs["Value"])
    lip.inputs["From Min"].default_value = 0.02; lip.inputs["From Max"].default_value = 0.06
    lip.inputs["To Min"].default_value = 1.0; lip.inputs["To Max"].default_value = 0.0
    lipm = math_node('MULTIPLY', math_node('MULTIPLY', lip.outputs[0], math_node('SUBTRACT', 1.0, seam.outputs[0])), math_node('SUBTRACT', 1.0, horiz))
    val = math_node('MULTIPLY_ADD', lipm, 0.10, val)
    # 大小の斑（10〜30cm）
    mott = noise(5.0, 4, 0.5, wide=True)
    val = math_node('MULTIPLY_ADD', math_node('SUBTRACT', mott, 0.5), 0.42, val)
    # 継ぎ目に沿ったあばた（砂利の抜け）：継ぎ目の近くで、ところどころ・細かく暗い
    near = N.new("ShaderNodeMapRange"); near.clamp = True
    L.new(tri, near.inputs["Value"])
    near.inputs["From Min"].default_value = 0.03; near.inputs["From Max"].default_value = 0.14
    near.inputs["To Min"].default_value = 1.0; near.inputs["To Max"].default_value = 0.0
    patch = N.new("ShaderNodeMapRange"); patch.clamp = True
    L.new(noise(2.2, 3, 0.5, stretch=(1, 1, 0.4)), patch.inputs["Value"])
    patch.inputs["From Min"].default_value = 0.48; patch.inputs["From Max"].default_value = 0.58
    speck = N.new("ShaderNodeMapRange"); speck.clamp = True
    L.new(noise(90.0, 3, 0.7), speck.inputs["Value"])
    speck.inputs["From Min"].default_value = 0.5; speck.inputs["From Max"].default_value = 0.62
    honey = math_node('MULTIPLY', math_node('MULTIPLY', math_node('MULTIPLY', near.outputs[0], patch.outputs[0]), speck.outputs[0]), vert)
    agg = N.new("ShaderNodeMapRange"); agg.clamp = True                              # 踏面の骨材の明るい粒
    L.new(noise(140.0, 3, 0.6), agg.inputs["Value"])
    agg.inputs["From Min"].default_value = 0.58; agg.inputs["From Max"].default_value = 0.66
    aggm = math_node('MULTIPLY', agg.outputs[0], horiz)
    val = math_node('MULTIPLY_ADD', honey, -0.7, val)
    val = math_node('MULTIPLY_ADD', aggm, 0.4, val)
    dagg = N.new("ShaderNodeMapRange"); dagg.clamp = True                            # 黒い粒・黒ずみ
    L.new(noise(170.0, 3, 0.6, stretch=(1.3, 1.3, 1.3)), dagg.inputs["Value"])
    dagg.inputs["From Min"].default_value = 0.40; dagg.inputs["From Max"].default_value = 0.33
    val = math_node('MULTIPLY_ADD', math_node('MULTIPLY', dagg.outputs[0], horiz), -0.4, val)
    val = math_node('MAXIMUM', val, 0.08)
    base = hex_to_linear(base_hex)
    col = N.new("ShaderNodeMix"); col.data_type = 'RGBA'; col.blend_type = 'MULTIPLY'
    col.inputs["Factor"].default_value = 1.0
    sock(col, "A").default_value = base
    cr = N.new("ShaderNodeCombineColor")
    for i in range(3):
        L.new(val, cr.inputs[i])
    L.new(cr.outputs[0], sock(col, "B"))
    L.new(sock(col, "Result", out=True), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.82
    p.inputs["Specular IOR Level"].default_value = 0.3
    # 凹凸
    h = math_node('MULTIPLY_ADD', grain_c.outputs[0], 0.3, 0.0)
    h = math_node('MULTIPLY_ADD', sand, 0.2, h)
    h = math_node('MULTIPLY_ADD', seam_f, -0.3, h)
    h = math_node('MULTIPLY_ADD', pore.outputs[0], -0.9, h)
    h = math_node('MULTIPLY_ADD', honey, -1.2, h)
    h = math_node('MULTIPLY_ADD', ring.outputs[0], -0.3, h)
    h = math_node('MULTIPLY_ADD', lipm, 0.4, h)
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.004
    L.new(h, bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


# ------------------------------------------------------------- 舞台：壁と階段
NS, RISE, RUN = 6, 0.19, 0.36          # 段の数・蹴上げ・踏面
Y0 = 0.0                               # 最下段の鼻先
YW = Y0 + NS * RUN                     # 壁の面
X0, DX, XR = -1.15, 0.25, 7.0          # 最下段の左端・段ごとに右へ下がる量・右端（画面外）

wall_mat = concrete("wall", "#BDBBB2", seed=0.0, board_axis='Z')
step_mat = concrete("steps", "#626059", seed=2.0, board_axis='Z')
ground_mat = concrete("ground", "#7D786F", seed=5.0, board_axis='Y')

bm = box_bm(-8, 8, YW, YW + 0.3, -0.2, 5.0)
wall = to_obj("wall", bm, wall_mat, smooth=False)

riser_mat = concrete("risers", "#5E5D58", seed=3.0, board_axis='Z')
NOSE, SLAB = 0.02, 0.05              # 踏面の板の張り出し・厚み＝鼻先の下に濃い影の帯
steps = []
for k in range(NS):
    bm = box_bm(X0 + k * DX, XR, Y0 + k * RUN, YW + 0.05, -0.05, (k + 1) * RISE - SLAB)
    bevel_bm(bm, 0.004, 2)
    steps.append(to_obj("step%d" % k, bm, riser_mat))
    bm = box_bm(X0 + k * DX - NOSE, XR, Y0 + k * RUN - NOSE, YW + 0.05, (k + 1) * RISE - SLAB, (k + 1) * RISE)
    bevel_bm(bm, 0.003, 2)
    steps.append(to_obj("tread%d" % k, bm, step_mat))

# 画面の右の外にある塊（写さない）。斜めの上辺が、壁の右上に斜めの影の楔を落とす
OCC_X0 = 0.95
occ_bm = bmesh.new()
prof = [(OCC_X0 + 0.37, 1.64), (4.5, 1.64), (4.5, 5.6), (OCC_X0 + 0.37 + 1.9, 5.6)]
vs = [[occ_bm.verts.new((x, y, z)) for (x, z) in prof] for y in (YW - 0.36, YW - 0.34)]
occ_bm.faces.new(vs[0][::-1]); occ_bm.faces.new(vs[1])
for i in range(4):
    j = (i + 1) % 4
    occ_bm.faces.new((vs[0][i], vs[0][j], vs[1][j], vs[1][i]))
bmesh.ops.recalc_face_normals(occ_bm, faces=occ_bm.faces)
occ = to_obj("occluder", occ_bm, step_mat, smooth=False)
occ.visible_camera = False
occ.visible_glossy = False

bm = box_bm(-8, 8, -6, YW + 0.1, -0.1, 0.0)
ground = to_obj("ground", bm, step_mat, smooth=False)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.50, 0.60, 0.80, 1)   # 空＝影の中の青み
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.24

# ------------------------------------------------------------- 被写体：卓上ランプ3台
# 笠＝丸い肩の低い帽子形（外周がわずかに裾広がり）・細い軸・平たい台座。頂に小さな押しボタン
SH_R, SH_H = 0.092, 0.078
shade_prof = round_profile([
    (0.0, SH_H), (SH_R - 0.006, SH_H, 0.040), (SH_R, 0.003, 0.0015), (SH_R - 0.0035, 0.0, 0.0015),
    (SH_R - 0.0065, SH_H - 0.004, 0.036), (0.0, SH_H - 0.004)], 0.03, n=10)
base_prof = round_profile([
    (0.0, 0.0), (0.066, 0.0, 0.004), (0.070, 0.012, 0.010), (0.050, 0.036, 0.026), (0.0, 0.038)], 0.01, n=10)
STEM_H = 0.185

lamp_mats = {
    "orange": principled("lac_orange", hex_to_linear("#8E3514"), rough=0.16, coat=1.0, coat_rough=0.02),
    "cream": principled("lac_cream", hex_to_linear("#EBDDB5"), rough=0.16, coat=1.0, coat_rough=0.02),
    "navy": principled("lac_navy", hex_to_linear("#0F1A36"), rough=0.16, coat=1.0, coat_rough=0.02),
}
steel = principled("steel", hex_to_linear("#C8C8C6"), rough=0.22, metal=1.0)
opal = principled("opal", hex_to_linear("#F2EFE8"), rough=0.5)

LAMPS = [   # (色, 段, x, 踏面の中の奥行き 0〜1, 回転°)
    ("orange", 4, -0.12, 1.45, 20),
    ("cream", 5, 0.30, 0.40, -10),
    ("navy", 5, 0.62, 0.55, 35),
]
parts, lamp_roots = [], []
for name, k, x, fy, rot in LAMPS:
    z0 = (k + 1) * RISE
    y = Y0 + k * RUN + fy * RUN
    root = bpy.data.objects.new("lamp_" + name, None); scene.collection.objects.link(root)
    root.location = (x, y, z0)
    root.rotation_euler = (0, 0, math.radians(rot))
    root.scale = (1.2, 1.2, 1.2)
    mat = lamp_mats[name]
    b = lathe("base_" + name, base_prof, mat=mat)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=0.0075, radius2=0.0075, depth=STEM_H + 0.03)
    for v in bm.verts:
        v.co.z += 0.034 + (STEM_H + 0.03) / 2
    bevel_bm(bm, 0.0015, 2)
    stem = to_obj("stem_" + name, bm, mat)
    sh = lathe("shade_" + name, shade_prof, loc=(0, 0, 0.034 + STEM_H), mat=mat)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=SH_R - 0.012, radius2=SH_R - 0.012, depth=0.003)
    dif = to_obj("diffuser_" + name, bm, opal, loc=(0, 0, 0.034 + STEM_H + 0.022))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.0055, radius2=0.0055, depth=0.006)
    bevel_bm(bm, 0.0012, 2)
    btn = to_obj("button_" + name, bm, steel, loc=(0, 0, 0.034 + STEM_H + SH_H + 0.002))
    for o in (b, stem, sh, dif, btn):
        o.parent = root
    parts.append(root); lamp_roots.append(root)
    parts += [b, stem, sh, dif, btn]

# ------------------------------------------------------------- 光：硬い日差し1灯＋空
sun_d = bpy.data.lights.new("sun", 'SUN')
sun_d.energy = 6.0
sun_d.angle = math.radians(1.0)
sun_d.color = (1.0, 0.95, 0.87)
sun = bpy.data.objects.new("sun", sun_d); scene.collection.objects.link(sun)
SUN_AZ, SUN_EL = -32.0, 50.0      # 方位（+x から反時計回り・光が来る側）・高度


def sun_dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))   # 太陽のある向き


def set_sun(az, el):
    d = sun_dir(az, el)
    sun.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()


set_sun(SUN_AZ, SUN_EL)

# 映り込み専用の板：カメラの後ろ上。塗膜に空の白い斑を映す（カメラ・拡散・影には出さない）
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-2.5, -6.0, 5.0))
refl = bpy.context.object; refl.name = "reflector"
refl.scale = (9.0, 5.0, 1.0)
refl.rotation_euler = (Vector((0.3, 1.8, 1.1)) - refl.location).to_track_quat('Z', 'Y').to_euler()
rm = bpy.data.materials.new("refl"); rm.use_nodes = True
rn = rm.node_tree.nodes; rn.remove(rn["Principled BSDF"])
em = rn.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.4
em.inputs["Color"].default_value = (0.92, 0.95, 1.0, 1)
rm.node_tree.links.new(em.outputs[0], rn["Material Output"].inputs["Surface"])
gtc = rn.new("ShaderNodeTexCoord"); gmp = rn.new("ShaderNodeMapping")       # 縁の無い映り込み：中心から縁へ落とす
gmp.inputs["Location"].default_value = (0, 0, 0); gmp.inputs["Scale"].default_value = (2.0, 2.0, 1.0)
rm.node_tree.links.new(gtc.outputs["Object"], gmp.inputs["Vector"])
grd = rn.new("ShaderNodeTexGradient"); grd.gradient_type = 'QUADRATIC_SPHERE'
rm.node_tree.links.new(gmp.outputs[0], grd.inputs["Vector"])
gm = rn.new("ShaderNodeMath"); gm.operation = 'MULTIPLY'; gm.inputs[1].default_value = 2.2
rm.node_tree.links.new(grd.outputs["Fac"], gm.inputs[0])
rm.node_tree.links.new(gm.outputs[0], em.inputs["Strength"])
refl.data.materials.append(rm)
refl.visible_camera = False; refl.visible_diffuse = False; refl.visible_shadow = False
refl.visible_transmission = False; refl.visible_volume_scatter = False

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
cd.clip_start = 0.02
scene.camera = cam


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


HERO_LOC, HERO_TGT = Vector((0.0, -1.95, 1.55)), Vector((0.22, 1.7, 0.92))

OR = Vector((-0.12, 1.96, 1.24))       # 橙の笠の肩
SHOTS = [
    dict(sec=3.0,   # 光の走り：壁ぎわの低い位置から斜めに見て、日が回って橙の影が壁を渡る
         cam=lambda t: (lerp((-1.05, 0.95, 1.18), (-0.98, 0.98, 1.20), ease(t)), Vector((-0.28, 2.1, 1.10)), 50, 5.6, None)),
    dict(sec=2.5,   # マクロ：橙の笠の肩をなめる。ピントを壁の影→笠の肩へ送る
         cam=lambda t: (lerp((0.30, 1.30, 1.36), (0.22, 1.36, 1.33), ease(t)), OR + Vector((0.0, 0.0, -0.02)),
                        120, 4.0, 1.05 - 0.45 * ease(t))),
    dict(sec=3.0,   # スライド：踏面すれすれの高さで横に滑り、クリームと紺の前を抜ける
         cam=lambda t: (lerp((-0.25, 0.95, 1.24), (0.95, 0.95, 1.27), ease(t)),
                        lerp((0.05, 1.97, 1.22), (0.75, 1.97, 1.22), ease(t)), 50, 4.0, None)),
    dict(sec=3.0,   # 決め：引きながら入って hero で止まる
         cam=lambda t: (lerp(HERO_LOC + Vector((-0.25, 0.9, -0.25)), HERO_LOC, ease_out(min(1.0, t / 0.6))),
                        lerp(HERO_TGT + Vector((-0.1, 0, -0.1)), HERO_TGT, ease_out(min(1.0, t / 0.6))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh_ in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh_["frames"] = round(sh_["sec"] * FPS)
    N_FRAMES += sh_["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    for r, (_, _, _, _, rot) in zip(lamp_roots, LAMPS):
        r.rotation_euler = (0, 0, math.radians(rot))


def light_path(i, t):
    if i == 0:
        set_sun(SUN_AZ - 30 + 30 * ease(t), SUN_EL - 12 + 12 * ease(t))
    else:
        set_sun(SUN_AZ, SUN_EL)


for i, sh_ in enumerate(SHOTS):
    for k in range(sh_["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh_["frames"] - 1)
        T = (f - 1) / max(1, N_FRAMES - 1)
        loc, tgt, lens, fstop, focus = sh_["cam"](t)
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
        for o in lamp_roots:
            o.keyframe_insert("rotation_euler", frame=f)
            o.keyframe_insert("location", frame=f)
        light_path(i, t)
        sun.keyframe_insert("rotation_euler", frame=f)

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

if "shots" in modes:
    for i, sh_ in enumerate(SHOTS):
        for j, frac in enumerate((0.0, 0.5, 1.0)):
            fr = shot_start[i] + round(frac * (sh_["frames"] - 1))
            still(os.path.join(OUT, "_shot_%d_%d.png" % (i, j)), 480, 24, fr)
    print(">> shots done")

if "still" in modes:
    still(os.path.join(OUT, "hero.png"), 2560, 256)
    print(">> hero done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = res(int(os.environ.get("II_ANIM_LONG", "1080")))
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
