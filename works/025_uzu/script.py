# =============================================================
# monaka design. — MIDDLE STUDY 025 "UZU"（渦）
# 黒い渦が宙でゆっくり回る。外は黒い渦の腕、中心＝眼（め）に
# ライムの光。腕は中心へ吸い込まれ、眼だけが静かに灯る＝真ん中に光。
#
# 機構：黒いボウル状ファンネル（bmesh回転体）の凹んだ中心＝ライム
#   発光の眼（凹面発光で光源を渦の奥に隠す＝007 KIRITORI/023 UTSUWA
#   と同じ手・グレージング #19 と Glare箱 #11 を構造回避／眼は広い凹面
#   パッチで点輝点を作らない）。上に N=5 枚の黒い対数螺旋リッジ（腕）を
#   bmesh 実寸で掃引し field を埋める（#11 を防ぐ・NENRIN/AYA と同じ）。
#   アニメ＝腕だけを渦の法線まわりに 2π/N（72°）回す＝N-fold 対称が
#   自分に一致する整数周期の完全ループ（013 HAGURUMA と同じ）。対数
#   螺旋は自己相似なので回転が「内へ吸い込まれる流れ」に読める。眼は
#   回転対称で静止＝渦は回るが眼は静か。リグ＝渦中心の単一 Tilt-Empty
#   の子に funnel/arms を local 原点中心・location=0 で置き、腕の
#   rotation_euler.z を親フレーム＝傾いた渦法線まわりの回転にする
#   （matrix_parent_inverse は identity のまま＝#9 の罠を構造回避、
#   object.scale/transform_apply 不使用＝#15）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_uzu.py -- <mode...>
#   modes: test | still | anim | glb | blend
#   env: ES_EYE(発光強度) SPEC_FUNNEL COAT_FUNNEL TILT_DEG ROT_SPACINGS
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

CENTER_Z = 1.45            # 浮遊高さ
TILT = math.radians(float(os.environ.get("TILT_DEG", "36")))  # 渦面をカメラ側へ（眼を中央へ）

# --- 渦（浅い螺旋ディスク：深いボウルだと眼が下に沈む→中央に光が来ない） ---
R_OUT = 0.92               # 渦の外半径（直径1.84 ≒ 実効横2.81 の65%・#18）
R_EYE = 0.21               # 眼（ライム発光パッチ）の半径
BOWL_D = 0.22              # 皿の浅い窪み（浅くして眼を視覚中央に保つ）
BOWL_P = 1.9               # プロファイルの指数
RN = 40                    # 半径分割
AN = 128                   # 角度分割

# --- 腕（対数螺旋リッジ） ---
N_ARMS = 5
ARM_R0 = R_EYE * 1.70      # 腕の内端（眼にリッジが噛まないよう外へ）
ARM_R1 = R_OUT * 0.88      # 腕の外端（rimのタブ露出を抑える）
ARM_TURNS = 0.72           # 螺旋の巻き（周）
ARM_W = 0.055              # リッジ幅（接線直交・水平）
ARM_H = 0.050              # リッジ高さ（面法線方向）
ARM_C = 8                  # 断面分割
ARM_M = 52                 # 掃引分割

# --- マテリアル調整（env で hero スイープ） ---
ES_EYE = float(os.environ.get("ES_EYE", "1.9"))  # 2026-07-21引き上げ：旧0.92は白飛び0%最適化のペンキ化（#24）。2.8はGlare箱（#11）が出たため1.9（中間調#A5E02E＋ホットコア・#14改訂）
SPEC_FUNNEL = float(os.environ.get("SPEC_FUNNEL", "0.08"))  # #17-c: 一様bright env下の黒平面/曲面は反射率で決まる
COAT_FUNNEL = float(os.environ.get("COAT_FUNNEL", "0.0"))

