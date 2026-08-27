# =============================================================
# MIDDLE STUDY 063 — HASAMI（鋏 / 握り鋏 Japanese thread snips）
#
# 黒い和鋏が一挺、画面の左に寄って浮いている。右はぜんぶ余白。
# 和鋏には**支点が無い**。一本の鋼を折り返しただけだ。曲がるのは、いちばん奥の弓（ゆみ）のところ。
# その一本の鋼の**あいだ**に、ライム #A5E02E の光が一条だけ通っている。
# 指で締めると隙間は細り、光は**刃と刃が触れた一点**で終わる。その先はもう、切れている。
# **二枚の刃は、ほんとうに合わさることはない。触れているのは、いつも一点だけ。**
# **切るという仕事は、刃にはない。すれちがう、そのあいだにしかない。**
#
# 🔴 構図の型＝**端寄せ**（#57：62作中51作が「全身」。端寄せは 052 TAIKO の1作のみ）
#    hero 実測 重心x 28.9%・枠への接触0辺・長辺58% で `compositions.py --verify` 通過
# 🔴 光の型＝**隙間**（#53：62作で18作＝最多だが、**直近10作では0回**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72 に続く6例目）
#    今日選べたのは 光＝隙間／芯／背光 × 構図＝全身／端寄せ／対。
#    ・**芯は却下**——halo が基準期の38%まで落ちて🔴が出ている状態で「中心の小さな塊」を選ぶと
#      ライム面積が確実に痩せる。芯の最低記録が 050 KENDAMA の halo 2,828／面積0.22%
#      ＝#51 の退行そのものを再演する型になる。
#    ・**背光は残したかった（3/62で最少）が、端寄せと組めない**——端寄せの条件は
#      `edge==0 かつ 重心xが中央から12%以上` で、**重心は「暗い∪ライム」のマスクで測る**。
#      背光は被写体の背後に広い光源を要求するので、その光が余白側にはみ出した瞬間に
#      重心が中央へ戻り、余白が余白でなくなる。対（#67⑤）・群（#71①）・寄り（#72）に続いて、
#      **背光は端寄せとも組めない**（4例目）。
#    ・残る 全身 は51/62の既定＝#57 が潰そうとしているもの。
#    → **隙間 × 端寄せ**が一意に決まった（好みで選んでいない）。
#
# 🔴 機構＝**弓（ゆみ）の巻き**。和鋏の弾性は U 字のバネにしかない。
#    U を**弧長 S_U 一定・曲率だけが変わる円弧**として書くと、開き角 Θ が唯一の変数になり、
#    R = S_U/Θ ＝ **締めるほど弓は深く、きつく巻く**（実物がそうである理由：鋼は伸びない）。
#    刃と腕は剛体で、U の端の**接線**にそのまま乗るので、
#    **刃の開きは与えていない。弓の巻き方から出てくる**（049 の「拘束から出てくる量」の型）。
#    Θ(t) = Θ_OPEN + (Θ_CLOSE − Θ_OPEN)·0.5(1−cos2πt) の整数周期で厳密に閉じる。
#    光の量は**隙間の幅そのもの**で、**発光の値は1フレームも動かしていない**（#69②／#70④）。
#    #40⑥ は幾何で積分して 0.399。
#
# 🔴🔴 **6周かかった。うち5周は「毛抜き（ピンセット）」からの脱出**（#33 の型の失敗）。
#    腕を太らせ・肩を付け・片刃の楔にし・先反りを入れ——**どれも効かなかった**。
#    効いたのは造形ではなく**どの瞬間を hero にするか**だった：
#    刃が交差した姿（＝X）だけが、一目で鋏に読める。和鋏は洋鋏のような大きな X を作れないので、
#    **X を作れる側の端をヒーローに置く**しかない。→ PITFALLS #74
#
# 🔴 光は #49② の教え通り「隙間を埋めない」。隙間の**中に、機構と一緒に伸びる一条の線**を置く。
#    幅は隙間の GAP_K 倍だけ（＝両側に必ず黒い鋼の縁が残る）。両端は楕円で**幅を 0 に**絞る（#49①）。
#    線の上には**すれちがう一点**（V_NODE）を焼いてあり、そこだけ白へ抜く（#70④）。
#    長手の微かな波（rip）＝鍛えた刃の線は機械のように真っ直ぐではない
#    ——これが無いと ライムstd は 32 で頭打ちだった（均一な光は勾配があっても塗装に見える）。
#
# 造形＝boolean 不使用。断面は超楕円を掃引した1本の鋼。
#    U では「面内に薄く・奥行に広い」帯（＝面内にしか曲がらない板ばね）、
#    刃では「面内に広く・奥行に薄い」片刃の楔へ連続的に化ける＝**実物の鋼のねじれ**。
#    左右は奥行 ±YOFF ずらしてあるので、締めると刃先が**すれちがって重なる**。
#
# 【ドメイン】手仕事・和鋏（シリーズ未踏）。直近10作＝製紙・紙漉き／古墳・埴輪／炊事・竈／
#    証・割符／空・凧／運搬・車輪／盤上遊戯／鋳造・鋳型／植物・果実／漁労・浮子 と別。
#    036 SAYA【武具・刀剣／鞘】は「収める」機構、013 HAGURUMA【道具・構造】は噛み合う歯車2枚で、
#    どちらも「一本の鋼が、支点を持たずに、あいだを閉じる」機構ではない。
#    059 WARIFU も二つの黒だが、あちらは**離れた二枚**（対）でこちらは**繋がった一本**（端寄せ）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 150.0                      # #58③：随伴のライム光源（発光体の外・#67⑥の遠い床へ）

