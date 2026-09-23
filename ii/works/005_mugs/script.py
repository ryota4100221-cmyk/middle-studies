# =============================================================
# MIDDLE STUDIES II — 雛形（2026-09-23）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / phases   （省略時 test）
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

# ------------------------------------------------------------- LOOK（005 MUGS）
LOOK = dict(
    aspect=(4, 3),
    lens=50,
    fstop=8.0,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=0.15,
)
FPS, SECONDS = 24, 6
N_FRAMES = FPS * SECONDS
STILL_FRAME = 1

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


# ------------------------------------------------------------- 舞台：オークの天板（実寸・m）
from mathutils import Matrix, Quaternion


def sock(node, name, kind, out=False):
    """#103：Mix の同名ソケットは型で引く"""
    ss = node.outputs if out else node.inputs
    return next(s for s in ss if s.name == name and s.type == kind)


def wood_material():
    m = bpy.data.materials.new("oak"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.58
    p.inputs["Coat Weight"].default_value = 0.08
    p.inputs["Coat Roughness"].default_value = 0.35
    tc = N.new("ShaderNodeTexCoord")
    oi = N.new("ShaderNodeObjectInfo")
    mp = N.new("ShaderNodeMapping")
    # 板ごとに木目をずらす（Object Info の Random）
    off = N.new("ShaderNodeVectorMath"); off.operation = 'SCALE'
    L.new(oi.outputs["Random"], off.inputs["Scale"])
    comb = N.new("ShaderNodeCombineXYZ")
    comb.inputs[0].default_value = 3.1; comb.inputs[1].default_value = 7.3; comb.inputs[2].default_value = 1.7
    L.new(comb.outputs[0], off.inputs[0])
    add = N.new("ShaderNodeVectorMath"); add.operation = 'ADD'
    L.new(tc.outputs["Object"], add.inputs[0]); L.new(off.outputs[0], add.inputs[1])
    L.new(add.outputs[0], mp.inputs["Vector"])
    # 木目は板の長手（x）に流れる：y 方向に縞。x 方向には長く伸ばす
    mp.inputs["Scale"].default_value = (4.0, 180.0, 180.0)
    # ゆらぎ
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25
    nz.inputs["Detail"].default_value = 3.0
    L.new(mp.outputs[0], nz.inputs["Vector"])
    warp = N.new("ShaderNodeVectorMath"); warp.operation = 'MULTIPLY_ADD'
    L.new(nz.outputs["Color"], warp.inputs[0])
    warp.inputs[1].default_value = (0.0, 3.5, 0.0)
    L.new(mp.outputs[0], warp.inputs[2])
    wave = N.new("ShaderNodeTexWave"); wave.wave_type = 'BANDS'; wave.bands_direction = 'Y'
    wave.wave_profile = 'SAW'
    wave.inputs["Scale"].default_value = 2 * math.pi / 20
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 4.0
    L.new(warp.outputs[0], wave.inputs["Vector"])
    # 柾目：長手に引き伸ばしたノイズ（Wave の縞は一定間隔の罫線に見えた）
    grain = N.new("ShaderNodeTexNoise"); grain.inputs["Scale"].default_value = 1.0
    grain.inputs["Detail"].default_value = 2.0; grain.inputs["Roughness"].default_value = 0.62
    gmp = N.new("ShaderNodeMapping"); gmp.inputs["Scale"].default_value = (14.0, 260.0, 260.0)
    L.new(add.outputs[0], gmp.inputs["Vector"]); L.new(gmp.outputs[0], grain.inputs["Vector"])
    gr = N.new("ShaderNodeMapRange")
    gr.inputs["From Min"].default_value = 0.2; gr.inputs["From Max"].default_value = 0.8
    gr.inputs["To Min"].default_value = 0.1; gr.inputs["To Max"].default_value = 0.9
    L.new(grain.outputs["Fac"], gr.inputs["Value"])
    # 細い導管（柾目の細い筋）
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 1.0
    fmp = N.new("ShaderNodeMapping"); fmp.inputs["Scale"].default_value = (6.0, 900.0, 900.0)
    L.new(add.outputs[0], fmp.inputs["Vector"]); L.new(fmp.outputs[0], fine.inputs["Vector"])
    fine.inputs["Detail"].default_value = 2.0
    # 大きな色むら
    blot = N.new("ShaderNodeTexNoise"); blot.inputs["Scale"].default_value = 0.02
    L.new(add.outputs[0], blot.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = hex_to_linear(WOOD_DARK)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = hex_to_linear(WOOD_LIGHT)
    mix1 = N.new("ShaderNodeMath"); mix1.operation = 'MULTIPLY_ADD'
    L.new(fine.outputs["Fac"], mix1.inputs[0]); mix1.inputs[1].default_value = 0.05
    L.new(gr.outputs[0], mix1.inputs[2])
    mix2 = N.new("ShaderNodeMath"); mix2.operation = 'MULTIPLY_ADD'
    L.new(blot.outputs["Fac"], mix2.inputs[0]); mix2.inputs[1].default_value = 0.35
    L.new(mix1.outputs[0], mix2.inputs[2])
    sc = N.new("ShaderNodeMapRange")
    sc.inputs["From Min"].default_value = 0.35; sc.inputs["From Max"].default_value = 1.45
    L.new(mix2.outputs[0], sc.inputs["Value"])
    L.new(sc.outputs[0], ramp.inputs["Fac"])
    # 導管の細い濃い線：引き伸ばしたノイズの尾根だけを拾う
    # ノイズの尾根はぼやけた帯になった→長手に引き伸ばした Voronoi の縁（細く・間隔が不揃い・長く続く）
    ln = N.new("ShaderNodeTexVoronoi"); ln.feature = 'DISTANCE_TO_EDGE'
    ln.inputs["Scale"].default_value = 1.0
    lmp = N.new("ShaderNodeMapping"); lmp.inputs["Scale"].default_value = (0.06, 16.0, 16.0)
    L.new(warp.outputs[0], lmp.inputs["Vector"]); L.new(lmp.outputs[0], ln.inputs["Vector"])
    lr = N.new("ShaderNodeMapRange")
    lr.inputs["From Min"].default_value = 0.05; lr.inputs["From Max"].default_value = 0.0
    L.new(ln.outputs["Distance"], lr.inputs["Value"])
    lmix = N.new("ShaderNodeMix"); lmix.data_type = 'RGBA'; lmix.blend_type = 'MULTIPLY'
    L.new(lr.outputs[0], lmix.inputs["Factor"])
    L.new(ramp.outputs["Color"], sock(lmix, "A", 'RGBA'))
    sock(lmix, "B", 'RGBA').default_value = hex_to_linear("#9C7048")
    L.new(sock(lmix, "Result", 'RGBA', out=True), p.inputs["Base Color"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.03
    bump.inputs["Distance"].default_value = 0.0004
    L.new(mix1.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


WOOD_LIGHT, WOOD_DARK = "#E8BE78", "#B47C3C"
oak = wood_material()
PLANK_W, GAP, TH = 0.30, 0.0018, 0.03
for i, yc in enumerate((-PLANK_W, 0.0, PLANK_W)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, yc + 0.04, -TH / 2))
    pl = bpy.context.object; pl.name = "plank%d" % i
    pl.scale = (2.4, PLANK_W - GAP, TH); bpy.ops.object.transform_apply(scale=True)
    bevel_obj(pl, 0.0012, segments=2)
    pl.data.materials.append(oak)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hex_to_linear("#D8C09A")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5

# ------------------------------------------------------------- 被写体：タブ持ち手のマグ（自作の造形）
GLAZES = dict(lavender="#9A8CD8", slate="#6781A6", sage="#AFC78A", ecru="#E6DECC",
              char="#2F302E", moss="#6D7563", clay="#C9A68A", rose="#DCA69C", mist="#B3C8DE")
INNER = "#D3C7B0"
PROFILE = [(0.0, 0.0065), (0.029, 0.0065), (0.0315, 0.0045), (0.0325, 0.0), (0.0355, 0.0),
           (0.0378, 0.0012), (0.0392, 0.0045), (0.0408, 0.016), (0.0416, 0.035), (0.0419, 0.06),
           (0.0419, 0.084), (0.0417, 0.0895), (0.0411, 0.0917), (0.0401, 0.0927), (0.0391, 0.0923),
           (0.0385, 0.0905), (0.0383, 0.084), (0.0381, 0.04), (0.0372, 0.016), (0.0345, 0.0112),
           (0.030, 0.0098), (0.0, 0.0098)]
MUG_H = 0.0927


def glaze(name, hexc, rough=0.30):
    m = principled(name, hex_to_linear(hexc), rough=rough, coat=0.45)
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Coat Roughness"].default_value = 0.28
    # 梨地：細かい粒のバンプ（粒 約0.3mm）＋粗さのむら
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3200.0
    nz.inputs["Detail"].default_value = 1.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.08
    bp.inputs["Distance"].default_value = 0.00005
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough - 0.06; rr.inputs["To Max"].default_value = rough + 0.06
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"]); nt.links.new(rr.outputs[0], p.inputs["Roughness"])
    return m


mat_inner = glaze("inner", INNER, 0.16)
mat_foot = principled("bisque", hex_to_linear("#C7B39A"), rough=0.75)


def make_mug(name, color):
    me = bpy.data.meshes.new(name + "_body")
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in PROFILE]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=128,
                   use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    body = bpy.data.objects.new(name, me); scene.collection.objects.link(body)
    # 持ち手：丸めた板に長円の窓（タブ型）
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0535, 0, 0.050))
    h = bpy.context.object
    h.scale = (0.029, 0.009, 0.058); bpy.ops.object.transform_apply(scale=True)
    bevel_obj(h, 0.0024, segments=4)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.0, depth=0.05, location=(0.0555, 0, 0.050),
                                        rotation=(math.pi / 2, 0, 0))
    hole = bpy.context.object
    hole.scale = (0.0068, 0.020, 1.0); bpy.ops.object.transform_apply(scale=True, rotation=True)
    mod = h.modifiers.new("hole", 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = hole
    bpy.context.view_layer.objects.active = h
    bpy.ops.object.modifier_apply(modifier="hole")
    bpy.data.objects.remove(hole)
    bevel_obj(h, 0.0022, segments=4, clamp=True, angle=40)
    mod = body.modifiers.new("join", 'BOOLEAN'); mod.operation = 'UNION'; mod.object = h
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier="join")
    bpy.data.objects.remove(h)
    bevel_obj(body, 0.0016, segments=3, clamp=False, angle=50)
    body.data.materials.clear()   # Boolean が持ち手の空スロット(None)を先頭に足す＝index 0 が既定の白になる
    body.data.materials.append(glaze(name + "_glaze", color))
    body.data.materials.append(mat_inner)
    body.data.materials.append(mat_foot)
    for p in body.data.polygons:
        c = p.center
        r = math.hypot(c.x, c.y)
        if c.z > 0.0085 and r < 0.0394 and c.x < 0.04:
            p.material_index = 1
        elif c.z < 0.0014 and 0.031 < r < 0.037:
            p.material_index = 2
    return body


