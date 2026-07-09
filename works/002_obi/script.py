# =============================================================
# monaka design. — MIDDLE STUDY 002 "OBI"
# 黒いメビウスの帯。縁だけがライム #A5E02E に発光し、
# その光の線は帯を二周する「一本の線」になる。
# 回転すると、ねじれの中を光の縁が旅する。
#
# 実行:
#   Blender --background --python monaka_ribbon.py -- <mode...>
#   modes: test | still | anim | glb | blend
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

RC = 0.85       # 帯の中心円半径
W = 0.42        # 帯の幅
T = 0.085       # 帯の厚み（＝発光する縁の太さ）
U_SEGS = 288    # 周方向の分割数
CENTER_Z = 1.42 # 浮遊高さ
TILT = math.radians(62)  # 帯の傾き

FPS = 24
N_FRAMES = 144  # 6秒 完全ループ（360°回転）
STILL_FRAME = 1

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

# 黒い帯（サテン仕上げ）
mat_band, b = make_principled("obi_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.26
b.inputs["Coat Weight"].default_value = 0.3
b.inputs["Coat Roughness"].default_value = 0.12

# 発光する縁
mat_edge, edge_bsdf = make_principled("edge_lime")
edge_bsdf.inputs["Base Color"].default_value = LIME
edge_bsdf.inputs["Emission Color"].default_value = LIME
edge_bsdf.inputs["Emission Strength"].default_value = 2.6
edge_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- メビウスの帯（bmeshで手続き生成） ----------
# 断面（幅W×厚みT の長方形）を中心円に沿って半回転(π)ねじりながら掃引。
# 長方形は180°対称なので u=2π で断面が自分自身に一致し、閉じたソリッドになる。
# 断面の角 k は一周後に角 (k+2)%4 に写る → 幅広面同士・縁面同士が連続し、
# 縁のライム面は「帯を二周する一本の光の線」になる。
bm = bmesh.new()
w, t = W / 2, T / 2
corners = [(-w, -t), (w, -t), (w, t), (-w, t)]
rings = []
for i in range(U_SEGS):
    u = 2 * math.pi * i / U_SEGS
    phi = u / 2  # 半ねじり
    r_hat = Vector((math.cos(u), math.sin(u), 0))
    z_hat = Vector((0, 0, 1))
    center = RC * r_hat
    ring = []
    for a, b_ in corners:
        off = a * (math.cos(phi) * r_hat + math.sin(phi) * z_hat) \
            + b_ * (-math.sin(phi) * r_hat + math.cos(phi) * z_hat)
        ring.append(bm.verts.new(center + off))
    rings.append(ring)

for i in range(U_SEGS):
    j = (i + 1) % U_SEGS
    shift = 2 if j == 0 else 0  # 一周の継ぎ目で断面の角を半回転ぶんずらして接続
    for k in range(4):
        k2 = (k + 1) % 4
        f = bm.faces.new((
            rings[i][k], rings[i][k2],
            rings[j][(k2 + shift) % 4], rings[j][(k + shift) % 4]))
        f.smooth = True
        # k=0,2: 幅広面（黒） / k=1,3: 縁（ライム発光）
        f.material_index = 0 if k in (0, 2) else 1

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
mesh = bpy.data.meshes.new("mobius")
bm.to_mesh(mesh)
bm.free()

band = bpy.data.objects.new("obi", mesh)
scene.collection.objects.link(band)
band.data.materials.append(mat_band)   # index 0
band.data.materials.append(mat_edge)   # index 1
bpy.context.view_layer.objects.active = band
band.select_set(True)
try:
    bpy.ops.object.shade_auto_smooth(angle=0.7)  # 掃引方向は滑らか、90°角は鋭く
except Exception:
    bpy.ops.object.shade_smooth()

# ---------- リグ（傾き＋回転） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "ObiRig"
rig.rotation_euler = (TILT, 0, math.radians(12))
band.parent = rig

# ---------- アニメーション（360°回転 = 完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

# 毎フレームにキーを打つ（Blender 5はaction.fcurves直アクセス廃止のため、
# 補間に頼らず値そのものを線形に刻む）
for f in range(1, N_FRAMES + 1):
    band.rotation_euler.z = 2 * math.pi * (f - 1) / N_FRAMES
    band.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

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
study = add_caption("MIDDLE STUDY 002 — OBI", 0.045, (0.15, -1.3, 0.06), "study")

# ---------- ライティング（001と同一セットアップ＝シリーズの一貫性） ----------
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
bpy.ops.object.camera_add(location=(0.55, -8.3, 1.95))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, CENTER_Z + 0.05))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = band
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
        filepath=os.path.join(OUT, "obi.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name == "obi")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "obi.glb"),
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
    scene.render.filepath = os.path.join(OUT, "obi_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "obi_hero.png")
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
    scene.render.filepath = os.path.join(OUT, "obi_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
