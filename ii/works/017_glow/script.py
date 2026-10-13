# =============================================================
# MIDDLE STUDIES II 017 — GLOW（香水瓶）
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots
# 基準：Tais Sirote の青いガラスの香水瓶の製品写真（ii/refs/017.png・非公開）
#   取ったもの：右上奥の大きな面光源が地を起こし、瓶は後ろから透かされて液が光る／厚いガラス＋黒いキャップ＋濡れた黒い台
#   造形は自分で起こす：平面が角の丸い楕円の厚底瓶・まっすぐの円柱キャップ・銀の口金・中は吸い上げ管だけ。
#   瓶は黒いアクリルの段に片足を掛けて左へ傾く（実寸・1単位＝1m）
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

LOOK = dict(
    aspect=(4, 5),
    lens=100,
    fstop=5.6,
    view="AgX",
    look="AgX - Medium High Contrast",
    exposure=-0.8,
    bg="#4C74A8",
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


def link_obj(ob):
    scene.collection.objects.link(ob)
    return ob


def mesh_obj(name, verts, faces, smooth=True):
    me = bpy.data.meshes.new(name + "_me")
    me.from_pydata(verts, [], faces); me.update()
    for p in me.polygons:
        p.use_smooth = smooth
    return link_obj(bpy.data.objects.new(name, me))


# ------------------------------------------------------------- 被写体の形
# 平面＝超楕円（n=4：角の丸い四角と楕円の間）。縦の断面＝底の丸み・まっすぐの胴・肩の丸み
A, B, H = 0.037, 0.024, 0.074     # 半幅・半奥行き・胴の高さ（m）
RB, RT = 0.005, 0.011             # 底と肩の丸み
NSE, SEG = 2.6, 160


FLUTES, FLUTE_D = 22, 0.00035     # 背面の縦溝：本数（背面の半周あたり）・深さ（m）


def se_ring(a, b, z, n=NSE, seg=SEG, flute=0.0):
    out = []
    for i in range(seg):
        t = 2 * math.pi * i / seg
        c, s = math.cos(t), math.sin(t)
        x, y = a * math.copysign(abs(c) ** (2 / n), c), b * math.copysign(abs(s) ** (2 / n), s)
        if flute and s > 0:      # 背面（+Y）だけ。正面は平滑のまま
            w = min(1.0, s / 0.35) ** 2
            d = flute * w * (0.5 - 0.5 * math.cos(FLUTES * 2 * t))
            r = math.hypot(x, y)
            x, y = x * (1 - d / r), y * (1 - d / r)
        out.append((x, y, z))
    return out


def rounded_prism(name, a, b, h, rb, rt, n=NSE, seg=SEG, steps=10, flute=0.0):
    prof = []                                              # (z, inset)
    for k in range(steps + 1):                             # 底の丸み
        t = (math.pi / 2) * (1 - k / steps)
        prof.append((rb - rb * math.sin(t), rb - rb * math.cos(t)))
    for k in range(1, 6):
        prof.append((rb + (h - rt - rb) * k / 6, 0.0))
    for k in range(steps + 1):                             # 肩の丸み
        t = (math.pi / 2) * k / steps
        prof.append((h - rt + rt * math.sin(t), rt - rt * math.cos(t)))
    verts, faces = [], []
    for (z, ins) in prof:
        verts += se_ring(max(a - ins, 1e-4), max(b - ins, 1e-4), z, n, seg, flute * (1 - ins / max(rb, rt)))
    R = len(prof)
    for r in range(R - 1):
        for i in range(seg):
            j = (i + 1) % seg
            faces.append((r * seg + i, r * seg + j, (r + 1) * seg + j, (r + 1) * seg + i))
    verts.append((0, 0, prof[0][0])); cb = len(verts) - 1
    verts.append((0, 0, prof[-1][0])); ct = len(verts) - 1
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((cb, j, i))
        faces.append((ct, (R - 1) * seg + i, (R - 1) * seg + j))
    return mesh_obj(name, verts, faces)


def cylinder(name, r, z0, z1, seg=128, bev=0.0008, bseg=4):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=seg, location=(0, 0, (z0 + z1) / 2))
    ob = bpy.context.object; ob.name = name
    if bev:
        bevel_obj(ob, bev, segments=bseg)
    return ob


