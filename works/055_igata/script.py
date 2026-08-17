# =============================================================
# monaka design. — MIDDLE STUDY 055 "IGATA"（鋳型 a two-part bell mould）
#
# 黒い鋳型が、ふたつ。鉄の枠に、土を突き固めたもの。
# 型がひらくと、合わせ面に彫られた**空洞**が現れる。梵鐘のかたちをした、へこみ。
# **型そのものには、かたちが無い。**あるのは、鐘の"外側"だけだ。
# ライム #A5E02E が満ちているのは、その空洞——つまり、**まだ何も無い場所**。
# 型が閉じれば、光は合わせ目の一本だけになる。
# **鐘になるのは、ふたつの型の、あいだにしかない。**
#
# 【ドメイン】鋳造・鋳型（シリーズ未踏）。直近10作（植物・果実／漁労・浮子／楽器・打／
#   貨幣・銭／玩具・けん玉／武・弓／農・製粉／商い・暖簾／書物・巻子／土木・橋）と別。
#   🔴 020 TSUGITE【木工・継手】は「離すと**実体（ほぞ）**が現れる」。
#      055 は「離すと**空洞**が現れる」＝**正負の反転**。同じ開閉でも主題が逆。
#   🔴 036 SAYA【鞘】は「収める」機構。ここに収まる物は、まだ存在しない。
#
# 【光の型＝窓】#53：直近5作の 内包／面／稜線／芯／背光 と、直近10作で5回出た 隙間 は選べない。
#   窓＝「黒に開いた孔の"形"が光る。孔の形が主役」（017 KAGIANA／031 TOURO）。
#   ここでの孔の輪郭は**これから生まれる梵鐘のシルエットそのもの**＝孔の形が主役、の極北。
#   🔴 孔の縁（合わせ面 x=0）で ES を厳密に落とす（b=0）ので、**平らな合わせ面に緑が1画素も乗らない**。
#      光は空洞の"中"だけに棲む＝隙間（2つの塊の間に光の板がある型）と機構が逆であることの担保。
#
# 【構図＝対】🔴 #57：54作のうち **51作が「全身」**（1個の物が枠の中央に丸ごと）。
#   「対」は**シリーズ初**。2つの塊を離し、**その間**を主題にする＝タグラインの直訳。
#   合格条件は 塊がちょうど2つ・大きい方が72%以下。
#   🔴 これは構図のために物を2つ置いたのではない。**割型は2つでなければ成立しない。**
#
# 【機構＝ひらく（型抜き）】光の量を2つの独立な幾何が同時に動かす。
#   ① 各半型が**後端の蝶番まわりに外へ倒れる**＝合わせ面がカメラを向いていく（facing が増える）
#   ② 同時に左右へ**引き抜かれる**（SEP）＝互いの遮蔽が外れる
#   θ(t)=θmin+(θmax−θmin)·a(t)、SEP(t)=smin+(smax−smin)·a(t)、a(t)=0.5(1−cos2πt) の整数周期＝
#   厳密に閉じる。**回転キーと位置キーだけ**なので glb にそのまま乗る（#60）。
#   さらに全体の微かな首振り SWAY·sin(2πt)（t=0,1 で厳密に 0・cos位相と直交するので静止しない）。
#   🔴 完全には閉じない（GAP_MIN）。閉じ切った瞬間も**合わせ目に一本だけ光が残る**＝真ん中に光。
#
# 【造形】boolean を1つも使わない（#15/#37②）。
#   空洞は**半回転体（φ∈[90°,270°]）そのもの**＝孔の縁が数式で厳密に出る。
#   合わせ面は、その縁を境に**行ごとの2本の帯**で張る＝孔の輪郭にジャギーが出ない。
#   梵鐘の記号（上帯・下帯・乳4×...・撞座）は半径への加算 Δ(z,φ) で入れる＝型では**へこみ**になる。
#
# 🔴 #52 の例外：黒の肌（SUBSURF＋DISPLACE）を**土の塊には掛けない**。
#   この作の主役は「孔の輪郭」で、SUBSURF は輪郭を丸め、DISPLACE は縁をがたつかせる。
#   質感は**鉄の枠（鋳枠 flask）側**で出す＝実物どおり「鉄の枠＋突き固めた土」の2素材（MATERIALS.md 掟4の例外）。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 鐘（＝空洞）------------------------------------------------
# 🔴 大きさは「開いたときの左右の広がり」で決まる（1周目の実測）。
#    半幅 = D·cosθ + W·sinθ + SEP で、**面を見せるほど（θを上げるほど）横に伸びる**。
#    R=0.42 で θ=40° にしたら広がりが 2.72m ＝ 枠の 97%（合格は 44〜66%）。
#    θ は「面がカメラを向く量」＝光の量そのものなので下げられない。**鐘の側を縮める。**
# 🔴🔴 2周目の最大の失敗＝**空洞が「凸」に見えた**（緑の鐘が手前に出ているように読める）。
#    原因は陰影ではなく**比率**：合わせ面の幅 0.78 に対して孔が 0.56＝面の85%を孔が占めていて、
#    「孔が開いている平面」が画面に存在しなかった（＝ただの開いた箱に見える）。
#    017 KAGIANA が成立したのは、**板が板として見えていたから**。
#    → 孔を小さくし、**黒い平面を主役の面積で残す**（孔／面 = 60%）。
#    横幅は「開くほど広がる」ので鐘を縮めるしかない：半幅 = D·cosθ + W·sinθ + SEP ≤ 0.925。
#    その制約下で**画面に映る空洞の幅 2R·sinθ を最大化すると θ は大きいほど良い**（56°で最適近傍）。
# 🔴🔴🔴 3周目：孔の比率は直ったが、今度は**電球／ボウリングのピン**に見えた。
#    原因は湯口が**鐘の軸の真上に立っている**こと＝鐘の輪郭と湯口が1本の輪郭に繋がり、
#    「胴＋首」＝瓶の記号になる。梵鐘に首は無いのに、湯口が首を作っていた。
#    → ① 鐘を寸胴に（H/口径 1.75→1.41＝短くすると横に見えて鐘に読める）
#      ② 湯口を**軸から蝶番側へ寄せて立てる**＝鐘の輪郭が笠形で閉じ、湯口は別の「溝」になる
R_MAX = 0.195          # 口縁の半径
H_BELL = 0.55          # 口縁 → 笠形の頂（H/口径 = 1.41）
RS0, RS_MID, RS1 = 0.020, 0.013, 0.055   # 湯口：笠形の頂に**段差で**開く細い湯道 → 天で漏斗
SPRUE_L = 0.42         # 湯口の長さ（立ち上がる押湯）
LEAN = 0.115           # 湯口が軸から蝶番側へ寄る量（＝鐘の輪郭から切り離す）

