# =============================================================
# MIDDLE STUDIES II 003 — DIAL（OBJECT）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
#
# 黒アルマイトの卓上スピーカー。天面に削り出しのアルミのダイヤル1つ。
# 真上やや奥からの絞ったスポット1灯で、天面と稜線だけが起き、正面は闇に沈む。
# 基準＝teenage engineering OB-4 の製品写真（光・素材・構図・色だけを取る。形は自分で起こす）
# 🔴 実寸（m）で組む（#101：dm で組むとボケが出ない）
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(1, 1),
    lens=100,
    fstop=9.0,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=0.0,
)
FPS = 24
# 尺（N_FRAMES）と静止画のフレーム（STILL_FRAME）は、下の「動画」節の SHOTS から決まる


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

# 寸法（m）
BW, BD, BH = 0.220, 0.100, 0.150      # 本体 幅・奥行き・高さ
RC = 0.032                            # 平面の角の半径
DIAL_R, DIAL_H = 0.034, 0.020
DIAL_X = 0.052                        # 天面での位置（右寄り）


# ------------------------------------------------------------- 造形の道具
def bevel_edges(ob, edges_fn, width, segments, clamp=True):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    bm.edges.ensure_lookup_table()
    edges = [e for e in bm.edges if edges_fn(e)]
    bmesh.ops.bevel(bm, geom=edges, offset=width, segments=segments, profile=0.5,
                    affect='EDGES', clamp_overlap=clamp)
    bm.to_mesh(me); bm.free()
    return ob


def smooth(ob, angle=35):
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        ob.data.set_sharp_from_angle(angle=math.radians(angle))
    except Exception:
        pass


def is_vertical(e):
    a, b = e.verts[0].co, e.verts[1].co
    return abs(a.x - b.x) < 1e-6 and abs(a.y - b.y) < 1e-6


def sharp(e, deg=30):
    return e.is_manifold and e.calc_face_angle(0) > math.radians(deg)


def nodes_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    return m, nt, p


