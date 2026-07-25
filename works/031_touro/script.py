# =============================================================
# monaka design. — MIDDLE STUDY 031 "TOURO"（灯籠 / 石灯籠 stone garden lantern）
# 黒い石灯籠が宙に浮く。火袋（灯りの部屋）の窓の奥から ライム #A5E02E が満ち引きする
# ＝灯籠の炎が真ん中で息づく。真ん中＝火袋に、光がある。
#
# 機構: 最も堅牢な「黒い部屋＋窓＋奥の発光を息づかせる」（004 ANDON の籠＝#11回避・
#   028/030 の呼吸ディッシュ系）を、新ドメイン＝建築・庭園（石灯籠）に適用。
#   造形＝bmesh実寸の石灯籠を縦に積む（基礎→竿＋節→中台→火袋→笠→露盤→宝珠）。
#   火袋＝六角の6本の隅柱＋上下の石板で、柱間の6面が開いた「窓」（boolean不要・030の
#   隅タイル方式の柱版／object.scale・transform_apply 不使用 #15）＝奥の発光を多数の窓から
#   分散して覗かせ Glare箱 #11 を構造回避（004/019/024/030）。
#   光＝火袋内に立てた発光ライムの縦ロゼンジ（純発光体 #13）。solid の塊を窓越しに見るので
#   #27 通り camera が覗く縦軸に沿った1次元バンドグラデ Emission（Generated Z の |z-0.5|
#   →MapRange＝火袋中央高さをホットコアに白飛び・上下へ暗部＝「白い芯→#A5E02E→暗部」の
#   縦勾配で #24ペンキ化回避）＋随伴ライム点光源（#22）で内壁・笠裏を洗う。火袋背後に黒い
#   裏当て板（窓抜けの白背景を止める #26②/#28）。
# アニメ: 発光ロゼンジを object.scale で呼吸（種火 SEED_S=0.6 の広い溜まり #26③→満）
#   ＝灯籠の炎の息づき。b(t)=0.5(1−cos2πt)＝still(t=0.5) で満・両端で種火＝完全ループ。
#   glb に scale が乗る（#23/#28）。
# 素材: 石は一様bright env 下の黒平面＝Spec 低・Coat 0（#17-c）でマット石に、フレネルの縁で
#   形を持たせ黒を黒に保つ。リグ＝灯籠中心の単一 Tilt-Empty（025/027/028）。建築モチーフは
#   3Dボリュームなのでシリーズ標準カメラのまま、YAW の3/4視で正面＋側面の2窓を灯す（寝かせない）。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
#   env: ES_CORE ES_RIM GLOW_E TILT_DEG YAW_DEG SEED_S SPEC_STONE
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

CENTER_Z = 1.72          # 灯籠（火袋）の world 位置。look より上に置き画面上寄りに＝頭上の余白を締め台座を字幕から離す
LOOK_Z = 1.48            # カメラ注視点（火袋のわずか下）。CENTER_Z と分離して bottom-heavy な灯籠を上へ寄せる
TILT = math.radians(float(os.environ.get("TILT_DEG", "2")))    # 笠の天面をわずかに覗かせる（立体物なので寝かせない・ほぼ直立）
YAW = math.radians(float(os.environ.get("YAW_DEG", "20")))     # 3/4視＝正面＋側面の2窓を見せる／フレーム右の余白へ

# --- 火袋（六角・隅柱＋上下石板・6面が窓） ---
R_FB = 0.34              # 火袋の六角 circumradius（中心→頂点）
HF = 0.30               # 火袋の半高（z: -HF..+HF）
PLATE_T = 0.065         # 上下石板の厚み
POST_H = 0.055          # 隅柱の断面半幅（正方形断面）
SPEC_STONE = float(os.environ.get("SPEC_STONE", "0.06"))  # #17-c: 一様bright env 下の黒石平面は反射率支配（笠の傾斜面がプラ光沢に転ぶので低く）