# --- 置き方（端寄せ：左に寄せ、右を余白にする）-------------------
OFF_X = -0.46                       # 画面中央からの左寄せ（#57 端寄せ＝|重心x−50|≧12）
Z_BASE = 1.30                       # 弓の底の高さ。🔴 これ未満だとキャプション帯に落ちる
LEAN_Y = -0.135                     # 面内の傾き（rad）。垂直に立てると「音叉／毛抜き」に読める
YAW_Z = 0.320                       # 振り（rad）。刃の奥行ずれ（すれちがい）はこれで見える
RY_AMP = 0.052                      # 揺れ（面内）
RZ_AMP = 0.030                      # 揺れ（振り・2倍周期）
DZ_AMP = 0.045                      # 上下の揺れ

# --- 鋼（一本もの）------------------------------------------------
SCALE = 1.090                       # 長辺の実測 54% を 55〜65% の帯の内側へ
S_U = 0.600 * SCALE                         # 🔴 弓の弧長。**これは定数**（鋼は伸びない）＝機構の芯
TH_OPEN = 3.0100           # ひらいた時の弓の巻き角 Θ（rad）
TH_CLOSE = 3.2650          # 締めた時の Θ。R = S_U/Θ なので締めるほど弓は深い
L_HALF = 1.780 * SCALE                      # U の端から刃先までの長さ（片側）
YOFF = 0.0190 * SCALE                       # 左右の奥行ずれ（＝刃がすれちがう）
YOFF_S0, YOFF_S1 = 0.12, 0.62       # ずれが立ち上がる区間（ξ/L_HALF）

# 断面表（ξ/L_HALF, ζ_in＝内側の縁の内寄せ, a＝面内の半幅, b＝奥行の半幅）
# 🔴 a と b が入れ替わるのが和鋏の実物：U は「面内に薄い板ばね」、刃は「面内に広い板」
PROF = [
    (0.000, 0.0200, 0.0200, 0.0480),
    (0.060, 0.0100, 0.0210, 0.0470),
    (0.150, -0.0060, 0.0230, 0.0450),
    (0.260, -0.0150, 0.0270, 0.0420),   # 弓から立ち上がった腕のふくらみ（belly）
    (0.360, -0.0180, 0.0330, 0.0390),
    (0.450, -0.0130, 0.0390, 0.0350),   # 指宛（しあて）＝親指と人差指が当たる平らな幅
    (0.530, -0.0020, 0.0400, 0.0300),
    (0.590, 0.0140, 0.0300, 0.0250),    # くびれ
    (0.620, 0.0230, 0.0290, 0.0220),
    (0.650, 0.0330, 0.0520, 0.0150),    # 🔴🔴 刃の肩。**ここで外へ段が付く**。
    (0.720, 0.0620, 0.0500, 0.0120),    #    3周目までは腕から刃へ滑らかに細るだけで、
    (0.800, 0.1000, 0.0400, 0.0105),    #    silhouette が「毛抜き」から動かなかった。
    (0.880, 0.1400, 0.0280, 0.0098),    #    実物の和鋏は**刃が腕より広い**＝くびれと肩がある
    (0.950, 0.1760, 0.0150, 0.0090),
    (1.000, 0.1985, 0.0035, 0.0075),    # 刃先。a は肩から単調に減らす＝三角の板
]
NH, NU, NSEC = 92, 46, 12           # 片側の分割 / 弓の分割 / 断面の頂点数

