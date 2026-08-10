# =============================================================
# monaka design. — MIDDLE STUDY 048 "ISHIUSU"（石臼）
#
# 黒い石臼が宙にある。上の石と下の石が触れているのは、真ん中の一枚の面だけ。
# 穀は天面の穴から入り、その一枚の面で挽かれ、光になって、へりからこぼれる。
# 臼が回ると、光は縁をゆっくりひとめぐりする。
#
# 【機構の刷新＝歳差（precession）】シリーズ初。
#   上臼はわずかに「狂って」いる（挽き臼は実際そうなる）。傾き β を臼の材料側に固定し、
#   回転 α と一緒に方位が回るように組む＝ R = Rz(α)·Rx(β)。
#   すると合わせ面の隙間が  g(φ) = GAP − R·sinβ·sin(α−φ)  という**楔（くさび）**になり、
#   楔のいちばん開いた方位が α と一緒に一周する。
#   → 光の線は「全周が一斉に太る／細る」（042・045）ではなく、**縁を移動する**。
#   キーは回転だけ＝ glb にそのまま乗る。360°で厳密に閉じる。
#
# 🔴 #40⑥（機構が光を変えているか）は幾何で積分する（#46）。
#    このスクリプトは Blender を起動しなくても解ける形にしてあり、
#    STILL_FRAME も同じ積分の argmax から決めている（構図の勘で決めない）。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | still | phases | anim | blend | glb
# =============================================================
import bpy, bmesh, math, sys, os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))

LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 石臼 -----------------------------------------------------
R_LO_TOP = 0.812      # 下臼 胴のいちばん太いところ
R_LO_BOT = 0.848      # 下臼 底半径
H_LO     = 0.34
R_UP     = 0.735      # 上臼（下臼より小さい＝段が出て「二つの石」に読める／隙間の口がカメラを向く）
H_UP     = 0.30
GAP      = 0.032      # 合わせ面の平均隙間
# 🔴 R_UP·sinβ ≒ GAP にすると、楔は片側で**ほぼ閉じる**＝光が全周のリングでなく
#    三日月になる。連続した光る輪はそれ自体が「製品（LEDリング）」の記号（round1で実証）。
BETA     = math.radians(2.30)
R_HOLE   = 0.155      # 供給口
FILL_DEPTH = 0.052    # 光る面（穀）が天面からどれだけ下か＝黒いベゼルの深さ（#28）
PEG_AT   = 0.480      # 挽き手の立つ半径
PEG_H    = 0.300      # 柄の高さ（肘まで）
R_PUCK   = 0.727      # 🔴 上臼の縁より内側。はみ出すと「隙間から漏れる光」でなく裸の発光板になる
NSEG     = 64
TILT     = math.radians(19.0)   # カメラへ向けて傾ける（#26）。深いと天面が「蓋」に読める
CENTER_Z = 1.60
HEW      = 2.1        # 石を手で割った肌にする変位の倍率（0で機械挽きのつるつる＝ノブに読める）

# --- 発光 -----------------------------------------------------
ES_CORE  = 6.5        # 供給口の穀（ホットコア）
ES_CBASE = 1.3
ES_IN    = 3.5        # 挽き面：内側
ES_OUT   = 2.1        # 挽き面：外側（縁）。#27 中心で作られた光が外へ広がって薄まる
LAMP_GAP = 3.0        # 🔴 隙間の随伴点光源。強いと隙間まわりを「塗って」しまう（round2で実証）
LAMP_HOP = 3.2

FPS = 24
N_FRAMES = 120        # 5秒・360°で厳密に閉じる

CAM_LOC = (0.55, -8.3, 1.95)

