# =============================================================
# monaka design. — MIDDLE STUDY 040 "TENBIN"（天秤 a balance / 釣り合いの支点）
# 黒い天秤が宙に浮き、ゆっくりと傾いては戻る。皿は上下するが、光はどちらの皿にも
# 移らない。支点——竿のちょうど真ん中——だけが、釣り合ったその瞬間にいちばん明るく
# 開く。傾けば光は細く短くなり、水平に戻ればまた一枚のレンズに満ちる。
# 真ん中は、両側が等しいときにだけ見える。
#
# 【ドメイン】計量・秤（シリーズ未踏）。直近10作（貝・海／折紙／玩具・独楽／
#   武具・鞘／装身・櫛／調度・屏風／縄・繊維／信仰・鈴／建築・灯籠／幾何・蜂の巣）
#   と別領域。026 SUNADOKEI は【時間・計測】＝「時を測る」、040 は「重さを測る」。
#
# 【機構】シリーズ初の「**遮蔽シャッター**」＝運動が光の量そのものを決める。
#   ・竿（beam）＋支点座（boss）が world Y 軸まわりに θ 回る（吊りの柄と鐶は回らない）。
#     θ(t) = θMAX·sin(2πt)     ＝ 整数周期＝ t=0 と t=1 が厳密一致＝完全ループ
#   ・boss には**縦長の楕円の窓**が開いている。窓は竿と一緒に回る。
#   ・窓の奥の**発光レンズ（vesica）は回らない**（＝支点に固定）。
#   → 水平（θ=0）で窓とレンズが揃い、光は満ちる。傾くと窓がレンズを斜めに切り、
#     上下が閉じて光は短く細くなる。**芯（レンズ中心）は常に窓の中**なので、
#     ホットコアは真ん中から一歩も動かない（034/035 と同じ主題／#35 の要請）。
#   ・皿は竿端に吊られた剛体なので**平行移動だけ**（実物の天秤と同じ）。
#     θ=0 が hero＝左右対称・光が最大（STILL_FRAME=1）。
#
# 【光】#29 のとおり「開口と同軸・同形の発光体で窓を面で満たす」。裸の緑棒（#13/#18）に
#   しないため、発光体は**幅を持ったレンズ形**（vesica）にして #22「面積で稼ぎ強度で
#   稼がない」を守る。勾配は #34 の2軸を楕円距離で1本にまとめた：
#     d = √((x/VES_W)² + (z/VES_H)²) → MapRange(ES_CORE→0, SMOOTHSTEP)
#   d=1（レンズの縁）で ES が厳密に 0 に落ちる＝緑スピルが構造的に出ない（#26②/#28）。
#   レンズは静止＝回らないので #35 の「軸ごとに座標系を変える」は不要（Object 座標1つ）。
#   Base＝純黒・Spec=0（#32）。さらに背後の**黒い裏板（backing）を boss より小さく**
#   （BACK_R < BOSS_R）作ってあるので、どの角度でも窓の外へ白背景が抜けない（#32/#28）。
#
# 【読み（#16/#33）】「モビール／凧」に転ばないための署名ディテール——
#   ① 竿の**テーパー**（中央が厚く先へ細る＝秤竿）②竿端の**吊り環**
#   ③ 皿は3本の吊り紐で吊る（＝天秤皿の唯一の吊り方）④ 皿の**丸縁（rolled rim）**
#   ——カメラは水平から 2.5°しか上にないので皿は真横から見える。浅い皿は縁の
#   丸みと紐の三脚でしか読めない（#36③ の平皿版）⑤ 回らない**吊りの柄と鐶**が「吊られている」ことを宣言する。
#   #33 の撤退条件（細い部材で中心を囲まない／大きな平円盤を主役にしない／
#   光は隙間から）を満たす。
#
# 【罠を構造的に回避】object.scale / transform_apply 不使用・実寸で頂点を作る（#15）。
#   boolean 不使用（窓は楕円穴つき円板を極座標グリッドで直接張る）。
#   リグは原点（#9・matrix_parent_inverse は identity）。毎フレームキー（#1）。
#   glb は必ず最後尾（#30）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_tenbin.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_tenbin")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "2.10"))   # 支点の world 高さ
LOOK_Z = float(os.environ.get("LOOK_Z", "1.72"))
CAM_LOC = (0.55, -8.3, 1.95)

