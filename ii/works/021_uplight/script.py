# =============================================================
# MIDDLE STUDIES II 021 — UPLIGHT（仰ぐ灯）
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots
# 基準：FLOS「Luminator」ストーリーの主画像（暗い青緑の部屋に黄色のアッパーライト3本）
#   取るもの＝光（灯具の上向きの光が壁に扇を描く・四隅は闇）／素材（艶の黄の焼付け塗装・艶消しの黒）／
#            構図（2:1・手前の1本を中央に大きく切り、奥の2本を左右に）／色（青緑8割・黄数%・黒）
#   写さないもの＝三脚の細い脚・白い笠の形。こちらは「重い円盤の台座＋黒い軸＋関節＋黄の管＋浅い反射皿」
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}
OFF = set(os.environ.get("II_OFF", "").split(","))

LOOK = dict(
    aspect=(2, 1),
    lens=40,
    fstop=64.0,          # 製品写真の全面ピント（基準も手前と奥が両方合っている）
    view="Standard",
    look="Medium High Contrast",
    exposure=-0.4,
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


# ------------------------------------------------------------- 造形の道具
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


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, spec=0.5, coat_rough=0.05):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = coat_rough
    p.inputs["Specular IOR Level"].default_value = spec
    return m


def emission(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = color
    e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def setmat(ob, m):
    ob.data.materials.clear(); ob.data.materials.append(m)


def lathe(name, prof, seg=96):
    """prof: [(r, z), …] を z 軸まわりに回す（開いた断面）"""
    bm = bmesh.new()
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for (r, z) in prof])
    for i in range(seg):
        A, B = rings[i], rings[(i + 1) % seg]
        for j in range(len(prof) - 1):
            bm.faces.new((A[j], B[j], B[j + 1], A[j + 1]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


# ------------------------------------------------------------- 材質
YELLOW = principled("enamel_yellow", hex_to_linear("#F5D000"), rough=0.32, coat=0.2, coat_rough=0.14, spec=0.35)
BLACK = principled("black_satin", (0.012, 0.013, 0.014, 1), rough=0.38, spec=0.4)
DISH_IN = principled("dish_in", (0.86, 0.86, 0.84, 1), rough=0.30)
RUBBER = principled("cable", (0.008, 0.008, 0.009, 1), rough=0.45, spec=0.35)
BULB = principled("bulb", (0.95, 0.94, 0.92, 1), rough=0.45)
_bp = BULB.node_tree.nodes["Principled BSDF"]
_bp.inputs["Emission Color"].default_value = (1.0, 0.82, 0.58, 1)
_bp.inputs["Emission Strength"].default_value = 14.0

# ------------------------------------------------------------- 舞台：暗い部屋（床＋奥の壁）
WALL_Y = 6.5
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
floor = bpy.context.object; floor.name = "floor"
floor.scale = (24, 16, 1); floor.location = (0, WALL_Y - 8, 0)
FLOORM = principled("floor", hex_to_linear("#2A4850"), rough=0.38, spec=0.35)
setmat(floor, FLOORM)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, WALL_Y, 4))
wall = bpy.context.object; wall.name = "wall"
wall.scale = (24, 8, 1); wall.rotation_euler = (math.radians(90), 0, 0)
setmat(wall, principled("wall", hex_to_linear("#8CB2BE"), rough=0.85, spec=0.2))



def falloff(mat, axis, a0, a1, v0, v1):
    """Object 座標の axis（0=x,1=y,2=z）で a0→a1 の間に明度を v0→v1 へ落とす（四隅の闇は光でなく地で作る）"""
    nt = mat.node_tree; p = nt.nodes["Principled BSDF"]
    base = tuple(p.inputs["Base Color"].default_value)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sx.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.clamp = True; mr.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(sx.outputs[axis], mr.inputs["Value"])
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = a0, a1
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = v0, v1
    mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = 'SCALE'
    mul.inputs[0].default_value = base[:3]
    nt.links.new(mr.outputs["Result"], mul.inputs["Scale"])
    nt.links.new(mul.outputs[0], p.inputs["Base Color"])


