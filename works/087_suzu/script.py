# =============================================================
# MIDDLE STUDY 087 — SUZU（鈴 / a bell rings because it is cut）
#
#   光の型＝隙間（#53）  構図の型＝群（#57）  ドメイン＝神事の鳴り物・鋳鈴
#
# 鈴は、閉じた球では鳴らない。鋳上がった球の腹を一文字に切って、はじめて鈴になる。
# **音が出てくるのは金属からではない。切れているところからだ。**
# 中には丸（＝舌）が一つ、どこにも留まらずに入っている。丸は鈴の一部ではない。
# くっついていない物が、切れ目の向こうで動いている——それが鳴るということ。
#
# 造形：鈴は「切れ目の長手」を local X に取った回転体的パラメータで書く。
#       断面は (y, z) の楕円（z 方向に KZ=0.93 扁平＝鋳鈴の腹）。切れ目は
#       φ=−π/2（local −Z）を中心に半角 Δ(x)=Δ0·(1−(2x/L)²)^0.40 で開く。
#       指数 0.40 は「両端が丸く終わる」＝実物の鳴り口（端に小孔が来る）の形。
#       外面・内面・鳴り口の厚みの壁（rim）を1枚の閉じた殻として張り、
#       合わせ目（φ=0,π の鋳バリ）と鳴り口を挟む2本の圏線を半径に焼く。
#       🔴 黒の肌は tetsu（#52/MATERIALS.md）だが DISPLACE は使わない——
#          SUBSURF が鳴り口の縁を枕形に丸める（#65 と同型）。鋳肌は頂点に直接焼く。
#
# 光：隙間。**光っているのは鈴の内壁そのもの**（中に電球を置かない＝#96 の一手）。
#     内壁の発光は鳴り口の真向かい（local +Z 側）が芯で、鳴り口の縁へ向けて落ちて
#     G_LO で 0 になる＝縁は純黒の裏当て（#32）。だから外から見えるのは
#     **切れ目の形をした光**だけで、鈴そのものは光らない。
#     🔴 発光の値は1フレームも動かしていない（#69②／#70④）。振れは全部ジオメトリ。
#
# 動き：①各鈴が世界Zまわりに 360°/loop 回る（τ だけ傾けてあるので鳴り口は
#         1周に1度だけカメラを向く）。s=±1 で2個だけ逆回し＝光が消えきらない。
#       ②舌が内部を 2周/loop で回り、鳴り口を横切って光を欠けさせる
#       ③各鈴が半径 A の小円を1周（浮遊）
#       すべて整数周期＝数学的に閉じる。確かめ方＝`python3 script.py -- geom`
#       （Blender を起動せず、画面に出ている鳴り口の面積を積分し、
#         さらに**塊どうしの画面上の最小すきま**をフレーム総なめで出す＝群の生命線）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = float(os.environ.get("LIME_W", "110"))

