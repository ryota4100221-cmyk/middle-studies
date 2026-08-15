# =============================================================
# monaka design. — MIDDLE STUDY 053 "UKIDAMA"（浮玉 / ビン玉 glass floats）
#
# 黒い浮玉が、いくつも宙にある。水は描かれていない。
# それでも水面がどこにあるかは分かる——**浮玉の真ん中に、ライムの線が通っているから。**
# うねりが来ると玉は持ち上がり、線は腹から底へ滑って細くなり、やがて消える。
# 波が引いて玉が平水面に戻ったとき、線はもう一度いちばん太いところ＝真ん中に戻る。
# **水面は見えない。真ん中が光っている玉だけが、そこを教えている。**
#
# 【ドメイン】漁労・浮子（シリーズ未踏）。直近10作（楽器・打／貨幣・銭／玩具・けん玉／
#   武・弓／農・製粉／商い・暖簾／書物・巻子／土木・橋／建築・寺社／虫・生命）と別。
#   039 HAMAGURI【貝・海】は「一枚の貝が開く」機構で別物。011 NAMI【自然・現象】は
#   同心円の波紋そのものが主役で、ここは「波に乗る物の側」を見ている。
#
# 【光の型＝稜線】#53 の8型で最少タイの型（52作で4作＝002 OBI／032 SUZU ほか）。
#   直近5作に出ている 面／隙間／芯／背光 は選べない。**赤道に沿って走る線**を採る。
#
# 【構図＝寄り】🔴 #57：52作のうち **52作すべてが枠に1辺も接していなかった**（edge=0）。
#   052 は中央を外したが、まだ物は丸ごと枠の中に収まっていた。053 は**枠で切る**。
#   主玉は左と上で画面から出る。「水面はフレームの外まで続いている」を絵で言うのがこの型。
#   🔴 最初は「群」（小玉11個）で組んで捨てた。**カメラが水平（z=1.95 から z=1.92 を見る）なので、
#      水平面はフレームの中で高さ 13% の細い帯にしか写らない。**11個は投影が16組重なって塊が4つ
#      しか立たず（群の条件は5以上）、6個まで減らして通しても、**画面の 13% に並んだ小さな数珠玉**
#      にしかならなかった。**「群」はこのカメラでは水平面のモチーフと両立しない**——
#      分布を見せたければ被写体は**体積**を占めていなければならない。これは 053 の失敗ではなく、
#      #57 の型を選ぶときの前提条件（次に「群」を採る人はここを読むこと）。
#
# 【機構＝平水面と、それに対する上下（riding the swell）】シリーズ初の「群の位相差」。
#   光は**世界座標の水平面 Z_W に固定**され、玉のほうが上下する。玉の中心が Z_W にある瞬間だけ
#   線は赤道＝いちばん太いところに来る。持ち上がれば線は下の緯度へ滑り、円周が細り、
#   |h| > R で玉から外れて消える。**同じ波でも、小さい玉ほど先に光を失う。**
#     h_i(t) = A1·cos(2πt − φ_i) + A2·cos(4πt − 2φ_i)      φ_i = KW·x_i
#   第1・第2高調波とも整数周期なので t=0 と t=1 が厳密一致＝完全ループ。
#   位置キーと回転キーだけなので glb にそのまま乗る（#60）。
#   傾きは波の勾配 ∂h/∂x そのもの（＝浮玉は斜面に垂直に立つ）。物理から出す＝目分量で振らない。
#
# 🔴 #48 対策：**球＋光る赤道は、単体だと必ず「ノブ／ボタン」に読める。**
#   #48 の一般則「回転対称を破る部品は、その道具が人と接する所にある」に従い、
#   ビン玉が人と接する所＝**網（漁網の掛け）と、吹き硝子のへそ**を出す。
#   さらにこの作では**11個が別々の緯度で光る**ので、同じ製品が並んでいる絵にならない。
#
# 🔴 #34/#49 対策：発光は「覆い（coverage）」と「強さ（strength）」で**別々の勾配**を持つ。
#   さらに視線に対して寝る所（シルエットの端）で落とす＝白背景に切り口が出ない。
#
# 🔴 #40⑥ は幾何で積分する（#46）。Blender を起動せず --probe-only で解ける。
#   球の緯度 ζ における「カメラから見える帯の幅」は 2·√(R²−ζ²)＝水平視の投影長。
#   （面積で積分すると **アルキメデスの帽子箱定理**で総量が定数になり、機構が測れない。
#    球は帯の面積が高さにしか依らない＝**総発光量は玉が動いても変わらない**。
#    変わるのは**見え方**なので、投影で積分する。）
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 水（見えない平水面）------------------------------------------
Z_W = 2.70             # 平水面の高さ（world）。光はここに固定される
#  🔴 うねりの振幅を上げると、いちばん沈む位相で主玉の底が**キャプションに被る**。
#     キャプションは y=-1.7（カメラに近い）なので、world z ではなく画面 y で見る：
#     見出しの上端は sy=0.176、Z_W=2.70 での主玉の底は最下位相でも sy=0.214 で clear。

