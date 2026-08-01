# =============================================================
# monaka design. — MIDDLE STUDY 038 "ORIZURU"（折鶴 a folded paper crane）
# 黒い紙の鶴が宙に浮く。翼を上げると胸——鶴のちょうど真ん中——がひらいて
# ライム #A5E02E が差し、翼を下ろすと光は一条の線に戻る。
# 一枚の紙は、折られてはじめて中を持つ。
#
# 【ドメイン】折紙（シリーズ未踏）。直近10作（玩具・独楽／武具・鞘／装身・櫛／
#   調度・屏風／縄・繊維／信仰・鈴／建築・灯籠／幾何・蜂の巣／植物・松毬／書・円相）と別領域。
#   37作すべてが「挽く・編む・積む・彫る」の立体だったので、シリーズ初の**折られた平面**。
#
# 【機構】剛体の2枚（＝鶴の左右）を**背の稜線（spine）まわりに開閉**する。
#   紙の鶴の実機構そのもの：胴の側面と翼は1枚の紙のL字なので、
#   胴が開けば（下端が外へ振れれば）翼は必ず**上がる**。1つの角 α が
#   「胴の開き」と「翼の高さ」を同時に決める＝**機構がそのまま光の強弱になる**
#   （034/035/036/037 で確立した美点）。
#     α(t) = A_MID + A_AMP·cos(2π·K·t)   K=2（整数周期＝t=0とt=1が厳密一致）
#   翼を上げた瞬間がいちばん開いていちばん明るい＝hero（STILL_FRAME=1）。
#
# 【光】#29 の正典どおり「開口の奥を面で満たす」＝胴の内側の中央面（x=0）に置いた
#   発光の**竜骨（keel）**。首と尾は同じ中央面に立つので、光は必ず
#   **首と尾のあいだ＝鶴の真ん中**に出る。#32 のとおり Base＝純黒・Spec=0 で、
#   胸の V 字から白背景が抜けるのを止める**裏当てを兼ねる**。
#   勾配は #34 の2軸楕円（前後 y ＋ 上下 z）。1軸だと「緑のテープ」に転ぶ。
#
# 【読み（#16/#33）】「黒い紙くず」に転ばないための署名ディテール——
#   ① 前へ折れたくちばし（鶴の顔は1秒で読める唯一の部位）② まっすぐな尾
#   ③ 翼の付け根の**折り筋**（#31-b の「一段細かい階層」＝紙に読ませる）
#   ④ 全部が平面＋鋭い稜線＝板でなく紙。
#   #33 の撤退条件（細い部材で中心を囲まない／大きな平円盤を使わない／
#   単一の塊が主役で光は隙間）を満たす。
#
# 【素材】紙（#17-b：ラフ0.56・コート0）だが、一様bright env 下の平面は
#   鏡面反射率が支配項（#17-c）なので Spec は 0.10 まで落として黒を黒に保つ。
#
# 【罠を構造的に回避】object.scale / transform_apply 不使用（#15）。
#   姿勢（yaw/pitch）は**静的な pose Empty に焼き**、その子で翼の開閉だけを
#   local Y 回転にする（#29 の2段分離）＝ matrix_parent_inverse は identity（#9）。
#   glb は必ず最後尾（#30）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_orizuru.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_orizuru")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "1.50"))   # spine（＝リグ原点）の world 高さ
LOOK_Z = float(os.environ.get("LOOK_Z", "1.62"))
CAM_LOC = (0.55, -8.3, 1.95)

# --- 鶴の寸法（crane-local：+y=頭のほう / +x=右翼 / z=上、spine が z=0） ---
SZ = float(os.environ.get("SZ", "1.12"))      # 全体の大きさ（#18：横で 55〜65%）
BF = float(os.environ.get("BF", "0.40")) * SZ      # 胴の前端（spine の前）
BB = float(os.environ.get("BB", "0.44")) * SZ      # 胴の後端
D_BODY = float(os.environ.get("D_BODY", "0.38")) * SZ  # 胴の深さ（spine から下）
W_SPAN = float(os.environ.get("W_SPAN", "0.90")) * SZ  # 片翼の張り（local x）
T_PAPER = float(os.environ.get("T_PAPER", "0.016"))   # 紙の厚み（胴・翼）
T_SPINE = float(os.environ.get("T_SPINE", "0.026"))   # 首・尾（2枚重ね）
T_KEEL = 0.012

