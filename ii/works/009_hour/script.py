# =============================================================
# MIDDLE STUDIES II 009 HOUR — ブレスレットを輪にして紙の上に置いた腕時計（OBJECT）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots
#
# 基準：Braun 公式のスライダー画像（光・素材・構図・色の組み立てだけを取る。造形・文字盤の意匠は自分で起こす）
# 縮尺：1単位＝10cm（1mm＝0.01）。#101：10倍で組んだぶん f値も1/10 にする
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}
MM = 0.01

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(21, 9),
    lens=100,
    fstop=1.2,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=-1.1,
    paper="#E2E2E0",
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


def to_obj(name, bm, mat=None, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


def prism(bm, outline, z0, z1, matrix=Matrix()):
    """xy の輪郭を z0→z1 に押し出した角柱を bm に足す"""
    vs0 = [bm.verts.new(matrix @ Vector((x, y, z0))) for x, y in outline]
    vs1 = [bm.verts.new(matrix @ Vector((x, y, z1))) for x, y in outline]
    n = len(outline)
    bm.faces.new(list(reversed(vs0)))
    bm.faces.new(vs1)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i]))


def box(bm, cx, cy, sx, sy, z0, z1, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    pts = [(-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)]
    prism(bm, [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts], z0, z1)


def round_profile(pts, r, n=4):
    """(r,z,mat) の折れ線の角を半径 r で丸める（滑らかシェーディングで角が汚れないように）"""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = Vector(pts[i - 1][:2]), Vector(pts[i][:2]), Vector(pts[i + 1][:2])
        rr = pts[i][3] if len(pts[i]) > 3 else r
        d0, d1 = (p0 - p1), (p2 - p1)
        l = min(rr, d0.length * 0.45, d1.length * 0.45)
        a, b = p1 + d0.normalized() * l, p1 + d1.normalized() * l
        for k in range(n + 1):
            t = k / n
            q = (1 - t) ** 2 * a + 2 * (1 - t) * t * p1 + t * t * b
            out.append((q.x, q.y, pts[i - 1][2] if k < n / 2 else pts[i][2]))
    out.append(pts[-1])
    return out


def lathe(name, prof, seg=160):
    """(r,z,mat) の断面を Z 軸まわりに回す。mat は次の点までの区間の材質番号"""
    bm = bmesh.new()
    rings = []
    for (r, z, m) in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
                          for k in range(seg)])
    for i in range(len(rings) - 1):
        A, B, m = rings[i], rings[i + 1], prof[i][2]
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(A) == 1:
                f = bm.faces.new((A[0], B[k], B[k2]))
            elif len(B) == 1:
                f = bm.faces.new((A[k], B[0], A[k2]))
            else:
                f = bm.faces.new((A[k], B[k], B[k2], A[k2]))
            f.material_index = m
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_obj(name, bm)


def mat_nodes(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree, m.node_tree.nodes["Principled BSDF"]


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, trans=0.0, ior=1.45):
    m, nt, p = mat_nodes(name)
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    return m


def steel(name, rough, aniso, axis='Z', hair=0.0, color="#C9CBCC"):
    """ヘアラインのステンレス：異方性＋細く引き伸ばしたノイズのバンプ（#106：寄与は小さく）"""
    m, nt, p = mat_nodes(name)
    p.inputs["Base Color"].default_value = hex_to_linear(color)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = rough
    p.inputs["Anisotropic"].default_value = aniso
    tg = nt.nodes.new("ShaderNodeTangent"); tg.direction_type = 'RADIAL'; tg.axis = axis
    nt.links.new(tg.outputs["Tangent"], p.inputs["Tangent"])
    if hair > 0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        sc = {'X': (900, 6, 6), 'Y': (6, 900, 6), 'Z': (6, 6, 900)}[axis]
        mp.inputs["Scale"].default_value = sc
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
        nz.inputs["Detail"].default_value = 2.0
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = hair
        bp.inputs["Distance"].default_value = 0.0005
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def grained(name, color, rough, scale, strength, dist=0.0003):
    """砂目・紙の肌：細かいノイズのバンプ"""
    m, nt, p = mat_nodes(name)
    p.inputs["Base Color"].default_value = hex_to_linear(color)
    p.inputs["Roughness"].default_value = rough
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 4.0
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = strength
    bp.inputs["Distance"].default_value = dist
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0), size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color = energy, color
    if size_y:
        ld.shape, ld.size, ld.size_y = 'RECTANGLE', size, size_y
    else:
        ld.shape, ld.size = 'SQUARE', size
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


