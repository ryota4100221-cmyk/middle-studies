# =============================================================
# MIDDLE STUDY 065 — TORII（鳥居 / 正中）
#
# 黒い鳥居がひとつ、高いところにある。下はぜんぶ余白——参道だ。
# 鳥居には扉が無い。閉めるためのものではないから。柱が二本と、横木が三本。
# それだけで、こちらとあちらが分かれる。
# 光は鳥居の**うしろ**にある。だから黒は縁だけが灯り、
# **何も無いまんなかが、いちばん明るい。**
# 参道のまんなかは「正中（せいちゅう）」といって、神の通る道だ。だから人は端を歩く。
# **まんなかは、通れないのではない。空けてあるのだ。**
# 鳥居は動かない。動くのは、光のほうだ。
#
# 🔴 光の型＝**背光**（#53：64作で3作＝**8型のうち最少**。012 蝕／035 櫛／051 銭）
# 🔴 構図の型＝**天地**（#57：64作で2作＝**6型のうち最少タイ**。054 鬼灯（高く）／060 竈（低く））
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75② に続く8例目）
#    今日選べたのは 光＝稜線／芯／背光 × 構図＝全身／天地／群。
#    ・まず **`measure.py --trend` が halo 🔴 36%**（基準期36,032→直近5作13,079）を出している。
#      #51④ の処方は「下限を割ったら造形でなく光の出し方を変える＝**面で出す・透過させる**」。
#      **稜線（線）と芯（点）は、その処方の逆を行く型**——051 が同じ状況で選び直したのが背光で、
#      あれだけが halo 86,091＝基準期の2.4倍を出している。→ **背光**。
#    ・**群は不成立**。#71① の通り群（clusters≥5）は「共有の光源を宙に置いた瞬間に全部が1塊に繋がる」ので
#      ライムは各個体の内側に閉じ込めるしかない。**背光は定義上その逆**（光源が被写体の背後にある）。
#      稜線×群も、光が多数の物に同時に載るので**絵は「反復」になる**（＝宣言だけ変えて絵は同じ、#57が潰そうとしたもの）。
#    ・→ 残るは 全身／天地。**#74② は「背光は実質 全身 専用」と書いたが、
#      潰れているのは 寄り（#67⑤）・対（#69①）・群（#71①）・端寄せ（#74②）の4つで、
#      天地だけは一度も検算されていない。** ここで解く：
#      端寄せが潰れた理由は「背後の光が余白側へはみ出すと**重心xが中央へ戻る**」だった。
#      天地が要求するのは**重心y**で、背光のはみ出しは**被写体と同じ高さに広がる**（上下には偏らない）。
#      ＝**背光は重心yを動かさない**ので、天地とは干渉しない。→ **背光×天地が一意**。
#      （#75② のカメラ検算も通る：面と違って背光は「立った面」である必要がない）
#
# 🔴 機構＝**日の道（transit）**。鳥居は1フレームも動かさない。動くのは光だけ。
#    光の中心 x=AIM_X+A_X·sin2πt ／ z=Z_MID+A_Z·cos2πt ＝**楕円の軌道を1周**（整数周期・厳密に閉じる）。
#    t=0.5 で正中（＝hero）／t=0 で島木の裏／t=0.25,0.75 で柱の裏。
#    **発光の値は1フレームも動かしていない**（#69②／#70④）。変わるのは
#    「柱と貫と島木が、光のどこを隠しているか」だけ＝#40⑥ は幾何で積分する（--probe-only）。
#
# 🔴 光は「発光板」にしない（#49①／#75①）。板の ES=0 の余白は**白い背景の前では黒い板**になるので、
#    プロファイル E をそのまま **Transparent との Mix Shader の fac** にして、
#    E→0 の外周は**完全に透明**にする（＝縁が存在しない光）。さらに
#    ・芯だけ白へ抜く＝halo はこれでしか出ない（#70④）
#    ・**薄雲の層＝world Z で切る横縞**（#74⑤：滑らかな解析関数だけの光は必ず塗装に見える。
#      揺らぎは題材の性質から取る＝地平に近い光は靄の層に横に切られる。
#      🔴 縞は **Geometry→Position（world）** から引く。UV に焼くと光と一緒に動いてしまう）
#
# 造形＝明神鳥居（柱2・貫・楔・額束・島木・笠木）。boolean 不使用、すべて掃引で組む。
#    黒の質感は MATERIALS.md の **`touki`（陶＝石鳥居）**。朱塗りは「色」が主役になるので取らない——
#    いちばん古い鳥居は、色を塗らない。
#    🔴 DISPLACE は掛けるが **SUBSURF は掛けない**（#52 のコードは Catmull-Clark なので、
#    角のある部材に掛けると**箱が丸まる**）。掃引の段階で十分な密度を作り、実起伏だけを乗せる。
#
# 【ドメイン】神域・鳥居（シリーズ未踏）。直近10作＝鏡・柄鏡／手仕事・和鋏／製紙・紙漉き／
#    古墳・埴輪／炊事・竈／証・割符／空・凧／運搬・車輪／盤上遊戯／鋳造・鋳型 と別。
#    044 SHINBASHIRA【建築・寺社／五重塔】は仏塔で、主題は「**塔は揺れる。真ん中だけが動かない**」＝不動。
#    こちらは神社の門で、主題は「**まんなかは、空けてある**」＝不使用。物も宗旨も主題も別。
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
LIME_W = 150.0                      # #58③：随伴のライム光源（発光体の外）

