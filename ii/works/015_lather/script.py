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

# ------------------------------------------------------------- LOOK（015 LATHER）
LOOK = dict(
    aspect=(5, 4),
    lens=100,
    fstop=22.0,               # 実寸（m）で 0.68m 先＝f22 で被写界深度 ±3cm＝積み全体にピント
    view="AgX",
    look="AgX - Base Contrast",
    exposure=-0.35,
    bg=(0.53, 0.50, 0.40),
)
FPS = 24
# 尺（N_FRAMES）と静止画のフレーム（STILL_FRAME）は、下の「動画」節の SHOTS から決まる

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


# ------------------------------------------------------------- 舞台：背景紙（実寸 m）
R, W, D, H = 0.30, 4.0, 2.0, 2.0
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 16 * math.pi / 2 for i in range(1, 17)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + 0.42, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
paper = principled("paper", LOOK["bg"] + (1.0,), rough=0.85)
paper.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15
sweep.data.materials.append(paper)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.52, 0.47, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0

# ------------------------------------------------------------- 被写体：3つの石鹸（平面の形を変える）
def plan_outline(a, b, nexp, N=320):
    """超楕円 |x/a|^n+|y/b|^n=1 を弧長で等間隔に取り直す（角で辺が粗くならないように）"""
    raw = []
    for i in range(4000):
        t = 2 * math.pi * i / 4000
        c, s_ = math.cos(t), math.sin(t)
        raw.append((a * math.copysign(abs(c) ** (2 / nexp), c), b * math.copysign(abs(s_) ** (2 / nexp), s_)))
    L = [0.0]
    for i in range(1, len(raw) + 1):
        p0, p1 = raw[i - 1], raw[i % len(raw)]
        L.append(L[-1] + math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
    out, j = [], 0
    for k in range(N):
        d = L[-1] * k / N
        while L[j + 1] < d:
            j += 1
        f = (d - L[j]) / max(1e-12, L[j + 1] - L[j])
        p0, p1 = raw[j], raw[(j + 1) % len(raw)]
        out.append((p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f))
    return out


def bar(name, a, b, h, nexp, bev, seg=4):
    ol = plan_outline(a, b, nexp)
    bm = bmesh.new()
    vb = [bm.verts.new((x, y, 0.0)) for x, y in ol]
    vt = [bm.verts.new((x, y, h)) for x, y in ol]
    N = len(ol)
    bm.faces.new(list(reversed(vb)))
    bm.faces.new(vt)
    for i in range(N):
        j = (i + 1) % N
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bm.normal_update()
    me = bpy.data.meshes.new(name + "_me"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    bevel_obj(ob, bev, segments=seg, angle=40)
    return ob


def soap(name, hexcol, sss_rgb, rough=0.52, sss=0.55, scale=0.004, spec=0.12):
    m = principled(name, hex_to_linear(hexcol), rough=rough)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Subsurface Radius"].default_value = sss_rgb
    p.inputs["Subsurface Scale"].default_value = scale
    p.inputs["Specular IOR Level"].default_value = spec
    # 石鹸の肌：ごく細かい凹凸（型抜きの肌理）
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0
    nz.inputs["Detail"].default_value = 4.0
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.16
    bp.inputs["Distance"].default_value = 0.0002
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nzb = nt.nodes.new("ShaderNodeTexNoise"); nzb.inputs["Scale"].default_value = 520.0
    nzb.inputs["Detail"].default_value = 6.0; nzb.inputs["Roughness"].default_value = 0.65
    nt.links.new(tc.outputs["Object"], nzb.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = 'ADD'
    nt.links.new(nz.outputs["Fac"], mx.inputs[0]); nt.links.new(nzb.outputs["Fac"], mx.inputs[1])
    nt.links.new(mx.outputs["Value"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    # 蝋の中の淡いむら（明度だけ ±5%）
    nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 160.0
    nz2.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.88; mr.inputs["To Max"].default_value = 1.07
    nt.links.new(nz2.outputs["Fac"], mr.inputs["Value"])
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    hsv.inputs["Color"].default_value = hex_to_linear(hexcol)
    nt.links.new(mr.outputs["Result"], hsv.inputs["Value"])
    # 切り口の崩れ：Bevel の法線と面の法線の差で縁だけを取り、欠け（バンプ）と白けた粒を入れる
    bev = nt.nodes.new("ShaderNodeBevel"); bev.inputs["Radius"].default_value = 0.0028; bev.samples = 8
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dt = nt.nodes.new("ShaderNodeVectorMath"); dt.operation = 'DOT_PRODUCT'
    nt.links.new(bev.outputs["Normal"], dt.inputs[0]); nt.links.new(geo.outputs["Normal"], dt.inputs[1])
    em = nt.nodes.new("ShaderNodeMapRange")
    em.inputs["From Min"].default_value = 0.998; em.inputs["From Max"].default_value = 0.975
    nt.links.new(dt.outputs["Value"], em.inputs["Value"])          # 縁=1・平らな面=0
    nz3 = nt.nodes.new("ShaderNodeTexNoise"); nz3.inputs["Scale"].default_value = 1400.0
    nz3.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], nz3.inputs["Vector"])
    gt = nt.nodes.new("ShaderNodeMapRange")
    gt.inputs["From Min"].default_value = 0.52; gt.inputs["From Max"].default_value = 0.64
    nt.links.new(nz3.outputs["Fac"], gt.inputs["Value"])
    chip = nt.nodes.new("ShaderNodeMath"); chip.operation = 'MULTIPLY'
    nt.links.new(em.outputs["Result"], chip.inputs[0]); nt.links.new(gt.outputs["Result"], chip.inputs[1])
    lite = nt.nodes.new("ShaderNodeHueSaturation")
    lite.inputs["Saturation"].default_value = 0.9; lite.inputs["Value"].default_value = 1.3
    nt.links.new(hsv.outputs["Color"], lite.inputs["Color"])
    mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = 'RGBA'
    sk = lambda n, nm, io: next(x for x in (n.inputs if io else n.outputs) if x.name == nm and x.type == 'RGBA')
    nt.links.new(chip.outputs["Value"], mx2.inputs["Factor"])
    nt.links.new(hsv.outputs["Color"], sk(mx2, "A", 1)); nt.links.new(lite.outputs["Color"], sk(mx2, "B", 1))
    nt.links.new(sk(mx2, "Result", 0), p.inputs["Base Color"])
    hh = nt.nodes.new("ShaderNodeMath"); hh.operation = 'MULTIPLY_ADD'
    nt.links.new(chip.outputs["Value"], hh.inputs[0]); hh.inputs[1].default_value = -1.5
    nt.links.new(mx.outputs["Value"], hh.inputs[2])
    nt.links.new(hh.outputs["Value"], bp.inputs["Height"])           # 欠けは凹む
    return m


# 下：角の丸い厚板（セージ）
H1, H2, H3 = 0.040, 0.034, 0.034
low = bar("low", 0.048, 0.034, H1, 40.0, 0.0006, seg=3)
low.location = (0.004, 0.0, 0.0); low.rotation_euler = (0, 0, math.radians(-40))
low.data.materials.append(soap("sage", "#776D52", (1.0, 1.0, 0.85)))

# 中：楕円の小判（クリーム・いちばん透ける）。壁がわずかに膨らみ、天面がゆるく盛り上がる型抜きの断面
def pebble(name, a, b, h, nexp, dome):
    ol = plan_outline(a, b, nexp, N=256)
    prof = [(0.975, 0.0), (0.993, 0.0012), (1.0, 0.004), (1.004, h * 0.45), (1.0, h * 0.78),
            (0.985, h * 0.90), (0.955, h * 0.965), (0.91, h + dome * 0.15), (0.80, h + dome * 0.45),
            (0.62, h + dome * 0.75), (0.38, h + dome * 0.93), (0.15, h + dome)]
    bm = bmesh.new()
    rings = [[bm.verts.new((x * sc, y * sc, z)) for x, y in ol] for sc, z in prof]
    N = len(ol)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(N):
            j = (i + 1) % N
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    c0 = bm.verts.new((0, 0, 0.0)); c1 = bm.verts.new((0, 0, h + dome * 1.02))
    for i in range(N):
        j = (i + 1) % N
        bm.faces.new((rings[0][j], rings[0][i], c0))
        bm.faces.new((rings[-1][i], rings[-1][j], c1))
    bm.normal_update()
    me = bpy.data.meshes.new(name + "_me"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    return ob


DOME = 0.0022
mid = pebble("mid", 0.045, 0.031, H2, 3.6, DOME)
mid.location = (0.010, -0.002, H1); mid.rotation_euler = (0, 0, math.radians(-36))
mid.data.materials.append(soap("cream", "#C6B994", (1.0, 0.9, 0.7), rough=0.46, sss=0.85, scale=0.006))

# 上：天面に3本の溝を刻んだ角（焼けた橙）
top = bar("top", 0.040, 0.028, H3, 40.0, 0.0006, seg=3)
bm = bmesh.new(); bm.from_mesh(top.data)
ed = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(40)
      and max(v.co.z for v in e.verts) < 0.0015]
bmesh.ops.bevel(bm, geom=ed, offset=0.0009, segments=3, profile=0.5, affect='EDGES', clamp_overlap=True)
bm.to_mesh(top.data); bm.free()   # 下の縁だけ太い面取り＝透けた縁が光を拾う
for k, gx in enumerate((0.012, 0.020, 0.028)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=1.0,
                                         location=(gx, 0.0, H3 + 0.0026 - 0.0011))
    cut = bpy.context.object
    cut.scale = (0.0026, 0.017, 0.0026)   # 両端の丸い溝（縁まで抜かない）
    md = top.modifiers.new("g%d" % k, 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut
    md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = top
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cut)
bm = bmesh.new(); bm.from_mesh(top.data)
ed = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(40)
      and min(v.co.z for v in e.verts) > H3 - 0.0015 and abs(e.verts[0].co.x) < 0.040]
bmesh.ops.bevel(bm, geom=ed, offset=0.0005, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
bm.to_mesh(top.data); bm.free()
for p in top.data.polygons:
    p.use_smooth = abs(p.normal.z) < 0.999   # 🔴 Boolean 後の多角形の天面をスムーズにすると V 字の陰の割れが出る
top.data.materials.clear()
top.data.materials.append(soap("terracotta", "#93421E", (1.0, 0.45, 0.25), rough=0.52, sss=0.8, scale=0.008))
top.location = (-0.010, 0.004, H1 + H2 + DOME * 0.97)   # 盛り上がりの頂に乗る
top.rotation_euler = (0, 0, math.radians(-24))
parts = [low, mid, top]   # 🔴 被写体は全部ここへ

# ------------------------------------------------------------- 光：左やや手前の大きな1灯＋右の消し板
key = area("key", (-0.60, 0.10, 0.13), 0.25, 30, (1.0, 0.95, 0.88), target=(0.0, 0.0, 0.05))
wall = area("wall", (-0.3, -0.2, 0.9), 0.8, 1.0, (1.0, 0.96, 0.9), target=(-0.25, 0.42, 0.18))
flag_me = bpy.data.meshes.new("flag_me")
flag_me.from_pydata([(0, -0.3, 0), (0, 0.3, 0), (0, 0.3, 0.5), (0, -0.3, 0.5)], [], [(0, 1, 2, 3)])
flag = bpy.data.objects.new("flag", flag_me); scene.collection.objects.link(flag)
flag.location = (0.17, -0.02, 0.03)
flag.rotation_euler = (0, 0, math.radians(-35))
flag.data.materials.append(principled("black", (0.003, 0.003, 0.003, 1), rough=0.9))
flag.visible_camera = False
flag.visible_shadow = False
fill = area("fill", (0.45, -0.55, 0.12), 0.7, 0.3, (0.75, 0.88, 1.0), target=(0.0, 0.0, 0.05))
fill_col = bpy.data.collections.new("soaps_only")
for L in (key, wall, fill):
    L.visible_camera = False
    L.visible_glossy = False
for o in parts:
    fill_col.objects.link(o)
fill.light_linking.receiver_collection = fill_col   # 陰の面にだけ無彩の起こし（基準の陰は灰みのオリーブ 37,35,28）
stage_col = bpy.data.collections.new("stage_only")
stage_col.objects.link(sweep)
wall.light_linking.receiver_collection = stage_col   # 壁の起こしは紙だけに（石鹸の右面を黒く保つ）

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
TGT = Vector((0.002, 0.0, 0.054))
HERO_CAM = Vector((0.0, -0.68, 0.135))
TOP_REST = top.location.copy()
TOP_ROT = top.rotation_euler[2]
bpy.context.view_layer.update()
GROOVE = top.matrix_world @ Vector((0.020, 0.0, H3))      # 溝の中ほど（天面）
GDIR = (top.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()   # 溝を横切る向き

SHOTS = [
    dict(sec=3.0,   # マクロ：天面の3本の溝を横切ってなめる（ピントは溝に置いたまま）
         cam=lambda t: (GROOVE + GDIR * (-0.040 + 0.045 * ease(t)) + Vector((0.0, -0.20, 0.17)),
                        GROOVE + GDIR * (-0.014 + 0.024 * ease(t)), 135, 16.0, None)),
    dict(sec=3.0,   # 物の動き：上の角が降りてきて、盛り上がりの頂に収まる（カメラは右上から回り込む）
         cam=lambda t: (orbit(TGT, 0.52, 0.16 - 0.03 * ease(t), 24 - 16 * ease(t)),
                        Vector((0.0, 0.0, 0.085)), 85, 16.0, None)),
    dict(sec=2.5,   # 光の走り：右の陰の面と床の影。キーが奥から回り込み、影が床を掃く
         cam=lambda t: (lerp((0.20, -0.40, 0.05), (0.15, -0.42, 0.06), ease(t)),
                        Vector((0.05, 0.0, 0.035)), 100, 16.0, None)),
    dict(sec=3.0,   # 決め：右下から滑り込んで hero の構図で止まる
         cam=lambda t: (lerp((0.17, -0.60, 0.065), HERO_CAM, ease_out(min(1.0, t / 0.6))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    top.location = TOP_REST.copy()
    top.rotation_euler = (0, 0, TOP_ROT)
    if i == 1:
        u = min(1.0, t / 0.9)
        k = (1 - u) ** 2                     # 置くように減速して収まる
        top.location.z = TOP_REST.z + 0.035 * k
        top.rotation_euler = (0, 0, TOP_ROT + math.radians(14) * k)


key_light = bpy.data.objects.get("key")
KEY_REST = key_light.location.copy()
KEY_TGT = Vector((0.0, 0.0, 0.05))


CUR_F = [1]


def light_path(i, t):
    loc = KEY_REST.copy()
    if i == 2:
        loc = lerp((-0.38, 0.48, 0.16), KEY_REST, ease(t))
    key_light.location = loc
    key_light.rotation_euler = (KEY_TGT - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    key_light.keyframe_insert("rotation_euler", frame=CUR_F[0])


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
        for o in parts:
            o.keyframe_insert("rotation_euler", frame=f)
            o.keyframe_insert("location", frame=f)
        CUR_F[0] = f
        light_path(i, t)
        if key_light:
            key_light.keyframe_insert("location", frame=f)

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


def film_grain(path, sigma=4.0 / 255, seed=15):
    """写真の粒を後から乗せる（#104：肌理をレンダー内で作るとモアレ）"""
    import numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, sigma, (w * h, 1)).astype(np.float32)
    px[:, :3] = np.clip(px[:, :3] + n, 0.0, 1.0)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = path; img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


if "test" in modes:
    still(os.path.join(OUT, "_test.png"), 720, 48)
    print(">> test done")

if "testhero" in modes:
    still(os.path.join(OUT, "_testhero.png"), 1600, 128)
    film_grain(os.path.join(OUT, "_testhero.png"))
    print(">> testhero done")

if "shots" in modes:    # 各カットの頭・中・終わり（ii/scripts/contact.py で1枚に並べる）
    for i, sh in enumerate(SHOTS):
        for j, frac in enumerate((0.0, 0.5, 1.0)):
            fr = shot_start[i] + round(frac * (sh["frames"] - 1))
            still(os.path.join(OUT, "_shot_%d_%d.png" % (i, j)), 480, 24, fr)
    print(">> shots done")

if "still" in modes:
    still(os.path.join(OUT, "hero.png"), 2560, 256)
    film_grain(os.path.join(OUT, "hero.png"))
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
