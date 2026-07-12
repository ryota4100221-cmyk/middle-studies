# =============================================================
# monaka design. — MIDDLE STUDY 014 "NENRIN"
# 黒い木口（円盤）に同心の黒いリッジ＝年輪。中心の芯だけライム #A5E02E
# に灯る。各輪が高さをcosで呼吸し、位相ラグで内→外へ波が伝わる。
# 中心の光が盛り上がった輪の内側を照らし、ライムのきらめきが年輪を伝う。
# 木の芯に、光がある。年輪を伝って、外へ広がる。
# "Designing the Middle of Your Story."
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
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

N_RINGS = 9           # 年輪の数
R0 = 0.24             # 最内リングの半径
R_STEP = 0.135        # リング間隔
RING_TUBE = 0.05      # リッジ（チューブ）の太さ
DISC_R = 1.6          # 木口円盤の半径

CORE_R = 0.14         # 中心の芯（発光）の半径
CORE_EMIT = 1.9       # 芯の発光強度（控えめ＝Glare箱回避）
CORE_LIGHT_W = 30     # 芯の点光源（隆起した輪の内側を照らす）

BREATHS = 2           # ループ中の呼吸回数
LAG_WAVES = 1.5       # 半径方向にかける位相の波数（内→外の伝播）
Z_MIN, Z_MAX = 0.35, 1.9   # リッジ高さ(z-scale)の呼吸範囲

CENTER_Z = 1.28
TILT_X = math.radians(50)   # 木口を手前へ倒して年輪を見せる
TILT_Z = math.radians(-6)

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 18      # ヒーロー：呼吸の波が伝播する途中


def hex_to_linear(h):
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

# 黒い木口・年輪（サテン寄り：呼吸で移るハイライトが見えるように。クローム化は回避）
mat_wood, b = make_principled("wood_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.36
b.inputs["Specular IOR Level"].default_value = 0.3

mat_disc, b = make_principled("disc_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.5
b.inputs["Specular IOR Level"].default_value = 0.12

# 発光する芯
mat_core, core_bsdf = make_principled("core_lime")
core_bsdf.inputs["Base Color"].default_value = LIME
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Emission Strength"].default_value = CORE_EMIT
core_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- 傾きリグ（CENTER_Zで木口を倒す） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "NenrinRig"
rig.rotation_euler = (TILT_X, 0, TILT_Z)

# ---------- 木口円盤 ----------
bpy.ops.mesh.primitive_cylinder_add(radius=DISC_R, depth=0.06, vertices=128,
                                    location=(0, 0, -0.05))
disc = bpy.context.active_object
disc.name = "disc"
bev = disc.modifiers.new("Bevel", "BEVEL")
bev.width = 0.015
bev.segments = 2
bpy.ops.object.shade_smooth()
disc.data.materials.append(mat_disc)
disc.parent = rig

# ---------- 中心の芯（発光）＋点光源 ----------
bpy.ops.mesh.primitive_ico_sphere_add(radius=CORE_R, subdivisions=3,
                                      location=(0, 0, 0.04))
core = bpy.context.active_object
core.name = "core"
bpy.ops.object.shade_smooth()
core.data.materials.append(mat_core)
core.visible_shadow = False
core.parent = rig

bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.14))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.energy = CORE_LIGHT_W
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.25
core_light.parent = rig

# ---------- 年輪リング（トーラス。z-scaleで隆起を呼吸） ----------
rings = []
for i in range(N_RINGS):
    r = R0 + i * R_STEP
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0, 0, 0.0),
                                     major_radius=r, minor_radius=RING_TUBE,
                                     major_segments=160, minor_segments=12)
    o = bpy.context.active_object
    o.name = f"ring_{i:02d}"
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat_wood)
    o.parent = rig
    rings.append((o, r))

R_MAX = R0 + (N_RINGS - 1) * R_STEP

# ---------- アニメーション（隆起の呼吸が内→外へ伝播：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    for o, r in rings:
        phase = (r / R_MAX) * 2 * math.pi * LAG_WAVES        # 半径で位相ラグ
        b01 = 0.5 * (1 - math.cos(2 * math.pi * BREATHS * t - phase))  # 0..1
        zs = Z_MIN + (Z_MAX - Z_MIN) * b01
        o.scale = (1.0, 1.0, zs)
        o.keyframe_insert(data_path="scale", index=2, frame=f)
    # 芯はゆっくり呼吸
    bc = 0.5 * (1 - math.cos(2 * math.pi * BREATHS * t))
    core_bsdf.inputs["Emission Strength"].default_value = 1.6 + 0.6 * bc
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    core_light.data.energy = CORE_LIGHT_W * (0.7 + 0.5 * bc)
    core_light.data.keyframe_insert(data_path="energy", frame=f)

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
                      0.1, (0.15, -1.35, 0.36), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.35, 0.18), "logo")
study = add_caption("MIDDLE STUDY 014 — NENRIN", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜015と同一＝シリーズの一貫性） ----------
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
bpy.ops.object.camera_add(location=(0.55, -12.0, 2.3))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, CENTER_Z + 0.02))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = core
cam.data.dof.aperture_fstop = 7.0
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_nenrin.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith("ring_") or o.name in ("disc", "core"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_nenrin.glb"),
        export_format='GLB', use_selection=True,
        export_animations=True, export_yup=True)
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

if "hero480" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 48
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero_check.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero_check render done")

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
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
