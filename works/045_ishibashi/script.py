# =============================================================
# monaka design. — MIDDLE STUDY 045 "ISHIBASHI"（石橋 / a stone arch bridge）
# 黒い石の眼鏡橋が宙に架かる。二つのアーチは、それぞれの岸から迫り上がって、
# 真ん中の一本——橋脚——で出会う。
# その出会う一線だけが開いて、奥から ライム #A5E02E が差す。
# 橋がゆっくり息をすると、二つの半身は離れ、また寄る。
# **橋は、真ん中で出会うためにある。**
#
# 【ドメイン】土木・橋（シリーズ未踏）。直近10作（建築・寺社／虫・生命／工芸・繕い／
#   植物・竹／計量・秤／貝・海／折紙／玩具・独楽／武具・鞘／装身・櫛）と別領域。
#   044 SHINBASHIRA は「垂直の積層」、045 は「水平の迫り」＝主題もシルエットも別。
#
# 【型（#33）— 3周かけて単アーチを捨てた】
#   1〜3周目は**単アーチ**で組んだが、hero でも 480px でも「門／トンネルの坑口／
#   黒い蹄鉄」にしか読めなかった。起拱点を下げる・胴を厚くする・迫元に勾配を付ける・
#   笠石を通す——どれも一手ずつは効いたが、**逆U字の輪郭**という型そのものは残った。
#   → **二連アーチ（眼鏡橋）に替えた瞬間に「橋」に読めた。**
#   アーチが2つ並ぶ輪郭は水路橋／石橋以外に既製品の記号を持たないので、
#   文脈（水・岸）が無い白い床の上でも1秒で読める。#32-c/#41 の
#   「反復の数が読みを決める」の応用＝**1では門、2で橋**。
#
# 【機構】シリーズ初の「**並進の開離（two rigid halves parting along the span）**」。
#   ・二つの半身（アーチ1つ＋橋脚の半分）が、径間の方向に ±d(t) だけ離れる。
#   ・回転で開くと橋面の水平線が「へ」の字に折れて**橋の読みが壊れる**ので、
#     ここでは並進を採る（＝天端の線が一直線のまま、真ん中の一線だけが開く）。
#   ・開口の幅は高さに依らず一定 → 橋脚の全高に**均一な光の一線**が立つ。
#   ・d(t)=D_MID−D_AMP·cos2πt の整数周期＝完全ループ。位置キーのみ＝glb に乗る。
#   ・純math スキャンで露出発光面積が 11%→100%（#40⑥ 合格）。
#
# 【光】橋脚の合わせ目＝Base 純黒＋Spec 0（#32：随伴光で暗部が緑のベタになるのを回避）。
#   勾配は #34 の2軸楕円距離を UV に焼き込む（#39）：u=x/FX（＝合わせ石の半幅。
#   縁で ES が厳密に 0＝そのまま裏当て）、v=(z−Z_HOT)/FZ（v=±1 で 0）。
#   FZ は全高の 30% しかないので、光は**二つのアーチのあいだ＝橋脚の面**にしか居ない
#   （#43②/#31-d：橋面より上・水面より下は ES=0 の黒い詰め物＝白抜け止めを兼ねる）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_ishibashi.py -- <mode...>
#   modes: probe | bbox | test | testhero | still | anim | blend | glb  （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

TAU = math.pi * 2.0

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_ishibashi")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "1.56"))   # 橋の上下中心（world）
LOOK_Z = float(os.environ.get("LOOK_Z", "1.62"))
CAM_LOC = (0.55, -8.3, 1.95)
BRIDGE_X = float(os.environ.get("BRIDGE_X", "0.10"))   # 画面の横中心（screen_x の cx）
YAW = math.radians(float(os.environ.get("YAW", "14.0")))

BS = float(os.environ.get("BS", "0.96"))               # 橋ぜんたいの寸法係数

