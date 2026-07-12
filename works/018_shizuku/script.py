# =============================================================
# monaka design. — MIDDLE STUDY 018 "SHIZUKU"
# 黒い雫が垂れ、伸びてネックが細り、千切れる寸前まで痩せる。
# その瞬間、細った黒い糸の芯にライム #A5E02E が灯る——液の中の光。
# また縮んでまるい一滴に戻る。完全ループ。
# 外は黒、真ん中に光がある。伸びて痩せて、はじめて芯が見える。
# "Designing the Middle of Your Story."
#
# 技法：回転体（surface of revolution）の雫をラーゼ生成し、
#       ネックを痩せさせるシェイプキー "stretch" で伸展→細ネックを作る
#       （黒い糸は繋がったまま＝裸の緑玉を作らない）。
#       ネック位置に発光ライム球を置き、痩せた黒糸の芯として露出。
#       s(t)=0.5(1-cos2πt)を毎フレームキー＝数学的完全ループ。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: test | test2 | sweep | hero480 | still | anim | glb | blend
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

# 雫（回転体）のジオメトリ
TOP_WZ = 1.78         # 雫の頂点（付け根）のワールド高さ＝固定。ここから下へ伸びる
R0 = 0.44             # 雫の最大半径
H0 = 0.92             # 静止時の雫の高さ（頂点→底）
H1 = 1.44             # 伸展時の高さ
N_RINGS = 64          # 回転体の輪数
SEGS = 64             # 円周分割
UW = 0.19             # ネックの位置（u=0が頂点／小さいほど付け根寄り）
WSIG = 0.060          # ネックの鋭さ
WDEPTH = 0.92         # ネックの痩せ量（1に近いほど千切れそう）
STRETCH_THIN = 0.94   # 伸展時に全体を少し細らせる（体積感）

# ライムの芯（発光球）＝ネックに置き、伸展量svに比例して露出
R_CORE = 0.078        # 芯の半径（黒糸から帯状にのぞく最大）
CORE_EMIT = 2.0       # 芯の発光（控えめ・白飛びさせずライムを保つ）
CORE_LIGHT_W = 3.0    # 芯の点光源（PITFALL#11回避＝弱く柔らかく）

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 61      # ヒーロー：最も痩せて芯が灯る瞬間（掃引で確定）


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

# 黒い液滴（濡れた黒：わずかな艶。クローム化はさせない＝015/010の教訓）
mat_drop, b = make_principled("drop_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.28
b.inputs["Specular IOR Level"].default_value = 0.32

# 発光するライムの芯
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

# ---------- 雫（回転体）の生成 ----------
# u=0 が頂点（付け根・固定）、u=1 が底。ローカルzは頂点0から下へ負。
def r_rest(u):
    # ティアドロップ：頂点(u=0)は細く尖り、底(u=1)へ向けて膨らむ雫形
    env = math.sqrt(max(0.0, math.sin(math.pi * u)))   # 両端0の包絡
    skew = 0.58 + 0.62 * u                             # 上細・下太
    return R0 * env * skew

def waist(u):
    return 1.0 - WDEPTH * math.exp(-((u - UW) / WSIG) ** 2)

def profile(u, sv):
    """svは伸展量(0..1)。zとrを返す（ローカル・頂点基準で下へ負）。"""
    H = H0 + sv * (H1 - H0)
    z = -u * H
    r = r_rest(u)
    # 伸展時はネックを痩せさせ全体も少し細らせる
    r = r * (1.0 - sv) + r * STRETCH_THIN * waist(u) * sv
    return z, r

def build_drop_verts(sv):
    verts = []
    for i in range(N_RINGS):
        u = i / (N_RINGS - 1)
        z, r = profile(u, sv)
        r = max(r, 1e-4)
        for s in range(SEGS):
            a = 2.0 * math.pi * s / SEGS
            verts.append((r * math.cos(a), r * math.sin(a), z))
    # 上下の極（キャップ中心）
    z_top, _ = profile(0.0, sv)
    z_bot, _ = profile(1.0, sv)
    verts.append((0.0, 0.0, z_top + 0.01))   # top pole
    verts.append((0.0, 0.0, z_bot - 0.01))   # bottom pole
    return verts

def build_faces():
    faces = []
    for i in range(N_RINGS - 1):
        for s in range(SEGS):
            s2 = (s + 1) % SEGS
            a = i * SEGS + s
            b_ = i * SEGS + s2
            c = (i + 1) * SEGS + s2
            d = (i + 1) * SEGS + s
            faces.append((a, b_, c, d))
    top_pole = N_RINGS * SEGS
    bot_pole = N_RINGS * SEGS + 1
    for s in range(SEGS):
        s2 = (s + 1) % SEGS
        faces.append((top_pole, s2, s))                      # top cap
        base = (N_RINGS - 1) * SEGS
        faces.append((bot_pole, base + s, base + s2))        # bottom cap
    return faces

verts0 = build_drop_verts(0.0)
faces = build_faces()
me = bpy.data.meshes.new("shizuku")
me.from_pydata(verts0, [], faces)
me.update()
me.materials.append(mat_drop)
drop = bpy.data.objects.new("shizuku", me)
scene.collection.objects.link(drop)
drop.location = (0.0, 0.0, TOP_WZ)

# シェイプキー：basis(sv=0) と stretch(sv=1)
drop.shape_key_add(name="Basis", from_mix=False)
sk = drop.shape_key_add(name="stretch", from_mix=False)
verts1 = build_drop_verts(1.0)
for idx, co in enumerate(verts1):
    sk.data[idx].co = co
sk.value = 0.0

# スムーズシェード
bpy.context.view_layer.objects.active = drop
drop.select_set(True)
bpy.ops.object.shade_auto_smooth(angle=math.radians(50))
drop.select_set(False)

# ---------- ライムの芯（発光球・ネックに置く） ----------
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=48, ring_count=24,
                                     location=(0, 0, TOP_WZ))
