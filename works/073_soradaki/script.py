# =============================================================
# MIDDLE STUDY 073 — SORADAKI（空薫 / burning it where no one looks）
#
# 空薫（そらだき）は、香を焚いているところを見せない焚き方だ。
# 客が来る前に炭を埋め、灰を押さえ、香炉は棚の陰に置く。
# 部屋に入った人は、香りだけを受け取る。**火は、どこにも見えない。**
#
# ここには黒い器がふたつある。
# 左は香炉。灰を盛った山の中に、炭がひとつ埋まっている。
# 右は香合。焚く前の香木が、蓋の下で待っている。
#
# 光は、どちらか一方にしかない。
# 香合がひらいているあいだ、香炉は口を伏せて暗い。
# 香炉がこちらを向いたときには、蓋はもう閉じている。
# **受け渡しの一瞬、光はどちらにも無い。**
# 香りだけが在って、火の在処が分からない——それが空薫だ。
#
# 🔴 光の型＝**内包**（#53：72作で8作。黒い殻の内側が光り、開口から見える）
# 🔴 構図の型＝**対**（#57：72作で4作。**72作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／
#    #76⑤／#78／#79／#80／#81／#82⑤ に続く16例目）。今日選べたのは
#    光＝内包／隙間／背光 × 構図＝全身／端寄せ／対。9通りを works.json で数えたら：
#      内包×全身  5 ／ 内包×端寄せ 0 ／ 内包×対 0
#      隙間×全身 18 ／ 隙間×端寄せ 1 ／ 隙間×対 0
#      背光×全身  3 ／ 背光×端寄せ 0 ／ 背光×対 0
#    ・**背光は #67⑤（寄り）／#69①（対）／#71①（群）／#74②（端寄せ）で4方向とも潰れている**＝
#      実質「全身」専用。空欄が3つあるのは自由度ではなく、**組めないから空いている**。→ 落とす。
#    ・隙間(19) と 全身(51) はシリーズの既定であって、もう型ではない。→ 落とす。
#    ・残る空欄は **内包×端寄せ** と **内包×対**。
#    → **内包×対**。ここは「まだ無い」ではなく **「対が要求している唯一の光の型」** だから選ぶ：
#      #71① のとおり `compositions.py` の塊マスクは**「暗い ∪ ライム」**なので、
#      **光を2つの物の“あいだ”に置いた瞬間、光が2つを繋いで clusters==1 になり対が壊れる**。
#      内包はライムを各々の殻の内側に閉じ込める＝**投影が物の輪郭から出ない**唯一の型。
#      072作で一度も無い組み合わせ。
#
# 🔴 機構＝**受け渡し**。光は増えも減りもせず、左右を行き来するだけ。
#    香炉：口の傾き rx(t) = −36°·cos2πt。t=0.5 でこちらを向き（灰山が見える）、
#          t=0 で伏せる（縁が灰山を完全に隠す＝**遮蔽で光を消す。発光は一切いじらない**）。
#    香合：蓋を横へ滑らせる d(t) = D·(0.09 + 0.91·((1+cos2πt)/2)^1.6)。t=0 で全開、t=0.5 で細目。
#    位相は逆。**どちらも幾何**なので #40⑥ が素直に測れて、そのまま glb にも乗る（#60）。
#    🔴 #80⑥：傾きと滑りは cos（端で静止する）ので、**漂い（z）と首振りは sin** ＝
#    位相が π/2 ずれ、どちらかが止まる瞬間にもう一方が最速。静止率が上がらない。
#    🔴 #71②の罠を避けた：位相を逆にしただけだと**合計が定数**になる（A+B=const で #40⑥ 0.9台）。
#      香合の開きを 1.6乗にして t=0.25/0.75 で 0.33 まで落とし、香炉は傾き0で完全に消えるので、
#      **合計は t=0.25 で谷になる**＝受け渡しの瞬間に光がどちらにも無い、が数値でもそうなる。
#
# 造形＝すべて回転体（bmesh・実寸）。boolean 不使用・object.scale 不使用（#15）。
#    香炉：三足＋双耳。**耳と脚が無いと 023 UTSUWA（黒い碗）と同じ絵になる**ので、
#          「香炉に見える」を作っているのは器ではなく**外に出た5本の付属物のシルエット**。
#    灰山：内壁と同じ半径で接する**凸のドーム**。#77⑤（広い口＋奥にへこんだ発光面＝ダウンライト）
#          を、凹面を作らないことで構造的に外す。実物の香炉の灰も、へこませず山に押さえる。
#    🔴 #82②：発光体の**光っていない部分の形**が犯人になる。灰山の縁は E≈0.03 の黒だが、
#       縁の半径を内壁と一致させたので**縁は必ず壁の下に潜る**＝輪郭を持たせない（#76③）。
#
# 黒の質感は MATERIALS.md の **`touki`（陶）**。香炉も香合も焼き物。1作1素材（掟4）。
#    add_relief は器体（碗・身・蓋）だけに掛け、脚と耳（半径0.017〜0.042）には掛けない（#77⑩）。
#
# 【ドメイン】香道・香（シリーズ未踏）。直近10作＝水引／的／躙口／薬研／茶筅／蛸壺／和蝋燭／
#    鳥居／柄鏡／和鋏 と別。067 TAKOTSUBO は「口より中が広い壺」で光を溜めたが、
#    あれは群（多数）＋絞った口で、こちらは**開いた口を伏せて隠す**＝機構が逆。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
#   （Blender 無しの幾何プローブ: python3 script.py --probe-only）
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52      # y=0 の平面での実効フレーム
LIME_W = 55.0                     # 随伴のライム光源（#58／#80⑤：シリーズ定数ではない）

