# =============================================================
# monaka design. — MIDDLE STUDY 054 "HOOZUKI"（鬼灯／酸漿 a Chinese lantern plant）
#
# 黒い鬼灯が、高いところに吊られている。下は、ぜんぶ余白。
# 萼（がく）は5枚に裂けていて、その裂け目の奥に**実**がある。
# 萼がひらけば裂け目は広がり、実の光が漏れる。閉じれば、ただの黒い実に戻る。
# **鬼灯は「灯」と書く。灯りは外にはない。萼の中にある。**
#
# 【ドメイン】植物・果実（鬼灯）。直近10作（土木・橋／書物・巻子／商い・暖簾／農・製粉／
#   武・弓／玩具・けん玉／貨幣・銭／楽器・打／漁労・浮子）と別。029 MATSUKASA【植物】は
#   25作前で、あちらは「鱗片が卵形の表面を過剰被覆する」造形＝別機構。
#
# 【光の型＝内包】#53 の8型。直近5作に出ている 稜線／面／背光／芯／隙間 は選べない。
#   黒い殻の内側が光り、**裂け目から見える**（001 THE FILLING／004 ANDON と同じ型）。
#
# 【構図＝天地】🔴 #57：53作のうち **51作が「全身」**（＝1個の物が正面から丸ごと枠の中央）。
#   054 は**高く吊る**。物を上へ置き、**下の余白の量そのもの**を主題にする。
#   合格条件は edge=0 かつ 重心y が基準63%から12%以上ずれること（＝c_y ≤ 51）。
#   🔴 これは「吊るす」という**題材の側の必然**であって、構図のために物を移動させたのではない。
#      鬼灯は枝から下がる。だから上にいて、下が空く。
#   🔴 副産物：被写体がカメラ（z=1.95）より上に来るので、**シリーズで初めて被写体を見上げる**。
#      萼の開口は下向きなので、見上げる角度でしか奥が見えない＝構図と光の型が同じ方向を向く。
#
# 【機構＝ひらく × まわる】光の量を2つの独立な幾何で同時に動かす。
#   ① 縦の裂け目が**その場で開く**（萼の角幅を細らせるシェイプキー）。a(t)=0.5(1−cos2πt)
#      🔴 1周目・2周目は「5枚の萼を首のヒンジまわりに剛体で倒す」機構だった（029 MATSUKASA 方式）。
#         2周とも hero が**黒いチューリップ／吊り下げランプ**に転んだ。原因は機構そのもの：
#         剛体で倒すと**尖端の5点が離れて花弁になる**。鬼灯の萼は嘴（くちばし）で閉じたまま、
#         **中ほどだけが裂ける**。だから開閉は「倒す」ではなく「その場で細る」で書く。
#         裂け目の角度は上下端で 0.9°（＝閉じている）に落とし、腹だけが 3.9°→16.9° に開く。
#   ② 全体が Z 軸まわりに **72°／1周** 回る（5回対称なので t=0 と t=1 が厳密一致）。
#      カメラの正面に**裂け目が来る位相**と**萼が来る位相**が交互に立つ。
#   ①②の位相を合わせ、t=0.5 で「最大に開き、かつ裂け目が正面」＝最も明るい。
#   t=0 は「閉じ、かつ萼が正面」＝最も暗い。#40⑥ は幾何で積分して確認する。
#   さらに吊り元まわりの微かな揺れ SWAY·sin(2πt)（t=0,1 で厳密に 0）。
#
# 🔴 #13/#18 対策：実は萼に遮られたまま**裸の緑玉にしない**。開き切っても萼は実を覆う。
# 🔴 #27 対策：solid な発光体に3D放射グラデを当てるとホットコアが内部に埋まってペンキになる。
#    ここは**縦の裂け目から覗く**ので、勾配は Generated Z の1次元（実の赤道を hot に）。
# 🔴 #52 対策：黒の肌は薄物（nuno_usu）。萼は紙のように薄い。葉脈は**厚みの変化**で作る
#    （別オブジェクトの管を足さない＝裂け目の縁が自然に太くなり、そこが葉脈に読める）。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 吊り元と大きさ ---------------------------------------------
# 🔴 フレームは 縦3.52 × 横2.81（#18）。長辺（＝縦）で 44〜66% に収める（#51③）。
#    さらに c_y ≤ 51 が要るので、**重心を画面の上から36%あたり**に置く。
Z_PIVOT = 3.46         # 吊り元（茎の天）の world z。ここが揺れの支点
STEM_L = 0.22          # 茎の長さ（吊り元 → 首）
L_HUSK = 1.50          # 萼の長さ（首 → 尖端）
HUSK_R = 0.720         # 萼の最大半径（実物の鬼灯は「背より少し細い」程度＝ほぼ球）
N_LOBE = 5             # 萼は5裂（実物どおり）
GAP_END = 0.9          # 上下の端に残す裂け目（度）＝ここは閉じている。0 にすると面が重なる
GAP_MID, GAP_OPEN = 3.0, 16.0   # 腹の裂け目（度）：閉じたとき／開いたとき（GAP_END に足す）
SPIN_DEG = 360.0 / N_LOBE   # 1周で72°＝5回対称で厳密に閉じる
SWAY_DEG = 3.2         # 吊り元まわりの揺れ