# ------------------------------------------------------------- 材質
def glass_mat():
    m = bpy.data.materials.new("glass"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.93, 0.96, 1.0, 1)
    p.inputs["Roughness"].default_value = 0.0
    p.inputs["Transmission Weight"].default_value = 1.0
    va = nt.nodes.new("ShaderNodeVolumeAbsorption")      # 厚い底ほど青い
    va.inputs["Color"].default_value = hex_to_linear("#4CB8D8")
    va.inputs["Density"].default_value = GLASS_DENSITY
    nt.links.new(va.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    p.inputs["IOR"].default_value = 1.5
    return m


def liquid_mat():
    """液はガラスの中にある＝境界の IOR は 1.33/1.5。色は体積吸収で（厚いところほど濃い青）"""
    m = bpy.data.materials.new("liquid"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = nt.nodes["Material Output"]
    g = nt.nodes.new("ShaderNodeBsdfGlass")
    g.inputs["IOR"].default_value = LIQ_IOR
    g.inputs["Roughness"].default_value = 0.0
    g.inputs["Color"].default_value = (1, 1, 1, 1)
    print(">> liquid IOR", g.inputs["IOR"].default_value)
    va = nt.nodes.new("ShaderNodeVolumeAbsorption")
    va.inputs["Color"].default_value = LIQ_COLOR
    va.inputs["Density"].default_value = LIQ_DENSITY
    nt.links.new(g.outputs[0], out.inputs["Surface"])
    nt.links.new(va.outputs[0], out.inputs["Volume"])
    return m


LIQ_IOR = 0.97        # 実際は 1.33/1.5=0.887 だが、肩の斜面で全反射して灰色の板が出る（round 16）
LIQ_COLOR = hex_to_linear("#10BCD8")
LIQ_DENSITY = 50.0
GLOW_W = 50.0
SHEEN_W = 40.0
GLASS_DENSITY = 18.0
WALL_GLOSSY = 0.2
GLOW_AT = (-0.30, 0.75, 0.07)   # カメラ→瓶の中心の延長が地に当たる点（hero の位置で計算）

# ------------------------------------------------------------- 被写体
WALL, BASE_T = 0.0045, 0.013       # 胴の壁厚・底の厚み
FILL = 0.975                        # 液の高さ（胴の内側に対する割合）

body = rounded_prism("glass", A, B, H, RB, RT, seg=480, flute=FLUTE_D)
body.data.materials.append(glass_mat())

li_h = (H - BASE_T - WALL) * FILL
liquid = rounded_prism("liquid", A - WALL, B - WALL, H - WALL - BASE_T, 0.004, RT - WALL, steps=8)   # 満タン：肩の丸みまで液
liquid.location.z = BASE_T
liquid.data.materials.append(liquid_mat())

NECK_R = 0.0085
COL_Z0, COL_Z1 = H - 0.0012, H + 0.0042
collar = cylinder("collar", 0.0102, COL_Z0, COL_Z1, bev=0.0005, bseg=3)
collar.data.materials.append(principled("alu", hex_to_linear("#C9CCD1"), rough=0.22, metal=1.0))

CAP_R, CAP_H = 0.0168, 0.031
cap = cylinder("cap", CAP_R, COL_Z1 + 0.0004, COL_Z1 + 0.0004 + CAP_H, seg=160, bev=0.0011, bseg=5)
cap.data.materials.append(principled("cap", hex_to_linear("#0E0F12"), rough=0.32, coat=0.25))

# 吸い上げ管：口金から底へ、わずかに曲がる
pts = []
for k in range(25):
    t = k / 24
    z = COL_Z0 - t * (COL_Z0 - BASE_T - 0.0015)
    pts.append((0.0035 * math.sin(t * math.pi * 0.9), -0.002 * t, z))
cu = bpy.data.curves.new("tube_c", 'CURVE'); cu.dimensions = '3D'
sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
for p, q in zip(sp.points, pts):
    p.co = (*q, 1)
cu.bevel_depth = 0.0009; cu.bevel_resolution = 4; cu.use_fill_caps = True
tube_c = link_obj(bpy.data.objects.new("tube_c", cu))
bpy.context.view_layer.objects.active = tube_c
for o in bpy.data.objects:
    o.select_set(o == tube_c)
bpy.ops.object.convert(target='MESH')
tube = bpy.context.object; tube.name = "tube"
tube.data.materials.append(principled("tube", (0.95, 0.97, 1.0, 1), rough=0.05, trans=1.0, ior=1.06))
for p in tube.data.polygons:
    p.use_smooth = True

bottle = bpy.data.objects.new("bottle", None); link_obj(bottle)
parts = [body, liquid, collar, cap, tube]
for o in parts:
    o.parent = bottle

# ------------------------------------------------------------- 舞台：濡れた黒の床＋黒アクリルの段＋青い地
LEDGE_X0, LEDGE_H = 0.0, 0.011
TILT = math.degrees(math.asin(LEDGE_H / (2 * A))) * 1.02


def place_bottle():
    """瓶を Y 軸で傾け、左の底が床に、右の底が段の縁に乗るよう位置を解く"""
    rot = Matrix.Rotation(math.radians(-TILT), 4, 'Y')
    vs = [rot @ v.co for v in body.data.vertices]
    zmin = min(v.z for v in vs)
    xr = max(v.x for v in vs)
    # 右端の点（段に乗る側）の高さ
    right = [v for v in vs if v.x > xr - 0.004]
    zr = min(v.z for v in right) - zmin
    lift = -zmin
    return rot, lift, xr, zr


rot, lift, XR, ZR = place_bottle()
bottle.rotation_euler = (0, math.radians(-TILT), 0)
bottle.location = (0, 0, lift)
LEDGE_X0 = XR - 0.006           # 段の縁＝瓶の右の底の角の下
print(">> tilt %.2f deg  right foot z=%.4f  ledge=%.4f" % (TILT, ZR, LEDGE_H))

bpy.ops.mesh.primitive_cube_add(size=1, location=(LEDGE_X0 + 0.2, 0.125, LEDGE_H / 2))
ledge = bpy.context.object; ledge.name = "ledge"
ledge.scale = (0.4, 0.35, LEDGE_H); bpy.ops.object.transform_apply(scale=True)
bevel_obj(ledge, 0.0012, segments=4)
ledge.data.materials.append(principled("acrylic", hex_to_linear("#05070B"), rough=0.04, coat=0.0))
ledge.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15

bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0.6, 0))
floor = bpy.context.object; floor.name = "floor"
floor.data.materials.append(principled("floor", hex_to_linear("#03050A"), rough=0.22))
floor.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.035