R_I = 0.270 * BS         # アーチ内半径（内輪）
T_R = 0.090 * BS         # 輪石（アーチ環）の厚み
R_O = R_I + T_R          # 外輪
PHW = 0.150 * BS         # 中央の橋脚の半幅（＝合わせ目から脚の面まで）
XC = PHW + R_I           # アーチの中心（±XC）
AB = 0.185 * BS          # 橋台（アーチの外側の石積み）
HWB = XC + R_I + AB      # 橋の半幅
Z_S = 0.240 * BS         # 起拱点の高さ（＝橋脚が水から立ち上がる高さ）
Z_D0 = 0.860 * BS        # 橋面（デッキ）の中央高さ
CAMBER = 0.060 * BS      # 反り（端で下がる量）
BATTER = 0.055 * BS      # 橋台の勾配（下が広い＝石積みの護岸の記号）
PAR_H = 0.090 * BS       # 高欄の高さ
PAR_IN = 0.048 * BS      # 高欄の見込み方向の引っ込み
PAR_X = 0.830 * BS       # 高欄の端（デッキ端より内側＝小さな踏み場が出る）
COPE_H = 0.022 * BS      # 笠石の高さ
COPE_OUT = 0.015 * BS    # 笠石の出（＝天端に水平線を1本通す）
DEP = 0.420 * BS         # 橋の見込み（奥行き）
YH = DEP * 0.5
PROUD = 0.011 * BS       # 輪石が面から出る量（＝放射状の目地を彫らずに作る）
NV = 9                   # 1アーチ（180°）あたりの輪石の数
JGAP = 0.0034 * BS       # 輪石どうしの目地（内輪での弧長）

# --- 合わせ石（＝光）と機構 ---
HW_EM = float(os.environ.get("HW_EM", "0.046")) * BS   # 合わせ石の半幅
FX = float(os.environ.get("FX", "0.046")) * BS         # 短軸（横）の減衰幅＝縁で ES=0（#34）
Z_HOT = float(os.environ.get("Z_HOT", "0.440")) * BS   # 光の芯＝橋脚の面の中ほど
FZ = float(os.environ.get("FZ", "0.460")) * BS         # 長軸（縦）＝橋脚の足元〜天端に届く一本の線
ES_CORE = float(os.environ.get("ES_CORE", "4.4"))
D_POW = float(os.environ.get("D_POW", "2.00"))         # #38④：暗い裾の広さ＝中間調
KEY_BACK = 0.003 * BS                                  # 合わせ石の面の引っ込み（同一平面を作らない）

D_MID = float(os.environ.get("D_MID", "0.021")) * BS   # 開離（m）
D_AMP = float(os.environ.get("D_AMP", "0.017")) * BS

# --- 材質（#17-c/#39-c：一様bright env では反射率が支配項） ---
SPEC_STONE = float(os.environ.get("SPEC_STONE", "0.16"))
ROUGH_STONE = float(os.environ.get("ROUGH_STONE", "0.55"))
SPEC_RING = float(os.environ.get("SPEC_RING", "0.16"))
ROUGH_RING = float(os.environ.get("ROUGH_RING", "0.56"))

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


# ---------- 橋の骨格（すべて「橋ローカル座標」＝底が z=0・合わせ目が x=0） ----------
def deck(x):
    """反りのある橋面。中央がいちばん高い。"""
    return Z_D0 - CAMBER * (x / HWB) ** 2


def extrados_u(u):
    return Z_S + math.sqrt(max(0.0, R_O * R_O - u * u))


KEY_TOP = deck(0.0) + PAR_H
H_TOTAL = KEY_TOP
Z_HALF = H_TOTAL * 0.5
Z_EXTRA = Z_S + R_O          # 外輪の頂
Z_INTRA = Z_S + R_I          # 内輪の頂


def ZL(z):
    """橋の絶対 z → リグ・ローカル z（リグは原点＝#9／object.scale 不使用＝#15）"""
    return z - Z_HALF


def es_uv(x, z):
    """材質ノードと同じ式（#34/#39 の2軸楕円距離）。"""
    d = math.sqrt((x / FX) ** 2 + ((z - Z_HOT) / FZ) ** 2) ** D_POW
    d = max(0.0, min(1.0, d))
    return ES_CORE * (1.0 - (3.0 * d * d - 2.0 * d ** 3))


