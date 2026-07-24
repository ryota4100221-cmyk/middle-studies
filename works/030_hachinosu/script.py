# =============================================================
# monaka design. — MIDDLE STUDY 030 "HACHINOSU"（蜂の巣 / honeycomb）
# 黒い蜂の巣がカメラに正対して浮く。外周の房（セル）は黒いまま、巣の中心＝
# 真ん中の房から ライム #A5E02E の光が満ち、また退く。真ん中に、光がある。
#
# 機構: 028 ENSO で確立した「発光ディッシュを黒いモチーフの奥に置き object.scale で
#   満ち引きさせる（glbに乗る）」＋ 019 AYA・024 OUGI の「黒い格子/覆いの奥の発光面を
#   多数の隙間から分散して覗かせ Glare箱 #11 を構造回避」を、六角テッセレーションに合成。
#   造形＝pointy-top 六角セルを axial 座標で R_RINGS 分（61房）配置。各房は「外六角→内六角の
#   連続前面シート（黒・穴あき）＋内六角を奥へ押し出した筒壁（房の深さ）」。隣接房の外縁が
#   正確にタイルして一枚の穴あき黒板になる（bmesh実寸・remove_doubles で溶接／
#   object.scale・transform_apply 不使用 #15）。3層（カメラ=-Y→+Y）：
#     ①黒い蜂の巣壁（y∈[-WALL_D,0]・窓が開く）
#     ②発光ライムの浅凹ディッシュ（y≈+0.03・半径≦巣・028/027 の 2D放射グラデ Emission
#       ＝中心ホットコア→#A5E02E→暗部で #24 ペンキ化回避／#25b 凹面でホットコアを奥に隠す）
#     ③黒い裏当て板（y≈+0.5・巣より広く全房を覆い白背景の抜けを止める＝#26② の逆用）
#   → 外周の房は裏当ての黒を、中心の房はディッシュの光を見る＝六角形の光の粒に量子化。
# アニメ: ディッシュを scale (SEED_S→1.0) で呼吸＋随伴ライム点光源を同期。
#   b(t)=0.5(1−cos2πt)＝still(t=0.5) で満・両端で種火＝完全ループ。glb に scale が乗る。
# 素材: 巣壁は一様bright env 下の平面黒＝Spec 0.10・Coat 0（#17-c）でエッジのフレネルだけで
#   形を持たせ黒を黒に保つ。リグ＝巣中心の Tilt-Empty（025/027/028）。#26 の平面モチーフ則に
#   従い ほぼ正対（rig X≈14°＝窓の奥の筒壁を少し覗かせ 3D honeycomb に読ませる・寝かせない）。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
#   env: ES_CORE ES_RIM GLOW_E TILT_DEG SEED_S HR WALL_D SPEC_WALL
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

CENTER_Z = 1.50          # 巣の視覚中心（シリーズ共通の画面中心付近）
TILT = math.radians(float(os.environ.get("TILT_DEG", "14")))   # 上を少しカメラへ倒し筒壁を覗かせる（寝かせない・#26）
ROT_Z_RIG = math.radians(4.0)  # フレームの空いている右側へわずかに（#18）