# ---------- #40⑥／STILL_FRAME を純mathで解く（Blender不要） ----------
# 隙間の口の「カメラを向いた投影面積」 A(α) = ∫ g(φ)·R·max(0, n̂(φ)·v̂) dφ
# n̂(φ) は臼のローカル系での外向き径方向。v̂ は臼へ向かうカメラ方向をローカルに戻したもの。
def _v_local():
    v = Vector((CAM_LOC[0], CAM_LOC[1], CAM_LOC[2] - CENTER_Z)).normalized()
    c, s = math.cos(TILT), math.sin(TILT)       # Rx(-TILT) で親の傾きを解く
    return (v.x, v.y * c + v.z * s, -v.y * s + v.z * c)

VL = _v_local()

def visible_area(alpha, n=720):
    tot = 0.0
    for k in range(n):
        phi = 2 * math.pi * k / n
        w = math.cos(phi) * VL[0] + math.sin(phi) * VL[1]
        if w <= 0:
            continue
        g = GAP - R_UP * math.sin(BETA) * math.sin(alpha - phi)
        tot += max(g, 0.0) * R_UP * w * (2 * math.pi / n)
    return tot

_AS = [visible_area(2 * math.pi * i / N_FRAMES) for i in range(N_FRAMES)]

# 🔴 hero は「見える面積が最大の位相」では**ない**。面積最大は楔のいちばん太い所が正面に来る位相で、
#    見える弧の中では光の太さがほとんど変わらない＝ただの輪に写る（round4で実証）。
#    hero に要るのは**光が自分の長さ方向に変化していること**＝先細り。
#    taper(α) = |g(210°) − g(330°)|（見える弧の両肩での隙間の差）を最大化する。
#    ただし挽き木が正面／真後ろを向くと棒が潰れて読めないので、方位を [120°,235°] に絞る。
#    taper(α) = |g(210°) − g(330°)|（見える弧の両肩での隙間の差）は α=90°/270° で最大になるが、
#    そこは挽き木が真後ろ／正面を向いて棒が点に潰れる位相でもある。両方を掛けて選ぶ。
def taper(alpha):
    g = lambda phi: GAP - R_UP * math.sin(BETA) * math.sin(alpha - math.radians(phi))
    return abs(g(210) - g(330))

def arm_proj(alpha):
    """挽き木が画面上でどれだけ長さを持つか＝視線と直交する成分。
       🔴 投影長だけでは足りない：手前半分（sinα<0）だと腕が天面の上に**寝てしまい**、
       背景に対する輪郭を失って「石に付いた傷」に見える（round6で実証）。奥半分に限る。"""
    if math.sin(alpha) <= 0.05:
        return 0.0
    d = math.cos(alpha) * VL[0] + math.sin(alpha) * VL[1]
    return math.sqrt(max(0.0, 1.0 - d * d))

# 🔴 hero の位相は3つの積で決める。どれか1つを最大化すると必ず他が落ちる：
#    ① taper  光が自分の長さ方向に変化しているか（これが無いとただの輪＝LEDリング）
#    ② arm    挽き木が背景に対して立って見えるか（「回す道具」の宣言）
#    ③ 面積   見える隙間の量。ここが痩せると閾値1.2を越えず**ブルームが死ぬ**（round7で実測 halo 572）
def still_score(i):
    a = 2 * math.pi * i / N_FRAMES
    return taper(a) * arm_proj(a) * _AS[i]

STILL_FRAME = max(range(N_FRAMES), key=still_score) + 1


def hex_to_linear(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)

LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- マテリアル ----------
def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]

