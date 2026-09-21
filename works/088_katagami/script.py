# =============================================================
# MIDDLE STUDY 088 — KATAGAMI（伊勢型紙 / the thread that holds what would fall）
#
#   光の型＝背光（#53）  構図の型＝天地（#57）  ドメイン＝染め・型紙（シリーズ未踏）
#
# 型紙は、彫って作る。彫ったところが模様になる。**つまり、捨てたところが絵になる。**
# 残った紙は、染めない側だ。紙は一度も模様を持たない——紙が持っているのは、孔だけ。
#
# そして彫り進めると、どうしても**どこにも繋がっていない紙（島）**が出る。
# 島はそのままでは落ちる。落ちたら模様は死ぬ。だから彫り師は、二枚に剥いだ紙のあいだに
# 絹の糸を挟んで貼り直す——**糸入れ**。糸は染めには一切関わらない。ただ、
# 落ちるはずのものを、落ちないように、真ん中で吊っているだけだ。
#
# **模様を模様にしているのは、彫った孔ではない。落ちるはずの島を吊っている糸のほうだ。**
#
# 造形：紙は弧長でパラメータを取った 120×150 の格子（#72：板ではないと見せる＝
#       下端の巻きと横の反りを**弧長を保ったまま**積分で入れる。伸び縮みしない）。
#       孔は実ジオメトリではなく**ステンシル画像のアルファ**で抜く——錐彫りの点は
#       実物で径 1mm 前後、格子で抜くと必ず階段になる（#68 と同型の事故）。
#       画像は numpy で描く：鮫小紋（扇状に並ぶ同心円弧の点・約 5,000 粒）と、
#       観世水（波打つ同心の切れ目・6本）。観世水は紙の左と下の**縁を切って**いる
#       ＝孔が輪郭を切り欠く（#98①：切れ目が輪郭に届いて初めて「模様」でなく「割れている物」になる）。
#       糸入れは 5 本の絹糸（半径 0.0042）で、紙の裏側にだけ出して面に沿わせた。
#       黒は nuno_usu（#52／MATERIALS.md の薄物＝紙・幕）。DISPLACE も SUBSURF も掛けない
#       （#76⑦：角のある部材に Catmull-Clark を掛けると別の物になる。紙は角がある）。
#
# 光：背光。065 TORII の光をそのまま移植した（#89③：値ごと移せる）。
#     紙のうしろに楕円の発光面を置き、**不透明さを発光の強さから切り離す**（K_ALPHA＝#76①）。
#     芯は白飛び → #A5E02E → 不透明なまま背景より暗いライム。紙はその前で真っ黒に落ちる。
#     🔴 だから錐彫りの点は**位置によって色が違う**——中心の点は白、外へ行くほどライム、
#        縁の点は暗いライム。勾配は紙が「標本」のように拾う。
#     🔴 発光の値は1フレームも動かしていない（#69②／#70④）。光の振れは全部ジオメトリ。
#
# 動き：紙を渡る進行波。A(t)·sin(2π·N·u/W − 2πt) は
#         sin(θ−2πt) = sinθ·cos2πt − cosθ·sin2πt
#       と展開できるので、**固定した2つの形（S と C）の線形結合**で厳密に書ける
#       ＝シェイプキー4枚（S±・C±）＋毎フレームの重みだけで glb にそのまま乗る。
#       振幅 A(t)=0.35+0.65·(1−cos2πt)/2 は t=0 で最小・t=0.5 で最大＝**紙の面が
#       立つほど孔の射影面積が減る**ので、発光を一切触らずに光が呼吸する（#84 の逆手）。
#       ヨーも cos で振る。すべて整数周期＝数学的に閉じる。
#       確かめ方＝`python3 script.py -- geom`（Blender を起動せず、孔の射影面積を
#       毎フレーム積分して、光の振れと閉じを数字で出す）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = float(os.environ.get("LIME_W", "60"))

