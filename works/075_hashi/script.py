# =============================================================
# MIDDLE STUDY 075 — HASHI（箸 / 両細 the middle that belongs to neither）
#
# 祝箸は、両端が細い。**片方は人の口、もう片方は神の口。**
# 正月の膳に出る柳の両口箸は、ひっくり返して取り箸に使うためのものではない。
# 一方の端は人が、もう一方の端は神が使う——**神人共食**の約束が、
# かたちだけで書いてある。だから両端とも細い。
#
# すると、使われない場所がひとつだけ残る。**真ん中だ。**
# どちらの口も届かない。どちらのものでもない。
# **人が持つのは、そこだけである。**
#
# 黒い箸が十本、宙にある。四膳と、連れのない二本。
# 光っているのは、どの一本も**真ん中の稜（面取りの角）だけ**——
# 端へ向かうほど断面は角を失って丸くなり、線は消える。
# **稜が在るのは真ん中だけで、稜が在るところだけが光る。**
#
# 🔴 光の型＝**稜線**（#53：74作で7作）
# 🔴 構図の型＝**群**（#57：74作で4作。**74作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#71①／#74②／#75②／#76⑤／
#    #80／#81／#82⑤／#83⑤／#84 に続く18例目）。今日選べたのは
#    光＝反復／稜線／背光 × 構図＝全身／端寄せ／群。9通りを works.json で数えたら：
#      反復×全身 7 ／ 反復×端寄せ 1（068・7作前）／ 反復×群 1（056）
#      稜線×全身 4 ／ 稜線×端寄せ **0** ／ 稜線×群 **0**
#      背光×全身 3 ／ 背光×端寄せ 0 ／ 背光×群 0
#    ・**背光は #67⑤（寄り）／#69①（対）／#71①（群）／#74②（端寄せ）で4方向とも潰れている**
#      ＝今日の3構図では「全身」しか組めない＝既定に戻る。→ 落とす。
#    ・反復×端寄せ は 068 CHASEN（7作前）。反復×全身 は既定の構図。→ 落とす。
#    → 残るのは **稜線×端寄せ** と **稜線×群**（どちらも 0/74）。
#      稜線の既存7作は 002/005/032/037＝全身、069＝対で、**すべて「大きな塊の輪郭に1本」**。
#      069 WARIFU（稜線×対）は6作前で、破面という**面**に光を置いた作。
#      → **稜線×群**＝「1本の線」を**多数の細い体に散らす**。稜線でいちばん遠い絵になる。
#
# 🔴 機構＝**断面の角が、真ん中にしか無い**。s∈[-1,1]（箸の長さ方向）ひとつから3つが同時に出る：
#      ① 太さ  r(s)=R_MID·(RT+(1-RT)(1-|s|^TAPER))  ＝中太両細（はらみ箸の実形）
#      ② 角の有無  超楕円の指数 n(s)=2+(N_SQ-2)·sq(s)。|s|>S_SQ で n=2＝**完全な丸**
#      ③ 光      E(s,θ)=ax(s)·ang(θ)。ang は45°/135°/225°/315°（＝角）に立つ
#    **①②③はぜんぶ同じ s の関数**なので、「真ん中が太い」「真ん中に角がある」「真ん中が光る」が
#    別々の意匠ではなく**ひとつの事実の三つの見え方**になる。
#
# 🔴 動き＝**ヨー（画面奥へ振る）で稜が短くなる**。#69② のとおり「角そのもの」は
#    法線がカメラを向いたままなので首を振っても光量が変わらない。動くのは**投影の長さ**だけ：
#      軸 = (cosφcosψ, cosφsinψ, sinφ) → 投影長 ∝ √(1-cos²φ·sin²ψ)
#    ψ0 を 0 でなく **+22°前後に置く**（0 にすると |cosψ| が両端で対称に戻り振れが半減する）。
#    🔴 #71②：位相を等間隔に配ると群の光量は定数になる。**A/B/C の3膳をほぼ同位相**にして
#    群全体を一緒に振らせ、D/E/F を外して打ち消しを防ぐ。
#    🔴 #80⑥：ヨーは sin、二本のあいだ（gap・鋏角）は cos ＝位相が π/2 ずれる（静止率対策）。
#
# 🔴 二本は**交差させない**。中心をずらした平行な2本をそれぞれ自分の中心まわりに開くと、
#    片側で必ずめり込む（分離 = gap + u·scis は u<0 側で 0 を通る）。
#    gap(t) を鋏角と同位相で開かせ、**分離の最小値 gap−(L/2)·scis > 2·R_MID** を probe で保証する。
#
# 造形＝超楕円ロフト（bmesh・実寸／boolean 不使用／object.scale 不使用＝#15）。
# 黒の質感＝**`urushi`**（MATERIALS.md）。塗り箸・黒檀の箸は実在の黒で、
#    🔴 しかも **urushi だけが DISPLACE を必要としない**（「漆は肌が無いのが肌」）＝
#    MATERIALS 掟1「add_relief は発光体に掛けない」と衝突しない唯一のレシピ。
#    箸は1本の物体の上に黒と発光が同居するので、実起伏を載せると #14 の勾配が壊れる。
#
# 🔴🔴 **6周。学びは4つ（→ PITFALLS #85）。**
#  ① **K_MIX の裾を E_FLOOR で切らないと「稜線」が「全身発光」になる。**角度フォールオフの裾が
#     1/K_MIX(=0.0625) を超えるだけで平面までフル発光に転び、10本が蛍光スティックになった
#     （ライムstd 33.1＝#14 ペンキ化）。`ang = max(0,(ang-E_FLOOR)/(1-E_FLOOR))` で std 48.2 に戻る。
#     🔴 **発光の強さでは直らない。**ES_CORE 3.4→7.4 でも std は戻らず、中間調が #9ED620→#B0E160 と
#     白ける方向にだけ動いた。
#  ② 🔴 **細い線で halo は買えない。**halo ≒（光る線の長さ）×（帯の幅）で、発光の強さはほぼ効かない
#     ——ES_CORE 5.4→7.4（+37%）で halo は +9% しか動かなかった。効いたのは
#     **R_MID 0.040→0.050・S_LIT 0.60→0.66（線を25%太く・10%長く）＝ hero halo 13,989→18,572（+33%）**。
#     光が足りないとき上げるのは「強さ」ではなく「光る面積」。
#  ③ **「群」は太らせると位置ではなく寸法で直す。**probe の分離マージンは 2.4·R_MID に比例するので、
#     R_MID を 1.25 倍すると要求すきまも 1.25 倍になり、太らせるたび分離が 3.3%→0.8% と落ちた。
#     直したのは配置ではなく **L_STICK 0.98→0.90**（塊の footprint が縮み、分離と長辺が同時に戻る）。
#  ④ **#79④ を踏み直した。**test(480×600) の halo（1,549）を不合格と読んで2周ぶん造形を疑った。
#     halo は生の画素数で hero の 1/11.1。**数値の判定は hero か `testhero` にだけ当てる。**
#
# 【ドメイン】食・箸／祝箸（両口箸）。シリーズ未踏。直近10作＝木工・鉋／香道・香／儀礼・水引／
#    弓術・的／茶室・躙口／医薬・薬研／茶・茶筅／漁労・蛸壺／灯火・和蝋燭／神域・鳥居 と別。
#    068 CHASEN（茶筅）も細い部材の集まりだが、あちらは**1個の物の中の80本**（穂＝反復・端寄せ）。
#    こちらは**別々の10本が散る**（群）で、単位が違う。
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
LIME_W = 105.0                     # 随伴のライム光源（#58／#80⑤：シリーズ定数ではない）

