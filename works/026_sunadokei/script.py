# =============================================================
# monaka design. — MIDDLE STUDY 026 "SUNADOKEI"（砂時計）
# 黒い砂時計。上の砂が落ち、下に積もる。光っているのは
# くびれ＝真ん中のひと点だけ。砂が落ちきると器がゆっくり
# ひっくり返り、また落ちはじめる＝時間の真ん中。
#
# 機構：
#  ・器＝黒い縦リブ 12 本（bmesh 掃引・**直線の双円錐**メリディアン
#    r(z)=R_NECK+(R_MAX-R_NECK)·|z|/H に沿わせる）＋上下の黒い円盤＋
#    くびれの黒いカラー。ガラスは張らず「骨」だけでシルエットを描く
#    （004 ANDON/024 OUGI の籠＝隙間から光が漏れ #11 の Glare箱を回避）。
#    球状バルブ(sin)は hero で鳥籠に転んだ＝▽△の直円錐が砂時計のアイコン。
#  ・砂＝上下の回転体（マット黒）。**直円錐は「水位が下がった残り」が
#    相似形**なので、シェイプキー不要で object の scale だけで減り／
#    積もりを表現できる。上砂は原点＝くびれ平面・径倍率
#    fx(s)=(R_NECK+s(R_MAX-R_NECK))/R_MAX で上面を壁に接地させ（一様
#    スケールだと壁から離れて「浮いた黒い塊」に見える）、下砂は原点＝
#    底の円盤で一様スケール（安息角一定＝相似成長が物理的に正しい）。
#    glb に transform アニメとして乗る。
#  ・光＝くびれを落ちるライム発光の紡錘（純発光体 #13・両端を細らせて
#    #21）＋随伴する柔らかいライム点光源。細い円柱は「裸の緑の棒」に
#    転び、細く強い発光体はコアが白緑に飛ぶ＝**太く弱く**が正解（#14 実測）。
#  ・ループ＝前半で砂が落ち(u:0→1)、後半で器全体が **Y軸まわりに
#    180°反転**。砂時計は上下対称なので反転後の状態＝初期状態＝
#    数学的に閉じる（013/025 の整数対称ループの反転版・シリーズ初）。
#    リブ角は 2πi/12 で φ→π−φ に閉じるので籠も反転で自己一致。
#
# 実行:
#   Blender --background --factory-startup --python monaka_sunadokei.py -- <mode...>
#   modes: test | still | anim | glb | blend
#   env: ES_FLOW SPEC_RIB TILT_DEG STILL_FRAME
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

CENTER_Z = 1.52            # 浮遊高さ（くびれ＝画面中央）

# --- 器のシルエット（#18: 縦3.52 / 横2.81 に収める） ---
H_HALF = 0.86              # くびれ→端 の高さ（全高 1.83 ≒ 縦の52%）
R_MAX = 0.54               # バルブの最大半径（a=1/(2·BULB_B) で到達）
R_NECK = 0.155             # くびれの半径
BULB_B = 0.72              # <0.5で単調凹＝スツールに転ぶ。>0.5でバルブが膨らみ端で絞れる

N_RIB = 12                 # 縦リブ本数（偶数＝反転で自己一致）
RIB_R = 0.019              # リブの太さ（丸断面）
RIB_M = 72                 # 掃引分割
RIB_C = 7                  # 断面分割

R_PLATE = 0.56             # 円盤は口径(R_MAX)より少しだけ大きく（大きいと丸テーブルに読める）
T_PLATE = 0.036
COLLAR_MINOR = 0.011       # くびれのカラー（太いと中央の光を塞ぐ）

# --- 砂 ---
GAP = 0.17                 # くびれの空き＝光の通る喉（狭いと中央の光が消える）
SAND_K = 0.94              # 砂は器の内側に（リブに食い込ませない）
SAND_N = 44                # 母線分割
SAND_A = 96                # 周分割
S_MIN = 0.06               # 空のときの残り

# --- 光 ---
FLOW_R = float(os.environ.get("FLOW_R", "0.050"))  # 細すぎる発光体は白緑に飛ぶ（#14の実測で確定）
FLOW_H = 0.200            # 筋の半長（上端は上砂の中に隠れ、下端は宙で細って消える）
ES_FLOW = float(os.environ.get("ES_FLOW", "2.6"))  # 2026-07-21引き上げ（#24ペンキ化是正・#14改訂）
GLOW_BASE = 0.30           # 反転中も残る燠火（ループの連続性）
GLOW_W = float(os.environ.get("GLOW_W", "26"))   # 2026-07-21引き上げ：ハロー復活のため（コア白緑は#22の面積側で制御）