# --- 鈴の形（local：切れ目の長手＝X／鳴り口＝−Z／鈕＝+Z）-------------
P_SHAPE = 2.10                 # 腹の膨らみ（2.0＝真球・大きいほど鋳物らしく角が張る）
KZ = 0.86                      # 鳴り口−鈕の軸方向の扁平（🔴 0.93 は「球」＝ボールに読めた）
T_REL = 0.085                  # 肉厚 / R（🔴 斜めから覗くので、厚いと奥がけられて光が出ない）
SLIT_L = float(os.environ.get("SLIT_L", "1.96"))   # 切れ目の長さ / R
# 🔴 実物の鳴り口は**端から端まで**走り、両端は側面の小孔で終わる。1.8R では切れ目の端が
#    輪郭の内側に収まってしまい、「球の表面についた模様」＝目に読まれる。2R 近くまで伸ばすと
#    切れ目が**シルエットを切り欠く**ので、面の模様ではなく「割れている物」になる。
SLIT_A = float(os.environ.get("SLIT_A", "0.35"))   # 切れ目の半角(rad)
# 🔴 1周目は 0.46×1.30＝ほぼ丸穴で、8個そろって**目**に読めた（#95：記号の形の孔は既知の記号になる）。
#    halo は口の大きさで買う（#88）が、**口が丸いと題材が死ぬ**。細長い「切れ目」に振り、
#    足りない光は個数（8個）と発光の勾配で買う。
SLIT_E = 0.40                  # 端の丸み（小さいほど両端が丸く終わる）
NX, NPHI = 60, 80
PIT = 0.024                    # 鋳肌（R 比。🔴 0.040 は胡桃の殻。鋳鈴の肌はもっと静か）
SHOULD = 0.120                 # 肩の絞り（鈕の側を細く＝球でなく鈴の輪郭にする）
SEAM_H, SEAM_W = 0.021, 0.075  # 合わせ目の鋳バリ（R 比・rad）
GR_OFF, GR_D, GR_W = 0.50, 0.020, 0.060   # 鳴り口を挟む圏線
LOOP_MAJ, LOOP_MIN, LOOP_UP = 0.30, 0.066, 0.075   # 鈕（R 比。🔴 小さいと「実（み）のヘタ」に読める）
TONGUE_R, TONGUE_ORB, TONGUE_Z = 0.16, 0.80, -0.30  # 舌（内半径比）
# 🔴 0.30/0.38/−0.30 も 0.24/0.58/−0.40 も、舌が鳴り口の真ん中に据わって**瞳**になった。
#    小さくしても真ん中にある限り瞳。🔴 **内壁に接触させる**（軌道半径 0.80·Ri＋球半径 0.16 ≒ 0.96）
#    ＝舌は宙に浮いた玉ではなく「内側を転がっている物」になり、光を横から欠けさせる。

# --- 光（内壁の勾配。UV.x = g、g=1 が鳴り口の真向かい）---------------
G_LO, G_HI = 0.09, 0.22        # 🔴 ここより下＝鳴り口の縁（リップ）は純黒（#32）
G_PK0, G_PK1 = 0.34, 0.50      # 芯の立ち上がり
G_PK2, G_PK3 = 0.62, 0.86      # 芯の落ち（🔴 上を切らないと天井が一面白く飛び #14 を割る）
G_DP0, G_DP1, DEEP_MIN = 0.22, 0.52, 0.16
# 🔴 g は「鳴り口の真向かい＝1」。斜めから覗くと見えているのは g が 0.05〜0.6 の帯で、
#    4周目まで芯を 0.78〜0.97 に置いていたため**見えている所は全部消灯していた**。
ES_BASE = float(os.environ.get("ES_BASE", "2.40"))
ES_CORE = float(os.environ.get("ES_CORE", "5.00"))
WHITE_BASE, WHITE_TO = 0.12, 0.84
# 🔴 halo（150<R<230・G>200・90<B<190）は**純ライムでは作れない**（青が上がらない・#81③）。
#    芯の帯を狭めて勾配を残しつつ、その帯だけ白を強く混ぜて halo の色域に入れる。
K_MIX, E_FLOOR = 16.0, 0.12    # 🔴 #85①：裾を 0 に切らないと鈴が丸ごと光る

