# =============================================================
# monaka design. — MIDDLE STUDY 010 "SOROBAN"（算盤）
# 黒い算盤。5本の縦軸に通った黒い菱形の珠が、中央の梁へ
# 上下から寄っては離れる。珠が梁を挟んで出会う瞬間、
# 間のライムのコアが点る。軸ごとに位相をずらし、寄せの波が
# 左から右へ走る。機構＝カウントの真ん中に、光がある。
#
# 技法: 双円錐の珠をbmeshで生成し10個配置。上下の珠の位置を
#   o_r(t)=0.5(1-cos2π(t-r/R)) で駆動＝軸ごと位相ラグの波。
#   寄った瞬間に発光コアのスケール＋点光源エネルギーをcosで
#   同期発火。珠の往復・波・微ヨーいずれも整数周期で完全ループ。
#   道具/構造ドメイン。
#
# 実行:
#   Blender --background --factory-startup --python monaka_soroban.py -- <mode...>
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

CENTER_Z = 1.35     # 浮遊高さ（算盤の中心＝梁の高さ）
R = 5               # 縦軸の本数
DX = 0.37           # 軸の間隔
H = 0.86            # フレーム半高（梁から上下の桁まで）
WTOT = 1.80         # フレーム総幅（左右の枠の間）

RMID = 0.135        # 珠の胴（最大半径）
RTIP = 0.028        # 珠の先（尖端の半径）
HB = 0.125          # 珠の半高
Z_FAR = 0.60        # 梁から離れた（休止）ときの珠中心オフセット
Z_NEAR = 0.19       # 梁へ寄った（出会う）ときの珠中心オフセット

BASE_YAW = math.radians(-25)  # 3/4ビューにする固定ヨー
YAW_AMP = math.radians(7)     # 微ヨー揺れ（1周期・視差の生気）

FPS = 24
N_FRAMES = 120      # 5秒 完全ループ
STILL_FRAME = 109   # heroに使う静止フレーム（中央軸r=2が完全収束＝焦点が中央に灯る）

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

# 黒い算盤（黒漆寄り＝低ラフ＋低スペキュラで平面がグレーに転ばないよう）
mat_black, b = make_principled("soroban_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.20
b.inputs["Specular IOR Level"].default_value = 0.32
b.inputs["Coat Weight"].default_value = 0.15
b.inputs["Coat Roughness"].default_value = 0.10

# 発光コア（ライム）
mat_core, core_bsdf = make_principled("core_lime")
core_bsdf.inputs["Base Color"].default_value = LIME
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Emission Strength"].default_value = 3.4
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

# ---------- 造形ヘルパー ----------
def finalize(o, mat, smooth_angle=0.9):
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_angle)
    except Exception:
        bpy.ops.object.shade_smooth()
    o.select_set(False)
    return o

def make_bead(name):
    """双円錐（菱形）のそろばん珠。胴で最大・上下の先で細る。"""
    bm = bmesh.new()
    N = 40
    mid, top, bot = [], [], []
    for i in range(N):
        a = 2 * math.pi * i / N
        c, s = math.cos(a), math.sin(a)
        mid.append(bm.verts.new((RMID * c, RMID * s, 0)))
        top.append(bm.verts.new((RTIP * c, RTIP * s, HB)))
        bot.append(bm.verts.new((RTIP * c, RTIP * s, -HB)))
    tcap = bm.verts.new((0, 0, HB))
    bcap = bm.verts.new((0, 0, -HB))
    for i in range(N):
        j = (i + 1) % N
        bm.faces.new((mid[i], mid[j], top[j], top[i]))
        bm.faces.new((bot[i], bot[j], mid[j], mid[i]))
        bm.faces.new((top[i], top[j], tcap))
        bm.faces.new((bot[j], bot[i], bcap))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    return finalize(o, mat_black, smooth_angle=0.9)

