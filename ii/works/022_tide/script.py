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
from mathutils import Vector, Euler

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK（毎回決める）
LOOK = dict(
    aspect=(3, 4),
    lens=84,
    fstop=3.2,
    view="Standard",          # 空の色を ramp の値そのままで出す（AgX は空色を灰に寄せる＝#110）
    look="None",
    exposure=0.0,
    bg=(0.0, 0.0, 0.0),
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


# ------------------------------------------------------------- 舞台：日没後の空＋さざ波の水面
# 空は World の方向（Generated＝視線の向き）の z＝仰角の sin で塗る。光源はこの空だけ
SKY = [  # (sin仰角, sRGB)
    (-0.02, "#3A4652"), (0.0, "#C3996A"), (0.035, "#D6B487"), (0.075, "#DAB9A0"),
    (0.11, "#BDBDBA"), (0.15, "#93A6B6"), (0.19, "#62839F"), (0.23, "#456685"), (0.45, "#2E5274"), (1.0, "#294C6C"),
]
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
wn, wl = world.node_tree.nodes, world.node_tree.links
tc = wn.new("ShaderNodeTexCoord")
nrm = wn.new("ShaderNodeVectorMath"); nrm.operation = 'NORMALIZE'
sep = wn.new("ShaderNodeSeparateXYZ")
rmp = wn.new("ShaderNodeValToRGB")
wl.new(tc.outputs["Generated"], nrm.inputs[0]); wl.new(nrm.outputs[0], sep.inputs[0])
# 🔴 #113：elements.new() は並べ替える。先に全部足してから、位置で引き直して塗る
cr = rmp.color_ramp; cr.interpolation = 'B_SPLINE'
while len(cr.elements) < len(SKY):
    cr.elements.new(0.5)
lo, hi = -0.05, 1.0
for i, (z, h) in enumerate(SKY):
    cr.elements[i].position = (z - lo) / (hi - lo)
for i, (z, h) in enumerate(SKY):
    cr.elements[i].color = hex_to_linear(h)
print(">> sky", [(round(e.position, 3), tuple(round(c, 3) for c in e.color[:3])) for e in cr.elements])
mr = wn.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = lo, hi
wl.new(sep.outputs["Z"], mr.inputs["Value"]); wl.new(mr.outputs["Result"], rmp.inputs["Fac"])
# 背後の空（カメラの後ろ＝夕暮れの反対側）：地球の影の紺の上に桃色の帯。前後は視線の y で混ぜる
BACK = [(-0.02, "#1A222D"), (0.0, "#3A4252"), (0.03, "#B88D92"), (0.07, "#EAB0A2"), (0.13, "#F0BFA8"),
        (0.20, "#E7C3B5"), (0.30, "#B9C3D3"), (0.40, "#8DB6DE"), (0.55, "#5D8CC0"), (1.0, "#2F527A")]
rmp2 = wn.new("ShaderNodeValToRGB"); cr2 = rmp2.color_ramp; cr2.interpolation = 'B_SPLINE'
while len(cr2.elements) < len(BACK):
    cr2.elements.new(0.5)
for i, (z, h) in enumerate(BACK):
    cr2.elements[i].position = (z - lo) / (hi - lo)
for i, (z, h) in enumerate(BACK):
    cr2.elements[i].color = hex_to_linear(h)
wl.new(mr.outputs["Result"], rmp2.inputs["Fac"])
fy = wn.new("ShaderNodeMapRange"); fy.inputs["From Min"].default_value, fy.inputs["From Max"].default_value = -0.6, 0.6
wl.new(sep.outputs["Y"], fy.inputs["Value"])
mixs = wn.new("ShaderNodeMix"); mixs.data_type = 'RGBA'
wl.new(fy.outputs["Result"], mixs.inputs[0])
wl.new(rmp2.outputs["Color"], mixs.inputs[6]); wl.new(rmp.outputs["Color"], mixs.inputs[7])   # 🔴 #103：RGBA は 6/7/2
# ガラスを通った光線だけが見る前方の空：カメラに写る範囲（sin 0.22）より上に杏〜桃の帯、天頂は濃紺
#   （round 16〜17：屈折で上へ曲がった光線が灰青の高い空を拾って塊が藤色に沈んだ。帯を全員に見せると水面まで桃に転ぶ）
THRU = [(-0.02, "#3A4652"), (0.0, "#C98C72"), (0.035, "#EAA892"), (0.075, "#EDA5A4"), (0.11, "#EBB5A6"), (0.15, "#E6ACAA"), (0.19, "#F0C79A"), (0.225, "#62A6EE")] + [(0.29, "#E2A9A4"), (0.36, "#F2C996"), (0.44, "#EBADA8"), (0.52, "#D6E6F4"), (0.60, "#22375A"), (1.0, "#16294A")]
THRU_BACK = [(-0.02, "#0E1420"), (0.0, "#141C2C"), (0.06, "#1B2A44"), (0.12, "#BFD6EE"), (0.17, "#1E3050"), (0.40, "#2A4468"), (1.0, "#16294A")]
rmp3 = wn.new("ShaderNodeValToRGB"); cr3 = rmp3.color_ramp; cr3.interpolation = 'B_SPLINE'
while len(cr3.elements) < len(THRU):
    cr3.elements.new(0.5)
for i, (z, h) in enumerate(THRU):
    cr3.elements[i].position = (z - lo) / (hi - lo)
for i, (z, h) in enumerate(THRU):
    cr3.elements[i].color = hex_to_linear(h)
wl.new(mr.outputs["Result"], rmp3.inputs["Fac"])
if os.environ.get("II_DIAG2"):   # 診断：帯ごとに別の色（一定）で塗る
    cr3.interpolation = 'CONSTANT'
    HUES = [(1,0,0),(1,.5,0),(1,1,0),(0,1,0),(0,1,1),(0,0,1),(.5,0,1),(1,0,1),(1,1,1),(.3,.3,.3),(0,0,0),(.6,.3,0)]
    for i, el in enumerate(cr3.elements):
        el.color = HUES[i % len(HUES)] + (1,)
mixt = wn.new("ShaderNodeMix"); mixt.data_type = 'RGBA'
wl.new(fy.outputs["Result"], mixt.inputs[0])
rmp4 = wn.new("ShaderNodeValToRGB"); cr4 = rmp4.color_ramp; cr4.interpolation = 'B_SPLINE'
while len(cr4.elements) < len(THRU_BACK):
    cr4.elements.new(0.5)
for i, (z, h) in enumerate(THRU_BACK):
    cr4.elements[i].position = (z - lo) / (hi - lo)
for i, (z, h) in enumerate(THRU_BACK):
    cr4.elements[i].color = hex_to_linear(h)
wl.new(mr.outputs["Result"], rmp4.inputs["Fac"])
if os.environ.get("II_DIAG2"):   # 診断：背後（ガラス越し）は一律の濃い緑
    for el in cr4.elements:
        el.color = (0.0, 0.25, 0.0, 1)
wl.new(rmp4.outputs["Color"], mixt.inputs[6]); wl.new(rmp3.outputs["Color"], mixt.inputs[7])
wlp = wn.new("ShaderNodeLightPath")
wgt = wn.new("ShaderNodeMath"); wgt.operation = 'GREATER_THAN'; wgt.inputs[1].default_value = 0.5
wl.new(wlp.outputs["Transmission Depth"], wgt.inputs[0])
mixg = wn.new("ShaderNodeMix"); mixg.data_type = 'RGBA'
wl.new(wgt.outputs[0], mixg.inputs[0])
wl.new(mixs.outputs[2], mixg.inputs[6]); wl.new(mixt.outputs[2], mixg.inputs[7])
bgn = wn["Background"]
wl.new(mixg.outputs[2], bgn.inputs["Color"])
if os.environ.get("II_DIAG4"):   # 診断：前方（ガラス越し）だけ一色に
    world.node_tree.links.remove(mixt.inputs[7].links[0]); mixt.inputs[7].default_value = (1, 0, 1, 1)
if os.environ.get("II_DIAG3"):   # 診断：ガラスを通った光線の空を真っ黒に／カメラ直の空は残す
    mixg.inputs[7].default_value = (0, 0, 0, 1)
    world.node_tree.links.remove(mixg.inputs[7].links[0])
if os.environ.get("II_DIAG"):   # 診断：背後の空を緑に
    for el in cr2.elements:
        el.color = (0.0, 0.6, 0.0, 1)
bgn.inputs["Strength"].default_value = 1.0
SKY_STRENGTH = bgn.inputs["Strength"]

# 水面：🔴 バンプは効かない（水面すれすれの視線では、Cycles が反射を面より上に保つために法線を平らに戻す）
#        → Ocean モディファイアで本物の波の形を作る。遠くは一段下げた平らな板でつなぐ
wm = bpy.data.materials.new("water"); wm.use_nodes = True
pw = wm.node_tree.nodes["Principled BSDF"]
pw.inputs["Base Color"].default_value = hex_to_linear("#0B1418")
pw.inputs["IOR"].default_value = 1.33
# ガラスを一度でも通った光線から見た水面だけ粗くする＝塊の中に波の細かい肌理を写さない（round 8〜9）
_n, _l = wm.node_tree.nodes, wm.node_tree.links
_lp = _n.new("ShaderNodeLightPath")
_gt = _n.new("ShaderNodeMath"); _gt.operation = 'GREATER_THAN'; _gt.inputs[1].default_value = 0.5
_mr = _n.new("ShaderNodeMapRange"); _mr.inputs["To Min"].default_value = 0.03
_mr.inputs["To Max"].default_value = float(os.environ.get("II_WR", "0.25"))
_l.new(_lp.outputs["Transmission Depth"], _gt.inputs[0]); _l.new(_gt.outputs[0], _mr.inputs["Value"])
_l.new(_mr.outputs["Result"], pw.inputs["Roughness"])
# 同じ光線から見た水の地色は明るい薔薇に＝深い角度で当たって反射が5%に落ちても、塊の中が泥の色に沈まない
_mx = _n.new("ShaderNodeMix"); _mx.data_type = 'RGBA'
_mx.inputs[6].default_value = hex_to_linear("#0B1418")
_mx.inputs[7].default_value = hex_to_linear(os.environ.get("II_WC", "#E8B8A4"))
# さらに同じ光線では反射を強く（IOR を上げる）＝深い角度でも背後の空の桃を映す。藤色の灰の正体は「深い角度の弱い反射」だった（round 16 の診断）
_ir = _n.new("ShaderNodeMapRange"); _ir.inputs["To Min"].default_value = 1.33
_ir.inputs["To Max"].default_value = float(os.environ.get("II_WI", "1.33"))
_l.new(_gt.outputs[0], _ir.inputs["Value"]); _l.new(_ir.outputs["Result"], pw.inputs["IOR"])
# ガラスを通った光線から見た水面＝杏の黄の発光面（round 25：拡散面は暗く、粗い反射は空の縞を平均して灰になる）
_em = _n.new("ShaderNodeEmission")
_gp = _n.new("ShaderNodeNewGeometry"); _gs = _n.new("ShaderNodeVectorMath"); _gs.operation = 'LENGTH'
_l.new(_gp.outputs["Position"], _gs.inputs[0])
_gr = _n.new("ShaderNodeMapRange"); _gr.inputs["From Min"].default_value = 0.0; _gr.inputs["From Max"].default_value = 3.5
_l.new(_gs.outputs["Value"], _gr.inputs["Value"])
_gc = _n.new("ShaderNodeValToRGB"); _gcr = _gc.color_ramp
_gcr.elements[0].color = hex_to_linear("#F4CF9C"); _gcr.elements[1].color = hex_to_linear("#B7A8BF")
_gy = _gcr.elements.new(0.17); _gy.color = hex_to_linear("#F3D7A4")
_gd = _gcr.elements.new(0.06); _gd.color = hex_to_linear("#F4CF9C")
_gcr.elements[0].color = hex_to_linear(os.environ.get("II_NEAR", "#1E2840"))   # 足元＝濃紺（上の縁の墨）
_gm = _gcr.elements.new(0.35); _gm.color = hex_to_linear("#EAA6A2")   # 🔴 #113：new() は並べ替える＝足したものを直接塗る
_gb = _gcr.elements.new(0.62); _gb.color = hex_to_linear("#9DB8DC")
_l.new(_gr.outputs["Result"], _gc.inputs["Fac"])
# 遠くの水は大きなノイズで 杏の黄 ⇄ 藤 に揺らす（round 33：上半分が一色の面になった）
# 🔴 ノイズは屈折で同心円の縞になった（round 35）＝横位置の緩い勾配で揺らす
_fsep = _n.new("ShaderNodeSeparateXYZ"); _l.new(_gp.outputs["Position"], _fsep.inputs[0])
_fn = _n.new("ShaderNodeMapRange"); _fn.inputs["From Min"].default_value = -2.5; _fn.inputs["From Max"].default_value = 2.5
_l.new(_fsep.outputs["X"], _fn.inputs["Value"])
_fr = _n.new("ShaderNodeValToRGB"); _fr.color_ramp.elements[0].position = 0.38; _fr.color_ramp.elements[1].position = 0.62
_fr.color_ramp.elements[0].color = hex_to_linear("#EBD8B6"); _fr.color_ramp.elements[1].color = hex_to_linear("#F1CD9E")
_l.new(_fn.outputs["Result"], _fr.inputs["Fac"])
_fm = _n.new("ShaderNodeMix"); _fm.data_type = 'RGBA'
_fk = _n.new("ShaderNodeMapRange"); _fk.inputs["From Min"].default_value = 0.6; _fk.inputs["From Max"].default_value = 0.9
_l.new(_gr.outputs["Result"], _fk.inputs["Value"]); _l.new(_fk.outputs["Result"], _fm.inputs[0])
_l.new(_gc.outputs["Color"], _fm.inputs[6]); _l.new(_fr.outputs["Color"], _fm.inputs[7])
_l.new(_fm.outputs[2], _em.inputs["Color"])
_em.inputs["Strength"].default_value = float(os.environ.get("II_WES", "0.75"))
_ms = _n.new("ShaderNodeMixShader")
_out = _n["Material Output"]
_l.new(_gt.outputs[0], _ms.inputs[0]); _l.new(pw.outputs["BSDF"], _ms.inputs[1]); _l.new(_em.outputs[0], _ms.inputs[2])
_l.new(_ms.outputs[0], _out.inputs["Surface"])
wm.cycles.emission_sampling = 'NONE'   # 🔴 10万面の水が光源扱いになり描画が120秒を超えた（ガラス越しに見えるだけの面なので光源にしない）
if os.environ.get("II_DIAG") or os.environ.get("II_DIAG2"):   # 診断：ガラス越しの水を赤に
    _mx.inputs[7].default_value = (0.8, 0.0, 0.0, 1)
_l.new(_gt.outputs[0], _mx.inputs[0]); _l.new(_mx.outputs[2], pw.inputs["Base Color"])   # 🔴 #103：RGBA は 6/7/2
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
water = bpy.context.object; water.name = "water"
oc = water.modifiers.new("ocean", 'OCEAN')
oc.geometry_mode = 'GENERATE'
oc.spatial_size = int(os.environ.get("II_OS", "4")); oc.resolution = int(os.environ.get("II_OR", "24"))
oc.repeat_x, oc.repeat_y = 5, 8
water.location = (-15.0, -8.0, 0.0)   # タイルは原点から +x +y へ並ぶ＝カメラ（y=-6）の手前から始める
oc.wave_scale = float(os.environ.get("II_WS", "0.018")); oc.choppiness = 0.6
oc.wind_velocity = float(os.environ.get("II_WV", "1.1"))
oc.wave_alignment = 0.6; oc.wave_direction = math.radians(90); oc.damping = 0.3
oc.random_seed = 7
oc.use_normals = True
water.data.materials.append(wm)
for p in water.data.polygons:
    p.use_smooth = True
bpy.ops.mesh.primitive_plane_add(size=800, location=(0, 0, -0.01))
far = bpy.context.object; far.name = "far_water"; far.data.materials.append(wm)


class _OT:   # 時間は Ocean の time で送る（下の毎フレームキーから呼ぶ）
    def __init__(self, m): self.m = m
    @property
    def default_value(self): return self.m.time
    @default_value.setter
    def default_value(self, v): self.m.time = v
    def keyframe_insert(self, path, frame): self.m.keyframe_insert("time", frame=frame)
water_t = _OT(oc)

# ------------------------------------------------------------- 被写体：彫ったガラスの塊
# 縦長の角丸の塊から、切り面（平面）と大きなえぐり（楕円体）を Boolean で引き、ボクセルで一体化して稜を少し丸める
def cube(name, loc, scale, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=[math.radians(r) for r in rot])
    o = bpy.context.object; o.name = name; o.scale = scale
    return o

def ell(name, loc, scale, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=1.0, location=loc,
                                         rotation=[math.radians(r) for r in rot])
    o = bpy.context.object; o.name = name; o.scale = scale
    return o

# 本体：8点×6段のリングを張った低ポリの塊を Catmull-Clark で細分割＝大きく滑らかな曲面だけでできた塊
# （メタボールは継ぎ目のうねりが小さなレンズになって中がざわついた＝round 6）
import random
rnd = random.Random(22)
RINGS = [  # (z, 半径x, 半径y, 中心x, 中心y)
    (-0.12, 0.25, 0.18, 0.03, 0.00),
    (0.20, 0.29, 0.20, 0.00, 0.00),
    (0.52, 0.29, 0.21, -0.01, 0.01),
    (0.78, 0.25, 0.18, 0.00, 0.00),
    (0.96, 0.19, 0.11, 0.03, 0.00),
    (1.06, 0.12, 0.05, 0.05, 0.01),
]
NA = 8
bm = bmesh.new()
rings = []
for li, (z, rx, ry, cx, cy) in enumerate(RINGS):
    ring = []
    for k in range(NA):
        a_ = 2 * math.pi * k / NA + math.radians(22.5)
        j = 1.0 + rnd.uniform(-0.12, 0.12)
        ring.append(bm.verts.new((cx + rx * j * math.cos(a_), cy + ry * j * math.sin(a_), z + rnd.uniform(-0.03, 0.03))))
    rings.append(ring)
for li in range(len(rings) - 1):
    for k in range(NA):
        bm.faces.new((rings[li][k], rings[li][(k + 1) % NA], rings[li + 1][(k + 1) % NA], rings[li + 1][k]))
bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me_ = bpy.data.meshes.new("glass"); bm.to_mesh(me_); bm.free()
body = bpy.data.objects.new("glass", me_); scene.collection.objects.link(body)
sd = body.modifiers.new("sd", 'SUBSURF'); sd.levels = sd.render_levels = 5
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="sd")
from mathutils import Vector as _V
_bb = [body.matrix_world @ _V(c) for c in body.bound_box]
X0, X1 = min(v.x for v in _bb), max(v.x for v in _bb)
Y0, Y1 = min(v.y for v in _bb), max(v.y for v in _bb)
Z1 = max(v.z for v in _bb)
print(">> blob bbox x %.3f..%.3f y %.3f..%.3f ztop %.3f" % (X0, X1, Y0, Y1, Z1))
CUTS = [
    # 切り面は2枚だけ：左前の縦の面・頭の斜め
    cube("c_left", (X0 - 0.10, Y0 - 0.06, 0.45), (0.7, 0.7, 2.2), (0, 3, 45)),
    cube("c_top", (0.0, 0.0, Z1 - 0.08 + 0.25), (1.6, 1.6, 0.5), (7, -15, 0)),
    # えぐり：右前の中ほどの大きな凹み
    ell("s_main", (0.08, Y0 + 0.05, 0.46), (0.16, 0.16, 0.25), (0, -14, 0)),
    cube("c_low", (X0 - 0.30, Y0 - 0.22, -0.05), (0.7, 0.7, 0.7), (28, -18, 40)),
    ell("s_main3", (0.03, Y0 + 0.08, 0.64), (0.09, 0.12, 0.16), (0, -35, 0)),
    ell("s_main2", (0.15, Y0 + 0.06, 0.30), (0.10, 0.12, 0.13), (0, 30, 0)),
    ell("s_dip", (-0.05, 0.0, Z1 - 0.03), (0.09, 0.5, 0.12)),
    ell("s_head", (-0.10, Y0 + 0.03, Z1 - 0.24), (0.12, 0.09, 0.10), (0, 20, 0)),
    ell("s_rsh", (X1 - 0.02, -0.06, 0.76), (0.08, 0.16, 0.18), (0, 10, 0)),
]
for c in [c for c in CUTS if c.name in os.environ.get("II_NOCUT", "").split(",")]:
    CUTS.remove(c); bpy.data.objects.remove(c, do_unlink=True)