# 石：#17-b マット寄り。ただし #45 の下限 0.10 は絶対に割らない
mat_stone, sp = principled("stone")
sp.inputs["Base Color"].default_value = BLACK
sp.inputs["Roughness"].default_value = 0.62
sp.inputs["Specular IOR Level"].default_value = 0.16
# 石の肌：Object座標のノイズ→Bump。石と一緒に回るので回転が読める（フラットシェードの面と併せて）
snt = mat_stone.node_tree
stc = snt.nodes.new("ShaderNodeTexCoord")
sno = snt.nodes.new("ShaderNodeTexNoise")
sno.inputs["Scale"].default_value = 15.0
sno.inputs["Detail"].default_value = 8.0
sno.inputs["Roughness"].default_value = 0.55
sbu = snt.nodes.new("ShaderNodeBump")
sbu.inputs["Strength"].default_value = 0.45
sbu.inputs["Distance"].default_value = 0.017
snt.links.new(stc.outputs["Object"], sno.inputs["Vector"])
snt.links.new(sno.outputs["Fac"], sbu.inputs["Height"])
snt.links.new(sbu.outputs["Normal"], sp.inputs["Normal"])

mat_wood, wp = principled("handle")
wp.inputs["Base Color"].default_value = BLACK
wp.inputs["Roughness"].default_value = 0.54
wp.inputs["Specular IOR Level"].default_value = 0.26   # 挽き手は手擦れした木。#45 の下限を割らない


