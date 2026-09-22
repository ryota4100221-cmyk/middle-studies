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

# ------------------------------------------------------------- LOOK（毎回決める）
LOOK = dict(
    aspect=(4, 5),            # 4:5 / 1:1 / 3:4 / 16:9 / 9:16 …
    lens=70,                  # mm
    fstop=4.0,
    view="AgX",               # AgX / Khronos PBR Neutral / Filmic 系。題材の色域で選ぶ
    look="AgX - Base Contrast",
    exposure=0.0,
    bg=(0.62, 0.60, 0.57),    # 地の色（linear）。無限背景紙・床・空間のどれにするかは下の舞台で決める
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


# ------------------------------------------------------------- 舞台（毎回決める）
# 仮置き：無限背景紙（床と奥の壁を R でつなぐ）
R, W, D, H = 1.2, 14.0, 6.0, 7.0      # 立ち上がりの半径・幅・手前の奥行き・壁の高さ
# 断面 (y, z)：手前の床 → R で立ち上がる → 奥の壁。これを x 方向に押し出す
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 12 * math.pi / 2 for i in range(1, 13)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + 2.5, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
sweep.data.materials.append(principled("paper", LOOK["bg"] + (1.0,), rough=0.62))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.05, 0.05, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4

# ------------------------------------------------------------- 被写体（毎回作る）
# 仮置き：面取りした角丸の箱＋リング。**動作確認用。これを題材にしない**
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.9))
body = bpy.context.object; body.name = "body"
body.scale = (0.9, 0.9, 1.3); bpy.ops.object.transform_apply(scale=True)
bevel_obj(body, 0.08, segments=5)
body.data.materials.append(principled("body", hex_to_linear("#2B3A55"), rough=0.28, coat=0.6))

bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.05, location=(0, 0, 0.9),
                                 major_segments=128, minor_segments=24)  # 既定48×12は面が割れて見える
ring = bpy.context.object; ring.name = "ring"
for p in ring.data.polygons:
    p.use_smooth = True
ring.data.materials.append(principled("ring", hex_to_linear("#C9A45C"), rough=0.22, metal=1.0))
parts = [body, ring]

# ------------------------------------------------------------- 光（毎回組む）
# 仮置き：大きいキー＋縁取り。光の組み方は基準の作品から読む（SKILL.md 工程1）
area("key", (-3.2, -3.0, 3.6), 3.0, 900, (1.0, 0.96, 0.9))
area("rim", (2.8, 2.2, 2.6), 1.2, 420, (0.9, 0.95, 1.0))

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.lens = LOOK["lens"]
dist = LOOK["lens"] / 70 * 6.2
cam.location = (0.0, -dist, 1.35)
cam.rotation_euler = (Vector((0, 0, 0.9)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True
cd.dof.focus_object = body
cd.dof.aperture_fstop = LOOK["fstop"]
scene.camera = cam

# ------------------------------------------------------------- 動き（毎フレームキー＝数学的に閉じる）
# 🔴 イージングのキーフレーム2点で済ませない。位相 t∈[0,1) で書き、t=1 が t=0 に一致すること
def pose(t):
    body.rotation_euler = (0, 0, 2 * math.pi * t)
    ring.rotation_euler = (math.radians(90) * (0.5 + 0.5 * math.cos(2 * math.pi * t)), 0, 2 * math.pi * t)

for f in range(1, N_FRAMES + 2):
    pose((f - 1) / N_FRAMES)
    for o in parts:
        o.keyframe_insert("rotation_euler", frame=f)
for o in parts:
    if o.animation_data and o.animation_data.action:
        try:
            for fc in o.animation_data.action.fcurves:
                for k in fc.keyframe_points:
                    k.interpolation = 'LINEAR'
        except AttributeError:
            pass  # Blender 5.x の layered action。毎フレームキーなので補間は効かない

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
