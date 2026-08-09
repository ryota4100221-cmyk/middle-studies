# =============================================================
# monaka design. — MIDDLE STUDY 046 "MAKIMONO"（巻物 / a handscroll）
# 黒い巻物が宙にある。上と下から巻かれていて、ひらかれているのは真ん中だけ。
# その真ん中に、一条の ライム #A5E02E が横たわる。
# 軸が回ると紙は吸い込まれ、光は細い線になる。ほどければ、また太くなる。
# **物語は、真ん中だけがひらかれている。**
#
# 【ドメイン】書物・巻子。直近10作（土木・橋／建築・寺社／虫・生命／工芸・繕い／
#   植物・竹／計量・秤／貝・海／折紙／玩具・独楽／武具・鞘）と別領域。
#   022 HON【書物】は「ページが扇に開いて綴じ目が光る」＝開閉の機構と縦のシルエット。
#   046 は「両端が巻かれていて真ん中だけが開いている」＝巻き取りの機構と横の一条。
#   タグライン "Designing the Middle of Your Story." の最も直接的な立体化。
#
# 【機構】シリーズ初の「**転がり接触（rolling without slipping）**」。
#   ・軸は回るだけでは足りない。紙を吐き出した分だけ**離れて**いかなければならない。
#     ＝ 回転 α と 並進 z が R で結ばれる（ż = R·α̇）。これが「巻き取る」の実体。
#   ・θ(t)=Θ·0.5(1−cos2πt) を巻き取り量とすると
#       span(t) = SPAN_MAX − 2R·θ(t)、軸の中心 z = ±span/2、α = ∓θ。
#     cos の整数周期＝完全ループ。**回転キー＋位置キー＋scale キーのみ＝glb にそのまま乗る。**
#   ・上下対称に巻き取るので、**紙は縮んでも光の芯は画面の真ん中から一歩も動かない**
#     （034/035/044 と同じ主題を「巻く」で書いた版）。
#   ・機構がそのまま光の量になる：巻き取られると軸が光の帯の上下を食う。
#     純math スキャンで露出発光面積は 100%→65%以下（#40⑥）。
#
# 【光】紙＝Base 純黒＋低 Spec（#32）。勾配は #34 の2軸楕円距離。
#   ただし紙は scale.z で伸縮するので、**UV に焼くと帯まで一緒に縮む**（#39 が使えない）。
#   → #35 のとおり「**回転も伸縮もしない参照 Empty の Object 座標**」で取る＝
#     帯は世界に固定され、紙の端（＝軸に入る所）がそれを切る。これが正しい物理でもある。
#   FX は紙の半幅より内側（縁で ES＝0＝そのまま裏当て／緑スピルなし #26②/#28）。
#
# 【型（#33）への手当て】黒い紙＋2本の軸だけでは「ロールスクリーン／印刷機」に転びうるので、
#   巻物の署名を2つ入れる：①**軸端（じくさき）が紙幅の外に出る**（#40①「支えている側を出す」）
#   ②**巻いた紙の断面＝同心のリング**が木口に出る（#43-i：材料の署名は人工物の痕跡）。
#   リングを見せるために rig を yaw して 3/4 に振る（#18：フレームは右に余裕がある）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_makimono.py -- <mode...>
#   modes: probe | bbox | test | testhero | still | anim | blend | glb  （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

TAU = math.pi * 2.0

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_makimono")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "1.90"))    # 巻物の上下中心（world）
LOOK_Z = float(os.environ.get("LOOK_Z", "1.90"))        # ＝CENTER_Z：光の芯を画面中央へ
CAM_LOC = (0.55, -8.3, 1.95)
SCROLL_X = float(os.environ.get("SCROLL_X", "0.10"))
YAW = math.radians(float(os.environ.get("YAW", "-21.0")))   # 負＝右（余裕のある側）を手前へ