# --- うねり ------------------------------------------------------
# 🔴 帯の太さが変わって見えるのは、緯度の円周が √(1−(h/R)²) で細るからで、
#    h/R が 0.4 程度では 9% しか細らない＝絵では何も起きない。**h/R は 0.8 まで振る。**
A1 = 0.600             # 第1高調波（うねりの主）
A2 = 0.160             # 第2高調波（波頭を尖らせる＝ただの正弦にしない）
KW = 1.10              # 波数 rad/m。玉の x の広がり 3.0m に対して位相差 ≒ 0.53 波長
# 🔴 2つの玉は位相が 2.41 rad ずれている（KW·Δx）。同時に赤道にならないので、
#    「片方が真ん中・片方が端」という絵が必ずどこかの位相に立つ。
# 🔴 沖の玉を主玉と同じ 0.95 にしたら #40⑥ が **0.755**（不合格 0.75）になった——
#    大きさが同じだと、片方が細るぶんを片方が太って**打ち消し合う**。0.72 に落として
#    |h|max/R を 1.06 にする＝**沖の玉だけが完全に光を失う位相ができる**と一気に通る。
TILT = 0.34            # 傾きの利き（浮玉は波の斜面に垂直に立つ＝∂h/∂x に比例）

# --- 光（赤道の線）------------------------------------------------
BAND_H = 0.105         # 覆いの半幅（world z）。これを超えると黒い玉に戻る
HOT_H = 0.038          # 芯（強さの勾配）の半幅
ES_CORE = 2.85         # 発光の基準
ES_BASE = 0.55         # 芯の外での強さの下限（0 にすると帯の縁が死ぬ＝#49）
HOT_MUL = 0.85         # 芯で何倍にするか
EDGE_LO = 0.30         # シルエットの端での下限（0 にすると白背景に切り口が立つ）
EDGE_P = 0.55          # 端の落ち方のべき

# --- 浮玉（ビン玉）------------------------------------------------
# (x, y, R)  y は奥行き（カメラは y=-8.3 から +y を見る）
# 🔴 手で置かない。①奥行き y ごとの見かけ半径 r=R/(2·hw(y)) を出し、②**画面上のどこに置くか**を
#    決め、③そこから世界の x を逆に解く（hw(y)=1.405·(y+8.3)/8.3・cx(y)=−0.55y/8.3）。
#    主玉は画面 0.300 を中心に半径 0.364＝**左端（−0.064）で枠から出る**＝#57「寄り」の条件。
FLOATS = [
    (-0.482, -0.60, 0.95),     # 主玉。画面 -0.064..0.664＝**左端で枠から出る**／沈むと上も出る
    (+1.712, +7.00, 0.72),     # 沖の玉。画面 0.781..1.059＝**右端で枠から出る**
]
# 🔴 3個目は置けない。主玉が画面の -0.06..0.66 を占めるので、その奥に置いた玉は必ず隠れる。
#    「寄り」は**見えている物を減らす型**で、足すと必ずどれかが無駄になる。
# 🔴 2個で足りる理由：ライムの線は**同じ world z**に出るので、離れた2つの玉の線を目が1本に繋ぐ。
#    ——それが「水面はフレームの外まで続いている」の絵。
SPREAD = 1.00          # 群の広がり（画面占有だけを決める。比は上で決める＝#50）
R_MUL = 1.00           # 玉の大きさの一括倍率

