# =============================================================
# MIDDLE STUDY 089 — KAIAWASE（貝合わせ / the seam decides the pair）
#
#   光の型＝面（#53）  構図の型＝対（#57）  ドメイン＝平安の遊び・貝合わせ（シリーズ未踏）
#
# 黒い蛤が二枚、離れて浮いている。一枚は返してあって、内側が光っている。
# もう一枚はまだ伏せたままだ。
#
# 貝合わせ（貝覆い）は、絵を合わせる遊びではない。**合わせるのは、貝のほうだ。**
# 蛤の合わせ目——蝶番の歯の形は一枚ごとに違うから、一枚の貝に合う相手は、この世に一枚しかない。
# 三百六十枚を伏せて並べても、間違えようがない。**合わないものは、合わないから。**
#
# 光っているのは内側の面だ。そこには、そこに付いていた身の跡が残っている——
# 二つの筋の跡と、縁に沿って走る一本の線。**面が返しているのは、もういない身の形のほう。**
#
# 伏せたままの一枚も、内側は同じように光っている。こちらから見えないだけだ
# （床に落ちている緑が、その光）。**真ん中にあるのは、二枚の貝ではなく、合わせ目のほうだ。**
#
# 造形：貝は「臍から扇に育つ面」P(s,θ) = U + s·L(θ)·dir(θ)（s＝成長段階・θ＝臍から見た方位）。
#       s=1 の縁は平面＝合わせ目の面、s=0 の臍がいちばん奥へ膨らむ＝実際の二枚貝の育ち方。
#       🔴 何に見えるかを決めたのは L(θ) の**両端の落とし方**だった（→ PITFALLS #100①）。
#       成長線は外面だけの実ジオメトリの段。内面に同じ段を刻むと一段ずつ鏡面を拾って銀の扇になる。
#       蝶番の歯は内面の臍寄りに3つ。**合うか合わないかを決めている所。**
#       黒は陶（#52。漆は段が鏡面を拾いすぎた）。DISPLACE は掛けない。
#
# 光：面。内面の明るさ g は頂点の (s,θ) から引いた純関数で UV.x に焼いてある
#     （釣鐘 × 蝶番のゲート × 縁のゲート − 筋の跡2つ − 外套線 + 成長線の明暗）。
#     🔴 g は1フレームも動かさない（#69②／#70④）。光の振れは全部ジオメトリ
#        ＝二枚が向き合うほど内面の射影が cos で落ちる（`-- geom` で 2.26 倍と先に確認した）。
#     🔴 床のライムは**随伴光の置き場所**で作った。画面に写っている床は被写体より 15〜38m 奥なので、
#        足元の点光源では届かない（600W で 0.08%）。奥へ向けたスポットを貝より奥に置くと、
#        貝はコーンの後ろに居るので色が乗らないまま床だけ緑になる（→ PITFALLS #100③）。
#
# 動き：ph(t)=(1−cos2πt)/2 の1周期だけ。ヨー・寄り・上下、すべて剛体（loc/rot）＝
#       glb にそのまま乗り、ループは数学的に閉じる。t=0 が開き（面が正面）、
#       t=0.5 が向き合い（光があいだへ入る）。振り幅は左右で変えてある（#75③）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
# 🔴 #58 の「150W前後」は**発光面が床を向いている作**の値。この作は発光面が1つで、しかも
#    斜めを向いているので床に何も落ちない（150W で 0.08%＝検知器が鳴る）。600W で 4.3%。
LIME_W = float(os.environ.get("LIME_W", "600"))

# --- 貝（local：臍＝原点、θ=0 が真下、+Y が奥＝カメラの反対）--------
#     L(θ)：臍から縁までの距離（θ は度・+ が posterior 側）
SC = float(os.environ.get("SC", "0.95"))             # 全体の寸法（画面占有 55〜65%＝#51③）
LTAB = tuple((a, b * SC) for a, b in
             ((-80.0, 0.190), (-70.0, 0.300), (-58.0, 0.420), (-44.0, 0.505),
              (-28.0, 0.555), (-14.0, 0.582), (0.0, 0.590), (14.0, 0.588),
              (28.0, 0.575), (44.0, 0.545), (58.0, 0.475), (70.0, 0.360),
              (80.0, 0.235)))
