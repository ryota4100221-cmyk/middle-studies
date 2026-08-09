# =============================================================
# monaka design. — MIDDLE STUDY 044 "SHINBASHIRA"（心柱 / the heart pillar）
# 黒い五重塔が宙に浮く。五つの層が、互い違いに、ゆっくりと捻れる。
# 塔の中心を貫く心柱（しんばしら）だけは、どの層にも繋がっていない——だから動かない。
# 層が捻れて扉が心柱から外れると光は細り、真っ直ぐに揃った瞬間、
# ちょうど真ん中の層——三重目——の扉の奥から、ライム #A5E02E がいちばん深く差す。
#
# 【ドメイン】建築・寺社／五重塔（シリーズ未踏）。直近10作（虫・生命／工芸・繕い／
#   植物・竹／計量・秤／貝・海／折紙／玩具・独楽／武具・鞘／装身・櫛／調度・屏風）と別領域。
#   031 TOURO（石灯籠）は「窓を面で満たす灯り」＝灯籠。044 は「塊の連なりの、
#   ただ一つの扉の奥に細い光」＝#43② の逆＝行灯にしないための構え。
#
# 【機構】シリーズ初の「**捻れによる開口の走査（rotational scan）**」。
#   ・各層（body＋roof）を塔の軸まわりに θ_k(t)=Θ·w_k·sin2πt で回す。
#     w=(0.45,−0.80,+1.00,−0.80,0.45)＝交互・対称・**真ん中が最大**（蛇行振動の腹）。
#   ・扉は前面の壁にしか無いので、層が回ると扉は軸から横へ a·sinθ だけ振れ、
#     幅は DW·cosθ に縮む。心柱（半径 RP・不動）との重なりがそのまま光の量になる。
#     probe の実測で 100%→42%（#40⑥ の「75% を切る」を満たす）。
#   ・sin の1周期＝完全ループ。**光は真ん中から一切動かない**（#35 の主題を、
#     モチーフを回す側で書いた版）。相輪も心柱に載っているので動かない。
#
# 【光】心柱＝Base 純黒＋Spec 0（#32：随伴光で暗部が緑のベタになるのを構造回避）。
#   勾配は #34 の2軸楕円距離を **UV に焼き込む**（#39）：u=x/FX（＝心柱の半径。
#   シルエットの縁で ES が厳密に 0＝そのまま裏当て）、v=(z−Z_HOT)/FZ。
#   FZ は塔の全高の 26% しかないので、光は**三重目とその上下**にしか居ない（#43②/#31-d）。
#   一重目・五重目の扉の奥は「黒い心柱」＝暗い開口として読める。
#
# 【型（#33）】①細い部材で中心を囲まない（層は板壁の塊）②大きな平円盤を使わない
#   （屋根は反りのある寄棟＝天板に読めない）③塊が主役・光は細い扉 ④相輪が
#   「五重塔である」ことを1秒で宣言する（#40① の"支えている側を出す"に相当）。
#   屋根は**中空にせず平らな軒天の solid**にする＝屋根裏が出来ないので、
#   軒の隙間から心柱が覗いて「光る継ぎ目」になる事故（#32-b/#38②）を構造的に消す。
#
# 実行:
#   Blender --background --factory-startup --python monaka_shinbashira.py -- <mode...>
#   modes: probe | bbox | test | testhero | still | anim | blend | glb  （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

TAU = math.pi * 2.0
SQ2 = math.sqrt(2.0)

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_shinbashira")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "1.88"))
LOOK_Z = float(os.environ.get("LOOK_Z", "1.72"))
CAM_LOC = (0.55, -8.3, 1.95)

NST = 5
TS = float(os.environ.get("TS", "0.735"))          # 塔ぜんたいの寸法係数

UWB = (0.300, 0.272, 0.247, 0.224, 0.203)         # 塔身の半幅（単位）
UWR = (0.606, 0.554, 0.506, 0.463, 0.424)         # 軒の半幅（単位）
UHB = (0.320, 0.296, 0.274, 0.254, 0.236)         # 塔身の高さ（単位）
UHR = (0.352, 0.322, 0.293, 0.269, 0.318)         # 軒→頂までの立ち上がり（単位）