NUB_R = 0.21           # へそ（吹き硝子の口）の半径 / R
NUB_H = 0.14           # へそのせり出し / R
ROPE = 0.020           # 網の縄の太さ（半径）
N_MER = 5              # 大円の本数（1本で経線2本ぶん＝計10本）
LAT = 0.62             # 緯線の高さ / R

FPS = 24
N_FRAMES = 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.0, 1.92
LIME_W = 160.0         # 随伴のライム光源（#58）。2灯に割る。**発光体の外**に置く
# 🔴 斑を消すために光源を 1.9m 遠ざけたら、床のライムが 0.42%→**0.07%（不合格）**に落ちた。
#    #58 の「効くのはW数だけ」は距離を固定した話で、**距離を動かすと二乗で効く**。
#    位置は戻し、消すのは specular だけにして、W で床の量を作る。

FLOATS = [(x * SPREAD, y * SPREAD, r * R_MUL) for (x, y, r) in FLOATS]


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def ss(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def phase(x):
    return KW * x


def h_of(x, i):
    """平水面からの上下。整数周期2つ＝t=0 と t=1 が厳密一致。"""
    t = (i % N_FRAMES) / N_FRAMES
    p = phase(x)
    return A1 * math.cos(2 * math.pi * t - p) + A2 * math.cos(4 * math.pi * t - 2 * p)


def slope(x, i):
    """波の斜面 ∂h/∂x（浮玉の傾きはこれに比例する）。"""
    t = (i % N_FRAMES) / N_FRAMES
    p = phase(x)
    return (A1 * KW * math.sin(2 * math.pi * t - p)
            + 2 * A2 * KW * math.sin(4 * math.pi * t - 2 * p))


def cov(a):
    """覆い（黒↔発光の混合）。a = |z − Z_W|"""
    return 1.0 - ss(a / BAND_H) if a < BAND_H else 0.0


def es(a):
    """強さ。覆いとは別の勾配を持たせる（#34：1つの勾配で両方を書かない）。"""
    return ES_BASE + HOT_MUL * (1.0 - ss(a / HOT_H) if a < HOT_H else 0.0)


def vis_one(R, h, n=160):
    """1個の玉の「見える発光量」。緯度 ζ の帯はカメラから 2·√(R²−ζ²) の幅に見える。
       🔴 面積で積分してはいけない（アルキメデスの帽子箱定理で定数になる＝機構が測れない）。"""
    s = 0.0
    for k in range(n):
        z_ = -R + 2 * R * (k + 0.5) / n
        a = abs(h + z_)                       # 玉の中心が Z_W+h にあるので、水面までの差は h+z_
        if a >= BAND_H:
            continue
        s += cov(a) * es(a) * 2.0 * math.sqrt(max(0.0, R * R - z_ * z_)) * (2 * R / n)
    return s


def total(i):
    return sum(vis_one(R, h_of(x, i)) for (x, y, R) in FLOATS)


_LS = [total(i) for i in range(N_FRAMES)]
_LMAX = max(_LS)


def variety(i):
    """玉ごとの「線がどの緯度に来ているか」の散らばり。
       🔴 全部が同時に赤道だと、同じ製品が11個並んだ絵になる（#48 の型の失敗の群版）。
          hero は**光の量**だけでなく、**緯度が散っている位相**から選ぶ。"""
    v = [max(-1.6, min(1.6, h_of(x, i) / R)) for (x, y, R) in FLOATS]
    m = sum(v) / len(v)
    return math.sqrt(sum((q - m) ** 2 for q in v) / len(v))


def at_middle(i):
    """「真ん中が光っている玉」が何個あるか（|h|/R < 0.25）＝シリーズの主題そのもの。"""
    return sum(1 for (x, y, R) in FLOATS if abs(h_of(x, i)) / R < 0.25)


def main_mid(i):
    """主玉の線が赤道にどれだけ近いか。🔴 hero は「真ん中に光がある」瞬間でなければならない
       ——群の平均で選ぶと、**主玉の線が腹の下に落ちた位相**が選ばれる（1周目の実測＝h/R -0.46）。"""
    x, y, R = FLOATS[0]
    return 1.0 - min(1.0, abs(h_of(x, i)) / R / 0.55)


_SC = [(_LS[i] / _LMAX) * (1.0 + 0.22 * at_middle(i)) * (0.30 + 0.70 * main_mid(i))
       * (0.55 + 0.45 * variety(i)) for i in range(N_FRAMES)]
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _SC[i]) + 1