# 🔴🔴 この形が何に見えるかを決めたのは L(θ) の**両端の落とし方**だった。
#    扇の射線（θ=±THMAX）は必ず直線になるので、L を端まで大きいまま持っていくと
#    「半月の器」（88°・1周目）か「折り畳みの扇」（55°・3周目）にしか読めない。
#    端で L を 0.59→0.19 まで落とすと、直線でいるのは臍の脇の短い区間だけ＝**蝶番の線**になり、
#    縁は臍へ向かって曲がって閉じる。いちばん広い所は高さの 43%、幅／高さ＝1.29＝蛤の比。
THMAX = 80.0
D_CUP = float(os.environ.get("D_CUP", "0.185")) * SC     # 臍の膨らみ（幅の 26%）
P_CUP = 1.7                                          # 膨らみの落ち方
TH_UMBO, TH_TAPER = 0.030, 0.55                      # 殻の肉厚（臍 → 縁で薄くなる）
NS, NT = 92, 160
RIDGE_N, RIDGE_P = 25.0, 1.30                        # 成長線の本数と詰み方
RIDGE_OUT, RIDGE_IN = 0.0038, 0.0010   # 🔴 成長線は外面のもの。内面に同じ段を刻むと
                                       #    一つ一つが鏡面を拾って**銀色の扇**になった（2周目）
BEAK, BEAK_S = 0.022, 0.450   # 🔴 0.055/0.30 は「角」。蛤の嘴は緩い膨らみ      # 🔴 臍を蝶番の線より上へ出す（silhouette の頂点＝一目で二枚貝）
TOOTH = ((-17.0, 0.0052), (4.0, 0.0058), (25.0, 0.0050))   # 蝶番の歯（θ°, 高さ）
TOOTH_S0, TOOTH_S1, TOOTH_W = 0.130, 0.320, 7.5

# --- 光（内面の勾配 g。UV.x に焼く）--------------------------------
HINGE0, HINGE1 = 0.100, 0.240      # 蝶番の板は純黒（#32 の裏当て）
S_PK, S_W = 0.38, 0.30             # 🔴 深さの落ちは段（smooth）でなく釣鐘。段だと g=1 の
                                   #    平地が白い帯になり「豆電球」。🔴 裾が短いと光が臍の下の
                                   #    小さな楕円になり、二枚並ぶと**目**に読まれる（#98）。
                                   #    裾を長く取り、縁のゲートで黒に落とす＝光る所が貝の形になる
RIM0, RIM1 = 0.50, 0.86            # 縁の黒い帯（ここで 0 に落とす）
SCARS = ((0.40, -46.0, 0.115, 14.0, 0.62),   # 閉殻筋の跡（前）
         (0.43, 47.0, 0.125, 15.0, 0.62))    # 　　　　　（後。🔴 濃いと「目」になる）
PAL_S, PAL_D, PAL_W, PAL_K = 0.600, 0.200, 0.035, 0.55   # 🔴 外套線は筋の跡と**つなぐ**   # 外套線
ARC_K = 0.10     # 成長線の明暗。🔴 芯では切る（白い所に同心の輪が出ると**的**＝#75①／#99）
ES_BASE = float(os.environ.get("ES_BASE", "0.55"))
ES_CORE = float(os.environ.get("ES_CORE", "3.45"))
WHITE_FROM, WHITE_TO = 0.940, 0.998
# 🔴 halo は純ライムでは作れない（青が上がらない・#81③）。芯だけ白を混ぜて色域に入れる。
K_MIX, E_FLOOR = 7.0, 0.045        # 🔴 #85①：裾を 0 に切る

# --- 対（姿勢。左右で値を変える＝#75③）-----------------------------
DX = 0.455          # 中心から左右へ
DZ = 0.170          # 高さの差（対角に置く）
APPROACH = 0.150    # 向き合うときに寄る量（#59 の動き量。0.085 では 1.12＝基準期の1/3）
# 🔴 5周目まで二枚とも内側をこちらへ向けていた。鏡像の二枚が正面で並ぶと、
#    筋の跡2つ＋外套線が**顔（笑っている顔）**に読まれる（#95：配置が記号を作る）。
#    貝覆いは**伏せて並べ、一枚だけ返す**遊び＝出貝と伏せ貝。片方を裏返した瞬間に顔は消え、
#    黒い塊（伏せ貝の甲）と光る面（出貝の内側）の対になった。
#    🔴 伏せ貝の内側も発光は切らない。こちらからは見えないが、床と輪郭に光が回る
#       ＝「伏せていても光はある。見えないだけ」。
PAIR = (dict(mx=-1, sgn=+1, flip=0, x=AIM_X - DX, y=0.00, z=LOOK_Z + DZ,
             psi0=22.0, dpsi=58.0, rx=-4.0, ry=+6.0, zamp=+0.055),
        dict(mx=+1, sgn=-1, flip=1, x=AIM_X + DX, y=0.02, z=LOOK_Z - DZ,
             psi0=26.0, dpsi=52.0, rx=+6.0, ry=-3.0, zamp=-0.048))
