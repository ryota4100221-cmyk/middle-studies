# =============================================================
# MIDDLE STUDIES II 020 — PLEAT（折）  FORM
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
#
# 細かい山谷折りを入れた白い紙の帯2本が、灰の壁の前でねじれながら絡む。
# 基準（Richard Sweeney の紙の彫刻）から取ったのは、左上の大きな柔らかい1灯で
# 折りの面ごとに白と灰が交互に割れる縞と、灰の壁×暖かい白の単色の組み立て。造形は自分で起こす。
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Quaternion

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(4, 5),
    lens=85,
    fstop=8.0,
    view="AgX",
    look="AgX - Medium High Contrast",
    exposure=0.0,
    bg=(0.118, 0.126, 0.146),   # 壁の灰（linear）
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


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.3), shape='RECTANGLE', size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.shape, ld.size = energy, color, shape, size
    if size_y:
        ld.size_y = size_y
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


# ------------------------------------------------------------- 舞台：灰の壁（被写体のすぐ後ろ）
WALL_Y = 0.60
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, WALL_Y, 0.3), rotation=(math.radians(90), 0, 0))
wall = bpy.context.object; wall.name = "wall"
wm = principled("wall", LOOK["bg"] + (1.0,), rough=0.9)
wall.data.materials.append(wm)
# 背景紙の左右の落ち（基準：左183→右134）。キーの減衰だけでは右が落ちきらないので、壁の地色に横の階調を持たせる
_n, _l = wm.node_tree.nodes, wm.node_tree.links
_tc = _n.new("ShaderNodeTexCoord"); _sep = _n.new("ShaderNodeSeparateXYZ"); _mr = _n.new("ShaderNodeMapRange")
_ramp = _n.new("ShaderNodeValToRGB")
_l.new(_tc.outputs["Object"], _sep.inputs["Vector"])
_l.new(_sep.outputs["X"], _mr.inputs["Value"])
_mr.inputs["From Min"].default_value, _mr.inputs["From Max"].default_value = -0.45, 0.50
_l.new(_mr.outputs["Result"], _ramp.inputs["Fac"])
_c = LOOK["bg"]
_ramp.color_ramp.elements[0].color = (_c[0] * 1.10, _c[1] * 1.10, _c[2] * 1.10, 1)
_ramp.color_ramp.elements[1].color = (_c[0] * 0.70, _c[1] * 0.70, _c[2] * 0.70, 1)
_l.new(_ramp.outputs["Color"], _n["Principled BSDF"].inputs["Base Color"])

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.30, 0.30, 0.30, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.09

