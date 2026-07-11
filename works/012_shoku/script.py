# =============================================================
# monaka design. — MIDDLE STUDY 012 "SHOKU"
# 奥にライム #A5E02E の発光円盤（太陽）、手前に少し大きい黒い円盤（月）。
# 月が太陽をほぼ覆い、縁からライムの細い三日月だけがのぞく。
# 月が太陽の周りを1周しながら、三日月の太さがcosで呼吸する。
# 光の三日月が縁を一周し、痩せては満ちる——蝕。真ん中の光が隠れ、また現れる。
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

R_SUN = 1.0           # 太陽（発光円盤）の半径
R_MOON = 1.05         # 月（黒円盤）の半径（少し大きく＝片側だけ三日月）
SUN_Y = 0.05          # 太陽の奥行き位置（カメラは-Y側）
MOON_Y = -0.05        # 月の奥行き位置（手前）
DISK_D_SUN = 0.05     # 円盤の厚み
DISK_D_MOON = 0.07

D0 = 0.30             # 月中心のオフセット半径（三日月の最大の太さ側）
D_BREATH = 2          # 三日月の呼吸回数（cos＝完全ループ）
ORBIT_TURNS = 1       # 月が太陽を回る周回数（整数＝完全ループ）

SUN_EMIT = 2.4        # 太陽の発光強度（呼吸で±する中央値）

CENTER_Z = 1.28       # 蝕の浮遊高さ（中心）
TILT_X = math.radians(13)   # 奥行きを見せる静的傾き
TILT_Z = math.radians(-7)

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 20      # ヒーロー：三日月が左下・太め（蝕らしいクレセント）


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

# 黒い月（マット＝黒を黒く保つ）
mat_moon, b = make_principled("moon_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.46
b.inputs["Specular IOR Level"].default_value = 0.22

# 発光する太陽
mat_sun, sun_bsdf = make_principled("sun_lime")
sun_bsdf.inputs["Base Color"].default_value = LIME
sun_bsdf.inputs["Emission Color"].default_value = LIME
sun_bsdf.inputs["Emission Strength"].default_value = SUN_EMIT
sun_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- リグ（原点。蝕全体を静的に傾け奥行きを見せる） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "ShokuRig"
rig.rotation_euler = (TILT_X, 0, TILT_Z)

def add_disk(name, radius, depth, y, mat):
    """XZ平面に立つ円盤（法線±Y＝カメラに正対）。"""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=128, location=(0, y, CENTER_Z))
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = (math.radians(90), 0, 0)  # 軸をZ→Yへ倒し円面を正対
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.01
    bev.segments = 2
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    o.parent = rig
    return o

sun = add_disk("sun", R_SUN, DISK_D_SUN, SUN_Y, mat_sun)
moon = add_disk("moon", R_MOON, DISK_D_MOON, MOON_Y, mat_moon)

# ---------- アニメーション（月のオービット＋三日月の呼吸：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    """0..1 → 0..1、cosベース＝完全ループ"""
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    br = osc(t, D_BREATH)                     # 三日月の太さ 0..1
    d = D0 * (0.55 + 0.45 * br)               # 月中心オフセット半径
    phi = 2 * math.pi * ORBIT_TURNS * t       # オービット角
    # 月をXZ平面（円盤の面内）で公転させる＝三日月が縁を一周
    moon.location.x = d * math.cos(phi)
    moon.location.z = CENTER_Z + d * math.sin(phi)
    moon.keyframe_insert(data_path="location", index=0, frame=f)
    moon.keyframe_insert(data_path="location", index=2, frame=f)
    # 三日月が太いほど強く光る
    sun_bsdf.inputs["Emission Strength"].default_value = 1.7 + 0.85 * br
    sun_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)

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
study = add_caption("MIDDLE STUDY 012 — SHOKU", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜006と同一＝シリーズの一貫性） ----------
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
bpy.ops.object.camera_add(location=(0.55, -11.8, 2.05))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, CENTER_Z + 0.02))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = moon
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
        filepath=os.path.join(OUT, "monaka_shoku.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("sun", "moon"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_shoku.glb"),
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

if "test2" in modes:
    # アニメ検証：三日月が縁を回り呼吸するか別フレームも1枚
    scene.frame_set(1)
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_f1.png")
    bpy.ops.render.render(write_still=True)
    print(">> test_f1 render done")

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
