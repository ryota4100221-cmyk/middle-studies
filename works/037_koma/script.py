# =============================================================
# monaka design. — MIDDLE STUDY 037 "KOMA"（独楽 / 唐独楽 a spinning top）
# 黒い独楽が宙で回る。胴は上下に分かれていて、その一線——独楽のちょうど真ん中、
# 回転の軸が通るところ——だけが ライム #A5E02E に光る。
# 独楽は傾いたまま、ゆっくりと首を回す（歳差）。けれど光は真ん中から動かない。
# 回れるのは、真ん中に芯があるから。
#
# 【ドメイン】玩具・遊戯（シリーズ未踏）。直近10作（武具・鞘／装身・櫛／調度・屏風／
#   縄・繊維／信仰・鈴／建築・灯籠／幾何・蜂の巣／植物・松毬／書・円相／光学・絞り）と別領域。
#
# 【機構（シリーズ初）】**歳差（precession）＋章動（nutation）**。
#   これまでの機構は「開閉」「回転対称の整数回転」「反転」「伸縮」だった。
#   ここでは剛体が**傾いたまま軸のまわりを首振りする**——コマが実際にやる運動。
#     precession ψ(t) = 2π·t            （1周／ループ＝厳密に閉じる）
#     nutation   β(t) = B0 + BA·cos(2π·3t) （cos・整数周期＝厳密に閉じる）
#     spin       φ(t) = 2π·N_SPIN·t     （整数回転＝厳密に閉じる／回転体なので絵には出ないが glb に乗る）
#   軸 n(ψ,β) = (sinψ·sinβ, −cosψ·sinβ, cosβ)。
#
# 【機構がそのまま光の強弱になる】（034/035/036 で確立した美点をこの機構で満たす）
#   赤道のスリットは**ルーバー**なので、視線がスリット面と平行に近いほど奥まで見える。
#   歳差で軸が振れると視線とスリット面のなす角 θ が 2.5°〜15.6° を往復し、
#   覗ける発光ドラムの高さ = GAP − E_OVER·tanθ が呼吸する＝光が静かに満ち引きする。
#   ψ=π/2（横へ傾く）で θ 最小＝最も明るく、かつ**傾きが画面内で最大に見える**——
#   最も明るい瞬間と最もコマらしい瞬間が一致するので、そこを hero にする（STILL_FRAME=31）。
#
# 【光】#29 の正典どおり「開口と同軸・同形の発光体で開口を面で満たす」＝赤道スリットと
#   同軸の発光ドラム（円筒）。中心に球を置く案（裸の緑玉 #13/#18）は採らない。
#   ドラムは #32 のとおり Base＝純黒・Spec=0 で、スリットの向こうの白背景を止める
#   **裏当てを兼ねる**（これが無いと近側スリット→遠側スリット→白背景が抜ける）。
#
#   ★ 新しい罠と対処（#35 として PITFALLS に追記）：
#   **周方向スリットの奥の発光体に object 座標の勾配を焼くと、勾配が本体と共回りする。**
#   しかも円筒の生 emission は view 非依存（#25b）なので、横方向は完全に均一＝
#   「黒いコマに緑のテープを巻いた」＝#24 のペンキ signature に必ず転ぶ。
#   → 勾配の座標を**回転しない参照 Empty の Object 座標**に取り、
#     r = √((x/FX)² + (z/FZ)²) の2軸楕円（#34）で MapRange。
#     こうすると芯は常に画面の真ん中に固定され、帯は中央が白く飛び、
#     左右の端と帯の上下で純黒に落ちる＝「白い芯→#A5E02E→暗部」の勾配ができる。
#     副産物として「コマは揺れるが、光は真ん中から動かない」という主題が立つ
#     （034 の光の筋・035 の光の窓と同じ）。
#
# 【読み（#16/#31-b/#33）】「黒いスツール／ランプ」に転ばないための署名ディテール——
#   ① 先端の鋭い錐（コマは点で立つ）② 心棒（軸）＝縦のアクセント ③ 傾いた姿勢
#   ④ 轆轤挽きの同心の削り筋（#31-b の「一段細かい階層」＝木を挽いた玩具に読ませる）。
#   #33 の撤退条件（囲まない／大きな平円盤を使わない／単一の塊が主役で光は隙間）を満たす。
#
# 【素材】轆轤挽きの黒漆。曲面主体なので #17（ラフ0.34系）だが、一様bright env 下では
#   鏡面反射率が支配項（#17-c）なので Spec は 0.12 まで落として黒を黒に保つ。
#
# 実行:
#   Blender --background --factory-startup --python monaka_koma.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
#   env: ES_CORE FX_EM FZ_EM GLOW_E B0 BA GAP E_OVER R_MAX CENTER_Z LOOK_Z TESTFRAME
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_koma")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "1.62"))   # 赤道スリット（＝光）の world 高さ
LOOK_Z = float(os.environ.get("LOOK_Z", "1.62"))       # カメラ注視点
CAM_LOC = (0.55, -8.3, 1.95)

