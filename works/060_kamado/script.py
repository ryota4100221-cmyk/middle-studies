# =============================================================
# MIDDLE STUDY 060 — KAMADO（竈 / a clay hearth）
#
# 黒い竈が、画面の低いところにひとつ。上はぜんぶ余白——煙の通り道だ。
# 焚口は胴のちょうど真ん中にあって、そこだけが ライム #A5E02E に灯っている。
# 熾（おき）は放っておけば散って、灰をかぶって伏せる。火掻き棒で真ん中へ掻き寄せると、
# 伏せていた面が起き上がって、また燃え立つ。
# **火は、竈にもなく、薪にもない。囲われた真ん中にしか立たない。**
#
# 🔴 光の型＝**内包**（#53：59作で6作。001 THE FILLING／004 ANDON／031 TOURO）
#    004 ANDON・031 TOURO との違いを隠さない：あちらは**灯り**（光ることが目的の道具）で、
#    機構は「奥の発光体が scale で息をする」＝**光そのもののアニメ**。
#    こちらの火は炊事の副産物で、機構は**黒い道具が火を並べ替える**＝
#    光の位置も量も**行為の結果**であって、光を直接アニメしていない。
# 🔴 構図の型＝**天地**（#57：59作中51作が「全身」）。054 HOOZUKI が**高く吊った**側なので、
#    こちらは**低く沈める**側を取る（c_y ≥ 75）。竈は家のいちばん低いところに据わる物で、
#    **上の余白＝煙の通り道**＝余白の配分そのものが題材になっている。
# 🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①）：
#    内包＝光は殻の内側／天地＝edge==0 かつ重心yのずれ。塊の数は縛らないので矛盾しない。
#    逆に **カメラ（水平・z=1.95）の下に沈める＝上から覗けない**ので、
#    **口が上を向いた器（硯・火鉢・囲炉裏）は原理的に成立しない**——2.6°の見下ろしでは
#    洞の床は 0.016 に潰れる。**開口が前を向いている竈だけが、この構図で中を見せられる。**
#    （硯を1周ぶん設計してからこの検算で捨てた＝#69⑤ の「先に解く」の適用）
#
# 【ドメイン】炊事・竈（シリーズ未踏）。直近10作＝証・割符／空・凧／運搬・車輪／盤上遊戯／
#            鋳造／植物・果実／漁労／楽器・打／貨幣／玩具・けん玉 と別。
#
# 機構＝**掻き寄せる（raking the embers together）**：a(t)=0.5(1−cos2πt)。
#   🔴 #69② の教訓を先に効かせる——**発光の強さで光量を作らない。幾何で作る。**
#      熾は薄い板で、散っているとき**伏せている**（ピッチ76°＝カメラには小口しか見えない）。
#      掻き寄せると**起き上がる**（8°＝広い面が正対する）。見える発光面は 0.0058→0.0134 の
#      **2.3倍**で、これは発光の値を1つも動かさずに出る量。強度の増減(0.62→1.0)は添え物。
#   位置キーと回転キーだけなので glb にそのまま乗る（#60）。整数周期で厳密に閉じる。
#
# 造形＝boolean 不使用。**リング積み（059 と同族）で焚口を「掘る」**：
#   各高さの断面（角R付き長方形）の**前面の一区間だけ y を奥へ送る**。
#   焚口の外では 6mm の浅い羽目（PANEL_D）に留めるので、リングの頂点数が全高で一定になり、
#   洞の床・天井・側壁が**リング間の四角形として自動的に生まれる**。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 竈 ---------------------------------------------------------
KX, KY, KZ0 = 0.62, 0.0, 1.15        # 胴の中心x・奥行中心y・底のz
H = 0.735                             # 胴の高さ（横に広く低い＝竈の据わり）
CR = 0.030                            # 断面の角R（大きいと枕形に丸まって樹脂に見える＝#65①の親戚）
# 胴の輪郭（zn, 半幅hx, 半奥行hy）。0.865 から上が **釜羽**（かまば）の張り出し
PROF = [(0.000, 0.560, 0.452), (0.050, 0.569, 0.459), (0.095, 0.551, 0.444),
        (0.700, 0.527, 0.425), (0.820, 0.533, 0.430), (0.868, 0.586, 0.473),
        (0.950, 0.590, 0.476), (1.000, 0.578, 0.466)]
RH = 0.378                            # 鍋穴の半径（＝釜羽を細くして天面の白帯を減らす）
HOLE_D = 0.12                         # 鍋穴の深さ

MW = 0.262                            # 焚口の半幅
LZ0, LZ1 = 0.155, 0.575               # 焚口の下端・上端（局所z）
LZS = LZ1 - MW                        # ここから上が半円のアーチ
W_MIN = 0.13                          # アーチ頂の幅の下限（0にすると頂点が潰れる）
CAV_D = 0.40                          # 洞の深さ
PANEL_D = 0.006                       # 焚口まわりの羽目（リングの頂点数を一定に保つ・上記参照）

