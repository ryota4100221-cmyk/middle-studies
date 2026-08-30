# =============================================================
# MIDDLE STUDY 066 — SHIN（芯 / the hollow wick of a Japanese candle）
#
# 黒い和蝋燭が一本、燃え尽きるまぎわで宙にある。大きすぎて、枠に収まらない。
# 左右は切れていて、この蝋燭がどこまで太いのか、こちらからは見えない。
# 見えるのは**まんなかだけ**だ。溶けた口の底に、ライム #A5E02E の蝋が溜まっていて、
# その中心に、焦げた芯が一本だけ立っている。
#
# **和蝋燭の芯は、空洞だ。** 和紙を巻いた筒に藺草（いぐさ）の髄を通しただけの、中の無い筒。
# 中が空だから下から空気が昇り、だから炎が大きくなる。**真ん中に何も無いことが、燃える理由になっている。**
# そして蝋が尽きても、芯だけは最後まで立っている。
# 蝋は流れて、縁のひくいところ（注ぎ口）からこぼれ、外側を涙になって垂れた。
# 蝋燭が一周まわると、その注ぎ口はこちらを向き、また背を向ける。
# **光の量を変えているのは光ではない。こちらへ開いているか、閉じているか、それだけだ。**
#
# 🔴 光の型＝**芯**（#53：65作で7作。中心の小さな塊・周りは黒）
# 🔴 構図の型＝**寄り**（#57：65作で3作。65作中51作が「全身」）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／065 に続く9例目）
#    今日選べたのは 光＝内包／稜線／芯 × 構図＝全身／寄り／群。
#    ・`measure.py --trend` が **halo 🔴 36%**（基準期36,032→直近5作13,079）を出している。
#      #51④ の処方は「光の**出し方**を変える＝面で出す・透過させる・内側から出す」。
#      **寄りは、光そのものを大きくせずに halo を戻せる唯一の構図**——同じ光でも、
#      寄れば画面に占める割合が上がる。だから今日は「光を強くする」ではなく「近づく」で解く。
#    ・**群は不成立**（#71①：共有光源を宙に置くと全部が1塊に繋がる／個体内に閉じ込めると光が痩せる＝
#      halo を戻したい今日の目的と正面から矛盾する）。
#    ・**稜線×寄りも不成立**：#67⑤ の系（縁が画面に無いものは縁で光れない）。
#      寄りは輪郭を枠の外へ出す構図なので、輪郭に載せる光とは食い合う。
#    ・→ 残るは **内包×寄り** と **芯×寄り**。両方成立するので、**halo で決めた**：
#      内包は「殻の隙間から漏れる光」＝開口の面積で頭打ちになる（047/019 の halo は 8〜14k）。
#      芯は塊なので、**寄れば寄るほど画面上で大きくなる**。→ **芯×寄り**。
#
# 🔴 #67⑦「大きくすれば寄りになる」ではない。寄りは**全体を見せないこと**。
#    ここでは連立で解いた：①胴の直径が実効フレーム幅を **14%** 上回る（左右が切れる）
#    ②いちばん下の縁がキャプション帯を割らない ③芯の先が上端に触れない（＝光が切れない）。
#    → TILT/OBJ_Z/R_T はこの3本でほぼ一意に決まる（--probe-only が数字で出す）。
#
# 🔴 機構＝**注ぎ口が一周する**（整数周期・厳密に閉じる）。発光の値は1フレームも動かさない（#69②／#70④）。
#    変わるのは「溶けた縁が、光のどこを隠しているか」だけ＝#40⑥ は幾何で積分する（--probe-only）。
#    自転は**局所 Z 軸**まわり（rotation_mode='ZYX' で M = Rx(TILT)·Rz(spin)＝傾けたまま自分の軸で回る）。
#    🔴 局所 Z 軸上の点は自転で動かない → **炉内のライム灯を軸上に置けば、灯は追従不要**（世界固定でよい）。
#
# 造形＝碇型（いかりがた）の和蝋燭が燃え落ちた残り。上へ向かって太る胴、溶けて不揃いになった縁、
#    縁のいちばん低いところ（注ぎ口）と、そこから外を垂れる蝋涙8条。boolean 不使用・全て回転体の変形で組む。
#    黒の質感は MATERIALS.md の **`urushi`（漆）**——溶けて固まり直した蝋は「深く沈んだ艶」そのもの。
#    🔴 urushi は DISPLACE を持たない（#52 の表）。肌は**蝋涙の実ジオメトリ**が作る。
#    🔴 urushi は鏡面 0.34 ＝ #47 の映り込み事故と隣り合わせなので hero を必ず目視する。
#
# 【ドメイン】灯火・和蝋燭（シリーズ未踏）。直近10作＝神域・鳥居／鏡・柄鏡／手仕事・和鋏／製紙・紙漉き／
#    古墳・埴輪／炊事・竈／証・割符／空・凧／運搬・車輪／盤上遊戯 と別。
#    004 ANDON【行灯】と 031 TOURO【石灯籠】は「光を囲う器」で、主題は囲い。
#    こちらは**燃える当のもの**で、主題は「芯が空洞であること」。物も主題も別。
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
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 95.0                      # #58③：随伴のライム光源（発光体の外）

