# =============================================================
# monaka design. — MIDDLE STUDY 003 "DANSOU"
# 黒い板を34枚積んだタワー。中腹がtanhプロファイルで水平にスライドし、
# 断層のずれた段差からライム #A5E02E の光が漏れる。
# 各層の境界には最初からライムの薄層が埋まっていて、
# ずれた時だけ「中に光があった」ことがわかる。
# "Designing the Middle of Your Story."
#
# 実行:
#   Blender --background --python monaka_dansou.py -- <mode...>
#   modes: test | still | anim | glb | blend
# =============================================================
import bpy
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

N_PLATES = 20          # 積層する黒い板の枚数
W = 1.5                # 板の一辺（正方形）
H = 1.1                # タワーの全高（短く・塊感を出す＝001/002と同じ中心構図）
Z0 = 0.70              # タワー底面の浮遊高さ（床の明部から離す）
CENTER_Z = Z0 + H / 2  # = 1.25
FAULT_Z = 1.25         # 断層の中心高さ（タワー正中＝画面中央）
SIGMA = 0.05           # tanh遷移幅（小さいほど断層が鋭い＝剛体的なズレ）
SLIDE = 0.55           # 上部ブロックの最大水平スライド量（横ずれが主役）
LIFT = 0.06            # 上部ブロックの微小な持ち上がり（口をわずかに開けるだけ）
INSET = 0.010          # ライム層のXYインセット（閉時は板の縁の影に隠れる）
LIME_T = 0.050         # 断層ライム層の厚み（横ずれで断面を見せる）
FAULT_BAND_K = 1.1     # 断層ライムを仕込む帯（×pitch）。ここだけ光る＝黒を保つ
TOWER_X = -0.20        # タワー基準位置（スライドが+Xへ出るぶん左に置く）
RIG_ROT_Z = math.radians(-20)  # 平面的に見えないよう角を見せる回転

FPS = 24
N_FRAMES = 120         # 5秒 完全ループ
STILL_FRAME = 61       # 断層が最大に開いた瞬間

def hex_to_linear(h):
    """sRGB hex → Blender linear RGB"""
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)

LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)

# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]

# 黒い板（マット / サテンを交互に＝001と同じ質感リズム）
mat_matte, b = make_principled("plate_matte")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.48
b.inputs["Specular IOR Level"].default_value = 0.35

mat_satin, b = make_principled("plate_satin")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.22
b.inputs["Coat Weight"].default_value = 0.25
b.inputs["Coat Roughness"].default_value = 0.15

# ライムの断層光（発光）
mat_lime, lime_bsdf = make_principled("fault_lime")
lime_bsdf.inputs["Base Color"].default_value = LIME
lime_bsdf.inputs["Emission Color"].default_value = LIME
lime_bsdf.inputs["Emission Strength"].default_value = 3.0
lime_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- リグ ----------
bpy.ops.object.empty_add(location=(TOWER_X, 0, 0))
rig = bpy.context.active_object
rig.name = "DansouRig"
rig.rotation_euler = (0, 0, RIG_ROT_Z)

def shade(obj):
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            pass

def add_box(name, sx, sy, sz, z):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z))
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    o.location = (0.0, 0.0, z)  # transform_applyがlocationを0に落とすため明示再設定
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = min(0.006, sz * 0.3)
    bev.segments = 2
    shade(o)
    o.parent = rig
    return o

# ---------- 積層タワー（板＋境界のライム層） ----------
pitch = H / N_PLATES
plate_t = pitch * 0.85  # 板間に黒隙間を残し積層感を出す（隙間は黒＝光らせない）
FAULT_BAND = pitch * FAULT_BAND_K

plates = []   # (obj, rest_z)
for i in range(N_PLATES):
    z = Z0 + pitch * (i + 0.5)
    p = add_box(f"plate_{i:02d}", W, W, plate_t, z)
    p.data.materials.append(mat_matte if i % 2 == 0 else mat_satin)
    plates.append((p, z))

# ライム層は断層帯の継ぎ目だけに埋める。下ブロック側に固定し、
# 上ブロックが退いた時だけ露出する＝「中に光があった」ことがわかる。
limes = []    # (obj, rest_z)
for i in range(N_PLATES - 1):
    z = Z0 + pitch * (i + 1)
    if abs(z - FAULT_Z) > FAULT_BAND:
        continue
    l = add_box(f"lime_{i:02d}", W - 2 * INSET, W - 2 * INSET, LIME_T, z)
    l.data.materials.append(mat_lime)
    limes.append((l, z))