# 煙出し（角の筒＝丸くすると缶に見える）
SM_X, SM_Y = 0.205, 0.250
SM_H, SM_R0, SM_R1 = 0.175, 0.136, 0.124

# --- 熾（おき）---------------------------------------------------
N_OKI = 5
OKI_X, OKI_Y = 0.080, 0.031                   # 薄い板（割った薪の小片）
# 🔴 高さを1本ずつ変える。**同じ高さで並べると、緑の煉瓦が1個置いてあるだけになる**
#    （1周目・2周目とも「焚口いっぱいの緑のベタ」に転んだ原因がこれ）。中央がいちばん高い＝盛り
OKI_ZS = [0.140, 0.205, 0.245, 0.196, 0.130]
# 1本ずつ傾きも変える（全部同じ角度で並ぶと、割木ではなく「緑の板」になる）
OKI_TILT = [0.10, -0.06, 0.03, -0.09, 0.07]
PITCH_FLAT = math.radians(76.0)               # 散：伏せている（灰をかぶって面が下を向く）
PITCH_UP = math.radians(8.0)                  # 集：起き上がってカメラに正対する
SP_SPREAD, SP_GATHER = 0.110, 0.098   # 集でも隣と 0.018 空ける（重ねると緑のベタに融ける）           # x の間隔（散でも焚口の内に収まる幅）
OKI_Y_FLAT, OKI_Y_UP = -0.175, -0.318         # 手前へ掻き寄せられる（奥壁から離す）
OKI_Z_BASE = 0.018                            # 伏せているときの芯の高さ（板厚の半分）
ES_CORE = 7.0
EM_LO = 0.62                                  # 散っているときの強度（添え物・主役は幾何）

# --- 火掻き棒 ---------------------------------------------------
TIP0 = (0.60, -0.155, 1.452)
RAKE_U = (0.55, 0.81, 0.12)
RAKE_L = 1.30
RAKE_R = 0.032                                # 角棒の半辺
BL_W, BL_T, BL_H = 0.130, 0.014, 0.125        # 刃（爪）
SWING = 0.10                                  # 先端まわりの首振り（rad）。t=0.5＝heroでは 0
# 🔴 #59 の実測から出た設計：**棒を軸方向へ滑らせても、画素はほとんど変わらない**
#    ——棒は自分のシルエットの上を滑るので、動くのは両端だけ。行程を 0.15→0.42 に伸ばしても
#    動き量は 0.39→0.50 までしか上がらなかった。**軸に直交する動き（首振り）だけが、
#    棒の全長の画素を入れ替える。** θ(t)=SWING·sin2πt は整数周期で厳密に閉じ、
#    t=0.5（hero）で 0 に戻るので**静止画の構図は1ピクセルも動かさずに動きだけ足せる。**
RAKE_TRAVEL = 0.42                            # a: 0→1 で外へ引く
# 🔴 #59：**光がいくら振れても、動き量は幾何でしか出ない。**
#    最初 0.15 で組んだら 光の振れ 3.43・静止率 4% と出ているのに 動き量 0.39 で不合格だった
#    （熾は焚口の中だけで動くので、画面上で動く画素がほとんど無い）。棒を短くして行程を伸ばし、
#    **画面を横切る長い黒い棒そのものを動かす**ことで動き量を作る。

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
LIME_W = 150.0   # 🔴 #58：竈の火は部屋の床を照らす。火を箱に閉じ込めたままだと光の落ちる先が無い。
                 # 🔴 halo は**絶対画素数**なので 480×600 のテストで測ってはいけない（画素が 1/11.1）。
                 # 3周目に halo 1,051 を「不合格」と読んで LIME_W を 95→250 まで上げたが、
                 # 実際は hero 換算で約 11,700＝合格していた。**判定は必ず 1600×2000 で測る。**
FRAME_W, FRAME_H = 2.81, 3.52

NZ_LO, NZ_MO, NZ_AR, NZ_HI = 9, 6, 14, 7   # リングの段数（下・垂直部・アーチ・上）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def a_of(t):
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * t))


def prof(zn):
    zn = min(1.0, max(0.0, zn))
    for i in range(len(PROF) - 1):
        z0, x0, y0 = PROF[i]
        z1, x1, y1 = PROF[i + 1]
        if zn <= z1:
            u = 0.0 if z1 == z0 else (zn - z0) / (z1 - z0)
            return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    return PROF[-1][1], PROF[-1][2]