# --- 香炉（左上）------------------------------------------------
KORO_C = (0.13, 0.0, 2.33)
R_O, H_O = 0.456, 0.382            # 碗の外半径・深さ
T_W, T_B = 0.037, 0.055            # 側の肉厚・底の肉厚
R_I = 0.433                        # 内側の縁の半径（＝口の半径・BOWL_IN の末端）
RIM_Z = 0.007                      # 縁の天面
NSEG = 96

LEG_AZ = (math.radians(210), math.radians(330), math.radians(90))
LEG_R0, LEG_Z0 = 0.336, -0.315     # 取り付き（碗の外面の上）
LEG_R1, LEG_Z1 = 0.393, -0.593     # 足先
LEG_RAD = (0.043, 0.027, 0.034)    # 付け根／中ほど／足の膨らみ
EAR_AZ = (0.0, math.pi)
EAR_P = ((0.451, -0.114), (0.707, 0.182), (0.470, 0.005))   # 耳の弧（半径方向, z）
EAR_RAD = 0.030   # 🔴 耳は**縁より上へ出す**。1周目は最大半径 0.420＝碗と同径で見えず、
                  #    2周目は横へ出しただけで「鍋の取っ手」に読めた。立耳（縁上 0.087）で香炉になる

# 灰山（内壁と同じ半径で接する凸ドーム）
R_M = 0.376
Z_M = -0.190                       # 縁が内壁に接する高さ
H_M = 0.068                        # 山の高さ。🔴 0.090 では**光る卵**に読めた（#82②の別型：
                                   #    形が球だと「器に入った別の物」になる。灰は面であって玉ではない）

# --- 香合（右下）------------------------------------------------
KOGO_C = (0.99, 0.0, 1.42)
R_G, H_G = 0.329, 0.143            # 身の外半径・高さ
T_G, B_G, C_G = 0.032, 0.040, 0.032
R_L, H_L, T_L = 0.329, 0.080, 0.023   # 蓋の半径・盛り上がり・厚み
TILT_G = math.radians(36.0)        # 香合の据え角（常時こちら向き）
D_MAX = 0.360                      # 蓋を滑らせる最大量（<2R なので投影は必ず重なる＝clusters 2）
AJAR = 0.34                        # 閉じても残す細目（#71② 定数化よけ）
R_BED = R_G - T_G - 0.016          # 香木の床（縁は身の壁の下に潜る）
Z_BED = -H_G + B_G + 0.004
H_BED = 0.019

# --- 動き -------------------------------------------------------
TILT_MID = math.radians(10.0)       # 🔴 振れを 0 中心にすると t=0 で香炉が**ひっくり返った鍋**になる
TILT_A = math.radians(32.0)        # 香炉の口の振れ（−22°〜+38°）
YAW_A, YAW_B = math.radians(9.0), math.radians(7.0)
BOB_A, BOB_B = 0.030, 0.024

# --- 光（#81④：halo は白へ抜ける広い勾配でしか出ない）-------------
GL_M, HOT_U_M = 0.245, 0.160       # 灰山
GL_B, HOT_U_B = 0.175, 0.085       # 香木の床
HOT_A = 0.46
E_PEAK = 1.0 + HOT_A
E_FLOOR = 0.010
ES_CORE = 5.6                      # 🔴 6.4 なら halo 22,128 まで伸びるが 中間調 #B4EF44・std 36.8＝
                                   #    白黄色へ寄る（#14）。halo 19,118／#AFEA3B／std 39.3 を採った