# --- 置き方（#67⑦ の連立を解いた値）------------------------------
TILT = math.radians(18.0)           # 上をカメラ側へ倒す＝水平カメラで「溶けた井戸の中」が見える唯一の手
OBJ_X, OBJ_Y, OBJ_Z = AIM_X, 0.30, 1.62

# --- 蝋燭（燃え落ちかけの太い和蝋燭。実寸は world 単位）-----------
# 🔴🔴 1〜2周目はどちらも「黒い鉢」になった。**器と蝋燭を分けるのは、肉厚の比だった。**
#    1周目：肉厚 0.34／口径比 0.92 → 焼き物の椀。2周目：肉厚を 0.13 まで薄くしたら**紙の器**になった。
#    ——薄い縁は、それが何の縁でも「容器の口」に読める（#33 の型）。
#    直したのは逆側：**肉を厚くする**（0.13→0.62）。燃えている蝋燭の上は、
#    広い蝋の平らな面（溶けかけ）の**まんなかに小さな井戸が空いている**だけで、器の口ではない。
#    ＝口径比 0.61 まで落とし、外周は「縁」ではなく「面」にした。
H       = 1.35        # 胴の高さ（外縁の公称位置）
R_B     = 1.42        # 底の半径（碇型＝上へ向かってわずかに太る。ほぼ円筒）
R_T     = 1.60        # 外縁の半径＝実効フレーム幅を超える（寄り）
FLARE_P = 1.00
D_BOWL  = 0.34        # 井戸の深さ
Z_POOL  = H - D_BOWL  # 蝋だまりの高さ
R_CRA0  = 0.98        # 井戸の口の半径（外縁 1.60 の 0.61＝**まんなかの小さな穴**）
R_POOL0 = 0.60        # 蝋だまりの公称半径（実際は不揃い＝rpool）
SAG_E   = 0.30        # 注ぎ口で外縁が下がる量
SAG_R   = 0.14        # 注ぎ口で井戸の口が下がる量
NOTCH_W = 1.05        # 注ぎ口の角度半幅
PHI_NOTCH = math.pi / 2    # 局所方位。spin=π（t=0.5）でカメラを向く＝hero
WOB     = 0.055       # 溶けた面の不揃い
LAYER_A, LAYER_P = 0.004, 0.22    # 生掛けの段（2周目は 0.011 で**波板のバケツ**になった）
R_WO, R_WI = 0.095, 0.062   # 芯（和紙の筒）の外半径・内半径＝**中は空洞**
WICK_H  = 0.86        # 蝋だまりから上へ出ている芯の長さ

# 蝋涙（注ぎ口の下に濃く、他にも数条）: (注ぎ口からの角度, 太さ, 角度幅, 垂れの長さ)
DRIPS = [(0.00, 0.200, 0.19, 1.30), (0.28, 0.140, 0.15, 1.02), (-0.32, 0.165, 0.16, 1.16),
         (0.60, 0.090, 0.13, 0.62), (-0.68, 0.078, 0.12, 0.52), (2.30, 0.100, 0.14, 0.70),
         (-2.05, 0.086, 0.13, 0.58), (3.05, 0.070, 0.12, 0.44)]

# --- 光（芯と、その足もとの蝋だまりだけ）-------------------------
ES_CORE = 6.0
POOL_E  = 1.00        # 蝋だまりの芯もとの明るさ（縁で厳密に 0＝#26／#49①）
POOL_P  = 0.85
WHITE_FROM, WHITE_TO = 0.30, 0.58   # 芯を白へ抜く＝halo はこの帯でしか出ない（#70④）
K_MIX   = 9.0         # E→0 側は黒い蝋そのものへ戻す（発光板の縁を作らない）
LIME_IN_W = 110.0      # 口の中のライム灯（局所 Z 軸上＝自転で動かない）

