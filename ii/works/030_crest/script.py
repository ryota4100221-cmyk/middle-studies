# =============================================================
# MIDDLE STUDIES II — 雛形（2026-09-23）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
#
# 🔴 これは「インフラ」の雛形であって、見た目の雛形ではない。
#    第1期の雛形（白床・3色・85mm・キャプション・4灯）は**持ち込まない**。
#    LOOK（色・地・光・レンズ・判型）は毎回ここで決め直し、works.json の look に同じ値を書く。
#    下の LOOK の値は動作確認用の仮置き。**そのまま出すと check.py look で前作と比べられる**。
#
# 残してあるのは、どの見た目でも要るものだけ：
#   出力モード／判型から解像度を出す計算／Cycles+GPU+デノイズ／毎フレームキーのループ／
#   面取り（bmesh・clamp の罠つき）／glb 書き出し
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

def hex_to_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


# ------------------------------------------------------------- LOOK（030 CREST）
# 基準：Anish Kapoor「1000 Names」(1982) の Christie's 掲載写真。
# 取ったもの：非常に大きな正面の柔光／鏡面ゼロの乾いた顔料／白地に極彩度の単色1色／縦長に中央。
# 形は写さない（基準＝壁から垂れる舌）。こちらは床に立つ、薄い層が重なった波頭。
LOOK = dict(
    aspect=(4, 5),
    lens=105,
    fstop=8.0,
    view="Standard",          # 飽和色の主役は AgX で灰に寄る（#115/#122）
    look="None",
    exposure=-1.60,
    bg=hex_to_linear("#E9E9E9")[:3],
)
FPS = 24

def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


# ------------------------------------------------------------- 初期化
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    return m


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.8), shape='RECTANGLE', size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.shape, ld.size = energy, color, shape, size
    if size_y:
        ld.size_y = size_y
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    L.visible_camera = False
    return L


# ------------------------------------------------------------- 舞台：白の無限背景紙
R, W, D, H = 3.0, 120.0, 40.0, 30.0
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 24 * math.pi / 2 for i in range(1, 25)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + 3.0, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
paper = principled("paper", LOOK["bg"] + (1.0,), rough=0.9)
paper.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.1
sweep.data.materials.append(paper)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = WORLD_STR = 0.95

# ------------------------------------------------------------- 被写体：層の重なった波頭
PIG = hex_to_linear("#C9161F")
NL = 9                 # 層の数
GAP = 0.030            # 層の間隔
TH = 0.036             # 層の厚み（間隔より厚い＝隣と溶けて1つの塊になる）
LEN = 1.85             # 芯の長さ
NT, NS = 220, 28


def layer_points(k):
    """層 k の芯と幅。奥の層ほど少し先へ伸び、少し外へずれる＝小口が段々に見える"""
    c = (NL - 1) / 2
    thmax = math.radians(78 + 2.6 * k)
    L = LEN * (1 + 0.012 * k)
    x0 = 0.16 + 0.018 * k
    P = [(x0, 0.0)]
    x, z = x0, 0.0
    ds = L / (NT - 1)
    angs = [0.0]
    for i in range(1, NT):
        t = i / (NT - 1)
        th = math.radians(-20) * math.sin(math.pi * t) + thmax * t ** 2.2
        x -= math.sin(th) * ds
        z += math.cos(th) * ds
        P.append((x, z)); angs.append(th)
    rows = []
    for i, ((x, z), th) in enumerate(zip(P, angs)):
        t = i / (NT - 1)
        w = 0.66 * (1 - t ** 3.2) ** 0.5 * (0.42 + 0.58 * math.sin(math.pi * min(1.0, t / 0.74) * 0.5) ** 1.4)
        w *= (1 - 0.018 * abs(k - c))
        w *= 1 + 0.012 * math.sin(2 * math.pi * (5.0 * t + 0.04 * k)) + 0.035 * math.sin(2 * math.pi * 2.6 * t + 1.1)
        nx, nz = math.cos(th), math.sin(th)     # 芯の法線（外側）
        off = 0.02 * k * (1 - t)                # 根元ほど層ごとに横へずれる
        off += 0.035 * math.sin(2 * math.pi * 1.35 * t + 0.4) * math.sin(math.pi * t)   # 輪郭のうねり（左の縁を直線にしない）
        rows.append([(x + nx * (s * w / 2 + off), z + nz * (s * w / 2 + off))
                     for s in [-1 + 2 * j / (NS - 1) for j in range(NS)]])
    return rows