def radial_glow(name, r_from, r_to, es_from, es_to, core=0.0, core_r=0.0, core_pow=1.4):
    """Object座標の径方向グラデで発光。#32 Base純黒で裏当てを兼ねる。
       #35 のとおり座標は「そのオブジェクトのローカル」＝回っても伸びても壊れない。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0, 0, 0, 1)
    p.inputs["Specular IOR Level"].default_value = 0.0
    p.inputs["Emission Color"].default_value = LIME
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])

    def mnode(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None: n.inputs[1].default_value = val
        return n

    x2, y2 = mnode('POWER', 2.0), mnode('POWER', 2.0)
    nt.links.new(sep.outputs["X"], x2.inputs[0]); nt.links.new(sep.outputs["Y"], y2.inputs[0])
    ad = mnode('ADD'); nt.links.new(x2.outputs[0], ad.inputs[0]); nt.links.new(y2.outputs[0], ad.inputs[1])
    rr = mnode('SQRT'); nt.links.new(ad.outputs[0], rr.inputs[0])

    band = nt.nodes.new("ShaderNodeMapRange")
    band.inputs["From Min"].default_value = r_from; band.inputs["From Max"].default_value = r_to
    band.inputs["To Min"].default_value = es_from;  band.inputs["To Max"].default_value = es_to
    band.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(rr.outputs[0], band.inputs["Value"])
    out = band.outputs["Result"]

    if core > 0.0:
        cm = nt.nodes.new("ShaderNodeMapRange")
        cm.inputs["From Min"].default_value = 0.0; cm.inputs["From Max"].default_value = core_r
        cm.inputs["To Min"].default_value = 1.0;   cm.inputs["To Max"].default_value = 0.0
        cm.interpolation_type = 'SMOOTHSTEP'
        nt.links.new(rr.outputs[0], cm.inputs["Value"])
        cp = mnode('POWER', core_pow); nt.links.new(cm.outputs["Result"], cp.inputs[0])
        cx = mnode('MULTIPLY', core);  nt.links.new(cp.outputs[0], cx.inputs[0])
        sm = mnode('ADD'); nt.links.new(band.outputs["Result"], sm.inputs[0])
        nt.links.new(cx.outputs[0], sm.inputs[1])
        out = sm.outputs[0]
    nt.links.new(out, p.inputs["Emission Strength"])
    return m

# 挽き面：中心で作られ、外へ広がりながら薄まる（#27 の勾配を「面の中の物語」として使う）
mat_bed = radial_glow("glow_bed", 0.10, 0.86, ES_IN, ES_OUT)
# 供給口の穀：ホットコア → #A5E02E → 穴の壁で落ちる（#14／#28 黒ベゼル）
mat_hop = radial_glow("glow_hopper", 0.0, R_HOLE, ES_CBASE, ES_CBASE,
                      core=ES_CORE, core_r=R_HOLE, core_pow=1.4)

mat_floor, fp = principled("floor")
fp.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp.inputs["Roughness"].default_value = 0.42
mat_text, tp = principled("text")
tp.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp.inputs["Roughness"].default_value = 0.6

# ---------- 旋盤（lathe）ヘルパ ----------
def hewn(a, zi, ph):
    """手で割った石の肌。方位 a と輪郭点 zi の関数＝高さ方向にも崩れる。
       決定的（乱数なし）なので、360°回しても自分に一致する＝完全ループは壊れない。"""
    return (0.0105 * math.sin(3 * a + 0.6 + ph)
            + 0.0068 * math.sin(5 * a + 2.1 + ph)
            + 0.0040 * math.sin(11 * a + 4.4 + ph)
            + 0.0046 * math.sin(2 * a + 1.7 * zi + ph)
            + 0.0032 * math.sin(7 * a + 2.6 * zi + ph))


def lathe(name, prof, nseg, mat, hw=None, jph=0.0, closed=False, smooth=0.0):
    """prof: [(r,z)…]。r=0 は極（1頂点）。closed=True で最後→最初も繋ぐ（穴あき＝トーラス位相）。
       hw: 輪郭点ごとの「石の崩し」重み（0..1）。0にした点は真円のまま残る
           ＝上臼の底の縁は真円に保ち、発光板がはみ出さないようにするために要る。"""
    bm = bmesh.new()
    rings = []
    for zi, (r, z) in enumerate(prof):
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            w = 1.0 if hw is None else hw[zi]
            ring = []
            for k in range(nseg):
                a = 2 * math.pi * k / nseg
                sc = HEW * w * min(1.0, r / 0.35)
                rr = r + sc * hewn(a, zi, jph)
                # 径方向だけ崩すと**天面（ほぼ水平な面）は平らなまま**残る＝そこだけ樹脂に見える。
                # z にも崩しを入れると使い減りの起伏が出る。hw=0 の輪は動かないので発光板は守られる。
                zz = z + sc * 0.42 * hewn(a, zi + 3.7, jph + 1.1)
                ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), zz)))
            rings.append(ring)
    pairs = [(i, i + 1) for i in range(len(prof) - 1)]
    if closed:
        pairs.append((len(prof) - 1, 0))
    for i, j in pairs:
        A, B = rings[i], rings[j]
        if len(A) == 1 or len(B) == 1:
            pole = A[0] if len(A) == 1 else B[0]
            ring = B if len(A) == 1 else A
            for k in range(nseg):
                bm.faces.new((pole, ring[k], ring[(k + 1) % nseg]))
        else:
            for k in range(nseg):
                bm.faces.new((A[k], A[(k + 1) % nseg], B[(k + 1) % nseg], B[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    if smooth > 0.0:
        bpy.ops.object.select_all(action='DESELECT')   # rig(Empty)が選択に残るとモディファイア警告が出る
        bpy.context.view_layer.objects.active = o
        o.select_set(True); bpy.ops.object.shade_auto_smooth(angle=smooth); o.select_set(False)
    return o

# ---------- リグ（傾きの親） ----------
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, CENTER_Z))
rig = bpy.context.active_object; rig.name = "rig"
rig.rotation_euler = (TILT, 0, 0)      # 天面をカメラ側へ倒す

def attach(o, parent, loc):
    o.location = loc
    o.parent = parent
    o.matrix_parent_inverse.identity()   # #016 の教訓：matrix_parent_inverse を使うとズレる

# ---------- 下臼（動かない） ----------
# 🔴 round2 の事故：下臼の天面が上臼より 0.06 も張り出していたため、そこが**棚**になって
#    随伴点光源に照らされ、隙間から漏れる光でなく「塗られた輪」になった（#24／#32）。
#    合わせ面では上臼とほぼ面一にし、下へ向かってだけ広がる石にする。
LO = [(0.0, -H_LO),
      (R_LO_BOT - 0.052, -H_LO),
      (R_LO_BOT, -H_LO + 0.062),     # 底の欠け
      (R_LO_TOP, -0.115),            # 胴。下ほど太い＝合わせ面の下に「光を受ける肩」ができる
      (R_UP, 0.0),                   # 🔴 合わせ面の縁は上臼と**面一**。棚を作らない（hw=0で真円）
      (0.0, 0.0)]
lower = lathe("lower", LO, NSEG, mat_stone, hw=[0, 1.0, 1.0, 0.85, 0.0, 0], jph=0.0)
attach(lower, rig, (0, 0, 0))

# ---------- 挽き面（発光体・動かない） ----------
PUCK = [(0.0, 0.004), (R_PUCK, 0.004), (R_PUCK, 0.0), (0.0, 0.0)]
bed = lathe("bed", PUCK, 96, mat_bed, hw=[0, 0, 0, 0])
attach(bed, rig, (0, 0, 0))

# ---------- 上臼（回る＋歳差） ----------
# 🔴 底の2点だけ真円のまま残す（hw=0）。ここを崩すと縁が痩せた方位で発光板が顔を出し、
#    「隙間から漏れる光」が「裸の発光板」に転ぶ（round1 の事故そのもの）。
#    使う面ほど摺れて平らになるので、造形としてもこれが正しい。
# 天面は**窪ませる**（使い減りの皿）。平らだと「蓋」、盛り上げると「ベーグル」に読めた（round1/2）
# 🔴 底の外反りは 0.036 も取ってはいけない。楔（0.0025〜0.0615）に定数が乗ると
#    口の開閉比が 25倍→2.5倍まで潰れ、三日月にならず一定の輪になる（round2/3で実証・047のSLIT_Wと同型）
UP = [(R_HOLE, 0.0),
      (R_UP - 0.010, 0.0),
      (R_UP, 0.008),
      (R_UP, H_UP - 0.050),
      (R_UP - 0.046, H_UP),          # 天面の外周＝いちばん高い
      (R_UP * 0.55, H_UP - 0.048),   # 皿の底
      (R_HOLE + 0.070, H_UP - 0.030),
      (R_HOLE, H_UP + 0.006)]        # 供給口のまわりだけ少し立つ
upper = lathe("upper", UP, NSEG, mat_stone,
              hw=[0, 0, 0, 1.0, 1.0, 0.9, 0.7, 0], jph=1.9, closed=True)
attach(upper, rig, (0, 0, GAP))

# ---------- 供給口の穀（光る面） ----------
bm = bmesh.new()
RH = R_HOLE - 0.005
DOME = 0.020
rings = []
for ri in range(9):
    r = RH * ri / 8
    if ri == 0:
        rings.append([bm.verts.new((0, 0, DOME))]); continue
    ring = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), DOME * (1 - (r / RH) ** 2))))
    rings.append(ring)
for i in range(8):
    A, B = rings[i], rings[i + 1]
    if len(A) == 1:
        for k in range(48):
            bm.faces.new((A[0], B[k], B[(k + 1) % 48]))
    else:
        for k in range(48):
            bm.faces.new((A[k], A[(k + 1) % 48], B[(k + 1) % 48], B[k]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
me = bpy.data.meshes.new("hopper"); bm.to_mesh(me); bm.free()
hopper = bpy.data.objects.new("hopper", me)
bpy.context.collection.objects.link(hopper)
hopper.data.materials.append(mat_hop)
bpy.context.view_layer.objects.active = hopper
hopper.select_set(True); bpy.ops.object.shade_auto_smooth(angle=1.2); hopper.select_set(False)
attach(hopper, upper, (0, 0, H_UP + 0.030 - FILL_DEPTH))

# ---------- 挽き木（回す道具であることの宣言） ----------
# 🔴 round1/2 の型の失敗（#33）：同軸の円盤2枚＋光る赤道＝それ自体が「ロータリーノブ／家電」の記号で、
#    石の肌も三日月の光もその内側の話にすぎなかった。**回転対称を破って「手で回す道具」にする**。
#    垂直の柄だけではアンテナに見える。L字の腕まで出して初めて臼になる（#42 と同型の構造的な直し）。
def tube(name, p0, p1, r0, r1, seg=22):
    d = Vector(p1) - Vector(p0); L = d.length
    bm = bmesh.new()
    q = d.to_track_quat('Z', 'Y')
    A, B = [], []
    for k in range(seg):
        a = 2 * math.pi * k / seg
        A.append(bm.verts.new(Vector(p0) + q @ Vector((r0 * math.cos(a), r0 * math.sin(a), 0.0))))
        B.append(bm.verts.new(Vector(p0) + q @ Vector((r1 * math.cos(a), r1 * math.sin(a), L))))
    for k in range(seg):
        bm.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))
    for ring, p in ((A, p0), (B, p1)):
        c = bm.verts.new(Vector(p))
        for k in range(seg):
            bm.faces.new((c, ring[k], ring[(k + 1) % seg]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat_wood)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = o
    o.select_set(True); bpy.ops.object.shade_auto_smooth(angle=0.9); o.select_set(False)
    return o

ZP = H_UP - 0.036               # 柄の根元（皿の中）。上臼のローカル系なので GAP は足さない
ZK = ZP + PEG_H                  # 肘
ARM_END = R_UP + 0.235           # 腕の先。伸ばしすぎると #18 の占有を割る
arms = [tube("arm_post", (PEG_AT, 0, ZP), (PEG_AT, 0, ZK + 0.004), 0.060, 0.049),
        tube("arm_beam", (PEG_AT - 0.082, 0, ZK - 0.006), (ARM_END, 0, ZK - 0.006), 0.030, 0.042),
        # #21：自由端は必ず細らせる。切りっぱなしの平キャップは「鉄パイプの口」に見える
        tube("arm_grip", (ARM_END - 0.175, 0, ZK - 0.006), (ARM_END + 0.052, 0, ZK - 0.006), 0.058, 0.022)]
for a in arms:
    attach(a, upper, (0, 0, 0))

# ---------- 随伴点光源（#22：光を「塗装」にしないため） ----------
def lamp(name, parent, loc, radius, energy):
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
    L = bpy.context.active_object; L.name = name
    L.data.shadow_soft_size = radius
    L.data.energy = energy
    L.data.color = LIME[:3]
    L.visible_camera = False        # 光源そのものは写さない（隙間から玉が覗くのを防ぐ）
    attach(L, parent, loc)
    return L

lamp("lamp_gap", rig, (0, 0, 0.014), 0.36, LAMP_GAP)
lamp("lamp_hopper", upper, (0, 0, H_UP + 0.030 - FILL_DEPTH + 0.045), 0.075, LAMP_HOP)

# ---------- アニメーション（回転キーだけ＝glbにそのまま乗る） ----------
for i in range(N_FRAMES + 1):                      # +1 は折り返し（glb用）。レンダーは1..120
    a = 2 * math.pi * i / N_FRAMES
    upper.rotation_euler = (BETA, 0.0, a)          # XYZ順＝ Rz(a)·Rx(β)＝狂いの方位が回る＝歳差
    upper.keyframe_insert("rotation_euler", frame=i + 1)
# #1：action.fcurves は 5.x で廃止。補間設定に頼らず**毎フレーム打つ**（等間隔の直線ランプなので
#      既定のベジェ補間でも折れない）。値は α=2πi/N で計算しているので歪みはゼロ。

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_floor)

def caption(body, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object; tx.name = name
    tx.data.body = body; tx.data.size = size; tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx

caps = [caption("Designing the Middle of Your Story.", 0.1, (0.15, -1.7, 0.62), "tagline"),
        caption("monaka design.", 0.06, (0.15, -1.7, 0.45), "logo"),
        caption("MIDDLE STUDY 048 — ISHIUSU", 0.045, (0.15, -1.7, 0.34), "study")]

def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

focus = (0, 0, CENTER_Z)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((0.1, 0, CENTER_Z + 0.02)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = upper
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception:
    scene.view_settings.view_transform = 'AgX'

def setup_bloom():
    ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    ou = ng.nodes.new("NodeGroupOutput")
    try: gl.inputs["Type"].default_value = 'BLOOM'
    except Exception: pass
    gl.inputs["Threshold"].default_value = 1.2
    gl.inputs["Strength"].default_value = 0.35
    try: gl.inputs["Size"].default_value = 0.55
    except Exception: pass
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], ou.inputs["Image"])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True
setup_bloom()

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME)

if "probe" in modes:
    print(">> CLEARANCE  隙間 min %.4f / max %.4f m（min>0.006 なら食い込まない）"
          % (GAP - R_UP * math.sin(BETA), GAP + R_UP * math.sin(BETA)))
    print(">> #40⑥ 見える隙間の投影面積  min/max = %.3f  （合格 0.75以下）"
          % (min(_AS) / max(_AS)))
    print("   最大 frame %d ／ 最小 frame %d" % (_AS.index(max(_AS)) + 1, _AS.index(min(_AS)) + 1))
    # 楔がいちばん開いた方位が一周しているか＝「光が縁を移動する」の実測
    print(">> SWEEP  楔の開いた方位（deg・ローカル）")
    for i in range(0, N_FRAMES, 15):
        a = 2 * math.pi * i / N_FRAMES
        print("   f%3d  α=%6.1f°  開き方位=%6.1f°  面積=%.5f"
              % (i + 1, math.degrees(a), (math.degrees(a) + 90) % 360, _AS[i]))
    # bbox（#18 占有）
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, zs = [], []
    for o in [lower, upper, hopper, bed] + arms:
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            w = ev.matrix_world @ v.co
            xs.append(w.x); zs.append(w.z)
    print(">> BBOX  x %.3f..%.3f (%.3f)  z %.3f..%.3f (%.3f)  ／ フレーム 横2.81・縦3.52"
          % (min(xs), max(xs), max(xs) - min(xs), min(zs), max(zs), max(zs) - min(zs)))
    print(">> 占有  横%.0f%%  縦%.0f%%   キャプション上端 0.72 とのクリアランス %.3f"
          % ((max(xs) - min(xs)) / 2.81 * 100, (max(zs) - min(zs)) / 3.52 * 100, min(zs) - 0.72))

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 480, 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero done")

if "phases" in modes:
    # #35 ループものは still 以外の位相も撮る（材質側の破綻は1枚では出ない）
    for fr in (46, 78):
        scene.frame_set(fr)
        scene.render.resolution_x, scene.render.resolution_y = 480, 600
        scene.cycles.samples = 24
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(OUT, "_phase_%03d.png" % fr)
        bpy.ops.render.render(write_still=True)
    print(">> phases done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = 720, 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> anim done")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_048.blend"))

# 🔴 glb は必ず最後（#30：Emission を定数へ潰すので、レンダーの前に置かない）
if "glb" in modes:
    for m, es in ((mat_bed, 2.4), (mat_hop, 3.4)):
        p = m.node_tree.nodes["Principled BSDF"]
        for l in list(m.node_tree.links):
            if l.to_socket == p.inputs["Emission Strength"]:
                m.node_tree.links.remove(l)
        p.inputs["Emission Strength"].default_value = es
    scene.frame_end = N_FRAMES + 1      # 折り返しのキーまで含める
    for o in bpy.data.objects:
        o.select_set(o.name in ("rig", "lower", "upper", "hopper", "bed",
                                "arm_post", "arm_beam", "arm_grip"))
    bpy.context.view_layer.objects.active = upper
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