if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d" % STILL_FRAME)
    print(">> #40(6) 見える発光量 min/max = %.3f  （合格 0.75以下）" % (min(_LS) / _LMAX))
    print(">> ループの閉じ: h(f=0)=%.6f  h(f=120)=%.6f （x=0）"
          % (h_of(0.0, 0), h_of(0.0, 120)))
    print(">> 位相ごとの群の様子")
    for i in range(0, N_FRAMES, 8):
        print("   t=%.3f  光量 %5.0f%%  緯度の散らばり %.2f  真ん中が光る玉 %2d 個  score %.2f"
              % (i / N_FRAMES, 100 * _LS[i] / _LMAX, variety(i), at_middle(i), _SC[i]))
    print(">> hero 位相での各玉（h/R が 0 に近いほど線が赤道＝太い）")
    for n, (x, y, R) in enumerate(FLOATS):
        hh = h_of(x, STILL_FRAME - 1)
        print("   #%02d x%+.2f y%+.2f R%.3f   h%+.3f  h/R %+.2f  見える光 %.4f  傾き %+.1f°"
              % (n, x, y, R, hh, hh / R, vis_one(R, hh),
                 math.degrees(math.atan(TILT * slope(x, STILL_FRAME - 1)))))
    print(">> 群の広がり  x %.2f..%.2f   y %.2f..%.2f   R %.3f..%.3f"
          % (min(f[0] for f in FLOATS), max(f[0] for f in FLOATS),
             min(f[1] for f in FLOATS), max(f[1] for f in FLOATS),
             min(f[2] for f in FLOATS), max(f[2] for f in FLOATS)))
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
# 玉＝硝子。5つのレシピに硝子は無いので、いちばん近い「深く沈んだ艶」＝漆を当てる。
# 網＝縄なので布（厚物）。**色は1色も増えない。質感の語彙だけ増やす**（MATERIALS.md）
RECIPE_BALL, RECIPE_ROPE = "urushi", "nuno"
# 🔴 MATERIALS.md の urushi をそのまま当てたら、玉が**銀色のガラス玉**になった（1周目の実測）。
#    レシピは径0.3程度の球で測った値で、ここは径2.5の大きな曲面＝明るい環境（0.92）を面で返す量が
#    桁で違う（052 と同じ前提の差＝#62④）。効くのは2つ：① Coat を落とす（Coat は Metallic で
#    黒くならない**常に誘電体の白い層**）② 金属度を入れる（#57②：#0a0a0a の金属はグレー環境を
#    映しても黒いまま／誘電体の鏡面は白い）。網の縄も同じ理由で光沢を落とす。
BLACK_RECIPES["urushi"] = dict(rough=0.34, spec=0.30, coat=0.0, metal=0.42)
BLACK_RECIPES["nuno"] = dict(rough=0.82, spec=0.14, sheen=0.30, sheen_rough=0.30)


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


mat_rope = black_material("rope", RECIPE_ROPE)
mat_ball_plain = black_material("ball_plain", RECIPE_BALL)     # glb 用（発光は別リングで持つ）


