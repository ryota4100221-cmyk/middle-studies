# =============================================================
# MIDDLE STUDY 064 — KAGAMI（鏡 / 柄鏡・合わせ鏡）
#
# 黒い柄鏡が二面、離れて宙にある。
# 向かい合っているあいだ、二面はこちらに**縁しか見せない**。
# けれどそのとき、二面のあいだには**終わりのない廊下**ができている。
# 鏡がゆっくりこちらを向くと、磨いた面が ライム #A5E02E に灯る。光は、こちらに届く。
# **けれど、廊下はもう無い。**
# 合わせ鏡の廊下には、鏡を持っている人だけが入れない。覗こうとすると、自分の頭が奥を塞ぐ。
# **見えるようにした瞬間に、無くなるものがある。**
#
# 🔴 構図の型＝**対**（#57：63作中51作が「全身」。対は 059 WARIFU／012 SHOKU の2作のみ）
# 🔴 光の型＝**面**（#53：63作で5作＝いま選べる型のなかで最少）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74② に続く7例目）
#    今日選べたのは 光＝面／芯／背光 × 構図＝全身／天地／対。
#    ・**背光は却下**——#67⑤（寄り）・#69①（対）・#71①（群）・#74②（端寄せ）で
#      すでに4方向つぶれていて、**背光は実質「全身」専用**。全身は51/63の既定＝#57が潰そうとしているもの。
#    ・**芯も却下**——`measure.py --trend` が **halo 36%（🔴）** を出している。
#      その状態で「中心の小さな塊」を選ぶのは #51 の退化の再演（芯の最低記録＝050 KENDAMA
#      halo 2,828／ライム面積 0.22%）。**警報が鳴っている方向へ自分から歩かない。**
#    ・→ **面**が一意。面はライムを「大きな立った面」で出すので、halo と面積を基準期へ戻す唯一の型。
#    ・構図：**天地は却下**。理由は好みではなく**カメラ**——CAM_LOC の z と LOOK_Z が
#      どちらも 1.95 ＝ **このシリーズのカメラ軸は完全に水平**で、画面のいちばん下（z=0.19）でも
#      俯角は atan(1.76/8.3)=**12°しかない**。つまり「沈めて上から覗き込む」は原理的にできず、
#      **面は必ず“立った面”になる**（天地を選んでも面の見え方は1mmも変わらない＝構図が仕事をしない）。
#    ・→ **対**。#69① の通り「対」はライムを宙に置く道を閉じる（あいだの光は第3の塊になる）が、
#      **面は光が塊そのものの表面なので、対の唯一の相棒**。しかも合わせ鏡は**二面でなければ成立しない**
#      ＝構図の型と題材が同じことを言っている（好みで選んでいない）。
#
# 🔴 機構＝**振り角ひとつ**。φ(t)=Φ_MIN+(Φ_MAX−Φ_MIN)·0.5(1+cos2πt)。
#    左は +φ、右は −φ ＝ φが大きいほど二面は互いを向き（＝廊下ができ）、カメラには縁だけを見せる。
#    **発光の値は1フレームも動かしていない**（#69②／#70④）。変わるのは面の法線とカメラの角度だけ。
#    #40⑥ は幾何で積分して 0.17（合格 0.75以下）。整数周期・回転キーのみ＝glb にそのまま乗る。
#
# 🔴 光は「均一なベタ塗り」にしない（#24）。和鏡は**平らではなく、ほんの少しふくらんでいる**
#    （小さくても顔が全部映るのはこのため）。その膨らみ SAG をそのまま勾配の芯にし、
#    ・縁で厳密に 0（#26／#49①）＝ライムが鏡の外へ漏れない
#    ・熱点は中心ではなく**あいだ側へ寄せる**（相手の鏡から光が来る側）
#    ・研ぎ跡（同心の細い波）＝均一な勾配は「塗装」に見える（#70④／062 の地合と同じ話）
#    ・芯だけ白へ抜く＝halo はこれでしか出ない（#70④）
#
# 造形＝boolean 不使用。すべて回転体と掃引。鏡胎（磨いた白銅）は MATERIALS.md の `tetsu`。
#    🔴 ただし DISPLACE は使わない——**磨いた面と研いだ地に鋳肌は無い**（063 と同じ判断）。
#    黒の立体感は「丸めた縁（鰭）が鏡面を拾う」ほうで作る。
#
# 【ドメイン】鏡・柄鏡（シリーズ未踏）。直近10作＝手仕事・和鋏／製紙・紙漉き／古墳・埴輪／
#    炊事・竈／証・割符／空・凧／運搬・車輪／盤上遊戯／鋳造・鋳型／植物・果実 と別。
#    012 SHOKU【天体・光学】も二枚の円盤だが、あちらは**重ねて欠けを作る**（隙間）話で、
#    こちらは**離したまま向きだけ変える**（面）。034 の光学器具は「透かして見る」道具で、
#    鏡は「跳ね返して見る」道具＝逆向き。059 WARIFU も対だが、あちらは割れた一枚の再会。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 150.0                      # #58③：随伴のライム光源（発光体の外）