# 配置：(名前, 色, x, y, 寝かせるか, 向き[deg], 回る向き)
LAYOUT = [   # 寝かせたものは回さない（sp=0）＝群れを詰められる
    ("m_moss", "moss", -0.270, 0.050, True, 100, 0),
    ("m_lav", "lavender", -0.070, 0.170, False, 35, +1),
    ("m_ecru", "ecru", 0.090, 0.125, True, -25, 0),
    ("m_rose", "rose", 0.250, 0.100, False, 140, -1),
    ("m_slate", "slate", -0.120, -0.020, False, 200, +1),
    ("m_mist", "mist", 0.060, -0.045, True, 20, 0),
    ("m_sage", "sage", 0.250, -0.090, True, 160, 0),
    ("m_char", "char", -0.200, -0.185, True, -35, 0),
    ("m_clay", "clay", 0.020, -0.205, False, 300, -1),
]
parts, rig = [], []
for nm, col, x, y, lying, ang, sp in LAYOUT:
    ob = make_mug(nm, GLAZES[col])
    ob.rotation_mode = 'QUATERNION'
    if lying:
        # 胴の中心を原点へ寄せて横倒し：持ち手が上を向く。胴の最大半径で天板に乗る
        # Y軸 -90°：持ち手(+x)が上(+z)、口(+z)が -x へ
        # 胴の軸まわりに転がして、持ち手を斜めに倒す（真上だと鞄のシルエットになった）
        roll = math.radians((35, -28, 40, -32)[len(parts) % 4])
        base = Matrix.Translation((0, 0, 0.0419)) @ Matrix.Rotation(math.radians(-90), 4, 'Y') \
            @ Matrix.Rotation(roll, 4, 'Z') @ Matrix.Translation((0, 0, -MUG_H / 2))
    else:
        base = Matrix.Identity(4)
    parts.append(ob); rig.append((ob, Vector(((x + 0.005) * 0.88, y * 0.88, 0)), math.radians(ang), sp, base))