# --- 紙（弧長座標 u:幅 / v:高さ。原点＝紙の中心）-------------------
CX, CZ = AIM_X, float(os.environ.get("CZ", "2.40"))   # 天地＝高く置く（重心yが基準63%から −16%）
SW = float(os.environ.get("SW", "1.35"))
SH = float(os.environ.get("SH", "1.78"))
NU, NV = 120, 150
PSI0, DPSI = 22.0, 20.0         # ヨー（度）。2°〜42° を cos で往復する。
# 🔴 光の振れ（#59：ライム面積の最大/最小 ≥1.22）を作るのは孔ではなく**紙が光を隠す量**。
#    波だけでは山と谷が射影面積を打ち消し合って 1.06 倍しか振れない（#94 の型）。
#    紙が正面を向くと光を最大に隠し、振れると隠さない＝振れは cos ψ でそのまま出る。
KU = 0.55                       # 横の反り（円筒の曲率）。両端がこちらへ来る
KV, V0F, LVF = 1.15, -0.02, 0.52    # 下端の巻き（曲率・始まる高さ・立ち上がりの長さ）
WAVE_N = 2.6                    # 進行波の本数（幅方向）
WAVE_A = 0.055                  # 振幅
WAVE_LO = 0.35                  # 振幅の下限比（t=0 でも平らにはしない）
PH_V = 1.25                     # 波の稜を斜めにする（v 方向の位相）。縦縞に見せない
TAPER = 0.30                    # 上端での振幅比（吊られている側は揺れない）
STILL_FRAME = int(os.environ.get("STILL_FRAME", "31"))

# --- 彫り（ステンシル）-------------------------------------------
MG = 0.055                      # 小紋を置かない縁
# 鮫小紋（地）：扇状に並ぶ同心円弧の点
SX, SY = 0.176, 0.112           # 割付
DR, DS, RD, FAN, NA = 0.024, 0.021, 0.0046, 1.22, 5
# 流水（大柄）：紙を左の縁から右の縁まで横切る一筋。
# 🔴 1周目は「観世水＝同心の輪」を彫ったが、絵は**指紋**になった（#95：記号の形の孔は
#    既知の記号に読まれる。同心の輪は指紋か的）。**中心を持たない一筋**に替えた。
#    この一筋は紙を上下2つに切り離す＝下側は糸だけで吊られている（＝糸入れの理由そのもの）。
RB_V0, RB_SL = -0.10, 0.55      # 流れの高さ（SH比）と傾き
RB_A1, RB_F1, RB_P1 = 0.075, 1.15, 0.90     # うねり
RB_W, RB_WF, RB_WP = 0.086, 0.70, 3.6       # 幅・幅のうねりの周期と位相
# 島（木の葉）：流れの中に浮く紙。どこにも繋がっていないので、糸が無ければ落ちる
LEAF = ((-0.40, 0.080, 0.030, 0.55), (-0.02, 0.070, 0.027, 0.30),
        (0.34, 0.075, 0.028, 0.10), (0.62, 0.055, 0.024, -0.10))
MW, MH = 1250, 1650             # ステンシル画像（hero の 1.6 倍の密度）

# --- 糸入れ -------------------------------------------------------
TH_N, TH_SP, TH_ANG, TH_R = 5, 0.28, -7.0, 0.0060
TH_V0 = -0.10                   # 糸の束の中心（v）
TH_OFF = 0.0055                 # 紙の裏側へ逃がす量（表からは見えない＝実物の糸入れ）
TH_IN = 0.035                   # 🔴 両端を紙の内側で止める。縁まで通すと、糸の端が
                                #    明るいコロナの上に**小さな突起**として並ぶ（1600×2000 で初めて出た＝#68）

# --- 光（紙のうしろ）。065 TORII の型をそのまま移植（#76／#89③）----
Y_GLOW = 0.95
RX, RZ = 1.14, 1.53             # 紙の輪郭（投影 1.115倍）より外まで可視域を届かせる（#76②）
NRF, NAF = 72, 120
ES_CORE = 7.5
WHITE_FROM, WHITE_TO = 0.80, 0.46
K_ALPHA = 11.0                  # #76①：不透明さを発光の強さから切り離す
HAZE_A1, HAZE_F1 = 0.05, 4.5
HAZE_A2, HAZE_F2 = 0.035, 11.0

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def smooth(e0, e1, x):
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def v_profile():
    """下端の巻き。弧長を保ったまま上から積分する（#72：紙は伸び縮みしない）"""
    ds = SH / NV
    ys = [0.0] * (NV + 1)
    zs = [0.0] * (NV + 1)
    th = 0.0
    y = z = 0.0
    ys[NV], zs[NV] = 0.0, 0.0
    for i in range(NV - 1, -1, -1):
        vm = -SH / 2 + (i + 0.5) * ds
        k = KV * smooth(0.0, 1.0, (V0F * SH - vm) / (LVF * SH))
        th += k * ds
        y -= math.sin(th) * ds
        z -= math.cos(th) * ds
        ys[i], zs[i] = y, z
    zc = 0.5 * (zs[0] + zs[NV])
    return ys, [zz - zc for zz in zs], ds


VY, VZ, DSV = v_profile()