NPHI, NO, NT, NI = 168, 44, 12, 12
WALL_E  = 0.12
# 🔴 7周目：胴の下半分が**のっぺりした黒い塊**だった（画面の45%）。黒は光を持たないと形が出ない
#    ——蝋涙は silhouette にしか出ないのに、その左右は寄りで枠の外にある（#68① の逆）。
#    足したのは装飾ではなく**物理**：注ぎ口からこぼれた蝋は、まだ熱いあいだ光ったまま胴を垂れる。
# 8周目：幅 0.30rad で張ったら**緑のエプロン**になった（ライム面積 13.8%）。樋は細い。
#   (注ぎ口からの角度, 付け根の角度半幅, 末端の角度半幅, 付け根の明るさ, 垂れの長さ)
RUNNELS = [(0.00, 0.072, 0.026, 0.95, 0.82, 0.085, 3.4),
           (-0.34, 0.044, 0.018, 0.58, 0.54, -0.055, 4.8)]
#   末尾2つ＝蛇行の振幅と周期。9周目は直線で張って**ネオンの帯**になった。垂れる蝋は真っ直ぐ落ちない
RUN_OFF = 0.042       # 面から浮かせる量（8周目は 0.010 で胴の起伏が突き抜けた）
NRU, NRW = 72, 15        # 🔴 3周目：内壁まで光らせたら「緑のペンキを張った桶」になった。
#                       光は蝋だまり（＝芯のまわり）だけ。内壁は黒のまま、口のライム灯に舐めさせる
STILL_FRAME = 61      # t=0.5 ＝ 注ぎ口がこちらを向く唯一の瞬間


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def bump(d, w):
    d = abs(d)
    return math.cos(math.pi * d / (2.0 * w)) ** 2 if d < w else 0.0


def base_profile(u):
    u = max(0.0, min(1.0, u))
    return R_B + (R_T - R_B) * u ** FLARE_P


def h_edge(phi):
    """外縁の高さ。注ぎ口でいちばん低い（そこから蝋がこぼれた）＋溶けた不揃い"""
    return (H - 0.02 - SAG_E * bump(wrap(phi - PHI_NOTCH), NOTCH_W)
            + WOB * (math.sin(3.0 * phi + 0.7) + 0.55 * math.sin(5.0 * phi + 2.3)) / 1.55)


def z_rim(phi):
    """井戸の口の高さ。注ぎ口では蝋だまりとほぼ同じ高さまで下がる＝そこが樋になる"""
    return max(Z_POOL + 0.10,
               H - 0.10 - SAG_R * bump(wrap(phi - PHI_NOTCH), NOTCH_W)
               + 0.6 * WOB * math.sin(4.0 * phi + 1.9)
               + 0.35 * WOB * math.sin(7.0 * phi + 0.4))


def r_cr(phi):
    return R_CRA0 * (1.0 + 0.10 * math.sin(3.0 * phi + 0.5))


def rpool(phi):
    """蝋だまりの縁。**真円にしない**——溶け残りが縁を作るので不揃いで、注ぎ口の側へ広がる"""
    return R_POOL0 * (1.0 + 0.14 * math.sin(3.0 * phi + 1.1)
                      + 0.08 * math.sin(5.0 * phi + 0.35)
                      + 0.16 * bump(wrap(phi - PHI_NOTCH), 1.0))


def r_out(z, phi):
    """外側の半径。ほぼ円筒の胴＋生掛けの段＋蝋涙"""
    u = z / H
    r = (base_profile(u)
         + LAYER_A * (0.5 + 0.5 * math.cos(2.0 * math.pi * z / LAYER_P))
         + (0.026 * math.sin(4.0 * phi + 1.1) + 0.014 * math.sin(7.0 * phi + 3.0))
         * (0.35 + 0.65 * min(1.0, u)))
    for dphi, amp, w, L in DRIPS:
        d = wrap(phi - (PHI_NOTCH + dphi))
        if abs(d) > 3.0 * w:
            continue
        q = (h_edge(PHI_NOTCH + dphi) - z) / L
        if q < 0.0 or q > 1.0:
            continue
        prof = (1.0 - q) ** 0.55 * min(1.0, 0.30 + q / 0.12)
        r += amp * math.exp(-(d / w) ** 2) * prof
    return r


def r_edge(phi):
    return r_out(h_edge(phi), phi)


def top_z(t, phi):
    """広い蝋の面（外縁から井戸の口へ、なだらかに落ちる皿）。t=0 が井戸の口・t=1 が外縁"""
    zr, he = z_rim(phi), h_edge(phi)
    return zr + (he - zr) * t ** 0.8


def top_r(t, phi):
    return r_cr(phi) + (r_edge(phi) - r_cr(phi)) * t


