# =============================================================
# monaka design. — MIDDLE STUDY 013 "HAGURUMA"
# 中央に穴の空いた黒い大歯車。穴の奥にライム #A5E02E の核が灯る。
# 噛み合う黒い小歯車が回り、機構が回転する。歯数30:15＝2:1で、
# 大が1回転・小が2回転して噛み合い・回転とも整数周期＝完全ループ。
# 機械の真ん中に、光がある。
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

# 大歯車
BIG_N = 30
BIG_TIP = 0.92
BIG_ROOT = 0.80
BIG_HOLE = 0.24
# 小歯車
SML_N = 15
SML_TIP = 0.50
SML_ROOT = 0.40
SML_HOLE = 0.13

GEAR_THICK = 0.16     # 歯車の厚み
TOOTH_TIP_H = 0.17    # 歯先の角度半幅（ピッチ比）
TOOTH_FLANK = 0.13    # 歯面（フランク）の角度幅（ピッチ比）

# ピッチ半径の和＝中心間距離（噛み合う）
BIG_PITCH = (BIG_TIP + BIG_ROOT) / 2
SML_PITCH = (SML_TIP + SML_ROOT) / 2
DX = BIG_PITCH + SML_PITCH
# ペアの水平中心が0に来るよう配置
BIG_X = -DX / 2
SML_X = DX / 2

CORE_R = 0.27         # ライム核（大歯車の穴の奥）の半径（穴を塞ぐ最小限）
CORE_Y = 0.10         # 核の奥行き（歯車より奥）
CORE_EMIT = 1.6       # 核の発光強度（呼吸で±する中央値）
CORE_LIGHT_W = 22     # 核の内部ポイントライト

CENTER_Z = 1.30
TILT_X = math.radians(12)   # 歯の奥行きを見せる静的傾き
TILT_Z = math.radians(-5)

BIG_TURNS = 1         # 大歯車の回転数（整数）
FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 8       # ヒーロー：噛み合いが綺麗に見える辺り


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

# 黒い歯車（マット＝黒を黒く保つ。機械的にわずかな艶）
mat_gear, b = make_principled("gear_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.25

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

# ---------- リグ（原点。全体を静的に傾け奥行きを見せる） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "HagurumaRig"
rig.rotation_euler = (TILT_X, 0, TILT_Z)

# ---------- 歯車の造形（トゥースプロファイル環状メッシュ＋厚み） ----------
def gear_radius(theta, n, r_tip, r_root):
    """歯プロファイル：各ピッチの中心(p=0.5)に台形の歯"""
    p = (theta * n / (2 * math.pi)) % 1.0
    dc = abs(p - 0.5)
    if dc < TOOTH_TIP_H:
        return r_tip
    if dc < TOOTH_TIP_H + TOOTH_FLANK:
        f = (dc - TOOTH_TIP_H) / TOOTH_FLANK
        return r_tip + (r_root - r_tip) * f
    return r_root

def make_gear(name, n, r_tip, r_root, r_hole, xpos, phase):
    """歯付き環状板の歯車。XZ平面で生成し法線を±Yへ（カメラ正対）。
    軸がYなのでスピンは rotation_euler の index=1（Y）純回転になる。"""
    bm = bmesh.new()
    M = n * 12
    outer, inner = [], []
    for k in range(M):
        theta = 2 * math.pi * k / M
        r = gear_radius(theta - phase, n, r_tip, r_root)  # phaseで歯位置を合わせる
        ct, st = math.cos(theta), math.sin(theta)
        outer.append(bm.verts.new((r * ct, 0, r * st)))   # XZ平面
        inner.append(bm.verts.new((r_hole * ct, 0, r_hole * st)))
    # 半径方向を複数リングに分割（長い放射クアッドを避け面を素直にする）
    RINGS = 5
    for k in range(M):
        k2 = (k + 1) % M
        for j in range(RINGS):
            f0 = j / RINGS
            f1 = (j + 1) / RINGS
            def lerp(vin, vout, fr):
                return (vin.co.x + (vout.co.x - vin.co.x) * fr,
                        vin.co.y + (vout.co.y - vin.co.y) * fr,
                        vin.co.z + (vout.co.z - vin.co.z) * fr)
            a = bm.verts.new(lerp(inner[k], outer[k], f0))
            b = bm.verts.new(lerp(inner[k2], outer[k2], f0))
            c = bm.verts.new(lerp(inner[k2], outer[k2], f1))
            d = bm.verts.new(lerp(inner[k], outer[k], f1))
            bm.faces.new([a, b, c, d])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat_gear)
    sol = o.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = GEAR_THICK
    sol.offset = 0
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.006
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)  # 鋭い歯・縁だけ面取り、平面の放射エッジは除外
    o.location = (xpos, 0, CENTER_Z)
    o.parent = rig
    return o

# 大歯車：噛み合い側(+X, theta=0)に谷が来るよう phase=0（歯中心はp=0.5）
big = make_gear("big", BIG_N, BIG_TIP, BIG_ROOT, BIG_HOLE, BIG_X, 0.0)
# 小歯車：噛み合い側(-X, theta=π)に歯が来るよう phase=0（theta=πでp=0.5＝歯）
sml = make_gear("small", SML_N, SML_TIP, SML_ROOT, SML_HOLE, SML_X, 0.0)

# ---------- ライム核（大歯車の穴の奥）＋内部ポイントライト ----------
bpy.ops.mesh.primitive_cylinder_add(radius=CORE_R, depth=0.06, vertices=96,
                                    location=(BIG_X, CORE_Y, CENTER_Z))
core = bpy.context.active_object
core.name = "core"
core.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.shade_smooth()
core.data.materials.append(mat_core)
core.parent = rig

bpy.ops.object.light_add(type='POINT', location=(BIG_X, CORE_Y - 0.15, CENTER_Z))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.energy = CORE_LIGHT_W
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.1
core_light.parent = rig

# ---------- アニメーション（歯車の噛み合い回転＋核の呼吸：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

def osc(t01, cycles=1):
    return 0.5 * (1 - math.cos(2 * math.pi * cycles * t01))

ratio = BIG_N / SML_N  # =2。小歯車は逆回転で2倍速
for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    ang = 2 * math.pi * BIG_TURNS * t
    # 軸がYなのでY純回転（index=1）で面内スピン。小は逆回転で2倍速
    big.rotation_euler = (0, ang, 0)
    sml.rotation_euler = (0, -ang * ratio, 0)
    big.keyframe_insert(data_path="rotation_euler", index=1, frame=f)
    sml.keyframe_insert(data_path="rotation_euler", index=1, frame=f)
    # 核はゆっくり呼吸
    br = osc(t, 2)
    core_bsdf.inputs["Emission Strength"].default_value = 1.25 + 0.5 * br
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    core_light.data.energy = CORE_LIGHT_W * (0.7 + 0.5 * br)
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
study = add_caption("MIDDLE STUDY 013 — HAGURUMA", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜012と同一＝シリーズの一貫性） ----------
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
bpy.ops.object.camera_add(location=(0.15, -14.5, 2.2))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((-0.25, 0, CENTER_Z + 0.02))  # 大歯車側にやや寄せる
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = big
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_haguruma.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("big", "small", "core"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_haguruma.glb"),
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
    scene.frame_set(1 + N_FRAMES // 4)  # 回転して噛み合いが動くか確認
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_q.png")
    bpy.ops.render.render(write_still=True)
    print(">> test_q render done")

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
