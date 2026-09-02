# =============================================================
# MIDDLE STUDY 069 — YAGEN（薬研 / a Japanese drug mill）
#
# 黒い舟形の器が下にあり、その上に黒い車輪が浮いている。二つは触れていない。
#
# 薬研は、薬を粉にする道具。舟の底のV字の溝に薬を入れ、
# 両手で柄を持って車輪を前後に転がす。
#
# 光っているのは、二つの「縁」だけだ。
# 溝のいちばん底を走る一本の線と、車輪のいちばん外を回る一本の輪。
# **この二つは、道具じゅうでただ一箇所、たがいに触れる場所**で、
# そこでしか薬は砕けない。
#
# 車輪は、面では効かない。縁でしか効かない。
# 溝は、口では効かない。底でしか効かない。
# 舟は端まであるのに、光は**真ん中でだけ**明るい。
# **どちらの道具も、効いているのは真ん中の一本だけだ。**
#
# そして薬研は、置いてある姿では何も起きない。
# 車輪が降りて溝に入り、二本の線が重なった一瞬にだけ薬は砕ける。
# ——この絵では、その一瞬を撮っていない。**離れている時間のほうを撮った。**
# 触れる前の、いちばん明るい隙間を。
#
# 🔴 光の型＝**稜線**（#53：68作で6作の最少）
# 🔴 構図の型＝**対**（#57：68作で3作。**68作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／#78 に続く12例目）
#    今日選べたのは 光＝隙間／窓／稜線 × 構図＝全身／天地／対。
#    ・隙間(19) はシリーズの既定でありもう型ではない。全身(51) も同じ。→ 落とす。
#    ・天地は #75② で「このシリーズのカメラでは選んでも意味がない」（背光とだけ組める＝#76⑤）
#      と実測で結論が出ている。背光は今日選べない。→ 天地は落とす。
#    ・窓(7) は 031 TOURO／055 IGATA が「黒い枠＋奥の光る面」で、この題材だと
#      舟に孔を開けることになり薬研でなくなる。
#    ・→ **稜線 × 対**。056 WARIFU も同じ組み合わせだが、あちらは**同じ形が2つ**（割符の
#      合わせ口）で、光は**割れ口の輪郭**。こちらは**違う形が2つ**（受ける器と転がる輪）で、
#      光は**互いに触れる2本の作用線**。稜線が2本あるので #51④ の「線は halo が痩せる」
#      に対しては**輪（周長 4.0）を主役**に置いて面積で戻す。
#
# 🔴 機構＝**転がしと、器の煽り**。どちらも整数周期・厳密に閉じる。
#    ・車輪：x(t)=A·sin2πt を溝方向に往復し、回転は θ=−x/R＝**滑らない転がり**。
#      さらに 真ん中を通るときだけ沈む：gap(t)=G_LO+(G_HI−G_LO)·sin²2πt
#      （sin² は周期 1/2 で厳密に閉じる。t=0,0.5＝溝の真ん中で最も低い＝「効いている瞬間」）
#    ・器：ρ(t)=ROLL0+ROLL_A·cos2πt。長軸まわりに煽る＝溝の底が見えたり隠れたりする。
#      🔴 **これが #40⑥ の唯一の駆動源**。車輪は縁の上に浮いているので溝を遮蔽しない
#      （遮蔽で光を振らせようとすると必ず塊が1つに繋がり、#57「対」の clusters==2 を割る）。
#    位置・回転キーだけ＝シェイプキー不要でそのまま glb に乗る（#60）。
#
# 🔴 #34「カメラに正対する細長い発光面は幅方向にも落として芯を残さないとテープになる」
#    ＝どちらの発光も「ある曲線からの距離 d」の1本の式で書いた。
#      溝＝底の線からの距離、輪＝縁の円からの距離。**両端・両縁で厳密に 0**（#49①）。
#    溝だけは長さ方向に sin^2.2 を掛ける＝両端で 0＝「真ん中でだけ効く」を式に入れる。
#
# 造形＝掃引（loft）と回転体だけ。boolean 不使用。object.scale / transform_apply 不使用（#15）。
#    黒の質感は MATERIALS.md の **`tetsu`**＝薬研は鋳物（鉄・青銅）。硬くて重いもの。
#    🔴 #76⑦：SUBSURF は付けず **DISPLACE だけ**（舟には縁と竜骨の角がある）。
#    🔴 MATERIALS.md 掟1：発光面は歪ませない → DISPLACE に**頂点グループ(1−E)**を渡す。
#
# 【ドメイン】医・薬／薬研（シリーズ未踏）。直近10作＝茶・茶筅／漁労・蛸壺／灯火・和蝋燭／
#    神域・鳥居／鏡・柄鏡／手仕事・和鋏／製紙・紙漉き／古墳・埴輪／炊事・竈／証・割符 と別。
#    049 ISHIUSU【農・製粉／石臼】も「挽く」道具だが、あちらは**回る二枚の円盤**で
#    光は隙間、シルエットは積み重ね。こちらは**舟と輪**で光は2本の稜線、構図は対。
#    056 WARIFU【証・割符】も稜線×対だが、あちらは**同形2つ**、こちらは**異形2つ**。
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
LIME_W = 100.0                     # #58③：随伴のライム光源（発光体の外・奥）

