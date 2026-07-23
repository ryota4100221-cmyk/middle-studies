# =============================================================
# monaka design. — MIDDLE STUDY 029 "MATSUKASA"（松毬 / まつぼっくり）
# 黒い松毬が宙に浮く。鱗片（うろこ）が開くと、鱗片の隙間の奥＝芯から
# ライム #A5E02E の光が満ち、閉じると鱗片が重なり合って光を完全に覆い、
# 黒い毬に戻る。真ん中＝毬の芯に、光がある。
#
# 機構: 造形＝卵形(ovoid)回転体の表面に、フィロタキシー（黄金角 137.507°）で
#   N 枚の黒い鱗片を配置（シリーズ初の黄金角配置）。各鱗片は bmesh 実寸のタブ
#   （幅×長さ×薄いz＋わずかな凸カップ）で、局所原点＝ヒンジ（付け根）・+Y＝谷側
#   （下向き）・+Z＝外向き法線。開閉＝各鱗片を自分のヒンジ（接線方向の軸）まわりに
#   rotation_euler.x で振り、閉じると鱗片が重なって芯を遮蔽、開くと谷側の先端が外へ
#   持ち上がり隙間ができる。光＝毬の芯（軸）に立てた発光ライムの紡錘(spindle・回転体)
#   ＋半径依存の放射グラデ Emission（027/028 と同じ＝中心ホットコア→#A5E02E→暗部の
#   勾配で #24 ペンキ化回避／広い発光面で #11 Glare箱回避／#25b の view 非依存対策）
#   ＋随伴する柔らかいライム点光源（#22 弱め）。鱗片が閉じると紡錘は完全に覆われ、
#   開くと多数の隙間の奥から分散して覗く（024 OUGI と同じ「黒い覆いの奥に発光面・
#   多数の隙間から分散」＝Glare箱を構造回避／裸の緑棒 #13 も遮蔽で回避）。
# アニメ: 開き角 φ_i(t)=φ_max·breath(t−LAG·s_i)（s_i＝高さ、LAG小＝下から上への静かな
#   波・014 NENRIN の位相ラグ）、breath(t)=0.5(1−cos2πt)＝still(t=0.5) で開・両端で閉
#   ＝完全ループ。鱗片は object 回転(transform)なので glb にアニメが乗る。
# 素材: 鱗片は一様bright env 下の平面黒＝Spec 0.10・Coat 0（#17-c）でエッジのフレネル
#   だけで形を持たせ黒を黒に保つ。リグ＝毬中心の Tilt-Empty（025/027）＋各鱗片は
#   「ヒンジ姿勢を焼いた静的 Empty E_i」の子に置き E_i local X まわりの rotation で開く
#   （rest とアニメを2段で分離＝matrix_parent_inverse=identity で #9 回避、
#   object.scale/transform_apply 不使用 #15）。上下の極に白背景抜け防止＋先端の黒キャップ。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
#   env: ES_CORE ES_RIM GLOW_E TILT_DEG PHI_MAX N_SCALES SPEC_BLADE
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector, Matrix

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.50          # 松毬の視覚中心（シリーズ共通の画面中心付近）
TILT = math.radians(float(os.environ.get("TILT_DEG", "13")))   # 軸を上→奥へ倒しカメラに上の鱗片も見せる
ROT_Z_RIG = math.radians(6.0)  # フレームの空いている右側へわずかに回す（#18・「撮った写真」に寄せる）

# --- 松毬の卵形(ovoid)本体 ---
H_AXIS = 1.70            # 軸長（z = -0.85 .. +0.85）
R_MAX = 0.62             # 卵形の最大半径（t=0.5）。開き幅を #18 の55〜65%に収める
OVOID_P = 0.72           # r(t)=R_MAX·sin(pi·t)^OVOID_P（<1でやや樽・両端で0）
T_LO, T_HI = 0.11, 0.93  # 鱗片を配る軸パラメータ範囲（極は空けてキャップで塞ぐ）

