# =============================================================
# MIDDLE STUDIES II 024 — WARP（経糸）  FORM
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots
# 基準: Gabriel Dawe「Plexus A1」設置写真（白い展示室・窓の昼光・糸のスペクトル）
# 造形は自前：天井の長い線から床の短い線へ、ねじれた線織面として糸を張る
# =============================================================
import bpy, bmesh, math, os, sys, colorsys, random
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(3, 2),
    lens=36,
    fstop=11.0,
    view="AgX",
    look="AgX - Medium High Contrast",
    exposure=0.15,
)
FPS = 24


def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


def srgb_to_linear(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def hex_to_linear(h):
    h = h.lstrip("#")
    return srgb_to_linear([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def bevel_obj(ob, width, segments=3, clamp=True, angle=30):
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
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    return m


def box(name, lo, hi, mat, bev=0.0):
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=c)
    o = bpy.context.object; o.name = name
    o.scale = [hi[i] - lo[i] for i in range(3)]
    bpy.ops.object.transform_apply(scale=True)
    if bev:
        bevel_obj(o, bev, segments=2)
    o.data.materials.append(mat)
    return o


# ------------------------------------------------------------- 舞台：白い展示室
RX0, RX1, RY0, RY1, RZ = -4.0, 4.5, -7.0, 9.0, 5.2   # 部屋の内寸
wall_m = principled("plaster", hex_to_linear("#E9E6E0"), rough=0.75)
trim_m = principled("trim", hex_to_linear("#DCD8D0"), rough=0.6)
floor_m = bpy.data.materials.new("oak"); floor_m.use_nodes = True
nt = floor_m.node_tree; P = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.9, 0.06, 1.0)  # 板目は y 方向に長い
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30.0
nz.inputs["Detail"].default_value = 6.0
nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
# 板の継ぎ目（幅 12cm）
wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
wv.inputs["Scale"].default_value = 1.0 / 0.12 / 1.0
wv.inputs["Distortion"].default_value = 0.0
nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
cr = nt.nodes.new("ShaderNodeValToRGB")
cr.color_ramp.elements[0].position = 0.3; cr.color_ramp.elements[0].color = hex_to_linear("#8A5F3A")
cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = hex_to_linear("#BE8D57")
nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
P.inputs["Roughness"].default_value = 0.32
P.inputs["Coat Weight"].default_value = 0.35
P.inputs["Coat Roughness"].default_value = 0.18
# 板ごとの色むら（板の番号＝x を 12cm で切った値でノイズを引く）＋継ぎ目の暗い線
sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sx.inputs[0])
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'DIVIDE'; mul.inputs[1].default_value = 0.12
nt.links.new(sx.outputs["X"], mul.inputs[0])
fl = nt.nodes.new("ShaderNodeMath"); fl.operation = 'FLOOR'; nt.links.new(mul.outputs[0], fl.inputs[0])
wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = '1D'; nt.links.new(fl.outputs[0], wn.inputs["W"])
plank = nt.nodes.new("ShaderNodeMapRange"); plank.inputs[3].default_value = 0.78; plank.inputs[4].default_value = 1.12
nt.links.new(wn.outputs["Value"], plank.inputs[0])
fr = nt.nodes.new("ShaderNodeMath"); fr.operation = 'FRACT'; nt.links.new(mul.outputs[0], fr.inputs[0])
seam = nt.nodes.new("ShaderNodeMapRange"); seam.inputs[1].default_value = 0.0; seam.inputs[2].default_value = 0.035
seam.inputs[3].default_value = 0.45; seam.inputs[4].default_value = 1.0
nt.links.new(fr.outputs[0], seam.inputs[0])
m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = 'RGBA'; m1.blend_type = 'MULTIPLY'; m1.inputs[0].default_value = 1.0
nt.links.new(cr.outputs["Color"], m1.inputs[6])
# 長さ方向の継ぎ目：板ごとに乱数でずらした 0.9m 刻み
yy = nt.nodes.new("ShaderNodeMath"); yy.operation = 'MULTIPLY_ADD'
nt.links.new(wn.outputs["Value"], yy.inputs[0]); yy.inputs[1].default_value = 0.9
nt.links.new(sx.outputs["Y"], yy.inputs[2])
yd = nt.nodes.new("ShaderNodeMath"); yd.operation = 'DIVIDE'; yd.inputs[1].default_value = 0.9
nt.links.new(yy.outputs[0], yd.inputs[0])
yf = nt.nodes.new("ShaderNodeMath"); yf.operation = 'FRACT'; nt.links.new(yd.outputs[0], yf.inputs[0])
yseam = nt.nodes.new("ShaderNodeMapRange"); yseam.inputs[1].default_value = 0.0; yseam.inputs[2].default_value = 0.006
yseam.inputs[3].default_value = 0.5; yseam.inputs[4].default_value = 1.0
nt.links.new(yf.outputs[0], yseam.inputs[0])
# 継ぎ目の先の板は色を変える（板の番号＋継ぎ目の番号で別の乱数）
yfl = nt.nodes.new("ShaderNodeMath"); yfl.operation = 'FLOOR'; nt.links.new(yd.outputs[0], yfl.inputs[0])
wn2 = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn2.noise_dimensions = '2D'
cv = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(fl.outputs[0], cv.inputs[0]); nt.links.new(yfl.outputs[0], cv.inputs[1])
nt.links.new(cv.outputs[0], wn2.inputs["Vector"])
nt.links.new(wn2.outputs["Value"], plank.inputs[0])
s2 = nt.nodes.new("ShaderNodeMath"); s2.operation = 'MULTIPLY'
nt.links.new(seam.outputs[0], s2.inputs[0]); nt.links.new(yseam.outputs[0], s2.inputs[1])
cmb = nt.nodes.new("ShaderNodeMath"); cmb.operation = 'MULTIPLY'
nt.links.new(plank.outputs[0], cmb.inputs[0]); nt.links.new(s2.outputs[0], cmb.inputs[1])
nt.links.new(cmb.outputs[0], m1.inputs[7])
# 🔴 Mix(RGBA) は index 6/7/2 で繋ぐ（名前の "A"/"Result" は Float のソケットを返す＝PITFALLS #103）
nt.links.new(m1.outputs[2], P.inputs["Base Color"])

