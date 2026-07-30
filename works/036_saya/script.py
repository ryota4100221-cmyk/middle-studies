# =============================================================
# monaka design. — MIDDLE STUDY 036 "SAYA"（鞘 / 鯉口 the mouth of a scabbard）
# 黒い刀が宙に立つ。抜かれはしない。鯉口（こいくち＝鞘の口）がわずかに切られ、
# その一点——刀の全長のちょうど真ん中——から ライム #A5E02E が差す。
# 口が開くほど光は長く伸び、閉じれば一条の線に戻る。真ん中に、光がある。
#
# 機構: 柄側（鎺・鍔・縁・柄・頭）を +d/2、鞘側（鞘・発光刀身）を −d/2 と
#   対称にずらして重心＝光の帯の中心を画面に固定する。
#   d(t) = DMIN + (DMAX−DMIN)·0.5(1−cos2πt) は cos なので t=0 と t=1 が厳密一致＝完全ループ。
#   露出する刀身の長さがそのまま d ＝ **機構がそのまま光の強弱になる**（034/035 で確立した美点）。
#   ※ 発光刀身は「鞘側」に属させる。こうすると発光の勾配が常に鯉口に固定され、
#     「鞘の口から光が湧く」に読める（物理的には刀身は柄と動くが、絵はこちらが正しい）。
#     鎺（はばき）が帯の上端を黒く額装するので、DMIN では一条の細い線だけが残る。
#   反り（sori）は z=0（＝鯉口）を頂点とする放物線。頂点なので接線が垂直＝
#   ローカル z へ平行移動しても口で折れない（誤差 d²/8R ≒ 1mm）。
#   造形は #15 のとおり実寸で頂点を作り object.scale / transform_apply 不使用。
#   リグは Empty ひとつ（#9：matrix_parent_inverse は既定の identity のまま）。
#
# 光: #29 の正典どおり「開口（鯉口）と同軸・同形の発光プリズム」＝刀身断面そのもの。
#   中心に球を置く案（裸の緑玉 #13/#18）ではなく、口を面で満たす。
#   Emission は #27 の1次元バンドグラデ（Generated Z）：鯉口の直上をホットコアに
#   白飛びさせ、上へ向かって暗部→0 に落とす。#31-d のとおり**バンドを短く**保つ
#   （長く引き回すと暗いライム画素が中間調を沈める）。ES=0 の領域は完全な黒＝
#   スラブ自身が裏当てを兼ねる（#32：Base＝純黒・Spec=0。随伴点光源に拡散照明されて
#   ペンキ化するのを防ぐ）。
#
# 読み（#16/#31-b）: 「黒い棒」に転ばないための署名ディテール——
#   ① 鍔（つば）＝1秒で刀と分かる最強の記号 ② 柄の菱巻＝断面半径を交差する2本の
#   帯で変調して作る「一段細かい階層」 ③ 反り ④ 鐺（こじり）の丸め＋鎺・縁・頭の
#   金具（#31-c：意味を持つ端は細らせず留め具で締める）。
#
# 素材: 鞘＝黒漆の曲面（#17）／柄巻＝布はマット（#17-b）／金具＝低反射の鉄（#17-c）。
#   一様bright env 下では鏡面反射率が支配項なので Spec を低く保って黒を黒に。
#
# 実行:
#   Blender --background --factory-startup --python monaka_saya.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
#   env: ES_CORE W_EM Z_HOT GLOW_E DMAX DMIN CENTER_Z LOOK_Z LEAN SORI_A WRAP_A TESTFRAME
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_saya")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "2.50"))   # 鯉口（＝光）の world 高さ
LOOK_Z = float(os.environ.get("LOOK_Z", "2.14"))       # カメラ注視点（#29：縦長モチーフは分離）
CAM_LOC = (0.55, -8.3, 1.95)
LEAN = math.radians(float(os.environ.get("LEAN", "7.0")))  # #18：空いている右へ倒す

# --- 反り（z=0 ＝鯉口 を頂点とする放物線。全パーツ共通の芯線） ---
SORI_A = float(os.environ.get("SORI_A", "0.170"))
SORI_H = 1.55

# --- 鞘 ---
L_SAYA = float(os.environ.get("L_SAYA", "1.36"))
W_MOUTH, D_MOUTH = 0.112, 0.048      # 鯉口の身幅・厚み
W_KOJ, D_KOJ = 0.096, 0.041          # 鐺（こじり）側
R_END = 0.042                        # 鐺の丸め（#31-c：端は留め具/丸めで締める）
COL_H, COL_K = 0.055, 0.075          # 鯉口の襟（口金）

