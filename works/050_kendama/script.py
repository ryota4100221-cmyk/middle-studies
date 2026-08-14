# =============================================================
# monaka design. — MIDDLE STUDY 050 "KENDAMA"（けん玉 / a kendama）
#
# 黒いけん玉が宙にある。光っているのは剣先だけ——けんと玉が出会う、ただ一点。
# 玉がゆっくり降りてきて、その光を呑む。深く沈むほど光は細り、離れればまた満ちる。
# **狙っているのは、真ん中の一点だけ。**
#
# 【ドメイン】玩具・けん玉。直近10作（武・弓／農・製粉／商い・暖簾／書物・巻子／土木・橋／
#   建築・寺社／虫・生命／工芸・繕い／植物・竹／計量・秤）と別。037 KOMA【玩具・独楽】は13作前で、
#   あちらは「回す」＝歳差、こちらは「受ける」＝軸に沿った差し込み＝機構が別。
#
# 【機構＝差し込みによる遮蔽（plunging occlusion）】シリーズ初。
#   40 TENBIN の「回る開口が発光体を切る」シャッターに対し、050 は**発光体そのものが黒い塊に呑まれる**。
#   玉の中心 z(t) = Z0 − TRAVEL·0.5(1−cos2πt) の整数周期＝完全ループ。
#   位置キーだけなので glb にそのまま乗る（#25c の材質アニメ問題を回避）。
#   🔴 最上位相でも玉の底は剣先の 0.02 上にしかない（#44）。離して落とす設計だと
#      ループの前半がずっと 100%＝「機構が光を変えている」時間が無くなる。
#
# 【光】剣先＝カメラに正対する細長い発光体なので #34 の2軸楕円グラデ（長軸=z・短軸=x）。
#   短軸の減衰 FX は剣先の半径より少し広い程度に取り、縁で ES が 0 に落ちる＝黒い台木へ溶ける。
#   ES=0 の裾は**黒いけんの上にしか無い**（#49①：背景の前に置いた ES=0 は裏当てでなく黒い板）。
#
# 🔴 #40⑥ は幾何で積分する（#46）。Blender を起動せず --probe-only で解ける。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- けん（一本の轆轤挽き） -----------------------------------
# 🔴 寸法比は実物（玉6cm／けん16cm／皿胴6.5cm／皿深1.6cm）から起こす。
#    2周目は握りが太く・けんが短く・皿が浅かったため hero で「ダンベル＋蝋燭」に転んだ（#16/#33）。
Z_BOT     = 0.770      # 中皿の縁＝最下端
Z_DISH    = 0.890      # 中皿の底（皿は下を向く）
R_CUP     = 0.175      # 中皿の外径
Z_CUPTOP  = 0.925      # 中皿の胴の上端
R_GRIP    = 0.082      # 握りの太さ
Z_TOP     = 1.900      # けんの天面（ここから剣先が出る）
R_TOP     = 0.054      # 🔴 剣先の根元の径（0.050）とほぼ同じにする。天面が広いと**燭台のソケット**に見え、
#                        発光する剣先が「蝋燭の炎」に読める（3周目の hero で発覚・#16）

# --- 皿胴（crosspiece）：#48 回転対称を破る署名。大皿と小皿の非対称がけん玉を宣言する ---
Z_CROSS   = 1.660
R_BARREL  = 0.082
X_OZARA, R_OZARA, D_OZARA = -0.345, 0.205, 0.150     # 大皿（左）
X_KOZARA, R_KOZARA, D_KOZARA = 0.335, 0.185, 0.135   # 小皿（右）
YAW       = math.radians(22.0)   # 皿胴だけを振る＝大皿の口がわずかに開いて「皿」に読める

# --- 剣先（＝発光体） ----------------------------------------
SP_BASE   = 1.870
SP_TIP    = 2.170
R_SP      = 0.055   # 🔴 2026-08-14：0.105まで太らせたら #50 の「蝋燭」に転んだ。元に戻す
SP_POW    = 0.85       # 先細りのべき（1.0 で直円錐・小さいほど張った稜線）
Z_HOT     = 2.100      # ホットコアの高さ（#34 長軸）
FZ        = 0.300      # 縦の減衰（ES=0 が根元 1.87 にちょうど来る）
FX        = 0.115      # 🔴 #51：ライム面積0.35%・halo2,805＝細すぎた。横の減衰を広げる      # 横の減衰（#34：発光体の半幅と同じか少し狭く）
GPOW      = 1.55       # 勾配のべき（#38④ 暗い裾を締める）
ES_CORE   = 3.6
LAMP_W    = 4.5        # 随伴点光源（#22 spill）。強いと玉の腹が抹茶色に被る

