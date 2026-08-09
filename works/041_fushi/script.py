# =============================================================
# monaka design. — MIDDLE STUDY 041 "FUSHI"（節 / 竹の一節 an internode of bamboo）
# 黒い竹が一節、宙に立つ。上と下に節がある。その二つの節のあいだ——竹のちょうど
# 真ん中——だけが、拗じれて裂け、奥から ライム #A5E02E が差す。捻りが戻れば、
# 裂け目は一条の線に閉じ、光は消える。竹は、節と節のあいだにしか中を持たない。
#
# 【ドメイン】植物・竹（シリーズ未踏）。直近10作（計量・秤／貝・海／折紙／玩具・独楽／
#   武具・鞘／装身・櫛／調度・屏風／縄・繊維／信仰・鈴／建築・灯籠）と別領域。
#   029 MATSUKASA は【植物・種子】＝鱗片の被覆、041 は【竹】＝中空の稈と節。
#
# 【機構】シリーズ初の「**捻り（torsion）で開く**」。開閉(039/024)・折り(034)・
#   撓み(035)・歳差(037)・遮蔽シャッター(040)のどれでもない。
#   ・稈は上下で逆向きに捻られる（ψ に TW·(z/ZH)·γ を足す）。
#   ・裂け目の半角 a(z) = A0 + A_OPEN·γ(t)·s(z)、s(z)=max(0,1−(z/NZ)²)^1.2。
#     s は**節（z=±NZ）で厳密に 0**＝裂け目が開くのは節と節のあいだだけ。
#     s のべき 1.2 は端で導関数 0 ＝ 亀裂の先端が尖ってフェザーする（#21/#31-c）。
#   ・γ(t) = 0.5(1−cos2πt)（整数周期＝t=0 と t=1 が厳密一致＝完全ループ）。
#   → 開口の面積がそのまま光の量になる（#40⑥ の検算を probe に入れてある）。
#     hero は γ=1（最も開いた位相）＝ STILL_FRAME=61。
#   ・実装はシェイプキー1枚（closed→open）。頂点は実寸で作り object.scale /
#     transform_apply は使わない（#15）。glb にモーフとして乗る（018/019 と同じ手）。
#
# 【光】#29 のとおり「開口と同軸・同形の発光体」＝稈の内側に沿う**円筒アークの帯**。
#   裸の緑棒（#13/#18）にならない。勾配は #34 の2軸（長軸=z／短軸=x）を
#   楕円距離1本にまとめ、MapRange(ES_CORE→0, SMOOTHSTEP)。d=1 の縁で ES が
#   厳密に 0 に落ちるので緑スピルが構造的に出ない（#26②/#28）。
#   Base＝純黒・Spec=0（#32：随伴点光源が発光体自身を拡散照明してペンキ化するのを防ぐ）。
#   **発光の半幅 0.0585 < 開口の半幅 0.0713**（#40③：光は開口より細く。太いと
#   横の勾配が縁に隠れて「白い芯の入った蛍光灯」になる）。帯は捻らない＝静止なので
#   #35 の「軸ごとに座標系を変える」は不要（Object 座標1つで足りる）。
#
# 【読み（#16/#33）】「黒いプラスチックのパイプ」（#17 の 021 FUE の罠）に転ばない
#   ための署名ディテール —— ① **節の隆起＋その下のくびれ**（竹の節の断面そのもの）
#   ② 上下に隣の節間の**切り株**を残し、切り口に**中空の環**を見せる（＝中が空である宣言）
#   ③ 縦の繊維条（#31-b の一段細かい階層。捻りで斜めに剪断されるので**捻れが目に見える**）
#   ④ 上へわずかに細るテーパー。#33 の撤退条件（細い部材で中心を囲まない／大きな平円盤を
#   使わない／単一の塊が主役で光は隙間から）を満たす。
#
# 【罠を構造的に回避】object.scale / transform_apply 不使用（#15）・boolean 不使用・
#   リグは原点（#9）・毎フレームキー（#1）・glb は必ず最後尾（#30）。
#   シェイプキーの頂点順を保つため、稈だけ remove_doubles を掛けない（構造上重複なし）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_fushi.py -- <mode...>
#   modes: probe | bbox | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_fushi")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "2.18"))
LOOK_Z = float(os.environ.get("LOOK_Z", "1.72"))
CAM_LOC = (0.55, -8.3, 1.95)