# --- 鳥居（明神鳥居。比は実物から起こす＝#50）---------------------
# 🔴 構図＝天地。**高く浮かせる**側を取る（054 鬼灯と同じ側だが、あちらは吊られた実で
#    こちらは自立する門＝「下に何も無い」の意味が逆になる：あちらは吊り元、こちらは参道）
Z_BASE = 1.78          # 柱の下端。キャプション上端 z≒1.09 との余白 0.69
H_COL = 1.170          # 柱（下端→島木の下端）
X_COL_B, X_COL_T = 0.600, 0.570      # 柱の芯（下・上）＝転び（内へ 0.030）
R_COL_B, R_COL_T = 0.084, 0.075      # 石鳥居の柱は太い（径/柱間 = 0.168/1.200 = 1/7.1）
NCJ, NCK = 34, 48                    # 柱の分割（縦・周）

Z_NUKI0, Z_NUKI1 = 0.772, 0.878      # 貫（Z_BASE からの高さ）
X_NUKI, D_NUKI = 0.760, 0.034        # 出貫＝柱より外へ出る／奥行の半分
X_KUSABI, W_KUSABI = 0.712, 0.017    # 楔（貫の出に打ち込む）
Z_KUSABI0, Z_KUSABI1 = 0.744, 0.906
D_KUSABI = 0.048
W_GAKU, D_GAKU = 0.058, 0.040        # 額束（貫と島木のあいだ・まんなかに立つ）
Z_SHIMA0, H_SHIMA, D_SHIMA = 1.170, 0.102, 0.082      # 島木（＝柱の上端）
Z_KASA0, H_KASA, D_KASA = 1.272, 0.130, 0.106         # 笠木
X_SHIMA, X_KASA = 0.720, 0.810
SORI = 0.055                         # 反り増し（両端が上がる）。島木と笠木は同じ曲線に乗る
NSEG, NK = 40, 5                     # 掃引の分割（長手・断面は 4·NK 点）

TOP_Z = Z_BASE + Z_KASA0 + H_KASA + SORI            # 笠木の端の天端
WIDTH = 2 * X_KASA