# --- 火袋内の発光ライム「光の塊」＝火袋と同軸の六角プリズム（炎で満ちた部屋）---
# 球だと窓の奥に「裸の緑玉」として浮く（#13/#18）。火袋と同じ六角の光の塊にして各窓を
# 面で満たす＝「灯りのパネル」に読ませる（004 ANDON の灯り）。窓開口幅(≈側長-2柱)より広い面で塞ぐ。
CORE_R = 0.25           # 光の塊の六角 circumradius（窓を面で満たす・柱の内側に収める）
CORE_HZ = 0.205         # 垂直半高（火袋内 HF-PLATE_T 内に収める）

# --- 火袋背後の黒い裏当て板（窓抜けの白背景を止める・#26②/#28）---
BACK_R = 0.30           # 火袋の apothem(≈0.294) を覆う
BACK_Y = 0.24           # ロゼンジ(半径0.155)の奥・火袋 back 面(apothem≈0.294)の内側

# --- マテリアル調整（env で hero スイープ） ---
ES_CORE = float(os.environ.get("ES_CORE", "6.2"))   # 火袋中央＝ホットコア（白飛びさせハローを出す）#25b/#24/#27
ES_RIM = float(os.environ.get("ES_RIM", "0.40"))    # 上下端＝暗部へ落とす（縦勾配で std を上げる）
GLOW_E = float(os.environ.get("GLOW_E", "10.0"))    # 随伴ライム点光源（窓越しに床へ光をこぼす・#22。塊にほぼ遮蔽されるので弱め）

SEED_S = float(os.environ.get("SEED_S", "0.60"))    # 種火 scale（点にせず広い溜まりに・#26③/#11）

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 61         # t≈0.5 ＝ 満（炎が最も満ちた瞬間）


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


# 石（灯籠本体）＝マットな黒石。一様bright env（0.92・シリーズ不変）下では鏡面反射が一様な
# 灰色ヴェールになり roughness では消せない＝#17-c に従い鏡面反射率そのもの（Specular IOR
# Level・Coat）を落とす。正対面は暗く沈み、縁だけフレネルで明るく立って石の稜線が出る。
mat_stone, b = make_principled("touro_stone")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.62
b.inputs["Specular IOR Level"].default_value = SPEC_STONE
b.inputs["Coat Weight"].default_value = 0.0

# 裏当て黒板（窓の奥が見る黒）。灯籠石と同じ黒・反射さらに低。
mat_back, b = make_principled("touro_back")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.55
b.inputs["Specular IOR Level"].default_value = 0.06
b.inputs["Coat Weight"].default_value = 0.0

# 炎の芯＝発光ライム縦ロゼンジ。#13 純発光体（Base を暗ライムに落とし反射白の上乗せを消す）。
# #24/#25b/#27：生の emission は view 非依存で core≒mid＝勾配が出ず「ペンキ」に退化する。solid の
# 塊を窓越しに見るので、Emission Strength を「camera が覗く縦軸（Generated Z）の |z-0.5|」に
# 依存させた1次元バンドグラデにして、火袋中央高さをホットコアに白飛びさせ上下端を暗部へ落とす
# ＝「白い芯→#A5E02E→暗部」の縦勾配（#27 の solid 塊の正しい適用）。
mat_core, core_bsdf = make_principled("touro_core")
core_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.10
_ct = mat_core.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
# dz = Z-0.5（ロゼンジは縦・Generated Z が縦軸）。|dz| が中央(0)→端(0.5)。
_dz = _ct.nodes.new("ShaderNodeMath"); _dz.operation = 'SUBTRACT'; _dz.inputs[1].default_value = 0.5
_ct.links.new(_sep.outputs["Z"], _dz.inputs[0])
_abz = _ct.nodes.new("ShaderNodeMath"); _abz.operation = 'ABSOLUTE'
_ct.links.new(_dz.outputs[0], _abz.inputs[0])
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 0.46   # 中央(0)→ホットコア／上下端(≈0.5)→暗部
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
_ct.links.new(_abz.outputs[0], _mr.inputs["Value"])
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