HY_MOUTH = prof((LZ0 + LZ1) * 0.5 / H)[1]
YF = KY - HY_MOUTH                     # 焚口の前面 y
CAV_BACK = YF + CAV_D                  # 洞の奥壁 y
CAVZ = KZ0 + LZ0                       # 洞の床 z


def oki_state(i, t):
    """i番目の熾の（中心座標・ピッチ・発光倍率）"""
    a = a_of(t)
    sp = SP_SPREAD + (SP_GATHER - SP_SPREAD) * a
    x = KX + (i - (N_OKI - 1) * 0.5) * sp
    y = OKI_Y_FLAT + (OKI_Y_UP - OKI_Y_FLAT) * a
    z = CAVZ + OKI_Z_BASE + (OKI_ZS[i] * 0.5 - OKI_Z_BASE) * a
    p = PITCH_FLAT + (PITCH_UP - PITCH_FLAT) * a + OKI_TILT[i]
    return (x, y, z), p, EM_LO + (1.0 - EM_LO) * a


# 中央の2枚を明るく＝**真ん中がいちばん熱い**（タグラインの直訳）
OKI_W = [0.62, 0.92, 1.00, 0.88, 0.58]


def light_visible(t, want_area=False):
    """🔴 #40⑥ は幾何で積分する（#46/#64②）＝**見えている発光**。
       熾は箱なので6面それぞれで E × max(0, n̂·v̂) × 面積 を積む。
       ピッチが変われば n̂·v̂ が変わる＝**機構がそのまま光の量になっている**ことを数で見る。"""
    C = CAM_LOC
    tot = 0.0
    area = 0.0
    for i in range(N_OKI):
        Z = OKI_ZS[i]
        hx, hy, hz = OKI_X * 0.5, OKI_Y * 0.5, Z * 0.5
        faces = [((1, 0, 0), OKI_Y * Z), ((-1, 0, 0), OKI_Y * Z),
                 ((0, 1, 0), OKI_X * Z), ((0, -1, 0), OKI_X * Z),
                 ((0, 0, 1), OKI_X * OKI_Y), ((0, 0, -1), OKI_X * OKI_Y)]
        off = [(0, hx, 0, 0), (0, -hx, 0, 0), (0, 0, hy, 0), (0, 0, -hy, 0),
               (0, 0, 0, hz), (0, 0, 0, -hz)]
        (cx, cy, cz), p, em = oki_state(i, t)
        cp, sp_ = math.cos(p), math.sin(p)
        for (n, A), (_, ox, oy, oz) in zip(faces, off):
            # 局所→世界（x軸まわりのピッチ）
            nx, ny, nz = n[0], n[1] * cp - n[2] * sp_, n[1] * sp_ + n[2] * cp
            px = cx + ox
            py = cy + oy * cp - oz * sp_
            pz = cz + oy * sp_ + oz * cp
            vx, vy, vz = C[0] - px, C[1] - py, C[2] - pz
            L = math.sqrt(vx * vx + vy * vy + vz * vz)
            fac = (nx * vx + ny * vy + nz * vz) / L
            if fac <= 0.0:
                continue
            tot += ES_CORE * em * OKI_W[i] * fac * A
            area += fac * A
    return (tot, area) if want_area else tot


_VS = [light_visible(i / N_FRAMES) for i in range(N_FRAMES)]
_VMAX = max(_VS)
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _VS[i]) + 1


def rake_axis():
    n = math.sqrt(sum(c * c for c in RAKE_U))
    u = tuple(c / n for c in RAKE_U)
    # 刃を必ず真下へ向けるため、軸から正規直交基底を組む（回転差分に任せない）
    up = (0.0, 0.0, 1.0)
    d = sum(u[i] * up[i] for i in range(3))
    e3 = tuple(up[i] - d * u[i] for i in range(3))
    m = math.sqrt(sum(c * c for c in e3))
    e3 = tuple(c / m for c in e3)
    e2 = (e3[1] * u[2] - e3[2] * u[1], e3[2] * u[0] - e3[0] * u[2], e3[0] * u[1] - e3[1] * u[0])
    return u, e2, e3


U_AX, E2, E3 = rake_axis()
OUT0 = tuple(TIP0[i] - RAKE_L * U_AX[i] for i in range(3))


def proj_xz(P):
    """被写体面（y=0）に立てた枠での正規化画面座標（透視で 0..1）"""
    C = CAM_LOC
    dy = P[1] - C[1]
    if dy <= 0.05:
        return None
    s = (0.0 - C[1]) / dy
    x = C[0] + s * (P[0] - C[0])
    z = C[2] + s * (P[2] - C[2])
    return ((x - (AIM_X - FRAME_W / 2)) / FRAME_W,
            ((LOOK_Z + FRAME_H / 2) - z) / FRAME_H)