# --- 光（鳥居のうしろ）-------------------------------------------
Y_GLOW = 0.55          # 被写体面より奥。カメラからの見かけ倍率 8.3/8.85 = 0.938
# 🔴 2周目：光は**鳥居より大きい**こと。1周目は開口の内側に収まる大きさで、
#    絵は「門に吊るした豆電球」になった（#75① の背光版）。051 の背光がそう見えるのは
#    **黒の外側にコロナが回り込んでいる**からで、被写体より小さい光では逆光にならない。
# 🔴 7周目：**円い光は「惑星」に見える**（#33 の型）。等方に近い比＋横縞は縞のある球そのもので、
#    絵は「門のうしろの緑の星」になった。光にかたちを持たせないために、比は 1.8:1 まで横へ潰し、
#    **笠木の端より外まで届かせて鳥居を丸ごとシルエットにする**（＝逆光の定義そのもの）。縞は 1/2 に落とす。
RX, RZ = 1.20, 0.72    # 光の広がり（横長＝かたちを持たない「向こうの明るさ」）
A_X, A_Z = 0.60, 0.26                 # 日の道の振幅
Z_HERO = Z_BASE + 0.58                # t=0.5＝正中（hero）
Z_MID = Z_HERO + A_Z                  # t=0 は Z_MID+A_Z＝島木の裏
NRF, NAF = 72, 120                    # 光の面の分割（勾配を焼くので細かく）
ES_CORE = 7.5
WHITE_FROM, WHITE_TO = 0.80, 0.46     # 芯を白へ抜く＝halo はこの「白→ライム」の帯でしか出ない（#70④）
# 🔴🔴 6周目の答え。**白い地の前では、光の裾は「暗いライム」にならない**——
#    薄くすると背景の白が透けて**淡くなる**だけなので、輝度は上へ潰れ std は 21〜24 で頭打ちになる。
#    直し方は強さでも広さでもなく、**不透明さを発光の強さから切り離すこと**：
#    E がまだ高いうちに alpha を 1 まで上げてしまえば、そこから先は
#    「不透明なまま、背景より暗いライム」＝#24 が要求する**暗部の勾配**が作れる。
K_ALPHA = 11.0                        # E≥0.071 で不透明。そこから外は「背景より暗いライム」になる
HAZE_A1, HAZE_F1 = 0.05, 4.5          # 薄雲の層（world Z で切る）
HAZE_A2, HAZE_F2 = 0.035, 11.0

STILL_FRAME = 61       # t=0.5 ＝ 正中（光が鳥居のまんなかに来る唯一の瞬間）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def sori(x):
    """反り増し。島木・笠木は同じ曲線に乗る（だから積み重なる）"""
    return SORI * ((x - AIM_X) / X_KASA) ** 2


def sun_xz(t):
    """日の道。楕円を1周＝整数周期で厳密に閉じる。t=0.5 で正中"""
    return (AIM_X + A_X * math.sin(2.0 * math.pi * t),
            Z_MID + A_Z * math.cos(2.0 * math.pi * t))


def field_e(du, dv):
    """光のプロファイル（0..1）。r=1 で厳密に 0＝縁が存在しない（#26／#49①）。
       🔴 等方のガウス1枚は必ず「豆電球」になる（#75①）。**芯＋裾**の2枚で組む。
       🔴🔴 3周目の学び：裾は「広ければいい」のではない。**白い背景（linear 0.5）より明るくないと
       そこに何も無いのと同じ**——2周目の裾は ES 0.5 で背景に沈み、コロナが1本も出なかった。
       裾は黒の外まで**はっきりライムのまま**届き、そこから急に落ちる。"""
    r = math.hypot(du / RX, dv / RZ)
    if r >= 1.0:
        return 0.0
    # 🔴 8周目：**明るい平場（プラトー）を作ると、その終わりが輪郭になる**——
    #    芯＋広い平場＋暗い環は「緑の卵」に読めた（#33）。平場を消し、
    #    中心から外へ**ひたすら単調に落ちるだけ**にすると、光は境目を持たなくなる。
    core = 0.55 * math.exp(-(r / 0.30) ** 2)
    skirt = 0.45 * (1.0 - r * r) ** 2.8
    return core + skirt