def crater_r(s, phi):
    """井戸の内壁。s=0 が蝋だまり・s=1 が口"""
    rp = rpool(phi)
    return rp + (r_cr(phi) - rp) * s ** 0.8


def surface_z(rho, phi):
    """半径 rho における蝋の上面の高さ（遮蔽の判定に使う）"""
    rp, rc, re = rpool(phi), r_cr(phi), r_edge(phi)
    if rho <= rp:
        return Z_POOL
    if rho <= rc:
        s = ((rho - rp) / (rc - rp)) ** (1.0 / 0.8)
        return Z_POOL + (z_rim(phi) - Z_POOL) * s
    if rho <= re:
        return top_z((rho - rc) / (re - rc), phi)
    return -9.0


def pool_e(r, phi):
    """蝋だまりの発光。芯もとで最大、**不揃いな縁で厳密に 0**（縁が存在しない光＝#26／#49①）"""
    rp = rpool(phi)
    if r >= rp:
        return 0.0
    s = (rp - r) / (rp - R_WO)
    return POOL_E * max(0.0, min(1.0, s)) ** POOL_P


def wall_e(s):
    """井戸の内壁の発光。蝋だまり側から立ち上がり、**口で厳密に 0**"""
    return WALL_E * max(0.0, 1.0 - s) ** 1.6


# --- 遮蔽（#40⑥ を幾何で積分する）--------------------------------
# 🔴 発光の値は一切入っていない。変わるのは「溶けた縁が光のどこを隠しているか」だけ。
#    蝋だまりの各点から カメラへ向かう線を局所座標で追い、縁を越えられるかを見る。
def _rot_t(v, spin):
    """world ベクトル v を局所へ戻す（R = Rx(TILT)·Rz(spin) の転置）"""
    ct, st = math.cos(TILT), math.sin(TILT)
    x, y, z = v
    y2, z2 = ct * y + st * z, -st * y + ct * z          # Rx(-TILT)
    cs, ss = math.cos(spin), math.sin(spin)
    return (cs * x + ss * y2, -ss * x + cs * y2, z2)    # Rz(-spin)


def _cam_dir_local(spin):
    ct, st = math.cos(TILT), math.sin(TILT)
    pool_w = (OBJ_X, OBJ_Y - Z_POOL * st, OBJ_Z + Z_POOL * ct)
    d = [CAM_LOC[i] - pool_w[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in d))
    return _rot_t([c / n for c in d], spin)


_SAMP = []
for _i in range(11):
    _fr = (_i + 0.5) / 11.0
    _n = max(6, int(30 * _fr))
    for _j in range(_n):
        _p = 2.0 * math.pi * (_j + 0.5) / _n
        _r = R_WO + (rpool(_p) - R_WO) * _fr
        _SAMP.append((_r * math.cos(_p), _r * math.sin(_p), pool_e(_r, _p) * _r / _n))


def light_visible(t):
    """発光の値は一切入っていない。変わるのは「溶けた蝋が光のどこを隠しているか」だけ"""
    d = _cam_dir_local(2.0 * math.pi * t)
    tot = 0.0
    for x, y, wgt in _SAMP:
        if wgt <= 0.0:
            continue
        ok = True
        for k in range(1, 110):
            s = k * 0.045
            qx, qy, qz = x + d[0] * s, y + d[1] * s, Z_POOL + 0.01 + d[2] * s
            ph = math.atan2(qy, qx)
            rho = math.hypot(qx, qy)
            if rho > r_edge(ph):
                break
            if qz < surface_z(rho, ph):
                ok = False
                break
        if ok:
            tot += wgt
    return tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]
_VS = [light_visible(t) for t in _TS]
_VMAX = max(_VS)