# --- 置き方（対：二面を離して置き、そのあいだを主題にする）--------
SEP = 1.12                          # 中心間の距離。🔴 これが「あいだ」そのもの
Z_DISC = 2.32                       # 鏡胎の中心の高さ
ZOFF = 0.090                        # 🔴 左右の高さ違い。揃えると「二つのアイコン」に見える（2周目）
PHI_ASYM = 0.85                     # 🔴 3周目：振りも左右で違える。**完全な鏡像は絵ではなく図案**
#                                     （二人が持てば、同じ角度にはならない）
PHI_MAX = math.radians(84.0)        # 向かい合う（＝カメラには縁だけ）
PHI_MIN = math.radians(44.0)        # こちらを向く（＝面が灯る・hero）
# 🔴 2周目：34°では円盤が正円に見え、振りが絵に出なかった（＝「向きを変える道具」に読めない）。
#    44°なら投影は 0.72:1 の楕円＝**一目で「こちらへ向けたところ」**になる
BOB = 0.048                         # 上下の揺れ
LEAN = math.radians(3.6)            # 面内の揺れ（2倍周期）
TIP = math.radians(2.4)             # 前後の揺れ（2倍周期）

# --- 鏡胎（回転体・ローカル：面は X–Z 平面、法線は −Y＝カメラ側）---
R_OUT = 0.330                       # 外径の半径
R_FACE = 0.238                      # 磨いた面の半径。🔴 2周目に 0.262 から詰めた——
#                                     縁の黒が細いと「光る円盤」になり、鏡の枠に読めない
SAG = 0.013                         # 🔴 ふくらみ。和鏡は平らではない＝これが勾配の芯
NR = 96                             # 回転の分割（縁の段をきっぱり出すため 72→96）
# 断面（r, y）。y が負＝カメラ側。前の極 → 縁 → 背 → 後ろの極
# 🔴 2周目：鉢（フライパン）に見えたのは**縁が丸い土手**だったから。
#    縁は「きっぱり段を作って、そこから先は平ら」＝鏡の枠の作り。厚みも 0.060→0.046 へ薄くする
PROF_BODY = [
    (0.000, +0.0060), (0.110, +0.0060), (0.190, +0.0060),
    (0.238, +0.0060),                       # 面の受け（ここまでが磨いた面）
    (0.246, -0.0080), (0.252, -0.0112),     # 段（crisp な立ち上がり）
    (0.310, -0.0120),                       # 平らな縁＝「枠」に読ませる面
    (0.322, -0.0100), (0.330, -0.0020),
    (0.330, +0.0180), (0.320, +0.0250), (0.300, +0.0285),
    (0.220, +0.0305), (0.130, +0.0320), (0.060, +0.0350),
    (0.026, +0.0390),                       # 鈕（ちゅう）＝背の摘み
    (0.000, +0.0405),
]