for c in CUTS:
    m = body.modifiers.new(c.name, 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = c; m.solver = 'EXACT'
    c.hide_render = True; c.hide_viewport = True
if float(os.environ.get("II_VX", "0")) > 0:   # 🔴 ボクセルはえぐりの縁を段のギザギザにする（round 28・testhero で見えた）＝既定は通さない
    rm = body.modifiers.new("rm", 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = float(os.environ.get("II_VX", "0"))
sm = body.modifiers.new("sm", 'SMOOTH'); sm.factor = 0.5; sm.iterations = int(os.environ.get("II_SM", "0"))
bpy.context.view_layer.objects.active = body
for m in list(body.modifiers):
    bpy.ops.object.modifier_apply(modifier=m.name)
for c in CUTS:
    bpy.data.objects.remove(c, do_unlink=True)
for p in body.data.polygons:
    p.use_smooth = True
# 🔴 Boolean の縁の細い三角形は頂点法線の補間で鋸歯に写る（round 29）＝角度で稜を分ける
bpy.context.view_layer.objects.active = body; body.select_set(True)
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
gm = principled("glass", hex_to_linear(os.environ.get("II_GC", "#FBE0DE")), rough=0.0, trans=1.0, ior=1.6)   # 薄い薔薇色の色ガラス
if float(os.environ.get("II_ABS", "0.7")) > 0:   # 体積吸収：長く通る縁ほど暗く（round 39）
    _va = gm.node_tree.nodes.new("ShaderNodeVolumeAbsorption")
    _va.inputs["Color"].default_value = hex_to_linear("#E8D0CC"); _va.inputs["Density"].default_value = float(os.environ.get("II_ABS", "0.7"))
    gm.node_tree.links.new(_va.outputs[0], gm.node_tree.nodes["Material Output"].inputs["Volume"])
if float(os.environ.get("II_RIM", "1")) > 0:   # 輪郭の墨：視線と面がすれ違う所ほど色ガラスを暗く（round 41）
    _gn, _gl = gm.node_tree.nodes, gm.node_tree.links
    _lw = _gn.new("ShaderNodeLayerWeight"); _lw.inputs["Blend"].default_value = 0.5
    _rr = _gn.new("ShaderNodeMapRange"); _rr.inputs["From Min"].default_value = float(os.environ.get("II_RIM0", "0.78"))
    _rr.inputs["From Max"].default_value = 0.97
    _gl.new(_lw.outputs["Facing"], _rr.inputs["Value"])
    _rm = _gn.new("ShaderNodeMix"); _rm.data_type = 'RGBA'
    _rm.inputs[6].default_value = hex_to_linear(os.environ.get("II_GC", "#FBE0DE")); _rm.inputs[7].default_value = hex_to_linear("#3B2B30")
    _gl.new(_rr.outputs["Result"], _rm.inputs[0]); _gl.new(_rm.outputs[2], _gn["Principled BSDF"].inputs["Base Color"])
body.data.materials.clear()   # 🔴 Boolean が空のスロットを足す＝面が None のスロットを指して灰色の不透明に写る
body.data.materials.append(gm)
# 黒レフ：カメラの左右後方に黒い板（カメラ・影には写らず、ガラスの反射と屈折にだけ写る）＝ガラスの縁と中の墨の線
def flag(name, loc, size, target, glossy=False):
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=0.5, fill_type='NGON', location=loc)
    f = bpy.context.object; f.name = name; f.scale = (size[0], size[1], 1)
    f.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.004, 0.005, 0.008, 1)
    b.inputs["Roughness"].default_value = 1.0; b.inputs["Specular IOR Level"].default_value = 0.0
    if not os.environ.get("II_FLAGNOISE"):   # ノイズで抜くと染みになった（round 29）＝既定は無地の楕円
        f.data.materials.append(m)
        f.visible_camera = False; f.visible_shadow = False; f.visible_diffuse = False; f.visible_glossy = glossy
        return f
    nn, ll = m.node_tree.nodes, m.node_tree.links
    tx = nn.new("ShaderNodeTexCoord"); mpp = nn.new("ShaderNodeMapping"); mpp.inputs["Scale"].default_value = (1.0, 3.5, 1.0)
    nz = nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 4.0
    nz.noise_dimensions = '4D'; nz.inputs["W"].default_value = len(name) * 1.7 + (3.1 if name.endswith("r") else 0.0)
    rr = nn.new("ShaderNodeMapRange"); rr.inputs["From Min"].default_value = 0.47; rr.inputs["From Max"].default_value = 0.53
    gd = nn.new("ShaderNodeVectorMath"); gd.operation = 'LENGTH'
    rad = nn.new("ShaderNodeMapRange"); rad.inputs["From Min"].default_value = 0.30; rad.inputs["From Max"].default_value = 0.5
    rad.inputs["To Min"].default_value = 0.0; rad.inputs["To Max"].default_value = 0.6
    ad = nn.new("ShaderNodeMath"); ad.operation = 'ADD'
    tr = nn.new("ShaderNodeBsdfTransparent"); mx = nn.new("ShaderNodeMixShader")
    ll.new(tx.outputs["Object"], mpp.inputs["Vector"]); ll.new(mpp.outputs["Vector"], nz.inputs["Vector"])
    ll.new(tx.outputs["Object"], gd.inputs[0]); ll.new(gd.outputs["Value"], rad.inputs["Value"])
    ll.new(nz.outputs["Fac"], ad.inputs[0]); ll.new(rad.outputs["Result"], ad.inputs[1])
    ll.new(ad.outputs[0], rr.inputs["Value"])
    ll.new(rr.outputs["Result"], mx.inputs[0]); ll.new(b.outputs["BSDF"], mx.inputs[1]); ll.new(tr.outputs[0], mx.inputs[2])
    ll.new(mx.outputs[0], nn["Material Output"].inputs["Surface"])
    f.data.materials.append(m)
    f.visible_camera = False; f.visible_shadow = False; f.visible_diffuse = False
    f.visible_glossy = False     # 水面とガラスの「反射」には写さない＝屈折にだけ写る
    return f
