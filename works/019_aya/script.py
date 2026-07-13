# =============================================================
# monaka design. — MIDDLE STUDY 019 "AYA"（綾 / 織り目）
# 黒い経糸と緯糸が上下に織り重なるバスケット織の円盤。
# 織り目が締まると真っ黒、緩むと隙間の奥からライム #A5E02E が差す。
# 外は黒、真ん中に光がある——布の織り目に、光がある。
#
# 造形: 経糸(縦=Z方向)・緯糸(横=X方向)をbmeshのsineチューブで生成し、
#       交互位相で互いを上下に潜らせて over/under 交差（バスケット織）。
#       円形にクリップした織り盤の裏中央にライム発光面＋点光源。
# アニメ: シェイプキー "open" でチューブ半径を細らせ隙間を開く単一モーフ。
#       sk(t)=0.5(1-cos2πt) を毎フレームキー＝数学的に完全ループ。
#       (018 SHIZUKU と同じ単一メッシュ＋モーフ方式でglbにもアニメが乗る)
#
# 実行:
#   Blender --background --factory-startup --python monaka_aya.py -- <mode...>
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

CENTER_Z = 1.42     # 浮遊高さ
PITCH = 0.24        # 糸の間隔
RD = 1.05           # 織り盤の半径（円形クリップ）
KMAX = 4            # 中心から片側 ±KMAX 本 → 各方向 2*KMAX+1 = 9 本
AMP = 0.145         # Y方向の織りうねり（over/underの深さ）
R_CLOSED = 0.100    # 締まった状態のチューブ半径（隙間 pitch-2R ≈ 0.04）
R_OPEN = 0.058      # 緩んだ状態のチューブ半径（隙間 ≈ 0.12）
K_SIDES = 10        # チューブ断面の分割
DS = 0.05           # 中心線サンプリング間隔

FPS = 24
N_FRAMES = 120      # 5秒 完全ループ
STILL_FRAME = 61    # t=0.5 → 完全に開いた（最も光る）瞬間をheroに

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

# 黒い糸（布の艶。SOROBANの教訓：平面的な黒は環境光でグレー化するので
# 低ラフ＋控えめスペキュラで黒漆化。丸いチューブなので反射は細い線に収まる）
mat_yarn, b = make_principled("aya_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.34
b.inputs["Specular IOR Level"].default_value = 0.32
b.inputs["Coat Weight"].default_value = 0.12
b.inputs["Coat Roughness"].default_value = 0.14

# 裏で灯るライム発光面
mat_glow, g = make_principled("aya_lime")
g.inputs["Base Color"].default_value = LIME
g.inputs["Emission Color"].default_value = LIME
g.inputs["Emission Strength"].default_value = 2.6
g.inputs["Roughness"].default_value = 0.5

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- 織り盤（bmeshで手続き生成） ----------
# 交差点 (x_i, z_j) で (i+j) が偶数なら経糸が手前(カメラ=-Y側)、奇数なら緯糸が手前。
# これを連続チューブで実現するため、うねりを整数位相の余弦にする：
#   経糸(列k, x=k·p): y(z) = -AMP·(-1)^k·cos(π·z/p)   → 行z_jで y=-AMP·(-1)^(k+j)
#   緯糸(行j, z=j·p): y(x) = +AMP·(-1)^j·cos(π·x/p)   → 列x_iで y=+AMP·(-1)^(i+j)
# 経糸と緯糸は各交差で符号が逆＝上下に割れて over/under に組み合う。
bm = bmesh.new()
open_coords = []   # 各bmesh頂点に対応する "open"(細い)状態の座標（生成順）

def parity(k):
    return -1 if (k % 2) else 1

def add_tube(pts, up):
    """中心線 pts に沿ってチューブを張り、open状態(細い)の座標を記録"""
    rings = []
    n = len(pts)
    for m in range(n):
        if m == 0:
            t = pts[1] - pts[0]
        elif m == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[m + 1] - pts[m - 1]
        t.normalize()
        side = t.cross(up)
        if side.length < 1e-6:
            side = t.cross(Vector((0, 1, 0)))
        side.normalize()
        nrm = side.cross(t)
        nrm.normalize()
        c = pts[m]
        ring = []
        for k in range(K_SIDES):
            a = 2 * math.pi * k / K_SIDES
            dirv = math.cos(a) * side + math.sin(a) * nrm
            v = bm.verts.new(c + R_CLOSED * dirv)
            open_coords.append(c + R_OPEN * dirv)
            ring.append(v)
        rings.append(ring)
    for m in range(n - 1):
        for k in range(K_SIDES):
            k2 = (k + 1) % K_SIDES
            f = bm.faces.new((rings[m][k], rings[m][k2],
                              rings[m + 1][k2], rings[m + 1][k]))
            f.smooth = True
    # 端の蓋（円盤の縁に開口を見せない）
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))