# --- 型の塊（鋳枠に突き固めた土）--------------------------------
W_FACE = 0.80          # 鋳枠の外法（y）。蝶番 y=0 → 手前の端 y=-W_FACE
D_BODY = 0.28          # 土の奥行き（x）。R_MAX より深くないと空洞が背中に抜ける
Z_BOT = -0.26          # 鋳枠の下端
Z_TOP = H_BELL + SPRUE_L
CLAY_EPS = 0.003       # 鉄と土のあいだの見切り（同一平面にすると z ファイティング）

# --- 鋳枠（flask・鉄）------------------------------------------
# 🔴 **天は無い**（＝湯を注ぐために開いている）。実物どおりで、湯口が天まで抜けられる。
FT, FP, FD = 0.075, 0.022, 0.28   # 桁の見付け幅／合わせ面から出る量／奥行き
CY0 = -W_FACE + FT + CLAY_EPS     # 土の合わせ面（手前の端）
CY1 = -FT - CLAY_EPS              # 土の合わせ面（蝶番側の端）
CZ0 = Z_BOT + FT + CLAY_EPS       # 土の下端
CZ1 = Z_TOP                       # 土の上端（天は開いている）
YC = (CY0 + CY1) / 2.0            # 鐘の軸（合わせ面の中央）

# --- 合わせ面のダボ（位置決め）＝「割型である」ことの記号 --------
DOW_R, DOW_L, DOW_DY = 0.016, 0.012, 0.24
DOW_Z = (0.050, 0.120)   # 下＝土の下端から／上＝笠形の少し上（湯口が細い所）

# --- ひらく ----------------------------------------------------
TH_MIN, TH_MAX = 1.4, 56.0     # 各半型の外倒し（度）
SEP_MIN, SEP_MAX = 0.026, 0.075  # 左右への引き抜き（m）。閉でも 2×SEP_MIN の隙が残る
SWAY_DEG = 2.6

# --- 光（空洞の内壁）-------------------------------------------
ES_CORE = 5.20
Z_HOT = 0.50 * H_BELL  # 鐘の腹＝いちばん明るい高さ
FZ = 0.62              # 縦の減衰の尺（|a|=1 で 0 に落ちる）。押湯は A_BASE まで落ちて細い線に残る
A_BASE = 0.14          # 上下の端に残す下限（0 にすると縁が死ぬ＝#49）
B_KNEE = 0.95          # 合わせ面の縁（b=0）から、どれだけ奥で満ちるか（奥ほど明るい＝手前から奥への勾配）
EDGE_LO = 0.045        # 縁の下限。ほぼ 0＝平らな合わせ面に緑を乗せない
# 🔴 1周目：発光は UV（z と φ）だけの関数だったので**面の向きが絵に出ず、
#    空洞が「バックライトの平板」になった**（乳も帯も撞座も1つも見えない）。
#    純発光体は陰影を持たないので、**法線に依存する項を明示的に入れないと形が消える。**
# 🔴 2周目に 0.20/0.85 まで強くしたら、今度は**凸に見える**方向へ効いた
#    （へこみの最深部がいちばんカメラを向く＝ふくらみと同じ陰影になる）。
#    立体は「面の向き」ではなく**平面＋孔という構造**で読ませ、この項は乳と帯が見える最小限に留める。
FAC_LO, FAC_P = 0.34, 1.0    # カメラを向いた面ほど明るい（＝乳・帯・撞座が見える）

