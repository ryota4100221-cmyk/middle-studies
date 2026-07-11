# =============================================================
# monaka design. — MIDDLE STUDY 006 "ITO"
# 黒い球体に巻きついた1本のライム #A5E02E の糸。
# 糸は北極から南極へ球面をらせんに巻き、ほどけては巻き直る。
# 球の中心（真ん中）へ光の糸が収束していく——外は黒、芯に光。
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

BALL_R = 0.92         # 黒い球の半径
THREAD_LIFT = 0.022   # 糸を球面からどれだけ浮かせるか
THREAD_BEVEL = 0.017  # 糸（チューブ）の太さ
N_WIND = 9            # 糸が球を巻く回数（極から極へ・少なめ＝1本の螺旋と読める）
N_PTS = 900           # 糸カーブの分割数
POLE_INSET = 0.02     # 極付近を少し避ける（t範囲）

THREAD_EMIT = 3.2     # 糸の発光強度（呼吸で±する中央値）
BFE_MIN = 0.05        # ほどけた時に残る割合（0だと完全消滅するので少し残す）

CENTER_Z = 1.25       # 球の浮遊高さ（中心）
RIG_ROT_TURNS = 1     # ループ中の全体回転（整数＝完全ループ）

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 10      # ヒーロー：ほぼ巻き終わり（螺旋が読め、南極側に先端が見える）


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

# 黒い球（マット寄り＝黒を黒く保つ。001の球と同じ質感）
mat_ball, b = make_principled("ball_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.46
b.inputs["Specular IOR Level"].default_value = 0.22

# 発光する糸
mat_thread, thread_bsdf = make_principled("thread_lime")
thread_bsdf.inputs["Base Color"].default_value = LIME
thread_bsdf.inputs["Emission Color"].default_value = LIME
thread_bsdf.inputs["Emission Strength"].default_value = THREAD_EMIT
thread_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- リグ（原点。球＋糸を中心軸で回す） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "ItoRig"

# ---------- 黒い球 ----------
bpy.ops.mesh.primitive_uv_sphere_add(radius=BALL_R, location=(0, 0, CENTER_Z),
                                     segments=96, ring_count=48)
ball = bpy.context.active_object
ball.name = "ball"
bpy.ops.object.shade_smooth()
ball.data.materials.append(mat_ball)
ball.parent = rig

# ---------- ライムの糸（球面スパイラルカーブ→発光チューブ） ----------
cu = bpy.data.curves.new("ito_curve", "CURVE")
cu.dimensions = '3D'
sp = cu.splines.new('POLY')
sp.points.add(N_PTS - 1)
Rt = BALL_R + THREAD_LIFT
for i in range(N_PTS):
    t = POLE_INSET + (1 - 2 * POLE_INSET) * i / (N_PTS - 1)  # 極を少し避ける
    a = math.pi * t                     # 極角 0..π（北極→南極）
    azi = 2 * math.pi * N_WIND * t       # 方位（N_WIND周）
    x = Rt * math.sin(a) * math.cos(azi)
    y = Rt * math.sin(a) * math.sin(azi)
    z = CENTER_Z + Rt * math.cos(a)
    sp.points[i].co = (x, y, z, 1.0)
cu.bevel_depth = THREAD_BEVEL
cu.bevel_resolution = 3
cu.use_fill_caps = True
thread = bpy.data.objects.new("ito", cu)
scene.collection.objects.link(thread)
thread.data.materials.append(mat_thread)
thread.parent = rig

# ---------- アニメーション（ほどけ→巻き直し＋回転：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    """0..1 → 0..1、cosベース＝完全ループ"""
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    # bevel_factor_end: 1(全巻)→BFE_MIN(ほどけ)→1(巻き直し)、cos＝完全ループ
    wound = 0.5 * (1 + math.cos(2 * math.pi * t))  # 1→0→1
    bfe = BFE_MIN + (1 - BFE_MIN) * wound
    cu.bevel_factor_end = bfe
    cu.keyframe_insert(data_path="bevel_factor_end", frame=f)
    # 糸が巻き締まるほど強く光る（ほどけると弱く）
    thread_bsdf.inputs["Emission Strength"].default_value = 1.9 + 1.1 * wound
    thread_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
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
study = add_caption("MIDDLE STUDY 006 — ITO", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜005と同一＝シリーズの一貫性） ----------
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
cam.data.dof.focus_object = ball
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
        filepath=os.path.join(OUT, "monaka_ito.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("ball", "ito"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_ito.glb"),
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

if "test2" in modes:
    # アニメ検証用：ほどけた中間フレームも1枚出して糸長が変わるか確認
    scene.frame_set(N_FRAMES // 2)
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_mid.png")
    bpy.ops.render.render(write_still=True)
    print(">> test_mid render done")

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