# --- 遮蔽（#40⑥ を幾何で積分する）--------------------------------
# 🔴 凸体をカメラという一点から平面へ投影した影は、**頂点の投影の凸包そのもの**。
#    だから ray marching は要らない：部材の頂点を Y_GLOW の平面へ飛ばして凸包を取り、
#    光の面の各点が どれかの凸包に入っているかだけを見る。鳥居は動かないので**1回だけ**計算する。
def _proj(v):
    """カメラから見て v が Y_GLOW の平面に落とす影の位置（x, z）"""
    s = (Y_GLOW - CAM_LOC[1]) / (v[1] - CAM_LOC[1])
    return (CAM_LOC[0] + s * (v[0] - CAM_LOC[0]),
            CAM_LOC[2] + s * (v[2] - CAM_LOC[2]))


def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    cr = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo = []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    up = []
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _box_v(x0, x1, y0, y1, z0, z1):
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def _occluders():
    """部材を凸体の集まりとして書き出す（曲がった部材は分割して凸に保つ）"""
    obs = []
    for sgn in (-1.0, 1.0):
        for j in range(8):                       # 柱＝8段に割って凸に保つ（転び＋上細り）
            s0, s1 = j / 8.0, (j + 1) / 8.0
            vs = []
            for s, in ((s0,), (s1,)):
                ax = AIM_X + sgn * (X_COL_B + (X_COL_T - X_COL_B) * s)
                r = R_COL_B + (R_COL_T - R_COL_B) * s
                z = Z_BASE + H_COL * s
                for k in range(12):
                    th = 2.0 * math.pi * k / 12
                    vs.append((ax + r * math.cos(th), r * math.sin(th), z))
            obs.append(vs)
    obs.append(_box_v(AIM_X - X_NUKI, AIM_X + X_NUKI, -D_NUKI, D_NUKI,
                      Z_BASE + Z_NUKI0, Z_BASE + Z_NUKI1))
    obs.append(_box_v(AIM_X - W_GAKU, AIM_X + W_GAKU, -D_GAKU, D_GAKU,
                      Z_BASE + Z_NUKI1, Z_BASE + Z_SHIMA0))
    for sgn in (-1.0, 1.0):
        cx = AIM_X + sgn * X_KUSABI
        obs.append(_box_v(cx - W_KUSABI, cx + W_KUSABI, -D_KUSABI, D_KUSABI,
                          Z_BASE + Z_KUSABI0, Z_BASE + Z_KUSABI1))
    for hx, z0, h, d in ((X_SHIMA, Z_SHIMA0, H_SHIMA, D_SHIMA),
                         (X_KASA, Z_KASA0, H_KASA, D_KASA)):
        for j in range(16):                      # 反りがあるので分割して凸に保つ
            x0 = AIM_X - hx + 2 * hx * j / 16
            x1 = AIM_X - hx + 2 * hx * (j + 1) / 16
            zb = Z_BASE + z0 + min(sori(x0), sori(x1))
            zt = Z_BASE + z0 + h + max(sori(x0), sori(x1))
            obs.append(_box_v(x0, x1, -d, d, zb, zt))
    return [_hull([_proj(v) for v in o]) for o in obs]


_HULLS = _occluders()
GX0, GX1 = AIM_X - (A_X + RX) - 0.02, AIM_X + (A_X + RX) + 0.02
GZ0, GZ1 = Z_MID - (A_Z + RZ) - 0.02, Z_MID + (A_Z + RZ) + 0.02
NGX, NGZ = 104, 96
_DX, _DZ = (GX1 - GX0) / NGX, (GZ1 - GZ0) / NGZ


def _inside(p, hull):
    n = len(hull)
    if n < 3:
        return False
    for i in range(n):
        a, b = hull[i], hull[(i + 1) % n]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < 0.0:
            return False
    return True


