# =============================================================
# monaka design. — MIDDLE STUDY 032 "SUZU"（鈴 / 本坪鈴 shrine bell）
# 黒い鈴が宙に浮き、ゆっくり揺れる。腰をぐるりと走る割れ口（口）の奥から
# ライム #A5E02E が一本の光の帯として差す。真ん中＝口に、光がある。
#
# 機構: 028/030/031 と3作続いた「発光体を object.scale で呼吸させる」を止め、
#   発光は一定のまま物体が振れる純モーション＝シリーズ初の振り子（rocking）。
#   造形＝扁球（oblate spheroid）の厚み T の中空シェルを bmesh 実寸で生成
#   （外皮＋内皮＋口のリム＝閉じた多様体／object.scale・transform_apply 不使用 #15）。
#   口＝腰を方位 SWEEP ぶん走るベルト状の開口。両端は幅を smoothstep で 0 へテーパー
#   （#21 のブラント端回避＝鋳物の口に読ませる／背側は繋がったブリッジで構造を保つ）。
#   開口は「列ごとに u をパラメトリック再マップ」して作るのでグリッド段差が出ない。
#   光＝#29 の正典どおり「開口と同軸・同形の発光プリズム」＝内皮に沿う扁球バンドの solid
#   （半径 K_EM 倍＝一定クリアランス）で口を面で満たす＝裸の緑玉（#13/#18）にならず
#   「一本の光の帯」に読める。Emission は #27 通り camera が覗く縦軸（Generated Z）の
#   1次元バンドグラデ（口の中心＝ホットコア白飛び→口の縁で暗部＝白い芯→#A5E02E→暗部の
#   勾配で #24 ペンキ化回避）。口の深さ（シェル厚＋クリアランス）が斜めからの視線を自然に
#   遮るので、帯は正面で最も明るく側面へ向かって幾何で閉じる（人工的なフェード不要）。
# アニメ: 吊り点（球の上 HANG）に置いた Rock-Empty の rotation_euler.y（＝視線軸まわり
#   ＝画面内の左右振り）を θ(t)=ROCK·sin(2πt) で振る＝周期1の完全ループ。
#   still は t=0 の水平＝左右対称の一枚。glb に rotation が乗る。
# 素材: 一様bright env 下の黒い曲面＝#17/#17-c で Spec 低・Coat 0 のマット鋳鉄に。
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
#   env: ES_CORE ES_RIM GLOW_E ROCK_DEG SLIT_W SWEEP_DEG SPEC_BELL FALLOFF RIDGE
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

CENTER_Z = 1.55          # 鈴（球体）の中心の world 高さ
LOOK_Z = 1.48            # カメラ注視点（口のわずか上）。#29：CENTER_Z と分離して構図を締める
HANG = 1.00              # 吊り点（Rock-Empty）を球中心の何 m 上に置くか＝振り子の腕
ROCK = math.radians(float(os.environ.get("ROCK_DEG", "10")))  # 振れ幅（片側）

# --- 鈴の胴（扁球シェル） ---
A_OUT = 0.80             # 赤道半径（＝シルエット幅の半分）
C_OUT = 0.66             # 極半径（扁球＝横に張った鋳物の鈴）
T_SHELL = 0.042          # 鋳物の肉厚。口のリムの深さになる
A_IN = A_OUT - T_SHELL
C_IN = C_OUT - T_SHELL

# --- 口（割れ口・ベルト状の開口） ---
Z_SLIT = -0.08                                        # 口の中心高さ（腰＝わずかに赤道の下）
SLIT_W = float(os.environ.get("SLIT_W", "0.082"))      # 口の幅（表面に沿った弧長）
SWEEP = math.radians(float(os.environ.get("SWEEP_DEG", "250")))  # 口が走る方位角（残り110°は背側のブリッジ）
TAPER = math.radians(38)                              # 両端のテーパー帯（#21：ブラント端は機械部品に見える）

SEG = 160                # 方位分割
NU_LO = 30               # 下シェルのリング数
NU_HI = 24               # 上シェルのリング数

SPEC_BELL = float(os.environ.get("SPEC_BELL", "0.10"))   # #17-c：一様bright env 下の黒は鏡面反射率が支配項
RIDGE = int(os.environ.get("RIDGE", "0"))                # 口を額装する圏線（鋳物のリブ）2本

# --- 光（口と同軸の発光バンド） ---
K_EM = 0.992             # 内皮に対する半径倍率＝一定クリアランス（口の奥に光の面を置く）
DU_EM = 3.0              # 発光バンドの u 半幅 ＝ DU_EM × 口の u 半幅（口の外は殻に隠れる）