# 壁：上へ行くほど闇へ（壁の Object 座標は回転前の平面＝ y が高さ方向・-0.5 が床・z=4+8y）
falloff(wall.data.materials[0], 1, -0.35, -0.16, 1.0, 0.05)   # z=1.2m→2.7m
# 壁の上の闇を「灰の黒」でなく深い青緑に：落ちた分だけ弱い自発光で底上げ（基準の闇は 7,23,31＝青に寄った黒）
_wn = wall.data.materials[0].node_tree
_wmr = [n for n in _wn.nodes if n.type == 'MAP_RANGE'][0]
_inv = _wn.nodes.new("ShaderNodeMath"); _inv.operation = 'MULTIPLY_ADD'
_inv.inputs[1].default_value = -0.07; _inv.inputs[2].default_value = 0.07   # (1 - v) * 0.07
_wn.links.new(_wmr.outputs["Result"], _inv.inputs[0])
_wp = _wn.nodes["Principled BSDF"]
_wp.inputs["Emission Color"].default_value = hex_to_linear("#0E4A63")
_wn.links.new(_inv.outputs[0], _wp.inputs["Emission Strength"])
# 床：壁際から手前へ闇へ（床の Object y：+0.5 が壁際）
falloff(FLOORM, 1, 0.49, 0.04, 1.0, 0.06)   # 壁際→壁から5m手前
# 床の艶も壁際だけ（手前まで艶があると、浅い角度のフレネルで壁を映して手前が灰に光る＝#114）
_nt = FLOORM.node_tree
_mr = [n for n in _nt.nodes if n.type == 'MAP_RANGE'][0]
_m2 = _nt.nodes.new("ShaderNodeMapRange"); _m2.clamp = True
_nt.links.new(_mr.inputs["Value"].links[0].from_socket, _m2.inputs["Value"])
_m2.interpolation_type = 'SMOOTHERSTEP'   # 線形で切ると艶の終わりが床に横一線の段になった
_m2.inputs["From Min"].default_value, _m2.inputs["From Max"].default_value = 0.49, 0.12
_m2.inputs["To Min"].default_value, _m2.inputs["To Max"].default_value = 0.35, 0.0
_nt.links.new(_m2.outputs["Result"], _nt.nodes["Principled BSDF"].inputs["Specular IOR Level"])

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hex_to_linear("#0A3446")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.10


# ------------------------------------------------------------- 灯具（自作）
# 円盤の台座 → 黒い軸 → 関節（ここで傾く）→ 黄の管 → 浅い反射皿＋乳白の球
BASE_R, BASE_H = 0.165, 0.028
STEM_L, STEM_R = 0.78, 0.0085
TUBE_R = 0.021
DISH_R = 0.088