# --- 紙と軸 ---
HW = float(os.environ.get("HW", "0.638"))                # 紙の半幅
T_P = float(os.environ.get("T_P", "0.0055"))            # 紙の厚み（＝巻きのピッチ）
R0 = float(os.environ.get("R0", "0.0396"))               # 軸（じく）の半径
N_TURN = float(os.environ.get("N_TURN", "5.6"))         # 巻き数（木口に出るリングの数）
R = R0 + T_P * (N_TURN + 1.0)                           # 巻いた紙の外半径
KNOB_OUT = float(os.environ.get("KNOB_OUT", "0.077"))   # 軸が紙幅の外へ出る長さ
KNOB_R = float(os.environ.get("KNOB_R", "0.055"))       # 軸端（じくさき）の半径
KNOB_L = float(os.environ.get("KNOB_L", "0.0286"))
BOW = float(os.environ.get("BOW", "0.060"))            # 紙の反り（巻き癖）＝平板に見せない
Y_BACK = 0.0010                                         # 軸を紙より 1mm 奥へ（同一平面を作らない #42-c）

SPAN_MAX = float(os.environ.get("SPAN_MAX", "1.738"))    # ひらいた紙の長さ（軸の接点間）
SPAN_MIN = float(os.environ.get("SPAN_MIN", "0.52"))    # 巻き取ったとき（2R より大きいこと）
THETA_MAX = (SPAN_MAX - SPAN_MIN) / (2.0 * R)           # 転がり接触：離れた分だけ回る

# --- 光（#34 の2軸／#35 の参照座標） ---
FX = float(os.environ.get("FX", "0.090"))               # 短軸＝線の半幅（#34：横の減衰が無いとテープになる）
FZ = float(os.environ.get("FZ", "0.70"))                # 長軸＝縦の一行。紙の端（軸に入る所）がこれを切る
ES_CORE = float(os.environ.get("ES_CORE", "5.6"))
D_POW = float(os.environ.get("D_POW", "1.20"))          # #38④：暗い裾の広さ＝中間調