# ------------------------------------------------------------- 造形：山谷折りの紙の帯
def catmull(pts, n):
    """制御点を通る滑らかな曲線を n 点で返す"""
    P = [Vector(p) for p in pts]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    segs = len(P) - 3
    out = []
    for k in range(n):
        u = k / (n - 1) * segs
        i = min(int(u), segs - 1); t = u - i
        p0, p1, p2, p3 = P[i:i + 4]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    return out


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def ribbon(name, spine_pts, width_fn, twist_fn, pitch, depth_fn, nv=14, up=(0, -1, 0), squeeze=0.80, serrate=True, crease=0.8):
    """spine に沿う帯。長手方向に pitch ごとの山谷折り（三角波）を入れる。
    width_fn(s)＝幅、twist_fn(s)＝ねじれ（度）、depth_fn(s, v)＝折りの深さ（v は 0=内縁→1=外縁）。
    シェイプキー "fold"＝紙の長さを保ったまま、蛇腹を squeeze 倍に縮めて折りを深くした形。"""
    dense = catmull(spine_pts, 4000)
    L = [0.0]
    for a, b in zip(dense, dense[1:]):
        L.append(L[-1] + (b - a).length)
    total = L[-1]
    n_pleat = int(total / pitch)
    SUB = 4                                     # 1折りを4分割（山・中・谷・中）
    ns = n_pleat * SUB + 1

    def at(dist):
        dist = max(0.0, min(total, dist))
        lo, hi = 0, len(L) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if L[mid] < dist: lo = mid
            else: hi = mid
        f = (dist - L[lo]) / max(1e-9, L[hi] - L[lo])
        return dense[lo].lerp(dense[hi], f), (dense[hi] - dense[lo]).normalized()

    # 平行移動フレーム
    frames = []
    W = None
    FR = [0.0, 0.35, 0.70, 0.85]           # 非対称の折り：山→谷が 0.7 ピッチ、谷→山が 0.3
    for k in range(ns):
        s = min(1.0, (k // SUB + FR[k % SUB]) / n_pleat)
        p, T = at(s * total)
        if W is None:
            W = (Vector(up) - T * Vector(up).dot(T)).normalized()
        else:
            W = (W - T * W.dot(T)).normalized()
        frames.append((s, p, T, W.copy()))

    def build(contract):
        verts = []
        for k, (s, p, T, W0) in enumerate(frames):
            # 縮めるとき：帯の中心（s=0.5）へ寄せる
            s2 = 0.5 + (s - 0.5) * contract
            p2, T2 = at(s2 * total)
            q = Quaternion(T2, math.radians(twist_fn(s2)))
            Wv = q @ (W0 - T2 * W0.dot(T2)).normalized()
            Nv = T2.cross(Wv).normalized()
            tri = [-1.0, 0.0, 1.0, 0.0][k % SUB]
            w = width_fn(s2)
            for j in range(nv):
                v = j / (nv - 1)
                d0 = depth_fn(s2, v)
                # 紙の長さを保つ：半ピッチ h と深さ d の斜辺を一定に
                h0 = pitch / 2
                l = math.hypot(h0, d0)
                h1 = h0 * contract
                d = math.sqrt(max(0.0, l * l - h1 * h1))
                edge = 0.0
                if serrate and j == nv - 1:
                    edge = 0.0 * w * tri       # 外縁は鋸歯
                if serrate and j == 0:
                    edge = 0.0 * w * tri
                off = (v - 0.5) * w + edge
                bend = crease * w * (v - 0.5) ** 2    # 曲線折り：折り目を幅方向に弧にする
                verts.append(p2 + Wv * off + Nv * (d * tri) + T2 * bend)
        return verts

    base = build(1.0)
    faces = []
    for k in range(ns - 1):
        for j in range(nv - 1):
            a = k * nv + j
            faces.append((a, a + 1, a + nv + 1, a + nv))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in base], [], faces); me.update()
    for poly in me.polygons:
        poly.use_smooth = True
    # 折り目（山・谷の横線）だけ鋭く
    sharp = me.attributes.new("sharp_edge", 'BOOLEAN', 'EDGE')
    for e in me.edges:
        a, b = e.vertices
        ka, kb = a // nv, b // nv
        if ka == kb and ka % SUB in (0, 2):
            sharp.data[e.index].value = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.shape_key_add(name="Basis")
    sk = ob.shape_key_add(name="fold")
    for i, v in enumerate(build(squeeze)):
        sk.data[i].co = v
    sol = ob.modifiers.new("paper", 'SOLIDIFY')
    sol.thickness = 0.0007
    sol.offset = 0.0
    sol.use_even_offset = False
    return ob


paper = principled("paper", (0.80, 0.78, 0.72, 1.0), rough=0.85)
pp = paper.node_tree.nodes["Principled BSDF"]
pp.inputs["Subsurface Weight"].default_value = 0.05
pp.inputs["Subsurface Radius"].default_value = (1.0, 0.95, 0.85)
pp.inputs["Subsurface Scale"].default_value = 0.002
pp.inputs["Sheen Weight"].default_value = 0.0
# 紙の繊維：細かいノイズを弱いバンプに
_pn, _pl = paper.node_tree.nodes, paper.node_tree.links
_nz = _pn.new("ShaderNodeTexNoise"); _nz.inputs["Scale"].default_value = 2600.0; _nz.inputs["Detail"].default_value = 4.0
_bp = _pn.new("ShaderNodeBump"); _bp.inputs["Strength"].default_value = 0.08; _bp.inputs["Distance"].default_value = 0.0002
_pl.new(_nz.outputs["Fac"], _bp.inputs["Height"]); _pl.new(_bp.outputs["Normal"], pp.inputs["Normal"])
pp.inputs["Specular IOR Level"].default_value = 0.25