SPEC_RIB = float(os.environ.get("SPEC_RIB", "0.08"))  # #17-c

FPS = 24
N_FRAMES = 144             # 6秒 完全ループ（前半=落下 / 後半=反転）
STILL_FRAME = int(os.environ.get("STILL_FRAME", "37"))  # 落下の中間＝上下半々


def hex_to_linear(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


def r_prof(z):
    """砂時計のメリディアン（|z| で対称）。**直線＝双円錐**。
    球状バルブ(sin)は hero で鳥籠に転んだ。直線の双円錐＝▽△が砂時計のアイコンで、
    かつ『くびれから水位までの砂』が円錐の相似形になるのでスケールだけで壁沿いに落ちる。"""
    a = min(1.0, abs(z) / H_HALF)
    return R_NECK + (R_MAX - R_NECK) * a


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]

# 器のリブ（細い曲面・env露出 → 反射率を落とす #17/#17-c）
mat_rib, rb = make_principled("sd_rib")
rb.inputs["Base Color"].default_value = BLACK
rb.inputs["Roughness"].default_value = 0.34
rb.inputs["Specular IOR Level"].default_value = SPEC_RIB
rb.inputs["Coat Weight"].default_value = 0.0
rb.inputs["Coat Roughness"].default_value = 0.20

# 上下の円盤・カラー（平面主体・一様bright env → 反射率を落とす #17-c）
mat_plate, pb = make_principled("sd_plate")
pb.inputs["Base Color"].default_value = BLACK
pb.inputs["Roughness"].default_value = 0.30
pb.inputs["Specular IOR Level"].default_value = 0.10
pb.inputs["Coat Weight"].default_value = 0.0

# 砂（マット＝粒の質感。器と質感の階層を作る #17-b）
mat_sand, sb = make_principled("sd_sand")
sb.inputs["Base Color"].default_value = BLACK
sb.inputs["Roughness"].default_value = 0.62
sb.inputs["Specular IOR Level"].default_value = 0.10
sb.inputs["Coat Weight"].default_value = 0.0

# 落ちる砂の筋（露出した発光体 → 純発光体 #13）
mat_flow, fb = make_principled("sd_flow")
fb.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
fb.inputs["Emission Color"].default_value = LIME
fb.inputs["Emission Strength"].default_value = ES_FLOW
fb.inputs["Specular IOR Level"].default_value = 0.10
fb.inputs["Roughness"].default_value = 0.5

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


def new_obj(name, bm, mats, smooth_angle=0.7):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    for m in mats:
        o.data.materials.append(m)
    bpy.context.view_layer.objects.active = o
    for s in bpy.context.selected_objects:
        s.select_set(False)
    o.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_angle)
    except Exception:
        bpy.ops.object.shade_smooth()
    o.select_set(False)
    return o


# ---------- 器：縦リブ（メリディアン掃引） ----------
bm = bmesh.new()
for i in range(N_RIB):
    phi = 2 * math.pi * i / N_RIB       # φ→π−φ に閉じる（反転で自己一致）
    ex = Vector((math.cos(phi), math.sin(phi), 0.0))
    et = Vector((-math.sin(phi), math.cos(phi), 0.0))
    centers = []
    for m in range(RIB_M + 1):
        z = -H_HALF + 2 * H_HALF * m / RIB_M
        centers.append(Vector((r_prof(z) * ex.x, r_prof(z) * ex.y, z)))
    rings = []
    for m in range(RIB_M + 1):
        P = centers[m]
        m0, m1 = max(0, m - 1), min(RIB_M, m + 1)
        T = (centers[m1] - centers[m0])
        T = T.normalized() if T.length > 1e-9 else Vector((0, 0, 1))
        nrm = T.cross(et).normalized()   # 面法線（径方向）
        ring = []
        for c in range(RIB_C):
            a = 2 * math.pi * c / RIB_C
            off = (RIB_R * math.cos(a)) * et + (RIB_R * math.sin(a)) * nrm
            ring.append(bm.verts.new(P + off))
        rings.append(ring)
    for m in range(RIB_M):
        for c in range(RIB_C):
            c2 = (c + 1) % RIB_C
            bm.faces.new((rings[m][c], rings[m][c2],
                          rings[m + 1][c2], rings[m + 1][c]))
    bm.faces.new([rings[0][c] for c in range(RIB_C)][::-1])
    bm.faces.new([rings[RIB_M][c] for c in range(RIB_C)])

