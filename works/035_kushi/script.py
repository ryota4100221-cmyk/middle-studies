# =============================================================
# monaka design. — MIDDLE STUDY 035 "KUSHI"（櫛 / 挿し櫛 a comb）
# 黒い櫛が宙に立つ。25本の歯が下へ並び、真ん中の歯と歯のあいだ——そこだけ、
# 奥から ライム #A5E02E が差す。歯は扇のようにしなって開き、また閉じる。
# 光の窓は動かない。真ん中に、光がある。
#
# 機構: シリーズ初の「歯のしなり（弾性たわみ）」。各歯は峰（背）に埋まった根元を
#   支点に、中心から外へ比例した角 θ_i(t) = −θMAX·(x_i/HW)·s(t) で扇状に開く
#   （中央の歯は動かず、端の歯ほど大きく振れる＝薄い材が撓む実際の挙動）。
#   s(t)=0.5(1−cos2πt) は cos なので t=0 と t=1 が厳密に一致＝完全ループ（毎フレームキー #1）。
#   開くと隣り合う歯の隙間が広がって奥の光が増え、閉じると歯が光を覆う＝
#   **機構がそのまま光の強弱になる**（034 屏風で確立した美点／動きの種類は新規）。
#   032 振り子・033 自軸回転・034 折り に続く純モーション（発光は一定・物体だけが動く）。
#   造形は #15 のとおり実寸で頂点を作り object.scale / transform_apply 不使用。
#   各歯は独立オブジェクトで location（根元）＋rotation_euler を直接キー（#9 と整合）。
#   光＝#29 の正典どおり「開口と同軸・同形の発光スラブ」を歯の奥に置いて隙間を面で満たす
#   （裸の緑板 #13/#18 回避）。Emission は #27 の1次元バンドグラデを2軸に：
#   Generated X（横＝真ん中の歯間をホットに）× Generated Z（縦＝歯の中ほどをホットに）。
#   発光はスラブの中央だけ・外はES=0＝**スラブ自身が裏当てを兼ねて白背景の抜けを止める**
#   （#32／#26②／#28。暗部を純黒に落とすので #31-d の「中間調が沈む」も同時に回避）。
#   Base=純黒・Spec=0（#32：随伴のライム点光源に拡散照明されてペンキ化するのを防ぐ）。
# 素材: 一様bright env 下の**平らな面**は鏡面反射率が支配項（#17-c）＝Spec 低・Coat 0 で
#   黒を黒に保ち、縁だけフレネルで立たせる。峰（黒漆）と歯（半艶）でわずかに差をつけ階層を作る（#17-b）。
# 没にした案: 035 は当初「鼓（つづみ）」で8周したが、上下の大きな革＋細い緒が中心を囲む形は
#   黒一色にすると必ず「鳥籠／スツール／行灯」に転び（004 ANDON の再演）、収束しなかった。→ PITFALLS #33
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
#   env: ES_CORE ES_RIM FX FZ GLOW_E THETA N_TEETH L_TOOTH TESTFRAME
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_kushi")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.60          # 櫛の中心の world 高さ
LOOK_Z = 1.55            # カメラ注視点

# --- 櫛 ---
HW = float(os.environ.get("HW", "0.75"))                   # 半幅
N_TEETH = int(os.environ.get("N_TEETH", "25"))             # 歯の数（#32-c：繰り返しの数が「何に見えるか」を決める）
W_TOOTH = float(os.environ.get("W_TOOTH", "0.030"))        # 歯の幅
T_TOOTH = 0.070                                            # 歯の厚み（奥行き）
L_TOOTH = float(os.environ.get("L_TOOTH", "1.10"))         # 歯の長さ
TIP = 0.20                                                 # 先細りの区間（歯先を細らせる＝角材化を防ぐ #21）
TIP_K = 0.34                                               # 先端の細さ
ROOT = 0.06                                                # 歯の根元を峰へ埋める量（開いても隙間が出ない）
SPINE_H = float(os.environ.get("SPINE_H", "0.55"))         # 峰（背）の高さ
SPINE_C = 0.55                                             # 峰の弧（端でどれだけ低くなるか）
T_SPINE = 0.100                                            # 峰の厚み（歯より厚い＝「背」の階層）
THETA = math.radians(float(os.environ.get("THETA", "8.0")))  # 端の歯の最大の開き