_CELLS = []
for iz in range(NGZ):
    z = GZ0 + (iz + 0.5) * _DZ
    for ix in range(NGX):
        x = GX0 + (ix + 0.5) * _DX
        if not any(_inside((x, z), h) for h in _HULLS):
            _CELLS.append((x, z))


def light_visible(t):
    """🔴 #40⑥ は幾何で積分する。発光の値は一切入っていない（隠している部材だけが変わる）"""
    xs, zs = sun_xz(t)
    tot = 0.0
    for x, z in _CELLS:
        tot += field_e(x - xs, z - zs)
    return tot * _DX * _DZ


def light_total(t):
    xs, zs = sun_xz(t)
    n = 0.0
    for iz in range(NGZ):
        z = GZ0 + (iz + 0.5) * _DZ
        for ix in range(NGX):
            n += field_e(GX0 + (ix + 0.5) * _DX - xs, z - zs)
    return n * _DX * _DZ


_TS = [i / N_FRAMES for i in range(N_FRAMES)]
_VS = [light_visible(t) for t in _TS]
_VMAX = max(_VS)

if "--probe-only" in sys.argv:
    print("── 065 TORII 幾何プローブ")
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    best = max(range(N_FRAMES), key=lambda i: _VS[i])
    worst = min(range(N_FRAMES), key=lambda i: _VS[i])
    print("   いちばん明るい frame %d（t=%.3f）／暗い frame %d（t=%.3f）  STILL_FRAME=%d"
          % (best + 1, _TS[best], worst + 1, _TS[worst], STILL_FRAME))
    for nm, t in (("正中(hero)", 0.5), ("柱の裏", 0.25), ("島木の裏", 0.0)):
        xs, zs = sun_xz(t)
        print("   %-10s 光の芯 (%.3f, %.3f)  遮られずに出る光 %5.1f%%（幾何のみ %5.1f%%）"
              % (nm, xs - AIM_X, zs, 100 * light_visible(t) / _VMAX,
                 100 * light_visible(t) / light_total(t)))
    h = TOP_Z - Z_BASE
    print("   鳥居 実寸 幅 %.3f（%.1f%%）× 高 %.3f（%.1f%%）→ 長辺 %.1f%%（55〜65%%）"
          % (WIDTH, WIDTH / FRAME_W * 100, h, h / FRAME_H * 100,
             max(WIDTH / FRAME_W, h / FRAME_H) * 100))
    print("   柱の下端 z=%.3f  笠木の天端 z=%.3f  画面 上端 3.71 / キャプション上端 1.09"
          % (Z_BASE, TOP_Z))
    print("   下の余白 %.3f（%.1f%%）／上の余白 %.3f（%.1f%%）"
          % (Z_BASE - 1.09, (Z_BASE - 1.09) / FRAME_H * 100,
             3.71 - TOP_Z, (3.71 - TOP_Z) / FRAME_H * 100))
    ml = 0.0
    for x, z in _CELLS:
        ml += 1.0 if field_e(x - AIM_X, z - Z_HERO) > 0.045 else 0.0
    ml *= _DX * _DZ * 0.938 ** 2
    ab = 2 * X_KASA * 0.13 + 2 * (2 * R_COL_B * H_COL) + 2 * X_NUKI * 0.102
    cz = (ab * (Z_BASE + 0.80) + ml * Z_HERO) / (ab + ml)
    print("   ざっくり重心 z=%.3f → c_y≈%.1f%%（天地の条件：51以下 か 75以上）"
          % (cz, (3.71 - cz) / (0.8 * FRAME_H) * 100))
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


