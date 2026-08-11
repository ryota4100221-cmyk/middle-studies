# =============================================================
# monaka design. — MIDDLE STUDY 049 "YUMI"（弓 / 和弓 a Japanese longbow）
#
# 黒い弓が一張り、宙にある。握りは木の真ん中ではない——下から三分の一。
# それでも上下の力は釣り合う。引き分けるほどに、弓と弦のあいだが割れて、
# その真ん中にだけ ライム #A5E02E の光が満ちる。手を緩めれば、光はまた一本の線に戻る。
#
# 【機構の刷新＝弾性たわみ（elastica）】シリーズ初。
#   48作すべては剛体変換・ブーリアン・掃引・布シムだった。049 は**曲げそのもの**が機構。
#   弓の曲率  κ(s) = (K0 + Δ(t))·f(s)   を弧長で積分して弓の形を出す（f は握りで 0＝剛）。
#   弦は**伸びない**——長さ L_up / L_lo を拘束として、番え所 N は
#   「上鉾の先を中心とする円」と「下鉾の先を中心とする円」の交点で決まる。
#   → **引き尺 d は与えるものではなく、拘束から出てくる**。
#     曲げると弭（はず）どうしが近づき、余った弦が手元へ膨らむ＝それが引き分け。
#   Δ(t)=Δmax·0.5(1−cos2πt) の整数周期＝完全ループ。
#
# 【光】弓と弦のあいだの隙間**そのもの**が光る。
#   面は毎フレーム張り直す（＝隙間の形）ので #44-b により UV に焼く（#39）。
#   u は「隙間を横切る**正規化**座標」なので、ES は常に弦と弓の際でちょうど 0＝
#   そのまま裏当て（白背景へ緑が漏れない・#26②/#28/#32）。
#   v は握りからの高さ／FZ＝上下は実在の境界に達する前に静かに落ちる。
#
# 🔴 #40⑥ は幾何で積分する（#46）。Blender を起動せずに解ける形にしてある。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
# =============================================================
import bpy, bmesh, math, sys, os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 弓 -------------------------------------------------------
L_BOW    = 2.21        # 弓の全長（弧長）＝和弓「並寸」の実寸
GRIP_F   = 0.355       # 握りの位置（下から）。🔴 和弓の署名＝木の真ん中ではない
GRIP_H   = 0.090       # 握り＝曲がらない剛の区間（片側）
RAMP     = 0.135       # 剛→撓のなめらかな移行
TIP_SOFT = 0.46        # 末端（関）の撓みやすさ。1.0 で中央と同じだけ曲がる
BRACE    = 0.155       # 弓把（ゆづか）＝張ったときの弦と握りの距離
DRAW     = 0.708       # 引き尺（矢束）。拘束を満たす Δmax を二分法で解く（曲率に対し非単調＝手前の枝）
NOCK_UP  = 0.080       # 矢を番える高さ（握りより上）
DEPTH_G  = 0.0560      # 弓の厚み（前後・画面では幅）：握り
#   🔴 実寸（24mm）だと 2.2m の中で針金になり、輪郭が「葉」に読める（1周目）。#34-b：
#      実物の寸法比を写すのではなく、hero で何 px に見えるかで決める
DEPTH_T  = 0.0300      # 同・末端
WIDTH_G  = 0.0400      # 幅（左右・画面では奥行き）
WIDTH_T  = 0.0235
NS       = 480         # 弧長サンプル（積分）
NRING    = 104         # メッシュのリング数
NSEC     = 14          # 断面の分割
R_STR    = 0.0095      # 弦
Z_GRIP   = 1.64        # 握りのワールド高さ

# 握り革（#48：その道具が人と接する所＝回転対称／上下対称を破る部品）
WRAP_LO, WRAP_HI = -0.075, 0.095
WRAP_R   = 0.0070
BAND_R   = 0.0098
BAND_W   = 0.014

# 矢（読みの宣言。弦と一緒に引かれる＝機構がもう一度読める）
ARROW    = False
ARR_L    = 0.95
ARR_R    = 0.0110
FLE_L, FLE_H = 0.120, 0.034

