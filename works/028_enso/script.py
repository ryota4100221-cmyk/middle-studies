# =============================================================
# monaka design. — MIDDLE STUDY 028 "ENSO"（円相 / 一円相）
# 黒い一筆の円相（禅の丸）が宙に浮く。円の内＝空（くう）に、
# ライム #A5E02E の光が呼吸する——満ちて筆の内縁まで上がり、
# また種火まで退く。
# 円の真ん中は空（無）で、その空こそ、光がある場所。
# ＝タグライン "Designing the Middle of Your Story." の最も直接な立体化。
#
# 機構: 円環パス（半径 R_ENSO・θ0〜θ0+SWEEP=約325°で35°の「円相の開き」を残す）に
#   沿って平たい筆リボン（radial 幅 × 薄い z ＝ flat brush）を bmesh 掃引。筆圧
#   プロファイル taper(u)＝入りは細く→太り→終いは細くフリック（#21 の両端テーパーを
#   筆致に）＋わずかな半径ゆらぎで「墨の一筆」に読ませる。光＝円中央の発光ライム浅凹面
#   ディッシュ（027 と同じ半径依存の放射グラデ Emission＝中心ホットコア→#A5E02E→暗部の
#   勾配で #24 ペンキ化を回避／広い凹パッチで #11 Glare箱回避／凹面で直視の白ベタを
#   防ぐ #25b）＋随伴する柔らかいライム点光源（#22＝面積で稼ぎ強度で稼がない・弱め）。
# アニメ: 満ち引き＝ディッシュの object.scale を種火(SEED_S)→満(1.0)にアニメ（023
#   UTSUWA と同じ transform 駆動＝glb にアニメが乗る）＋点光源エネルギーを同期。
#   b(t)=0.5(1−cos2πt)＝still(t=0.5) で満・両端で種火＝完全ループ。円相はカメラに
#   正対（TILT 小）なので満ち引きが正面から全部見える（#20 の深い器問題が起きない）。
# 素材: 筆リボンは一様bright env 下の平面黒＝Spec 0.10・Coat 0（#17-c）でエッジの
#   フレネルだけで形を持たせ黒を黒に保つ。リグ＝円相中心の単一 Tilt-Empty（025/027）。
#   造形で object.scale/transform_apply 不使用（#15）。裏当ての黒ディスクで開きの奥の
#   白背景抜けを止める。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
#   env: ES_DISH ES_CORE ES_RIM GLOW_E TILT_DEG SEED_S
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

CENTER_Z = 1.50          # 円相の視覚中心（シリーズ共通の画面中心付近）
# 円相は平たい円環＝「紙に描いた円」なので、カメラに正対して立たせる（＝XY面で作った環を
# X軸まわり 90° 起こして法線を -Y＝カメラ側へ向ける）。TILT はそこからの「後傾」＝上を少し
# 奥へ倒して立体感と凹面ディッシュのわずかな覗き込みを作る（大きくすると平皿に転ぶので小さく）。
TILT = math.radians(float(os.environ.get("TILT_DEG", "3")))   # 垂直からの後傾（3°＝ほぼ完全正対＝平らな墨に読ませ bowl 化を防ぐ）
ROT_Z_RIG = math.radians(2.0)  # 全体をわずかに Z ひねり＝「撮った写真」に寄せる（010/017）

# --- 円相の筆リボン（円環パスに沿った平たい墨の一筆） ---
R_ENSO = 0.78            # 円相の半径（直径1.56 ＝ 実効横2.81 の55%・#18）
W_MAX = 0.070            # 筆リボンの最大 radial 半幅（筆の腹）。抑揚で変わる
Z_RATIO = 0.038          # z 半厚 / radial 半幅＝ほぼ2次元の平らな墨（3D の巻いたリボンに見せない）
SWEEP = math.radians(308.0)   # 一筆で描く角度＝52°の大きな「円相の開き」（一目で円相と分かる）
TH0 = math.radians(81.0)      # 起点（太い筆の入り）＝上。開きは 29〜81°＝右上に来る
SEG = 300                # 掃引分割（滑らかな筆致）
WOBBLE = 0.028           # 半径のゆらぎ（手描きの円の歪み・見えるくらいに）
WOBBLE_N = 2.0           # ゆらぎの周期