# --- 竿（beam） ---
ARM = float(os.environ.get("ARM", "0.72"))       # 支点→吊り点の半長
BEAM_Y = float(os.environ.get("BEAM_Y", "0.09"))  # 竿は boss の**奥**（窓を塞がないため）
BM_HZ0 = 0.055   # 中央の半厚（縦）
BM_HZ1 = 0.030   # 先端の半厚
BM_HY0 = 0.042   # 中央の半幅（奥行）
BM_HY1 = 0.026
HOOK_R = 0.026   # 竿端の吊り環（major）
HOOK_T = 0.0075  # 同 minor

# --- 支点座（boss）＝回る遮蔽シャッター ---
BOSS_R = float(os.environ.get("BOSS_R", "0.276"))
BOSS_Y0, BOSS_Y1 = -0.078, -0.030      # 手前（カメラ側）。厚いと窓の内壁が見える
WW = float(os.environ.get("WW", "0.048"))   # 窓（楕円）の半幅
WH = float(os.environ.get("WH", "0.250"))   # 窓（楕円）の半高

# --- 発光レンズ（vesica）＝回らない。**窓より細く低く**（#34）・boss に必ず隠れる ---
VES_W = float(os.environ.get("VES_W", "0.038"))
VES_H = float(os.environ.get("VES_H", "0.215"))
VES_Y0, VES_Y1 = -0.024, -0.012
# 裏板（#32）：BACK_R < BOSS_R なので、どの回転角でも boss の外にはみ出さない
BACK_R = float(os.environ.get("BACK_R", "0.258"))
BACK_Y0, BACK_Y1 = -0.008, 0.030

# --- 吊り（stem＋鐶）＝**回らない**。実物の天秤で竿を支える側。
# 1周目は「回る指針」を立てたが、大きな円板＋テーパーした竿＋先の尖った針で
# hero が **ロケット／ダーツ**に転んだ（#33 の型の失敗）。天秤に読ませるのは
# 「吊られている」という宣言＝上端の鐶（032 SUZU と同じ手）。
STEM_Z1 = float(os.environ.get("STEM_Z1", "0.55"))
STEM_HX, STEM_HY = 0.026, 0.023
RING_R, RING_T = 0.058, 0.014

# --- 皿（pan） ---
PAN_R = float(os.environ.get("PAN_R", "0.20"))
PAN_D = float(os.environ.get("PAN_D", "0.085"))   # 皿の深さ（真横から見て「皿」に読ませる）
PAN_T = 0.011                                     # 皿の厚み
RIM_T = 0.009                                     # 丸縁（#31-b の一段細かい階層）
DROP = float(os.environ.get("DROP", "1.00"))      # 吊り点→皿の縁の高さ
CORD_R = 0.0055
N_CORD = 3
ATT_Z = -0.030    # 吊り点（環の下端）の竿ローカル z

# --- 運動 ---
TH_MAX = math.radians(float(os.environ.get("TH_MAX", "24.0")))
BOB = float(os.environ.get("BOB", "0.014"))

# --- 発光 ---
ES_CORE = float(os.environ.get("ES_CORE", "9.0"))
GLOW_E = float(os.environ.get("GLOW_E", "0.05"))   # 窓の内壁を洗うこぼれ光（#22）