# --- 梵鐘の記号（型では「へこみ」になる）------------------------
BAND_H = 0.0072        # 上帯・下帯
BAND_LO = (0.150, 0.205)
BAND_HI = (0.735, 0.790)
BOSS_H, BOSS_R = 0.0085, 0.027     # 乳（ち）
BOSS_PHI = (135.0, 225.0)          # この半型に見える2区。区の中で3列
BOSS_DPHI = 15.0
BOSS_V = (0.600, 0.652, 0.704)
TSUKIZA_H, TSUKIZA_R = 0.0065, 0.045  # 撞座（φ=180＝空洞のいちばん奥）
TSUKIZA_V = 0.330

FPS = 24
N_FRAMES = 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.0, 1.90
Z_BASE = 1.505         # ローカル z=0（鐘の口縁）の world z
LIME_W = 170.0         # 随伴のライム光源（#58）。**発光体の外**に置く

NZ, NPHI = 176, 108    # 空洞のグリッド（子午線 × 周）

# 梵鐘の輪郭（v=z/H_BELL, r/R_MAX）。口が少し広がり、長い胴、肩で締まって笠形へ
CP = [(0.00, 1.000), (0.030, 0.930), (0.09, 0.906), (0.18, 0.900), (0.30, 0.897),
      (0.45, 0.894), (0.58, 0.890), (0.68, 0.884), (0.76, 0.872), (0.83, 0.850),
      (0.885, 0.818), (0.93, 0.762), (0.965, 0.680), (0.99, 0.560), (1.00, 0.470)]
_XS = [p[0] for p in CP]
_YS = [p[1] for p in CP]


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def ss(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def _hermite(xs, ys, x):
    n = len(xs)
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    i = 0
    while i < n - 2 and x > xs[i + 1]:
        i += 1
    h = xs[i + 1] - xs[i]
    t = (x - xs[i]) / h
    m0 = (ys[i + 1] - ys[i - 1]) / (xs[i + 1] - xs[i - 1]) if i > 0 else (ys[1] - ys[0]) / (xs[1] - xs[0])
    m1 = ((ys[i + 2] - ys[i]) / (xs[i + 2] - xs[i]) if i + 2 < n
          else (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]))
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h * m0
            + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h * m1)


def _win(v, lo, hi, soft=0.012):
    """[lo,hi] の帯。端を soft でなます。"""
    return ss((v - lo) / soft) * ss((hi - v) / soft)


def r_bell(z):
    if z < 0.0 or z > H_BELL:
        return 0.0
    return R_MAX * _hermite(_XS, _YS, z / H_BELL)


def r_sprue(z):
    """湯口：笠形の頂から細い管に絞り、長く立ち上がって、天でだけ漏斗に開く。"""
    if z <= H_BELL or z > Z_TOP:
        return 0.0
    s = (z - H_BELL) / SPRUE_L
    return (RS0 + (RS_MID - RS0) * ss(s / 0.16)
            + (RS1 - RS_MID) * ss((s - 0.70) / 0.30))


def r_eff(z, phi):
    """空洞の半径。梵鐘の記号は**半径への加算**で入れる（型ではへこみになる）。"""
    if z > H_BELL:
        return r_sprue(z)
    r = r_bell(z)
    if r <= 0.0:
        return 0.0
    v = z / H_BELL
    d = 0.0
    d += BAND_H * _win(v, *BAND_LO)                       # 下帯
    d += BAND_H * _win(v, *BAND_HI)                       # 上帯
    ph = math.degrees(phi) % 360.0
    for pc in BOSS_PHI:                                   # 乳（3列 × 3段）
        for jc in (-1, 0, 1):
            c = pc + jc * BOSS_DPHI
            da = (ph - c + 180.0) % 360.0 - 180.0
            arc = math.radians(da) * R_MAX
            if abs(arc) > BOSS_R:
                continue
            for vr in BOSS_V:
                dz = (v - vr) * H_BELL
                dd = math.hypot(arc, dz)
                if dd < BOSS_R:
                    d += BOSS_H * (1.0 - ss(dd / BOSS_R))
    da = (ph - 180.0 + 180.0) % 360.0 - 180.0             # 撞座（空洞のいちばん奥）
    arc = math.radians(da) * R_MAX
    dz = (v - TSUKIZA_V) * H_BELL
    dd = math.hypot(arc, dz)
    if dd < TSUKIZA_R:
        d += TSUKIZA_H * (1.0 - ss(dd / TSUKIZA_R))
    return r + d


def yoff(z):
    """湯口の横ずれ。鐘の高さまでは 0（＝鐘は回転体のまま）、その上は**直線で**蝶番側へ寄る。
       🔴 5周目は smoothstep で寄せたので湯道が S字にうねり、**吊りコード**に見えた
          （鐘は電球に転ぶ）。溝は工具で引いた線なので、まっすぐでなければ溝に読めない。"""
    if z <= H_BELL:
        return 0.0
    return LEAN * min(1.0, (z - H_BELL) / (SPRUE_L * 0.90))


