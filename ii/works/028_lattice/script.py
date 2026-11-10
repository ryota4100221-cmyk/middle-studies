# =============================================================
# MIDDLE STUDIES II 028 — LATTICE（編み線の房）
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
#
# 基準：Ruth Asawa「Untitled (S.089)」c.1958 の写真（右手前の1灯・白い壁に大きくぼけた影）
# 取ったもの：光の組み方（右手前の1灯＋壁の照り返し）／細い金属線のループ編みの質／
#             横長で本体と影を対にする構図／白い壁に真鍮と焦げ茶だけの色の組み立て
# 造形は自分で起こす：中空の楕円体を S 字の背骨に沿って連ね、大きな房の中に小さな房を入れ子にする
# =============================================================
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix, Euler

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(16, 9),
    lens=85,
    fstop=11.0,
    view="Standard",
    look="None",
    exposure=-0.17,
    bg=(0.80, 0.80, 0.79),
)
FPS = 24


def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side


def srgb_to_linear(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def hex_to_linear(h):
    h = h.lstrip("#")
    return srgb_to_linear([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]) + (1.0,)


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


# ------------------------------------------------------------- 舞台：白い壁（被写体の後ろ WALL_Y）
WALL_Y = 0.85
me = bpy.data.meshes.new("wall_me")
me.from_pydata([(-30, WALL_Y, -6), (30, WALL_Y, -6), (30, WALL_Y, 24), (-30, WALL_Y, 24)], [], [(0, 1, 2, 3)])
wall = bpy.data.objects.new("wall", me); scene.collection.objects.link(wall)
wall.data.materials.append(principled("wall", LOOK["bg"] + (1.0,), rough=0.9))
# 漆喰の壁＝鏡面なし（rough 0.9 でも鏡面がキーの照り返しを丸い明るみとして壁に出した）
wall.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.0

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
WORLD_S = 0.42
world.node_tree.nodes["Background"].inputs["Strength"].default_value = WORLD_S

# ------------------------------------------------------------- 被写体：ループ編みの房
root = bpy.data.objects.new("root", None); scene.collection.objects.link(root)
ROOT_LOC = Vector((0.06, 0.0, 0.0))
root.location = ROOT_LOC

R_WIRE = 0.0009
AMP, KK, CURL = 0.6, 0.55, 0.5   # 輪の高さ（行の何倍の半分）・輪の幅（ピッチの何倍）


def metal_mat(name, col_hex, rough, dark_hex):
    """線の金属。物体座標の低周波ノイズで、焼けた所（dark）とまだ明るい所を混ぜる"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; P = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[1].default_value = 0.35; mr.inputs[2].default_value = 0.65
    nt.links.new(nz.outputs["Fac"], mr.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    mx.inputs[6].default_value = hex_to_linear(col_hex)
    mx.inputs[7].default_value = hex_to_linear(dark_hex)
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(mx.outputs[2], P.inputs["Base Color"])
    P.inputs["Metallic"].default_value = 0.6
    P.inputs["Roughness"].default_value = rough
    return m


MATS = dict(
    brass=metal_mat("brass", "#8E7632", 0.38, "#504222"),
    bronze=metal_mat("bronze", "#54402A", 0.45, "#2E2216"),
    iron=metal_mat("iron", "#4C4A44", 0.5, "#2A2824"),
)

# 房の並び：(中心 x, y, z) / 半径 (a, c) / 傾き(deg x, y) / 材 / 入れ子の房（半径比）
LOBES = [   # S 字：右上の小房から、左の大きな入れ子の房へ振れ、右下へ戻って細る
    ((0.28, 0.02, 2.16), (0.090, 0.082), (-20, 25), "iron", None),
    ((0.06, 0.00, 2.07), (0.150, 0.130), (12, -18), "brass", None),
    ((0.29, -0.03, 1.95), (0.068, 0.060), (30, 10), "brass", None),
    ((-0.13, 0.03, 1.86), (0.120, 0.110), (25, 40), "bronze", None),
    ((-0.20, 0.00, 1.64), (0.185, 0.165), (-8, 10), "brass", 0.55),
    ((0.02, 0.04, 1.47), (0.100, 0.092), (-15, -20), "iron", None),
    ((-0.33, -0.02, 1.46), (0.072, 0.066), (35, 20), "iron", None),
    ((0.12, 0.00, 1.30), (0.140, 0.122), (10, 28), "bronze", 0.6),
    ((0.27, 0.02, 1.12), (0.110, 0.100), (-28, 15), "brass", None),
    ((0.06, -0.02, 1.02), (0.095, 0.085), (6, -12), "brass", None),
    ((0.29, 0.00, 0.93), (0.070, 0.066), (-10, 30), "bronze", None),
]


def lobe_points(center, a, c, tilt, seed, W=0.0105, ROWH=0.024, PPL=20):
    """中空の楕円体を下の口から上の口へ1本の螺旋で編む。
    行に沿ってトロコイド（輪）を作り、上下にも振って前の行の輪に掛ける＝ループ編み"""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(8)]
    psi0, psi1 = math.radians(22), math.radians(158)          # 両極は口として開ける
    mer = (psi1 - psi0) * (a + c) / 2                          # 子午線の長さ（概算）
    turns = mer / ROWH
    rot = Euler((math.radians(tilt[0]), math.radians(tilt[1]), rnd.uniform(0, 6.28))).to_matrix()
    pts = []
    t, phi = 0.0, 0.0
    dpsi_row = (psi1 - psi0) / turns
    while t < turns:
        psi = psi0 + (psi1 - psi0) * t / turns
        th = 2 * math.pi * t
        # 手作りの歪み（房ごとに違うふくらみ）
        lump = 1 + 0.06 * math.sin(2 * th + ph[0]) * math.sin(psi) + 0.05 * math.sin(3 * psi + ph[1]) \
            + 0.03 * math.sin(th + 2 * psi + ph[2])
        rho = a * math.sin(psi) * lump
        Wl = W * (1 + 0.12 * math.sin(3 * th + ph[3]) + 0.08 * math.sin(7 * t + ph[4]))
        circ = max(2 * math.pi * rho, 0.02)
        dt = Wl / (PPL * circ)
        # 輪：行に沿って戻る（トロコイド）＋上下に振る（前の行に掛かる）＋内外に縫う
        # 手編みのむら：輪ごとに幅・高さ・傾きが揃わない（揃うと籠目の機械編みになる）
        n1 = 0.55 * math.sin(phi * 0.37 + ph[0]) + 0.3 * math.sin(phi * 0.91 + ph[3]) + 0.15 * math.sin(phi * 1.73 + ph[6])
        n2 = 0.55 * math.sin(phi * 0.29 + ph[1]) + 0.3 * math.sin(phi * 0.83 + ph[4]) + 0.15 * math.sin(phi * 1.61 + ph[7])
        kk = KK * Wl * (1 + 0.35 * n1)
        u_off = -kk * math.sin(phi) - 0.35 * kk * math.sin(2 * phi + 1.3 * n2) + 0.5 * Wl * n2 * math.cos(phi)
        # 輪の上下は cos を平たく（|cos|^0.5）＝輪の頭と次の行の輪の尻が同じ高さに溜まって「鎖の帯」、
        # その間は縦の脚だけの「透けた帯」になる（基準の横縞）
        cp = math.cos(phi); cp = math.copysign(abs(cp) ** 0.55, cp)
        psi_l = psi - AMP * dpsi_row * cp * (1 + 0.15 * n2) + 0.08 * dpsi_row * n1
        # 鎖の帯：輪の頭と尻（|cos| が大きい所）で小さく2〜3回巻く＝基準の撚れた横縞
        wb = max(0.0, abs(math.cos(phi)) - 0.35) / 0.65
        u_off += CURL * Wl * wb * math.sin(5 * phi + n1)
        psi_l += 0.10 * dpsi_row * wb * math.cos(5 * phi + n1)
        th_l = th + u_off / max(rho, 0.01)
        r_l = a * math.sin(psi_l) * lump + R_WIRE * 1.6 * math.sin(phi * 0.5 + ph[6])
        z_l = -c * math.cos(psi_l) * lump
        p = Vector((r_l * math.cos(th_l), r_l * math.sin(th_l), z_l))
        pts.append(rot @ p + Vector(center))
        phi += 2 * math.pi / PPL
        t += dt
    return pts


def spread(cen, k=1.2, x0=0.03):
    return (x0 + (cen[0] - x0) * k, cen[1], cen[2])


LOBE_PTS = []          # [(材, 点列)]
RS = 1.32
seed = 280
for (cen, (a, c), tilt, mat, nest) in LOBES:
    seed += 1
    cen = spread(cen)
    a, c = a * RS, c * RS
    LOBE_PTS.append((mat, lobe_points(cen, a, c, tilt, seed)))
    if nest:
        seed += 1
        inner = "brass" if mat != "brass" else "bronze"
        LOBE_PTS.append((inner, lobe_points(cen, a * nest, c * nest, (tilt[0] + 20, tilt[1] - 15), seed,
                                            W=0.009, ROWH=0.019)))

parts = []
for mat in MATS:
    curves = [p for (m, p) in LOBE_PTS if m == mat]
    if not curves:
        continue
    hc = bpy.data.hair_curves.new("wire_" + mat)
    hc.add_curves([len(p) for p in curves])
    flat = []
    for p in curves:
        for q in p:
            flat += [q.x, q.y, q.z]
    hc.position_data.foreach_set("vector", flat)
    n = len(flat) // 3
    rad = hc.attributes.new("radius", 'FLOAT', 'POINT')
    rad.data.foreach_set("value", [R_WIRE] * n)
    hc.materials.append(MATS[mat])
    ob = bpy.data.objects.new("wire_" + mat, hc); scene.collection.objects.link(ob)
    ob.parent = root
    parts.append(ob)
    print(">> %s: %d curves %d pts" % (mat, len(curves), n))

# 吊り線：一番上の房の天端から天井へ
top = Vector(LOBES[0][0]) + Vector((0, 0, LOBES[0][1][1] * 0.9))
bpy.ops.mesh.primitive_cylinder_add(radius=0.0009, depth=3.0, location=(top.x, top.y, top.z + 1.5), vertices=8)
hang = bpy.context.object; hang.name = "hang"
hang.data.materials.append(principled("hangwire", hex_to_linear("#8A8578"), rough=0.3, metal=1.0))
hang.parent = root
parts.append(hang)

# ------------------------------------------------------------- 光：右手前の1灯（壁に左へ影）
WASH_E = 40
KEY2_E = 1850
KEY_LOC = Vector((6.4, -4.4, 2.0))
kd = bpy.data.lights.new("key", 'SPOT')
kd.energy = 1450; kd.shadow_soft_size = 0.17; kd.spot_size = math.radians(110); kd.spot_blend = 0.55
kd.color = (1.0, 0.99, 0.975)
key_light = bpy.data.objects.new("key", kd); scene.collection.objects.link(key_light)
key_light.location = KEY_LOC
key_light.rotation_euler = (Vector((-0.9, 0.4, 1.55)) - KEY_LOC).to_track_quat('-Z', 'Y').to_euler()

# キーと同じ位置・同じ半径の2灯目を左の壁へ向ける＝影は1つのまま、遠い左の壁の落ちだけを埋める
k2d = bpy.data.lights.new("key2", 'SPOT')
k2d.energy = KEY2_E; k2d.shadow_soft_size = kd.shadow_soft_size; k2d.spot_size = math.radians(34); k2d.spot_blend = 1.0
k2d.color = kd.color
key2 = bpy.data.objects.new("key2", k2d); scene.collection.objects.link(key2)
key2.location = KEY_LOC
key2.rotation_euler = (Vector((-1.9, WALL_Y, 1.5)) - KEY_LOC).to_track_quat('-Z', 'Y').to_euler()

# 壁だけを左手前から洗う（キーが右から斜めに当たるぶんの左右の落ちを埋める）。影は落とさない
wcol = bpy.data.collections.new("wall_only"); wcol.objects.link(wall)
wd = bpy.data.lights.new("wash", 'AREA'); wd.energy = WASH_E; wd.size = 5.0; wd.use_shadow = False
wash = bpy.data.objects.new("wash", wd); scene.collection.objects.link(wash)
wash.location = (-5.0, -3.2, 1.7)
wash.rotation_euler = (Vector((-1.0, WALL_Y, 1.55)) - Vector(wash.location)).to_track_quat('-Z', 'Y').to_euler()
wash.light_linking.receiver_collection = wcol
wash.visible_camera = False

# 正面からの大きな弱い起こし（線の陰側を黒に落とさない）
fd = bpy.data.lights.new("fill", 'AREA'); fd.energy = 60; fd.size = 4.0; fd.color = (1, 1, 1)
fill = bpy.data.objects.new("fill", fd); scene.collection.objects.link(fill)
fill.location = (-0.5, -5.5, 1.8)
fill.rotation_euler = (Vector((0, 0, 1.55)) - Vector(fill.location)).to_track_quat('-Z', 'Y').to_euler()

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


HERO_CAM = Vector((0.04, -6.3, 1.55))
HERO_TGT = Vector((0.04, 0.0, 1.55))
HERO_ROT = math.radians(25)
ROT_SPAN = math.radians(70)
SECS = [3.0, 2.8, 3.0, 3.0]
_starts, _n = [], 0
for _s in SECS:
    _starts.append(_n); _n += round(_s * FPS)


def ang_at(i, t):
    """吊られた房はゆっくり回り続け、決めのカットで減速して hero の向き（HERO_ROT）で止まる"""
    if i < 3:
        T0 = (_starts[i] + t * (round(SECS[i] * FPS) - 1)) / _starts[3]
        return HERO_ROT - ROT_SPAN + ROT_SPAN * 0.85 * T0
    return HERO_ROT - ROT_SPAN * 0.15 * (1 - ease_out(min(1.0, t / 0.62)))


def world_of(p, ang):
    """房の中の点（root ローカル）の、その瞬間のワールド位置"""
    return ROOT_LOC + Matrix.Rotation(ang, 3, 'Z') @ Vector(p)


BIG = Vector(spread(LOBES[4][0]))      # 大きい入れ子の房（真鍮・中に青銅）


def macro(t):
    c = world_of(BIG, ang_at(0, t))
    tgt = c + Vector((0.02, 0, 0.02))
    loc = c + lerp((0.62, -0.78, 0.30), (0.30, -0.95, 0.12), ease(t))
    d = (tgt - loc).length
    rO = LOBES[4][1][0] * RS; rI = rO * LOBES[4][4]
    return loc, tgt, 135, 4.0, d - rO * 0.95 + (rO - rI) * 0.95 * ease(min(1.0, t / 0.8))   # 外の網の手前 → 中の房の手前へピント送り


SHOTS = [
    dict(sec=SECS[0], cam=macro),   # マクロ：入れ子の房をなめ、外の網から中の房へピント送り
    dict(sec=SECS[1],   # スライド：壁の影の前を左から右へ、影から本体へ
         cam=lambda t: (lerp((-1.55, -3.1, 1.45), (-0.45, -3.1, 1.55), ease(t)),
                        lerp((-1.35, WALL_Y, 1.40), (-0.15, 0.0, 1.55), ease(t)), 60, 5.6, None)),
    dict(sec=SECS[2],   # 物の動き：下から見上げる。房が回り、影が壁を流れる
         cam=lambda t: (lerp((0.22, -1.35, 0.15), (0.02, -1.45, 0.22), ease(t)), Vector((0.02, 0.1, 1.50)),
                        24, 8.0, None)),
    dict(sec=SECS[3],   # 決め：寄りから引いて hero で止まる
         cam=lambda t: (lerp((-0.05, -4.7, 1.62), HERO_CAM, ease_out(min(1.0, t / 0.62))),
                        lerp((-0.02, 0.0, 1.60), HERO_TGT, ease_out(min(1.0, t / 0.62))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    root.rotation_euler = (0, 0, ang_at(i, t))


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
        root.keyframe_insert("rotation_euler", frame=f)

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

# glb：Curves は glTF に載らない。粗い編み（輪を倍の幅・行を倍の高さ）を三角柱のメッシュで組む
if "glb" in modes:
    scene.frame_end = N_FRAMES + 1
    glb_objs = []
    seed = 280
    lob = []
    for (cen, (a, c), tilt, mat, nest) in LOBES:
        seed += 1
        cen = spread(cen)
        a, c = a * RS, c * RS
        lob.append((mat, lobe_points(cen, a, c, tilt, seed, W=0.045, ROWH=0.034, PPL=6)))
        if nest:
            seed += 1
            lob.append(("brass" if mat != "brass" else "bronze",
                        lobe_points(cen, a * nest, c * nest, (tilt[0] + 20, tilt[1] - 15), seed, W=0.04, ROWH=0.03, PPL=6)))
    RG = 0.0018
    for mat in MATS:
        verts, faces = [], []
        for (m, pts) in lob:
            if m != mat:
                continue
            base = len(verts)
            for j, q in enumerate(pts):
                d = (pts[min(j + 1, len(pts) - 1)] - pts[max(j - 1, 0)]).normalized()
                u = d.orthogonal().normalized(); v = d.cross(u)
                for k in range(3):
                    ang = 2 * math.pi * k / 3
                    verts.append(tuple(q + RG * (math.cos(ang) * u + math.sin(ang) * v)))
            for j in range(len(pts) - 1):
                for k in range(3):
                    a0 = base + j * 3 + k; a1 = base + j * 3 + (k + 1) % 3
                    faces.append((a0, a1, a1 + 3, a0 + 3))
        if not verts:
            continue
        me = bpy.data.meshes.new("glb_" + mat); me.from_pydata(verts, [], faces); me.update()
        go = bpy.data.objects.new("glb_" + mat, me); scene.collection.objects.link(go)
        go.data.materials.append(MATS[mat]); go.parent = root
        glb_objs.append(go)
    for o in bpy.data.objects:
        o.select_set(o in glb_objs or o == root)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