# 🔴 カメラの後ろに立てた黒レフは効かなかった（round 20）：ガラスを通った光線はほぼ前へ抜ける。黒は塊の向こう側に置く
FLAGS = [] if os.environ.get("II_NOFLAG") else [
    flag("flag_l", (-0.30, 1.2, 0.60), (0.18, 0.85), (0.4, -6, 0.2)),
    flag("flag_r", (0.26, 1.5, 0.32), (0.14, 0.55), (-0.6, -6, 0.9)),
    flag("flag_top", (0.0, 0.3, 1.6), (3.0, 3.0), (0.0, 0.0, 0.0)),
    flag("flag_back", (0.0, 2.2, 1.9), (2.4, 1.0), (0.0, 0.0, 0.9)),
] + ([] if os.environ.get("II_NORIMFLAG") else [
    # 輪郭の墨：反射にだけ写る黒い板（round 42）。画角の外なので水面の映り込みは画面に入らない
    flag("rim_l", (-6.0, 1.0, 1.0), (5.0, 4.0), (0, 0, 0.5), glossy=True),
    flag("rim_r", (6.0, 1.0, 1.0), (5.0, 4.0), (0, 0, 0.5), glossy=True),
    flag("rim_t", (0.0, 1.5, 4.0), (5.0, 4.0), (0, 0, 0.5), glossy=True),
])
parts = [body]   # 🔴 被写体は全部ここへ（水面・空は入れない）

