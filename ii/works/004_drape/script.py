# =============================================================
# MIDDLE STUDIES II — 雛形（2026-09-23）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / phases   （省略時 test）
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
    aspect=(4, 3),
    lens=105,
    fstop=4.5,
    view="Standard",   # PBR Neutral は暗部の藍を群青へ持ち上げた（round 43 で4変換を実測）
    look="Medium High Contrast",
    exposure=-0.6,
    bg=(0.24, 0.24, 0.38),
)
FPS, SECONDS = 24, 7
N_FRAMES = FPS * SECONDS
STILL_FRAME = 1

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


# ------------------------------------------------------------- 被写体（毎回作る）
# 地は無い＝画面の全部が布。奥に明るい紫の起伏（羽毛布団のような丸い膨らみ＋鋭い折り目）、
# 手前に濃い藍の布が1枚、斜めの稜線になって被さる。高さ場は numpy で直接書く（布シムは使わない＝#43-e）
import numpy as np
rng = np.random.default_rng(4)


def smoothmax(stack, p):
    """p-ノルムの smooth-max。高さ0のドームは寄与しない（log-sum-exp は log(N)/s だけ全体を底上げして平らに潰した）"""
    return (np.clip(stack, 0, None) ** p).sum(axis=0) ** (1 / p)


def wrinkles(X, Y, seed, amp, kmin, kmax, n=14):
    r = np.random.default_rng(seed)
    out = np.zeros_like(X)
    for _ in range(n):
        th = r.uniform(0, math.pi); k = r.uniform(kmin, kmax); ph = r.uniform(0, 6.283)
        env = 0.5 + 0.5 * np.sin(X * r.uniform(0.2, 0.6) + Y * r.uniform(0.2, 0.6) + r.uniform(0, 6.283))
        out += env ** 2 * np.sin(k * (X * math.cos(th) + Y * math.sin(th)) + ph)
    return amp * out / n


def creases(X, Y, seed, count, xr, yr, depth, width):
    """鋭い折り目＝細い谷＋両脇の小さな盛り上がり。端は細らせる（#21）"""
    r = np.random.default_rng(seed)
    out = np.zeros_like(X)
    for _ in range(count):
        cx, cy = r.uniform(*xr), r.uniform(*yr)
        th = r.uniform(-0.9, 0.9) + (math.pi / 2 if r.random() < 0.5 else 0)
        L = r.uniform(0.6, 1.8); w = width * r.uniform(0.7, 1.4)
        u = (X - cx) * math.cos(th) + (Y - cy) * math.sin(th)
        v = -(X - cx) * math.sin(th) + (Y - cy) * math.cos(th)
        taper = np.clip(1 - (u / L) ** 2, 0, 1) ** 1.5
        prof = -np.exp(-(v / w) ** 2) + 0.45 * np.exp(-((np.abs(v) - 1.6 * w) / w) ** 2)
        out += depth * r.uniform(0.6, 1.2) * taper * prof
    return out


def back_height(X, Y):
    # 膨らみ＝ずらした格子の丸いドームを smooth-max で繋ぐ。繋ぎ目が折り目の谷になる
    domes = []
    for j, cy in enumerate(np.arange(-0.5, 30.0, 1.45)):
        for cx in np.arange(-7.0, 7.5, 1.75):
            px = cx + (0.87 if j % 2 else 0) + rng.uniform(-0.55, 0.55)
            py = cy + rng.uniform(-0.45, 0.45)
            R = rng.uniform(0.85, 1.35); h = rng.uniform(0.38, 0.68)
            th = rng.uniform(0, math.pi); el = rng.uniform(1.0, 1.6)   # 楕円の向きと扁平をばらばらに
            u = (X - px) * math.cos(th) + (Y - py) * math.sin(th)
            v = -(X - px) * math.sin(th) + (Y - py) * math.cos(th)
            r2 = (u / (R * el)) ** 2 + (v / R) ** 2
            domes.append(h * np.clip(1 - r2 ** 1.25, 0, 1) ** 1.5)   # 枕の断面：天が平らで縁は接線0（sqrt は縁で垂直の壁＝破片に見えた）
    H = smoothmax(np.stack(domes), 4.0)
    H += 0.10 * np.clip(Y - 2.5, 0, None)   # 遠くほど持ち上げ、上端まで布で埋める
    H -= 0.6 * np.clip((2.0 - Y) / 1.2, 0, 1) ** 2   # 手前の稜線の下では沈める（突き抜けると紙の縁に見えた）
    H += wrinkles(X, Y, 11, 0.014, 8.0, 18.0)
    H += creases(X, Y, 12, 220, (-6, 6), (0, 26), 0.03, 0.035)
    return H