def relief(sN, t):
    """全層に同じだけ入れる起伏：幅方向の膨らみ＋斜めに走る折れ込み（手前が -y）"""
    dome = -0.09 * (1 - sN * sN) * math.sin(math.pi * min(1.0, 0.15 + t))
    c = 0.35 - 0.75 * t                         # 溝の位置：根元は右、上へ行くほど左へ
    crease = 0.10 * math.exp(-((sN - c) / 0.20) ** 2) * math.sin(math.pi * min(1.0, t * 1.15))
    crease += 0.24 * math.exp(-((sN - c) / 0.06) ** 2) * math.exp(-((t - 0.68) / 0.13) ** 2)
    lip = -0.42 * max(0.0, (t - 0.55) / 0.45) ** 1.8      # 頂部は手前へ覆いかぶさる
    return dome + crease + lip


verts, faces = [], []
for k in range(NL):
    y = (k - (NL - 1) / 2) * GAP
    rows = layer_points(k)
    base = len(verts)
    for side in (-1, 1):
        for i, row in enumerate(rows):
            t = i / (NT - 1)
            for j, (x, z) in enumerate(row):
                sN = -1 + 2 * j / (NS - 1)
                verts.append((x, y + side * TH / 2 + relief(sN, t), z))
    off = NT * NS
    idx = lambda sd, i, j: base + sd * off + i * NS + j
    for i in range(NT - 1):
        for j in range(NS - 1):
            faces.append((idx(0, i, j), idx(0, i, j + 1), idx(0, i + 1, j + 1), idx(0, i + 1, j)))
            faces.append((idx(1, i, j), idx(1, i + 1, j), idx(1, i + 1, j + 1), idx(1, i, j + 1)))
    # 縁を縫う
    ring = [(i, 0) for i in range(NT)] + [(NT - 1, j) for j in range(1, NS)] + \
           [(i, NS - 1) for i in range(NT - 2, -1, -1)] + [(0, j) for j in range(NS - 2, 0, -1)]
    for a_, b_ in zip(ring, ring[1:] + ring[:1]):
        faces.append((idx(0, *a_), idx(1, *a_), idx(1, *b_), idx(0, *b_)))
