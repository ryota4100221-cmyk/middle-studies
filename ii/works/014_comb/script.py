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
# 014 COMB — 直線に並べた薄い板の櫛。板の天端で、うねる溝とくぼみを彫り、球がそこを転がる。
# 基準（Wannerstedt）から取ったのは光・素材・構図・色の組み立てだけ。基準の円筒の渦は写さない。
LOOK = dict(
    aspect=(5, 3),
    lens=70,
    fstop=5.6,
    view="Standard",
    look="Medium Contrast",
    exposure=0.0,
    bg="#D6D0CF",
)
FPS = 24


def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


def hex_to_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def bevel_obj(ob, width, segments=3, clamp=True, angle=30):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    edges = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(angle)]
    bmesh.ops.bevel(bm, geom=edges, offset=width, segments=segments, profile=0.5,
                    affect='EDGES', clamp_overlap=clamp)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return ob


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, trans=0.0, ior=1.45, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["IOR"].default_value = ior
    p.inputs["Specular IOR Level"].default_value = spec
    return m


def grain(m, rough, scale=900.0, strength=0.06):
    """砂目：細かいノイズのバンプ＋粗さの揺らぎ（基準の樹脂は全面に肌理がある）"""
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 2.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = strength
    bp.inputs["Distance"].default_value = 0.002
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = rough - 0.06; mr.inputs["To Max"].default_value = rough + 0.06
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], p.inputs["Roughness"])


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.0), shape='RECTANGLE', size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.shape, ld.size = energy, color, shape, size
    if size_y:
        ld.size_y = size_y
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


# ------------------------------------------------------------- 造形：櫛
X0, X1 = -1.62, 1.62          # 櫛の左右
Y0, Y1 = -0.92, 0.92          # 手前・奥
ZB = -4.5                     # 底（画面の外）
N_PL = 30                     # 板の枚数
PITCH = (X1 - X0) / N_PL
THICK = PITCH * 0.72          # 板の厚み（残りがすき間）
NY = 120                      # 板1枚の天端の分割


def groove_c(x):              # 溝の中心線（うねり）
    return 0.24 * math.sin(1.75 * x + 0.55) - 0.04


def bump(d, w):               # 天が平らで縁の接線0の断面
    u = min(1.0, abs(d) / w)
    return (1 - u * u) ** 2


BOWL = (0.92, 0.22)           # 青緑の球が収まるくぼみ（x, y）


def top(x, y):
    """板の天端の高さ。段（左が高い）＋奥へわずかに上がる＋溝＋くぼみ"""
    z = 0.26 * math.tanh((-x - 0.15) * 2.6) + 0.06 * (y - Y0)
    z -= 0.52 * bump(y - groove_c(x), 0.60) * (0.55 + 0.45 * bump(x - 0.15, 2.2))
    dx, dy = x - BOWL[0], y - BOWL[1]
    z -= 0.55 * bump(math.hypot(dx, dy), 0.60)
    return z


verts, faces = [], []
for i in range(N_PL):
    xc = X0 + PITCH * (i + 0.5)
    xa, xb = xc - THICK / 2, xc + THICK / 2
    yh = max(0.26, Y1 * (1 - (xc / (X1 + 0.04)) ** 2) ** 0.62)   # 平面は横長の楕円＝端の板ほど短い
    ys = [-yh + 2 * yh * k / (NY - 1) for k in range(NY)]
    zs = [top(xc, y) for y in ys]
    base = len(verts)
    # 0..NY-1: 左面の天端／NY..2NY-1: 右面の天端／2NY..: 左面の底／3NY..: 右面の底
    for y, z in zip(ys, zs):
        verts.append((xa, y, z))
    for y, z in zip(ys, zs):
        verts.append((xb, y, z))
    for y in ys:
        verts.append((xa, y, ZB))
    for y in ys:
        verts.append((xb, y, ZB))
    T0, T1, B0, B1 = base, base + NY, base + 2 * NY, base + 3 * NY
    for k in range(NY - 1):
        faces.append((T0 + k, T0 + k + 1, T1 + k + 1, T1 + k))            # 天端
        faces.append((B0 + k, B0 + k + 1, T0 + k + 1, T0 + k)[::-1])      # 左面
        faces.append((B1 + k, T1 + k, T1 + k + 1, B1 + k + 1)[::-1])      # 右面
        faces.append((B0 + k, B1 + k, B1 + k + 1, B0 + k + 1)[::-1])      # 底
    faces.append((T0, T1, B1, B0)[::-1])                                  # 手前
    faces.append((T0 + NY - 1, B0 + NY - 1, B1 + NY - 1, T1 + NY - 1)[::-1])  # 奥