# --- 鱗片（うろこ） ---
# 松毬は鱗片が密に重なる（シングル葺き）。閉じれば黒い卵、開けば谷側の先端が少しだけ
# 持ち上がり狭い隙間の奥から光が覗く（024 OUGI 方式・裸の緑棒 #13 を遮蔽で回避）。
N_SCALES = int(os.environ.get("N_SCALES", "84"))
PHI_GOLDEN = math.radians(137.507)   # 黄金角（フィロタキシー）
SC_W = 0.150             # 鱗片の最大 half-width（接線方向・隣と重なる幅）
SC_L = 0.400             # 鱗片の長さ（谷側 +Y・下の鱗を葺く）
SC_CUP = 0.050           # 外向き(+Z)の凸カップ＝鱗片が surface を抱く
SC_HZ = 0.0060           # 鱗片の z 半厚（薄い鱗）
SC_SECT = 11             # 長さ方向の分割
PHI_MAX = math.radians(float(os.environ.get("PHI_MAX", "30")))  # 開きは控えめ＝光は隙間から覗く（naked pill にしない）
LAG = 0.06               # 下→上への位相ラグ（静かな波・NENRIN）

# --- 中央の発光ライム紡錘（芯の光） ---
SP_R = 0.150             # 紡錘の最大半径（鱗片付け根 r より内＝閉時に覆われる）
SP_HALF = 0.60           # 紡錘の半長（z = -0.60 .. +0.60・鱗片野に隠れ隙間から覗く）
SP_P = 0.62
SP_RN, SP_AN = 24, 96

# --- マテリアル調整（env で hero スイープ） ---
ES_CORE = float(os.environ.get("ES_CORE", "7.0"))  # 中央高さの帯＝ホットコア（白飛びさせてハローを出す）#25b/#24
ES_RIM = float(os.environ.get("ES_RIM", "0.55"))   # 上下の極＝暗部へ落とす（勾配で std を上げる）
SPEC_BLADE = float(os.environ.get("SPEC_BLADE", "0.10"))  # #17-c: 一様bright env下の黒平面は反射率支配
GLOW_E = float(os.environ.get("GLOW_E", "16.0"))   # 随伴ライム点光源（内側の鱗片面をライムに洗う＝glow from within）

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 61         # t≈0.5 ＝ 全開（芯の光が隙間から満ちた瞬間）


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)

# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


# 鱗片＝黒い松毬の鱗。一様に明るいグレー env（0.92・シリーズ不変）下では鏡面反射が
# 一様な灰色ヴェールになり roughness では消せない＝#17-c に従い鏡面反射率そのもの
# （Specular IOR Level・Coat）を落とす。正対面は暗く沈み、縁だけフレネルで明るく立つ。
mat_scale, b = make_principled("matsu_scale")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.52   # 木質のマットさ
b.inputs["Specular IOR Level"].default_value = SPEC_BLADE
b.inputs["Coat Weight"].default_value = 0.0

# 芯の発光ライム紡錘。#13 に従い純発光体（Base Color を暗いライムに落として反射白の
# 上乗せを消す）。#24/#25b の要諦：生の emission は view 非依存で core≒mid＝勾配が
# 出ず「ペンキ」に退化する。Emission Strength を半径依存の放射グラデにして中心を
# ホットコアに白飛びさせ縁・端を #A5E02E 域に落とす＝「白い芯→#A5E02E→暗部」の勾配。
mat_core, core_bsdf = make_principled("matsu_core")
core_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.10
# --- 縦バンドの放射グラデ Emission（Generated Z の中心=毬の中央高さで最も熱く、上下の極へ
#   落とす）。★#25b の反省：3D 放射（中心からの距離）だと紡錘の「表面＝外側」が全部 rim に
#   なり、視認できる面が一様に暗くなる（＝ペンキ）。紡錘は solid なので中心(hot core)が
#   内部に埋もれて見えない。視認できる surface の上に勾配を作るには、camera が覗く「中央高さ」
#   の帯を白飛びさせ、上下へ #A5E02E→暗部に落とす縦グラデが正解＝隙間から覗く光に芯とハロー。
_ct = mat_core.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
_dz = _ct.nodes.new("ShaderNodeMath"); _dz.operation = 'SUBTRACT'; _dz.inputs[1].default_value = 0.5
_ct.links.new(_sep.outputs["Z"], _dz.inputs[0])
_absz = _ct.nodes.new("ShaderNodeMath"); _absz.operation = 'ABSOLUTE'
_ct.links.new(_dz.outputs[0], _absz.inputs[0])
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 0.42    # 中央高さ(0)→ホットコア／極(0.5)→暗部
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
_ct.links.new(_absz.outputs[0], _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], core_bsdf.inputs["Emission Strength"])

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（PITFALL #15） ----------
def new_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def shade_smooth(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.9)
    except Exception:
        pass
    o.select_set(False)


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