box("floor", (RX0, RY0, -0.1), (RX1, RY1, 0.0), floor_m)
box("ceiling", (RX0, RY0, RZ), (RX1, RY1, RZ + 0.1), wall_m)
DX0, DX1, DZ = -1.2, 0.6, 3.3   # 奥の壁の開口（次の部屋へ）
box("back_l", (RX0, RY1, 0), (DX0, RY1 + 0.3, RZ), wall_m)
box("back_r", (DX1, RY1, 0), (RX1, RY1 + 0.3, RZ), wall_m)
box("back_t", (DX0, RY1, DZ), (DX1, RY1 + 0.3, RZ), wall_m)
# 次の部屋（明るい）
box("next_floor", (RX0, RY1, -0.1), (RX1, RY1 + 5, 0.0), floor_m)
box("next_back", (RX0, RY1 + 5, 0), (RX1, RY1 + 5.2, RZ), wall_m)
box("next_ceil", (RX0, RY1, RZ), (RX1, RY1 + 5, RZ + 0.1), wall_m)
box("next_r", (RX1, RY1, 0), (RX1 + 0.2, RY1 + 5, RZ), wall_m)
box("next_l", (RX0 - 0.2, RY1, 0), (RX0, RY1 + 5, RZ), wall_m)
ld = bpy.data.lights.new("next_sky", 'AREA'); ld.shape = 'RECTANGLE'; ld.size, ld.size_y = 6.0, 4.0
ld.energy = 600; ld.color = (1.0, 0.97, 0.93)
_L = bpy.data.objects.new("next_sky", ld); scene.collection.objects.link(_L)
_L.location = (0.0, RY1 + 2.5, RZ - 0.05); _L.visible_camera = False
box("front", (RX0, RY0 - 0.2, 0), (RX1, RY0, RZ), wall_m)
box("right", (RX1, RY0, 0), (RX1 + 0.2, RY1, RZ), wall_m)
# 左の壁：背の高い窓を3つ抜く（窓の奥は空＝World）
WIN = [(-3.4, -1.4), (0.8, 2.8), (5.0, 7.0)]     # y の範囲
WZ0, WZ1 = 0.9, 4.4
ys = [RY0] + [v for w in WIN for v in w] + [RY1]
for k in range(0, len(ys), 2):
    box("lwall_%d" % k, (RX0 - 0.35, ys[k], 0), (RX0, ys[k + 1], RZ), wall_m)