WHITE_FROM, WHITE_TO = 0.44, 0.62
K_MIX = 16.0                       # #76①：不透明さを発光の強さから切り離す

STILL_FRAME = 61                   # t=0.5 ＝香炉がこちらを向く（光が最大）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def tau(t):
    return 2.0 * math.pi * t


def tilt_koro(t):
    return TILT_MID - TILT_A * math.cos(tau(t))


def yaw_koro(t):
    return YAW_A * math.sin(tau(t))


def bob_koro(t):
    return BOB_A * math.sin(tau(t))


def slide(t):
    return D_MAX * (AJAR + (1.0 - AJAR) * (0.5 + 0.5 * math.cos(tau(t))) ** 1.6)


def yaw_kogo(t):
    return -YAW_B * math.sin(tau(t))


def bob_kogo(t):
    return -BOB_B * math.sin(tau(t))


def rot_zyx(v, rx, rz):
    """rotation_mode='ZYX'＝まず自軸 Z、次に世界 X（#76⑦）"""
    x, y, z = v
    c, s = math.cos(rz), math.sin(rz)
    x, y = x * c - y * s, x * s + y * c
    c, s = math.cos(rx), math.sin(rx)
    y, z = y * c - z * s, y * s + z * c
    return (x, y, z)


def e_of(rho, gl, hu):
    """発光の値（0..1）。等値線は円（#82③）"""
    raw = math.exp(-((rho / gl) ** 2)) + HOT_A * math.exp(-((rho / hu) ** 2))
    return max(0.0, (raw / E_PEAK - E_FLOOR) / (1.0 - E_FLOOR))


def dome_z(r, R, H, z0):
    u = max(0.0, 1.0 - (r / R) ** 2)
    return z0 + H * u ** 1.2


def dome_n(r, R, H):
    """ドーム表面の法線（軸対称・r方向の傾きから）"""
    if r < 1e-6:
        return (0.0, 1.0)
    u = max(1e-9, 1.0 - (r / R) ** 2)
    dz = H * 1.2 * u ** 0.2 * (-2.0 * r / (R * R))
    n = math.hypot(1.0, dz)
    return (-dz / n, 1.0 / n)          # (径方向, z方向)


def _samples(R, H, z0, gl, hu, na=48, nr=26):
    """発光ドームの面素。(局所座標, 法線, E, dA)"""
    out = []
    for i in range(nr):
        r0, r1 = R * i / nr, R * (i + 1) / nr
        r = 0.5 * (r0 + r1)
        nrad, nz = dome_n(r, R, H)
        for j in range(na):
            phi = 2.0 * math.pi * (j + 0.5) / na
            p = (r * math.cos(phi), r * math.sin(phi), dome_z(r, R, H, z0))
            n = (nrad * math.cos(phi), nrad * math.sin(phi), nz)
            dA = 0.5 * (r1 * r1 - r0 * r0) * (2.0 * math.pi / na)
            out.append((p, n, e_of(r, gl, hu), dA))
    return out


SMP_M = _samples(R_M, H_M, Z_M, GL_M, HOT_U_M)
SMP_B = _samples(R_BED, H_BED, Z_BED, GL_B, HOT_U_B)


def _flux(samples, C, rx, rz, plane_z, disc_c, disc_r, blocking):
    """カメラから見える発光量。plane_z＝開口（または蓋）の平面の局所 z、
       disc_c＝その円の局所中心、disc_r＝半径。
       blocking=False → 円の内側なら見える（開口）／True → 内側なら隠れる（蓋）"""
    NL = rot_zyx((0.0, 0.0, 1.0), rx, rz)
    DC = rot_zyx((disc_c[0], disc_c[1], plane_z), rx, rz)
    DC = (DC[0] + C[0], DC[1] + C[1], DC[2] + C[2])
    tot = 0.0
    for (p, n, E, dA) in samples:
        if E < 0.04:
            continue
        P = rot_zyx(p, rx, rz)
        P = (P[0] + C[0], P[1] + C[1], P[2] + C[2])
        N = rot_zyx(n, rx, rz)
        D = (CAM_LOC[0] - P[0], CAM_LOC[1] - P[1], CAM_LOC[2] - P[2])
        dl = math.sqrt(sum(c * c for c in D))
        D = (D[0] / dl, D[1] / dl, D[2] / dl)
        face = D[0] * N[0] + D[1] * N[1] + D[2] * N[2]
        if face <= 0.0:
            continue
        den = D[0] * NL[0] + D[1] * NL[1] + D[2] * NL[2]
        inside = False
        if abs(den) > 1e-9:
            s = ((DC[0] - P[0]) * NL[0] + (DC[1] - P[1]) * NL[1] + (DC[2] - P[2]) * NL[2]) / den
            if s > 0.0:
                X = (P[0] + s * D[0], P[1] + s * D[1], P[2] + s * D[2])
                inside = math.dist(X, DC) < disc_r
        if blocking:
            if inside:
                continue
        else:
            if den <= 0.0 or not inside:
                continue
        tot += E * face * dA
    return tot