def front_height(X, Y):
    # 手前の布：左下→右上へ斜めに上る稜線。稜線の向こうは奥の布の下へ落ちる
    d = (Y - 1.0 - 0.10 * X) + 0.30 * np.sin(X * 1.6 + 0.9)   # 稜線からの距離（奥が正）
    crest = 0.40 + 0.13 * X + 0.09 * np.sin(X * 2.0 + 0.4)
    H = np.where(d < 0, crest - 0.15 * d ** 2, crest - 2.5 * d ** 2)
    H += 0.09 * np.sin(1.9 * (X * 0.8 - Y * 0.6) + 0.4) * np.clip(-d, 0, 1.2) + 0.06 * np.sin(3.1 * (X * 0.5 + Y * 0.85) + 1.1) * np.clip(-d / 1.5, 0, 1) + 0.12 * np.sin(4.2 * X - 2.0 * Y + 0.3) * np.clip(-d - 0.6, 0, 1.5)   # 大きく緩い膨らみ（近景まで）
    for bx, by, br, bh in ((0.6, -0.7, 0.5, 0.09), (-0.7, -1.2, 0.5, 0.10), (0.3, -1.9, 0.6, 0.12), (0.52, 0.1, 0.35, 0.10), (0.42, -0.9, 0.35, 0.10)):   # 近景の大きな膨らみ（105mm の近景の画角は横 ±0.77）
        H += bh * np.exp(-((X - bx) ** 2 + (Y - by) ** 2) / br ** 2) * np.clip(-d / 0.6, 0, 1)
    H += 0.07 * np.exp(-((d + 1.35) / 0.35) ** 2) * np.clip(X + 0.3, 0, 1.5)   # 右下に稜線と平行な緩い折れ
    H += wrinkles(X, Y, 21, 0.02, 3.0, 7.0)
    H += creases(X, Y, 22, 12, (-2.5, 2.5), (-0.5, 1.2), 0.05, 0.07)
    return H


# 動き：布の下を通る「うねり」。cos/sin の2枚のシェイプキーを cos(2πt)/sin(2πt) で混ぜる＝進行波で、t=1 で閉じる
WAVES_BACK = [((1.0, 1.6), 0.07, 1), ((-1.5, 0.8), 0.04, 2)]   # (波数ベクトル, 振幅, 1ループの周回数)
WAVES_FRONT = [((1.6, 0.9), 0.05, 1)]


def build_sheet(name, fn, waves, xr, yr, nx, ny, mat):
    xs = np.linspace(*xr, nx); ys = np.linspace(*yr, ny)
    X, Y = np.meshgrid(xs, ys)
    Z = fn(X, Y)
    verts = np.stack([X, Y, Z], -1).reshape(-1, 3)
    idx = np.arange(nx * ny).reshape(ny, nx)
    faces = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts.tolist(), [], faces.tolist()); me.update()
    for p in me.polygons:
        p.use_smooth = True
    uv = me.uv_layers.new(name="UVMap")
    lx = np.array([v.co.x for v in me.vertices]); ly = np.array([v.co.y for v in me.vertices])
    loops = np.array([l.vertex_index for l in me.loops])
    uvs = np.stack([lx[loops], ly[loops]], -1).ravel()
    uv.data.foreach_set("uv", uvs)
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    me.materials.append(mat)
    ob.shape_key_add(name="Basis")
    keys = []
    for i, ((kx, ky), a, cyc) in enumerate(waves):
        env = a * (0.6 + 0.4 * np.sin(X * 0.4 + i))
        ph = kx * X + ky * Y
        for tag, f in (("c", np.cos), ("s", np.sin)):
            sk = ob.shape_key_add(name=f"w{i}{tag}")
            sk.slider_min, sk.slider_max = -1, 1
            co = verts.copy(); co[:, 2] += (env * f(ph)).ravel()
            sk.data.foreach_set("co", co.ravel())
            keys.append((sk, tag, cyc))
    for fr in range(1, N_FRAMES + 2):
        t = (fr - 1) / N_FRAMES
        for sk, tag, cyc in keys:
            sk.value = math.cos(2 * math.pi * cyc * t) if tag == "c" else math.sin(2 * math.pi * cyc * t)
            sk.keyframe_insert("value", frame=fr)
    return ob