# --- 発光 -----------------------------------------------------
FZ       = 0.125       # 🔴 光の縦の広がり。大きくすると面が開口を全部塞ぎ、弓の内側が黒く埋まって
#                      輪郭が「葉」に読める（3周目の実測）。#40②：帯に絞ると開口が空いて弓に戻る
GPOW     = 1.90        # 勾配のべき（#38④ 暗い裾を締める）
ES_CORE  = 3.1
LAMP_W   = 5.0         # 随伴点光源（#22 spill）。強いと隙間まわりを「塗る」
UOVER    = 1.045
UEDGE    = 0.92        # 面の際の u。1.0 にすると ES=0 の暗い縁が帯に残って中間調を下げる（#31-d の縁版）       # 面を弦・弓の内側へ少しだけ食い込ませる（継ぎ目を黒で隠す）

FPS = 24
N_FRAMES = 120         # 5秒
CAM_LOC = (0.55, -8.3, 1.95)
CENTER_Z = 1.86        # ライトの注視／被写体の中心
LOOK_Z   = 1.90
AIM_X    = 0.36        # 造形が引き分けで右へ出るので注視点も右へ（#18 フレームは右に余裕がある）

# =============================================================
# ここから下（elastica と弦の拘束）は Blender に依存しない純 math。
# probe も #40⑥ も STILL_FRAME も、シーンを組まずにここで解ける（#31 の規律）。
# =============================================================
S_G = GRIP_F * L_BOW
DS  = L_BOW / NS
IG  = int(round(S_G / DS))
TIP_REACH = max(S_G, L_BOW - S_G) - GRIP_H


def stiff(s):
    """曲率の分布 f(s)。握りは 0（剛）／中程が最もよく撓み／末端（関）は硬い。"""
    d = abs(s - S_G)
    if d <= GRIP_H:
        return 0.0
    u = min(1.0, (d - GRIP_H) / RAMP)
    f = u * u * (3 - 2 * u)
    dt = min(1.0, (d - GRIP_H) / TIP_REACH)
    v = max(0.0, min(1.0, (dt - 0.60) / 0.40))
    return f * (1.0 - (1.0 - TIP_SOFT) * (v * v * (3 - 2 * v)))


_STE = [stiff((i + 0.5) * DS) for i in range(NS)]
_LOW = [1.0 if (i + 0.5) * DS >= S_G else 0.0 for i in range(NS)]


def stave(k0, d, low, bl=None):
    """握りを原点・接線を鉛直に固定して弧長で積分。(xs, zs, phs) を返す。
       κ(s) = (k0·bl + d·low)·f(s)   （下鉾）  ／  (k0 + d)·f(s)  （上鉾）
       🔴 和弓の非対称は2つ別々に効く。**張り姿**（bl）と**引いたときの応答**（low）。
          1周目は low を張り姿にも掛けて、下鉾だけが35°曲がった歪な弓になった。
          2周目は張り姿を均等にしたら、今度は長い上鉾の弭だけが手前へ出て
          **弦が 6.6° 傾いた**（実物の和弓は張ると弦が鉛直に立つ）。
          弓師が裏反りを均すのは、まさにこの2つを別々に合わせる作業。"""
    if bl is None: bl = BL
    xs = [0.0] * (NS + 1); zs = [0.0] * (NS + 1); ph = [0.0] * (NS + 1)
    kU, kL = k0 + d, k0 * bl + d * low
    x = z = p = 0.0
    for i in range(IG, NS):                       # 上鉾
        p2 = p + kU * _STE[i] * DS
        pm = 0.5 * (p + p2)
        x += math.sin(pm) * DS; z += math.cos(pm) * DS; p = p2
        xs[i + 1] = x; zs[i + 1] = z; ph[i + 1] = p
    x = z = p = 0.0
    for i in range(IG, 0, -1):                    # 下鉾
        p2 = p - kL * _STE[i - 1] * DS
        pm = 0.5 * (p + p2)
        x -= math.sin(pm) * DS; z -= math.cos(pm) * DS; p = p2
        xs[i - 1] = x; zs[i - 1] = z; ph[i - 1] = p
    return xs, zs, ph


def depth_at(s):
    """弓の厚み（前後）。末端へ細る。#21 端は細らせる／#31-c 弭は締める。"""
    d = min(1.0, abs(s - S_G) / (max(S_G, L_BOW - S_G)))
    t = d * d * (3 - 2 * d)
    return DEPTH_G + (DEPTH_T - DEPTH_G) * t