# ---------- ジオメトリ・ヘルパ（PITFALL #15：bmesh実寸・object.scale/transform_apply不使用） ----------
def new_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def shade_flat(o):
    for p in o.data.polygons:
        p.use_smooth = False


def breath(t01):
    return 0.5 * (1.0 - math.cos(2 * math.pi * t01))


def hexpts(radius, cx=0.0, cy=0.0):
    """六角の6頂点 (x,y)。頂点を 60°*i に置くと -Y(=270°)に flat 面が向く（カメラへ平面窓）。"""
    return [(cx + radius * math.cos(math.radians(60 * i)),
             cy + radius * math.sin(math.radians(60 * i))) for i in range(6)]


def add_hex_prism(bm, r_bot, r_top, z0, z1, cap_bot=True, cap_top=True):
    """六角フラスタム（solid）を z0..z1 に。r_bot/r_top で台形テーパー。"""
    bot = [bm.verts.new((x, y, z0)) for (x, y) in hexpts(r_bot)]
    top = [bm.verts.new((x, y, z1)) for (x, y) in hexpts(r_top)]
    for i in range(6):
        j = (i + 1) % 6
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    if cap_bot:
        bm.faces.new(list(reversed(bot)))
    if cap_top:
        bm.faces.new(top)
    return bot, top


def add_cyl(bm, r_bot, r_top, z0, z1, seg=40, cap_bot=True, cap_top=True):
    """円錐台（竿・節・宝珠台などの丸物）。"""
    bot = [bm.verts.new((r_bot * math.cos(2 * math.pi * j / seg),
                         r_bot * math.sin(2 * math.pi * j / seg), z0)) for j in range(seg)]
    top = [bm.verts.new((r_top * math.cos(2 * math.pi * j / seg),
                         r_top * math.sin(2 * math.pi * j / seg), z1)) for j in range(seg)]
    for j in range(seg):
        k = (j + 1) % seg
        bm.faces.new((bot[j], bot[k], top[k], top[j]))
    if cap_bot:
        bm.faces.new(list(reversed(bot)))
    if cap_top:
        bm.faces.new(top)
    return bot, top


def add_post(bm, cx, cy, z0, z1, half):
    """火袋の隅柱＝正方形断面の縦柱を (cx,cy) 中心に z0..z1。"""
    s = half
    corners = [(cx - s, cy - s), (cx + s, cy - s), (cx + s, cy + s), (cx - s, cy + s)]
    bot = [bm.verts.new((x, y, z0)) for (x, y) in corners]
    top = [bm.verts.new((x, y, z1)) for (x, y) in corners]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)


