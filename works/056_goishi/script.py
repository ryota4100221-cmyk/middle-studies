# =============================================================
# MIDDLE STUDY 056 — GOISHI（碁石 / 眼 the eyes of a living group）
#
# 黒い石が、いくつもの塊になって宙にある。盤は無い。
# 光っているのは石ではなく、石が囲んだ**空点＝「眼」**だけ。
# 石が一つ滑ってその空点を埋めると、塊の光は消える。
# ただ真ん中の塊だけは眼をふたつ持っていて、片方を埋められても、もう片方が残る。
# **生きているかどうかは、石の数ではない。真ん中に空きがあるかどうかで決まる。**
#
# 🔴 構図の型＝**群**（#57：55作中51作が「全身」。「群」はシリーズ初）
#    #63① の前提条件：「群」は水平面のモチーフとは両立しない（水平カメラでは1次元にしか散れない）。
#    → 碁は**盤面を正面から見る＝棋譜の見え方**が正典なので、格子を**立てて**カメラに正対させる。
#      これで被写体は画面の2次元に散る＝#63① の要件をそのまま満たす。
# 🔴 光の型＝**反復**（#53：縞・輪・格子として多数現れる。7つの眼が盤の上に散る）
# 【ドメイン】盤上遊戯・囲碁（シリーズ未踏）。直近10作＝鋳造/植物・果実/漁労/楽器・打/貨幣/
#            玩具・けん玉/武・弓/農・製粉/商い・暖簾/書物・巻子 と別。
#            037 KOMA・050 KENDAMA は【玩具】＝一人の身体技、こちらは二人の配置で別物。
#
# 機構＝**眼を埋める一手（filling the eye）**。各塊の眼に隣接する石が1路ぶん滑って空点に座る。
#   a_g(t) = 0.5(1 − cos(2πt − ψ_g)) の整数周期＝完全ループ。**位置キーだけ**なので glb に乗る。
#   移動距離＝1路＝PITCH で、PITCH = R_STONE + R_EYE。よって a=0 で厳密に外接（光は満ちる）、
#   a=1 で厳密に全遮蔽（光は消える）＝#40⑥ が幾何で 0 まで振れる。
#   ψ を上から下へずらして**光が盤を渡る波**にする（＝光の型「反復」の担保）。
#   塊 D だけは眼が2つで、2つの蓋石が**逆位相**（ψ と ψ+π）＝どちらかは必ず開いている。
#
# 🔴 盤は描かない（描くと全塊が1つに繋がって「群」が壊れる）。代わりに
#    **塊ごとの黒い裏当て板（占有マスの和＝ポリオミノ）**を石の後ろに置く。
#    これが無いと石と石のすき間から**白い背景**が抜けて、塊が透けたレースになる。
#    板は石の footprint と同寸（半路＝0.085）なので、正面からは石に隠れて見えない。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 盤（見えない格子）------------------------------------------
PITCH = 0.170                  # 一路
R_STONE = 0.0855               # 碁石の半径（実物は径22.2mm／路22mm＝ほぼ路いっぱい）
T_STONE = 0.300 * 2 * R_STONE  # 🔴 実物は 0.414（9.2/22.2）だが、1周目はビー玉に見えた。
                               #    真上に近い視線では厚みは輪郭に出ず**陰影の丸さ**だけが残るため、
                               #    実測比より薄くして「石」に寄せる
H_STONE = T_STONE / 2.0
R_EYE = PITCH - R_STONE        # 🔴 = 0.0845。蓋石が座ったとき**厳密に**眼を覆い切る寸法
STONE_P = 3.4                  # 碁石の断面＝超楕円 |r/R|^p+|h/H|^p=1（p=2.6 で「縁の丸いレンズ」）

NI, NJ = 10, 13                # 格子の路数（i=0..9 / j=0..12）
U0 = -(NI - 1) / 2.0           # 中心を原点に
V0 = -(NJ - 1) / 2.0