# --- 刀身（＝発光スラブ／#29） ---
W_HA, D_HA = 0.086, 0.024
HA_ZB, HA_ZT = -0.14, 0.42           # 下は鞘の中・上は柄の中に隠れる

# --- 金具・柄 ---
HAB_Z0, HAB_Z1 = -0.055, 0.0         # 鎺（はばき）＝光の帯の上端を額装する
W_HAB0, D_HAB0 = 0.104, 0.040
W_HAB1, D_HAB1 = 0.100, 0.036
TSU_Z0, TSU_Z1 = 0.0, 0.036          # 鍔
R_TSUBA = float(os.environ.get("R_TSUBA", "0.136"))
FU_Z0, FU_Z1 = 0.036, 0.082          # 縁
W_FU, D_FU = 0.112, 0.062
TK_Z0, TK_Z1 = 0.082, 0.592          # 柄
W_T0, D_T0 = 0.106, 0.058
W_T1, D_T1 = 0.098, 0.053
KA_Z0, KA_Z1 = 0.592, 0.630          # 頭
W_KA, D_KA = 0.108, 0.060

# 菱巻（#31-b：一段細かい階層。交差する2本の帯で断面半径を変調）
WRAP_A = float(os.environ.get("WRAP_A", "0.0040"))
WRAP_KZ = 16.0                        # 単位 z あたりの巻き数
WRAP_PW = 0.21                        # 帯の幅（周期に対する半幅）

# --- 抜き（d の呼吸） ---
DMIN = float(os.environ.get("DMIN", "0.075"))
DMAX = float(os.environ.get("DMAX", "0.300"))

# --- 発光（#27 の1次元バンド／#31-d バンドは短く） ---
ES_CORE = float(os.environ.get("ES_CORE", "9.0"))
ES_RIM = float(os.environ.get("ES_RIM", "0.0"))       # #32：暗部は完全な黒＝裏当てになる
Z_HOT = float(os.environ.get("Z_HOT", "0.035"))       # ホットコア＝鯉口の直上
W_EM = float(os.environ.get("W_EM", "0.200"))         # そこから ES=0 までの距離（縦）
FX_EM = float(os.environ.get("FX_EM", "0.044"))       # 同（横）＝刃の縁で 0 に落として芯を残す
GLOW_E = float(os.environ.get("GLOW_E", "0.7"))       # 金具・鞘へこぼれる光（#22）

# --- 材質（#17 / #17-b / #17-c） ---
SPEC_SAYA = float(os.environ.get("SPEC_SAYA", "0.11"))
ROUGH_SAYA = 0.36
SPEC_MET = 0.11
ROUGH_MET = 0.40
SPEC_WRAP = 0.07
ROUGH_WRAP = 0.55

