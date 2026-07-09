# =============================================================
# monaka design. — "THE FILLING"
# 黒いウエハース（スライス積層の球体）が真ん中から開き、
# ライム #A5E02E の餡が発光する。
# "Designing the Middle of Your Story."
#
# 実行:
#   Blender --background --python monaka_filling.py -- <mode...>
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

N_SLICES = 44          # 球を構成するスライス数
R = 1.0                # 球の半径
GAP_RATIO = 0.26       # スライス間の隙間（光の漏れ）
CENTER_Z = 1.25        # 球の浮遊高さ
OPEN_ZONE = 0.38       # |z| < これ のスライスが開く
OPEN_MAX = 0.55        # 赤道ギャップの最大量（上下合計）
CORE_R = 0.68          # 発光コアの半径

FPS = 24
N_FRAMES = 120         # 5秒 完全ループ
STILL_FRAME = 58       # 静止画は開ききった瞬間

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

# 黒ウエハース（マット / サテンの2種を交互に）
mat_matte, b = make_principled("wafer_matte")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.48
b.inputs["Specular IOR Level"].default_value = 0.35

mat_satin, b = make_principled("wafer_satin")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.22
b.inputs["Coat Weight"].default_value = 0.25
b.inputs["Coat Roughness"].default_value = 0.15

# ライムの餡（発光）
mat_core, core_bsdf = make_principled("filling_lime")
core_bsdf.inputs["Base Color"].default_value = LIME
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Emission Strength"].default_value = 3.0
core_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション（濃グレー）
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- 彫刻の親 ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "Sculpture"

def shade(obj):
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            pass

# ---------- スライス群（手続き生成） ----------
pitch = 2 * R / N_SLICES
slices = []  # (obj, z_norm, is_opening, amp, phase)
for i in range(N_SLICES):
    z = -R + pitch * (i + 0.5)              # スライス中心（ローカル）
    rr = R * R - z * z
    if rr <= 0.004:                          # 極付近の極小スライスは省く
        continue
    r = math.sqrt(rr)
    thick = pitch * (1 - GAP_RATIO)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=128, radius=r, depth=thick, location=(0, 0, z))
    d = bpy.context.active_object
    d.name = f"slice_{i:02d}"
    bev = d.modifiers.new("Bevel", "BEVEL")
    bev.width = min(0.008, thick * 0.3)
    bev.segments = 2
    shade(d)
    d.data.materials.append(mat_matte if i % 2 == 0 else mat_satin)
    d.parent = rig

    zn = z / R
    # 上下に裂けるアコーディオン：赤道に近いスライスほど大きく離れる
    amp = math.copysign(1.0, zn) * 0.5 * OPEN_MAX * (1 - abs(zn)) ** 0.8
    # 赤道から極へ波が伝播する位相遅れ
    phase = abs(zn) * 0.6
    slices.append((d, z, amp, phase))

# ---------- 発光コア ----------
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=96, ring_count=48, radius=CORE_R, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "filling_core"
shade(core)
core.data.materials.append(mat_core)
core.parent = rig

# ---------- アニメーション（完全ループ / 開いて閉じる呼吸） ----------
def openness(t01, phase):
    """0..1 → 0..1、cosベースなので周期的（完全ループ保証）"""
    return 0.5 * (1 - math.cos(2 * math.pi * t01 - phase))

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for d, z0, amp, phase in slices:
    for f in range(1, N_FRAMES + 1):
        t01 = (f - 1) / N_FRAMES
        d.location.z = z0 + amp * openness(t01, phase)
        d.keyframe_insert(data_path="location", index=2, frame=f)
    # 毎フレームにキーを打っているため補間設定は不要
    # （Blender 5 では action.fcurves への直接アクセスが廃止された）

# コアの発光も呼吸に同期（開くほど強く）
es = core_bsdf.inputs["Emission Strength"]
for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    es.default_value = 1.5 + 1.5 * openness(t01, 0.0)
    es.keyframe_insert(data_path="default_value", frame=f)

# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

def add_caption(body, size, loc, name):
    """カメラ正対のフローティングキャプション（向きは後でカメラに合わせる）"""
    bpy.ops.object.text_add(location=loc)
    t = bpy.context.active_object
    t.name = name
    t.data.body = body
    t.data.size = size
    t.data.align_x = 'CENTER'
    try:
        t.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    t.data.materials.append(mat_text)
    return t

tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.36), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.18), "logo")

# ---------- ライティング ----------
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

# ワールド（明るいグレー環境光）
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
look = Vector((0.1, 0, CENTER_Z + 0.17))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = core
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam

# キャプションをカメラに正対させる
for t in (tagline, logo):
    t.rotation_euler = cam.rotation_euler

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
            try:
                glare.inputs["Type"].default_value = 'Bloom'
            except Exception:
                pass
        glare.inputs["Threshold"].default_value = 1.2
        glare.inputs["Strength"].default_value = 0.5
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
        filepath=os.path.join(OUT, "monaka_filling.blend"))
    print(">> saved .blend")

if "glb" in modes:
    # 開いた状態で書き出し（アニメーション付き）
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith("slice_") or o.name == "filling_core")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_filling.glb"),
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