def v_at(v):
    """v（弧長）での (y, z)。格子の節点以外も線形で引ける"""
    x = (v + SH / 2) / SH * NV
    i = max(0, min(NV - 1, int(x)))
    f = x - i
    return (VY[i] + (VY[i + 1] - VY[i]) * f, VZ[i] + (VZ[i + 1] - VZ[i]) * f)


def u_at(u):
    """横の反り（曲率一定の円弧）。u は弧長"""
    a = KU * u
    return (math.sin(a) / KU, -(1.0 - math.cos(a)) / KU)


def base_pt(u, v):
    xu, yu = u_at(u)
    yv, zv = v_at(v)
    return (xu, yu + yv, zv)


def base_nrm(u, v):
    h = 3e-3
    p0 = base_pt(u, v)
    pu = base_pt(min(SW / 2, u + h), v)
    pv = base_pt(u, min(SH / 2, v + h))
    au = [pu[i] - p0[i] for i in range(3)]
    av = [pv[i] - p0[i] for i in range(3)]
    n = (au[1] * av[2] - au[2] * av[1],
         au[2] * av[0] - au[0] * av[2],
         au[0] * av[1] - au[1] * av[0])
    m = math.sqrt(sum(c * c for c in n)) or 1.0
    n = tuple(c / m for c in n)
    return n if n[1] < 0 else tuple(-c for c in n)     # 法線はカメラ側（−y）へ


def wave_phase(u, v):
    return 2.0 * math.pi * WAVE_N * (u + SW / 2) / SW + PH_V * (v / SH)


def wave_amp(v):
    return WAVE_A * (TAPER + (1.0 - TAPER) * ((SH / 2 - v) / SH) ** 1.05)


def amp_t(t):
    return WAVE_LO + (1.0 - WAVE_LO) * 0.5 * (1.0 - math.cos(2.0 * math.pi * t))


def weights(t):
    """進行波 A(t)·sin(θ−2πt) ＝ w1·sinθ + w2·cosθ（固定2形の線形結合）"""
    a = amp_t(t)
    return (a * math.cos(2.0 * math.pi * t), -a * math.sin(2.0 * math.pi * t))


def yaw_t(t):
    return math.radians(PSI0 + DPSI * math.cos(2.0 * math.pi * t))


def to_screen(p):
    """カメラは (0.55,−8.3,1.95) から +Y を真っ直ぐ見る＝射影は素直な相似"""
    d = (p[1] + 8.3) / 8.3
    return (0.5 + (p[0] - AIM_X) / (FRAME_W * d),
            0.5 + (p[2] - LOOK_Z) / (FRAME_H * d))


def pose_pt(u, v, t):
    """その時刻の世界座標（波＋ヨー＋位置）"""
    bx, by, bz = base_pt(u, v)
    n = base_nrm(u, v)
    w1, w2 = weights(t)
    th = wave_phase(u, v)
    d = wave_amp(v) * (w1 * math.sin(th) + w2 * math.cos(th))
    lx, ly, lz = bx + n[0] * d, by + n[1] * d, bz + n[2] * d
    c, s = math.cos(yaw_t(t)), math.sin(yaw_t(t))
    return (CX + lx * c - ly * s, lx * s + ly * c, CZ + lz)


def pose_nrm(u, v, t):
    n = base_nrm(u, v)
    c, s = math.cos(yaw_t(t)), math.sin(yaw_t(t))
    return (n[0] * c - n[1] * s, n[0] * s + n[1] * c, n[2])