def cloth_mat(name, base, sheen_tint, rough=0.6, weave=0.007, sheen=0.35, spec=0.35):
    m = principled(name, base, rough=rough)
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Sheen Weight"].default_value = sheen
    p.inputs["Sheen Roughness"].default_value = 0.35
    p.inputs["Sheen Tint"].default_value = sheen_tint
    p.inputs["Specular IOR Level"].default_value = spec
    # 織り目：縦糸・横糸の帯を掛け合わせて Bump に
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / weave,) * 3
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    wa = nt.nodes.new("ShaderNodeTexWave"); wa.bands_direction = 'X'; wa.inputs["Scale"].default_value = 2 * math.pi / 20
    wb = nt.nodes.new("ShaderNodeTexWave"); wb.bands_direction = 'Y'; wb.inputs["Scale"].default_value = 2 * math.pi / 20   # Wave の周期は 2π/(20·Scale)。Scale 1 だと weave の1/3で画面上2px＝消える
    for w in (wa, wb):
        w.wave_profile = 'SIN'
        w.inputs["Distortion"].default_value = 3.0   # 糸の揺らぎ（0だと縦縞のピンストライプに見えた）
        w.inputs["Detail Scale"].default_value = 2.0
        nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = 'MULTIPLY'
    nt.links.new(wa.outputs["Fac"], mx.inputs[0]); nt.links.new(wb.outputs["Fac"], mx.inputs[1])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25
    bp.inputs["Distance"].default_value = weave * 0.3
    nt.links.new(mx.outputs["Value"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    # 糸のムラ：細かいノイズで明度を±6%揺らす（完全に均一だと樹脂に見えた）
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0 / (weave * 1.5)
    nz.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["UV"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.94; mr.inputs["To Max"].default_value = 1.06
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = 'RGBA'; mc.blend_type = 'MULTIPLY'
    mc.inputs["Factor"].default_value = 1.0
    mc.inputs["A"].default_value = base
    nt.links.new(mr.outputs["Result"], mc.inputs["B"])
    nt.links.new(mc.outputs["Result"], p.inputs["Base Color"])
    return m


VIOLET = hex_to_linear("#8E50BC"); INDIGO = hex_to_linear("#2E2474")
m_back = cloth_mat("violet", VIOLET, hex_to_linear("#E2CCFF"))
m_front = cloth_mat("indigo", INDIGO, hex_to_linear("#3A3470"), rough=0.75, sheen=0.10, spec=0.04)
DENS = float(os.environ.get("II_DENS", "1.0"))
back = build_sheet("back", back_height, WAVES_BACK, (-7, 7), (0.0, 30.0), int(280 * DENS), int(600 * DENS), m_back)
front = build_sheet("front", front_height, WAVES_FRONT, (-3, 3), (-1.5, 2.0), int(300 * DENS), int(180 * DENS), m_front)
for o in (back, front):
    sub = o.modifiers.new("sub", 'SUBSURF'); sub.levels = 0; sub.render_levels = 1
parts = [back, front]

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = LOOK["bg"] + (1.0,)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3

# ------------------------------------------------------------- 光（毎回組む）
# 上やや奥から大きく柔らかい1灯＝膨らみの頂だけが起き、手前の布は光を背にする
area("key", (-9.0, 12.0, 6.0), 12.0, 2600, (1.0, 0.97, 1.0), target=(0, 4, 0))
area("top", (-2.0, 3.0, 8.0), 6.0, 90, (0.95, 0.92, 1.0), target=(0, 4, 0))
area("key2", (9.0, 13.0, 5.0), 12.0, 850, (0.95, 0.9, 1.0), target=(0, 5, 0))   # 右奥の返し：膨らみの陰の側を中間の紫まで起こす
area("side", (6.0, -1.5, 0.5), 4.0, 400, (0.9, 0.75, 0.85), target=(0.8, -0.8, 0.3))   # 右下の近景の起伏を拾う
area("fill", (3.5, -6.0, 2.2), 5.0, 300, (0.58, 0.58, 1.0), target=(0, 0.5, 0.3))

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.lens = LOOK["lens"]
cam.location = (-0.25, -4.5, 0.95)
AIM = Vector((-0.3, 3.0, 0.15))
cam.rotation_euler = (AIM - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True
cd.dof.focus_distance = (Vector((0.3, 0.4, 0.45)) - cam.location).length
cd.dof.aperture_fstop = LOOK["fstop"]
scene.camera = cam

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

if "phases" in modes:   # 動きの途中を4枚（ループの破綻は hero には出ない）
    for i, fr in enumerate((1, N_FRAMES // 4 + 1, N_FRAMES // 2 + 1, 3 * N_FRAMES // 4 + 1)):
        still(os.path.join(OUT, "_phase_%d.png" % i), 600, 32, fr)
    print(">> phases done")

if "still" in modes:
    still(os.path.join(OUT, "hero.png"), 2560, 256)
    print(">> hero done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = res(1080)
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