# 帯A：左下から立ち上がり、上で外へ巻き返す大きな S
A = ribbon("bandA",
           [(-0.06, 0.02, 0.02), (0.05, -0.01, 0.10), (0.07, -0.04, 0.22), (-0.03, -0.02, 0.33),
            (-0.09, 0.00, 0.44), (-0.02, -0.04, 0.54), (0.08, -0.02, 0.56), (0.11, 0.02, 0.47)],
           width_fn=lambda s: 0.05 + 0.12 * math.sin(math.pi * min(1.0, 0.08 + s)) ** 0.5,
           twist_fn=lambda s: 50 + 130 * smoothstep(0.05, 0.95, s),
           pitch=0.011,
           depth_fn=lambda s, v: 0.0030 + 0.0080 * v * (0.9 + 0.1 * math.sin(math.pi * s)))
# 帯B：細い帯が右下から斜めに A をくぐり、左上へ抜ける
B = ribbon("bandB",
           [(0.07, -0.03, 0.03), (0.165, -0.01, 0.15), (0.205, -0.04, 0.32), (0.14, -0.07, 0.50),
            (-0.01, -0.06, 0.585), (-0.11, -0.03, 0.52)],
           width_fn=lambda s: 0.016 + 0.008 * math.sin(math.pi * s),
           twist_fn=lambda s: -60 + 300 * smoothstep(0.0, 1.0, s),
           pitch=0.009,
           depth_fn=lambda s, v: 0.0,
           serrate=False, nv=6,
           up=(1, 0, 0))
C = ribbon("bandC",
           [(-0.11, -0.03, 0.09), (-0.05, -0.07, 0.19), (0.03, -0.06, 0.29), (0.07, -0.03, 0.39), (0.01, 0.01, 0.47)],
           width_fn=lambda s: 0.015 + 0.075 * math.sin(math.pi * min(1.0, s * 1.15)) ** 0.8,
           twist_fn=lambda s: 50 - 140 * smoothstep(0.0, 1.0, s),
           pitch=0.008,
           depth_fn=lambda s, v: 0.0025 + 0.0060 * v)
for o in (A, B, C):
    o.data.materials.append(paper)

# 回転の中心を形の中心に置く空（被写体の動きはこの親を回す）
rig = bpy.data.objects.new("rig", None); scene.collection.objects.link(rig)
rig.location = (0, 0, 0.29)
for o in (A, B, C):
    o.parent = rig
    o.location = (0, 0, -0.29)
parts = [A, B, C]   # 被写体は全部ここへ

# ------------------------------------------------------------- 光
key = area("key", (-1.5, -0.8, 1.2), 1.0, 230, (1.0, 0.93, 0.80), target=(0.15, 0, 0.3))
fill = area("fill", (0.9, -1.5, 0.5), 2.2, 6, (0.97, 0.98, 1.0), target=(0, 0, 0.3))

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def orbit(center, radius, height, deg):
    r = math.radians(deg)
    return Vector((center[0] + radius * math.sin(r), center[1] - radius * math.cos(r), height))


TGT = Vector((0.027, 0, 0.30))
HERO_CAM = Vector((0.0, -1.72, 0.36))
# マクロの狙い：hero のカメラから画面上の点へ光線を飛ばし、紙の面に当たった位置と向きを取る
#   （目測の座標で狙うとピントが空を切る＝初回の shots でマクロが全面ぼけた）
rig.rotation_euler = (0, 0, math.radians(-8)); bpy.context.view_layer.update()