# --- 箸の骨格（実物：24cm・中央5.5mm前後・両端2mm＝L/2R≒22〜25 の中太両細）---
L_STICK = 0.90                     # 長さ（画面の1辺に対して35%前後）
R_MID = 0.0500                     # 真ん中の半径（超楕円の平面側。角はこの1.23倍）
RT_R = 0.30                        # 端の半径 ÷ 真ん中の半径
TAPER_P = 1.25                     # 細りの指数（小さいほど早く細る）
N_SQ = 5.5                         # 真ん中の超楕円指数（2=円／大きいほど角が立つ）
S_SQ = 0.72                        # |s| がこれを超えると断面は完全な丸＝稜が消える
NS, NT = 80, 64                    # 長さ方向／周方向の分割

# --- 光（#81④：halo は白へ抜ける広い勾配でしか出ない）-------------
S_LIT = 0.66                       # 光る範囲＝真ん中の 52%（両端48%ずつは黒）
E_TOP = 1.0
W_CORE, W_TAIL, W_A = 0.16, 0.62, 0.60
E_FLOOR = 0.12                     # 🔴 これを引かないと K_MIX 16 が平面まで発光に変えて #14 のペンキになる    # 角からの角距離（rad）。芯は白、裾はライム
ES_CORE = 5.4
WHITE_FROM, WHITE_TO = 0.58, 0.82
K_MIX = 16.0                       # #76①：不透明さを発光の強さから切り離す

