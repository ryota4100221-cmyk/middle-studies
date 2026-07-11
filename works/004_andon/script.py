# =============================================================
# monaka design. — MIDDLE STUDY 004 "ANDON"
# 黒い細格子の籠（行灯）。中に光るライム #A5E02E の核。
# 核の光は格子の隙間から漏れ、黒いスラットが影を切り、
# 床に網目模様を落とす。籠がゆっくり360°回り、
# 網目が床を掃きながら核が呼吸するように明滅する。
# 「外は黒。真ん中に、光がある。」
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

# 籠（行灯）の寸法
WC = 1.35              # 一辺（正方形断面）
HALF = WC / 2
HC = 1.5              # 籠の高さ（やや縦長の行灯＝一目で読める）
Z0 = 0.52             # 籠底面の浮遊高さ
CENTER_Z = Z0 + HC / 2

N_VERT = 7            # 各面の縦スラット本数（隙間で網目の縦線を作る）
BAR_W = 0.045        # スラットの幅（面接線方向）
BAR_D = 0.055        # スラットの奥行き（面法線方向）
N_RING = 4           # 横リングの段数（網目の横線を作る）
RING_T = 0.05        # リングの太さ
CAP_T = 0.06         # 天板・地板の厚み
CAP_INSET = 0.02     # 天地キャップの水平インセット

CORE_R = 0.34        # 発光核（球）の半径
CORE_EMIT = 3.0      # 核の発光強度（呼吸で±する中央値）
CORE_LIGHT_W = 520   # 核の内部ポイントライト（床に網目影を落とす実光源）

RIG_ROT_TURNS = 1    # ループ中の籠の回転周回数（整数＝完全ループ）

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ（003と同尺）
STILL_FRAME = 25      # ヒーロー静止画：籠の角がこちらを向く辺り


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

# 黒い格子（細い桟は強い反射が乗るとクロームに見えるため、
# コート無し・低スペキュラ・高ラフネスで「黒を黒く」保つ。細部の質感差だけ2種）
mat_matte, b = make_principled("frame_matte")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.58
b.inputs["Specular IOR Level"].default_value = 0.12

mat_satin, b = make_principled("frame_satin")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.44
b.inputs["Specular IOR Level"].default_value = 0.18

# 発光する核
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

# ---------- リグ（籠全体を回す） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "AndonRig"

def shade(obj):
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            pass