# --- 蜂の巣（六角格子）---
# 六角パッチは横長（左右が corner・上下が flat）で、丸いディッシュ/裏当てと形が合わず
# 端でスピルする（#16 で発覚）。→ 房を円でクリップして丸い蜂の巣にし、外周は固定の黒ベゼル環
# （SHIBORI #25② と同じ「実レンズの黒バレル」）で締める＝ディッシュ/裏当ての端も隠れ縁が clean。
HR = float(os.environ.get("HR", "0.110"))       # 房の外六角 circumradius（中心→頂点）
R_RINGS = 5                                      # クリップ前のリング数（余分に作り円で抜く）
R_CLIP = float(os.environ.get("R_CLIP", "0.70"))  # この半径内に中心がある房だけ残す＝丸い蜂の巣
IWALL = 0.80                                     # 内六角＝HR·IWALL（窓）。1-IWALL が壁の太さ
WALL_D = float(os.environ.get("WALL_D", "0.038"))  # 房の深さ（筒壁・カメラへ -Y に押し出す）。深すぎると外周の筒壁がシルエット端で"タブ"に飛び出す（#16）
# --- 固定の黒ベゼル環（外周を締め・丸いディッシュ/裏当ての端を隠す・SHIBORI #25②）---
R_BZ_IN = float(os.environ.get("R_BZ_IN", "0.735"))   # ベゼル内縁（蜂の巣の外周を少し食う）
R_BZ_OUT = float(os.environ.get("R_BZ_OUT", "0.830"))  # ベゼル外縁＝clean な円シルエット
SPEC_WALL = float(os.environ.get("SPEC_WALL", "0.10"))  # #17-c: 一様bright env 下の黒平面は反射率支配

# --- 奥の発光ライム凹ディッシュ（芯の光）---
# 満(still・scale=1.0)で全房を覆い蜂の巣全体を灯す（放射グラデで中心ホット・縁は暗ライム＝
# 「外は黒」に近い）。呼吸で scale が縮むと光が中心へ退き、外周房は裏当ての黒を見せる＝
# 光が中心から満ちて外へ広がるループ。DISH_R は巣前面(≈0.872)の内・win_reach(0.85)以上に。
DISH_R = float(os.environ.get("DISH_R", "0.720"))  # 満で内側の房を覆う（< ベゼル内縁 0.735 で隠れる）
DISH_Y = 0.030           # 巣の背後（+Y）。壁 back(y=0) のすぐ奥
DISH_CONCAVE = 0.060     # 中心を奥へ凹ませホットコアを隠す（#25b・浅く＝ボウル化 #26 回避）
DISH_RN, DISH_AN = 22, 84

# --- 裏当て黒板（白背景抜け止め）---
# #26②：裏当てを巣の外周より大きくするとシルエットが黒ディスクに堕ちモチーフが埋もれる。
# → 外周の窓を覆う最小限（巣とほぼ同径）に収め、巣の背後に隠す＝シルエットは六角パッチ本体。
BACK_R = 0.800           # 全窓を覆う（端はベゼルが前から隠す）
BACK_Y = 0.135           # ディッシュ凹み最深(≈0.09)の奥・巣のすぐ背後

# --- マテリアル調整（env で hero スイープ） ---
ES_CORE = float(os.environ.get("ES_CORE", "6.4"))   # 中心＝ホットコア（白飛びさせハローを出す）#25b/#24
ES_RIM = float(os.environ.get("ES_RIM", "0.22"))    # 縁＝暗部へ落とす（外周房を暗ライム＝ほぼ黒に・勾配で std を上げる）
GLOW_E = float(os.environ.get("GLOW_E", "22.0"))    # 随伴ライム点光源（房の内壁をライムに洗う）

SEED_S = float(os.environ.get("SEED_S", "0.50"))    # 種火 scale（点にせず広い溜まりに・#26③/#11）

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 61         # t≈0.5 ＝ 満（中心の房群が光で満ちた瞬間）


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


# 巣壁＝黒い蜂の巣。一様bright env（0.92・シリーズ不変）下では鏡面反射が一様な灰色ヴェールに
# なり roughness では消せない＝#17-c に従い鏡面反射率そのもの（Specular IOR Level・Coat）を落とす。
# 正対面は暗く沈み、窓の内壁エッジだけフレネルで明るく立って honeycomb の凹凸が出る。
mat_wall, b = make_principled("hachi_wall")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.50
b.inputs["Specular IOR Level"].default_value = SPEC_WALL
b.inputs["Coat Weight"].default_value = 0.0

# 裏当て黒板（外周の房が見る黒）。巣壁と同じ黒。
mat_back, b = make_principled("hachi_back")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.55
b.inputs["Specular IOR Level"].default_value = 0.06
b.inputs["Coat Weight"].default_value = 0.0

