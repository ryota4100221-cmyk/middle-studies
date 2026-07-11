# =============================================================
# monaka design. — MIDDLE STUDY 008 "SUKIMA"
# 2枚の黒い壁が狭い隙間（スリット）を挟んで並ぶ。その谷間を、
# ライム #A5E02E の光の粒が呼吸するように上下へ行き来する。
# 壁は光を隠し、スリットから漏れる光だけが移動する。
# 隙間の中に、光がある。狭さの奥に、灯りが通う。
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

WALL_W = 0.9          # 壁の幅
WALL_H = 1.75         # 壁の高さ
WALL_D = 0.6          # 壁の奥行き
GAP = 0.2             # 隙間（スリット）の幅

N_ORBS = 3            # 光の粒の数
ORB_R = 0.1           # 粒の半径（隙間に収まる）
ORB_AMP = 0.58        # 上下振動の振幅
ORB_CYCLES = 2        # 往復回数（sin＝完全ループ）
ORB_EMIT = 3.4        # 粒の発光強度
ORB_Y = -0.14         # 粒の奥行き位置（スリット開口の手前寄り＝正面へ強く漏れる）
SLIT_LIGHT_W = 55     # 隙間の実光源（壁内面と床へ光をこぼす）

CENTER_Z = 1.25       # 壁の中心高さ
TILT_X = math.radians(6)
TILT_Z = math.radians(14)   # ほぼ正対＋わずかに振って隙間の奥行きを見せる

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 11      # ヒーロー：3粒が上・中・下に均等に散る瞬間


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

# 黒い壁（マット＝黒を黒く保つ）
mat_wall, b = make_principled("wall_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.44
b.inputs["Specular IOR Level"].default_value = 0.22

# 発光する光の粒
mat_orb, orb_bsdf = make_principled("orb_lime")
orb_bsdf.inputs["Base Color"].default_value = LIME
orb_bsdf.inputs["Emission Color"].default_value = LIME
orb_bsdf.inputs["Emission Strength"].default_value = ORB_EMIT
orb_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- リグ（原点。隙間の奥が見えるよう静的に振る） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "SukimaRig"
rig.rotation_euler = (TILT_X, 0, TILT_Z)

def add_wall(name, xpos):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(xpos, 0, CENTER_Z))
    o = bpy.context.active_object
    o.name = name
    o.scale = (WALL_W, WALL_D, WALL_H)
    bpy.ops.object.transform_apply(scale=True)
    # PITFALL#7-b: --factory-startupではtransform_apply(scale)がワールド焼き込み
    # ＆location→0。位置は既に正しいので再設定しない。
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.012
    bev.segments = 2
    o.data.materials.append(mat_wall)
    o.parent = rig
    return o

wall_l = add_wall("wall_l", -(GAP / 2 + WALL_W / 2))
wall_r = add_wall("wall_r", +(GAP / 2 + WALL_W / 2))

# ---------- 光の粒（発光球）＋隙間の実光源 ----------
orbs = []
for i in range(N_ORBS):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ORB_R, location=(0, ORB_Y, CENTER_Z),
                                         segments=32, ring_count=16)
    o = bpy.context.active_object
    o.name = f"orb_{i}"
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat_orb)
    o.parent = rig
    orbs.append(o)

# 隙間中央のライトは中程の粒に追従（壁内面・床へ漏光）
bpy.ops.object.light_add(type='POINT', location=(0, 0, CENTER_Z))
slit_light = bpy.context.active_object
slit_light.name = "slit_light"
slit_light.data.energy = SLIT_LIGHT_W
slit_light.data.color = (LIME[0], LIME[1], LIME[2])
slit_light.data.shadow_soft_size = 0.06
slit_light.parent = rig

# ---------- アニメーション（粒が隙間を上下に行き来：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    for i, o in enumerate(orbs):
        ph = i / N_ORBS                      # 位相ずらしで流れる粒
        z = CENTER_Z + ORB_AMP * math.sin(2 * math.pi * ORB_CYCLES * t + ph * 2 * math.pi)
        o.location = (0, ORB_Y, z)
        o.keyframe_insert(data_path="location", index=2, frame=f)
    # ライトは先頭の粒に追従
    zc = CENTER_Z + ORB_AMP * math.sin(2 * math.pi * ORB_CYCLES * t)
    slit_light.location = (0, ORB_Y, zc)
    slit_light.keyframe_insert(data_path="location", index=2, frame=f)

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
study = add_caption("MIDDLE STUDY 008 — SUKIMA", 0.045, (0.15, -1.35, 0.055), "study")

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
bpy.ops.object.camera_add(location=(0.55, -11.3, 2.15))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, CENTER_Z + 0.04))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = orbs[0]
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_sukima.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith(("wall_", "orb_")))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_sukima.glb"),
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