# --- 実（内包される光）------------------------------------------
FRUIT_R = 0.300        # 1周目 0.345 は裸の緑玉（#13）。萼に包まれている量を増やす
FRUIT_V = 0.40         # 萼のどの高さに実があるか（v＝首0→尖端1）
ES_CORE = 3.30         # 発光の基準（#14：中間調が #A5E02E より明るい側に来るのが健全）
ES_BASE = 0.18         # 赤道から離れた所の下限（0 にすると縁が死ぬ＝#49）
HOT_MUL = 1.40         # 赤道で何倍にするか
HOT_H = 0.32           # 芯の半幅（Generated Z の 0..1 に対する割合）
EDGE_LO, EDGE_P = 0.32, 0.55   # シルエットの端での落とし（#49）

# --- 萼の厚み（葉脈は厚みで作る）--------------------------------
T_MID, T_VEIN = 0.008, 0.026   # 面の厚み／裂け目の縁（葉脈）の厚み
OUT_VEIN = 0.024               # 葉脈が外へせり出す量
VEIN_W = 0.105                 # 葉脈の幅（rad）
MID_RIB = 0.022                # 萼1枚の中央にも稜を通す（実物は縦に10本のリブ）
# 🔴 黒の肌は Bump では出ない（MATERIALS.md）。稜は**実ジオメトリ**で作る＝
#    面が env のグレーを返すだけの「プラスチックの膜」になるのを、稜のハイライトで止める。

FPS = 24
N_FRAMES = 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.0, 1.92
LIME_W = 180.0         # 随伴のライム光源（#58）。2灯に割る。**発光体の外**に置く

Z_NECK = Z_PIVOT - STEM_L      # 首の world z（萼のローカル原点）

# 萼の輪郭（v, r）。r は正規化前の生値＝最大で割って HUSK_R を掛ける
# 🔴 1周目の輪郭は下半分が細りすぎて、萼が**5本の牙**になり「黒いチューリップ」に転んだ（#16/#33）。
#    鬼灯の下端は嘴（くちばし）状＝**腹を保ったまま最後だけ一気に尖る**。
CP = [(0.00, 0.120), (0.06, 0.262), (0.14, 0.408), (0.24, 0.512), (0.36, 0.556),
      (0.48, 0.553), (0.60, 0.522), (0.72, 0.462), (0.82, 0.372), (0.90, 0.270),
      (0.95, 0.170), (1.00, 0.020)]