ribs = new_obj("sd_ribs", bm, [mat_rib], 0.7)


# ---------- 器：上下の円盤 ＋ くびれのカラー ----------
bm = bmesh.new()
for sgn in (1, -1):
    zc = sgn * (H_HALF + T_PLATE * 0.5)
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=96,
                                radius1=R_PLATE, radius2=R_PLATE, depth=T_PLATE)
    bmesh.ops.translate(bm, verts=res["verts"], vec=(0, 0, zc))
# くびれのカラー（黒いリング＝「真ん中」を締める）
CR = R_NECK + 0.014
CSEG, CMIN = 64, 20
verts_ring = []
for j in range(CSEG):
    a = 2 * math.pi * j / CSEG
    row = []
    for k in range(CMIN):
        b2 = 2 * math.pi * k / CMIN
        rr = CR + COLLAR_MINOR * math.cos(b2)
        row.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a),
                                 COLLAR_MINOR * math.sin(b2))))
    verts_ring.append(row)
for j in range(CSEG):
    j2 = (j + 1) % CSEG
    for k in range(CMIN):
        k2 = (k + 1) % CMIN
        bm.faces.new((verts_ring[j][k], verts_ring[j2][k],
                      verts_ring[j2][k2], verts_ring[j][k2]))

shell = new_obj("sd_shell", bm, [mat_plate], 0.9)


# ---------- 砂：上（漏斗）／下（山） ----------
def sand_mesh(name, sign):
    """sign=+1: 上砂（原点＝くびれ平面 z=0。h=GAP..H_HALF を張る）
       sign=-1: 下砂（原点＝底の円盤。h=0..H_HALF-GAP を張る）
    どちらも同じ r_prof から作るので満杯どうしは厳密な鏡像＝反転ループが閉じる。"""
    bm = bmesh.new()
    span = H_HALF - GAP           # 母線の高さ
    rings = []
    for i in range(SAND_N + 1):
        t = i / SAND_N
        if sign > 0:              # 上砂：原点はくびれ平面（相似縮小＝壁沿いに落ちる）
            h = GAP + span * t
            zw = h
        else:                     # 下砂：原点は底面（相似成長＝積もる山）
            h = span * t
            zw = -H_HALF + h
        rr = max(0.012, SAND_K * r_prof(zw))
        row = []
        for j in range(SAND_A):
            a = 2 * math.pi * j / SAND_A
            row.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), h)))
        rings.append(row)
    for i in range(SAND_N):
        for j in range(SAND_A):
            j2 = (j + 1) % SAND_A
            bm.faces.new((rings[i][j], rings[i + 1][j],
                          rings[i + 1][j2], rings[i][j2]))
    # 端を閉じる（頂点側は小さな円、外側は平らなキャップ）
    bm.faces.new([rings[0][j] for j in range(SAND_A)][::-1])
    bm.faces.new([rings[SAND_N][j] for j in range(SAND_A)])
    return new_obj(name, bm, [mat_sand], 0.9)


sand_up = sand_mesh("sd_sand_up", +1)
sand_up.location = (0, 0, 0.0)        # 原点＝くびれ平面（不動点）
sand_lo = sand_mesh("sd_sand_lo", -1)
sand_lo.location = (0, 0, -H_HALF)    # 原点＝底の円盤（不動点）


# ---------- 光：落ちる砂の筋 ----------
# 一定断面の円柱は hero で「裸の緑の棒」に転ぶ（018/022 の罠）。
# #21 に従い両端を細らせた紡錘形にして、砂の筋＝流れとして読ませる。
bm = bmesh.new()
FN, FA = 40, 24
frings = []
for i in range(FN + 1):
    t = i / FN
    rr = max(0.0015, FLOW_R * (math.sin(math.pi * t) ** 0.45))
    z = -FLOW_H + 2 * FLOW_H * t
    frings.append([bm.verts.new((rr * math.cos(2 * math.pi * j / FA),
                                 rr * math.sin(2 * math.pi * j / FA), z))
                   for j in range(FA)])
for i in range(FN):
    for j in range(FA):
        j2 = (j + 1) % FA
        bm.faces.new((frings[i][j], frings[i][j2],
                      frings[i + 1][j2], frings[i + 1][j]))