mat_body = black_material("torii_touki", RECIPE)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・world 実寸。object.scale / transform_apply 不使用＝#15） ----
def _rect_ring(bm, c, U, V, hu, hv):
    """断面＝角丸の無い矩形。4·NK 点で一周（DISPLACE が乗る密度を掃引の段階で作る）"""
    pts = []
    for side in range(4):
        for k in range(NK):
            s = k / NK
            if side == 0:      u, v = -hu + 2 * hu * s, -hv
            elif side == 1:    u, v = hu, -hv + 2 * hv * s
            elif side == 2:    u, v = hu - 2 * hu * s, hv
            else:              u, v = -hu, hv - 2 * hv * s
            pts.append(bm.verts.new((c[0] + U[0] * u + V[0] * v,
                                     c[1] + U[1] * u + V[1] * v,
                                     c[2] + U[2] * u + V[2] * v)))
    return pts


def sweep(name, p0, p1, U, V, hu, hv, nseg=NSEG, bend=None, taper=None):
    """p0→p1 へ矩形断面を掃引した閉じたソリッド。bend(s)＝V 方向へのずれ、taper(s)＝断面の倍率"""
    bm = bmesh.new()
    rings = []
    for j in range(nseg + 1):
        s = j / nseg
        c = [p0[i] + (p1[i] - p0[i]) * s for i in range(3)]
        if bend is not None:
            d = bend(c)
            c = [c[0] + V[0] * d, c[1] + V[1] * d, c[2] + V[2] * d]
        f = 1.0 if taper is None else taper(s)
        rings.append(_rect_ring(bm, c, U, V, hu * f, hv * f))
    n = 4 * NK
    for j in range(nseg):
        for k in range(n):
            k2 = (k + 1) % n
            bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    for idx, sign in ((0, -1), (nseg, 1)):
        c = [sum(v.co[i] for v in rings[idx]) / n for i in range(3)]
        cv = bm.verts.new(c)
        for k in range(n):
            k2 = (k + 1) % n
            bm.faces.new((cv, rings[idx][k], rings[idx][k2])[::sign])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return me


def column_mesh(sgn):
    """柱＝内へ転び、上へ細る円柱。上端は島木に少し埋める（継ぎ目を見せない）"""
    bm = bmesh.new()
    rings = []
    for j in range(NCJ + 1):
        s = j / NCJ
        ax = AIM_X + sgn * (X_COL_B + (X_COL_T - X_COL_B) * s)
        r = R_COL_B + (R_COL_T - R_COL_B) * s
        z = Z_BASE + (H_COL + 0.030) * s
        rings.append([bm.verts.new((ax + r * math.cos(2 * math.pi * k / NCK), 0.0,
                                    z)) for k in range(NCK)])
        for k in range(NCK):
            th = 2 * math.pi * k / NCK
            rings[-1][k].co = (ax + r * math.cos(th), r * math.sin(th), z)
    for j in range(NCJ):
        for k in range(NCK):
            k2 = (k + 1) % NCK
            bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    for idx, rev in ((0, True), (NCJ, False)):
        cv = bm.verts.new((AIM_X + sgn * (X_COL_B if idx == 0 else X_COL_T), 0.0,
                           Z_BASE + (0.0 if idx == 0 else H_COL + 0.030)))
        for k in range(NCK):
            k2 = (k + 1) % NCK
            f = (cv, rings[idx][k], rings[idx][k2])
            bm.faces.new(f[::-1] if rev else f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("hashira"); bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=0.52):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


EX, EY, EZ = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
parts = [link(column_mesh(-1.0), "hashira_hidari", mat_body),
         link(column_mesh(+1.0), "hashira_migi", mat_body)]

# 貫（出貫）。柱を貫いて外へ出る＝これが「明神鳥居」を宣言する部材
parts.append(link(sweep("nuki",
                        (AIM_X - X_NUKI, 0.0, Z_BASE + (Z_NUKI0 + Z_NUKI1) / 2),
                        (AIM_X + X_NUKI, 0.0, Z_BASE + (Z_NUKI0 + Z_NUKI1) / 2),
                        EY, EZ, D_NUKI, (Z_NUKI1 - Z_NUKI0) / 2), "nuki", mat_body))
