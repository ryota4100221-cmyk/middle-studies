# =============================================================
# monaka design. — MIDDLE STUDY 043 "MAYU"（繭 / a cocoon）
# 黒い繭が宙に浮く。糸が幾重にも架かっていて、外側は真っ黒。
# けれど、くびれ——繭のちょうど真ん中——では糸のあいだが開いていて、
# 奥からライムの光が差す。層と層がすれ違うたび、隙間は開き、また閉じる。
# まだ名前のないものが、中にいる。
#
# 【ドメイン】虫・生命／繭（シリーズ未踏）。直近10作（工芸・繕い／植物・竹／計量・秤／
#   貝・海／折紙／玩具・独楽／武具・鞘／装身・櫛／調度・屏風／縄・繊維）と別領域。
#   006 ITO は「黒い球に巻きついた**ライムの糸**」＝糸そのものが光る話。
#   043 は「**黒い糸の層**が光を包み、その隙間から漏れる」話で、主役も光の置き場も逆。
#   033 NAWA（縄）は撚り＝1本の綱の話で、こちらは層（レイヤ）の話。
#
# 【機構】シリーズ初の「**すれ違い（同巻き2層の相対ずれ）**」。
#   ・糸を6層架ける。うち **A と B は同じ本数（62）・同じ巻き角（+1.55）の対**で、
#     A は +2π/62、B は −2π/62 だけ**逆向きに**回る。同巻きなので両者の方位差は
#     **高さに依らず一定** ＝ 繭ぜんぶで**一斉に**重なり／ずれる。
#     重なれば糸は 62 本ぶんの隙間を残し、ずれれば 124 本ぶんに割れて塞がる。
#   ・1ループで相対ずれは 2ピッチ進むので、**正面は2回開いて2回閉じる**。
#     各層は自分の1ピッチぶん回って自己一致するので **t=0 と t=1 が厳密一致＝完全ループ**
#     （013/025/033 の「N-fold 対称を整数回転で自己一致」の多層版）。
#   ・残る4層（c1/c2/d/e）は巻き角のばらばらな添え糸で、交差して「絡まった糸」を作る。
#   ・回転キーだけ＝シェイプキー不要・glb にそのまま乗る・食い込みは層の半径差で構造的に無い
#     （object.scale／transform_apply 不使用 #15／リグは原点 #9）。
#   ⚠️ **逆巻き同士を回しても光の量は変わらない**（1周目の失敗）。逆巻きだと重なる高さが
#     上下に流れるだけで、見える発光面積は 98%〜100% しか動かなかった（#40⑥ 不合格）。
#     **同巻き・同本数**にして初めて「全高で一斉に開閉」になる。
#
# 【光】繭と同軸・同形の**発光シェル**を糸の内側に置く（#29：開口と同形で隙間を面で満たす。
#   中心に球を置くと「裸の緑玉」#13/#18 になる）。Base＝純黒・Spec 0（#32）。
#   勾配は #34 の2軸楕円距離を **UV に焼き込む**（#39）：u＝x/FX（画面の横＝芯を真ん中に留める）、
#   v＝(z−Z_HOT)/FZ（縦）。FZ は半高の 16% しかないので、光は**くびれの帯だけ**に居る。
#   d=1 の縁で ES が厳密に 0 に落ちるので、シェルの周縁は完全な黒＝**そのまま裏当て**。
#   この「黒い裏当て」が効きの本質で、**格子の隙間から白背景でなく黒が見える**から、
#   胴は網ではなく**糸を巻いた黒い塊**に読める（#26②/#28 の緑スピル・白抜けも同時に消える）。
#
# 【読み（#16/#33）】**5周目まで hero が「編んだラタンの照明器具」に転んでいた**。
#   黒い格子の奥に大きな発光面を置く構図は、それ自体が「行灯」の記号＝004/031 の再演。
#   効いたのは**光を全高の 45% から 16% の細い帯に絞ったこと**——胴の格子の奥が
#   黒い裏当てだけになり、開口が「明かり窓」でなくなった瞬間に照明器具の読みが消えた。
#   #33 の撤退条件も同時に満たす：①中心を"すかすかに"囲まない（胴の被覆 70〜90%）
#   ②大きな平円盤を使わない ③塊が主役で光は細い帯 ④輪郭が唯一無二。
#   くびれは**浅く**（waist/max=0.88）——深くすると「殻つきの落花生」に転ぶ（1周目）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_mayu.py -- <mode...>
#   modes: probe | bbox | test | testhero | still | anim | blend | glb  （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_mayu")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "1.98"))
LOOK_Z = float(os.environ.get("LOOK_Z", "1.70"))
CAM_LOC = (0.55, -8.3, 1.95)