def width_at(s):
    d = min(1.0, abs(s - S_G) / (max(S_G, L_BOW - S_G)))
    t = d * d * (3 - 2 * d)
    return WIDTH_G + (WIDTH_T - WIDTH_G) * t


_XB = DEPTH_G * 0.5          # 握りの弦側の面（弓把はここから測る）

# --- 弦の拘束 -------------------------------------------------
def _bisect(fn, lo, hi, target, it=60):
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if fn(mid) < target: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)


def _brace_nock(k0, bl):
    xs, zs, _ = stave(k0, 0.0, 1.0, bl)
    A = (xs[0], zs[0]); B = (xs[NS], zs[NS])
    q = (NOCK_UP - A[1]) / (B[1] - A[1])
    ch = math.hypot(B[0] - A[0], B[1] - A[1])
    return (A[0] + q * (B[0] - A[0]), NOCK_UP), q * ch, (1 - q) * ch, B[0] - A[0]


def _k0_for(bl):
    return _bisect(lambda k: _brace_nock(k, bl)[0][0] - _XB, 0.001, 2.0, BRACE, 40)


# ① 張り姿：上下の弭の x を揃える＝張った弦が鉛直に立つ
BL = _bisect(lambda w: -_brace_nock(_k0_for(w), w)[3], 0.6, 6.0, 0.0, 26)
K0 = _k0_for(BL)
_N0, L_LO, L_UP, _ = _brace_nock(K0, BL)   # 弦の長さ（不変の拘束）はここで確定する


def nock(d, low):
    """弦は伸びない。番え所 N ＝ 二円の交点（手前側）。引き尺は**ここから出てくる**。"""
    xs, zs, _ = stave(K0, d, low)
    A = (xs[0], zs[0]); B = (xs[NS], zs[NS])
    dx, dz = B[0] - A[0], B[1] - A[1]
    dd = math.hypot(dx, dz)
    a = (L_LO * L_LO - L_UP * L_UP + dd * dd) / (2 * dd)
    h = math.sqrt(max(0.0, L_LO * L_LO - a * a))
    px, pz = A[0] + a * dx / dd, A[1] + a * dz / dd
    return (px + h * dz / dd, pz - h * dx / dd), (A[0], A[1]), (B[0], B[1])


def _solve_dk(low):
    """🔴 引き尺は曲率に対して**単調ではない**（曲げすぎると弭が寄って弦の膨らみが戻る）。
       1周目はこれを知らずに二分法で山の向こう側（κ=3.84＝鉾が渦を巻く形）を掴んだ。
       山を先に走査して、必ず**手前の枝**で解く。"""
    ds = [3.0 * j / 60 for j in range(61)]
    dr = [nock(x, low)[0][0] - _XB for x in ds]
    kp = ds[max(range(61), key=lambda j: dr[j])]
    return _bisect(lambda x: nock(x, low)[0][0] - _XB, 0.0, kp, DRAW, 36)


# ② 引いたときの応答：番え所が下がらない LOWK を解く（＝上下の釣り合い＝矢が水平に出る）
LOWK = _bisect(lambda w: nock(_solve_dk(w), w)[0][1], 0.6, 12.0, NOCK_UP, 26)
DK = _solve_dk(LOWK)


def delta(i):
    return DK * 0.5 * (1 - math.cos(2 * math.pi * i / N_FRAMES))


# --- 隙間（＝光の形）を高さの関数で ---------------------------
def _interp_x(xs, zs, z):
    """弓の芯線の x を高さ z で引く（z は単調）。"""
    if z <= zs[0]: return xs[0]
    if z >= zs[NS]: return xs[NS]
    lo, hi = 0, NS
    while hi - lo > 1:
        m = (lo + hi) // 2
        if zs[m] <= z: lo = m
        else: hi = m
    t = (z - zs[lo]) / max(1e-9, zs[hi] - zs[lo])
    return xs[lo] + t * (xs[hi] - xs[lo])


def _interp_s(zs, z):
    if z <= zs[0]: return 0.0
    if z >= zs[NS]: return L_BOW
    lo, hi = 0, NS
    while hi - lo > 1:
        m = (lo + hi) // 2
        if zs[m] <= z: lo = m
        else: hi = m
    t = (z - zs[lo]) / max(1e-9, zs[hi] - zs[lo])
    return (lo + t) * DS