# --- 柄（え）------------------------------------------------------
# 🔴 2周目：柄が短くて先が尖っていたので「フライパン／棒付き飴」に読めた。
#    実物の柄鏡は**柄の長さ＝鏡胎の直径**。木口は尖らせず平らに落とす
H_Z0, H_Z1 = -0.290, -0.990         # ローカル z（上端は鏡胎の中に埋める）
NS, NC = 44, 24     # 🔴 NC=14 では超楕円の平らな辺が頂点の間に落ち、柄の輪郭が波打った
HPROF = [                           # (s, 面内の半幅 a, 奥行の半幅 b)
    (0.000, 0.0760, 0.0330),        # 座（首）＝鏡胎に食い込む所は太い
    (0.050, 0.0640, 0.0310), (0.130, 0.0580, 0.0290),
    (0.340, 0.0552, 0.0278), (0.620, 0.0548, 0.0276),
    (0.860, 0.0580, 0.0292),        # 手元でわずかに膨らむ
    (0.965, 0.0552, 0.0280), (1.000, 0.0330, 0.0195),  # 木口＝平らに落とす
    # 🔴 7周目：細くて先が尖った柄は**鋳物ではなくゴムに見える**。実物の柄鏡の柄は
    #    鏡胎と同じ一つの鋳物で、太さはほとんど変わらない。太く・真っ直ぐ・木口は平らに
]

# --- 光（磨いた面）------------------------------------------------
NRF, NAF = 96, 128   # 🔴 奥の段は面の 5% 径まで縮むので、粗いと廊下が潰れる
# 🔴🔴🔴 4周目の答え。**鏡の面は、勾配では絶対に鏡にならない。**
#    2周目（等方のガウス）＝豆電球。3周目（縦長のガウス＋同心の波）＝的（まと）。
#    どちらも「光っている円盤」で、**鏡が返しているもの**が描かれていなかった。
#    合わせ鏡が実際に見せているのは**入れ子の像が消失点へ吸い込まれていく廊下**で、
#    ・段の間隔は等間隔ではなく**等比**（奥ほど詰まる＝これが遠近そのもの）
#    ・消失点は面の中心ではなく**相手の鏡の側**へ寄る
#    ・段と段のあいだには**相手の鏡の枠**＝細い暗い環が入る（波ではなく、きっぱりした境目）
#    この3つが揃った瞬間に、同じ円盤が「光る面」から「奥がある面」に変わる。
VP_U, VP_V = 0.42, 0.20             # 消失点（面の正規化座標）。あいだ側・やや上
K_DEPTH = 0.74                      # 段の縮み率（等比）。🔴 0.60 は段が中心に潰れて絵に出なかった
N_DEPTH = 5.6                       # 何段まで見えるか
SEP_W = 0.155                       # 段の境目（相手の鏡の枠）の太さ（段の単位）。
#    🔴 実物では枠は細くない——縁は半径の28%を占める。**暗い環は太いのが正しい**し、
#    そうして初めて「黒が主役／光は段の上だけ」になる（#45 の黒面積もこれで戻る）
DEEP_FLOOR = 0.075                   # いちばん手前の段の明るさ。🔴 ここを上げると全面が同じ＝ペンキ
DEEP_GAM = 1.80                     # 奥へ向かう明るさの上がり方
RIM_P = 0.80                        # 縁で厳密に 0 にする指数（#26／#49①）
ES_CORE = 6.6                       # 発光の芯（いちばん奥の段）
WHITE_FROM, WHITE_TO = 0.88, 0.52   # 芯だけ白へ抜く＝halo（#70④）

STILL_FRAME = 61                    # t=0.5（＝いちばんこちらを向く・揺れの sin 項が全部 0＝#70②）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def phi_of(t):
    """振り角。t=0＝向かい合う（PHI_MAX）／t=0.5＝こちらを向く（PHI_MIN）。整数周期で厳密に閉じる"""
    return PHI_MIN + (PHI_MAX - PHI_MIN) * 0.5 * (1.0 + math.cos(2.0 * math.pi * t))