# --- 繭の外形（くびれた落花生形・前後非対称 #37-d） ---
ZH = float(os.environ.get("ZH", "1.02"))        # 半高（糸の envelope）
# くびれは**浅く**（waist/max = 0.92）。1周目は 0.80 で組んで hero が完全に
# 「殻つきの落花生」に転んだ（#37-d：左右対称の卵形は果実に読める、の親戚）。
# 繭のくびれは実物でもごく浅い。深さでなく「そこだけ光る」ことで真ん中を宣言する。
PROFILE = [
    (-1.000, 0.048), (-0.955, 0.145), (-0.900, 0.232), (-0.820, 0.318),
    (-0.700, 0.398), (-0.560, 0.440), (-0.420, 0.455), (-0.280, 0.448),
    (-0.140, 0.418), (0.000, 0.400), (0.140, 0.409), (0.280, 0.430),
    (0.420, 0.440), (0.560, 0.428), (0.700, 0.393), (0.820, 0.318),
    (0.900, 0.230), (0.955, 0.142), (1.000, 0.046),
]

# --- 糸の層（6枚） ---
# A と B は**同じ巻き**（同じ本数・同じ W）。同巻きなので両者の方位差は高さに依らず一定
#   ＝ **全高で同時に**重なり／ずれる＝隙間が繭ぜんぶで一斉に開閉する。
#   逆巻き同士だと重なる高さが上下に流れるだけで、見える光の総量は変わらない（1周目の失敗）。
# C1/C2/D/E は**巻き角のばらばらな添え糸**。2〜3方向しか無いと交点が揃いすぎて
#   hero が「規則正しい菱形のローレット＝機械加工の金属／ネット」に読めた（2〜3周目）。
#   繭の糸は方向がでたらめに絡まっている。方向を6つに増やし、添え糸を細くして、
#   格子の規則性を消す（#31-b：読みは一段細かい階層が決める）。
# **本数は全て互いに素に近い別の数**にする。同数だと特定の高さで重なって被覆が落ち、
#   そこだけ籠に見える（#33①）。ずらすと重なりは方位のうなりに変わり、高さ方向に均される。
NB = int(os.environ.get("NB", "62"))              # A/B の本数（同数＝全高で一斉に開閉）
W_AB = float(os.environ.get("W_AB", "1.55"))      # A/B の巻き角（全高での方位の進み[rad]）
# 糸の半幅[m]。**開閉する対 A/B を太く、常に居る添え糸を細く**すると、「hero の開き」と
# 「閉じたときの塞がり」を別々に決められる。全部同じ幅にすると、開きを確保した瞬間に
# 閉じ側が 100%（＝真っ黒）へ振り切れる。
BW_AB = float(os.environ.get("BW_AB", "0.00723"))
BW_MOD = float(os.environ.get("BW_MOD", "0.20"))  # 糸の太りの揺らぎ（u だけの関数＝
#   全ての糸で同一なので N-fold 対称＝完全ループは壊れない）。押し出した等断面のチューブは
#   「繊維」でなく「配管」に見える。
BELT_W = float(os.environ.get("BELT_W", "0.190"))     # 帯の幅（正規化 z）
BELT_DIP_AB = float(os.environ.get("BELT_DIP_AB", "0.18"))   # 帯での A/B の細り
BELT_DIP_SUB = float(os.environ.get("BELT_DIP_SUB", "0.96"))  # 同・添え糸
RAD_MOD = float(os.environ.get("RAD_MOD", "0.0030"))  # 糸の浮き沈み[m]
BT = float(os.environ.get("BT", "0.0026"))        # 糸の半厚[m]（扁平＝巻かれた絹）
ZLIM = float(os.environ.get("ZLIM", "0.885"))     # 糸が架かる正規化 z の範囲
M_SEG = int(os.environ.get("M_SEG", "76"))        # 1本あたりの分割
NX_SEC = 8                                        # 断面の頂点数

# --- 端（糸が詰まった両端。糸の切り口を隠す） ---
CAP_ZN = float(os.environ.get("CAP_ZN", "0.855"))
CAP_EXTRA = float(os.environ.get("CAP_EXTRA", "0.037"))