def pick(u, v):
    """hero の画面の (u, v)（左下0・右上1）に写っている紙の点と法線"""
    fwd = (TGT - HERO_CAM).normalized()
    right = fwd.cross(Vector((0, 0, 1))).normalized(); up = right.cross(fwd)
    h = 36 / LOOK["lens"]; w = h * LOOK["aspect"][0] / LOOK["aspect"][1]
    d = (fwd + right * (u - 0.5) * w + up * (v - 0.5) * h).normalized()
    hit, loc, nor, *_ = scene.ray_cast(bpy.context.evaluated_depsgraph_get(), HERO_CAM, d)
    print(">> pick", u, v, hit, tuple(round(x, 3) for x in loc))
    return loc, nor


M_LOC, M_NOR = pick(0.20, 0.64)                 # 上の扇の外縁近く（曲線折りと鋸歯と地が1枚に入る）
if M_NOR.dot(HERO_CAM - M_LOC) < 0:
    M_NOR = -M_NOR
M_SIDE = M_NOR.cross(Vector((0, 0, 1))).normalized()


def macro_cam(t):
    eye = M_LOC + M_NOR * 0.36 + M_SIDE * (0.05 - 0.09 * ease(t)) + Vector((0, 0, 0.04))
    tgt = M_LOC + M_SIDE * (0.03 - 0.04 * ease(t))
    # ピントは毎フレーム、カメラ→注視点の光線が紙に当たった距離（注視点が宙に浮くと全面ぼける）
    hit, loc, *_ = scene.ray_cast(bpy.context.evaluated_depsgraph_get(), eye, (tgt - eye).normalized())
    return eye, tgt, 120, 7.0, ((loc - eye).length if hit else (tgt - eye).length)


SHOTS = [
    dict(sec=3.0,   # スライド：寄りで帯の前を下から上へ滑る
         cam=lambda t: (lerp((-0.05, -0.72, 0.12), (-0.02, -0.70, 0.40), ease(t)),
                        lerp((0.0, 0, 0.10), (0.0, 0, 0.40), ease(t)), 70, 4.0, None)),
    dict(sec=3.0,   # マクロ：上の扇の曲線折りを横になめる（ピントは紙の面に当てた距離）
         cam=macro_cam),
    dict(sec=2.5,   # 物の動き：横から回り込みながら、蛇腹が縮んで折りが深くなる
         cam=lambda t: (orbit(TGT, 1.05, 0.22, 58 - 22 * ease(t)), TGT + Vector((0, 0, 0.02)), 85, 6.0, None)),
    dict(sec=3.0,   # 決め：下から引き上げながら入って hero の構図で止まる
         cam=lambda t: (lerp(HERO_CAM + Vector((-0.12, 0.45, -0.16)), HERO_CAM, ease_out(min(1.0, t / 0.6))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    """帯の束をわずかに回し、3カット目で蛇腹を縮めて戻す"""
    # 回すのは後半2カットだけ（マクロのピントを光線で測った姿勢を保つ）
    rig.rotation_euler = (0, 0, math.radians(-8 + 8 * ease(t) if i == 3 else (-8 + 3 * ease(t) if i == 2 else -8)))
    fold = 0.0
    if i == 2:
        fold = math.sin(math.pi * ease(t)) * 1.0
    for o in parts:
        o.data.shape_keys.key_blocks["fold"].value = fold


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
        rig.keyframe_insert("rotation_euler", frame=f)
        for o in parts:
            o.data.shape_keys.key_blocks["fold"].keyframe_insert("value", frame=f)
        light_path(i, t)

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

if "shots" in modes:
    for i, sh in enumerate(SHOTS):
        for j, frac in enumerate((0.0, 0.5, 1.0)):
            fr = shot_start[i] + round(frac * (sh["frames"] - 1))
            still(os.path.join(OUT, "_shot_%d_%d.png" % (i, j)), 480, 24, fr)
    print(">> shots done")

if "still" in modes:
    still(os.path.join(OUT, "hero.png"), 2560, 256)
    print(">> hero done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = res(int(os.environ.get("II_ANIM_LONG", "1080")))
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

if "glb" in modes:
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {"rig"}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True,
                              export_apply=False, export_morph=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