def add_box(name, sx, sy, sz, loc, mat, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    # PITFALL#7の逆: --factory-startupではtransform_apply(scale)が
    # メッシュをワールド位置に焼き込みlocation→0にする（位置は既に正しい）。
    # ここでo.location=locを再設定すると二重オフセットになるため設定しない。
    # rig(原点)にparentし原点Z軸で回すことで籠が中心軸で回転する。
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = min(bevel, min(sx, sy, sz) * 0.3)
    bev.segments = 2
    shade(o)
    o.data.materials.append(mat)
    o.parent = rig
    return o

# ---------- 籠の造形（縦スラット＋横リング＋天地キャップ） ----------
frame_parts = []
mi = 0  # マテリアル交互カウンタ

# 縦スラット：4面。各面に N_VERT 本、接線方向に均等配置。
# tangential 位置は -HALF..+HALF（端はコーナー付近）
def slat_positions(n):
    if n == 1:
        return [0.0]
    return [-HALF + 2 * HALF * i / (n - 1) for i in range(n)]

verts_t = slat_positions(N_VERT)
for t in verts_t:
    # 前(y=-HALF)・後(y=+HALF)面：スラットはX方向に並ぶ（幅=X, 奥行=Y）
    for sy_sign in (-1, 1):
        add_box(f"vbar_fb_{mi:03d}", BAR_W, BAR_D, HC,
                (t, sy_sign * HALF, CENTER_Z),
                mat_matte if mi % 2 == 0 else mat_satin)
        mi += 1
    # 左(x=-HALF)・右(x=+HALF)面：スラットはY方向に並ぶ（幅=Y, 奥行=X）
    for sx_sign in (-1, 1):
        add_box(f"vbar_lr_{mi:03d}", BAR_D, BAR_W, HC,
                (sx_sign * HALF, t, CENTER_Z),
                mat_matte if mi % 2 == 0 else mat_satin)
        mi += 1

# 横リング：N_RING 段。各段は4本の横バーで正方形の枠を作る。
ring_zs = [Z0 + HC * (k + 0.5) / N_RING for k in range(N_RING)]
for z in ring_zs:
    # 前後（X方向に伸びる横バー）
    for sy_sign in (-1, 1):
        add_box(f"ring_fb_{mi:03d}", WC + BAR_D, RING_T, RING_T,
                (0, sy_sign * HALF, z),
                mat_matte if mi % 2 == 0 else mat_satin)
        mi += 1
    # 左右（Y方向に伸びる横バー）
    for sx_sign in (-1, 1):
        add_box(f"ring_lr_{mi:03d}", RING_T, WC + BAR_D, RING_T,
                (sx_sign * HALF, 0, z),
                mat_matte if mi % 2 == 0 else mat_satin)
        mi += 1

# 天板（黒キャップ・ソリッド）：上への漏れを止め、光を下＝床へ向ける
cap_w = WC + BAR_D + 0.06
add_box("cap_top", cap_w, cap_w, CAP_T,
        (0, 0, Z0 + HC + CAP_T / 2 - CAP_INSET), mat_matte, bevel=0.008)

# 地板は格子（ワッフルグリッド）：核の光が升目を抜けて床に網目模様を落とす
N_BGRID = 5
BGRID_T = 0.05
zb = Z0 + BGRID_T / 2 - CAP_INSET
bpos = slat_positions(N_BGRID)
for t in bpos:
    add_box(f"bgrid_x_{mi:03d}", WC + BAR_D, BGRID_T, BGRID_T,
            (0, t, zb), mat_matte if mi % 2 == 0 else mat_satin)
    mi += 1
    add_box(f"bgrid_y_{mi:03d}", BGRID_T, WC + BAR_D, BGRID_T,
            (t, 0, zb), mat_matte if mi % 2 == 0 else mat_satin)
    mi += 1
# 地板の縁枠（グリッドを締める薄い外周）
for sy_sign in (-1, 1):
    add_box(f"brim_x_{mi:03d}", cap_w, BGRID_T, BGRID_T,
            (0, sy_sign * HALF, zb), mat_matte)
    mi += 1
    add_box(f"brim_y_{mi:03d}", BGRID_T, cap_w, BGRID_T,
            (sy_sign * HALF, 0, zb), mat_matte)
    mi += 1

# ---------- 発光核（球）＋内部ポイントライト ----------
bpy.ops.mesh.primitive_uv_sphere_add(radius=CORE_R, location=(0, 0, CENTER_Z),
                                     segments=48, ring_count=24)
core = bpy.context.active_object
core.name = "core"
bpy.ops.object.shade_smooth()
core.data.materials.append(mat_core)
core.parent = rig

# 実光源：核の中心のポイントライト。黒スラットの影を床に落とす（＝網目模様）。
bpy.ops.object.light_add(type='POINT', location=(0, 0, CENTER_Z))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.energy = CORE_LIGHT_W
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.03  # 小さめ＝網目の影がくっきり出る
core_light.parent = rig  # リグと一緒に回す（網目が床を掃く）

# ---------- アニメーション（籠の360°回転＋核の呼吸：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, lag=0.0):
    """0..1 → 0..1、cosベース＝完全ループ"""
    return 0.5 * (1 - math.cos(2 * math.pi * t01 - lag))

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    # 籠の回転（整数周＝完全ループ）
    rig.rotation_euler = (0, 0, 2 * math.pi * RIG_ROT_TURNS * t)
    rig.keyframe_insert(data_path="rotation_euler", index=2, frame=f)
    # 核の呼吸：スケール＆発光をcosで（完全ループ）
    br = osc(t)
    s = 0.94 + 0.12 * br
    core.scale = (s, s, s)
    core.keyframe_insert(data_path="scale", frame=f)
    core_bsdf.inputs["Emission Strength"].default_value = 1.8 + 0.9 * br
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    core_light.data.energy = CORE_LIGHT_W * (0.75 + 0.45 * br)
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
study = add_caption("MIDDLE STUDY 004 — ANDON", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜003と同一＝シリーズの一貫性） ----------
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
bpy.ops.object.camera_add(location=(0.55, -11.3, 2.0))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, CENTER_Z + 0.05))
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
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(OUT, "monaka_andon.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name.startswith(("vbar_", "ring_", "cap_", "bgrid_", "brim_")) or o.name == "core")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_andon.glb"),
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