# --- 独楽の寸法 ---
R_MAX = float(os.environ.get("R_MAX", "0.760"))        # 赤道の半径
GAP = float(os.environ.get("GAP", "0.075"))            # 赤道スリットの高さ
E_OVER = float(os.environ.get("E_OVER", "0.055"))      # 鍔の張り出し（＝ルーバーの深さ）
R_CORE = R_MAX - E_OVER                                # 発光ドラムの半径

Z_LOW_TOP = 0.657                                      # 下半身の上端（スリット下縁）
Z_UP_BOT = Z_LOW_TOP + GAP                             # 上半身の下端（スリット上縁）
Z_EQ = (Z_LOW_TOP + Z_UP_BOT) * 0.5                    # スリット中心（tip からの高さ）

# 轆轤の削り筋（#31-b：一段細かい階層）
# 2周目：ピッチ0.052・深さ0.0062 は hero で「ネジ山／黒ゴム」に見えた。
# 細く浅くして「木を挽いた跡」に落とす（#34-b：繰り返しは"向き"と"細かさ"で読みが変わる）。
GRV_P = float(os.environ.get("GRV_P", "0.030"))        # 筋のピッチ（z）
GRV_A = float(os.environ.get("GRV_A", "0.0028"))       # 筋の深さ
GRV_W = 0.30                                           # 筋の半幅（周期に対する比）
UP_SQ = float(os.environ.get("UP_SQ", "0.85"))         # 上半身（ドーム）の扁平率

# --- 運動 ---
B0 = math.radians(float(os.environ.get("B0", "13.0")))   # 章動の中心（傾き）
BA = math.radians(float(os.environ.get("BA", "2.5")))    # 章動の振幅
NUT_K = 3                                                # 歳差1周あたりの首振り回数（整数＝閉じる）
N_SPIN = 7                                               # 歳差1周あたりの自転数（整数＝閉じる）

# --- 発光（#34：長軸＋短軸の2軸／#35：回転しない参照座標） ---
ES_CORE = float(os.environ.get("ES_CORE", "6.0"))      # hero実測で決定（#14／12.0はコアが飛んだ）
ES_RIM = float(os.environ.get("ES_RIM", "0.0"))        # #32：暗部は完全な黒＝裏当てを兼ねる
FX_EM = float(os.environ.get("FX_EM", "0.700"))        # 横：ドラムの縁で 0 に落として芯を残す
FZ_EM = float(os.environ.get("FZ_EM", "0.055"))        # 縦：帯の中でも芯→暗の勾配を作る
GLOW_E = float(os.environ.get("GLOW_E", "0.7"))        # 隙間からこぼれる光（#22）