# --- 動き --------------------------------------------------------
G0, GA = 0.122, 0.054              # 二本のあいだ（cos で開閉）
SC0, SCA = 0.004, 0.070            # 鋏角 rad（cos）
# ψ = psi0 + ya·sin(2π(t+q))       ヨー（sin）＝#80⑥ で gap と π/2 ずらす

# --- 置き方（sx,sz は「画面上の位置」＝y=0 平面での座標。奥行 y は別に持つ）---
#     scale は**画面上の見かけの大きさ**（世界スケールは奥行で補正する）
D = math.radians
CLUSTERS = [
    dict(n="A", kind="pair",   sx=0.175, sz=2.95, y= 0.8, phi=D(-16), sc=0.96, psi0=D( 22), ya=D(42), q=0.02, p=0.11),
    dict(n="B", kind="pair",   sx=1.095, sz=2.95, y= 2.2, phi=D( 38), sc=0.88, psi0=D(-18), ya=D(36), q=0.07, p=0.43),
    dict(n="C", kind="pair",   sx=0.172, sz=1.75, y=-1.0, phi=D( 48), sc=1.02, psi0=D( 26), ya=D(40), q=0.04, p=0.79),
    dict(n="D", kind="pair",   sx=1.112, sz=1.565, y= 0.1, phi=D(-30), sc=0.93, psi0=D(-26), ya=D(40), q=0.56, p=0.24),
    dict(n="E", kind="single", sx=0.822, sz=2.270, y= 2.9, phi=D( 68), sc=0.44, psi0=D( 20), ya=D(38), q=0.69, p=0.00),
    dict(n="F", kind="single", sx=0.674, sz=1.28, y=-1.4, phi=D( -8), sc=0.58, psi0=D(-16), ya=D(36), q=0.33, p=0.00),
]

STILL_FRAME = 61


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def gap_of(cl, t):
    return (G0 + GA * 0.5 * (1 - math.cos(2 * math.pi * (t + cl["p"])))) * cl["sc"]


def scis_of(cl, t):
    return SC0 + SCA * 0.5 * (1 - math.cos(2 * math.pi * (t + cl["p"])))


def psi_of(cl, t):
    return cl["psi0"] + cl["ya"] * math.sin(2 * math.pi * (t + cl["q"]))


def mag(y):
    return (8.3 + y) / 8.3


def radius_of(s):
    a = min(abs(s), 1.0)
    return R_MID * (RT_R + (1 - RT_R) * (1 - a ** TAPER_P))


