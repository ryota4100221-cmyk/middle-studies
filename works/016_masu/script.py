# =============================================================
# monaka design. — MIDDLE STUDY 016 "MASU"
# 入れ子の黒い角枡（正方形フレーム）が、回転しながら段階的に開く。
# 閉じれば同心の正方形にネストし、開けば各段が持ち上がり捻れて
# 螺旋の塔になり、最内の底のライム #A5E02E が現れる。
# 入れ子の芯に、光がある。段を開いて、はじめて届く。
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

N_BOX = 5
W0 = 0.6              # 最外枡の半辺
W_STEP = 0.095        # 段ごとに縮む量
H = 0.32             # 枡の壁の高さ
TH = 0.045           # 壁の厚み

LIFT = 0.34          # 開いたとき各段が持ち上がる量（段番号×）＝段が分離
ROT_STEP = math.radians(34)   # 段ごとの捻れ角（螺旋）＝上から見て捻れがはっきり
BREATHS = 1          # 開閉回数（1＝ゆっくり一度開いて閉じる）
GLOBAL_TURNS = 1     # 全体回転の周回数

CORE_EMIT = 2.0      # 最内の底の発光強度（控えめ＝Glare箱回避）
CORE_LIGHT_W = 26    # 底の点光源（塔の内側へ光をこぼす）

CENTER_Z = 1.28
BASE_Z = CENTER_Z - 0.22   # 閉時の枡の中心高さ

FPS = 24
N_FRAMES = 120       # 5秒 完全ループ
STILL_FRAME = 61     # ヒーロー：最も開いた瞬間（塔＋最内の光）


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

# 黒い枡（マット寄り。角ばった黒がクローム化しないようコート無し・低スペキュラ）
mat_box, b = make_principled("box_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.44
b.inputs["Specular IOR Level"].default_value = 0.16

# 発光する最内の底
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

# ---------- 回転リグ（原点。全体を中心軸で回す） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "MasuRig"

# ---------- 角枡フレーム（正方形の中空チューブ） ----------
def make_frame_mesh(w, h, th):
    bm = bmesh.new()
    outs, inns = w, w - th
    def sq(s, z):
        return [bm.verts.new((s, s, z)), bm.verts.new((-s, s, z)),
                bm.verts.new((-s, -s, z)), bm.verts.new((s, -s, z))]
    ob = sq(outs, -h / 2); ot = sq(outs, h / 2)
    ib = sq(inns, -h / 2); it = sq(inns, h / 2)
    for k in range(4):
        k2 = (k + 1) % 4
        bm.faces.new([ob[k], ob[k2], ot[k2], ot[k]])      # 外壁
        bm.faces.new([ib[k2], ib[k], it[k], it[k2]])      # 内壁
        bm.faces.new([ot[k], ot[k2], it[k2], it[k]])      # 上縁
        bm.faces.new([ib[k], ib[k2], ob[k2], ob[k]])      # 下縁
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("frame")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_box)
    return me

pivots = []
for i in range(N_BOX):
    w = W0 - i * W_STEP
    me = make_frame_mesh(w, H, TH)
    piv = bpy.data.objects.new(f"pivot_{i}", None)
    scene.collection.objects.link(piv)
    piv.location = (0, 0, BASE_Z)
    piv.parent = rig
    o = bpy.data.objects.new(f"box_{i}", me)
    scene.collection.objects.link(o)
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.008
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    o.parent = piv
    # 角枡はフラットシェーディング（シャープなエッジ）。auto_smoothはmodifierを
    # 追加しリグに誤爆するため使わない。
    pivots.append((piv, i, w))

# ---------- 最内の底（発光）＋点光源：最内枡の底に固定（螺旋の頂で灯る） ----------
# 最内ピボットに直接parent（matrix_parent_inverseは使わない＝005の罠回避）。
# 開くと最内枡が塔の頂へ上がり、その底のライムが現れ、光が塔の内側を伝って降りる。
inner_piv = pivots[-1][0]
inner_w = pivots[-1][2]
core_hw = inner_w - TH - 0.005   # 最内枡の内寸に収める小さな芯
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "core"
core.scale = (core_hw, core_hw, 0.02)
bpy.ops.object.transform_apply(scale=True)
core.data.materials.append(mat_core)
core.visible_shadow = False
core.location = (0, 0, -H / 2 + 0.02)   # 最内枡ローカルの底面
core.parent = inner_piv

bpy.ops.object.light_add(type='POINT', location=(0, 0, -H / 2 + 0.1))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.energy = CORE_LIGHT_W
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.2
core_light.parent = inner_piv

# ---------- アニメーション（開閉＋捻れ＋全体回転：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    op = osc(t, BREATHS)                      # 0=閉 1=開
    for piv, i, w in pivots:
        piv.location = (0, 0, BASE_Z + i * LIFT * op)
        piv.rotation_euler = (0, 0, i * ROT_STEP * op)
        piv.keyframe_insert(data_path="location", index=2, frame=f)
        piv.keyframe_insert(data_path="rotation_euler", index=2, frame=f)
    # 全体回転（整数周＝完全ループ）
    rig.rotation_euler = (0, 0, 2 * math.pi * GLOBAL_TURNS * t)
    rig.keyframe_insert(data_path="rotation_euler", index=2, frame=f)
    # 開くほど底が強く光る
    core_bsdf.inputs["Emission Strength"].default_value = 1.5 + 0.9 * op
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
study = add_caption("MIDDLE STUDY 016 — MASU", 0.045, (0.15, -1.35, 0.055), "study")

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

# ---------- カメラ（少し上から塔を見下ろす） ----------
bpy.ops.object.camera_add(location=(0.42, -8.4, 5.2))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, CENTER_Z + 0.12))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = core
cam.data.dof.aperture_fstop = 6.5
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_masu.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith("box_") or o.name == "core")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_masu.glb"),
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

if "test2" in modes:
    scene.frame_set(1)  # 閉じてネストした状態を確認
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