def make_lamp(tag, x, y, tube_len, tilt=0.0, yaw=0.0, scale=1.0, stem_len=STEM_L):
    objs = []
    root = bpy.data.objects.new(tag + "_root", None); scene.collection.objects.link(root)
    root.location = (x, y, 0); root.rotation_euler = (0, 0, math.radians(yaw)); root.scale = (scale,) * 3
    # 台座：縁を面取りした鋳物の円盤
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=BASE_R, depth=BASE_H, location=(0, 0, BASE_H / 2))
    base = bpy.context.object; base.name = tag + "_base"
    bevel_obj(base, 0.006, segments=4); setmat(base, BLACK)
    # 軸の付け根のボス
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.03, depth=0.03, location=(0, 0, BASE_H + 0.012))
    boss = bpy.context.object; boss.name = tag + "_boss"
    bevel_obj(boss, 0.004, segments=3); setmat(boss, BLACK)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=STEM_R, depth=stem_len, location=(0, 0, BASE_H + stem_len / 2))
    stem = bpy.context.object; stem.name = tag + "_stem"
    bevel_obj(stem, 0.002, segments=2); setmat(stem, BLACK)
    for o in (base, boss, stem):
        o.parent = root; objs.append(o)
    # 関節：黒い球＋管の受け
    kz = BASE_H + stem_len
    knuckle = bpy.data.objects.new(tag + "_pivot", None); scene.collection.objects.link(knuckle)
    knuckle.parent = root; knuckle.location = (0, 0, kz)
    knuckle.rotation_euler = (0, math.radians(tilt), 0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.017, location=(0, 0, 0))
    ball = bpy.context.object; ball.name = tag + "_ball"; setmat(ball, BLACK)
    for p in ball.data.polygons:
        p.use_smooth = True
    ball.parent = root; ball.location = (0, 0, kz); objs.append(ball)
    # 受け：球から管へ細く絞って広がる旋盤の段（平らな筒だと電池に見えた）
    _r1 = TUBE_R + 0.0022
    _prof = [(0.0, 0.010), (0.0105, 0.010), (0.0112, 0.0125), (0.0118, 0.020)]
    _prof += [(0.0118 + (_r1 - 0.0118) * (1 - math.cos(math.pi / 2 * i / 10)), 0.020 + 0.022 * (i / 10)) for i in range(1, 11)]
    _prof += [(_r1, 0.050), (_r1 - 0.0012, 0.0525), (TUBE_R * 0.98, 0.0532)]
    collar = lathe(tag + "_collar", _prof, seg=96); setmat(collar, BLACK)
    # 黄の管
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=TUBE_R, depth=tube_len, location=(0, 0, 0.045 + tube_len / 2))
    tube = bpy.context.object; tube.name = tag + "_tube"
    bevel_obj(tube, 0.005, segments=4); setmat(tube, YELLOW)
    # 反射皿：外は黄・内は白（薄い殻）
    hz = 0.045 + tube_len
    prof_out = [(TUBE_R * 0.9, hz - 0.004)] + [
        (TUBE_R * 0.9 + (DISH_R - TUBE_R * 0.9) * (i / 16) ** 0.75, hz + 0.055 * (i / 16) ** 1.6) for i in range(1, 17)]
    dish = lathe(tag + "_dish", prof_out + [(DISH_R + 0.0015, prof_out[-1][1] + 0.002)])
    setmat(dish, YELLOW)
    prof_in = [(0.0, hz + 0.0035)] + [
        (TUBE_R * 0.9 + (DISH_R - 0.003 - TUBE_R * 0.9) * (i / 16) ** 0.75, hz + 0.0035 + 0.053 * (i / 16) ** 1.6)
        for i in range(0, 17)]
    dish_in = lathe(tag + "_dishin", prof_in)
    setmat(dish_in, DISH_IN)
    for p in dish_in.data.polygons:
        p.flip()
    # 乳白の玉：皿の縁から半分以上のぞかせる（下から見上げても「灯っている」と読める）
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.04, location=(0, 0, hz + 0.05))
    bulb = bpy.context.object; bulb.name = tag + "_bulb"; setmat(bulb, BULB)
    for p in bulb.data.polygons:
        p.use_smooth = True
    for o in (collar, tube, dish, dish_in, bulb):
        o.parent = knuckle
        objs.append(o)
    # dish/dish_in は lathe でワールド原点に作った＝親の座標系へそのまま（関節が原点）
    # 灯：乳白の球の中の点光源（上向きの壁の扇は別の灯で描く）
    ld = bpy.data.lights.new(tag + "_glow", 'POINT'); ld.energy = 22; ld.color = (1.0, 0.9, 0.78)
    ld.shadow_soft_size = 0.03
    L = bpy.data.objects.new(tag + "_glow", ld); scene.collection.objects.link(L)
    L.parent = knuckle; L.location = (0, 0, hz + 0.05)
    return root, knuckle, objs


lamps = {}
# 手前の1本（中央・大きく切る）／奥左（直立）／奥右（傾く）
lamps["C"] = make_lamp("C", 0.05, -2.62, 1.0, tilt=0.0, yaw=0, scale=1.5, stem_len=0.50)
lamps["L"] = make_lamp("L", -1.75, 2.2, 1.0, tilt=0.0, yaw=20)
lamps["R"] = make_lamp("R", 1.55, 2.0, 1.0, tilt=-17.0, yaw=-8)


# コード：台座から床を這う黒い線
def cable(tag, pts, r=0.0042):
    cu = bpy.data.curves.new(tag + "_cable", 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], r, 1)
    sp.order_u = 4; sp.use_endpoint_u = True
    cu.bevel_depth = r; cu.bevel_resolution = 4; cu.resolution_u = 24
    ob = bpy.data.objects.new(tag + "_cable", cu); scene.collection.objects.link(ob)
    ob.data.materials.append(RUBBER)
    return ob


cables = [
    cable("C", [(0.05 + 0.24, -2.62, 0), (0.5, -2.7, 0), (0.7, -2.95, 0), (0.85, -3.3, 0), (0.95, -3.9, 0)]),
    cable("L", [(-1.75 + 0.15, 2.25, 0), (-1.45, 2.05, 0), (-1.6, 1.6, 0), (-2.3, 1.35, 0), (-3.2, 1.5, 0), (-4.2, 1.3, 0)]),
    cable("R", [(1.55 + 0.15, 2.05, 0), (2.3, 2.15, 0), (2.7, 1.95, 0), (3.1, 2.2, 0), (3.6, 2.1, 0)]),
]
parts = [o for k in lamps for o in lamps[k][2]] + cables