def face_y(u, v):
    """面の膨らみ（ローカル y。負がカメラ側）。u,v は正規化（u²+v²≤1）"""
    return 0.0040 - SAG * (1.0 - (u * u + v * v))


def light_e(u, v, side, norm=1.0):
    """発光スカラー（0..1）。u,v＝面の正規化座標。side＝-1 で消失点を左右反転（右の鏡）。
       合わせ鏡の廊下を、面の上に**等比で縮む入れ子の環**として焼く。
       #26／#49①：縁（u²+v²=1）で**厳密に 0**＝ライムが鏡の外へ漏れない。"""
    rr = u * u + v * v
    if rr >= 1.0:
        return 0.0
    cu, cv = side * VP_U, VP_V
    px, py = u - cu, v - cv
    A = px * px + py * py
    if A < 1e-12:
        d = 0.0
    else:
        # 消失点から (u,v) の向きに伸ばして外形（単位円）に当たるまでの倍率 t → d=1/t
        B = cu * px + cv * py
        C = cu * cu + cv * cv - 1.0
        t = (-B + math.sqrt(max(0.0, B * B - A * C))) / A
        d = 1.0 / t if t > 1e-9 else 0.0
    # 深さ n（等比）：d = K^n。奥ほど n が大きい
    n = 1e9 if d <= 1e-7 else math.log(d) / math.log(K_DEPTH)
    n = max(0.0, n)
    if n >= N_DEPTH:
        # 🔴 いちばん奥は「段」ではなく**行き止まりの光**。ここを段として扱うと
        #    n=N_DEPTH がちょうど境目に当たり、**廊下の突き当たりに黒い点が開いた**（5周目）
        sep, deep = 1.0, 1.0
    else:
        # 段の境目＝相手の鏡の枠（暗い環）
        fr = n - math.floor(n)
        fr = min(fr, 1.0 - fr)
        sep = 1.0 - 0.97 * math.exp(-((fr / SEP_W) ** 2))
        deep = DEEP_FLOOR + (1.0 - DEEP_FLOOR) * (n / N_DEPTH) ** DEEP_GAM
    rim = (1.0 - rr) ** RIM_P
    # 研ぎ跡＝地のわずかな揺らぎ。均一な面は塗装に見える（#70④／062 の地合）
    rho = math.sqrt(rr)
    rip = 1.0 + 0.070 * math.sin(17.3 * rho + 1.2) + 0.050 * math.sin(3.0 * math.atan2(v, u) + 0.7)
    return deep * sep * rim * rip / norm


E_NORM = max(light_e(u / 120.0, v / 120.0, +1)
             for u in range(-119, 120) for v in range(-119, 120)
             if (u * u + v * v) < 14400)


