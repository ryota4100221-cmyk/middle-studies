# =============================================================
# MIDDLE STUDIES II 019 — VANITY（化粧台）
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
#
# 角を丸めた四角の断面（スーパー楕円）で揃えた自作の化粧品一式を、卓の奥の縁に横一列に並べる。
# 奥の高い位置から硬めの1灯で、影は手前の卓へ落ちる。正面は大きく柔らかい起こし。上半分は壁の余白。
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}
OFF = set(os.environ.get("II_OFF", "").split(","))   # 光を1つずつ消して犯人を探す用


def hex_to_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(2, 1),
    lens=105,
    fstop=9.0,
    view="Khronos PBR Neutral",
    look="None",
    exposure=-0.6,
    wall="#ECE7E4",
    table="#8E9389",
)
FPS = 24


def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ------------------------------------------------------------- 造形の道具
def sq_pt(a, b, n, t):
    c, s = math.cos(t), math.sin(t)
    return (a * math.copysign(abs(c) ** (2 / n), c), b * math.copysign(abs(s) ** (2 / n), s))


def sq_solid(name, a, b, h, n=3.2, rb=0.002, rt=0.002, slope=0.0, N=128, K=6, z0=0.0, bulge=0.0):
    """スーパー楕円（半径 a×b・指数 n）の柱。下と上の縁は半径 rb/rt の丸み（行で起こす＝面取り込み）。
    slope は天面の傾き（z += slope·x）＝口紅の斜めの切り口。bulge は胴のわずかな膨らみ。"""
    rows = []                                    # (inset d, z, 天面の傾きを掛けるか)
    for k in range(K + 1):                       # 下の丸み
        p = math.pi / 2 * k / K
        rows.append((rb * (1 - math.sin(p)), rb * (1 - math.cos(p)), False))
    for k in range(1, 6):                        # 胴
        rows.append((-bulge * math.sin(math.pi * k / 6), rb + (h - rb - rt) * k / 6, False))
    for k in range(K + 1):                       # 上の丸み
        p = math.pi / 2 * k / K
        rows.append((rt * (1 - math.cos(p)), h - rt + rt * math.sin(p), True))
    bm = bmesh.new()
    rings = []
    for d, z, top in rows:
        ring = []
        for i in range(N):
            x, y = sq_pt(max(a - d, 1e-4), max(b - d, 1e-4), n, 2 * math.pi * i / N)
            ring.append(bm.verts.new((x, y, z0 + z + (slope * x if top else 0))))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(N):
            j = (i + 1) % N
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    cb = bm.verts.new((0, 0, z0)); ct = bm.verts.new((0, 0, z0 + h))
    for i in range(N):
        j = (i + 1) % N
        bm.faces.new((rings[0][j], rings[0][i], cb))
        bm.faces.new((rings[-1][i], rings[-1][j], ct))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, trans=0.0, ior=1.45, spec=0.5,
               sss=0.0, coat_rough=0.03):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = coat_rough
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    p.inputs["Specular IOR Level"].default_value = spec
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (0.004, 0.0015, 0.001)
    return m


def setmat(ob, m):
    ob.data.materials.clear(); ob.data.materials.append(m)
    return ob


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.05), shape='RECTANGLE', size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.shape, ld.size = energy, color, shape, size
    if size_y:
        ld.size_y = size_y
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    if name in OFF:
        ld.energy = 0
    return L


# ------------------------------------------------------------- 素材
M = dict(
    cream=principled("cream", hex_to_linear("#F1E5E0"), rough=0.30, spec=0.45),
    blush=principled("blush", hex_to_linear("#EBC8BC"), rough=0.30, spec=0.45),
    sage=principled("sage", hex_to_linear("#C9CCBF"), rough=0.34, spec=0.45),
    lacquer=principled("lacquer", hex_to_linear("#E8381F"), rough=0.30, coat=1.0, coat_rough=0.012, spec=0.0),
    gold=principled("gold", (1.0, 0.70, 0.30, 1), rough=0.06, metal=1.0),
    black=principled("black", hex_to_linear("#18181A"), rough=0.32, spec=0.5),
    wax=principled("wax", hex_to_linear("#C2402E"), rough=0.42, sss=0.15),
    balm=principled("balm", hex_to_linear("#E9B49C"), rough=0.40, sss=0.15),
)

