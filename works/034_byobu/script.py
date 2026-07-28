# =============================================================
# monaka design. — MIDDLE STUDY 034 "BYOUBU"（屏風 / 二曲一双 a pair of folding screens）
# 黒い屏風が一双、向かい合って立つ。二隻のあいだ＝真ん中の一条だけ、
# 奥から ライム #A5E02E が差す。屏風は畳まれ、また開く。光の筋は動かない。
#
# 機構: シリーズ初の「ヒンジ連鎖（アコーディオン）＝折り」。各扇は隣の扇の縁を蝶番に
#   して折れ、折り角 φ(t)=PHI_MID+PHI_AMP·sin(2πt) が**数学的に完全ループ**する
#   （sin なので t=0 と t=1 が厳密に一致・毎フレームキー #1）。畳まれる（φ大）と
#   内側の扇がカメラ側へ振り出て真ん中の隙間を狭め、開く（φ小）と光が広がる＝
#   **機構がそのまま光の強弱になる**。022 HON（2枚の見開き＋綴じ目の光）とは別物
#   （こちらは4扇のジグザグ＋二隻の"あいだ"の光）。028/030/031 の呼吸ループを
#   032/033 で2作止めたので、ここでも発光は一定＝物体の運動だけで語る。
#   造形＝扇は bmesh 実寸の「框（かまち）＋一段落ちた紙の面」（#17-b：素材の差が
#   階層を生む＝框は半艶・紙はマット）。object.scale / transform_apply 不使用（#15）、
#   親子付けもせず各扇に location+rotation_euler を直接キーする（#9 と整合）。
#   光＝#29 の正典どおり「開口と同軸・同形の発光プリズム」＝隙間より広い縦の
#   発光スラブを D_EM=0.20m 奥に置いて隙間を**面で満たす**（裸の緑板 #13/#18 回避）。
#   奥行き 0.20m が斜めからの視線を幾何で遮るので、光は正面で最も明るく側面へ自然に閉じる。
#   Emission は #27 通り「camera が覗く縦軸（Generated Z）の1次元バンドグラデ」＝
#   屏風の中ほどの高さをホットコアに白飛びさせ上下へ暗部（白い芯→#A5E02E→暗部 #24）。
#   発光スラブは全高でなく中央 52% だけ（全長に走らせると暗いライム画素が中間調を
#   沈める＝#31-d）。奥に黒い裏当て板を置いて白背景の抜けを止める（#26②/#28）。
# 素材: 一様bright env 下の**平らな面**は鏡面反射率が支配項（#17-c）＝Spec 低・Coat 0 で
#   黒を黒に保ち、縁だけフレネルで立たせる。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
#   env: ES_CORE ES_RIM FALLOFF GLOW_E SPEC_PAPER GAP D_EM HW_EM PHI_MID PHI_AMP W H
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_byobu")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.63          # 屏風の中心の world 高さ
LOOK_Z = 1.58            # カメラ注視点

# --- 屏風（二曲一双＝2扇 × 2隻） ---
NPAN = 3                                                   # 1隻に入る扇の数（三曲一双）
W = float(os.environ.get("W", "0.310"))                    # 扇1枚の幅
H = float(os.environ.get("H", "1.68"))                     # 屏風の高さ
T = 0.030                                                  # 扇の厚み
FR = float(os.environ.get("FR", "0.030"))                  # 框（かまち）の幅
FR_B = float(os.environ.get("FR_B", "0.050"))              # 下框は太い＝1秒で「調度」に読ませる（#16）
RC = 0.016                                                 # 紙の面の落ち込み（框より一段奥）
GAP = float(os.environ.get("GAP", "0.080"))                # 二隻のあいだ＝真ん中の隙間

PHI_MID = math.radians(float(os.environ.get("PHI_MID", "54")))   # 折り角の中央値
PHI_AMP = math.radians(float(os.environ.get("PHI_AMP", "12")))   # 折り角の振れ幅

SPEC_PAPER = float(os.environ.get("SPEC_PAPER", "0.08"))   # #17-c：平面×一様bright env は反射率が支配項
ROUGH_PAPER = 0.55                                         # #17-b：紙はマット
SPEC_FRAME = 0.13                                          # 框はわずかに照らせて階層を作る
ROUGH_FRAME = 0.33