# --- 材質（#17-b 紙／#17-c 一様bright env では反射率が支配項） ---
SPEC_PAPER = float(os.environ.get("SPEC_PAPER", "0.10"))
ROUGH_PAPER = float(os.environ.get("ROUGH_PAPER", "0.62"))
SPEC_WOOD = float(os.environ.get("SPEC_WOOD", "0.10"))
ROUGH_WOOD = float(os.environ.get("ROUGH_WOOD", "0.75"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.90")),
         float(os.environ.get("CAP_Z2", "0.72")),
         float(os.environ.get("CAP_Z3", "0.60")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92
                 for v in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 機構（純math：Blender を起動せずに当てる #31） ----------
def theta(t):
    return THETA_MAX * 0.5 * (1.0 - math.cos(TAU * t))


def span(t):
    return SPAN_MAX - 2.0 * R * theta(t)


def es_xz(x, z):
    """材質ノードと同じ式（#34 の2軸楕円距離／参照座標＝世界に固定）。"""
    d = math.sqrt((x / FX) ** 2 + (z / FZ) ** 2) ** D_POW
    d = max(0.0, min(1.0, d))
    return ES_CORE * (1.0 - (3.0 * d * d - 2.0 * d ** 3))


def lit_area(sp):
    """露出している紙の上の ES 重み付き面積（#40⑥）。紙は |z| <= sp/2 にしか無い。"""
    NX, NZ = 40, 80
    zc = min(sp * 0.5, FZ)
    dx, dz = 2.0 * FX / NX, 2.0 * zc / NZ
    tot = 0.0
    for i in range(NX):
        x = -FX + dx * (i + 0.5)
        for j in range(NZ):
            z = -zc + dz * (j + 0.5)
            tot += es_xz(x, z) * dx * dz
    return tot


def _pick_still():
    best, bf = -1e9, 1
    for f in range(1, N_FRAMES + 1):
        a = lit_area(span((f - 1) / N_FRAMES))
        if a > best:
            best, bf = a, f
    return bf


STILL_FRAME = int(os.environ.get("STILL_FRAME", str(_pick_still())))
H_TOTAL = SPAN_MAX + 2.0 * R


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_paper, b = make_principled("mk_paper")       # 巻かれた紙（軸のまわり）
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_PAPER
b.inputs["Specular IOR Level"].default_value = SPEC_PAPER
b.inputs["Coat Weight"].default_value = 0.0

mat_wood, b = make_principled("mk_jiku")         # 軸・軸端
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_WOOD
b.inputs["Specular IOR Level"].default_value = SPEC_WOOD
b.inputs["Coat Weight"].default_value = 0.0

mat_em, em_bsdf = make_principled("mk_hon")      # 本紙＝ひらかれた真ん中＝光
em_bsdf.inputs["Base Color"].default_value = BLACK   # #32（暗ライム不可。ただし純黒は「穴」に見える）
em_bsdf.inputs["Emission Color"].default_value = LIME
em_bsdf.inputs["Roughness"].default_value = ROUGH_PAPER
em_bsdf.inputs["Specular IOR Level"].default_value = SPEC_PAPER

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
def smooth_auto(o, angle=0.55):
    """#6：5.x は shade_auto_smooth（active+selected で呼ぶ）。#43-g：shade_smooth は使わない。"""
    try:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_auto_smooth(angle=angle)
    except Exception as e:
        print(">> shade_auto_smooth skipped:", e)


def finish(name, bm, mats, smooth=True, weld=False, auto=True):
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


def band_x(bm, lo, hi, x0, x1):
    """lo / hi は同数の (y,z) 列。x0..x1 に掃引して閉じた solid にする。
    n-gon を作らないので、螺旋のように曲がった断面でも三角化が崩れない（#10）。"""
    n = len(lo)
    A, B = [], []
    for i in range(n):
        A.append((bm.verts.new((x0, lo[i][0], lo[i][1])),
                  bm.verts.new((x0, hi[i][0], hi[i][1]))))
        B.append((bm.verts.new((x1, lo[i][0], lo[i][1])),
                  bm.verts.new((x1, hi[i][0], hi[i][1]))))
    for i in range(n - 1):
        bm.faces.new((A[i][0], A[i + 1][0], A[i + 1][1], A[i][1]))    # 木口（x0）
        bm.faces.new((B[i][0], B[i + 1][0], B[i + 1][1], B[i][1]))    # 木口（x1）
        bm.faces.new((A[i][0], A[i + 1][0], B[i + 1][0], B[i][0]))    # 内側の面
        bm.faces.new((A[i][1], A[i + 1][1], B[i + 1][1], B[i][1]))    # 外側の面
    bm.faces.new((A[0][0], A[0][1], B[0][1], B[0][0]))                # 紙の端（自由端）
    bm.faces.new((A[-1][0], A[-1][1], B[-1][1], B[-1][0]))            # 紙の端（軸に接する側）


def cyl_x(bm, x0, x1, r, seg=72):
    """x 軸まわりの円柱（キャップつき）。ベベルを掛けないので n-gon キャップで可。"""
    r0, r1 = [], []
    for i in range(seg):
        a = TAU * i / seg
        y, z = r * math.cos(a), r * math.sin(a)
        r0.append(bm.verts.new((x0, y, z)))
        r1.append(bm.verts.new((x1, y, z)))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(list(reversed(r0)))
    bm.faces.new(r1)


def lin(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


# ---------- 造形（すべて「軸のローカル座標」＝軸の芯が原点・x が軸方向） ----------
def build_wound(sg):
    """巻かれた紙。自由端（φ=π＝紙が離れる接点）から内へアルキメデス螺旋で巻く。
    木口に同心のリングが N_TURN 本出る＝「巻いた紙」の署名（#43-i）。
    sg=+1 が上の軸／−1 が下の軸（z 鏡像＝巻きの向きも反転する）。"""
    bm = bmesh.new()
    lo, hi = [], []
    NS = max(64, int(N_TURN * 96))
    for i in range(NS + 1):
        s = TAU * N_TURN * i / NS
        phi = math.pi - s                 # 自由端は接点（−y 側＝カメラ側）
        ro = R - T_P * (s / TAU)
        ri = ro - T_P
        c, sn = math.cos(phi), math.sin(phi)
        lo.append((ri * c, sg * ri * sn))
        hi.append((ro * c, sg * ro * sn))
    band_x(bm, lo, hi, -HW, HW)
    return finish("wound%+d" % sg, bm, [mat_paper])


def build_jiku(sg):
    """軸＋軸端。紙幅の外へ出る＝「巻物である」ことの宣言（#40①／#41：肋は2つまで）。"""
    bm = bmesh.new()
    xe = HW + KNOB_OUT
    cyl_x(bm, -xe, xe, R0)
    cyl_x(bm, -xe, -xe + KNOB_L, KNOB_R)
    cyl_x(bm, xe - KNOB_L, xe, KNOB_R)
    return finish("jiku%+d" % sg, bm, [mat_wood])


def build_honshi():
    """本紙＝ひらかれた真ん中。前面 y=0（軸はここに接する）／奥へ T_P の厚み。
    z は SPAN_MAX で作り、scale.z で伸縮させる（発光は参照座標なので一緒に縮まない #35）。"""
    bm = bmesh.new()
    zs = lin(-SPAN_MAX * 0.5, SPAN_MAX * 0.5, 40)

    def _bow(z):
        return -BOW * (1.0 - (2.0 * z / SPAN_MAX) ** 2)

    band_x(bm, [(_bow(z), z) for z in zs], [(T_P + _bow(z), z) for z in zs], -HW, HW)
    return finish("honshi", bm, [mat_em])


# ---------- 組み立て（#9：リグは原点／matrix_parent_inverse は identity） ----------
bpy.ops.object.empty_add(location=(SCROLL_X, 0.0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "mk_pose"
rig.rotation_euler = (0.0, 0.0, YAW)

honshi = build_honshi()
honshi.parent = rig
honshi.location = (0.0, 0.0, 0.0)

PARTS = [honshi]
ROLLS = []
for sg in (+1, -1):
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    e = bpy.context.active_object
    e.name = "roll%+d" % sg
    e.parent = rig
    e.location = (0.0, R + Y_BACK, sg * SPAN_MAX * 0.5)
    ROLLS.append((sg, e))
    for o in (build_wound(sg), build_jiku(sg)):
        o.parent = e
        o.location = (0.0, 0.0, 0.0)
        PARTS.append(o)

# 発光の勾配を取るための参照（回らない・伸び縮みしない）
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
ref = bpy.context.active_object
ref.name = "mk_ref"
ref.parent = rig
ref.location = (0.0, 0.0, 0.0)


# ---------- 発光の勾配（#35：参照 Empty の Object 座標＝紙が伸縮しても帯は動かない） ----------
_ct = mat_em.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_tc.object = ref
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Object"], _sep.inputs["Vector"])


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


_u = _m('DIVIDE', _sep.outputs["X"], val=FX)
_v = _m('DIVIDE', _sep.outputs["Z"], val=FZ)
_d = _m('SQRT', _m('ADD', _m('MULTIPLY', _u, _u), _m('MULTIPLY', _v, _v)))
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


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    th = theta(t)
    sp = span(t)
    k = sp / SPAN_MAX
    # y も同率で縮める＝反り（巻き癖）は span に比例する。y=0 の接点は動かないので接線は保たれる
    honshi.scale = (1.0, k, k)
    honshi.keyframe_insert(data_path="scale", frame=f)
    for sg, e in ROLLS:
        e.location = (0.0, R + Y_BACK, sg * sp * 0.5)
        e.rotation_euler = (-sg * th, 0.0, 0.0)   # ż = R·α̇（転がり接触）
        e.keyframe_insert(data_path="location", frame=f)
        e.keyframe_insert(data_path="rotation_euler", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(SCROLL_X, -0.30, CENTER_Z))
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


tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, CAP_Z[0]), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, CAP_Z[1]), "logo")
study = add_caption("MIDDLE STUDY 046 — MAKIMONO", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


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


def screen_x(x, y=0.0):
    dist = y - CAM_LOC[1]
    half = (36.0 / 2.0 / 85.0) * dist * (1600.0 / 2000.0)
    cx = CAM_LOC[0] + (0.1 - CAM_LOC[0]) * (dist / (0.0 - CAM_LOC[1]))
    return (x - cx) / half


# ---------- 出力モード ----------
modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "probe" in modes:
    print(">> 紙 %.3f×%.3f  軸 R=%.4f（芯 %.3f・巻き %.1f 周）  全高 %.3f  全幅 %.3f"
          % (2 * HW, SPAN_MAX, R, R0, N_TURN, H_TOTAL, 2 * (HW + KNOB_OUT)))
    print(">> 転がり接触：Θ=%.2f rad（%.0f°）  span %.3f→%.3f  STILL_FRAME=%d"
          % (THETA_MAX, math.degrees(THETA_MAX), SPAN_MAX, SPAN_MIN, STILL_FRAME))
    cl = SPAN_MIN - 2.0 * R
    print(">> 【軸の当たり】最接近の隙間 %.4f m → %s"
          % (cl, "OK" if cl > 0.005 else "🔴 NG：SPAN_MIN を上げるか R を下げる"))
    print(">> 【緑スピル】FX %.3f vs 紙の半幅 %.3f → %s（#26②/#28）"
          % (FX, HW, "OK（縁で ES=0）" if FX < HW - 0.02 else "🔴 NG"))
    a0 = lit_area(SPAN_MAX)
    print(">> 光の量（#40⑥ 75%%を切れば合格）:")
    for tt in (0.0, 0.125, 0.25, 0.375, 0.5):
        print("   t=%.3f  span=%.3f  %.1f%%"
              % (tt, span(tt), 100.0 * lit_area(span(tt)) / a0))
    zb, zt = CENTER_Z - H_TOTAL * 0.5, CENTER_Z + H_TOTAL * 0.5
    print(">> 画面（#18 縦 -1..+1）: 下 %+.3f  上 %+.3f  占有 %.0f%%"
          % (screen_y(zb), screen_y(zt), 50.0 * (screen_y(zt) - screen_y(zb))))
    print(">> 光の芯 %+.3f（0 が画面中央）  帯の上下 %+.3f / %+.3f"
          % (screen_y(CENTER_Z), screen_y(CENTER_Z + FZ), screen_y(CENTER_Z - FZ)))
    for i, z in enumerate(CAP_Z):
        print("   キャプション%d %+.3f" % (i + 1, screen_y(z, -1.3)))
    # 横：yaw と見込みを込みで4隅を実測（#18：近い側ほど拡大する）
    xs = []
    for sx in (-1, +1):
        for yy in (0.0, 2.0 * R):
            px = SCROLL_X + sx * (HW + KNOB_OUT) * math.cos(YAW) - yy * math.sin(YAW)
            py = sx * (HW + KNOB_OUT) * math.sin(YAW) + yy * math.cos(YAW)
            xs.append(screen_x(px, py))
    print(">> 横（-1..+1）: 左 %+.3f  右 %+.3f  占有 %.0f%%"
          % (min(xs), max(xs), 50.0 * (max(xs) - min(xs))))

if "bbox" in modes:
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME)
    dg.update()
    for o in PARTS:
        ob = o.evaluated_get(dg)
        ws = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        print(">> %-10s x %+.3f..%+.3f  y %+.3f..%+.3f  z %+.3f..%+.3f  verts=%d"
              % (o.name, min(w.x for w in ws), max(w.x for w in ws),
                 min(w.y for w in ws), max(w.y for w in ws),
                 min(w.z for w in ws), max(w.z for w in ws), len(ob.data.vertices)))

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "makimono.blend"))
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
    keep = {rig.name, ref.name} | {e.name for _s, e in ROLLS} | {o.name for o in PARTS}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "makimono.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