# ---------- ステンシル（彫り）。numpy で描く。画像と積分で同じ式を使う ----------
def stencil_mask(U, V, aa):
    """U,V＝紙の中心を原点とする弧長座標（numpy配列）。戻り値 1.0=紙 / 0.0=孔"""
    import numpy as np

    def band(d, half):
        return np.clip((half - d) / aa + 0.5, 0.0, 1.0)

    hole = np.zeros_like(U)

    # 流水（大柄）：中心を持たない一筋。左の縁から右の縁まで抜けて紙を2つに切る
    ph = 2.0 * np.pi * RB_F1 * (U + SW / 2) / SW + RB_P1
    vc = RB_V0 * SH + RB_SL * U + RB_A1 * np.sin(ph)
    bw = RB_W * (0.75 + 0.25 * np.sin(2.0 * np.pi * RB_WF * (U + SW / 2) / SW + RB_WP))
    hole = np.maximum(hole, band(np.abs(V - vc), bw))

    # 島（木の葉）：流れの中に浮かぶ紙。ここだけ hole を 0 に戻す
    keep = np.zeros_like(U)
    for (lu, la, lb, lr) in LEAF:
        cu = lu * SW / 2
        cv = (RB_V0 * SH + RB_SL * cu
              + RB_A1 * math.sin(2.0 * math.pi * RB_F1 * (cu + SW / 2) / SW + RB_P1))
        c, s2 = math.cos(lr), math.sin(lr)
        du, dv = U - cu, V - cv
        pu = du * c + dv * s2
        pv = -du * s2 + dv * c
        e = np.hypot(pu / la, pv / lb)
        keep = np.maximum(keep, np.clip((1.0 - e) * la / aa + 0.5, 0.0, 1.0))
    hole = np.minimum(hole, 1.0 - keep)

    # 鮫小紋：扇状に並ぶ同心円弧の点。縁（MG）の内側だけ
    inm = ((np.abs(U) < SW / 2 - MG) & (V < SH / 2 - MG) & (V > -SH / 2 + MG)).astype(U.dtype)
    row = np.floor((V + SH / 2) / SY)
    for di in (-1, 0, 1):
        ri = row + di
        off = np.where(np.mod(ri, 2.0) < 0.5, 0.0, SX * 0.5)
        col = np.floor((U + SW / 2 - off) / SX)
        ccv = ri * SY - SH / 2
        for dj in (-1, 0, 1):
            ccu = (col + dj + 0.5) * SX + off - SW / 2
            pu, pv = U - ccu, V - ccv
            rr = np.hypot(pu, pv)
            ph = np.arctan2(pu, pv)
            for k in range(NA):
                rk = (k + 0.5) * DR
                dphi = DS / rk
                nmax = math.floor(FAN / dphi)
                n = np.clip(np.round(ph / dphi), -nmax, nmax)
                d = np.hypot(rr - rk, rk * (ph - n * dphi))
                hole = np.maximum(hole, band(d, RD) * inm)

    return 1.0 - hole


def open_grid(nu, nv):
    """粗い格子ごとの開口率（積分用。ステンシルと同じ式から作る）"""
    import numpy as np
    sub = 6
    u = (np.arange(nu * sub) + 0.5) / (nu * sub) * SW - SW / 2
    v = (np.arange(nv * sub) + 0.5) / (nv * sub) * SH - SH / 2
    U, V = np.meshgrid(u, v)
    m = stencil_mask(U, V, SW / (nu * sub))
    op = 1.0 - m
    return op.reshape(nv, sub, nu, sub).mean(axis=(1, 3))


# ---------- Blender を起動しない検算 ----------
if "geom" in modes or "probe-only" in modes:
    import numpy as np

    NGU, NGV = 44, 60
    OP = open_grid(NGU, NGV)
    cu = [(-SW / 2 + (i + 0.5) * SW / NGU) for i in range(NGU)]
    cv = [(-SH / 2 + (j + 0.5) * SH / NGV) for j in range(NGV)]
    cell = (SW / NGU) * (SH / NGV)

    def light(t):
        """孔と紙の、それぞれの射影面積。
           🔴 画面のライム＝（光の面のうち紙に隠れていない所）＋（孔から漏れる所）
              ＝ G − 紙の射影面積 + 開口率×紙の射影面積 ＝ G − (1−開口率)·A(t)
           つまり**光の振れを作るのは孔ではなく、紙が光をどれだけ隠すか**（#94 の型：
           波の山と谷は射影面積を打ち消し合うので、波だけでは光は 1.06 倍しか振れない）"""
        so = sa = 0.0
        for j, v in enumerate(cv):
            for i, u in enumerate(cu):
                p = pose_pt(u, v, t)
                n = pose_nrm(u, v, t)
                d = (CAM_LOC[0] - p[0], CAM_LOC[1] - p[1], CAM_LOC[2] - p[2])
                m = math.sqrt(sum(c * c for c in d))
                a = cell * abs(sum(n[k] * d[k] for k in range(3))) / m
                sa += a
                so += OP[j][i] * a
        return so, sa

    OPEN = OP.mean()
    LA = [light(f / N_FRAMES) for f in range(N_FRAMES)]
    L = [x[0] for x in LA]
    A = [x[1] for x in LA]
    lo, hi = min(L), max(L)
    alo, ahi = min(A), max(A)
    print("── 幾何の検算（Blender 無し）")
    print("   孔の開口率        %.4f（紙の面積比）" % OPEN)
    print("   孔の射影 最小 %.5f / 最大 %.5f / 振れ %.2f 倍" % (lo, hi, hi / lo))
    print("   紙の射影 最小 %.5f / 最大 %.5f / 振れ %.2f 倍" % (alo, ahi, ahi / alo))
    for G in (1.8, 2.4, 3.0):
        f = lambda a: G - (1.0 - OPEN) * a
        print("   画面のライム（光の面 G=%.2f 相当）振れ %.2f 倍" % (G, f(alo) / f(ahi)))
    print("   閉じ  L(0)=%.6f  L(1)=%.6f  差 %.2e" % (L[0], light(1.0)[0], abs(L[0] - light(1.0)[0])))
    stat = sum(1 for f in range(N_FRAMES)
               if abs(A[(f + 1) % N_FRAMES] - A[f]) < 0.002 * (ahi - alo))
    print("   ほぼ止まっているフレーム %d / %d" % (stat, N_FRAMES))

    xs, ys = [], []
    for fr in (STILL_FRAME, 1, 31, 61, 91):
        t = (fr - 1) / N_FRAMES
        px = []
        py = []
        for v in (-SH / 2, 0.0, SH / 2):
            for u in (-SW / 2, 0.0, SW / 2):
                sx, sy = to_screen(pose_pt(u, v, t))
                px.append(sx); py.append(sy)
        x0, x1, y0, y1 = min(px), max(px), min(py), max(py)
        print("   [f%3d] 紙 bbox x %.3f..%.3f  y %.3f..%.3f  横 %.1f%% 縦 %.1f%%"
              % (fr, x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100))
        if fr == STILL_FRAME:
            xs, ys = [x0, x1], [y0, y1]

    # 光の面（楕円）は紙より外まで可視域が届いているか（#76②）
    gz = LOOK_Z + (CZ - LOOK_Z) * (8.3 + Y_GLOW) / 8.3
    for nm, rr in (("可視域(0.70R)", 0.70), ("外周(1.00R)", 1.00)):
        gx0, gy0 = to_screen((CX - RX * rr, Y_GLOW, gz - RZ * rr))
        gx1, gy1 = to_screen((CX + RX * rr, Y_GLOW, gz + RZ * rr))
        print("   光 %-14s 画面 x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%"
              % (nm, gx0, gx1, gy0, gy1, (gx1 - gx0) * 100, (gy1 - gy0) * 100))
    print("   キャプション上端 z=1.09 → 画面 y %.3f" % to_screen((AIM_X, -1.7, 1.09))[1])
    sys.exit(0)