SPEC_TOOTH = float(os.environ.get("SPEC_TOOTH", "0.10"))   # #17-c：平面×一様bright env は反射率が支配項
ROUGH_TOOTH = float(os.environ.get("ROUGH_TOOTH", "0.38"))
SPEC_SPINE = float(os.environ.get("SPEC_SPINE", "0.15"))
ROUGH_SPINE = float(os.environ.get("ROUGH_SPINE", "0.30"))
COAT_TOOTH = float(os.environ.get("COAT_TOOTH", "0.0"))
COAT_SPINE = float(os.environ.get("COAT_SPINE", "0.06"))

# --- 光（歯間と同軸・同形の発光スラブ／#29） ---
D_EM = float(os.environ.get("D_EM", "0.055"))              # 歯の面からの奥行き
TE = 0.030                                                 # スラブの肉厚
# #26②：裏当てを外形まで広げるとシルエットが「黒い板」になりモチーフが埋もれる。
# スラブは真ん中の歯間を満たすぶんだけ。外側の歯の隙間からは白背景が抜けてよい（＝櫛らしさ）。
LIGHT_CZ = -L_TOOTH * 0.50                                 # 光の中心＝歯の中ほど
FX = float(os.environ.get("FX", "0.21"))                   # 横：真ん中の光の広がり（world m）＝「真ん中に光」
FZ = float(os.environ.get("FZ", "0.28"))                   # 縦：ホットコア→暗部（world m）#31-d
EM_K = 1.00                                                # スラブの輪郭は減衰と同形（楕円）＝黒い矩形の端を見せない
ES_CORE = float(os.environ.get("ES_CORE", "7.2"))
ES_RIM = float(os.environ.get("ES_RIM", "0.0"))            # #32：暗部は完全な黒＝裏当てになる
GLOW_E = float(os.environ.get("GLOW_E", "0.8"))            # 歯・床へこぼれる光（#22）

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 61         # t=0.5 ＝ s=1（歯がいちばん開いた一枚）

PITCH = 2 * HW / N_TEETH
Z0 = CENTER_Z + (L_TOOTH - SPINE_H) / 2   # 櫛の上下の中心が CENTER_Z に来るよう置く


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- しなりの数式（完全ループ） ----------
def s_at(t01):
    """開き。cos なので t=0 と t=1 が厳密に一致＝数学的に閉じる。"""
    return 0.5 * (1.0 - math.cos(2 * math.pi * t01))


def tooth_x(i):
    return -HW + PITCH * (i + 0.5)


def theta_i(i, s):
    """中央の歯は動かず、端の歯ほど大きく開く（薄い材のたわみ）。"""
    return -THETA * (tooth_x(i) / HW) * s


def spine_top(x):
    """峰（背）の上縁。中央が高く端が低い緩い弧。"""
    return SPINE_H * (1.0 - SPINE_C * (x / HW) ** 2)


def gap_at(s):
    """隣り合う歯先の隙間（機構＝光の強弱を数値で確認する）。"""
    d = (PITCH / HW) * THETA * s * L_TOOTH
    return PITCH - W_TOOTH + d


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_tooth, b = make_principled("kushi_tooth")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_TOOTH
b.inputs["Specular IOR Level"].default_value = SPEC_TOOTH
b.inputs["Coat Weight"].default_value = COAT_TOOTH

mat_spine, b = make_principled("kushi_spine")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_SPINE
b.inputs["Specular IOR Level"].default_value = SPEC_SPINE
b.inputs["Coat Weight"].default_value = COAT_SPINE

# 光＝歯間と同形の発光スラブ。#13 純発光体／#32 Base は**純黒**
mat_core, core_bsdf = make_principled("kushi_light")
core_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る） ----------
def mesh_object(name, verts, faces, mats):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [list(f) for f in faces])
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    for m in mats:
        o.data.materials.append(m)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return o