me = bpy.data.meshes.new("comb_me")
me.from_pydata(verts, [], faces); me.update()
comb = bpy.data.objects.new("comb", me); scene.collection.objects.link(comb)
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
bevel_obj(comb, THICK * 0.16, segments=3, angle=35)
C_SALMON = hex_to_linear("#E6B0A0")
m_salmon = principled("salmon", C_SALMON, rough=0.46, spec=0.45)
grain(m_salmon, 0.46, scale=260.0, strength=0.22)
comb.data.materials.append(m_salmon)


# ------------------------------------------------------------- 球
def rest_z(px, py, r):
    """板の天端に乗る球の中心の高さ（板の稜線ごとに当たりを取る）"""
    zc = -9
    for i in range(N_PL):
        xc = X0 + PITCH * (i + 0.5)
        dx = abs(xc - px) - THICK / 2
        dx = max(0.0, dx)
        if dx >= r:
            continue
        for k in range(41):
            y = py - r + 2 * r * k / 40
            d2 = dx * dx + (y - py) ** 2
            if d2 >= r * r:
                continue
            zc = max(zc, top(xc, y) + math.sqrt(r * r - d2))
    return zc


def ball(name, r, color, rough):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=96, ring_count=48)
    b = bpy.context.object; b.name = name
    for p in b.data.polygons:
        p.use_smooth = True
    mb = principled(name, hex_to_linear(color), rough=rough, spec=0.45)
    grain(mb, rough, scale=500.0, strength=0.10)
    b.data.materials.append(mb)
    return b


R_RED, R_TEAL = 0.29, 0.31
red = ball("red", R_RED, "#E8605A", 0.55)
teal = ball("teal", R_TEAL, "#0F5468", 0.55)
# 青緑の球の継ぎ目（半球を合わせた線）：細い溝のリング
bpy.ops.mesh.primitive_torus_add(major_radius=R_TEAL * 0.997, minor_radius=0.0035,
                                 major_segments=160, minor_segments=12)
seam = bpy.context.object; seam.name = "teal_seam"
seam.data.materials.append(principled("seam", hex_to_linear("#06222B"), rough=0.6))
seam.parent = teal
seam.rotation_euler = (math.radians(90), 0, math.radians(20))

RED_PATH = (-1.45, -0.86)      # 溝の中を転がる x の始点・終点
TEAL_POS = Vector((BOWL[0], BOWL[1], rest_z(BOWL[0], BOWL[1], R_TEAL)))
teal.location = TEAL_POS
_red_z = {}


def red_at(x):
    key = round(x, 3)
    if key not in _red_z:
        _red_z[key] = rest_z(x, groove_c(x), R_RED)
    return Vector((x, groove_c(x), _red_z[key]))


parts = [comb, red, teal, seam]

# ------------------------------------------------------------- 舞台：継ぎ目のない壁（床→R→壁）
R_, W_, D_, H_ = 3.0, 40.0, 14.0, 16.0
pts = [(-D_, 0.0), (0.0, 0.0)] + [(R_ * math.sin(t), R_ - R_ * math.cos(t)) for t in
                                  [i / 16 * math.pi / 2 for i in range(1, 17)]] + [(R_, H_)]
sv, sf = [], []
for x in (-W_ / 2, W_ / 2):
    for (y, z) in pts:
        sv.append((x, y + 2.2, z + ZB))
n = len(pts)
for i in range(n - 1):
    sf.append((i, i + 1, n + i + 1, n + i))
sme = bpy.data.meshes.new("sweep_me"); sme.from_pydata(sv, [], sf); sme.update()
sweep = bpy.data.objects.new("sweep", sme); scene.collection.objects.link(sweep)
for p in sme.polygons:
    p.use_smooth = True
