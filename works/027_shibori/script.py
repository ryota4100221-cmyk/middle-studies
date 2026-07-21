# =============================================================
# monaka design. — MIDDLE STUDY 027 "SHIBORI"（絞 / 羽根絞り・aperture）
# 黒い羽根絞りが同心に開いては閉じる。閉じれば黒い円盤、開けば
# 中心の開口の奥から、ライム #A5E02E が満ち引きする。
# 真ん中——開口（あな）——に、光がある。
#
# 機構: 022 背表紙・023 器・024 扇で3回成功した「奥の凹面発光を開口
#   越しに覗かせる」手を円対称の絞りに応用＝緑棒罠（#13/#18）が構造的に
#   起きない（光源は奥、露出は開口の中の凹面ディッシュだけ）。
#   造形＝N=8 枚の黒い羽根（bmesh 実寸の環状セクタ板：内半径 R_IN から
#   外縁 R_OUT のアーク板）を、リム上に等配置した各自のピボットまわりに
#   回して中心に開口を作る（024 OUGI の放射を円対称の絞りに組み替え）。
#   φ=0 で内縁が全て R_IN ＝きれいな円開口（全開）、φ を増やすと各羽根が
#   ピボットまわりに旋回して内縁が中心へ寄り開口が閉じる。羽根は隣接と
#   角度的に重ねて（8×68°>360°）リムを黒い連続環にし白抜けを防ぐ（024 の重なり）。
#   光＝絞りの奥の発光ライム浅凹面ディッシュ（凹面をカメラ側へ・半径≧最大開口）。
#   凹面正対で面で光る（グレージング #19 回避）／広い凹パッチで点輝点にしない
#   （Glare箱 #11 回避）／凹面の勾配＋ホットコアでハローを残す（#24 ペンキ化回避）。
#   羽根の平面材は一様bright env で反射率支配＝Spec 0.10・Coat 0（#17-c）。
# リグ: 絞り中心の単一 Tilt-Empty（025 UZU 方式）の子に羽根/ディッシュを
#   local 原点中心・location=P_k で置き、羽根の rotation_euler.z=α_k+φ(t) を
#   親フレーム＝傾いた絞り法線まわりの回転にする（matrix_parent_inverse=
#   identity で #9 回避、object.scale/transform_apply 不使用 #15）。
#   羽根 k の object 変換は Translate(P_k)·Rz(α_k+φ)、mesh は blade0 を
#   ピボット原点にした実寸＝φ=0 で Rz(α_k)·blade0（O まわり回転）に一致。
# アニメ: φ(t)=φ_close·0.5(1+cos2πt)＝still(t=0.5) で全開・両端で全閉＝
#   数学的に完全ループ。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
#   env: ES_DISH SPEC_BLADE TILT_DEG PHI_CLOSE
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.50          # 絞りの視覚中心（シリーズ共通の画面中心付近）
TILT = math.radians(float(os.environ.get("TILT_DEG", "28")))  # 絞り面をカメラ側へ（開口の奥を見せる）
ROT_Z_RIG = math.radians(4.0)  # 全体をわずかに Z ひねり＝「撮った写真」に寄せる（010/017）

# --- 絞り羽根（直線コード＝circular segment 板） ---
# 各羽根の内縁＝直線コード（x=R_IN の接線）。リム上のピボット(R_PIV,0)まわりに
# 回すと、O からコードまでの距離 dist(φ)=R_PIV·cosφ−(R_PIV−R_IN) が減り、8枚の
# 半平面の交わり＝八角開口が縮む。cosφ=(R_PIV−R_IN)/R_PIV で dist=0＝完全に閉じる。
# 外縁のブレは固定の黒ベゼル環で隠す（実際のレンズ絞りと同じ）。
N_BLADES = 10            # 羽根の枚数。10＝隣接の重なりを厚くし閉時の羽根間スリット漏れを防ぐ（8だと漏れた）。開口は十角＝十分カメラの絞りに読める
R_OUT = 0.92            # ベゼル外縁半径＝全体の外半径（直径1.84 ＝ 実効横2.81 の65%・#18）
R_IN = 0.30            # 内縁コードの接線半径＝全開（φ=0）の開口の内接半径。中央の光の穴
R_BLADE_OUT = 0.52      # 羽根（circular segment）の外弧半径。小さく＝振り出しをベゼル内に収める
R_PIV = 0.46            # ピボット半径（内側寄り。振り出し半径 R_PIV+d_corner≈0.89<R_OUT でベゼル内に隠れる）
R_RING_IN = 0.47        # 固定ベゼル環の内半径（羽根外縁0.50を0.03重ねて隠し白抜け防止・穴は塞がない）
T_BLADE = 0.016         # 羽根の厚み（絞り法線方向 z）
PITCH_Z = 0.007         # 羽根を前後にわずかに積む（z-fight回避・実際の絞りの重ね）
RN_B = 8                # 羽根の半径分割
AN_B = 40               # 羽根の角度分割
# 開口 φ。φ=0 で全開（開口 R_IN）、φ_close で全閉（dist<0）。cosφ_close=(0.46-0.30)/0.46=0.348→69.6°。
PHI_CLOSE = math.radians(float(os.environ.get("PHI_CLOSE", "70.0")))  # 有限セグメントの中心被覆が最小開口になる最適角（scan で確定：0.010＝実質全閉）