# ------------------------------------------------------------- 光：右上から低い硬い太陽
# SUN は無限遠で画面全体が均一に照る＝日だまりが作れない。遠くの小さなスポットで太陽の代わりをする
SUN_R = 8.0
SUN_AIM = Vector((-0.20, 0.15, 0.0))        # 日だまりの中心（左上）
sun_d = bpy.data.lights.new("sun", 'SPOT')
sun_d.energy = 5.0 * 4 * math.pi * SUN_R ** 2 * 1.6
sun_d.spot_size = math.radians(12)
sun_d.spot_blend = 1.0
sun_d.shadow_soft_size = SUN_R * math.tan(math.radians(0.9) / 2)
sun_d.color = (1.0, 0.88, 0.68)
sun = bpy.data.objects.new("sun", sun_d); scene.collection.objects.link(sun)
sky = area("sky", (1.1, 1.0, 1.4), 2.2, 22, (1.0, 0.97, 0.92), target=(0, 0, 0.05))
sky.visible_camera = False   # 胴に映る「空」。艶の帯は素材ではなく映り込むものが作る
SUN_EL, SUN_AZ = 27.0, 38.0   # 仰角・方位（+x から反時計回り）


def sun_dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))


# ------------------------------------------------------------- カメラ：ほぼ真上の俯瞰
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.lens = LOOK["lens"]
cam.location = (0.0, -0.40, 0.90)
cam.rotation_euler = (Vector((0, -0.005, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True
cd.dof.focus_distance = (cam.location - Vector((0, 0, 0.04))).length
cd.dof.aperture_fstop = LOOK["fstop"]
scene.camera = cam

# ------------------------------------------------------------- 動き：マグが1回転ずつ、太陽がわずかに振れる
last_q = {}


def pose(t):
    for ob, pos, ang, sp, base in rig:
        M = Matrix.Translation(pos) @ Matrix.Rotation(ang + sp * 2 * math.pi * t, 4, 'Z') @ base
        loc, q, _ = M.decompose()
        if ob.name in last_q and last_q[ob.name].dot(q) < 0:
            q = -q
        last_q[ob.name] = q
        ob.location = loc
        ob.rotation_quaternion = q
    d = sun_dir(SUN_AZ + 5.0 * math.sin(2 * math.pi * t), SUN_EL + 1.5 * math.cos(2 * math.pi * t))
    sun.location = SUN_AIM + d * SUN_R
    sun.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()


for f in range(1, N_FRAMES + 2):
    pose((f - 1) / N_FRAMES)
    for ob in parts:
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_quaternion", frame=f)
    sun.keyframe_insert("rotation_euler", frame=f)
    sun.keyframe_insert("location", frame=f)

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

if "phases" in modes:   # 動きの途中を4枚（ループの破綻は hero には出ない）
    for i, fr in enumerate((1, N_FRAMES // 4 + 1, N_FRAMES // 2 + 1, 3 * N_FRAMES // 4 + 1)):
        still(os.path.join(OUT, "_phase_%d.png" % i), 600, 32, fr)
    print(">> phases done")

if "still" in modes:
    still(os.path.join(OUT, "hero.png"), 2560, 256)
    print(">> hero done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = res(1080)
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