# 地：瓶の奥 0.7m の壁。右上ほど明るい
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.05, 0.75, 0.3))
wall = bpy.context.object; wall.name = "wall"
wall.scale = (2.0, 1.0, 0.8); wall.rotation_euler = (math.radians(90), 0, 0)
wall.data.materials.append(principled("wall", hex_to_linear(LOOK["bg"]), rough=0.8))
wall.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.1
# 床が浅い角度で地を映すと手前が明るい青になる＝光沢の光線から見た地だけを暗くする（基準の手前は濃紺）
_nt = wall.data.materials[0].node_tree
_lp = _nt.nodes.new("ShaderNodeLightPath")
_dk = _nt.nodes.new("ShaderNodeMix"); _dk.data_type = 'RGBA'
sock(_dk, "A", 'RGBA').default_value = hex_to_linear(LOOK["bg"])
sock(_dk, "B", 'RGBA').default_value = tuple(c * WALL_GLOSSY for c in hex_to_linear(LOOK["bg"])[:3]) + (1.0,)
_nd = _nt.nodes.new("ShaderNodeMath"); _nd.operation = 'LESS_THAN'; _nd.inputs[1].default_value = 0.5
_nt.links.new(_lp.outputs["Transmission Depth"], _nd.inputs[0])      # ガラス・液を通った光線は除く
_ng = _nt.nodes.new("ShaderNodeMath"); _ng.operation = 'MULTIPLY'
_nt.links.new(_lp.outputs["Is Glossy Ray"], _ng.inputs[0]); _nt.links.new(_nd.outputs[0], _ng.inputs[1])
_nt.links.new(_ng.outputs[0], _dk.inputs["Factor"])
_nt.links.new(next(o for o in _dk.outputs if o.name == "Result" and o.type == 'RGBA'),
              _nt.nodes["Principled BSDF"].inputs["Base Color"])

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hex_to_linear("#0B1424")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3

