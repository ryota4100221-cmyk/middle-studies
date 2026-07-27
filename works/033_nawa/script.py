# =============================================================
# monaka design. — MIDDLE STUDY 033 "NAWA"（縄 / 三つ撚りの縄 laid rope）
# 黒い縄が宙に立つ。三本の撚り（より）の間に走る溝の奥から、ライム #A5E02E が
# 螺旋の光となって差す。いちばん明るいのは、縄の真ん中。真ん中に、光がある。
#
# 機構: シリーズ初の「自軸まわりの N-fold 回転＝撚りが昇って見える」（barber-pole）。
#   3本の撚りは位相 120° 差の同一螺旋なので、**Z軸まわり 120° の回転で厳密に自分自身に
#   一致する**（013/025 の整数対称ループの螺旋版）。回転を -Z 方向へ回すと、螺旋パターンは
#   見かけ上 PITCH/3 だけ昇る＝「縄が撚り上がっていく」。032 の振り子に続き、発光は一定で
#   物体が動く純モーション（呼吸ループの復活を避ける）。
#   造形＝3本の撚りを bmesh 実寸で掃引（平行移動フレームで断面円を運ぶ・#15）。全体に
#   紡錘テーパー（真ん中が最も太い＝主題の強調）＋両端は先細り（#21 ブラント端回避）。
#   撚り同士は接触させず（R/D < 0.866）三条の螺旋スロットを残す。芯には黒い心縄を通し、
#   スロット越しに白背景が抜けるのを止める（#26②/#28 の裏当てに相当）。
#   光＝#29 の正典どおり「開口と同軸・同形の発光プリズム」＝スロットと同じ螺旋則の
#   発光ライムのバンド（円弧断面の solid）を溝に落とし込む＝裸の緑棒（#13/#18）にならず
#   「溝を満たす光の筋」に読める。溝の深さ（(D+R)-ρ）が斜めからの視線を幾何で遮るので、
#   光は正面で最も明るく側面へ自然に閉じる（人工的フェード不要・032 と同じ手）。
#   Emission は #27 通り「camera が覗く縦軸（Generated Z）の1次元バンドグラデ」＝
#   縄の中央高さをホットコアに白飛びさせ上下へ暗部（白い芯→#A5E02E→暗部の勾配で #24 回避）。
#   → 光の明るい窓は世界に固定され、螺旋だけがその中を通り抜けて昇る。
# 素材: 繊維＝一様bright env 下では鏡面反射率が支配項（#17-c）。Spec 低・Coat 0 の
#   マットな麻縄に。#17-b（紙・布はマット）に倣いラフを高めに。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
#   env: ES_CORE ES_RIM FALLOFF GLOW_E SPEC_ROPE HW_DEG RHO_F QR D0 TURNS HEIGHT CORE
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector, Matrix

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_nawa")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.66          # 縄の中心の world 高さ
LOOK_Z = 1.62            # カメラ注視点

# --- 縄（三つ撚り） ---
NSTR = 3                                                   # 撚りの本数（3＝三つ撚り）
HEIGHT = float(os.environ.get("HEIGHT", "2.24"))           # 縄の全長
D0 = float(os.environ.get("D0", "0.205"))                  # 撚りの中心が乗る半径（中央）
QR = float(os.environ.get("QR", "0.78"))                   # 撚りの太さ / D。0.866 で接触＝溝が閉じる
R0 = D0 * QR
TURNS = float(os.environ.get("TURNS", "1.60"))             # 全長に入る撚りの回数
PITCH = HEIGHT / TURNS                                     # 撚りの一巻きの長さ
PHASE0 = math.radians(float(os.environ.get("PHASE0", "-60")))  # 中央高さの溝を正面（-Y）に向ける

E_END = 0.90             # 紡錘テーパー：両端の太さ倍率（ほぼ均一＝「縄の一節」に読ませる）
E_POW = 0.40             # 紡錘の肩の張り（小さいほど中央が長く太い）
# 端は先細りにせず「切り口＋巻き止め（whipping）」で締める。1周目は先細りが
# 瘤（こぶ）になって「捻り飴／ドリル」に転んだ（#16）。巻き止めは1秒で「縄」に読ませる。
COL_V = 0.032            # 巻き止めの位置（v）。端から少し内側＝先に短い房が残る
COL_H = 0.068            # 巻き止めの高さ（半分）。薄いと hero で「ワッシャー」に見える（#16）
COL_R = 1.022            # 巻き止めの半径 ÷ 縄の外半径。出っ張らせず「締めた帯」に