# --- 塊（棋譜の断片）--------------------------------------------
# stones=石のマス / eyes=空点（光る） / lids=(蓋石の元マス, 埋めにゆく眼, 位相ψ[turn])
# 🔴 塊どうしは **横3路・縦2路** 空ける＝投影のすき間 横193px・縦96px（#63①：12pxで繋がる）
GROUPS = {
    "A": dict(stones=[(0, 10), (1, 10), (2, 10), (3, 10), (0, 11), (2, 11), (3, 11),
                      (0, 12), (1, 12)],
              eyes=[(1, 11)], lids=[((1, 10), (1, 11), -0.16)]),
    "B": dict(stones=[(7, 10), (8, 10), (6, 11), (8, 11), (9, 11),
                      (7, 12), (8, 12), (9, 12)],
              eyes=[(7, 11)], lids=[((7, 12), (7, 11), -0.10)]),
    "C": dict(stones=[(0, 4), (1, 4), (1, 5), (2, 5), (0, 6), (2, 6), (0, 7), (1, 7)],
              eyes=[(1, 6)], lids=[((1, 5), (1, 6), -0.03)]),
    # 🔴 二つの眼＝生きている塊。蓋は逆位相なので、どちらかは必ず開いている
    "D": dict(stones=[(8, 4), (9, 4), (7, 5), (9, 5), (7, 6), (8, 6), (9, 6),
                      (7, 7), (9, 7), (7, 8), (8, 8)],
              eyes=[(8, 5), (8, 7)],
              lids=[((8, 4), (8, 5), 0.03), ((8, 8), (8, 7), 0.53)]),
    "E": dict(stones=[(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (2, 1), (1, 2), (2, 2)],
              eyes=[(1, 1)], lids=[((1, 0), (1, 1), 0.10)]),
    "F": dict(stones=[(6, 1), (7, 0), (8, 0), (9, 0), (7, 1), (9, 1), (8, 2), (9, 2)],
              eyes=[(8, 1)], lids=[((8, 2), (8, 1), 0.16)]),
    # 単独の石（捨て石／打ちかけの手）。**塊を2列3段のグリッドに見せない**ための3子
    "G": dict(stones=[(5, 3)], eyes=[], lids=[]),
    "H": dict(stones=[(4, 7)], eyes=[], lids=[]),
    "I": dict(stones=[(5, 9)], eyes=[], lids=[]),
}
# 🔴 1〜6周目の記録（どれもパラメータでは直らなかった「型」の失敗）
#    ・マスをぎっしり埋めた面   → 黒いキャビア／気泡緩衝材（同じ丸い物が密に並ぶと texture になる）
#    ・四方＋斜め2子の最小の囲み → **花**（対称な輪＋中心の光＝#64 と同じ罠）
#    直ったのは形でも材質でもなく **並び**：碁の塊は蛇行する鎖で、腕が伸び、角が欠け、
#    盤には必ず単独の石が落ちている。**規則正しい輪をやめた瞬間に「置かれた石」に読める。**
#    塊どうしは中心間 2路以上（dx²+dy² ≥ 4）＝投影のすき間 39px 以上を probe で機械検査する。

HOP = 0.055                    # 蓋石が「置かれる」ときの手前への浮き（正面カメラなので遮蔽には効かない）

# --- 裏当て板（塊ごと）------------------------------------------
PLUG_Y = 0.100                 # 穴埋めの球の中心（石の裏。詳細は plug_mesh）

# --- 眼（発光）--------------------------------------------------
# 🔴 1周目：眼を「石と同径・同位置の発光レンズ」にしたら、**黒い碁石に混じった緑の碁石**に見えた
#    （#24 のペンキ化と同じ構造：光が「面」でなく「物」に見えている）。
#    → **黒い井戸を掘って、底にだけ光を置く。** 手前の黒い筒壁が見えることで
#      「石が無い＝空点」が絵として成立する。ES=0 の裾も筒の中なので白背景に晒されない（#49）。
EYE_RIM_Y = 0.004              # 井戸の口（盤面のすぐ奥）
EYE_FLOOR_Y = 0.036            # 井戸の底（深さ 0.032。深すぎると斜めから底が見えない）
EYE_SAG = 0.012                # 底のわずかな窪み
ES_CORE = 13.5
EYE_BASE = 0.0                 # 🔴 縁で厳密に 0（筒の内壁との境が光ると井戸が消える）
EYE_P = 1.15
FAC_LO, FAC_P = 0.55, 1.0      # #65：底は平らなので Facing は弱く（強いと凹が凸に転ぶ）

# --- 盤ぜんぶの揺れ（機構ではなく気配。整数周期）----------------
SWAY_Z_DEG = 1.6
SWAY_X_DEG = 0.9
YAW_DEG = 14.0                 # 盤の据わり。石の小口が片側に見える＝板でなく石だと分かる
LEAN_DEG = -6.0                # 天を奥へ倒す（下段が手前＝キーライトを拾い、上段は退く）

FPS = 24
N_FRAMES = 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.0, 1.95
Z_C = 2.20                     # 盤の中心の world z（キャプションから 13% 逃がす）
LIME_W = 95.0                  # 随伴のライム光源（#58）。**発光体の外**に置く

NSEG, NRING = 40, 16           # 碁石のラチェ分割
NEYE_R, NEYE_S = 14, 40


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def uv_of(i, j):
    """格子 → 盤ローカル (x, z)"""
    return ((i + U0) * PITCH, (j + V0) * PITCH)


def a_of(t, psi):
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * (t - psi)))