# ---------- 卵形(ovoid)プロファイル ----------
def ovoid_r(t):
    return R_MAX * (math.sin(math.pi * t) ** OVOID_P)


def ovoid_z(t):
    return H_AXIS * (t - 0.5)


def ovoid_point(t, a):
    r = ovoid_r(t)
    return Vector((r * math.cos(a), r * math.sin(a), ovoid_z(t)))


def ovoid_frame(t, a):
    """表面点 P とヒンジ姿勢 (X=幅, Y=谷側/下向き, Z=外向き法線)。右手系・Z 外向き。"""
    dt = 1e-4
    r0, r1 = ovoid_r(max(0.0, t - dt)), ovoid_r(min(1.0, t + dt))
    rp = (r1 - r0) / (2 * dt)
    zp = H_AXIS  # dz/dt 一定
    ca, sa = math.cos(a), math.sin(a)
    Tg = Vector((-sa, ca, 0.0))                     # 接線（水平・方位）
    Tm = Vector((rp * ca, rp * sa, zp)).normalized()  # 経線接線（t 増＝上向き）
    X = (-Tg).normalized()                          # 幅（-Tg で右手系＆ Z 外向きに）
    Y = (-Tm)                                        # 谷側（t 減＝下向き）
    Z = X.cross(Y).normalized()                     # 外向き法線（代数上 rad 正）
    P = ovoid_point(t, a)
    if Z.dot(Vector((ca, sa, 0.0))) < 0:            # 安全：外向きでなければ反転（右手系保持）
        Z = -Z
        X = -X
    return P, X, Y, Z


# ---------- 鱗片メッシュ（局所フレーム：ヒンジ原点・+Y 谷側・+Z 外向き） ----------
def scale_halfwidth(s):
    """s=0(ヒンジ)→1(先端)。付け根やや細→腹で満幅→先端で丸く細る。"""
    grow = 0.42 + 0.58 * smooth01(s / 0.26)
    taper = 1.0 - 0.86 * smooth01((s - 0.66) / 0.34)
    return SC_W * max(0.05, grow * taper)


def scale_cup(s):
    """外向き(+Z)の凸カップ。先端ほど surface を抱くように持ち上げる。"""
    return SC_CUP * (s ** 1.25)


def build_scale(name):
    bm = bmesh.new()
    rings = []
    for j in range(SC_SECT + 1):
        s = j / SC_SECT
        y = SC_L * s
        hw = scale_halfwidth(s)
        zc = scale_cup(s)
        vt0 = bm.verts.new((+hw, y, zc + SC_HZ))
        vt1 = bm.verts.new((-hw, y, zc + SC_HZ))
        vb1 = bm.verts.new((-hw, y, zc - SC_HZ))
        vb0 = bm.verts.new((+hw, y, zc - SC_HZ))
        rings.append((vt0, vt1, vb1, vb0))
    for j in range(SC_SECT):
        a = rings[j]
        c = rings[j + 1]
        bm.faces.new((a[0], a[1], c[1], c[0]))  # top(+Z)
        bm.faces.new((a[1], a[2], c[2], c[1]))  # -X side
        bm.faces.new((a[2], a[3], c[3], c[2]))  # bottom(-Z)
        bm.faces.new((a[3], a[0], c[0], c[3]))  # +X side
    s0, s1 = rings[0], rings[SC_SECT]
    bm.faces.new((s0[0], s0[3], s0[2], s0[1]))  # ヒンジ端キャップ
    bm.faces.new((s1[1], s1[2], s1[3], s1[0]))  # 先端キャップ
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_scale)
    shade_smooth(o)
    return o


# ---------- 芯の発光紡錘（回転体・027/028 のディッシュの縦長版） ----------
def build_spindle(name):
    bm = bmesh.new()

    def sr(u):  # u:0(底)..1(頂)
        return SP_R * (math.sin(math.pi * u) ** SP_P)

    def sz(u):
        return SP_HALF * (2 * u - 1)

    bot = bm.verts.new((0, 0, sz(0.0)))
    top = bm.verts.new((0, 0, sz(1.0)))
    rings = []
    for i in range(1, SP_RN):
        u = i / SP_RN
        r = sr(u)
        z = sz(u)
        ring = [bm.verts.new((r * math.cos(2 * math.pi * j / SP_AN),
                              r * math.sin(2 * math.pi * j / SP_AN), z))
                for j in range(SP_AN)]
        rings.append(ring)
    for j in range(SP_AN):
        j2 = (j + 1) % SP_AN
        bm.faces.new((bot, rings[0][j], rings[0][j2]))
        bm.faces.new((top, rings[-1][j2], rings[-1][j]))
    for i in range(len(rings) - 1):
        for j in range(SP_AN):
            j2 = (j + 1) % SP_AN
            bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_core)
    shade_smooth(o)
    return o