# 楔（くさび）＝貫の出に打ち込む。上が太く下が細い
for sgn, nm in ((-1.0, "hidari"), (1.0, "migi")):
    cx = AIM_X + sgn * X_KUSABI
    parts.append(link(sweep("kusabi_" + nm,
                            (cx, 0.0, Z_BASE + Z_KUSABI1), (cx, 0.0, Z_BASE + Z_KUSABI0),
                            EX, EY, W_KUSABI, D_KUSABI, nseg=10,
                            taper=lambda s: 1.0 - 0.34 * s), "kusabi_" + nm, mat_body))
# 額束（がくづか）＝貫と島木のあいだ、**まんなかに立つ**唯一の部材
parts.append(link(sweep("gakuzuka",
                        (AIM_X, 0.0, Z_BASE + Z_NUKI1), (AIM_X, 0.0, Z_BASE + Z_SHIMA0),
                        EX, EY, W_GAKU, D_GAKU, nseg=14), "gakuzuka", mat_body))
# 島木・笠木＝同じ反りの曲線に乗るので、そのまま積み重なる
for nm, hx, z0, h, d in (("shimagi", X_SHIMA, Z_SHIMA0, H_SHIMA, D_SHIMA),
                         ("kasagi", X_KASA, Z_KASA0, H_KASA, D_KASA)):
    zc = Z_BASE + z0 + h / 2
    parts.append(link(sweep(nm, (AIM_X - hx, 0.0, zc), (AIM_X + hx, 0.0, zc),
                            EY, EZ, d, h / 2, bend=lambda c: sori(c[0])), nm, mat_body))


def add_relief(objs, recipe):
    """黒の肌は実ジオメトリで作る（Bump は黒では見えない＝#52）。造形が済んだ最後に呼ぶ。
       🔴 SUBSURF は掛けない——Catmull-Clark は角のある部材を丸めてしまう。密度は掃引で作った。"""
    r = BLACK_RECIPES[recipe]
    tex = bpy.data.textures.new("relief_" + recipe, 'CLOUDS')
    tex.noise_scale = r["dsize"]
    for o in objs:
        d = o.modifiers.new("disp", 'DISPLACE')
        d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5


add_relief(parts, RECIPE)


# ---------- 光（鳥居のうしろ）------------------------------------
def glow_mesh():
    """光の面＝楕円のディスク。E を UV 'grad' の U に焼く（#34/#39）。
       🔴 r=1 で E=0 → そこは **完全に透明**（#49①：ES=0 の板は白い背景の前では黒い板）"""
    bm = bmesh.new()
    ctr = bm.verts.new((0.0, 0.0, 0.0))
    rings = []
    for j in range(1, NRF + 1):
        rho = j / NRF
        rings.append([bm.verts.new((rho * RX * math.cos(2 * math.pi * k / NAF), 0.0,
                                    rho * RZ * math.sin(2 * math.pi * k / NAF)))
                      for k in range(NAF)])
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
            lp[uvl].uv = (field_e(co.x, co.z), 0.5)
    me = bpy.data.meshes.new("hikari"); bm.to_mesh(me); bm.free()
    return me


