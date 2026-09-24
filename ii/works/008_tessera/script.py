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

# ------------------------------------------------------------- LOOK（毎回決める）
LOOK = dict(
    aspect=(1, 1),
    lens=85,
    fstop=8.0,
    view="Standard",
    look="Medium Contrast",
    exposure=0.0,
)
FPS = 24

# 納品寸法：長辺で決める（hero 2560 / loop 1080）
def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


def hex_to_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


# ------------------------------------------------------------- 初期化
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------- 造形の道具
def bevel_obj(ob, width, segments=3, clamp=True, angle=30):
    """🔴 面取りは bmesh で（BEVELモディファイア＋harden_normals は硬く見える）。
    Boolean 合体後の仕上げは clamp=False（clamp=True だと極小エッジに引っ張られ面取りが0に縮む）。
    薄板に clamp=False を掛けると反転して針状に潰れる＝薄いものは合体に混ぜず clamp=True で別部品。"""
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    edges = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(angle)]
    bmesh.ops.bevel(bm, geom=edges, offset=width, segments=segments, profile=0.5,
                    affect='EDGES', clamp_overlap=clamp)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return ob


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, trans=0.0, ior=1.45):
    """roughness の目安：モノは 0.16〜0.55（0.8 はキャラの肌の値で、モノが粘土に見える）"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    return m


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.8), shape='RECTANGLE'):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.shape, ld.size = energy, color, shape, size
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


# ------------------------------------------------------------- 舞台：床（中灰）＋奥の壁（チャコール）
def plane(name, verts, color, rough):
    me = bpy.data.meshes.new(name + "_me"); me.from_pydata(verts, [], [(0, 1, 2, 3)]); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.data.materials.append(principled(name, hex_to_linear(color), rough=rough))
    return ob

WALL_Y = 1.1
floor = plane("floor", [(-12, -12, 0), (12, -12, 0), (12, WALL_Y, 0), (-12, WALL_Y, 0)], "#6E6E6E", 0.7)
wall = plane("wall", [(-12, WALL_Y, 0), (12, WALL_Y, 0), (12, WALL_Y, 9), (-12, WALL_Y, 9)], "#141414", 0.8)

# 壁は光を受けない沈んだ面（キーと床の光が当たって灰に浮くため・round 6）
_wm = wall.data.materials[0]; _nt = _wm.node_tree
for _n in list(_nt.nodes):
    if _n.type != 'OUTPUT_MATERIAL':
        _nt.nodes.remove(_n)
_em = _nt.nodes.new("ShaderNodeEmission")
_em.inputs["Color"].default_value = hex_to_linear("#2A2A2A"); _em.inputs["Strength"].default_value = 1.0
_nt.links.new(_em.outputs[0], _nt.nodes["Material Output"].inputs["Surface"])

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.02, 0.02, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3

# ------------------------------------------------------------- 被写体：浮き彫りのタイル盤 6×6
PAL = {k: hex_to_linear(v) for k, v in dict(
    R="#F0493A", Y="#F7C744", S="#79CBEE", N="#23255C", C="#E6DFD2", M="#6FD0A8",
    P="#F5A3B7", B="#3350D6", O="#FF8636", G="#29A35F").items()}
MATS = {}


def mat(k):
    if k not in MATS:
        m = principled("pl_" + k, PAL[k], rough=0.32, coat=0.0)
        MATS[k] = m
    return MATS[k]


parts, movers = [], []
CELL, NC = 0.2, 6
X0, Z0 = -CELL * NC / 2, 0.0


def finish(ob, bev, seg=3):
    bevel_obj(ob, bev, segments=seg)
    wn = ob.modifiers.new("wn", 'WEIGHTED_NORMAL'); wn.mode = 'FACE_AREA'; wn.keep_sharp = True
    parts.append(ob)
    return ob


def box(name, cx, cz, w, h, yf, depth, col, bev=0.0035):
    """前面 y=yf・奥行き depth（+Y 向き）の角丸箱"""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * w, yf + depth / 2 + v.co.y * depth, v.co.z * h))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.location = (cx, 0, cz)
    ob.data.materials.append(mat(col))
    return finish(ob, bev)


def sector(name, cx, cz, r0, r1, a0, a1, yf, depth, col, bev=0.004, n=None):
    """円・輪・扇・四分円を1つの関数で。原点は (cx, 0, cz)＝回すときの軸"""
    full = (a1 - a0) >= 2 * math.pi - 1e-6
    n = n or max(12, int(160 * (a1 - a0) / (2 * math.pi) * min(1.0, 0.35 + r1 * 3)))
    angs = [a0 + (a1 - a0) * i / n for i in range(n if full else n + 1)]
    bm = bmesh.new()
    lay = []
    for y in (yf, yf + depth):
        o = [bm.verts.new((r1 * math.cos(a), y, r1 * math.sin(a))) for a in angs]
        if r0 > 0:
            i = [bm.verts.new((r0 * math.cos(a), y, r0 * math.sin(a))) for a in angs]
        else:
            i = [bm.verts.new((0, y, 0))] * len(angs)
        lay.append((o, i))
    m = len(angs)
    rng = range(m) if full else range(m - 1)
    (oF, iF), (oB, iB) = lay
    for k in rng:
        k2 = (k + 1) % m
        for (o, i) in lay:
            if r0 > 0:
                bm.faces.new((o[k], o[k2], i[k2], i[k]))
            else:
                bm.faces.new((o[k], o[k2], i[0]))
        bm.faces.new((oF[k], oB[k], oB[k2], oF[k2]))
        if r0 > 0:
            bm.faces.new((iF[k], iF[k2], iB[k2], iB[k]))
    if not full:
        for k in (0, m - 1):
            if r0 > 0:
                bm.faces.new((oF[k], iF[k], iB[k], oB[k]))
            else:
                bm.faces.new((oF[k], iF[0], iB[0], oB[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.location = (cx, 0, cz)
    ob.data.materials.append(mat(col))
    return finish(ob, bev)


def prism(name, cx, cz, pts, yf, depth, col, bev=0.004):
    bm = bmesh.new()
    F = [bm.verts.new((x, yf, z)) for x, z in pts]
    B = [bm.verts.new((x, yf + depth, z)) for x, z in pts]
    bm.faces.new(F); bm.faces.new(list(reversed(B)))
    n = len(pts)
    for k in range(n):
        bm.faces.new((F[k], B[k], B[(k + 1) % n], F[(k + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.location = (cx, 0, cz)
    ob.data.materials.append(mat(col))
    return finish(ob, bev)


def cell_center(r, c, w=1, h=1):
    return X0 + CELL * (c + w / 2), Z0 + CELL * (NC - r - h / 2)


import random
rnd = random.Random(8)
G = 0.0035   # 目地（片側）


def tile(r, c, w, h, col, depth=None):
    cx, cz = cell_center(r, c, w, h)
    d = depth if depth is not None else rnd.choice((0.03, 0.05, 0.075, 0.1))
    if (r == 0 or r + h == NC) and d > 0.02:
        d = 0.06   # 外周の上下は厚みを揃える（見下ろし・見上げで下辺・上辺がガタつくため）
    box("t%d%d" % (r, c), cx, cz, CELL * w - 2 * G, CELL * h - 2 * G, -d, d, col)
    return cx, cz, -d


def dots(r, c, col, k, base, dr=None):
    cx, cz, yf = tile(r, c, 1, 1, base)
    if k == 2:
        rr, sp, grid = dr or 0.029, 0.047, [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        grid = [(a * sp, b * sp) for a, b in grid]
    elif k == 3:
        rr, sp = dr or 0.021, 0.058
        grid = [(a * sp, b * sp) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    else:   # 5 = 十字
        rr, sp = dr or 0.021, 0.058
        grid = [(0, 0), (sp, 0), (-sp, 0), (0, sp), (0, -sp)]
    for j, (dx, dz) in enumerate(grid):
        sector("d%d%d_%d" % (r, c, j), cx + dx, cz + dz, 0, rr, 0, 2 * math.pi, yf - 0.014, 0.016, col,
               bev=0.003, n=40)


def disc(r, c, col, base, rad=0.072):
    cx, cz, yf = tile(r, c, 1, 1, base)
    sector("disc%d%d" % (r, c), cx, cz, 0, rad, 0, 2 * math.pi, yf - 0.022, 0.024, col, bev=0.006)


def half(r, c, col, base, rot=0.0):
    cx, cz, yf = tile(r, c, 1, 1, base)
    sector("half%d%d" % (r, c), cx, cz, 0, 0.088, rot, rot + math.pi, yf - 0.02, 0.022, col, bev=0.005)


def quarter(r, c, col, base, corner=(-1, -1)):
    cx, cz, yf = tile(r, c, 1, 1, base)
    px, pz = cx + corner[0] * (CELL / 2 - G - 0.006), cz + corner[1] * (CELL / 2 - G - 0.006)
    a0 = math.atan2(-corner[1], -corner[0]) - math.pi / 4
    sector("q%d%d" % (r, c), px, pz, 0, 0.15, a0, a0 + math.pi / 2, yf - 0.02, 0.022, col, bev=0.005)


def steps(r, c, cols):
    cx, cz, yf = tile(r, c, 1, 1, cols[0])
    for j, col in enumerate(cols[1:]):
        s = CELL - 2 * G - 0.05 * (j + 1)
        yf -= 0.018
        box("st%d%d_%d" % (r, c, j), cx, cz, s, s, yf, 0.02, col, bev=0.004)


def tri(r, c, col, base, flip=False):
    cx, cz, yf = tile(r, c, 1, 1, base)
    h = CELL / 2 - G - 0.004
    pts = [(-h, -h), (h, -h), (-h, h)] if not flip else [(h, -h), (h, h), (-h, h)]
    prism("tri%d%d" % (r, c), cx, cz, pts, yf - 0.024, 0.026, col, bev=0.005)


def ribs(r, c, w, h, col, base, n, vertical=True):
    cx, cz, yf = tile(r, c, w, h, base, depth=0.03)
    L = (CELL * (h if vertical else w)) - 2 * G - 0.02
    span = CELL * (w if vertical else h) - 2 * G - 0.02
    rr = span / n / 2 * 0.86
    for j in range(n):
        off = -span / 2 + span / n * (j + 0.5)
        if vertical:
            box("rb%d%d_%d" % (r, c, j), cx + off, cz, rr * 2, L, yf - rr * 1.4, rr * 1.4, col, bev=rr * 0.95)
        else:
            box("rb%d%d_%d" % (r, c, j), cx, cz + off, L, rr * 2, yf - rr * 1.4, rr * 1.4, col, bev=rr * 0.95)


def grille(r, c, w, h, col, n, dcol=None, ndots=0, vertical=True):
    cx, cz, yf = tile(r, c, w, h, "N", depth=0.012)
    W, H = CELL * w - 2 * G, CELL * h - 2 * G
    rr = 0.0042
    y = -0.045
    span = (W if vertical else H) - 0.012
    for j in range(n):
        off = -span / 2 + span * j / (n - 1)
        if vertical:
            box("gr%d%d_%d" % (r, c, j), cx + off, cz, rr * 2, H - 0.004, y, rr * 2, col, bev=rr * 0.9)
        else:
            box("gr%d%d_%d" % (r, c, j), cx, cz + off, W - 0.004, rr * 2, y, rr * 2, col, bev=rr * 0.9)
    for j in range(ndots):
        dz = (j - (ndots - 1) / 2) * (H / ndots)
        sector("gd%d%d_%d" % (r, c, j), cx, cz + dz, 0, 0.03, 0, 2 * math.pi, y - 0.018, 0.018, dcol,
               bev=0.003, n=40)


def pill(r, c, w, h, col, base):
    cx, cz, yf = tile(r, c, w, h, base, depth=0.025)
    pw, ph = CELL * w - 0.09, CELL * h - 0.07
    box("pill%d%d" % (r, c), cx, cz, pw, ph, yf - 0.045, 0.045, col, bev=min(pw, ph) / 2 * 0.98)


# 裏板（凹みの底＝紺）
box("backplate", 0, CELL * NC / 2, CELL * NC + 0.004, CELL * NC + 0.004, 0.0, 0.03, "N", bev=0.006)

# --- 大きな部品：2×2 の輪（右上）と、2×2 の四分円の虹（左下）
rcx, rcz, ryf = tile(1, 3, 2, 2, "S", depth=0.05)
ring_out = sector("ring_out", rcx, rcz, 0.13, 0.222, 0, 2 * math.pi, ryf - 0.085, 0.085, "B", bev=0.008)
ring_mid = sector("ring_mid", rcx, rcz, 0.066, 0.13, 0.0, 1.5 * math.pi, ryf - 0.11, 0.11, "P", bev=0.008)
ring_mid.rotation_euler[1] = math.radians(45)
ring_cap = sector("ring_cap", rcx, rcz, 0.066, 0.13, 1.5 * math.pi, 2 * math.pi, ryf - 0.07, 0.07, "Y", bev=0.008)
ring_cap.rotation_euler[1] = math.radians(45)
ring_core = sector("ring_core", rcx, rcz, 0, 0.066, 0, 2 * math.pi, ryf - 0.05, 0.05, "R", bev=0.007)
movers += [ring_out, ring_mid, ring_cap]

qcx, qcz, qyf = tile(4, 0, 2, 2, "C", depth=0.04)
qx, qz = qcx - CELL + G + 0.006, qcz - CELL + 0.0015
bands = [(0.27, 0.37, "R", 0.028), (0.17, 0.27, "O", 0.05), (0.08, 0.17, "Y", 0.072), (0.0, 0.08, "B", 0.094)]
arcs = []
for j, (a, b, col, dz) in enumerate(bands):
    arcs.append(sector("arc%d" % j, qx, qz, a, b - 0.004, 0, math.pi / 2, qyf - dz, dz, col, bev=0.006))
movers += arcs

# --- 1セルの部品（配置は手で決める）
dots(0, 0, "S", 3, "C")
ribs(0, 1, 2, 1, "O", "O", 15, vertical=True)
disc(0, 3, "Y", "G")
steps(0, 4, ["P", "C", "R"])
ribs(0, 5, 1, 1, "P", "N", 7, vertical=False)

half(1, 0, "R", "Y")
dots(1, 1, "Y", 2, "B")
tri(1, 2, "S", "N")
dots(1, 5, "C", 5, "R")

quarter(2, 0, "B", "M", corner=(1, 1))
grille(2, 1, 1, 2, "P", 9, dcol="Y", ndots=3)
disc(2, 2, "S", "R", rad=0.06)
dots(2, 5, "S", 2, "Y")

dots(3, 0, "R", 5, "P")
steps(3, 2, ["Y", "O", "C"])
grille(3, 3, 1, 1, "S", 8, vertical=False)
half(3, 4, "G", "C", rot=math.pi)
dots(3, 5, "Y", 3, "G")

dots(4, 2, "N", 5, "S")
disc(4, 3, "R", "Y", rad=0.082)
dots(4, 4, "S", 2, "R")
tri(4, 5, "Y", "B", flip=True)

_x, _z, _y = tile(5, 2, 1, 1, "P", depth=0.05)
sector("sring", _x, _z, 0.04, 0.074, 0, 2 * math.pi, _y - 0.02, 0.022, "B", bev=0.005)
dots(5, 3, "C", 3, "S")
quarter(5, 4, "O", "Y", corner=(-1, 1))
disc(5, 5, "G", "M", rad=0.07)

# ------------------------------------------------------------- 光：正面左上の大きな面光源1灯＋弱い起こし
PANEL_C = (0, 0, CELL * NC / 2)
key = area("key", (2.4, -2.6, 1.9), 1.8, 250, (1.0, 0.97, 0.93), target=PANEL_C)
fill = area("fill", (-2.8, -3.5, 1.6), 3.0, 60, (0.95, 0.97, 1.0), target=PANEL_C)
fill.data.specular_factor = 0.3
floor_l = area("floorlight", (0, -2.6, 3.0), 5.0, 30, (1, 1, 1), target=(0, -1.0, 0))

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
TGT = Vector((0, 0, 0.6))
HERO = dict(deg=-4.0, dist=4.0, h=0.6, tgt=Vector((0.0, 0, 0.6)))
RC = Vector((ring_core.location.x, -0.1, ring_core.location.z))


def hero_cam(k=1.0):
    return orbit(HERO["tgt"], HERO["dist"] * k, HERO["h"], HERO["deg"])


SHOTS = [
    dict(sec=3.0,   # マクロ：上段の粒の列を斜めになめる＋ピント送り
         cam=lambda t: (lerp((-0.95, -1.1, 1.16), (-0.55, -1.25, 1.12), ease(t)),
                        lerp((-0.5, 0, 1.1), (-0.2, 0, 1.07), ease(t)), 135, 2.4, None)),
    dict(sec=3.0,   # 物の動き：輪が回って所定の位置に噛む
         cam=lambda t: (lerp(RC + Vector((0.35, -2.1, 0.25)), RC + Vector((0.22, -1.8, 0.18)), ease(t)),
                        RC, 100, 5.0, None)),
    dict(sec=2.5,   # スライド：左手前の低い位置から、左の列を斜めになめて上がる
         cam=lambda t: (lerp((-1.25, -1.45, 0.3), (-1.2, -1.5, 0.78), ease(t)),
                        lerp((-0.25, 0, 0.26), (-0.2, 0, 0.66), ease(t)), 70, 4.0, None)),
    dict(sec=3.0,   # 決め：寄りから引いて hero で止まる
         cam=lambda t: (lerp(orbit(HERO["tgt"], HERO["dist"] * 0.8, HERO["h"] + 0.1, HERO["deg"] - 14),
                             hero_cam(), ease_out(min(1.0, t / 0.6))), HERO["tgt"],
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

REST = {o.name: tuple(o.rotation_euler) for o in movers}
REST_LOC = {o.name: tuple(o.location) for o in movers}


def pose(i, t, T):
    """カット2で輪が回って止まる／カット3で虹の弧が1枚ずつ押し出されて戻る"""
    for o in movers:
        o.rotation_euler = REST[o.name]
        o.location = REST_LOC[o.name]
    if i == 0:
        k = 0.0
    elif i == 1:
        k = ease(min(1.0, t / 0.85))
    else:
        k = 1.0
    ring_out.rotation_euler[1] = REST["ring_out"][1] + math.radians(-120) * (1 - k)
    ring_mid.rotation_euler[1] = REST["ring_mid"][1] + math.radians(200) * (1 - k)
    ring_cap.rotation_euler[1] = REST["ring_cap"][1] + math.radians(200) * (1 - k)
    if i == 2:
        for j, a in enumerate(arcs):
            u = max(0.0, min(1.0, (t - 0.12 * j) / 0.5))
            a.location.y = REST_LOC[a.name][1] - 0.03 * math.sin(math.pi * u)


def light_path(i, t):
    pass


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
        cd.dof.focus_distance = focus if focus else (Vector(tgt) - Vector(loc)).length
        for path in ("location", "rotation_euler"):
            cam.keyframe_insert(path, frame=f)
        cd.keyframe_insert("lens", frame=f)
        cd.dof.keyframe_insert("aperture_fstop", frame=f)
        cd.dof.keyframe_insert("focus_distance", frame=f)
        pose(i, t, T)
        for o in movers:
            o.keyframe_insert("rotation_euler", frame=f)
            o.keyframe_insert("location", frame=f)

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
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