STILL_FRAME = int(os.environ.get("STILL_FRAME", "5"))

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def smooth(e0, e1, x):
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def _cr(p0, p1, p2, p3, u):
    """Catmull-Rom（1次元）"""
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


def L_of(thd):
    """臍から縁までの距離。制御点を Catmull-Rom で結ぶ（#83①）。"""
    thd = max(LTAB[0][0], min(LTAB[-1][0], thd))
    n = len(LTAB)
    for i in range(n - 1):
        a, b = LTAB[i], LTAB[i + 1]
        if a[0] <= thd <= b[0]:
            u = (thd - a[0]) / (b[0] - a[0])
            p0 = LTAB[max(0, i - 1)][1]
            p3 = LTAB[min(n - 1, i + 2)][1]
            return _cr(p0, a[1], b[1], p3, u)
    return LTAB[-1][1]


def f_cup(s):
    """膨らみ（s=0 の臍で 1・s=1 の縁で 0＝縁は平面＝合わせ目の面）"""
    return (1.0 - min(1.0, s) ** P_CUP) ** 0.80


def ridge(s):
    return 0.5 - 0.5 * math.cos(2 * math.pi * RIDGE_N * s ** RIDGE_P)


def tooth_y(s, thd):
    """蝶番の歯（内面の臍寄りに立つ隆起。−Y＝手前へ出る）"""
    w = smooth(TOOTH_S0, TOOTH_S0 + 0.05, s) * (1.0 - smooth(TOOTH_S1 - 0.05, TOOTH_S1, s))
    if w <= 0.0:
        return 0.0
    v = 0.0
    for td, h in TOOTH:
        d = (thd - td) / TOOTH_W
        if abs(d) < 3.0:
            v += h * math.exp(-d * d)
    return -v * w


def surf(s, thd, side):
    """内面（side=-1）／外面（side=+1）の local 座標。臍が原点・+Y が奥。"""
    th = math.radians(thd)
    r = s * L_of(thd)
    x, z = r * math.sin(th), -r * math.cos(th)
    z += BEAK * (1.0 - smooth(0.0, BEAK_S, s))
    y = D_CUP * f_cup(s)
    if side < 0:
        y += RIDGE_IN * ridge(s) + tooth_y(s, thd)
    return x, y, z


def normal_at(s, thd, side):
    """数値微分で面の法線（+Y 側＝外向き）"""
    ds, dt = 1e-3, 0.25
    p = surf(s, thd, side)
    a = surf(min(1.0, s + ds), thd, side)
    b = surf(s, min(THMAX, thd + dt), side)
    u = (a[0] - p[0], a[1] - p[1], a[2] - p[2])
    v = (b[0] - p[0], b[1] - p[1], b[2] - p[2])
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    m = math.sqrt(sum(c * c for c in n)) or 1.0
    n = tuple(c / m for c in n)
    if n[1] < 0:
        n = tuple(-c for c in n)
    # 🔴 臍（s→0）では扇のパラメータが1点に潰れるので数値微分が壊れ、
    #    肉厚ぶん逃がした外面の頂点が四方へ散る＝**棘の冠**（1600×2000 で初めて出た）。
    w = smooth(0.0, 0.14, s)
    n = (n[0] * w, n[1] * w + (1.0 - w), n[2] * w)
    m = math.sqrt(sum(c * c for c in n)) or 1.0
    return tuple(c / m for c in n)


def thick(s):
    # 🔴 臍では肉厚を 0 に絞る。**臍のリング半径（s=0.01 で 0.006）より肉厚（0.030）が太いと、
    #    外面が自分自身を突き抜けて「棘の冠」になる。**480×600 では見えず 1600×2000 で出る。
    return TH_UMBO * (1.0 - TH_TAPER * s) * smooth(0.0, 0.18, s)