# --- 光（隙間の中を走る一条）--------------------------------------
GAP_K = 0.520                       # 🔴 隙間の何割を光が占めるか。#49②：**埋めない**
W_CAP = 0.088 * SCALE                       # 光の半幅の上限（これが「レンズ」を「線」に留める）
LZ_PAD0 = 0.095 * SCALE                     # 下端（弓の口）から少し上げる
LIGHT_EPS = 0.0055 * SCALE                  # 上端＝隙間がこの幅まで閉じたところ
NV, NW = 150, 16
LIGHT_DX = 0.013 * 1.090            # 🔴 隙間は工具の frame では x=0 に対して対称だが、
                                    #    振り（YAW）と透視で**投影では左へ寄る**。光が左の刃に貼り付いて
                                    #    見えるのはこれ。幾何を歪めず、帯だけを投影の中心へ寄せる
V_NODE, V_SIG, V_GAIN = 0.800, 0.200, 1.00
V_BASE = 0.155                      # 節の外側の底値。🔴 これを上げると全面が同じ明るさ＝ペンキ
V_BIAS = 0.28                        # 長手の重み（下＝腕、上＝刃）   # すれちがう一点（刃先寄り）
ES_CORE = 16.5

STILL_FRAME = 61                    # t=0.5（＝ひらき最大・揺れの sin 項が全部 0＝#70②）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def a_of(t):
    """締め具合。0＝閉じ、1＝ひらき。整数周期で厳密に閉じる"""
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * t))


def theta_of(a):
    # 🔴🔴 5周目の答え。a=1（＝t=0.5＝hero）が**締め＝刃が交差した姿**。
    #    ひらいた姿は左右対称の2本の針で「毛抜き」にしか読めず、幅も肩も楔も先反りも効かなかった。
    #    効いたのは**どの瞬間を hero にするか**——交差した瞬間だけ、鋏は一目で鋏になる。
    #    和鋏（支点が無い）は洋鋏のような大きな X を作れないので、
    #    **X を作れる側の端をヒーローに置く**しかない（#33 の型の失敗は構図側でしか解けない）。
    return TH_OPEN + (TH_CLOSE - TH_OPEN) * a


def _lerp_prof(f):
    """ξ/L_HALF=f における (ζ_in, a, b) を表から線形補間"""
    if f <= PROF[0][0]:
        return tuple(SCALE * v for v in PROF[0][1:])
    for i in range(len(PROF) - 1):
        f0, f1 = PROF[i][0], PROF[i + 1][0]
        if f <= f1:
            u = (f - f0) / (f1 - f0)
            return tuple(PROF[i][1 + k] + (PROF[i + 1][1 + k] - PROF[i][1 + k]) * u
                         for k in range(3))
    return PROF[-1][1:]


def _smooth(seq, passes=1):
    out = list(seq)
    for _ in range(passes):
        nxt = out[:]
        for i in range(1, len(out) - 1):
            nxt[i] = 0.25 * out[i - 1] + 0.5 * out[i] + 0.25 * out[i + 1]
        out = nxt
    return out


