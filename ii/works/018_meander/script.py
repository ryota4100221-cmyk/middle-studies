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
    aspect=(3, 2),
    lens=55,
    fstop=8.0,
    view="Standard",
    look="Medium High Contrast",
    exposure=-1.55,
    bg=(0.80, 0.80, 0.79),
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


# ------------------------------------------------------------- 舞台：白い壁（XZ 面・y=0）
wall_me = bpy.data.meshes.new("wall_me")
wall_me.from_pydata([(-6, 0.0005, -2), (6, 0.0005, -2), (6, 0.0005, 6), (-6, 0.0005, 6)], [], [(0, 1, 2, 3)])
wall = bpy.data.objects.new("wall", wall_me); scene.collection.objects.link(wall)
wall.data.materials.append(principled("wall", LOOK["bg"] + (1.0,), rough=0.85))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

# ------------------------------------------------------------- 被写体：トルシェの陶板
# 正方形の板（S）に、向かい合う2つの角を中心にした四分円の半円筒を2本ずつ載せる。
# 板を 0/90° に回して並べると、管が板をまたいで曲がりくねる1本の道になる。
S, GAP, T = 0.10, 0.0008, 0.009          # 板の一辺・目地・板厚（m）
RHO = 0.0195                              # 管の半径
RADII = (S / 2,)                          # 1本の太い管
CENTER = Vector((0.0, 0.0, 1.40))         # 塊の中心（壁の上）
MASK = [                                  # 上の行から。X＝板あり
    "...XX...",
    "..XXX.X.",
    ".XXXXXXX",
    "XXXXXX..",
    ".XXXXX..",
    "..XXXXXX",
    "XXXXXX.X",
    "..XXX...",
    "...X....",
]
import random
rng = random.Random(18)


DROP = 1.0
WOBBLE = 0.06
SEED_OFF = Vector((0, 0, 0))
from mathutils import noise


def add_half_tube(bm, c, R, rho, a0, a1, z0, nseg=56, nprof=24):
    rings = []
    for i in range(nseg + 1):
        a = a0 + (a1 - a0) * i / nseg
        d = Vector((math.cos(a), math.sin(a), 0))
        ring = []
        for j in range(nprof + 1):
            al = math.asin(min(0.95, 0.40 * DROP))   # 板面より下まで断面を回して、底を板に埋める
            f = -al + (math.pi + 2 * al) * j / nprof
            p0 = Vector((c[0], c[1], z0)) + d * R
            k = 1.0 + WOBBLE * noise.noise(p0 * 22.0 + SEED_OFF)            # 手で成形した太さのゆらぎ
            p = p0 + d * (rho * k * math.cos(f)) + Vector((0, 0, rho * k * math.sin(f)))
            ring.append(bm.verts.new(p))
        rings.append(ring)
    for i in range(nseg):
        A, B = rings[i], rings[i + 1]
        for j in range(nprof):
            bm.faces.new((A[j], B[j], B[j + 1], A[j + 1]))
        bm.faces.new((A[nprof], B[nprof], B[0], A[0]))      # 底
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))


def tile_mesh(name):
    bm = bmesh.new()
    h = (S - GAP) / 2
    res_ = bmesh.ops.create_cube(bm, size=1.0)
    for v in res_["verts"]:
        v.co = Vector((v.co.x * 2 * h, v.co.y * 2 * h, (v.co.z + 0.5) * T))
    plate_faces = list(bm.faces)
    # 角 (-S/2,-S/2) と (+S/2,+S/2) を中心にした四分円
    for (cx, cy, base) in ((-S / 2, -S / 2, 0.0), (S / 2, S / 2, math.pi)):
        for R in RADII:
            a0 = math.asin((GAP / 2) / R)
            add_half_tube(bm, (cx, cy), R, RHO, base + a0, base + math.pi / 2 - a0, T + 0.35 * RHO)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in plate_faces:
        f.material_index = 1                              # 板＝釉が溜まった濃い緑
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


def glaze():
    m = principled("glaze", hex_to_linear("#2A8C58"), rough=0.40, coat=0.0)
    m.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.42
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    info = nt.nodes.new("ShaderNodeObjectInfo")
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    mr = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(info.outputs["Random"], mr.inputs["Value"])
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.88, 1.10
    hsv.inputs["Color"].default_value = p.inputs["Base Color"].default_value
    nt.links.new(mr.outputs["Result"], hsv.inputs["Value"])
    nt.links.new(hsv.outputs["Color"], p.inputs["Base Color"])
    # 釉のゆらぎ（ごく弱い凹凸）
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90.0
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05
    bump.inputs["Distance"].default_value = 0.0004
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


GLAZE = glaze()
POOL = GLAZE.copy(); POOL.name = "glaze_pool"
POOL.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.55
POOL.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.25
next(n for n in POOL.node_tree.nodes if n.type == 'MAP_RANGE').inputs["To Min"].default_value = 0.50
next(n for n in POOL.node_tree.nodes if n.type == 'MAP_RANGE').inputs["To Max"].default_value = 0.60
ROT = {}