for (a, b) in WIN:
    box("sill_%d" % a, (RX0 - 0.35, a, 0), (RX0, b, WZ0), wall_m)
    box("head_%d" % a, (RX0 - 0.35, a, WZ1), (RX0, b, RZ), wall_m)
    # 窓の桟（縦1本・横2本）
    box("mul_%d" % a, (RX0 - 0.2, (a + b) / 2 - 0.03, WZ0), (RX0 - 0.14, (a + b) / 2 + 0.03, WZ1), trim_m)
    for zz in (WZ0 + (WZ1 - WZ0) / 3, WZ0 + 2 * (WZ1 - WZ0) / 3):
        box("tr_%d_%d" % (a, zz * 10), (RX0 - 0.2, a, zz - 0.03), (RX0 - 0.14, b, zz + 0.03), trim_m)
# 巾木
box("base_r", (RX1 - 0.03, RY0, 0), (RX1, RY1, 0.16), trim_m)
box("base_b", (RX0, RY1 - 0.03, 0), (RX1, RY1, 0.16), trim_m)
# 糸を受ける低い白い台（床の線の下）
plinth_m = principled("plinth", hex_to_linear("#F1EFEA"), rough=0.5)
box("base_plinth", (0.45, 3.1, 0.0), (1.45, 4.7, 0.05), plinth_m, bev=0.012)
# 天井の回り縁
box("cornice_l", (RX0, RY0, RZ - 0.22), (RX0 + 0.12, RY1, RZ), trim_m, bev=0.01)
box("cornice_r", (RX1 - 0.12, RY0, RZ - 0.22), (RX1, RY1, RZ), trim_m, bev=0.01)
box("cornice_b", (RX0, RY1 - 0.12, RZ - 0.22), (RX1, RY1, RZ), trim_m, bev=0.01)
# 左の壁の巾木と腰の見切り
box("base_l", (RX0, RY0, 0), (RX0 + 0.03, RY1, 0.16), trim_m)
# 奥行きの柱（正方形の角柱・面取り）
PILLARS = [(2.6, 3.2), (2.6, 6.6)]
for i, (px, py) in enumerate(PILLARS):
    box("pillar_%d" % i, (px - 0.28, py - 0.28, 0), (px + 0.28, py + 0.28, RZ), wall_m, bev=0.01)
    box("plinth_%d" % i, (px - 0.36, py - 0.36, 0), (px + 0.36, py + 0.36, 0.55), trim_m, bev=0.01)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
sky = world.node_tree.nodes.new("ShaderNodeTexSky")
try:
    sky.sky_type = 'NISHITA'
except Exception:
    pass
bgn = world.node_tree.nodes["Background"]
world.node_tree.links.new(sky.outputs["Color"], bgn.inputs["Color"])
bgn.inputs["Strength"].default_value = 0.35
SUN_ROT = (math.radians(60), 0, math.radians(-100))   # 左手前の高い日差し
try:
    sky.sun_elevation = math.radians(38)
    sky.sun_rotation = math.radians(200)
    sky.sun_disc = False
except Exception:
    pass

sun_d = bpy.data.lights.new("sun", 'SUN'); sun_d.energy = 11.0; sun_d.angle = math.radians(1.2)
sun_d.color = (1.0, 0.95, 0.88)
sun = bpy.data.objects.new("sun", sun_d); scene.collection.objects.link(sun)
sun.rotation_euler = SUN_ROT
# 窓からの天空光（面光源を窓の外に・カメラには写さない）
for (a, b) in WIN:
    ld = bpy.data.lights.new("win_%d" % a, 'AREA'); ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = (b - a), (WZ1 - WZ0); ld.energy = 150; ld.color = (0.92, 0.96, 1.0)
    L = bpy.data.objects.new("win_%d" % a, ld); scene.collection.objects.link(L)
    L.location = (RX0 - 0.4, (a + b) / 2, (WZ0 + WZ1) / 2)
    L.rotation_euler = (0, math.radians(90), 0)   # -Z を +X（室内）へ
    L.rotation_euler = (Vector((1, 0, 0))).to_track_quat('-Z', 'Y').to_euler()
    L.visible_camera = False