_CPMAX = max(r for _, r in CP)


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def ss(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def _hermite(xs, ys, x):
    """制御点を通る滑らかな補間（中央差分の接線）。輪郭を折れ線にしない。"""
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


_XS = [p[0] for p in CP]
_YS = [p[1] for p in CP]


def r_of(v):
    """萼の半径（首 v=0 → 尖端 v=1）"""
    return HUSK_R * _hermite(_XS, _YS, min(1.0, max(0.0, v))) / _CPMAX


def z_of(v):
    return -L_HUSK * v


U_H = r_of(0.0)                       # ヒンジ（首）の半径
Z_FRUIT = -L_HUSK * FRUIT_V           # 実の中心（萼ローカル z）


def mer_normal(v):
    """子午線の外向き法線 (nr, nz)。"""
    d = 1e-3
    dr = (r_of(min(1.0, v + d)) - r_of(max(0.0, v - d)))
    dz = (z_of(min(1.0, v + d)) - z_of(max(0.0, v - d)))
    L = math.hypot(dr, dz) or 1.0
    return (-dz / L, dr / L)


def open_of(t):
    """裂け目の開き 0→1。cos位相なので t=0 と t=1 が厳密一致。"""
    return 0.5 * (1.0 - math.cos(2 * math.pi * t))


def spin_of(t):
    """t=0.5 で「裂け目が正面」。t=0 で「萼が正面」。72°/周なので5回対称で閉じる。"""
    return math.radians(-18.0 + SPIN_DEG * t)


def sway_of(t):
    return math.radians(SWAY_DEG) * math.sin(2 * math.pi * t)


def win_of(v):
    """裂ける窓＝上下の端では 0（首と嘴で萼は繋がったまま）、腹で 1。"""
    return ss(v / 0.17) * ss((1.0 - v) / 0.11)


def gap_of(v, a):
    """高さ v・開き a における裂け目の全角（rad）。"""
    return math.radians(GAP_END + (GAP_MID + (GAP_OPEN - GAP_MID) * a) * win_of(v))


def half_of(v, a):
    """萼1枚の半角（rad）。"""
    return math.pi / N_LOBE - gap_of(v, a) / 2


def shell_lookup(z, a):
    """高さ z における（半径 u, 萼の半角 θe）。萼の外なら None。"""
    if z > 0.0 or z < -L_HUSK:
        return None
    v = -z / L_HUSK
    return (max(1e-4, r_of(v)), half_of(v, a))


def visible(t, nx=41, nz=41):
    """#40⑥：カメラから**実際に見えている発光面の量**を幾何で積分する（#46）。
       カメラ方向を +Y の平行投影とみなし、実の前面の各点について
       「その視線が萼の面を横切るか、裂け目を通るか」を判定する。
       ——裂け目の弧の量ではなく**光っている面が何割見えているか**を直接測る（#62②）。"""
    a, sp = open_of(t), spin_of(t)
    tot = 0.0
    for iz in range(nz):
        z = Z_FRUIT + FRUIT_R * (-1.0 + 2.0 * (iz + 0.5) / nz)
        rr = math.sqrt(max(0.0, FRUIT_R ** 2 - (z - Z_FRUIT) ** 2))       # その高さでの実の半幅
        hot = ES_BASE + HOT_MUL * (1.0 - ss(abs(z - Z_FRUIT) / (2 * FRUIT_R) / HOT_H))
        hit = shell_lookup(z, a)
        for ix in range(nx):
            x = -rr + 2 * rr * (ix + 0.5) / nx
            if hit is None:
                tot += hot * (2 * rr / nx); continue
            u, the = hit
            if abs(x) >= u:                          # 萼のシルエットの外＝そのまま見える
                tot += hot * (2 * rr / nx); continue
            th = math.atan2(-math.sqrt(u * u - x * x), x)                 # 手前側で萼を横切る方位
            blocked = False
            for j in range(N_LOBE):
                d = (th - (sp + 2 * math.pi * j / N_LOBE) + math.pi) % (2 * math.pi) - math.pi
                if abs(d) <= the:
                    blocked = True; break
            if not blocked:
                tot += hot * (2 * rr / nx)
    return tot


_VS = [visible(i / N_FRAMES) for i in range(N_FRAMES)]
_VMAX = max(_VS)
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _VS[i]) + 1