def lit_area(dd):
    """露出している発光面の ES 重み付き面積（#40⑥／#31 の純math スキャン）。"""
    NZ, NX = 120, 24
    dz = KEY_TOP / NZ
    g = min(dd, HW_EM)
    dx = 2.0 * g / NX
    tot = 0.0
    for i in range(NZ):
        z = dz * (i + 0.5)
        for j in range(NX):
            x = -g + dx * (j + 0.5)
            tot += es_uv(x, z) * dx * dz
    return tot


def dpart(t):
    return D_MID - D_AMP * math.cos(TAU * t)


def _pick_still():
    best, bf = -1e9, 1
    for f in range(1, N_FRAMES + 1):
        a = lit_area(dpart((f - 1) / N_FRAMES))
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


mat_stone, b = make_principled("ib_stone")      # 橋台・橋脚・高欄（大きな平面＝反射率が支配項 #17-c）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_STONE
b.inputs["Specular IOR Level"].default_value = SPEC_STONE
b.inputs["Coat Weight"].default_value = 0.0

mat_ring, b = make_principled("ib_ring")        # 輪石（小さな塊＝縁を少しだけ立てる）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_RING
b.inputs["Specular IOR Level"].default_value = SPEC_RING
b.inputs["Coat Weight"].default_value = 0.0

mat_em, em_bsdf = make_principled("ib_awase")   # 合わせ石＝光
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


def band(bm, lo, hi, y0, y1):
    """lo / hi は同数の (x,z) 列。front/back/上下/両端を張って閉じた solid にする。
    n-gon を作らないので凹んだ輪郭でも三角化が崩れない（#10）。"""
    n = len(lo)
    F, B = [], []
    for i in range(n):
        F.append((bm.verts.new((lo[i][0], y0, ZL(lo[i][1]))),
                  bm.verts.new((hi[i][0], y0, ZL(hi[i][1])))))
        B.append((bm.verts.new((lo[i][0], y1, ZL(lo[i][1]))),
                  bm.verts.new((hi[i][0], y1, ZL(hi[i][1])))))
    for i in range(n - 1):
        bm.faces.new((F[i][0], F[i + 1][0], F[i + 1][1], F[i][1]))
        bm.faces.new((B[i][0], B[i + 1][0], B[i + 1][1], B[i][1]))
        bm.faces.new((F[i][0], F[i + 1][0], B[i + 1][0], B[i][0]))
        bm.faces.new((F[i][1], F[i + 1][1], B[i + 1][1], B[i][1]))
    bm.faces.new((F[0][0], F[0][1], B[0][1], B[0][0]))
    bm.faces.new((F[-1][0], F[-1][1], B[-1][1], B[-1][0]))


def span(bm, xs, flo, fhi, y0, y1):
    band(bm, [(x, flo(x)) for x in xs], [(x, fhi(x)) for x in xs], y0, y1)


