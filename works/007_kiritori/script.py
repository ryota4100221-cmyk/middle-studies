# =============================================================
# monaka design. — MIDDLE STUDY 007 "KIRITORI"
# 黒い立方体の中心から球をくり抜く。球の半径が呼吸し、面の距離を
# 超えると各面に円い窓が開き、中のライム #A5E02E に光る球状空洞の
# 内壁がのぞく。閉じれば真っ黒な立方体＝光は隠れ、また開いて現れる。
# 立方体の芯に、光がある。切り取られて、はじめて見える。
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

CUBE_HALF = 0.82      # 立方体の半辺（面までの距離＝0.82）
R_MIN = 0.76          # くり抜き球の最小半径（<0.82＝ほぼ塞がる）
R_MAX = 1.06          # 最大半径（>0.82で窓が開く・<1.13で辺は残る）
BREATHS = 2           # 開閉の呼吸回数（cos＝完全ループ）

CORE_EMIT = 1.8       # 空洞内壁の発光強度（呼吸で±する中央値）
CORE_LIGHT_W = 26     # 内部ポイントライト（窓から光をこぼす）

CENTER_Z = 1.28       # 立方体の浮遊高さ（中心）
TILT_X = math.radians(20)   # 角を見せる静的傾き
TILT_Z = math.radians(-24)

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 28      # ヒーロー：窓が大きく開き内部が最も見える辺り


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

# 黒い立方体外殻（マット＝黒を黒く保つ）
mat_cube, b = make_principled("cube_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.44
b.inputs["Specular IOR Level"].default_value = 0.22

# 発光する空洞内壁
mat_core, core_bsdf = make_principled("cavity_lime")
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

# ---------- リグ（原点。立方体を角が見えるよう静的に傾ける） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "KiritoriRig"
rig.rotation_euler = (TILT_X, 0, TILT_Z)

# ---------- 立方体（外殻・黒） ----------
bpy.ops.mesh.primitive_cube_add(size=CUBE_HALF * 2, location=(0, 0, CENTER_Z))
cube = bpy.context.active_object
cube.name = "cube"
cube.data.materials.append(mat_cube)   # slot0: 黒

# ---------- くり抜き球（カッター・ライム内壁） ----------
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, CENTER_Z),
                                     segments=96, ring_count=48)
cutter = bpy.context.active_object
cutter.name = "cutter"
bpy.ops.object.shade_smooth()
cutter.data.materials.append(mat_core)  # カッターの面＝ライム（転写で内壁に乗る）
cutter.hide_render = True                # カッター自体は描画しない（ブーリアンには使われる）

# 立方体にブーリアン（差）＋マテリアル転写で内壁をライムに
boo = cube.modifiers.new("Cut", "BOOLEAN")
boo.operation = 'DIFFERENCE'
boo.solver = 'EXACT'
boo.object = cutter
try:
    boo.material_mode = 'TRANSFER'   # カッターのマテリアルを切断面へ転写
except Exception:
    pass
# 窓の縁をわずかに面取り（ブーリアンの後）
bev = cube.modifiers.new("Bevel", "BEVEL")
bev.width = 0.012
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(30)

cube.parent = rig
cutter.parent = rig  # 立方体と一緒に傾く（相対位置固定）

# ---------- 内部ポイントライト（窓から光をこぼす） ----------
bpy.ops.object.light_add(type='POINT', location=(0, 0, CENTER_Z))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.energy = CORE_LIGHT_W
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.15
core_light.parent = rig

# ---------- アニメーション（球の呼吸で窓が開閉：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    op = osc(t, BREATHS)                      # 0=閉 1=開
    r = R_MIN + (R_MAX - R_MIN) * op
    cutter.scale = (r, r, r)                  # 球半径＝ブーリアンが毎フレーム再計算
    cutter.keyframe_insert(data_path="scale", frame=f)
    # 開くほど内壁が強く光り、内部ライトも強まる
    core_bsdf.inputs["Emission Strength"].default_value = 1.25 + 0.7 * op
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    core_light.data.energy = CORE_LIGHT_W * (0.4 + 0.8 * op)
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
study = add_caption("MIDDLE STUDY 007 — KIRITORI", 0.045, (0.15, -1.35, 0.055), "study")

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
cam.data.dof.focus_object = cube
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_kiritori.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    # ブーリアン適用済みメッシュをエクスポートするためcubeを評価してGLBへ
    for o in bpy.data.objects:
        o.select_set(o.name == "cube")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_kiritori.glb"),
        export_format='GLB', use_selection=True,
        export_animations=True, export_yup=True,
        export_apply=True)  # モディファイア適用（ブーリアン込み）
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
    scene.frame_set(1)  # 閉じた状態（真っ黒な立方体）を確認
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_closed.png")
    bpy.ops.render.render(write_still=True)
    print(">> test_closed render done")

if "hero480" in modes:
    # PITFALL#10: 造形物はheroサイズでも一度検証（480pxで潰れるアーティファクト対策）
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