def _smoothstep(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


_FS = [i / NH for i in range(NH + 1)]
# 🔴🔴 4周目の答え＝**先反り（hook）**。和鋏の刃は先が内へ反っていて、**先が先に当たる**。
#    反りが無いと、ひらいた姿は左右対称の2本の針＝「毛抜き（ピンセット）」にしか読めない
#    （#33 の型の失敗。3周ぶん、幅・肩・楔で救おうとして全部だめだった）。
#    反りを入れると**どのフレームでも刃先が交差する**＝X ができ、一目で鋏になる。
HOOK = 0.000
_ZIN = _smooth([_lerp_prof(f)[0] + HOOK * _smoothstep((f - 0.780) / 0.220) for f in _FS])
_A = _smooth([_lerp_prof(f)[1] for f in _FS])
_B = _smooth([_lerp_prof(f)[2] for f in _FS])


def u_frame(theta):
    """弓＝弧長 S_U 一定・半径 R=S_U/Θ の円弧。中心 (0,0,R)、底が z=0。
       戻り値：R と、左半分の取り付け点 E・上向き u・内向き n"""
    R = S_U / theta
    h = theta * 0.5
    E = (-R * math.sin(h), 0.0, R - R * math.cos(h))
    u = (-math.cos(h), 0.0, math.sin(h))       # 弓の端の接線（外向きに出ていく向き）
    n = (u[2], 0.0, -u[0])                     # 面内で u に直交・内向き（+x 側）
    return R, E, u, n


def half_pt(theta, i, zeta):
    """左半分（A）の局所座標 (ξ=i/NH·L_HALF, ζ＝内向き) → 工具ローカルの (x, z)"""
    _, E, u, n = u_frame(theta)
    xi = _FS[i] * L_HALF
    return (E[0] + xi * u[0] + zeta * n[0], E[2] + xi * u[2] + zeta * n[2])


def inner_edge(theta):
    """左の刃・腕の**内側の縁**（＝隙間に面している側）の折れ線 [(x, z)]。x<0 が開いている"""
    return [half_pt(theta, i, _ZIN[i]) for i in range(NH + 1)]


def slot_half_at(edge, z):
    """左の内縁から x=0 までの距離（＝隙間の半幅）。edge は z について単調に近い"""
    if z <= edge[0][1]:
        return -edge[0][0]
    for i in range(len(edge) - 1):
        z0, z1 = edge[i][1], edge[i + 1][1]
        if (z0 - z) * (z1 - z) <= 0.0 and abs(z1 - z0) > 1e-12:
            u = (z - z0) / (z1 - z0)
            return -(edge[i][0] + (edge[i + 1][0] - edge[i][0]) * u)
    return -edge[-1][0]


def light_span(theta):
    """光の通る z の範囲。上端＝隙間が LIGHT_EPS まで閉じたところ（閉じると下がる）"""
    edge = inner_edge(theta)
    z0 = edge[0][1] + LZ_PAD0
    z1 = edge[-1][1]
    for i in range(len(edge) - 1, 0, -1):
        if -edge[i][0] >= LIGHT_EPS:
            z1 = edge[i][1]
            break
    return z0, max(z1, z0 + 0.05), edge


def light_e(v, w):
    """発光スカラー（0..1）。v＝長手（下→上）、w＝幅（−1..1）。
       #34 の2軸／#26 の縁で厳密に 0／#49① の「幅 0 に絞る」を全部ここで満たす。
       V_NODE の瘤＝**二枚の刃が触れている一点**（実物の鋏は面では触れない）"""
    al = max(0.0, 1.0 - abs(2.0 * v - 1.0) ** 2.6) ** 0.45
    bias = V_BIAS + (1.0 - V_BIAS) * v ** 1.10      # 🔴 開閉するのは刃の側だけ＝重みも上へ
    node = V_BASE + V_GAIN * math.exp(-((v - V_NODE) / V_SIG) ** 2)
    ac = max(0.0, 1.0 - w * w) ** 0.70
    # 🔴 鍛えた刃の線は機械のように真っ直ぐではない。隙間の幅は長手で微かに波打っていて、
    #    そこを通る光も一定にならない。#14 の std（ペンキ化の検知）は、勾配だけでは 32 で頭打ちだった
    #    ——**均一な光は、どれだけ綺麗な勾配を持っていても塗装に見える**（062 の「地合」と同じ話）
    rip = (1.0 + 0.30 * math.sin(9.1 * v + 0.70) + 0.20 * math.sin(15.3 * v + 2.10)
           + 0.13 * math.sin(24.7 * v - 1.20))
    return al * ac * bias * node * rip / E_NORM      # 🔴 min(1,·) で頭を切ると勾配が平らになる（ペンキ化）


ELL_P, ELL_Q = 0.60, 0.60
ELL_NORM = max((v / 400.0) ** ELL_P * (1.0 - v / 400.0) ** ELL_Q for v in range(1, 400))
E_NORM = 1.0
E_NORM = max(light_e(j / 240.0, w / 8.0)
             for j in range(241) for w in range(-8, 9))


def light_grid(theta):
    """光の帯の格子。幅は隙間の GAP_K 倍（上限 W_CAP）＝**発光の値は動かさない**"""
    z0, z1, edge = light_span(theta)
    rows = []
    for j in range(NV + 1):
        v = j / NV
        z = z0 + (z1 - z0) * v
        # 🔴 幅も長手の重みに合わせる（腹では細い糸、刃では太る）＝光が「莢」に見えないように
        # 🔴 幅のピークは**刃の側**（v=0.67）。対称の楕円だと腹がいちばん太って「莢／木の葉」になる
        ell = ((max(v, 0.0) ** ELL_P) * (max(1.0 - v, 0.0) ** ELL_Q)) / ELL_NORM   # #49①：端で 0
        #    2周目は強度だけ 0 にしていたので、下端が「白地の上の黒い板」として写った
        hw = min(GAP_K * max(0.0, slot_half_at(edge, z)) * (0.42 + 0.58 * v ** 0.8), W_CAP) * ell
        rows.append((z, hw))
    return rows


def light_visible(theta):
    """🔴 #40⑥ は幾何で積分する。発光の値は一切入っていない（幅だけが変わる）"""
    rows = light_grid(theta)
    tot = 0.0
    for j in range(NV):
        z0, h0 = rows[j]
        z1, h1 = rows[j + 1]
        dz = z1 - z0
        hm = 0.5 * (h0 + h1)
        v = (j + 0.5) / NV
        for k in range(NW):
            w = -1.0 + 2.0 * (k + 0.5) / NW
            tot += light_e(v, w) * (2.0 * hm / NW) * dz
    return tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]