if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d (t=%.3f)" % (STILL_FRAME, (STILL_FRAME - 1) / N_FRAMES))
    print(">> #40(6) 見える光 min/max = %.3f  （合格 0.75以下）" % (min(_VS) / _VMAX))
    print(">> ループの閉じ: open(0)=%.4f open(1)=%.4f  sway(0)=%.4f sway(1)=%.4f  spin差=%.1f°(=72°で5回対称)"
          % (open_of(0), open_of(1), sway_of(0), sway_of(1),
             math.degrees(spin_of(1) - spin_of(0))))
    print(">> 萼  首 r=%.3f  最大 r=%.3f  長さ %.2f   実 R=%.3f  z=%.3f" % (U_H, HUSK_R, L_HUSK, FRUIT_R, Z_FRUIT))
    print(">> 世界での上下: 天 %.2f / 首 %.2f / 尖端 %.2f （床0・カメラ z=1.95）"
          % (Z_PIVOT, Z_NECK, Z_NECK - L_HUSK))
    for i in range(0, N_FRAMES, 10):
        t = i / N_FRAMES
        print("   t=%.3f  開き %.2f  腹の裂け目 %4.1f°  正面までの裂け目 %5.1f°  見える光 %5.1f%%"
              % (t, open_of(t), math.degrees(gap_of(0.45, open_of(t))),
                 math.degrees(min(abs(((spin_of(t) + 2 * math.pi * j / N_LOBE + math.pi / N_LOBE)
                                       - (-math.pi / 2) + math.pi) % (2 * math.pi) - math.pi)
                                  for j in range(N_LOBE))),
                 100 * _VS[i] / _VMAX))
    for tt in (0.0, 0.5):
        a = open_of(tt)
        for v in (0.30, 0.45, 0.70):
            print("   t=%.1f v=%.2f  半径 %.3f  裂け目 %4.1f°（幅 %.3f m）"
                  % (tt, v, r_of(v), math.degrees(gap_of(v, a)), r_of(v) * gap_of(v, a)))
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
# 萼＝紙のように薄い＝薄物（MATERIALS.md「光を透かすほど薄いもの」）。1作に1素材（掟4）。
RECIPE = "nuno_usu"
# 🔴 #62③/#63④：レシピは径0.3程度の球で測った値。萼は径1.1の大きな曲面なので、
#    そのまま当てると明るい env（0.92）を面で返して**オリーブ色の樹脂**に見えた（1周目の実測）。
#    効くのは金属度（#57②：#0a0a0a の金属はグレー環境を映しても黒いまま）。粗さは紙のまま。
BLACK_RECIPES["nuno_usu"] = dict(rough=0.70, spec=0.32, metal=0.42, sheen=0.30, sheen_rough=0.30)


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


mat_husk = black_material("husk", RECIPE)