if "--probe-only" in sys.argv:
    ct, st = math.cos(TILT), math.sin(TILT)
    mag = lambda y: 8.3 / (8.3 - y)

    def proj(loc, lz):
        """局所 (x,0,z) を world へ → 画面上の見かけ位置（x, z）"""
        wx, wy, wz = OBJ_X + loc, OBJ_Y - lz * st, OBJ_Z + lz * ct
        m = mag(wy)
        return (AIM_X + (wx - AIM_X) * m, LOOK_Z + (wz - LOOK_Z) * m)

    print("── 066 SHIN 幾何プローブ")
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    b = max(range(N_FRAMES), key=lambda i: _VS[i])
    w = min(range(N_FRAMES), key=lambda i: _VS[i])
    print("   いちばん明るい frame %d（t=%.3f）／暗い frame %d（t=%.3f）  STILL_FRAME=%d"
          % (b + 1, _TS[b], w + 1, _TS[w], STILL_FRAME))
    for nm, t in (("注ぎ口が正面(hero)", 0.5), ("横", 0.25), ("注ぎ口が背", 0.0)):
        print("   %-18s 見える光 %5.1f%%" % (nm, 100 * light_visible(t) / _VMAX))

    rx, rz = proj(r_edge(0.0), h_edge(0.0))
    half = FRAME_W / 2.0
    print("   縁の左右 見かけ半幅 %.3f ／ 実効フレーム半幅 %.3f → **%+.1f%%**（寄り＝正の値）"
          % (rx - AIM_X, half, (rx - AIM_X - half) / half * 100))
    _, low = proj(0.0, 0.0)
    lowz = LOOK_Z + (OBJ_Z - R_B * st - LOOK_Z) * mag(OBJ_Y - R_B * ct)
    _, topz = proj(0.0, Z_POOL + WICK_H)
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * mag(-1.7)
    print("   いちばん下の縁 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (lowz, capz, lowz - capz))
    print("   芯の先 z=%.3f ／ 画面上端 3.71 → 上の余白 %.3f（%.1f%%）"
          % (topz, 3.71 - topz, (3.71 - topz) / FRAME_H * 100))
    print("   長辺（縦）%.1f%% ／ 横は左右が切れるので 100%%  → s_long=100（寄りの条件 78 以上）"
          % ((topz - lowz) / FRAME_H * 100))
    _, pz = proj(0.0, Z_POOL)
    print("   蝋だまりの高さ z=%.3f → 画面の上から %.1f%%" % (pz, (3.71 - pz) / FRAME_H * 100))
    ap = math.pi * (R_POOL0 * 1.1) ** 2 * math.sin(TILT) * 1.9
    print("   蝋だまりの見かけ面積 ≒ %.2f ／ 画面 %.2f → ライム面積 ≒ %.1f%%（帯 0.8〜12）"
          % (ap, FRAME_W * FRAME_H, ap / (FRAME_W * FRAME_H) * 100))
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
# 🔴 1周目は urushi（漆・鏡面0.34）で組み、hero は**黒い焼き物の鉢**になった。
#    溶けて固まり直した蝋は艶ではなく**曇り**なので touki（陶）へ替え、実起伏を乗せる（#52）。
BLACK_RECIPES = {"touki": dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10)}
RECIPE = "touki"


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def black_material(name, recipe):
    m, p = principled(name)
    r = BLACK_RECIPES[recipe]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    return m


mat_body = black_material("rou_touki", RECIPE)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 発光（芯と蝋だまり）----------------------------------
def glow_material(name):
    """E→0 側は**黒い蝋そのもの**へ戻す（＝発光板の縁を作らない・#49①）。
       芯だけ白へ抜く＝halo はこの「白→ライム」の帯でしか出ない（#70④）"""
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
    r = BLACK_RECIPES[RECIPE]
    blk.inputs["Base Color"].default_value = BLACK
    blk.inputs["Roughness"].default_value = r["rough"]
    blk.inputs["Specular IOR Level"].default_value = r["spec"]

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


mat_glow = glow_material("hikari")


# ---------- 造形（bmesh・world 実寸。object.scale / transform_apply 不使用＝#15） ----
def profile(phi):
    """一方位ぶんの断面（r, z）。全方位で点数を揃える＝そのまま格子になる。
       胴 → 広い蝋の面 → 井戸の内壁 → 井戸の底、の4区間"""
    he = h_edge(phi)
    pts = [(r_out(he * j / NO, phi), he * j / NO) for j in range(NO + 1)]
    for j in range(1, NT + 1):                      # 広い面（外縁 → 井戸の口）
        t = 1.0 - j / NT
        pts.append((top_r(t, phi), top_z(t, phi)))
    for j in range(1, NI + 1):                      # 井戸の内壁（口 → 蝋だまり）
        sv = 1.0 - j / NI
        pts.append((crater_r(sv, phi), Z_POOL + (z_rim(phi) - Z_POOL) * sv))
    pts.append((rpool(phi) * 0.55, Z_POOL - 0.018))  # 井戸の底（蝋だまりの下）
    pts.append((R_WO * 0.85, Z_POOL - 0.030))
    return pts