# --- 置き場所 ----------------------------------------------------
X0, Y0 = 0.49, 0.0
Z_O    = 1.30                      # 溝の底の中央（＝オブジェクト原点）の高さ
YAW    = math.radians(36.0)        # 🔴 21°では柄が奥行きへ抜けて消え、輪が正円＝「惑星」になった（#76③）

# --- 舟（薬研）の寸法 --------------------------------------------
# 🔴 薬研は**厚い鋳物**。1周目に肉を薄くしたら「折った金属板の樋」になった。
#    溝の下に胴（TB）を厚く取るほど「重い器」に見える
LB     = 1.8260                     # 全長
WIN0   = 0.2200                     # V の口の半幅（中央）
TW     = 0.0990                     # 肉厚
ZR0    = 0.1720                     # 中央の縁の高さ（溝の底から）＝V 壁は 43.8°
ZR_END = 0.00                      # 端で縁がどれだけ上がるか（🔴 0.85 は「折れた鰭」に見えた）
TB     = 0.2530                     # 溝の底から船底まで（＝胴の厚み）
ROCK   = 0.000                     # 端で底が持ち上がる量（舟のシア）
V_ROUND = 0.035                     # V の底の丸み（0 で鋭角）
TAPER_P = 0.00                      # 端で口が閉じる速さ（早く閉じるほど舳先が塊になる）
NX, NI, NO = 62, 20, 20

# --- 車輪（薬研車）の寸法 ----------------------------------------
# 🔴 レンズ形（連続な曲面）の円盤は**鉢**に見える。平らな面＋縁の面取りにすると車輪に戻る
R_W    = 0.5500                     # 半径
H_FACE = 0.1045                     # 円盤の面の半厚
H_RIM  = 0.0198                     # 踏み面の半厚
CH     = 0.0550                     # 縁の面取りの幅（ここに光が乗る）
R_HUB, L_HUB = 0.0990, 0.1232        # ハブ（軸の座）
R_AXLE, L_AXLE = 0.0374, 0.6490      # 柄（軸）
R_GRIP, GRIP_L = 0.0484, 0.1650      # 柄の握り
NPHI, NFACE, NCH = 128, 6, 10
R_STEP = 0.3300                      # 面の段（鋳物の車輪の顔）。無いと円盤が**ドーム**に見える
H_STEP = 0.000                      # 段の落差

# --- 機構 --------------------------------------------------------
A_ROLL   = 0.4180                   # 車輪の往復（溝方向）
G_LO, G_HI = 0.3630, 0.6820          # 縁の最高点からの隙間（真ん中で沈む）
ROLL0    = math.radians(40.0)      # 器の煽り（溝が見える角）
ROLL_A   = math.radians(7.0)
Z_TOP_R  = ZR0 * (1.0 + ZR_END) + ROCK      # 縁のいちばん高い点（端）