# --- 中央の発光ライム凹面ディッシュ（満ち引きする空の光） ---
R_DISH = 0.64            # 満（scale=1）時の半径。筆の内縁 R_ENSO−W_MAX≈0.708 の内に収める
DISH_DEPTH = 0.06        # 浅い凹み（中心が奥・凹面をカメラ側へ／ホットコアを奥に隠す #25b）
DISH_Z = -0.03           # 筆リボン（z≈0）よりわずかに奥（rig local）
DISH_RN = 34
DISH_AN = 128
SEED_S = float(os.environ.get("SEED_S", "0.52"))  # 種火（引き切った時の最小 scale）。点にせず広い光の溜まりに保つ＝#11 の Glare 十字を構造回避（0.34 では十字が残った）

# --- マテリアル調整（env で hero スイープ） ---
ES_CORE = float(os.environ.get("ES_CORE", "3.0"))  # 中心＝ホットコア（上位数%だけ白飛び）#25b
ES_RIM = float(os.environ.get("ES_RIM", "0.16"))   # 縁＝暗部へ落とす（中心→#A5E02E→暗の勾配・std を上げる）
SPEC_BLADE = float(os.environ.get("SPEC_BLADE", "0.10"))  # #17-c: 一様bright env下の黒平面は反射率支配
GLOW_E = float(os.environ.get("GLOW_E", "9.0"))    # 随伴ライム点光源（#22＝弱め・面積で稼ぐ）

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 61         # t≈0.5 ＝ 満（光が円の内縁まで満ちた瞬間）


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


# 円相の筆＝黒い墨のリボン。一様に明るいグレー env（0.92・シリーズ不変）下では
# 鏡面反射が一様な灰色ヴェールになり roughness では消せない＝#17-c に従い鏡面反射率
# そのもの（Specular IOR Level・Coat）を落とす。正対面は暗く沈み、縁だけフレネルで
# 明るく立つ＝黒い筆致がエッジの光でかたちを持つ（墨のマットさとも整合）。
mat_ink, b = make_principled("enso_ink")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.60   # 墨のマットさ（艶を消す）
b.inputs["Specular IOR Level"].default_value = SPEC_BLADE
b.inputs["Coat Weight"].default_value = 0.0

# 中央の発光ライム凹面ディッシュ。#13 に従い純発光体（Base Color を暗いライムに落として
# 反射白の上乗せを消す）。★#24/#25b の要諦：生の emission は view 非依存で core≒mid＝
# 勾配が出ず「ペンキ」に退化する。Emission Strength を半径依存の放射グラデにして中心を
# ホットコアに白飛びさせ縁を #A5E02E 域に落とす＝「白い芯→#A5E02E→暗部」の勾配（001 の光）。
mat_dish, dish_bsdf = make_principled("enso_dish")
dish_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
dish_bsdf.inputs["Emission Color"].default_value = LIME
dish_bsdf.inputs["Roughness"].default_value = 0.5
dish_bsdf.inputs["Specular IOR Level"].default_value = 0.10
# --- 半径依存の Emission Strength（Generated 座標の中心からの距離でランプ・027 と同一） ---
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


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def brush_taper(u):
    """筆圧プロファイル：太い筆の入り→抑揚しながら掃く→末は掠れて細いフリック（#21）。
    純対称テーパーは機械的なので、はっきり見える thick/thin の抑揚を足す。"""
    entry = 0.28 + 0.72 * smooth01(u / 0.09)                 # 入り＝細く筆が触れて太る 0.28 → 1.0（角ばった tab を避ける）
    exitf = 1.0 - 0.93 * smooth01((u - 0.76) / 0.24)         # 終い＝末24%で掠れて細いフリック 1.0 → 0.07
    # 一筆の中の抑揚（墨の載り・運筆速度）。複数の正弦で円周を通して太い所／細い所を作る
    press = 1.0 + 0.24 * math.sin(2 * math.pi * (1.2 * u + 0.10)) \
                - 0.17 * math.sin(2 * math.pi * (2.3 * u + 0.40)) \
                + 0.09 * math.sin(2 * math.pi * (3.7 * u + 0.15))
    return max(0.06, min(entry, exitf) * press)