def lid_pos(t, src, dst, psi):
    """蓋石のローカル座標 (x, y, z)。y は手前（−）へ浮く"""
    a = a_of(t, psi)
    x0, z0 = uv_of(*src)
    x1, z1 = uv_of(*dst)
    return (x0 + (x1 - x0) * a, -HOP * math.sin(math.pi * a), z0 + (z1 - z0) * a)


def circ_overlap(d, R, r):
    """2円の重なり面積（d=中心間距離）"""
    if d >= R + r:
        return 0.0
    if d <= abs(R - r):
        return math.pi * min(R, r) ** 2
    a1 = math.acos((d * d + R * R - r * r) / (2 * d * R))
    a2 = math.acos((d * d + r * r - R * R) / (2 * d * r))
    return (R * R * (a1 - math.sin(2 * a1) / 2) + r * r * (a2 - math.sin(2 * a2) / 2))


A_EYE = math.pi * R_EYE ** 2


def eye_visible(t):
    """#40⑥ は幾何で積分する（#46）。見えている発光面＝眼の円 − 蓋石の円の重なり。
       盤はカメラにほぼ正対しているので、投影の縮みは全部の眼に等しく効く＝比には出ない。"""
    tot = 0.0
    for g in GROUPS.values():
        cov = {e: 0.0 for e in g["eyes"]}
        for src, dst, psi in g["lids"]:
            a = a_of(t, psi)
            d = PITCH * (1.0 - a)
            cov[dst] = max(cov[dst], circ_overlap(d, R_EYE, R_STONE))
        for e in g["eyes"]:
            tot += max(0.0, A_EYE - cov[e])
    return tot


def eye_states(t):
    """各眼の開き（0=消灯 1=満ちる）"""
    out = []
    for gn, g in sorted(GROUPS.items()):
        cov = {e: 0.0 for e in g["eyes"]}
        for src, dst, psi in g["lids"]:
            d = PITCH * (1.0 - a_of(t, psi))
            cov[dst] = max(cov[dst], circ_overlap(d, R_EYE, R_STONE))
        for e in g["eyes"]:
            out.append((gn, e, max(0.0, A_EYE - cov[e]) / A_EYE))
    return out


_VS = [eye_visible(i / N_FRAMES) for i in range(N_FRAMES)]
_VMAX = max(_VS)


def _score(i):
    """hero の選び方（#62②：hero は「現象が見えている」ことで選ぶ）。
       総量を主にしつつ、**三日月に欠けた眼が1つ以上ある**フレームを選ぶ＝
       「石が眼を埋めにゆく」がスチル1枚で読める。"""
    t = i / N_FRAMES
    st = [v for _, _, v in eye_states(t)]
    cres = sum(1 for v in st if 0.20 < v < 0.80)
    return sum(st) + (0.55 * min(cres, 3) if cres else -99)