sweep.data.materials.append(principled("wall", hex_to_linear(LOOK["bg"]), rough=0.8, spec=0.2))
sweep.visible_diffuse = False      # 明るい壁の照り返しで塊の陰が持ち上がるのを止める

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hex_to_linear("#EDBFB2")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.13

# ------------------------------------------------------------- 光：左上手前の大きく柔らかい1灯＋起こし
KEY_LOC = Vector((-5.8, -1.6, 4.8))
key_light = area("key", KEY_LOC, 2.6, 820, (1.0, 0.97, 0.94), target=(0.2, 0.2, -0.4))
# 壁だけを均一に起こす光（ライトリンクで壁だけに当てる）＝地は明るい灰みのピンクで平ら
wall_col = bpy.data.collections.new("wall_only"); wall_col.objects.link(sweep)
WALL_L = area("wall_light", (2.6, -6.0, 3.5), 16.0, 2500, (1.0, 1.0, 1.0), target=(0, 3.0, 0.5))
WALL_L.light_linking.receiver_collection = wall_col
WALL_L.data.use_shadow = False
fill_light = area("fill", (5.5, -3.5, 1.5), 4.0, 70, (1.0, 0.62, 0.55), target=(0, 0, -0.5))
# キーと起こしは被写体だけに当てる（壁に当てると左が白く飛び右が沈む＝地の明暗が基準の平らな地と違う）
subj_col = bpy.data.collections.new("subject")
for o in parts:
    subj_col.objects.link(o)
key_light.light_linking.receiver_collection = subj_col
fill_light.light_linking.receiver_collection = subj_col

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
cd.clip_start = 0.05
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


HERO_LOC = Vector((-3.85, -6.75, 5.85))
HERO_TGT = Vector((0.04, 0.22, -0.80))
TGT = Vector((0, 0, -0.1))
SHOTS = [
    dict(sec=3.0,   # 物の動き：珊瑚の球が溝を転がり込む。中くらいの距離で球を追って並走
         cam=lambda t: (lerp((-3.55, -3.85, 2.3), (-3.35, -3.95, 2.2), ease(t)),
                        lerp((-1.12, -0.22, 0.0), (-1.05, -0.22, -0.02), ease(t)), 50, 5.6, None)),
    dict(sec=2.75,  # マクロ：手前の板の稜線にピント→くぼみの青緑の球へピント送り
         cam=lambda t: (lerp((-0.12, -1.55, 0.28), (0.12, -1.5, 0.24), ease(t)),
                        Vector((0.92, 0.22, -0.45)), 110, 2.0, 1.1 + 0.9 * ease(t))),
    dict(sec=3.0,   # 回り込み：右奥の高い位置から櫛の段を弧で
         cam=lambda t: (orbit(TGT, 5.2, 3.4, 48 - 30 * ease(t)), TGT, 55, 6.0, None)),
    dict(sec=3.0,   # 決め：寄りながら入って hero の構図で止まる
         cam=lambda t: (lerp(HERO_LOC + Vector((0.5, 1.2, -0.3)), HERO_LOC, ease_out(min(1.0, t / 0.6))),
                        lerp(HERO_TGT + Vector((0.1, 0, 0.05)), HERO_TGT, ease_out(min(1.0, t / 0.6))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

ROLL_END = (shot_start[1] - 1) / (N_FRAMES - 1)   # 1カット目の中で転がり切る（後のカットに持ち越すと動きが小さく割れて見えない）


def pose(i, t, T):
    u = ease(min(1.0, T / ROLL_END))
    x = RED_PATH[0] + (RED_PATH[1] - RED_PATH[0]) * u
    p = red_at(x)
    red.location = p
    dist = (x - RED_PATH[0]) * 1.08        # 溝のうねりぶん少し長い
    # 進む向き（xとyの接線）に直交する軸まわりに転がる
    dydx = 0.24 * 1.75 * math.cos(1.75 * x + 0.55)
    yaw = math.atan2(dydx, 1.0)
    red.rotation_euler = (0, dist / R_RED, yaw)
    teal.location = TEAL_POS


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
        for o in (red, teal):
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