# ---------- 円相の筆リボン（円環パスに沿った平たい墨の掃引） ----------
def build_enso(name):
    bm = bmesh.new()
    # 各断面 u に 4 頂点（radial ±hw、z ±hz）。u に沿って side/cap を張る。
    rings = []   # rings[j] = (v_ro_t, v_ri_t, v_ri_b, v_ro_b) 4頂点（外radial上/内radial上/内下/外下）
    for j in range(SEG + 1):
        u = j / SEG
        th = TH0 + SWEEP * u
        rr = R_ENSO * (1.0 + WOBBLE * math.sin(WOBBLE_N * 2 * math.pi * u + 0.7))
        tp = brush_taper(u)
        hw = W_MAX * tp
        hz = W_MAX * Z_RATIO * tp
        rad = Vector((math.cos(th), math.sin(th), 0.0))  # radial 方向
        c = rr * rad
        v_ro_t = bm.verts.new((c.x + hw * rad.x, c.y + hw * rad.y, +hz))
        v_ri_t = bm.verts.new((c.x - hw * rad.x, c.y - hw * rad.y, +hz))
        v_ri_b = bm.verts.new((c.x - hw * rad.x, c.y - hw * rad.y, -hz))
        v_ro_b = bm.verts.new((c.x + hw * rad.x, c.y + hw * rad.y, -hz))
        rings.append((v_ro_t, v_ri_t, v_ri_b, v_ro_b))
    for j in range(SEG):
        a = rings[j]
        b2 = rings[j + 1]
        # 4 側面（top / inner / bottom / outer）を四角形で張る
        bm.faces.new((a[0], a[1], b2[1], b2[0]))  # top
        bm.faces.new((a[1], a[2], b2[2], b2[1]))  # inner
        bm.faces.new((a[2], a[3], b2[3], b2[2]))  # bottom
        bm.faces.new((a[3], a[0], b2[0], b2[3]))  # outer
    # 両端のキャップ（入り・終い）
    s, e = rings[0], rings[SEG]
    bm.faces.new((s[0], s[3], s[2], s[1]))
    bm.faces.new((e[1], e[2], e[3], e[0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_ink)
    add_bevel(o, 0.0016)  # 角をごくわずか丸めるだけ（平らな墨の帯を保つ）
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.9)
    except Exception:
        pass
    o.select_set(False)
    return o


enso = build_enso("enso_stroke")


# ---------- 中央の発光ライム凹面ディッシュ（回転体・凹面をカメラ側へ／027 と同一） ----------
def build_dish(name):
    bm = bmesh.new()

    def dz(r):
        return -DISH_DEPTH * (1.0 - (r / R_DISH) ** 2)  # 中心が最も奥・凹面が +z（カメラ側）

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


dish = build_dish("enso_dish")
dish.location = (0.0, 0.0, DISH_Z)


# ---------- 暗い内側の空（うつろ）＝裏当てディスク ----------
# ★半径は筆の帯の「内〜中」に収める（R_ENSO＝筆の中線）。筆の外縁(≈0.86)より内なので
#   シルエットは筆そのものが白背景に立ち、開き（gap）も背景に抜けて読める。かつディッシュ
#   (0.64)より広いので、光が引くと内側は暗い空になり「闇から光が満ちる」落差が出る（023）。
def build_backing(name):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, radius=R_ENSO, segments=96, cap_ends=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_ink)
    return o