def uvx_of(z):
    """発光の縦の座標。🔴 湯道は**鐘より速く暗くなる**ようにする＝主役は鐘の空洞で、
       湯道は「そこへ湯が入る道」であって光そのものではない（明るいままだとコードに見える）。"""
    if z <= H_BELL:
        return (z - Z_HOT) / FZ
    return (H_BELL - Z_HOT) / FZ + (z - H_BELL) / (FZ * 0.45)


def ycen(z):
    return YC + yoff(z)


def r_edge(z):
    """合わせ面（x=0）における孔の縁。φ=90° の実効半径そのもの＝縁が数式で厳密に出る。"""
    return r_eff(z, math.pi / 2)


def a_of(t):
    return 0.5 * (1.0 - math.cos(2 * math.pi * t))


def theta_of(t):
    return math.radians(TH_MIN + (TH_MAX - TH_MIN) * a_of(t))


def sep_of(t):
    return SEP_MIN + (SEP_MAX - SEP_MIN) * a_of(t)


def sway_of(t):
    return math.radians(SWAY_DEG) * math.sin(2 * math.pi * t)


# --- 半型の姿勢（S=+1 左／S=-1 右）------------------------------
# ローカル：合わせ面 x=0（法線 +X）・胴 x∈[-D,0]・面 y∈[-W,0]（蝶番 y=0）・z∈[Z_BOT,Z_TOP]
# world  ：x を S 倍してから、Z 軸まわりに -S·θ 回し、x を -S·SEP ずらし、Z_BASE 持ち上げる
def place(S, t):
    th = -S * theta_of(t) + sway_of(t)
    return (S, th, -S * sep_of(t))


def to_world(S, th, dx, p):
    x, y, z = S * p[0], p[1], p[2]
    c, s = math.cos(th), math.sin(th)
    return (x * c - y * s + dx, x * s + y * c, z + Z_BASE)


def to_world_dir(S, th, d):
    x, y, z = S * d[0], d[1], d[2]
    c, s = math.cos(th), math.sin(th)
    return (x * c - y * s, x * s + y * c, z)


def to_local(S, th, dx, q):
    x, y, z = q[0] - dx, q[1], q[2] - Z_BASE
    c, s = math.cos(-th), math.sin(-th)
    return (S * (x * c - y * s), x * s + y * c, z)


def visible(t, nz=44, nph=34):
    """#40⑥：カメラから**実際に見えている発光量**を幾何で積分する。
       ① 面の向き（n·v）② 自分の合わせ面による遮蔽（孔を通って出られるか）
       ③ 相手の半型（直方体）による遮蔽 の3つを実際に判定する。"""
    tot = 0.0
    poses = [place(+1, t), place(-1, t)]
    for S, th, dx in poses:
        oth = [q for q in poses if q[0] != S][0]
        for iz in range(nz):
            z = Z_TOP * (iz + 0.5) / nz
            rr = r_eff(z, math.pi)
            if rr <= 0.0:
                continue
            dz = Z_TOP / nz
            for ip in range(nph):
                phi = math.pi / 2 + math.pi * (ip + 0.5) / nph
                r = r_eff(z, phi)
                if r <= 0.0:
                    continue
                # 局所座標の点と外向き（空洞の内側を向く）法線
                p = (r * math.cos(phi), ycen(z) + r * math.sin(phi), z)
                n = (-math.cos(phi), -math.sin(phi), 0.0)
                a = uvx_of(z)
                b = -math.cos(phi)
                es = ((A_BASE + (1 - A_BASE) * (1.0 - ss(abs(a))))
                      * (EDGE_LO + (1 - EDGE_LO) * ss(b / B_KNEE)))
                dA = r * (math.pi / nph) * dz
                P = to_world(S, th, dx, p)
                N = to_world_dir(S, th, n)
                vx, vy, vz = CAM_LOC[0] - P[0], CAM_LOC[1] - P[1], CAM_LOC[2] - P[2]
                L = math.sqrt(vx * vx + vy * vy + vz * vz)
                vx, vy, vz = vx / L, vy / L, vz / L
                face = N[0] * vx + N[1] * vy + N[2] * vz
                if face <= 0.0:
                    continue
                # ② 自分の合わせ面（局所 x=0）を、孔の中で抜けられるか
                d_loc = to_local(S, th, dx, (P[0] + vx, P[1] + vy, P[2] + vz))
                o_loc = (S * p[0], p[1], p[2])
                ddx = d_loc[0] - o_loc[0]
                if ddx <= 1e-9:
                    continue
                k = (0.0 - o_loc[0]) / ddx
                ye = o_loc[1] + k * (d_loc[1] - o_loc[1])
                ze = o_loc[2] + k * (d_loc[2] - o_loc[2])
                if abs(ye - ycen(ze)) > r_edge(ze):
                    continue
                # ③ 相手の直方体（局所 x∈[-D,0]・y∈[-W,0]・z∈[Z_BOT,Z_TOP]）を貫かないか
                S2, th2, dx2 = oth
                o2 = to_local(S2, th2, dx2, P)
                d2 = to_local(S2, th2, dx2, (P[0] + vx, P[1] + vy, P[2] + vz))
                lo = (-FD, -W_FACE, Z_BOT)          # 相手は鋳枠の外法で見る（土より大きい方）
                hi = (FP, 0.0, Z_TOP)
                t0, t1 = 1e-4, 1e9
                blocked = True
                for ax in range(3):
                    dd = d2[ax] - o2[ax]
                    if abs(dd) < 1e-9:
                        if o2[ax] < lo[ax] or o2[ax] > hi[ax]:
                            blocked = False
                            break
                        continue
                    ta = (lo[ax] - o2[ax]) / dd
                    tb = (hi[ax] - o2[ax]) / dd
                    if ta > tb:
                        ta, tb = tb, ta
                    t0, t1 = max(t0, ta), min(t1, tb)
                    if t0 > t1:
                        blocked = False
                        break
                if blocked:
                    continue
                tot += es * face * dA
    return tot