# --- 稈（culm） ---
H = float(os.environ.get("H", "2.20"))          # 全高
ZH = H * 0.5
R_OUT = float(os.environ.get("R_OUT", "0.26"))  # 基準の外半径
TAPER = float(os.environ.get("TAPER", "0.06"))   # 上へ細る
WALL = float(os.environ.get("WALL", "0.042"))    # 肉厚
NZ1 = float(os.environ.get("NZ1", "0.42"))       # 内側の節（＝裂ける節間の両端）
NZ2 = float(os.environ.get("NZ2", "0.94"))       # 外側の節
NODES = (-NZ2, -NZ1, NZ1, NZ2)                   # #32-c：反復の数が「何に見えるか」を決める
NODE_AMP = 0.100      # 節の隆起（相対）＝1周目 0.078 は弱いリブ／2周目 0.130+深いくびれは
NODE_W = 0.020        # 「挽き物の finial」に転んだ。鋭く細いリングに
NODE_DIP = 0.022      # 節の下のくびれ（浅く）
NODE_DW = 0.045
STRI_N = int(os.environ.get("STRI_N", "64"))     # 縦の繊維条の本数
STRI_A = float(os.environ.get("STRI_A", "0.0007"))

# --- 裂け目（split） ---
A0 = float(os.environ.get("A0", "0.026"))        # 閉じたときの半角（一条の線）
A_OPEN = float(os.environ.get("A_OPEN", "0.274"))  # 開きで足す半角
TW = math.radians(float(os.environ.get("TW", "7.4")))  # 捻り（±ZH での ψ オフセット）

# --- 発光帯（#29：開口と同軸・同形。#40③：開口より細く） ---
BAND_R1 = float(os.environ.get("BAND_R1", "0.200"))   # 外半径
BAND_R0 = BAND_R1 - 0.015                               # 内半径
BAND_ARC = float(os.environ.get("BAND_ARC", "0.305"))    # 方位の半角
BAND_ZH = float(os.environ.get("BAND_ZH", "0.34"))      # 帯の実体の半高
FX = BAND_R1 * math.sin(BAND_ARC)   # 短軸の減衰幅＝帯の半幅（縁で ES=0）
FZ = float(os.environ.get("FZ", "0.30"))                # 長軸の減衰幅（#31-d：中央だけ）

# --- 姿勢・運動 ---
CRACK_YAW = math.radians(3.1)   # 裂け目をカメラの光軸へ正対させる（cam x=0.55 / look x=0.1）
SWAY = math.radians(float(os.environ.get("SWAY", "1.6")))
BOB = float(os.environ.get("BOB", "0.013"))

# --- 発光 ---
ES_CORE = float(os.environ.get("ES_CORE", "8.0"))
D_POW = float(os.environ.get("D_POW", "1.0"))   # 楕円距離のべき。小さいほど暗い裾が広がる（#31-d）
GLOW_E = float(os.environ.get("GLOW_E", "0.06"))   # 裂け目の側壁を洗うこぼれ光（#22）

# --- 材質（#17：曲面／#17-c：一様bright env 下は反射率を落とす） ---
SPEC_BLACK = float(os.environ.get("SPEC_BLACK", "0.10"))
ROUGH_BLACK = float(os.environ.get("ROUGH_BLACK", "0.46"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.72")),
         float(os.environ.get("CAP_Z2", "0.54")),
         float(os.environ.get("CAP_Z3", "0.42")))

NA = int(os.environ.get("NA", "256"))   # 方位の分割（STRI_N の整数倍）
FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ
STILL_FRAME = 61          # t=0.5 ＝ γ=1 ＝ 最も開いた位相


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 数式 ----------
def gamma_at(t01):
    """開き。0.5(1−cos2πt)＝t=0 と t=1 が厳密一致＝完全ループ。t=0.5 が hero。"""
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * t01))


def gap_shape(z):
    """裂け目のプロファイル。内側の節（±NZ1）で厳密に 0＝開くのは節と節のあいだだけ。
    べき 1.2 は端で導関数 0 ＝ 亀裂の先端が尖る（#21：ブラント端は機械部品に見える）。"""
    x = z / NZ1
    return max(0.0, 1.0 - x * x) ** 1.2


def half_angle(z, g):
    return A0 + A_OPEN * g * gap_shape(z)


def R_base(z):
    return R_OUT * (1.0 - TAPER * (z + ZH) / (2.0 * ZH))


def node_f(z):
    """節：隆起（鋭いリング）＋その下のくびれ。竹の節の断面そのもの。"""
    f = 1.0
    for zn in NODES:
        d = z - zn
        f += NODE_AMP * math.exp(-(d / NODE_W) ** 2)
        f -= NODE_DIP * math.exp(-((d + 0.055) / NODE_DW) ** 2)
    return f