# --- 群（x, y, z, R, τ°, ρ°, tp, s, A, β°, γ°）-----------------------
#     位置は「画面上で先に置いてから」世界座標へ戻した（塊の最小すきま＝#81 の 0.248 が生命線）
#     🔴 tp ＝その鈴の鳴り口がカメラを正面に向く時刻。**等間隔に配ってはいけない**
#        （#71①：位相を等間隔にすると群の光量は定数になる）。かといって全部そろえると
#        1周のうち1/3が真っ暗になる（1周目の geom で実際にそうなった）。
#        だから **4個を t≈1/3 に束ね、1個を半開き(0.45)・1個を裏(0.72)に置く**。
#        🔴 6周目まで8個で組んでいたが、**8個ぶんの口の合計では光が足りなかった**
#        （halo 5765・ライム面積 0.42%）。#88＝光は口の大きさで買う。個数を 8→6 に減らし、
#        R を 0.16〜0.22 → 0.27〜0.28 に上げ、切れ目も 0.235→0.38rad に広げた。
#        配置は総当たりで解いた（最小すきま 144px ≥ #81 の設計値 141px）。
#        2個を1点に寄せた版（0.79/0.84）は谷が深く長くなりすぎた（geom で 20.3倍）。
# 🔴 τ＝鈕の軸を世界Zから何度倒すか。**2周目まで 64〜108°＝鈴を横倒しにしていた**ので、
#    鳴り口がカメラを向くと鈕はちょうど真裏に隠れ、「穴の開いた球」＝猫の目になった（#95）。
#    τ を 46〜68° にすると鈕は立つが、**鳴り口はまだ球の真ん中**にあり目のまま（3周目）。
#    27〜44° まで起こすと目には読まれなくなるが、今度は**光が死ぬ**（4周目：見えているのが
#    発光を切ってある縁ばかりになる）。41〜57° が両立点で、切れ目は腹を横切る**長い一文字**
#    として下半分に出る。勾配は「奥が芯」ではなく「**縁から奥へ立ち上がる**」に組み替えた。
BELLS = [
    (0.4599, -0.70, 2.0870, 0.2702,  49,  14, 0.30,  1, 0.030,  20,   0),
    (0.7764, 0.40, 1.3098, 0.2798,  44,  62, 0.36, -1, 0.026, 150, 120),
    (-0.0327, -0.20, 1.4347, 0.2708,  56, -38, 0.45,  1, 0.032, 265, 240),
    (1.0731, 1.10, 2.8829, 0.2824,  41,  80, 0.27, -1, 0.024,  70,  60),
    (1.3463, 1.50, 1.9708, 0.2779,  58,  28, 0.72,  1, 0.022, 205, 300),
    (0.0892, 0.70, 2.9195, 0.2819,  46, -66, 0.33,  1, 0.028, 330, 180),
]
STILL_FRAME = 41      # t=1/3（＝束ねた6個が開いている瞬間。残る2個は黒い鈴のまま）


def psi_of(i, t):
    """世界Zまわりの回り。t=tp でちょうど鳴り口がカメラを向く。"""
    x, y, z, R, tau, rho, tp, s, A, b, g = BELLS[i]
    return math.pi / 2 + 2 * math.pi * s * (t - tp)


def drift_of(i, t):
    x, y, z, R, tau, rho, tp, s, A, b, g = BELLS[i]
    a = 2 * math.pi * t + math.radians(b)
    return (A * math.cos(a), 0.40 * A * math.sin(a), A * math.sin(a))


def tongue_of(i, t):
    """舌は内部を 2周/loop。鳴り口の側（local −Z 寄り）を回る。"""
    x, y, z, R, tau, rho, tp, s, A, b, g = BELLS[i]
    Ri = R * (1.0 - T_REL)
    a = 4 * math.pi * t + math.radians(g)
    return (TONGUE_ORB * Ri * math.cos(a), TONGUE_ORB * Ri * math.sin(a),
            TONGUE_Z * Ri * KZ)


def slit_half(u):
    """切れ目の半角（u = 2x/L ∈ [-1,1] の外では 0）。"""
    if abs(u) >= 1.0:
        return 0.0
    return SLIT_A * (1.0 - u * u) ** SLIT_E


def mouth_dir(i, t):
    """鳴り口の法線（world）。R = Rz(ψ)·Ry(τ) なので local(0,0,-1) の像。"""
    tau = math.radians(BELLS[i][4])
    ps = psi_of(i, t)
    return (-math.sin(tau) * math.cos(ps), -math.sin(tau) * math.sin(ps), -math.cos(tau))


# =============================================================
# -- geom : Blender を起動せず「画面に出ている鳴り口」を積分する（#40⑥）
#           ＋ bbox・長辺・重心・**塊の画面上の最小すきま（群の判定）**
# =============================================================
TAN_H = (FRAME_W / 2) / 8.3
TAN_V = (FRAME_H / 2) / 8.3
PX_W, PX_H = 1600, 2000


def to_screen(p):
    d = p[1] + 8.3
    return (0.5 + 0.5 * (p[0] - AIM_X) / d / TAN_H,
            0.5 + 0.5 * (p[2] - LOOK_Z) / d / TAN_V)


def bell_pose(i, t):
    x, y, z, R, tau, rho, tp, s, A, b, g = BELLS[i]
    dx, dy, dz = drift_of(i, t)
    return (x + dx, y + dy, z + dz, R)