# ------------------------------------------------------------- 光
def hide_from_cam(L, glossy=True):
    L.visible_camera = False
    L.visible_glossy = glossy
    return L

# 地を右上から起こす大きな面（壁にだけ向ける）
wall_l = hide_from_cam(area("wall_key", (0.35, 0.30, 0.95), 0.9, 25, (0.9, 0.95, 1.0), target=(0.10, 0.75, 0.65)), glossy=False)
# 瓶の後ろの細い面＝ガラスと液を後ろから透かす
back = hide_from_cam(area("back", (0.03, 0.22, 0.06), 0.12, 6.0, (0.85, 0.92, 1.0), target=(0.0, 0.0, 0.05)), glossy=False)
STRIPS = []
# 左右の縦長の面＝ガラスの縁に縦の照り
for nm, loc, e in (("strip_l", (-0.22, 0.05, 0.08), 3.0), ("strip_r", (0.20, 0.24, 0.16), 0.8)):
    L = hide_from_cam(area(nm, loc, 0.04, e, (0.92, 0.96, 1.0), target=(0, 0, 0.06)))
    L.data.size_y = 0.30
    STRIPS.append(L)
# 左前の縦長の柔らかい面＝正面の丸みに幅の広い照りの帯
# （面光源だと長方形の縁がそのまま写る＝横方向に釣鐘形に光る板にして、光沢の光線にだけ見せる）
def soft_card(name, loc, w, h, strength, target):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.object; ob.name = name; ob.scale = (w, h, 1)
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mt = nt.nodes.new("ShaderNodeMath"); mt.operation = 'SUBTRACT'; mt.inputs[1].default_value = 0.5
    sq = nt.nodes.new("ShaderNodeMath"); sq.operation = 'MULTIPLY'
    ex = nt.nodes.new("ShaderNodeMath"); ex.operation = 'MULTIPLY'; ex.inputs[1].default_value = -18.0
    e = nt.nodes.new("ShaderNodeMath"); e.operation = 'EXPONENT'
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.95, 0.97, 1.0, 1)
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = strength
    L = nt.links.new
    L(tc.outputs["Generated"], sep.inputs[0]); L(sep.outputs["X"], mt.inputs[0])
    L(mt.outputs[0], sq.inputs[0]); L(mt.outputs[0], sq.inputs[1]); L(sq.outputs[0], ex.inputs[0])
    L(ex.outputs[0], e.inputs[0]); L(e.outputs[0], mul.inputs[0]); L(mul.outputs[0], em.inputs["Strength"])
    L(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    ob.data.materials.append(m)
    ob.visible_camera = False; ob.visible_shadow = False; ob.visible_diffuse = False
    ob.visible_volume_scatter = False
    return ob


sheen = soft_card("sheen", (-0.20, -0.30, 0.09), 0.20, 0.45, SHEEN_W, (0, 0, 0.05))
# 前上の弱い起こし：キャップの天面と肩
key = hide_from_cam(area("key", (-0.20, -0.30, 0.40), 0.45, 4.0, (1.0, 0.98, 0.95), target=(0, 0, 0.08)))

# 瓶の真後ろの地にだけ丸い光だまり＝透かして液の中心を光らせる
sd = bpy.data.lights.new("glow", 'SPOT'); sd.energy = GLOW_W; sd.color = (0.80, 0.90, 1.0)
sd.spot_size = math.radians(60); sd.spot_blend = 1.0; sd.shadow_soft_size = 0.05
glow = bpy.data.objects.new("glow", sd); scene.collection.objects.link(glow)
glow.location = (-0.14, 0.36, 0.20)
glow.rotation_euler = (Vector(GLOW_AT) - glow.location).to_track_quat('-Z', 'Y').to_euler()
hide_from_cam(glow)

# 縦の面光源は瓶にだけ（段・床に白い板を写さない）
rx = bpy.data.collections.new("bottle_rx")
for o in parts:
    rx.objects.link(o)
for L in STRIPS:
    L.light_linking.receiver_collection = rx

for _n in filter(None, os.environ.get("II_OFF", "").split(",")):   # 調べ用：名前の光を消す
    bpy.data.objects[_n].hide_render = True
# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
cd.clip_start = 0.01
scene.camera = cam

scene.cycles.max_bounces = 32
scene.cycles.transmission_bounces = 24
scene.cycles.glossy_bounces = 12
scene.cycles.transparent_max_bounces = 16
scene.cycles.volume_bounces = 2
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.cycles.blur_glossy = 0.5

# ------------------------------------------------------------- 動画＝プロダクトフィルム
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


TGT = Vector((0.016, 0, 0.056))
HERO = dict(deg=24, dist=0.50, h=0.048)


def hero_cam():
    return orbit(TGT, HERO["dist"], HERO["h"], HERO["deg"])


COLLAR_FRONT = bottle.matrix_world @ Vector((0, -0.0102, COL_Z1))       # 口金の手前の縁（マクロのピント）
CAP_EDGE = bottle.matrix_world @ Vector((-0.004, -CAP_R, COL_Z1 + 0.004))  # キャップの下の縁


def macro_cam(t):
    loc = orbit(Vector((-0.004, 0, 0.088)), 0.21, 0.097 - 0.006 * ease(t), 38 - 16 * ease(t))
    fp = CAP_EDGE.lerp(COLLAR_FRONT, ease(t))                              # ピント送り：キャップの縁→口金
    return loc, Vector((-0.006, 0, 0.083)), 150, 4.0, (fp - loc).length


SHOTS = [
    dict(sec=3.0,   # 光の走り：中寄りで止め、照りの帯を左の外から胴へ滑り込ませる
         cam=lambda t: (orbit(TGT, 0.36, 0.050 + 0.006 * ease(t), 30 - 6 * ease(t)), TGT + Vector((-0.006, 0, 0.004)),
                        100, 5.6, None)),
    dict(sec=2.5, cam=macro_cam),   # マクロ：キャップの縁と口金をなめる＋ピント送り
    dict(sec=3.0,   # 押し込み：左手前の低い位置から、床に乗った足と映り込みへ寄る
         cam=lambda t: (lerp(orbit(TGT, 0.60, 0.020, -38), orbit(TGT, 0.40, 0.015, -30), ease(t)),
                        Vector((-0.012, 0, 0.026)), 120, 4.0, None)),
    dict(sec=3.0,   # 決め：回り込みながら入って hero で止まる
         cam=lambda t: (orbit(TGT, HERO["dist"] + 0.05 * (1 - ease_out(min(1.0, t / 0.6))), HERO["h"],
                              HERO["deg"] - 14 * (1 - ease_out(min(1.0, t / 0.6)))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

SHEEN_HOME = Vector(sheen.location)


def pose(i, t, T):
    pass


def light_path(i, t):
    """1カット目：照りの板を右→左へ滑らせる＝柔らかい照りの帯が胴を横切る"""
    if i == 0:
        sheen.location = SHEEN_HOME + Vector((-0.30 * (1 - ease(t)), 0, 0))
    elif i == 2:    # 押し込み（左の低い位置）では床に映るので画面の外へ逃がす
        sheen.location = SHEEN_HOME + Vector((-0.6, -0.4, 0.5))
    else:
        sheen.location = SHEEN_HOME


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
        light_path(i, t)
        sheen.keyframe_insert("location", frame=f)

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

if "probe" in modes:    # anim の1フレームの秒数を測る（長辺1080・II_ANIM_SAMPLES）
    import time
    t0 = time.time()
    still(os.path.join("/tmp", "_ii017_probe.png"), 1080, int(os.environ.get("II_ANIM_SAMPLES", "24")), 1)
    print(">> probe %.1fs/frame" % (time.time() - t0))

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
    # glb の動き：傾いた瓶をゆっくり一回転させる（動画のカメラワークは glb に乗らないため）
    bottle.animation_data_clear()
    for f, deg in ((1, 0), (N_FRAMES + 1, 360)):
        bottle.rotation_euler = (0, math.radians(-TILT), math.radians(deg))
        bottle.keyframe_insert("rotation_euler", frame=f)
    for fc in bottle.animation_data.action.fcurves if hasattr(bottle.animation_data.action, "fcurves") else []:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    names = {o.name for o in parts} | {"bottle"}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = bottle
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