def sqness(s):
    a = min(abs(s), 1.0)
    if a >= S_SQ:
        return 0.0
    return (1.0 - (a / S_SQ) ** 1.6)


def section(s, th):
    """超楕円の断面。戻りは (y, z) の局所座標（x が軸）"""
    r = radius_of(s)
    n = 2.0 + (N_SQ - 2.0) * sqness(s)
    e = 2.0 / n
    ct, st = math.cos(th), math.sin(th)
    return (r * math.copysign(abs(ct) ** e, ct),
            r * math.copysign(abs(st) ** e, st))


def e_of(s, th):
    """#40⑥ の光の場。角（45°+90°m）に立ち、真ん中でだけ生きる"""
    a = abs(s)
    if a >= S_LIT:
        return 0.0
    ax = (1.0 - (a / S_LIT) ** 2) ** 0.9
    d = (th - math.pi / 4) % (math.pi / 2)
    d = min(d, math.pi / 2 - d)
    ang = W_A * math.exp(-(d / W_CORE) ** 2) + (1 - W_A) * math.exp(-(d / W_TAIL) ** 2)
    ang = max(0.0, (ang - E_FLOOR) / (1.0 - E_FLOOR))
    return min(1.0, E_TOP * ax * ang)


def sticks_of(cl):
    return (-1, 1) if cl["kind"] == "pair" else (0,)


def pose(cl, j, t):
    """1本の世界での (中心, XYZオイラー, 世界スケール)"""
    m = mag(cl["y"])
    ws = cl["sc"] * m
    pc = (AIM_X + (cl["sx"] - AIM_X) * m, cl["y"], LOOK_Z + (cl["sz"] - LOOK_Z) * m)
    phi = cl["phi"] + (j * scis_of(cl, t) / 2 if j else 0.0)
    psi = psi_of(cl, t)
    g = gap_of(cl, t) / 2 * m if j else 0.0
    # 事前（ヨー前）の垂直方向 = Ry(-phi)·(0,0,1) = (-sin phi, 0, cos phi)
    ox, oz = -math.sin(cl["phi"]) * j * g, math.cos(cl["phi"]) * j * g
    cy, sy = math.cos(psi), math.sin(psi)
    center = (pc[0] + ox * cy, pc[1] + ox * sy, pc[2] + oz)
    return center, (0.0, -phi, psi), ws


def axis_of(cl, j, t):
    _, (_, my, psi), _ = pose(cl, j, t)
    phi = -my
    return (math.cos(phi) * math.cos(psi), math.cos(phi) * math.sin(psi), math.sin(phi))


def world_pt(cl, j, t, s, th):
    c, (rx, ry, rz), ws = pose(cl, j, t)
    y_, z_ = section(s, th)
    p = (s * L_STICK / 2 * ws, y_ * ws, z_ * ws)
    # R = Rz(rz)·Ry(ry)（rx=0）
    cy_, sy_ = math.cos(ry), math.sin(ry)
    q = (p[0] * cy_ + p[2] * sy_, p[1], -p[0] * sy_ + p[2] * cy_)
    cz_, sz_ = math.cos(rz), math.sin(rz)
    w = (q[0] * cz_ - q[1] * sz_, q[0] * sz_ + q[1] * cz_, q[2])
    return (c[0] + w[0], c[1] + w[1], c[2] + w[2])


def proj(x, y, z):
    m = 8.3 / (8.3 + y)
    return (AIM_X + (x - AIM_X) * m, LOOK_Z + (z - LOOK_Z) * m, m)


def seg_endpoints(cl, j, t):
    a = world_pt(cl, j, t, -1.0, 0.0)
    b = world_pt(cl, j, t, 1.0, 0.0)
    return proj(*a)[:2], proj(*b)[:2]