def mouth_area(R):
    """鳴り口の開口面積（実面積・世界単位）。∫ 2Δ(x)·r(x) dx を数値で。"""
    tot, N = 0.0, 160
    L = SLIT_L * R
    for k in range(N):
        xx = -L / 2 + L * (k + 0.5) / N
        u = 2 * xx / L
        rr = R * (1.0 - min(1.0, abs(xx) / R) ** P_SHAPE) ** (1.0 / P_SHAPE)
        tot += 2 * slit_half(u) * rr * (L / N)
    return tot


def visible_lime(t):
    """見えている「切れ目の光」の総量。開口 × cosθ × 肉厚のけられ × 舌の欠け。"""
    tot = 0.0
    for i in range(len(BELLS)):
        bx, by, bz, R = bell_pose(i, t)
        ux, uy, uz = (AIM_X - bx), (-8.3 - by), (LOOK_Z - bz)
        ln = math.sqrt(ux * ux + uy * uy + uz * uz)
        ux, uy, uz = ux / ln, uy / ln, uz / ln
        mx, my, mz = mouth_dir(i, t)
        c = mx * ux + my * uy + mz * uz
        if c <= 0.04:
            continue
        # 肉厚 T が口の幅 W をけらせる（斜めから覗くほど奥が見えない）
        W = 2 * SLIT_A * R * KZ
        vign = max(0.0, 1.0 - (T_REL * R / W) * math.sqrt(max(0.0, 1 - c * c)) / max(c, 1e-3))
        # 舌の欠け（鳴り口の正面に来ているときだけ効く）
        tgx, tgy, tgz = tongue_of(i, t)
        Ri = R * (1.0 - T_REL)
        occ = 1.0 - 0.26 * max(0.0, 1.0 - math.hypot(tgx, tgy) / (0.75 * Ri))
        tot += mouth_area(R) * c * vign * occ / ((by + 8.3) / 8.3) ** 2
    return tot


modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]

if "geom" in modes:
    print("── 画面に出ている切れ目の光（#40⑥）と群の成立（Blender 不使用）")
    vals = []
    for f in range(0, N_FRAMES, 8):
        t = f / N_FRAMES
        v = visible_lime(t)
        vals.append((v, f + 1))
        opens = "".join("●" if (mouth_dir(i, t)[1] < -0.35) else "·" for i in range(len(BELLS)))
        print("   f%3d  t %.2f  可視発光 %.5f   鳴り口 %s" % (f + 1, t, v, opens))
    lo, hi = min(v for v, _ in vals), max(v for v, _ in vals)
    if lo <= 1e-9:
        print("   🔴 可視発光が 0 のフレームがある＝1周のどこかで作が消える")
    else:
        print("   #40⑥ min/max = %.3f   光の振れ（max/min）= %.2f   最大は f%d"
              % (lo / hi, hi / lo, max(vals)[1]))

    # --- 塊の最小すきま（群＝clusters≥5 の生命線。#81：設計値 141px）---
    worst, wf = 1e9, 0
    for f in range(N_FRAMES):
        t = f / N_FRAMES
        sc = []
        for i in range(len(BELLS)):
            bx, by, bz, R = bell_pose(i, t)
            d = by + 8.3
            sx, sy = to_screen((bx, by, bz))
            sc.append((sx * PX_W, (1 - sy) * PX_H, 800 * R / (d * TAN_H)))
        for a in range(len(sc)):
            for b in range(a + 1, len(sc)):
                g = math.hypot(sc[a][0] - sc[b][0], sc[a][1] - sc[b][1]) - sc[a][2] - sc[b][2]
                if g < worst:
                    worst, wf = g, f + 1
    print("   塊どうしの最小すきま %.0f px（f%d）  ※#81 の設計値 141px・12px を割ると連結する"
          % (worst, wf))

    # --- bbox / 長辺 / 重心 ---
    t = (STILL_FRAME - 1) / N_FRAMES
    xs, ys = [], []
    for i in range(len(BELLS)):
        bx, by, bz, R = bell_pose(i, t)
        Rb = R * (1.0 + LOOP_UP + LOOP_MAJ + LOOP_MIN)      # 鈕まで含めた外接
        d = by + 8.3
        rp = 800 * Rb / (d * TAN_H)
        sx, sy = to_screen((bx, by, bz))
        xs += [sx * PX_W - rp, sx * PX_W + rp]
        ys += [(1 - sy) * PX_H - rp, (1 - sy) * PX_H + rp]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print("   bbox x %.0f..%.0f px  y %.0f..%.0f px   横 %.1f%%  縦 %.1f%%  長辺 %.1f%%（55〜65）"
          % (x0, x1, y0, y1, (x1 - x0) / PX_W * 100, (y1 - y0) / PX_H * 100,
             max((x1 - x0) / PX_W, (y1 - y0) / PX_H) * 100))
    print("   接触 %d 辺   重心x %.1f%%   下端 %.0f px（キャプション帯 1600px より上であること）"
          % ((x0 <= 0) + (x1 >= PX_W) + (y0 <= 0) + (y1 >= PX_H),
             (x0 + x1) / 2 / PX_W * 100, y1))
    for nm, z in (("tagline", 1.02), ("logo", 0.85), ("study", 0.74)):
        print("   キャプション %-8s 画面の上から %.1f%%" % (nm, (1 - to_screen((AIM_X, -1.7, z))[1]) * 100))
    print("   鳴り口の開口 %.4f〜%.4f（世界面積）" % (mouth_area(min(b[3] for b in BELLS)),
                                              mouth_area(max(b[3] for b in BELLS))))
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