# ------------------------------------------------------------- カメラ：水面すれすれの望遠
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.sensor_width = 18
scene.camera = cam
_B = int(os.environ.get("II_BOUNCE", "24"))
scene.cycles.max_bounces = _B
scene.cycles.transmission_bounces = _B
scene.cycles.glossy_bounces = _B
scene.cycles.transparent_max_bounces = 16
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False

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
TGT = Vector((0, 0, 0.47))
HERO_LOC = Vector((0.0, -6.0, 0.05))
HERO_TGT = Vector((0.0, 0.0, 0.50))
SHOTS = [
    dict(sec=3.0,   # 回り込み：左から弧で入る。屈折の面が流れて入れ替わる
         cam=lambda t: (orbit(TGT, 5.2, 0.12, -38 + 26 * ease(t)), TGT + Vector((0, 0, 0.02)), 70, 5.6, None)),
    dict(sec=2.75,  # マクロ：えぐりの縁をなめ上がる・浅いピント
         cam=lambda t: (lerp((0.55, -1.55, 0.30), (0.45, -1.50, 0.62), ease(t)), Vector((0.10, -0.12, 0.42 + 0.22 * ease(t))),
                        120, 8.0, (Vector((0.10, -0.17, 0.42 + 0.22 * ease(t))) - lerp((0.55, -1.55, 0.30), (0.45, -1.50, 0.62), ease(t))).length)),
    dict(sec=2.75,  # 押し込み：水面の高さで寄る。足元の映り込みとさざ波
         cam=lambda t: (lerp((1.9, -2.9, 0.04), (1.3, -2.2, 0.04), ease(t)), Vector((0.0, 0.0, 0.34)), 55, 4.0, None)),
    dict(sec=3.0,   # 決め：右から寄りながら入って止まる
         cam=lambda t: (lerp(HERO_LOC + Vector((0.7, 0.9, 0.06)), HERO_LOC, ease_out(min(1.0, t / 0.62))), HERO_TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    pass

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
        water_t.default_value = 0.35 * (f - 1) / FPS
        water_t.keyframe_insert("default_value", frame=f)

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
