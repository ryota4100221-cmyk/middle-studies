# =============================================================
# monaka design. — MIDDLE STUDY 005 "KAWA"
# 波打つ2枚の最中の皮（黒いウエハース）が上下に向き合い、
# 閉じかけの隙間からライム #A5E02E の餡がのぞく。
# 皮がゆっくり呼吸するように開閉し、開くほど餡の光があふれる。
# 最中そのもの——「二枚の皮の、真ん中に餡（光）がある」。
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

SHELL_R = 0.9         # 皮の半径
DOME_H = 0.42         # 皮のドーム高さ（中心の膨らみ）
RIPPLE_A = 0.045      # 同心円リップル振幅（最中の凹凸）
RIPPLE_K = 5.0        # リップルの周期数（半径方向）
SCALLOP = 0.05        # 縁のスカラップ（花形の波打ち）振幅
N_SCALLOP = 14        # 縁のスカラップ山数
SHELL_THICK = 0.028   # 皮の厚み（solidify）
N_R = 44              # 放射メッシュ：リング数
N_A = 120             # 放射メッシュ：角度分割

GAP_MIN = 0.05        # 閉じたときの上下皮の隙間（半開＝完全には閉じない）
GAP_MAX = 0.24        # 開いたときの隙間（控えめ＝隙間から"のぞく"）
BREATHS = 2           # ループ中の開閉回数（cos＝完全ループ）

FILL_RXY = 0.82       # 餡（レンズ）の水平半径（縁のすぐ内側まで）
FILL_RZ = 0.12        # 餡の垂直半径（薄いレンズ＝隙間に収まり縁だけのぞく）
CORE_EMIT = 3.0       # 餡の発光強度（呼吸で±する中央値）
FILL_LIGHT_W = 55     # 餡の実光源（隙間から光をこぼす）

CENTER_Z = 1.28       # 最中の浮遊高さ（中心）
RIG_ROT_TURNS = 1     # ループ中の全体回転（整数＝完全ループ）

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 31      # ヒーロー：隙間が最大に開き餡が最も見える瞬間


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

# 黒い皮（サテン寄り：最中の皮の艶を少しだけ）
mat_shell, b = make_principled("shell_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.40
b.inputs["Specular IOR Level"].default_value = 0.30

# 発光する餡
mat_core, core_bsdf = make_principled("an_lime")
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

# ---------- リグ（原点。最中全体を中心軸で回す＋皮を上下に開閉） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "KawaRig"

# ---------- 皮の造形（波打つ放射ドームメッシュ） ----------
def shell_z(u, sign, half_gap):
    """u=r/R (0..1)。sign=+1上/-1下。皮の高さプロファイル"""
    dome = DOME_H * (1 - u * u)
    ripple = RIPPLE_A * math.cos(RIPPLE_K * math.pi * u) * u
    return sign * (half_gap + dome + ripple)

def make_shell(name, sign):
    """半開状態(GAP_MIN)で皮メッシュを生成。開閉はアニメでlocation.zを動かす。"""
    bm = bmesh.new()
    half = GAP_MIN / 2
    # 中心頂点
    apex = bm.verts.new((0, 0, shell_z(0.0, sign, half)))
    rings = []
    for i in range(1, N_R + 1):
        u = i / N_R
        r = SHELL_R * u
        ring = []
        for j in range(N_A):
            theta = 2 * math.pi * j / N_A
            scal = 1 + SCALLOP * math.cos(N_SCALLOP * theta) * u  # 縁ほどスカラップが効く
            rr = r * scal
            x = rr * math.cos(theta)
            y = rr * math.sin(theta)
            ring.append(bm.verts.new((x, y, shell_z(u, sign, half))))
        rings.append(ring)
    # 中心ファン
    for j in range(N_A):
        j2 = (j + 1) % N_A
        bm.faces.new([apex, rings[0][j], rings[0][j2]])
    # リング間クアッド
    for i in range(N_R - 1):
        for j in range(N_A):
            j2 = (j + 1) % N_A
            bm.faces.new([rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]])
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat_shell)
    # 厚み（最中の皮のエッジ）
    sol = o.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = SHELL_THICK
    sol.offset = 0
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    o.location = (0, 0, CENTER_Z)  # メッシュはz≈0で生成→中心高さへ配置
    o.parent = rig
    return o

shell_top = make_shell("shell_top", +1)
shell_bot = make_shell("shell_bot", -1)

# ---------- 餡（発光レンズ）＋内部ポイントライト ----------
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, CENTER_Z),
                                     segments=64, ring_count=32)
fill = bpy.context.active_object
fill.name = "an"
fill.scale = (FILL_RXY, FILL_RXY, FILL_RZ)
bpy.ops.object.shade_smooth()
fill.data.materials.append(mat_core)
fill.parent = rig

bpy.ops.object.light_add(type='POINT', location=(0, 0, CENTER_Z))
fill_light = bpy.context.active_object
fill_light.name = "an_light"
fill_light.data.energy = FILL_LIGHT_W
fill_light.data.color = (LIME[0], LIME[1], LIME[2])
fill_light.data.shadow_soft_size = 0.08
fill_light.parent = rig

# ---------- アニメーション（開閉＋回転＋餡の呼吸：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    """0..1 → 0..1、cosベース＝完全ループ"""
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    op = osc(t, BREATHS)  # 0=閉 1=開
    gap = GAP_MIN + (GAP_MAX - GAP_MIN) * op
    dz = (gap - GAP_MIN) / 2  # 生成時GAP_MINからの追加ひらき
    # 皮を上下に開く（メッシュはGAP_MINで作成済み。中心高さ＋差分）
    shell_top.location.z = CENTER_Z + dz
    shell_bot.location.z = CENTER_Z - dz
    shell_top.keyframe_insert(data_path="location", index=2, frame=f)
    shell_bot.keyframe_insert(data_path="location", index=2, frame=f)
    # 餡：隙間に合わせて厚みが呼吸し、開くほど強く光る
    rz = FILL_RZ * (0.85 + 0.6 * op)
    fill.scale = (FILL_RXY, FILL_RXY, rz)
    fill.keyframe_insert(data_path="scale", frame=f)
    core_bsdf.inputs["Emission Strength"].default_value = 1.4 + 0.75 * op
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    fill_light.data.energy = FILL_LIGHT_W * (0.6 + 0.7 * op)
    fill_light.data.keyframe_insert(data_path="energy", frame=f)
    # 全体をゆっくり回して立体を見せる（整数周＝完全ループ）
    rig.rotation_euler = (0, 0, 2 * math.pi * RIG_ROT_TURNS * t)
    rig.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

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
study = add_caption("MIDDLE STUDY 005 — KAWA", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜004と同一＝シリーズの一貫性） ----------
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
bpy.ops.object.camera_add(location=(0.55, -11.5, 2.15))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, CENTER_Z + 0.05))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = fill
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
        filepath=os.path.join(OUT, "monaka_kawa.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("shell_top", "shell_bot", "an"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_kawa.glb"),
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