def N(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        if k.startswith("in_"):
            key = k[3:] if k[3:] in n.inputs else k[3:].replace("_", " ")
            n.inputs[key].default_value = v
        else:
            setattr(n, k, v)
    return n


def sock(coll, name, typ='RGBA'):
    """🔴 Mix ノードは同名ソケット（Float/Vector/Color）を持つ。名前だけで引くと Float が返る"""
    return next(x for x in coll if x.name == name and x.type == typ)


def math_node(nt, op, a=None, b=None, va=None, vb=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    if a is not None: nt.links.new(a, n.inputs[0])
    elif va is not None: n.inputs[0].default_value = va
    if b is not None: nt.links.new(b, n.inputs[1])
    elif vb is not None: n.inputs[1].default_value = vb
    return n.outputs[0]


# ------------------------------------------------------------- 材質
ANOD = hex_to_linear("#1A202C")        # 黒アルマイト（純黒にしない・わずかに青）


def anodized_body():
    """黒アルマイト。正面だけパンチングの穴（object座標の格子で穴＝bump で凹ませ、穴の中は落とす）"""
    m, nt, p = nodes_mat("anodized")
    p.inputs["Metallic"].default_value = 0.85
    p.inputs["Roughness"].default_value = 0.34
    p.inputs["Coat Weight"].default_value = 0.0
    tc = N(nt, "ShaderNodeTexCoord")
    sep = N(nt, "ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nsep = N(nt, "ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Normal"], nsep.inputs[0])
    PITCH = 0.0042; HOLE = 0.0014
    # 千鳥の格子：行ごとに半ピッチずらす
    row = math_node(nt, "FLOOR", math_node(nt, "DIVIDE", sep.outputs[2], vb=PITCH * 0.866))
    shift = math_node(nt, "MULTIPLY", math_node(nt, "MODULO", row, vb=2.0), vb=0.5 * PITCH)
    gx = math_node(nt, "SUBTRACT",
                   math_node(nt, "FRACT", math_node(nt, "DIVIDE",
                                                    math_node(nt, "ADD", sep.outputs[0], shift), vb=PITCH)), vb=0.5)
    gz = math_node(nt, "SUBTRACT",
                   math_node(nt, "FRACT", math_node(nt, "DIVIDE", sep.outputs[2], vb=PITCH * 0.866)), vb=0.5)
    d = math_node(nt, "SQRT", math_node(nt, "ADD", math_node(nt, "MULTIPLY", gx, gx),
                                        math_node(nt, "MULTIPLY", math_node(nt, "MULTIPLY", gz, vb=0.866),
                                                  math_node(nt, "MULTIPLY", gz, vb=0.866))))
    # d はピッチ単位。穴の半径 HOLE/PITCH、縁を少しだけぼかす
    r = HOLE / PITCH
    sm = N(nt, "ShaderNodeMapRange", in_From_Min=r + 0.03, in_From_Max=r - 0.03)
    nt.links.new(d, sm.inputs["Value"])
    # 正面の窓：|x| < BW/2-RC-0.008, z in [0.022, BH-0.030], normal.y < -0.9
    ax = math_node(nt, "ABSOLUTE", sep.outputs[0])
    in_x = math_node(nt, "LESS_THAN", ax, vb=BW / 2 - RC - 0.010)
    in_z1 = math_node(nt, "GREATER_THAN", sep.outputs[2], vb=0.024)
    in_z2 = math_node(nt, "LESS_THAN", sep.outputs[2], vb=BH - 0.034)
    front = math_node(nt, "LESS_THAN", nsep.outputs[1], vb=-0.9)
    win = math_node(nt, "MULTIPLY", math_node(nt, "MULTIPLY", in_x, in_z1),
                    math_node(nt, "MULTIPLY", in_z2, front))
    holes = math_node(nt, "MULTIPLY", sm.outputs[0], win)
    # 穴の中は黒く・粗く
    mix = N(nt, "ShaderNodeMix", data_type='RGBA')
    sock(mix.inputs, "A").default_value = ANOD
    sock(mix.inputs, "B").default_value = (0.004, 0.004, 0.005, 1)
    nt.links.new(holes, mix.inputs["Factor"])
    nt.links.new(sock(mix.outputs, "Result"), p.inputs["Base Color"])
    rmix = math_node(nt, "ADD", math_node(nt, "MULTIPLY", holes, vb=0.5), vb=0.34)
    nt.links.new(rmix, p.inputs["Roughness"])
    mmix = math_node(nt, "SUBTRACT", va=0.85, b=math_node(nt, "MULTIPLY", holes, vb=0.85))
    nt.links.new(mmix, p.inputs["Metallic"])
    # 細かいアルマイトの梨地（微小な凹凸）＋穴の凹み
    noise = N(nt, "ShaderNodeTexNoise", in_Scale=2600.0, in_Detail=2.0)
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    h = math_node(nt, "SUBTRACT", math_node(nt, "MULTIPLY", noise.outputs["Fac"], vb=0.08), holes)
    bump = N(nt, "ShaderNodeBump", in_Strength=0.35, in_Distance=0.0006)
    nt.links.new(h, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def machined_alu():
    """削り出しのアルミ：側面はローレット（円周方向の細かい溝）、天面は同心円の旋盤目"""
    m, nt, p = nodes_mat("alu")
    p.inputs["Base Color"].default_value = hex_to_linear("#8C9097")
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.28
    p.inputs["Anisotropic"].default_value = 0.6
    tc = N(nt, "ShaderNodeTexCoord")
    sep = N(nt, "ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nsep = N(nt, "ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Normal"], nsep.inputs[0])
    ang = math_node(nt, "ARCTAN2", sep.outputs[1], sep.outputs[0])
    rad = math_node(nt, "SQRT", math_node(nt, "ADD", math_node(nt, "MULTIPLY", sep.outputs[0], sep.outputs[0]),
                                          math_node(nt, "MULTIPLY", sep.outputs[1], sep.outputs[1])))
    knurl = math_node(nt, "SINE", math_node(nt, "MULTIPLY", ang, vb=90.0))
    knurl = math_node(nt, "POWER", math_node(nt, "ABSOLUTE", knurl), vb=0.5)
    lathe = math_node(nt, "SINE", math_node(nt, "MULTIPLY", rad, vb=14000.0))
    side = math_node(nt, "LESS_THAN", math_node(nt, "ABSOLUTE", nsep.outputs[2]), vb=0.5)
    top = math_node(nt, "SUBTRACT", va=1.0, b=side)
    h = math_node(nt, "ADD", math_node(nt, "MULTIPLY", knurl, side),
                  math_node(nt, "MULTIPLY", math_node(nt, "MULTIPLY", lathe, vb=0.15), top))
    bump = N(nt, "ShaderNodeBump", in_Strength=0.5, in_Distance=0.0003)
    nt.links.new(h, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    # 異方性の向き＝円周方向
    tan = N(nt, "ShaderNodeTangent", direction_type='RADIAL', axis='Z')
    nt.links.new(tan.outputs[0], p.inputs["Tangent"])
    return m


def simple(name, color, rough, metal=0.0, spec=0.5):
    m, nt, p = nodes_mat(name)
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Specular IOR Level"].default_value = spec
    return m


def emissive(name, color, strength):
    m, nt, p = nodes_mat(name)
    p.inputs["Base Color"].default_value = (0, 0, 0, 1)
    p.inputs["Emission Color"].default_value = color
    p.inputs["Emission Strength"].default_value = strength
    return m


# ------------------------------------------------------------- 被写体
rig = bpy.data.objects.new("rig", None); scene.collection.objects.link(rig)

# 本体：平面の縦4辺を大きく丸め → 残りの稜線を小さく面取り
bpy.ops.mesh.primitive_cube_add(size=1.0)
body = bpy.context.object; body.name = "body"
me = body.data
for v in me.vertices:
    v.co.x *= BW; v.co.y *= BD; v.co.z = (v.co.z + 0.5) * BH
bevel_edges(body, is_vertical, RC, 12)
bevel_edges(body, lambda e: sharp(e, 20), 0.0014, 3, clamp=True)
smooth(body, 40)
body.data.materials.append(anodized_body())
body.parent = rig

# 天面のダイヤル座（浅い段）
bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=DIAL_R + 0.004, depth=0.002,
                                    location=(DIAL_X, 0.0, BH + 0.001))
seat = bpy.context.object; seat.name = "seat"
bevel_edges(seat, lambda e: sharp(e), 0.0006, 2)
smooth(seat)
seat.data.materials.append(simple("seat", hex_to_linear("#0E1014"), 0.45, 0.6))
seat.parent = rig

# ダイヤル：面取りした円柱（ローレットは材質の bump）
bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=DIAL_R, depth=DIAL_H,
                                    location=(0, 0, 0))
dial = bpy.context.object; dial.name = "dial"
for v in dial.data.vertices:
    v.co.z += DIAL_H / 2
bevel_edges(dial, lambda e: sharp(e), 0.0016, 4)
smooth(dial)
dial.data.materials.append(machined_alu())
dial.location = (DIAL_X, 0.0, BH + 0.002)
dial.parent = rig

# ダイヤルの指標（天面の細い溝＝暗い線）
bpy.ops.mesh.primitive_cube_add(size=1.0)
mark = bpy.context.object; mark.name = "mark"
for v in mark.data.vertices:
    v.co.x *= 0.0010; v.co.y *= 0.012; v.co.z *= 0.0006
    v.co.y += DIAL_R - 0.012; v.co.z += DIAL_H + 0.0001
mark.data.materials.append(simple("mark", (0.01, 0.01, 0.012, 1), 0.6))
mark.parent = dial

# 左の2つのボタン（天面にほぼ面一）
buttons = []
for i, bx in enumerate((-0.074, -0.044)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.0085, depth=0.003, location=(bx, 0.004, BH + 0.0005))
    b = bpy.context.object; b.name = f"btn{i}"
    bevel_edges(b, lambda e: sharp(e), 0.0009, 3)
    smooth(b)
    b.data.materials.append(simple(f"btn{i}", hex_to_linear("#15171C"), 0.28, 0.8))
    b.parent = rig
    buttons.append(b)

# 状態表示のアンバー1点（唯一の差し色）
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.0011, location=(-0.020, 0.010, BH))
led = bpy.context.object; led.name = "led"
smooth(led)
led.data.materials.append(emissive("led", hex_to_linear("#FF8A2A"), 60.0))
led.parent = rig

# 足（床から2mm浮かせる＝底の影の縁をつくる）
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ft = bpy.context.object; ft.name = f"foot{sx}"
    for v in ft.data.vertices:
        v.co.x = v.co.x * 0.06 + sx * 0.05; v.co.y *= 0.05; v.co.z = (v.co.z + 0.5) * 0.002
    ft.data.materials.append(simple("foot", (0.01, 0.01, 0.01, 1), 0.8))
    ft.parent = rig
body.location.z = 0.002  # 本体は足の上
for o in (seat, led) + tuple(buttons):
    o.location.z += 0.002
dial.location.z += 0.002

parts = [rig, body, seat, dial, mark, led] + buttons

# ------------------------------------------------------------- 舞台：無限の床（奥は闇へ）
bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 0, 0))
floor = bpy.context.object; floor.name = "floor"
fm, fnt, fp = nodes_mat("floor")
fmott = N(fnt, "ShaderNodeTexNoise", in_Scale=30.0, in_Detail=6.0, in_Roughness=0.62)
fstretch = N(fnt, "ShaderNodeMapRange", in_From_Min=0.38, in_From_Max=0.62)
fnt.links.new(fmott.outputs["Fac"], fstretch.inputs["Value"])
framp = N(fnt, "ShaderNodeMix", data_type='RGBA')
sock(framp.inputs, "A").default_value = hex_to_linear("#0A0E17")
sock(framp.inputs, "B").default_value = hex_to_linear("#3A4A66")
fnt.links.new(fstretch.outputs["Result"], framp.inputs["Factor"])
# 細かい粒（数mm）は bump では暗い床に出ない＝色で乗せる
fgrain = N(fnt, "ShaderNodeTexNoise", in_Scale=260.0, in_Detail=2.0)
fgm = N(fnt, "ShaderNodeMix", data_type='RGBA', blend_type='MULTIPLY')
fgm.inputs["Factor"].default_value = 0.55
fgs = N(fnt, "ShaderNodeMapRange", in_From_Min=0.3, in_From_Max=0.7, in_To_Min=0.6, in_To_Max=1.4)
fnt.links.new(fgrain.outputs["Fac"], fgs.inputs["Value"])
fnt.links.new(sock(framp.outputs, "Result"), sock(fgm.inputs, "A"))
fnt.links.new(fgs.outputs["Result"], sock(fgm.inputs, "B"))
fnt.links.new(sock(fgm.outputs, "Result"), fp.inputs["Base Color"])
fp.inputs["Roughness"].default_value = 0.62
fp.inputs["Specular IOR Level"].default_value = 0.35
fnoise = N(fnt, "ShaderNodeTexNoise", in_Scale=400.0, in_Detail=4.0)
fb = N(fnt, "ShaderNodeBump", in_Strength=0.35, in_Distance=0.0010)
fnt.links.new(fnoise.outputs["Fac"], fb.inputs["Height"])
fnt.links.new(fb.outputs["Normal"], fp.inputs["Normal"])
floor.data.materials.append(fm)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.016, 0.028, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

# ------------------------------------------------------------- 光
def spot(name, loc, target, energy, angle, blend, radius, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'SPOT')
    ld.energy, ld.color = energy, color
    ld.spot_size, ld.spot_blend = math.radians(angle), blend
    ld.shadow_soft_size = radius
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.08), size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color = energy, color
    if size_y:
        ld.shape = 'RECTANGLE'; ld.size, ld.size_y = size, size_y
    else:
        ld.shape = 'DISK'; ld.size = size
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