# =============================================================
# ここから Blender
# =============================================================
import bpy, bmesh                                        # noqa: E402
import numpy as np                                       # noqa: E402
from mathutils import Vector                             # noqa: E402


def hex_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- マテリアル（MATERIALS.md の nuno_usu＝薄物・紙／#52）----------
NUNO_USU = dict(rough=0.66, spec=0.28, sheen=0.55, sheen_rough=0.25)


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p, r):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("sheen"):
        p.inputs["Sheen Weight"].default_value = r["sheen"]
        p.inputs["Sheen Roughness"].default_value = r["sheen_rough"]
        p.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_ito, ip_ = principled("ito"); apply_black(ip_, NUNO_USU)

# ---------- ステンシル画像（彫り）----------
print(">> 彫っています（%d×%d）…" % (MW, MH))
_u = (np.arange(MW) + 0.5) / MW * SW - SW / 2
_v = (np.arange(MH) + 0.5) / MH * SH - SH / 2
_U, _V = np.meshgrid(_u, _v)
MASK = stencil_mask(_U, _V, SW / MW).astype(np.float32)
print(">> 開口率 %.4f（紙の面積比）" % (1.0 - MASK.mean()))

img = bpy.data.images.new("stencil", MW, MH, alpha=True, float_buffer=False)
img.colorspace_settings.name = 'Non-Color'
buf = np.zeros((MH, MW, 4), dtype=np.float32)
buf[..., 3] = MASK                      # アルファ＝紙。RGB は黒のまま
img.pixels.foreach_set(buf.ravel())
img.pack()