me = bpy.data.meshes.new("crest_me")
me.from_pydata(verts, [], faces); me.update()
crest = bpy.data.objects.new("crest", me); scene.collection.objects.link(crest)
bpy.context.view_layer.objects.active = crest
crest.select_set(True)
rm = crest.modifiers.new("remesh", 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = VOXEL = 0.0042
bpy.ops.object.modifier_apply(modifier="remesh")
sm = crest.modifiers.new("smooth", 'SMOOTH'); sm.factor = 0.7; sm.iterations = 12
bpy.ops.object.modifier_apply(modifier="smooth")
# 手で塗り重ねた数mmの凹凸
tex = bpy.data.textures.new("lumps", 'CLOUDS'); tex.noise_scale = 0.05; tex.noise_depth = 2
dp = crest.modifiers.new("lumps", 'DISPLACE'); dp.texture = tex; dp.strength = 0.004; dp.mid_level = 0.5
dp.texture_coords = 'OBJECT'
bpy.ops.object.modifier_apply(modifier="lumps")
# ねじり：高さに応じて縦軸まわりに回し、中ほどを手前へふくらませる（平板な切り絵にしない）
TWIST = math.radians(38)
ROT0 = math.radians(-28)
for v in crest.data.vertices:
    x, y, z = v.co
    h = max(0.0, z) / 1.55
    a_ = TWIST * h
    x2 = x * math.cos(a_) - y * math.sin(a_)
    y2 = x * math.sin(a_) + y * math.cos(a_)
    y2 -= 0.16 * math.sin(math.pi * min(1.0, h))
    y2 += 0.10 * math.sin(2 * math.pi * (x * 0.9 + z * 0.35) + 0.6) * min(1.0, h * 2)
    ca, sa = math.cos(ROT0), math.sin(ROT0)
    v.co = (x2 * ca - y2 * sa, x2 * sa + y2 * ca, z - 0.004)
for p in crest.data.polygons:
    p.use_smooth = True
crest.data.update()


def pigment_mat(name, color):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = 1.0
    p.inputs["Specular IOR Level"].default_value = 0.0
    if "Diffuse Roughness" in p.inputs:
        p.inputs["Diffuse Roughness"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 140; nz.inputs["Detail"].default_value = 6
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.0015
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    # 色の斑（数cm）と粒：明度だけを揺らす
    nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 9; nz2.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.94; mr.inputs["To Max"].default_value = 1.06
    mr.inputs["From Min"].default_value = 0.3; mr.inputs["From Max"].default_value = 0.7
    nt.links.new(nz2.outputs["Fac"], mr.inputs["Value"])
    mr2 = nt.nodes.new("ShaderNodeMapRange"); mr2.inputs["To Min"].default_value = 0.92; mr2.inputs["To Max"].default_value = 1.08
    mr2.inputs["From Min"].default_value = 0.3; mr2.inputs["From Max"].default_value = 0.7
    nt.links.new(nz.outputs["Fac"], mr2.inputs["Value"])
    ml = nt.nodes.new("ShaderNodeMath"); ml.operation = 'MULTIPLY'
    nt.links.new(mr.outputs["Result"], ml.inputs[0]); nt.links.new(mr2.outputs["Result"], ml.inputs[1])
    mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = 'RGBA'; mc.blend_type = 'MULTIPLY'
    mc.inputs[0].default_value = 1.0
    mc.inputs[6].default_value = color
    nt.links.new(ml.outputs[0], mc.inputs[7])
    nt.links.new(mc.outputs[2], p.inputs["Base Color"])
    p.inputs["Sheen Weight"].default_value = 0.08
    p.inputs["Sheen Roughness"].default_value = 0.6
    p.inputs["Sheen Tint"].default_value = (1.0, 0.32, 0.30, 1)
    return m


pig = pigment_mat("pigment", PIG)
crest.data.materials.append(pig)

# 足元にこぼれた顔料の粉（点群）
import random
random.seed(30)
foot = [(v.co.x, v.co.y) for v in crest.data.vertices if v.co.z < 0.01]
dv = []
for _ in range(110000):
    fx, fy = random.choice(foot)
    u_ = random.random()
    r = random.expovariate(1 / 0.035) if u_ < 0.8 else (random.expovariate(1 / 0.10) if u_ < 0.97 else random.expovariate(1 / 0.3))
    a_ = random.uniform(0, 2 * math.pi)
    r *= 0.35 + 0.9 * (0.5 + 0.5 * math.sin(a_ * 2 + 0.8)) ** 2 + 0.3 * random.random()
    dv.append((fx + r * math.cos(a_), fy + r * math.sin(a_) * 0.8, 0.0))
# 根元に溜まった顔料の小山（足跡からの距離で高さを落とす）
from mathutils import kdtree
kd = kdtree.KDTree(len(foot))
for i_, (fx, fy) in enumerate(foot):
    kd.insert((fx, fy, 0.0), i_)
kd.balance()
cx = sum(f[0] for f in foot) / len(foot); cy = sum(f[1] for f in foot) / len(foot)
MN = 220; MR = 0.7
mv, mf = [], []
for i_ in range(MN):
    for j_ in range(MN):
        x = cx - MR + 2 * MR * i_ / (MN - 1); y = cy - MR + 2 * MR * j_ / (MN - 1)
        dd = kd.find((x, y, 0.0))[2]
        ang = math.atan2(y - cy, x - cx)
        wob = 0.55 + 0.45 * math.sin(3 * ang + 0.7) * math.sin(5 * ang + 2.1) + 0.25 * math.sin(11 * ang)
        hgt = 0.012 * math.exp(-dd / (0.010 + 0.014 * max(0.1, wob))) + 0.002 * math.exp(-dd / 0.04)
        hgt *= 1 + 0.35 * math.sin(x * 61 + math.sin(y * 47) * 2) * math.sin(y * 53)
        mv.append((x, y, max(0.0, hgt) - 0.0035))
for i_ in range(MN - 1):
    for j_ in range(MN - 1):
        a0 = i_ * MN + j_
        mf.append((a0, a0 + MN, a0 + MN + 1, a0 + 1))
mme = bpy.data.meshes.new("mound_me"); mme.from_pydata(mv, [], mf); mme.update()
mound = bpy.data.objects.new("mound", mme); scene.collection.objects.link(mound)
for p in mme.polygons:
    p.use_smooth = True
mound.data.materials.append(pig)
mound.hide_render = True   # 赤い面と白い床の境目がそのまま「皿の縁」になる＝粉の点だけで溜まりを作る

dme = bpy.data.meshes.new("dust_me"); dme.from_pydata(dv, [], []); dme.update()
dust = bpy.data.objects.new("dust", dme); scene.collection.objects.link(dust)
ng = bpy.data.node_groups.new("dust_gn", 'GeometryNodeTree')
ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
gi = ng.nodes.new("NodeGroupInput"); go = ng.nodes.new("NodeGroupOutput")
m2p = ng.nodes.new("GeometryNodeMeshToPoints")
rv = ng.nodes.new("FunctionNodeRandomValue"); rv.data_type = 'FLOAT'
rv.inputs[2].default_value = 0.0006; rv.inputs[3].default_value = 0.0022
sp = ng.nodes.new("GeometryNodeSetPosition")
cmb = ng.nodes.new("ShaderNodeCombineXYZ")
smat = ng.nodes.new("GeometryNodeSetMaterial"); smat.inputs["Material"].default_value = None
ng.links.new(gi.outputs[0], m2p.inputs["Mesh"])
ng.links.new(rv.outputs[1], m2p.inputs["Radius"])
ng.links.new(m2p.outputs[0], smat.inputs["Geometry"])
ng.links.new(smat.outputs[0], go.inputs[0])
gm = dust.modifiers.new("gn", 'NODES'); gm.node_group = ng
dust_mat = pigment_mat("dust", PIG)
smat.inputs["Material"].default_value = dust_mat
dust.data.materials.append(dust_mat)

parts = [crest]   # 粉は床の一部として扱う（構図の点検は塊で測る）

# ------------------------------------------------------------- 光：正面上の巨大な柔光＋白い環境
KEY_POS = (-6.5, -5.0, 6.0)
KEY_E = 2000
key = area("key", KEY_POS, 9.0, KEY_E, (1.0, 0.99, 0.97), target=(0, 0, 0.6))
fill = area("fill", (2.5, -10.0, 2.5), 8.0, 700, (1, 1, 1), target=(0, 0, 0.8))
wash = area("wash", (0.0, 1.2, 7.5), 12.0, 900, (1, 1, 1), target=(0, 4.0, 0.3))
# 壁の洗いは被写体から外す（#122）
wl = bpy.data.collections.new("subject_rx"); bpy.context.scene.collection.children.link(wl)
wl.objects.link(crest)
wash.light_linking.receiver_collection = wl
wash.light_linking.receiver_collection.collection_objects[0].light_linking.link_state = 'EXCLUDE' 

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam
# ------------------------------------------------------------- 動画＝プロダクトフィルム（2026-09-23〜）
# 🔴 10〜12秒・3〜4カットの CM 型。ループは「最後のカット → 最初のカット」をカットで戻る（継ぎ目なしにしない）。
#    最後のカットは静止画（hero）と同じ構図で終わり、1秒以上止まる＝ STILL_FRAME はその中に置く。
# 型（組み合わせて使う。毎回同じ並びにしない）：
#   マクロ  … 長いレンズ（100〜150mm）で縁・肌理・部品をなめる。浅い被写界深度＋ピント送り
#   スライド… カメラが横・縦に平行移動して、光や物の前を滑る
#   回り込み… 被写体を中心に弧を描く（15〜60°）
#   押し込み… まっすぐ寄る／引く（レンズを変えずに距離で）
#   光の走り… 面光源を動かして、ハイライトの帯を表面に走らせる（カメラは止めてよい）
#   物の動き… 回る・開く・持ち上がる・落ちる・並ぶ
#   決め    … hero の構図。動きながら入ってきて止まる
# 🔴 カメラの動きは必ず加減速（ease）。等速の直線移動は安いCGに見える。
# 🔴 カットの切り替えは「動いている途中」で切る（止まってから切ると間延びする）。
# 🔴 モーションブラーは使わない：毎フレームキーのカメラは、カットの境目で前後のカットの間を補間してブレる。

def ease(t):                  # 加減速（sine in-out）
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):              # 動きながら入って止まる（決めのカット向き）
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def orbit(center, radius, height, deg):   # 被写体まわりの弧（deg=0 が正面 -Y）
    r = math.radians(deg)
    return Vector((center[0] + radius * math.sin(r), center[1] - radius * math.cos(r), height))

# 各カット：sec（秒）／cam(t)→(カメラ位置, 注視点, レンズmm, f値, ピント距離 or None=注視点まで)
#           ／pose(t)→物の動き（任意）。t はそのカットの中で 0→1。
# 🔴 下は動作確認用の仮置き。**毎回、基準と題材に合わせて組み直す**。
TGT = Vector((0.20, 0.0, 0.80))
HERO_CAM = orbit((0.12, 0.0, 0.0), 8.0, 1.6, 22)


def hero_cam(t):
    return (lerp(HERO_CAM + Vector((1.4, -0.6, 0.5)), HERO_CAM, ease_out(min(1.0, t / 0.65))), TGT,
            LOOK["lens"], LOOK["fstop"], None)


SHOTS = [
    dict(sec=3.0,   # 回り込み：横から層の重なりを見せ、正面寄りへ弧で回る
         cam=lambda t: (orbit((0.12, 0.0, 0.0), 6.2, 1.25, 48 - 32 * ease(t)), Vector((0.1, 0.0, 0.85)),
                        85, 5.6, None)),
    dict(sec=3.0,   # マクロ：頂部の層の段を、右から左へ滑りながらなめる（ピントは塊の表面）
         cam=lambda t: (orbit((0.12, 0.0, 0.0), 2.5, 1.95, 46 - 26 * ease(t)),
                        Vector((0.30 - 0.25 * ease(t), 0.0, 1.42)), 135, 5.6, "hit")),
    dict(sec=2.5,   # 押し込み：床すれすれで根元の粉へ寄る
         cam=lambda t: (lerp((-0.9, -3.4, 0.32), (-0.6, -2.4, 0.26), ease(t)), Vector((0.15, 0.0, 0.10)),
                        100, 4.0, None)),
    dict(sec=3.0, cam=hero_cam),   # 決め：右上から入って hero で止まる
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    pass


def light_path(i, t):
    key.location = KEY_POS
    key.data.energy = KEY_E


for i, sh in enumerate(SHOTS):
    for k in range(sh["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh["frames"] - 1)
        T = (f - 1) / max(1, N_FRAMES - 1)
        loc, tgt, lens, fstop, focus = sh["cam"](t)
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cd.lens = lens
        cd.dof.aperture_fstop = fstop
        if focus == "hit":
            dg = bpy.context.evaluated_depsgraph_get()
            d_ = (Vector(tgt) - Vector(loc)).normalized()
            ok, hp, *_ = scene.ray_cast(dg, Vector(loc), d_)
            focus = (hp - Vector(loc)).length if ok else (Vector(tgt) - Vector(loc)).length
        cd.dof.focus_distance = focus if focus else (Vector(tgt) - Vector(loc)).length
        for path in ("location", "rotation_euler"):
            cam.keyframe_insert(path, frame=f)
        cd.keyframe_insert("lens", frame=f)
        cd.dof.keyframe_insert("aperture_fstop", frame=f)
        cd.dof.keyframe_insert("focus_distance", frame=f)
        pose(i, t, T)
        for o in parts:
            o.keyframe_insert("rotation_euler", frame=f)
            o.keyframe_insert("location", frame=f)
        light_path(i, t)
        key.keyframe_insert("location", frame=f)
        key.keyframe_insert("rotation_euler", frame=f)
        key.data.keyframe_insert("energy", frame=f)

# ------------------------------------------------------------- レンダー設定
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.view_settings.view_transform = LOOK["view"]
try:
    scene.view_settings.look = LOOK["look"]
except TypeError:
    print(">> look not available:", LOOK["look"])
scene.view_settings.exposure = LOOK["exposure"]
scene.frame_start, scene.frame_end = 1, N_FRAMES
scene.render.fps = FPS
scene.render.film_transparent = False


def still(path, long_side, samples, frame=STILL_FRAME):
    scene.frame_set(frame)
    scene.render.resolution_x, scene.render.resolution_y = res(long_side)
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


if "test" in modes:
    still(os.path.join(OUT, "_test.png"), 720, 48)
    print(">> test done")

if "testhero" in modes:
    still(os.path.join(OUT, "_testhero.png"), 1600, 128)
    print(">> testhero done")

if "shots" in modes:    # 各カットの頭・中・終わり（ii/scripts/contact.py で1枚に並べる）
    for i, sh in enumerate(SHOTS):
        for j, frac in enumerate((0.0, 0.5, 1.0)):
            fr = shot_start[i] + round(frac * (sh["frames"] - 1))
            still(os.path.join(OUT, "_shot_%d_%d.png" % (i, j)), 480, 24, fr)
    print(">> shots done")

if "still" in modes:
    still(os.path.join(OUT, "hero.png"), 2560, 256)
    print(">> hero done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = res(int(os.environ.get("II_ANIM_LONG", "1080")))  # II_ANIM_LONG は試験用
    scene.cycles.samples = int(os.environ.get("II_ANIM_SAMPLES", "24"))
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> anim done")

# glb は最後（マテリアルを書き換える作品があるため）
if "glb" in modes:
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    dec = crest.modifiers.new("dec", 'DECIMATE'); dec.ratio = float(os.environ.get("II_GLB_RATIO", "0.3"))  # 8MB 以下に（ボクセル 4.2mm は 19.5MB）
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True, export_apply=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