def runnel_mesh():
    """注ぎ口からこぼれて胴を垂れる、まだ熱い蝋。井戸の内壁 → 広い面 → 外壁を面に浮かせて張る。
       **末端も両縁も E=0**＝どこにも塗った縁が無い（#49①）。冷えれば黒い蝋に戻る"""
    bm = bmesh.new()
    ee = {}
    for dphi, w0, w1, e0, rl, mA, mF in RUNNELS:
        rows = []
        for i in range(NRU + 1):
            u = i / NRU
            w = w0 + (w1 - w0) * u
            row = []
            for j in range(NRW):
                lat = -1.0 + 2.0 * j / (NRW - 1)
                phi = (PHI_NOTCH + dphi + mA * math.sin(mF * u) * min(1.0, u / 0.30)
                       + lat * w)
                if u < 0.12:                                   # 井戸の内壁を上る
                    sv = u / 0.12
                    r = crater_r(sv, phi)
                    z = Z_POOL + (z_rim(phi) - Z_POOL) * sv
                elif u < 0.40:                                 # 広い蝋の面を渡る
                    tt = (u - 0.12) / 0.28
                    r, z = top_r(tt, phi), top_z(tt, phi)
                else:                                          # 外壁を垂れる
                    q = (u - 0.40) / 0.60
                    z = h_edge(phi) - rl * q
                    r = r_out(z, phi)
                v = bm.verts.new(((r + RUN_OFF) * math.cos(phi),
                                  (r + RUN_OFF) * math.sin(phi), z))
                ee[v] = e0 * (1.0 - u) ** 2.3 * max(0.0, 1.0 - lat * lat) ** 1.5
                row.append(v)
            rows.append(row)
        for i in range(NRU):
            for j in range(NRW - 1):
                bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = (ee[lp.vert], 0.5)
    me = bpy.data.meshes.new("tare"); bm.to_mesh(me); bm.free()
    return me