def silhouette(t):
    """竈＋煙出し＋火掻き棒を粗く撒いて画面上の範囲と重心を見る"""
    a = a_of(t)
    us, vs = [], []
    for iz in range(31):
        zn = iz / 30
        hx, hy = prof(zn)
        z = KZ0 + zn * H
        for k in range(40):
            th = 2 * math.pi * k / 40
            uv = proj_xz((KX + hx * math.cos(th), KY + hy * math.sin(th), z))
            if uv:
                us.append(uv[0]); vs.append(uv[1])
    for iz in range(6):
        z = KZ0 + H - 0.02 + SM_H * iz / 5
        r = SM_R0 + (SM_R1 - SM_R0) * iz / 5
        for k in range(8):
            th = 2 * math.pi * k / 8
            uv = proj_xz((KX + SM_X + r * math.cos(th), KY + SM_Y + r * math.sin(th), z))
            if uv:
                us.append(uv[0]); vs.append(uv[1])
    sh = tuple(-RAKE_TRAVEL * a * U_AX[i] for i in range(3))
    for k in range(41):
        s = RAKE_L * k / 40
        P = tuple(OUT0[i] + s * U_AX[i] + sh[i] for i in range(3))
        for dz in (-RAKE_R, RAKE_R):
            uv = proj_xz((P[0], P[1], P[2] + dz))
            if uv:
                us.append(uv[0]); vs.append(uv[1])
    return min(us), max(us), min(vs), max(vs)


if "--probe-only" in sys.argv:
    th = (STILL_FRAME - 1) / N_FRAMES
    print(">> STILL_FRAME %d (t=%.3f, a=%.3f)" % (STILL_FRAME, th, a_of(th)))
    print(">> #40(6) 見える光 min/max = %.3f  （合格 0.75以下）" % (min(_VS) / _VMAX))
    # 🔴 #69②：強度を止めて幾何だけで測る＝機構が光を動かしているかの切り分け
    def geo_only(t):
        C = CAM_LOC
        s = 0.0
        for i in range(N_OKI):
            Z = OKI_ZS[i]
            hx, hy, hz = OKI_X * .5, OKI_Y * .5, Z * .5
            faces = [((1, 0, 0), OKI_Y * Z, (hx, 0, 0)), ((-1, 0, 0), OKI_Y * Z, (-hx, 0, 0)),
                     ((0, 1, 0), OKI_X * Z, (0, hy, 0)), ((0, -1, 0), OKI_X * Z, (0, -hy, 0)),
                     ((0, 0, 1), OKI_X * OKI_Y, (0, 0, hz)), ((0, 0, -1), OKI_X * OKI_Y, (0, 0, -hz))]
            (cx, cy, cz), p, _ = oki_state(i, t)
            cp, sp_ = math.cos(p), math.sin(p)
            for n, A, o in faces:
                nx, ny, nz = n[0], n[1] * cp - n[2] * sp_, n[1] * sp_ + n[2] * cp
                px, py, pz = cx + o[0], cy + o[1] * cp - o[2] * sp_, cz + o[1] * sp_ + o[2] * cp
                vx, vy, vz = C[0] - px, C[1] - py, C[2] - pz
                L = math.sqrt(vx * vx + vy * vy + vz * vz)
                f = (nx * vx + ny * vy + nz * vz) / L
                if f > 0:
                    s += f * A
        return s
    g = [geo_only(i / N_FRAMES) for i in range(N_FRAMES)]
    print(">> 強度を止めて幾何だけ min/max = %.3f （＝機構そのものが動かしている量・#69②）"
          % (min(g) / max(g)))
    print(">> ループの閉じ: V(0)=%.6f V(1)=%.6f 差 %.2e" % (_VS[0], light_visible(1.0),
                                                       abs(_VS[0] - light_visible(1.0))))
    _, ar = light_visible(th, want_area=True)
    body = FRAME_W * FRAME_H * 0.80
    print(">> 熾の投影面積 %.4f m² ＝ 上80%%の枠 %.4f m² の %.2f%%（壁の照り返しは別に乗る）"
          % (ar, body, ar / body * 100))
    ap = (2 * MW) * (LZ1 - LZ0)
    print(">> 焚口の開口 %.3f m² ＝ 枠の %.2f%%（#51 ライム面積の上限になる器）" % (ap, ap / body * 100))
    for lab, tt in (("hero(集)", th), ("散", 0.0)):
        L, R, T, B = silhouette(tt)
        print(">> %-9s 画面 x %.3f..%.3f  y %.3f..%.3f  長辺 %.1f%%  重心x %.1f%%  重心y %.1f%%"
              % (lab, L, R, T, B, max(R - L, B - T) * 100, (L + R) / 2 * 100,
                 (T + B) / 2 / 0.80 * 100))
        print("   %-9s 枠まで 左%.3f 右%.3f 上%.3f（負なら枠外＝edge）" % ("", L, 1 - R, T))
    for tx, zz in (("tagline", 1.02), ("logo", 0.85), ("study", 0.74)):
        uv = proj_xz((AIM_X, -1.7, zz))
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx, uv[1] * 100))
    for i in range(0, N_FRAMES, 10):
        t = i / N_FRAMES
        print("   t=%.3f  a=%.3f  ピッチ %4.1f°  光 %5.1f%%"
              % (t, a_of(t), math.degrees(oki_state(0, t)[1]), 100 * _VS[i] / _VMAX))
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