FPS = 24
N_FRAMES = 144             # 6秒 完全ループ
ROT_SPACINGS = int(os.environ.get("ROT_SPACINGS", "1"))  # 回す腕間隔数（整数=完全ループ）
STILL_FRAME = int(os.environ.get("STILL_FRAME", "1"))


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

# 黒いファンネル（大きな曲面・一様bright env → 反射率を落とす #17-c）
mat_funnel, fb = make_principled("uzu_funnel")
fb.inputs["Base Color"].default_value = BLACK
fb.inputs["Roughness"].default_value = 0.36
fb.inputs["Specular IOR Level"].default_value = SPEC_FUNNEL
fb.inputs["Coat Weight"].default_value = COAT_FUNNEL
fb.inputs["Coat Roughness"].default_value = 0.20

# 眼（ライム発光・眼はボウル開口から key を拾い得る → #13: 暗ライムベースの純発光体に）
mat_eye, eb = make_principled("uzu_eye")
eb.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)  # #13 反射白の上乗せを消す
eb.inputs["Emission Color"].default_value = LIME
eb.inputs["Emission Strength"].default_value = ES_EYE
eb.inputs["Specular IOR Level"].default_value = 0.10
eb.inputs["Roughness"].default_value = 0.5

# 黒い腕リッジ（曲面・env露出 → 反射率低め #17-c）
mat_arm, ab = make_principled("uzu_arm")
ab.inputs["Base Color"].default_value = BLACK
ab.inputs["Roughness"].default_value = 0.34
ab.inputs["Specular IOR Level"].default_value = 0.12
ab.inputs["Coat Weight"].default_value = 0.05
ab.inputs["Coat Roughness"].default_value = 0.20

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ファンネル形状（局所座標：中心bottom=z0 / 外縁rim=+D） ----------
def funnel_z(r):
    return BOWL_D * (r / R_OUT) ** BOWL_P

bm = bmesh.new()
# 中心ポール
pole = bm.verts.new((0.0, 0.0, funnel_z(0.0)))
rings = []
for i in range(1, RN + 1):
    r = R_OUT * i / RN
    z = funnel_z(r)
    ring = []
    for j in range(AN):
        ang = 2 * math.pi * j / AN
        ring.append(bm.verts.new((r * math.cos(ang), r * math.sin(ang), z)))
    rings.append(ring)

def r_at(i):  # ring index i(1..RN) → radius
    return R_OUT * i / RN

# 中心ファン（pole → ring1）: eye 内なので lime
for j in range(AN):
    j2 = (j + 1) % AN
    f = bm.faces.new((pole, rings[0][j], rings[0][j2]))
    f.material_index = 1  # eye
# リング間クアッド
for i in range(RN - 1):
    r_mid = 0.5 * (r_at(i + 1) + r_at(i + 2))
    mi = 1 if r_mid < R_EYE else 0
    for j in range(AN):
        j2 = (j + 1) % AN
        f = bm.faces.new((rings[i][j], rings[i + 1][j],
                          rings[i + 1][j2], rings[i][j2]))
        f.material_index = mi

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
mesh_f = bpy.data.meshes.new("uzu_funnel_mesh")
bm.to_mesh(mesh_f)
bm.free()

funnel = bpy.data.objects.new("uzu_funnel", mesh_f)
scene.collection.objects.link(funnel)
funnel.data.materials.append(mat_funnel)  # index 0
funnel.data.materials.append(mat_eye)     # index 1
bpy.context.view_layer.objects.active = funnel
funnel.select_set(True)
try:
    bpy.ops.object.shade_auto_smooth(angle=0.9)
except Exception:
    bpy.ops.object.shade_smooth()


# ---------- 腕（対数螺旋リッジ・bmesh掃引） ----------
bm = bmesh.new()
theta_span = ARM_TURNS * 2 * math.pi
k = math.log(ARM_R1 / ARM_R0) / theta_span  # r = ARM_R0 * e^(k*theta)

def spiral_point(theta, phase):
    r = ARM_R0 * math.exp(k * theta)
    ang = theta + phase
    z = funnel_z(r) + ARM_H * 0.6  # 面に載せる
    return Vector((r * math.cos(ang), r * math.sin(ang), z))