# ---------- アニメーション（tanh断層シア / cos完全ループ） ----------
def profile(z):
    """0(下部ブロック)→1(上部ブロック)。遷移帯の数枚だけが段差になる"""
    return 0.5 * (1 + math.tanh((z - FAULT_Z) / SIGMA))

def osc(t01, lag):
    """0..1 → 0..1、cosベース＝完全ループ。lagで断層から波が伝う"""
    return 0.5 * (1 - math.cos(2 * math.pi * t01 - lag))

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def animate(obj, rest_z):
    prof = profile(rest_z)
    lag = 0.22 * abs(rest_z - FAULT_Z)  # 微小な伝播ラグ（ブロックはほぼ剛体で動く）
    for f in range(1, N_FRAMES + 1):
        o = osc((f - 1) / N_FRAMES, lag)
        obj.location.x = SLIDE * prof * o
        obj.location.z = rest_z + LIFT * prof * o
        obj.keyframe_insert(data_path="location", index=0, frame=f)
        obj.keyframe_insert(data_path="location", index=2, frame=f)

for p, z in plates:
    animate(p, z)
# ライムは下ブロックに固定＝動かさない。上ブロックが退いて初めて露出する。

# 断層が開くほど光が強く（毎フレームキー / Blender 5作法）
es = lime_bsdf.inputs["Emission Strength"]
for f in range(1, N_FRAMES + 1):
    es.default_value = 1.3 + 0.9 * osc((f - 1) / N_FRAMES, 0.0)
    es.keyframe_insert(data_path="default_value", frame=f)

# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

def add_caption(body, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object
    tx.name = name
    tx.data.body = body
    tx.data.size = size
    tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx

tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.36), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.18), "logo")
study = add_caption("MIDDLE STUDY 003 — DANSOU", 0.045, (0.15, -1.3, 0.055), "study")

# ---------- ライティング（001/002と同一＝シリーズの一貫性） ----------
def add_area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.size = size
    L.data.energy = energy
    L.data.color = color
    direction = Vector(target) - Vector(loc)
    L.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return L

focus = (0, 0, CENTER_Z)
add_area("key",  (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
add_area("rim",  (3.5, 4.0, 3.2),  3.0, 420, (0.88, 0.94, 1.0), focus)
add_area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
    bg.inputs[1].default_value = 0.55

# ---------- カメラ ----------
bpy.ops.object.camera_add(location=(0.55, -12.2, 2.05))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, CENTER_Z + 0.30))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = limes[len(limes) // 2][0] if limes else plates[N_PLATES // 2][0]
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam

for tx in (tagline, logo, study):
    tx.rotation_euler = cam.rotation_euler

# ---------- レンダー設定 ----------
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = True
    scene.cycles.device = 'GPU'
    print(">> Metal GPU enabled")
except Exception as e:
    print(">> GPU setup failed, using CPU:", e)

scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
    print(">> view: PBR Neutral")
except Exception:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Punchy'
    print(">> view: AgX Punchy")

# ---------- コンポジター（Bloom / Blender 5 新方式） ----------
def setup_bloom():
    try:
        ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out='OUTPUT',
                                socket_type='NodeSocketColor')
        rl = ng.nodes.new("CompositorNodeRLayers")
        glare = ng.nodes.new("CompositorNodeGlare")
        out = ng.nodes.new("NodeGroupOutput")
        try:
            glare.inputs["Type"].default_value = 'BLOOM'
        except Exception:
            pass
        glare.inputs["Threshold"].default_value = 1.2
        glare.inputs["Strength"].default_value = 0.35
        try:
            glare.inputs["Size"].default_value = 0.55
        except Exception:
            pass
        ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
        ng.links.new(glare.outputs["Image"], out.inputs["Image"])
        scene.compositing_node_group = ng
        scene.render.use_compositing = True
        print(">> Bloom compositor OK")
    except Exception as e:
        print(">> Bloom setup failed (render continues without):", e)

setup_bloom()

# ---------- 出力モード ----------
modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(OUT, "monaka_dansou.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith("plate_") or o.name.startswith("lime_"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_dansou.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero still done")

if "anim" in modes:
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'  # Blender 5: 動画はmedia_type経由
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