# ------------------------------------------------------------- 舞台：卓と壁
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.45, -0.03))
table = bpy.context.object; table.name = "table"
table.scale = (3.0, 1.0, 0.06); bpy.ops.object.transform_apply(scale=True)
table.location.y = -0.45 + 0.5 - 0.06          # 奥の縁を y=+0.06 に
setmat(table, principled("table", hex_to_linear(LOOK["table"]), rough=0.85, spec=0.08))

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 1.8, 0.4))
wall = bpy.context.object; wall.name = "wall"
wall.scale = (6, 3, 1); wall.rotation_euler = (math.radians(90), 0, 0)
setmat(wall, principled("wall", hex_to_linear(LOOK["wall"]), rough=0.8, spec=0.2))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.48, 0.46, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

# ------------------------------------------------------------- 被写体（左→右）
parts = []


def put(ob, x, y=0.0, z=0.0, rot=(0, 0, 0)):
    ob.location = (x, y, z); ob.rotation_euler = [math.radians(r) for r in rot]
    parts.append(ob)
    return ob


def group(obs, x, y=0.0, z=0.0, rot=(0, 0, 0)):
    """部品を1つの空の親にまとめて置く（動かすのは親）"""
    e = bpy.data.objects.new("grp", None); scene.collection.objects.link(e)
    for o in obs:
        o.parent = e
        parts.append(o)
    e.location = (x * XS, y, z); e.rotation_euler = [math.radians(r) for r in rot]
    return e


G = {}
XS = 1.0   # 並びの詰め具合
# A スティック（セージ・金の帯・桃の頭）
G["stick"] = group([
    setmat(sq_solid("stick_body", 0.0125, 0.0125, 0.070, rb=0.0025, rt=0.0015), M["sage"]),
    setmat(sq_solid("stick_band", 0.0127, 0.0127, 0.007, rb=0.0006, rt=0.0006, z0=0.070), M["gold"]),
    setmat(sq_solid("stick_balm", 0.0105, 0.0105, 0.012, rb=0.0005, rt=0.004, z0=0.077), M["balm"]),
], -0.212, 0.0)

# B コンパクト（赤のラッカー・縁で立てる・金の継ぎ目）
G["compact"] = group([
    setmat(sq_solid("compact_lo", 0.036, 0.036, 0.0075, n=2.6, rb=0.0068, rt=0.0005, z0=-0.0075), M["lacquer"]),
    setmat(sq_solid("compact_seam", 0.0352, 0.0352, 0.0012, n=2.6, rb=0.0003, rt=0.0003, z0=-0.0006), M["gold"]),
    setmat(sq_solid("compact_hi", 0.036, 0.036, 0.0075, n=2.6, rb=0.0005, rt=0.0068, z0=0.0005), M["lacquer"]),
], -0.132, -0.012, 0.0355, rot=(77, 0, 15))

# C 口紅（桜色の胴・金の帯・斜めに切った赤い芯）
G["lip"] = group([
    setmat(sq_solid("lip_body", 0.0115, 0.0100, 0.058, rb=0.002, rt=0.0008), M["blush"]),
    setmat(sq_solid("lip_band", 0.0098, 0.0084, 0.008, rb=0.0004, rt=0.0004, z0=0.058), M["gold"]),
    setmat(sq_solid("lip_wax", 0.0082, 0.0068, 0.024, rb=0.0003, rt=0.0012, z0=0.066, slope=0.55), M["wax"]),
], -0.090, 0.002)

# D 口紅の蓋（金・横倒しで手前に）
cap = setmat(sq_solid("cap", 0.0122, 0.0106, 0.040, rb=0.0006, rt=0.002), M["gold"])
G["cap"] = group([cap], -0.068, -0.040, 0.0106, rot=(-90, 0, -32))

# E 美容液（クリームの胴・金の襟・金のポンプ）
G["serum"] = group([
    setmat(sq_solid("serum_body", 0.021, 0.0165, 0.112, rb=0.003, rt=0.006, bulge=0.0004), M["cream"]),
    setmat(sq_solid("serum_collar", 0.0115, 0.0100, 0.010, rb=0.0006, rt=0.0006, z0=0.111), M["gold"]),
    setmat(sq_solid("serum_head", 0.0100, 0.0088, 0.016, rb=0.0008, rt=0.004, z0=0.121), M["black"]),
], -0.040, 0.016)