# --- 奥の発光ライム凹面ディッシュ ---
R_DISH = 0.40           # 最大開口(R_IN=0.30)より広くベゼル穴(0.47)より狭い＝穴から常に覗き縁は羽根が隠す
DISH_DEPTH = 0.14       # 凹みの深さ（中心が最も奥・凹面をカメラ側へ／ホットコアを奥に隠す）
DISH_GAP = 0.09         # 羽根スタック（z 0..~0.05）より奥に置く rim の local z = -DISH_GAP
DISH_RN = 34
DISH_AN = 128

# --- マテリアル調整（env で hero スイープ） ---
ES_DISH = float(os.environ.get("ES_DISH", "2.6"))  # #24/#14改訂：中間調#A5E02E＋ホットコア＋ハロー。凹面で勾配が出る。hero で #14 測定してスイープ
SPEC_BLADE = float(os.environ.get("SPEC_BLADE", "0.10"))  # #17-c: 一様bright env下の黒平面は反射率支配

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 61         # t≈0.5 ＝ φ=0 ＝最も開いた瞬間


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


# 絞り羽根＝黒い平面板。一様に明るいグレー env（0.92・シリーズ不変）下では
# 鏡面反射が一様な灰色ヴェールになり roughness では消せない＝#17-c に従い
# 鏡面反射率そのもの（Specular IOR Level・Coat）を落とす。正対面は暗く沈み、
# 縁だけフレネルで明るく立つ＝黒い羽根がエッジの光でかたちを持つ。
mat_blade, b = make_principled("blade_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.35
b.inputs["Specular IOR Level"].default_value = SPEC_BLADE
b.inputs["Coat Weight"].default_value = 0.0

# 奥の発光ライム凹面ディッシュ。開口越しに key(1400W) を拾い得る → #13 に従い
# 純発光体として組む：Base Color を暗いライムに落として反射白の上乗せを消す。
# ★#24/#14 の要諦：均一発光（生の emission は view 非依存）だと core≒mid で勾配が
# 出ず「ペンキ」に退化する（1周目 std32.5・blown0）。Emission Strength を半径依存の
# 放射グラデにして中心をホットコアに白飛びさせ、縁を #A5E02E 域に落とす＝
# 「白い芯→#A5E02E→暗部」の勾配を作る（001 THE FILLING の光の作り）。
ES_CORE = float(os.environ.get("ES_CORE", "5.4"))   # 中心＝ホットコア（上位数%が白飛び）
ES_RIM = float(os.environ.get("ES_RIM", "1.7"))     # 縁＝中間調 #A5E02E 域
mat_dish, dish_bsdf = make_principled("dish_lime")
dish_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
dish_bsdf.inputs["Emission Color"].default_value = LIME
dish_bsdf.inputs["Roughness"].default_value = 0.5
dish_bsdf.inputs["Specular IOR Level"].default_value = 0.10
# --- 半径依存の Emission Strength（Generated 座標の中心からの距離でランプ） ---
_dt = mat_dish.node_tree
_tc = _dt.nodes.new("ShaderNodeTexCoord")
_sep = _dt.nodes.new("ShaderNodeSeparateXYZ")
_dt.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
_cx = _dt.nodes.new("ShaderNodeMath"); _cx.operation = 'SUBTRACT'; _cx.inputs[1].default_value = 0.5
_cy = _dt.nodes.new("ShaderNodeMath"); _cy.operation = 'SUBTRACT'; _cy.inputs[1].default_value = 0.5
_dt.links.new(_sep.outputs["X"], _cx.inputs[0])
_dt.links.new(_sep.outputs["Y"], _cy.inputs[0])
_cx2 = _dt.nodes.new("ShaderNodeMath"); _cx2.operation = 'MULTIPLY'
_cy2 = _dt.nodes.new("ShaderNodeMath"); _cy2.operation = 'MULTIPLY'
_dt.links.new(_cx.outputs[0], _cx2.inputs[0]); _dt.links.new(_cx.outputs[0], _cx2.inputs[1])
_dt.links.new(_cy.outputs[0], _cy2.inputs[0]); _dt.links.new(_cy.outputs[0], _cy2.inputs[1])
_sum = _dt.nodes.new("ShaderNodeMath"); _sum.operation = 'ADD'
_dt.links.new(_cx2.outputs[0], _sum.inputs[0]); _dt.links.new(_cy2.outputs[0], _sum.inputs[1])
_rad = _dt.nodes.new("ShaderNodeMath"); _rad.operation = 'SQRT'
_dt.links.new(_sum.outputs[0], _rad.inputs[0])
_mr = _dt.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 0.5     # Generated 半径0（中心）〜0.5（縁）
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
_dt.links.new(_rad.outputs[0], _mr.inputs["Value"])
_dt.links.new(_mr.outputs["Result"], dish_bsdf.inputs["Emission Strength"])

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


def add_bevel(o, width, segs=2):
    """PITFALL #10：全エッジ面取りは平面上に扇状ストリークを生む。鋭角のみに限定。"""
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = width
    bev.segments = segs
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)
    return bev


