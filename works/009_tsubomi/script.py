# =============================================================
# monaka design. — MIDDLE STUDY 009 "TSUBOMI"
# 黒い花弁が閉じた蕾。花弁が外へ倒れて開くと中心のライム #A5E02E の
# コアが現れ、また閉じて光を包む。cosで一度ゆっくり咲いて閉じる完全ループ。
# 蕾の芯に、光がある。開いて、はじめて灯る。
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

N_PETALS = 6
PETAL_L = 0.72        # 花弁の長さ
PETAL_HW = 0.2        # 花弁の最大半幅（広め＝重なって花らしく）
PETAL_CURL = 0.17     # 先端が内へ反る量
PETAL_CUP = 0.45      # 幅方向のカップ（内側へえぐる）
PETAL_THICK = 0.02
NU, NW = 26, 12       # 花弁メッシュ分割

BASE_R = 0.10         # 花弁基部リングの半径
BASE_DZ = -0.30       # 花弁基部の高さオフセット（中心より下）
THETA_CLOSED = math.radians(7)    # 閉じたときの花弁の開き角
THETA_OPEN = math.radians(50)     # 開いたときの開き角（開きすぎない＝カップを保つ）

CORE_R = 0.17         # 中心コア（発光）の半径
CORE_EMIT = 2.2       # コアの発光強度（開くほど強く）
CORE_LIGHT_W = 26     # 内部ポイントライト

CENTER_Z = 1.28
BLOOMS = 1            # ループ中の開閉回数（1＝ゆっくり一度咲いて閉じる）

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 61      # ヒーロー：満開でコアが最も見える瞬間


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

# 黒い花弁（マット＋ごく弱いコートで花弁の艶。クローム化は回避）
mat_petal, b = make_principled("petal_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.25
b.inputs["Coat Weight"].default_value = 0.08
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

# ---------- リグ ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "TsubomiRig"

# ---------- 花弁メッシュ（カップ状の葉形。基部を原点・+Zへ伸びる） ----------
def petal_point(u, w):
    hw = PETAL_HW * (math.sin(math.pi * max(1e-4, min(1, u))) ** 0.6)  # 葉形の幅
    xc = -PETAL_CURL * (u ** 1.8)            # 先端が内(-X)へ反る
    z = PETAL_L * u
    xcup = PETAL_CUP * (w * w) * (hw / PETAL_HW)   # 幅の縁が内(-X)へえぐれる
    return (xc + xcup, w * hw, z)

def make_petal_mesh():
    bm = bmesh.new()
    grid = []
    for iu in range(NU + 1):
        u = iu / NU
        row = []
        for iw in range(NW + 1):
            w = -1 + 2 * iw / NW
            row.append(bm.verts.new(petal_point(u, w)))
        grid.append(row)
    for iu in range(NU):
        for iw in range(NW):
            bm.faces.new([grid[iu][iw], grid[iu][iw + 1],
                          grid[iu + 1][iw + 1], grid[iu + 1][iw]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("petal")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_petal)
    return me

petal_mesh = make_petal_mesh()

# 花弁の枢軸（基部）ピボットをリング状に配置。open角をアニメ
pivots = []
for i in range(N_PETALS):
    a = 2 * math.pi * i / N_PETALS
    piv = bpy.data.objects.new(f"pivot_{i}", None)  # empty
    scene.collection.objects.link(piv)
    piv.empty_display_size = 0.05
    piv.location = (BASE_R * math.cos(a), BASE_R * math.sin(a), CENTER_Z + BASE_DZ)
    piv.rotation_euler = (0, THETA_CLOSED, a)   # (X, Y=開き角, Z=方位)
    piv.parent = rig
    o = bpy.data.objects.new(f"petal_{i}", petal_mesh)
    scene.collection.objects.link(o)
    sol = o.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = PETAL_THICK
    sol.offset = 0
    o.parent = piv
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_smooth()
    o.select_set(False)
    pivots.append((piv, a))

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
core_light.data.shadow_soft_size = 0.1
core_light.parent = rig

# ---------- アニメーション（花弁の開閉＋コアの発光：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    op = osc(t, BLOOMS)                       # 0=閉 1=開
    theta = THETA_CLOSED + (THETA_OPEN - THETA_CLOSED) * op
    for piv, a in pivots:
        piv.rotation_euler = (0, theta, a)
        piv.keyframe_insert(data_path="rotation_euler", index=1, frame=f)
    core_bsdf.inputs["Emission Strength"].default_value = 1.2 + 0.85 * op
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    core_light.data.energy = CORE_LIGHT_W * (0.3 + 0.9 * op)
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
study = add_caption("MIDDLE STUDY 009 — TSUBOMI", 0.045, (0.15, -1.35, 0.055), "study")

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

# ---------- カメラ（少し上から蕾の中を覗く） ----------
bpy.ops.object.camera_add(location=(0.45, -7.5, 2.4))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, CENTER_Z + 0.0))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_tsubomi.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith("petal_") or o.name == "core")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_tsubomi.glb"),
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
    scene.frame_set(1)  # 閉じた蕾（光が隠れる）を確認
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