# F 重ねた2つのジャー＋傾けた金の蓋
G["jar"] = group([
    setmat(sq_solid("jar_lo", 0.026, 0.026, 0.026, n=2.8, rb=0.003, rt=0.0012), M["sage"]),
    setmat(sq_solid("jar_hi", 0.024, 0.024, 0.024, n=2.8, rb=0.0012, rt=0.003, z0=0.0262), M["blush"]),
], 0.030, 0.004)
jl = setmat(sq_solid("jar_lid", 0.0245, 0.0245, 0.011, n=2.8, rb=0.0008, rt=0.003), M["gold"])
G["lid"] = group([jl], 0.036, 0.0, 0.0512, rot=(0, -24, 0))

# G 細い筒（赤のラッカー・金の首）
G["tube"] = group([
    setmat(sq_solid("tube_body", 0.0115, 0.0115, 0.118, rb=0.002, rt=0.002), M["lacquer"]),
    setmat(sq_solid("tube_neck", 0.0072, 0.0072, 0.010, rb=0.0004, rt=0.0012, z0=0.118), M["gold"]),
], 0.077, 0.006)

# H 横倒しの黒いスティック（桃の頭を右手前へ）
G["lying"] = group([
    setmat(sq_solid("ly_body", 0.0135, 0.0135, 0.068, rb=0.002, rt=0.0012), M["black"]),
    setmat(sq_solid("ly_band", 0.0137, 0.0137, 0.005, rb=0.0005, rt=0.0005, z0=0.068), M["gold"]),
    setmat(sq_solid("ly_balm", 0.0112, 0.0112, 0.006, rb=0.0004, rt=0.0045, z0=0.073), M["balm"]),
], 0.014, -0.058, 0.0135, rot=(-90, 0, 118))

# I 背の高い噴霧瓶（クリーム・黒の頭）
G["mist"] = group([
    setmat(sq_solid("mist_body", 0.0175, 0.0175, 0.130, rb=0.003, rt=0.003), M["cream"]),
    setmat(sq_solid("mist_collar", 0.0110, 0.0110, 0.006, rb=0.0005, rt=0.0005, z0=0.130), M["gold"]),
    setmat(sq_solid("mist_head", 0.0110, 0.0110, 0.017, rb=0.0006, rt=0.0035, z0=0.136), M["cream"]),
], 0.112, 0.014)

# J 金のコンパクト（縁で立てる）
G["gold"] = group([
    setmat(sq_solid("goldc", 0.031, 0.031, 0.013, n=2.3, rb=0.0064, rt=0.0064, z0=-0.0065), M["gold"]),
], 0.150, -0.004, 0.031, rot=(80, 0, -14))

# K 黒い細身のスティック（金の帯）
G["slim"] = group([
    setmat(sq_solid("slim_body", 0.0120, 0.0120, 0.084, rb=0.002, rt=0.0012), M["black"]),
    setmat(sq_solid("slim_band", 0.0122, 0.0122, 0.006, rb=0.0005, rt=0.0005, z0=0.084), M["gold"]),
    setmat(sq_solid("slim_top", 0.0100, 0.0100, 0.010, rb=0.0005, rt=0.0035, z0=0.090), M["sage"]),
], 0.192, 0.004)



# M 化粧筆（細い黒の軸・金の口金・クリームの穂）＝列に細い縦の線を1本入れる
G["brush"] = group([
    setmat(sq_solid("br_handle", 0.0042, 0.0042, 0.098, rb=0.0012, rt=0.0004, bulge=-0.0008), M["black"]),
    setmat(sq_solid("br_ferrule", 0.0050, 0.0050, 0.024, rb=0.0004, rt=0.0006, z0=0.098, bulge=-0.0004), M["gold"]),
    setmat(sq_solid("br_hair", 0.0060, 0.0060, 0.032, rb=0.0010, rt=0.0058, z0=0.122, bulge=0.0016, n=2.0), principled("hair", hex_to_linear("#B08D78"), rough=0.62, spec=0.3, sss=0.1)),
], 0.004, 0.030, 0.0, rot=(0, 4, 0))