CAP_Z = (float(os.environ.get("CAP_Z1", "1.03")),
         float(os.environ.get("CAP_Z2", "0.85")),
         float(os.environ.get("CAP_Z3", "0.73")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ
STILL_FRAME = 61          # t=0.5 ＝ d=DMAX（いちばん開いた一枚）


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 数式 ----------
def d_at(t01):
    """鯉口の開き。cos なので t=0 と t=1 が厳密に一致＝数学的に閉じる。"""
    return DMIN + (DMAX - DMIN) * 0.5 * (1.0 - math.cos(2 * math.pi * t01))


def sori(z):
    """反り。z=0（鯉口）が頂点＝接線が垂直なので、ローカル z の平行移動で口が折れない。"""
    return SORI_A * (1.0 - (z / SORI_H) ** 2)


def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = math.tan(math.atan(18.0 / 85.0)) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_saya, b = make_principled("saya_lacquer")      # 鞘＝黒漆の曲面（#17）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_SAYA
b.inputs["Specular IOR Level"].default_value = SPEC_SAYA
b.inputs["Coat Weight"].default_value = 0.0   # #17-c：一様bright env では Coat が黒を灰にする

mat_met, b = make_principled("saya_fittings")      # 鍔・鎺・縁・頭＝鉄（#17-c 低反射）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_MET
b.inputs["Specular IOR Level"].default_value = SPEC_MET
b.inputs["Coat Weight"].default_value = 0.0

mat_wrap, b = make_principled("saya_wrap")         # 柄巻＝布はマット（#17-b）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_WRAP
b.inputs["Specular IOR Level"].default_value = SPEC_WRAP
b.inputs["Coat Weight"].default_value = 0.0

# 光＝鯉口と同軸・同形の発光プリズム。#13 純発光体／#32 Base は**純黒**
mat_core, core_bsdf = make_principled("saya_light")
core_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る） ----------
def mesh_object(name, verts, faces, mats):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [list(f) for f in faces])
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    for m in mats:
        o.data.materials.append(m)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return o


def add_bevel(o, width=0.0022):
    """#10：ANGLE 制限で鋭角の辺だけ面取り。#17-c の「縁だけフレネルで立つ」を効かせる。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)


def smooth(o):
    for ob in bpy.data.objects:
        ob.select_set(False)
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)   # PITFALL #6
    except Exception:
        pass


def section(cx, w, dpt, n, e=2.0, bumps=None):
    """超楕円の閉じた断面。bumps(i) があれば半径方向に加算（＝菱巻の変調）。"""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ca, sa = math.cos(a), math.sin(a)
        px = math.copysign(abs(ca) ** (2.0 / e), ca)
        py = math.copysign(abs(sa) ** (2.0 / e), sa)
        bp = 0.0 if bumps is None else bumps(i)
        pts.append((cx + (w / 2 + bp) * px, (dpt / 2 + bp) * py))
    return pts


def loft(name, secs, mat, cap_b=True, cap_t=True):
    """同じ頂点数の断面列を積んで閉じたソリッドにする。"""
    n = len(secs[0][1])
    m = len(secs)
    verts = [(x, y, z) for (z, pts) in secs for (x, y) in pts]
    faces = []
    for k in range(m - 1):
        for j in range(n):
            j2 = (j + 1) % n
            faces.append([k * n + j, k * n + j2, (k + 1) * n + j2, (k + 1) * n + j])
    if cap_b:
        faces.append(list(range(n - 1, -1, -1)))
    if cap_t:
        faces.append(list(range((m - 1) * n, m * n)))
    return mesh_object(name, verts, faces, [mat])


# ---------- 鞘 ----------
def saya_wh(z):
    u = (z + L_SAYA) / L_SAYA               # 0 = 鐺 / 1 = 鯉口
    w = W_KOJ + (W_MOUTH - W_KOJ) * u
    d = D_KOJ + (D_MOUTH - D_KOJ) * u
    s = 1.0
    r = z + L_SAYA
    if r < R_END:                            # 鐺の丸め
        s *= 0.04 + 0.96 * math.sqrt(max(0.0, 1.0 - ((R_END - r) / R_END) ** 2))
    if z > -COL_H:                           # 鯉口の襟（口金）
        s *= 1.0 + COL_K * (1.0 - (-z / COL_H)) ** 0.6
    return w * s, d * s


def build_saya():
    n, m = 40, 160
    secs = []
    for k in range(m + 1):
        z = -L_SAYA + L_SAYA * (k / m)
        w, d = saya_wh(z)
        secs.append((z, section(sori(z), w, d, n, e=2.9)))
    o = loft("saya_body", secs, mat_saya)
    smooth(o)
    return o


# ---------- 刀身（＝発光スラブ／#29） ----------
def build_ha():
    n = 24
    secs = []
    for z in (HA_ZB, HA_ZB + 0.02, HA_ZT - 0.02, HA_ZT):
        secs.append((z, section(sori(z), W_HA, D_HA, n, e=2.4)))
    o = loft("saya_light", secs, mat_core)
    smooth(o)
    return o


# ---------- 金具・柄 ----------
def build_habaki():
    n = 28
    secs = [(HAB_Z0, section(sori(HAB_Z0), W_HAB0, D_HAB0, n, e=2.6)),
            (HAB_Z1, section(sori(HAB_Z1), W_HAB1, D_HAB1, n, e=2.6))]
    o = loft("saya_habaki", secs, mat_met)
    add_bevel(o, 0.0018)
    return o


def build_tsuba():
    n = 64
    secs = []
    for (z, rs) in ((TSU_Z0, 0.90), (TSU_Z0 + 0.008, 1.0),
                    (TSU_Z1 - 0.008, 1.0), (TSU_Z1, 0.90)):
        secs.append((z, section(sori(z), 2 * R_TSUBA * rs, 2 * R_TSUBA * rs, n, e=2.0)))
    o = loft("saya_tsuba", secs, mat_met)
    add_bevel(o, 0.0022)
    smooth(o)
    return o


def build_fuchi():
    n = 28
    secs = [(FU_Z0, section(sori(FU_Z0), W_FU, D_FU, n, e=2.6)),
            (FU_Z1, section(sori(FU_Z1), W_FU * 0.98, D_FU * 0.98, n, e=2.6))]
    o = loft("saya_fuchi", secs, mat_met)
    add_bevel(o, 0.0018)
    return o


def _pulse(u):
    v = (u - 0.5) / WRAP_PW
    return max(0.0, 1.0 - v * v) ** 1.5


def build_tsuka():
    """柄。断面半径を交差する2本の帯で変調＝菱巻（#31-b の一段細かい階層）。"""
    n, m = 48, 184
    secs = []
    for k in range(m + 1):
        u = k / m
        z = TK_Z0 + (TK_Z1 - TK_Z0) * u
        w = W_T0 + (W_T1 - W_T0) * u
        d = D_T0 + (D_T1 - D_T0) * u

        def bumps(i, z=z):
            phi = i / n
            # 方位の係数 2 ＝ 帯を斜めに立てる（1 では鉢巻きのような「輪」に見えた）
            return WRAP_A * max(_pulse((WRAP_KZ * z + 2.0 * phi) % 1.0),
                                _pulse((WRAP_KZ * z - 2.0 * phi) % 1.0))
        secs.append((z, section(sori(z), w, d, n, e=2.8, bumps=bumps)))
    o = loft("saya_tsuka", secs, mat_wrap)
    smooth(o)
    return o


def build_kashira():
    n = 28
    secs = []
    steps = ((KA_Z0, 1.0), (KA_Z1 - 0.014, 1.0), (KA_Z1 - 0.005, 0.86), (KA_Z1, 0.55))
    for (z, rs) in steps:
        secs.append((z, section(sori(z), W_KA * rs, D_KA * rs, n, e=2.6)))
    o = loft("saya_kashira", secs, mat_met)
    smooth(o)
    return o


saya = build_saya()
ha = build_ha()
habaki = build_habaki()
tsuba = build_tsuba()
fuchi = build_fuchi()
tsuka = build_tsuka()
kashira = build_kashira()

SAYA_SIDE = [saya, ha]                              # −d/2（鞘＋光）
TSUKA_SIDE = [habaki, tsuba, fuchi, tsuka, kashira]  # +d/2（柄側）

# ---------- リグ（#9：Empty ひとつ・matrix_parent_inverse は既定の identity） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "saya_rig"
rig.rotation_euler = (0.0, LEAN, 0.0)
for o in SAYA_SIDE + TSUKA_SIDE:
    o.parent = rig
    o.location = (0.0, 0.0, 0.0)


# ---------- 発光の勾配（#27 の1次元バンドを2軸に＝楕円の紡錘） ----------
# 1周目の失敗：縦（Generated Z）だけに勾配を付けたら、**横方向が完全に均一**になり
# hero で「緑のテープ」＝#24 のペンキ signature に転んだ。刃の**幅方向にも**落として
# 中央に白飛びの芯を残す（＝刃の中を光の芯が通っているように読ませる）。
_ct = mat_core.node_tree
_span = HA_ZT - HA_ZB
_gz_hot = (Z_HOT - HA_ZB) / _span
_axes = (("X", 0.5, W_HA / 2.0, FX_EM),      # 横：Generated 半幅 0.5 ↔ 実寸 W_HA/2
         ("Z", _gz_hot, _span / 2.0, W_EM))  # 縦：ホットコアは鯉口の直上

_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
_sq = []
for (ax, ctr, half_m, falloff) in _axes:
    sub = _ct.nodes.new("ShaderNodeMath")
    sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = ctr
    _ct.links.new(_sep.outputs[ax], sub.inputs[0])
    sc = _ct.nodes.new("ShaderNodeMath")
    sc.operation = 'MULTIPLY'
    sc.inputs[1].default_value = (half_m / 0.5) / falloff   # Generated → 実寸 → 正規化
    _ct.links.new(sub.outputs[0], sc.inputs[0])
    m2 = _ct.nodes.new("ShaderNodeMath")
    m2.operation = 'MULTIPLY'
    _ct.links.new(sc.outputs[0], m2.inputs[0])
    _ct.links.new(sc.outputs[0], m2.inputs[1])
    _sq.append(m2)
_add = _ct.nodes.new("ShaderNodeMath")
_add.operation = 'ADD'
_ct.links.new(_sq[0].outputs[0], _add.inputs[0])
_ct.links.new(_sq[1].outputs[0], _add.inputs[1])
_sqrt = _ct.nodes.new("ShaderNodeMath")
_sqrt.operation = 'SQRT'
_ct.links.new(_add.outputs[0], _sqrt.inputs[0])
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 1.0
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'   # 端の境界を柔らかく（線形だと縁が立つ＝#24）
except Exception:
    pass
_ct.links.new(_sqrt.outputs[0], _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], core_bsdf.inputs["Emission Strength"])