ES_CORE = float(os.environ.get("ES_CORE", "9.0"))     # 口の中心＝ホットコア（白飛びさせハローを出す）#24/#27
ES_RIM = float(os.environ.get("ES_RIM", "0.40"))      # 口の縁の外＝暗部へ落とす（帯を横切る勾配で std を上げる）
FALLOFF = float(os.environ.get("FALLOFF", "0.042"))   # ホットコア→暗部の落ち幅（world m・口の半幅よりわずかに広い）
GLOW_E = float(os.environ.get("GLOW_E", "2.5"))       # 口からこぼれる光（床・胴下部へのスピル）#22

FPS = 24
N_FRAMES = 120           # 5秒 完全ループ
STILL_FRAME = 1          # t=0 ＝ 揺れの中央＝口が水平・左右対称の一枚


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)

# ---------- 口の位置をパラメータ u（0=下極, 1=上極）へ変換 ----------
# 表面: theta = pi*u, r = A*sin(theta), z = -C*cos(theta)
THETA_C = math.acos(max(-1.0, min(1.0, -Z_SLIT / C_OUT)))
U_C = THETA_C / math.pi
# 子午線の弧長スケール ds/du（口の幅[m]を u 幅へ換算）
DSDU = math.pi * math.hypot(A_OUT * math.cos(THETA_C), C_OUT * math.sin(THETA_C))
HW_U = (SLIT_W * 0.5) / DSDU

# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


# 鈴の鋳物（黒）。#17：曲面は環境光を線状に拾って「黒いプラスチック」に転ぶ／
# #17-c：一様bright env 下では roughness でなく鏡面反射率（Specular IOR Level・Coat）が支配項。
# → ラフを上げつつ Spec を落とし、フレネルの縁だけで球の稜線を出して黒を黒に保つ。
mat_bell, b = make_principled("suzu_iron")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.46
b.inputs["Specular IOR Level"].default_value = SPEC_BELL
b.inputs["Coat Weight"].default_value = 0.0

# 光の帯＝口と同軸の発光バンド。#13 純発光体（Base を暗ライムに落とし反射白の上乗せを消す）。
# #24/#25b/#27：生の emission は view 非依存で core≒mid＝勾配が出ず「ペンキ」に退化する。
# solid の塊を口越しに見るので Emission Strength を「camera が覗く縦軸（Generated Z）」の
# 1次元バンドグラデにし、口の中心をホットコアに白飛びさせ口の縁へ暗部を落とす。
mat_core, core_bsdf = make_principled("suzu_light")
core_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.5
core_bsdf.inputs["Specular IOR Level"].default_value = 0.10

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


def auto_smooth(o, angle=0.6):
    """PITFALL #6：5.x は shade_auto_smooth(ops)。球は滑らかに・口のリムは鋭角のまま。"""
    for ob in bpy.data.objects:
        ob.select_set(False)
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    try:
        bpy.ops.object.shade_auto_smooth(angle=angle)
    except Exception as e:
        print(">> auto smooth skipped:", e)


def hw_at(phi):
    """方位 phi（0＝カメラ側の正面 -Y）での口の u 半幅。両端は smoothstep で 0 へテーパー（#21）。"""
    d = abs((phi + math.pi) % (2 * math.pi) - math.pi)
    half = SWEEP * 0.5
    if d >= half:
        return 0.0
    x = (half - d) / TAPER
    if x >= 1.0:
        return HW_U
    return HW_U * (x * x * (3.0 - 2.0 * x))


def surf(u, phi, A, C):
    """扁球面上の点。phi=0 が -Y（カメラ側）を向く。"""
    th = math.pi * u
    r = A * math.sin(th)
    return (r * math.sin(phi), -r * math.cos(phi), -C * math.cos(th))


def add_cyl(bm, r_bot, r_top, z0, z1, seg=64, cap_bot=True, cap_top=True):
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


def add_torus_y(bm, cz, R, r, mseg=48, nseg=16):
    """Y軸まわりのトーラス（＝輪の面が XZ ＝カメラに正対）＝鈴の鐶（吊り輪）。"""
    grid = []
    for i in range(mseg):
        a = 2 * math.pi * i / mseg
        ca, sa = math.cos(a), math.sin(a)
        ring = []
        for j in range(nseg):
            bta = 2 * math.pi * j / nseg
            rr = R + r * math.cos(bta)
            ring.append(bm.verts.new((rr * ca, r * math.sin(bta), cz + rr * sa)))
        grid.append(ring)
    for i in range(mseg):
        i2 = (i + 1) % mseg
        for j in range(nseg):
            j2 = (j + 1) % nseg
            bm.faces.new((grid[i][j], grid[i2][j], grid[i2][j2], grid[i][j2]))


