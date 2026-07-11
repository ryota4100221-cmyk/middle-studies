# =============================================================
# monaka design. — MIDDLE STUDY 015 "KESSHOU"
# 中心のライム #A5E02E の発光コアを、12本の黒い結晶柱（六角柱＋尖端）が
# 正20面体の頂点方向に放射して囲む。結晶が縮むとコアを覆い真っ黒な塊に、
# 外へ成長すると継ぎ目が開いて中心の光が漏れる。cos伸縮の完全ループ。
# 結晶の芯に、光がある。成長して、はじめて漏れる。
# "Designing the Middle of Your Story."
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
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

CRYS_RB = 0.17        # 結晶の六角基部半径
CRYS_RT = 0.82        # 先端側の半径比（テーパー）
CRYS_LBODY = 0.52     # 柱部の長さ
CRYS_LTIP = 0.32      # 尖端の長さ

CORE_R = 0.28         # 中心コア（発光）の半径（黒を主役に：小さめの芯）
R_IN = 0.18           # 結晶基部の最小距離（縮＝コアを抱き込み継ぎ目だけ漏れる）
R_OUT = 0.52          # 最大距離（成長＝継ぎ目が開きコアが見える）
BREATHS = 2           # 伸縮の呼吸回数（cos＝完全ループ）

CORE_EMIT = 1.5       # コアの発光強度（呼吸で±する中央値）
CORE_LIGHT_W = 22     # 内部ポイントライト（継ぎ目から光をこぼす）

CENTER_Z = 1.28
TILT_X = math.radians(16)
TILT_Z = math.radians(-20)

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 31      # ヒーロー：最も成長し継ぎ目からコアが漏れる瞬間


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

# 黒い結晶（黒を黒く保ちつつ鉱物のわずかな艶。コートは弱めでクローム化を回避）
mat_crys, b = make_principled("crystal_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.40
b.inputs["Specular IOR Level"].default_value = 0.26
b.inputs["Coat Weight"].default_value = 0.06
b.inputs["Coat Roughness"].default_value = 0.3

# 発光するコア
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

# ---------- リグ（原点。結晶塊を角が見えるよう静的に傾ける） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "KesshouRig"
rig.rotation_euler = (TILT_X, 0, TILT_Z)

# ---------- 結晶メッシュ（六角柱＋尖端。+Z方向・基部を原点に） ----------
def make_crystal_mesh():
    bm = bmesh.new()
    base, top = [], []
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        ca, sa = math.cos(a), math.sin(a)
        base.append(bm.verts.new((CRYS_RB * ca, CRYS_RB * sa, 0.0)))
        top.append(bm.verts.new((CRYS_RB * CRYS_RT * ca,
                                 CRYS_RB * CRYS_RT * sa, CRYS_LBODY)))
    apex = bm.verts.new((0.0, 0.0, CRYS_LBODY + CRYS_LTIP))
    bm.faces.new(list(reversed(base)))                 # 基部キャップ
    for k in range(6):
        k2 = (k + 1) % 6
        bm.faces.new([base[k], base[k2], top[k2], top[k]])   # 柱側面
        bm.faces.new([top[k], top[k2], apex])                # 尖端
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("crystal")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_crys)
    return me

crystal_mesh = make_crystal_mesh()

# 正20面体の12頂点方向（正規化）＝放射方向
PHI = (1 + 5 ** 0.5) / 2
_ico = [(0, 1, PHI), (0, 1, -PHI), (0, -1, PHI), (0, -1, -PHI),
        (1, PHI, 0), (1, -PHI, 0), (-1, PHI, 0), (-1, -PHI, 0),
        (PHI, 0, 1), (PHI, 0, -1), (-PHI, 0, 1), (-PHI, 0, -1)]
DIRS = [Vector(v).normalized() for v in _ico]

crystals = []  # (obj, dir)
for i, d in enumerate(DIRS):
    o = bpy.data.objects.new(f"crystal_{i:02d}", crystal_mesh)
    scene.collection.objects.link(o)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()  # +Zをdへ
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.008
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(25)
    o.parent = rig
    crystals.append((o, d))

# ---------- 中心コア（発光）＋内部ポイントライト ----------
bpy.ops.mesh.primitive_ico_sphere_add(radius=CORE_R, subdivisions=3,
                                      location=(0, 0, CENTER_Z))
core = bpy.context.active_object
core.name = "core"
bpy.ops.object.shade_smooth()
core.data.materials.append(mat_core)
core.parent = rig

bpy.ops.object.light_add(type='POINT', location=(0, 0, CENTER_Z))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.energy = CORE_LIGHT_W
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.12
core_light.parent = rig

# ---------- アニメーション（結晶の伸縮呼吸＋コアの発光：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

center = Vector((0, 0, CENTER_Z))
for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    grow = osc(t, BREATHS)                    # 0=縮 1=成長
    dist = R_IN + (R_OUT - R_IN) * grow
    for o, d in crystals:
        o.location = center + d * dist
        o.keyframe_insert(data_path="location", frame=f)
    core_bsdf.inputs["Emission Strength"].default_value = 1.1 + 0.7 * grow
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    core_light.data.energy = CORE_LIGHT_W * (0.35 + 0.85 * grow)
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
study = add_caption("MIDDLE STUDY 015 — KESSHOU", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜013と同一＝シリーズの一貫性） ----------
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
cam.data.dof.focus_object = core
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_kesshou.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith("crystal_") or o.name == "core")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_kesshou.glb"),
        export_format='GLB', use_selection=True,
        export_animations=True, export_yup=True, export_apply=True)
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
    scene.frame_set(1)  # 縮んでコアを覆った状態を確認
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_closed.png")
    bpy.ops.render.render(write_still=True)
    print(">> test_closed render done")

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