def ball_material(name):
    """黒い硝子玉＋**世界座標の水面に固定された**発光の帯。
       🔴 帯は world z で書く。玉が上下しても帯は動かない＝「水面のほうが本体」。
       🔴 覆い（MixShader の Fac）と強さ（Emission Strength）で**別々の勾配**を持つ（#34）。
       🔴 さらにシルエットの端で落とす（#49：白背景に ES の切り口を立てない）。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')

    glass = nt.nodes.new("ShaderNodeBsdfPrincipled")
    set_black(glass, RECIPE_BALL)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = LIME
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(glass.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])

    geo = nt.nodes.new("ShaderNodeNewGeometry")
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], xyz.inputs["Vector"])   # Position は world 座標

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

    d = mn('SUBTRACT', Z_W); nt.links.new(xyz.outputs["Z"], d.inputs[0])
    ab = mn('ABSOLUTE'); nt.links.new(d.outputs[0], ab.inputs[0])

    covn = mr(0.0, BAND_H, 1.0, 0.0)          # 覆い：帯の外は完全に黒い玉へ戻る
    nt.links.new(ab.outputs[0], covn.inputs["Value"])
    nt.links.new(covn.outputs["Result"], mx.inputs["Fac"])

    hot = mr(0.0, HOT_H, 1.0, 0.0)            # 強さ：芯だけ持ち上げる
    nt.links.new(ab.outputs[0], hot.inputs["Value"])
    hm = mn('MULTIPLY', HOT_MUL); nt.links.new(hot.outputs["Result"], hm.inputs[0])
    hb = mn('ADD', ES_BASE); nt.links.new(hm.outputs[0], hb.inputs[0])

    lw = nt.nodes.new("ShaderNodeLayerWeight")            # Facing：1＝シルエットの端
    lw.inputs["Blend"].default_value = 0.5
    fw = mn('SUBTRACT'); fw.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs["Facing"], fw.inputs[1])
    fp = mn('POWER', EDGE_P); nt.links.new(fw.outputs[0], fp.inputs[0])
    fs = mn('MULTIPLY', 1.0 - EDGE_LO); nt.links.new(fp.outputs[0], fs.inputs[0])
    fa = mn('ADD', EDGE_LO); nt.links.new(fs.outputs[0], fa.inputs[0])

    e1 = mn('MULTIPLY'); nt.links.new(hb.outputs[0], e1.inputs[0])
    nt.links.new(fa.outputs[0], e1.inputs[1])
    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e1.outputs[0], e2.inputs[0])
    nt.links.new(e2.outputs[0], em.inputs["Strength"])
    return m


mat_ball = ball_material("ball")

mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
NSEG = 128


def lathe(profile, name, mat):
    """(r, z) の輪郭を Z 軸まわりに回して閉じたソリッドにする。r=0 の点は極として1頂点に潰す。"""
    bm = bmesh.new()
    rings, poles = [], []
    for (r, z) in profile:
        if r < 1e-6:
            v = bm.verts.new((0.0, 0.0, z)); rings.append(None); poles.append(v)
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / NSEG),
                                        r * math.sin(2 * math.pi * k / NSEG), z))
                          for k in range(NSEG)])
            poles.append(None)
    for i in range(len(profile) - 1):
        A, B = rings[i], rings[i + 1]
        if A is None and B is None:
            continue
        if A is None:
            p = poles[i]
            for k in range(NSEG):
                bm.faces.new((p, B[(k + 1) % NSEG], B[k]))
        elif B is None:
            p = poles[i + 1]
            for k in range(NSEG):
                bm.faces.new((p, A[k], A[(k + 1) % NSEG]))
        else:
            for k in range(NSEG):
                bm.faces.new((A[k], A[(k + 1) % NSEG], B[(k + 1) % NSEG], B[k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    sharp = []
    for e in bm.edges:
        try:
            if e.calc_face_angle() > math.radians(35):
                sharp.append(e)
        except Exception:
            pass
    if sharp:                                     # #17：稜線が光を拾わないと黒はプラスチックになる
        bmesh.ops.bevel(bm, geom=sharp, offset=0.004, segments=2,
                        affect='EDGES', clamp_overlap=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def ball_profile(R):
    """底の極から球をなぞり、上で「へそ」（吹き硝子の口）に繋ぐ。
       🔴 #48：球のままだと単体では必ずノブに読める。**人と接する所**＝口と網を出す。"""
    pts = [(0.0, -R)]
    N = 72
    a_end = math.radians(72.0)                    # ここから上はへそ
    for k in range(1, N + 1):
        a = -math.pi / 2 + (a_end + math.pi / 2) * k / N
        pts.append((R * math.cos(a), R * math.sin(a)))
    rn, zn = R * NUB_R, R * math.sin(a_end)
    pts.append((rn * 1.32, zn + R * 0.030))       # 口のくびれ（肩）
    pts.append((rn, zn + R * 0.055))
    pts.append((rn, zn + R * NUB_H))              # 口の立ち上がり
    pts.append((rn * 0.72, zn + R * (NUB_H + 0.030)))
    pts.append((0.0, zn + R * (NUB_H + 0.042)))   # 天
    return pts