def seg_dist(p1, p2, q1, q2):
    def d_pt_seg(p, a, b):
        vx, vy = b[0] - a[0], b[1] - a[1]
        wx, wy = p[0] - a[0], p[1] - a[1]
        L2 = vx * vx + vy * vy
        u = 0.0 if L2 == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / L2))
        return math.hypot(p[0] - (a[0] + u * vx), p[1] - (a[1] + u * vy))
    return min(d_pt_seg(p1, q1, q2), d_pt_seg(p2, q1, q2),
               d_pt_seg(q1, p1, p2), d_pt_seg(q2, p1, p2))


def visible_light(t):
    """#40⑥。稜は互いに（膳の相方に）隠れるので z バッファで数える（#78⑦）"""
    GW, GH = 260, 325
    zb = {}
    for cl in CLUSTERS:
        for j in sticks_of(cl):
            c, (rx, ry, rz), ws = pose(cl, j, t)
            dcam = (CAM_LOC[0] - c[0], CAM_LOC[1] - c[1], CAM_LOC[2] - c[2])
            dl = math.sqrt(sum(v * v for v in dcam))
            v_hat = tuple(v / dl for v in dcam)
            for i in range(0, 41):
                s = -S_LIT + 2 * S_LIT * i / 40
                for k in range(NT):
                    th = 2 * math.pi * k / NT
                    e = e_of(s, th)
                    if e < 0.03:
                        continue
                    w = world_pt(cl, j, t, s, th)
                    # 法線（断面の外向き）を近似
                    y0, z0 = section(s, th)
                    y1, z1 = section(s, th + 0.05)
                    ty, tz = y1 - y0, z1 - z0
                    nl = (0.0, tz, -ty)
                    nn = math.hypot(tz, ty) or 1.0
                    nl = (0.0, nl[1] / nn, nl[2] / nn)
                    cy_, sy_ = math.cos(ry), math.sin(ry)
                    nq = (nl[0] * cy_ + nl[2] * sy_, nl[1], -nl[0] * sy_ + nl[2] * cy_)
                    cz_, sz_ = math.cos(rz), math.sin(rz)
                    nw = (nq[0] * cz_ - nq[1] * sz_, nq[0] * sz_ + nq[1] * cz_, nq[2])
                    fac = sum(nw[a] * v_hat[a] for a in range(3))
                    if fac <= 0:
                        continue
                    sx, sz2, m = proj(*w)
                    gx = int((sx - (AIM_X - FRAME_W / 2)) / FRAME_W * GW)
                    gy = int((sz2 - (LOOK_Z - FRAME_H / 2)) / FRAME_H * GH)
                    if not (0 <= gx < GW and 0 <= gy < GH):
                        continue
                    cell = zb.get((gx, gy))
                    if cell is None or w[1] < cell[0]:
                        zb[(gx, gy)] = (w[1], e * fac)
    return sum(c[1] for c in zb.values())