def glow_material(name):
    """Emission ⊕ Transparent。fac も強さも E から引くので、**外周に縁が存在しない**。
       横縞（薄雲の層）は world Z から引く＝光が動いても縞は空に残る（#74⑤）"""
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

    geo = nt.nodes.new("ShaderNodeNewGeometry")
    gsep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], gsep.inputs["Vector"])

    def band(freq, amp, phase):
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = 2.0 * math.pi * freq
        nt.links.new(gsep.outputs["Z"], mul.inputs[0])
        add = nt.nodes.new("ShaderNodeMath"); add.operation = 'ADD'
        add.inputs[1].default_value = phase
        nt.links.new(mul.outputs[0], add.inputs[0])
        sn = nt.nodes.new("ShaderNodeMath"); sn.operation = 'SINE'
        nt.links.new(add.outputs[0], sn.inputs[0])
        ma = nt.nodes.new("ShaderNodeMath"); ma.operation = 'MULTIPLY_ADD'
        ma.inputs[1].default_value = 0.5 * amp
        ma.inputs[2].default_value = 0.5 * amp
        nt.links.new(sn.outputs[0], ma.inputs[0])
        return ma.outputs[0]

    b1, b2 = band(HAZE_F1, HAZE_A1, 0.0), band(HAZE_F2, HAZE_A2, 1.7)
    bsum = nt.nodes.new("ShaderNodeMath"); bsum.operation = 'ADD'
    nt.links.new(b1, bsum.inputs[0]); nt.links.new(b2, bsum.inputs[1])
    haze = nt.nodes.new("ShaderNodeMath"); haze.operation = 'SUBTRACT'
    haze.inputs[0].default_value = 1.0
    nt.links.new(bsum.outputs[0], haze.inputs[1])

    # 芯だけ白へ抜く＝halo はこれでしか出ない（#70④）
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

    es0 = nt.nodes.new("ShaderNodeMath"); es0.operation = 'MULTIPLY'
    es0.inputs[1].default_value = ES_CORE
    nt.links.new(E, es0.inputs[0])
    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    nt.links.new(es0.outputs[0], es.inputs[0]); nt.links.new(haze.outputs[0], es.inputs[1])

    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")

    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_ALPHA
    nt.links.new(E, a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MULTIPLY'
    nt.links.new(a1.outputs[0], a2.inputs[0]); nt.links.new(haze.outputs[0], a2.inputs[1])

    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("hikari")
glow = bpy.data.objects.new("hikari", glow_mesh())
bpy.context.collection.objects.link(glow)
glow.data.materials.append(mat_glow)
glow.visible_shadow = False       # 光そのものが逆光を遮らないように

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    xs, zs = sun_xz(i / N_FRAMES)
    glow.location = (xs, Y_GLOW, zs)
    glow.keyframe_insert("location", frame=f + 1)

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
        caption("MIDDLE STUDY 065 — TORII", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, Z_BASE + 0.62)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
# 🔴 9周目：4灯目（逆光）は #55/#56 の不変条件だが、**背光の作では白い逆光が
#    ライムの回り込みを上書きする**——柱と横木の縁が全部「白い線」になり、
#    黒の上に暗いライムが1画素も乗らない（＝#14 の std が 21〜24 で止まった正体のひとつ）。
#    灯を消すのではなく、**ライムの随伴光より弱くする**（1800→620W）。
back = area("back", (0.0, 5.2, 2.2), 4.0, 620, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：鳥居は抜けだらけ＝逆光がそのままカメラに写る

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

# 🔴 6周目。**白い背景の前では、光の裾は「暗いライム」にならない**——薄くなるほど白へ寄るので、
#    ライムの輝度分布は上へ潰れて std が 21 で頭打ちになった（#14 のペンキ化判定に引っかかる）。
#    暗いライムが作れるのは**黒の上だけ**なので、柱と横木の縁をライムで舐める灯を足す。
#    床は受光から外す（#58 の床のライムは既に 27% あり、これ以上は舞台が緑になる）。
rimlamps = []
for sx, sy, sz, w in ((-1.05, 1.05, Z_BASE + 0.66, 230.0), (1.05, 1.05, Z_BASE + 0.66, 230.0),
                      (0.00, 1.45, Z_BASE + 1.20, 260.0)):
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
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not glow:
        lit_by_lime.objects.link(o)
for lp in limelamps:
    lp.light_linking.receiver_collection = lit_by_lime

lit_by_rim = bpy.data.collections.new("lit_by_rim")
bpy.context.scene.collection.children.link(lit_by_rim)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not glow and o is not floor_obj:
        lit_by_rim.objects.link(o)
for lp in rimlamps:
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
        if o.type != 'MESH' or o is floor_obj or o is glow:
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 鳥居の投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_065.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    glow.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {glow.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = glow
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