# ---------- 極の黒キャップ（白背景抜け防止＋松毬らしい先端） ----------
def build_cap(name, z_apex, z_base, r_base):
    bm = bmesh.new()
    seg = 40
    apex = bm.verts.new((0, 0, z_apex))
    ring = [bm.verts.new((r_base * math.cos(2 * math.pi * j / seg),
                          r_base * math.sin(2 * math.pi * j / seg), z_base))
            for j in range(seg)]
    cen = bm.verts.new((0, 0, z_base))
    for j in range(seg):
        j2 = (j + 1) % seg
        bm.faces.new((apex, ring[j], ring[j2]))
        bm.faces.new((cen, ring[j2], ring[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_scale)
    shade_smooth(o)
    return o


# ---------- リグ（毬中心の Tilt-Empty・025/027 方式） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "MatsuRig"
rig.rotation_euler = (TILT, 0.0, ROT_Z_RIG)


def child_of(obj, parent, basis=None):
    """parent 付け＋ matrix_parent_inverse=identity（#9）。basis は parent-local の rest 変換。"""
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix()
    if basis is not None:
        obj.matrix_basis = basis
    return obj


# 芯の紡錘・極キャップ（rig 直下）
spindle = build_spindle("matsu_core")
child_of(spindle, rig, Matrix.Translation((0, 0, 0)))

cap_top = build_cap("matsu_cap_top", ovoid_z(1.0) + 0.13, ovoid_z(T_HI) + 0.02, ovoid_r(T_HI) * 0.9)
child_of(cap_top, rig, Matrix.Translation((0, 0, 0)))
cap_bot = build_cap("matsu_cap_bot", ovoid_z(0.0) - 0.07, ovoid_z(T_LO) - 0.01, ovoid_r(T_LO) * 0.95)
child_of(cap_bot, rig, Matrix.Translation((0, 0, 0)))

# ---------- 鱗片をフィロタキシー配置し、2段（静的 Empty E_i ＋ 回転する鱗片 S_i）で組む ----------
scales = []       # (S_i, s_height) 　アニメ対象
scale_names = []  # glb 選択用
empty_names = []
for i in range(N_SCALES):
    t = T_LO + (T_HI - T_LO) * (i / (N_SCALES - 1))
    a = i * PHI_GOLDEN
    P, X, Y, Z = ovoid_frame(t, a)
    # 静的 Empty：ヒンジ位置＋姿勢（列＝X,Y,Z）を焼く
    M = Matrix((
        (X.x, Y.x, Z.x, P.x),
        (X.y, Y.y, Z.y, P.y),
        (X.z, Y.z, Z.z, P.z),
        (0.0, 0.0, 0.0, 1.0)))
    bpy.ops.object.empty_add(location=(0, 0, 0))
    E = bpy.context.active_object
    E.name = "matsu_E_%02d" % i
    E.empty_display_size = 0.05
    child_of(E, rig, M)
    empty_names.append(E.name)
    # 回転する鱗片：E の子・rest=identity（E local X まわりに開く）
    S = build_scale("matsu_scale_%02d" % i)
    child_of(S, E, Matrix())
    s_h = (t - T_LO) / (T_HI - T_LO)   # 0(下)..1(上)
    scales.append((S, s_h))
    scale_names.append(S.name)


# ---------- 随伴ライム点光源（芯の光を鱗片の内側に照り返す・#22 弱め） ----------
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
glow = bpy.context.active_object
glow.name = "matsu_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.shadow_soft_size = 0.7
child_of(glow, rig, Matrix.Translation((0, 0, 0)))


# ---------- アニメーション（完全ループ・開閉） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS


def breath(t01):
    return 0.5 * (1.0 - math.cos(2 * math.pi * t01))


for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    for (S, s_h) in scales:
        b = breath((t01 - LAG * s_h) % 1.0)   # 下→上への位相ラグ（周期1で閉じる）
        S.rotation_euler = (PHI_MAX * b, 0.0, 0.0)   # E local X まわり＝ヒンジで開く
        S.keyframe_insert(data_path="rotation_euler", frame=f)
    bt = breath(t01)
    glow.data.energy = GLOW_E * (0.10 + 0.90 * bt)   # 開くほど明るく（閉でほぼ消灯）
    glow.data.keyframe_insert(data_path="energy", frame=f)
# 毎フレーム打っているので補間設定は不要（PITFALL #1）


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)


def add_caption(body, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object
    tx.name = name
    tx.data.body = body
    tx.data.size = size
    tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。z=0.52/0.34/0.22。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.34), "logo")