# ------------------------------------------------------------- 被写体：糸の線織面
N_THREADS = 4800
N_BUCKET = 36
R_THREAD = 0.0006
SEG = 40
TOP0, TOP1 = Vector((RX0 + 0.02, -3.0, 2.3)), Vector((1.6, 5.2, RZ))  # 左の壁の中ほど→天井の奥へ斜めに上る長い線
BOT0, BOT1 = Vector((1.15, 4.35, 0.05)), Vector((0.75, 3.45, 0.05))   # 床の短い線（向きを返してねじる）
# 起点は2本：u<SPLIT は左の壁を斜めに上る線、u>=SPLIT は奥の天井の線。床の1本で合わせる＝V字に開き、間から部屋が抜ける
WALL0, WALL1 = Vector((RX0 + 0.02, -4.4, 0.7)), Vector((RX0 + 0.02, 1.0, 5.0))
CEIL0, CEIL1 = Vector((-0.6, 4.2, RZ)), Vector((2.3, 6.4, RZ))
SPLIT = 0.5


def top_anchor(u):
    if u < SPLIT:
        t = u / SPLIT   # 壁の上で前上へふくらむ弧＝面の縁が直線にならない
        return WALL0.lerp(WALL1, t) + Vector((0, -1.1, 0.9)) * math.sin(math.pi * t)
    return CEIL0.lerp(CEIL1, (u - SPLIT) / (1 - SPLIT))


def bot_anchor(u):
    """床の線。手前の束は並びを逆にする＝壁の線と交差して、面の縁が直線でなく包絡の弧になる"""
    mid = BOT0.lerp(BOT1, SPLIT)
    if u < SPLIT:
        return mid.lerp(BOT0, u / SPLIT)
    return BOT0.lerp(BOT1, u)


random.seed(24)


def spectrum(u):
    """u=0 青紫 → 1 赤。糸の染めの色＝飽和は高いが蛍光にはしない"""
    h = 0.74 * (1 - u)
    r, g, b = colorsys.hsv_to_rgb(h, 0.86, 0.92)
    return srgb_to_linear((r, g, b)) + (1.0,)