# ---------- 石灯籠本体（1つの bmesh に積層） ----------
# ローカル z は火袋中央=0。全パーツを実寸で作り、リグ(CENTER_Z)が持ち上げる。
def build_lantern(name):
    bm = bmesh.new()

    zt = HF                 # 火袋 天面
    zb = -HF                # 火袋 底面

    # ① 火袋（火の袋）：上下の六角石板＋6本の隅柱＝柱間の6面が窓
    add_hex_prism(bm, R_FB, R_FB, zt - PLATE_T, zt)          # 天板
    add_hex_prism(bm, R_FB, R_FB, zb, zb + PLATE_T)          # 底板
    for (vx, vy) in hexpts(R_FB):                            # 6頂点に隅柱
        add_post(bm, vx, vy, zb + PLATE_T, zt - PLATE_T, POST_H)

    # ② 中台（火袋を受ける台・少し広い六角盤）
    mt0 = zb - 0.11
    add_hex_prism(bm, 0.40, 0.36, mt0, zb)                   # 上に向かってすぼむ
    add_hex_prism(bm, 0.30, 0.40, mt0 - 0.05, mt0)          # 下の受け（反り）

    # ③ 竿（柱）＋節（2つの膨らみ）
    sh_top = mt0 - 0.05
    sh_bot = -1.03          # 竿を短めに＝bottom-heavy を抑え台座を字幕帯から持ち上げる
    add_cyl(bm, 0.11, 0.105, sh_bot, sh_top, cap_bot=False, cap_top=False)  # 本体
    for zc in (sh_bot + (sh_top - sh_bot) * 0.34, sh_bot + (sh_top - sh_bot) * 0.68):
        add_cyl(bm, 0.135, 0.135, zc - 0.028, zc + 0.028)   # 節（リング状の膨らみ）

    # ④ 基礎（台座・反花＝下すぼみの六角ドラム＋足）
    add_hex_prism(bm, 0.34, 0.30, sh_bot - 0.16, sh_bot)    # ドラム
    add_hex_prism(bm, 0.40, 0.34, sh_bot - 0.24, sh_bot - 0.16)  # 反り出す足（最下＝-1.44）

    # ⑤ 笠（屋根）：広い軒スラブ＋六角の屋根錐（軒を反らせる）
    ea0 = zt
    add_hex_prism(bm, 0.56, 0.54, ea0, ea0 + 0.055)         # 軒スラブ（最も広い＝シルエット幅）
    # 軒の6隅をわずかに持ち上げて反り（蕨手）を示唆
    add_hex_prism(bm, 0.52, 0.16, ea0 + 0.055, ea0 + 0.30)  # 屋根の傾斜面（錐）

    # ⑥ 露盤（屋根上の小箱）＋宝珠（頂の玉）
    add_hex_prism(bm, 0.11, 0.10, ea0 + 0.30, ea0 + 0.35)   # 露盤
    add_cyl(bm, 0.10, 0.055, ea0 + 0.35, ea0 + 0.40)       # 請花（すぼむ）
    # 宝珠（玉）＝縦ラティスの小球
    jb_z, jb_r = ea0 + 0.40, 0.075
    jc = bm.verts.new((0, 0, jb_z + jb_r * 2))
    prev = None
    seg = 20
    for ri in range(1, 7):
        th = math.pi * ri / 7
        z = jb_z + jb_r * (1 - math.cos(th))
        rr = jb_r * math.sin(th)
        ring = [bm.verts.new((rr * math.cos(2 * math.pi * j / seg),
                              rr * math.sin(2 * math.pi * j / seg), z)) for j in range(seg)]
        if ri == 1:
            for j in range(seg):
                bm.faces.new((jc, ring[j], ring[(j + 1) % seg]))
        else:
            for j in range(seg):
                k = (j + 1) % seg
                bm.faces.new((prev[j], ring[j], ring[k], prev[k]))
        prev = ring

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_stone)
    shade_flat(o)
    return o


# ---------- 炎の芯＝発光ライム六角プリズム（火袋と同軸・窓を面で満たす／#27縦バンドグラデ） ----------
def build_core(name):
    bm = bmesh.new()
    # 火袋の六角と同じ向き（hexpts）で光の塊を作る＝各窓の奥に flat 面が正対して窓を満たす。
    add_hex_prism(bm, CORE_R, CORE_R, -CORE_HZ, CORE_HZ)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_core)
    shade_flat(o)
    return o