def torus(name, major, minor, loc, rot, mat, mseg=48, nseg=10):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=mseg, minor_segments=nseg,
                                     location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(mat)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        pass
    o.select_set(False)
    return o


rigs, bases, balls, parts = [], [], [], []
for n, (x, y, R) in enumerate(FLOATS):
    rig = bpy.data.objects.new("uki_%02d" % n, None)          # 動く方（上下・傾き）
    bpy.context.collection.objects.link(rig)
    rig.location = (x, y, Z_W)
    base = bpy.data.objects.new("uki_%02d_base" % n, None)    # 静止の姿勢（口の向きを散らす）
    bpy.context.collection.objects.link(base)
    base.parent = rig
    # 🔴 口が11個とも真上を向いていると「同じ製品が11個」になる。姿勢だけ散らす（決め打ち・乱数不使用）
    base.rotation_euler = (math.radians(-26 + 13 * ((n * 5) % 7)),
                           0.0,
                           math.radians(17 * n))
    b = lathe(ball_profile(R), "ball_%02d" % n, mat_ball)
    b.parent = base
    rigs.append(rig); bases.append(base); balls.append(b); parts += [rig, base, b]

    # 網（漁網の掛け）：大円 N_MER 本＝経線 2·N_MER 本 ＋ 緯線2本
    rr = R + ROPE
    for k in range(N_MER):
        az = math.pi * k / N_MER + math.radians(11 * n)
        t = torus("net_%02d_m%d" % (n, k), rr, ROPE, (0, 0, 0), (math.pi / 2, 0.0, az), mat_rope)
        t.parent = base; parts.append(t)
    for sgn in (-1, +1):
        zl = sgn * LAT * rr
        t = torus("net_%02d_l%d" % (n, sgn), math.sqrt(max(1e-6, rr * rr - zl * zl)), ROPE,
                  (0, 0, zl), (0, 0, 0), mat_rope)
        t.parent = base; parts.append(t)

# --- キーフレーム（毎フレーム打つ＝イージング不使用・#25c）----------
FR = list(range(N_FRAMES)) + [0]                  # 末尾に折り返し＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    for n, (x, y, R) in enumerate(FLOATS):
        rig = rigs[n]
        rig.location = (x, y, Z_W + h_of(x, i))
        rig.rotation_euler = (0.0, math.atan(TILT * slope(x, i)), 0.0)
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


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 0.85), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.68), "logo"),
        caption("MIDDLE STUDY 053 — UKIDAMA", 0.045, (AIM_X, -1.7, 0.57), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0.0, 0.0, Z_W)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）

