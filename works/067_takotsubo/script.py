# =============================================================
# MIDDLE STUDY 067 — TAKOTSUBO（蛸壺 / an octopus pot）
#
# 黒い蛸壺が、いくつも宙にある。素焼きの、腹のふくらんだ壺だ。
# 大きいのも小さいのもあって、ひとつは割れている。
# 口はこちらを向いていて、その奥に ライム #A5E02E の光が溜まっている。
# **口より、中のほうが広い。**だから外からは、光の全部は見えない。
#
# **蛸壺には、餌を入れない。返しも仕掛けも無い。**
# あるのは、暗くて狭い真ん中だけだ。それでも蛸は、自分から入る。
# **空けておくことが、いちばん強い誘いになる。**
#
# 潮が返ると、壺はいっせいに向きを変える。口が背を向けたあいだ、光はどこにも無い。
# 割れた壺だけは、いつまでも暗いままだ。**囲えなくなった器には、真ん中が無い。**
#
# 🔴 光の型＝**内包**（#53：66作で7作）
# 🔴 構図の型＝**群**（#57：66作で2作。**66作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／065／066 に続く10例目）
#    今日選べたのは 光＝内包／窓／稜線 × 構図＝全身／端寄せ／群。
#    ・**「群」を選んだ時点で、光は 内包 か 窓 の二択になる**（#71①：共有光源を宙／背後に置くと
#      物のあいだが光って `clusters==1` に落ちる）。**稜線×群は原理的に不成立**なので、
#      いちばん珍しい光の型（稜線 6/66）は今日は取れない——これは好みではなく幾何の結論。
#    ・061 HANIWA が **窓×群** をやっている。残るのは **内包×群**＝シリーズで一度も無い組み合わせ。
#    ・「群」は 66作で2作（056/061）。「全身」51作の偏りをいちばん強く戻せる型。
#
# 🔴 #71⑥「同じ形を等間隔に並べると、題材が何であれ竹か電池に見える」への手当ては、
#    デザインの工夫ではなく**実物どおり**にした：蛸壺は一本の縄に**大小を混ぜて**通す。
#    さらに **割れた壺を1つ混ぜる**（漁具として死んだ個体＝群のなかの異種）。
#
# 🔴 #76③「円い光は惑星に見える」への手当て：口を**軸の正面から見せない**。
#    壺の軸を視線から 25〜57°ずらして置くと、口は楕円になり、腹と肩が一緒に読める。
#    軸を正対させると「穴のあいた黒い円盤」＝ボタンにしかならない。
#
# 🔴 機構＝**潮が返る**（整数周期・厳密に閉じる）。壺はぜんぶ同じ向きに回る（＝同じ潮を受けている）。
#    #71②：位相を 2π に散らすと群の合計光量は定数になるので、**個体差は ±0.9rad の幅に収める**。
#    発光の値は1フレームも動かさない（#69②／#70④）。変わるのは「口がこちらを向いているか」だけ。
#    #71⑦：動き量は個体でなく**群ごと**の横揺れで出す（個体を振ると隣と重なって群が融ける）。
#
# 造形＝ろくろ（回転体）だけ。boolean 不使用。壺は個体ごとに**実寸で別メッシュ**を組む
#    （object.scale を使わない＝#15）。黒の質感は MATERIALS.md の **`touki`（陶）**＝素焼き。
#
# 【ドメイン】漁労・蛸壺。直近10作＝灯火・和蝋燭／神域・鳥居／鏡・柄鏡／手仕事・和鋏／製紙・紙漉き／
#    古墳・埴輪／炊事・竈／証・割符／空・凧／運搬・車輪 と別。
#    053 UKIDAMA【漁労・浮子】は「見えない水面を教える」機構で、浮子は中身を持たない。
#    こちらは**空洞そのものが漁具**＝主題も機構も別。
#    061 HANIWA【古墳・埴輪】も素焼きの群だが、あちらは直立した筒の**貫通穴**（窓）、
#    こちらは横倒しの腹と**口より広い内部**（内包）。
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
LIME_W = 95.0                      # #58③：随伴のライム光源（発光体の外・遠く）