_VS = [light_visible(theta_of(a_of(t))) for t in _TS]
_VMAX = max(_VS)

if "--probe-only" in sys.argv:
    print("── 063 HASAMI 幾何プローブ")
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    best = max(range(N_FRAMES), key=lambda i: _VS[i])
    print("   いちばん明るいフレーム = %d（t=%.3f）  STILL_FRAME=%d"
          % (best + 1, _TS[best], STILL_FRAME))
    for nm, th in (("ひらき", TH_OPEN), ("なかば", math.pi), ("締め", TH_CLOSE)):
        R, E, u, n = u_frame(th)
        edge = inner_edge(th)
        z0, z1, _ = light_span(th)
        tip = edge[-1]
        belly = max(range(NH + 1), key=lambda i: -edge[i][0])
        print("   %-4s Θ=%.4f  弓R=%.4f  腕の傾き%+5.1f°  "
              "刃先x=%+.4f(高さ%.3f)  最大隙間%.3f(高さ%.2f)  光z %.2f→%.2f  光%5.1f%%"
              % (nm, th, R, math.degrees(math.atan2(-u[0], u[2])),
                 tip[0], tip[1], -edge[belly][0], edge[belly][1], z0, z1,
                 100 * light_visible(th) / _VMAX))
    # 鋼の長さ（弓＋腕）が Θ で変わっていないことの確認＝機構の主張そのもの
    for nm, th in (("ひらき", TH_OPEN), ("締め", TH_CLOSE)):
        R = S_U / th
        print("   %-4s 弓の弧長 %.5f（S_U=%.3f）  全長 %.3f  弓の外幅 %.3f"
              % (nm, R * th, S_U, R - R * math.cos(th * 0.5) + L_HALF,
                 2 * R * math.sin(th * 0.5)))
    hw = max(h for _, h in light_grid(TH_OPEN))
    z0, z1, _ = light_span(TH_OPEN)
    print("   光の最大幅 %.4f（%.0fpx／1600幅換算）  長さ %.3f  アスペクト 1:%.1f"
          % (2 * hw, 2 * hw / FRAME_W * 1600, z1 - z0,
             (z1 - z0) / max(1e-6, 2 * hw)))
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
    "base": dict(rough=0.36, spec=0.15, coat=0.05),
    # 🔴 和鋏の地は**鍛えた鋼**なので MATERIALS.md の tetsu。ただし DISPLACE は使わない——
    #    刃の半厚は 0.007 しかなく、レシピの strength 0.012 はシルエットを食う（#61 の型）。
    #    黒の立体感は「丸めた稜線が鏡面を拾う」ほうで作る（断面が超楕円なのはこのため）
    "tetsu": dict(rough=0.56, spec=0.32, metal=0.22),
    # 🔴 #67③：刃先と木口は**カメラに正対する平らな黒い面**で rim を正面から受けて銀の楔になる。
    #    すれすれではないので金属では逃げない。鏡面を下限（0.10・#45）まで落として粗さで散らす
    "kuchi": dict(rough=0.88, spec=0.10),
}


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def black_material(name, recipe):
    m, p = principled(name)
    r = BLACK_RECIPES[recipe]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)
    return m