def koro_light(t):
    C = (KORO_C[0], KORO_C[1], KORO_C[2] + bob_koro(t))
    return _flux(SMP_M, C, tilt_koro(t), yaw_koro(t), RIM_Z, (0.0, 0.0), R_I, False)


def kogo_light(t):
    C = (KOGO_C[0], KOGO_C[1], KOGO_C[2] + bob_kogo(t))
    return _flux(SMP_B, C, TILT_G, yaw_kogo(t), 0.0, (slide(t), 0.0), R_L, True)


def visible_light(t):
    return koro_light(t) + kogo_light(t)


def proj(x, y, z):
    m = 8.3 / (8.3 + y)
    return (AIM_X + (x - AIM_X) * m, LOOK_Z + (z - LOOK_Z) * m, m)


_TS = [i / N_FRAMES for i in range(N_FRAMES)]

if "--probe-only" in sys.argv:
    print("── 073 SORADAKI 幾何プローブ")
    print("   香炉 外半径%.3f 口の半径%.3f 深さ%.3f ／ 灰山 半径%.3f 高さ%.3f 頂点z=%.3f（縁 %.3f）"
          % (R_O, R_I, H_O, R_M, H_M, Z_M + H_M, RIM_Z))
    print("   香合 身 半径%.3f 高さ%.3f ／ 蓋 半径%.3f ／ 滑り %.3f〜%.3f（2R=%.3f＝投影は必ず重なる）"
          % (R_G, H_G, R_L, slide(0.5), slide(0.0), 2 * R_L))
    print("\n   ── 光の受け渡し（#40⑥ / #71②）")
    ks = [koro_light(x / 24) for x in range(24)]
    gs = [kogo_light(x / 24) for x in range(24)]
    vs = [a + b for a, b in zip(ks, gs)]
    vmax = max(vs)
    print("   香炉 " + " ".join("%3.0f" % (100 * v / vmax) for v in ks))
    print("   香合 " + " ".join("%3.0f" % (100 * v / vmax) for v in gs))
    print("   合計 " + " ".join("%3.0f" % (100 * v / vmax) for v in vs))
    print("   🔴 見える光 min/max = %.3f （合格 0.75以下）" % (min(vs) / vmax))
    th = (STILL_FRAME - 1) / N_FRAMES
    print("   hero(t=%.3f) 香炉%.0f%% 香合%.0f%% 合計は最大の %.0f%%"
          % (th, 100 * koro_light(th) / vmax, 100 * kogo_light(th) / vmax,
             100 * visible_light(th) / vmax))

    print("\n   ── 画面（hero frame %d）" % STILL_FRAME)
    pts = {"koro": [], "kogo": []}
    rx, rz = tilt_koro(th), yaw_koro(th)
    Ck = (KORO_C[0], KORO_C[1], KORO_C[2] + bob_koro(th))
    for i in range(0, 49):
        a = 0.5 * math.pi * i / 48
        for j in range(24):
            phi = 2 * math.pi * j / 24
            r = R_O * math.sin(a) ** 0.75
            z = -H_O * math.cos(a) ** 1.1
            v = rot_zyx((r * math.cos(phi), r * math.sin(phi), z), rx, rz)
            pts["koro"].append((v[0] + Ck[0], v[1] + Ck[1], v[2] + Ck[2]))
    for az in EAR_AZ:
        for u in (0.0, 0.25, 0.5, 0.75, 1.0):
            p0, p1, p2 = EAR_P
            rr = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
            zz = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
            v = rot_zyx((rr * math.cos(az), rr * math.sin(az), zz), rx, rz)
            pts["koro"].append((v[0] + Ck[0], v[1] + Ck[1], v[2] + Ck[2]))
    for az in LEG_AZ:
        for (rr, zz) in ((LEG_R0, LEG_Z0), (LEG_R1, LEG_Z1 - LEG_RAD[2])):
            v = rot_zyx((rr * math.cos(az), rr * math.sin(az), zz), rx, rz)
            pts["koro"].append((v[0] + Ck[0], v[1] + Ck[1], v[2] + Ck[2]))
    Cg = (KOGO_C[0], KOGO_C[1], KOGO_C[2] + bob_kogo(th))
    for j in range(48):
        phi = 2 * math.pi * j / 48
        for (rr, zz) in ((R_G, 0.0), (R_G, -H_G), (0.0, -H_G),
                         (R_L, 0.0), (0.0, H_L)):
            cx = slide(th) if zz >= 0.0 and rr in (R_L, 0.0) else 0.0
            v = rot_zyx((rr * math.cos(phi) + cx, rr * math.sin(phi), zz), TILT_G, yaw_kogo(th))
            pts["kogo"].append((v[0] + Cg[0], v[1] + Cg[1], v[2] + Cg[2]))
    SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2
    box = {}
    for k, ps in pts.items():
        xs = [proj(*p)[0] for p in ps]
        zs = [proj(*p)[1] for p in ps]
        box[k] = (min(xs), max(xs), min(zs), max(zs))
        print("   %-5s x %5.1f..%5.1f%%  z %5.1f..%5.1f%%"
              % (k, (box[k][0] - SX0) / FRAME_W * 100, (box[k][1] - SX0) / FRAME_W * 100,
                 (box[k][2] - SZ0) / FRAME_H * 100, (box[k][3] - SZ0) / FRAME_H * 100))
    x0 = min(b[0] for b in box.values()); x1 = max(b[1] for b in box.values())
    z0 = min(b[2] for b in box.values()); z1 = max(b[3] for b in box.values())
    print("   🔴 長辺 %.1f%%（帯 55〜65）  幅 %.1f%%  高さ %.1f%%"
          % (max((x1 - x0) / FRAME_W, (z1 - z0) / FRAME_H) * 100,
             (x1 - x0) / FRAME_W * 100, (z1 - z0) / FRAME_H * 100))
    print("   枠まで 左%.3f 右%.3f 上%.3f（正なら edge=0）"
          % (x0 - SX0, SX0 + FRAME_W - x1, SZ0 + FRAME_H - z1))
    gap = math.hypot(max(0.0, box["kogo"][0] - box["koro"][1]),
                     max(0.0, box["koro"][2] - box["kogo"][3]))
    print("   🔴 2塊の隙間 ≒ %.3f（%.0f px@1600・膨張2セル=12pxより大きいこと＝clusters 2）"
          % (gap, gap / FRAME_W * 1600))
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    print("   下端 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (z0, capz, z0 - capz))
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

# ---------- マテリアル（MATERIALS.md の実測レシピ・#52） ----------
# 香炉も香合も焼き物＝`touki`（陶）。1作1素材（掟4）。
BLACK_RECIPES = {"touki": dict(rough=0.58, spec=0.26, disp=0.005, dsize=0.10)}
RECIPE = "touki"


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p):
    r = BLACK_RECIPES[RECIPE]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = 0.0