# ------------------------------------------------------------- 光
# 壁の扇：灯具ごとに壁際の床から上へ向けたスポット（壁と床だけに当てる）
wash_rc = bpy.data.collections.new("wash_receivers")
wash_rc.objects.link(wall)


def spot(name, loc, target, energy, cone, blend, color, radius=0.15):
    ld = bpy.data.lights.new(name, 'SPOT')
    ld.energy, ld.color = energy, color
    ld.spot_size = math.radians(cone); ld.spot_blend = blend; ld.shadow_soft_size = radius
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


WASH_COL = (0.80, 0.92, 1.0)
washes = [
    spot("washL", (-3.4, WALL_Y - 1.6, 0.2), (-1.3, WALL_Y, 1.5), 560, 80, 0.75, WASH_COL, 0.6),
    spot("washC", (0.1, WALL_Y - 1.4, 0.4), (0.0, WALL_Y, 0.6), 35, 125, 1.0, WASH_COL, 0.9),
    spot("washR", (0.8, WALL_Y - 1.6, 0.2), (2.9, WALL_Y, 1.6), 560, 80, 0.75, WASH_COL, 0.6),
]
for w in washes:
    w.light_linking.receiver_collection = wash_rc
floor_rc = bpy.data.collections.new("floor_receivers"); floor_rc.objects.link(floor)


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.8), size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color = energy, color
    if size_y:
        ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = size_y
    else:
        ld.size = size
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


# 灯具の照り：壁の明るさを返す縦長の面（灯具だけに当てる）
lamp_rc = bpy.data.collections.new("lamp_receivers")
for o in parts:
    lamp_rc.objects.link(o)
rimL = area("rimL", (-1.2, 0.0, 1.2), 0.6, 8, WASH_COL, target=(0.05, -2.62, 1.0), size_y=2.4)
fill = area("fill", (-1.2, -4.5, 1.4), 2.5, 6, (0.75, 0.9, 1.0), target=(0.05, -2.62, 1.0))
key = area("key", (2.4, -4.0, 1.8), 1.2, 110, (1.0, 0.97, 0.92), target=(0.0, 1.0, 1.0), size_y=2.0)
for L in (rimL, fill, key):
    L.light_linking.receiver_collection = lamp_rc
# 奥の2本だけを起こす正面右のキー（手前の1本は距離が 1/2.5 なので、同じ灯では奥が沈む）
far_rc = bpy.data.collections.new("far_receivers")
for k in ("L", "R"):
    for o in lamps[k][2]:
        far_rc.objects.link(o)
key2 = area("key2", (4.2, 0.2, 1.8), 0.8, 300, (1.0, 0.97, 0.92), target=(0.0, 2.1, 1.0), size_y=1.6)
key2.light_linking.receiver_collection = far_rc
fill.visible_glossy = False

band = area("band", (0.3, WALL_Y + 0.4, 0.9), 10.0, 1500, (0.95, 0.98, 1.0), target=(0.3, WALL_Y - 3.0, 0.0), size_y=0.3)
band.light_linking.receiver_collection = floor_rc
band.visible_glossy = False
# 帯の灯は壁の裏に置き、影を落とすのは灯具だけ（壁の手前に置くと、その後ろの壁際数cmが面光源の裏で暗い線になった）
_bk = bpy.data.collections.new("band_blockers")
for o in parts:
    _bk.objects.link(o)
band.light_linking.blocker_collection = _bk   # 鏡面に出すと手前の床全体が無彩の灰に光る
band.data.spread = math.radians(180)

# 壁の足元：床すれすれの細長い面から壁の下 1m を起こす（扇が宙に浮かず床際から立ち上がるように）
foot = area("foot", (0.0, WALL_Y - 0.5, 0.03), 12.0, 60, WASH_COL, target=(0.0, WALL_Y, 0.7), size_y=0.2)
foot.light_linking.receiver_collection = wash_rc

for nm in OFF:
    if nm and nm in bpy.data.objects:
        bpy.data.objects[nm].hide_render = True

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