# --- 壺の断面（正規化。個体ごとに S 倍して実寸でメッシュを組む）---
# z は腹の中心を 0 に取る（＝object の原点。**回転しても動かない点**なので、
# 内部のライム灯をここに置けばキーフレームが要らない）
PROF = [(-0.360, 0.000), (-0.356, 0.090), (-0.346, 0.150), (-0.328, 0.200),
        (-0.300, 0.238), (-0.240, 0.266), (-0.150, 0.282), (-0.050, 0.287),
        (0.045, 0.276), (0.115, 0.252), (0.165, 0.216), (0.205, 0.178),
        (0.240, 0.155), (0.266, 0.148), (0.284, 0.172), (0.300, 0.158)]
# 0.266（くびれ）→ 0.284（玉縁）＝縁を巻き締めたふくらみ。
#   🔴 1周目はここが無く、口が胴のシルエットに溶けて **黒い卵に緑の錠剤** にしか見えなかった
# 🔴🔴 **口の広さは意匠ではなく光学で決まる。**深さ d の光が θ 倒した壺から見えるのは
#    d·tanθ < R_MOUTH のときだけ。喉の内半径は「首の外径 − 肉厚」なので、
#    首を細くするほど中は見えなくなる。5周目は首 0.152／肉厚 0.046＝内 0.106 で、
#    θ=50° の壺は**完全に塞がっていた**（#40⑥ は比なので 0.000 のまま＝合格に見える）。
# 🔴🔴🔴 7周目はその逆に振れて口を 0.198 まで広げた。1600×2000 で見ると
#    **黒い筒＋奥にへこんだ発光面＝ダウンライト（照明器具）**にしか読めなかった（#33 の型）。
#    480×600 では出ない（#68）。解いたのは口の広さではなく **光の深さ**——
#    皿を口の近く（d=0.125）へ上げると、**細い口（0.102＝腹の 0.36）でも中心が見える**。
#    肩の突帯も落として、口まわりの同心の輪を 5 本から 3 本に減らした
WALL     = 0.046      # 胴の肉厚
Z_CAVTOP = 0.250      # 内腔の天井（ここから上は「喉」＝内半径 R_MOUTH の直筒）
Z_LIP    = 0.300      # 口の縁
R_MOUTH  = 0.102      # 喉の内半径。腹の内半径 0.202 の **0.51**＝中は口の 1.94 倍広い＝内包
#  🔴 喉の長さ 0.050・口の縁（環）の幅 0.038。**喉が長いほど奥行きは出るが、
#     倒した壺（θ=50°）では喉が視線を塞いで光が消える**——奥行きと光量は喉の長さで取り合う。
#     効いたのは「喉を短くして、代わりに玉縁（0.190 のふくらみ）で縁の厚みを見せる」
Z_FLOOR  = -0.290     # 内腔の底（底の肉厚 0.070＝沈むための重さ。実物もここが厚い）

# --- 光（内腔だけ。喉と縁は黒のまま＝#49① 塗った縁を作らない）---
# 🔴🔴 2周を「内壁を光らせる」で溶かした。**口という絞りは、明るい所しか見せない。**
#    内腔の壁に勾配を焼いても、口の中では一様に見える＝**どう作っても緑の錠剤**（#74⑤）。
#    効いたのは 060 KAMADO と同じ構え——**光は壁ではなく、中に在る物**。
#    暗い内壁に囲まれた小さな発光体を置くと、口の中に「明るい芯と、そのまわりの暗がり」が同時に入る。
# 🔴 扁球（球の発光体）も外れだった：**明るい極が壺の軸を向くので、倒した壺では
#    その極が喉に隠れ、見えるのは暗い側面だけになる**（ライム面積 0.38%＝#51 不合格）。
#    027 SHIBORI／028 ENSO と同じ「**浅い凹面ディッシュを開口の奥に正対させる**」に戻した。
#    ディッシュは θ が変わっても cos θ で痩せるだけで、勾配は常に正面から見える。
R_LENS   = 0.135      # 中の光（浅い皿）。内腔の半径 0.202 より小さい＝まわりに暗がりが残る
ZL_C     = 0.175      # 皿の高さ。**d = Z_LIP - ZL_C = 0.125 が θ の上限を決める**
#                       （d·tanθ < R_MOUTH → θ < 39.2° で皿の中心＝白い芯が見える）
LENS_SAG = 0.024      # 縁が口の側へ反る量（凹面＝グレージングで LED テープ化しない・#19）
ES_CORE = 12.0
POW_E   = 1.15        # 中心で 1・縁で厳密に 0（縁の無い光＝#49①）
WHITE_FROM, WHITE_TO = 0.70, 0.62   # halo はこの「白→ライム」の帯でしか出ない（#70④）
K_MIX   = 7.0         # E→0 側は黒い素焼きへ戻す（発光体の縁を作らない＝#49①）