_VS = [visible(i / N_FRAMES) for i in range(N_FRAMES)]
_VMAX = max(_VS)
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _VS[i]) + 1

if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d (t=%.3f)" % (STILL_FRAME, (STILL_FRAME - 1) / N_FRAMES))
    print(">> #40(6) 見える光 min/max = %.3f  （合格 0.75以下）" % (min(_VS) / _VMAX))
    print(">> ループの閉じ: a(0)=%.5f a(1)=%.5f  sway(0)=%.5f sway(1)=%.5f  θ(0)=%.2f° θ(1)=%.2f°"
          % (a_of(0), a_of(1), sway_of(0), sway_of(1),
             math.degrees(theta_of(0)), math.degrees(theta_of(1))))
    print(">> 鐘 R=%.3f H=%.3f  型 W=%.2f D=%.2f  z %.2f..%.2f（高さ %.2f）"
          % (R_MAX, H_BELL, W_FACE, D_BODY, Z_BOT, Z_TOP, Z_TOP - Z_BOT))
    # 開いたときの左右の広がり（純mathの見積り。実測は probe の投影bboxで）
    for tt in (0.0, 0.5):
        th = theta_of(tt)
        xs = []
        for S in (+1, -1):
            _, TH, DX = place(S, tt)
            for p in [(0, 0, 0), (0, -W_FACE, 0), (-D_BODY, 0, 0), (-D_BODY, -W_FACE, 0)]:
                xs.append(to_world(S, TH, DX, p)[0])
        print("   t=%.1f  θ=%4.1f°  引き抜き %.3f  左右の広がり %.3f m（枠 2.81 の %.0f%%）"
              % (tt, math.degrees(th), sep_of(tt), max(xs) - min(xs),
                 (max(xs) - min(xs)) / 2.81 * 100))
    print(">> 縦の広がり %.3f m（枠 3.52 の %.0f%%）"
          % (Z_TOP - Z_BOT, (Z_TOP - Z_BOT) / 3.52 * 100))
    print(">> 孔の縁 r_edge: v=0.00 %.3f / 0.18 %.3f / 0.50 %.3f / 0.76 %.3f / 0.95 %.3f"
          % tuple(r_edge(v * H_BELL) for v in (0.0, 0.18, 0.50, 0.76, 0.95)))
    print(">> 枠の内法まで  手前 %.3f / 蝶番側 %.3f （0 を割ると鋳枠が孔に食い込む）"
          % ((YC - r_edge(H_BELL * 0.0)) - (-W_FACE + FT), (-FT) - (YC + r_edge(0.0))))
    for i in range(0, N_FRAMES, 10):
        t = i / N_FRAMES
        print("   t=%.3f  θ %5.1f°  引き抜き %.3f  見える光 %5.1f%%"
              % (t, math.degrees(theta_of(t)), sep_of(t), 100 * _VS[i] / _VMAX))
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
BLACK_RECIPES = {
    "base":   dict(rough=0.36, spec=0.15, coat=0.05),
    "urushi": dict(rough=0.30, spec=0.34, coat=0.05, coat_rough=0.25),
    "touki":  dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10),
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25, disp=0.004, dsize=0.05),
    "nuno_usu": dict(rough=0.66, spec=0.28, sheen=0.55, sheen_rough=0.25),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
}
# 実物どおりの2素材（掟4の例外）：突き固めた土＝陶／鋳枠＝鉄
CLAY, IRON = "touki", "tetsu"
# 🔴 #62③/#63④ と同じ罠：レシピは径0.3の球で測った値で、**平らな大面には効き方が違う**。
#    touki の 0.58/0.26 を 0.6m の平面に当てたら、キーライトの広いハイライトを面で返して
#    2周・3周とも**角の丸いつやのある樹脂の箱**に見えた。突き固めた真土は艶が無い。
#    粗さを上げ、下がる黒は金属度で戻す（#57②：#0a0a0a の金属はグレー環境を映しても黒いまま）。
BLACK_RECIPES["touki"] = dict(rough=0.72, spec=0.20, metal=0.18)


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def set_black(p, recipe):
    r = BLACK_RECIPES[recipe]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)
    if r.get("sheen"):
        p.inputs["Sheen Weight"].default_value = r["sheen"]
        p.inputs["Sheen Roughness"].default_value = r.get("sheen_rough", 0.25)
    return p


def black_material(name, recipe):
    m, p = principled(name)
    set_black(p, recipe)
    return m