# ---------- 鈴の胴（口の開いた中空シェル） ----------
def build_bell(name):
    bm = bmesh.new()
    hw = [hw_at(2 * math.pi * j / SEG) for j in range(SEG)]
    ulo = [U_C - h for h in hw]
    uhi = [U_C + h for h in hw]

    def make_skin(A, C):
        """扁球の皮を1枚。口の上下で分かれた2つの帯を返す（口の縁のリング）。"""
        pole_b = bm.verts.new((0.0, 0.0, -C))
        pole_t = bm.verts.new((0.0, 0.0, C))
        lo = []
        for i in range(1, NU_LO + 1):
            lo.append([bm.verts.new(surf(ulo[j] * i / NU_LO, 2 * math.pi * j / SEG, A, C))
                       for j in range(SEG)])
        hi = []
        for i in range(NU_HI):
            hi.append([bm.verts.new(surf(uhi[j] + (1.0 - uhi[j]) * i / NU_HI,
                                         2 * math.pi * j / SEG, A, C)) for j in range(SEG)])
        for j in range(SEG):
            k = (j + 1) % SEG
            bm.faces.new((pole_b, lo[0][j], lo[0][k]))
            bm.faces.new((pole_t, hi[-1][k], hi[-1][j]))
        for ring in (lo, hi):
            for i in range(len(ring) - 1):
                for j in range(SEG):
                    k = (j + 1) % SEG
                    bm.faces.new((ring[i][j], ring[i][k], ring[i + 1][k], ring[i + 1][j]))
        return lo[-1], hi[0]

    out_lo, out_hi = make_skin(A_OUT, C_OUT)      # 外皮
    in_lo, in_hi = make_skin(A_IN, C_IN)          # 内皮

    # 口のリム（外皮と内皮を繋ぐ帯）＝鋳物の肉厚が見える。幅0の背側では作らない。
    for j in range(SEG):
        k = (j + 1) % SEG
        if max(hw[j], hw[k]) <= 1e-9:
            continue
        bm.faces.new((out_lo[j], out_lo[k], in_lo[k], in_lo[j]))
        bm.faces.new((out_hi[j], out_hi[k], in_hi[k], in_hi[j]))

    # 圏線（口を額装する鋳物のリブ2本）＝「ただの黒い球」に堕さぬための鋳物のディテール
    if RIDGE:
        for zr in (Z_SLIT + 0.11, Z_SLIT - 0.11):
            rr = A_OUT * math.sqrt(max(0.0, 1.0 - (zr / C_OUT) ** 2)) + 0.010
            add_cyl(bm, rr, rr, zr - 0.008, zr + 0.008)

    # 襟＋鐶（吊り輪）＝1秒で「鈴」に読ませる（#16）
    add_cyl(bm, 0.115, 0.085, 0.58, 0.70)
    add_torus_y(bm, 0.785, 0.085, 0.024)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_bell)
    auto_smooth(o)
    return o


# ---------- 光の帯（口と同軸・内皮に沿う発光バンドの solid／#29） ----------
EM_U0 = U_C - DU_EM * HW_U
EM_U1 = U_C + DU_EM * HW_U
EM_Z0 = -C_IN * math.cos(math.pi * EM_U0)
EM_Z1 = -C_IN * math.cos(math.pi * EM_U1)
EM_SPAN = EM_Z1 - EM_Z0


def build_light(name):
    bm = bmesh.new()
    nu = 14
    rings = []
    for i in range(nu + 1):
        u = EM_U0 + (EM_U1 - EM_U0) * i / nu
        rings.append([bm.verts.new(surf(u, 2 * math.pi * j / SEG, K_EM * A_IN, C_IN))
                      for j in range(SEG)])
    for i in range(nu):
        for j in range(SEG):
            k = (j + 1) % SEG
            bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0])))    # 上下の蓋（殻に隠れて見えない）
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat_core)
    auto_smooth(o)
    return o


# Emission Strength ＝ Generated Z の1次元バンドグラデ（#27）。
# 口の中心（Generated z = GZ_C）をホットコアに白飛びさせ、FALLOFF[m] で暗部へ落とす。
GZ_C = (Z_SLIT - EM_Z0) / EM_SPAN
GZ_F = FALLOFF / EM_SPAN
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