# N 左端：桜色の細いスポイト瓶（黒い吸い口）
G["dropper"] = group([
    setmat(sq_solid("dr_body", 0.0150, 0.0150, 0.072, n=3.6, rb=0.003, rt=0.004), M["blush"]),
    setmat(sq_solid("dr_collar", 0.0085, 0.0085, 0.008, rb=0.0005, rt=0.0008, z0=0.071), M["gold"]),
    setmat(sq_solid("dr_bulb", 0.0068, 0.0068, 0.026, n=2.0, rb=0.002, rt=0.0066, z0=0.079, bulge=0.0008), M["black"]),
], -0.241, 0.012)

# O 左端の手前：低いクリームのジャー（金の蓋）
G["pot"] = group([
    setmat(sq_solid("pot_body", 0.022, 0.022, 0.020, n=3.0, rb=0.003, rt=0.001), M["cream"]),
    setmat(sq_solid("pot_lid", 0.0225, 0.0225, 0.010, n=3.0, rb=0.0008, rt=0.003, z0=0.020), M["gold"]),
], -0.272, -0.034, 0.0, rot=(0, 0, 20))

# P 右端：低い桜色のジャー（金の蓋）と、背の高いセージの瓶
G["pot2"] = group([
    setmat(sq_solid("pot2_body", 0.025, 0.025, 0.024, n=2.6, rb=0.003, rt=0.001), M["blush"]),
    setmat(sq_solid("pot2_lid", 0.0255, 0.0255, 0.008, n=2.6, rb=0.0008, rt=0.0025, z0=0.024), M["sage"]),
], 0.224, -0.026, 0.0, rot=(0, 0, -10))
G["tall"] = group([
    setmat(sq_solid("tall_body", 0.017, 0.013, 0.106, n=4.0, rb=0.003, rt=0.005), M["sage"]),
    setmat(sq_solid("tall_collar", 0.0090, 0.0080, 0.007, rb=0.0005, rt=0.0005, z0=0.105), M["gold"]),
    setmat(sq_solid("tall_cap", 0.0090, 0.0080, 0.020, rb=0.0006, rt=0.003, z0=0.112), M["black"]),
], 0.258, 0.014)

# L 黒い角の箱（左の奥・金の天面）
G["box"] = group([
    setmat(sq_solid("box_body", 0.0135, 0.0105, 0.098, n=6, rb=0.0015, rt=0.0012), M["black"]),
    setmat(sq_solid("box_top", 0.0133, 0.0103, 0.004, n=6, rb=0.0004, rt=0.0012, z0=0.098), M["gold"]),
], -0.178, 0.018, 0.0, rot=(0, 0, 6))

# ------------------------------------------------------------- 光
# キー：奥の高い所の小さめの面光源（影を手前の卓へ落とす）
KEY0 = (0.45, 1.25, 0.62)
area("key", KEY0, 0.10, 240, (1.0, 0.98, 0.95), target=(0.0, 0.0, 0.0))
# 起こし：正面の大きく柔らかい面
area("fill", (-0.4, -2.2, 0.9), 2.4, 55, (0.98, 0.99, 1.0), target=(0.0, 0.0, 0.06))
# 壁：壁だけを起こす（被写体の後ろから）
area("wallwash", (0.0, 0.6, 2.2), 5.0, 230, (0.98, 0.99, 1.0), target=(0.0, 1.8, 0.3))



# 🔴 キーは壁を照らさない（壁に斜めの光の筋が出た＝ライトリンクで壁だけ外す）
_rc = bpy.data.collections.new("key_receivers")
for o in [table] + parts:
    _rc.objects.link(o)
bpy.data.objects["key"].light_linking.receiver_collection = _rc
_wc = bpy.data.collections.new("wash_receivers"); _wc.objects.link(wall)
bpy.data.objects["wallwash"].light_linking.receiver_collection = _wc