def sample_line(a, b, fn_y, axis):
    """軸(axis='z'|'x')に沿って a→b をサンプルし中心線を返す"""
    length = abs(b - a)
    n = max(6, int(length / DS))
    pts = []
    for m in range(n + 1):
        s = a + (b - a) * m / n
        y = fn_y(s)
        if axis == 'z':
            pts.append(Vector((cur_fixed, y, s)))
        else:
            pts.append(Vector((s, y, cur_fixed)))
    return pts

# 経糸（縦 = Z方向）
for k in range(-KMAX, KMAX + 1):
    xk = k * PITCH
    if xk * xk >= RD * RD:
        continue
    zext = math.sqrt(RD * RD - xk * xk)
    pk = parity(k)
    cur_fixed = xk
    pts = sample_line(-zext, zext,
                      lambda z, pk=pk: -AMP * pk * math.cos(math.pi * z / PITCH),
                      'z')
    add_tube(pts, up=Vector((1, 0, 0)))

# 緯糸（横 = X方向）
for j in range(-KMAX, KMAX + 1):
    zj = j * PITCH
    if zj * zj >= RD * RD:
        continue
    xext = math.sqrt(RD * RD - zj * zj)
    pj = parity(j)
    cur_fixed = zj
    pts = sample_line(-xext, xext,
                      lambda x, pj=pj: AMP * pj * math.cos(math.pi * x / PITCH),
                      'x')
    add_tube(pts, up=Vector((0, 0, 1)))

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
mesh = bpy.data.meshes.new("aya")
bm.to_mesh(mesh)
bm.free()

weave = bpy.data.objects.new("aya", mesh)
scene.collection.objects.link(weave)
weave.data.materials.append(mat_yarn)
weave.location = (0.0, 0.0, CENTER_Z)   # 平メッシュなのでlocation直指定でOK（transform_applyの罠は無関係）
bpy.context.view_layer.objects.active = weave
weave.select_set(True)
try:
    bpy.ops.object.shade_auto_smooth(angle=0.7)
except Exception:
    bpy.ops.object.shade_smooth()

# ---------- シェイプキー "open"（チューブを細らせ隙間を開く） ----------
weave.shape_key_add(name="Basis")
sk_open = weave.shape_key_add(name="open")
for i, co in enumerate(open_coords):
    sk_open.data[i].co = co

# ---------- アニメーション（open値をcosで呼吸＝完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS
kb = weave.data.shape_keys.key_blocks["open"]
kb.slider_min = 0.0
kb.slider_max = 1.0
for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    kb.value = 0.5 * (1 - math.cos(2 * math.pi * t))
    kb.keyframe_insert(data_path="value", frame=f)

# ---------- 裏の発光（中央だけライム＝middle-glowバイアス） ----------
# 織り盤の裏(+Y)中央に小さめのライム面。緩んだ隙間からこれが覗く。
# 面は織り盤より小さくし、盤の縁は白背景＝中央にだけ光がある構図に。
bpy.ops.mesh.primitive_circle_add(radius=0.62, fill_type='NGON',
                                  location=(0.0, 0.30, CENTER_Z))
glow = bpy.context.active_object
glow.name = "lime_back"
glow.rotation_euler = (math.pi / 2, 0, 0)  # 法線を-Y（カメラ）へ向ける
glow.data.materials.append(mat_glow)

# 裏の柔らかいライム点光源（糸の裏面と床にわずかに緑を差す。集中輝点を作らない＝Glare箱回避）
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.62, CENTER_Z))
lp = bpy.context.active_object
lp.name = "lime_point"
lp.data.energy = 42
lp.data.color = LIME[:3]
lp.data.shadow_soft_size = 1.4

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
study = add_caption("MIDDLE STUDY 019 — AYA", 0.045, (0.15, -1.3, 0.06), "study")

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
look = Vector((0.1, 0, CENTER_Z + 0.05))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = weave
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "aya.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name == "aya")
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "aya.glb"),
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
    scene.render.filepath = os.path.join(OUT, "aya_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "aya_hero.png")
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
    scene.render.filepath = os.path.join(OUT, "aya_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