# --- 光（#49① 端で厳密に 0 ／ #34 幅方向にも落とす）--------------
# 🔴 1周目は EB_D=0.17／EW_D=0.115＝**器の内側も円盤の面もまるごと光った**。
#    「稜線」は幅で決まる。帯を部材の1〜2割まで絞って初めて線になる（#24 の抹茶色もこれで消えた）
EB_D     = 0.0275                    # 溝：底の線からこの距離で 0（V の口の 12%＝「線」）
EB_Q     = 1.15
EB_LEN_Q = 2.20                    # 長さ方向 sin(π(0.5+0.5u))^Q ＝両端で 0
EW_D     = 0.0209                   # 輪：縁の円からこの距離で 0（＝面取りの幅ぶん）
EW_Q     = 0.75
ES_CORE  = 26.0
WHITE_FROM, WHITE_TO = 0.66, 0.60  # halo はこの「白→ライム」の帯でしか出ない（#70④）
K_MIX    = 7.0                     # E→0 側は黒い鉄へ戻す（発光体の縁を作らない＝#49①）

STILL_FRAME = 91                   # t=0.25 ＝ 車輪が端で最も高く、溝の光が全部見える


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def uof(x):
    return 2.0 * x / LB


def rock(x):
    return ROCK * uof(x) ** 2


def win_(x):
    # 🔴 5周を「端で口をすぼめ、縁を反らせ、底を持ち上げる」形に費やして全部捨てた。
    #    3つを重ねると面が捩れ、どの角度からも**くしゃくしゃの金属箔**にしか見えない。
    #    薬研は角柱の樋＝断面はほぼ一定で、端は平らな板で閉じる。**捩れを1つも入れない**
    return WIN0 * (1.0 + TAPER_P * uof(x) ** 2)


def zr_(x):
    return ZR0 * (1.0 + ZR_END * uof(x) ** 2)


def wout_(x):
    return win_(x) + TW


_VN = math.sqrt(1.0 + V_ROUND ** 2) - V_ROUND


def f_len(x):
    """溝の光の長さ方向。両端で厳密に 0・真ん中が 1"""
    return math.sin(math.pi * (0.5 + 0.5 * uof(x))) ** EB_LEN_Q


def e_boat(x, y, dz):
    """溝の発光。dz＝底の線からの高さ"""
    d = math.hypot(y, dz)
    if d >= EB_D:
        return 0.0
    return f_len(x) * (1.0 - d / EB_D) ** EB_Q


def e_wheel(r, y):
    """輪の発光。縁の円 (r=R_W, y=0) からの距離"""
    d = math.hypot(R_W - r, y)
    if d >= EW_D:
        return 0.0
    return (1.0 - d / EW_D) ** EW_Q


def boat_section(x):
    """舟の断面。閉じた輪を (y, z, tag, E) で返す。tag: 'in' / 'rim' / 'out'"""
    wi, wo, zr, rk = win_(x), wout_(x), zr_(x), rock(x)
    pts = []
    for i in range(NI + 1):                       # 内側の V（左 → 右）
        a = -1.0 + 2.0 * i / NI
        y = a * wi
        dz = zr * (math.sqrt(a * a + V_ROUND ** 2) - V_ROUND) / _VN
        pts.append((y, rk + dz, "in", e_boat(x, y, dz)))
    pts.append((0.5 * (wi + wo), rk + zr, "rim", 0.0))       # 右の縁の天端
    for i in range(NO + 1):                       # 外側（右 → 左）
        b = 1.0 - 2.0 * i / NO
        y = b * wo
        # 🔴 外壁は**ほぼ垂直**に立てる。|b|^n 型（下ほど内へ絞る）にすると
        #    見下ろし47°では外壁がまったく見えず、**折り曲げた金属板の樋**になった
        dz = -TB + (zr + TB) * (1.0 - (1.0 - abs(b)) ** 0.5)
        pts.append((y, rk + dz, "out", 0.0))
    pts.append((-0.5 * (wi + wo), rk + zr, "rim", 0.0))      # 左の縁の天端
    return pts


def boat_grid():
    """(sections, M) — sections[k] = [(x,y,z,E), ...]（列は閉じた輪）"""
    secs = []
    for k in range(NX + 1):
        x = -0.5 * LB + LB * k / NX
        secs.append([(x, y, z, E) for (y, z, _t, E) in boat_section(x)])
    return secs, len(secs[0])