# ---------- 火袋背後の黒い裏当て板（窓抜けの白背景を止める・#26②/#28） ----------
def build_backing(name):
    bm = bmesh.new()
    seg = 48
    cen = bm.verts.new((0.0, BACK_Y, 0.0))
    ring = [bm.verts.new((BACK_R * math.cos(2 * math.pi * j / seg), BACK_Y,
                          BACK_R * math.sin(2 * math.pi * j / seg))) for j in range(seg)]
    for j in range(seg):
        k = (j + 1) % seg
        bm.faces.new((cen, ring[j], ring[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_back)
    shade_flat(o)
    return o


# ---------- リグ（灯籠中心の Tilt-Empty・025/027/028 方式） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "TouroRig"
rig.rotation_euler = (TILT, 0.0, YAW)


def child_of(obj, parent, basis=None):
    """parent 付け＋ matrix_parent_inverse=identity（#9）。"""
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix()
    if basis is not None:
        obj.matrix_basis = basis
    return obj


lantern = build_lantern("touro_stone")
child_of(lantern, rig, Matrix.Translation((0, 0, 0)))

core = build_core("touro_core")
child_of(core, rig, Matrix.Translation((0, 0, 0)))

backing = build_backing("touro_back")
child_of(backing, rig, Matrix.Translation((0, 0, 0)))

# 随伴ライム点光源（芯の光を火袋の内壁・笠裏に照り返す・#22）。火袋中央に。
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
glow = bpy.context.active_object
glow.name = "touro_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.shadow_soft_size = 0.5
child_of(glow, rig, Matrix.Translation((0, 0, 0)))


# ---------- アニメーション（完全ループ・炎の息づき＝芯 scale） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    bt = breath(t01)
    s = SEED_S + (1.0 - SEED_S) * bt        # 種火(0.6)→満(1.0)
    core.scale = (s, s, s)
    core.keyframe_insert(data_path="scale", frame=f)
    glow.data.energy = GLOW_E * (0.14 + 0.86 * bt)
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
study = add_caption("MIDDLE STUDY 031 — TOURO", 0.045, (0.15, -1.3, 0.22), "study")


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
look = Vector((0.1, 0, LOOK_Z))
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
    # 幾何を数値で当てる（#18/#16）。全体の縦横（#18 の 55〜65%）、浮遊（基礎が床から浮くか）、
    # 火袋の窓（apothem）を裏当てが覆うか、を確認。
    verts_z = [(-1.03 - 0.24), (HF + 0.40 + 0.075 * 2)]  # 基礎最下(sh_bot-0.24) .. 宝珠頂
    world_bot = CENTER_Z + verts_z[0]
    world_top = CENTER_Z + verts_z[1]
    height = verts_z[1] - verts_z[0]
    width = 2 * 0.56   # 軒スラブ径＝シルエット最大幅
    apo = R_FB * math.cos(math.radians(30))   # 火袋 flat 面までの距離（apothem）
    print(f">> height = {height:.3f} / 3.52 ({height/3.52*100:.0f}%)   width(eave) = {width:.3f} / 2.81 ({width/2.81*100:.0f}%)")
    print(f">> world z: base_bottom={world_bot:.3f} ({'OK 浮遊' if world_bot > 0.03 else 'WARN 床にめり込み'})  finial_top={world_top:.3f}  firebox_center={CENTER_Z:.3f}")
    print(f">> firebox R_FB={R_FB:.3f} apothem={apo:.3f}  backing R={BACK_R:.3f} ({'OK 窓を覆う' if BACK_R >= apo else 'WARN 窓抜け→白背景'})")
    print(f">> core rosenji: R={CORE_R:.3f} HZ={CORE_HZ:.3f}  firebox内高={HF-PLATE_T:.3f} ({'OK 収まる' if CORE_HZ <= HF-PLATE_T else 'WARN 芯が石板を突き抜け'})")
    print(f">> SEED_S={SEED_S} ES_CORE={ES_CORE} ES_RIM={ES_RIM} GLOW_E={GLOW_E}  TILT={math.degrees(TILT):.0f} YAW={math.degrees(YAW):.0f}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "touro.blend"))
    print(">> saved .blend")

if "glb" in modes:
    # glTF は放射/バンドグラデ Emission ノード網で NaN を吐く（#25c）。書き出し直前に定数へ差し替え。
    try:
        for lk in list(core_bsdf.inputs["Emission Strength"].links):
            mat_core.node_tree.links.remove(lk)
        core_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> core emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {"touro_stone", "touro_core", "touro_back", "TouroRig"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "touro.glb"),
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