# 芯の発光ライム凹ディッシュ。#13 純発光体（Base を暗ライムに落とし反射白の上乗せを消す）。
# #24/#25b：生の emission は view 非依存で core≒mid＝勾配が出ず「ペンキ」に退化する。
# Emission Strength を 2D放射グラデ（Generated の中心距離→MapRange）にして中心をホットコアに
# 白飛びさせ縁を #A5E02E 域に落とす＝「白い芯→#A5E02E→暗部」の勾配。ディッシュは薄い凹シェルで
# 視認面＝凹んだ内側が Generated 中心（半径0＝ホットコア）に近い＝#25b の正しい適用条件。
mat_core, core_bsdf = make_principled("hachi_core")
core_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.10
_ct = mat_core.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
# dx=X-0.5, dz=Z-0.5（ディッシュは XZ 平面・厚みは Y）
_dx = _ct.nodes.new("ShaderNodeMath"); _dx.operation = 'SUBTRACT'; _dx.inputs[1].default_value = 0.5
_ct.links.new(_sep.outputs["X"], _dx.inputs[0])
_dz = _ct.nodes.new("ShaderNodeMath"); _dz.operation = 'SUBTRACT'; _dz.inputs[1].default_value = 0.5
_ct.links.new(_sep.outputs["Z"], _dz.inputs[0])
_x2 = _ct.nodes.new("ShaderNodeMath"); _x2.operation = 'MULTIPLY'
_ct.links.new(_dx.outputs[0], _x2.inputs[0]); _ct.links.new(_dx.outputs[0], _x2.inputs[1])
_z2 = _ct.nodes.new("ShaderNodeMath"); _z2.operation = 'MULTIPLY'
_ct.links.new(_dz.outputs[0], _z2.inputs[0]); _ct.links.new(_dz.outputs[0], _z2.inputs[1])
_sum = _ct.nodes.new("ShaderNodeMath"); _sum.operation = 'ADD'
_ct.links.new(_x2.outputs[0], _sum.inputs[0]); _ct.links.new(_z2.outputs[0], _sum.inputs[1])
_sqrt = _ct.nodes.new("ShaderNodeMath"); _sqrt.operation = 'POWER'; _sqrt.inputs[1].default_value = 0.5
_ct.links.new(_sum.outputs[0], _sqrt.inputs[0])
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 0.46   # 中心(0)→ホットコア／縁(≈0.5)→暗部
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
_ct.links.new(_sqrt.outputs[0], _mr.inputs["Value"])
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


def shade_flat(o):
    # 蜂の巣の壁は角を立てたいのでフラット（六角のエッジをくっきり）
    for p in o.data.polygons:
        p.use_smooth = False


def breath(t01):
    return 0.5 * (1.0 - math.cos(2 * math.pi * t01))


# ---------- 六角格子（pointy-top・axial 座標）の房中心 ----------
def hex_centers():
    """中心が半径 R_CLIP 内にある房中心 (cx, cz) を返す（XZ 平面）＝丸い蜂の巣。"""
    cs = []
    for q in range(-R_RINGS, R_RINGS + 1):
        for r in range(-R_RINGS, R_RINGS + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) > R_RINGS:
                continue
            cx = math.sqrt(3.0) * HR * (q + r / 2.0)
            cz = 1.5 * HR * r
            if math.hypot(cx, cz) > R_CLIP:
                continue
            cs.append((cx, cz))
    return cs


def hex_corner(cx, cz, radius, i):
    """pointy-top 六角の頂点 i（-30°始点で 60° 刻み）。XZ 平面。"""
    ang = math.radians(60.0 * i - 30.0)
    return (cx + radius * math.cos(ang), cz + radius * math.sin(ang))