def crater_mesh():
    """井戸の内壁の発光面。黒い内壁の 0.008 内側に張る。口で E=0＝黒い蝋へ戻る（#49①）"""
    bm = bmesh.new()
    rings = []
    NS = 26
    for k in range(NPHI):
        phi = 2.0 * math.pi * k / NPHI
        c, sn = math.cos(phi), math.sin(phi)
        row = []
        for j in range(NS + 1):
            sv = j / NS
            r = crater_r(sv, phi) - 0.008
            z = Z_POOL + (z_rim(phi) - Z_POOL) * sv
            row.append(bm.verts.new((r * c, r * sn, z)))
        rings.append(row)
    for k in range(NPHI):
        k2 = (k + 1) % NPHI
        for j in range(NS):
            bm.faces.new((rings[k][j], rings[k2][j], rings[k2][j + 1], rings[k][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            co = lp.vert.co
            ph = math.atan2(co.y, co.x)
            zr = z_rim(ph)
            sv = 0.0 if zr - Z_POOL < 1e-6 else (co.z - Z_POOL) / (zr - Z_POOL)
            lp[uvl].uv = (wall_e(max(0.0, min(1.0, sv))), 0.5)
    me = bpy.data.meshes.new("ido"); bm.to_mesh(me); bm.free()
    return me


def body_mesh():
    bm = bmesh.new()
    rings = []
    for k in range(NPHI):
        phi = 2.0 * math.pi * k / NPHI
        c, s = math.cos(phi), math.sin(phi)
        rings.append([bm.verts.new((r * c, r * s, z)) for r, z in profile(phi)])
    npt = len(rings[0])
    for k in range(NPHI):
        k2 = (k + 1) % NPHI
        for j in range(npt - 1):
            bm.faces.new((rings[k][j], rings[k2][j], rings[k2][j + 1], rings[k][j + 1]))
    bot = bm.verts.new((0.0, 0.0, -0.012))
    top = bm.verts.new((0.0, 0.0, Z_POOL - 0.042))
    for k in range(NPHI):
        k2 = (k + 1) % NPHI
        bm.faces.new((bot, rings[k2][0], rings[k][0]))
        bm.faces.new((top, rings[k][npt - 1], rings[k2][npt - 1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("rousoku"); bm.to_mesh(me); bm.free()
    return me


def pool_mesh():
    """蝋だまり＝芯の足もとから不揃いな縁へ落ちる面。E を UV 'grad' の U に焼く（#34/#39）"""
    NR, NA = 44, 168
    bm = bmesh.new()
    ctr = bm.verts.new((0.0, 0.0, Z_POOL + 0.006))
    rings = []
    for j in range(1, NR + 1):
        f = j / NR
        row = []
        for k in range(NA):
            ph = 2.0 * math.pi * k / NA
            r = R_WO * 0.90 + (rpool(ph) - R_WO * 0.90) * f
            row.append(bm.verts.new((r * math.cos(ph), r * math.sin(ph),
                                     Z_POOL + 0.006 - 0.020 * f ** 2)))
        rings.append(row)
    for k in range(NA):
        k2 = (k + 1) % NA
        bm.faces.new((ctr, rings[0][k], rings[0][k2]))
    for j in range(NR - 1):
        for k in range(NA):
            k2 = (k + 1) % NA
            bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (pool_e(math.hypot(co.x, co.y), math.atan2(co.y, co.x)), 0.5)
    me = bpy.data.meshes.new("rou_tamari"); bm.to_mesh(me); bm.free()
    return me


ZW0, ZW1 = Z_POOL - 0.060, Z_POOL + WICK_H
BEND = 0.105          # 焦げた芯は真っ直ぐ立たない。hero では画面の右へ反る


def wick_axis(sv):
    """芯の軸。s∈[0,1] で反る（局所方位 PHI_NOTCH+π/2 の向き＝hero で画面右）"""
    a = PHI_NOTCH + math.pi / 2.0
    d = BEND * sv ** 1.8
    return (d * math.cos(a), d * math.sin(a), ZW0 + (ZW1 - ZW0) * sv)


def wick_top(th):
    """焼けた口は平らに切れない"""
    return 0.030 * math.sin(3.0 * th + 1.2) + 0.018 * math.sin(5.0 * th + 0.3)


def wick_meshes():
    """芯＝和紙を巻いた筒。**中は空洞**。外は焦げた黒、内側と口だけが光る"""
    NA, NJ = 64, 26
    rr = lambda r, sv: r * (1.0 - 0.30 * sv ** 1.3)      # 焦げるほど細る
    bmB, bmG = bmesh.new(), bmesh.new()
    ob, ib = [], []
    for j in range(NJ + 1):
        sv = j / NJ
        ax, ay, az = wick_axis(sv)
        rowB, rowG = [], []
        for k in range(NA):
            th = 2.0 * math.pi * k / NA
            dz = wick_top(th) * sv ** 3
            rowB.append(bmB.verts.new((ax + rr(R_WO, sv) * math.cos(th),
                                       ay + rr(R_WO, sv) * math.sin(th), az + dz)))
            rowG.append(bmG.verts.new((ax + rr(R_WI, sv) * math.cos(th),
                                       ay + rr(R_WI, sv) * math.sin(th), az + dz)))
        ob.append(rowB); ib.append(rowG)
    for j in range(NJ):
        for k in range(NA):
            k2 = (k + 1) % NA
            bmB.faces.new((ob[j][k], ob[j][k2], ob[j + 1][k2], ob[j + 1][k]))
            bmG.faces.new((ib[j][k], ib[j][k2], ib[j + 1][k2], ib[j + 1][k]))
    cb = bmB.verts.new((0.0, 0.0, ZW0))                     # 外筒の底（閉じる）
    for k in range(NA):
        bmB.faces.new((cb, ob[0][(k + 1) % NA], ob[0][k]))
    # 口の環（内→外へ E が落ちる。外縁で 0＝縁を作らない）
    ax, ay, az = wick_axis(1.0)
    rim_out = []
    for k in range(NA):
        th = 2.0 * math.pi * k / NA
        rim_out.append(bmG.verts.new((ax + rr(R_WO, 1.0) * math.cos(th),
                                      ay + rr(R_WO, 1.0) * math.sin(th),
                                      az + wick_top(th))))
    for k in range(NA):
        k2 = (k + 1) % NA
        bmG.faces.new((ib[NJ][k], ib[NJ][k2], rim_out[k2], rim_out[k]))
    cg = bmG.verts.new((0.0, 0.0, ZW0 + 0.010))             # 筒の底（内側から昇ってくる光）
    for k in range(NA):
        bmG.faces.new((cg, ib[0][k], ib[0][(k + 1) % NA]))
    for bm in (bmB, bmG):
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bmG.loops.layers.uv.new("grad")
    zt = wick_axis(1.0)[2]
    for f in bmG.faces:
        for lp in f.loops:
            co = lp.vert.co
            sv = max(0.0, min(1.0, (co.z - ZW0) / (zt - ZW0)))
            th = math.atan2(co.y - wick_axis(sv)[1], co.x - wick_axis(sv)[0])
            rr_ = math.hypot(co.x - wick_axis(sv)[0], co.y - wick_axis(sv)[1])
            if sv > 0.985 and rr_ > rr(R_WI, 1.0) * 1.001:                   # 口の環
                q = (rr_ - rr(R_WI, 1.0)) / max(1e-6, rr(R_WO, 1.0) - rr(R_WI, 1.0))
                e = 0.95 * (1.0 - max(0.0, min(1.0, q))) ** 1.2
            else:                                                            # 内壁・筒の底
                e = 0.50 + 0.50 * sv ** 1.4
            lp[uvl].uv = (e, 0.5)
    meB = bpy.data.meshes.new("shin_soto"); bmB.to_mesh(meB); bmB.free()
    meG = bpy.data.meshes.new("shin_naka"); bmG.to_mesh(meG); bmG.free()
    return meB, meG


def link(me, name, mat, smooth=0.62):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    ob.location = (OBJ_X, OBJ_Y, OBJ_Z)
    ob.rotation_mode = 'ZYX'          # 🔴 M = Rx(TILT)·Rz(spin)＝傾けたまま自分の軸で回る
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def add_relief(objs, recipe):
    """黒の肌は実ジオメトリで作る（Bump は黒では見えない＝#52）。造形が済んだ最後に呼ぶ。
       🔴 SUBSURF は掛けない（#52 のコードは Catmull-Clark＝薄い縁が丸まって消える）。
       密度は NPHI×NO の格子で作ってある。"""
    r = BLACK_RECIPES[recipe]
    tex = bpy.data.textures.new("relief_" + recipe, 'CLOUDS')
    tex.noise_scale = r["dsize"]
    for o in objs:
        d = o.modifiers.new("disp", 'DISPLACE')
        d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5


meB, meG = wick_meshes()
parts = [link(body_mesh(), "rousoku", mat_body),
         link(crater_mesh(), "ido", mat_glow),
         link(runnel_mesh(), "tare", mat_glow),
         link(pool_mesh(), "tamari", mat_glow),
         link(meB, "shin_soto", mat_body),
         link(meG, "shin_naka", mat_glow)]

add_relief([parts[0], parts[4]], RECIPE)        # 🔴 発光体には掛けない（#52 の掟1）

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    for ob in parts:
        ob.rotation_euler = (TILT, 0.0, 2.0 * math.pi * i / N_FRAMES)
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
        caption("MIDDLE STUDY 066 — SHIN", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, OBJ_Z + 0.80)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：上に大きく空きがある構図＝面光源が素通しで写る

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③/#67⑥：**奥**（画面62〜80%の帯に届く位置）へ
limelamps = []
for sx, sy, sz, w in ((-0.85, 12.0, 0.30, LIME_W), (0.30, 24.0, 0.30, LIME_W),
                      (1.60, 38.0, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = w
    lp.data.shadow_soft_size = 2.60
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0
    limelamps.append(lp)

# 🔴 口の中のライム灯。**局所 Z 軸の上**に置くので、自転しても動かない（世界固定でよい）。
#    内壁を舐めて注ぎ口からこぼれる＝「光っている物」でなく「光源」になる（#58）
_ct, _st = math.cos(TILT), math.sin(TILT)
_zc = Z_POOL + 0.28
bpy.ops.object.light_add(type='POINT',
                         location=(OBJ_X, OBJ_Y - _zc * _st, OBJ_Z + _zc * _ct))
lamp_in = bpy.context.active_object
lamp_in.name = "lime_kuchi"
lamp_in.data.energy = LIME_IN_W
lamp_in.data.shadow_soft_size = 0.22
lamp_in.data.color = LIME[:3]
lamp_in.visible_camera = False

# 黒の上にだけ「暗いライム」が作れる（#14 の std）。外側の蝋涙の稜線を舐める灯
rimlamps = []
for sx, sy, sz, w in ((-2.05, 0.9, OBJ_Z + 0.95, 190.0), (2.05, 0.9, OBJ_Z + 0.95, 190.0)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "rim_%+0.2f" % sx
    lp.data.energy = w
    lp.data.shadow_soft_size = 0.80
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    rimlamps.append(lp)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 8.30
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは**全ジオメトリ生成後**に置く（#56②）。床だけ受光から外す
lit = bpy.data.collections.new("lit_by_back")
bpy.context.scene.collection.children.link(lit)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not floor_obj:
        lit.objects.link(o)
back.light_linking.receiver_collection = lit

# 🔴 #63③：ライムの随伴光源は「誰から外すか」で書く（外すものを最小に）
lit_by_rim = bpy.data.collections.new("lit_by_rim")
bpy.context.scene.collection.children.link(lit_by_rim)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not floor_obj:
        lit_by_rim.objects.link(o)
for lp in rimlamps + [lamp_in]:
    lp.light_linking.receiver_collection = lit_by_rim

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
    print(">> #40(6) 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, ys = [], []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o is floor_obj:
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 蝋燭の投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%（下20%%は測定外）"
              % (tx.name, (1 - c.y) * 100))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_066.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    for ob in parts:
        if ob.data.materials[0] is mat_glow:
            ob.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True,
                                  export_morph_animation=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