# --- 群（#71⑥ 大小を混ぜる／1つは割れている・#70⑤ 等間隔にしない）----
# (x, y, z, S, rx, ry, dpsi, bob, beta, broken)
#   rx = 静止姿勢の傾き。π/2 で口が真横。**視線と軸の角 θ が 29〜38° になるよう個体ごとに散らす**
#        🔴 θ が小さい（＝軸に近い所から覗く）と、同心の輪（口・喉・玉縁）が揃って
#           **カメラのレンズ**に読める（#33 の型）。腹の稜線が一緒に見える角度まで倒す
#        （#76③：軸を正対させると「穴のあいた黒い円盤」＝ボタンにしかならない）
#        🔴 喉が長い（0.105）ので θ を広げすぎると口が塞がる。上限は atan(2R/L)=63°
#        rx = π/2 + 仰角 + θ。仰角は壺ごとに違う（カメラは群の下にある）ので rx も個体ごとに違う
#   dpsi = 潮に対する個体差。**カメラ方位（壺ごとに違う）＋ ±0.30rad の揺らぎ**だけ
#        （#71②：2π に散らすと合計が定数になる。#40⑥ を潰さないため幅を持たせない）
POTS = [
    dict(x=-0.018, y=+0.60, z=3.441, S=0.65, rx=2.257, ry=+0.22, dpsi=+0.284, bob=0.040, beta=0.4),
    dict(x=+0.752, y=-0.45, z=3.300, S=0.77, rx=2.382, ry=-0.15, dpsi=-0.178, bob=0.036, beta=2.1),
    dict(x=+1.445, y=+1.10, z=3.470, S=0.71, rx=2.237, ry=+0.31, dpsi=+0.185, bob=0.030, beta=4.0),
    dict(x=+0.198, y=-0.60, z=2.556, S=0.90, rx=2.249, ry=-0.26, dpsi=-0.203, bob=0.044, beta=5.2),
    dict(x=+1.123, y=+0.35, z=2.732, S=0.83, rx=2.221, ry=+0.11, dpsi=+0.054, bob=0.038, beta=1.2),
    dict(x=+0.073, y=+0.90, z=1.939, S=0.85, rx=2.350, ry=-0.34, dpsi=-0.248, bob=0.034, beta=3.3,
         broken=True),
    dict(x=+0.895, y=-0.20, z=1.995, S=0.85, rx=2.235, ry=+0.19, dpsi=+0.131, bob=0.042, beta=0.1),
]
SWAY = 0.160          # #71⑦ 群ごとの横揺れ（t=0.5＝hero では 0）
# 🔴 潮は「一周」ではなく「返す」。1周目は ψ=2πt（全周回転）で組んだが、
#    光が出ているのは**ループの23%だけ**で、残りは真っ黒な静止画だった（--probe-only が数字で出す）。
#    実物も、海底の壺は回り続けない——寄せて、返す。ψ = dpsi + A(1+cos2πt) なら
#    t=0.5 でいっせいに口がこちらを向き、t=0/1 で 2A だけ背ける。cos の整数周期で厳密に閉じる。
PSI_A = 0.92          # 振れ幅の半分（2A=1.84rad=105°まで背ける）
# 割れた壺の割れ線 z_b(φ)＝傾いた面＋小さなうねり。
# 🔴 1600×2000 で見ると、**面を格子ごと落とす作り方は割れ口が階段になる**（480×600 では出ない＝#68）。
#    直したのは解像度ではなく作り方——**列（φ）ごとに、断面を割れ線まで同じ点数で生成する**。
#    全列の点数が揃うので面は綺麗に張れ、縁は z_b(φ) の上に厳密に乗る（#71⑤ と同じ発想）
BRK_PHI, BRK_Z0, BRK_A = 0.55, 0.075, 0.170