# ---------- マテリアル（MATERIALS.md の実測レシピ・#52） ----------
BLACK_RECIPES = {
    "base":   dict(rough=0.36, spec=0.15, coat=0.05),
    # 竈＝土を突き固めて漆喰で塗ったもの → **陶**（焼き物・石・土・瓦・臼）
    "touki":  dict(rough=0.58, spec=0.28, metal=0.16, disp=0.005, dsize=0.075),
    # 火掻き棒＝鉄。#68②：細い丸みの稜線は白い studio をそのまま映して白い帯になる。
    # #0a0a0a の金属は白を浴びても黒い（#57②/#66④）ので metal で黒へ戻す
    "tetsu":  dict(rough=0.55, spec=0.26, metal=0.32, disp=0.010, dsize=0.09),
    # 熾＝燃え差しの薪。炭は艶が無く、細かい亀裂で光を拾う
    "sumi":   dict(rough=0.72, spec=0.22, metal=0.12),
}


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
    return p


def black_material(name, recipe):
    m, p = principled(name)
    set_black(p, recipe)
    return m


mat_kama = black_material("kamado", "touki")
mat_tetsu = black_material("hibashi", "tetsu")


def oki_material(name):
    """熾＝燃えている薪の小片。勾配は **UV に焼いた E**（#34/#39）。
       板の上ほど熱く、下は灰をかぶって落ちる。#24：均一なベタ塗りはペンキに見えるので
       炭の亀裂のムラを光そのものに乗せる。#65②：純発光体は法線依存の項が無いと形が消える。"""
    m, p = principled(name)
    set_black(p, "sumi")
    nt = m.node_tree
    p.inputs["Base Color"].default_value = BLACK          # #68⑤：下地に色を置かない
    p.inputs["Emission Color"].default_value = LIME

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    fcs = mn('MULTIPLY', 0.16); nt.links.new(lw.outputs["Facing"], fcs.inputs[0])
    fca = mn('ADD', 0.84); nt.links.new(fcs.outputs[0], fca.inputs[0])

    ntx = nt.nodes.new("ShaderNodeTexNoise")
    ntx.inputs["Scale"].default_value = 46.0
    ntx.inputs["Detail"].default_value = 7.0
    ntx.inputs["Roughness"].default_value = 0.62
    nmr = nt.nodes.new("ShaderNodeMapRange"); nmr.clamp = True
    nmr.inputs["From Min"].default_value = 0.30; nmr.inputs["From Max"].default_value = 0.74
    nmr.inputs["To Min"].default_value = 0.24; nmr.inputs["To Max"].default_value = 1.45
    nt.links.new(ntx.outputs["Fac"], nmr.inputs["Value"])

    e1 = mn('MULTIPLY'); nt.links.new(xyz.outputs["X"], e1.inputs[0])
    nt.links.new(fca.outputs[0], e1.inputs[1])
    e0 = mn('MULTIPLY'); nt.links.new(e1.outputs[0], e0.inputs[0])
    nt.links.new(nmr.outputs["Result"], e0.inputs[1])
    # 🔴 #69④：halo（＝光が滲んでいる証拠）は**芯を白へ抜く**ことでしか出ない。
    #    ライム一色をいくら強くしても G が飽和するだけで B が上がらず、halo の定義
    #    （150<r<230・g>200・90<b<190）に1画素も入らない（2周目は halo 1,105 で不合格だった）。
    #    上端だけ発光色を白へ寄せる＝白い芯 →#A5E02E→暗部 の勾配になり #24 のペンキ化も同時に解ける
    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = 0.56; wmr.inputs["From Max"].default_value = 1.05
    wmr.inputs["To Min"].default_value = 0.0; wmr.inputs["To Max"].default_value = 0.66
    nt.links.new(e0.outputs[0], wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])
    nt.links.new(mixc.outputs[2], p.inputs["Emission Color"])

    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e0.outputs[0], e2.inputs[0])
    # 強度アニメ用に1段かませる（値は後でキーを打つ）
    e3 = mn('MULTIPLY', 1.0); nt.links.new(e2.outputs[0], e3.inputs[0])
    nt.links.new(e3.outputs[0], p.inputs["Emission Strength"])
    m["_gain"] = e3.name
    return m


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
def finish_mesh(bm, name, bevel=0.0018, angle=32, smooth=True):
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
    me["_smooth"] = smooth
    return me