# ---------- 蜂の巣壁を単一 bmesh で構築 ----------
# 各房：①前面シート（外六角→内六角の穴あき環・y=-WALL_D、カメラ側）
#        ②窓の筒壁（内六角を y=-WALL_D..0 に押し出す＝房の深さ）
# 隣接房の外縁は正確にタイルするので remove_doubles で一枚の穴あき黒板に溶接される。
def build_comb(name):
    bm = bmesh.new()
    yf = -WALL_D  # 前面（カメラ側）
    yb = 0.0      # 背面
    rin = HR * IWALL
    for (cx, cz) in hex_centers():
        outer_f, inner_f, inner_b = [], [], []
        for i in range(6):
            ox, oz = hex_corner(cx, cz, HR, i)
            ix, iz = hex_corner(cx, cz, rin, i)
            outer_f.append(bm.verts.new((ox, yf, oz)))
            inner_f.append(bm.verts.new((ix, yf, iz)))
            inner_b.append(bm.verts.new((ix, yb, iz)))
        for i in range(6):
            j = (i + 1) % 6
            # ① 前面の環（外→内・穴あきシート）
            bm.faces.new((outer_f[i], outer_f[j], inner_f[j], inner_f[i]))
            # ② 窓の筒壁（前 inner → 背 inner）
            bm.faces.new((inner_f[i], inner_f[j], inner_b[j], inner_b[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_wall)
    shade_flat(o)
    return o


# ---------- 発光凹ディッシュ（薄シェル・XZ 平面・-Y 側=カメラへ凹）----------
def build_dish(name):
    bm = bmesh.new()

    def yy(rr):  # 半径 rr での y（中心を奥へ凹ませる＝ホットコアを隠す #25b）
        return DISH_Y + DISH_CONCAVE * (1.0 - (rr / DISH_R) ** 2)

    cen = bm.verts.new((0.0, yy(0.0), 0.0))
    rings = []
    for ri in range(1, DISH_RN + 1):
        rr = DISH_R * ri / DISH_RN
        y = yy(rr)
        ring = [bm.verts.new((rr * math.cos(2 * math.pi * j / DISH_AN), y,
                              rr * math.sin(2 * math.pi * j / DISH_AN)))
                for j in range(DISH_AN)]
        rings.append(ring)
    for j in range(DISH_AN):
        j2 = (j + 1) % DISH_AN
        bm.faces.new((cen, rings[0][j], rings[0][j2]))
    for i in range(len(rings) - 1):
        for j in range(DISH_AN):
            j2 = (j + 1) % DISH_AN
            bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_core)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    o.select_set(False)
    return o


# ---------- 固定の黒ベゼル環（外周を締め・丸いディッシュ/裏当ての端を隠す・SHIBORI #25②）----------
def build_bezel(name):
    bm = bmesh.new()
    seg = 96
    yb = -WALL_D - 0.004   # 蜂の巣前面のさらにわずか手前（前から端を隠す）
    inn, out = [], []
    for j in range(seg):
        a = 2 * math.pi * j / seg
        inn.append(bm.verts.new((R_BZ_IN * math.cos(a), yb, R_BZ_IN * math.sin(a))))
        out.append(bm.verts.new((R_BZ_OUT * math.cos(a), yb, R_BZ_OUT * math.sin(a))))
    for j in range(seg):
        j2 = (j + 1) % seg
        bm.faces.new((inn[j], out[j], out[j2], inn[j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_wall)
    shade_flat(o)
    return o


# ---------- 裏当て黒板（白背景抜け止め）----------
def build_backing(name):
    bm = bmesh.new()
    seg = 64
    cen = bm.verts.new((0.0, BACK_Y, 0.0))
    ring = [bm.verts.new((BACK_R * math.cos(2 * math.pi * j / seg), BACK_Y,
                          BACK_R * math.sin(2 * math.pi * j / seg))) for j in range(seg)]
    for j in range(seg):
        j2 = (j + 1) % seg
        bm.faces.new((cen, ring[j], ring[j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_back)
    shade_flat(o)
    return o


# ---------- リグ（巣中心の Tilt-Empty・025/027/028 方式） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "HachiRig"
rig.rotation_euler = (TILT, 0.0, ROT_Z_RIG)


def child_of(obj, parent, basis=None):
    """parent 付け＋ matrix_parent_inverse=identity（#9）。"""
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix()
    if basis is not None:
        obj.matrix_basis = basis
    return obj


comb = build_comb("hachi_comb")
child_of(comb, rig, Matrix.Translation((0, 0, 0)))

dish = build_dish("hachi_core")
child_of(dish, rig, Matrix.Translation((0, 0, 0)))

backing = build_backing("hachi_back")
child_of(backing, rig, Matrix.Translation((0, 0, 0)))

bezel = build_bezel("hachi_bezel")
child_of(bezel, rig, Matrix.Translation((0, 0, 0)))

# 随伴ライム点光源（ディッシュ光を房の内壁に照り返す・#22）。ディッシュのすぐ奥に。
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
glow = bpy.context.active_object
glow.name = "hachi_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.shadow_soft_size = 0.6
child_of(glow, rig, Matrix.Translation((0, 0.22, 0)))


# ---------- アニメーション（完全ループ・満ち引き＝ディッシュ scale） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    bt = breath(t01)
    s = SEED_S + (1.0 - SEED_S) * bt        # 種火(0.5)→満(1.0)
    dish.scale = (s, 1.0, s)                # XZ 面内でスケール（厚み Y は不変）
    dish.keyframe_insert(data_path="scale", frame=f)
    glow.data.energy = GLOW_E * (0.12 + 0.88 * bt)
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
study = add_caption("MIDDLE STUDY 030 — HACHINOSU", 0.045, (0.15, -1.3, 0.22), "study")


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
    # 幾何を数値で当てる（#18/#16）。巣の全体幅（#18 の 55〜65%）、房数、
    # 満(still)でのディッシュ world 半径 < 巣半径（白背景スピル回避 #26②）を確認。
    cs = hex_centers()
    fw = 2 * R_BZ_OUT   # 見かけのシルエット径＝ベゼル外縁
    win_reach = max(math.hypot(cx, cz) for (cx, cz) in cs) + HR * IWALL
    dish_full = DISH_R * (SEED_S + (1 - SEED_S) * 1.0)   # 満(still)での world 半径
    dish_seed = DISH_R * SEED_S
    print(f">> N_cells = {len(cs)} (R_CLIP={R_CLIP})   HR={HR:.3f} WALL_D={WALL_D:.3f}")
    print(f">> silhouette Ø(bezel) = {fw:.3f} / 2.81 ({fw / 2.81 * 100:.0f}%)   bezel {R_BZ_IN:.3f}..{R_BZ_OUT:.3f}")
    print(f">> window circumradius = {HR*IWALL:.3f}  win_reach = {win_reach:.3f}")
    print(f">> dish R: seed={dish_seed:.3f} full={dish_full:.3f}  vs bezel_in={R_BZ_IN:.3f}  "
          f"{'OK(満でもベゼル内に隠れる)' if dish_full <= R_BZ_IN else 'WARN(ディッシュがベゼル内縁を越える→緑スピル)'}")
    print(f">> BACK_R={BACK_R:.3f}  {'OK(窓を覆う)' if BACK_R >= win_reach else 'WARN(窓抜け→白背景)'}  "
          f"{'OK(端はベゼルが隠す)' if BACK_R <= R_BZ_OUT else 'WARN(裏当てがベゼル外に出る)'}")
    print(f">> layers y: bezel={-WALL_D-0.004:.3f} comb[{-WALL_D:.3f}..0] dish~{DISH_Y:.3f} back={BACK_Y:.3f}  ES_CORE={ES_CORE} ES_RIM={ES_RIM}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hachinosu.blend"))
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
    keep = {"hachi_comb", "hachi_core", "hachi_back", "hachi_bezel", "HachiRig"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "hachinosu.glb"),
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