WB = [v * TS for v in UWB]
WR = [v * TS for v in UWR]
HB = [v * TS for v in UHB]
HR = [v * TS for v in UHR]

FT = [0.30, 0.30, 0.30, 0.30, 0.22]               # 屋根の頂部半径／軒半径
CUP = float(os.environ.get("CUP", "0.118"))       # 隅の反り（軒半幅に対する比）
EAVE_T = float(os.environ.get("EAVE_T", "0.028")) # 軒の見えがかりの厚み
TW = float(os.environ.get("TW", "0.030"))         # 壁の厚み
NU = 9
NPSI = 96                                         # 96 は 45°/90° に頂点が乗る（隅棟が立つ）

# --- 扉（開口）と心柱（光） ---
DW = float(os.environ.get("DW", "0.066"))         # 扉の半幅
RP = float(os.environ.get("RP", "0.063"))         # 心柱の半径
FX = float(os.environ.get("FX", "0.064"))         # 短軸（画面の横）の減衰幅＝縁で ES=0（#34）
FZ = float(os.environ.get("FZ", "0.550"))         # 長軸（縦）の減衰幅＝全高の 26%（#43②）
ES_CORE = float(os.environ.get("ES_CORE", "4.0"))
D_POW = float(os.environ.get("D_POW", "2.05"))    # #38④：暗い裾の広さ＝中間調
RAYK = 0.55 / 8.3                                 # カメラの横オフセット由来の視線の傾き
DOOR_DX_K = float(os.environ.get("DOOR_DX_K", "1.0"))

# --- 捻れ（機構） ---
THETA = math.radians(float(os.environ.get("THETA", "26.5")))
W_MODE = (0.45, -0.80, 1.00, -0.80, 0.45)         # 交互・対称・真ん中が腹