mat_steel = black_material("hasami_tetsu", "tetsu")
mat_kuchi = black_material("hasami_kuchi", "kuchi")


def light_material(name):
    """隙間を走る一条。勾配は **UV 'grad' の U に焼いた実数1つ**（#34/#39）。
       🔴 #70④：halo は**芯を白へ抜く**ことでしか出ない（ライムは B がほぼ無い）"""
    m, p = principled(name)
    p.inputs["Base Color"].default_value = BLACK            # #68⑤：下地に色を置かない
    p.inputs["Roughness"].default_value = 0.55
    p.inputs["Specular IOR Level"].default_value = 0.12
    nt = m.node_tree
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = 0.86; wmr.inputs["From Max"].default_value = 1.00
    wmr.inputs["To Min"].default_value = 0.0; wmr.inputs["To Max"].default_value = 0.55
    nt.links.new(xyz.outputs["X"], wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])
    nt.links.new(mixc.outputs[2], p.inputs["Emission Color"])

    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    es.inputs[1].default_value = ES_CORE
    nt.links.new(xyz.outputs["X"], es.inputs[0])
    nt.links.new(es.outputs[0], p.inputs["Emission Strength"])
    return m


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
WEDGE_MIN = 0.14                    # 切刃の先の残り厚（0 にすると刃先が数値的に潰れる）


def sec_ring(c, inv, a, b, kw=0.0):
    """断面。inv＝面内で**切刃（隙間に面した側）**を向く単位ベクトル。面内に半幅 a、奥行に半幅 b。
       🔴 角を丸めた矩形にするのは #17（稜線が光を拾わないと黒はプラスチックになる）。
          刃先で a→0 になるので BEVEL modifier は使えない（幅を食う）。
       🔴🔴 kw>0 で**片刃の楔**になる（切刃の側だけ奥行が薄い）。2周目までは左右対称の
          超楕円で、シルエットが「毛抜き（ピンセット）」にしか読めなかった（#33 の型）。
          鋏に読ませているのは開き角ではなく、**切刃が一本の細い面として光を返すこと**。"""
    out = []
    for k in range(NSEC):
        th = 2.0 * math.pi * k / NSEC
        cs, sn = math.cos(th), math.sin(th)
        e = 4.6
        px = a * (abs(cs) ** (2.0 / e)) * (1 if cs >= 0 else -1)
        py = b * (abs(sn) ** (2.0 / e)) * (1 if sn >= 0 else -1)
        if kw > 0.0 and a > 1e-9:
            u = 0.5 * (1.0 - px / a)                       # 0＝切刃側 / 1＝峰（背）側
            py *= (1.0 - kw) + kw * (WEDGE_MIN + (1.0 - WEDGE_MIN) * u ** 0.75)
        out.append((c[0] + px * inv[0], c[1] + py, c[2] + px * inv[2]))
    return out