# 撚り（strand）はさらに細い子縄（yarn）を撚って作る。2周目まで「捻り飴／ドリル」に
# 見えていた主因はこれが無かったこと＝1本のつるりとした太いチューブは飴に見える（#16）。
# 子縄の撚りは親の撚りと逆向き（実際の縄と同じ）。位相は v だけの関数なので 120° 対称は保たれる。
NY = 4                   # 1本の撚りに入る子縄の数
DY = 0.50                # 子縄の芯が乗る半径 ÷ 撚りの半径
RY = 0.52                # 子縄の太さ ÷ 撚りの半径（DY+RY≒1.02 で撚りの外径に一致・互いに融合）
YTURNS = float(os.environ.get("YTURNS", "11.0"))   # 全長に入る子縄の撚り回数
YDIR = -1.0              # 親の撚りと逆向き

NV = 420                 # 撚りの掃引ステップ
NSEG = 10                # 子縄の断面分割
CORE = int(os.environ.get("CORE", "1"))                    # 心縄（白背景の抜け止め）

SPEC_ROPE = float(os.environ.get("SPEC_ROPE", "0.11"))     # #17-c：一様bright env 下は反射率が支配項
ROUGH_ROPE = float(os.environ.get("ROUGH_ROPE", "0.56"))   # #17-b：繊維はマット

# --- 光（溝と同形の発光バンド） ---
RHO_F = float(os.environ.get("RHO_F", "0.52"))             # 発光バンドの半径 = D + RHO_F*R。溝は「外側が広く内へ閉じるV」なので浅い側に置く（scan で確定）
HW_DEG = float(os.environ.get("HW_DEG", "6.0"))           # バンドの方位半幅
THK_EM = 0.014                                             # バンドの肉厚（solid にする）
EM_V0 = float(os.environ.get("EM_V0", "0.28"))             # バンドの縦の範囲＝縄の真ん中だけを灯す
EM_V1 = float(os.environ.get("EM_V1", "0.72"))             # （全長に走らせると暗いライム画素が支配して中間調が沈む＝#14）
EM_FEATH = 0.10                                            # 両端で幅を絞る帯（#21）

ES_CORE = float(os.environ.get("ES_CORE", "5.2"))          # 中央＝ホットコア（白飛びさせハローを出す）#24/#27
ES_RIM = float(os.environ.get("ES_RIM", "0.80"))           # 上下の端＝暗部
FALLOFF = float(os.environ.get("FALLOFF", "0.40"))         # ホットコア→暗部の落ち幅（world m・縦方向）
GLOW_E = float(os.environ.get("GLOW_E", "0.5"))            # 溝からこぼれる光（床・縄へのスピル）#22

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 1          # t=0 ＝ 中央の溝が正面を向く一枚
ROT_DIR = float(os.environ.get("ROT_DIR", "-1"))           # -1 で螺旋が「昇る」
ROT_SPAN = 2 * math.pi / NSTR                              # 120°＝3本撚りの自己一致角＝完全ループ


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 縄の数式（撚りの芯線・テーパー） ----------
def env(v):
    """紡錘テーパー（中央がわずかに太い）。端は切り口のままにして巻き止めで締める。v∈[0,1]"""
    return E_END + (1.0 - E_END) * (math.sin(math.pi * max(0.0, min(1.0, v))) ** E_POW)


def zloc(v):
    return (v - 0.5) * HEIGHT


def phase(k, v):
    """撚り k の方位角。全長で TURNS 回転。120°差＝Z軸 120°回転で自己一致。"""
    return 2 * math.pi * k / NSTR + 2 * math.pi * zloc(v) / PITCH + PHASE0


def pol(rho, phi, z):
    """方位 phi=0 が -Y（カメラ側）を向く極座標（032 surf() と同じ規約）。"""
    return Vector((rho * math.sin(phi), -rho * math.cos(phi), z))


def strand_center(k, v):
    return pol(D0 * env(v), phase(k, v), zloc(v))


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