def thread_mat(i, col):
    m = bpy.data.materials.new("thread_%02d" % i); m.use_nodes = True
    nt = m.node_tree; P = nt.nodes["Principled BSDF"]
    # 長さ方向の明暗のむら（撚りで光が割れる＝基準の糸のまだら）
    #   🔴 物体座標のノイズは糸をまたぐ斑点になる。糸1本ごとの乱数（Hair Info の Random）で振る
    hi = nt.nodes.new("ShaderNodeHairInfo")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[3].default_value = 0.6; mr.inputs[4].default_value = 1.3
    nt.links.new(hi.outputs["Random"], mr.inputs[0])
    mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = 'RGBA'; mx2.blend_type = 'MULTIPLY'; mx2.inputs[0].default_value = 1.0
    mx2.inputs[6].default_value = col
    nt.links.new(mr.outputs[0], mx2.inputs[7])
    nt.links.new(mx2.outputs[2], P.inputs["Base Color"])
    P.inputs["Roughness"].default_value = 0.28
    P.inputs["Sheen Weight"].default_value = 0.6
    P.inputs["Sheen Tint"].default_value = col
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = col
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs["Fac"].default_value = 0.15
    out = nt.nodes["Material Output"]
    nt.links.new(P.outputs["BSDF"], mx.inputs[1]); nt.links.new(tr.outputs["BSDF"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
    return m


buckets = [[] for _ in range(N_BUCKET)]
for k in range(N_THREADS):
    v = (k + random.random() * 0.8) / N_THREADS
    u = v * 1.5 if v < 1 / 3 else SPLIT + (v - 1 / 3) * 0.75   # 奥の束は遠くて細るので手前の2倍の本数
    buckets[min(N_BUCKET - 1, int(u * N_BUCKET))].append(u)

# 🔴 糸は Curves（髪のカーブ）で持つ。メッシュの管（Curve の bevel）は外接箱が細長く、
#    2点のままだと 360px・8smp が37秒（糸なし3秒）。24区間に刻んでも 32smp で36秒。Curves は同じ絵で 6.8秒。
#    Curves も 1本を SEG 区間に刻む（BVH が糸の区間ごとに箱を持つ）
def trim_group():
    ng = bpy.data.node_groups.new("trim", 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    s = ng.interface.new_socket("End", in_out='INPUT', socket_type='NodeSocketFloat')
    s.default_value = 1.0; s.min_value = 0.0; s.max_value = 1.0
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gi = ng.nodes.new("NodeGroupInput"); go = ng.nodes.new("NodeGroupOutput")
    tr = ng.nodes.new("GeometryNodeTrimCurve"); tr.mode = 'FACTOR'
    ng.links.new(gi.outputs[0], tr.inputs["Curve"])
    ng.links.new(gi.outputs[1], tr.inputs[3])          # End（Factor モードの終点）
    ng.links.new(tr.outputs[0], go.inputs[0])
    return ng


TRIM = trim_group()
threads = []                 # [(上の点, 下の点, 材質番号)] を色の束ごとに（glb 用にも使う）
parts = []
for i, us in enumerate(buckets):
    rows = []
    for u in us:
        a = top_anchor(u); b = bot_anchor(u)
        b = b + Vector((random.gauss(0, 0.004), random.gauss(0, 0.004), 0))
        r = random.random()   # 0 自分・1 暗い自分・2/3 隣の色（±2束ぶん）＝束の中で糸ごとに色が混ざる
        rows.append((a, b, 0 if r < 0.45 else 1 if r < 0.7 else 2 if r < 0.85 else 3))
    threads.append(rows)
    uc = (i + 0.5) / N_BUCKET
    hc = bpy.data.hair_curves.new("warp_%02d" % i)
    hc.add_curves([SEG + 1] * len(rows))
    pos = []
    for (a, b, _) in rows:
        for j in range(SEG + 1):
            q = a.lerp(b, j / SEG); pos += [q.x, q.y, q.z]
    hc.position_data.foreach_set("vector", pos)
    rad = hc.attributes.new("radius", 'FLOAT', 'POINT')
    rr = R_THREAD * (1.9 if uc < SPLIT else 1.0)   # 手前の面は糸を太く＝1本ずつ色が読める
    rad.data.foreach_set("value", [rr] * (len(rows) * (SEG + 1)))
    uc = (i + 0.5) / N_BUCKET
    col = spectrum(uc / SPLIT if uc < SPLIT else 1 - (uc - SPLIT) / (1 - SPLIT))   # 手前で紫→赤、奥で赤→紫に折り返す
    hc.materials.append(thread_mat(i, col))
    # 同じ色の中に暗い糸を混ぜる（4割）＝束の縞の肌理
    hc.materials.append(thread_mat(i + 100, tuple([c * 0.55 for c in col[:3]] + [1.0])))
    for dj in (-4, 4):
        uc2 = min(0.999, max(0.0, uc + dj / N_BUCKET))
        if (uc2 < SPLIT) != (uc < SPLIT):
            uc2 = uc
        hc.materials.append(thread_mat(i + 200 + int(dj), spectrum(uc2 / SPLIT if uc2 < SPLIT else 1 - (uc2 - SPLIT) / (1 - SPLIT))))
    mi = hc.attributes.new("material_index", 'INT', 'CURVE')
    mi.data.foreach_set("value", [r[2] for r in rows])
    ob = bpy.data.objects.new("warp_%02d" % i, hc); scene.collection.objects.link(ob)
    md = ob.modifiers.new("trim", 'NODES'); md.node_group = TRIM
    parts.append(ob)


def trim_key():
    return [it.identifier for it in TRIM.interface.items_tree if getattr(it, "in_out", "") == 'INPUT' and it.name == "End"][0]


TRIM_ID = trim_key()

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
cd.clip_start = 0.05
scene.camera = cam


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


HERO_LOC = Vector((0.9, -4.6, 1.55))
HERO_TGT = Vector((0.2, 3.0, 1.75))
FOCUS = 4.2   # 手前の糸とくびれの間
SHOTS = [
    # 物の動き：台の脇の低い所から見上げる。糸が天井から色の順に降りてきて台に届く
    dict(sec=3.2, cam=lambda t: (lerp((2.9, 0.2, 0.55), (2.6, 0.7, 0.62), ease(t)), Vector((0.9, 4.3, 1.25)), 24, 8.0, None)),
    # マクロ：120mm で台の上のくびれ。手前の糸からくびれへピントを送る
    dict(sec=3.0, cam=lambda t: (lerp((2.75, 1.55, 0.42), (2.55, 1.75, 0.36), ease(t)), Vector((0.98, 3.92, 0.22)),
                                 120, 2.8, 2.15 + 0.75 * ease(t))),
    # 光の走り：手前の面を右から。日差しが回って窓の日だまりが床を滑る
    dict(sec=2.6, cam=lambda t: (lerp((2.6, -2.6, 1.25), (2.4, -2.3, 1.3), ease(t)), Vector((-2.2, 0.6, 1.5)), 40, 8.0, 3.6)),
    # 決め：引きから寄りながら hero の構図に入って止まる
    dict(sec=2.7, cam=lambda t: (lerp(HERO_LOC + Vector((-0.35, -0.9, 0.12)), HERO_LOC, ease_out(min(1.0, t / 0.6))), HERO_TGT,
                                 LOOK["lens"], LOOK["fstop"], FOCUS)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    """1カット目だけ、糸が天井から降りる（色の束ごとに少しずつ遅れて）。以降は張り終わった姿"""
    for k, o in enumerate(parts):
        if i == 0:
            d = 0.45 * k / (len(parts) - 1)
            v = ease(min(1.0, max(0.0, (t * 1.25 - d) / 0.55)))
            o.modifiers["trim"][TRIM_ID] = max(0.001, v)
        else:
            o.modifiers["trim"][TRIM_ID] = 1.0


def light_path(i, t):
    """3カット目だけ日差しを回して、窓の日だまりを床の上で滑らせる"""
    if i == 2:
        sun.rotation_euler = (SUN_ROT[0], 0, SUN_ROT[2] + math.radians(-24 + 40 * ease(t)))
    else:
        sun.rotation_euler = SUN_ROT


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
            o.keyframe_insert('modifiers["trim"]["%s"]' % TRIM_ID, frame=f)
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
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 5
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

# glb は最後：糸（Curve）はメッシュに直して書き出す。糸の「降りてくる」動きは形状なので、
# glb には各色の束の y スケールで降下を近似したキーを打つ
if "glb" in modes:
    # Curves は glTF に載らない → 糸を三角柱（3面・1区間）のメッシュに直す（4800本で約3万頂点）。
    # 動きは1カット目の「糸が降りる」：束ごとに天井側の重心を原点にして、伸び（scale）を 0→1 にキーで打つ
    glb_objs = []
    for i, rows in enumerate(threads):
        top_c = sum((r[0] for r in rows), Vector()) / len(rows)
        verts, faces = [], []
        rr = R_THREAD * 2.5
        for (a, b, _) in rows:
            d = (b - a).normalized()
            n1 = d.orthogonal().normalized(); n2 = d.cross(n1)
            base = len(verts)
            for p in (a, b):
                for k in range(3):
                    ang = 2 * math.pi * k / 3
                    verts.append(tuple(p - top_c + (n1 * math.cos(ang) + n2 * math.sin(ang)) * rr))
            for k in range(3):
                k2 = (k + 1) % 3
                faces.append((base + k, base + k2, base + 3 + k2, base + 3 + k))
        me = bpy.data.meshes.new("glb_warp_%02d" % i); me.from_pydata(verts, [], faces); me.update()
        me.materials.append(parts[i].data.materials[0])
        go = bpy.data.objects.new("warp_%02d_mesh" % i, me); scene.collection.objects.link(go)
        go.location = top_c
        glb_objs.append(go)
    for f in list(range(1, SHOTS[0]["frames"] + 1)) + [N_FRAMES]:
        t = (f - 1) / max(1, SHOTS[0]["frames"] - 1)
        for k, go in enumerate(glb_objs):
            if f <= SHOTS[0]["frames"]:
                d = 0.45 * k / (len(glb_objs) - 1)
                v = max(0.001, ease(min(1.0, max(0.0, (t * 1.25 - d) / 0.55))))
            else:
                v = 1.0
            go.scale = (v, v, v)
            go.keyframe_insert("scale", frame=f)
    scene.frame_end = N_FRAMES + 1
    for o in bpy.data.objects:
        o.select_set(o in glb_objs)
    bpy.context.view_layer.objects.active = glb_objs[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