# ---------- マテリアル（MATERIALS.md の tetsu・#52）----------
TETSU = dict(rough=0.50, spec=0.32, metal=0.35)
# 🔴 DISPLACE は使わない（鳴り口の縁が丸まる＝#65）。鋳肌は頂点に焼いてある。


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p, r):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_tetsu, mp_ = principled("tetsu"); apply_black(mp_, TETSU)


def glow_material(name):
    """内壁の勾配。UV.x = g（1 が鳴り口の真向かい＝芯、G_LO 以下は純黒の裏当て）。
       🔴 キーフレームは1本も無い。光の振れはジオメトリ（回り・舌）だけで作る。"""
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

    gate = mr(G_LO, G_HI, 0.0, 1.0)
    pk_u = mr(G_PK0, G_PK1, 0.0, 1.0)
    pk_d = mr(G_PK2, G_PK3, 1.0, 0.0)
    peak = nt.nodes.new("ShaderNodeMath"); peak.operation = 'MINIMUM'
    nt.links.new(pk_u.outputs["Result"], peak.inputs[0])
    nt.links.new(pk_d.outputs["Result"], peak.inputs[1])
    deep = mr(G_DP0, G_DP1, DEEP_MIN, 1.0)

    sm = nt.nodes.new("ShaderNodeMath"); sm.operation = 'MULTIPLY_ADD'
    sm.inputs[1].default_value = (ES_CORE - ES_BASE) / ES_CORE
    sm.inputs[2].default_value = ES_BASE / ES_CORE
    nt.links.new(peak.outputs[0], sm.inputs[0])
    Ed = nt.nodes.new("ShaderNodeMath"); Ed.operation = 'MULTIPLY'
    nt.links.new(deep.outputs["Result"], Ed.inputs[0])
    nt.links.new(sm.outputs[0], Ed.inputs[1])
    Em = nt.nodes.new("ShaderNodeMath"); Em.operation = 'MULTIPLY'
    nt.links.new(gate.outputs["Result"], Em.inputs[0])
    nt.links.new(Ed.outputs[0], Em.inputs[1])

    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = 0.0
    wmr.inputs["From Max"].default_value = 1.0
    wmr.inputs["To Min"].default_value = WHITE_BASE
    wmr.inputs["To Max"].default_value = WHITE_TO
    nt.links.new(peak.outputs[0], wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])
    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    es.inputs[1].default_value = ES_CORE
    nt.links.new(Em.outputs[0], es.inputs[0])
    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])

    blk = nt.nodes.new("ShaderNodeBsdfPrincipled")
    apply_black(blk, TETSU)                                 # 🔴 #32：裏当ては純黒の鉄
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = E_FLOOR
    nt.links.new(gate.outputs["Result"], sub.inputs[0])
    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_MIX
    nt.links.new(sub.outputs[0], a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MAXIMUM'
    a2.inputs[1].default_value = 0.0
    nt.links.new(a1.outputs[0], a2.inputs[0])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("naka")


# ---------- 鈴の殻（local：切れ目の長手＝X・鳴り口＝−Z）----------
def wrapd(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def base_r(x, R):
    u = min(1.0, abs(x) / R)
    return R * (1.0 - u ** P_SHAPE) ** (1.0 / P_SHAPE)


def shoulder(phi):
    """鈕の側（φ=+π/2）を絞り、鳴り口の側を膨らませる＝球でなく鈴の輪郭。"""
    return 1.0 - SHOULD * math.sin(phi)


def skin(x, phi, R, sd):
    """鋳肌（頂点に焼く）＋合わせ目の鋳バリ＋鳴り口を挟む圏線。φ は 2π 周期。"""
    # 🔴 sin(x)·sin(φ) の積は格子になり、黒い球の上で**ゴルフボール**に見えた（1周目）。
    #    斜めに走る波の和（q は整数＝2π 周期）に替えると鋳肌の不定形になる。
    v = (0.42 * math.sin(9.0 * x / R + 5 * phi + 1.1 * sd)
         + 0.30 * math.sin(17.0 * x / R - 11 * phi + 2.7 * sd)
         + 0.20 * math.sin(29.0 * x / R + 19 * phi + 0.4 * sd)
         + 0.14 * math.sin(43.0 * x / R - 7 * phi + 3.9 * sd)
         + 0.10 * math.sin(61.0 * x / R + 27 * phi + 5.3 * sd))
    d = PIT * v
    for c in (0.0, math.pi):                       # 合わせ目（鋳バリ）
        d += SEAM_H * math.exp(-(wrapd(phi - c) / SEAM_W) ** 2)
    for c in (-math.pi / 2 - GR_OFF, -math.pi / 2 + GR_OFF):   # 圏線
        if abs(x) < 0.82 * R:
            d -= GR_D * math.exp(-(wrapd(phi - c) / GR_W) ** 2)
    return R * d


def shell_rings(R, sd, inner):
    """各ステーションの (x, φの配列, 半径の配列)。φ は鳴り口の外側を NPHI+1 点で。"""
    Ri = R * (1.0 - T_REL)
    rings = []
    for j in range(NX + 1):
        x = -R + 2 * R * j / NX
        dlt = slit_half(2 * x / (SLIT_L * R))
        a0 = -math.pi / 2 + dlt
        span = 2 * math.pi - 2 * dlt
        phis = [a0 + span * k / NPHI for k in range(NPHI + 1)]
        if inner:
            # 🔴 内面は「小さい相似形」ではなく**等肉厚のオフセット**。相似形だと
            #    切れ目の両端で肉が 0.28R まで厚くなり、口の端が深いトンネルになって光が出ない。
            rr = [max(0.004 * R, min(base_r(x, R) * shoulder(p) - T_REL * R,
                                     base_r(x, R) * shoulder(p) * 0.85)) for p in phis]
        else:
            rr = [max(0.002 * R, base_r(x, R) * shoulder(p) + skin(x, p, R, sd)) for p in phis]
        rings.append((x, phis, rr, dlt))
    return rings


def to_xyz(x, phi, r):
    return (x, r * math.cos(phi), r * KZ * math.sin(phi))


def shell_mesh(name, R, sd, inner):
    rings = shell_rings(R, sd, inner)
    verts, faces = [], []
    for (x, phis, rr, dlt) in rings:
        for k in range(NPHI + 1):
            verts.append(to_xyz(x, phis[k], rr[k]))
    row = NPHI + 1
    for j in range(NX):
        for k in range(NPHI):
            q = (j * row + k, j * row + k + 1, (j + 1) * row + k + 1, (j + 1) * row + k)
            faces.append(q[::-1] if inner else q)
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(me); bm.free(); me.update()
    return me


def rim_mesh(name, R, sd):
    """鳴り口の厚みの壁（外の縁 → 内の縁）。切れ目のあるステーションだけ。"""
    ro = shell_rings(R, sd, False)
    ri = shell_rings(R, sd, True)
    verts, faces = [], []
    idx = {}
    for j in range(NX + 1):
        if ro[j][3] <= 1e-6:
            continue
        for side in (0, NPHI):
            for src in (ro, ri):
                x, phis, rr, _ = src[j]
                idx[(j, side, src is ri)] = len(verts)
                verts.append(to_xyz(x, phis[side], rr[side]))
    for j in range(NX):
        if ro[j][3] <= 1e-6 or ro[j + 1][3] <= 1e-6:
            continue
        for side, flip in ((0, False), (NPHI, True)):
            a = idx[(j, side, False)]; b = idx[(j, side, True)]
            c = idx[(j + 1, side, True)]; d = idx[(j + 1, side, False)]
            faces.append((a, b, c, d) if not flip else (d, c, b, a))
    # 切れ目の両端（Δ→0 の側）は外縁と内縁を繋いで塞ぐ
    ends = [j for j in range(NX + 1) if ro[j][3] > 1e-6]
    for j, nb in ((ends[0], ends[0] + 1), (ends[-1], ends[-1] - 1)):
        if (j, 0, False) in idx and (j, NPHI, False) in idx:
            faces.append((idx[(j, 0, False)], idx[(j, 0, True)],
                          idx[(j, NPHI, True)], idx[(j, NPHI, False)]))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    return me


def loop_mesh(name, R, NU=40, NV=14):
    """鈕（吊り手）。XZ 面のトーラス＝腹の真上。"""
    cz = R * KZ + R * LOOP_UP
    Rmaj, Rmin = R * LOOP_MAJ, R * LOOP_MIN
    verts, faces = [], []
    for a in range(NU):
        ta = 2 * math.pi * a / NU
        cx, czz = Rmaj * math.cos(ta), cz + Rmaj * math.sin(ta)
        nx, nz = math.cos(ta), math.sin(ta)
        for b in range(NV):
            tb = 2 * math.pi * b / NV
            verts.append((cx + Rmin * math.cos(tb) * nx,
                          Rmin * math.sin(tb),
                          czz + Rmin * math.cos(tb) * nz))
    for a in range(NU):
        a2 = (a + 1) % NU
        for b in range(NV):
            b2 = (b + 1) % NV
            faces.append((a * NV + b, a2 * NV + b, a2 * NV + b2, a * NV + b2))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    return me


def ball_mesh(name, r, NU=28, NV=16):
    verts, faces = [], []
    for j in range(NV + 1):
        th = math.pi * j / NV
        for k in range(NU):
            ph = 2 * math.pi * k / NU
            verts.append((r * math.sin(th) * math.cos(ph),
                          r * math.sin(th) * math.sin(ph), r * math.cos(th)))
    for j in range(NV):
        for k in range(NU):
            k2 = (k + 1) % NU
            faces.append((j * NU + k, j * NU + k2, (j + 1) * NU + k2, (j + 1) * NU + k))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bm.to_mesh(me); bm.free(); me.update()
    return me


def set_grad_uv(me, R):
    """g = ((1+sinφ)/2)·(1−0.55(x/R)²)。頂点座標から引くので remove_doubles 後でも狂わない。"""
    lay = me.uv_layers.new(name="grad")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            phi = math.atan2(co.z / KZ, co.y)
            g = (1.0 + math.sin(phi)) / 2.0 * (1.0 - 0.55 * min(1.0, (co.x / R) ** 2))
            lay.data[li].uv = (g, 0.5)


def link(me, name, mats, smooth_ang=0.7):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.clear()
    for m in mats:
        ob.data.materials.append(m)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_ang)
    except Exception:
        pass
    return ob


shells, glows, loops, tongues, parts = [], [], [], [], []
for i, (bx, by, bz, R, tau, rho, tp, s, A, b_, g_) in enumerate(BELLS):
    rot = Matrix.Rotation(math.radians(rho), 4, 'Z')        # ρ＝切れ目の向き（メッシュに焼く）
    me_o = shell_mesh("m_kara_%d" % i, R, 1.0 + 0.7 * i, False)
    me_r = rim_mesh("m_fuchi_%d" % i, R, 1.0 + 0.7 * i)
    me_i = shell_mesh("m_uchi_%d" % i, R, 1.0 + 0.7 * i, True)
    set_grad_uv(me_i, R)                                    # 🔴 UV は回す前（local）で引く
    me_l = loop_mesh("m_chu_%d" % i, R)
    for me in (me_o, me_r, me_i, me_l):
        me.transform(rot)
    ob_o = link(me_o, "kara_%d" % i, [mat_tetsu], 0.55)
    ob_r = link(me_r, "fuchi_%d" % i, [mat_tetsu], 0.30)
    ob_i = link(me_i, "uchi_%d" % i, [mat_glow], 1.30)
    ob_l = link(me_l, "chu_%d" % i, [mat_tetsu], 0.70)
    ob_t = link(ball_mesh("m_shita_%d" % i, TONGUE_R * R * (1 - T_REL)),
                "shita_%d" % i, [mat_tetsu], 1.30)
    shells.append((ob_o, ob_r, ob_i, ob_l))
    tongues.append(ob_t)
    parts += [ob_o, ob_r, ob_i, ob_l, ob_t]

# --- キーフレーム（毎フレーム・剛体だけ。イージング無し＝#ループの不変条件）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, ix in enumerate(FR_):
    t = ix / N_FRAMES
    for i, (bx, by, bz, R, tau, rho, tp, s, A, b_, g_) in enumerate(BELLS):
        dx, dy, dz = drift_of(i, t)
        loc = (bx + dx, by + dy, bz + dz)
        eul = (0.0, math.radians(tau), psi_of(i, t))        # R = Rz(ψ)·Ry(τ)
        for ob in shells[i]:
            ob.location = loc
            ob.rotation_euler = eul
            ob.keyframe_insert("location", frame=f + 1)
            ob.keyframe_insert("rotation_euler", frame=f + 1)
        # 舌は鈴の local 座標で回るので、親の姿勢を掛けてから置く
        M = (Matrix.Rotation(eul[2], 4, 'Z') @ Matrix.Rotation(eul[1], 4, 'Y')
             @ Matrix.Rotation(math.radians(rho), 4, 'Z'))
        p = M @ Vector(tongue_of(i, t))
        tongues[i].location = (loc[0] + p.x, loc[1] + p.y, loc[2] + p.z)
        tongues[i].keyframe_insert("location", frame=f + 1)

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
        caption("MIDDLE STUDY 087 — SUZU", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = (0.60, 0.0, 2.25)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：群は塊のあいだが抜けている

# 🔴 #58③：随伴のライム光源は発光体の外。群の裏・床寄り
for sx, sy, sz in ((-0.30, 2.4, 0.30), (0.62, 4.8, 0.30), (1.30, 7.6, 0.30)):
    bpy.ops.object.light_add(type='POINT', location=(sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = LIME_W
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

tH = (STILL_FRAME - 1) / N_FRAMES
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME,
      " 可視発光 %.5f  鳴り口の開き %s"
      % (visible_lime(tH), " ".join("%.2f" % -mouth_dir(i, tH)[1] for i in range(len(BELLS)))))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 61, 91):
        scene.frame_set(fr); dg.update()
        allx, ally = [], []
        for ob in parts:
            ev = ob.evaluated_get(dg)
            for v in list(ev.data.vertices)[::7]:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                allx.append(c.x); ally.append(c.y)
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  "
              "重心x %.1f%%  下端（上から）%.1f%%"
              % (fr, x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100, edge,
                 (x0 + x1) / 2 * 100, (1 - y0) * 100))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_087.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("tetsu_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = TETSU["rough"]
    pi.inputs["Metallic"].default_value = TETSU["metal"]
    m_em = bpy.data.materials.new("naka_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_BASE * 0.80
    for (ob_o, ob_r, ob_i, ob_l) in shells:
        ob_o.data.materials[0] = m_bk
        ob_r.data.materials[0] = m_bk
        ob_l.data.materials[0] = m_bk
        ob_i.data.materials[0] = m_em
    for ob in tongues:
        ob.data.materials[0] = m_bk
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