# ---------- 絞り羽根（circular segment 板・blade0 をピボット原点で作る） ----------
# blade0 ＝ 絞り座標のディスク(半径 R_BLADE_OUT) ∩ 半平面{x≥R_IN}（＝直線コード内縁）。
# 角度 a∈[-θ0,θ0]（θ0=acos(R_IN/R_BLADE_OUT)）ごとに r を rin(a)=R_IN/cos(a)（コードの極表現）
# から R_BLADE_OUT まで張る。頂点を P0=(R_PIV,0) だけ引いて object 原点＝ピボットに。
# 以降 location=P_k・rotation_euler.z=α_k+φ で φ=0 のとき Rz(α_k)·blade0（O まわり回転）に一致。
THETA0 = math.acos(R_IN / R_BLADE_OUT)


def build_blade(name):
    bm = bmesh.new()
    P0 = Vector((R_PIV, 0.0, 0.0))
    top = [[None] * (AN_B + 1) for _ in range(RN_B + 1)]
    bot = [[None] * (AN_B + 1) for _ in range(RN_B + 1)]
    for j in range(AN_B + 1):
        a = -THETA0 + 2 * THETA0 * j / AN_B
        rin = R_IN / math.cos(a)
        for i in range(RN_B + 1):
            r = rin + (R_BLADE_OUT - rin) * i / RN_B
            q = Vector((r * math.cos(a), r * math.sin(a), 0.0)) - P0
            top[i][j] = bm.verts.new((q.x, q.y, +T_BLADE / 2))
            bot[i][j] = bm.verts.new((q.x, q.y, -T_BLADE / 2))
    # 上下グリッド面
    for i in range(RN_B):
        for j in range(AN_B):
            bm.faces.new((top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]))
            bm.faces.new((bot[i][j], bot[i + 1][j], bot[i + 1][j + 1], bot[i][j + 1]))
    # 側壁（内縁・外縁・両側）
    for j in range(AN_B):  # 内縁 i=0
        bm.faces.new((top[0][j], bot[0][j], bot[0][j + 1], top[0][j + 1]))
    for j in range(AN_B):  # 外縁 i=RN_B
        bm.faces.new((top[RN_B][j + 1], bot[RN_B][j + 1], bot[RN_B][j], top[RN_B][j]))
    for i in range(RN_B):  # 側 j=0
        bm.faces.new((top[i][0], bot[i][0], bot[i + 1][0], top[i + 1][0]))
    for i in range(RN_B):  # 側 j=AN_B
        bm.faces.new((top[i + 1][AN_B], bot[i + 1][AN_B], bot[i][AN_B], top[i][AN_B]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_blade)
    add_bevel(o, 0.004)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        pass
    o.select_set(False)
    return o


blades = []
for k in range(N_BLADES):
    a_k = 2 * math.pi * k / N_BLADES
    o = build_blade(f"shibori_blade_{k:02d}")
    # ピボット P_k = R(α_k)·P0（rig local 座標。z は前後に薄く積む）
    o.location = (R_PIV * math.cos(a_k), R_PIV * math.sin(a_k), k * PITCH_Z)
    o.rotation_euler = (0.0, 0.0, a_k)  # φ=0（全開）。アニメで α_k+φ を打つ
    blades.append(o)


def a_k_of(k):
    return 2 * math.pi * k / N_BLADES


# ---------- 奥の発光ライム凹面ディッシュ（回転体・凹面をカメラ側へ） ----------
def build_dish(name):
    bm = bmesh.new()

    def dz(r):
        # 中心が最も奥（-DISH_DEPTH）・rim が 0。凹面が +z（カメラ側）を向く。
        return -DISH_DEPTH * (1.0 - (r / R_DISH) ** 2)

    pole = bm.verts.new((0.0, 0.0, dz(0.0)))
    rings = []
    for i in range(1, DISH_RN + 1):
        r = R_DISH * i / DISH_RN
        z = dz(r)
        ring = [bm.verts.new((r * math.cos(2 * math.pi * j / DISH_AN),
                              r * math.sin(2 * math.pi * j / DISH_AN), z))
                for j in range(DISH_AN)]
        rings.append(ring)
    for j in range(DISH_AN):
        j2 = (j + 1) % DISH_AN
        bm.faces.new((pole, rings[0][j], rings[0][j2]))
    for i in range(DISH_RN - 1):
        for j in range(DISH_AN):
            j2 = (j + 1) % DISH_AN
            bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_dish)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.9)
    except Exception:
        pass
    o.select_set(False)
    return o