# 縄（黒い繊維）。#17：曲面は環境光を線状に拾って「黒いプラスチック」に転ぶ／
# #17-c：一様bright env 下では roughness でなく鏡面反射率が支配項。
mat_rope, b = make_principled("nawa_fiber")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_ROPE
b.inputs["Specular IOR Level"].default_value = SPEC_ROPE
b.inputs["Coat Weight"].default_value = 0.0

# 光の筋＝溝と同形の発光バンド。#13 純発光体（Base を暗ライムに落とし反射白の上乗せを消す）。
mat_core, core_bsdf = make_principled("nawa_light")
core_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.10

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：bmesh実寸・object.scale/transform_apply不使用） ----------
def new_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def auto_smooth(o, angle=0.6):
    """PITFALL #6：5.x は shade_auto_smooth(ops)。"""
    for ob in bpy.data.objects:
        ob.select_set(False)
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    try:
        bpy.ops.object.shade_auto_smooth(angle=angle)
    except Exception as e:
        print(">> auto smooth skipped:", e)


def frames_for(pts):
    """平行移動フレーム（parallel transport）。ref=Z は Z回転に不変なので、
    撚り k のフレーム＝撚り 0 のフレームを 120°k 回した物になる＝120° 対称が保たれる。"""
    n = len(pts)
    tans = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        tans.append(t.normalized())
    ref = Vector((0, 0, 1))
    if abs(tans[0].dot(ref)) > 0.9:
        ref = Vector((1, 0, 0))
    nrm = (ref - tans[0] * ref.dot(tans[0])).normalized()
    us, ws = [], []
    for i in range(n):
        if i > 0:
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        us.append(nrm.copy())
        ws.append(tans[i].cross(nrm))
    return tans, us, ws


def sweep_tube(bm, pts, radii, nseg=NSEG, cap='flat'):
    """平行移動フレームで断面円を運ぶ掃引。端は切り口（flat）。"""
    n = len(pts)
    tans, us, ws = frames_for(pts)
    rings = []
    for i in range(n):
        ring = []
        for j in range(nseg):
            a = 2 * math.pi * j / nseg
            ring.append(bm.verts.new(pts[i] + (us[i] * math.cos(a) + ws[i] * math.sin(a)) * radii[i]))
        rings.append(ring)
    for i in range(n - 1):
        for j in range(nseg):
            k = (j + 1) % nseg
            bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    # 端の蓋。'flat'＝切り口（縄は巻き止めで締めるので瘤にしない）／'pole'＝尖端（#21）
    if cap == 'pole':
        p0 = bm.verts.new(pts[0] - tans[0] * radii[0] * 0.7)
        p1 = bm.verts.new(pts[-1] + tans[-1] * radii[-1] * 0.7)
    else:
        p0 = bm.verts.new(pts[0])
        p1 = bm.verts.new(pts[-1])
    for j in range(nseg):
        k = (j + 1) % nseg
        bm.faces.new((p0, rings[0][k], rings[0][j]))
        bm.faces.new((p1, rings[-1][j], rings[-1][k]))


def add_collar(bm, zc, half_h, r_out, seg=48):
    """巻き止め（whipping）＝縄を締める黒い帯。回転対称なので 120° ループを壊さない。
    全部同じ黒マテリアルなので、内部で撚りと交差していても見えない（solid の和）。"""
    prof = [(-half_h, r_out * 0.80), (-half_h * 0.66, r_out),
            (half_h * 0.66, r_out), (half_h, r_out * 0.80)]
    rings = []
    for dz, rr in prof:
        rings.append([bm.verts.new((rr * math.cos(2 * math.pi * j / seg),
                                    rr * math.sin(2 * math.pi * j / seg), zc + dz))
                      for j in range(seg)])
    for i in range(len(rings) - 1):
        for j in range(seg):
            k = (j + 1) % seg
            bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])