def link(me, name, mat, parent=None):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if not ob.data.materials:
        ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    if me.get("_smooth"):
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        try:
            bpy.ops.object.shade_auto_smooth(angle=0.35)
        except Exception:
            pass
        ob.select_set(False)
    return ob


NF, NC, NS, NB, NCAV = 6, 6, 7, 11, 9


def arch_w(lz):
    """焚口の幅の係数。straight（下）→ 半円のアーチ（上）。
       🔴 頂点数を全高で一定に保つため、幅を **0 にせず** W_MIN で止める
       （0 にすると切り欠きの頂点が1点に潰れて面がゼロ面積になる）。"""
    if lz <= LZS:
        return 1.0
    u = min(1.0, (lz - LZS) / MW)
    return max(W_MIN, math.sqrt(max(0.0, 1.0 - u * u)))


def ring(hx, hy, cav, w=1.0):
    """断面（角R付き長方形）の閉多角形。**前面の |x|<=MW·w の区間だけ y を cav へ送る**。
       頂点数は cav / w に依らず一定＝焚口の外でも羽目（6mm）として同じ頂点を持つので、
       洞の床・天井・側壁・アーチがリング間の四角形として自動的に生まれる（boolean 不使用）。"""
    P = []
    mw = MW * w
    x0, y0 = hx - CR, hy - CR
    yf = KY - hy
    P.append((x0, yf))
    for i in range(1, NF + 1):                      # 前面 +x → +mw
        P.append((x0 + (mw - x0) * i / NF, yf))
    P.append((mw, cav))                             # 洞の右側壁
    for i in range(1, NCAV):                        # 洞の奥壁
        P.append((mw - 2 * mw * i / NCAV, cav))
    P.append((-mw, cav))
    P.append((-mw, yf))                             # 洞の左側壁
    for i in range(1, NF + 1):                      # 前面 −mw → −x
        P.append((-mw + (-x0 + mw) * i / NF, yf))
    for i in range(1, NC + 1):                      # 左前の角
        th = math.pi * 0.5 * i / NC
        P.append((-x0 - CR * math.sin(th), -y0 - CR * math.cos(th)))
    for i in range(1, NS + 1):                      # 左面
        P.append((-hx, -y0 + 2 * y0 * i / NS))
    for i in range(1, NC + 1):                      # 左後の角
        th = math.pi * 0.5 * i / NC
        P.append((-x0 - CR * math.cos(th), y0 + CR * math.sin(th)))
    for i in range(1, NB + 1):                      # 背面
        P.append((-x0 + 2 * x0 * i / NB, hy))
    for i in range(1, NC + 1):                      # 右後の角
        th = math.pi * 0.5 * i / NC
        P.append((x0 + CR * math.sin(th), y0 + CR * math.cos(th)))
    for i in range(1, NS + 1):                      # 右面
        P.append((hx, y0 - 2 * y0 * i / NS))
    for i in range(1, NC):                          # 右前の角（始点に戻るので最後は打たない）
        th = math.pi * 0.5 * i / NC
        P.append((x0 + CR * math.cos(th), -y0 - CR * math.sin(th)))
    return [(KX + p[0], p[1]) for p in P]