def gap_profile(i, rows):
    """フレーム i の各高さ z における (弓の弦側の面 x, 弦 x)。"""
    d = delta(i)
    xs, zs, _ = stave(K0, d, LOWK)
    N, A, B = nock(d, LOWK)
    out = []
    for z in rows:
        s = _interp_s(zs, z)
        xb = _interp_x(xs, zs, z) + 0.5 * depth_at(s)
        # 🔴 分母は符号付き。max(1e-9, den) と書くと下側で den=−0.8 が 1e-9 に潰れ、
        #    弦の x が 1e7 に飛ぶ（1周目の実測）。ゼロ除算の保護は絶対値で書く。
        P = B if z >= N[1] else A
        den = P[1] - N[1]
        t = (z - N[1]) / den if abs(den) > 1e-9 else 0.0
        xstr = N[0] + t * (P[0] - N[0])
        out.append((xb, xstr))
    return out


# 光の面を張る行（＝隙間の高さ範囲）。v = (z-NOCK_UP)/FZ で ±1 に落ちる
NROW, NCOL = 72, 31    # 粗いと hero で面の折れ線が「凧の骨」として出る（5周目）
ROWS = [NOCK_UP + FZ * (-1.0 + 2.0 * j / (NROW - 1)) for j in range(NROW)]
def vtaper(z):
    """🔴 面の幅を上下端で 0 に絞る。2周目は隙間を全高そのまま埋めたので、
       ES=0 の黒い帯が**幅を持ったまま**残り、hero に水平の切り口が2本出た（#46）。
       純黒の裏当てが効くのは「黒い造形の奥」にいるときだけで、
       白背景に露出した ES=0 の面は、ただの黒い板として写る（#44-c の裏返し）。
       絞り方は cos（＝菱形）ではなく **√(1−v²)＝楕円**。5周目の hero で、
       cos だと弦の折れ（V）と噛み合って光が「緑の凧」という図形記号に読めた。"""
    v = max(-1.0, min(1.0, (z - NOCK_UP) / FZ))
    return math.sqrt(max(0.0, 1.0 - v * v))


_WZ = []
for z in ROWS:                      # 縦の重み＝（幅の絞り）×（ES の縦プロファイル）
    v = abs((z - NOCK_UP) / FZ)
    _WZ.append(vtaper(z) * max(0.0, 1.0 - min(1.0, v ** GPOW)))


def visible_area(i):
    """#40⑥：見える発光面積＝Σ 隙間(z)·縦の重み(z)·Δz。レンダーの画素数で測らない（#46）。"""
    pr = gap_profile(i, ROWS)
    dz = ROWS[1] - ROWS[0]
    return sum(max(0.0, b - a) * w * dz for (a, b), w in zip(pr, _WZ))


_AS = [visible_area(i) for i in range(N_FRAMES)]

# 🔴 hero の位相は「面積最大」ではなく積で決める（#48-c）：
#   ① 面積（痩せるとブルームが死ぬ）② 弓が撓んで見えるか（＝引き分けの宣言）
#   ③ 矢が弓から離れて見えるか（機構がもう一度読める）
def still_score(i):
    bend = delta(i) / max(1e-9, DK)            # 撓みの深さ＝引き分けの宣言
    return _AS[i] * (0.30 + 0.70 * bend)


STILL_FRAME = max(range(N_FRAMES), key=still_score) + 1

if "--probe-only" in sys.argv:                  # Blender 無しで幾何だけ見る
    print("LOWK %.3f  K0 %.4f  DK %.4f  brace %.4f  draw %.4f" % (LOWK, K0, DK, BRACE, nock(DK, LOWK)[0][0] - _XB))
    print("#40(6) min/max = %.3f" % (min(_AS) / max(_AS)))
    for i in range(0, 61, 15):
        print("  t=%.3f  area %.5f  (%.0f%%)" % (i / N_FRAMES, _AS[i], 100 * _AS[i] / max(_AS)))
    sys.exit(0)