# --- 光（隙間と同軸・同形の発光スラブ／#29） ---
# 1周目は D_EM=0.20 と「発光は中央52%だけ」で組んだが、隙間の上端から白背景が抜けた
# （視線はカメラが上にあるぶん奥へ行くほど上がるので、奥に置くほど抜け代が増える）。
# → スラブを浅く（0.105）・屏風の全高に伸ばし、暗い側を ES_RIM≈0 まで落として
#   スラブ自身を裏当てに兼用する。中間調が沈む問題（#31-d）は「発光体を短くする」
#   のではなく「暗い側を黒に落としてライム画素として数えさせない」で解いた。
D_EM = float(os.environ.get("D_EM", "0.060"))              # 隙間の面からの奥行き（斜めの視線を幾何で遮る）
TE = 0.030                                                 # スラブの肉厚
HW_EM = float(os.environ.get("HW_EM", "0.260"))            # スラブの半幅（隙間より広い＝面で満たす・扇の内側に隠れる）
H_EM = H + 0.012                                            # 屏風より僅かに高い（上端の抜け止め）
EM_Z_OFF = -0.002                                            # 上下端で幅を絞る帯（#21・はみ出しを針状にして消す）

ES_CORE = float(os.environ.get("ES_CORE", "5.0"))          # 中ほどの高さ＝ホットコア（白飛びさせハローを出す）#24/#27
ES_RIM = float(os.environ.get("ES_RIM", "0.0"))           # 上下の端＝ほぼ黒（裏当てを兼ねる）
FALLOFF = float(os.environ.get("FALLOFF", "0.34"))         # ホットコア→暗部の落ち幅（world m）
GLOW_E = float(os.environ.get("GLOW_E", "0.9"))            # 隙間からこぼれる光（框・床へのスピル）#22

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 1          # t=0 ＝ φ=PHI_MID（中庸の折り＝屏風がいちばん屏風に見える一枚）


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 折りの数式（ヒンジ連鎖＝完全ループ） ----------
def phi_at(t01):
    """折り角。sin なので t=0 と t=1 が厳密に一致＝数学的に閉じる。"""
    return PHI_MID + PHI_AMP * math.sin(2 * math.pi * t01)


def chain(phi, side):
    """1隻ぶんのヒンジ連鎖を解く。side=+1 が右隻、-1 が左隻（鏡像）。
    扇 i の向き d_i は ∓φ/2 の交互＝ジグザグ。真ん中の縁（x=±GAP/2, y=0）が
    いちばん奥＝二隻のあいだが「谷」になり、外へ行くほどカメラ側へ振り出る。
    戻り値: [(location_xy, rotation_z), ...]"""
    out = []
    x, y = side * GAP / 2, 0.0
    for i in range(NPAN):
        d = (-1.0 if i % 2 == 0 else 1.0) * phi / 2          # 右隻の向き
        rot = d if side > 0 else math.pi - d                 # 左隻は鏡像
        out.append(((x, y), rot))
        x += W * math.cos(rot)
        y += W * math.sin(rot)
    return out


def half_width(phi):
    """φ における屏風全体の幅（#18：実効フレーム横 2.81 に対して測る）。"""
    return GAP + 2 * NPAN * W * math.cos(phi / 2)


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


# 紙の面（一段落ちた本紙）。#17-b：紙はマット／#17-c：平面は反射率を落として黒を黒に保つ
mat_paper, b = make_principled("byobu_paper")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_PAPER
b.inputs["Specular IOR Level"].default_value = SPEC_PAPER
b.inputs["Coat Weight"].default_value = 0.0

# 框（かまち）＝縁の木。紙とわずかに質感を変えて「縁／面」の階層を作る（#17-b）
mat_frame, b = make_principled("byobu_frame")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_FRAME
b.inputs["Specular IOR Level"].default_value = SPEC_FRAME
b.inputs["Coat Weight"].default_value = 0.05

# 光＝隙間と同形の発光スラブ。#13 純発光体。ここでは Base を**純黒**にする——
# 暗ライム(#13の既定値)だと、随伴のライム点光源がその拡散面を照らして
# 「暗部が均一な暗オリーブのベタ塗り」＝#24 のペンキ signature になった（3周目で発覚）。
# Base=0 なら ES が 0 に落ちた領域は完全な黒＝裏当てとして働く。
mat_core, core_bsdf = make_principled("byobu_light")
core_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.0

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：bmesh実寸・object.scale/transform_apply不使用） ----------
def new_object(name, bm, mats):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    for m in mats:
        o.data.materials.append(m)
    return o


