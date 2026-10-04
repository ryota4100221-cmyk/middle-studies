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

# ------------------------------------------------------------- LOOK（013 GRILLE）
LOOK = dict(
    aspect=(1, 1),
    lens=85,                  # 縮尺10倍（1単位＝10cm）。f値は実寸の1/10前後で読む（#101）
    fstop=2.8,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=0.0,
    bg=(0.035, 0.035, 0.035),
)
FPS = 24
# 尺（N_FRAMES）と静止画のフレーム（STILL_FRAME）は、下の「動画」節の SHOTS から決まる

# 納品寸法：長辺で決める（hero 2560 / loop 1080）
def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


def hex_to_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


# ------------------------------------------------------------- 初期化
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------- 造形の道具
def bevel_obj(ob, width, segments=3, clamp=True, angle=30):
    """🔴 面取りは bmesh で（BEVELモディファイア＋harden_normals は硬く見える）。
    Boolean 合体後の仕上げは clamp=False（clamp=True だと極小エッジに引っ張られ面取りが0に縮む）。
    薄板に clamp=False を掛けると反転して針状に潰れる＝薄いものは合体に混ぜず clamp=True で別部品。"""
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    edges = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(angle)]
    bmesh.ops.bevel(bm, geom=edges, offset=width, segments=segments, profile=0.5,
                    affect='EDGES', clamp_overlap=clamp)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return ob


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, trans=0.0, ior=1.45):
    """roughness の目安：モノは 0.16〜0.55（0.8 はキャラの肌の値で、モノが粘土に見える）"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    return m


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.8), shape='RECTANGLE'):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.shape, ld.size = energy, color, shape, size
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


def sock(node, name, kind):
    return next(s for s in node.inputs if s.name == name and s.type == kind)


PAPER_LO, PAPER_HI = 0.08, 1.35
PAPER_Y0, PAPER_Z = -1.0, 1.5
CAV_EMIT = 0.02
# ------------------------------------------------------------- 舞台（013：チャコールの無限背景紙）
# 縮尺10倍（1単位＝10cm）。床と奥の壁を大きな R でつなぎ、継ぎ目を見せない
R, W, D, H = 6.0, 60.0, 14.0, 24.0
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 24 * math.pi / 2 for i in range(1, 25)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + 3.0, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
paper = principled("paper", LOOK["bg"] + (1.0,), rough=0.85)
paper.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15
# 地の上下の明暗：床を沈め、壁の上ほど明るく（基準＝上68→下59）。光で作ると継ぎ目に段が出た（round 5）
_n = paper.node_tree.nodes; _l = paper.node_tree.links
_g = _n.new("ShaderNodeNewGeometry"); _sx = _n.new("ShaderNodeSeparateXYZ")
_l.new(_g.outputs["Position"], _sx.inputs[0])
_mr = _n.new("ShaderNodeMapRange"); _mr.clamp = True
_mr.inputs["From Min"].default_value = PAPER_Y0; _mr.inputs["From Max"].default_value = PAPER_Z
_mr.inputs["To Min"].default_value = PAPER_LO; _mr.inputs["To Max"].default_value = PAPER_HI
# 🔴 Z だけで落とすと、被写体の天面の後ろに見える奥の床（z≈0）まで暗くなり、上辺が地に溶けた（round 33）。
#    手前の床だけを落とす＝Y+Z で測る（被写体より奥は明るいまま）
_yz = _n.new("ShaderNodeMath"); _yz.operation = 'ADD'
_l.new(_sx.outputs["Y"], _yz.inputs[0]); _l.new(_sx.outputs["Z"], _yz.inputs[1])
_l.new(_yz.outputs[0], _mr.inputs["Value"])
_mul = _n.new("ShaderNodeMix"); _mul.data_type = 'RGBA'; _mul.blend_type = 'MULTIPLY'
_mul.inputs["Factor"].default_value = 1.0
sock(_mul, "A", 'RGBA').default_value = LOOK["bg"] + (1.0,)
_l.new(_mr.outputs["Result"], sock(_mul, "B", 'RGBA'))
_l.new(next(s_ for s_ in _mul.outputs if s_.type == 'RGBA'), _n["Principled BSDF"].inputs["Base Color"])
sweep.data.materials.append(paper)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.05, 0.05, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.08


# ------------------------------------------------------------- 被写体：携帯スピーカー
BW, BD, BH = 2.30, 0.86, 1.02          # 幅23cm・奥行8.6cm・高さ10.2cm
Z0 = BH / 2
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, Z0))
body = bpy.context.object; body.name = "body"
body.scale = (BW, BD, BH); bpy.ops.object.transform_apply(scale=True)
bevel_obj(body, 0.15, segments=10)
# 正面のくぼみ（グリルの窓）
FM = 0.11                               # 枠の太さ
GW, GH = BW - 2 * FM, BH - 2 * FM
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -BD / 2, Z0))
cut = bpy.context.object; cut.name = "cut"
cut.scale = (GW, 0.30, GH); bpy.ops.object.transform_apply(scale=True)
bevel_obj(cut, 0.07, segments=8)
md = body.modifiers.new("cut", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut; md.solver = 'EXACT'
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="cut")
bpy.data.objects.remove(cut)
bevel_obj(body, 0.012, segments=3, clamp=False, angle=40)
body.data.materials.clear()


def leather_mat():
    """シボ革：大きく不揃いな粒（しわの網目＝Voronoi の縁を溝に）＋粒の中の細かい丸み。
    ・DISTANCE_TO_EDGE だけ＝平らな板が溝で区切られたクロコ（round 3）
    ・F1 のドームだけ＝均一な鱗で爬虫類（round 12）／ドームを潰すと紙やすり（round 13）
    → 溝が主・ドームが従。座標は大きく歪めて粒の形を不揃いに"""
    m = bpy.data.materials.new("leather"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    dn = N.new("ShaderNodeTexNoise"); dn.inputs["Scale"].default_value = LEATHER_SCALE * 0.6
    dn.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], dn.inputs["Vector"])
    warp = N.new("ShaderNodeVectorMath"); warp.operation = 'MULTIPLY_ADD'
    L.new(dn.outputs["Color"], warp.inputs[0]); warp.inputs[1].default_value = (LEATHER_WARP,) * 3
    L.new(tc.outputs["Object"], warp.inputs[2])
    # しわの網目（溝）
    ve = N.new("ShaderNodeTexVoronoi"); ve.feature = 'DISTANCE_TO_EDGE'
    ve.inputs["Scale"].default_value = LEATHER_SCALE
    L.new(warp.outputs["Vector"], ve.inputs["Vector"])
    cre = N.new("ShaderNodeMapRange"); cre.clamp = True
    cre.inputs["From Min"].default_value = 0.0; cre.inputs["From Max"].default_value = LEATHER_GROOVE
    L.new(ve.outputs["Distance"], cre.inputs["Value"])
    csm = N.new("ShaderNodeMath"); csm.operation = 'POWER'; csm.inputs[1].default_value = 0.5
    L.new(cre.outputs["Result"], csm.inputs[0])
    # 粒の中の丸み（細かい F1 ドーム）
    v = N.new("ShaderNodeTexVoronoi"); v.feature = 'F1'
    v.inputs["Scale"].default_value = LEATHER_SCALE * 2.6
    L.new(warp.outputs["Vector"], v.inputs["Vector"])
    dm = N.new("ShaderNodeMapRange"); dm.clamp = True
    dm.inputs["From Min"].default_value = 0.0; dm.inputs["From Max"].default_value = 0.7
    dm.inputs["To Min"].default_value = 1.0; dm.inputs["To Max"].default_value = 0.35
    L.new(v.outputs["Distance"], dm.inputs["Value"])
    h = N.new("ShaderNodeMath"); h.operation = 'MULTIPLY'
    L.new(csm.outputs[0], h.inputs[0]); L.new(dm.outputs["Result"], h.inputs[1])
    fn = N.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = LEATHER_SCALE * 12
    L.new(tc.outputs["Object"], fn.inputs["Vector"])
    add = N.new("ShaderNodeMath"); add.operation = 'MULTIPLY_ADD'
    L.new(fn.outputs["Fac"], add.inputs[0]); add.inputs[1].default_value = 0.05
    L.new(h.outputs[0], add.inputs[2])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = LEATHER_BUMP
    bump.inputs["Distance"].default_value = 0.003
    L.new(add.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])
    rr = N.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = LEATHER_ROUGH + 0.28
    rr.inputs["To Max"].default_value = LEATHER_ROUGH
    L.new(h.outputs[0], rr.inputs["Value"])
    L.new(rr.outputs["Result"], p.inputs["Roughness"])
    cr = N.new("ShaderNodeMix"); cr.data_type = 'RGBA'
    sock(cr, "A", 'RGBA').default_value = hex_to_linear("#020202")
    sock(cr, "B", 'RGBA').default_value = hex_to_linear("#131211")
    L.new(h.outputs[0], cr.inputs["Factor"])
    L.new(next(s for s in cr.outputs if s.type == 'RGBA'), p.inputs["Base Color"])
    p.inputs["Specular IOR Level"].default_value = 0.18
    return m


LEATHER_SCALE, LEATHER_BUMP, LEATHER_ROUGH = 46.0, 0.75, 0.30
LEATHER_WARP, LEATHER_GROOVE = 0.016, 0.06
body.data.materials.append(leather_mat())

# --- グリル：斜めに編んだ金属メッシュ（頂点ごとに高さを計算した実形状）
PITCH = 0.054                     # 斜めの格子の周期（菱形1つ）
WIRE = 0.16                       # 線の半幅（周期比）
STEP = 0.0019
gx0, gx1 = -GW / 2 - 0.022, GW / 2 + 0.022
gz0, gz1 = Z0 - GH / 2 - 0.022, Z0 + GH / 2 + 0.022
nx = int((gx1 - gx0) / STEP) + 1
nz_ = int((gz1 - gz0) / STEP) + 1
GY = -BD / 2 + 0.030              # くぼみの底より少し手前


def weave(x, z):
    a = (x + z) / (PITCH * math.sqrt(2)) * 1.0
    b = (x - z) / (PITCH * math.sqrt(2)) * 1.0
    best, wire = -0.6, 0.0
    # A 線：b = k + 0.5 を中心に a 方向へ走る
    kb = math.floor(b); fb = b - kb - 0.5
    if abs(fb) < WIRE:
        prof = math.sqrt(1 - (fb / WIRE) ** 2)
        h = 0.5 * math.cos(math.pi * (a - 0.5) + math.pi * kb) + 0.8 * prof
        if h > best:
            best = h
        wire = max(wire, prof)
    ka = math.floor(a); fa = a - ka - 0.5
    if abs(fa) < WIRE:
        prof = math.sqrt(1 - (fa / WIRE) ** 2)
        h = -0.5 * math.cos(math.pi * (b - 0.5) + math.pi * ka) + 0.8 * prof
        if h > best:
            best = h
        wire = max(wire, prof)
    return best, wire


gv, gf, gw = [], [], []
AMP = PITCH * 0.22
for j in range(nz_):
    z = gz0 + j * STEP
    for i in range(nx):
        x = gx0 + i * STEP
        h, w = weave(x, z)
        gv.append((x, GY - h * AMP, z))
        gw.append(w)
for j in range(nz_ - 1):
    for i in range(nx - 1):
        k = j * nx + i
        gf.append((k, k + 1, k + nx + 1, k + nx))
gme = bpy.data.meshes.new("grille_me")
gme.from_pydata(gv, [], gf); gme.update()
ca = gme.color_attributes.new("wire", 'FLOAT_COLOR', 'POINT')
for idx, w in enumerate(gw):
    ca.data[idx].color = (w, w, w, 1.0)
for p in gme.polygons:
    p.use_smooth = True
grille = bpy.data.objects.new("grille", gme); scene.collection.objects.link(grille)

gm = bpy.data.materials.new("mesh"); gm.use_nodes = True
nt = gm.node_tree; N = nt.nodes; L = nt.links
p = N["Principled BSDF"]
at = N.new("ShaderNodeAttribute"); at.attribute_name = "wire"
mx = N.new("ShaderNodeMix"); mx.data_type = 'RGBA'
sock(mx, "A", 'RGBA').default_value = (0.0, 0.0, 0.0, 1)
sock(mx, "B", 'RGBA').default_value = hex_to_linear("#0A0A0A")
L.new(at.outputs["Fac"], mx.inputs["Factor"])
L.new(next(s for s in mx.outputs if s.type == 'RGBA'), p.inputs["Base Color"])
p.inputs["Metallic"].default_value = 0.0
p.inputs["Coat Weight"].default_value = 0.3
p.inputs["Roughness"].default_value = 0.24
# 🔴 網は1枚の連続メッシュ＝「穴」は黒く塗った凹みでしかなかった（round 8）。線の外を透明にして奥の布を見せる
_hm = N.new("ShaderNodeMapRange"); _hm.clamp = True
_hm.inputs["From Min"].default_value = 0.02; _hm.inputs["From Max"].default_value = 0.12
L.new(at.outputs["Fac"], _hm.inputs["Value"])
_tr = N.new("ShaderNodeBsdfTransparent")
_ms = N.new("ShaderNodeMixShader")
L.new(_hm.outputs["Result"], _ms.inputs["Fac"])
L.new(_tr.outputs[0], _ms.inputs[1]); L.new(p.outputs[0], _ms.inputs[2])
L.new(_ms.outputs[0], N["Material Output"].inputs["Surface"])
grille.data.materials.append(gm)
# 網の奥の空洞（真っ黒の板）
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, GY + 0.010, Z0), rotation=(math.radians(90), 0, 0))
cav = bpy.context.object; cav.name = "cavity"
cav.scale = (GW + 0.03, GH + 0.03, 1); bpy.ops.object.transform_apply(scale=True)
cvm = principled("cavity", hex_to_linear("#0E0E0E"), rough=0.9)
_n = cvm.node_tree.nodes; _l = cvm.node_tree.links
_nz = _n.new("ShaderNodeTexVoronoi"); _nz.inputs["Scale"].default_value = 260
_bp = _n.new("ShaderNodeBump"); _bp.inputs["Strength"].default_value = 1.0
_l.new(_nz.outputs["Distance"], _bp.inputs["Height"]); _l.new(_bp.outputs["Normal"], _n["Principled BSDF"].inputs["Normal"])
# 布は自分で薄く光らせる：窓の縁では筐体が布の光を遮って黒い菱形が並んだ（round 23。遮蔽リンクでも消えなかった）
_pb = _n["Principled BSDF"]
_pb.inputs["Emission Color"].default_value = (1, 1, 1, 1)
_pb.inputs["Emission Strength"].default_value = CAV_EMIT
# 照り返しも受けると枠の下だけ暗く沈むので、布は発光だけで描く（点の肌理は明るさの揺らぎで）
_em = _n.new("ShaderNodeEmission"); _em.inputs["Strength"].default_value = CAV_EMIT
_fm = _n.new("ShaderNodeMapRange"); _fm.inputs["To Min"].default_value = 0.25; _fm.inputs["To Max"].default_value = 1.0
_l.new(_nz.outputs["Distance"], _fm.inputs["Value"])
_l.new(_fm.outputs["Result"], _em.inputs["Color"])
_l.new(_em.outputs[0], _n["Material Output"].inputs["Surface"])
cav.data.materials.append(cvm)

# --- 天面：真鍮のノブ＋黒い座金、左にボタン3つ、赤いボタン1つ
TOPZ = BH
KX = 0.38
FLOOR_W = 220
CAV_W = 0
TOP_W = 60
WALL_SIZE, WALL_W = 22.0, 5000
# 座金＝立ち上がった黒い輪（中を抜いてノブを沈める）
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.185, depth=0.05, location=(KX, 0.0, TOPZ + 0.005))
bezel = bpy.context.object; bezel.name = "bezel"
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.14, depth=0.2, location=(KX, 0.0, TOPZ + 0.1))
_hole = bpy.context.object
_bm = bezel.modifiers.new("hole", 'BOOLEAN'); _bm.operation = 'DIFFERENCE'; _bm.object = _hole; _bm.solver = 'EXACT'
bpy.context.view_layer.objects.active = bezel; bpy.ops.object.modifier_apply(modifier="hole")
bpy.data.objects.remove(_hole)
bezel.data.materials.clear()
bevel_obj(bezel, 0.01, segments=4, clamp=False)
bezel.data.materials.append(principled("bezel", hex_to_linear("#0A0A0A"), rough=0.3))
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.128, depth=0.05, location=(KX, 0.0, TOPZ + 0.014))
knob = bpy.context.object; knob.name = "knob"
bevel_obj(knob, 0.012, segments=4)


def brass_mat():
    m = bpy.data.materials.new("brass"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    p.inputs["Base Color"].default_value = hex_to_linear("#D9B77A")
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.26
    p.inputs["Anisotropic"].default_value = 0.6
    tc = N.new("ShaderNodeTexCoord")
    # 天面の同心円のヘアライン：中心からの距離に細かいノイズ
    sep = N.new("ShaderNodeVectorMath"); sep.operation = 'LENGTH'
    L.new(tc.outputs["Object"], sep.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 2
    cmb = N.new("ShaderNodeCombineXYZ")
    L.new(sep.outputs["Value"], cmb.inputs["X"])
    L.new(cmb.outputs["Vector"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.001
    L.new(nz.outputs["Fac"], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


knob.data.materials.append(brass_mat())
# ノブの天面の刻み線（回転を見せる・film round 1）
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(KX + 0.072, 0.0, TOPZ + 0.039))
notch = bpy.context.object; notch.name = "notch"
notch.scale = (0.07, 0.009, 0.004); bpy.ops.object.transform_apply(scale=True)
bevel_obj(notch, 0.0015, segments=2)
notch.data.materials.append(principled("notch", hex_to_linear("#2A2116"), rough=0.5, metal=1.0))
notch.parent = knob; notch.matrix_parent_inverse = knob.matrix_world.inverted()
btns = []
for k, bx in enumerate((-0.80, -0.62)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.045, depth=0.02, location=(bx, -0.05, TOPZ + 0.002))
    bt = bpy.context.object; bt.name = "btn%d" % k
    bevel_obj(bt, 0.006, segments=3)
    bt.data.materials.append(principled("btn", hex_to_linear("#111111"), rough=0.35))
    btns.append(bt)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.71, 0.18, TOPZ - 0.001))
red = bpy.context.object; red.name = "red"
red.scale = (0.24, 0.07, 0.02); bpy.ops.object.transform_apply(scale=True)
bevel_obj(red, 0.012, segments=4)
red.data.materials.append(principled("red", hex_to_linear("#250203"), rough=0.6, coat=0.0))
red.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.71, 0.18, TOPZ - 0.004))
redrim = bpy.context.object; redrim.name = "redrim"
redrim.scale = (0.29, 0.11, 0.016); bpy.ops.object.transform_apply(scale=True)
bevel_obj(redrim, 0.02, segments=4)
redrim.data.materials.append(principled("redrim", hex_to_linear("#030303"), rough=0.75))
redrim.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15
parts = [body, notch, redrim, grille, cav, bezel, knob, red] + btns   # 🔴 被写体は全部ここへ

# ------------------------------------------------------------- 光
# 基準：真上〜やや手前の大きく柔らかい1灯。天面が一段明るく、正面は暗い
key = area("key", (0.0, -3.0, 6.2), 4.5, 950, (1.0, 0.98, 0.95), target=(0, 0, 0.5))
fill = area("fill", (0.0, -6.5, 0.9), 5.0, 1400, (1.0, 1.0, 1.0), target=(0, 0, 0.6))
# 地のグラデーション：壁の中ほどだけを起こす
wall = area("wall", (0.0, -4.0, 11.0), WALL_SIZE, WALL_W, (1.0, 1.0, 1.0), target=(0, 6.0, 7.0))
# ライトリンク：キーと正面の起こしは被写体だけ（床が明るくなる・#104）
subj = bpy.data.collections.new("subj"); scene.collection.children.link(subj)
for o in parts:
    for c in o.users_collection:
        c.objects.unlink(o)
    subj.objects.link(o)
stage = bpy.data.collections.new("stage_only"); scene.collection.children.link(stage)
scene.collection.objects.unlink(sweep); stage.objects.link(sweep)
# 天面の映り込み：奥の高めの大きな面＝天面の鏡面方向に置く（round 10）
toplight = area("toplight", (0.0, 4.5, 5.5), 7.0, TOP_W, (1.0, 1.0, 1.0), target=(0, 0, 1.0))
toplight.data.cycles.is_caustics_light = False
for L_ in (key, toplight):
    L_.light_linking.receiver_collection = subj
# 正面の起こしは革の筐体だけ（網に当てると金属が銀色に光る・round 18）
bodyc = bpy.data.collections.new("body_only"); scene.collection.children.link(bodyc)
bodyc.objects.link(body)
fill.light_linking.receiver_collection = bodyc
wall.light_linking.receiver_collection = stage
# 🔴 被写体が壁の光（22の大きな面）の影を落とすと、床と壁の継ぎ目に横一線の段が出る（round 5）。
#    壁の光は被写体に遮らせない＝影は床の光（真上の小さめの面）だけが作る
wall.light_linking.blocker_collection = stage
# 床：被写体の真上から弱く＝影は被写体の真下に溜まる
floor_l = area("floor", (0.0, -0.3, 7.0), 2.2, FLOOR_W, (1.0, 1.0, 1.0), target=(0, 0, 0))
floor_l.light_linking.receiver_collection = stage
# 網の奥の布だけを正面から弱く起こす（枠と網の影で真っ黒になる・round 7）
cavc = bpy.data.collections.new("cav_only"); scene.collection.children.link(cavc)
subj.objects.unlink(cav); cavc.objects.link(cav)
cav_l = area("cavlight", (0.0, -3.0, 0.6), 3.0, CAV_W, (1.0, 1.0, 1.0), target=(0, 0, 0.5))
cav_l.light_linking.receiver_collection = cavc
cav_l.light_linking.blocker_collection = cavc
for L_ in (key, fill):
    pass

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam

# ------------------------------------------------------------- 動画＝プロダクトフィルム（2026-09-23〜）
# 🔴 10〜12秒・3〜4カットの CM 型。ループは「最後のカット → 最初のカット」をカットで戻る（継ぎ目なしにしない）。
#    最後のカットは静止画（hero）と同じ構図で終わり、1秒以上止まる＝ STILL_FRAME はその中に置く。
# 型（組み合わせて使う。毎回同じ並びにしない）：
#   マクロ  … 長いレンズ（100〜150mm）で縁・肌理・部品をなめる。浅い被写界深度＋ピント送り
#   スライド… カメラが横・縦に平行移動して、光や物の前を滑る
#   回り込み… 被写体を中心に弧を描く（15〜60°）
#   押し込み… まっすぐ寄る／引く（レンズを変えずに距離で）
#   光の走り… 面光源を動かして、ハイライトの帯を表面に走らせる（カメラは止めてよい）
#   物の動き… 回る・開く・持ち上がる・落ちる・並ぶ
#   決め    … hero の構図。動きながら入ってきて止まる
# 🔴 カメラの動きは必ず加減速（ease）。等速の直線移動は安いCGに見える。
# 🔴 カットの切り替えは「動いている途中」で切る（止まってから切ると間延びする）。
# 🔴 モーションブラーは使わない：毎フレームキーのカメラは、カットの境目で前後のカットの間を補間してブレる。

def ease(t):                  # 加減速（sine in-out）
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):              # 動きながら入って止まる（決めのカット向き）
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def orbit(center, radius, height, deg):   # 被写体まわりの弧（deg=0 が正面 -Y）
    r = math.radians(deg)
    return Vector((center[0] + radius * math.sin(r), center[1] - radius * math.cos(r), height))

# 各カット：sec（秒）／cam(t)→(カメラ位置, 注視点, レンズmm, f値, ピント距離 or None=注視点まで)
#           ／pose(t)→物の動き（任意）。t はそのカットの中で 0→1。
# 🔴 下は動作確認用の仮置き。**毎回、基準と題材に合わせて組み直す**。
TGT = Vector((0, 0, Z0))
HERO_CAM = Vector((0.0, -8.8, 3.1))
HERO_TGT = Vector((0.0, 0.0, 1.22))
KT = Vector((KX, 0.0, TOPZ + 0.08))
SHOTS = [
    dict(sec=3.0,   # スライド：グリルの前を左から右へ、斜めに滑る
         cam=lambda t: (lerp((-2.4, -3.1, 0.62), (-0.7, -3.35, 0.78), ease(t)),
                        lerp((-1.0, 0, 0.5), (0.35, 0, 0.52), ease(t)), 70, 1.6, None)),
    dict(sec=3.0,   # マクロ：真鍮のノブが回る（物の動き）＋ピント送り
         cam=lambda t: (lerp((KX + 0.95, -1.35, 1.75), (KX + 0.62, -1.45, 1.58), ease(t)), KT,
                        135, 0.9, (KT - lerp((KX + 0.95, -1.35, 1.75), (KX + 0.62, -1.45, 1.58), ease(t))).length
                        + 0.12 * (1 - ease(t)))),
    dict(sec=2.5,   # 光の走り：天面の革を低い角度でなめる。キーが横に走り、粒の照りが流れる
         cam=lambda t: (lerp((-1.9, -1.55, 1.22), (-1.75, -1.6, 1.2), ease(t)), Vector((-0.2, 0.0, 1.0)),
                        100, 1.4, None)),
    dict(sec=3.0,   # 決め：上から降りながら寄って hero の構図で止まる
         cam=lambda t: (lerp(HERO_CAM + Vector((0.6, -2.2, 1.6)), HERO_CAM, ease_out(min(1.0, t / 0.6))),
                        lerp(HERO_TGT + Vector((0.1, 0, 0.2)), HERO_TGT, ease_out(min(1.0, t / 0.6))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES        # 最後のフレーム＝決めのカットが止まったところ＝hero


def pose(i, t, T):
    """ノブだけが回る（マクロのカットで60°）。他は止まる"""
    ang = 0.0
    if i == 1:
        ang = math.radians(60) * ease(t)
    elif i >= 2:
        ang = math.radians(60)
    knob.rotation_euler = (0, 0, ang)


key_light = bpy.data.objects.get("key")
KEY_HOME = Vector(key_light.location)


def light_path(i, t):
    if i == 2:
        key_light.location = KEY_HOME + Vector((-4.5 + 9.0 * ease(t), 0, 0))
    else:
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
        if key_light:
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
    # 網は頂点ごとの実形状で約55万頂点＝そのままだと glb が 30MB（8MB 上限）。glb にだけ間引いて渡す
    _dm = grille.modifiers.new("decimate", 'DECIMATE'); _dm.ratio = 0.06
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True, export_apply=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