# --- 発光シェル（＝光） ---
EM_OFF = float(os.environ.get("EM_OFF", "0.048"))  # 糸の内側へ引っ込める量[m]
EM_ZN = float(os.environ.get("EM_ZN", "0.880"))
FX = float(os.environ.get("FX", "0.400"))          # 短軸（画面の横）の減衰幅[m]
FZ = float(os.environ.get("FZ", "0.160"))          # 長軸（縦）の減衰幅[m]＝全高の45%
Z_HOT = float(os.environ.get("Z_HOT", "0.00"))     # 光の芯＝くびれ＝真ん中
ES_CORE = float(os.environ.get("ES_CORE", "4.6"))
D_POW = float(os.environ.get("D_POW", "1.50"))     # #38④：べきが小さいと暗い裾が中間調を沈める
GLOW_E = float(os.environ.get("GLOW_E", "0.03"))   # 糸の内側を洗うこぼれ光（#22）

# --- 材質（#17/#38①/#39-c：細い曲面＋一様bright env は反射率を落とす） ---
SPEC_BLACK = float(os.environ.get("SPEC_BLACK", "0.20"))
ROUGH_BLACK = float(os.environ.get("ROUGH_BLACK", "0.50"))

# --- 姿勢 ---
POSE_YAW = math.radians(float(os.environ.get("POSE_YAW", "0.0")))
SWAY = math.radians(float(os.environ.get("SWAY", "1.1")))
BOB = float(os.environ.get("BOB", "0.014"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.72")),
         float(os.environ.get("CAP_Z2", "0.54")),
         float(os.environ.get("CAP_Z3", "0.42")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)
TAU = 2.0 * math.pi


# ---------- 繭の輪郭（Catmull-Rom） ----------
_PZ = [p[0] for p in PROFILE]
_PR = [p[1] for p in PROFILE]


def prof_r(z):
    """z[m] → 外半径[m]。制御点の値に Catmull-Rom（区間内は線形パラメータ）。"""
    zn = max(-1.0, min(1.0, z / ZH))
    m = len(_PZ)
    i = 0
    while i < m - 2 and zn > _PZ[i + 1]:
        i += 1
    u = (zn - _PZ[i]) / (_PZ[i + 1] - _PZ[i])
    p0 = _PR[max(i - 1, 0)]
    p1 = _PR[i]
    p2 = _PR[i + 1]
    p3 = _PR[min(i + 2, m - 1)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * u
                  + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u)


def prof_dr(z, h=0.004):
    return (prof_r(z + h) - prof_r(z - h)) / (2.0 * h)


# ---------- 層の定義 ----------
# spin＝1ループで回る「自分のピッチ」の整数倍。整数なので t=0 と t=1 が厳密に自己一致。
# A(+1) と B(−1) の相対ずれは 1ループで 2ピッチ＝**正面が2回開いて2回閉じる**。
LAYERS = {
    #     本数  巻き角   半径offset  1周の自転  半幅        揺らぎ位相
    "a":  dict(n=NB, w=W_AB, off=-0.012, spin=+1, bw=BW_AB,  ph=0.0),
    "b":  dict(n=NB, w=W_AB, off=-0.003, spin=-1, bw=BW_AB,  ph=1.9),
    "c1": dict(n=67, w=-1.80, off=+0.006, spin=+1, bw=0.00274, ph=3.4),
    "c2": dict(n=53, w=-2.75, off=+0.015, spin=-1, bw=0.00320, ph=0.8),
    "d":  dict(n=44, w=+3.40, off=+0.024, spin=+1, bw=0.00362, ph=5.0),
    "e":  dict(n=71, w=-0.75, off=+0.033, spin=-1, bw=0.00300, ph=2.6),
}
LKEYS = ("a", "b", "c1", "c2", "d", "e")


def belt_thin(layer, u):
    """くびれ（＝光の帯）で糸を細らせる係数。u だけの関数＝対称は壊れない。
    **#14 の中間調を救った手**：光を細い帯に絞っても mid は #85B41C から動かなかった。
    ES も勾配のべきも効かない（#22 の「平均は動くのにコアが動かない」型）。
    正体は **光が細かい網目を透けていること**——359本の糸が帯を横切るので、
    半端に照らされた糸の縁の画素が大量に生まれ、それが数で 20〜80% 帯を占領する。
    → 帯のところだけ添え糸を細らせ、**開口を少なく大きく**する。
    実物の繭も腰のあたりが薄い（だから光が漏れる）ので、造形としても正しい。"""
    zn = -ZLIM + 2.0 * ZLIM * u
    dip = BELT_DIP_AB if layer in ("a", "b") else BELT_DIP_SUB
    return 1.0 - dip * math.exp(-(zn / BELT_W) ** 2)


def bw_at(layer, u):
    """糸の半幅。u だけの関数で揺らすので全ての糸で同一＝N-fold 対称は壊れない。"""
    L = LAYERS[layer]
    return (L["bw"] * (1.0 + BW_MOD * math.sin(3.7 * math.pi * u + L["ph"]))
            * belt_thin(layer, u))


def off_at(layer, u):
    """糸の半径オフセット。同じく u だけの関数＝対称は壊れない。
    完全に滑らかな回転体の上に等間隔で乗せると、菱形が揃いすぎて
    「ローレット加工の金属」に読める。層ごとに浮き沈みさせて面を乱す。"""
    L = LAYERS[layer]
    return L["off"] + RAD_MOD * math.sin(5.3 * math.pi * u + 2.1 * L["ph"])


def band_psi(layer, i, u):
    """糸 i の方位（メッシュ上＝回転前）。u∈[0,1] は下端→上端。"""
    L = LAYERS[layer]
    return TAU * i / L["n"] + L["w"] * u


def spin_at(layer, t):
    """層の自転角。1ループで自分の spin ピッチぶん回る＝t=0 と t=1 が厳密一致。"""
    L = LAYERS[layer]
    return L["spin"] * TAU / L["n"] * t


def band_dpsi_half(layer, z):
    """その高さで糸が占める方位の半幅[rad]（水平に切ると 1/cosθ 倍に伸びる）。"""
    L = LAYERS[layer]
    r = max(prof_r(z) + L["off"], 1e-3)
    dpsi_dz = L["w"] / (2.0 * ZLIM * ZH)
    cth = 1.0 / math.hypot(1.0, r * dpsi_dz)     # cos(糸と鉛直のなす角)
    u = (z / ZH + ZLIM) / (2.0 * ZLIM)
    return bw_at(layer, min(1.0, max(0.0, u))) / (r * cth)


def _wrap(a):
    while a > math.pi:
        a -= TAU
    while a < -math.pi:
        a += TAU
    return a


def open_area(t, nz=44, npsi=120):
    """**カメラから見える**「糸に塞がれていない発光面」の重み付き面積[cm²]。
    #40⑥ の検算（機構が光の量を変えているか）と hero フレームの選定に使う。
    レンダーを回さず純 math で解く（#31 の規律）。"""
    area = 0.0
    for iz in range(nz):
        z = -FZ + 2.0 * FZ * (iz + 0.5) / nz
        u = (z / ZH + ZLIM) / (2.0 * ZLIM)
        if not (0.0 <= u <= 1.0):
            continue
        rem = max(prof_r(z) - EM_OFF, 1e-3)
        dz = 2.0 * FZ / nz
        for ip in range(npsi):
            psi = -1.15 + 2.30 * (ip + 0.5) / npsi
            if math.cos(psi) <= 0.0:
                continue
            x = rem * math.sin(psi)
            d = math.hypot(x / FX, (z - Z_HOT) / FZ)
            if d >= 1.0:
                continue
            es = (1.0 - d) ** D_POW                    # 明るさの重み
            blocked = False
            for lay in LKEYS:
                L = LAYERS[lay]
                ph = spin_at(lay, t)
                hw = band_dpsi_half(lay, z)
                base = TAU / L["n"]
                dev = _wrap(psi - (L["w"] * u + ph))
                k = round(dev / base)
                if abs(dev - k * base) < hw:
                    blocked = True
                    break
            if blocked:
                continue
            dpsi = 2.30 / npsi
            area += es * rem * dpsi * dz * math.cos(psi)
    return area * 1e4


def _pick_still():
    best, bf = -1e9, 1
    for f in range(1, N_FRAMES + 1):
        a = open_area((f - 1) / N_FRAMES, nz=26, npsi=80)
        if a > best:
            best, bf = a, f
    return bf


STILL_FRAME = int(os.environ.get("STILL_FRAME", str(_pick_still())))


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_silk, b = make_principled("mayu_silk")        # 黒い糸
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_BLACK
b.inputs["Specular IOR Level"].default_value = SPEC_BLACK
b.inputs["Coat Weight"].default_value = 0.0

mat_cap, b = make_principled("mayu_cap")          # 詰まった両端
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.62
b.inputs["Specular IOR Level"].default_value = 0.20
b.inputs["Coat Weight"].default_value = 0.0

mat_em, em_bsdf = make_principled("mayu_em")      # 発光シェル＝光
em_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)   # #32
em_bsdf.inputs["Emission Color"].default_value = LIME
em_bsdf.inputs["Roughness"].default_value = 0.5
em_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
def finish(name, bm, mats, smooth=True, weld=True, auto=False):
    me = bpy.data.meshes.new(name)
    if weld:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.verts.index_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    for m in mats:
        o.data.materials.append(m)
    if auto:
        smooth_auto(o)
    return o


def smooth_auto(o, angle=0.60):
    """#6：5.x は shade_auto_smooth（active+selected で呼ぶ）。"""
    try:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_auto_smooth(angle=angle)
    except Exception as e:
        print(">> shade_auto_smooth skipped:", e)


def loft(bm, rings, cap=True):
    vs = [[bm.verts.new(tuple(p)) for p in r] for r in rings]
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            bm.faces.new((vs[i][j], vs[i][j2], vs[i + 1][j2], vs[i + 1][j]))
    if cap:
        bm.faces.new(vs[0][::-1])
        bm.faces.new(vs[-1])
    return vs


def _pos(layer, i, u):
    """糸 i の中心線上の点。"""
    L = LAYERS[layer]
    z = (-ZLIM + 2.0 * ZLIM * u) * ZH
    psi = band_psi(layer, i, u)
    r = prof_r(z) + off_at(layer, u)
    return Vector((r * math.sin(psi), -r * math.cos(psi), z)), psi, z


def build_layer(layer):
    """1枚の層（n 本の帯）を1メッシュに。断面は扁平な楕円＝巻かれた絹の帯。"""
    L = LAYERS[layer]
    bm = bmesh.new()
    for i in range(L["n"]):
        rings = []
        for m in range(M_SEG + 1):
            u = m / M_SEG
            c, psi, z = _pos(layer, i, u)
            # 接線（前進差分／端は片側差分）
            du = 1.0 / M_SEG
            a = _pos(layer, i, min(1.0, u + du))[0]
            bpt = _pos(layer, i, max(0.0, u - du))[0]
            T = (a - bpt)
            if T.length < 1e-9:
                T = Vector((0, 0, 1))
            T.normalize()
            # 面法線（回転体 r(z)：外向き）
            dr = prof_dr(z)
            n = Vector((math.sin(psi), -math.cos(psi), -dr))
            n.normalize()
            B = T.cross(n)
            if B.length < 1e-9:
                B = Vector((math.cos(psi), math.sin(psi), 0))
            B.normalize()
            hw = bw_at(layer, u)
            ring = []
            for k in range(NX_SEC):
                ang = TAU * k / NX_SEC
                p = c + B * (hw * math.cos(ang)) + n * (BT * math.sin(ang))
                ring.append((p.x, p.y, p.z))
            rings.append(ring)
        loft(bm, rings, cap=True)
    o = finish("mayu_%s" % layer, bm, (mat_silk,), smooth=True, weld=False, auto=True)
    return o


def build_cap(sign):
    """糸の切り口を隠す、詰まった端。回転体（極で1点に収束）。"""
    bm = bmesh.new()
    NP = 96
    NS = 22
    rings = []
    for i in range(NS + 1):
        s = i / NS
        zn = sign * (CAP_ZN + (1.0 - CAP_ZN) * s)
        z = zn * ZH
        extra = CAP_EXTRA * (1.0 - s) ** 0.7
        r = max(prof_r(z) + extra, 0.004)
        rings.append([(r * math.cos(TAU * j / NP), r * math.sin(TAU * j / NP), z)
                      for j in range(NP)])
    if sign < 0:
        rings = rings[::-1]
    loft(bm, rings, cap=True)
    o = finish("mayu_cap_%s" % ("top" if sign > 0 else "bot"), bm, (mat_cap,),
               smooth=True, weld=True, auto=True)
    return o


def build_emissive(nz=88, npsi=176):
    """繭と同軸・同形の発光シェル（#29）。UV に正規化2軸座標を焼く（#39）。
    u = x/FX（画面の横＝芯を真ん中に留める）／v = (z−Z_HOT)/FZ（縦）。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    grid = []
    for i in range(nz + 1):
        zn = -EM_ZN + 2.0 * EM_ZN * i / nz
        z = zn * ZH
        r = max(prof_r(z) - EM_OFF, 0.010)
        row = []
        for j in range(npsi):
            psi = TAU * j / npsi
            row.append(bm.verts.new((r * math.sin(psi), -r * math.cos(psi), z)))
        grid.append(row)
    pole_b = bm.verts.new((0.0, 0.0, -EM_ZN * ZH - 0.02))
    pole_t = bm.verts.new((0.0, 0.0, EM_ZN * ZH + 0.02))

    def uv_of(v):
        return (v.co.x / FX, (v.co.z - Z_HOT) / FZ)

    def face(vs):
        f = bm.faces.new(vs)
        for lo in f.loops:
            lo[uvl].uv = uv_of(lo.vert)
        return f

    for i in range(nz):
        for j in range(npsi):
            j2 = (j + 1) % npsi
            face((grid[i][j], grid[i][j2], grid[i + 1][j2], grid[i + 1][j]))
    for j in range(npsi):
        j2 = (j + 1) % npsi
        face((pole_b, grid[0][j2], grid[0][j]))
        face((pole_t, grid[nz][j], grid[nz][j2]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new("mayu_em")
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new("mayu_em", me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat_em)
    return o


LAYER_OBJ = {k: build_layer(k) for k in LKEYS}
CAP_B = build_cap(-1)
CAP_T = build_cap(+1)
EMIT = build_emissive()

PARTS = tuple(LAYER_OBJ[k] for k in LKEYS) + (CAP_B, CAP_T, EMIT)


# ---------- リグ（#9：原点に置く／matrix_parent_inverse は identity） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "mayu_pose"
rig.rotation_euler = (0.0, 0.0, POSE_YAW)

for o in PARTS:
    o.parent = rig
    o.location = (0.0, 0.0, 0.0)


# ---------- 発光の勾配（UV に焼いた正規化2軸／d=1 の縁で厳密に 0） ----------
_ct = mat_em.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["UV"], _sep.inputs["Vector"])


def _m(op, a=None, b=None, val=None):
    n = _ct.nodes.new("ShaderNodeMath")
    n.operation = op
    if a is not None:
        _ct.links.new(a, n.inputs[0])
    if b is not None:
        _ct.links.new(b, n.inputs[1])
    if val is not None:
        n.inputs[1].default_value = val
    return n.outputs[0]


_d = _m('SQRT', _m('ADD',
                   _m('MULTIPLY', _sep.outputs["X"], _sep.outputs["X"]),
                   _m('MULTIPLY', _sep.outputs["Y"], _sep.outputs["Y"])))
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 1.0
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = 0.0      # #32：暗部は完全な黒＝そのまま裏当て
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'
except Exception:
    pass
_ct.links.new(_m('POWER', _d, val=D_POW), _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], em_bsdf.inputs["Emission Strength"])

# 糸の内側を洗うこぼれ光（#22：面積で稼ぎ強度で稼がない）
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.0))
glow = bpy.context.active_object
glow.name = "mayu_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.14
glow.parent = rig
glow.location = (0.0, -0.30, 0.0)
try:
    glow.visible_camera = False
except Exception:
    pass


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    for k in LKEYS:
        LAYER_OBJ[k].rotation_euler = (0.0, 0.0, spin_at(k, t))
        LAYER_OBJ[k].keyframe_insert(data_path="rotation_euler", frame=f)
    rig.location = (0.0, 0.0, CENTER_Z + BOB * math.sin(TAU * t))
    rig.rotation_euler = (0.0, SWAY * math.sin(TAU * t), POSE_YAW)
    rig.keyframe_insert(data_path="location", frame=f)
    rig.keyframe_insert(data_path="rotation_euler", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, -0.42, CENTER_Z))
focus_null = bpy.context.active_object
focus_null.name = "focus_null"


def add_caption(body_text, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object
    tx.name = name
    tx.data.body = body_text
    tx.data.size = size
    tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, CAP_Z[0]), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, CAP_Z[1]), "logo")
study = add_caption("MIDDLE STUDY 043 — MAYU", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


# ---------- ライティング（001と同一＝シリーズの一貫性） ----------
def add_area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.size = size
    L.data.energy = energy
    L.data.color = color
    direction = Vector(target) - Vector(loc)
    L.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0, 0, CENTER_Z - 0.15)
add_area("key",  (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
add_area("rim",  (3.5, 4.0, 3.2),  3.0, 420, (0.88, 0.94, 1.0), focus)
add_area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
    bg.inputs[1].default_value = 0.55


# ---------- カメラ ----------
bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, LOOK_Z))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus_null
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam

for tx in (tagline, logo, study):
    tx.rotation_euler = cam.rotation_euler


# ---------- レンダー設定 ----------
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = True
    scene.cycles.device = 'GPU'
    print(">> Metal GPU enabled")
except Exception as e:
    print(">> GPU setup failed, using CPU:", e)

scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
    print(">> view: PBR Neutral")
except Exception:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Punchy'
    print(">> view: AgX Punchy")


# ---------- コンポジター（Bloom / PITFALL #3の新方式） ----------
def setup_bloom():
    try:
        ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out='OUTPUT',
                                socket_type='NodeSocketColor')
        rl = ng.nodes.new("CompositorNodeRLayers")
        glare = ng.nodes.new("CompositorNodeGlare")
        out = ng.nodes.new("NodeGroupOutput")
        try:
            glare.inputs["Type"].default_value = 'BLOOM'
        except Exception:
            pass
        glare.inputs["Threshold"].default_value = 1.2
        glare.inputs["Strength"].default_value = 0.35
        try:
            glare.inputs["Size"].default_value = 0.55
        except Exception:
            pass
        ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
        ng.links.new(glare.outputs["Image"], out.inputs["Image"])
        scene.compositing_node_group = ng
        scene.render.use_compositing = True
        print(">> Bloom compositor OK")
    except Exception as e:
        print(">> Bloom setup failed (render continues without):", e)


setup_bloom()


# ---------- 検算ヘルパ ----------
def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = (18.0 / 85.0) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


def cover_frac(z, t, npsi=720):
    """その高さで糸が覆っている割合（0..1）。#27①：75%前後まで葺けているか。"""
    hit = 0
    for ip in range(npsi):
        psi = -math.pi + TAU * (ip + 0.5) / npsi
        u = (z / ZH + ZLIM) / (2.0 * ZLIM)
        for lay in LKEYS:
            L = LAYERS[lay]
            dev = _wrap(psi - (L["w"] * u + spin_at(lay, t)))
            base = TAU / L["n"]
            k = round(dev / base)
            if abs(dev - k * base) < band_dpsi_half(lay, z):
                hit += 1
                break
    return hit / npsi


# ---------- 出力モード ----------
modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "probe" in modes:
    print(">> STILL_FRAME=%d  糸 %s = %d本"
          % (STILL_FRAME, "+".join("%s%d" % (k, LAYERS[k]["n"]) for k in LKEYS),
             sum(LAYERS[k]["n"] for k in LKEYS)))
    dg = bpy.context.evaluated_depsgraph_get()
    for f in (1, 31, STILL_FRAME, 91):
        scene.frame_set(f)
        dg.update()
        xs, zs_, ys = [], [], []
        for o in PARTS:
            ob = o.evaluated_get(dg)
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                xs.append(w.x)
                zs_.append(w.z)
                ys.append(w.y)
        print(f">> f{f} 横 {min(xs):+.2f}..{max(xs):+.2f} "
              f"({max(xs)-min(xs):.2f}/2.81={(max(xs)-min(xs))/2.81*100:.0f}%)  "
              f"縦 {min(zs_):.2f}..{max(zs_):.2f} "
              f"({max(zs_)-min(zs_):.2f}/3.52={(max(zs_)-min(zs_))/3.52*100:.0f}%)")
        print(f"   screen 縦 {screen_y(min(zs_)):+.3f}..{screen_y(max(zs_)):+.3f} "
              f"{'OK' if abs(screen_y(min(zs_))) < 0.97 and abs(screen_y(max(zs_))) < 0.97 else 'WARN 切れる'}")
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    print(">> 被覆率（#27①：籠にしないため 65〜90% を狙う。最小値が効く）")
    cmin, cmax = 1.0, 0.0
    for zn in (-0.70, -0.45, -0.20, 0.0, 0.20, 0.45, 0.70):
        cs = [cover_frac(zn * ZH, (f - 1) / N_FRAMES) for f in (1, 16, 31, 46, 61, 76, 91, 106)]
        cmin, cmax = min(cmin, min(cs)), max(cmax, max(cs))
        print("   zn=%+.2f  %s" % (zn, " ".join("%.0f%%" % (c * 100) for c in cs)))
    print("   最小 %.0f%% / 最大 %.0f%%  %s"
          % (cmin * 100, cmax * 100,
             "OK" if cmin >= 0.63 else "WARN 開きすぎ＝籠に見える"))
    print(">> 見える発光面積（#40⑥：75%を切る位相があること＝機構が光を変えている）")
    a_h = open_area((STILL_FRAME - 1) / N_FRAMES)
    lo = 1e9
    for f in range(1, N_FRAMES + 1, 6):
        a = open_area((f - 1) / N_FRAMES, nz=26, npsi=80)
        lo = min(lo, a)
    for f in (1, 31, STILL_FRAME, 61, 91):
        a = open_area((f - 1) / N_FRAMES)
        print("   f%-4d %6.2f cm² (%3.0f%%)" % (f, a, a / a_h * 100))
    print("   最小/hero = %.0f%%  %s"
          % (lo / a_h * 100, "OK" if lo / a_h < 0.75 else "WARN 機構が光を変えていない"))
    _omax = max(LAYERS[k]["off"] for k in LKEYS)
    print(">> 糸の外径 %.4f vs 端キャップの出っ張り %.4f : %s"
          % (_omax + BT, CAP_EXTRA, "OK 切り口は隠れる"
             if CAP_EXTRA > _omax + BT else "WARN 糸の切り口が出る"))
    _omin = min(LAYERS[k]["off"] for k in LKEYS)
    print(">> 層の半径差 %.4f vs 糸の厚み %.4f : %s"
          % (0.012, 2 * BT, "OK 層は食い込まない" if 0.012 > 2 * BT else "WARN 食い込む"))
    print(">> 最内層の内面 %.4f vs 発光シェル %.4f : %s"
          % (prof_r(0.0) + _omin - BT, prof_r(0.0) - EM_OFF,
             "OK" if prof_r(0.0) + _omin - BT > prof_r(0.0) - EM_OFF else "WARN 糸が光に刺さる"))
    _xmax = max(prof_r(z * ZH) - EM_OFF for z in (-0.4, -0.2, 0.0, 0.2, 0.4))
    _dlimb = _xmax / FX
    _es_limb = ES_CORE * max(0.0, 1.0 - (3 - 2 * min(1.0, _dlimb ** D_POW))
                             * min(1.0, _dlimb ** D_POW) ** 2)
    print(">> 発光シェルの周縁 |x|=%.3f → d=%.2f → ES=%.2f : %s"
          % (_xmax, _dlimb, _es_limb,
             "OK 周縁はほぼ純黒＝裏当て" if _es_limb < 0.35 * ES_CORE
             else "WARN 周縁が黒に落ちない（緑スピル #26②/#28）"))
    print(">> loop: %s の整数回転＝t=0とt=1が厳密一致 / %df %.3fs"
          % (" ".join("%s:%+d/%d" % (k, LAYERS[k]["spin"], LAYERS[k]["n"]) for k in LKEYS),
             N_FRAMES, N_FRAMES / FPS))

if "bbox" in modes:
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME)
    dg.update()
    for o in PARTS:
        ob = o.evaluated_get(dg)
        ws = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        print(">> %-12s x %+.3f..%+.3f  y %+.3f..%+.3f  z %+.3f..%+.3f  verts=%d"
              % (o.name, min(w.x for w in ws), max(w.x for w in ws),
                 min(w.y for w in ws), max(w.y for w in ws),
                 min(w.z for w in ws), max(w.z for w in ws), len(ob.data.vertices)))

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "mayu.blend"))
    print(">> saved .blend")

if "test" in modes:
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "testhero" in modes:
    # PITFALL #16：480pxでは「何に見えるか」が見えない。造形が固まったら hero で目視。
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test_hero") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> hero-size test done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero still done")

if "anim" in modes:
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'   # PITFALL #2
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

# 🔴 PITFALL #30：glb は Emission を定数へ潰す副作用があるので必ず最後尾に置く。
if "glb" in modes:
    try:
        for lk in list(em_bsdf.inputs["Emission Strength"].links):
            mat_em.node_tree.links.remove(lk)
        em_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {rig.name} | {o.name for o in PARTS}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "mayu.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