# --- 材質（#17-c/#39-c：一様bright env では反射率が支配項） ---
SPEC_ROOF = float(os.environ.get("SPEC_ROOF", "0.18"))
ROUGH_ROOF = float(os.environ.get("ROUGH_ROOF", "0.52"))
SPEC_BODY = float(os.environ.get("SPEC_BODY", "0.18"))
ROUGH_BODY = float(os.environ.get("ROUGH_BODY", "0.46"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.72")),
         float(os.environ.get("CAP_Z2", "0.54")),
         float(os.environ.get("CAP_Z3", "0.42")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92
                 for v in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 縦の積み上げ（屋根の中に上層が座る＝屋根裏を作らない） ----------
PLAT_H = (0.030 * TS, 0.064 * TS)     # 基壇 2段の上端
PLAT_W = (0.372 * TS, 0.318 * TS)

ZB = [0.0] * NST      # 塔身の下端
ZE = [0.0] * NST      # 塔身の上端＝軒の高さ
ZB[0] = PLAT_H[1]
for k in range(NST):
    ZE[k] = ZB[k] + HB[k]
    if k + 1 < NST:
        # 屋根の半径が上層の半幅の 1.10 倍になる高さに、上層の下端を座らせる
        useat = (1.0 - 1.10 * WB[k + 1] / WR[k]) / (1.0 - FT[k])
        useat = max(0.05, min(0.97, useat))
        ZB[k + 1] = ZE[k] + HR[k] * (useat ** 1.6)

# 扉の上下
DZ0 = [0.0] * NST
DZ1 = [0.0] * NST
for k in range(NST):
    DZ0[k] = ZB[k] + (0.075 if k == 0 else 0.082)
    DZ1[k] = ZE[k] - 0.014

# 相輪
ROBAN_W = 0.088 * TS
ROBAN_H = 0.028
FUKU_H = 0.046
KURIN_N = 2
KURIN_GAP = 0.0640
KURIN_R = 0.086
KURIN_T = 0.0195
ROD_R = 0.0345
HOJU_R = 0.036

Z_TOP4 = ZE[NST - 1] + HR[NST - 1]
Z_ROBAN = Z_TOP4 + ROBAN_H
Z_FUKU = Z_ROBAN + FUKU_H
Z_K0 = Z_FUKU + 0.016
Z_KTOP = Z_K0 + (KURIN_N - 1) * KURIN_GAP
Z_HOJU = Z_KTOP + 0.115
TOTAL_H = Z_HOJU + HOJU_R
Z_HALF = TOTAL_H * 0.5

PZ0 = 0.010                       # 心柱の下端（基壇の中）
PZ1 = Z_ROBAN                     # 心柱の上端（露盤の中）
Z_HOT_ABS = 0.5 * (DZ0[2] + DZ1[2])       # 光の芯＝三重目の扉の中心
Z_HOT = Z_HOT_ABS - Z_HALF


def ZL(z):
    """塔の絶対 z → リグ・ローカル z（リグは原点＝#9／object.scale 不使用＝#15）"""
    return z - Z_HALF


def door_dx(k):
    """カメラが x=+0.55 から見るので、扉を少しずらさないと心柱の芯を通らない。"""
    return DOOR_DX_K * RAYK * (WB[k] - 0.5 * TW)


def es_at(dz):
    """材質ノードと同じ式（心柱の芯 u=0 での ES）。"""
    d = (abs(dz) / FZ) ** D_POW
    d = max(0.0, min(1.0, d))
    return ES_CORE * (1.0 - (3.0 * d * d - 2.0 * d ** 3))


def open_area(t):
    """機構が光を変えているかを幾何で当てる（#40⑥／#31 の純math スキャン）。"""
    s = math.sin(TAU * t)
    tot = 0.0
    for k in range(NST):
        th = THETA * W_MODE[k] * s
        a = WB[k] - 0.5 * TW
        c = a * math.sin(th)
        hw = DW * math.cos(th)
        lo = max(-RP, c - hw)
        hi = min(RP, c + hw)
        w = max(0.0, hi - lo)
        tot += w * (DZ1[k] - DZ0[k]) * es_at(0.5 * (DZ0[k] + DZ1[k]) - Z_HOT_ABS)
    return tot


def _pick_still():
    best, bf = -1e9, 1
    for f in range(1, N_FRAMES + 1):
        a = open_area((f - 1) / N_FRAMES)
        if a > best:
            best, bf = a, f
    return bf


STILL_FRAME = int(os.environ.get("STILL_FRAME", str(_pick_still())))


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_roof, b = make_principled("to_roof")           # 瓦屋根（大きな傾斜面＝反射率を落とす #17-c）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_ROOF
b.inputs["Specular IOR Level"].default_value = SPEC_ROOF
b.inputs["Coat Weight"].default_value = 0.0

mat_body, b = make_principled("to_body")           # 塔身（板壁・柱）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_BODY
b.inputs["Specular IOR Level"].default_value = SPEC_BODY
b.inputs["Coat Weight"].default_value = 0.0

mat_stone, b = make_principled("to_stone")         # 基壇（石）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.64
b.inputs["Specular IOR Level"].default_value = 0.18
b.inputs["Coat Weight"].default_value = 0.0

mat_metal, b = make_principled("to_sourin")        # 相輪（鋳物）＝小さいので少しだけ照らせる
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.36
b.inputs["Specular IOR Level"].default_value = 0.20
b.inputs["Coat Weight"].default_value = 0.0

mat_em, em_bsdf = make_principled("to_shinbashira")  # 心柱＝光
em_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)   # #32
em_bsdf.inputs["Emission Color"].default_value = LIME
em_bsdf.inputs["Roughness"].default_value = 0.5
em_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
def finish(name, bm, mats, smooth=True, weld=True, auto=True):
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
    for m in mats:
        o.data.materials.append(m)
    if auto:
        smooth_auto(o)
    return o


def smooth_auto(o, angle=0.55):
    """#6：5.x は shade_auto_smooth（active+selected で呼ぶ）。"""
    try:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_auto_smooth(angle=angle)
    except Exception as e:
        print(">> shade_auto_smooth skipped:", e)


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


def box(bm, x0, x1, y0, y1, z0, z1):
    """閉じた直方体（#15：頂点を実寸で置くだけ）。"""
    if x1 - x0 <= 1e-6 or z1 - z0 <= 1e-6:
        return
    p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    v = [bm.verts.new(q) for q in p]
    bm.faces.new((v[0], v[3], v[2], v[1]))
    bm.faces.new((v[4], v[5], v[6], v[7]))
    bm.faces.new((v[0], v[1], v[5], v[4]))
    bm.faces.new((v[1], v[2], v[6], v[5]))
    bm.faces.new((v[2], v[3], v[7], v[6]))
    bm.faces.new((v[3], v[0], v[4], v[7]))


def slab(bm, hw, z0, z1):
    box(bm, -hw, hw, -hw, hw, z0, z1)


def cyl(bm, z0, z1, r0, r1, n=40):
    rings = []
    for (z, r) in ((z0, r0), (z1, r1)):
        rings.append([(r * math.cos(TAU * i / n), r * math.sin(TAU * i / n), z)
                      for i in range(n)])
    loft(bm, rings, cap=True)


def torus(bm, zc, R, r, nu=40, nv=10):
    vs = [[None] * nv for _ in range(nu)]
    for i in range(nu):
        a = TAU * i / nu
        ca, sa = math.cos(a), math.sin(a)
        for j in range(nv):
            b2 = TAU * j / nv
            rr = R + r * math.cos(b2)
            vs[i][j] = bm.verts.new((rr * ca, rr * sa, zc + r * math.sin(b2)))
    for i in range(nu):
        i2 = (i + 1) % nu
        for j in range(nv):
            j2 = (j + 1) % nv
            bm.faces.new((vs[i][j], vs[i2][j], vs[i2][j2], vs[i][j2]))


def sphere(bm, zc, R, nu=32, nv=16, zsq=1.0):
    rings = []
    for j in range(nv + 1):
        th = math.pi * j / nv
        rr = max(R * math.sin(th), 1e-5)
        z = zc + R * zsq * math.cos(th)
        rings.append([(rr * math.cos(TAU * i / nu), rr * math.sin(TAU * i / nu), z)
                      for i in range(nu)])
    loft(bm, rings, cap=False)


# ---------- 塔の造形 ----------
def build_roof(k):
    """反りのある寄棟屋根。**中空にせず平らな軒天の solid**（屋根裏を作らない）。"""
    bm = bmesh.new()
    wr, ze, hr, ft = WR[k], ZE[k], HR[k], FT[k]
    cup = CUP * wr
    rings = []
    for i in range(NU, -1, -1):          # u=1（頂部の小さな正方形＝キャップ）→ u=0（軒）
        u = i / NU
        ring = []
        for j in range(NPSI):
            psi = TAU * j / NPSI
            c, s = math.cos(psi), math.sin(psi)
            m = max(abs(c), abs(s))
            re = wr / m
            cf = (1.0 / m - 1.0) / (SQ2 - 1.0)          # 0=軒の真ん中 / 1=隅
            r = re * (1.0 - (1.0 - ft) * u)
            z = ze + hr * (u ** 1.6) + cup * cf * max(0.0, 1.0 - u / 0.34) ** 2
            ring.append((r * c, r * s, ZL(z)))
        rings.append(ring)
    ring = []                                            # 軒天（平らな底＝閉じた solid）
    for j in range(NPSI):
        psi = TAU * j / NPSI
        c, s = math.cos(psi), math.sin(psi)
        re = wr / max(abs(c), abs(s))
        ring.append((re * c, re * s, ZL(ze - EAVE_T)))
    rings.append(ring)
    loft(bm, rings, cap=True)
    return finish("roof%d" % k, bm, [mat_roof], smooth=True, weld=False)


def build_body(k):
    """四方の板壁＋前面のただ一つの扉（＝光の唯一の出口）。"""
    bm = bmesh.new()
    w, z0, z1 = WB[k], ZB[k], ZE[k]
    dx = door_dx(k)
    d0, d1 = DZ0[k], DZ1[k]
    yf0, yf1 = -w, -w + TW
    box(bm, -w, w, w - TW, w, ZL(z0), ZL(z1))                 # 背面
    box(bm, -w, -w + TW, -w, w, ZL(z0), ZL(z1))               # 左
    box(bm, w - TW, w, -w, w, ZL(z0), ZL(z1))                 # 右
    box(bm, -w, dx - DW, yf0, yf1, ZL(z0), ZL(z1))            # 前・左方立
    box(bm, dx + DW, w, yf0, yf1, ZL(z0), ZL(z1))             # 前・右方立
    box(bm, dx - DW, dx + DW, yf0, yf1, ZL(d1), ZL(z1))       # 前・楣
    box(bm, dx - DW, dx + DW, yf0, yf1, ZL(z0), ZL(d0))       # 前・敷居
    if k >= 1:                                                # 縁（層の読みを作る水平線）
        slab(bm, w + 0.028 * TS, ZL(z0 + 0.042), ZL(z0 + 0.056))
    return finish("body%d" % k, bm, [mat_body], smooth=True, weld=False)


def build_platform():
    bm = bmesh.new()
    slab(bm, PLAT_W[0], ZL(0.0), ZL(PLAT_H[0]))
    slab(bm, PLAT_W[1], ZL(PLAT_H[0]), ZL(PLAT_H[1]))
    return finish("kidan", bm, [mat_stone], smooth=True, weld=False)


def build_sourin():
    """相輪＝「五重塔である」ことを1秒で宣言する署名（#40①）。心柱に載るので動かない。"""
    bm = bmesh.new()
    slab(bm, ROBAN_W, ZL(Z_TOP4), ZL(Z_ROBAN))                       # 露盤
    sphere(bm, ZL(Z_ROBAN), 0.072 * TS, zsq=FUKU_H / (0.072 * TS))   # 伏鉢（半球）
    cyl(bm, ZL(Z_ROBAN), ZL(Z_HOJU), ROD_R, ROD_R * 0.30, n=32)      # 擦管＝先細りの尖塔
    # 🔴 九輪は3周（薄い輪→厚い輪→太い円盤）試して3周とも hero で「ねじ／ばね」に
    #    読めた。#33＝型の失敗はパラメータで救えない。**細い棒に肋を等間隔で並べる型
    #    そのもの**がねじの記号なので、輪を2枚だけに落として型ごと捨てる（2枚では
    #    反復として読めない＝ねじにならない／#32-c の逆用）。
    for i in range(KURIN_N):
        z = Z_K0 + i * KURIN_GAP
        r = KURIN_R * (1.0 - 0.150 * i)
        cyl(bm, ZL(z - KURIN_T * 0.5), ZL(z + KURIN_T * 0.5), r, r * 0.90, n=44)
    sphere(bm, ZL(Z_HOJU), HOJU_R)                                   # 宝珠
    return finish("sourin", bm, [mat_metal], smooth=True, weld=False)


def build_shinbashira():
    """心柱＝光。UV に正規化2軸を焼く（#39／#34）。どの層にも繋がっていない＝動かない。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    nz, nps = 72, 48
    rings = []
    for i in range(nz + 1):
        z = PZ0 + (PZ1 - PZ0) * (i / nz)
        rings.append([(RP * math.cos(TAU * j / nps), RP * math.sin(TAU * j / nps), ZL(z))
                      for j in range(nps)])
    loft(bm, rings, cap=True)
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        for l in f.loops:
            x, _y, z = l.vert.co
            l[uvl].uv = (x / FX, (z - Z_HOT) / FZ)
    return finish("shinbashira", bm, [mat_em], smooth=True, weld=False, auto=False)


# ---------- 組み立て（#9：リグは原点／matrix_parent_inverse は identity） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "to_pose"

PARTS = []
STOREY = []
for k in range(NST):
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    e = bpy.context.active_object
    e.name = "storey%d" % k
    e.parent = rig
    e.location = (0.0, 0.0, 0.0)
    STOREY.append(e)
    for o in (build_body(k), build_roof(k)):
        o.parent = e
        o.location = (0.0, 0.0, 0.0)
        PARTS.append(o)

for o in (build_platform(), build_sourin(), build_shinbashira()):
    o.parent = rig
    o.location = (0.0, 0.0, 0.0)
    PARTS.append(o)


# ---------- 発光の勾配（UV に焼いた正規化2軸／d=1 の縁で厳密に 0） ----------
_ct = mat_em.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["UV"], _sep.inputs["Vector"])


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


_d = _m('SQRT', _m('ADD',
                   _m('MULTIPLY', _sep.outputs["X"], _sep.outputs["X"]),
                   _m('MULTIPLY', _sep.outputs["Y"], _sep.outputs["Y"])))
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 1.0
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = 0.0      # #32：暗部は完全な黒＝そのまま裏当て
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'
except Exception:
    pass
_ct.links.new(_m('POWER', _d, val=D_POW), _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], em_bsdf.inputs["Emission Strength"])


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    s = math.sin(TAU * (f - 1) / N_FRAMES)
    for k in range(NST):
        STOREY[k].rotation_euler = (0.0, 0.0, THETA * W_MODE[k] * s)
        STOREY[k].keyframe_insert(data_path="rotation_euler", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, -0.42, CENTER_Z + Z_HOT))
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


tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, CAP_Z[0]), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, CAP_Z[1]), "logo")
study = add_caption("MIDDLE STUDY 044 — SHINBASHIRA", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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


# ---------- 検算ヘルパ ----------
def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = (18.0 / 85.0) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


def screen_x(x, y=0.0):
    dist = y - CAM_LOC[1]
    half = (36.0 / 2.0 / 85.0) * dist * (1600.0 / 2000.0)
    cx = CAM_LOC[0] + (0.1 - CAM_LOC[0]) * (dist / (0.0 - CAM_LOC[1]))
    return (x - cx) / half


# ---------- 出力モード ----------
modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "probe" in modes:
    print(">> 全高 %.3f m  基壇半幅 %.3f  最下軒半幅 %.3f" % (TOTAL_H, PLAT_W[0], WR[0]))
    print(">> STILL_FRAME=%d" % STILL_FRAME)
    for k in range(NST):
        print("   層%d  塔身 z %.3f..%.3f (h%.3f)  軒 %.3f  扉 z %.3f..%.3f (h%.3f) dx%+.4f  ES%.2f"
              % (k, ZB[k], ZE[k], HB[k], WR[k], DZ0[k], DZ1[k], DZ1[k] - DZ0[k],
                 door_dx(k), es_at(0.5 * (DZ0[k] + DZ1[k]) - Z_HOT_ABS)))
    a0 = open_area(0.0)
    print(">> 光の量（#40⑥ 75%%を切れば合格）:")
    for tt in (0.0, 0.0625, 0.125, 0.1875, 0.25):
        print("   t=%.4f  %.1f%%" % (tt, 100.0 * open_area(tt) / a0))
    zt = CENTER_Z + ZL(TOTAL_H)
    zbm = CENTER_Z + ZL(0.0)
    print(">> 画面（#18 縦 -1..+1）: 塔 底 %+.3f  頂 %+.3f  占有 %.0f%%"
          % (screen_y(zbm), screen_y(zt), 50.0 * (screen_y(zt) - screen_y(zbm))))
    print(">> 光の芯 %+.3f（0 が画面中央）" % screen_y(CENTER_Z + Z_HOT))
    for i, z in enumerate(CAP_Z):
        print("   キャプション%d %+.3f" % (i + 1, screen_y(z, -1.3)))
    wmax = 0.0
    for k in range(NST):
        th = abs(THETA * W_MODE[k])
        wmax = max(wmax, WR[k] * (math.cos(th) + math.sin(th)))
    print(">> 横の実効半幅 %.3f → 画面 %+.3f（#18 |x|<1）" % (wmax, screen_x(wmax)))

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "shinbashira.blend"))
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
        for lk in list(em_bsdf.inputs["Emission Strength"].links):
            mat_em.node_tree.links.remove(lk)
        em_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {rig.name} | {e.name for e in STOREY} | {o.name for o in PARTS}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "shinbashira.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