def wedge_of(f):
    """楔にする区間（刃の付け根から先）"""
    return _smoothstep((f - 0.630) / 0.090)


def steel_sections(theta):
    """鋼一本ぶんの断面列。刃先A → 腕A → 弓 → 腕B → 刃先B の順（1本の連続した掃引）"""
    _, E, u, n = u_frame(theta)
    R = S_U / theta

    # sgn=-1（左＝A・計算値そのまま）／ +1（右＝B・x を反転）
    def half_side(sgn):
        pts = []
        for i in range(NH + 1):
            zc = _ZIN[i] - _A[i]
            yo = sgn * YOFF * _smoothstep((_FS[i] - YOFF_S0) / (YOFF_S1 - YOFF_S0))
            xi = _FS[i] * L_HALF
            x = E[0] + xi * u[0] + zc * n[0]
            z = E[2] + xi * u[2] + zc * n[2]
            pts.append((-sgn * x, yo, z))
        return pts

    left, right = half_side(-1), half_side(+1)

    secs = []
    # 刃先A → 弓の端A（i を降順）
    for i in range(NH, -1, -1):
        c = left[i]
        if i == NH:
            nxt = left[i - 1]
        else:
            nxt = left[i + 1]
        T = (c[0] - nxt[0], 0.0, c[2] - nxt[2]) if i == NH else (nxt[0] - c[0], 0.0, nxt[2] - c[2])
        L = math.hypot(T[0], T[2]) or 1.0
        T = (T[0] / L, 0.0, T[2] / L)
        secs.append((c, (n[0], 0.0, n[2]), _A[i], _B[i], wedge_of(_FS[i])))
    # 弓（Θ を −Θ/2 → +Θ/2 で回る。両端は腕と同じ断面）
    h = theta * 0.5
    for j in range(1, NU):
        psi = -h + theta * j / NU
        c = (R * math.sin(psi), 0.0, R - R * math.cos(psi))
        T = (math.cos(psi), 0.0, math.sin(psi))
        secs.append((c, (-T[2], 0.0, T[0]), _A[0], _B[0], 0.0))   # 🔴 腕の inv と揃える
        #    （逆向きだと断面の頂点順が半周ずれ、接合部に襟状の継ぎ目が出る）
    # 弓の端B → 刃先B（i を昇順）
    for i in range(0, NH + 1):
        c = right[i]
        nxt = right[i + 1] if i < NH else right[i - 1]
        T = (nxt[0] - c[0], 0.0, nxt[2] - c[2]) if i < NH else (c[0] - nxt[0], 0.0, c[2] - nxt[2])
        L = math.hypot(T[0], T[2]) or 1.0
        T = (T[0] / L, 0.0, T[2] / L)
        secs.append((c, (-n[0], 0.0, n[2]), _A[i], _B[i], wedge_of(_FS[i])))
    return secs


def steel_verts(theta):
    vs = []
    for c, inv, a, b, kw in steel_sections(theta):
        vs.extend(sec_ring(c, inv, a, b, kw))
    # 両端のキャップ中心
    s = steel_sections(theta)
    vs.append(s[0][0]); vs.append(s[-1][0])
    return vs


def steel_mesh(theta):
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in steel_verts(theta)]
    nsec = len(steel_sections(theta))
    for i in range(nsec - 1):
        for k in range(NSEC):
            bm.faces.new((vs[i * NSEC + k], vs[i * NSEC + (k + 1) % NSEC],
                          vs[(i + 1) * NSEC + (k + 1) % NSEC], vs[(i + 1) * NSEC + k]))
    c0, c1 = vs[nsec * NSEC], vs[nsec * NSEC + 1]
    for k in range(NSEC):                                   # キャップ＝艶消しスロット（#67③）
        f = bm.faces.new((c0, vs[(k + 1) % NSEC], vs[k])); f.material_index = 1
        f = bm.faces.new((c1, vs[(nsec - 1) * NSEC + k],
                          vs[(nsec - 1) * NSEC + (k + 1) % NSEC])); f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("steel"); bm.to_mesh(me); bm.free()
    return me