def wheel_profile():
    """車輪＋ハブ＋柄の母線。(r, y) を +Y の極 → −Y の極 の順で返す。
       🔴 面は平ら。縁は面取り（CH）。**光はこの面取りと踏み面にだけ乗る**"""
    R_FACE = R_W - CH
    P = [(0.0, L_AXLE + 0.015)]
    for i in range(1, 4):                              # 握りの端の丸み
        a = i / 4.0
        P.append((R_GRIP * math.sin(0.5 * math.pi * a), L_AXLE + 0.015 - 0.015 * a))
    P += [(R_GRIP, L_AXLE), (R_GRIP, L_AXLE - GRIP_L + 0.025),
          (R_AXLE, L_AXLE - GRIP_L), (R_AXLE, L_HUB + 0.030),
          (R_HUB, L_HUB), (R_HUB, H_FACE)]
    for sgn in (1, -1):
        if sgn < 0:
            for j in range(1, 4):                      # 踏み面（縁）
                P.append((R_W, H_RIM - 2.0 * H_RIM * j / 4.0))
        rng = range(1, NFACE + 1) if sgn > 0 else range(NCH, -1, -1)
        H2 = H_FACE - H_STEP
        if sgn > 0:
            for j in range(1, NFACE + 1):              # 内の面（+Y）
                P.append((R_HUB + (R_STEP - R_HUB) * j / NFACE, H_FACE))
            P.append((R_STEP, H2))                     # 段
            for j in range(1, NFACE + 1):              # 外の面（+Y）
                P.append((R_STEP + (R_FACE - R_STEP) * j / NFACE, H2))
            for j in range(1, NCH + 1):                # 面取り（+Y）
                a = j / NCH
                P.append((R_FACE + CH * a, H2 + (H_RIM - H2) * a ** 0.72))
        else:
            for j in range(NCH - 1, -1, -1):           # 面取り（−Y）
                a = j / NCH
                P.append((R_FACE + CH * a, -(H2 + (H_RIM - H2) * a ** 0.72)))
            for j in range(NFACE - 1, -1, -1):         # 外の面（−Y）
                P.append((R_STEP + (R_FACE - R_STEP) * j / NFACE, -H2))
            P.append((R_STEP, -H_FACE))                # 段
            for j in range(NFACE - 1, -1, -1):         # 内の面（−Y）
                P.append((R_HUB + (R_STEP - R_HUB) * j / NFACE, -H_FACE))
    P += [(R_HUB, -L_HUB), (R_AXLE, -L_HUB - 0.030),
          (R_AXLE, -(L_AXLE - GRIP_L)), (R_GRIP, -(L_AXLE - GRIP_L) - 0.025),
          (R_GRIP, -L_AXLE)]
    for i in range(3, 0, -1):
        a = i / 4.0
        P.append((R_GRIP * math.sin(0.5 * math.pi * a), -(L_AXLE + 0.015 - 0.015 * a)))
    P.append((0.0, -(L_AXLE + 0.015)))
    out, prev = [], None
    for q in P:                                        # 重複点を落とす
        if prev is None or abs(q[0] - prev[0]) > 1e-9 or abs(q[1] - prev[1]) > 1e-9:
            out.append(q); prev = q
    return out


WPROF = wheel_profile()


# --- 機構（厳密に閉じる）------------------------------------------
def tau(t):
    return 2.0 * math.pi * t


def xw(t):
    return A_ROLL * math.sin(tau(t))


def gapw(t):
    return G_LO + (G_HI - G_LO) * math.sin(tau(t)) ** 2


def zw(t):
    return Z_TOP_R + R_W + gapw(t)


def spin(t):
    return -xw(t) / R_W                       # 滑らない転がり


def roll(t):
    return ROLL0 + ROLL_A * math.cos(tau(t))


def rmat(t):
    """器の姿勢 Rz(YAW)·Rx(roll) を (3,3) で返す"""
    cr, sr = math.cos(roll(t)), math.sin(roll(t))
    cy, sy = math.cos(YAW), math.sin(YAW)
    # Rx
    A = ((1, 0, 0), (0, cr, -sr), (0, sr, cr))
    # Rz
    B = ((cy, -sy, 0), (sy, cy, 0), (0, 0, 1))
    return tuple(tuple(sum(B[i][k] * A[k][j] for k in range(3)) for j in range(3))
                 for i in range(3))


def to_world(p, R):
    return (X0 + R[0][0] * p[0] + R[0][1] * p[1] + R[0][2] * p[2],
            Y0 + R[1][0] * p[0] + R[1][1] * p[1] + R[1][2] * p[2],
            Z_O + R[2][0] * p[0] + R[2][1] * p[1] + R[2][2] * p[2])