# 🔴 #58③：随伴のライム光源は**発光体の外**に置く。2灯に割り、玉の手前・下に出す。
# 🔴 ただし**床だけを受光させる**（下でライトリンク）。理由は1周目の実測で2つ出た：
#    ① 黒い玉の腹に**ライムの丸い斑が2つ**出て下半分が抹茶色に被った（艶のある黒＝urushi の
#       拡散成分に、半径0.30のソフトな点光源がそのまま玉ボケとして乗る。`specular_factor=0`
#       では消えない＝**斑の正体は鏡面ではなく拡散**だった）。
#    ② **キャプションの3行が緑に染まった**（文字は y=-1.7＝光源から1mしかない）。
#    #58 が要求しているのは「床にライムが落ちていること」なので、受光を床に絞れば要求は満たす。
#    4灯目の逆光を床から外す（#56）のと同じ道具を、向きだけ逆に使う。
limelamps = []
for sgn in (-1, +1):
    bpy.ops.object.light_add(type='POINT',
                             location=(sgn * 0.90, -2.40, Z_W - 1.55))
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
cam.data.dof.focus_object = balls[0]      # 主玉に合わせる（沖の玉は柔らかく落ちる）
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
back.light_linking.receiver_collection = lit      # 🔴 データでなくオブジェクト側にある

# 🔴 ライムの随伴光源からは**キャプションだけ**を外す。
#    最初「床だけを受光させる」で組んだら、床のライムが 0.59%→**0.02%（不合格）**に落ちた。
#    measure が床とみなす帯（画面の上から 50〜80%）は、実際には **y≧6.5m の遠い床**で、
#    そこを照らしていたのは光源の直射ではなく**部屋ぜんぶの相互反射**だった＝
#    受光を床1枚に絞ると、その相互反射の経路がまるごと消える。
#    **「床を明るくしたい」と「床だけを照らす」は同じではない。**
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH':
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
    # 🔴 既定は 1920×1080（横）。判型を先に入れないと縦の占有が丸ごと嘘になる
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    print(">> #40(6) 見える発光量 min/max = %.3f （合格 0.75以下）" % (min(_LS) / _LMAX))
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, ys = [], []
    proj = []
    for n, b in enumerate(balls):
        ev = b.evaluated_get(dg)
        bx, by = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            bx.append(c.x); by.append(c.y)
        proj.append((min(bx), max(bx), min(by), max(by)))
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
    print(">> 占有  長辺 %.1f%%（合格 55〜65）" % (max((x1 - x0), (y1 - y0)) * 100))
    print(">> 重心x %.1f%%  枠まで 左%.3f 右%.3f 上%.3f 下%.3f"
          % ((x0 + x1) / 2 * 100, x0, 1 - x1, 1 - y1, y0))
    # 🔴 「寄り」の合否は edge≥1 かつ 長辺78%以上（#57）。枠から出ているかをここで先に見る
    print(">> 各玉の投影")
    for n, (a, b_, c_, d_) in enumerate(proj):
        print("   #%02d  x %.3f..%.3f  y %.3f..%.3f  幅 %.1f%%  高さ %.1f%%"
              % (n, a, b_, c_, d_, (b_ - a) * 100, (d_ - c_) * 100))
    over = ((x0 < 0.0) + (x1 > 1.0) + (y1 > 1.0))
    print(">> 枠から出ている辺 %d（「寄り」は1以上／measure は上80%%で切るので上は出やすい）" % over)

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_053.blend"))

# 🔴 glb は必ず最後（#30：Emission を定数へ潰すので、レンダーの前に置かない）
#    帯は world z に固定されていて glTF に翻訳できないので、**赤道に実体のリング**を足す。
#    ＝glb は「平水面にいる浮玉」の姿になる。#60（glb にライムが乗っていない）を構造的に回避。
if "glb" in modes:
    m_em = bpy.data.materials.new("band_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE
    for n, (x, y, R) in enumerate(FLOATS):
        rng = torus("band_%02d" % n, R + 0.004, BAND_H * 0.55, (0, 0, 0), (0, 0, 0), m_em,
                    mseg=64, nseg=8)
        rng.parent = bases[n]
        parts.append(rng)
        balls[n].data.materials.clear()
        balls[n].data.materials.append(mat_ball_plain)
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = balls[0]
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