# --- 材質（#17-c：黒は反射率を落とす。曲面の皿は env を拾いやすい） ---
SPEC_BLACK = float(os.environ.get("SPEC_BLACK", "0.10"))
ROUGH_BLACK = float(os.environ.get("ROUGH_BLACK", "0.42"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.66")),
         float(os.environ.get("CAP_Z2", "0.48")),
         float(os.environ.get("CAP_Z3", "0.36")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ
STILL_FRAME = 1           # t=0 ＝ 水平＝左右対称＝光が最大


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 数式 ----------
def theta_at(t01):
    """竿の傾き。sin の整数周期＝ t=0 と t=1 が厳密一致。t=0 が水平＝hero。"""
    return TH_MAX * math.sin(2.0 * math.pi * t01)


def bob_at(t01):
    return BOB * math.sin(2.0 * math.pi * t01)


def rot_y(x, z, th):
    """world Y 軸まわりの回転（+θ で右が下がる）。"""
    c, s = math.cos(th), math.sin(th)
    return (x * c + z * s, -x * s + z * c)


def lit_area(th, n=241):
    """窓（回る）∩ レンズ（回らない）の面積を数値積分。機構が光を変えることの検算。
    レンズ座標 (x,z) が、θ 回った**楕円の窓**の中にあるか＝
    ((x cosθ + z sinθ)/WW)² + ((−x sinθ + z cosθ)/WH)² ≤ 1。"""
    c, s = math.cos(th), math.sin(th)
    a = 0.0
    dz = 2.0 * VES_H / n
    dx = 2.0 * VES_W / n
    for i in range(n):
        z = -VES_H + (i + 0.5) * dz
        w = VES_W * math.sqrt(max(0.0, 1.0 - (z / VES_H) ** 2))
        for j in range(n):
            x = -VES_W + (j + 0.5) * dx
            if abs(x) > w:
                continue
            xp, zp = x * c + z * s, -x * s + z * c
            if (xp / WW) ** 2 + (zp / WH) ** 2 <= 1.0:
                a += dx * dz
    return a


def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = math.tan(math.atan(18.0 / 85.0)) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_iron, b = make_principled("tenbin_iron")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_BLACK
b.inputs["Specular IOR Level"].default_value = SPEC_BLACK
b.inputs["Coat Weight"].default_value = 0.0

# 光＝支点に固定した発光レンズ。#32：Base は**純黒**（裏当てを兼ねる）
mat_lens, lens_bsdf = make_principled("tenbin_light")
lens_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
lens_bsdf.inputs["Emission Color"].default_value = LIME
lens_bsdf.inputs["Roughness"].default_value = 0.5
lens_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_void, b = make_principled("tenbin_void")
b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
b.inputs["Roughness"].default_value = 0.9
b.inputs["Specular IOR Level"].default_value = 0.0
b.inputs["Coat Weight"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
def finish(name, bm, mat, smooth=True):
    me = bpy.data.meshes.new(name)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def add_bevel(o, width=0.0028):
    """#10：ANGLE 制限で鋭角の辺だけ面取り。黒い板の縁を立たせる。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)


def loft(bm, rings, cap=True):
    """rings[i] = 同じ頂点数の閉ループ（座標列）。順に四角で張る。"""
    vs = [[bm.verts.new(tuple(p)) for p in r] for r in rings]
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            bm.faces.new((vs[i][j], vs[i][j2], vs[i + 1][j2], vs[i + 1][j]))
    if cap:
        bm.faces.new(vs[0][::-1])
        bm.faces.new(vs[-1])
    return vs


def tube(bm, p0, p1, r, nseg=14):
    """p0→p1 の丸棒（吊り紐）。平行移動フレームで実寸生成。"""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    a = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(a).normalized()
    v = d.cross(u).normalized()
    rings = []
    for e in (p0, p1):
        rings.append([e + u * (r * math.cos(2 * math.pi * k / nseg))
                      + v * (r * math.sin(2 * math.pi * k / nseg)) for k in range(nseg)])
    loft(bm, rings, cap=True)


def torus(bm, center, axis, R, r, nmaj=44, nmin=12):
    """center を中心に axis を軸とするトーラス（吊り環／皿の丸縁）。"""
    c = Vector(center)
    n = Vector(axis).normalized()
    a = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = n.cross(a).normalized()
    v = n.cross(u).normalized()
    rings = []
    for i in range(nmaj):
        A = 2 * math.pi * i / nmaj
        du = u * math.cos(A) + v * math.sin(A)
        rings.append([c + du * (R + r * math.cos(2 * math.pi * k / nmin))
                      + n * (r * math.sin(2 * math.pi * k / nmin)) for k in range(nmin)])
    rings.append(rings[0])
    vs = [[bm.verts.new(tuple(p)) for p in ring] for ring in rings[:-1]]
    for i in range(nmaj):
        i2 = (i + 1) % nmaj
        for k in range(nmin):
            k2 = (k + 1) % nmin
            bm.faces.new((vs[i][k], vs[i][k2], vs[i2][k2], vs[i2][k]))


# ---------- 造形 ----------
def build_beam():
    """竿：中央が厚く先へ細るテーパー（#16：ただの棒だとモビールに転ぶ）＋竿端の吊り環。"""
    bm = bmesh.new()
    N = 28
    rings = []
    for i in range(N + 1):
        s = i / N
        x = -ARM + 2.0 * ARM * s
        k = abs(2.0 * s - 1.0) ** 1.35          # 0=中央 1=先端
        hz = BM_HZ0 + (BM_HZ1 - BM_HZ0) * k
        hy = BM_HY0 + (BM_HY1 - BM_HY0) * k
        rings.append([(x, BEAM_Y - hy, -hz), (x, BEAM_Y + hy, -hz),
                      (x, BEAM_Y + hy, hz), (x, BEAM_Y - hy, hz)])
    loft(bm, rings, cap=True)
    for sgn in (+1, -1):
        torus(bm, (sgn * ARM, BEAM_Y, ATT_Z + HOOK_R * 0.62), (0, 1, 0), HOOK_R, HOOK_T)
    o = finish("beam", bm, mat_iron, smooth=False)
    add_bevel(o)
    return o


def build_boss():
    """支点座＝**楕円の窓が開いた円板**（回る遮蔽シャッター）。
    boolean は使わない：窓の輪郭 r_in(ψ) から外周 R まで
    極座標グリッドを張るだけで、穴あき円板が閉じた多様体として出る（#15 の発想）。"""
    bm = bmesh.new()
    ps = [2 * math.pi * i / 256 for i in range(256)]

    def r_in(p):
        """窓の輪郭＝楕円（半径 WW×WH）。"""
        c, s = math.cos(p), math.sin(p)
        return 1.0 / math.sqrt((c / WW) ** 2 + (s / WH) ** 2)

    inn, out = [], []
    for p in ps:
        ri = r_in(p)
        inn.append((ri * math.cos(p), ri * math.sin(p)))
        out.append((BOSS_R * math.cos(p), BOSS_R * math.sin(p)))

    def ring(pts, y):
        return [(x, y, z) for (x, z) in pts]

    n = len(ps)
    V = {}
    for tag, pts, y in (("if", inn, BOSS_Y0), ("of", out, BOSS_Y0),
                        ("ib", inn, BOSS_Y1), ("ob", out, BOSS_Y1)):
        V[tag] = [bm.verts.new(p) for p in ring(pts, y)]
    for j in range(n):
        j2 = (j + 1) % n
        bm.faces.new((V["if"][j], V["if"][j2], V["of"][j2], V["of"][j]))   # 前面
        bm.faces.new((V["ob"][j], V["ob"][j2], V["ib"][j2], V["ib"][j]))   # 背面
        bm.faces.new((V["of"][j], V["of"][j2], V["ob"][j2], V["ob"][j]))   # 外周壁
        f = bm.faces.new((V["ib"][j], V["ib"][j2], V["if"][j2], V["if"][j]))  # 窓の内壁
        f.material_index = 1                    # ← 内壁だけ純黒（#32）
    o = finish("boss", bm, mat_iron, smooth=False)
    o.data.materials.append(mat_void)
    add_bevel(o, 0.0022)
    return o


def build_stem():
    """吊り：boss の裏から立ち上がる細い柄と、その先の鐶（かん）。**回らない**ので
    傾いても真上に立ったまま＝「竿が吊られている」ことが一目で分かる（#16）。"""
    bm = bmesh.new()
    N = 10
    rings = []
    for i in range(N + 1):
        z = -0.05 + (STEM_Z1 + 0.05) * i / N
        k = 1.0 - 0.30 * (i / N)
        rings.append([(-STEM_HX * k, BEAM_Y - STEM_HY * k, z),
                      (STEM_HX * k, BEAM_Y - STEM_HY * k, z),
                      (STEM_HX * k, BEAM_Y + STEM_HY * k, z),
                      (-STEM_HX * k, BEAM_Y + STEM_HY * k, z)])
    loft(bm, rings, cap=True)
    torus(bm, (0.0, BEAM_Y, STEM_Z1 + RING_R * 0.80), (0, 1, 0), RING_R, RING_T)
    o = finish("stem", bm, mat_iron, smooth=False)
    add_bevel(o)
    return o


def build_lens():
    """発光レンズ（vesica）。輪郭 x = ±VES_W·√(1−(z/VES_H)²)。厚みのある板。"""
    bm = bmesh.new()
    N = 96
    pts = []
    for i in range(N + 1):
        z = -VES_H + 2.0 * VES_H * i / N
        w = VES_W * math.sqrt(max(0.0, 1.0 - (z / VES_H) ** 2))
        pts.append((w, z))
    loop = [(x, z) for (x, z) in pts] + [(-x, z) for (x, z) in reversed(pts[1:-1])]
    rings = [[(x, VES_Y0, z) for (x, z) in loop], [(x, VES_Y1, z) for (x, z) in loop]]
    loft(bm, rings, cap=True)
    return finish("lens", bm, mat_lens, smooth=False)


def build_backing():
    """裏板（#32）：BACK_R < BOSS_R なので窓の外へ白背景が抜けない。"""
    bm = bmesh.new()
    N = 96
    loop = [(BACK_R * math.cos(2 * math.pi * i / N),
             BACK_R * math.sin(2 * math.pi * i / N)) for i in range(N)]
    rings = [[(x, BACK_Y0, z) for (x, z) in loop], [(x, BACK_Y1, z) for (x, z) in loop]]
    loft(bm, rings, cap=True)
    return finish("backing", bm, mat_void, smooth=False)


def build_pan(name):
    """皿＝浅い椀＋丸縁＋3本の吊り紐。原点は**吊り点**（＝竿端の環）に置く。
    カメラは水平から 2.5°しか上にないので皿は真横に見える（#36③）。
    「皿」に読ませるのは ①椀の断面の弧 ②丸縁の玉 ③三脚の紐 の3つ。"""
    bm = bmesh.new()
    NR, NA = 16, 72
    z0 = -DROP                       # 縁の高さ

    def dish(r):
        return z0 - PAN_D * (1.0 - (r / PAN_R) ** 2)

    up, dn = [], []
    for i in range(NR + 1):
        r = PAN_R * i / NR
        up.append([(r * math.cos(2 * math.pi * j / NA), r * math.sin(2 * math.pi * j / NA),
                    dish(r)) for j in range(NA)])
        dn.append([(r * math.cos(2 * math.pi * j / NA), r * math.sin(2 * math.pi * j / NA),
                    dish(r) - PAN_T) for j in range(NA)])
    Vu = [[bm.verts.new(p) for p in row] for row in up]
    Vd = [[bm.verts.new(p) for p in row] for row in dn]
    for i in range(NR):
        for j in range(NA):
            j2 = (j + 1) % NA
            bm.faces.new((Vu[i][j], Vu[i][j2], Vu[i + 1][j2], Vu[i + 1][j]))
            bm.faces.new((Vd[i + 1][j], Vd[i + 1][j2], Vd[i][j2], Vd[i][j]))
    for j in range(NA):                     # 縁の壁
        j2 = (j + 1) % NA
        bm.faces.new((Vu[NR][j], Vu[NR][j2], Vd[NR][j2], Vd[NR][j]))
    torus(bm, (0, 0, z0 - PAN_T * 0.5), (0, 0, 1), PAN_R, RIM_T)   # 丸縁
    for k in range(N_CORD):                 # 吊り紐（三脚）
        a = 2 * math.pi * k / N_CORD + math.radians(90)
        p = (PAN_R * 0.97 * math.cos(a), PAN_R * 0.97 * math.sin(a), z0 - PAN_T * 0.5)
        tube(bm, (0.0, 0.0, 0.0), p, CORD_R)
    torus(bm, (0, 0, -0.012), (0, 1, 0), 0.017, 0.006)             # 紐の集まる小環
    return finish(name, bm, mat_iron, smooth=True)


beam = build_beam()
boss = build_boss()
stem = build_stem()
lens = build_lens()
backing = build_backing()
pan_R = build_pan("pan_R")
pan_L = build_pan("pan_L")

ROTOR = (beam, boss)
STATIC = (lens, backing, stem)


# ---------- リグ（#9：原点に置く／matrix_parent_inverse は identity） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig_pose = bpy.context.active_object
rig_pose.name = "tenbin_pose"

bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
rig_beam = bpy.context.active_object
rig_beam.name = "tenbin_rotor"
rig_beam.parent = rig_pose
rig_beam.location = (0.0, 0.0, 0.0)

for o in ROTOR:
    o.parent = rig_beam
    o.location = (0.0, 0.0, 0.0)
for o in STATIC:
    o.parent = rig_pose
    o.location = (0.0, 0.0, 0.0)
for o in (pan_R, pan_L):
    o.parent = rig_pose


# ---------- 発光の勾配（#34 の2軸を楕円距離で／d=1 の縁で厳密に 0） ----------
_ct = mat_lens.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Object"], _sep.inputs["Vector"])


def _m(op, a=None, b=None, val=None):
    n = _ct.nodes.new("ShaderNodeMath")
    n.operation = op
    if a is not None:
        _ct.links.new(a, n.inputs[0])
    if b is not None:
        _ct.links.new(b, n.inputs[1])
    if val is not None:
        n.inputs[1].default_value = val
    return n.outputs[0]


# レンズは回らないので座標系は1つで足りる（#35 が問題にするのは「開口と一緒に傾く
# 発光体」の場合。ここは開口だけが回り、光は支点に固定されている）。
_u1 = _m('MULTIPLY', _sep.outputs["X"], val=1.0 / VES_W)
_u2 = _m('MULTIPLY', _sep.outputs["Z"], val=1.0 / VES_H)
_d = _m('SQRT', _m('ADD', _m('MULTIPLY', _u1, _u1), _m('MULTIPLY', _u2, _u2)))

_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 1.0
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = 0.0      # #32：暗部は完全な黒
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'
except Exception:
    pass
_du = _m('POWER', _d, val=0.5)     # ← #24：芯を締め、中間調 #A5E02E の面積を稼ぐ
_ct.links.new(_du, _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], lens_bsdf.inputs["Emission Strength"])

# 窓の内壁を洗うこぼれ光（#22：面積で稼ぎ強度で稼がない）
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.0))
glow = bpy.context.active_object
glow.name = "tenbin_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.10
glow.parent = rig_pose
glow.location = (0.0, -0.018, 0.0)
try:
    glow.visible_camera = False
except Exception:
    pass


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    th = theta_at(t)
    rig_beam.rotation_euler = (0.0, th, 0.0)
    rig_beam.keyframe_insert(data_path="rotation_euler", frame=f)
    for o, sgn in ((pan_R, +1), (pan_L, -1)):
        x, z = rot_y(sgn * ARM, ATT_Z, th)
        o.location = (x, BEAM_Y, z)         # 皿は剛体＝**平行移動だけ**（実物と同じ）
        o.keyframe_insert(data_path="location", frame=f)
    rig_pose.location = (0.0, 0.0, CENTER_Z + bob_at(t))
    rig_pose.keyframe_insert(data_path="location", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, 0, CENTER_Z - 0.25))
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


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, CAP_Z[0]), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, CAP_Z[1]), "logo")
study = add_caption("MIDDLE STUDY 040 — TENBIN", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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


focus = (0, 0, CENTER_Z - 0.25)
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
bpy.ops.object.camera_add(location=CAM_LOC)
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
    # #16/#18：レンダーで目視する前に構図と幾何を数値で当てる。
    dg = bpy.context.evaluated_depsgraph_get()
    for f in (1, N_FRAMES // 4 + 1, N_FRAMES // 2 + 1, 3 * N_FRAMES // 4 + 1):
        scene.frame_set(f)
        dg.update()
        xs, zs, ys = [], [], []
        for o in ROTOR + STATIC + (pan_R, pan_L):
            ob = o.evaluated_get(dg)
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                xs.append(w.x)
                zs.append(w.z)
                ys.append(w.y)
        t = (f - 1) / N_FRAMES
        print(f">> f{f} θ={math.degrees(theta_at(t)):+.1f}° "
              f"横 {min(xs):+.2f}..{max(xs):+.2f} ({max(xs)-min(xs):.2f}/2.81="
              f"{(max(xs)-min(xs))/2.81*100:.0f}%)  "
              f"縦 {min(zs):.2f}..{max(zs):.2f} ({max(zs)-min(zs):.2f}/3.52="
              f"{(max(zs)-min(zs))/3.52*100:.0f}%)  奥行 {min(ys):+.2f}..{max(ys):+.2f}")
        print(f"   screen 縦 {screen_y(min(zs)):+.3f}..{screen_y(max(zs)):+.3f} "
              f"{'OK' if abs(screen_y(min(zs))) < 0.97 and abs(screen_y(max(zs))) < 0.97 else 'WARN 切れる'}")
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    # 機構の検算：窓（回る）∩ レンズ（回らない）の面積が θ で本当に変わるか
    a0 = lit_area(0.0)
    print(f">> 見える発光面積  θ=0°: {a0*1e4:.2f} cm²  (＝hero・最大)")
    for dg_ in (5, 10, 15, 20, 25):
        th = math.radians(dg_)
        if th > TH_MAX + 1e-9:
            continue
        a = lit_area(th)
        print(f"   θ={dg_:>2}°: {a*1e4:.2f} cm²  ({a/a0*100:.0f}%)")
    aM = lit_area(TH_MAX)
    print("   " + ("OK（機構がそのまま光の強弱になる）" if aM / a0 < 0.75
                   else "WARN 変化が小さい＝TH_MAX を上げるか窓を細くする"))
    # 隠蔽の検算：裏板・レンズが boss からはみ出さないか（#28/#32）
    rv = math.hypot(VES_W, VES_H)
    rw = WH
    print(f">> 隠蔽 レンズ最外 {rv:.3f} < 裏板 {BACK_R:.3f} < boss {BOSS_R:.3f} "
          f"{'OK（白背景が抜けない・緑がはみ出さない）' if rv < BACK_R < BOSS_R else 'WARN'}")
    print(f"   窓の長半径 {rw:.3f} < 裏板 {BACK_R:.3f} "
          f"{'OK' if rw < BACK_R else 'WARN 窓から背景が抜ける'}")
    print(f">> 皿の上下動 ±{ARM*math.sin(TH_MAX):.3f}m  "
          f"loop: θ=θMAX·sin(2πt) ＝整数周期＝t=0とt=1が厳密一致 / "
          f"{N_FRAMES}f {N_FRAMES / FPS:.3f}s")

if "bbox" in modes:
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME)
    dg.update()
    for o in ROTOR + STATIC + (pan_R, pan_L):
        ob = o.evaluated_get(dg)
        ws = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        print(">> %-9s x %+.3f..%+.3f  y %+.3f..%+.3f  z %+.3f..%+.3f  verts=%d"
              % (o.name, min(w.x for w in ws), max(w.x for w in ws),
                 min(w.y for w in ws), max(w.y for w in ws),
                 min(w.z for w in ws), max(w.z for w in ws), len(ob.data.vertices)))

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "tenbin.blend"))
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
        for lk in list(lens_bsdf.inputs["Emission Strength"].links):
            mat_lens.node_tree.links.remove(lk)
        lens_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {rig_pose.name, rig_beam.name, pan_R.name, pan_L.name} \
        | {o.name for o in ROTOR} | {o.name for o in STATIC}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "tenbin.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