mat_body, bp_ = principled("touki")
apply_black(bp_)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は黒へ戻す（発光板の縁を作らない・#49①）。芯だけ白へ抜く＝halo は
       この「白→ライム」の帯でしか出ない（#81④）"""
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

    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    es.inputs[1].default_value = ES_CORE
    nt.links.new(E, es.inputs[0])

    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])

    blk = nt.nodes.new("ShaderNodeBsdfPrincipled")
    apply_black(blk)

    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_MIX
    nt.links.new(E, a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])

    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a1.outputs[0], mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("hi")


# ---------- 造形（bmesh・実寸）----------
def add_revolve(bm, profile, nseg=NSEG):
    """(r, z) の折れ線を Z 軸まわりに回す。r=0 は極（扇）として1頂点にまとめる"""
    prof = []
    for p in profile:
        if not prof or math.dist(p, prof[-1]) > 1e-6:
            prof.append(p)
    rings = []
    for (r, z) in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / nseg),
                                        r * math.sin(2 * math.pi * k / nseg), z))
                          for k in range(nseg)])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(nseg):
            k2 = (k + 1) % nseg
            if len(a) == 1:
                bm.faces.new((a[0], b[k], b[k2]))
            elif len(b) == 1:
                bm.faces.new((a[k], a[k2], b[0]))
            else:
                bm.faces.new((a[k], a[k2], b[k2], b[k]))