def add_box(name, loc, dims):
    """size=1のキューブをlive scaleで箱に（transform_applyしない＝#7回避）。"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (dims[0], dims[1], dims[2])
    o.data.materials.append(mat_black)
    o.select_set(False)
    return o

def add_rod(name, x):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.026, depth=2 * H, vertices=28, location=(x, 0, CENTER_Z))
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat_black)
    bpy.ops.object.shade_smooth()
    o.select_set(False)
    return o

# 軸のx座標（中心対称）
XS = [(r - (R - 1) / 2) * DX for r in range(R)]

# ---------- フレーム（枠・桁・梁） ----------
beam = add_box("beam", (0, 0, CENTER_Z), (WTOT, 0.13, 0.085))
rail_top = add_box("rail_top", (0, 0, CENTER_Z + H), (WTOT, 0.12, 0.09))
rail_bot = add_box("rail_bot", (0, 0, CENTER_Z - H), (WTOT, 0.12, 0.09))
post_l = add_box("post_l", (-WTOT / 2, 0, CENTER_Z), (0.09, 0.12, 2 * H + 0.09))
post_r = add_box("post_r", (WTOT / 2, 0, CENTER_Z), (0.09, 0.12, 2 * H + 0.09))

# ---------- 軸・珠・コア ----------
rods, beads_top, beads_bot, cores, lights = [], [], [], [], []
for r, x in enumerate(XS):
    rods.append(add_rod(f"rod{r}", x))

    bt = make_bead(f"bead_top{r}")
    bt.location = (x, 0, CENTER_Z + Z_FAR)
    beads_top.append(bt)

    bb = make_bead(f"bead_bot{r}")
    bb.location = (x, 0, CENTER_Z - Z_FAR)
    beads_bot.append(bb)

    # 発光コア（梁の前面・軸上。珠の間から正面に覗く）
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(x, -0.045, CENTER_Z))
    core = bpy.context.active_object
    core.name = f"core{r}"
    core.data.materials.append(mat_core)
    bpy.ops.object.shade_smooth()
    core.select_set(False)
    cores.append(core)

    # 芯を灯す小さな点光源（黒に緑を被せすぎないよう控えめ）
    bpy.ops.object.light_add(type='POINT', location=(x, -0.045, CENTER_Z))
    lp = bpy.context.active_object
    lp.name = f"corelight{r}"
    lp.data.shadow_soft_size = 0.06
    lp.data.color = (0.78, 0.95, 0.48)
    lp.data.energy = 6.0
    lights.append(lp)

# ---------- リグ（固定ヨー＋微ヨー揺れ／純Z回転なのでピボットzは無害） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "SorobanRig"
for o in (beam, rail_top, rail_bot, post_l, post_r,
          *rods, *beads_top, *beads_bot, *cores, *lights):
    o.parent = rig

# ---------- アニメーション（波＝軸ごと位相ラグ・完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    # リグの微ヨー（1周期で戻る）
    rig.rotation_euler.z = BASE_YAW + YAW_AMP * math.cos(2 * math.pi * t)
    rig.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

    for r in range(R):
        # 0=離れて休止, 1=梁へ寄って出会う。軸ごとに r/R 位相をずらす＝波
        o = 0.5 * (1 - math.cos(2 * math.pi * (t - r / R)))
        off = Z_FAR - (Z_FAR - Z_NEAR) * o

        bt = beads_top[r]
        bt.location.z = CENTER_Z + off
        bt.keyframe_insert(data_path="location", index=2, frame=f)

        bb = beads_bot[r]
        bb.location.z = CENTER_Z - off
        bb.keyframe_insert(data_path="location", index=2, frame=f)

        # 全コアは梁上で常時ほのかに灯り（真ん中の光の列）、寄った軸が強くフレア
        core = cores[r]
        sc = 0.85 + 0.7 * o
        core.scale = (sc, sc, sc)
        core.keyframe_insert(data_path="scale", frame=f)

        lp = lights[r]
        lp.data.energy = 13.0 + 40.0 * o
        lp.data.keyframe_insert(data_path="energy", frame=f)

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
study = add_caption("MIDDLE STUDY 010 — SOROBAN", 0.045, (0.15, -1.3, 0.06), "study")

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
look = Vector((0.0, 0, CENTER_Z + 0.02))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = beam
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "soroban.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    export_names = {o.name for o in (beam, rail_top, rail_bot, post_l, post_r,
                                     *rods, *beads_top, *beads_bot, *cores)}
    for o in bpy.data.objects:
        o.select_set(o.name in export_names)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "soroban.glb"),
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
    scene.render.filepath = os.path.join(OUT, "soroban_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "soroban_hero.png")
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
    scene.render.filepath = os.path.join(OUT, "soroban_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
