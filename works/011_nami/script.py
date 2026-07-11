# =============================================================
# monaka design. — MIDDLE STUDY 011 "NAMI"
# 黒い水面の中心から、ライム #A5E02E の光の波紋（同心リング）が
# 外へ広がり続ける。リングは中心で生まれ中程で最も明るく、
# 外周で消える。frac(i/N+t) で位置が循環し数学的に完全ループ。
# 水面の中心に、光がある。波となって、外へ伝わる。
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

N_RINGS = 5           # 同時に見える波紋リングの数（少なめ＝黒い間を残す）
R_MAX = 1.28          # 波紋が広がる最大半径
RING_TUBE = 0.023     # リング（チューブ）の太さ（細め＝繊細な波紋）
RING_EMIT = 2.6       # リングの発光強度（中央値・envで包絡）
POND_R = 1.42         # 黒い水面の半径
SRC_R = 0.07          # 中心の光源の芯（小さめ＝Glareの箱状アーティファクトを抑える）
SRC_EMIT = 1.7

WAVE_CYCLES = 1       # ループ中に波紋が外へ進む回数（1＝連続伝播で完全ループ）

CENTER_Z = 1.28
TILT_X = math.radians(44)   # 水面を手前へ倒してパースを付ける
TILT_Z = math.radians(-6)

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 30      # ヒーロー：波紋が均等に広がった瞬間


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

# 黒い水面（マット＝黒を黒く保つ。エリアライトの四角い映り込みを避けるため艶は抑える）
mat_pond, b = make_principled("pond_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 1.0
b.inputs["Specular IOR Level"].default_value = 0.0

# 発光する中心の芯
mat_src, src_bsdf = make_principled("src_lime")
src_bsdf.inputs["Base Color"].default_value = LIME
src_bsdf.inputs["Emission Color"].default_value = LIME
src_bsdf.inputs["Emission Strength"].default_value = SRC_EMIT
src_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- 傾きリグ（CENTER_Zで傾け、その場で水面を倒す） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "NamiRig"
rig.rotation_euler = (TILT_X, 0, TILT_Z)

# ---------- 黒い水面 ----------
bpy.ops.mesh.primitive_cylinder_add(radius=POND_R, depth=0.04, vertices=128,
                                    location=(0, 0, -0.02))
pond = bpy.context.active_object
pond.name = "pond"
bev = pond.modifiers.new("Bevel", "BEVEL")
bev.width = 0.01
bev.segments = 2
bpy.ops.object.shade_smooth()
pond.data.materials.append(mat_pond)
pond.parent = rig

# ---------- 中心の光源（面光源：集中した点にせずGlareの箱/十字を出さない） ----------
# 中心は最内リングが生まれる場所。集中発光の芯を置くとGlareのFFT箱＋streak十字が
# 均一な暗い水面上で目立つため、芯オブジェクトは置かず、広く柔らかいスポットのみ。
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.12))
src_light = bpy.context.active_object
src_light.name = "src_light"
src_light.data.energy = 22
src_light.data.color = (LIME[0], LIME[1], LIME[2])
src_light.data.shadow_soft_size = 0.5   # 大きめ＝広く柔らかい中心の灯り
src_light.parent = rig

# ---------- 波紋リング（単位トーラスをXYで拡大＝外へ伝播） ----------
rings = []
for i in range(N_RINGS):
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0, 0, 0.03),
                                     major_radius=1.0, minor_radius=RING_TUBE,
                                     major_segments=128, minor_segments=10)
    o = bpy.context.active_object
    o.name = f"ring_{i}"
    bpy.ops.object.shade_smooth()
    mat, bsdf = make_principled(f"ring_lime_{i}")
    bsdf.inputs["Base Color"].default_value = LIME
    bsdf.inputs["Emission Color"].default_value = LIME
    bsdf.inputs["Emission Strength"].default_value = RING_EMIT
    bsdf.inputs["Roughness"].default_value = 0.4
    o.data.materials.append(mat)
    o.visible_shadow = False   # 発光リングは影を落とさない
    o.parent = rig
    rings.append((o, bsdf))

# ---------- アニメーション（波紋が中心→外へ伝播：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    for i, (o, bsdf) in enumerate(rings):
        u = (i / N_RINGS + WAVE_CYCLES * t) % 1.0      # 0..1 循環＝完全ループ
        rr = max(1e-3, u * R_MAX)
        env = math.sin(math.pi * u) ** 2               # 中心/外周で0、中程で1（鋭め）
        o.scale = (rr, rr, 1.0)                         # XYで拡大＝半径rr
        o.keyframe_insert(data_path="scale", frame=f)
        bsdf.inputs["Emission Strength"].default_value = RING_EMIT * (0.06 + 0.94 * env)
        bsdf.inputs["Emission Strength"].keyframe_insert(
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
study = add_caption("MIDDLE STUDY 011 — NAMI", 0.045, (0.15, -1.35, 0.055), "study")

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
bpy.ops.object.camera_add(location=(0.55, -12.2, 2.25))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, CENTER_Z + 0.02))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = pond
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_nami.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith("ring_") or o.name == "pond")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_nami.glb"),
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