def outer(s, thd):
    """外面＝内面を法線方向へ肉厚ぶん逃がす（+成長線の段）
       🔴 base は side=+1（歯を含まない面）。内面をそのまま逃がすと**歯が外面にも出る**。"""
    p = surf(s, thd, 1)
    n = normal_at(s, thd, 1)
    t = thick(s) + RIDGE_OUT * ridge(s)
    return (p[0] + n[0] * t, p[1] + n[1] * t, p[2] + n[2] * t)


def g_of(s, thd):
    """内面の明るさ（0〜1）。**1フレームも動かさない**（#69②）"""
    if s <= 0.0 or s >= 1.0:
        return 0.0
    d = (s - S_PK) / S_W
    g = smooth(HINGE0, HINGE1, s) * math.exp(-d * d) * (1.0 - smooth(RIM0, RIM1, s))
    if g <= 0.0:
        return 0.0
    for ss, td, rs, rt, k in SCARS:            # 閉殻筋の跡
        d2 = ((s - ss) / rs) ** 2 + ((thd - td) / rt) ** 2
        if d2 < 9.0:
            g *= 1.0 - k * math.exp(-d2)
    sp = PAL_S - PAL_D * smooth(20.0, 50.0, abs(thd))                  # 外套線（両端で筋の跡へ上がる）
    dp = (s - sp) / PAL_W
    if abs(dp) < 3.0:
        g *= 1.0 - PAL_K * math.exp(-dp * dp)
    g *= 1.0 + ARC_K * 4.0 * g * (1.0 - g) * math.cos(2 * math.pi * RIDGE_N * s ** RIDGE_P)
    return max(0.0, min(1.0, g))


# --- 面の重心（object 原点を輪郭の重心に置く）-----------------------
def _zc():
    num = den = 0.0
    NI, NJ = 40, 80
    for i in range(NI):
        s = (i + 0.5) / NI
        for j in range(NJ):
            thd = -THMAX + (j + 0.5) / NJ * 2 * THMAX
            Lv = L_of(thd)
            dA = s * Lv * Lv * (1.0 / NI) * (2 * THMAX / NJ) * math.pi / 180.0
            num += (-s * Lv * math.cos(math.radians(thd))) * dA
            den += dA
    return -num / den


ZC = _zc()


def pose_of(k, t):
    """(loc, euler)。ph の1周期だけ＝数学的に閉じる。"""
    P = PAIR[k]
    ph = (1.0 - math.cos(2 * math.pi * t)) / 2.0
    psi = math.radians(P["psi0"] + P["dpsi"] * ph) * P["sgn"] + math.pi * P["flip"]
    loc = (P["x"] + P["sgn"] * APPROACH * ph,
           P["y"],
           P["z"] + P["zamp"] * math.sin(2 * math.pi * t))
    eul = (math.radians(P["rx"]), math.radians(P["ry"]), psi)
    return loc, eul


def _rot(eul):
    cx, sx = math.cos(eul[0]), math.sin(eul[0])
    cy, sy = math.cos(eul[1]), math.sin(eul[1])
    cz, sz = math.cos(eul[2]), math.sin(eul[2])
    Rx = ((1, 0, 0), (0, cx, -sx), (0, sx, cx))
    Ry = ((cy, 0, sy), (0, 1, 0), (-sy, 0, cy))
    Rz = ((cz, -sz, 0), (sz, cz, 0), (0, 0, 1))
    mm = lambda A, B: tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3))
                                  for j in range(3)) for i in range(3))
    return mm(mm(Rz, Ry), Rx)


def _ap(R, p):
    return tuple(sum(R[i][k] * p[k] for k in range(3)) for i in range(3))