# --- 玉 -------------------------------------------------------
BALL_R    = 0.315
BORE_R    = 0.068      # 穴（剣先が入る）
BORE_D    = 0.200
GAP0      = 0.005      # 最上位相の隙間（剣先の頭と玉の底）。大きくすると #44 の「前半ずっと100%」になる
TRAVEL    = 0.260      # 差し込みの深さ

# --- 糸 -------------------------------------------------------
STR_L     = 0.685      # 弦長一定。たわみは懸垂線で解く（玉が降りるほど弛む）
STR_R     = 0.0095
TH_ATT    = math.radians(62.0)   # 玉の取り付け（底から測った極角）
PH_ATT    = math.radians(22.0)   # 奥（+y）へ振る＝糸のたるみは皿胴の裏に隠れる
KEN_ATT   = (0.105, 0.055, Z_CROSS + 0.060)   # 皿胴の胴・奥上

FPS       = 24
N_FRAMES  = 120
CAM_LOC   = (0.55, -8.3, 1.95)
CENTER_Z  = 1.88
LOOK_Z    = 1.90
AIM_X     = 0.0

# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）。
# 懸垂線・#40⑥ の遮蔽積分・hero 位相の選択は、シーンを組まずにここで解ける。
# =============================================================
def dish_arc(a_deep, a_rim, r_rim, n=16):
    """球面の皿。a_deep（底・r=0）から a_rim（縁・r=r_rim）へ。戻り [(r,a)]。"""
    d = a_rim - a_deep
    u = (r_rim * r_rim + d * d) / (2 * d)
    ac = a_deep + u
    R = abs(u)
    sgn = 1.0 if (a_deep - ac) > 0 else -1.0
    a_end = math.acos(max(-1.0, min(1.0, (a_rim - ac) * sgn / R)))
    return [(R * math.sin(a_end * k / (n - 1)),
             ac + sgn * R * math.cos(a_end * k / (n - 1))) for k in range(n)]


# --- けん本体の断面：中皿の椀 → 胴 → 握り → 首 → 天面 -----------
KEN_PROF = dish_arc(Z_DISH, Z_BOT + 0.008, R_CUP - 0.012, 16)
KEN_PROF += [(R_CUP - 0.004, Z_BOT + 0.003), (R_CUP, Z_BOT + 0.012),
             (R_CUP - 0.001, Z_BOT + 0.040), (R_CUP - 0.005, Z_BOT + 0.090),
             (R_CUP - 0.014, Z_CUPTOP - 0.028), (R_CUP - 0.032, Z_CUPTOP),
             (0.132, Z_CUPTOP + 0.026), (0.104, Z_CUPTOP + 0.048), (0.092, Z_CUPTOP + 0.068),
             (R_GRIP + 0.004, 1.030), (R_GRIP + 0.002, 1.130), (R_GRIP + 0.001, 1.260),
             (R_GRIP, 1.380), (0.081, 1.480), (0.080, 1.580), (0.079, 1.680),
             (0.076, 1.760), (0.070, 1.830), (0.062, 1.875), (R_TOP, Z_TOP), (0.0, Z_TOP)]

# --- 皿胴の断面（軸＝x）。🔴 皿は「短い筒＋中の椀」。縁から胴へなだらかに絞ると
#     皿でなく**ラッパ／糸巻き**に読める（1周目）。深さは口径の 0.35 前後（2周目は 0.22 で平皿）
CROSS_PROF = dish_arc(X_OZARA + D_OZARA, X_OZARA, R_OZARA, 16)
CROSS_PROF += [(R_OZARA - 0.003, X_OZARA + 0.012), (R_OZARA - 0.006, X_OZARA + 0.045),
               (R_OZARA - 0.009, X_OZARA + 0.080), (R_OZARA - 0.025, X_OZARA + 0.105),
               (0.140, X_OZARA + 0.123), (0.100, X_OZARA + 0.138),
               (R_BARREL, X_OZARA + 0.155), (R_BARREL, X_KOZARA - 0.155),
               (0.100, X_KOZARA - 0.138), (0.140, X_KOZARA - 0.123),
               (R_KOZARA - 0.023, X_KOZARA - 0.105), (R_KOZARA - 0.009, X_KOZARA - 0.080),
               (R_KOZARA - 0.006, X_KOZARA - 0.045), (R_KOZARA - 0.003, X_KOZARA - 0.011)]