dish = build_dish("shibori_dish")
dish.location = (0.0, 0.0, -DISH_GAP)  # 羽根スタックより奥（rig local）


# ---------- 黒い裏当てディスク（穴の奥の白背景抜けを止める保険） ----------
def build_backing(name):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, radius=R_OUT, segments=96, cap_ends=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_blade)
    return o


backing = build_backing("shibori_backing")
backing.location = (0.0, 0.0, -DISH_GAP - DISH_DEPTH - 0.03)


# ---------- 固定の黒ベゼル環（羽根の外縁のブレを隠し円形シルエットを作る） ----------
def build_bezel(name):
    bm = bmesh.new()
    inner = [bm.verts.new((R_RING_IN * math.cos(2 * math.pi * j / 96),
                           R_RING_IN * math.sin(2 * math.pi * j / 96), 0.0))
             for j in range(96)]
    outer = [bm.verts.new((R_OUT * math.cos(2 * math.pi * j / 96),
                           R_OUT * math.sin(2 * math.pi * j / 96), 0.0))
             for j in range(96)]
    for j in range(96):
        j2 = (j + 1) % 96
        bm.faces.new((inner[j], outer[j], outer[j2], inner[j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_blade)
    return o


bezel = build_bezel("shibori_bezel")
# 羽根スタック（z 0..~0.056）より前（＝カメラ側）に置き外縁を隠す
bezel.location = (0.0, 0.0, N_BLADES * PITCH_Z + 0.02)


# ---------- リグ（絞り中心の Tilt-Empty・025 UZU 方式） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "ShiboriRig"
rig.rotation_euler = (TILT, 0.0, ROT_Z_RIG)
for o in blades:
    o.parent = rig
dish.parent = rig
backing.parent = rig
bezel.parent = rig


# ---------- アニメーション（完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS


def phi_of(t01):
    # φ=0（全開）↔ φ_close（全閉）。still(t=0.5) で 0、両端で PHI_CLOSE。
    return PHI_CLOSE * 0.5 * (1 + math.cos(2 * math.pi * t01))


for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    phi = phi_of(t01)
    for k, o in enumerate(blades):
        o.rotation_euler.z = a_k_of(k) + phi
        o.keyframe_insert(data_path="rotation_euler", index=2, frame=f)
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


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。
# 3行目クリップ回避で z=0.52/0.34/0.22。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.34), "logo")
study = add_caption("MIDDLE STUDY 027 — SHIBORI", 0.045, (0.15, -1.3, 0.22), "study")


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
# 光は開口の奥の凹面ディッシュ自体が面光源＝点光源を足さない（024 と同じ判断・#19）。

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
cam.data.dof.focus_object = rig    # 絞り面（中心）に合焦
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
    # 開口半径（開/閉）と全体幅を数値で当てる（#18/#16）。羽根の被覆で開口を測る。
    def blade_covers(Q, a_k, phi):
        """絞り座標の点 Q(x,y) を羽根 k が覆うか。m=Rz(-(a+phi))(Q-P_k)、
        q0=m+P0 が blade0（ディスク∩{x≥R_IN}）内か。"""
        Pk = Vector((R_PIV * math.cos(a_k), R_PIV * math.sin(a_k)))
        d = Q - Pk
        ca, sa = math.cos(-(a_k + phi)), math.sin(-(a_k + phi))
        m = Vector((ca * d.x - sa * d.y, sa * d.x + ca * d.y))
        q0 = m + Vector((R_PIV, 0.0))
        return (q0.x >= R_IN - 1e-6) and (q0.length <= R_BLADE_OUT + 1e-6)

    def opening_radius(phi):
        """中心 O から、円周が全周とも無被覆でいられる最大半径＝開口半径。"""
        aks = [2 * math.pi * k / N_BLADES for k in range(N_BLADES)]
        r = 0.0
        while r < R_OUT:
            covered = False
            for j in range(180):
                ang = 2 * math.pi * j / 180
                Q = Vector((r * math.cos(ang), r * math.sin(ang)))
                if any(blade_covers(Q, ak, phi) for ak in aks):
                    covered = True
                    break
            if covered:
                return r
            r += 0.005
        return R_OUT

    op = opening_radius(0.0)
    cl = opening_radius(PHI_CLOSE)
    print(f">> opening: OPEN(phi=0)={op:.3f} (=R_IN {R_IN})  "
          f"CLOSED(phi={math.degrees(PHI_CLOSE):.0f})={cl:.3f}  (closed should be ~0)")
    # 羽根の最大振り出し半径（全 φ）。R_OUT を超えるとベゼル外へ飛び出す＝手裏剣化。
    max_exc = 0.0
    for step in range(41):
        phi = PHI_CLOSE * step / 40
        for k in range(N_BLADES):
            ak = 2 * math.pi * k / N_BLADES
            Pk = Vector((R_PIV * math.cos(ak), R_PIV * math.sin(ak)))
            # blade0 の外弧上の角（絞り座標で r=R_BLADE_OUT の両端）を追う
            for sgn in (-1, 1):
                a = sgn * THETA0
                q0 = Vector((R_BLADE_OUT * math.cos(a), R_BLADE_OUT * math.sin(a)))
                m = q0 - Vector((R_PIV, 0.0))
                c, s = math.cos(ak + phi), math.sin(ak + phi)
                w = Vector((c * m.x - s * m.y, s * m.x + c * m.y)) + Pk
                max_exc = max(max_exc, w.length)
    print(f">> max blade excursion = {max_exc:.3f}  (must be < R_OUT {R_OUT} to stay hidden by bezel): "
          f"{'OK' if max_exc < R_OUT else 'FAIL(手裏剣)'}")
    print(f">> R_DISH={R_DISH:.3f} must exceed OPEN opening {op:.3f}: "
          f"{'OK' if R_DISH > op else 'FAIL'}")
    # 全体幅（#18）：傾いた円盤の world x 範囲。tilt は X 軸まわりなので x 幅≒2·R_OUT。
    deps = bpy.context.evaluated_depsgraph_get()
    xs = []
    zs = []
    for o in blades + [dish]:
        oe = o.evaluated_get(deps)
        for cc in oe.bound_box:
            w = oe.matrix_world @ Vector(cc)
            xs.append(w.x)
            zs.append(w.z)
    persp = 8.3 / (8.3 - 0.0)
    fw = (max(xs) - min(xs)) * persp
    print(f">> frame_w = {fw:.3f} / 2.81 ({fw / 2.81 * 100:.0f}%)   "
          f"z-range = {min(zs):+.3f}..{max(zs):+.3f}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "shibori.blend"))
    print(">> saved .blend")

if "glb" in modes:
    # glTF は放射グラデの Emission ノード網を表現できず NaN を吐く（#3 の教訓と同系）。
    # GLB は 3D モデル納品物なので、書き出し直前にディッシュ発光を定数に差し替える。
    try:
        for lk in list(dish_bsdf.inputs["Emission Strength"].links):
            mat_dish.node_tree.links.remove(lk)
        dish_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> dish emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {o.name for o in blades} | {"shibori_dish", "shibori_backing"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "shibori.glb"),
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