def R_out_at(z):
    return R_base(z) * node_f(z)


def R_in_at(z):
    return R_base(z) - WALL      # 節では内側が張り出さない＝肉が厚い（実物と同じ）


def stri(u):
    """縦の繊維条。材料（u）に貼り付いているので捻りで斜めに剪断される＝捻れが見える。"""
    return -STRI_A * 0.5 * (1.0 - math.cos(2.0 * math.pi * STRI_N * u))


def culm_point(z, u, g, outer):
    a = half_angle(z, g)
    psi = a + (2.0 * math.pi - 2.0 * a) * u + TW * g * (z / ZH)
    r = (R_out_at(z) + stri(u)) if outer else R_in_at(z)
    return (r * math.sin(psi), -r * math.cos(psi), z)


def win_half_w(z, g):
    """開口（裂け目）の半幅[m]。"""
    return R_out_at(z) * math.sin(half_angle(z, g))


def lit_half_w(z):
    """発光帯のうち ES>0 の半幅[m]（楕円距離 d=1 の内側）。"""
    k = 1.0 - (z / FZ) ** 2
    return FX * math.sqrt(k) if k > 0.0 else 0.0


def lit_area(g, n=601):
    """見える発光面積＝∫ 2·min(開口, 光) dz。機構が光を変えることの検算（#40⑥）。"""
    a = 0.0
    dz = 2.0 * FZ / n
    for i in range(n):
        z = -FZ + (i + 0.5) * dz
        a += 2.0 * min(win_half_w(z, g), lit_half_w(z)) * dz
    return a


def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = math.tan(math.atan(18.0 / 85.0)) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


def z_rows():
    """節の付近だけ密に取る（節の隆起 NODE_W=0.020 を潰さないため）。"""
    segs, prev = [], -ZH
    for zn in NODES:
        segs.append((prev, zn - 0.09, 0.014))
        segs.append((zn - 0.09, zn + 0.09, 0.0060))
        prev = zn + 0.09
    segs.append((prev, ZH, 0.014))
    zs = []
    for (a, b, step) in segs:
        n = max(2, int(round((b - a) / step)))
        for k in range(n):
            zs.append(a + (b - a) * k / n)
    zs.append(ZH)
    return zs


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_take, b = make_principled("fushi_take")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_BLACK
b.inputs["Specular IOR Level"].default_value = SPEC_BLACK
b.inputs["Coat Weight"].default_value = 0.0

# 光＝稈の内側に沿う発光帯。#32：Base は**純黒**（裏当てを兼ねる）
mat_light, light_bsdf = make_principled("fushi_light")
light_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
light_bsdf.inputs["Emission Color"].default_value = LIME
light_bsdf.inputs["Roughness"].default_value = 0.5
light_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_void, b = make_principled("fushi_void")
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
def finish(name, bm, mat, smooth=True, weld=True):
    me = bpy.data.meshes.new(name)
    if weld:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.verts.index_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def add_bevel(o, width=0.0024, angle=55):
    """#10：ANGLE 制限で鋭角の辺だけ面取り。角度は繊維条（〜41°）を拾わない 55° に。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(angle)


def loft(bm, rings, cap=True):
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


# ---------- 造形 ----------
def build_culm():
    """稈＝閉じた多様体（外皮＋内皮＋裂け目の側壁2枚＋上下の切り口の環）。
    シェイプキーのため頂点は生成順を保つ（remove_doubles を掛けない＝構造上重複なし）。"""
    bm = bmesh.new()
    zs = z_rows()
    nv = len(zs)
    V, closed, opened = [], [], []
    io = [[0] * (NA + 1) for _ in range(nv)]
    ii = [[0] * (NA + 1) for _ in range(nv)]

    def emit(p0, p1):
        V.append(bm.verts.new(p0))
        closed.append(p0)
        opened.append(p1)
        return len(V) - 1

    for i, z in enumerate(zs):
        for j in range(NA + 1):
            u = j / NA
            io[i][j] = emit(culm_point(z, u, 0.0, True), culm_point(z, u, 1.0, True))
            ii[i][j] = emit(culm_point(z, u, 0.0, False), culm_point(z, u, 1.0, False))

    for i in range(nv - 1):
        for j in range(NA):
            bm.faces.new((V[io[i][j]], V[io[i][j + 1]],
                          V[io[i + 1][j + 1]], V[io[i + 1][j]]))       # 外皮
            f = bm.faces.new((V[ii[i][j]], V[ii[i][j + 1]],
                              V[ii[i + 1][j + 1]], V[ii[i + 1][j]]))   # 内皮
            f.material_index = 1          # ← 純黒（#17-c：env の Fresnel を殺す）
        for j in (0, NA):                                              # 裂け目の側壁
            f = bm.faces.new((V[io[i][j]], V[ii[i][j]],
                              V[ii[i + 1][j]], V[io[i + 1][j]]))
            f.material_index = 1          # ← 同上。1周目はここが白い一条の線に光った
    for i in (0, nv - 1):                                              # 上下の切り口の環
        for j in range(NA):
            bm.faces.new((V[io[i][j]], V[io[i][j + 1]],
                          V[ii[i][j + 1]], V[ii[i][j]]))

    o = finish("culm", bm, mat_take, smooth=True, weld=False)
    o.data.materials.append(mat_void)
    # シェイプキー1枚（closed → open）。glb にモーフとして乗る（018/019）。
    o.shape_key_add(name="Basis", from_mix=False)
    sk = o.shape_key_add(name="open", from_mix=False)
    for k, p in enumerate(opened):
        sk.data[k].co = p
    sk.value = 0.0
    add_bevel(o, 0.0022, 55)
    return o, sk, len(closed)


def build_septum(z, hz=0.014):
    """節の隔壁。中を覗いても白背景が抜けない（#26②/#28）＋「中が空」の宣言。"""
    bm = bmesh.new()
    r = R_in_at(z) - 0.004
    N = 96
    loop = [(r * math.cos(2 * math.pi * i / N), r * math.sin(2 * math.pi * i / N))
            for i in range(N)]
    rings = [[(x, y, z - hz) for (x, y) in loop], [(x, y, z + hz) for (x, y) in loop]]
    loft(bm, rings, cap=True)
    return finish("septum_%+.2f" % z, bm, mat_void, smooth=False)