# --- 材質（#17 曲面 / #17-c 一様bright env では反射率が支配項） ---
# 2周目 Spec0.12/Rough0.38 は hero の黒が #1A1B17（灰）。曲面＋削り筋が env を線状に
# 拾うので、質感でなく**鏡面反射率**を落とす（#17-c）。
SPEC_BODY = float(os.environ.get("SPEC_BODY", "0.045"))
ROUGH_BODY = float(os.environ.get("ROUGH_BODY", "0.50"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.59")),
         float(os.environ.get("CAP_Z2", "0.41")),
         float(os.environ.get("CAP_Z3", "0.29")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ
STILL_FRAME = 31          # t=0.25 ＝ ψ=π/2（横へ傾く＝最も明るく・最もコマらしい）


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 数式 ----------
def psi_at(t01):
    """歳差。1周／ループ＝t=0 と t=1 が厳密一致。"""
    return 2.0 * math.pi * t01


def beta_at(t01):
    """章動。cos の整数周期＝厳密に閉じる。"""
    return B0 + BA * math.cos(2.0 * math.pi * NUT_K * t01)


def spin_at(t01):
    """自転。整数回転＝厳密に閉じる。"""
    return 2.0 * math.pi * N_SPIN * t01


def axis_at(t01):
    """独楽の軸（world）。n = Rz(ψ)·Rx(β)·ẑ"""
    ps, be = psi_at(t01), beta_at(t01)
    return Vector((math.sin(ps) * math.sin(be),
                   -math.cos(ps) * math.sin(be),
                   math.cos(be)))


def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = math.tan(math.atan(18.0 / 85.0)) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


Z_TIP = CENTER_Z - Z_EQ * math.cos(B0)   # 錐先の world 高さ（宙に浮く）


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_body, b = make_principled("koma_lacquer")      # 轆轤挽きの黒漆（#17 / #17-c）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_BODY
b.inputs["Specular IOR Level"].default_value = SPEC_BODY
b.inputs["Coat Weight"].default_value = 0.0

# 光＝スリットと同軸・同形の発光ドラム。#13 純発光体／#32 Base は**純黒**（裏当てを兼ねる）
mat_core, core_bsdf = make_principled("koma_light")
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


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
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


def catmull_rom(pts, steps=40):
    """制御点を Catmull-Rom で密にサンプル（#023：低ポリの面取りシルエットを消す）。"""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in range(steps):
            u = s / steps
            u2, u3 = u * u, u * u * u
            c = []
            for k in (0, 1):
                c.append(0.5 * ((2 * p1[k]) +
                                (-p0[k] + p2[k]) * u +
                                (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u2 +
                                (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u3))
            out.append((c[0], c[1]))
    out.append(pts[-1])
    return out


def groove(z, r):
    """轆轤の削り筋（#31-b）。半径の小さい所（錐先・心棒）には入れない。"""
    if r < 0.17:
        return 0.0
    ph = (z / GRV_P) % 1.0
    v = (ph - 0.5) / GRV_W
    return GRV_A * max(0.0, 1.0 - v * v) ** 1.2


def revolve(name, prof, mat, n=80, use_groove=True):
    """(z, r) のプロファイルを Z 軸まわりに回して閉じたソリッドにする。"""
    verts, faces = [], []
    rings = []
    for (z, r) in prof:
        rr = max(0.0, r - (groove(z, r) if use_groove else 0.0))
        if rr < 1e-6:
            rings.append([(0.0, 0.0, z)])
        else:
            rings.append([(rr * math.cos(2 * math.pi * i / n),
                           rr * math.sin(2 * math.pi * i / n), z) for i in range(n)])
    idx = []
    for ring in rings:
        idx.append(list(range(len(verts), len(verts) + len(ring))))
        verts.extend(ring)
    for k in range(len(rings) - 1):
        a, bl = idx[k], idx[k + 1]
        if len(a) == 1 and len(bl) == n:
            for j in range(n):
                faces.append([a[0], bl[(j + 1) % n], bl[j]])
        elif len(a) == n and len(bl) == 1:
            for j in range(n):
                faces.append([a[j], a[(j + 1) % n], bl[0]])
        elif len(a) == n and len(bl) == n:
            for j in range(n):
                j2 = (j + 1) % n
                faces.append([a[j], a[j2], bl[j2], bl[j]])
    if len(idx[0]) == n:
        faces.append(list(reversed(idx[0])))
    if len(idx[-1]) == n:
        faces.append(list(idx[-1]))
    o = mesh_object(name, verts, faces, [mat])
    smooth(o)
    return o


# ---------- 独楽（下半身：錐先から赤道まで） ----------
LOWER_CP = [
    (0.000, 0.000),   # 錐先（点で立つ＝1秒で「独楽」に読ませる署名）
    (0.030, 0.038),
    (0.075, 0.082),
    (0.140, 0.140),
    (0.230, 0.235),
    (0.340, 0.360),
    (0.450, 0.500),
    (0.545, 0.630),
    (0.610, 0.720),
    (0.640, 0.755),
    (Z_LOW_TOP, R_MAX),   # 赤道の縁（スリット下縁）
]

# ---------- 独楽（上半身：赤道から心棒の頭まで） ----------
# ドームだけ UP_SQ で扁平にする（心棒の長さは変えない）。
# 2周目：ドームが下の錐と同じ高さだと「蓋つきの壺／どんぐり」に寄る。
# 下の錐を主役にすると「回っているもの」＝独楽の読みが強まる（#16）。
_DOME = [
    (0.000, R_MAX),           # スリット上縁
    (0.028, R_MAX * 0.990),
    (0.088, R_MAX * 0.941),
    (0.158, R_MAX * 0.855),
    (0.228, R_MAX * 0.737),
    (0.298, R_MAX * 0.592),
    (0.358, R_MAX * 0.434),
    (0.398, R_MAX * 0.303),
    (0.423, R_MAX * 0.197),
    (0.438, R_MAX * 0.138),
    (0.443, 0.072),           # 心棒の付け根
]
_STEM = [
    (0.117, 0.068),           # 心棒（縦のアクセント）
    (0.155, 0.086),           # 頭の膨らみ（#31-c：意味を持つ端は留め具で締める）
    (0.190, 0.078),
    (0.207, 0.040),
    (0.212, 0.000),
]
UPPER_CP = ([(Z_UP_BOT + z * UP_SQ, r) for (z, r) in _DOME] +
            [(Z_UP_BOT + 0.443 * UP_SQ + dz, r) for (dz, r) in _STEM])

H_TOTAL = UPPER_CP[-1][0]


def build_lower():
    o = revolve("koma_lower", catmull_rom(LOWER_CP, steps=34), mat_body)
    add_bevel(o, 0.0020)
    return o


def build_upper():
    o = revolve("koma_upper", catmull_rom(UPPER_CP, steps=30), mat_body)
    add_bevel(o, 0.0020)
    return o


def build_core():
    """発光ドラム＝スリットと同軸・同形（#29）。上下の鍔に隠れる高さに収める。"""
    zb, zt = Z_LOW_TOP - 0.058, Z_UP_BOT + 0.058
    prof = [(zb, 0.0), (zb, R_CORE), (zt, R_CORE), (zt, 0.0)]
    return revolve("koma_light", prof, mat_core, n=96, use_groove=False)


lower = build_lower()
upper = build_upper()
core = build_core()
PARTS = [lower, upper, core]

# ---------- リグ（#9：Empty のみ・matrix_parent_inverse は既定の identity のまま） ----------
# rig_prec（歳差／錐先が枢軸）→ rig_tilt（章動）→ 各パーツ（自転）
bpy.ops.object.empty_add(location=(0.0, 0.0, Z_TIP))
rig_prec = bpy.context.active_object
rig_prec.name = "koma_rig_prec"

bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
rig_tilt = bpy.context.active_object
rig_tilt.name = "koma_rig_tilt"
rig_tilt.parent = rig_prec
rig_tilt.location = (0.0, 0.0, 0.0)

for o in PARTS:
    o.parent = rig_tilt
    o.location = (0.0, 0.0, 0.0)


# ---------- 発光の勾配（#34 の2軸楕円 ／ #35 回転しない参照座標） ----------
# 円筒の生 emission は view 非依存（#25b）なので、何もしないと帯は横方向に完全均一＝
# 「緑のテープ」（#24）。しかも object 座標だと勾配が本体と共回りしてしまう。
# → 回転しない参照 Empty の Object 座標で、横（X）と縦（Z）の2軸に落とす。
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
grad_ref = bpy.context.active_object
grad_ref.name = "koma_grad_ref"          # 親を持たない＝歳差にも自転にも従わない

#
# ★ さらに踏んだ罠（#35-b）：2軸とも同じ「固定参照」に取ってはいけない。
#   傾くとスリット円の手前側は world z が **±R_CORE·sinβ ＝ 0.159m** も上下する（FZ の3倍）。
#   固定参照の縦falloff だと手前の帯がまるごと ES=0 に落ち、**ψ=0/π で光が完全に消えた**
#   （f1 のテストレンダーで発覚。probe の「覗け高さ」は幾何しか見ないので気づけない）。
#   → 縦は**発光体自身のローカル Z**（＝スリット面に固定・自転しても不変）、
#     横は**回転しない参照 Empty の X**（＝芯が画面の真ん中に留まる）。軸ごとに座標系を変える。
_ct = mat_core.node_tree
_tc_ref = _ct.nodes.new("ShaderNodeTexCoord")     # 横：世界に固定（芯は画面中央）
_tc_ref.object = grad_ref
_sep_ref = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc_ref.outputs["Object"], _sep_ref.inputs["Vector"])
_tc_self = _ct.nodes.new("ShaderNodeTexCoord")    # 縦：発光体自身＝スリット面に固定
_sep_self = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc_self.outputs["Object"], _sep_self.inputs["Vector"])
_sq = []
for (src, ax, offset, falloff) in ((_sep_ref, "X", 0.0, FX_EM),
                                   (_sep_self, "Z", Z_EQ, FZ_EM)):
    sub = _ct.nodes.new("ShaderNodeMath")
    sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = offset
    _ct.links.new(src.outputs[ax], sub.inputs[0])
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
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'   # 線形だと縁が立つ＝#24
except Exception:
    pass
_ct.links.new(_sqrt.outputs[0], _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], core_bsdf.inputs["Emission Strength"])

# 隙間からこぼれる光（#22：面積で稼ぎ強度で稼がない／発光体の内部に埋めない #29）
# スリットの「カメラに最も近い一点」に毎フレーム置き直す（歳差で位置が動くため）。
bpy.ops.object.light_add(type='POINT', location=(0.0, -(R_CORE + 0.02), CENTER_Z))
glow = bpy.context.active_object
glow.name = "koma_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.35
try:
    glow.visible_camera = False
except Exception:
    pass


def glow_loc(t01):
    """スリット円の、カメラに最も近い点（＝手前の隙間の中）。"""
    n = axis_at(t01)
    c = Vector((0.0, 0.0, Z_TIP)) + n * Z_EQ
    u = Vector((0.0, -1.0, 0.0))
    u = u - n * u.dot(n)
    u.normalize()
    return c + u * (R_CORE + 0.020)


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    rig_prec.rotation_euler = (0.0, 0.0, psi_at(t))
    rig_prec.keyframe_insert(data_path="rotation_euler", frame=f)
    rig_tilt.rotation_euler = (beta_at(t), 0.0, 0.0)
    rig_tilt.keyframe_insert(data_path="rotation_euler", frame=f)
    sp = spin_at(t)
    for o in PARTS:
        o.rotation_euler = (0.0, 0.0, sp)
        o.keyframe_insert(data_path="rotation_euler", frame=f)
    glow.location = glow_loc(t)
    glow.keyframe_insert(data_path="location", frame=f)


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
study = add_caption("MIDDLE STUDY 037 — KOMA", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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
    # #16/#18/#31：レンダーで目視する前に幾何を数値で当てる。
    print(f">> 錐先 world z={Z_TIP:.3f}（宙に浮く）  全高={H_TOTAL:.3f}  赤道 z={CENTER_Z:.3f}")
    vmax, vmin, wmax = -9, 9, 0.0
    for f in range(1, N_FRAMES + 1):
        t = (f - 1) / N_FRAMES
        n = axis_at(t)
        # スリット面と視線のなす角 θ（ルーバー：小さいほど奥まで見える）
        c = Vector((0.0, 0.0, Z_TIP)) + n * Z_EQ
        v = (c - Vector(CAM_LOC)).normalized()
        th = math.asin(min(1.0, abs(v.dot(n))))
        vis = GAP - E_OVER * math.tan(th)
        if vis > vmax:
            vmax, fmax, thmax = vis, f, th
        if vis < vmin:
            vmin, fmin, thmin = vis, f, th
        # 横幅（歳差の振り出しを含む）
        for (zl, rl) in ((Z_EQ, R_MAX), (H_TOTAL, 0.09)):
            p = Vector((0.0, 0.0, Z_TIP)) + n * zl
            wmax = max(wmax, abs(p.x) + rl)
    print(f">> スリットの覗け高さ  最大 {vmax:.4f}m (f{fmax} θ={math.degrees(thmax):.1f}°) / "
          f"最小 {vmin:.4f}m (f{fmin} θ={math.degrees(thmin):.1f}°)  "
          f"＝機構がそのまま光の強弱（変調 {(1 - vmin / vmax) * 100:.0f}%）")
    print(f">> hero(f{STILL_FRAME}) の覗け高さ = "
          f"{GAP - E_OVER * math.tan(math.asin(abs(((Vector((0,0,Z_TIP)) + axis_at((STILL_FRAME-1)/N_FRAMES) * Z_EQ) - Vector(CAM_LOC)).normalized().dot(axis_at((STILL_FRAME-1)/N_FRAMES))))):.4f}m "
          f"→ hero 縦2000px 換算 ≒ {(GAP - E_OVER * 0.05) / 3.52 * 2000:.0f}px")
    print(f">> 横幅 ≒ {2 * wmax:.3f}/2.81 ({2 * wmax / 2.81 * 100:.0f}%)  "
          f"{'OK' if 0.50 < 2 * wmax / 2.81 < 0.70 else 'WARN 55〜65%から外れる'}")
    ztop = Z_TIP + H_TOTAL * math.cos(B0 + BA)
    print(f">> 縦 world z {Z_TIP:.3f}..{ztop:.3f} ({ztop - Z_TIP:.3f}/3.52)  "
          f"screen {screen_y(Z_TIP):+.3f}..{screen_y(ztop):+.3f} "
          f"{'OK' if abs(screen_y(Z_TIP)) < 0.97 and abs(screen_y(ztop)) < 0.97 else 'WARN 切れる'}")
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    print(f">> 錐先(screen {screen_y(Z_TIP):+.3f}) vs caption1(screen {screen_y(CAP_Z[0], -1.3):+.3f}) "
          f"{'OK' if screen_y(Z_TIP) > screen_y(CAP_Z[0], -1.3) + 0.03 else 'WARN 重なる'}")
    zb, zt = Z_LOW_TOP - 0.058, Z_UP_BOT + 0.058
    print(f">> 発光ドラム r={R_CORE:.3f} z {zb:.3f}..{zt:.3f}  張り出し {E_OVER:.3f}  "
          f"隠蔽 {'OK' if zb < Z_LOW_TOP and zt > Z_UP_BOT and R_CORE < R_MAX else 'WARN 露出'} / "
          f"裏当て {'OK（白背景を止める）' if R_CORE > 0 else 'WARN'}")
    print(f">> 勾配 r=√((x/{FX_EM})²+(z/{FZ_EM})²)  ES {ES_CORE}→{ES_RIM}  "
          f"帯の上下端(z=±{GAP / 2:.3f}) で r={GAP / 2 / FZ_EM:.2f} / "
          f"ドラム左右端(x=±{R_CORE:.3f}) で r={R_CORE / FX_EM:.2f} "
          f"{'OK（両端が0に落ちる＝芯が残る #34）' if R_CORE / FX_EM >= 0.95 else 'WARN 横が均一＝テープ化'}")
    print(f">> loop: ψ=2πt(1周) / β=B0+BA·cos(2π·{NUT_K}t) / spin=2π·{N_SPIN}t "
          f"＝すべて整数周期＝t=0とt=1が厳密一致 / {N_FRAMES}f {N_FRAMES / FPS:.3f}s")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "koma.blend"))
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
    keep = {o.name for o in PARTS} | {rig_prec.name, rig_tilt.name}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "koma.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