CROSS_PROF += list(reversed(dish_arc(X_KOZARA - D_KOZARA, X_KOZARA, R_KOZARA, 16)))

# --- 全体倍率：比率は上で決め、ここでは**画面占有だけ**を決める（縦 55〜65%） ---
S = 1.12
_z = lambda v: Z_BOT + (v - Z_BOT) * S
Z_DISH, Z_CUPTOP, Z_TOP, Z_CROSS, SP_BASE, SP_TIP, Z_HOT = (
    _z(Z_DISH), _z(Z_CUPTOP), _z(Z_TOP), _z(Z_CROSS), _z(SP_BASE), _z(SP_TIP), _z(Z_HOT))
(R_CUP, R_GRIP, R_TOP, R_BARREL, R_OZARA, R_KOZARA, R_SP, FZ, FX,
 X_OZARA, X_KOZARA, D_OZARA, D_KOZARA,
 BALL_R, BORE_R, BORE_D, GAP0, TRAVEL, STR_L, STR_R) = [v * S for v in (
    R_CUP, R_GRIP, R_TOP, R_BARREL, R_OZARA, R_KOZARA, R_SP, FZ, FX,
    X_OZARA, X_KOZARA, D_OZARA, D_KOZARA,
    BALL_R, BORE_R, BORE_D, GAP0, TRAVEL, STR_L, STR_R)]
KEN_ATT = (KEN_ATT[0] * S, KEN_ATT[1] * S, _z(KEN_ATT[2]))
KEN_PROF = [(r * S, _z(a)) for (r, a) in KEN_PROF]
CROSS_PROF = [(r * S, a * S) for (r, a) in CROSS_PROF]

BALL_Z0 = SP_TIP + GAP0 + BALL_R          # 最上位相の玉の中心


def ball_z(i):
    t = (i % N_FRAMES) / N_FRAMES
    return BALL_Z0 - TRAVEL * 0.5 * (1.0 - math.cos(2 * math.pi * t))


def insertion(i):
    """剣先が玉に呑まれた深さ（負なら離れている）。"""
    return SP_TIP - (ball_z(i) - BALL_R)


def sp_r(z):
    """剣先の半径。先端はごく僅かに丸める（尖りの白点＝#11 の輝点を作らない）。"""
    if z >= SP_TIP:
        return 0.0
    u = (SP_TIP - z) / (SP_TIP - SP_BASE)
    r = R_SP * (u ** SP_POW)
    tipr = 0.011
    if SP_TIP - z < tipr:                       # 先端 11mm を球で丸める
        d = tipr - (SP_TIP - z)
        r = min(r, math.sqrt(max(0.0, tipr * tipr - d * d)))
    return r


def es_at(x, z):
    """シェーダと同一の式（#34 の2軸楕円 → POWER → MapRange SMOOTHSTEP）。"""
    d = math.hypot(x / FX, (z - Z_HOT) / FZ) ** GPOW
    t = min(1.0, max(0.0, d))
    return ES_CORE * (1.0 - t * t * (3.0 - 2.0 * t))


def _seg_hits_sphere(p, c, R):
    """p → カメラ の線分が球（中心c・半径R）を横切るか。"""
    dx, dy, dz = CAM_LOC[0] - p[0], CAM_LOC[1] - p[1], CAM_LOC[2] - p[2]
    fx, fy, fz = p[0] - c[0], p[1] - c[1], p[2] - c[2]
    a = dx * dx + dy * dy + dz * dz
    b = 2.0 * (fx * dx + fy * dy + fz * dz)
    cc = fx * fx + fy * fy + fz * fz - R * R
    disc = b * b - 4 * a * cc
    if disc < 0:
        return False
    sq = math.sqrt(disc)
    for s in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)):
        if 1e-6 < s < 1.0:
            return True
    return False


def visible_glow(i, nz=140, nph=72):
    """#40⑥：見える発光面積＝Σ ES · 投影面積（玉に遮られない前面のみ）。"""
    zc = ball_z(i)
    tot = 0.0
    dz = (SP_TIP - SP_BASE) / nz
    for a in range(nz):
        z = SP_BASE + (a + 0.5) * dz
        r = sp_r(z)
        if r <= 1e-5:
            continue
        rp = (sp_r(min(SP_TIP, z + 0.5 * dz)) - sp_r(z - 0.5 * dz)) / dz
        sl = math.sqrt(1.0 + rp * rp)
        for b in range(nph):
            ph = 2 * math.pi * (b + 0.5) / nph
            p = (r * math.cos(ph), r * math.sin(ph), z)
            n = (math.cos(ph), math.sin(ph), -rp)
            nn = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
            v = (CAM_LOC[0] - p[0], CAM_LOC[1] - p[1], CAM_LOC[2] - p[2])
            vn = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
            c = (n[0] * v[0] + n[1] * v[1] + n[2] * v[2]) / (nn * vn)
            if c <= 0:
                continue
            if _seg_hits_sphere(p, (0.0, 0.0, zc), BALL_R):
                continue
            tot += es_at(p[0], z) * r * sl * dz * (2 * math.pi / nph) * c
    return tot