def light_visible(phi):
    """🔴 #40⑥ は幾何で積分する。発光の値は一切入っていない（面の向きだけが変わる）。
       面を極座標で刻み、各点の**世界法線とカメラ方向の内積**で重みを付けて足す。"""
    tot = 0.0
    for sgn in (-1.0, +1.0):                            # 左（x−）／右（x＋）
        # 🔴 Z 軸まわり ψ の回転で法線 (0,−1,0) は (sinψ, −cosψ, 0) になる。
        #    左（x−）が右を向く＝+x 成分が要る＝ψ=+Φ。よって **ψ = −pos·Φ**。
        a = -sgn * phi * (PHI_ASYM if sgn > 0 else 1.0)
        side = int(-sgn)                                # 熱点は「あいだ側」＝左は局所+x、右は局所−x
        ca, sa = math.cos(a), math.sin(a)
        cx = AIM_X + sgn * SEP * 0.5
        cz = Z_DISC - sgn * ZOFF
        for j in range(NRF):
            rho0, rho1 = j / NRF, (j + 1) / NRF
            rho = 0.5 * (rho0 + rho1)
            dA = math.pi * (rho1 ** 2 - rho0 ** 2) * R_FACE * R_FACE / NAF
            for k in range(NAF):
                th = 2.0 * math.pi * (k + 0.5) / NAF
                u, v = rho * math.cos(th), rho * math.sin(th)
                e = light_e(u, v, side, E_NORM)
                if e <= 0.0:
                    continue
                # ローカル座標と法線（y = face_y(u,v)、∂y/∂x = 2·SAG·x/R²）
                x, z = u * R_FACE, v * R_FACE
                y = face_y(u, v)
                gx, gz = 2.0 * SAG * x / (R_FACE ** 2), 2.0 * SAG * z / (R_FACE ** 2)
                nl = (gx, -1.0, gz)
                ln = math.sqrt(nl[0] ** 2 + 1.0 + nl[2] ** 2)
                nl = (nl[0] / ln, nl[1] / ln, nl[2] / ln)
                # Z 軸まわりに a 回転 → 世界へ
                wx = cx + x * ca - y * sa
                wy = x * sa + y * ca
                wz = cz + z
                nx = nl[0] * ca - nl[1] * sa
                ny = nl[0] * sa + nl[1] * ca
                vx, vy, vz = CAM_LOC[0] - wx, CAM_LOC[1] - wy, CAM_LOC[2] - wz
                vn = math.sqrt(vx * vx + vy * vy + vz * vz)
                dot = (nx * vx + ny * vy + nl[2] * vz) / vn
                if dot > 0.0:
                    tot += e * dA * dot
    return tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]
_VS = [light_visible(phi_of(t)) for t in _TS]
_VMAX = max(_VS)