NPHI, NCAV = 76, 30
STILL_FRAME = 61      # t=0.5 ＝ 口がいっせいにこちらを向く唯一の瞬間


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def r_out(z):
    """外側の半径（PROF を線形補間）。z は正規化（S を掛ける前）"""
    if z <= PROF[0][0]:
        return 0.0
    if z >= PROF[-1][0]:
        return PROF[-1][1]
    for i in range(len(PROF) - 1):
        z0, r0 = PROF[i]
        z1, r1 = PROF[i + 1]
        if z0 <= z <= z1:
            u = (z - z0) / (z1 - z0)
            return r0 + (r1 - r0) * (3 * u * u - 2 * u * u * u)      # smoothstep
    return PROF[-1][1]


def r_cav(z, broken=False):
    """内腔の半径。腹は肉厚ぶん内側、喉（Z_CAVTOP〜Z_LIP）は R_MOUTH の直筒。
       🔴 番兵 -1.0 を返す境界は **必ず許容差を付ける**。Z_CAVTOP-(Z_CAVTOP-Z_FLOOR)*1.0 は
          浮動小数で Z_FLOOR を 4e-17 下回ることがあり、内腔の底のリングが半径 -1.0＝
          **裏返った巨大な発光円盤**になった（絵は「白く発光する謎の球」で、エラーは出ない）"""
    if z < Z_FLOOR - 1e-9 or z > Z_LIP + 1e-9:
        return -1.0
    z = min(max(z, Z_FLOOR), Z_LIP)
    if z >= Z_CAVTOP and not broken:
        return R_MOUTH
    return max(0.02, r_out(z) - WALL)


def lens_e(q):
    """中の光の勾配。q = 中心からの正規化半径。中心 1・縁 0＝**縁の無い光**（#49①）"""
    return max(0.0, 1.0 - min(1.0, q) ** POW_E) ** 0.9


def lens_z(q):
    return ZL_C + LENS_SAG * q * q


def rot_local(v, rx, ry, psi):
    """world ベクトル v を壺の局所系へ戻す（R = Rz(psi)·Ry(ry)·Rx(rx) の転置）"""
    x, y, z = v
    c, s = math.cos(psi), math.sin(psi)
    x, y = c * x + s * y, -s * x + c * y          # Rz(-psi)
    c, s = math.cos(ry), math.sin(ry)
    x, z = c * x - s * z, s * x + c * z           # Ry(-ry)
    c, s = math.cos(rx), math.sin(rx)
    y, z = c * y + s * z, -s * y + c * z          # Rx(-rx)
    return (x, y, z)


def pot_loc(p, t):
    return (p["x"] + SWAY * math.sin(2.0 * math.pi * t), p["y"],
            p["z"] + p["bob"] * math.sin(2.0 * math.pi * t + p["beta"]))


def psi_of(p, t):
    return p["dpsi"] + PSI_A * (1.0 + math.cos(2.0 * math.pi * t))


# --- 遮蔽（#40⑥ を幾何で積分する）--------------------------------
# 発光の値は一切入っていない。変わるのは「口がこちらを向いているか」だけ。
# 内腔の各点からカメラへ向かう線を局所座標で追い、口から抜けられるかを見る。
_CAV = []
for _i in range(18):
    _q = (_i + 0.5) / 18.0
    _n = max(6, int(30 * _q) + 4)
    for _j in range(_n):
        _p = 2.0 * math.pi * (_j + 0.5) / _n
        _CAV.append((R_LENS * _q * math.cos(_p), R_LENS * _q * math.sin(_p),
                     lens_z(_q), lens_e(_q) * _q / _n))