mat_clay = black_material("clay", CLAY)
mat_iron = black_material("iron", IRON)


def cavity_material(name):
    """空洞の内壁＝発光。勾配は**UVに焼いた2軸**（#34/#39）。
       u = (z-Z_HOT)/FZ ：鐘の腹が芯。|u|=1 で 0（＝口縁と湯口の天が落ちる）
       v = -cosφ        ：0 が合わせ面の縁・1 が空洞のいちばん奥
       🔴 v=0 で ES をほぼ 0 にする＝**平らな合わせ面に緑が乗らない**（窓の型の担保・#49の裾は黒の上）"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)
    p.inputs["Roughness"].default_value = 0.55
    p.inputs["Specular IOR Level"].default_value = 0.10
    p.inputs["Emission Color"].default_value = LIME

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    def mr(lo, hi, a, b):
        n = nt.nodes.new("ShaderNodeMapRange")
        n.interpolation_type = 'SMOOTHSTEP'; n.clamp = True
        n.inputs["From Min"].default_value = lo; n.inputs["From Max"].default_value = hi
        n.inputs["To Min"].default_value = a; n.inputs["To Max"].default_value = b
        return n

    ab = mn('ABSOLUTE'); nt.links.new(xyz.outputs["X"], ab.inputs[0])
    fz = mr(0.0, 1.0, 1.0, 0.0)                       # 縦：腹が1 → 端で0
    nt.links.new(ab.outputs[0], fz.inputs["Value"])
    fzs = mn('MULTIPLY', 1.0 - A_BASE); nt.links.new(fz.outputs["Result"], fzs.inputs[0])
    fza = mn('ADD', A_BASE); nt.links.new(fzs.outputs[0], fza.inputs[0])

    fb = mr(0.0, B_KNEE, 0.0, 1.0)                    # 奥行き：縁が0 → 奥で1
    nt.links.new(xyz.outputs["Y"], fb.inputs["Value"])
    fbs = mn('MULTIPLY', 1.0 - EDGE_LO); nt.links.new(fb.outputs["Result"], fbs.inputs[0])
    fba = mn('ADD', EDGE_LO); nt.links.new(fbs.outputs[0], fba.inputs[0])

    # 🔴 面の向きに依存する項（#49 の裏返し）。**純発光体は陰影を持たない**ので、
    #    これが無いと空洞が「バックライトの平板」になり、乳も帯も撞座も1つも見えない（1周目の実測）。
    #    ここは 054 と逆で、**カメラを向いた面ほど明るい**＝へこみが立体に読める向きにする。
    lw = nt.nodes.new("ShaderNodeLayerWeight")            # Facing：1＝カメラに正対
    lw.inputs["Blend"].default_value = 0.5
    fcp = mn('POWER', FAC_P); nt.links.new(lw.outputs["Facing"], fcp.inputs[0])
    fcs = mn('MULTIPLY', 1.0 - FAC_LO); nt.links.new(fcp.outputs[0], fcs.inputs[0])
    fca = mn('ADD', FAC_LO); nt.links.new(fcs.outputs[0], fca.inputs[0])

    e1 = mn('MULTIPLY'); nt.links.new(fza.outputs[0], e1.inputs[0])
    nt.links.new(fba.outputs[0], e1.inputs[1])
    e0 = mn('MULTIPLY'); nt.links.new(e1.outputs[0], e0.inputs[0])
    nt.links.new(fca.outputs[0], e0.inputs[1])
    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e0.outputs[0], e2.inputs[0])
    nt.links.new(e2.outputs[0], p.inputs["Emission Strength"])
    return m


mat_cav = cavity_material("cavity")

mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
def finish(bm, name, mat, bevel=0.0025, angle=35, smooth=True):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    sharp = []
    for e in bm.edges:
        try:
            if e.calc_face_angle() > math.radians(angle):
                sharp.append(e)
        except Exception:
            pass
    if sharp and bevel > 0:                       # #17：稜線が光を拾わないと黒はプラスチックになる
        bmesh.ops.bevel(bm, geom=sharp, offset=bevel, segments=2,
                        affect='EDGES', clamp_overlap=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat)
    if smooth:
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        try:
            # 🔴 0.6rad(34°) だとベベル面まで滑らかに繋がり、箱が**角の丸い樹脂**に見えた（2周目）。
            #    20° に落として稜線を稜線のまま残す。
            bpy.ops.object.shade_auto_smooth(angle=0.35)
        except Exception:
            pass
        ob.select_set(False)
    return ob


def box(bm, S, x0, x1, y0, y1, z0, z1):
    """軸平行の直方体。x は S 倍（左右の半型は x の鏡像）。"""
    v = {}
    for i, x in enumerate((x0, x1)):
        for j, y in enumerate((y0, y1)):
            for k, z in enumerate((z0, z1)):
                v[(i, j, k)] = bm.verts.new((S * x, y, z))
    q = [((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)),
         ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)),
         ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)),
         ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
         ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)),
         ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1))]
    for f in q:
        bm.faces.new([v[i] for i in f])


ZS = [CZ0 + (CZ1 - CZ0) * i / NZ for i in range(NZ + 1)]
HOLE = [(ycen(z) - r_edge(z), ycen(z) + r_edge(z)) for z in ZS]


def make_block(S, name):
    """土の塊（鋳枠の内側に突き固めた真土）。
       合わせ面（x=0）は、孔の縁を境に**行ごとの2本の帯**で張る＝輪郭にジャギーが出ない。"""
    bm = bmesh.new()
    face = []
    for i, z in enumerate(ZS):
        ylo, yhi = HOLE[i]
        face.append((bm.verts.new((0.0, CY0, z)),
                     bm.verts.new((0.0, ylo, z)),
                     bm.verts.new((0.0, yhi, z)),
                     bm.verts.new((0.0, CY1, z))))
    for i in range(NZ):
        A, B = face[i], face[i + 1]
        bm.faces.new((A[0], A[1], B[1], B[0]))          # 手前側の帯
        bm.faces.new((A[2], A[3], B[3], B[2]))          # 蝶番側の帯
    # 背・両側・底（天は湯口の切り欠きがあるので別扱い）
    b = {}
    for j, y in enumerate((CY0, CY1)):
        for k, z in enumerate((CZ0, CZ1)):
            b[(j, k)] = bm.verts.new((-D_BODY, y, z))
    bm.faces.new((b[(0, 0)], b[(0, 1)], b[(1, 1)], b[(1, 0)]))                 # 背
    bm.faces.new((face[0][0], b[(0, 0)], b[(1, 0)], face[0][3]))               # 底
    bm.faces.new((face[0][0], face[0][1], face[0][2], face[0][3]))             # 底の合わせ面側の閉じ
    bm.faces.new((b[(0, 0)], face[0][0], face[NZ][0], b[(0, 1)]))              # 手前の側面
    bm.faces.new((b[(1, 0)], b[(1, 1)], face[NZ][3], face[0][3]))              # 蝶番側の側面
    # 天：湯口の切り欠き（|y-YC| <= re）を避けて3枚
    T = face[NZ]
    tlo, thi = HOLE[NZ]
    ret = (thi - tlo) / 2.0
    tb = [bm.verts.new((-D_BODY, y, CZ1)) for y in (CY0, tlo, thi, CY1)]
    tn = [bm.verts.new((-ret, y, CZ1)) for y in (tlo, thi)]
    bm.faces.new((T[0], tb[0], tb[1], T[1]))
    bm.faces.new((T[2], tb[2], tb[3], T[3]))
    bm.faces.new((tb[1], tb[2], tn[1], tn[0]))
    bm.faces.new((T[1], tn[0], tn[1], T[2]))            # 切り欠きの小口（湯口の漏斗の縁）
    # 合わせ面のダボ（位置決め）。孔を避けて上下に2本ずつ＝「割型である」ことの記号
    for zz in (CZ0 + DOW_Z[0], H_BELL + DOW_Z[1]):
        for dy in (-DOW_DY, DOW_DY):
            ring = []
            for k in range(24):
                a = 2 * math.pi * k / 24
                ring.append((bm.verts.new((0.0, YC + dy + DOW_R * math.cos(a),
                                           zz + DOW_R * math.sin(a))),
                             bm.verts.new((DOW_L, YC + dy + DOW_R * 0.82 * math.cos(a),
                                           zz + DOW_R * 0.82 * math.sin(a)))))
            cap = bm.verts.new((DOW_L, YC + dy, zz))
            for k in range(24):
                a0, a1 = ring[k], ring[(k + 1) % 24]
                bm.faces.new((a0[0], a1[0], a1[1], a0[1]))
                bm.faces.new((a0[1], a1[1], cap))
    for v in bm.verts:                                   # x を S 倍（右の半型は鏡像）
        v.co.x *= S
    # 🔴 孔の縁は border edge（相手の面が無い）ので calc_face_angle が例外→ bevel されない。
    #    ＝**輪郭はベベルで鈍らない**まま、箱の稜線とダボだけが光を拾う（#17）
    return finish(bm, name, mat_clay, bevel=0.003, angle=35)


def make_cavity(S, name):
    """空洞＝半回転体（φ∈[90°,270°]）。孔の縁が数式で厳密に出る。UVに勾配の2軸を焼く（#34/#39）。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    zs = [Z_TOP * i / NZ for i in range(NZ + 1)]
    grid, uvs = [], {}
    for z in zs:
        row = []
        for j in range(NPHI + 1):
            phi = math.pi / 2 + math.pi * j / NPHI
            r = max(1e-4, r_eff(z, phi))
            vt = bm.verts.new((S * r * math.cos(phi), ycen(z) + r * math.sin(phi), z))
            uvs[vt] = (uvx_of(z), -math.cos(phi))
            row.append(vt)
        grid.append(row)
    for i in range(NZ):
        for j in range(NPHI):
            a, b_, c, d = grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]
            f = bm.faces.new((a, b_, c, d) if S > 0 else (d, c, b_, a))
            for lp in f.loops:
                lp[uvl].uv = uvs[lp.vert]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat_cav)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=1.2)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def make_flask(S, name):
    """鋳枠（flask）＝鉄。土を突き固めて収める枠。**天は開いている**（湯を注ぐため＝湯口が抜ける）。
       合わせ面より FP だけ手前に出る＝閉じたとき土どうしは触れず、鉄の縁だけが当たる。"""
    bm = bmesh.new()
    x0, x1 = -FD, FP
    box(bm, S, x0, x1, -W_FACE, -W_FACE + FT, Z_BOT, Z_TOP)          # 手前の側桁
    box(bm, S, x0, x1, -FT, 0.0, Z_BOT, Z_TOP)                       # 蝶番側の側桁
    box(bm, S, x0, x1, -W_FACE + FT, -FT, Z_BOT, Z_BOT + FT)         # 底桁
    return finish(bm, name, mat_iron, bevel=0.004, angle=35)