def hex_to_linear(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- マテリアル ----------
def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


# 弓＝竹と櫨（はぜ）の積層。曲面主体（#17）だが #38① の縦溝は入れない
# （silhouette の長辺と平行な筋はハイライトが全長で繋がり「波板の金属」になる）
mat_bow, bp = principled("bow")
bp.inputs["Base Color"].default_value = BLACK
bp.inputs["Roughness"].default_value = 0.36
bp.inputs["Specular IOR Level"].default_value = 0.16      # #45 主材の下限 0.10 を割らない
bp.inputs["Coat Weight"].default_value = 0.06

mat_wrap, wp = principled("wrap")                          # 握り革：#17-b 質感の"差"で階層を作る
wp.inputs["Base Color"].default_value = BLACK
wp.inputs["Roughness"].default_value = 0.58
wp.inputs["Specular IOR Level"].default_value = 0.22

mat_str, sp = principled("string")
sp.inputs["Base Color"].default_value = BLACK
sp.inputs["Roughness"].default_value = 0.44
sp.inputs["Specular IOR Level"].default_value = 0.30       # 細いので照りが無いと消える

mat_arr, ap = principled("arrow")
ap.inputs["Base Color"].default_value = BLACK
ap.inputs["Roughness"].default_value = 0.40
ap.inputs["Specular IOR Level"].default_value = 0.24


def uv_glow(name):
    """#39：正規化2軸を UV に焼いてある。u=隙間を横切る±1／v=(z−番え所)/FZ。
       伸縮・変形する面なので座標は頂点に持たせる（#44-b の使い分け）。
       #32：随伴点光源があるので Base は純黒＝ES 0 の所はそのまま裏当てになる。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0, 0, 0, 1)
    p.inputs["Specular IOR Level"].default_value = 0.0
    p.inputs["Emission Color"].default_value = LIME
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None: n.inputs[1].default_value = val
        return n

    x2, y2 = mn('POWER', 2.0), mn('POWER', 2.0)
    nt.links.new(sep.outputs["X"], x2.inputs[0]); nt.links.new(sep.outputs["Y"], y2.inputs[0])
    ad = mn('ADD'); nt.links.new(x2.outputs[0], ad.inputs[0]); nt.links.new(y2.outputs[0], ad.inputs[1])
    rr = mn('SQRT'); nt.links.new(ad.outputs[0], rr.inputs[0])
    pw = mn('POWER', GPOW); nt.links.new(rr.outputs[0], pw.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = ES_CORE; mr.inputs["To Max"].default_value = 0.0
    mr.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(pw.outputs[0], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], p.inputs["Emission Strength"])
    return m


mat_glow = uv_glow("glow_gap")

mat_floor, fp = principled("floor")
fp.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp.inputs["Roughness"].default_value = 0.42
mat_text, tp = principled("text")
tp.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp.inputs["Roughness"].default_value = 0.6

# ---------- 形（フレームごとに頂点を作る） ----------
SEC = [(math.cos(2 * math.pi * k / NSEC), math.sin(2 * math.pi * k / NSEC)) for k in range(NSEC)]
RING_S = [L_BOW * j / (NRING - 1) for j in range(NRING)]


def bow_verts(i):
    """弓：芯線に沿って断面を掃く。断面は前後(x)に厚く左右(y)に細い角丸。"""
    xs, zs, ph = stave(K0, delta(i), LOWK)
    out = []
    for s in RING_S:
        k = min(NS - 1, int(s / DS)); t = s / DS - k
        cx = xs[k] + t * (xs[k + 1] - xs[k])
        cz = zs[k] + t * (zs[k + 1] - zs[k])
        an = ph[k] + t * (ph[k + 1] - ph[k])
        hd, hw = 0.5 * depth_at(s), 0.5 * width_at(s)
        # 弭（はず）：末端は #31-c に従い細らせず、わずかに膨らませて締める
        e = min(1.0, max(0.0, (min(s, L_BOW - s)) / 0.055))
        bulge = 1.0 + 0.42 * (1.0 - e) ** 2
        ca, sa = math.cos(an), math.sin(an)
        for (u, v) in SEC:
            su = math.copysign(abs(u) ** 0.72, u)      # 角丸の矩形（superellipse）
            sv = math.copysign(abs(v) ** 0.72, v)
            dx, dz = su * hd * bulge, 0.0
            out.append((cx + ca * dx - sa * dz, sv * hw * bulge, Z_GRIP + cz + sa * dx + ca * dz))
    return out


def tube_faces(nring, nsec):
    f = []
    for j in range(nring - 1):
        for k in range(nsec):
            a = j * nsec + k; b = j * nsec + (k + 1) % nsec
            f.append((a, b, b + nsec, a + nsec))
    return f


BOW_F = tube_faces(NRING, NSEC)

NSTR, SSEC = 60, 8
STR_SEC = [(math.cos(2 * math.pi * k / SSEC), math.sin(2 * math.pi * k / SSEC)) for k in range(SSEC)]
STR_F = tube_faces(NSTR, SSEC)


def str_verts(i):
    """弦：下弭 → 番え所 → 上弭 の折れ線。中仕掛（なかじかけ）で番え所を少し太らせる。"""
    N, A, B = nock(delta(i), LOWK)
    pts = []
    for j in range(NSTR):
        u = j / (NSTR - 1)
        if u <= 0.5:
            w = u / 0.5; p = (A[0] + w * (N[0] - A[0]), A[1] + w * (N[1] - A[1]))
        else:
            w = (u - 0.5) / 0.5; p = (N[0] + w * (B[0] - N[0]), N[1] + w * (B[1] - N[1]))
        pts.append(p)
    out = []
    for j, (px, pz) in enumerate(pts):
        q = min(j, NSTR - 1 - j)
        r = R_STR * (1.0 + 1.35 * math.exp(-((j - (NSTR - 1) / 2.0) / 3.2) ** 2))
        r *= (0.55 + 0.45 * min(1.0, q / 2.0))
        j2 = min(NSTR - 2, j); dxz = (pts[j2 + 1][0] - pts[j2][0], pts[j2 + 1][1] - pts[j2][1])
        ln = math.hypot(*dxz) or 1.0
        nx, nz = -dxz[1] / ln, dxz[0] / ln
        for (u, v) in STR_SEC:
            out.append((px + nx * r * u, r * v, Z_GRIP + pz + nz * r * u))
    return out


def sheet_verts(i):
    """光の面＝隙間そのもの。弓と弦の内側へ UOVER だけ食い込ませて継ぎ目を黒で隠す。"""
    pr = gap_profile(i, ROWS)
    out = []
    for j, z in enumerate(ROWS):
        a, b = pr[j]
        c, hw = 0.5 * (a + b), 0.5 * (b - a) * UOVER * vtaper(z)
        for k in range(NCOL):
            u = -1.0 + 2.0 * k / (NCOL - 1)
            out.append((c + u * hw, 0.0, Z_GRIP + z))
    return out


SHEET_F = []
for j in range(NROW - 1):
    for k in range(NCOL - 1):
        a = j * NCOL + k
        SHEET_F.append((a, a + 1, a + NCOL + 1, a + NCOL))
SHEET_UV = []
for j, z in enumerate(ROWS):
    for k in range(NCOL):
        SHEET_UV.append((UEDGE * (-1.0 + 2.0 * k / (NCOL - 1)), (z - NOCK_UP) / FZ))


def make_shapekeyed(name, frames, faces, mat, uvs=None, smooth=0.5):
    """毎フレームの頂点をシェイプキーに焼く（#43-e／047 で実証済み）。
       トポロジは不変なので glb にも morph target として乗る。"""
    me = bpy.data.meshes.new(name)
    me.from_pydata(frames[0], [], faces); me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    if uvs is not None:
        lay = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                lay.data[li].uv = uvs[me.loops[li].vertex_index]
    ob.shape_key_add(name="basis", from_mix=False)
    keys = []
    for f, vs in enumerate(frames):
        sk = ob.shape_key_add(name="f%03d" % f, from_mix=False)
        sk.slider_min, sk.slider_max = 0.0, 1.0
        for vi, co in enumerate(vs):
            sk.data[vi].co = co
        keys.append(sk)
    n = len(frames)
    for f, sk in enumerate(keys):
        for d in (-1, 0, 1):
            fr = f + d
            if 0 <= fr < n:
                sk.value = 1.0 if d == 0 else 0.0
                sk.keyframe_insert("value", frame=fr + 1)
    if smooth > 0:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        try: bpy.ops.object.shade_auto_smooth(angle=smooth)
        except Exception: pass
        ob.select_set(False)
    return ob


FR = list(range(N_FRAMES)) + [0]          # 末尾に折り返し＝glb でループが閉じる
bow = make_shapekeyed("bow", [bow_verts(i) for i in FR], BOW_F, mat_bow)
string = make_shapekeyed("string", [str_verts(i) for i in FR], STR_F, mat_str, smooth=0.8)
sheet = make_shapekeyed("sheet", [sheet_verts(i) for i in FR], SHEET_F, mat_glow,
                        uvs=SHEET_UV, smooth=0.0)


# ---------- 握り革（動かない＝握りは剛） ----------
def solid_tube(name, pts, radii, mat, seg=16, smooth=0.6):
    bm = bmesh.new()
    rings = []
    for (px, pz), r in zip(pts, radii):
        ring = [bm.verts.new((px + r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg),
                              Z_GRIP + pz)) for k in range(seg)]
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    for r in (rings[0], rings[-1]):
        bm.faces.new(r if r is rings[-1] else list(reversed(r)))
    bm.normal_update()
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    if smooth > 0:
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        try: bpy.ops.object.shade_auto_smooth(angle=smooth)
        except Exception: pass
        ob.select_set(False)
    return ob


_xs0, _zs0, _ = stave(K0, 0.0, LOWK)
wrap_pts, wrap_r = [], []
NW = 26
for j in range(NW):
    z = WRAP_LO + (WRAP_HI - WRAP_LO) * j / (NW - 1)
    s = _interp_s(_zs0, z)
    base = 0.5 * depth_at(s)
    e = min(1.0, min(j, NW - 1 - j) / 2.0)
    wrap_pts.append((_interp_x(_xs0, _zs0, z), z))
    wrap_r.append(base + WRAP_R * (0.35 + 0.65 * e))
solid_tube("wrap", wrap_pts, wrap_r, mat_wrap)
# 上下2本の巻き止めだけ（#41：等間隔の肋を並べるとねじに読める。反復は 3〜4 で記号になる）
for zc in (WRAP_LO - 0.006, WRAP_HI + 0.006):
    s = _interp_s(_zs0, zc)
    pts = [(_interp_x(_xs0, _zs0, zc + d), zc + d) for d in (-BAND_W / 2, 0, BAND_W / 2)]
    solid_tube("band_%.3f" % zc, pts, [0.5 * depth_at(s) + BAND_R] * 3, mat_wrap)

# ---------- 矢（弦と一緒に引かれる） ----------
if ARROW:
    bm = bmesh.new()
    seg = 14
    for (x0, x1, r0, r1) in [(0.0, -ARR_L, ARR_R, ARR_R * 0.86)]:
        ra, rb = [], []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            ra.append(bm.verts.new((x0, r0 * math.sin(a), Z_GRIP + NOCK_UP + r0 * math.cos(a))))
            rb.append(bm.verts.new((x1, r1 * math.sin(a), Z_GRIP + NOCK_UP + r1 * math.cos(a))))
        for k in range(seg):
            bm.faces.new((ra[k], ra[(k + 1) % seg], rb[(k + 1) % seg], rb[k]))
        bm.faces.new(list(reversed(ra))); bm.faces.new(rb)
    # 矢羽（上下2枚）：#48 「何であるか」を宣言する部品
    for sgn in (1, -1):
        v = [bm.verts.new((-0.030, 0.0, Z_GRIP + NOCK_UP + sgn * ARR_R * 0.7)),
             bm.verts.new((-0.030 - FLE_L, 0.0, Z_GRIP + NOCK_UP + sgn * (ARR_R * 0.7 + FLE_H))),
             bm.verts.new((-0.030 - FLE_L - 0.030, 0.0, Z_GRIP + NOCK_UP + sgn * ARR_R * 0.7))]
        bm.faces.new(v)
    bm.normal_update()
    me = bpy.data.meshes.new("arrow"); bm.to_mesh(me); bm.free()
    arrow = bpy.data.objects.new("arrow", me); bpy.context.collection.objects.link(arrow)
    arrow.data.materials.append(mat_arr)
    bpy.context.view_layer.objects.active = arrow; arrow.select_set(True)
    try: bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception: pass
    arrow.select_set(False)
    for i, fi in enumerate(FR):
        arrow.location = (nock(delta(fi), LOWK)[0][0] + 0.022, 0.0, 0.0)
        arrow.keyframe_insert("location", frame=i + 1)

# ---------- 随伴点光源（#22：光を「塗装」にしないため） ----------
bpy.ops.object.light_add(type='POINT', location=(0.30, 0.0, Z_GRIP + NOCK_UP))
gl = bpy.context.active_object; gl.name = "lamp_gap"
gl.data.shadow_soft_size = 0.42
gl.data.energy = LAMP_W
gl.data.color = LIME[:3]
gl.visible_camera = False

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_floor)


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
        caption("MIDDLE STUDY 049 — YUMI", 0.045, (AIM_X, -1.7, 0.57), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


focus = (0, 0, CENTER_Z)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = bow
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception:
    scene.view_settings.view_transform = 'AgX'


def setup_bloom():
    ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new("CompositorNodeRLayers")
    glr = ng.nodes.new("CompositorNodeGlare")
    ou = ng.nodes.new("NodeGroupOutput")
    try: glr.inputs["Type"].default_value = 'BLOOM'
    except Exception: pass
    glr.inputs["Threshold"].default_value = 1.2
    glr.inputs["Strength"].default_value = 0.35
    try: glr.inputs["Size"].default_value = 0.55
    except Exception: pass
    ng.links.new(rl.outputs["Image"], glr.inputs["Image"])
    ng.links.new(glr.outputs["Image"], ou.inputs["Image"])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True


setup_bloom()

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME)

if "probe" in modes:
    print(">> ELASTICA  LOWK %.3f  K0 %.4f  DK %.4f  ／ 弓把 %.4f  引き尺 %.4f m" %
          (LOWK, K0, DK, BRACE, nock(DK, LOWK)[0][0] - _XB))
    N1, A1, B1 = nock(DK, LOWK)
    A0, B0 = nock(0.0, LOWK)[1:]
    print(">> 弭（末端）  brace (%.3f,%.3f)/(%.3f,%.3f) → full (%.3f,%.3f)/(%.3f,%.3f)" %
          (_XB, 0, 0, 0, A1[0], A1[1], B1[0], B1[1]))
    xs1, zs1, ph1 = stave(K0, DK, LOWK)
    print(">> 接線角  末端 %.1f° / %.1f°（|φ|<80° なら z は単調＝形が破綻しない）" %
          (math.degrees(ph1[0]), math.degrees(ph1[NS])))
    print(">> #40(6) 見える発光面積 min/max = %.3f （合格 0.75以下）" % (min(_AS) / max(_AS)))
    print(">> 変化がループのどこに集中しているか（#44：前半ずっと100%%なら向きを疑う）")
    for i in range(0, N_FRAMES // 2 + 1, 10):
        print("   t=%.3f  面積 %.5f  (%3.0f%%)  隙間@番え所 %.3f" %
              (i / N_FRAMES, _AS[i], 100 * _AS[i] / max(_AS),
               gap_profile(i, [NOCK_UP])[0][1] - gap_profile(i, [NOCK_UP])[0][0]))
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, zs = [], []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name == "Plane": continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            w = ev.matrix_world @ v.co
            xs.append(w.x); zs.append(w.z)
    print(">> BBOX  x %.3f..%.3f (%.3f)  z %.3f..%.3f (%.3f)  ／ フレーム 横2.81・縦3.52" %
          (min(xs), max(xs), max(xs) - min(xs), min(zs), max(zs), max(zs) - min(zs)))
    print(">> 占有  横%.0f%%  縦%.0f%%   キャプション上端 0.72 とのクリアランス %.3f  中心z %.3f（LOOK %.2f）" %
          ((max(xs) - min(xs)) / 2.81 * 100, (max(zs) - min(zs)) / 3.52 * 100,
           min(zs) - 0.72, 0.5 * (min(zs) + max(zs)), LOOK_Z))

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
    # #35 ループものは still 以外の位相も撮る（材質側の破綻は1枚では出ない）
    for fr in (1, 31, 91):
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_049.blend"))

# 🔴 glb は必ず最後（#30：Emission を定数へ潰すので、レンダーの前に置かない）
if "glb" in modes:
    p = mat_glow.node_tree.nodes["Principled BSDF"]
    for l in list(mat_glow.node_tree.links):
        if l.to_socket == p.inputs["Emission Strength"]:
            mat_glow.node_tree.links.remove(l)
    p.inputs["Emission Strength"].default_value = 2.6
    scene.frame_end = N_FRAMES + 1
    names = {"bow", "string", "sheet", "wrap", "arrow"}
    for o in bpy.data.objects:
        o.select_set(o.name in names or o.name.startswith("band_"))
    bpy.context.view_layer.objects.active = bow
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