core = bpy.context.active_object
core.name = "core"
core.data.materials.append(mat_core)
core.visible_shadow = False
bpy.ops.object.shade_smooth()

def waist_world_z(sv):
    H = H0 + sv * (H1 - H0)
    return TOP_WZ - UW * H

# ---------- ライムの点光源（芯に追従・伸展に同期） ----------
bpy.ops.object.light_add(type='POINT', location=(0, 0, TOP_WZ))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.28

# ---------- アニメーション（伸展→細ネック→復元：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    sv = 0.5 * (1.0 - math.cos(2.0 * math.pi * t))     # 0→1→0 完全ループ
    # 黒い雫：シェイプキーで伸展
    sk.value = sv
    sk.keyframe_insert(data_path="value", frame=f)
    # ライムの芯：ネック位置に置き、伸展量に比例して露出（svで大きくなる）
    cz = waist_world_z(sv)
    cr = sv * R_CORE
    core.location = (0.0, 0.0, cz)
    core.scale = (cr, cr, cr)
    core.keyframe_insert(data_path="location", index=2, frame=f)
    core.keyframe_insert(data_path="scale", frame=f)
    # 芯の点光源
    core_light.location = (0.0, 0.0, cz)
    core_light.data.energy = CORE_LIGHT_W * sv
    core_light.keyframe_insert(data_path="location", index=2, frame=f)
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
study = add_caption("MIDDLE STUDY 018 — SHIZUKU", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜017と同一＝シリーズの一貫性） ----------
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

focus = (0, 0, 1.2)
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
bpy.ops.object.camera_add(location=(0.3, -6.8, 1.42))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, 1.16))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = drop
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_shizuku.blend"))
    print(">> saved .blend")

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
    scene.frame_set(1)   # 静止（まるい一滴）状態
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_rest.png")
    bpy.ops.render.render(write_still=True)
    print(">> test_rest render done")

if "sweep" in modes:
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    for fr in (46, 52, 56, 61):
        scene.frame_set(fr)
        scene.render.filepath = os.path.join(OUT, "sweep_%03d.png" % fr)
        bpy.ops.render.render(write_still=True)
    print(">> sweep render done")

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

# GLB：シェイプキー＋発光球をアニメ込みで書き出し
if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("shizuku", "core"))
    bpy.context.view_layer.objects.active = drop
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_shizuku.glb"),
        export_format='GLB', use_selection=True,
        export_animations=True, export_yup=True, export_apply=True)
    print(">> exported GLB")

print(">> ALL DONE")