# ---------- リグと配置 ----------
rigs, parts, cavs = [], [], []
for S in (+1, -1):
    rig = bpy.data.objects.new("half_%s" % ("L" if S > 0 else "R"), None)
    bpy.context.collection.objects.link(rig)
    rig.location = (0.0, 0.0, Z_BASE)
    blk = make_block(S, "block_%d" % S)
    cav = make_cavity(S, "cavity_%d" % S)
    fls = make_flask(S, "flask_%d" % S)
    for o in (blk, cav, fls):
        o.parent = rig
        parts.append(o)
    rigs.append((S, rig))
    parts.append(rig)
    cavs.append(cav)

# 🔴 鉄の枠だけに実起伏（#52）。土の塊には掛けない——SUBSURF が孔の輪郭を丸め、
#    DISPLACE が縁をがたつかせる。この作の主役は輪郭そのものなので、質感は鉄側で出す。
_ir = BLACK_RECIPES[IRON]
_tex = bpy.data.textures.new("relief_iron", 'CLOUDS')
_tex.noise_scale = _ir["dsize"]
for o in parts:
    if o.type == 'MESH' and o.name.startswith("flask"):
        sub = o.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 2
        # 🔴🔴 既定の Catmull-Clark は**箱を枕形に丸める**。2〜4周とも「角の丸い樹脂の箱」に
        #    見えていた真犯人はマテリアルではなくこれ（鋳枠の桁が丸まって外形線を作っていた）。
        #    起伏のための頂点だけが欲しいので SIMPLE にする＝稜線は稜線のまま残る。
        sub.subdivision_type = 'SIMPLE'
        d = o.modifiers.new("disp", 'DISPLACE')
        d.texture = _tex; d.strength = _ir["disp"]; d.mid_level = 0.5

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    for S, rig in rigs:
        _, th, dx = place(S, t)
        rig.rotation_euler = (0.0, 0.0, th)
        rig.location = (dx, 0.0, Z_BASE)
        rig.keyframe_insert("rotation_euler", frame=f + 1)
        rig.keyframe_insert("location", frame=f + 1)

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


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 0.85), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.68), "logo"),
        caption("MIDDLE STUDY 055 — IGATA", 0.045, (AIM_X, -1.7, 0.57), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0.0, -0.32, Z_BASE + Z_HOT)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）