def pot_visible(p, t):
    """この壺の、いま見えている発光量（相対値）。broken は光らない"""
    if p.get("broken"):
        return 0.0
    S = p["S"]
    loc = pot_loc(p, t)
    d = [CAM_LOC[i] - loc[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in d))
    u = rot_local([c / n for c in d], p["rx"], p["ry"], psi_of(p, t))
    tot = 0.0
    step = 0.012
    for x, y, z, w in _CAV:
        if w <= 0.0:
            continue
        ok = False
        for k in range(1, 90):
            s = k * step
            qx, qy, qz = x + u[0] * s, y + u[1] * s, z + u[2] * s
            if qz > Z_LIP:
                ok = True
                break
            rc = r_cav(qz)
            if qz < Z_FLOOR or rc < 0.0 or math.hypot(qx, qy) > rc:
                break
        if ok:
            tot += w
    return tot * S * S * (8.3 / (8.3 + p["y"])) ** 2


def light_visible(t):
    return sum(pot_visible(p, t) for p in POTS)


_TS = [i / N_FRAMES for i in range(N_FRAMES)]
_VS = [light_visible(t) for t in _TS]
_VMAX = max(_VS)

if "--probe-only" in sys.argv:
    mag = lambda y: 8.3 / (8.3 + y)

    def proj(p, t):
        """壺の見かけの中心と半径（外接球 0.30·S で近似＝実際の footprint より大きめ）"""
        x, y, z = pot_loc(p, t)
        m = mag(y)
        return (AIM_X + (x - AIM_X) * m, LOOK_Z + (z - LOOK_Z) * m, 0.34 * p["S"] * m)

    print("── 067 TAKOTSUBO 幾何プローブ")
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    b = max(range(N_FRAMES), key=lambda i: _VS[i])
    print("   いちばん明るい frame %d（t=%.3f）  STILL_FRAME=%d" % (b + 1, _TS[b], STILL_FRAME))
    print("   光の曲線 " + " ".join("%.0f" % (100 * _VS[i] / _VMAX) for i in range(0, N_FRAMES, 6)))
    on = sum(1 for v in _VS if v > 0.25 * _VMAX) / N_FRAMES * 100
    print("   光が25%%以上ある時間の割合 %.0f%%（低すぎるとloopが暗いだけの動画になる）" % on)
    _tot = sum(w for _, _, _, w in _CAV) * sum(p["S"] ** 2 * (8.3 / (8.3 + p["y"])) ** 2
                                               for p in POTS if not p.get("broken"))
    print("   🔴 **絶対量** hero で見えている発光 = 全発光の %.1f%%（#40⑥ は比なので"
          "光が 0 に潰れても 0.000＝合格に見える。5周目はこれが 2%% だった）" % (100 * _VMAX / _tot))

    print("\n   ── 群の見え方（t=0.5）")
    ps = [proj(p, 0.5) for p in POTS]
    x0 = min(c[0] - c[2] for c in ps); x1 = max(c[0] + c[2] for c in ps)
    z0 = min(c[1] - c[2] for c in ps); z1 = max(c[1] + c[2] for c in ps)
    print("   群のbbox  x %.2f..%.2f（%.1f%%）  z %.2f..%.2f（%.1f%%）→ 長辺 %.1f%%（帯 44〜66）"
          % (x0, x1, (x1 - x0) / FRAME_W * 100, z0, z1, (z1 - z0) / FRAME_H * 100,
             max((x1 - x0) / FRAME_W, (z1 - z0) / FRAME_H) * 100))
    print("   枠まで 左%.2f 右%.2f 上%.2f （負なら枠外＝edge。群はedge=0が望ましい）"
          % (x0 - (AIM_X - FRAME_W / 2), (AIM_X + FRAME_W / 2) - x1,
             (LOOK_Z + FRAME_H / 2) - z1))
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * mag(-1.7)
    band = LOOK_Z + FRAME_H / 2 - 0.62 * FRAME_H       # 床のライム帯（画面62〜80%）の上端
    print("   群の下端 z=%.2f ／ キャプション上端 z=%.2f ／ 床のライム帯の上端 z=%.2f"
          % (z0, capz, band))
    print("   → 帯との余白 %.3f（正なら床のライムが群のあいだに入らない＝#71① の回避）" % (z0 - band))

    worst = 9.9
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            d = math.hypot(ps[i][0] - ps[j][0], ps[i][1] - ps[j][1]) - ps[i][2] - ps[j][2]
            worst = min(worst, d)
    print("   壺どうしの最小すきま %.3f （%.0fpx@1600 ／ 膨張1セル=12px を割ると塊が融合する）"
          % (worst, worst / FRAME_W * 1600))

    la = 0.0
    for p in POTS:
        if p.get("broken"):
            continue
        la += math.pi * (R_MOUTH * p["S"]) ** 2 * (pot_visible(p, 0.5)
                                                   / max(1e-9, pot_visible(p, 0.5)) or 1.0)
    vis = [pot_visible(p, 0.5) for p in POTS]
    vmx = max(vis)
    la = sum(math.pi * (R_MOUTH * p["S"] * mag(p["y"])) ** 2 * (v / vmx) * 0.72
             for p, v in zip(POTS, vis))
    print("   口の見かけ面積の合計 ≒ %.3f ／ 画面 %.2f → ライム面積 ≒ %.1f%%（帯 0.8〜12）"
          % (la, FRAME_W * FRAME_H * 0.8, la / (FRAME_W * FRAME_H * 0.8) * 100))
    print("   壺ごとの見える光（t=0.5）: " + " ".join("%.2f" % (v / vmx) for v in vis))
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
# 素焼きの蛸壺＝**陶（touki）**。艶ではなく、触るとざらつくもの
# 🔴 disp/dsize は MATERIALS.md の 0.006/0.10 から振り直した。表の値は球・立方・トーラスで
#    採ったもので、**倒した回転体に当てると轆轤目でなく「皺の寄った革袋」になった**（1600×2000 で判明）。
#    粗さを大きく・振幅を小さく（0.20／0.0032）＝素焼きの肌に戻る
BLACK_RECIPES = {"touki": dict(rough=0.58, spec=0.26, disp=0.0032, dsize=0.20)}
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