# 翼の取り付け角。α=WING_D で翼が水平になる＝**水平は禁物**：カメラは水平から2.5°しか
# 上にないので、水平な翼は小口だけの線になって消える（6周目の f31 で発覚）。
# 逆に上げすぎると今度は**奥の翼**が小口になる（+23°で消えた）。両翼が同時に面で読める
# のは +8°〜+14° の狭い帯なので、**hero（α最大）がその帯に来るよう** WING_D=α_max−11° に取る。
WING_D = math.radians(float(os.environ.get("WING_D", "12.0")))
WING_CR = float(os.environ.get("WING_CR", "0.22"))  # 折り筋の位置（u）
WING_CZ = float(os.environ.get("WING_CZ", "0.062")) * SZ  # 折り筋の高さ

# --- 姿勢 ---
YAW = math.radians(float(os.environ.get("YAW", "142.0")))    # 180°=真正面。42°振って3/4に
PITCH = math.radians(float(os.environ.get("PITCH", "-7.0")))  # 負＝頭下げ（胸をカメラへ向ける）

# --- 運動 ---
A_MID = math.radians(float(os.environ.get("A_MID", "16.0")))
A_AMP = math.radians(float(os.environ.get("A_AMP", "7.0")))
FLAP_K = 2                                            # ループ内の羽ばたき回数（整数＝閉じる）
BOB = float(os.environ.get("BOB", "0.022"))           # 羽ばたきに同期した浮き沈み

# --- 発光（#34：長軸＋短軸の2軸／#32：暗部は純黒＝裏当てを兼ねる） ---
ES_CORE = float(os.environ.get("ES_CORE", "6.2"))
EM_Y0 = float(os.environ.get("EM_Y0", "0.16")) * SZ   # 芯の前後位置（胸寄り）
EM_Z0 = float(os.environ.get("EM_Z0", "-0.13")) * SZ  # 芯の高さ
FY_EM = float(os.environ.get("FY_EM", "0.30")) * SZ
FZ_EM = float(os.environ.get("FZ_EM", "0.24")) * SZ
GLOW_E = float(os.environ.get("GLOW_E", "1.1"))       # 胴の内側を洗うこぼれ光（#22/#32）