def wheel_pt(r, ylo, phi, t):
    """車輪の母線上の点（回転体・軸は局所 Y）を器の局所座標へ"""
    th = spin(t)
    c, s = math.cos(phi + th), math.sin(phi + th)
    return (xw(t) + r * c, ylo, zw(t) + r * s)


# --- #40⑥ を幾何で積分する（z バッファ＋面の向き）------------------
GW, GH = 300, 376
CELL_X, CELL_Y = FRAME_W / GW, FRAME_H / GH
SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2


def proj(P):
    m = 8.3 / (8.3 + P[1])
    sx = AIM_X + (P[0] - AIM_X) * m
    sz = LOOK_Z + (P[2] - LOOK_Z) * m
    return ((sx - SX0) / CELL_X, (sz - SZ0) / CELL_Y, P[1])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def norm(v):
    n = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / n for c in v)


def world_quads(t):
    """(v0,v1,v2,v3, E) をワールドで返す。E は 4 頂点の平均"""
    R = rmat(t)
    secs, M = boat_grid()
    W = [[to_world((p[0], p[1], p[2]), R) for p in s] for s in secs]
    Q = []
    for k in range(NX):
        for j in range(M):
            j2 = (j + 1) % M
            e = 0.25 * (secs[k][j][3] + secs[k][j2][3] +
                        secs[k + 1][j2][3] + secs[k + 1][j][3])
            Q.append((W[k][j], W[k][j2], W[k + 1][j2], W[k + 1][j], e))
    # 車輪
    NP = len(WPROF)
    rings = []
    for a in range(NPHI):
        phi = 2.0 * math.pi * a / NPHI
        rings.append([to_world(wheel_pt(r, yl, phi, t), R) for (r, yl) in WPROF])
    for a in range(NPHI):
        a2 = (a + 1) % NPHI
        for j in range(NP - 1):
            r0, r1 = WPROF[j][0], WPROF[j + 1][0]
            if r0 < 1e-6 and r1 < 1e-6:
                continue
            e = 0.5 * (e_wheel(*WPROF[j]) + e_wheel(*WPROF[j + 1]))
            Q.append((rings[a][j], rings[a][j + 1], rings[a2][j + 1], rings[a2][j], e))
    return Q


def visible_light(t, want_bbox=False):
    Q = world_quads(t)
    zb = [1e9] * (GW * GH)
    scr = []
    for (p0, p1, p2, p3, e) in Q:
        g = [proj(p) for p in (p0, p1, p2, p3)]
        scr.append((g, e, (p0, p1, p2, p3)))
        d = min(q[2] for q in g)
        xs = [q[0] for q in g]; ys = [q[1] for q in g]
        gx0, gx1 = max(0, int(min(xs))), min(GW - 1, int(max(xs)) + 1)
        gy0, gy1 = max(0, int(min(ys))), min(GH - 1, int(max(ys)) + 1)
        for gy in range(gy0, gy1 + 1):
            base = gy * GW
            for gx in range(gx0, gx1 + 1):
                if zb[base + gx] > d:
                    zb[base + gx] = d
    tot = 0.0
    area = 0.0
    bb = [9e9, -9e9, 9e9, -9e9]
    for (g, e, P) in scr:
        if want_bbox:
            for q in g:
                bb[0] = min(bb[0], q[0]); bb[1] = max(bb[1], q[0])
                bb[2] = min(bb[2], q[1]); bb[3] = max(bb[3], q[1])
        if e <= 1e-4:
            continue
        cx = sum(q[0] for q in g) / 4.0
        cy = sum(q[1] for q in g) / 4.0
        cz = sum(q[2] for q in g) / 4.0
        gi, gj = int(cx), int(cy)
        if gi < 0 or gj < 0 or gi >= GW or gj >= GH:
            continue
        if zb[gj * GW + gi] < cz - 0.010:
            continue
        n = norm(cross(tuple(P[1][i] - P[0][i] for i in range(3)),
                       tuple(P[3][i] - P[0][i] for i in range(3))))
        ctr = tuple(sum(P[i][j] for i in range(4)) / 4.0 for j in range(3))
        v = norm(tuple(CAM_LOC[j] - ctr[j] for j in range(3)))
        f = abs(sum(n[j] * v[j] for j in range(3)))       # 面の向き
        # 画面上の面積
        ar = 0.5 * abs((g[2][0] - g[0][0]) * (g[3][1] - g[1][1]) -
                       (g[3][0] - g[1][0]) * (g[2][1] - g[0][1]))
        tot += e * f * ar
        area += e * f * ar
    return (tot, bb, area) if want_bbox else tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]