def kamado_mesh():
    bm = bmesh.new()
    zs = []                                          # (局所z, 洞の中か, 幅係数)
    for i in range(NZ_LO + 1):                       # 焚口より下
        zs.append((LZ0 * i / NZ_LO, False, 1.0))
    zs.append((LZ0 + 0.005, True, 1.0))              # ← ここで洞が始まる（床が生まれる）
    for i in range(1, NZ_MO + 1):                    # 垂直の部分
        zs.append((LZ0 + 0.005 + (LZS - LZ0 - 0.005) * i / NZ_MO, True, 1.0))
    for i in range(1, NZ_AR + 1):                    # 半円のアーチ
        lz = LZS + (LZ1 - LZS) * i / NZ_AR
        zs.append((lz, True, arch_w(lz)))
    zs.append((LZ1 + 0.004, False, W_MIN))           # ← 洞が閉じる（アーチの頂が生まれる）
    zs.append((LZ1 + 0.016, False, 1.0))             # 羽目の幅へ戻す（6mm なので目に出ない）
    for i in range(1, NZ_HI + 1):
        zs.append((LZ1 + 0.016 + (H - LZ1 - 0.016) * i / NZ_HI, False, 1.0))

    rings = []
    for lz, inside, w in zs:
        hx, hy = prof(lz / H)
        cav = (KY - hy + CAV_D) if inside else (KY - hy + PANEL_D)
        z = KZ0 + lz
        rings.append([bm.verts.new((p[0], p[1], z)) for p in ring(hx, hy, cav, w)])
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    bm.faces.new(list(reversed(rings[0])))           # 底
    # 天面＝鍋穴つき（外周リング → 半径RHの円 → 深さHOLE_D → 底）
    top = rings[-1]
    ztop = KZ0 + H

    def inner(vlist, z, r):
        out = []
        for v in vlist:
            dx, dy = v.co.x - KX, v.co.y - KY
            d = math.hypot(dx, dy) or 1.0
            out.append(bm.verts.new((KX + dx / d * r, KY + dy / d * r, z)))
        return out

    # 🔴 #68② の派生：天面の白帯は「傾ければ直る」ではない。**外へ向けて 0.024 下げたら、
    #    面がまるごと key を正面から受けて、白い帯が白い屋根になった**（7周目）。
    #    傾けるのではなく **面積を減らす**——鍋穴を広げて釜羽を細い縁に変える。
    ri = inner(top, ztop, RH)
    rb = inner(top, ztop - HOLE_D, RH)
    for k in range(n):
        bm.faces.new((top[k], top[(k + 1) % n], ri[(k + 1) % n], ri[k]))
        bm.faces.new((ri[k], ri[(k + 1) % n], rb[(k + 1) % n], rb[k]))
    bm.faces.new(rb)

    # 煙出し（別の閉じた筒を同じ bmesh に足す＝重なりは黒の内部で見えない）
    scx, scy = KX + SM_X, KY + SM_Y
    prev = None
    for i in range(7):
        u = i / 6
        z = ztop - 0.03 + SM_H * u
        r = SM_R0 + (SM_R1 - SM_R0) * u
        if i == 6:                                    # 煙出しの笠（無いと「黒い角材」に見える）
            r = SM_R1 * 1.22
        if i == 5:
            r = SM_R1 * 1.02
        cur = [bm.verts.new((scx + r * math.cos(math.pi * (2 * k + 1) / 4) * 1.414,
                             scy + r * math.sin(math.pi * (2 * k + 1) / 4) * 1.414, z))
               for k in range(4)]
        if prev:
            for k in range(4):
                bm.faces.new((prev[k], prev[(k + 1) % 4], cur[(k + 1) % 4], cur[k]))
        else:
            bm.faces.new(list(reversed(cur)))
        prev = cur
    bm.faces.new(prev)
    return finish_mesh(bm, "kamado", bevel=0.0016, angle=28)


def oki_mesh(idx):
    """熾＝薄い板。UV『grad』の X に発光係数を焼く（板の上ほど熱い・#34/#39）"""
    bm = bmesh.new()
    hx, hy, hz = OKI_X * 0.5, OKI_Y * 0.5, OKI_ZS[idx] * 0.5
    # 🔴 直方体のままだと**緑のレゴ**にしか見えない（#66⑤「緑の碁石」と同じ落ち方）。
    #    8隅を index から決まる量だけずらして、角のある割木の塊にする（乱数は使わない＝再現する）
    vs = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                h = math.sin((idx * 7 + sx * 3 + sy * 11 + sz * 5) * 2.399)
                g = math.sin((idx * 13 + sx * 5 + sy * 2 + sz * 17) * 1.717)
                vs[(sx, sy, sz)] = bm.verts.new((sx * hx * (1 + 0.17 * h),
                                                 sy * hy * (1 + 0.22 * g),
                                                 sz * hz * (1 + 0.13 * g * h)))
    F = [((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)),
         ((1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1)),
         ((-1, 1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1)),
         ((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)),
         ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)),
         ((-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1))]
    for f in F:
        bm.faces.new([vs[k] for k in f])
    me = finish_mesh(bm, "oki_%d" % idx, bevel=0.0035, angle=25)
    uvl = me.uv_layers.new(name="grad")
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index]
            u = (v.co.z / OKI_ZS[idx]) + 0.5                # 0(下)..1(上)
            # 🔴 #24/#69④：勾配を深く取る。下は灰をかぶって落ち、上端だけが白へ抜ける
            uvl.data[li].uv = (OKI_W[idx] * (0.055 + 1.10 * u * u), 0.5)
    return me