# 黒い映り込みの板（金とラッカーに黒い帯を映す・カメラと影には写さない）
for nm, loc, rz in (("flagR", (0.55, -0.9, 0.35), 0), ("flagL", (-0.6, -0.8, 0.5), 0), ("flagC", (0.05, -0.9, 0.62), 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    fl = bpy.context.object; fl.name = nm
    fl.scale = (0.35, 0.6, 1)
    fl.rotation_euler = (Vector((0, 0, 0.05)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    setmat(fl, principled(nm, (0.01, 0.01, 0.01, 1), rough=0.9, spec=0.0))
    fl.visible_camera = False; fl.visible_shadow = False


# 🔴 起こしは鏡面に写さない（金とラッカーに大きなぼけた白が映って柔らかくなる）。代わりに縁の立った白い板を映す
bpy.data.objects["fill"].visible_glossy = False
for nm, loc, sz, st in (("cardL", (-0.24, -1.45, 0.36), (0.16, 0.42), 4.0), ("cardR", (0.26, -1.40, 0.10), (0.12, 0.30), 2.5), ("cardRed", (0.52, -1.35, 0.60), (0.14, 0.50), 3.5)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    cdo = bpy.context.object; cdo.name = nm
    cdo.scale = (sz[0], sz[1], 1)
    cdo.rotation_euler = (Vector((0, 0, 0.06)) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    em = bpy.data.materials.new(nm); em.use_nodes = True
    nt = em.node_tree; nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Strength"].default_value = st
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], o.inputs[0])
    setmat(cdo, em)
    cdo.visible_camera = False; cdo.visible_shadow = False; cdo.visible_diffuse = False

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
cd.sensor_fit = 'HORIZONTAL'
scene.camera = cam


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


HERO_CAM = Vector((-0.012, -1.90, 0.205))
HERO_TGT = Vector((-0.012, 0.0, 0.097))

def orbit(center, radius, height, deg):
    r = math.radians(deg)
    return Vector((center[0] + radius * math.sin(r), center[1] - radius * math.cos(r), height))


LIP = Vector((-0.090, 0.002, 0.074))


def macro(t):
    """ピントは金の帯（手前 6mm）から芯の稜へ送る。距離はカメラの位置から測る（固定値だと動いた先で外れた）"""
    loc = lerp((0.000, -0.290, 0.058), (-0.150, -0.265, 0.102), ease(t))
    tgt = LIP + Vector((0, 0, 0.004))
    return loc, tgt, 135, 2.8, (tgt - loc).length - 0.006 + 0.006 * ease(t)
JAR = Vector((0.030, 0.004, 0.050))
SHOTS = [
    dict(sec=3.0,   # マクロ：口紅の斜めの切り口を横から滑り、ピントを金の帯から芯の稜へ送る
         cam=lambda t: macro(t)),
    dict(sec=3.0,   # 回り込み：ジャーと筆と金の蓋の塊を、左前から正面へ弧で
         cam=lambda t: (orbit(JAR, 0.62, 0.150, -42 + 26 * ease(t)), JAR + Vector((0, 0, 0.020)), 85, 6.3, None)),
    dict(sec=2.5,   # 物の動き：金の蓋が持ち上がったところからジャーの縁へ降りて止まる（カメラはわずかに押し込む）
         cam=lambda t: (lerp((0.060, -0.52, 0.112), (0.050, -0.46, 0.104), ease(t)), JAR + Vector((0.004, 0, 0.006)),
                        100, 5.6, None)),
    dict(sec=3.0,   # 決め：右手前から引きながら入って hero の構図で止まる
         cam=lambda t: (lerp(HERO_CAM + Vector((0.10, 0.40, 0.03)), HERO_CAM, ease_out(min(1.0, t / 0.6))),
                        lerp(HERO_TGT + Vector((0.03, 0, 0.0)), HERO_TGT, ease_out(min(1.0, t / 0.6))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

grps = list(G.values())
base = {g.name: (g.location.copy(), g.rotation_euler.copy()) for g in grps}


def pose(i, t, T):
    """3カット目だけ、金の蓋が上から降りてジャーの縁に載る。ほかのカットは置いたまま"""
    lid = G["lid"]; l0, r0 = base[lid.name]
    lid.location, lid.rotation_euler = l0.copy(), r0.copy()
    if i == 2:
        u = 1 - ease_out(min(1.0, t / 0.8))
        lid.location = l0 + Vector((0.010 * u, 0, 0.034 * u))
        lid.rotation_euler = (r0[0], r0[1] - math.radians(30) * u, r0[2])


key_light = bpy.data.objects.get("key")


def light_path(i, t):
    if key_light:
        key_light.location = KEY0


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
        for g in grps:
            g.keyframe_insert("rotation_euler", frame=f)
            g.keyframe_insert("location", frame=f)
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
    names = {o.name for o in parts} | {g.name for g in grps}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