study = add_caption("MIDDLE STUDY 029 — MATSUKASA", 0.045, (0.15, -1.3, 0.22), "study")


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
bpy.ops.object.camera_add(location=(0.55, -8.3, 1.95))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, CENTER_Z))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = rig
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
    # 幾何を数値で当てる（#18/#16）。開時の全体幅・z範囲、鱗片が開くと先端半径が増えるか、
    # 閉時に紡錘が鱗片付け根より内に収まるか。
    deps = bpy.context.evaluated_depsgraph_get()

    def world_bounds(objs, frame):
        scene.frame_set(frame)
        deps2 = bpy.context.evaluated_depsgraph_get()
        xs, zs = [], []
        for o in objs:
            oe = o.evaluated_get(deps2)
            for cc in oe.bound_box:
                w = oe.matrix_world @ Vector(cc)
                xs.append(w.x); zs.append(w.z)
        return xs, zs

    sc_objs = [s for (s, _) in scales]
    xs_o, zs_o = world_bounds(sc_objs, STILL_FRAME)   # 開
    persp = 8.3 / 8.3
    fw = (max(xs_o) - min(xs_o)) * persp
    print(f">> OPEN frame_w = {fw:.3f} / 2.81 ({fw / 2.81 * 100:.0f}%)   z-range = {min(zs_o):+.3f}..{max(zs_o):+.3f}")
    xs_c, zs_c = world_bounds(sc_objs, 1)             # 閉
    print(f">> CLOSED frame_w = {(max(xs_c)-min(xs_c)):.3f} ({(max(xs_c)-min(xs_c))/2.81*100:.0f}%)")
    # 鱗片先端の半径が開で増えるか（開き方向の符号チェック）
    scene.frame_set(1)
    deps_c = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME)
    deps_o = bpy.context.evaluated_depsgraph_get()
    S0 = scales[len(scales)//2][0]
    tip_local = Vector((0, SC_L, scale_cup(1.0)))
    rc = (S0.evaluated_get(deps_c).matrix_world @ tip_local)
    ro = (S0.evaluated_get(deps_o).matrix_world @ tip_local)
    rc_r = math.hypot(rc.x - rig.location.x, rc.y - rig.location.y)
    ro_r = math.hypot(ro.x - rig.location.x, ro.y - rig.location.y)
    print(f">> mid-scale tip radial: closed={rc_r:.3f} open={ro_r:.3f}  {'OK(開くと外へ)' if ro_r>rc_r else 'FAIL(符号逆・PHI反転せよ)'}")
    print(f">> spindle SP_R={SP_R:.3f} vs base r(T_LO)={ovoid_r(T_LO):.3f} r(0.5)={ovoid_r(0.5):.3f}  "
          f"{'OK(芯は鱗片の内)' if SP_R < ovoid_r(T_LO) else 'WARN(芯が付け根より太い)'}")
    print(f">> N_SCALES={N_SCALES} PHI_MAX={math.degrees(PHI_MAX):.0f} still={STILL_FRAME}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "matsukasa.blend"))
    print(">> saved .blend")

if "glb" in modes:
    # glTF は放射グラデ Emission ノード網で NaN を吐く（#25c）。書き出し直前に定数へ差し替え。
    try:
        for lk in list(core_bsdf.inputs["Emission Strength"].links):
            mat_core.node_tree.links.remove(lk)
        core_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> core emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = set(scale_names) | set(empty_names) | {"matsu_core", "matsu_cap_top", "matsu_cap_bot", "MatsuRig"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "matsukasa.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")

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

print(">> ALL DONE")