_AS = [visible_glow(i) for i in range(N_FRAMES)]
_AMAX = max(_AS)

# --- hero 位相（#48-c：単一指標で選ばない） -------------------
#   ① 見える発光量（＝ブルームが死なない）× ② 差し込みが読める深さ（呑まれている途中）
INS_HERO = 0.075
_SC = [(_AS[i] / _AMAX) * math.exp(-((insertion(i) - INS_HERO) / 0.045) ** 2) for i in range(N_FRAMES)]
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _SC[i]) + 1


# --- 糸：長さ一定の懸垂線 -------------------------------------
def _ball_att(i):
    st, ct = math.sin(TH_ATT), math.cos(TH_ATT)
    return (BALL_R * st * math.cos(PH_ATT), BALL_R * st * math.sin(PH_ATT),
            ball_z(i) - BALL_R * ct)


def _cat_solve(h, v, L):
    """端点 (0,0)→(h,v)・弧長 L の懸垂線。 sqrt(L²−v²) = 2a·sinh(h/2a) を二分法で。"""
    tgt = math.sqrt(max(1e-9, L * L - v * v))
    f = lambda a: 2 * a * math.sinh(h / (2 * a))
    lo, hi = 1e-4, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > tgt:
            lo = mid                    # a を上げると LHS は h へ単調に下がる
        else:
            hi = mid
    a = 0.5 * (lo + hi)
    x0 = h / 2 - a * math.atanh(max(-0.999999, min(0.999999, v / L)))
    c = -a * math.cosh(-x0 / a)
    return a, x0, c


def string_pts(i, n=46):
    """糸の3D折れ線（玉→けん）。鉛直面内の懸垂線を世界へ戻す。"""
    A, B = _ball_att(i), KEN_ATT
    hx, hy = B[0] - A[0], B[1] - A[1]
    h = math.hypot(hx, hy)
    v = B[2] - A[2]
    if h < 1e-6:
        hx, hy, h = 1.0, 0.0, 1e-6
    ux, uy = hx / h, hy / h
    a, x0, c = _cat_solve(h, v, STR_L)
    s0 = a * math.sinh(-x0 / a)
    out = []
    for k in range(n):
        s = STR_L * k / (n - 1)
        x = x0 + a * math.asinh(s / a + s0 / a)
        z = a * math.cosh((x - x0) / a) + c
        out.append((A[0] + ux * x, A[1] + uy * x, A[2] + z))
    return out