def add_bevel(o, width=0.0028):
    """#10：ANGLE 制限で鋭角の辺だけ面取り（平面上の辺は除外）。
    #17-c の「縁だけフレネルで立つ」を効かせるための微ベベル。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)


# ---------- 扇（框＋一段落ちた紙の面／単一の閉じたソリッド） ----------
def build_panel(name):
    """ローカル原点＝扇の「左の蝶番の辺」。x∈[0,W] / y∈[-T/2,T/2] / z∈[-H/2,H/2]。
    面が重ならないよう、前面は「框の額縁4枚＋落ち込みの側壁4枚＋本紙1枚」で組む
    （箱を重ねると同一平面が z-fight する）。"""
    bm = bmesh.new()
    yf, yb, yr = -T / 2, T / 2, -T / 2 + RC
    xo0, xo1, zo0, zo1 = 0.0, W, -H / 2, H / 2
    xi0, xi1, zi0, zi1 = FR, W - FR, -H / 2 + FR_B, H / 2 - FR   # 下框だけ太い

    def ring(x0, x1, z0, z1, y):
        return [bm.verts.new((x0, y, z0)), bm.verts.new((x1, y, z0)),
                bm.verts.new((x1, y, z1)), bm.verts.new((x0, y, z1))]

    Of, Ob = ring(xo0, xo1, zo0, zo1, yf), ring(xo0, xo1, zo0, zo1, yb)
    If, Ir = ring(xi0, xi1, zi0, zi1, yf), ring(xi0, xi1, zi0, zi1, yr)

    def quad(a, b_, c, d, mi):
        f = bm.faces.new((a, b_, c, d))
        f.material_index = mi

    for i in range(4):
        j = (i + 1) % 4
        quad(Of[i], Of[j], Ob[j], Ob[i], 1)      # 側面（木口）
        quad(Of[i], Of[j], If[j], If[i], 1)      # 前面の框
        quad(If[i], If[j], Ir[j], Ir[i], 1)      # 落ち込みの側壁
    quad(Ob[0], Ob[1], Ob[2], Ob[3], 1)          # 背面
    quad(Ir[0], Ir[1], Ir[2], Ir[3], 0)          # 本紙（一段奥）

    o = new_object(name, bm, [mat_paper, mat_frame])
    add_bevel(o)
    return o


panels = []
for s, tag in ((1, "R"), (-1, "L")):
    for i in range(NPAN):
        panels.append((build_panel("byobu_%s%d" % (tag, i + 1)), s, i))


# ---------- 光（隙間と同軸・同形の発光スラブ／#29） ----------
def em_hw(u):
    """スラブの半幅（world z の関数）。屏風の縁の内側までは満幅、はみ出す僅かな
    ぶんだけ細らせて「黒いタブ」に見せない。u∈[0,1]"""
    z = (u - 0.5) * H_EM + EM_Z_OFF
    inner = H / 2 - 0.030
    if abs(z) <= inner:
        return HW_EM
    x = min(1.0, (abs(z) - inner) / (H_EM / 2 + abs(EM_Z_OFF) - inner))
    return HW_EM * (1 - x) + 0.070 * x


def build_light(name):
    bm = bmesh.new()
    nz = 64
    y0, y1 = D_EM - TE / 2, D_EM + TE / 2
    front, back = [], []
    for i in range(nz + 1):
        u = i / nz
        z = (u - 0.5) * H_EM + EM_Z_OFF
        hw = em_hw(u)
        front.append((bm.verts.new((-hw, y0, z)), bm.verts.new((hw, y0, z))))
        back.append((bm.verts.new((-hw, y1, z)), bm.verts.new((hw, y1, z))))
    for i in range(nz):
        a, b_ = front[i]
        c, d = front[i + 1]
        a2, b2 = back[i]
        c2, d2 = back[i + 1]
        bm.faces.new((a, b_, d, c))
        bm.faces.new((a2, b2, d2, c2))
        bm.faces.new((a, c, c2, a2))
        bm.faces.new((b_, b2, d2, d))
    bm.faces.new((front[0][0], front[0][1], back[0][1], back[0][0]))
    bm.faces.new((front[nz][0], front[nz][1], back[nz][1], back[nz][0]))
    return new_object(name, bm, [mat_core])


light = build_light("byobu_light")
light.location = (0.0, 0.0, CENTER_Z)

# Emission Strength ＝ Generated Z の1次元バンドグラデ（#27）。
# 屏風の中ほどの高さ（Generated z=0.5）をホットコアに白飛びさせ、FALLOFF[m] で暗部へ落とす。
GZ_C = 0.5
GZ_F = FALLOFF / H_EM
_ct = mat_core.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
_dz = _ct.nodes.new("ShaderNodeMath")
_dz.operation = 'SUBTRACT'
_dz.inputs[1].default_value = GZ_C
_ct.links.new(_sep.outputs["Z"], _dz.inputs[0])
_abz = _ct.nodes.new("ShaderNodeMath")
_abz.operation = 'ABSOLUTE'
_ct.links.new(_dz.outputs[0], _abz.inputs[0])
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = GZ_F
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = ES_RIM
_mr.clamp = True
_ct.links.new(_abz.outputs[0], _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], core_bsdf.inputs["Emission Strength"])

# 隙間からこぼれる光（框・床へのスピル・#22）。発光体の内部に埋めない（#29）。
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.045, CENTER_Z))
glow = bpy.context.active_object
glow.name = "byobu_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.5
try:
    glow.visible_camera = False
except Exception:
    pass


# ---------- アニメーション（折り角 φ(t)=PHI_MID+PHI_AMP·sin(2πt)＝完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    phi = phi_at(t01)
    sol = {1: chain(phi, 1), -1: chain(phi, -1)}
    for (o, s, i) in panels:
        (px, py), rot = sol[s][i]
        o.location = (px, py, CENTER_Z)
        o.rotation_euler = (0.0, 0.0, rot)
        o.keyframe_insert(data_path="location", frame=f)
        o.keyframe_insert(data_path="rotation_euler", frame=f)
# 毎フレーム打っているので補間設定は不要（PITFALL #1）


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
focus_null = bpy.context.active_object
focus_null.name = "focus_null"


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
study = add_caption("MIDDLE STUDY 034 — BYOUBU", 0.045, (0.15, -1.3, 0.22), "study")


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
    # #16/#18/#27：レンダーで目視する前に幾何を数値で当てる。
    CAM = (0.55, -8.3)
    for tag, phi in (("open  φmin", PHI_MID - PHI_AMP),
                     ("still φmid", PHI_MID),
                     ("fold  φmax", PHI_MID + PHI_AMP)):
        wdt = half_width(phi)
        depth = W * math.sin(phi / 2)
        # 隙間（x=±GAP/2, y=0）を通してスラブ（y=D_EM）のどこが見えるか＝可視帯の幅
        k = (abs(CAM[1]) + D_EM) / abs(CAM[1])
        xs = [(xg - CAM[0]) * k + CAM[0] for xg in (-GAP / 2, GAP / 2)]
        vis = xs[1] - xs[0]
        inside = max(abs(xs[0]), abs(xs[1])) < em_hw(0.5)
        print(f">> {tag}={math.degrees(phi):5.1f}deg  width={wdt:.3f} / 2.81 "
              f"({wdt / 2.81 * 100:.0f}%)  depth={depth:.3f}  "
              f"lightband x=[{xs[0]:+.3f},{xs[1]:+.3f}] w={vis:.3f}m "
              f"({'OK スラブ内' if inside else 'WARN スラブ端が見える → HW_EM を上げる'})")
    print(f">> height={H:.3f} / 3.52 ({H / 3.52 * 100:.0f}%)  "
          f"world z: bottom={CENTER_Z - H / 2:.3f} "
          f"({'OK 浮遊' if CENTER_Z - H / 2 > 0.05 else 'WARN 床'})  top={CENTER_Z + H / 2:.3f}")
    print(f">> caption top z=0.52 < object bottom z={CENTER_Z - H / 2:.3f} "
          f"({'OK' if CENTER_Z - H / 2 > 0.60 else 'WARN 重なる'})")
    # スラブ端（x=±HW_EM）が扇に隠れているか＝緑スピルの構造回避（#28）
    kk = (abs(CAM[1]) + D_EM) / abs(CAM[1])
    xe = (HW_EM - CAM[0]) * kk + CAM[0]
    ypan = -(abs(xe) - GAP / 2) * math.tan(PHI_MID / 2)
    print(f">> light: slot depth={D_EM:.3f}m  slab {2 * HW_EM:.3f}x{H_EM:.3f} "
          f"(屏風の {H_EM / H * 100:.0f}%)  slab端の視線 y=0 交点 x={xe:+.3f} → "
          f"扇の面 y={ypan:+.3f} ({'OK 隠れる' if ypan < 0 else 'WARN 露出'})")
    print(f">> 明部の高さ ±{FALLOFF:.2f}m = 屏風の {2 * FALLOFF / H * 100:.0f}%（#31-d）"
          f" / ES_RIM={ES_RIM} で暗部はライム画素にならない")
    print(f">> grad: GZ_C={GZ_C:.3f} GZ_F={GZ_F:.4f} (falloff {FALLOFF:.3f}m)")
    print(f">> loop: phi {math.degrees(PHI_MID - PHI_AMP):.0f}..{math.degrees(PHI_MID + PHI_AMP):.0f}deg "
          f"sin(2πt) ＝ t=0/t=1 厳密一致")
    print(f">> ES_CORE={ES_CORE} ES_RIM={ES_RIM} GLOW_E={GLOW_E} SPEC_PAPER={SPEC_PAPER} GAP={GAP}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "byobu.blend"))
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
# （still/anim より前に走ると hero が勾配なしでレンダーされる＝031/032 で踏んだ穴）
if "glb" in modes:
    try:
        for lk in list(core_bsdf.inputs["Emission Strength"].links):
            mat_core.node_tree.links.remove(lk)
        core_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {o.name for (o, s, i) in panels} | {"byobu_light"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "byobu.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