for a in range(N_ARMS):
    phase = 2 * math.pi * a / N_ARMS
    centers = []
    tangents = []
    for m in range(ARM_M + 1):
        th = theta_span * m / ARM_M
        centers.append(spiral_point(th, phase))
    for m in range(ARM_M + 1):
        m0 = max(0, m - 1)
        m1 = min(ARM_M, m + 1)
        t = (centers[m1] - centers[m0])
        if t.length < 1e-9:
            t = Vector((1, 0, 0))
        tangents.append(t.normalized())

    rings_a = []
    for m in range(ARM_M + 1):
        P = centers[m]
        T = tangents[m]
        side = T.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        nrm = side.cross(T).normalized()
        # 両端を細らせて水流の筋のようにフェザー（ブラントな端キャップを消す）
        u = m / ARM_M
        taper = 0.06 + 0.94 * max(0.0, min(u / 0.20, (1.0 - u) / 0.20, 1.0))
        ring = []
        for c in range(ARM_C):
            phi = 2 * math.pi * c / ARM_C
            off = (ARM_W * taper * math.cos(phi)) * side \
                + (ARM_H * taper * math.sin(phi)) * nrm
            ring.append(bm.verts.new(P + off))
        rings_a.append(ring)
    # 掃引クアッド
    for m in range(ARM_M):
        for c in range(ARM_C):
            c2 = (c + 1) % ARM_C
            bm.faces.new((rings_a[m][c], rings_a[m][c2],
                          rings_a[m + 1][c2], rings_a[m + 1][c]))
    # 端キャップ
    bm.faces.new([rings_a[0][c] for c in range(ARM_C)][::-1])
    bm.faces.new([rings_a[ARM_M][c] for c in range(ARM_C)])

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
mesh_a = bpy.data.meshes.new("uzu_arms_mesh")
bm.to_mesh(mesh_a)
bm.free()

arms = bpy.data.objects.new("uzu_arms", mesh_a)
scene.collection.objects.link(arms)
arms.data.materials.append(mat_arm)
bpy.context.view_layer.objects.active = arms
arms.select_set(True)
try:
    bpy.ops.object.shade_auto_smooth(angle=0.7)
except Exception:
    bpy.ops.object.shade_smooth()


# ---------- リグ（渦中心の Tilt-Empty） ----------
# TiltRig を渦中心(CENTER_Z)に置き、その local z ＝渦の法線（傾いた軸）。
# 子は mesh を局所原点中心で作り location=0・matrix_parent_inverse=identity。
# → 腕の rotation_euler.z は親フレーム＝傾いた渦法線まわりの回転になる（#9 罠回避）。
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "UzuRig"
rig.rotation_euler = (TILT, 0, 0)
funnel.parent = rig
arms.parent = rig

# ---------- アニメーション（腕を 2π/N・ROT_SPACINGS だけ回す＝完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS
ROT_TOTAL = ROT_SPACINGS * (2 * math.pi / N_ARMS)
for f in range(1, N_FRAMES + 1):
    arms.rotation_euler.z = ROT_TOTAL * (f - 1) / N_FRAMES
    arms.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

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

# キャプションは y=-1.3（カメラ寄り）。3行目クリップ回避で z=0.52/0.34/0.22（#20-b）
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.34), "logo")
study = add_caption("MIDDLE STUDY 025 — UZU", 0.045, (0.15, -1.3, 0.22), "study")

# ---------- ライティング（001と同一＝シリーズの一貫性） ----------
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
look = Vector((0.1, 0, CENTER_Z + 0.05))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = funnel
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "uzu.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("uzu_funnel", "uzu_arms"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "uzu.glb"),
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
    scene.render.filepath = os.path.join(OUT, "uzu_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "uzu_hero.png")
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
    scene.render.filepath = os.path.join(OUT, "uzu_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