if "--probe-only" in sys.argv:
    print("── 069 YAGEN 幾何プローブ")
    print("   舟 長さ%.3f 幅%.3f 高さ%.3f（底%.3f〜端の縁%.3f）"
          % (LB, 2 * wout_(0.0), Z_TOP_R + TB, -TB, Z_TOP_R))
    print("   輪 半径%.3f 踏み面%.3f 柄 全長%.3f   隙間 %.3f〜%.3f（縁の最高点から）"
          % (R_W, 2 * H_RIM, 2 * (L_AXLE + 0.012), G_LO, G_HI))
    print("   V 壁の角度 %.1f°（真上からの見下ろし %.1f°〜%.1f° で底が見える）"
          % (math.degrees(math.atan(ZR0 / WIN0)),
             math.degrees(ROLL0 - ROLL_A) + 9.2, math.degrees(ROLL0 + ROLL_A) + 9.2))

    step = max(1, N_FRAMES // 24)
    VS = {}
    for i in range(0, N_FRAMES, step):
        VS[i] = visible_light(_TS[i])
    vs = [VS[i] for i in sorted(VS)]
    vmax = max(vs)
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(vs) / vmax))
    b = max(VS, key=lambda i: VS[i])
    print("   いちばん明るい frame %d（t=%.3f）  STILL_FRAME=%d" % (b + 1, _TS[b], STILL_FRAME))
    print("   光の曲線 " + " ".join("%.0f" % (100 * v / vmax) for v in vs))
    on = sum(1 for v in vs if v > 0.25 * vmax) / len(vs) * 100
    print("   光が25%%以上ある時間の割合 %.0f%%" % on)

    t = (STILL_FRAME - 1) / N_FRAMES
    tot, bb, la = visible_light(t, want_bbox=True)
    print("\n   ── 画面占有（hero t=%.3f）" % t)
    print("   bbox x %.1f..%.1f%%  y(下から) %.1f..%.1f%%  → 長辺 %.1f%%（目標55〜65）"
          % (bb[0] / GW * 100, bb[1] / GW * 100, bb[2] / GH * 100, bb[3] / GH * 100,
             max((bb[1] - bb[0]) / GW, (bb[3] - bb[2]) / GH) * 100))
    print("   重心x ≒ %.1f%%   重心y（上から）≒ %.1f%%"
          % ((bb[0] + bb[1]) / 2 / GW * 100, 100 - (bb[2] + bb[3]) / 2 / GH * 100))
    print("   枠まで 左%.1f%% 右%.1f%% 上%.1f%% 下%.1f%%"
          % (bb[0] / GW * 100, 100 - bb[1] / GW * 100,
             100 - bb[3] / GH * 100, bb[2] / GH * 100))
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    print("   被写体の下端 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (SZ0 + bb[2] * CELL_Y, capz, SZ0 + bb[2] * CELL_Y - capz))
    print("   ライム面積 ≒ %.2f%%（帯 0.8〜12）"
          % (la * CELL_X * CELL_Y / (FRAME_W * FRAME_H * 0.8) * 100))

    # 対（#57）：塊が2つに割れているか＝輪の最下点と舟の輪郭の隙間
    R = rmat(t)
    lo = 9e9
    for a in range(0, NPHI, 2):
        phi = 2.0 * math.pi * a / NPHI
        g = proj(to_world(wheel_pt(R_W, 0.0, phi, t), R))
        lo = min(lo, g[1])
    hi = -9e9
    secs, M = boat_grid()
    for s in secs:
        for p in s:
            hi = max(hi, proj(to_world((p[0], p[1], p[2]), R))[1])
    print("   🔴 対（clusters==2）：輪の最下点 %.1f%% ／ 舟の最上点 %.1f%% → 隙間 %.1f%%（正なら離れている）"
          % (lo / GH * 100, hi / GH * 100, (lo - hi) / GH * 100))
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
# 薬研は**鋳物**＝`tetsu`。硬くて重いもの。
# 🔴 #76⑦：SUBSURF は付けない（舟の縁と竜骨の角が丸まる）。掃引の密度で DISPLACE だけ掛ける
# 🔴 #77⑩：MATERIALS.md の値はプリミティブで採った値。**金属度 0.35 を V 字の樋に当てると
#    凹面が発光を映し込み、溝いっぱいが緑の水たまりになる**（線に見えない）。
# 🔴🔴 さらに rough0.48/spec0.34 では、煽りが深いフレームで**円盤の平らな面が真っ白に飛ぶ**
#    （#47 の映り込み事故／黒が白くなる）。静止画では出ず、ループの1/4でだけ出る。
#    🔴 映していたのは光源ではなく**白い床**——煽りが深いフレームでは円盤の手前の面が
#    ほぼ真下を向く。だから鏡面を落とすだけでは足りず、**煽りの上限を下げる**のが本手
BLACK_RECIPES = {"tetsu": dict(rough=0.68, spec=0.13, metal=0.00, disp=0.0035, dsize=0.22)}
RECIPE = "tetsu"


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p):
    r = BLACK_RECIPES[RECIPE]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)