# ---------- リグ（吊り点に置いた Rock-Empty＝振り子） ----------
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z + HANG))
rig = bpy.context.active_object
rig.name = "SuzuRig"


def child_of(obj, parent, basis=None):
    """parent 付け＋ matrix_parent_inverse=identity（#9）。"""
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix()
    if basis is not None:
        obj.matrix_basis = basis
    return obj


bell = build_bell("suzu_bell")
child_of(bell, rig, Matrix.Translation((0, 0, -HANG)))

light = build_light("suzu_light")
child_of(light, rig, Matrix.Translation((0, 0, -HANG)))

# 口からこぼれる光（床・胴下部へのスピル・#22）。殻の外＝正面下に置き、
# 発光体の内部に埋めない（#29：solid の発光体の中の点光源は完全遮蔽され効かない）。
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
glow = bpy.context.active_object
glow.name = "suzu_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.6
try:
    glow.visible_camera = False   # 光源そのものが玉として写り込むのを止める
except Exception:
    pass
child_of(glow, rig, Matrix.Translation((0.0, -0.95, -HANG + Z_SLIT - 0.22)))


# ---------- アニメーション（完全ループ・振り子） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    rig.rotation_euler = (0.0, ROCK * math.sin(2 * math.pi * t01), 0.0)
    rig.keyframe_insert(data_path="rotation_euler", frame=f)
# 毎フレーム打っているので補間設定は不要（PITFALL #1）


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

# DOF のピント面は球の中心（リグは吊り点にあるので分離する）
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
study = add_caption("MIDDLE STUDY 032 — SUZU", 0.045, (0.15, -1.3, 0.22), "study")


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
    # #16/#18：レンダーで目視する前に幾何を数値で当てる。
    top = 0.785 + 0.085 + 0.024
    height = top + C_OUT
    swing = HANG * math.sin(ROCK)
    half_extent = A_OUT + swing
    print(f">> slit: U_C={U_C:.4f} HW_U={HW_U:.5f} width={SLIT_W:.3f}m  sweep={math.degrees(SWEEP):.0f}deg")
    print(f">> light band: u {EM_U0:.4f}..{EM_U1:.4f}  z {EM_Z0:.4f}..{EM_Z1:.4f} span={EM_SPAN:.4f}")
    print(f">> grad: GZ_C={GZ_C:.4f} GZ_F={GZ_F:.4f} (falloff {FALLOFF:.3f}m vs slit half {SLIT_W/2:.3f}m)")
    clear = (1.0 - K_EM) * A_IN * math.sin(math.pi * U_C)
    print(f">> clearance(light→inner skin)={clear:.4f}m  slot depth={T_SHELL + clear:.4f}m "
          f"→ 帯が閉じる方位 ±{math.degrees(math.atan2(SLIT_W, T_SHELL + clear)):.0f}deg")
    print(f">> size: width={2*A_OUT:.3f} / 2.81 ({2*A_OUT/2.81*100:.0f}%)  height={height:.3f} / 3.52 ({height/3.52*100:.0f}%)")
    print(f">> world z: bottom={CENTER_Z - C_OUT:.3f} ({'OK 浮遊' if CENTER_Z - C_OUT > 0.03 else 'WARN 床'})  "
          f"top={CENTER_Z + top:.3f}  pivot={CENTER_Z + HANG:.3f} "
          f"({'OK 吊り点は輪の上' if HANG > top else 'WARN 吊り点が体内'})")
    print(f">> rock: ±{math.degrees(ROCK):.0f}deg swing={swing:.3f}m  max half-extent={half_extent:.3f} / 1.405 "
          f"({half_extent/1.405*100:.0f}%) {'OK' if half_extent < 1.30 else 'WARN フレーム端'}")
    print(f">> ES_CORE={ES_CORE} ES_RIM={ES_RIM} GLOW_E={GLOW_E} SPEC_BELL={SPEC_BELL} RIDGE={RIDGE}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "suzu.blend"))
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
if "glb" in modes:
    # glTF はグラデ Emission のノード網で NaN を吐く（#25c）。書き出し直前に定数へ差し替え。
    try:
        for lk in list(core_bsdf.inputs["Emission Strength"].links):
            mat_core.node_tree.links.remove(lk)
        core_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {"suzu_bell", "suzu_light", "SuzuRig"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "suzu.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