def paper_material(name):
    """紙。アルファ（＝彫り）で Transparent と混ぜる。
       🔴 孔をジオメトリで抜かない理由：錐彫りの点は格子だと必ず階段になる（#68）"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    apply_black(p, NUNO_USU)
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "mask"
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img; tex.interpolation = 'Linear'; tex.extension = 'EXTEND'
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(p.outputs[0], mix.inputs[2])
    out = nt.nodes["Material Output"]
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m, p, tex


mat_kami, kami_p, kami_tex = paper_material("kami")

# ---------- 紙＋糸（1つのメッシュ。シェイプキーを共有する）----------
bm = bmesh.new()
uvl = bm.loops.layers.uv.new("mask")

US = [-SW / 2 + i * SW / NU for i in range(NU + 1)]
VS = [-SH / 2 + j * SH / NV for j in range(NV + 1)]
grid = []
for j, v in enumerate(VS):
    row = []
    for i, u in enumerate(US):
        row.append(bm.verts.new(base_pt(u, v)))
    grid.append(row)
bm.verts.ensure_lookup_table()
for j in range(NV):
    for i in range(NU):
        f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        f.material_index = 0
        # 🔴 UV（＝ステンシルを引く座標）はここで直に置く。
        #    bmesh の vert.index は index_update() を呼ぶまで当てにならない
        #    ——1周目はこれで全ループの UV が同じ隅に落ち、**紙が一つも彫られなかった**
        for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
            lp[uvl].uv = (a / NU, b / NV)

# 糸入れ（5本）。紙の裏へ TH_OFF だけ逃がして面に沿わせる
NSEG, NRING = 96, 6
ito_start = len(bm.verts)
for a in range(TH_N):
    v0 = TH_V0 + (a - (TH_N - 1) / 2.0) * TH_SP
    rings = []
    for s in range(NSEG + 1):
        u = -SW / 2 + TH_IN + s * (SW - 2 * TH_IN) / NSEG
        v = v0 + math.tan(math.radians(TH_ANG)) * u
        v = max(-SH / 2 + 1e-3, min(SH / 2 - 1e-3, v))
        p = base_pt(u, v)
        n = base_nrm(u, v)
        c = [p[k] - n[k] * TH_OFF for k in range(3)]          # 裏側（＝+y 側）へ
        q = base_pt(min(SW / 2, u + 4e-3), v)
        tg = [q[k] - p[k] for k in range(3)]
        m = math.sqrt(sum(x * x for x in tg)) or 1.0
        tg = [x / m for x in tg]
        e1 = [n[1] * tg[2] - n[2] * tg[1], n[2] * tg[0] - n[0] * tg[2],
              n[0] * tg[1] - n[1] * tg[0]]
        m = math.sqrt(sum(x * x for x in e1)) or 1.0
        e1 = [x / m for x in e1]
        ring = []
        for k in range(NRING):
            a2 = 2 * math.pi * k / NRING
            ring.append(bm.verts.new([
                c[q2] + TH_R * (math.cos(a2) * e1[q2] + math.sin(a2) * n[q2])
                for q2 in range(3)]))
        rings.append(ring)
    for s in range(NSEG):
        for k in range(NRING):
            k2 = (k + 1) % NRING
            f = bm.faces.new((rings[s][k], rings[s][k2], rings[s + 1][k2], rings[s + 1][k]))
            f.material_index = 1
            for lp in f.loops:
                lp[uvl].uv = (0.0, 0.0)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("kami_mesh")
bm.to_mesh(me); bm.free()
me.materials.append(mat_kami)
me.materials.append(mat_ito)
for p in me.polygons:
    p.use_smooth = True


kami = bpy.data.objects.new("katagami", me)
bpy.context.collection.objects.link(kami)
kami.location = (CX, 0.0, CZ)

# --- シェイプキー4枚（進行波を固定2形の線形結合に分解＝glb にそのまま乗る）---
NV_TOT = len(me.vertices)
base_co = np.empty(NV_TOT * 3, dtype=np.float32)
me.vertices.foreach_get("co", base_co)
base_co = base_co.reshape(NV_TOT, 3)

# 各頂点の (u, v)：紙は格子から、糸は生成時の (u, v) を持たないので基準点から逆に引く
offS = np.zeros((NV_TOT, 3), dtype=np.float32)
offC = np.zeros((NV_TOT, 3), dtype=np.float32)
idx = 0
for j, v in enumerate(VS):
    for i, u in enumerate(US):
        n = base_nrm(u, v)
        th = wave_phase(u, v)
        A = wave_amp(v)
        offS[idx] = [n[k] * A * math.sin(th) for k in range(3)]
        offC[idx] = [n[k] * A * math.cos(th) for k in range(3)]
        idx += 1
for a in range(TH_N):
    v0 = TH_V0 + (a - (TH_N - 1) / 2.0) * TH_SP
    for s in range(NSEG + 1):
        u = -SW / 2 + TH_IN + s * (SW - 2 * TH_IN) / NSEG
        v = v0 + math.tan(math.radians(TH_ANG)) * u
        v = max(-SH / 2 + 1e-3, min(SH / 2 - 1e-3, v))
        n = base_nrm(u, v)
        th = wave_phase(u, v)
        A = wave_amp(v)
        sS = [n[k] * A * math.sin(th) for k in range(3)]
        sC = [n[k] * A * math.cos(th) for k in range(3)]
        for k in range(NRING):
            offS[idx] = sS
            offC[idx] = sC
            idx += 1
assert idx == NV_TOT, (idx, NV_TOT)

kami.shape_key_add(name="Basis", from_mix=False)
KEYS = [("Sp", offS, 1.0), ("Sm", offS, -1.0), ("Cp", offC, 1.0), ("Cm", offC, -1.0)]
for nm, off, sgn in KEYS:
    kb = kami.shape_key_add(name=nm, from_mix=False)
    co = (base_co + off * sgn).ravel()
    kb.data.foreach_set("co", co)

# --- キーフレーム（毎フレーム・イージング無し＝ループの不変条件）----
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
kb = kami.data.shape_keys.key_blocks
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
for f, ix in enumerate(FR_):
    t = ix / N_FRAMES
    w1, w2 = weights(t)
    kb["Sp"].value = max(0.0, w1)
    kb["Sm"].value = max(0.0, -w1)
    kb["Cp"].value = max(0.0, w2)
    kb["Cm"].value = max(0.0, -w2)
    for nm in ("Sp", "Sm", "Cp", "Cm"):
        kb[nm].keyframe_insert("value", frame=f + 1)
    kami.rotation_euler = (0.0, 0.0, yaw_t(t))
    kami.keyframe_insert("rotation_euler", frame=f + 1)

parts = [kami]


# ---------- 光（紙のうしろ）。065／078 と同じ組み方 ----------
def field_e(du, dv):
    r = math.hypot(du / RX, dv / RZ)
    if r >= 1.0:
        return 0.0
    return 0.55 * math.exp(-(r / 0.30) ** 2) + 0.45 * (1.0 - r * r) ** 2.8


def glow_mesh():
    bmg = bmesh.new()
    ctr = bmg.verts.new((0.0, 0.0, 0.0))
    rings = []
    for j in range(1, NRF + 1):
        rho = j / NRF
        rings.append([bmg.verts.new((rho * RX * math.cos(2 * math.pi * k / NAF), 0.0,
                                     rho * RZ * math.sin(2 * math.pi * k / NAF)))
                      for k in range(NAF)])
    for k in range(NAF):
        bmg.faces.new((ctr, rings[0][k], rings[0][(k + 1) % NAF]))
    for j in range(NRF - 1):
        for k in range(NAF):
            k2 = (k + 1) % NAF
            bmg.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    bmesh.ops.recalc_face_normals(bmg, faces=bmg.faces)
    uvg = bmg.loops.layers.uv.new("grad")
    for f in bmg.faces:
        for lp in f.loops:
            co = lp.vert.co
            lp[uvg].uv = (field_e(co.x, co.z), 0.5)
    meg = bpy.data.meshes.new("hikari"); bmg.to_mesh(meg); bmg.free()
    return meg


def glow_material(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    E = sep.outputs["X"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    gsep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], gsep.inputs["Vector"])

    def band(freq, amp, phase):
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = 2.0 * math.pi * freq
        nt.links.new(gsep.outputs["Z"], mul.inputs[0])
        add = nt.nodes.new("ShaderNodeMath"); add.operation = 'ADD'
        add.inputs[1].default_value = phase
        nt.links.new(mul.outputs[0], add.inputs[0])
        sn = nt.nodes.new("ShaderNodeMath"); sn.operation = 'SINE'
        nt.links.new(add.outputs[0], sn.inputs[0])
        ma = nt.nodes.new("ShaderNodeMath"); ma.operation = 'MULTIPLY_ADD'
        ma.inputs[1].default_value = 0.5 * amp
        ma.inputs[2].default_value = 0.5 * amp
        nt.links.new(sn.outputs[0], ma.inputs[0])
        return ma.outputs[0]

    b1, b2 = band(HAZE_F1, HAZE_A1, 0.0), band(HAZE_F2, HAZE_A2, 1.7)
    bsum = nt.nodes.new("ShaderNodeMath"); bsum.operation = 'ADD'
    nt.links.new(b1, bsum.inputs[0]); nt.links.new(b2, bsum.inputs[1])
    haze = nt.nodes.new("ShaderNodeMath"); haze.operation = 'SUBTRACT'
    haze.inputs[0].default_value = 1.0
    nt.links.new(bsum.outputs[0], haze.inputs[1])
    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = WHITE_FROM
    wmr.inputs["From Max"].default_value = 1.0
    wmr.inputs["To Min"].default_value = 0.0
    wmr.inputs["To Max"].default_value = WHITE_TO
    nt.links.new(E, wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])
    es0 = nt.nodes.new("ShaderNodeMath"); es0.operation = 'MULTIPLY'
    es0.inputs[1].default_value = ES_CORE
    nt.links.new(E, es0.inputs[0])
    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    nt.links.new(es0.outputs[0], es.inputs[0]); nt.links.new(haze.outputs[0], es.inputs[1])
    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_ALPHA          # #76①：不透明さを強さから切り離す
    nt.links.new(E, a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MULTIPLY'
    nt.links.new(a1.outputs[0], a2.inputs[0]); nt.links.new(haze.outputs[0], a2.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("hikari")
glow = bpy.data.objects.new("hikari", glow_mesh())
bpy.context.collection.objects.link(glow)
glow.data.materials.append(mat_glow)
glow.location = (CX, Y_GLOW, LOOK_Z + (CZ - LOOK_Z) * (8.3 + Y_GLOW) / 8.3)
glow.visible_shadow = False

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor_obj = bpy.context.active_object
floor_obj.name = "floor"
floor_obj.data.materials.append(mat_floor)


def caption(body_s, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object; tx.name = name
    tx.data.body = body_s; tx.data.size = size; tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 1.02), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.85), "logo"),
        caption("MIDDLE STUDY 088 — KATAGAMI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = (CX, 0.0, CZ)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
# 🔴 #76④：背光の作では白い逆光がライムの回り込みを上書きする＝ライムより弱く（1800→620W）
back = area("back", (0.0, 5.2, 2.2), 4.0, 620, (1.0, 0.99, 0.96), focus)
back.visible_camera = False        # 🔴 #67①：紙は孔だらけ＝逆光がそのままカメラに写る

# 🔴 #58③：随伴のライム光源は発光体の外。紙の裏・床寄り
for sx, sy, sz in ((-1.25, 0.50, 0.32), (2.35, 0.50, 0.32)):
    bpy.ops.object.light_add(type='POINT', location=(sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f" % sx
    lp.data.energy = LIME_W
    lp.data.shadow_soft_size = 2.60
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0

world_d = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world_d; world_d.use_nodes = True
bgn = world_d.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 8.3
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは全ジオメトリ生成後（#56②）。床を受光から外す
lit = bpy.data.collections.new("lit_by_back")
bpy.context.scene.collection.children.link(lit)
for o in parts:
    lit.objects.link(o)
back.light_linking.receiver_collection = lit

scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
scene.cycles.transparent_max_bounces = 24      # 孔が多い＝透過の打ち切りで黒点が出る
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception:
    scene.view_settings.view_transform = 'AgX'


def setup_glare():
    """🔴 #54：try で包まない。2026-08-13 Ryota決定＝Streaks 続投。"""
    ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new("CompositorNodeRLayers")
    glr = ng.nodes.new("CompositorNodeGlare")
    ou = ng.nodes.new("NodeGroupOutput")
    glr.inputs["Type"].default_value = 'Streaks'
    glr.inputs["Threshold"].default_value = 1.2
    glr.inputs["Strength"].default_value = 0.35
    glr.inputs["Size"].default_value = 0.55
    ng.links.new(rl.outputs["Image"], glr.inputs["Image"])
    ng.links.new(glr.outputs["Image"], ou.inputs["Image"])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True