HERO_CAM = Vector((0.0, -3.6, 0.92))
HERO_TGT = Vector((0.0, 2.0, 0.95))
HERO_FOCUS = (Vector((0.05, -2.62, 0.95)) - HERO_CAM).length

# 手前の1本の関節（×1.5・軸 0.50）：マクロで受けの段から黄の管へなめ上げる
C_KZ = 1.5 * (BASE_H + 0.50)
C_XY = Vector((0.05, -2.62, 0.0))
WASHL_TGT = Vector((-1.3, WALL_Y, 1.5))


def macro_cam(t):
    loc = Vector((-0.30, -3.12, C_KZ - 0.06)).lerp(Vector((-0.26, -3.14, C_KZ + 0.16)), ease(t))
    tgt = Vector((C_XY.x, C_XY.y, C_KZ - 0.02)).lerp(Vector((C_XY.x, C_XY.y, C_KZ + 0.20)), ease(t))
    focus = (tgt - loc).length - 1.5 * TUBE_R          # 管の表面まで（芯でなく手前の面）
    return loc, tgt, 120, 2.8, focus


SHOTS = [
    dict(sec=3.0,   # 光の走り：左の灯と壁。床際から扇が立ち上がって壁を登る（カメラはわずかに寄る）
         cam=lambda t: (lerp((-0.35, -1.6, 0.95), (-0.6, -1.1, 0.95), ease(t)), Vector((-1.9, 2.2, 1.12)), 35, 64.0, None)),
    dict(sec=2.75,  # マクロ：受けの段から黄の管へ
         cam=macro_cam),
    dict(sec=3.0,   # 物の動き：見上げの寄り。右の灯の頭が関節で傾いて画面を横切る（直立→17°）
         cam=lambda t: (lerp((0.85, 0.15, 0.6), (0.75, 0.3, 0.62), ease(t)), Vector((1.45, 2.0, 1.55)), 45, 64.0, None)),
    dict(sec=3.0,   # 決め：左奥から回り込みながら入って hero で止まる
         cam=lambda t: (lerp(HERO_CAM + Vector((-0.45, -0.35, 0.10)), HERO_CAM, ease_out(min(1.0, t / 0.6))), HERO_TGT,
                        LOOK["lens"], LOOK["fstop"], HERO_FOCUS)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

pivots = [lamps[k][1] for k in lamps]


def pose(i, t, T):
    tilt = -17.0 * ease(min(1.0, t / 0.85)) if i == 2 else -17.0
    lamps["R"][1].rotation_euler = (0, math.radians(tilt), 0)


def light_path(i, t):
    """1カット目だけ：左の扇の灯を床際から上へ振り上げ、強さも上げる（壁を光が登る）"""
    L = bpy.data.objects["washL"]
    if i == 0:
        k = ease(t)
        tgt = Vector((-1.3, WALL_Y, -0.6 + 2.1 * k))
        L.data.energy = 560 * (0.25 + 0.75 * k)
    else:
        tgt = WASHL_TGT
        L.data.energy = 560
    L.rotation_euler = (tgt - L.location).to_track_quat('-Z', 'Y').to_euler()


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
        for o in pivots:
            o.keyframe_insert("rotation_euler", frame=f)
        light_path(i, t)
        bpy.data.objects["washL"].keyframe_insert("rotation_euler", frame=f)
        bpy.data.objects["washL"].data.keyframe_insert("energy", frame=f)

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

# 灯の芯だけに薄いにじみ（基準の笠は周りに光が滲む）。閾値は壁（≈1）より十分上
_cg = bpy.data.node_groups.new("comp", "CompositorNodeTree"); scene.compositing_node_group = _cg
_cg.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
_rl = _cg.nodes.new("CompositorNodeRLayers"); _gl = _cg.nodes.new("CompositorNodeGlare")
_go = _cg.nodes.new("NodeGroupOutput")
_gl.inputs["Type"].default_value = 'Bloom'
_gl.inputs["Threshold"].default_value = 3.0
_gl.inputs["Strength"].default_value = 0.8
_gl.inputs["Size"].default_value = 0.5
_cg.links.new(_rl.outputs["Image"], _gl.inputs["Image"])
_cg.links.new(_gl.outputs["Image"], _go.inputs[0])


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
    names = {o.name for o in parts} | {o.name for o in pivots} | {lamps[k][0].name for k in lamps}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