mat_body, bp_ = principled("tetsu")
apply_black(bp_)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は**鉄の黒そのもの**へ戻す（発光板の縁を作らない・#49①）。
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


mat_glow = glow_material("ryosen")


# ---------- 造形（bmesh・実寸。局所座標で作り、object に位置と回転を与える）----
def build_boat():
    """舟＝断面の閉じた輪を掃引。E は頂点 index の配列で持ち帰る（#39）"""
    secs, M = boat_grid()
    bm = bmesh.new()
    rings, Ev = [], []
    for s in secs:
        ring = []
        for (x, y, z, E) in s:
            v = bm.verts.new((x, y, z))
            ring.append(v); Ev.append(E)
        rings.append(ring)
    for k in range(NX):
        for j in range(M):
            j2 = (j + 1) % M
            bm.faces.new((rings[k][j], rings[k][j2], rings[k + 1][j2], rings[k + 1][j]))
    # 端の蓋。🔴 断面は V 字＝**凹の n-gon** なので1枚では張らない（分割が破綻する）。
    #    内側の点と外側の点を対にして帯で閉じる（NI==NO が前提）
    assert NI == NO
    for ring in (rings[0], rings[-1]):
        bm.faces.new((ring[NI], ring[NI + 1], ring[NI + 2]))          # 右の縁
        for i in range(NI):
            bm.faces.new((ring[i], ring[i + 1],
                          ring[2 * NI + 1 - i], ring[2 * NI + 2 - i]))
        bm.faces.new((ring[2 * NI + 2], ring[2 * NI + 3], ring[0]))   # 左の縁
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("yagen"); bm.to_mesh(me); bm.free()
    return me, Ev