def arc_at(r, c, corner):
    """板 (r,c) が corner（'TL','TR','BL','BR'）に弧を持つか。rot0＝左下と右上、rot1＝右下と左上"""
    if (r, c) not in ROT:
        return False
    return corner in (("BL", "TR") if ROT[(r, c)] == 0 else ("BR", "TL"))


def closes_ring(r, c):
    # (r,c) の4つの角の頂点それぞれで、囲む4枚が全部その頂点に弧を向けていたら輪
    for dr, dc in ((0, 0), (0, 1), (1, 0), (1, 1)):     # 頂点＝板 (r0,c0) の右下
        r0, c0 = r - 1 + dr, c - 1 + dc
        if (arc_at(r0, c0, "BR") and arc_at(r0, c0 + 1, "BL") and
                arc_at(r0 + 1, c0, "TR") and arc_at(r0 + 1, c0 + 1, "TL")):
            return True
    return False


def pick_rot(r, c):
    order = rng.sample((0, 1), 2)
    for o in order:
        ROT[(r, c)] = o
        if not closes_ring(r, c):
            return o
    ROT[(r, c)] = order[0]
    return order[0]


parts, tiles = [], []
rows, cols = len(MASK), len(MASK[0])
for r, line in enumerate(MASK):
    for c, ch in enumerate(line):
        if ch != "X":
            continue
        SEED_OFF = Vector((r * 7.3, c * 3.1, 0.0))
        ob = tile_mesh("tile_%d_%d" % (r, c))
        bevel_obj(ob, 0.0011, segments=3)
        ob.data.materials.append(GLAZE)
        ob.data.materials.append(POOL)
        u = (c - (cols - 1) / 2) * S
        v = ((rows - 1) / 2 - r) * S
        ob.rotation_mode = 'ZYX'
        rot = pick_rot(r, c)
        ob["home"] = (CENTER.x + u, CENTER.y, CENTER.z + v)
        ob["rot"] = rot
        ob.location = ob["home"]
        ob.rotation_euler = (math.radians(90), 0, math.radians(90 * rot))
        parts.append(ob); tiles.append(ob)

# ------------------------------------------------------------- 光：左上手前の大きく柔らかい1灯＋弱い返し
area("key", (-2.8, -7.4, 5.2), 5.0, 2300, (1.0, 0.98, 0.95), target=tuple(CENTER))
area("fill", (1.8, -2.2, 1.2), 2.5, 25, (0.95, 0.97, 1.0), target=tuple(CENTER))

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
TGT = CENTER + Vector((0.17, 0, 0))
HERO_CAM = Vector((-0.02, -2.65, 1.50))
SPIN = [t for t in tiles if t.name in ("tile_2_3", "tile_4_1", "tile_3_5", "tile_5_3")]
SHOTS = [
    dict(sec=3.0,   # スライド：壁すれすれの左から、管の起伏をなめて横へ
         cam=lambda t: (lerp((-0.80, -0.40, 1.20), (-0.62, -0.42, 1.52), ease(t)),
                        lerp((0.05, 0, 1.36), (0.12, 0, 1.46), ease(t)), 50, 5.6, None)),
    dict(sec=2.6,   # マクロ：塊の中の管の継ぎ目に寄ってピント送り
         cam=lambda t: (lerp((0.12, -0.30, 1.50), (0.06, -0.28, 1.47), ease(t)), Vector((-0.03, 0, 1.40)),
                        120, 4.0, 0.25 + 0.05 * ease(t))),
    dict(sec=3.2,   # 物の動き：右下からの3/4。板が浮いて90°回り、道がつなぎ変わる
         cam=lambda t: (lerp((0.72, -1.30, 1.05), (0.62, -1.38, 1.12), ease(t)), CENTER + Vector((0.02, 0, 0.02)),
                        55, 8.0, None)),
    dict(sec=3.0,   # 決め：引きながら入って hero の構図で止まる
         cam=lambda t: (lerp((-0.05, -2.10, 1.46), HERO_CAM, ease_out(min(1.0, t / 0.6))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    for k, ob in enumerate(SPIN):
        if i < 2:
            u = 0.0
        elif i == 2:
            u = max(0.0, min(1.0, (t - 0.08 - 0.14 * k) / 0.42))
        else:
            u = 1.0
        hx, hy, hz = ob["home"]
        ob.location = (hx, hy - 0.045 * math.sin(math.pi * ease(u)), hz)
        ob.rotation_euler = (math.radians(90), 0, math.radians(90 * (ob["rot"] - 1 + ease(u))))


key_light = None


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
        for o in parts:
            o.keyframe_insert("rotation_euler", frame=f)
            o.keyframe_insert("location", frame=f)
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