def build_band():
    """発光帯＝開口と同軸・同形の円筒アーク（#29）。捻らない＝静止（#35 が不要になる）。"""
    bm = bmesh.new()
    NP = 40
    NZs = 40
    rows = []
    for i in range(NZs + 1):
        z = -BAND_ZH + 2.0 * BAND_ZH * i / NZs
        loop = []
        for k in range(NP + 1):                     # 外面（カメラ側）
            p = -BAND_ARC + 2.0 * BAND_ARC * k / NP
            loop.append((BAND_R1 * math.sin(p), -BAND_R1 * math.cos(p)))
        for k in range(NP, -1, -1):                 # 内面
            p = -BAND_ARC + 2.0 * BAND_ARC * k / NP
            loop.append((BAND_R0 * math.sin(p), -BAND_R0 * math.cos(p)))
        rows.append([(x, y, z) for (x, y) in loop])
    loft(bm, rows, cap=True)
    return finish("band", bm, mat_light, smooth=True)


culm, sk_open, n_verts = build_culm()
septa = [build_septum(zn) for zn in NODES]
septa += [build_septum(ZH - 0.017, 0.017), build_septum(-(ZH - 0.017), 0.017)]
band = build_band()

PARTS = tuple([culm] + septa + [band])


# ---------- リグ（#9：原点に置く／matrix_parent_inverse は identity） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "fushi_pose"
rig.rotation_euler = (0.0, 0.0, CRACK_YAW)

for o in PARTS:
    o.parent = rig
    o.location = (0.0, 0.0, 0.0)


# ---------- 発光の勾配（#34 の2軸を楕円距離で／d=1 の縁で厳密に 0） ----------
_ct = mat_light.node_tree
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


_u1 = _m('MULTIPLY', _sep.outputs["X"], val=1.0 / FX)
_u2 = _m('MULTIPLY', _sep.outputs["Z"], val=1.0 / FZ)
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
_du = _m('POWER', _d, val=D_POW)   # #31-d：べきが小さいと暗い裾が20〜80%帯を占領し中間調が沈む
_ct.links.new(_du, _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], light_bsdf.inputs["Emission Strength"])