bm.faces.new([frings[0][j] for j in range(FA)][::-1])
bm.faces.new([frings[FN][j] for j in range(FA)])
flow = new_obj("sd_flow", bm, [mat_flow], 0.9)

bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
glow = bpy.context.active_object
glow.name = "sd_glow"
glow.data.color = (0.63, 0.88, 0.20)
glow.data.shadow_soft_size = 0.13
glow.data.energy = GLOW_W


# ---------- リグ（砂時計の中心・Y軸まわりに反転） ----------
# 子は mesh を局所原点まわりで作り location だけで置く（#15）。
# matrix_parent_inverse は identity のまま（#9 の罠を構造回避）。
bpy.ops.object.empty_add(location=(0, 0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "SunadokeiRig"
for o in (ribs, shell, sand_up, sand_lo, flow, glow):
    o.parent = rig


# ---------- アニメーション ----------
# t∈[0,0.5): 落下 u=0→1（器は静止）/ t∈[0.5,1): 器がY軸まわりに180°反転
# 反転後の状態は上下対称により初期状態と一致＝完全ループ
scene.frame_start = 1
scene.frame_end = N_FRAMES

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    if t < 0.5:
        a = t / 0.5
        u = 0.5 * (1 - math.cos(math.pi * a))       # 0→1（両端で速度0）
        rot = 0.0
        e = GLOW_BASE + (1 - GLOW_BASE) * math.sin(math.pi * a)
    else:
        b2 = (t - 0.5) / 0.5
        u = 1.0
        rot = math.pi * 0.5 * (1 - math.cos(math.pi * b2))   # 0→π
        e = GLOW_BASE

    # 上砂：水位 s のとき砂の上面は器の壁に接していなければ「浮いた黒い塊」に見える。
    #   壁 r(z)=R_NECK+(R_MAX-R_NECK)a なので、上面を壁に乗せる径倍率は
    #   fx(s) = (R_NECK + s(R_MAX-R_NECK)) / R_MAX（導出値・目分量ではない）。
    # 下砂：積もる山は安息角が一定＝相似成長なので一様スケールが物理的に正しい。
    # 満杯(s=1)では fx=1 で両者は厳密な鏡像＝反転ループの端は閉じる。
    s_up = max(S_MIN, 1.0 - u)
    s_lo = max(S_MIN, u)
    fx = (R_NECK + s_up * (R_MAX - R_NECK)) / R_MAX
    sand_up.scale = (fx, fx, s_up)
    sand_lo.scale = (s_lo, s_lo, s_lo)
    sand_up.keyframe_insert(data_path="scale", frame=f)
    sand_lo.keyframe_insert(data_path="scale", frame=f)

    rig.rotation_euler.y = rot
    rig.keyframe_insert(data_path="rotation_euler", index=1, frame=f)

    fs = 0.35 + 0.65 * e
    flow.scale = (1.0, 1.0, fs)
    flow.keyframe_insert(data_path="scale", frame=f)

    mat_flow.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"] \
        .default_value = ES_FLOW * e
    mat_flow.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"] \
        .keyframe_insert("default_value", frame=f)
    glow.data.energy = GLOW_W * e
    glow.data.keyframe_insert(data_path="energy", frame=f)


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

# #20-b: z=0.52/0.34/0.22（3行目のフレーム外落ちを回避）
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.34), "logo")
study = add_caption("MIDDLE STUDY 026 — SUNADOKEI", 0.045, (0.15, -1.3, 0.22), "study")

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
look = Vector((0.1, 0, CENTER_Z + 0.05))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = ribs
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
scene.render.fps = FPS

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

# ---------- コンポジター（Bloom / Blender 5 新方式） ----------
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
    deps = bpy.context.evaluated_depsgraph_get()
    for o in (ribs, shell, sand_up, sand_lo, flow):
        oe = o.evaluated_get(deps)
        pts = [oe.matrix_world @ Vector(c) for c in oe.bound_box]
        print(">> %-12s x[%.3f %.3f] z[%.3f %.3f]" % (
            o.name, min(p.x for p in pts), max(p.x for p in pts),
            min(p.z for p in pts), max(p.z for p in pts)))

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "sunadokei.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    keep = ("sd_ribs", "sd_shell", "sd_sand_up", "sd_sand_lo", "sd_flow")
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "sunadokei.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "sunadokei_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "sunadokei_hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero still done")

if "anim" in modes:
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "sunadokei_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