backing = build_backing("enso_backing")
backing.location = (0.0, 0.0, DISH_Z - DISH_DEPTH - 0.04)


# ---------- リグ（円相中心の Tilt-Empty・025/027 方式） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "EnsoRig"
# X=90° で XY面の環が立ってカメラ(-Y)に正対。TILT だけ後傾させ face をわずかに上から見せる。
rig.rotation_euler = (math.radians(90.0) - TILT, 0.0, ROT_Z_RIG)
enso.parent = rig
dish.parent = rig
backing.parent = rig


# ---------- 随伴ライム点光源（満ち引きを黒い筆内縁に照り返す・#22 弱め） ----------
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
glow = bpy.context.active_object
glow.name = "enso_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.shadow_soft_size = 0.6
glow.parent = rig
glow.location = (0.0, 0.0, DISH_Z + 0.10)  # ディッシュ手前でディッシュ縁と筆の内縁を洗う


# ---------- アニメーション（完全ループ・満ち引き） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS


def breath(t01):
    # b=0（種火）↔ 1（満）。still(t=0.5) で 1、両端で 0＝完全ループ。
    return 0.5 * (1.0 - math.cos(2 * math.pi * t01))


for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    b = breath(t01)
    s = SEED_S + (1.0 - SEED_S) * b           # ディッシュ scale：種火→満
    dish.scale = (s, s, s)
    dish.keyframe_insert(data_path="scale", frame=f)
    glow.data.energy = GLOW_E * (0.14 + 0.86 * b)   # 光量を同期（種火でも僅かに灯る）
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


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。
# 3行目クリップ回避で z=0.52/0.34/0.22。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.34), "logo")
study = add_caption("MIDDLE STUDY 028 — ENSO", 0.045, (0.15, -1.3, 0.22), "study")


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
cam.data.dof.focus_object = rig    # 円相面（中心）に合焦
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
    # 幾何を数値で当てる（#18/#16）。筆の内縁とディッシュ満径の関係、全体幅、z範囲。
    inner_edge = R_ENSO - W_MAX
    print(f">> stroke inner edge = {inner_edge:.3f}  vs  R_DISH(full) = {R_DISH:.3f}  "
          f"{'OK(光は筆の内に収まる)' if R_DISH < inner_edge else 'FAIL(光が筆を越える)'}")
    print(f">> gap = {360 - math.degrees(SWEEP):.0f} deg  at theta0 = {math.degrees(TH0):.0f} deg")
    deps = bpy.context.evaluated_depsgraph_get()
    xs = []
    zs = []
    for o in (enso, dish):
        oe = o.evaluated_get(deps)
        for cc in oe.bound_box:
            w = oe.matrix_world @ Vector(cc)
            xs.append(w.x)
            zs.append(w.z)
    persp = 8.3 / (8.3 - 0.0)
    fw = (max(xs) - min(xs)) * persp
    print(f">> frame_w = {fw:.3f} / 2.81 ({fw / 2.81 * 100:.0f}%)   "
          f"z-range = {min(zs):+.3f}..{max(zs):+.3f}")
    print(f">> breath: seed_scale={SEED_S}  still={STILL_FRAME} (t=0.5=満)")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "enso.blend"))
    print(">> saved .blend")

if "glb" in modes:
    # glTF は放射グラデの Emission ノード網を表現できず NaN を吐く（#25c）。
    # GLB は 3D モデル納品物なので、書き出し直前にディッシュ発光を定数に差し替える。
    try:
        for lk in list(dish_bsdf.inputs["Emission Strength"].links):
            mat_dish.node_tree.links.remove(lk)
        dish_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> dish emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {"enso_stroke", "enso_dish", "enso_backing"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "enso.glb"),
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