def frames(pts):
    """回転最小フレーム（parallel transport）"""
    T = []
    for i in range(len(pts)):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        T.append((Vector(b) - Vector(a)).normalized())
    up = Vector((0.0, 0.0, 1.0))
    u = up - T[0] * up.dot(T[0])
    if u.length < 1e-6:
        u = Vector((1.0, 0.0, 0.0)) - T[0] * T[0].x
    U = [u.normalized()]
    for i in range(1, len(pts)):
        w = U[-1] - T[i] * U[-1].dot(T[i])
        if w.length < 1e-9:
            w = Vector((0.0, 0.0, 1.0)) - T[i] * T[i].z
        U.append(w.normalized())
    return T, U


def add_tube(bm, pts, radii, nr=14):
    """中心線に沿った丸棒。両端は極で閉じる"""
    T, U = frames(pts)
    rings = []
    for i, p in enumerate(pts):
        V = T[i].cross(U[i]).normalized()
        rr = radii[i]
        rings.append([bm.verts.new((p[0] + (U[i] * (rr * math.cos(2 * math.pi * k / nr))
                                            + V * (rr * math.sin(2 * math.pi * k / nr))).x,
                                    p[1] + (U[i] * (rr * math.cos(2 * math.pi * k / nr))
                                            + V * (rr * math.sin(2 * math.pi * k / nr))).y,
                                    p[2] + (U[i] * (rr * math.cos(2 * math.pi * k / nr))
                                            + V * (rr * math.sin(2 * math.pi * k / nr))).z))
                      for k in range(nr)])
    for i in range(len(rings) - 1):
        for k in range(nr):
            k2 = (k + 1) % nr
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    bm.faces.new([rings[0][k] for k in range(nr - 1, -1, -1)])
    bm.faces.new([rings[-1][k] for k in range(nr)])


def catmull(cps, n):
    """制御点を通る滑らかな折れ線（Catmull-Rom）。焼き物の断面は単調なべき乗では出ない"""
    P = [cps[0]] + list(cps) + [cps[-1]]
    out = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        for k in range(n):
            u = k / n
            u2, u3 = u * u, u * u * u
            out.append(tuple(
                0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * u
                       + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * u2
                       + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * u3) for d in (0, 1)))
    out.append(cps[-1])
    return out


# 🔴 3周目まで r=R·sin^0.75 の単調な椀で組んだが、絵は**中華鍋**に読めた（脚と耳を足しても消えない）。
#    焼き物の香炉は「胴が張って、口でいったん窄まり、縁で外へ返る」。単調な曲線ではこの返しが作れない。
BOWL_OUT = ((0.000, -0.382), (0.194, -0.372), (0.353, -0.306), (0.456, -0.171),
            (0.477, -0.080), (0.458, -0.021), (0.470, 0.007))
BOWL_IN = ((0.000, -0.327), (0.171, -0.319), (0.317, -0.262), (0.419, -0.139),
           (0.440, -0.066), (0.424, -0.016), (0.433, 0.007))


def bowl_profile():
    """香炉の碗。外面（底の極→縁）→縁を渡る→内面（縁→内底の極）"""
    out = catmull(BOWL_OUT, 9)
    inn = catmull(BOWL_IN, 9)
    rim = [(0.470, RIM_Z), (0.451, RIM_Z + 0.003), (0.436, RIM_Z)]
    return out + rim + inn[::-1]


def case_profile():
    """香合の身。丸角の平たい筒＋内側の窪み"""
    n = 12
    out = [(0.0, -H_G)]
    for i in range(n + 1):
        a = -0.5 * math.pi + 0.5 * math.pi * i / n
        out.append((R_G - C_G + C_G * math.cos(a), -H_G + C_G + C_G * math.sin(a)))
    out.append((R_G, -0.010))
    rim = [(R_G, 0.0), (R_G - T_G, 0.0)]
    inn = []
    Ri, Hi, ci = R_G - T_G, H_G - B_G, 0.018
    for i in range(n + 1):
        a = -0.5 * math.pi * i / n
        inn.append((Ri - ci + ci * math.cos(a), -Hi + ci + ci * math.sin(a)))
    inn.append((0.0, -Hi))
    return out + rim + inn