# ------------------------------------------------------------- 材質
M_CASE = steel("case_brushed", 0.34, 0.55, 'Z', hair=0.25)
M_POL = steel("case_polished", 0.16, 0.0, 'Z', color="#D2D4D5")
M_LINK = steel("link_brushed", 0.40, 0.2, 'X', hair=0.12)
M_DIAL = grained("dial", "#B6B7B4", 0.55, 900, 0.18)
M_INK = principled("ink", hex_to_linear("#1E1F20"), rough=0.35)
M_HAND = principled("hand", hex_to_linear("#1A1B1C"), rough=0.22, coat=0.4)
M_ACC = principled("accent", (0.80, 0.05, 0.0, 1.0), rough=0.4, coat=0.0)
# 🔴 針と差し色は鏡面を絞る：明るい環境（光沢の光線だけ 0.92）を映して、黒が灰に・橙が桃色に褪せた（round 11）
for _m in (M_INK, M_HAND, M_ACC):
    _m.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.12
M_GREY = grained("subring", "#BDBEBB", 0.45, 1400, 0.1)
def thin_glass(name):
    """風防：屈折させない（厚い縁が文字盤の縁に色の輪を描いた）。透過＋フレネルの鏡面だけ"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.03
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = 1.5
    mx = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    # 🔴 影の光線は素通しにする：透過＋鏡面の Mix のままだと、文字盤が風防なしの 232 → 154 まで暗くなった
    lp = nt.nodes.new("ShaderNodeLightPath")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
    nt.links.new(lp.outputs["Is Shadow Ray"], inv.inputs[1])
    nt.links.new(fr.outputs[0], mul.inputs[0]); nt.links.new(inv.outputs[0], mul.inputs[1])
    nt.links.new(mul.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


M_GLASS = thin_glass("crystal")
M_PAPER = grained("paper", LOOK["paper"], 0.8, 260, 0.12, 0.0008)
# 文字盤と紙も同じ：金属のための明るい環境を拡散面が鏡面で拾い、文字盤の色を2段暗くしても明るさが動かなかった
for _m, _v in ((M_DIAL, 0.15), (M_PAPER, 0.2)):
    _m.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = _v

# ------------------------------------------------------------- 舞台：紙
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
paper = bpy.context.object; paper.name = "paper"
paper.scale = (12, 8, 1)
paper.data.materials.append(M_PAPER)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.9, 0.9, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.05
# 金属が映す環境だけを明るくする（撮影ではレフ板と白い天井に囲まれている）。拡散には暗いまま＝影を埋めない
_wn = world.node_tree
_lp = _wn.nodes.new("ShaderNodeLightPath")
_bright = _wn.nodes.new("ShaderNodeBackground")
_bright.inputs["Color"].default_value = (0.92, 0.92, 0.92, 1); _bright.inputs["Strength"].default_value = 0.75
_mx = _wn.nodes.new("ShaderNodeMixShader")
_wn.links.new(_lp.outputs["Is Glossy Ray"], _mx.inputs[0])
_wn.links.new(_wn.nodes["Background"].outputs[0], _mx.inputs[1])
_wn.links.new(_bright.outputs[0], _mx.inputs[2])
_wn.links.new(_mx.outputs[0], _wn.nodes["World Output"].inputs["Surface"])

# ------------------------------------------------------------- 被写体：時計
# ブレスレットを輪にして立てた上に、頭（ケース）が水平に載っている＝紙から浮いた高さが影のずれになる
R_CASE = 20 * MM
LUG_Y = 22.5 * MM
LINK_W, LINK_T, LINK_PITCH, LINK_GAP = 20 * MM, 3.0 * MM, 4.6 * MM, 0.3 * MM
EA, EB = 35 * MM, 8.0 * MM                      # ブレスレットの輪（YZ の楕円）
ECZ = EB + LINK_T / 2
TOP_Z = ECZ + EB * math.sqrt(max(0.0, 1 - (LUG_Y / EA) ** 2))   # 輪の上端（ラグの位置）
H0 = TOP_Z - 4.2 * MM                            # ケースの底の高さ
HEAD = Vector((0, 0, H0))

# ケース断面（r, z, 材質 0=ヘアライン 1=鏡面）。z はケースの底から
case_prof = round_profile([
    (0.0, 0.0, 0), (15.5, 0.0, 0), (18.4, 1.2, 0), (20.0, 3.6, 0), (20.0, 7.6, 1),
    (19.3, 9.3, 1, 0.25), (18.0, 9.9, 1, 0.2), (17.35, 9.6, 0, 0.1), (17.35, 7.3, 0, 0.1), (0.0, 7.3, 0),
], 0.5)
case = lathe("case", [(r * MM, z * MM, m) for r, z, m in case_prof])
case.data.materials.append(M_CASE); case.data.materials.append(M_POL)
case.location = HEAD

# 風防：わずかに膨らんだ円板
# 🔴 上面だけの殻にする：厚みのある円板だと、縁と裏面の多重反射が秒針の橙を文字盤の外周に輪として描いた
crys_prof = [(0.0, 10.05, 0), (8, 10.0, 0), (14, 9.9, 0), (17.3, 9.7, 0)]
crystal = lathe("crystal", [(r * MM, z * MM, m) for r, z, m in crys_prof], seg=128)
crystal.data.materials.append(M_GLASS)
crystal.location = HEAD
if os.environ.get('NOCRYS'): crystal.hide_render = True

# 文字盤（砂目）＋ 小窓の段（6時の24時間計）
dial_prof = [(0.0, 7.5, 0), (17.35, 7.5, 0), (17.35, 7.3, 0), (0.0, 7.3, 0)]
dial = lathe("dial", [(r * MM, z * MM, m) for r, z, m in dial_prof], seg=128)
dial.data.materials.append(M_DIAL)
dial.location = HEAD

Z_DIAL = 7.5 * MM
SUB = Vector((0, -8.2 * MM, 0))
bm = bmesh.new()
# 時の目盛り：細い棒。12時は2本・6時は小窓があるので置かない
for h in range(12):
    if h == 6:
        continue
    a = math.radians(90 - 30 * h)
    rin, rout = (11.8, 15.6) if h % 3 == 0 else (13.2, 15.6)
    rm = (rin + rout) / 2 * MM
    wide = 0.55 * MM
    if h == 0:
        for dx in (-0.6, 0.6):
            box(bm, dx * MM, rm, wide, (rout - rin) * MM, Z_DIAL, Z_DIAL + 0.12 * MM)
    else:
        box(bm, rm * math.cos(a), rm * math.sin(a), (rout - rin) * MM, wide, Z_DIAL, Z_DIAL + 0.12 * MM, a)
indices = to_obj("indices", bm, M_INK, smooth=False)
indices.location = HEAD

bm = bmesh.new()
# 分の目盛り：60本の細い線（外周の段の上）
for k in range(60):
    if k % 5 == 0:
        continue
    a = math.radians(90 - 6 * k)
    rm = 16.45 * MM
    box(bm, rm * math.cos(a), rm * math.sin(a), 0.9 * MM, 0.22 * MM, Z_DIAL, Z_DIAL + 0.06 * MM, a)
# 小窓の目盛り（24分割）
for k in range(24):
    a = math.radians(90 - 15 * k)
    ln = 0.9 if k % 6 == 0 else 0.5
    rm = (3.6 - ln / 2) * MM
    box(bm, SUB.x + rm * math.cos(a), SUB.y + rm * math.sin(a), ln * MM, 0.2 * MM,
        Z_DIAL + 0.05 * MM, Z_DIAL + 0.1 * MM, a)
ticks = to_obj("ticks", bm, M_INK, smooth=False)
ticks.location = HEAD

# 小窓：一段沈めた皿（外周に細い鏡面の縁）
# 小窓：文字盤の上に薄い皿を載せ、外周に細い鏡面の縁（文字盤の板の下に沈めると隠れて見えなかった＝round 9）
sub_prof = [(0.0, 0.05, 0), (3.85, 0.05, 1), (4.0, 0.16, 1), (4.3, 0.16, 1), (4.45, 0.0, 0), (0.0, 0.0, 0)]
subdial = lathe("subdial", [(r * MM, z * MM + Z_DIAL, m) for r, z, m in sub_prof], seg=96)
subdial.data.materials.append(M_GREY); subdial.data.materials.append(M_POL)
subdial.location = HEAD + SUB


def hand(name, length, tail, w_root, w_tip, z, thick, mat, pivot=Vector((0, 0, 0))):
    """針：根元から先へ細る平板。軸は原点・向きは +Y（12時）"""
    bm = bmesh.new()
    outline = [(-w_root / 2, -tail), (w_root / 2, -tail), (w_tip / 2, length), (-w_tip / 2, length)]
    prism(bm, outline, 0, thick)
    bevel_bm(bm, min(w_tip, thick) * 0.3, segments=2)
    ob = to_obj(name, bm, mat)
    ob.location = HEAD + pivot + Vector((0, 0, z))
    return ob


hour_h = hand("hour", 9.8 * MM, 1.8 * MM, 1.7 * MM, 1.2 * MM, Z_DIAL + 0.55 * MM, 0.3 * MM, M_HAND)
min_h = hand("minute", 15.0 * MM, 2.2 * MM, 1.3 * MM, 0.8 * MM, Z_DIAL + 0.95 * MM, 0.3 * MM, M_HAND)
sec_h = hand("second", 15.8 * MM, 4.2 * MM, 0.58 * MM, 0.42 * MM, Z_DIAL + 1.35 * MM, 0.18 * MM, M_ACC)
sub_h = hand("sub", 3.0 * MM, 0.6 * MM, 0.5 * MM, 0.3 * MM, Z_DIAL + 0.2 * MM, 0.15 * MM, M_HAND, SUB)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=1.25 * MM, radius2=1.25 * MM, depth=0.3 * MM)
bevel_bm(bm, 0.08 * MM)
cap = to_obj("cap", bm, M_ACC)
cap.location = HEAD + Vector((0, 0, Z_DIAL + 1.6 * MM))

# リューズ（3時）：刻みを入れた円筒
bm = bmesh.new()
N_KN = 30


rings = []
for x in (0.0, 2.8 * MM):
    ring = []
    for k in range(N_KN * 2):
        a = 2 * math.pi * k / (N_KN * 2)
        r = (2.6 if k % 2 == 0 else 2.35) * MM
        ring.append(bm.verts.new((x, r * math.cos(a), r * math.sin(a))))
    rings.append(ring)
n = N_KN * 2
bm.faces.new(list(reversed(rings[0])))
bm.faces.new(rings[1])
for k in range(n):
    k2 = (k + 1) % n
    bm.faces.new((rings[0][k], rings[0][k2], rings[1][k2], rings[1][k]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bevel_bm(bm, 0.12 * MM, segments=2, angle=60)
crown = to_obj("crown", bm, M_CASE)
crown.location = HEAD + Vector((20.3 * MM, 0, 5.4 * MM))
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=1.2 * MM, radius2=1.2 * MM, depth=1.2 * MM,
                      matrix=Matrix.Translation((19.8 * MM, 0, 5.4 * MM)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
stem = to_obj("stem", bm, M_CASE)
stem.location = HEAD

# ラグ：ケースの下からブレスレットを受ける台（上下）
lugs = []
for sgn in (1, -1):
    bm = bmesh.new()
    # ケース側で広く、ブレスレット側で細る台形（四角い箱だと継ぎ目が工作物に見えた＝round 9）
    prism(bm, [(-13.5 * MM, -3.5 * MM), (13.5 * MM, -3.5 * MM), (10.9 * MM, 3.5 * MM), (-10.9 * MM, 3.5 * MM)], 0, 5.4 * MM)
    bevel_bm(bm, 1.4 * MM, segments=5)
    ob = to_obj("lug%+d" % sgn, bm, M_CASE)
    ob.location = HEAD + Vector((0, sgn * 18.2 * MM, 0.9 * MM))
    ob.rotation_euler = (0, 0, 0 if sgn > 0 else math.pi)
    lugs.append(ob)

# ブレスレット：1枚のコマを楕円の輪に沿って並べる（同じメッシュを共有）
bm = bmesh.new()
box(bm, 0, 0, LINK_W, LINK_PITCH - LINK_GAP, -LINK_T / 2, LINK_T / 2)
bevel_bm(bm, 0.25 * MM, segments=3)
link_me = bpy.data.meshes.new("link")
bm.to_mesh(link_me); bm.free()
for p in link_me.polygons:
    # 平らな面は平らに塗る（全面を滑らかにすると、面取りの法線が天面に滲んで各コマが波打った筒に見えた）
    p.use_smooth = max(abs(c) for c in p.normal) < 0.99
link_me.materials.append(M_LINK)


def ell(phi):
    return Vector((0, EA * math.sin(phi), ECZ + EB * math.cos(phi)))


# 弧長の表
phi0 = math.asin(LUG_Y / EA)
Ns = 4000
phis = [phi0 + (2 * math.pi - 2 * phi0) * i / Ns for i in range(Ns + 1)]
acc = [0.0]
for i in range(Ns):
    acc.append(acc[-1] + (ell(phis[i + 1]) - ell(phis[i])).length)
total = acc[-1]
n_links = int(total / LINK_PITCH)
links = []
j = 0
for k in range(n_links):
    s = (k + 0.5) * total / n_links
    while acc[j + 1] < s:
        j += 1
    phi = phis[j] + (phis[j + 1] - phis[j]) * (s - acc[j]) / (acc[j + 1] - acc[j])
    p = ell(phi)
    t = Vector((0, EA * math.cos(phi), -EB * math.sin(phi))).normalized()
    X = Vector((1, 0, 0))
    Z = X.cross(t)                       # 輪の外向き
    if Z.dot(p - Vector((0, 0, ECZ))) < 0:
        Z = -Z
    Y = Z.cross(X)
    ob = bpy.data.objects.new("link%02d" % k, link_me)
    ob.matrix_world = Matrix.Translation(p) @ Matrix((X, Y, Z)).transposed().to_4x4()
    scene.collection.objects.link(ob)
    links.append(ob)

parts = [case, crystal, dial, indices, ticks, subdial, hour_h, min_h, sec_h, sub_h, cap, crown, stem] + lugs + links
ANIM = [sec_h, min_h, hour_h, sub_h]

# ------------------------------------------------------------- 光：奥やや左からの大きな窓光＋紙の照り返し
KEY_LOC = Vector((-3.0, 4.2, 4.4))
FLAG_X, FLAG_TOP = -3.0, 2.45
key_light = area("key", KEY_LOC, 5.0, 460, (1.0, 0.985, 0.965), target=(0.9, 0.3, 0), size_y=2.4)
key_light.data.spread = math.radians(52)   # 光の広がりを絞って、紙に明暗の傾きを作る（基準：左が落ちる）
# 消し板（#101）：キーと紙の左側のあいだに黒い板を立て、左だけを柔らかく落とす（広がりは面が大きいと効かない）
bm = bmesh.new()
for v in [(0, -3.0, 0.3), (0, 5.0, 0.3), (0, 5.0, FLAG_TOP), (0, -3.0, FLAG_TOP)]:
    bm.verts.new(v)
bm.faces.new(bm.verts)
flag = to_obj("flag", bm, principled("flag", (0.01, 0.01, 0.01, 1), rough=0.9), smooth=False)
flag.location = (FLAG_X, 0, 0)
flag.visible_camera = False
fill = area("fill", (0.4, -0.6, 3.0), 3.0, 60, (1, 1, 1), target=(0.3, 0, 0))
fill.data.energy = 3
fill.data.specular_factor = 0.0

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam
cd.clip_start = 0.01

# ------------------------------------------------------------- 時刻（hero：10時8分36秒）
T_H, T_M, T_S = 10, 8, 36.0


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


# hero の構図：真上から。時計を画面の右 2/3 に
HERO_H = 7.9          # カメラの高さ（紙から）
FRAME_W = 36 / LOOK["lens"] * (HERO_H - H0)
HERO_CAM = Vector((-0.17 * FRAME_W, 0.025, HERO_H))
HERO_TGT = Vector((HERO_CAM.x, HERO_CAM.y + 0.0001, 0))
C = HEAD + Vector((0, 0, Z_DIAL))

SHOTS = [
    dict(sec=3.0,   # スライド：低い位置から、ブレスレットがケースへ入っていく線を横に滑る
         cam=lambda t: (lerp((0.42, 0.95, 0.30), (-0.22, 0.90, 0.30), ease(t)),
                        lerp((0.05, 0.12, 0.17), (-0.03, 0.10, 0.17), ease(t)), 85, 2.0, None)),
    dict(sec=3.0,   # マクロ：秒針が外周の目盛りを渡る・ピントを中心から外周へ送る
         cam=lambda t: (lerp((0.36, -0.46, 0.80), (0.31, -0.41, 0.76), ease(t)), C + Vector((0.04, -0.03, 0)),
                        135, 11.0, (C - lerp((0.36, -0.46, 0.80), (0.31, -0.41, 0.76), ease(t))).length - 0.05 + 0.10 * ease(t))),
    dict(sec=2.5,   # 光の走り：斜め上から止めて、窓光を横に動かす
         cam=lambda t: (Vector((-0.55, -0.95, 1.05)), C + Vector((0.02, 0.0, -0.05)), 100, 1.4, None)),
    dict(sec=3.0,   # 決め：少し回りながら降りてきて真上で止まる
         cam=lambda t: (lerp(HERO_CAM + Vector((0.25, -0.35, 2.5)), HERO_CAM, ease_out(min(1.0, t / 0.62))),
                        None, LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def set_time(f):
    """秒針はスイープ（6°/秒）。hero のフレームで T_H:T_M:T_S"""
    ds = (f - STILL_FRAME) / FPS
    s = T_S + ds
    m = T_M + s / 60
    h = T_H + m / 60
    sec_h.rotation_euler = (0, 0, -math.radians(6 * s))
    min_h.rotation_euler = (0, 0, -math.radians(6 * m))
    hour_h.rotation_euler = (0, 0, -math.radians(30 * h))
    sub_h.rotation_euler = (0, 0, -math.radians(15 * h))


def light_path(i, t):
    if i == 2:
        key_light.location = lerp(KEY_LOC + Vector((-2.2, -0.8, 0)), KEY_LOC + Vector((2.6, 0.4, 0)), ease(t))
    else:
        key_light.location = KEY_LOC
    key_light.rotation_euler = (Vector((0.9, 0.3, 0)) - key_light.location).to_track_quat('-Z', 'Y').to_euler()


for i, sh in enumerate(SHOTS):
    for k in range(sh["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh["frames"] - 1)
        loc, tgt, lens, fstop, focus = sh["cam"](t)
        if tgt is None:        # 決め：真上から見下ろす。回転は画面の上＝+Y にそろえる
            cam.location = loc
            ang = 0.35 * (1 - ease_out(min(1.0, t / 0.62)))
            cam.rotation_euler = (0, 0, ang)
            dist = loc.z - C.z
        else:
            cam.location = loc
            cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
            dist = (Vector(tgt) - Vector(loc)).length
        cd.lens = lens
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus if focus else dist
        for path in ("location", "rotation_euler"):
            cam.keyframe_insert(path, frame=f)
        cd.keyframe_insert("lens", frame=f)
        cd.dof.keyframe_insert("aperture_fstop", frame=f)
        cd.dof.keyframe_insert("focus_distance", frame=f)
        set_time(f)
        for o in ANIM:
            o.keyframe_insert("rotation_euler", frame=f)
        light_path(i, t)
        key_light.keyframe_insert("location", frame=f)
        key_light.keyframe_insert("rotation_euler", frame=f)

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
    film_grain(path)


def film_grain(path, sigma=2.4 / 255, seed=9):
    """紙のざらつき＝写真の粒を後から乗せる（#104：レンダー内の細かいノイズはモアレになる）。003 の手"""
    import numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, sigma, (w * h, 1)).astype(np.float32)
    px[:, :3] = np.clip(px[:, :3] + n, 0.0, 1.0)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = path; img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


if "test" in modes:
    still(os.path.join(OUT, "_test.png"), 720, 48)
    print(">> test done")

if "testhero" in modes:
    still(os.path.join(OUT, "_testhero.png"), 1600, 128)
    print(">> testhero done")

if "shots" in modes:
    for i, sh in enumerate(SHOTS):
        for j, frac in enumerate((0.0, 0.5, 1.0)):
            fr = shot_start[i] + round(frac * (sh["frames"] - 1))
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