# 鯉口からこぼれる光（#22：面積で稼ぎ強度で稼がない／発光体の内部に埋めない #29）
bpy.ops.object.light_add(type='POINT',
                         location=(sori(0.0), -0.075, CENTER_Z + 0.03))
glow = bpy.context.active_object
glow.name = "saya_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.4
try:
    glow.visible_camera = False
except Exception:
    pass


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    d = d_at((f - 1) / N_FRAMES)
    for o in SAYA_SIDE:
        o.location = (0.0, 0.0, -d / 2)
        o.keyframe_insert(data_path="location", frame=f)
    for o in TSUKA_SIDE:
        o.location = (0.0, 0.0, d / 2)
        o.keyframe_insert(data_path="location", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
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
study = add_caption("MIDDLE STUDY 036 — SAYA", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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


focus = (0, 0, CENTER_Z)
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


# ---------- 出力モード ----------
modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "probe" in modes:
    # #16/#18：レンダーで目視する前に幾何を数値で当てる。
    for tag, d in (("閉 d=DMIN", DMIN), ("開 d=DMAX", DMAX)):
        bot = CENTER_Z - L_SAYA - d / 2
        top = CENTER_Z + KA_Z1 + d / 2
        print(f">> {tag}={d:.3f}  world z {bot:.3f}..{top:.3f}  "
              f"高さ={top - bot:.3f}/3.52 ({(top - bot) / 3.52 * 100:.0f}%)  "
              f"screen {screen_y(bot):+.3f}..{screen_y(top):+.3f} "
              f"({'OK' if abs(screen_y(bot)) < 0.97 and abs(screen_y(top)) < 0.97 else 'WARN 切れる'})")
        exposed = d - (HAB_Z1 - HAB_Z0)
        print(f"   露出する光の帯 = {max(0.0, exposed):.4f}m（鎺 {HAB_Z1 - HAB_Z0:.3f} が上端を額装）")
    w_all = 2 * R_TSUBA + 2 * (L_SAYA + KA_Z1) / 2 * math.sin(LEAN)
    print(f">> 横幅 ≒ {w_all:.3f}/2.81 ({w_all / 2.81 * 100:.0f}%)  "
          f"反り深さ ≒ {SORI_A * (1 - ((L_SAYA - KA_Z1) / 2 / SORI_H) ** 2) * 0.34:.4f}m")
    print(f">> 光の帯の中心 world z={CENTER_Z + Z_HOT:.3f} → screen "
          f"{screen_y(CENTER_Z + Z_HOT - DMAX / 2):+.3f}（0 が画面中央）")
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    print(f">> 刀 bottom(screen {screen_y(CENTER_Z - L_SAYA - DMAX / 2):+.3f}) vs "
          f"caption1(screen {screen_y(CAP_Z[0], -1.3):+.3f}) "
          f"{'OK' if screen_y(CENTER_Z - L_SAYA - DMAX / 2) > screen_y(CAP_Z[0], -1.3) + 0.03 else 'WARN 重なる'}")
    print(f">> 刀身スラブ z {HA_ZB:.2f}..{HA_ZT:.2f}  hot@{Z_HOT:.3f} (gz {_gz_hot:.3f})  "
          f"ES {ES_CORE}→{ES_RIM} が {W_EM:.3f}m で 0  "
          f"→ 帯は z {Z_HOT - W_EM:.3f}..{Z_HOT + W_EM:.3f} のみ（#31-d）")
    print(f">> 隠蔽: スラブ上端 {HA_ZT - DMAX / 2:.3f} < 柄上端 {KA_Z1 + DMAX / 2:.3f} "
          f"{'OK' if HA_ZT - DMAX / 2 < TK_Z1 + DMAX / 2 else 'WARN 露出'} / "
          f"スラブ下端 {HA_ZB - DMAX / 2:.3f} > 鞘下端 {-L_SAYA - DMAX / 2:.3f} OK")
    print(f">> 断面: 刀身 {W_HA:.3f}x{D_HA:.3f} ⊂ 鞘口 {W_MOUTH:.3f}x{D_MOUTH:.3f} "
          f"⊂ 柄 {W_T0:.3f}x{D_T0:.3f} "
          f"{'OK' if W_HA < W_MOUTH and W_HA < W_T0 and D_HA < D_MOUTH else 'WARN 貫通'}")
    print(f">> loop: d(t)=DMIN+(DMAX-DMIN)*0.5(1-cos2pi t) ＝ t=0/t=1 厳密一致 / "
          f"{N_FRAMES}f {N_FRAMES / FPS:.3f}s")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "saya.blend"))
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
        for lk in list(core_bsdf.inputs["Emission Strength"].links):
            mat_core.node_tree.links.remove(lk)
        core_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {o.name for o in SAYA_SIDE + TSUKA_SIDE}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "saya.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