mat_body = black_material("suyaki", RECIPE)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は**素焼きの黒そのもの**へ戻す（発光板の縁を作らない・#49①）。
       底だけ白へ抜く＝halo はこの「白→ライム」の帯でしか出ない（#70④）"""
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


# ---------- 造形（bmesh・実寸。object.scale / transform_apply 不使用＝#15）----
def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def brk_z(phi):
    """割れ口の縁の高さ。傾いた面＋うねり（焼き物は直線には割れない）"""
    return (BRK_Z0 + BRK_A * math.cos(phi - BRK_PHI)
            + 0.022 * math.sin(4.0 * phi + 1.3) + 0.012 * math.sin(7.0 * phi + 0.4))


def shell_mesh(S, broken):
    """外側 → 口の縁（環）→ 喉（直筒）。喉の下端で内腔メッシュへ継ぐ"""
    def col(phi):
        """この方位の断面。broken なら割れ線 z_b(φ) までを同じ点数で刻む"""
        zt = brk_z(phi) if broken else Z_LIP
        zs = [PROF[0][0] + (zt - PROF[0][0]) * (j / 64.0) ** 0.75 for j in range(65)]
        pts = [(r_out(z), z) for z in zs]
        if broken:                                  # 割れ口は肉厚が見える
            pts.append((max(0.02, r_out(zt) - WALL), zt))
            return pts
        return pts
    pts = col(0.0)
    if not broken:
        pts = pts + [(R_MOUTH, Z_LIP)]                 # 口の縁（環）＝幅 0.056 の厚い縁
        for j in range(1, 11):                         # 喉＝黒い影のトンネル（#71④）
            pts.append((R_MOUTH, Z_LIP - (Z_LIP - Z_CAVTOP) * j / 10.0))
        pts.append((max(R_MOUTH, r_out(Z_CAVTOP) - WALL), Z_CAVTOP))     # 喉の下の棚
    npt = len(pts)
    bm = bmesh.new()
    rings = []
    for k in range(NPHI):
        phi = 2.0 * math.pi * k / NPHI
        c, s = math.cos(phi), math.sin(phi)
        cp = col(phi) if broken else pts
        rings.append([bm.verts.new((r * c * S, r * s * S, z * S)) for r, z in cp])
    for k in range(NPHI):
        k2 = (k + 1) % NPHI
        for j in range(npt - 1):
            bm.faces.new((rings[k][j], rings[k2][j], rings[k2][j + 1], rings[k][j + 1]))
    bot = bm.verts.new((0.0, 0.0, (PROF[0][0] - 0.004) * S))
    for k in range(NPHI):
        bm.faces.new((bot, rings[(k + 1) % NPHI][0], rings[k][0]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("tsubo"); bm.to_mesh(me); bm.free()
    return me


def cavity_mesh(S, broken):
    """内腔＝口より広い内側。E を UV 'grad' の U に焼く（#34/#39）。
       法線は軸へ向ける（内側からしか見えない面）"""
    bm = bmesh.new()
    rings = []
    def czs(phi):
        top = brk_z(phi) if broken else Z_CAVTOP
        return [top - (top - Z_FLOOR) * (j / NCAV) ** 1.05 for j in range(NCAV + 1)]

    for k in range(NPHI):
        phi = 2.0 * math.pi * k / NPHI
        c, s = math.cos(phi), math.sin(phi)
        rings.append([bm.verts.new((max(0.0, r_cav(z, broken)) * c * S,
                                    max(0.0, r_cav(z, broken)) * s * S, z * S))
                      for z in czs(phi)])
    for k in range(NPHI):
        k2 = (k + 1) % NPHI
        for j in range(NCAV):
            bm.faces.new((rings[k][j], rings[k2][j], rings[k2][j + 1], rings[k][j + 1]))
    flo = bm.verts.new((0.0, 0.0, Z_FLOOR * S))
    for k in range(NPHI):
        bm.faces.new((flo, rings[k][NCAV], rings[(k + 1) % NPHI][NCAV]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                       # 内向きへ揃える
        c = f.calc_center_median()
        if f.normal.x * c.x + f.normal.y * c.y > 0.0 and math.hypot(c.x, c.y) > 1e-4:
            f.normal_flip()
    me = bpy.data.meshes.new("utsuro"); bm.to_mesh(me); bm.free()
    return me


def lens_mesh(S):
    """中の光＝浅い凹面の皿。**壺に完全に囲われている**ので「裸の緑玉」にはならない（#13）。
       E は中心からの半径（中心 1・縁 0）＝縁を作らない光（#49①）"""
    NA, NR = 64, 26
    bm = bmesh.new()
    ctr = bm.verts.new((0.0, 0.0, lens_z(0.0) * S))
    rings = []
    for j in range(1, NR + 1):
        q = j / NR
        rings.append([bm.verts.new((R_LENS * q * math.cos(2.0 * math.pi * k / NA) * S,
                                    R_LENS * q * math.sin(2.0 * math.pi * k / NA) * S,
                                    lens_z(q) * S)) for k in range(NA)])
    for k in range(NA):
        bm.faces.new((ctr, rings[0][k], rings[0][(k + 1) % NA]))
    for j in range(NR - 1):
        for k in range(NA):
            k2 = (k + 1) % NA
            bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                       # 口の側（+Z）へ向ける
        if f.normal.z < 0:
            f.normal_flip()
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (lens_e(math.hypot(co.x, co.y) / S / R_LENS), 0.5)
    me = bpy.data.meshes.new("hi"); bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=1.15):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for o in bpy.context.selected_objects:      # ライトが選択に残ると shade_auto_smooth が警告を出す
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def add_relief(objs, recipe):
    """黒の肌は実ジオメトリで作る（Bump は黒では見えない＝#52）。
       🔴 SUBSURF は掛けない（#76⑦：Catmull-Clark は口の縁を丸めて食う）"""
    r = BLACK_RECIPES[recipe]
    tex = bpy.data.textures.new("relief_" + recipe, 'CLOUDS')
    tex.noise_scale = r["dsize"]
    for o in objs:
        d = o.modifiers.new("disp", 'DISPLACE')
        d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5


parts, shells = [], []
for i, p in enumerate(POTS):
    br = bool(p.get("broken"))
    sh = link(shell_mesh(p["S"], br), "tsubo_%d" % i, mat_body)
    cv = link(cavity_mesh(p["S"], br), "utsuro_%d" % i, mat_body)   # 内腔の壁は黒のまま
    objs = [sh, cv]
    shells += [sh, cv]
    if not br:                       # 🔴 割れた壺には光を入れない（囲えなくなった器には真ん中が無い）
        objs.append(link(lens_mesh(p["S"]), "hi_%d" % i, mat_glow, smooth=1.2))
    parts += objs
    p["_objs"] = objs

add_relief(shells, RECIPE)        # 🔴 発光体には掛けない（#52 の掟1）

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    for p in POTS:
        loc = pot_loc(p, t)
        rot = (p["rx"], p["ry"], psi_of(p, t))
        for ob in p["_objs"]:
            ob.location = loc
            ob.rotation_euler = rot              # 既定の 'XYZ'＝R = Rz(psi)·Ry·Rx（潮は world Z）
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
        caption("MIDDLE STUDY 067 — TAKOTSUBO", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, LOOK_Z + 0.62)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：群は抜けだらけ＝面光源が壺のあいだから素通しで写る

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③/#67⑥：**奥**（画面62〜80%の帯に届く位置）へ
for sx, sy, sz, w in ((-0.90, 12.0, 0.30, LIME_W), (0.35, 24.0, 0.30, LIME_W),
                      (1.65, 38.0, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = w
    lp.data.shadow_soft_size = 2.60
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0

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

# 🔴 #71①：壺の中の光は床に当たらない（壺に囲われている）。当たると壺と壺のあいだの床が光って
#    塊マスク（暗い ∪ ライム）が繋がり、**群が1塊に落ちる**

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
    gx0 = gy0 = 9.0; gx1 = gy1 = -9.0
    boxes = []
    for i, p in enumerate(POTS):
        xs, ys = [], []
        for o in p["_objs"]:
            ev = o.evaluated_get(dg)
            for v in ev.data.vertices:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                xs.append(c.x); ys.append(c.y)
        bx = (min(xs), max(xs), min(ys), max(ys))
        boxes.append(bx)
        gx0 = min(gx0, bx[0]); gx1 = max(gx1, bx[1])
        gy0 = min(gy0, bx[2]); gy1 = max(gy1, bx[3])
        print(">> 壺%d  x %.3f..%.3f  y %.3f..%.3f  （幅%.1f%% 高%.1f%%）%s"
              % (i, bx[0], bx[1], bx[2], bx[3], (bx[1] - bx[0]) * 100, (bx[3] - bx[2]) * 100,
                 " ← 割れ" if p.get("broken") else ""))
    print(">> 群のbbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)  長辺 %.1f%%（帯 44〜66）"
          % (gx0, gx1, (gx1 - gx0) * 100, gy0, gy1, (gy1 - gy0) * 100,
             max(gx1 - gx0, gy1 - gy0) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (gx0, 1 - gx1, 1 - gy1, gy0))
    worst = 9.0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            dx = max(a[0] - b[1], b[0] - a[1])
            dy = max(a[2] - b[3], b[2] - a[3])
            d = max(dx, dy)
            if d < worst:
                worst, wp = d, (i, j)
    print(">> 壺どうしの最小すきま %.4f（%.0fpx@1600・膨張1セル=12px）  最接近 %s"
          % (worst, worst * 1600, wp))
    print(">> 群の下端 %.3f ／ 床のライム帯 0.20〜0.38（画面下から）→ 余白 %.3f"
          % (gy0, gy0 - 0.38))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_067.blend"))

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