def fruit_material(name):
    """実＝**純発光体**（#13：裸で露出しうる発光体は Base Color を落として反射成分を消す）。
       勾配は Generated Z の1次元（#27：solid な塊に3D放射を当てるとホットコアが内部に埋まる）。
       さらにシルエットの端で落とす（#49）。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)
    p.inputs["Roughness"].default_value = 0.55
    p.inputs["Specular IOR Level"].default_value = 0.10
    p.inputs["Emission Color"].default_value = LIME

    tc = nt.nodes.new("ShaderNodeTexCoord")
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], xyz.inputs["Vector"])

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

    d = mn('SUBTRACT', 0.5); nt.links.new(xyz.outputs["Z"], d.inputs[0])
    ab = mn('ABSOLUTE'); nt.links.new(d.outputs[0], ab.inputs[0])
    hot = mr(0.0, HOT_H, 1.0, 0.0)              # 赤道が芯・両極へ落ちる
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
    nt.links.new(e2.outputs[0], p.inputs["Emission Strength"])
    return m


mat_fruit = fruit_material("fruit")

mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
def finish(bm, name, mat, bevel=0.0025, angle=35):
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
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def lathe(profile, name, mat, nseg=96):
    bm = bmesh.new()
    rings, poles = [], []
    for (r, z) in profile:
        if r < 1e-6:
            v = bm.verts.new((0.0, 0.0, z)); rings.append(None); poles.append(v)
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / nseg),
                                        r * math.sin(2 * math.pi * k / nseg), z))
                          for k in range(nseg)])
            poles.append(None)
    for i in range(len(profile) - 1):
        A, B = rings[i], rings[i + 1]
        if A is None and B is None:
            continue
        if A is None:
            p = poles[i]
            for k in range(nseg):
                bm.faces.new((p, B[(k + 1) % nseg], B[k]))
        elif B is None:
            p = poles[i + 1]
            for k in range(nseg):
                bm.faces.new((p, A[k], A[(k + 1) % nseg]))
        else:
            for k in range(nseg):
                bm.faces.new((A[k], A[(k + 1) % nseg], B[(k + 1) % nseg], B[k]))
    return finish(bm, name, mat, bevel=0.0)


NV, NT = 46, 17                     # 萼1枚の分割（子午線 × 周）


def lobe_points(a):
    """萼1枚の頂点列（開き a）。**(i,j) ごとに 外→内 の順**で並べる。
       基底とシェイプキーで頂点の順序が厳密に同じでなければならないので、生成はこの1関数に集約する。
       葉脈は別部品にせず、**裂け目の縁と萼の中央で厚みを増す**ことで作る（黒の肌は実ジオメトリ）。"""
    pts = []
    for i in range(NV):
        v = i / (NV - 1)
        u0, w0 = r_of(v), z_of(v)
        nr, nz = mer_normal(v)
        H = half_of(v, a)
        fade = ss(v / 0.07) * ss((1.0 - v) / 0.07)          # 天地の端で葉脈を消す
        for j in range(NT):
            th = -H + 2 * H * j / (NT - 1)
            e = ss(1.0 - (H - abs(th)) / VEIN_W) * fade     # 縁（裂け目）に近いほど1
            em = ss(1.0 - abs(th) / (0.55 * H)) * fade      # 萼の中央の稜
            to = OUT_VEIN * e + MID_RIB * em
            ti = T_MID + (T_VEIN - T_MID) * e
            uo, zo = u0 + nr * to, w0 + nz * to
            ui, zi = u0 - nr * ti, w0 - nz * ti
            pts.append((uo * math.cos(th), uo * math.sin(th), zo))
            pts.append((ui * math.cos(th), ui * math.sin(th), zi))
    return pts


def lobe_mesh(name):
    """萼1枚。ローカル＝萼の座標（方位0が中心）。object.rotation_euler=(0,0,α) で5枚に配る。
       開閉は**シェイプキー**（その場で細る）＝#9/#15 を構造回避したまま、尖端と首は繋がったまま。
       🔴 bmesh.ops.bevel と remove_doubles は**使わない**（頂点の数と順序が変わるとシェイプキーが
          作れない）。稜の面取りは BEVEL モジファイアで掛ける（#10：角度制限つき）。"""
    pts = lobe_points(0.0)
    bm = bmesh.new()
    vs = [bm.verts.new(q) for q in pts]
    bm.verts.ensure_lookup_table()
    O = lambda i, j: vs[2 * (i * NT + j)]
    I = lambda i, j: vs[2 * (i * NT + j) + 1]
    for i in range(NV - 1):
        for j in range(NT - 1):
            bm.faces.new((O(i, j), O(i, j + 1), O(i + 1, j + 1), O(i + 1, j)))
            bm.faces.new((I(i, j), I(i + 1, j), I(i + 1, j + 1), I(i, j + 1)))
        for j in (0, NT - 1):                                # 裂け目の側面＝葉脈の小口
            bm.faces.new((O(i, j), O(i + 1, j), I(i + 1, j), I(i, j)))
    for j in range(NT - 1):                                  # 天と地のふさぎ
        bm.faces.new((O(0, j), I(0, j), I(0, j + 1), O(0, j + 1)))
        bm.faces.new((O(NV - 1, j), O(NV - 1, j + 1), I(NV - 1, j + 1), I(NV - 1, j)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat_husk)
    ob.shape_key_add(name="Basis", from_mix=False)
    sk = ob.shape_key_add(name="open", from_mix=False)
    for idx, q in enumerate(lobe_points(1.0)):
        sk.data[idx].co = q
    sk.value = 0.0
    bv = ob.modifiers.new("bev", 'BEVEL')
    bv.width = 0.0022; bv.segments = 2
    bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(32)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        pass
    ob.select_set(False)
    return ob, sk


def stem_profile():
    """茎（首 z=0 → 吊り元 z=STEM_L）。回転対称に保つ＝72°回転で厳密に閉じる。"""
    # 🔴 hero で見たら**針**だった（5周目）。480px では細い縦線にしか見えず気づかない（#16）。
    #    鬼灯の柄は短く、萼の肩からすっと立つ。長さを 0.50→0.34、太さを 1.5 倍に。
    # 🔴 hero で見たら**針**（5周目）→ 太く短くしたら今度は**玉ねぎの芽**（6周目）。
    #    鬼灯の柄は「細いまま短く立つ」。テーパーを付けず、ほぼ等径の丸棒＋丸い先にする。
    pts = [(0.0, -0.014), (0.062, 0.004)]
    N = 8
    for k in range(1, N + 1):
        a = k / N
        pts.append((0.048 - 0.008 * a, 0.020 + (STEM_L - 0.030) * a))
    pts.append((0.034, STEM_L - 0.004))
    pts.append((0.020, STEM_L + 0.008))
    pts.append((0.0, STEM_L + 0.016))
    return pts


def fruit_profile():
    pts = []
    N = 64
    for k in range(N + 1):
        a = -math.pi / 2 + math.pi * k / N
        pts.append((FRUIT_R * math.cos(a), FRUIT_R * math.sin(a)))
    return pts


# ---------- リグと配置 ----------
sway = bpy.data.objects.new("sway", None)
bpy.context.collection.objects.link(sway)
sway.location = (0.0, 0.0, Z_PIVOT)

spin = bpy.data.objects.new("spin", None)
bpy.context.collection.objects.link(spin)
spin.parent = sway
spin.location = (0.0, 0.0, -STEM_L)          # 首（萼のローカル原点）

parts = []
stem = lathe(stem_profile(), "stem", mat_husk, nseg=48)
stem.parent = spin; parts.append(stem)

fruit = lathe(fruit_profile(), "fruit", mat_fruit, nseg=96)
fruit.parent = spin
fruit.location = (0.0, 0.0, Z_FRUIT)
parts.append(fruit)

lobes, keys = [], []
for k in range(N_LOBE):
    lb, sk = lobe_mesh("lobe_%d" % k)
    lb.parent = spin
    lb.rotation_euler = (0.0, 0.0, 2 * math.pi * k / N_LOBE)
    lobes.append(lb); keys.append(sk); parts.append(lb)
parts += [sway, spin]

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    sway.rotation_euler = (0.0, sway_of(t), 0.0)
    sway.keyframe_insert("rotation_euler", frame=f + 1)
    spin.rotation_euler = (0.0, 0.0, spin_of(t))
    spin.keyframe_insert("rotation_euler", frame=f + 1)
    for sk in keys:
        sk.value = open_of(t)
        sk.keyframe_insert("value", frame=f + 1)

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
        caption("MIDDLE STUDY 054 — HOOZUKI", 0.045, (AIM_X, -1.7, 0.57), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0.0, 0.0, Z_NECK + Z_FRUIT)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）

# 🔴 #58③：随伴のライム光源は**発光体の外**に置く。2灯に割り、実の下・手前に出す。
limelamps = []
for sgn in (-1, +1):
    bpy.ops.object.light_add(type='POINT',
                             # 🔴 手前（y=-2.40）に置くと、床の照り返しで**キャプションがオリーブ色**になる
                             #    （5周目・420W で顕在化）。奥へ回し、measure が床とみなす帯（画面62〜80%
                             #    ＝遠い床）を直接照らす。キャプションは y=-1.7 なので光源から離れる。
                             location=(sgn * 0.95, 0.30, Z_NECK + Z_FRUIT - 1.35))
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
cam.data.dof.focus_object = fruit
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

# 🔴 ライムの随伴光源（#58）の受光先。**萼だけを外す。**
#    2周目に W を 160→240 に上げたら、萼の外側が**オリーブ色の樹脂**になった。
#    随伴光源は「実の光が空間に出ている」を作るための代役なので、**実の外側を外から緑に塗る**のは筋が違う。
#    萼の外側が拾ってよい緑は、実の emission が裂け目から漏れて回る分だけ（それは Cycles が計算する）。
#    🔴 ただし床1枚に絞ってはいけない（#63③：相互反射の経路ごと消えて床のライムが 0.02% に落ちる）。
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o not in lobes:
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
    print(">> 占有  長辺 %.1f%%（合格 44〜66・狙い55前後）" % (max((x1 - x0), (y1 - y0)) * 100))
    # 🔴 #57「天地」は edge=0 かつ 重心y が 63% から12%以上ずれること。画面の上からの% で見る
    cy_top = (1.0 - sum(ys) / len(ys)) * 100        # 画面の上から何%（頂点平均・近似）
    print(">> 頂点平均の高さ（画面の上から）%.1f%%  → measure の c_y 換算 %.1f%%（合格 51以下）"
          % (cy_top, cy_top / 0.8))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （上が 0.004 を切ると edge≥1 で天地は不合格）"
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_054.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("fruit_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.75
    fruit.data.materials.clear()
    fruit.data.materials.append(m_em)
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = fruit
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