# 🔴 #58③：随伴のライム光源は**発光体の外**に置く。空洞の口の少し外・下に出し、
#    ひらいたVの真ん中の床を直接照らす。キャプション（y=-1.7）からは離す。
limelamps = []
for sgn in (-1, +1):
    bpy.ops.object.light_add(type='POINT',
                             location=(sgn * 0.36, -0.34, Z_BASE - 0.20))
    lp = bpy.context.active_object
    lp.name = "lime_%d" % sgn
    lp.data.energy = LIME_W
    lp.data.shadow_soft_size = 0.30
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0
    limelamps.append(lp)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = cavs[0]
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

# 🔴 ライムの随伴光源（#58）の受光先。**土の塊だけを外す。**
#    随伴光源は「空洞の光が空間に出ている」を作るための代役なので、
#    合わせ面や背中を外から緑に塗るのは筋が違う（054の失敗＝黒がオリーブ色の樹脂に転ぶ）。
#    🔴 ただし床1枚に絞ってはいけない（#63③：相互反射の経路ごと消えて床のライムが 0.02% に落ちる）。
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and not o.name.startswith("block"):
        lit_by_lime.objects.link(o)
for lp in limelamps:
    lp.light_linking.receiver_collection = lit_by_lime

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
        if o.type != 'MESH' or o.name == "floor":
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 占有  長辺 %.1f%%（合格 44〜66・狙い55〜65）" % (max((x1 - x0), (y1 - y0)) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （どれかが 0 を割ると edge≥1）"
          % (x0, 1 - x1, 1 - y1, y0))
    # 「対」は 塊2つ・大きい方72%以下。2つの半型が画面で分かれているかを見る
    for nm in ("block_1", "block_-1"):
        o = bpy.data.objects[nm].evaluated_get(dg)
        cx = [world_to_camera_view(scene, cam, o.matrix_world @ v.co).x for v in o.data.vertices]
        print(">> %-9s 画面x %.3f..%.3f" % (nm, min(cx), max(cx)))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_055.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("cavity_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.75
    for c in cavs:
        c.data.materials.clear()
        c.data.materials.append(m_em)
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = cavs[0]
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