if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d  （挿入 %.3f m・見える発光 %.0f%%）"
          % (STILL_FRAME, insertion(STILL_FRAME - 1), 100 * _AS[STILL_FRAME - 1] / _AMAX))
    print(">> #40(6) 見える発光面積 min/max = %.3f  （合格 0.75以下）" % (min(_AS) / _AMAX))
    print(">> 変化がループのどこに集中しているか（#44）")
    for i in range(0, N_FRAMES // 2 + 1, 10):
        print("   t=%.3f  発光 %5.0f%%  挿入 %+.3f  玉底 z=%.3f  糸最下 z=%.3f"
              % (i / N_FRAMES, 100 * _AS[i] / _AMAX, insertion(i),
                 ball_z(i) - BALL_R, min(p[2] for p in string_pts(i))))
    print(">> 糸  張り %.3f〜%.3f m（弦長 %.3f・常に弛む＝伸びていない）"
          % (min(math.dist(_ball_att(i), KEN_ATT) for i in range(N_FRAMES)),
             max(math.dist(_ball_att(i), KEN_ATT) for i in range(N_FRAMES)), STR_L))
    zt = ball_z(STILL_FRAME - 1) + BALL_R
    _w = (abs(X_OZARA) + abs(X_KOZARA)) * math.cos(YAW)
    print(">> 縦 %.3f..%.3f = %.3f（フレーム3.52 の %.0f%%）  横 皿胴 %.3f（同2.81 の %.0f%%）"
          % (Z_BOT, zt, zt - Z_BOT, (zt - Z_BOT) / 3.52 * 100, _w, _w / 2.81 * 100))
    print(">> 穴の当たり  剣先半径@最深 %.4f < 穴 %.3f  ／ 挿入max %.3f < 穴深 %.3f"
          % (sp_r(ball_z(N_FRAMES // 2) - BALL_R), BORE_R,
             insertion(N_FRAMES // 2), BORE_D))
    sys.exit(0)

# =============================================================
# ここから Blender
# =============================================================
import bpy, bmesh                                        # noqa: E402
from mathutils import Vector                             # noqa: E402


def hex_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)


# ---------- マテリアル ----------
def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


# けん＝ブナの轆轤挽き。曲面主体（#17）／#45：主材の Specular IOR Level は 0.10 を割らない
mat_ken, kp = principled("ken")
kp.inputs["Base Color"].default_value = BLACK
kp.inputs["Roughness"].default_value = 0.36
kp.inputs["Specular IOR Level"].default_value = 0.15
kp.inputs["Coat Weight"].default_value = 0.05

# 玉＝塗りの厚い大きな球。#39-c の「大きな曲面は env を面で拾う」を、#45 の下限内で受ける
mat_ball, bp_ = principled("ball")
bp_.inputs["Base Color"].default_value = BLACK
bp_.inputs["Roughness"].default_value = 0.52
bp_.inputs["Specular IOR Level"].default_value = 0.11

# 穴の内壁＝純黒（#40④a：窓の内壁が拾う光は「四角い画面」を作る。ここでは緑の環になる）
mat_bore, bo = principled("bore")
bo.inputs["Base Color"].default_value = (0, 0, 0, 1)
bo.inputs["Roughness"].default_value = 0.85
bo.inputs["Specular IOR Level"].default_value = 0.0
# 🔴 #51：剣先だけでは光が小さすぎる（ライム面積0.36%）。剣先を太らせると #50 の蝋燭に転ぶので、
#    代わりに**玉が呑んだ光**として穴の内壁をわずかに発光させる。silhouette は1mmも変えない。
bo.inputs["Emission Color"].default_value = LIME
bo.inputs["Emission Strength"].default_value = 1.15

# 🔴 #51：剣先だけではライム面積0.39%。剣先を太らせると #50 の蝋燭に転ぶ（#61で実証済み）。
#    → **玉が呑んだ光が玉の腹に滲む**。穴（底）に近いほど強く、上へ消える勾配を玉の材質に焼く。
_bnt = mat_ball.node_tree
_btc = _bnt.nodes.new("ShaderNodeTexCoord")
_bsep = _bnt.nodes.new("ShaderNodeSeparateXYZ")
_bnt.links.new(_btc.outputs["Object"], _bsep.inputs["Vector"])
_bmr = _bnt.nodes.new("ShaderNodeMapRange")
_bmr.inputs["From Min"].default_value = -BALL_R * 0.98      # 玉の底（穴のある側）
_bmr.inputs["From Max"].default_value = BALL_R * 0.10
_bmr.inputs["To Min"].default_value = 0.75
_bmr.inputs["To Max"].default_value = 0.0
_bmr.clamp = True
_bnt.links.new(_bsep.outputs["Z"], _bmr.inputs["Value"])
_bnt.links.new(_bmr.outputs["Result"], bp_.inputs["Emission Strength"])
bp_.inputs["Emission Color"].default_value = LIME

mat_str, sp_ = principled("string")
sp_.inputs["Base Color"].default_value = BLACK
sp_.inputs["Roughness"].default_value = 0.46
sp_.inputs["Specular IOR Level"].default_value = 0.30      # 細いので照りが無いと消える


def uv_glow(name):
    """#34：カメラに正対する細長い発光体は長軸＋短軸の2軸で落とす。
       座標は剣先が動かないのでメッシュの UV に焼く（#39／#44-b の使い分け）。
       #32：随伴点光源があるので Base は純黒＝ES 0 の裾は黒いけんに溶ける。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0, 0, 0, 1)
    p.inputs["Specular IOR Level"].default_value = 0.0
    p.inputs["Emission Color"].default_value = LIME
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    x2, y2 = mn('POWER', 2.0), mn('POWER', 2.0)
    nt.links.new(sep.outputs["X"], x2.inputs[0]); nt.links.new(sep.outputs["Y"], y2.inputs[0])
    ad = mn('ADD'); nt.links.new(x2.outputs[0], ad.inputs[0]); nt.links.new(y2.outputs[0], ad.inputs[1])
    rr = mn('SQRT'); nt.links.new(ad.outputs[0], rr.inputs[0])
    pw = mn('POWER', GPOW); nt.links.new(rr.outputs[0], pw.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = ES_CORE; mr.inputs["To Max"].default_value = 0.0
    mr.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(pw.outputs[0], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], p.inputs["Emission Strength"])
    return m


mat_glow = uv_glow("glow_tip")

mat_floor, fp = principled("floor")
fp.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp.inputs["Roughness"].default_value = 0.42
mat_text, tp = principled("text")
tp.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp.inputs["Roughness"].default_value = 0.6


# ---------- 造形（すべて bmesh・ワールド実寸。object.scale / transform_apply 不使用＝#15） ----------
def lathe(name, prof, mats, axis='Z', seg=72, off=(0, 0, 0), slot_fn=None,
          bevel=0.0, smooth=0.6):
    """prof=[(r,a)] を軸まわりに回す閉じたソリッド。r=0 の端は極として畳む（#37②：開いた殻を作らない）。"""
    bm = bmesh.new()

    def P(r, a, ang):
        if axis == 'Z':
            v = (r * math.cos(ang), r * math.sin(ang), a)
        else:
            v = (a, r * math.cos(ang), r * math.sin(ang))
        return (v[0] + off[0], v[1] + off[1], v[2] + off[2])

    rows = []
    for (r, a) in prof:
        if r < 1e-6:
            rows.append([bm.verts.new(P(0.0, a, 0.0))])
        else:
            rows.append([bm.verts.new(P(r, a, 2 * math.pi * k / seg)) for k in range(seg)])
    for A, B in zip(rows, rows[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        if len(A) == 1:
            for k in range(seg):
                bm.faces.new((A[0], B[k], B[(k + 1) % seg]))
        elif len(B) == 1:
            for k in range(seg):
                bm.faces.new((A[k], A[(k + 1) % seg], B[0]))
        else:
            for k in range(seg):
                bm.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:                                   # #43-h：bmesh の bevel に angle_limit は無い
        sharp = []
        for e in bm.edges:
            try:
                if e.calc_face_angle() > math.radians(30):
                    sharp.append(e)
            except Exception:
                pass
        if sharp:
            bmesh.ops.bevel(bm, geom=sharp, offset=bevel, segments=2,
                            affect='EDGES', clamp_overlap=True)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    for m in mats:
        ob.data.materials.append(m)
    if slot_fn is not None:
        for f in me.polygons:
            c = f.center
            f.material_index = slot_fn(c)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


# --- けん本体：中皿の椀 → 胴 → 握り → 首 → 天面 -----------------
ken = lathe("ken", KEN_PROF, [mat_ken], bevel=0.0035, smooth=0.9)

# --- 皿胴：大皿（左・大）と小皿（右・小）。この非対称が「けん玉」を1秒で宣言する ---
cross = lathe("cross", CROSS_PROF, [mat_ken], axis='X', off=(0, 0, Z_CROSS),
              bevel=0.0035, smooth=0.9)
cross.rotation_euler = (0.0, 0.0, YAW)

# --- 剣先（発光）。根元は天面より内側から立ち上げる（#42-c：同じ向きの面を同じ平面で重ねない）---
NSP, SP_Z0 = 44, SP_BASE - 0.045
spp = [(0.0, SP_Z0)]
for k in range(NSP):
    _z = SP_Z0 + (SP_TIP - SP_Z0) * k / (NSP - 1)
    spp.append((R_SP if _z <= SP_BASE else sp_r(_z), _z))
spike = lathe("spike", spp, [mat_glow], seg=64, smooth=0.9)
uvl = spike.data.uv_layers.new(name="UVMap")
for poly in spike.data.polygons:
    for li in poly.loop_indices:
        co = spike.data.vertices[spike.data.loops[li].vertex_index].co
        uvl.data[li].uv = (co.x / FX, (co.z - Z_HOT) / FZ)

# --- 玉：球＋底の穴（一本の轆轤プロファイル＝boolean 不要・#15/#37②） ---
z_mouth = -math.sqrt(BALL_R ** 2 - BORE_R ** 2)
z_ceil = -BALL_R + BORE_D
bpf = [(0.0, z_ceil), (BORE_R * 0.5, z_ceil), (BORE_R, z_ceil), (BORE_R, z_mouth)]
th0 = math.asin(BORE_R / BALL_R)
NB = 60
bpf += [(BALL_R * math.sin(th0 + (math.pi - th0) * k / (NB - 1)),
         -BALL_R * math.cos(th0 + (math.pi - th0) * k / (NB - 1))) for k in range(NB)]
ball = lathe("ball", bpf, [mat_ball, mat_bore], seg=96, bevel=0.0025, smooth=0.9,
             slot_fn=lambda c: 1 if (c.z < z_ceil + 0.004 and
                                     math.hypot(c.x, c.y) < BORE_R + 0.006) else 0)
FR = list(range(N_FRAMES)) + [0]                 # 末尾に折り返し＝glb でループが閉じる
for f, i in enumerate(FR):
    ball.location = (0.0, 0.0, ball_z(i))
    ball.keyframe_insert("location", frame=f + 1)


# --- 糸：フレームごとに張り直してシェイプキーへ焼く（#43-e） ---
def tube_frames(ptsets, rad, seg=8):
    frames, faces = [], []
    n = len(ptsets[0])
    for pts in ptsets:
        vs = []
        for j, p in enumerate(pts):
            a = pts[max(0, j - 1)]; b = pts[min(n - 1, j + 1)]
            t = Vector((b[0] - a[0], b[1] - a[1], b[2] - a[2]))
            if t.length < 1e-9:
                t = Vector((0, 0, 1))
            t.normalize()
            ref = Vector((0, 1, 0)) if abs(t.z) > 0.9 else Vector((0, 0, 1))
            u = t.cross(ref).normalized(); w = t.cross(u).normalized()
            e = min(1.0, min(j, n - 1 - j) / 1.5)          # #21：端は細らせる（中は解けない）
            r = rad * (0.35 + 0.65 * e)
            for k in range(seg):
                ang = 2 * math.pi * k / seg
                vs.append(tuple(Vector(p) + u * (r * math.cos(ang)) + w * (r * math.sin(ang))))
        frames.append(vs)
    for j in range(n - 1):
        for k in range(seg):
            a = j * seg + k; b = j * seg + (k + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    return frames, faces


SPTS = [string_pts(i) for i in FR]
sfr, sfa = tube_frames(SPTS, STR_R)
me = bpy.data.meshes.new("string")
me.from_pydata(sfr[0], [], sfa); me.update()
string = bpy.data.objects.new("string", me)
bpy.context.collection.objects.link(string)
string.data.materials.append(mat_str)
string.shape_key_add(name="basis", from_mix=False)
_keys = []
for f, vs in enumerate(sfr):
    sk = string.shape_key_add(name="f%03d" % f, from_mix=False)
    sk.slider_min, sk.slider_max = 0.0, 1.0
    for vi, co in enumerate(vs):
        sk.data[vi].co = co
    _keys.append(sk)
for f, sk in enumerate(_keys):
    for d in (-1, 0, 1):
        fr = f + d
        if 0 <= fr < len(_keys):
            sk.value = 1.0 if d == 0 else 0.0
            sk.keyframe_insert("value", frame=fr + 1)
bpy.context.view_layer.objects.active = string; string.select_set(True)
try:
    bpy.ops.object.shade_auto_smooth(angle=0.9)
except Exception:
    pass
string.select_set(False)

# ---------- 随伴点光源（#22：光を「塗装」にしないため。強いと玉の腹が抹茶色に被る） ----------
bpy.ops.object.light_add(type='POINT', location=(0.0, -0.085, Z_HOT - 0.02))
gl = bpy.context.active_object; gl.name = "lamp_tip"
gl.data.shadow_soft_size = 0.30
gl.data.energy = LAMP_W
gl.data.color = LIME[:3]
gl.visible_camera = False

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_floor)


def caption(body, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object; tx.name = name
    tx.data.body = body; tx.data.size = size; tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 0.85), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.68), "logo"),
        caption("MIDDLE STUDY 050 — KENDAMA", 0.045, (AIM_X, -1.7, 0.57), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


focus = (0, 0, CENTER_Z)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = spike
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception:
    scene.view_settings.view_transform = 'AgX'


def setup_bloom():
    ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new("CompositorNodeRLayers")
    glr = ng.nodes.new("CompositorNodeGlare")
    ou = ng.nodes.new("NodeGroupOutput")
    try:
        glr.inputs["Type"].default_value = 'BLOOM'
    except Exception:
        pass
    glr.inputs["Threshold"].default_value = 1.2
    glr.inputs["Strength"].default_value = 0.35
    try:
        glr.inputs["Size"].default_value = 0.55
    except Exception:
        pass
    ng.links.new(rl.outputs["Image"], glr.inputs["Image"])
    ng.links.new(glr.outputs["Image"], ou.inputs["Image"])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True


setup_bloom()

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS


# ---------- #58 光を空間に出す（2026-08-14 の作り直しで追加） ----------
# 床にライムが1つも落ちていない絵は「光っている物」でなく「点いているパネル」に見える。
# 効くのは発光の強さでもバウンス数でもなく**随伴のライム光源のW数**（4.5W→150Wで床0.03%→4.68%）。
# 🔴 発光体の中に置くと発光体自身が遮って1ルクスも出ないので、被写体の下端の外に置く。
def _add_lime_spill(energy=300.0):
    xs, zs, ys = [], [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.lower().startswith(("floor", "plane", "text")):
            continue
        if max(o.dimensions) > 8:      # 床の巨大プレーンを除く
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            xs.append(w.x); ys.append(w.y); zs.append(w.z)
    if not zs:
        return None
    cx, cy, zmin = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)
    # 🔴 浮いている作は真下へ。床に接している作は真下だと**床の下に潜って1ルクスも出ない**ので、
    #    カメラ側(-Y)へ逃がして床すれすれに置く（031 TOURO で踏んだ）
    # 🔴 被写体の真下に置くと、床の光が画面の測定帯（62〜80%）より下に落ちて見えない。
    #    手前(-Y)の床を照らす位置にすると、光の溜まりがそのまま絵に入る（031で実測 0.00%→0.39%）。
    loc = (cx, cy - 0.62, min(0.42, max(0.16, zmin - 0.10)))
    bpy.ops.object.light_add(type='POINT', location=loc)
    L = bpy.context.active_object; L.name = "lime_spill"
    L.data.energy = energy; L.data.color = LIME[:3]
    L.data.shadow_soft_size = 0.30
    L.visible_camera = False
    print(">> lime_spill %.2f,%.2f,%.2f  (zmin %.2f, %.0fW)" % (loc[0], loc[1], loc[2], zmin, energy))
    return L


_add_lime_spill()

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME)

if "probe" in modes:
    print(">> #40(6) 見える発光面積 min/max = %.3f （合格 0.75以下）" % (min(_AS) / _AMAX))
    for i in range(0, N_FRAMES // 2 + 1, 10):
        print("   t=%.3f  発光 %5.0f%%  挿入 %+.3f" % (i / N_FRAMES, 100 * _AS[i] / _AMAX, insertion(i)))
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, zs = [], []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name == "Plane":
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            w = ev.matrix_world @ v.co
            xs.append(w.x); zs.append(w.z)
    print(">> BBOX  x %.3f..%.3f (%.3f)  z %.3f..%.3f (%.3f)  ／ フレーム 横2.81・縦3.52" %
          (min(xs), max(xs), max(xs) - min(xs), min(zs), max(zs), max(zs) - min(zs)))
    print(">> 占有  横%.0f%%  縦%.0f%%   キャプション上端 0.85 とのクリアランス %.3f  中心z %.3f（LOOK %.2f）" %
          ((max(xs) - min(xs)) / 2.81 * 100, (max(zs) - min(zs)) / 3.52 * 100,
           min(zs) - 0.85, 0.5 * (min(zs) + max(zs)), LOOK_Z))

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 480, 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test done")

if "testhero" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_testhero.png")
    bpy.ops.render.render(write_still=True)
    print(">> testhero done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero done")

if "phases" in modes:
    # #35：ループものは still 以外の位相も撮る（材質側の破綻は1枚では出ない）
    for fr in (1, 31, 61, 91):
        scene.frame_set(fr)
        scene.render.resolution_x, scene.render.resolution_y = 480, 600
        scene.cycles.samples = 24
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(OUT, "_phase_%03d.png" % fr)
        bpy.ops.render.render(write_still=True)
    print(">> phases done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = 720, 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> anim done")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_050.blend"))

# 🔴 glb は必ず最後（#30：Emission を定数へ潰すので、レンダーの前に置かない）
if "glb" in modes:
    p = mat_glow.node_tree.nodes["Principled BSDF"]
    for l in list(mat_glow.node_tree.links):
        if l.to_socket == p.inputs["Emission Strength"]:
            mat_glow.node_tree.links.remove(l)
    p.inputs["Emission Strength"].default_value = 2.6
    scene.frame_end = N_FRAMES + 1
    names = {"ken", "cross", "spike", "ball", "string"}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = ball
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