def rake_mesh():
    """火掻き棒。**世界座標で直に組む**（軸の基底を自分で立てるので回転差分に頼らない）。
       物体の location だけで軸方向に出し入れする＝キーは位置だけ＝glb に乗る。"""
    bm = bmesh.new()

    def P(s, a, b):
        return (OUT0[0] + s * U_AX[0] + a * E2[0] + b * E3[0],
                OUT0[1] + s * U_AX[1] + a * E2[1] + b * E3[1],
                OUT0[2] + s * U_AX[2] + a * E2[2] + b * E3[2])

    def box(s0, s1, ha, hb, db=0.0):
        q = [(-ha, -hb + db), (ha, -hb + db), (ha, hb + db), (-ha, hb + db)]
        v0 = [bm.verts.new(P(s0, a, b)) for a, b in q]
        v1 = [bm.verts.new(P(s1, a, b)) for a, b in q]
        for k in range(4):
            bm.faces.new((v0[k], v0[(k + 1) % 4], v1[(k + 1) % 4], v1[k]))
        bm.faces.new(list(reversed(v0)))
        bm.faces.new(v1)

    box(0.0, RAKE_L, RAKE_R, RAKE_R)                                  # 柄
    box(0.0, 0.075, RAKE_R * 1.55, RAKE_R * 1.55)                     # 手元の握り
    box(RAKE_L - BL_T, RAKE_L, BL_W, BL_H * 0.5, -BL_H * 0.5)         # 刃（下へ張り出す）
    return finish_mesh(bm, "hibashi", bevel=0.0016, angle=30)


# ---------- 配置 ----------
kamado = link(kamado_mesh(), "kamado", mat_kama)
# 火掻き棒は「先端まわりに振れる」ので、先端を原点にした空オブジェクトにぶら下げる
rake_root = bpy.data.objects.new("rake_root", None)
bpy.context.collection.objects.link(rake_root)
rake_root.location = TIP0
rake_root.rotation_mode = 'AXIS_ANGLE'
rake = link(rake_mesh(), "hibashi", mat_tetsu)
rake.parent = rake_root
rake.matrix_parent_inverse = Matrix.Translation(-Vector(TIP0))

okis, oki_mats = [], []
for i in range(N_OKI):
    m = oki_material("oki_%d" % i)
    ob = link(oki_mesh(i), "oki_%d" % i, m)
    okis.append(ob); oki_mats.append(m)

# 🔴 黒の肌は実ジオメトリ（#52）。**発光体には掛けない**（MATERIALS.md 掟1）
for ob, rec in ((kamado, "touki"), (rake, "tetsu")):
    r = BLACK_RECIPES[rec]
    tex = bpy.data.textures.new("relief_" + ob.name, 'CLOUDS'); tex.noise_scale = r["dsize"]
    sub = ob.modifiers.new("sub", 'SUBSURF')
    sub.levels = sub.render_levels = 2
    sub.subdivision_type = 'SIMPLE'            # 🔴 #65①：既定のCatmull-Clarkは面を枕に丸める
    d = ob.modifiers.new("disp", 'DISPLACE')
    d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    a = a_of(t)
    for j, ob in enumerate(okis):
        (x, y, z), p, em = oki_state(j, t)
        ob.location = (x, y, z)
        ob.rotation_euler = (p, 0.0, 0.0)
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)
        g = oki_mats[j].node_tree.nodes[oki_mats[j]["_gain"]]
        g.inputs[1].default_value = em
        g.inputs[1].keyframe_insert("default_value", frame=f + 1)
    rake.location = tuple(-RAKE_TRAVEL * a * U_AX[k] for k in range(3))
    rake.keyframe_insert("location", frame=f + 1)
    rake_root.rotation_axis_angle = (SWING * math.sin(2 * math.pi * t), E3[0], E3[1], E3[2])
    rake_root.keyframe_insert("rotation_axis_angle", frame=f + 1)

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
        caption("MIDDLE STUDY 060 — KAMADO", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (KX, -0.29, 1.42)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：被写体に抜けがある作では逆光がそのまま画面に写る。火掻き棒と竈のあいだは
#    素通しなので、4×4・1800W の面光源をカメラから隠す（照りは残り、板だけ消える）
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③/#67⑥：**奥**（画面62〜80%の帯に届く位置）へ
limelamps = []
for sx, sy in ((-0.90, 22.0), (0.45, 30.0), (1.90, 40.0)):
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
cam.data.dof.focus_object = okis[1]
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
oki_names = {o.name for o in okis}
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name not in oki_names:
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
    print(">> 占有  長辺 %.1f%%（帯 55〜65%%）  重心x %.1f%%  重心y(上から) %.1f%%（天地は75以上）"
          % (max((x1 - x0), (y1 - y0)) * 100, (x0 + x1) / 2 * 100,
             (1 - (y0 + y1) / 2) / 0.80 * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_060.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    for j, ob in enumerate(okis):
        m_em = bpy.data.materials.new(ob.name + "_glb"); m_em.use_nodes = True
        pe = m_em.node_tree.nodes["Principled BSDF"]
        pe.inputs["Base Color"].default_value = BLACK
        pe.inputs["Emission Color"].default_value = LIME
        pe.inputs["Emission Strength"].default_value = ES_CORE * 0.5 * OKI_W[j]
        ob.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {kamado.name, rake.name, rake_root.name} | oki_names
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = okis[1]
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