# ---------- Blender を起動しない検算（#96：先に幾何で確かめる）----------
def geom_report():
    NI, NJ = 46, 60
    cells = []
    for i in range(NI):
        s = (i + 0.5) / NI
        for j in range(NJ):
            thd = -THMAX + (j + 0.5) / NJ * 2 * THMAX
            g = g_of(s, thd)
            if g < E_FLOOR:
                continue
            Lv = L_of(thd)
            dA = s * Lv * Lv * (1.0 / NI) * (2 * THMAX / NJ) * math.pi / 180.0
            cells.append((s, thd, g, dA))
    print(">> 発光セル %d ／ 面積 %.4f" % (len(cells), sum(c[3] for c in cells)))

    def visible(t):
        tot = 0.0
        for k, P in enumerate(PAIR):
            loc, eul = pose_of(k, t)
            R = _rot(eul)
            for s, thd, g, dA in cells:
                td = thd * P["mx"]
                p = surf(s, td, -1)
                n = normal_at(s, td, -1)
                p = (p[0] * P["mx"], p[1], p[2] + ZC)
                n = (n[0] * P["mx"], n[1], n[2])
                n = (-n[0], -n[1], -n[2])          # 内面の法線＝手前向き
                pw = _ap(R, p)
                pw = (pw[0] + loc[0], pw[1] + loc[1], pw[2] + loc[2])
                nw = _ap(R, n)
                d = (CAM_LOC[0] - pw[0], CAM_LOC[1] - pw[1], CAM_LOC[2] - pw[2])
                m = math.sqrt(sum(c * c for c in d))
                c = sum(nw[i] * d[i] for i in range(3)) / m
                if c > 0:
                    tot += g * dA * c
        return tot

    vs = [visible(f / N_FRAMES) for f in range(N_FRAMES)]
    lo, hi = min(vs), max(vs)
    print(">> 見えているライム（射影・g 重み）")
    for f in range(0, N_FRAMES, 10):
        print("   t=%.2f  %.4f  %s" % (f / N_FRAMES, vs[f], "█" * int(vs[f] / hi * 44)))
    print(">> 光の振れ %.2f 倍（#59 は 1.22 以上）  閉じ |v(0)-v(1)| = %.2e"
          % (hi / lo if lo > 0 else 9.99, abs(vs[0] - visible(1.0))))
    # 画面占有（回転を入れた bbox の粗い見積り）
    for t in (STILL_FRAME / N_FRAMES, 0.0, 0.25, 0.5):
        xs, zs = [], []
        for k, P in enumerate(PAIR):
            loc, eul = pose_of(k, t)
            R = _rot(eul)
            for i in range(0, NI, 3):
                s = (i + 0.5) / NI
                for j in range(0, NJ, 3):
                    thd = (-THMAX + (j + 0.5) / NJ * 2 * THMAX) * P["mx"]
                    for sd in (-1, 1):
                        p = surf(s, thd, sd) if sd < 0 else outer(s, thd)
                        p = (p[0] * P["mx"], p[1], p[2] + ZC)
                        pw = _ap(R, p)
                        pw = (pw[0] + loc[0], pw[1] + loc[1], pw[2] + loc[2])
                        xs.append(pw[0]); zs.append(pw[2])
        w = (max(xs) - min(xs)) / FRAME_W * 100
        h = (max(zs) - min(zs)) / FRAME_H * 100
        print(">> t=%.2f  横 %.1f%%  縦 %.1f%%" % (t, w, h))


if "geom" in modes:
    geom_report()
    sys.exit(0)

# =============================================================
# ここから Blender
# =============================================================
import bpy, bmesh                                        # noqa: E402
from mathutils import Vector, Matrix                     # noqa: E402


def hex_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- マテリアル（MATERIALS.md の urushi＝漆・#52）----------
# 🔴 2周目は漆（0.30/0.34）で組んだが、成長線の段が一本ずつ鏡面を拾って**銀の扇**になった。
#    陶（0.58/0.26）に替え、段は外面だけに残した。DISPLACE は掛けない（段が丸まる）。
URUSHI = dict(rough=0.58, spec=0.26)


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p, r):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_kai, kp_ = principled("urushi"); apply_black(kp_, URUSHI)