STILL_FRAME = max(range(N_FRAMES), key=_score) + 1

if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d (t=%.3f)" % (STILL_FRAME, (STILL_FRAME - 1) / N_FRAMES))
    print(">> #40(6) 見える光 min/max = %.3f  （合格 0.75以下）" % (min(_VS) / _VMAX))
    print(">> ループの閉じ: V(0)=%.6f V(1)=%.6f  差 %.2e" % (_VS[0], eye_visible(1.0),
                                                          abs(_VS[0] - eye_visible(1.0))))
    ns = sum(len(g["stones"]) for g in GROUPS.values())
    ne = sum(len(g["eyes"]) for g in GROUPS.values())
    print(">> 石 %d 個／眼 %d 個／塊 %d（「群」の合格は 5 以上）" % (ns, ne, len(GROUPS)))
    w = (NI - 1) * PITCH + 2 * R_STONE
    h = (NJ - 1) * PITCH + 2 * R_STONE
    print(">> 盤の広がり  横 %.3f m（枠2.81 の %.1f%%） 縦 %.3f m（枠3.52 の %.1f%%）"
          % (w, w / 2.81 * 100, h, h / 3.52 * 100))
    print(">> 眼の全開面積 %.4f m² × %d = %.1f%%（枠 9.89 m²。#51 の帯 0.8〜12.0）"
          % (A_EYE, ne, A_EYE * ne / 9.89 * 100))
    print(">> world z %.3f .. %.3f（キャプション最上段は見かけ z=0.567）"
          % (Z_C - h / 2, Z_C + h / 2))
    # 塊どうしの格子上のすき間（投影のすき間はこれに比例する）
    boxes = {}
    for gn, g in GROUPS.items():
        cells = g["stones"] + g["eyes"]
        boxes[gn] = (min(c[0] for c in cells), max(c[0] for c in cells),
                     min(c[1] for c in cells), max(c[1] for c in cells))
    names = sorted(boxes)
    worst = 9e9
    for x in range(len(names)):
        for y in range(x + 1, len(names)):
            a, b = boxes[names[x]], boxes[names[y]]
            gx = max(a[0] - b[1], b[0] - a[1]) * PITCH - 2 * R_STONE
            gy = max(a[2] - b[3], b[2] - a[3]) * PITCH - 2 * R_STONE
            gap = max(gx, gy)
            worst = min(worst, gap)
    print(">> 塊どうしの最小すき間 %.3f m（横なら %.0fpx / 縦なら %.0fpx。12px で繋がる）"
          % (worst, worst / 2.81 * 1600, worst / 3.52 * 2000))
    bad = []
    gl = sorted(GROUPS)
    for x in range(len(gl)):
        for y in range(x + 1, len(gl)):
            for (i1, j1) in GROUPS[gl[x]]["stones"] + GROUPS[gl[x]]["eyes"]:
                for (i2, j2) in GROUPS[gl[y]]["stones"] + GROUPS[gl[y]]["eyes"]:
                    d2 = (i1 - i2) ** 2 + (j1 - j2) ** 2
                    if d2 < 4:
                        bad.append("%s%s %s-%s d²=%d" % (gl[x], gl[y], (i1, j1), (i2, j2), d2))
    print(">> 塊どうしの最小中心間: %s" % ("🔴 " + " / ".join(bad) if bad else "✅ 全ペア 2路以上"))
    for i in range(0, N_FRAMES, 10):
        t = i / N_FRAMES
        st = eye_states(t)
        print("   t=%.3f  光 %5.1f%%   " % (t, 100 * _VS[i] / _VMAX)
              + " ".join("%s%s%3.0f" % (g, "₁₂"[e[1] > 6] if g == "D" else " ", v * 100)
                         for g, e, v in st))
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
    # 碁石＝那智黒。urushi そのままだと**ビー玉**に見えた（2周とも）。
    # 粗さを上げてハイライトを広げ、クリアコートを外す（艶の層が球感を強める）
    # 🔴 #57②：発光が回り込むと黒が**抹茶色**に転ぶ。#0a0a0a の金属は反射がベースカラーで
    #    色づく＝ライムを浴びても黒いまま。誘電体のままだと拡散でオリーブになる。
    "nachiguro": dict(rough=0.46, spec=0.24, metal=0.42),
    "touki":  dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10),
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25, disp=0.004, dsize=0.05),
    "nuno_usu": dict(rough=0.66, spec=0.28, sheen=0.55, sheen_rough=0.25),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
}
# 碁石＝那智黒石（磨いた黒石）＝ urushi。径 0.171 はレシピを測った 0.3 球と同水準なので
# #63④（径1.0超は coat=0/metal=0.42）の補正は要らない。
STONE_R = "nachiguro"
# 裏当て板は「見えないことが仕事」。艶があると石のすき間から白い環境を返して縁が光る。
# 055 と同じ理由（#65）で touki を平面向けに振り直す：粗さを上げ、下がる黒は金属度で戻す。
# 🔴 2周目：板を誘電体（metal 0.22）にしたら、眼の発光を拡散で返して
#    石と石のすき間が全部ライムに光り、塊が「緑のキーパッド」になった。
#    #57②：#0a0a0a の**金属**は反射がベースカラーで色づく＝緑を浴びても黒いまま。
#    板は「見えないことが仕事」なので、ここは金属で正しい（#45 の対象は主役の黒）。
BLACK_RECIPES["plate"] = dict(rough=0.86, spec=0.12, metal=1.0)


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