def add_bevel(o, width=0.0026):
    """#10：ANGLE 制限で鋭角の辺だけ面取り。#17-c の「縁だけフレネルで立つ」を効かせる。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)


def prism(outline, ty0, ty1):
    """xz 平面の閉じた輪郭を y 方向に押し出して閉じたソリッドにする。"""
    n = len(outline)
    verts = [(x, ty0, z) for (x, z) in outline] + [(x, ty1, z) for (x, z) in outline]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    faces.append(list(range(n - 1, -1, -1)))
    faces.append(list(range(n, 2 * n)))
    return verts, faces


# ---------- 峰（背） ----------
def build_spine():
    ns = 96
    outline = [(-HW, 0.0), (HW, 0.0)]
    outline += [(HW - 2 * HW * i / ns, spine_top(HW - 2 * HW * i / ns)) for i in range(ns + 1)]
    verts, faces = prism(outline, -T_SPINE / 2, T_SPINE / 2)
    o = mesh_object("kushi_spine", verts, faces, [mat_spine])
    add_bevel(o, 0.0035)
    o.location = (0.0, 0.0, Z0)
    return o


# ---------- 歯（ローカル原点＝根元。回転はここを支点にする） ----------
def build_tooth(name):
    nz = 20
    verts, faces = [], []
    for k in range(nz + 1):
        u = k / nz
        z = ROOT - (ROOT + L_TOOTH) * u
        d = (-z) / L_TOOTH
        f = 1.0 if d < 1 - TIP else TIP_K + (1 - TIP_K) * max(0.0, (1 - d) / TIP)
        hw, hy = W_TOOTH / 2 * f, T_TOOTH / 2 * f
        verts += [(-hw, -hy, z), (hw, -hy, z), (hw, hy, z), (-hw, hy, z)]
    for k in range(nz):
        for j in range(4):
            j2 = (j + 1) % 4
            faces.append([k * 4 + j, k * 4 + j2, (k + 1) * 4 + j2, (k + 1) * 4 + j])
    faces.append([3, 2, 1, 0])
    faces.append([nz * 4 + 0, nz * 4 + 1, nz * 4 + 2, nz * 4 + 3])
    o = mesh_object(name, verts, faces, [mat_tooth])
    add_bevel(o)
    return o


spine = build_spine()
teeth = []
for i in range(N_TEETH):
    t = build_tooth("kushi_tooth%02d" % (i + 1))
    t.location = (tooth_x(i), 0.0, Z0)
    teeth.append((t, i))


# ---------- 光（歯間と同軸・同形の発光スラブ／#29） ----------
def build_light():
    # 輪郭＝発光の減衰と同形の楕円。矩形にすると純黒の端が白背景を背に「黒い板」として見える（#26②）。
    ns = 48
    outline = [(FX * EM_K * math.cos(2 * math.pi * i / ns),
                LIGHT_CZ + FZ * EM_K * math.sin(2 * math.pi * i / ns)) for i in range(ns)]
    verts, faces = prism(outline, D_EM - TE / 2, D_EM + TE / 2)
    o = mesh_object("kushi_light", verts, faces, [mat_core])
    o.location = (0.0, 0.0, Z0)
    return o


light = build_light()

# Emission = Generated X（横：真ん中の歯間をホットに）× Generated Z（縦：歯の中ほど）
# #27 の1次元バンドグラデを2軸に。スラブの外周は ES=0 ＝ 純黒の裏当て（#32/#26②）。
_ct = mat_core.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
_sq = []
for ax in ("X", "Z"):
    sub = _ct.nodes.new("ShaderNodeMath")
    sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = 0.5
    _ct.links.new(_sep.outputs[ax], sub.inputs[0])
    sc = _ct.nodes.new("ShaderNodeMath")
    sc.operation = 'MULTIPLY'
    sc.inputs[1].default_value = 2.0 * EM_K      # Generated 半幅 0.5 → 楕円半径 EM_K
    _ct.links.new(sub.outputs[0], sc.inputs[0])
    m2 = _ct.nodes.new("ShaderNodeMath")
    m2.operation = 'MULTIPLY'
    _ct.links.new(sc.outputs[0], m2.inputs[0])
    _ct.links.new(sc.outputs[0], m2.inputs[1])
    _sq.append(m2)
_add = _ct.nodes.new("ShaderNodeMath")
_add.operation = 'ADD'
_ct.links.new(_sq[0].outputs[0], _add.inputs[0])
_ct.links.new(_sq[1].outputs[0], _add.inputs[1])
_sqrt = _ct.nodes.new("ShaderNodeMath")
_sqrt.operation = 'SQRT'
_ct.links.new(_add.outputs[0], _sqrt.inputs[0])
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 1.0       # 楕円の縁でちょうど ES_RIM（=0）＝端は純黒
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'   # 端の境界を柔らかく（線形だと「緑の卵」の縁が立つ＝#24）
except Exception:
    pass
_ct.links.new(_sqrt.outputs[0], _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], core_bsdf.inputs["Emission Strength"])

# 歯間からこぼれる光（#22）。発光体の内部に埋めない（#29）。
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.030, Z0 - L_TOOTH / 2))
glow = bpy.context.active_object
glow.name = "kushi_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.5
try:
    glow.visible_camera = False
except Exception:
    pass


# ---------- アニメーション（開き s(t)=0.5(1−cos2πt)＝完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    s = s_at((f - 1) / N_FRAMES)
    for (o, i) in teeth:
        o.rotation_euler = (0.0, theta_i(i, s), 0.0)
        o.keyframe_insert(data_path="rotation_euler", frame=f)
# 毎フレーム打っているので補間設定は不要（PITFALL #1）


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
focus_null = bpy.context.active_object
focus_null.name = "focus_null"


def add_caption(body_text, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object
    tx.name = name
    tx.data.body = body_text
    tx.data.size = size
    tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。z=0.52/0.34/0.22。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.34), "logo")
study = add_caption("MIDDLE STUDY 035 — KUSHI", 0.045, (0.15, -1.3, 0.22), "study")


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
look = Vector((0.1, 0, LOOK_Z))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus_null
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


# ---------- コンポジター（Bloom / PITFALL #3の新方式） ----------
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

if "probe" in modes:
    # #16/#18：レンダーで目視する前に幾何を数値で当てる。
    CAM = (0.55, -8.3)
    for tag, s in (("閉 s=0", 0.0), ("開 s=1", 1.0)):
        wdt = 2 * (HW + THETA * s * L_TOOTH)
        print(f">> {tag}: 全幅={wdt:.3f}/2.81 ({wdt / 2.81 * 100:.0f}%)  "
              f"歯先の隙間={gap_at(s):.4f}m ({gap_at(s) / gap_at(0.0) * 100:.0f}%)")
    H_ALL = L_TOOTH + SPINE_H
    print(f">> 高さ={H_ALL:.3f}/3.52 ({H_ALL / 3.52 * 100:.0f}%)  "
          f"world z: bottom={Z0 - L_TOOTH:.3f} "
          f"({'OK 浮遊' if Z0 - L_TOOTH > 0.05 else 'WARN 床'})  top={Z0 + SPINE_H:.3f}")
    print(f">> caption top z=0.52 < 歯先 z={Z0 - L_TOOTH:.3f} "
          f"({'OK' if Z0 - L_TOOTH > 0.60 else 'WARN 重なる'})")
    print(f">> 歯 {N_TEETH}本  ピッチ={PITCH:.4f}  歯幅={W_TOOTH:.3f}  "
          f"隙間(閉)={PITCH - W_TOOTH:.4f}")
    # スラブが櫛を完全に覆うか＝白背景の抜け止め（#26②/#28/#32-b）
    ez0, ez1 = LIGHT_CZ - FZ * EM_K, LIGHT_CZ + FZ * EM_K
    print(f">> スラブ 楕円 {FX * EM_K:.3f}x{FZ * EM_K:.3f} @z={LIGHT_CZ:.2f}  "
          f"z {ez0:.2f}..{ez1:.2f}（歯 {-L_TOOTH:.2f}..0 の内側 "
          f"{'OK' if ez0 > -L_TOOTH and ez1 < 0.0 else 'WARN 歯からはみ出す'}）")
    print(f">> grad: 横 ±{FX:.2f}m（櫛幅の {FX / HW * 100:.0f}%＝真ん中／#31-d）  "
          f"縦 ±{FZ:.2f}m  ES {ES_CORE}→{ES_RIM}")
    print(f">> loop: s=0.5(1-cos2pi t) ＝ t=0/t=1 厳密一致 / {N_FRAMES}f {N_FRAMES / FPS:.3f}s  "
          f"θmax={math.degrees(THETA):.1f}deg")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "kushi.blend"))
    print(">> saved .blend")

if "test" in modes:
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "testhero" in modes:
    # PITFALL #16：480pxでは「何に見えるか」が見えない。造形が固まったら hero で目視。
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test_hero") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> hero-size test done")

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
    scene.render.image_settings.media_type = 'VIDEO'   # PITFALL #2
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

# 🔴 PITFALL #30：glb は Emission を定数へ潰す副作用があるので必ず最後尾に置く。
if "glb" in modes:
    try:
        for lk in list(core_bsdf.inputs["Emission Strength"].links):
            mat_core.node_tree.links.remove(lk)
        core_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {o.name for (o, i) in teeth} | {"kushi_spine", "kushi_light"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "kushi.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