def glow_material(name):
    """内面の勾配。UV.x = g（g は頂点座標から引いた純関数）。キーフレームは1本も無い。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    g = sep.outputs["X"]

    def mr(a, b, c, d):
        n = nt.nodes.new("ShaderNodeMapRange"); n.clamp = True
        n.inputs["From Min"].default_value = a
        n.inputs["From Max"].default_value = b
        n.inputs["To Min"].default_value = c
        n.inputs["To Max"].default_value = d
        nt.links.new(g, n.inputs["Value"])
        return n

    stren = mr(0.0, 1.0, ES_BASE, ES_CORE)
    white = mr(WHITE_FROM, WHITE_TO, 0.0, 1.0)
    gate = mr(E_FLOOR, E_FLOOR + 1.0 / K_MIX, 0.0, 1.0)    # 🔴 裾を純黒へ（#85①）

    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(white.outputs["Result"], mixc.inputs[0])

    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(stren.outputs["Result"], emi.inputs["Strength"])

    blk = nt.nodes.new("ShaderNodeBsdfPrincipled")
    apply_black(blk, URUSHI)                                # 🔴 #32：裏当ては純黒の漆
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gate.outputs["Result"], mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("uchi")


# ---------- メッシュ（内面／外面＋縁＋背の帯）----------
def _mesh(name, verts, faces):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(me); bm.free(); me.update()
    return me


def _quad(faces, a, b, c, d, verts, want):
    """法線が want の側を向くように巻き方を決める（開いた面なので機械で決める）"""
    p0, p1, p2 = verts[a], verts[b], verts[c]
    u = [p1[i] - p0[i] for i in range(3)]
    v = [p2[i] - p0[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    faces.append((a, b, c, d) if sum(n[i] * want[i] for i in range(3)) >= 0 else (d, c, b, a))


def inner_mesh(name, mx):
    verts, faces = [], []
    for i in range(NS + 1):
        s = i / NS
        for j in range(NT + 1):
            thd = (-THMAX + j / NT * 2 * THMAX)
            x, y, z = surf(s, thd * mx, -1)
            verts.append((x * mx, y, z + ZC))
    idx = lambda i, j: i * (NT + 1) + j
    for i in range(NS):
        for j in range(NT):
            _quad(faces, idx(i, j), idx(i, j + 1), idx(i + 1, j + 1), idx(i + 1, j),
                  verts, (0, -1, 0))
    return _mesh(name, verts, faces)


def outer_mesh(name, mx):
    """外面＋縁の帯＋背（蝶番側）の帯。ひとつの黒いメッシュにまとめる。"""
    verts, faces = [], []
    for i in range(NS + 1):
        s = i / NS
        for j in range(NT + 1):
            thd = (-THMAX + j / NT * 2 * THMAX)
            x, y, z = outer(s, thd * mx)
            verts.append((x * mx, y, z + ZC))
    base_in = len(verts)
    for i in range(NS + 1):
        s = i / NS
        for j in range(NT + 1):
            thd = (-THMAX + j / NT * 2 * THMAX)
            x, y, z = surf(s, thd * mx, -1)
            verts.append((x * mx, y, z + ZC))
    o = lambda i, j: i * (NT + 1) + j
    n_ = lambda i, j: base_in + i * (NT + 1) + j
    for i in range(NS):
        for j in range(NT):
            _quad(faces, o(i, j), o(i, j + 1), o(i + 1, j + 1), o(i + 1, j),
                  verts, (0, 1, 0))
    # 縁（s=1）の帯：外へ向ける
    for j in range(NT):
        thd = (-THMAX + (j + 0.5) / NT * 2 * THMAX) * mx
        w = (math.sin(math.radians(thd)) * mx, 0.0, -math.cos(math.radians(thd)))
        _quad(faces, o(NS, j), o(NS, j + 1), n_(NS, j + 1), n_(NS, j), verts, w)
    # 背（θ=±THMAX）の帯：横へ向ける
    for i in range(NS):
        _quad(faces, o(i, 0), o(i + 1, 0), n_(i + 1, 0), n_(i, 0), verts, (-mx, 0, 0))
        _quad(faces, o(i, NT), o(i + 1, NT), n_(i + 1, NT), n_(i, NT), verts, (mx, 0, 0))
    return _mesh(name, verts, faces)


def set_grad_uv(me, mx):
    """g を頂点座標から引き直して UV.x に焼く（remove_doubles 後でも狂わない）"""
    lay = me.uv_layers.new(name="grad")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            x, zz = co.x * mx, co.z - ZC
            thd = math.degrees(math.atan2(x, -zz))
            r = math.hypot(x, zz)
            Lv = L_of(thd) or 1.0
            lay.data[li].uv = (g_of(min(1.0, r / Lv), thd), 0.5)


def link(me, name, mat, smooth_ang=1.0):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.clear(); ob.data.materials.append(mat)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_ang)
    except Exception:
        pass
    return ob


parts, groups = [], []
for k, P in enumerate(PAIR):
    me_i = inner_mesh("m_uchi_%d" % k, P["mx"]); set_grad_uv(me_i, P["mx"])
    ob_i = link(me_i, "uchi_%d" % k, mat_glow, 1.20)
    ob_o = link(outer_mesh("m_kara_%d" % k, P["mx"]), "kara_%d" % k, mat_kai, 0.90)
    groups.append((ob_i, ob_o))
    parts += [ob_i, ob_o]

# --- キーフレーム（毎フレーム・剛体だけ。イージング無し＝ループの不変条件）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, ix in enumerate(FR_):
    t = ix / N_FRAMES
    for k in range(len(PAIR)):
        loc, eul = pose_of(k, t)
        for ob in groups[k]:
            ob.location = loc
            ob.rotation_euler = eul
            ob.keyframe_insert("location", frame=f + 1)
            ob.keyframe_insert("rotation_euler", frame=f + 1)
# 🔴 Blender 5.x の Action は slotted なので `.fcurves` は無い（AttributeError）。
#    補間は keyframe_insert の前に置いた keyframe_new_interpolation_type='LINEAR' が効く。

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
        caption("MIDDLE STUDY 089 — KAIAWASE", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = (AIM_X, 0.0, LOOK_Z)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)
# 🔴 #67①：二枚のあいだが抜けている＝面光源がそのままカメラに写って白い帯になる
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は発光体の外。
#    🔴 貝の裏（y=+0.42）に置くと、床のライムは 150W でも 0.09%＝検知器が鳴る。
#       片方が伏せ貝＝発光面が奥を向いているので、床を照らしていたのは光源でなく**発光面**のほうだった。
#       手前・下（y=−0.25 / z=0.55）へ移すと、同じW数で床に落ちる。
#    🔴 そのW数を貝に当てると、伏せ貝が抹茶色になる（001 の教訓）。**床だけに当てる**
#       ＝ライトリンクで受け手を床に限定する（#56 の書き方を逆向きに使う）。
#    🔴 そのW数を貝の近くで焚くと、伏せ貝が抹茶色になる（001 の教訓。黒面積が 5.0→3.4% に落ちて
#       数字にも出た）。🔴 ライトリンク（#56 の書き方）は**効かない**——receiver_collection を
#       与えた瞬間、その中に入れた床にも光が来なくなる（Blender 5.1.1 で実測：600W で 4.26%→0.10%）。
#    🔴 効いたのは置き場所のほう。**画面に写っている床は被写体より 15〜38m 奥**
#       （カメラ軸が水平なので手前の床は枠の下）。だから奥の床を照らすスポットを
#       **貝より奥に置き、奥へ向ける**＝貝はコーンの後ろに居るので1ルクスも当たらない。
bpy.ops.object.light_add(type='SPOT', location=(AIM_X, 2.50, 1.20))
sp = bpy.context.active_object
sp.name = "lime_floor"
sp.data.energy = LIME_W * 2.0
sp.data.spot_size = math.radians(88)
sp.data.spot_blend = 1.0
sp.data.shadow_soft_size = 1.20
sp.data.color = LIME[:3]
sp.data.specular_factor = 0.0
sp.visible_camera = False
sp.rotation_euler = (Vector((AIM_X, 22.0, 0.0)) - sp.location).to_track_quat('-Z', 'Y').to_euler()

# 貝のまわりの空気（弱く。これは色が乗らない範囲）
for sx, sy, sz in ((AIM_X - 0.70, -0.25, 0.60), (AIM_X + 0.70, -0.25, 0.60)):
    bpy.ops.object.light_add(type='POINT', location=(sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f" % sx
    lp.data.energy = LIME_W * 0.22
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

print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME, " ZC %.4f" % ZC,
      " 頂点 %d  面 %d" % (sum(len(o.data.vertices) for o in parts),
                          sum(len(o.data.polygons) for o in parts)))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 61, 91):
        scene.frame_set(fr); dg.update()
        allx, ally, per = [], [], []
        for gi, gp in enumerate(groups):
            gx = []
            for ob in gp:
                ev = ob.evaluated_get(dg)
                for v in list(ev.data.vertices)[::7]:
                    c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                    allx.append(c.x); ally.append(c.y); gx.append(c.x)
            per.append((min(gx), max(gx)))
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        gap = per[1][0] - per[0][1]
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  "
              "重心x %.1f%% 重心y（上から）%.1f%%  二枚のすきま %.1f%%"
              % (fr, x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100, edge,
                 (x0 + x1) / 2 * 100, (1 - (y0 + y1) / 2) * 100, gap * 100))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_089.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.55
    for gi, gp in enumerate(groups):
        gp[0].data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=False,
                                  export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