# 裂け目の側壁を洗うこぼれ光（#22：面積で稼ぎ強度で稼がない／#14 の spill）
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.0))
glow = bpy.context.active_object
glow.name = "fushi_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.09
glow.parent = rig
glow.location = (0.0, -0.170, 0.0)
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
    g = gamma_at(t)
    sk_open.value = g
    sk_open.keyframe_insert(data_path="value", frame=f)
    rig.location = (0.0, 0.0, CENTER_Z + BOB * math.sin(2.0 * math.pi * t))
    rig.rotation_euler = (0.0, SWAY * math.sin(2.0 * math.pi * t), CRACK_YAW)
    rig.keyframe_insert(data_path="location", frame=f)
    rig.keyframe_insert(data_path="rotation_euler", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, -0.28, CENTER_Z))
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
study = add_caption("MIDDLE STUDY 041 — FUSHI", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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


focus = (0, 0, CENTER_Z - 0.15)
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
    print(">> culm verts=%d  rows=%d  cols=%d" % (n_verts, len(z_rows()), NA + 1))
    dg = bpy.context.evaluated_depsgraph_get()
    for f in (1, 31, STILL_FRAME, 91):
        scene.frame_set(f)
        dg.update()
        xs, zs, ys = [], [], []
        for o in PARTS:
            ob = o.evaluated_get(dg)
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                xs.append(w.x)
                zs.append(w.z)
                ys.append(w.y)
        t = (f - 1) / N_FRAMES
        print(f">> f{f} γ={gamma_at(t):.2f} "
              f"横 {min(xs):+.2f}..{max(xs):+.2f} ({max(xs)-min(xs):.2f}/2.81="
              f"{(max(xs)-min(xs))/2.81*100:.0f}%)  "
              f"縦 {min(zs):.2f}..{max(zs):.2f} ({max(zs)-min(zs):.2f}/3.52="
              f"{(max(zs)-min(zs))/3.52*100:.0f}%)  奥行 {min(ys):+.2f}..{max(ys):+.2f}")
        print(f"   screen 縦 {screen_y(min(zs)):+.3f}..{screen_y(max(zs)):+.3f} "
              f"{'OK' if abs(screen_y(min(zs))) < 0.97 and abs(screen_y(max(zs))) < 0.97 else 'WARN 切れる'}")
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    # 裂け目の開き（幾何）
    print(">> 裂け目の幅[mm]  z:      閉じ    開き    光の半幅")
    for z in (0.0, 0.12, 0.24, 0.36, NZ1, 0.70, NZ2):
        print("   z=%+.2f  %6.1f  %6.1f   %6.1f %s"
              % (z, 2000 * win_half_w(z, 0.0), 2000 * win_half_w(z, 1.0),
                 1000 * lit_half_w(z),
                 "← 節（開かない）" if min(abs(abs(z) - n) for n in NODES) < 1e-6 else ""))
    # #40③：光は開口より細いか
    ok = all(lit_half_w(z) < win_half_w(z, 1.0) + 1e-9
             for z in [i * FZ / 40 for i in range(41)])
    print(">> #40③ 光の半幅 %.4f < 開口の半幅 %.4f (z=0) : %s"
          % (lit_half_w(0.0), win_half_w(0.0, 1.0),
             "OK（光の柔らかい輪郭が見える）" if ok else "WARN 光が開口より太い"))
    print(">> 帯の外半径 %.4f < 内皮 %.4f (z=0) クリアランス %.4f m"
          % (BAND_R1, R_in_at(0.0), R_in_at(0.0) - BAND_R1))
    # #40⑥：機構が本当に光を変えるか
    a1 = lit_area(1.0)
    for g in (0.0, 0.25, 0.5, 0.75, 1.0):
        a = lit_area(g)
        print("   γ=%.2f 見える発光面積 %6.2f cm²  (%3.0f%%)" % (g, a * 1e4, a / a1 * 100))
    print("   " + ("OK（機構がそのまま光の量になる）" if lit_area(0.0) / a1 < 0.75
                   else "WARN 変化が小さい"))
    print(">> loop: γ=0.5(1−cos2πt) 整数周期＝t=0とt=1が厳密一致 / %df %.3fs"
          % (N_FRAMES, N_FRAMES / FPS))

if "bbox" in modes:
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME)
    dg.update()
    for o in PARTS:
        ob = o.evaluated_get(dg)
        ws = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        print(">> %-12s x %+.3f..%+.3f  y %+.3f..%+.3f  z %+.3f..%+.3f  verts=%d"
              % (o.name, min(w.x for w in ws), max(w.x for w in ws),
                 min(w.y for w in ws), max(w.y for w in ws),
                 min(w.z for w in ws), max(w.z for w in ws), len(ob.data.vertices)))

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "fushi.blend"))
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
        for lk in list(light_bsdf.inputs["Emission Strength"].links):
            mat_light.node_tree.links.remove(lk)
        light_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {rig.name} | {o.name for o in PARTS}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "fushi.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_morph=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