def lid_profile():
    """香合の蓋。低い甲盛りの円盤"""
    n = 26
    out = []
    for i in range(n + 1):
        a = 0.5 * math.pi * i / n
        out.append((R_L * math.sin(a) ** 0.85, H_L * max(0.0, math.cos(a)) ** 1.6))
    out += [(R_L, -T_L * 0.45), (R_L - 0.010, -T_L)]
    inn = []
    for i in range(1, n + 1):
        a = 0.5 * math.pi * (1 - i / n)
        rr = (R_L - 0.026) * math.sin(a) ** 0.85
        inn.append((rr, -T_L - 0.004 - 0.018 * max(0.0, math.cos(a)) ** 1.6))
    return out + [(R_L - 0.026, -T_L - 0.004)] + inn


def build_koro():
    bm = bmesh.new()
    add_revolve(bm, bowl_profile())
    for az in LEG_AZ:
        pts = []
        for i in range(9):
            u = i / 8
            r = LEG_R0 + (LEG_R1 - LEG_R0) * u
            z = LEG_Z0 + (LEG_Z1 - LEG_Z0) * u
            pts.append((r * math.cos(az), r * math.sin(az), z))
        rad = [LEG_RAD[0] + (LEG_RAD[1] - LEG_RAD[0]) * (i / 8) ** 0.7 for i in range(9)]
        rad[-1] = LEG_RAD[2]
        add_tube(bm, pts, rad, nr=14)
    for az in EAR_AZ:
        pts = []
        for i in range(15):
            u = i / 14
            # 3点を通る二次ベジエ
            p0, p1, p2 = EAR_P
            rr = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
            zz = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
            pts.append((rr * math.cos(az), rr * math.sin(az), zz))
        add_tube(bm, pts, [EAR_RAD] * 15, nr=12)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("koro")
    bm.to_mesh(me); bm.free()
    return me


def knob_profile():
    """蓋の摘み。これが無いと蓋は「もう一つの碗」に読める（1周目の失敗）"""
    n = 16
    out = []
    for i in range(n + 1):
        a = 0.5 * math.pi * i / n
        out.append((0.056 * math.sin(a) ** 0.9, H_L + 0.030 * max(0.0, math.cos(a)) ** 1.3 - 0.004))
    out += [(0.050, H_L - 0.020), (0.036, H_L - 0.030), (0.0, H_L - 0.032)]
    return out