if "--probe-only" in sys.argv:
    print("── 064 KAGAMI 幾何プローブ")
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    best = max(range(N_FRAMES), key=lambda i: _VS[i])
    print("   いちばん明るいフレーム = %d（t=%.3f）  STILL_FRAME=%d"
          % (best + 1, _TS[best], STILL_FRAME))
    for nm, ph in (("向かい合う", PHI_MAX), ("なかば", 0.5 * (PHI_MAX + PHI_MIN)),
                   ("こちらへ", PHI_MIN)):
        pw = 2.0 * R_OUT * math.cos(ph)
        print("   %-5s φ=%5.1f°  面の投影幅 %.3f  二面の投影スパン %.3f（%.1f%%）  "
              "あいだ %.3f（%.1f%%）  光 %5.1f%%"
              % (nm, math.degrees(ph), pw, SEP + pw, (SEP + pw) / FRAME_W * 100,
                 SEP - pw, (SEP - pw) / FRAME_W * 100,
                 100 * light_visible(ph) / _VMAX))
    h = 2 * R_OUT + (-H_Z1 - R_OUT) + 2 * ZOFF
    print("   縦の実寸 %.3f（%.1f%%）  横の実寸 %.3f（%.1f%%）→ 長辺 %.1f%%（55〜65%%）"
          % (h, h / FRAME_H * 100, SEP + 2 * R_OUT * math.cos(PHI_MIN),
             (SEP + 2 * R_OUT * math.cos(PHI_MIN)) / FRAME_W * 100,
             max(h / FRAME_H, (SEP + 2 * R_OUT * math.cos(PHI_MIN)) / FRAME_W) * 100))
    print("   柄の下端 z=%.3f  キャプション上端 z≒1.09  余裕 %.3f"
          % (Z_DISC - ZOFF + H_Z1, Z_DISC - ZOFF + H_Z1 - 1.09))
    print("   カメラ俯角（画面下端） %.1f°  ＝**水平な面は作れない**（天地を却下した理由）"
          % math.degrees(math.atan(1.76 / 8.3)))
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
# 🔴 和鏡の地は**研いだ白銅**なので tetsu。ただし DISPLACE は使わない——
#    磨いた面と研いだ地に鋳肌は無い（#61 と同じ理由で、実起伏はシルエットの敵にもなる）。
#    Metallic はレシピの 0.35 から 0.24 へ落とす：#47 の映り込み事故は**平らで大きい面**で出る。
BLACK_RECIPES = {
    "tetsu": dict(rough=0.50, spec=0.32, metal=0.24),
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
    return m


mat_body = black_material("kagami_tetsu", "tetsu")


def light_material(name):
    """磨いた面。勾配は **UV 'grad' の U に焼いた実数1つ**（#34/#39）。
       🔴 #70④：halo は**芯を白へ抜く**ことでしか出ない（ライムは B がほぼ無い）"""
    m, p = principled(name)
    p.inputs["Base Color"].default_value = BLACK            # #68⑤：下地に色を置かない
    p.inputs["Roughness"].default_value = 0.42
    p.inputs["Specular IOR Level"].default_value = 0.14
    nt = m.node_tree
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = WHITE_FROM
    wmr.inputs["From Max"].default_value = 1.00
    wmr.inputs["To Min"].default_value = 0.0
    wmr.inputs["To Max"].default_value = WHITE_TO
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
def body_mesh():
    """鏡胎＝PROF_BODY を Y 軸まわりに回した回転体。両端は極。"""
    bm = bmesh.new()
    rings = []
    for r, y in PROF_BODY:
        if r < 1e-9:
            rings.append(None)
            continue
        ring = []
        for k in range(NR):
            th = 2.0 * math.pi * k / NR
            ring.append(bm.verts.new((r * math.cos(th), y, r * math.sin(th))))
        rings.append(ring)
    p_front = bm.verts.new((0.0, PROF_BODY[0][1], 0.0))
    p_back = bm.verts.new((0.0, PROF_BODY[-1][1], 0.0))
    seq = [(i, rings[i]) for i in range(len(rings)) if rings[i] is not None]
    for a in range(len(seq) - 1):
        r0, r1 = seq[a][1], seq[a + 1][1]
        for k in range(NR):
            k2 = (k + 1) % NR
            bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
    first, last = seq[0][1], seq[-1][1]
    for k in range(NR):
        k2 = (k + 1) % NR
        bm.faces.new((p_front, first[k], first[k2]))
        bm.faces.new((p_back, last[k2], last[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("kyoutai"); bm.to_mesh(me); bm.free()
    return me


def _hprof(s):
    if s <= HPROF[0][0]:
        return HPROF[0][1], HPROF[0][2]
    for i in range(len(HPROF) - 1):
        s0, s1 = HPROF[i][0], HPROF[i + 1][0]
        if s <= s1:
            u = (s - s0) / (s1 - s0)
            return (HPROF[i][1] + (HPROF[i + 1][1] - HPROF[i][1]) * u,
                    HPROF[i][2] + (HPROF[i + 1][2] - HPROF[i][2]) * u)
    return HPROF[-1][1], HPROF[-1][2]


def handle_mesh():
    """柄＝超楕円断面を z 方向へ掃引。角を丸めるのは #17（稜線が鏡面を拾わないと黒はプラスチック）"""
    bm = bmesh.new()
    rings = []
    for j in range(NS + 1):
        s = j / NS
        a, b = _hprof(s)
        z = H_Z0 + (H_Z1 - H_Z0) * s
        ring = []
        for k in range(NC):
            th = 2.0 * math.pi * k / NC
            cs, sn = math.cos(th), math.sin(th)
            e = 4.4
            px = a * (abs(cs) ** (2.0 / e)) * (1 if cs >= 0 else -1)
            py = b * (abs(sn) ** (2.0 / e)) * (1 if sn >= 0 else -1)
            ring.append(bm.verts.new((px, py, z)))
        rings.append(ring)
    c0 = bm.verts.new((0.0, 0.0, H_Z0))
    c1 = bm.verts.new((0.0, 0.0, H_Z1 - 0.010))
    for j in range(NS):
        for k in range(NC):
            k2 = (k + 1) % NC
            bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    for k in range(NC):
        k2 = (k + 1) % NC
        bm.faces.new((c0, rings[0][k2], rings[0][k]))
        bm.faces.new((c1, rings[NS][k], rings[NS][k2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("e"); bm.to_mesh(me); bm.free()
    return me


def face_mesh(side):
    """磨いた面＝ふくらんだ円盤。UV 'grad' の U に発光スカラーを焼く（#34/#39）"""
    bm = bmesh.new()
    ctr = bm.verts.new((0.0, face_y(0.0, 0.0), 0.0))
    rings = []
    for j in range(1, NRF + 1):
        rho = j / NRF
        ring = []
        for k in range(NAF):
            th = 2.0 * math.pi * k / NAF
            u, v = rho * math.cos(th), rho * math.sin(th)
            ring.append(bm.verts.new((u * R_FACE, face_y(u, v), v * R_FACE)))
        rings.append(ring)
    for k in range(NAF):
        k2 = (k + 1) % NAF
        bm.faces.new((ctr, rings[0][k], rings[0][k2]))
    for j in range(NRF - 1):
        for k in range(NAF):
            k2 = (k + 1) % NAF
            bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                                   # 法線をカメラ側（−Y）へ
        if f.normal.y > 0:
            f.normal_flip()
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            co = lp.vert.co
            u, v = co.x / R_FACE, co.z / R_FACE
            lp[uvl].uv = (light_e(u, v, side, E_NORM), 0.5)
    me = bpy.data.meshes.new("kagami_men"); bm.to_mesh(me); bm.free()
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


mat_light = light_material("men")
rigs, parts = [], []
for sgn, nm in ((-1.0, "hidari"), (+1.0, "migi")):
    side = int(-sgn)                                     # 熱点は「あいだ側」＝左は局所+x、右は局所−x
    rig = bpy.data.objects.new("kagami_" + nm, None)
    bpy.context.collection.objects.link(rig)
    rigs.append((rig, sgn))
    parts.append(link(body_mesh(), "kyoutai_" + nm, mat_body, parent=rig))
    parts.append(link(handle_mesh(), "e_" + nm, mat_body, parent=rig))
    parts.append(link(face_mesh(side), "men_" + nm, mat_light, parent=rig))

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    phi = phi_of(t)
    for rig, sgn in rigs:
        rig.location = (AIM_X + sgn * SEP * 0.5, 0.0,
                        Z_DISC - sgn * ZOFF + BOB * math.sin(2.0 * math.pi * t))
        # 🔴 振りは **Z 軸まわり**（Y 軸まわりだと面が自分の平面内で回るだけで、向きは1度も変わらない）
        rig.rotation_euler = (TIP * math.sin(4.0 * math.pi * t),
                              sgn * LEAN * math.sin(4.0 * math.pi * t),
                              -sgn * phi * (PHI_ASYM if sgn > 0 else 1.0))
        rig.keyframe_insert("location", frame=f + 1)
        rig.keyframe_insert("rotation_euler", frame=f + 1)

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
        caption("MIDDLE STUDY 064 — KAGAMI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, Z_DISC)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：抜け（二面のあいだ）がある造形では逆光がそのままカメラに写る
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③/#67⑥：**奥**（画面62〜80%の帯に届く位置）へ
limelamps = []
for sx, sy in ((-0.85, 22.0), (0.30, 30.0), (1.60, 40.0)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, 0.30))
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
faces_em = [o for o in bpy.data.objects if o.name.startswith("men_")]
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o not in faces_em:
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
    per = {}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o is floor_obj:
            continue
        ev = o.evaluated_get(dg)
        pxs = []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y); pxs.append(c.x)
        per[o.name] = (min(pxs), max(pxs))
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
    print(">> 重心x（bbox中心）%.1f%%" % ((x0 + x1) * 50))
    L = max(v[1] for k, v in per.items() if k.endswith("hidari"))
    R = min(v[0] for k, v in per.items() if k.endswith("migi"))
    print(">> 🔴 対のあいだ（左の右端→右の左端）%.1f%% ＝ %.0fpx／1600  "
          "（塊が繋がらないために必要なのは 18px 以上）" % ((R - L) * 100, (R - L) * 1600))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_064.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("men_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.42
    for o in faces_em:
        o.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {r.name for r, _ in rigs} | {o.name for o in parts}
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