KEY_COL = (0.70, 0.82, 1.0)
key = spot("key", (0.0, 0.85, 1.15), (0.0, 0.12, 0.0), 130, 20, 1.0, 0.20, KEY_COL)
# 稜線を拾うための細長い面光源（奥上。カメラには写さない）
rim = area("rim", (0.0, 0.55, 0.55), 0.9, 6.0, KEY_COL, target=(0, 0, 0.12), size_y=0.06)
rim.data.energy = 18.0
rim.visible_camera = False
# ごく弱い正面の起こし（正面が真っ黒の穴にならない程度）
fill = area("fill", (0.0, -1.4, 0.5), 1.2, 3.0, (0.8, 0.86, 1.0), target=(0, 0, 0.07))
fill.visible_camera = False
# 底の面取りに細い線を1本出すための、床すれすれの細長い光（本体だけに当てる）
kick = area("kick", (0.0, -0.9, 0.02), 1.0, 0.7, KEY_COL, target=(0, 0, 0.004), size_y=0.02)
kick.visible_camera = False
# 天面の手前の面取りに1本の線を映す細い光（面取りでの反射がここへ返る）
strip = area("strip", (0.0, -0.22, 1.15), 0.9, float(os.environ.get("II_STRIP", "10")), KEY_COL, target=(0, -0.05, 0.15), size_y=0.035)
strip.visible_camera = False
# 奥の床に濃紺の空気を乗せる大きく弱い光（床だけに当てる。基準の闇には色がある）
wash = area("wash", (0.0, 2.2, 2.6), 4.0, float(os.environ.get("II_WASH", "8")), (0.55, 0.68, 1.0), target=(0, 1.2, 0))
wash.visible_camera = False

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.lens = LOOK["lens"]
cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36
AIM = Vector((0.0, 0.0, 0.105))
cam.location = Vector((0.0, -1.18, 0.66))
cam.rotation_euler = (AIM - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True
cd.dof.focus_object = None
cd.dof.focus_distance = (Vector((0, -BD / 2, 0.11)) - cam.location).length
cd.dof.aperture_fstop = LOOK["fstop"]
scene.camera = cam

# ------------------------------------------------------------- 動画＝プロダクトフィルム（2026-09-24 作り直し）
# 旧版は8秒のターンテーブル1周のループ。hero・ルック・造形はそのままに、カメラを4カットに割り直す。
# 物の動き：台はわずかに振れて正面へ戻り、つまみは逆向きに回って指標が hero の位置で止まる（SETTLE で止まる）
HERO_CAM, HERO_AIM = cam.location.copy(), AIM.copy()
HERO_FOCUS = Vector((0, -BD / 2, 0.11))
DIAL_TOP = DIAL_H + 0.004 + BH          # つまみの天面の高さ（足の2mm込み）


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


def dial_at(T, dz=0.0):
    """全体の進み T でのつまみの中心（天面の高さ＋dz）。台が振れるのでカメラはこれを追う"""
    r = rig_angle(T)
    return Vector((DIAL_X * math.cos(r), DIAL_X * math.sin(r), DIAL_TOP + dz))


# 各カット：cam(t, T)→(カメラ位置, 注視点, レンズmm, f値, ピント距離 or None=注視点まで / "hero")
SHOTS = [
    dict(sec=3.0, kind="押し込み",   # 引き：右前の高みから、闇の中の光だまりと本体へまっすぐ寄る
         cam=lambda t, T: (lerp(orbit(AIM, 1.55, 0.78, 38), orbit(AIM, 1.20, 0.62, 38), ease(t)),
                           AIM + Vector((0, 0.02, -0.02)), 85, 11.0, None)),
    dict(sec=3.0, kind="マクロ",     # 寄り：回るつまみを左前の低めからなめ、ピントを天面の旋盤目からローレットの縁へ送る
         cam=lambda t, T: (dial_at(T) + lerp((-0.17, -0.30, 0.075), (-0.12, -0.32, 0.06), ease(t)),
                           dial_at(T, -0.010), 135, 3.5,
                           (1 - ease(t)) * (dial_at(T) - dial_at(T) - lerp((-0.17, -0.30, 0.075), (-0.12, -0.32, 0.06), ease(t))).length
                           + ease(t) * (dial_at(T, -0.010) + Vector((0, -DIAL_R, 0)) - dial_at(T) - lerp((-0.17, -0.30, 0.075), (-0.12, -0.32, 0.06), ease(t))).length)),
    dict(sec=2.5, kind="光の走り",   # 中：左の側面に回って止め、キーを左から中央へ送る＝光だまりと稜線の光が横へ走る
         cam=lambda t, T: (lerp(orbit(AIM, 0.95, 0.56, -58), orbit(AIM, 0.95, 0.52, -52), ease(t)),
                           AIM + Vector((0, 0, 0.0)), 85, 9.0, None)),
    dict(sec=3.0, kind="決め",       # 右上から寄りながら入り、hero の構図で止まる
         cam=lambda t, T: (lerp(HERO_CAM + Vector((0.16, 0.05, 0.10)), HERO_CAM, ease_out(min(1.0, t / 0.6))),
                           lerp(HERO_AIM + Vector((0.02, 0, 0.0)), HERO_AIM, ease_out(min(1.0, t / 0.6))),
                           LOOK["lens"], LOOK["fstop"], "hero")),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
SECONDS = N_FRAMES / FPS
STILL_FRAME = N_FRAMES        # 最後のフレーム＝決めのカットが止まったところ＝hero
SETTLE = (shot_start[-1] + round(SHOTS[-1]["frames"] * 0.6) - 1) / (N_FRAMES - 1)   # この T で動きが hero の位相に戻って止まる


def rig_angle(T):
    return math.radians(-24) * (1 - ease(min(1.0, T / SETTLE)))


def pose(T):
    """台は -24°→0°、つまみは逆向きに 3/4 周戻って指標が hero の位置で止まる"""
    rig.rotation_euler = (0, 0, rig_angle(T))
    dial.rotation_euler = (0, 0, math.radians(270) * (1 - ease(min(1.0, T / SETTLE))))


KEY_LOC, KEY_TGT = key.location.copy(), Vector((0.0, 0.12, 0.0))


def light_path(i, t):
    """光の走り：3カット目だけキーを左から元の位置へ送る（向きは平行移動＝光だまりが床と本体を横へ滑る）"""
    d = Vector((-0.75 * (1 - ease(t)), 0, 0)) if i == 2 else Vector((0, 0, 0))
    key.location = KEY_LOC + d
    key.rotation_euler = (KEY_TGT + d - key.location).to_track_quat('-Z', 'Y').to_euler()


for i, sh in enumerate(SHOTS):
    for k in range(sh["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh["frames"] - 1)
        T = (f - 1) / max(1, N_FRAMES - 1)
        pose(T)
        loc, tgt, lens, fstop, focus = sh["cam"](t, T)
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cd.lens = lens
        cd.dof.aperture_fstop = fstop
        if focus == "hero":
            focus = (HERO_FOCUS - Vector(loc)).length
        cd.dof.focus_distance = focus if focus else (Vector(tgt) - Vector(loc)).length
        for path in ("location", "rotation_euler"):
            cam.keyframe_insert(path, frame=f)
        cd.keyframe_insert("lens", frame=f)
        cd.dof.keyframe_insert("aperture_fstop", frame=f)
        cd.dof.keyframe_insert("focus_distance", frame=f)
        for o in (rig, dial):
            o.keyframe_insert("rotation_euler", frame=f)
        light_path(i, t)
        key.keyframe_insert("location", frame=f)
        key.keyframe_insert("rotation_euler", frame=f)

# ------------------------------------------------------------- ライトリンク（#56：起こしと縁は床に当てない）
lit = bpy.data.collections.new("lit_obj")
scene.collection.children.link(lit)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not floor:
        lit.objects.link(o)
rim.light_linking.receiver_collection = lit
fill.light_linking.receiver_collection = lit
kick.light_linking.receiver_collection = lit
strip.light_linking.receiver_collection = lit
flo = bpy.data.collections.new("floor_only")
scene.collection.children.link(flo)
flo.objects.link(floor)
wash.light_linking.receiver_collection = flo

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


def film_grain(path, sigma=1.2 / 255, seed=3):
    """写真の粒（センサーノイズ）を後から乗せる。床の肌理をレンダー内で細かくするとモアレになる（round 23）"""
    import numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, sigma, (w * h, 1)).astype(np.float32)   # 輝度の粒（色は揺らさない）
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

if "glb" in modes:
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {o.name for o in bpy.data.objects if o.name.startswith("foot")}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = body
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