setup_glare()

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME,
      " 頂点 %d  面 %d" % (len(me.vertices), len(me.polygons)))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 61, 91):
        scene.frame_set(fr); dg.update()
        allx, ally = [], []
        for ob in parts:
            ev = ob.evaluated_get(dg)
            for v in list(ev.data.vertices)[::11]:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                allx.append(c.x); ally.append(c.y)
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  "
              "重心x %.1f%%  紙の上端（上から）%.1f%%"
              % (fr, x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100, edge,
                 (x0 + x1) / 2 * 100, (1 - y1) * 100))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_088.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_kami = bpy.data.materials.new("kami_glb"); m_kami.use_nodes = True
    nt = m_kami.node_tree
    pk = nt.nodes["Principled BSDF"]
    apply_black(pk, NUNO_USU)
    uvg = nt.nodes.new("ShaderNodeUVMap"); uvg.uv_map = "mask"
    tg = nt.nodes.new("ShaderNodeTexImage")
    tg.image = img; tg.interpolation = 'Linear'; tg.extension = 'EXTEND'
    nt.links.new(uvg.outputs["UV"], tg.inputs["Vector"])
    nt.links.new(tg.outputs["Alpha"], pk.inputs["Alpha"])
    try:
        m_kami.blend_method = 'CLIP'
    except Exception:
        pass
    try:
        m_kami.surface_render_method = 'DITHERED'
    except Exception:
        pass
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = 1.8
    me.materials[0] = m_kami
    glow.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {glow.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True,
                                  export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