# --- 材質（#17-b 紙 / #17-c 一様bright env では反射率が支配項） ---
SPEC_PAPER = float(os.environ.get("SPEC_PAPER", "0.06"))
ROUGH_PAPER = float(os.environ.get("ROUGH_PAPER", "0.56"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.59")),
         float(os.environ.get("CAP_Z2", "0.41")),
         float(os.environ.get("CAP_Z3", "0.29")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ
STILL_FRAME = 1           # t=0 ＝ α 最大＝いちばん開いていちばん明るい


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 数式 ----------
def alpha_at(t01):
    """胴の開き＝翼の高さ。cos の整数周期＝厳密に閉じる。"""
    return A_MID + A_AMP * math.cos(2.0 * math.pi * FLAP_K * t01)


def bob_at(t01):
    return BOB * math.cos(2.0 * math.pi * FLAP_K * t01)


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


mat_paper, b = make_principled("orizuru_paper")     # 黒い和紙（#17-b / #17-c）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_PAPER
b.inputs["Specular IOR Level"].default_value = SPEC_PAPER
b.inputs["Coat Weight"].default_value = 0.0

# 光＝胴の中央面に立てた発光の竜骨。#32：Base は**純黒**（裏当てを兼ねる）
mat_keel, keel_bsdf = make_principled("orizuru_light")
keel_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
keel_bsdf.inputs["Emission Color"].default_value = LIME
keel_bsdf.inputs["Roughness"].default_value = 0.5
keel_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
def finish(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def add_poly(bm, pts):
    """3D点列から1枚のn-gonを張る（平面でなくてもよい）。"""
    vs = [bm.verts.new(tuple(p)) for p in pts]
    bm.faces.new(vs)
    bm.verts.index_update()
    return vs


def add_grid(bm, rows):
    """rows[i] = その行の頂点列（同じ長さ）。四角形で張る。"""
    vs = [[bm.verts.new(tuple(p)) for p in row] for row in rows]
    for i in range(len(rows) - 1):
        for j in range(len(rows[0]) - 1):
            bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    return vs


def solidify(bm, thickness):
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=thickness)


def add_bevel(o, width=0.0018):
    """#10：ANGLE 制限で鋭角の辺だけ面取り。紙の小口を立たせる。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)


def ry(p, th):
    c, s = math.cos(th), math.sin(th)
    return (p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c)


# ---------- 造形：左右の側（胴の側面＋翼＝1枚の紙のL字） ----------
def build_side(k):
    """k=+1 右／k=-1 左。ヒンジ（spine）を原点にした実寸メッシュ。"""
    bm = bmesh.new()

    # 胴の側面（spine から下へ垂れる台形。α=0 で x=0 の面）
    # 前上に**胸の切り欠き**を入れる：折鶴は首の下で紙が2枚に割れて中が見える。
    # 切り欠きが無いと開口が胴の底の小さな三角にしかならず、光が「腹の隅」に落ちる（1〜2周目）。
    # 胴は**三角の楔**（底は一点に集まる）。台形にすると hero で「黒い箱」に転ぶ（3周目・#16）。
    # 前縁は spine の 0.20BF から底の頂点へ**まっすぐ落とす**＝胸に開いた三角の窓。
    # 折れ点を持つ切り欠きにすると、前へ突き出た spur が hero で「割れたガラスの破片」に
    # 見えた（4周目）。窓の輪郭は直線1本に保つ。
    xo = k * T_PAPER * 0.5
    body = [(xo, BF * 0.34, 0.0),
            (xo, -BB, 0.0),
            (xo, 0.02, -D_BODY)]
    if k < 0:
        body = list(reversed(body))
    add_poly(bm, body)

    # 翼（u=外へ / v=前後）。付け根に折り筋（#31-b の「一段細かい階層」）を1本入れる。
    NU, NV = 16, 5
    Y_TIP_F, Y_TIP_B = -0.10, -0.34
    rows = []
    for i in range(NU + 1):
        u = i / NU
        x = 0.018 + u * (W_SPAN - 0.018)
        yf = BF * 0.98 + u * (Y_TIP_F - BF * 0.98)
        yb = -BB + u * (Y_TIP_B + BB)
        if u <= WING_CR:
            z = WING_CZ * (u / WING_CR)
        else:
            z = WING_CZ * (1.0 - 0.78 * (u - WING_CR) / (1.0 - WING_CR))
        row = []
        for j in range(NV + 1):
            v = j / NV
            p = (x, yf + (yb - yf) * v, z)
            p = ry(p, -WING_D)          # 取り付け角：α=WING_D で翼が水平になる
            row.append((k * p[0], p[1], p[2]))
        rows.append(row)
    if k < 0:
        rows = [list(reversed(r)) for r in rows]
    add_grid(bm, rows)

    solidify(bm, T_PAPER)
    o = finish("side_R" if k > 0 else "side_L", bm, mat_paper)
    add_bevel(o)
    return o


# ---------- 造形：首＋頭（中央面 x=0 の平たい刃） ----------
def blade(name, pts2d, thick, mat):
    bm = bmesh.new()
    add_poly(bm, [(-thick * 0.5, p[0], p[1]) for p in pts2d])
    solidify(bm, thick)
    o = finish(name, bm, mat)
    add_bevel(o)
    return o


def build_neck():
    # 首は急角度に立てる：4:5 ポートレートは横が先に死ぬ（#18）ので、
    # 高さは首と尾で稼ぎ、横は翼を詰める。
    R = (0.32 * SZ, -0.08 * SZ)          # 付け根の中心（胴の中）
    H = (0.72 * SZ, 0.70 * SZ)           # 頭の中心
    d = (H[0] - R[0], H[1] - R[1])
    L = math.hypot(*d)
    n = (-d[1] / L, d[0] / L)
    wr, wh = 0.090 * SZ, 0.046 * SZ
    a = (R[0] + wr * n[0], R[1] + wr * n[1])
    b = (H[0] + wh * n[0], H[1] + wh * n[1])
    b2 = (H[0] - wh * n[0], H[1] - wh * n[1])
    a2 = (R[0] - wr * n[0], R[1] - wr * n[1])
    neck = blade("neck", [a, b, b2, a2], T_SPINE, mat_paper)
    # 頭＋くちばし（前下がりに折れた三角＝鶴の顔。1秒で読ませる唯一の部位）
    head = blade("head", [b] + [(p[0] * SZ, p[1] * SZ) for p in
                                ((0.800, 0.758), (0.948, 0.646), (0.796, 0.610))] + [b2],
                 T_SPINE, mat_paper)
    return [neck, head]


def build_tail():
    T = (-0.35 * SZ, -0.06 * SZ)
    P = (-0.82 * SZ, 0.58 * SZ)
    d = (P[0] - T[0], P[1] - T[1])
    L = math.hypot(*d)
    n = (-d[1] / L, d[0] / L)
    wr, wt = 0.125 * SZ, 0.016 * SZ
    pts = [(T[0] + wr * n[0], T[1] + wr * n[1]),
           (P[0] + wt * n[0], P[1] + wt * n[1]),
           (P[0] - wt * n[0], P[1] - wt * n[1]),
           (T[0] - wr * n[0], T[1] - wr * n[1])]
    return blade("tail", pts, T_SPINE, mat_paper)


def build_keel():
    """胴の内側の中央面に立つ発光の竜骨。開口を面で満たし（#29）裏当ても兼ねる（#32）。"""
    # 輪郭は**切り欠く前の胴と同じ三角**。切り欠きから白背景が抜けない裏当てを兼ね（#32）、
    # かつ竜骨自身の縁が光の輪郭として出ない（縁では勾配が 0 に落ちている）。
    # 上端は spine より少し上に出す：z=-0.012 だと翼と胴の隙間から白背景が細い線で抜けた（3周目）。
    pts = [(BF * 0.98, 0.014),
           (-BB * 0.98, 0.014),
           (0.02, -D_BODY * 0.98)]
    bm = bmesh.new()
    add_poly(bm, [(-T_KEEL * 0.5, p[0], p[1]) for p in pts])
    solidify(bm, T_KEEL)
    o = finish("keel", bm, mat_keel)
    return o


side_R = build_side(+1)
side_L = build_side(-1)
NECK = build_neck()
tail = build_tail()
keel = build_keel()

STATIC = NECK + [tail, keel]


# ---------- リグ（#9：姿勢は静的 Empty に焼き、子は開閉だけ） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig_pose = bpy.context.active_object
rig_pose.name = "orizuru_pose"
rig_pose.rotation_euler = (PITCH, 0.0, YAW)

for o in (side_R, side_L):
    o.parent = rig_pose
    o.location = (0.0, 0.0, 0.0)      # ヒンジ＝spine＝メッシュの原点
for o in STATIC:
    o.parent = rig_pose
    o.location = (0.0, 0.0, 0.0)


# ---------- 発光の勾配（#34：長軸＋短軸の2軸楕円） ----------
# 竜骨は動かない（羽ばたくのは紙の側）ので座標は自身の Object 座標でよい（#35 の条件外）。
# 1軸だけだと「緑のテープ」（#34）に転ぶので、前後 y と上下 z の両方に落とす。
_ct = mat_keel.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Object"], _sep.inputs["Vector"])
_sq = []
for (ax, offset, falloff) in (("Y", EM_Y0, FY_EM), ("Z", EM_Z0, FZ_EM)):
    sub = _ct.nodes.new("ShaderNodeMath")
    sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = offset
    _ct.links.new(_sep.outputs[ax], sub.inputs[0])
    sc = _ct.nodes.new("ShaderNodeMath")
    sc.operation = 'MULTIPLY'
    sc.inputs[1].default_value = 1.0 / falloff
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
_mr.inputs["To Max"].default_value = 0.0      # #32：暗部は完全な黒
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'
except Exception:
    pass
_ct.links.new(_sqrt.outputs[0], _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], keel_bsdf.inputs["Emission Strength"])

# 胴の内側を洗うこぼれ光（#22：面積で稼ぎ強度で稼がない／#32：黒い紙に照り返しを作る）
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.0))
glow = bpy.context.active_object
glow.name = "orizuru_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.30
glow.parent = rig_pose
glow.location = (0.0, BF * 0.42, -D_BODY * 0.55)
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
    a = alpha_at(t)
    side_R.rotation_euler = (0.0, -a, 0.0)
    side_R.keyframe_insert(data_path="rotation_euler", frame=f)
    side_L.rotation_euler = (0.0, a, 0.0)
    side_L.keyframe_insert(data_path="rotation_euler", frame=f)
    rig_pose.location = (0.0, 0.0, CENTER_Z + bob_at(t))
    rig_pose.keyframe_insert(data_path="location", frame=f)


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
study = add_caption("MIDDLE STUDY 038 — ORIZURU", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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
    # #16/#18：レンダーで目視する前に構図を数値で当てる。
    dg = bpy.context.evaluated_depsgraph_get()
    for f in (1, N_FRAMES // 4 + 1, N_FRAMES // 2 + 1):
        scene.frame_set(f)
        dg.update()
        xs, zs, ys = [], [], []
        for o in (side_R, side_L, tail, keel) + tuple(NECK):
            ob = o.evaluated_get(dg)
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                xs.append(w.x)
                zs.append(w.z)
                ys.append(w.y)
        t = (f - 1) / N_FRAMES
        a = alpha_at(t)
        print(f">> f{f} α={math.degrees(a):.1f}° 翼={math.degrees(a - WING_D):+.1f}° "
              f"胸の開き={2 * D_BODY * math.sin(a):.3f}m  "
              f"横 {min(xs):+.2f}..{max(xs):+.2f} ({max(xs)-min(xs):.2f}/2.81="
              f"{(max(xs)-min(xs))/2.81*100:.0f}%)  "
              f"縦 {min(zs):.2f}..{max(zs):.2f} ({max(zs)-min(zs):.2f}/3.52="
              f"{(max(zs)-min(zs))/3.52*100:.0f}%)  奥行 {min(ys):+.2f}..{max(ys):+.2f}")
        print(f"   screen 縦 {screen_y(min(zs)):+.3f}..{screen_y(max(zs)):+.3f} "
              f"{'OK' if abs(screen_y(min(zs))) < 0.97 and abs(screen_y(max(zs))) < 0.97 else 'WARN 切れる'}")
    scene.frame_set(STILL_FRAME)
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    print(f">> 勾配 r=√((y-{EM_Y0})/{FY_EM})²+((z-{EM_Z0})/{FZ_EM})²  ES {ES_CORE}→0 "
          f"竜骨の端(y={BF:.2f}/z={-D_BODY:.2f})で r="
          f"{math.hypot((BF - EM_Y0) / FY_EM, (-D_BODY - EM_Z0) / FZ_EM):.2f} "
          f"{'OK（端が0に落ちる＝芯が残る #34）' if math.hypot((BF-EM_Y0)/FY_EM, (-D_BODY-EM_Z0)/FZ_EM) >= 0.95 else 'WARN 均一＝テープ化'}")
    print(f">> loop: α=A_MID+A_AMP·cos(2π·{FLAP_K}t) ＝整数周期＝t=0とt=1が厳密一致 / "
          f"{N_FRAMES}f {N_FRAMES / FPS:.3f}s")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "orizuru.blend"))
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
        for lk in list(keel_bsdf.inputs["Emission Strength"].links):
            mat_keel.node_tree.links.remove(lk)
        keel_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {side_R.name, side_L.name, rig_pose.name} | {o.name for o in STATIC}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "orizuru.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