# ---------- 縄（3本の撚り＋心縄＋巻き止め） ----------
def build_rope(name):
    bm = bmesh.new()
    for k in range(NSTR):
        pts = [strand_center(k, i / NV) for i in range(NV + 1)]
        _t, us, ws = frames_for(pts)
        for j in range(NY):
            ypts, yrad = [], []
            for i in range(NV + 1):
                v = i / NV
                psi = 2 * math.pi * j / NY + YDIR * 2 * math.pi * YTURNS * v
                ypts.append(pts[i] + (us[i] * math.cos(psi) + ws[i] * math.sin(psi))
                            * (DY * R0 * env(v)))
                yrad.append(RY * R0 * env(v))
            sweep_tube(bm, ypts, yrad)
    if CORE:
        # 心縄＝スロット越しに白背景が抜けるのを止める黒い芯（撚りには触れない太さ）
        cr = (D0 - R0) * 0.92
        pts = [Vector((0.0, 0.0, zloc(i / NV))) for i in range(NV + 1)]
        rad = [cr * env(i / NV) for i in range(NV + 1)]
        sweep_tube(bm, pts, rad, nseg=12)
    for v in (COL_V, 1.0 - COL_V):
        add_collar(bm, zloc(v), COL_H, (D0 + R0) * env(v) * COL_R)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_rope)
    auto_smooth(o)
    return o


# ---------- 光（溝と同軸・同形の発光バンド／#29） ----------
HW = math.radians(HW_DEG)
NA = 6      # バンドの円弧分割


def em_hw(v):
    """バンドの方位半幅。両端 EM_FEATH で絞って尖らせる（#21・端キャップを隠す）。"""
    x = min(v - EM_V0, EM_V1 - v) / (EM_FEATH * (EM_V1 - EM_V0))
    if x >= 1.0:
        return HW
    x = max(0.0, x)
    return HW * (0.08 + 0.92 * (x * x * (3.0 - 2.0 * x)))


def em_rho(v):
    return (D0 + RHO_F * R0) * env(v)


def em_center_phase(k, v):
    """溝の中心＝隣り合う撚りの中間方位。"""
    return phase(k, v) + math.pi / NSTR


def build_light(name):
    bm = bmesh.new()
    nv = 200
    for k in range(NSTR):
        outer, inner = [], []
        for i in range(nv + 1):
            v = EM_V0 + (EM_V1 - EM_V0) * i / nv
            phi0 = em_center_phase(k, v)
            rho = em_rho(v)
            hw = em_hw(v)
            z = zloc(v)
            outer.append([bm.verts.new(pol(rho, phi0 - hw + 2 * hw * j / NA, z)) for j in range(NA + 1)])
            inner.append([bm.verts.new(pol(rho - THK_EM, phi0 - hw + 2 * hw * j / NA, z)) for j in range(NA + 1)])
        for i in range(nv):
            for j in range(NA):
                bm.faces.new((outer[i][j], outer[i][j + 1], outer[i + 1][j + 1], outer[i + 1][j]))
                bm.faces.new((inner[i][j + 1], inner[i][j], inner[i + 1][j], inner[i + 1][j + 1]))
            # 側壁
            bm.faces.new((outer[i][0], outer[i + 1][0], inner[i + 1][0], inner[i][0]))
            bm.faces.new((outer[i][NA], inner[i][NA], inner[i + 1][NA], outer[i + 1][NA]))
        # 端の蓋
        for arr, rev in ((0, False), (nv, True)):
            for j in range(NA):
                q = (outer[arr][j], outer[arr][j + 1], inner[arr][j + 1], inner[arr][j])
                bm.faces.new(tuple(reversed(q)) if rev else q)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_core)
    auto_smooth(o)
    return o


# Emission Strength ＝ Generated Z の1次元バンドグラデ（#27）。
# 縄の中央高さ（Generated z=0.5）をホットコアに白飛びさせ、FALLOFF[m] で暗部へ落とす。
EM_SPAN = (EM_V1 - EM_V0) * HEIGHT
GZ_C = 0.5
GZ_F = FALLOFF / EM_SPAN
_ct = mat_core.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
_dz = _ct.nodes.new("ShaderNodeMath")
_dz.operation = 'SUBTRACT'
_dz.inputs[1].default_value = GZ_C
_ct.links.new(_sep.outputs["Z"], _dz.inputs[0])
_abz = _ct.nodes.new("ShaderNodeMath")
_abz.operation = 'ABSOLUTE'
_ct.links.new(_dz.outputs[0], _abz.inputs[0])
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = GZ_F
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
_ct.links.new(_abz.outputs[0], _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], core_bsdf.inputs["Emission Strength"])


# ---------- リグ（原点の Spin-Empty＝自軸まわりの回転／#9） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "NawaRig"


def child_of(obj, parent, basis=None):
    """parent 付け＋ matrix_parent_inverse=identity（#9）。"""
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix()
    if basis is not None:
        obj.matrix_basis = basis
    return obj