if "--probe-only" in sys.argv:
    print("── 075 HASHI 幾何プローブ")
    print("   箸 長さ%.2f 真ん中の半径%.4f（角は%.4f）端%.4f  L/2R=%.1f"
          % (L_STICK, R_MID, R_MID * 2 ** (0.5 - 1 / N_SQ), radius_of(1.0),
             L_STICK / (2 * R_MID)))
    print("   稜が在る範囲 |s|<%.2f ／ 光る範囲 |s|<%.2f ／ 断面指数 %.1f→2.0"
          % (S_SQ, S_LIT, N_SQ))
    print("   本数 %d本 / 塊 %d（群＝5以上）"
          % (sum(len(sticks_of(c)) for c in CLUSTERS), len(CLUSTERS)))

    # --- めり込み検査（二本のあいだ）---
    worst = 1e9
    for cl in CLUSTERS:
        if cl["kind"] != "pair":
            continue
        for x in range(48):
            t = x / 48
            sep = gap_of(cl, t) - (L_STICK / 2) * scis_of(cl, t)
            worst = min(worst, sep - 2 * R_MID)
    print("\n   ── 二本のあいだ（負ならめり込む）")
    print("   🔴 最小すきま %.4f（>0 で不接触）" % worst)

    # --- 塊の分離（全位相）---
    print("\n   ── 塊の分離（#63①：画面上 0.022 で繋がる）")
    gmin, gwhen = 1e9, None
    for x in range(24):
        t = x / 24
        segs = []
        for cl in CLUSTERS:
            segs.append([seg_endpoints(cl, j, t) for j in sticks_of(cl)])
        for a in range(len(segs)):
            for b in range(a + 1, len(segs)):
                for s1 in segs[a]:
                    for s2 in segs[b]:
                        d = seg_dist(s1[0], s1[1], s2[0], s2[1])
                        d -= 2.4 * R_MID * max(CLUSTERS[a]["sc"], CLUSTERS[b]["sc"])
                        if d < gmin:
                            gmin, gwhen = d, (CLUSTERS[a]["n"], CLUSTERS[b]["n"], t)
    print("   🔴 最小すきま %.4f ＝ 画面幅の %.1f%%（2.2%%以上・目標3%%）  %s-%s @t=%.2f"
          % (gmin, gmin / FRAME_W * 100, gwhen[0], gwhen[1], gwhen[2]))

    # --- 見える光 ---
    print("\n   ── 見える光（#40⑥ / #59）")
    vs = [visible_light(x / 24) for x in range(24)]
    vmax = max(vs)
    print("   " + " ".join("%3.0f" % (100 * v / vmax) for v in vs))
    print("   🔴 見える光 min/max = %.3f （合格 0.75以下）" % (min(vs) / vmax))
    th_ = (STILL_FRAME - 1) / N_FRAMES
    print("   hero(frame %d, t=%.3f) は最大の %.0f%%"
          % (STILL_FRAME, th_, 100 * visible_light(th_) / vmax))

    # --- 画面 ---
    print("\n   ── 画面（hero frame %d）" % STILL_FRAME)
    SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2
    allx, allz = [], []
    for cl in CLUSTERS:
        xs, zs = [], []
        for j in sticks_of(cl):
            for s in (-1.0, -0.5, 0.0, 0.5, 1.0):
                for k in range(0, NT, 8):
                    px, pz, _ = proj(*world_pt(cl, j, th_, s, 2 * math.pi * k / NT))
                    xs.append(px); zs.append(pz)
        allx += xs; allz += zs
        print("   %-2s x %6.1f..%6.1f%%  z %6.1f..%6.1f%%"
              % (cl["n"], (min(xs) - SX0) / FRAME_W * 100, (max(xs) - SX0) / FRAME_W * 100,
                 (min(zs) - SZ0) / FRAME_H * 100, (max(zs) - SZ0) / FRAME_H * 100))
    x0, x1, z0, z1 = min(allx), max(allx), min(allz), max(allz)
    sl = max(min(x1, SX0 + FRAME_W) - max(x0, SX0), 0) / FRAME_W
    sh = max(min(z1, SZ0 + FRAME_H) - max(z0, SZ0), 0) / FRAME_H
    edge = ((x0 <= SX0) + (x1 >= SX0 + FRAME_W) + (z0 <= SZ0) + (z1 >= SZ0 + FRAME_H))
    cx = (sum(allx) / len(allx) - SX0) / FRAME_W * 100
    cz = (sum(allz) / len(allz) - SZ0) / FRAME_H * 100
    print("   🔴 長辺 %.1f%%（55〜65%%）  幅 %.1f%%  高さ %.1f%%  枠への接触 %d辺  重心 x%.1f%% y%.1f%%"
          % (max(sl, sh) * 100, sl * 100, sh * 100, edge, cx, 100 - cz))
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    print("   群の下端 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
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
# 🔴 urushi は DISPLACE を要らない唯一のレシピ＝黒と発光が同じ物体に同居できる（掟1）
URUSHI = dict(rough=0.30, spec=0.34, coat=0.05, coat_rough=0.25)


def apply_black(p):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = URUSHI["rough"]
    p.inputs["Specular IOR Level"].default_value = URUSHI["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = 0.0
    p.inputs["Coat Weight"].default_value = URUSHI["coat"]
    p.inputs["Coat Roughness"].default_value = URUSHI["coat_rough"]


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は黒（漆）へ戻す＝発光板の縁を作らない（#49①）。
       芯だけ白へ抜く＝halo はこの「白→ライム」の帯でしか出ない（#81④）"""
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


mat_glow = glow_material("hashi")


# ---------- 造形（bmesh・実寸。boolean 不使用・object.scale 不使用）----------
def stick_mesh(name, ws):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    emap = {}
    rings = []
    for i in range(NS + 1):
        s = -1.0 + 2.0 * i / NS
        ring = []
        for k in range(NT):
            th = 2 * math.pi * k / NT
            y_, z_ = section(s, th)
            v = bm.verts.new((s * L_STICK / 2 * ws, y_ * ws, z_ * ws))
            emap[v] = e_of(s, th)
            ring.append(v)
        rings.append(ring)
    for i in range(NS):
        for k in range(NT):
            k2 = (k + 1) % NT
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    # 端は浅い円錐で閉じる（半径は真ん中の 30%＝ほぼ点）
    for sgn, ring in ((-1, rings[0]), (1, rings[-1])):
        tip = bm.verts.new((sgn * (L_STICK / 2 + radius_of(1.0) * 0.8) * ws, 0.0, 0.0))
        emap[tip] = 0.0
        for k in range(NT):
            k2 = (k + 1) % NT
            if sgn > 0:
                bm.faces.new((ring[k], ring[k2], tip))
            else:
                bm.faces.new((ring[k2], ring[k], tip))
    bm.normal_update()
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = (emap[lp.vert], 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=1.0):
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
    return ob


parts, plan = [], []
for cl in CLUSTERS:
    for j in sticks_of(cl):
        ws = cl["sc"] * mag(cl["y"])
        ob = link(stick_mesh("m_%s%+d" % (cl["n"], j), ws), "hashi_%s%+d" % (cl["n"], j),
                  mat_glow)
        parts.append(ob); plan.append((cl, j, ob))

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    for cl, j, ob in plan:
        c, eul, _ = pose(cl, j, t)
        ob.location = c
        ob.rotation_euler = eul
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
        caption("MIDDLE STUDY 075 — HASHI", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
# 🔴 #67①：被写体が10本の細い棒＝抜けだらけ。面光源をカメラから隠す
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。群の下・奥に置いて空間へ光を出す
for sx, sy, sz, w in ((-0.40, 2.4, 0.26, LIME_W), (0.55, 5.2, 0.26, LIME_W),
                      (1.30, 8.8, 0.26, LIME_W)):
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
cam.data.dof.focus_distance = 8.3 + 0.55
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
    allx, ally = [], []
    for ob in parts:
        ev = ob.evaluated_get(dg)
        xs, ys = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
        allx += xs; ally += ys
        print(">> %-12s x %6.3f..%6.3f  y %6.3f..%6.3f" % (ob.name, min(xs), max(xs),
                                                           min(ys), max(ys)))
    x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
    sl = max(0.0, min(x1, 1) - max(x0, 0))
    sh = max(0.0, min(y1, 1) - max(y0, 0))
    edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
    print(">> 全体 bbox x %.3f..%.3f y %.3f..%.3f" % (x0, x1, y0, y1))
    print(">> 🔴 長辺 %.1f%%（55〜65%%）  枠への接触 %d辺" % (max(sl, sh) * 100, edge))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_075.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("hashi_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.34
    for ob in parts:
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
                                  export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