mat_stone = black_material("stone", STONE_R)
mat_plate = black_material("plate", "plate")


def eye_material(name):
    """眼＝空点に溜まった光。勾配は **UV に焼いた半径**（#34/#39）。
       u = r/R_EYE ：中心が芯・|u|=1（縁）で EYE_BASE まで落ちる。
       縁の外は黒い裏当て板なので、白背景に ES=0 の面を晒す #49 の事故は起きない。
       🔴 #65：純発光体は法線依存の項が無いと形が消える。窪みなので Facing を弱く掛けて
          「孔に溜まっている」向きの陰影だけ残す（強くすると凹が凸に転ぶ）。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)   # #32：裏当ては純黒寄り
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

    fr = mr(0.0, 1.0, 1.0, 0.0)                       # 半径：中心1 → 縁0
    nt.links.new(xyz.outputs["X"], fr.inputs["Value"])
    frp = mn('POWER', EYE_P); nt.links.new(fr.outputs["Result"], frp.inputs[0])
    frs = mn('MULTIPLY', 1.0 - EYE_BASE); nt.links.new(frp.outputs[0], frs.inputs[0])
    fra = mn('ADD', EYE_BASE); nt.links.new(frs.outputs[0], fra.inputs[0])

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    fcp = mn('POWER', FAC_P); nt.links.new(lw.outputs["Facing"], fcp.inputs[0])
    fcs = mn('MULTIPLY', 1.0 - FAC_LO); nt.links.new(fcp.outputs[0], fcs.inputs[0])
    fca = mn('ADD', FAC_LO); nt.links.new(fcs.outputs[0], fca.inputs[0])

    e1 = mn('MULTIPLY'); nt.links.new(fra.outputs[0], e1.inputs[0])
    nt.links.new(fca.outputs[0], e1.inputs[1])
    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e1.outputs[0], e2.inputs[0])
    nt.links.new(e2.outputs[0], p.inputs["Emission Strength"])
    return m


mat_eye = eye_material("eye")

mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
def finish_mesh(bm, name, bevel=0.0018, angle=32, smooth=True):
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
    me["_smooth"] = smooth
    return me


def link(me, name, mat, parent, mat2=None):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if not ob.data.materials:
        ob.data.materials.append(mat)
        if mat2 is not None:
            ob.data.materials.append(mat2)
    ob.parent = parent
    if me.get("_smooth"):
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        try:
            bpy.ops.object.shade_auto_smooth(angle=0.35)
        except Exception:
            pass
        ob.select_set(False)
    return ob


def stone_mesh():
    """碁石＝超楕円レンズを **Y 軸まわり**に回した実体。
       Y 軸まわりに作るので、盤の法線＝−Y（カメラ側）が最初から出る
       ＝#57① の「リグの Rx の符号を間違えて造形が丸ごと裏に回る」罠を構造的に踏まない。"""
    bm = bmesh.new()
    prof = []                                     # (r, h) 上半分：極 → 赤道
    for k in range(NRING + 1):
        th = math.pi / 2 * k / NRING
        r = R_STONE * (math.sin(th) ** (2.0 / STONE_P))
        h = H_STONE * (math.cos(th) ** (2.0 / STONE_P))
        prof.append((r, h))
    rings = []
    for sgn in (+1, -1):                          # 表（−Y 側）と裏
        pp = prof if sgn > 0 else list(reversed(prof[:-1]))
        for r, h in pp:
            if r < 1e-6:
                rings.append([bm.verts.new((0.0, -sgn * h, 0.0))])
            else:
                rings.append([bm.verts.new((r * math.cos(2 * math.pi * s / NSEG),
                                            -sgn * h,
                                            r * math.sin(2 * math.pi * s / NSEG)))
                              for s in range(NSEG)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for s in range(NSEG):
                bm.faces.new([a[0], b[s], b[(s + 1) % NSEG]])
        elif len(b) == 1:
            for s in range(NSEG):
                bm.faces.new([a[s], a[(s + 1) % NSEG], b[0]])
        else:
            for s in range(NSEG):
                bm.faces.new([a[s], a[(s + 1) % NSEG], b[(s + 1) % NSEG], b[s]])
    return finish_mesh(bm, "goishi", bevel=0.0)   # レンズに鋭い稜線は無い


def eye_mesh():
    """眼＝**黒い井戸**（筒壁）＋ 底の発光面。マテリアルスロット 0=筒壁(黒) / 1=底(発光)。
       🔴 1周目は「石と同径の発光レンズ」で、黒石に混じった**緑の碁石**に見えた。
          手前に黒い筒壁が立つと「そこに石が無い＝空点だ」が絵として先に読める。
       UV.x に r/R_EYE を焼く（#39）。ES は縁で厳密に 0（筒壁との境を光らせない）。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")

    def ring(y, r):
        return [bm.verts.new((r * math.cos(2 * math.pi * s / NEYE_S), y,
                              r * math.sin(2 * math.pi * s / NEYE_S)))
                for s in range(NEYE_S)]

    lip = ring(EYE_RIM_Y, R_EYE)                     # 井戸の口
    bot = ring(EYE_FLOOR_Y, R_EYE)                   # 底の縁
    wall = []
    for s in range(NEYE_S):
        wall.append(bm.faces.new([lip[s], lip[(s + 1) % NEYE_S],
                                  bot[(s + 1) % NEYE_S], bot[s]]))
    # 底（わずかに窪ませる。平らだと「点いたパネル」になる＝#65）
    rings = [bot]
    for k in range(NEYE_R - 1, 0, -1):
        rr = R_EYE * k / NEYE_R
        yy = EYE_FLOOR_Y + EYE_SAG * (1.0 - (k / NEYE_R) ** 2)
        rings.append(ring(yy, rr))
    cen = bm.verts.new((0.0, EYE_FLOOR_Y + EYE_SAG, 0.0))
    floor = []
    for u, v in zip(rings, rings[1:]):
        for s in range(NEYE_S):
            floor.append(bm.faces.new([u[s], u[(s + 1) % NEYE_S],
                                       v[(s + 1) % NEYE_S], v[s]]))
    for s in range(NEYE_S):
        floor.append(bm.faces.new([rings[-1][s], rings[-1][(s + 1) % NEYE_S], cen]))
    # 口の外へ返す薄いつば＝背景/板との継ぎ目を消し、閉じた多様体にする
    out = ring(EYE_RIM_Y, R_EYE + 0.012)
    outb = ring(EYE_FLOOR_Y + EYE_SAG + 0.010, R_EYE + 0.012)
    botc = bm.verts.new((0.0, EYE_FLOOR_Y + EYE_SAG + 0.010, 0.0))
    for s in range(NEYE_S):
        wall.append(bm.faces.new([lip[s], out[s], out[(s + 1) % NEYE_S],
                                  lip[(s + 1) % NEYE_S]]))
        wall.append(bm.faces.new([out[s], outb[s], outb[(s + 1) % NEYE_S],
                                  out[(s + 1) % NEYE_S]]))
        wall.append(bm.faces.new([outb[s], botc, outb[(s + 1) % NEYE_S]]))
    fl = set(f.index if f.index >= 0 else id(f) for f in floor)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.material_index = 1 if f in floor else 0
        for lp in f.loops:
            q = lp.vert.co
            lp[uvl].uv = (min(1.0, math.hypot(q.x, q.z) / R_EYE), 0.5)
    me = bpy.data.meshes.new("eye"); bm.to_mesh(me); bm.free()
    me["_smooth"] = True
    me["_2mat"] = True
    return me


def plug_mesh(cells, eyes, name):
    """🔴 3周目の直し：**塊の輪郭は石そのものであるべき**。
       2周目までは「占有マスの和＝ポリオミノの板」を裏に置いていたが、
       板の**角が石の輪郭から 0.035m はみ出す**ので、6つの塊がぜんぶ
       角のある黒いスラブ（＝キーパッド）に見えていた。深さでは直らない（角は深さと無関係）。

       代わりに、**石の陰に完全に隠れる黒い球**で穴だけを塞ぐ：
         ・マスの中心に半径 0.086（＝石の半径と同寸）→ 石の裏に隠れる
         ・4隅が埋まっているマス目の中心に半径 0.068 → 斜めの菱形の穴だけを塞ぐ
       2つの和は塊の内側を隙間なく覆い、外へは 1px も出ない。
       球にするのは、円板だと前面が同一平面で重なって z ファイティングするため。"""
    occ = set(cells)
    # 🔴 眼のマスには球を置かない（井戸の底を球が飲み込んで**光が丸ごと消える**。3周目に踏んだ）。
    #    眼は井戸の本体（外つば r=0.0965）が自分で塞ぐので、隣の球と重なって穴は残らない。
    pts = [(uv_of(i, j), 0.086) for (i, j) in cells if (i, j) not in set(eyes)]
    for (i, j) in cells:                       # マス目（4隅が石／眼で埋まっている所）
        if (i + 1, j) in occ and (i, j + 1) in occ and (i + 1, j + 1) in occ:
            x0, z0 = uv_of(i, j)
            pts.append(((x0 + PITCH / 2, z0 + PITCH / 2), 0.068))
    bm = bmesh.new()
    NS, NR = 16, 9
    for (x, z), r in pts:
        rings = []
        for k in range(NR + 1):
            th = math.pi * k / NR
            rr = r * math.sin(th)
            yy = PLUG_Y - r * math.cos(th)
            if k in (0, NR):
                rings.append([bm.verts.new((x, yy, z))])
            else:
                rings.append([bm.verts.new((x + rr * math.cos(2 * math.pi * u / NS), yy,
                                            z + rr * math.sin(2 * math.pi * u / NS)))
                              for u in range(NS)])
        for p_, q_ in zip(rings, rings[1:]):
            if len(p_) == 1:
                for u in range(NS):
                    bm.faces.new([p_[0], q_[u], q_[(u + 1) % NS]])
            elif len(q_) == 1:
                for u in range(NS):
                    bm.faces.new([p_[u], p_[(u + 1) % NS], q_[0]])
            else:
                for u in range(NS):
                    bm.faces.new([p_[u], p_[(u + 1) % NS], q_[(u + 1) % NS], q_[u]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me["_smooth"] = True
    return me


# ---------- 配置 ----------
board = bpy.data.objects.new("board", None)
bpy.context.collection.objects.link(board)
board.location = (0.0, 0.0, Z_C)

me_stone = stone_mesh()
me_eye = eye_mesh()

parts, eyes_ob, lids = [], [], []
for gn, g in sorted(GROUPS.items()):
    cells = list(g["stones"]) + list(g["eyes"])
    pl = link(plug_mesh(cells, g["eyes"], "plug_%s" % gn), "plug_%s" % gn, mat_plate, board)
    parts.append(pl)
    lid_src = {src for src, _, _ in g["lids"]}
    for (i, j) in g["stones"]:
        if (i, j) in lid_src:
            continue
        x, z = uv_of(i, j)
        ob = link(me_stone, "stone_%s_%d_%d" % (gn, i, j), mat_stone, board)
        ob.location = (x, 0.0, z)
        parts.append(ob)
    for (i, j) in g["eyes"]:
        x, z = uv_of(i, j)
        ob = link(me_eye, "eye_%s_%d_%d" % (gn, i, j), mat_plate, board, mat_eye)
        ob.location = (x, 0.0, z)
        parts.append(ob); eyes_ob.append(ob)
    for src, dst, psi in g["lids"]:
        ob = link(me_stone, "lid_%s_%d_%d" % (gn, dst[0], dst[1]), mat_stone, board)
        parts.append(ob); lids.append((ob, src, dst, psi))

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    board.rotation_euler = (math.radians(LEAN_DEG + SWAY_X_DEG * math.sin(2 * math.pi * t)),
                            0.0,
                            math.radians(YAW_DEG + SWAY_Z_DEG * math.sin(2 * math.pi * t)))
    board.keyframe_insert("rotation_euler", frame=f + 1)
    for ob, src, dst, psi in lids:
        ob.location = lid_pos(t, src, dst, psi)
        ob.keyframe_insert("location", frame=f + 1)

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
        caption("MIDDLE STUDY 056 — GOISHI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0.0, 0.0, Z_C)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）

# 🔴 #58③：随伴のライム光源は**発光体の外**に置く。盤の手前・下に出して、
#    盤の真下の床を直接照らす。キャプション（y=-1.7）からは離す。
limelamps = []
for sx in (-0.55, 0.0, 0.55):
    bpy.ops.object.light_add(type='POINT', location=(sx, -0.62, Z_C - 1.45))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f" % sx
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
cam.data.dof.focus_object = eyes_ob[len(eyes_ob) // 2]
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

# 🔴 #63③：ライムの随伴光源は「誰に当てるか」ではなく「誰から外すか」で書く。
#    メッシュを全部入れ、キャプション（FONT）だけを外す。床1枚に絞ると相互反射の経路ごと消えて
#    床のライムが 0.02% に落ちる。
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    # 🔴 1周目：板と井戸の内壁までライムが当たり、塊が「緑に光るキーパッド」になった。
    #    外すのはこの2つだけ（#63③：外すものを最小にしないと相互反射の経路ごと消える）
    if o.type == 'MESH' and not o.name.startswith(("plug_", "eye_")):
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
    gbox = {}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name == "floor":
            continue
        ev = o.evaluated_get(dg)
        cx, cy = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y); cx.append(c.x); cy.append(c.y)
        g = o.name.split("_")[1]
        b = gbox.setdefault(g, [9, -9, 9, -9])
        b[0] = min(b[0], min(cx)); b[1] = max(b[1], max(cx))
        b[2] = min(b[2], min(cy)); b[3] = max(b[3], max(cy))
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 占有  長辺 %.1f%%（合格 44〜66・狙い55〜65）" % (max((x1 - x0), (y1 - y0)) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （どれかが 0 を割ると edge≥1）"
          % (x0, 1 - x1, 1 - y1, y0))
    names = sorted(gbox)
    worst = (9, "")
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            p, q = gbox[names[a]], gbox[names[b]]
            gx = max(p[0] - q[1], q[0] - p[1])
            gy = max(p[2] - q[3], q[2] - p[3])
            gap = max(gx, gy)
            if gap < worst[0]:
                worst = (gap, "%s-%s" % (names[a], names[b]))
    print(">> 塊どうしの投影すき間 最小 %.4f（%s）＝ 横なら %.0fpx / 縦なら %.0fpx"
          % (worst[0], worst[1], worst[0] * 1600, worst[0] * 2000))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_056.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("eye_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.75
    for c in eyes_ob:
        c.data.materials[1] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {board.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = eyes_ob[0]
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