def build_case(profile, name):
    bm = bmesh.new()
    add_revolve(bm, profile)
    if name == "futa":
        add_revolve(bm, knob_profile(), nseg=48)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def build_dome(R, H, z0, gl, hu, name, na=120, nb=40):
    """発光ドーム。UV の X に E を焼く。縁（E≈0）は必ず器の壁の下（#82②／#76③）"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    cen = bm.verts.new((0.0, 0.0, dome_z(0.0, R, H, z0)))
    rings, evs = [], []
    for ib in range(1, nb + 1):
        r = R * (ib / nb) ** 0.9
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / na),
                                    r * math.sin(2 * math.pi * k / na),
                                    dome_z(r, R, H, z0))) for k in range(na)])
        evs.append(e_of(r, gl, hu))
    e0 = e_of(0.0, gl, hu)

    def setuv(f, m):
        for lp in f.loops:
            lp[uvl].uv = (m[lp.vert], 0.5)

    for k in range(na):
        k2 = (k + 1) % na
        f = bm.faces.new((cen, rings[0][k], rings[0][k2]))
        setuv(f, {cen: e0, rings[0][k]: evs[0], rings[0][k2]: evs[0]})
    for ib in range(nb - 1):
        for k in range(na):
            k2 = (k + 1) % na
            f = bm.faces.new((rings[ib][k], rings[ib][k2],
                              rings[ib + 1][k2], rings[ib + 1][k]))
            setuv(f, {rings[ib][k]: evs[ib], rings[ib][k2]: evs[ib],
                      rings[ib + 1][k2]: evs[ib + 1], rings[ib + 1][k]: evs[ib + 1]})
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=0.9):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    ob.rotation_mode = 'ZYX'          # #76⑦ 傾けたまま自軸で回す
    return ob


koro = link(build_koro(), "koro", mat_body)
hai = link(build_dome(R_M, H_M, Z_M, GL_M, HOT_U_M, "hai"), "hai", mat_glow, smooth=1.2)
kogo = link(build_case(case_profile(), "kogo"), "kogo", mat_body)
futa = link(build_case(lid_profile(), "futa"), "futa", mat_body)
kou = link(build_dome(R_BED, H_BED, Z_BED, GL_B, HOT_U_B, "kou"), "kou", mat_glow, smooth=1.2)

parts = [koro, hai, kogo, futa, kou]

# --- 黒の肌は実ジオメトリ（#52）。器体だけ。脚・耳・発光体には掛けない（#77⑩／掟1）
tex_relief = bpy.data.textures.new("relief_touki", 'CLOUDS')
tex_relief.noise_scale = BLACK_RECIPES[RECIPE]["dsize"]
for ob in (kogo, futa):
    sub = ob.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 1
    d = ob.modifiers.new("disp", 'DISPLACE')
    d.texture = tex_relief; d.strength = BLACK_RECIPES[RECIPE]["disp"]; d.mid_level = 0.5
d = koro.modifiers.new("disp", 'DISPLACE')       # 碗は分割が既に細かい（96×92）
d.texture = tex_relief; d.strength = BLACK_RECIPES[RECIPE]["disp"]; d.mid_level = 0.5


# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
def kogo_lid_loc(t):
    """蓋は身の座標系で横へ滑る（傾いた面の中で滑る）"""
    v = rot_zyx((slide(t), 0.0, 0.0), TILT_G, yaw_kogo(t))
    return (KOGO_C[0] + v[0], KOGO_C[1] + v[1], KOGO_C[2] + bob_kogo(t) + v[2])


FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    ck = (KORO_C[0], KORO_C[1], KORO_C[2] + bob_koro(t))
    rk = (tilt_koro(t), 0.0, yaw_koro(t))
    cg = (KOGO_C[0], KOGO_C[1], KOGO_C[2] + bob_kogo(t))
    rg = (TILT_G, 0.0, yaw_kogo(t))
    for ob, loc, rot in ((koro, ck, rk), (hai, ck, rk), (kogo, cg, rg),
                         (futa, kogo_lid_loc(t), rg), (kou, cg, rg)):
        ob.location = loc
        ob.rotation_euler = rot
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor_obj = bpy.context.active_object
floor_obj.name = "floor"
floor_obj.data.materials.append(mat_floor)


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


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 1.02), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.85), "logo"),
        caption("MIDDLE STUDY 073 — SORADAKI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, 1.95)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：対の作は2つの塊のあいだが素通し＝面光源がそこに写る
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。器の下、床すれすれに置いて帯（画面62〜80%）へ届かせる
for sx, sy, sz, w in ((-0.55, 3.4, 0.26, LIME_W), (0.35, 6.2, 0.26, LIME_W),
                      (1.15, 10.0, 0.26, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = w
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
cam.data.dof.focus_distance = math.hypot(8.3, 0.5 * (KORO_C[2] + KOGO_C[2]) - LOOK_Z)
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは**全ジオメトリ生成後**に置く（#56②）。床を受光から外す
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

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME)

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    GW, GH = 200, 250
    grids = {"koro": set(), "kogo": set()}
    allx, ally = [], []
    for ob in parts:
        ev = ob.evaluated_get(dg)
        key = "koro" if ob.name in ("koro", "hai") else "kogo"
        xs, ys = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
            gx, gy = int(c.x * GW), int(c.y * GH)
            if 0 <= gx < GW and 0 <= gy < GH:
                grids[key].add((gx, gy))
        allx += xs; ally += ys
        print(">> %-5s x %.3f..%.3f  y %.3f..%.3f" % (ob.name, min(xs), max(xs),
                                                      min(ys), max(ys)))
    x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
    print(">> 全体 bbox x %.3f..%.3f y %.3f..%.3f → 長辺 %.1f%%（帯 55〜65）"
          % (x0, x1, y0, y1, max(x1 - x0, y1 - y0) * 100))
    print(">> 枠まで 左%.3f 右%.3f 上%.3f 下%.3f（すべて正なら edge=0）"
          % (x0, 1 - x1, 1 - y1, y0))
    a, b = len(grids["koro"]), len(grids["kogo"])
    print(">> 🔴 投影の占有 香炉%d 香合%d → big_share %.0f%%（対は72%%以下）"
          % (a, b, 100 * max(a, b) / (a + b)))
    cx = sum(allx) / len(allx) * 100
    print(">> 重心x ≒ %.1f%%" % cx)
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))
    print(">> 面数 %d" % sum(len(o.evaluated_get(dg).data.polygons)
                            for o in bpy.data.objects if o.type == 'MESH'))

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_073.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("hi_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    hai.data.materials[0] = m_em
    kou.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
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