def build_wheel():
    """車輪＝母線の回転体（軸は局所 Y）。両端は極で閉じる"""
    NP = len(WPROF)
    bm = bmesh.new()
    rings, Ev = [], []
    for a in range(NPHI):
        phi = 2.0 * math.pi * a / NPHI
        c, s = math.cos(phi), math.sin(phi)
        ring = []
        for (r, yl) in WPROF:
            v = bm.verts.new((r * c, yl, r * s))
            ring.append(v); Ev.append(e_wheel(r, yl))
        rings.append(ring)
    for a in range(NPHI):
        a2 = (a + 1) % NPHI
        for j in range(NP - 1):
            if WPROF[j][0] < 1e-6 and WPROF[j + 1][0] < 1e-6:
                continue
            if WPROF[j][0] < 1e-6:
                bm.faces.new((rings[a][j], rings[a][j + 1], rings[a2][j + 1]))
            elif WPROF[j + 1][0] < 1e-6:
                bm.faces.new((rings[a][j], rings[a][j + 1], rings[a2][j]))
            else:
                bm.faces.new((rings[a][j], rings[a][j + 1],
                              rings[a2][j + 1], rings[a2][j]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("kuruma"); bm.to_mesh(me); bm.free()
    return me


# 🔴 スムーズ角 60° は**面取り(57°)まで均して円盤をドーム**にする＝独楽に見える原因。34° に落とす
def link(me, name, mat, smooth=0.60):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat_body)      # slot 0 ＝ 黒（鉄）
    ob.data.materials.append(mat)           # slot 1 ＝ 発光（UV 勾配）
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def bake_uv(me, ob, efun):
    """🔴 UV は面の並び順ではなく **頂点の位置/index** から引き直す（#39）。
       同時に「1−E」の頂点グループを作り、DISPLACE から発光面を守る（MATERIALS.md 掟1）"""
    uvl = me.uv_layers.new(name="grad")
    vg = ob.vertex_groups.new(name="skin")
    for vi, v in enumerate(me.vertices):
        vg.add([vi], max(0.0, 1.0 - 2.2 * efun(vi, v.co)), 'REPLACE')
    for poly in me.polygons:
        emax = 0.0
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            e = efun(vi, me.vertices[vi].co)
            uvl.data[li].uv = (e, 0.5)
            emax = max(emax, e)
        # 🔴 glb はノード網を持てない（#25c）。発光する面だけスロット1に分けておき、
        #    glb ではそのスロットだけを定数のライムへ潰す＝**glb にも光が乗る**（#60）
        poly.material_index = 1 if emax > 0.02 else 0
    return vg


me_boat, EV_BOAT = build_boat()
ob_boat = link(me_boat, "yagen", mat_glow)
vg_boat = bake_uv(me_boat, ob_boat, lambda vi, co: EV_BOAT[vi])

me_wheel = build_wheel()
ob_wheel = link(me_wheel, "kuruma", mat_glow)
vg_wheel = bake_uv(me_wheel, ob_wheel,
                   lambda vi, co: e_wheel(math.hypot(co.x, co.z), co.y))

# 🔴 黒の肌は実ジオメトリ（#52）。SUBSURF は付けず DISPLACE だけ（#76⑦）
_r = BLACK_RECIPES[RECIPE]
tex_relief = bpy.data.textures.new("relief_tetsu", 'CLOUDS')
tex_relief.noise_scale = _r["dsize"]
for ob, vg in ((ob_boat, vg_boat), (ob_wheel, vg_wheel)):
    d = ob.modifiers.new("disp", 'DISPLACE')
    d.texture = tex_relief; d.strength = _r["disp"]; d.mid_level = 0.5
    d.vertex_group = vg.name

parts = [ob_boat, ob_wheel]
ob_boat.rotation_mode = 'XYZ'          # R = Rz(YAW)·Rx(roll)
ob_wheel.rotation_mode = 'YXZ'         # R = Rz(YAW)·Rx(roll)·Ry(spin)

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    R = rmat(t)
    ob_boat.location = (X0, Y0, Z_O)
    ob_boat.rotation_euler = (roll(t), 0.0, YAW)
    ob_wheel.location = to_world((xw(t), 0.0, zw(t)), R)
    ob_wheel.rotation_euler = (roll(t), spin(t), YAW)
    for ob in parts:
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
        caption("MIDDLE STUDY 069 — YAGEN", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, LOOK_Z + 0.30)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：舟と輪のあいだが抜けている＝面光源が素通しで写る

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

world_d = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world_d; world_d.use_nodes = True
bgn = world_d.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 7.95     # 器は煽って手前へ倒れ、輪はさらに手前。被写体の重心へ合わせる
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
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    gx0 = gy0 = 9.0; gx1 = gy1 = -9.0
    for ob in parts:
        ev = ob.evaluated_get(dg)
        xs, ys = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
        print(">> %-8s x %.3f..%.3f  y %.3f..%.3f" % (ob.name, min(xs), max(xs),
                                                      min(ys), max(ys)))
        gx0 = min(gx0, min(xs)); gx1 = max(gx1, max(xs))
        gy0 = min(gy0, min(ys)); gy1 = max(gy1, max(ys))
    print(">> bbox x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)  長辺 %.1f%%（帯 55〜65）"
          % (gx0, gx1, (gx1 - gx0) * 100, gy0, gy1, (gy1 - gy0) * 100,
             max(gx1 - gx0, gy1 - gy0) * 100))
    print(">> 重心x ≒ %.1f%%  枠まで 左%.3f 右%.3f 上%.3f 下%.3f"
          % ((gx0 + gx1) / 2 * 100, gx0, 1 - gx1, 1 - gy1, gy0))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_069.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("ryosen_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    ob_boat.data.materials[1] = m_em
    ob_wheel.data.materials[1] = m_em
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