def light_verts(theta):
    rows = light_grid(theta)
    vs = []
    for j in range(NV + 1):
        z, hw = rows[j]
        for k in range(NW + 1):
            w = -1.0 + 2.0 * k / NW
            vs.append((LIGHT_DX + w * hw, 0.0, z))
    return vs


def light_mesh(theta):
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in light_verts(theta)]
    W1 = NW + 1
    for j in range(NV):
        for k in range(NW):
            bm.faces.new((vs[j * W1 + k], vs[j * W1 + k + 1],
                          vs[(j + 1) * W1 + k + 1], vs[(j + 1) * W1 + k]))
    bm.verts.index_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                                   # 法線をカメラ側（−Y）へ
        if f.normal.y > 0:
            f.normal_flip()
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            idx = lp.vert.index
            j, k = idx // W1, idx % W1
            lp[uvl].uv = (light_e(j / NV, -1.0 + 2.0 * k / NW), 0.5)
    me = bpy.data.meshes.new("hikari"); bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, parent=None, smooth=0.42):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if not ob.data.materials:
        ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def add_open_key(ob, verts_open):
    """基底＝a=0 の姿／シェイプキー＝a=1 の姿。値は 0.5(1−cos2πt) で駆動。
       🔴 基底とキーは **theta_of(0)/theta_of(1)** から作る。定数名（TH_OPEN/TH_CLOSE）で書いていたら、
          6周目に theta_of の向きだけ入れ替えたときに**基底が置き去りになり、hero が
          ずっと「ひらいた姿」でレンダーされていた**（絵は正常に出るので目視で気づけない）。
       🔴 位置キーでなくシェイプキーにするのは、**鋼が一本もの**だからで、
          剛体に割ると弓の底が裂ける（実物には支点が無い）。glb には morph target で乗る"""
    ob.shape_key_add(name="Basis", from_mix=False)
    sk = ob.shape_key_add(name="open", from_mix=False)
    for i, p in enumerate(verts_open):
        sk.data[i].co = Vector(p)
    return sk


rig = bpy.data.objects.new("hasami", None)
bpy.context.collection.objects.link(rig)

ob_steel = link(steel_mesh(theta_of(0.0)), "steel", mat_steel, parent=rig)
ob_steel.data.materials.append(mat_kuchi)
sk_steel = add_open_key(ob_steel, steel_verts(theta_of(1.0)))

mat_light = light_material("hikari")
ob_light = link(light_mesh(theta_of(0.0)), "hikari", mat_light, parent=rig)
sk_light = add_open_key(ob_light, light_verts(theta_of(1.0)))

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    a = a_of(t)
    sk_steel.value = a; sk_light.value = a
    sk_steel.keyframe_insert("value", frame=f + 1)
    sk_light.keyframe_insert("value", frame=f + 1)
    rig.rotation_euler = (0.0,
                          LEAN_Y + RY_AMP * math.sin(2.0 * math.pi * t),
                          YAW_Z + RZ_AMP * math.sin(4.0 * math.pi * t))
    rig.location = (AIM_X + OFF_X, 0.0, Z_BASE + DZ_AMP * math.sin(2.0 * math.pi * t))
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


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 1.02), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.85), "logo"),
        caption("MIDDLE STUDY 063 — HASAMI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X + OFF_X, 0.0, 2.25)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：抜け（隙間）がある造形では逆光がそのままカメラに写る
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③/#67⑥：**奥**（画面62〜80%の帯に届く位置）へ
limelamps = []
for sx, sy in ((-0.85, 22.0), (0.30, 30.0), (1.60, 40.0)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + OFF_X + sx, sy, 0.30))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = LIME_W
    lp.data.shadow_soft_size = 2.60
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
cam.data.dof.focus_distance = 8.32
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
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not ob_light:
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
        if o.type != 'MESH' or o is floor_obj:
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
    print(">> 重心x（bbox中心）%.1f%%  ＝端寄せは |重心x−50|≧12" % ((x0 + x1) * 50))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_063.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.42
    ob_light.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {rig.name, ob_steel.name, ob_light.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = ob_steel
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