def lin(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


# ---------- 橋の造形（sg=-1 が左半／+1 が右半・合わせ目は x=0） ----------
def build_mass(sg):
    """橋台（勾配つき）＋アーチの上のスパンドレル＋中央の橋脚の半分。"""
    bm = bmesh.new()
    cx = sg * XC
    xo = sg * (XC + R_O)          # アーチの外の縁
    # ① 橋台＝**下が広い勾配（batter）**。span() は勾配が書けないので band() で上下を別に張る
    lo, hi = [], []
    for i in range(13):
        u = i / 12.0
        xl = HWB + ((XC + R_O - 0.02 * BS) - HWB) * u
        xh = (HWB - BATTER) + ((XC + R_O - 0.02 * BS) - (HWB - BATTER)) * u
        lo.append((sg * xl, 0.0))
        hi.append((sg * xh, deck(sg * xh)))
    band(bm, lo, hi, -YH, YH)
    # ② スパンドレル（外輪の上〜橋面）＋中央の橋脚の半分を**ひと続きの span** で作る。
    #    🔴 別々の solid にして x=±PHW で front 面を重ねると、同一平面の z-fighting が
    #    橋脚の面に縦の線として出る（6周目に hero で発覚）。段差は 1.5mm の縦面で表す。
    eps = 0.0015 * BS
    xs = sorted([sg * v for v in lin(XC + R_O, PHW + eps, 24)]
                + [sg * PHW, sg * PHW * 0.5, 0.0])

    def _flo(x):
        if abs(x) <= PHW + 1e-9:
            return 0.0
        return min(extrados_u(abs(x) - XC) - 0.006 * BS, deck(x) - 0.010 * BS)

    span(bm, xs, _flo, deck, -YH, YH)
    # ④ アーチの外側の迫元（内輪〜外輪のあいだ・起拱点より下）
    xs = sorted([sg * v for v in lin(XC + R_O + 0.02 * BS, XC + R_I, 4)])
    span(bm, xs, lambda x: 0.0, lambda x: Z_S + 0.006 * BS, -YH, YH)
    return finish("mass%+d" % sg, bm, [mat_stone], smooth=True, weld=False)


def build_ring(sg):
    """輪石（voussoir）。面から PROUD 出して**放射状の目地**を作る（彫らずに読ませる／#31-b）。"""
    bm = bmesh.new()
    cx = sg * XC
    dpsi = math.pi / NV
    gap = JGAP / R_I * 0.5
    for k in range(NV):
        p0 = -math.pi * 0.5 + k * dpsi + gap
        p1 = -math.pi * 0.5 + (k + 1) * dpsi - gap
        lo, hi = [], []
        for i in range(7):
            ps = p0 + (p1 - p0) * i / 6.0
            s, c = math.sin(ps), math.cos(ps)
            lo.append((cx + R_I * s, Z_S + R_I * c))
            hi.append((cx + (R_O + 0.006 * BS) * s, Z_S + (R_O + 0.006 * BS) * c))
        band(bm, lo, hi, -YH - PROUD, YH + PROUD)
    return finish("ring%+d" % sg, bm, [mat_ring], smooth=True, weld=False)


def build_parapet(sg):
    """高欄＝見込みを引っ込めた無地の石壁（細い束柱を並べない＝#33①/#41）。"""
    bm = bmesh.new()
    xs = sorted([sg * v for v in lin(PAR_X, 0.0, 20)])
    span(bm, xs, lambda x: deck(x) - 0.004 * BS,
         lambda x: deck(x) + PAR_H - COPE_H, -(YH - PAR_IN), (YH - PAR_IN))
    # 笠石＝少しだけ出して天端に水平線を1本通す
    span(bm, xs, lambda x: deck(x) + PAR_H - COPE_H - 0.002 * BS,
         lambda x: deck(x) + PAR_H,
         -(YH - PAR_IN + COPE_OUT), (YH - PAR_IN + COPE_OUT))
    return finish("parapet%+d" % sg, bm, [mat_stone], smooth=True, weld=False)


def build_awaseishi():
    """合わせ石＝光。動かない。UV に正規化2軸を焼く（#39／#34）。
    橋面より上・水面より下は ES=0 の黒い詰め物＝そのまま裏当て（#32）。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    xs = lin(-HW_EM, HW_EM, 20)
    band(bm, [(x, 0.0) for x in xs], [(x, deck(x)) for x in xs],
         -(YH - KEY_BACK), (YH - KEY_BACK))
    band(bm, [(x, deck(x) - 0.002 * BS) for x in xs],
         [(x, deck(x) + PAR_H) for x in xs],
         -(YH - PAR_IN - KEY_BACK), (YH - PAR_IN - KEY_BACK))
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        for l in f.loops:
            x, _y, z = l.vert.co
            l[uvl].uv = (x / FX, ((z + Z_HALF) - Z_HOT) / FZ)
    return finish("awaseishi", bm, [mat_em], smooth=True, weld=False, auto=False)


# ---------- 組み立て（#9：リグは原点／matrix_parent_inverse は identity） ----------
bpy.ops.object.empty_add(location=(BRIDGE_X, 0.0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "ib_pose"
rig.rotation_euler = (0.0, 0.0, YAW)

PARTS = []
HALVES = []
for sg in (-1, +1):
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    e = bpy.context.active_object
    e.name = "half%+d" % sg
    e.parent = rig
    e.location = (0.0, 0.0, 0.0)
    HALVES.append((sg, e))
    for o in (build_mass(sg), build_ring(sg), build_parapet(sg)):
        o.parent = e
        o.location = (0.0, 0.0, 0.0)
        PARTS.append(o)

awase = build_awaseishi()
awase.parent = rig
awase.location = (0.0, 0.0, 0.0)
PARTS.append(awase)


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
    dd = dpart((f - 1) / N_FRAMES)
    for sg, e in HALVES:
        e.location = (sg * dd, 0.0, 0.0)      # 径間の方向に離れる＝真ん中の一線が開く
        e.keyframe_insert(data_path="location", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(BRIDGE_X, -0.30, CENTER_Z + ZL(Z_HOT)))
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
study = add_caption("MIDDLE STUDY 045 — ISHIBASHI", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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
    print(">> 全高 %.3f  全幅 %.3f  見込み %.3f  内輪 %.3f  外輪 %.3f  起拱 %.3f"
          % (H_TOTAL, 2 * HWB, DEP, R_I, R_O, Z_S))
    print(">> 内輪の頂 %.3f  外輪の頂 %.3f  橋面 %.3f  天端 %.3f  光の芯 %.3f"
          % (Z_INTRA, Z_EXTRA, deck(0.0), KEY_TOP, Z_HOT))
    print(">> STILL_FRAME=%d  開離 d %.4f..%.4f m  橋脚半幅 %.3f"
          % (STILL_FRAME, D_MID - D_AMP, D_MID + D_AMP, PHW))
    gmax = D_MID + D_AMP
    print(">> 【漏れ】最大の開口半幅 %.4f  vs 合わせ石半幅 %.4f  → %s"
          % (gmax, HW_EM, "OK（白抜けなし）" if gmax < HW_EM else "🔴 NG：合わせ石を広げる"))
    print(">> 【橋脚】合わせ石半幅 %.4f  vs 橋脚半幅+開離 %.4f  → %s"
          % (HW_EM, PHW + gmax,
             "OK（アーチの空へ食み出さない）" if HW_EM < PHW + gmax else "🔴 NG"))
    # 🔴 輪石は起拱点で x=cx+R_O まで橋脚に食い込む。ここが合わせ目に届くと
    #    面から出ている輪石が光を前から遮り、**線がくびれて砂時計になる**（5周目で発覚）。
    print(">> 【輪石の到達】XC-R_O %.4f  vs 合わせ石半幅+開離 %.4f  → %s"
          % (XC - R_O, HW_EM + gmax,
             "OK（一本の線が通る）" if XC - R_O > HW_EM else "🔴 NG：橋脚を太らせる"))
    a0 = lit_area(gmax)
    print(">> 光の量（#40⑥ 75%%を切れば合格）:")
    for tt in (0.5, 0.375, 0.25, 0.125, 0.0):
        print("   t=%.3f  d=%.4f  %.1f%%"
              % (tt, dpart(tt), 100.0 * lit_area(dpart(tt)) / a0))
    zb = CENTER_Z + ZL(0.0)
    zt = CENTER_Z + ZL(KEY_TOP)
    print(">> 画面（#18 縦 -1..+1）: 橋 底 %+.3f  天 %+.3f  占有 %.0f%%"
          % (screen_y(zb), screen_y(zt), 50.0 * (screen_y(zt) - screen_y(zb))))
    print(">> 光の芯 %+.3f（0 が画面中央）" % screen_y(CENTER_Z + ZL(Z_HOT)))
    for i, z in enumerate(CAP_Z):
        print("   キャプション%d %+.3f" % (i + 1, screen_y(z, -1.3)))
    # 横：yaw と開離を込みで実効半幅を出す
    wx = HWB + gmax
    hw_eff = wx * math.cos(YAW) + (YH + PROUD) * math.sin(YAW)
    print(">> 横の実効半幅 %.3f（yaw %.1f°込み）→ 画面 %+.3f / %+.3f  占有 %.0f%%"
          % (hw_eff, math.degrees(YAW),
             screen_x(BRIDGE_X + hw_eff), screen_x(BRIDGE_X - hw_eff),
             50.0 * (screen_x(BRIDGE_X + hw_eff) - screen_x(BRIDGE_X - hw_eff))))

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "ishibashi.blend"))
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
    keep = {rig.name} | {e.name for _s, e in HALVES} | {o.name for o in PARTS}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "ishibashi.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