rope = build_rope("nawa_rope")
child_of(rope, rig, Matrix.Translation((0, 0, CENTER_Z)))

light = build_light("nawa_light")
child_of(light, rig, Matrix.Translation((0, 0, CENTER_Z)))

# 溝からこぼれる光（床・縄へのスピル・#22）。発光体の内部に埋めない（#29）。
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
glow = bpy.context.active_object
glow.name = "nawa_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.6
try:
    glow.visible_camera = False
except Exception:
    pass
glow.location = (0.0, -0.80, CENTER_Z)


# ---------- アニメーション（完全ループ＝120°で自己一致） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    rig.rotation_euler = (0.0, 0.0, ROT_DIR * ROT_SPAN * t01)
    rig.keyframe_insert(data_path="rotation_euler", frame=f)
# 毎フレーム打っているので補間設定は不要（PITFALL #1）


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
focus_null = bpy.context.active_object
focus_null.name = "focus_null"


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


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。z=0.52/0.34/0.22。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.34), "logo")
study = add_caption("MIDDLE STUDY 033 — NAWA", 0.045, (0.15, -1.3, 0.22), "study")


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
    # #16/#18/#27：レンダーで目視する前に幾何を数値で当てる。
    outer_r = D0 + R0 * (DY + RY)
    print(f">> rope: D0={D0:.3f} R0={R0:.3f} (R/D={QR:.3f}, 0.866で接触＝溝が閉じる) "
          f"pitch={PITCH:.3f} turns={TURNS:.2f}")
    print(f">> size: width={2*outer_r:.3f} / 2.81 ({2*outer_r/2.81*100:.0f}%)  "
          f"height={HEIGHT:.3f} / 3.52 ({HEIGHT/3.52*100:.0f}%)")
    zb, zt = CENTER_Z - HEIGHT / 2, CENTER_Z + HEIGHT / 2
    print(f">> world z: bottom={zb:.3f} ({'OK 浮遊' if zb > 0.05 else 'WARN 床'})  top={zt:.3f}")

    # 発光バンド → 撚り芯線の最短距離（3D）。R0*env より大きければ撚りに刺さっていない。
    worst = 1e9
    worst_v = 0.0
    centers = []
    for k in range(NSTR):
        centers.append([strand_center(k, i / 600.0) for i in range(601)])
    for i in range(41):
        v = EM_V0 + (EM_V1 - EM_V0) * i / 40.0
        hw = em_hw(v)
        rho = em_rho(v)
        for dj in (-hw, 0.0, hw):
            p = pol(rho, em_center_phase(0, v) + dj, zloc(v))
            for k in range(NSTR):
                for c in centers[k]:
                    d = (p - c).length - R0 * (DY + RY) * env(v)
                    if d < worst:
                        worst, worst_v = d, v
    print(f">> band→strand clearance min={worst:+.4f}m at v={worst_v:.2f} "
          f"({'OK' if worst > 0.004 else 'WARN 撚りに刺さる → HW_DEG か RHO_F を下げる'})")
    print(f">> band: rho={em_rho(0.5):.3f} (溝の深さ {outer_r - em_rho(0.5):.3f}m) "
          f"visible arc width={2*HW*em_rho(0.5):.4f}m  hw={HW_DEG:.1f}deg")
    print(f">> grad: GZ_C={GZ_C:.3f} GZ_F={GZ_F:.4f} (falloff {FALLOFF:.3f}m = 縄の {FALLOFF*2/HEIGHT*100:.0f}%)")
    print(f">> loop: rot {math.degrees(ROT_SPAN):.0f}deg dir={ROT_DIR:+.0f} "
          f"→ 見かけの上昇 {PITCH/NSTR:.3f}m / loop")
    print(f">> ES_CORE={ES_CORE} ES_RIM={ES_RIM} GLOW_E={GLOW_E} SPEC_ROPE={SPEC_ROPE} CORE={CORE}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "nawa.blend"))
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
# （still/anim より前に走ると hero が勾配なしでレンダーされる＝031/032 で踏んだ穴）
if "glb" in modes:
    try:
        for lk in list(core_bsdf.inputs["Emission Strength"].links):
            mat_core.node_tree.links.remove(lk)
        core_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {"nawa_rope", "nawa_light", "NawaRig"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "nawa.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
