# =============================================================
# MIDDLE STUDIES II 001 — FLASK（水筒）
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / phases
#
# 基準：BALMUDA The Pot 公式の製品写真（左奥の窓光1灯・粉体塗装のシボ・低い望遠・2個目を奥にボカす）
# 造形は基準を写さない。真空断熱ボトル2本（テラコッタ／サンド）を旋盤プロファイルから起こす。
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

LOOK = dict(
    aspect=(16, 9),
    lens=125,
    fstop=0.45,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=-0.2,
)
FPS, SECONDS = 24, 6
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


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------- 色
C_TERRA = hex_to_linear("#9A4E36")   # 主役：焼いた土の赤茶（粉体塗装）
C_SAND = hex_to_linear("#D8CDBB")    # 奥：砂
C_FLOOR = hex_to_linear("#7C7974")   # コンクリートの天板
C_WALL = hex_to_linear("#DCD6CD")    # 漆喰の壁
C_BRASS = hex_to_linear("#B08D57")   # 差し色（キャップの細い帯）


# ------------------------------------------------------------- 造形の道具
def arc(cx, cz, r, a0, a1, n=10):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cz + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def lathe(name, prof, segs=160):
    """prof: (r, z) を軸上(0,z0)から始めて軸上(0,z1)で終える。閉じた回転体を作る。"""
    bm = bmesh.new()
    rings = []
    for (r, z) in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / segs),
                                        r * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)])
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(segs):
                bm.faces.new((a[0], b[(k + 1) % segs], b[k]))
        elif len(b) == 1:
            for k in range(segs):
                bm.faces.new((a[k], a[(k + 1) % segs], b[0]))
        else:
            for k in range(segs):
                bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def strap(name, rad, thick, width, z0, segs=64, csegs=24):
    """キャップの上の持ち手：平たい帯を半円＋脚で曲げる（XZ面・幅はY）。下端はキャップに埋める。"""
    bm = bmesh.new()
    # 中心線：左脚 → 半円 → 右脚
    path = [(-rad, z0 - 0.04), (-rad, z0)] + \
           [(-rad * math.cos(math.pi * i / segs), z0 + rad * math.sin(math.pi * i / segs)) for i in range(1, segs)] + \
           [(rad, z0), (rad, z0 - 0.04)]
    # 断面：角の丸い長方形（法線方向に thick、Y方向に width）
    cs = []
    rr = min(thick, width) * 0.45
    hw, ht = width / 2 - rr, thick / 2 - rr
    for (cy, cn, a0) in ((hw, ht, 0), (-hw, ht, math.pi / 2), (-hw, -ht, math.pi), (hw, -ht, 1.5 * math.pi)):
        for i in range(csegs // 4 + 1):
            a = a0 + (math.pi / 2) * i / (csegs // 4)
            cs.append((cy + rr * math.cos(a), cn + rr * math.sin(a)))
    rings = []
    for i, (x, z) in enumerate(path):
        # 接線から法線（XZ面）を出す
        xa, za = path[max(0, i - 1)]
        xb, zb = path[min(len(path) - 1, i + 1)]
        tx, tz = xb - xa, zb - za
        l = math.hypot(tx, tz) or 1
        nx, nz = -tz / l, tx / l
        rings.append([bm.verts.new((x + nx * n, y, z + nz * n)) for (y, n) in cs])
    m = len(cs)
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(m):
            bm.faces.new((a[k], a[(k + 1) % m], b[(k + 1) % m], b[k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


def powder(name, color, rough=0.46, grain=0.018):
    """粉体塗装：rough 0.46 の誘電体＋細かいシボ（ノイズの Bump）。暗色ではないので Bump が効く（#52 は黒の話）"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = 0.5
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 900.0
    nz.inputs["Detail"].default_value = 4.0
    nz.inputs["Roughness"].default_value = 0.6
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    bp.inputs["Distance"].default_value = grain
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def principled(name, color, rough=0.35, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.8), size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color = energy, color
    if size_y:
        ld.shape = 'RECTANGLE'; ld.size, ld.size_y = size, size_y
    else:
        ld.shape = 'SQUARE'; ld.size = size
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


# ------------------------------------------------------------- ボトル（単位＝dm。高さ2.2＝22cm）
def bottle(tag, R, H, base_col, loc):
    rn = 0.05                       # 底の角R
    neck = R * 0.80                 # 肩で絞った口の半径
    zs = H * 0.80                   # 肩の始まり
    body_prof = [(0.0, 0.0)] + arc(R - rn, rn, rn, -math.pi / 2, 0, 8) + [(R, zs)]
    # 肩：なだらかなS（cos で半径を落とす）
    zn = zs + 0.16
    body_prof += [(neck + (R - neck) * (0.5 + 0.5 * math.cos(math.pi * i / 12)), zs + (zn - zs) * i / 12)
                  for i in range(1, 13)]
    body_prof += [(neck, zn + 0.03), (neck - 0.01, zn + 0.035), (0.0, zn + 0.035)]
    body = lathe(tag + "_body", body_prof)
    body.data.materials.append(powder(tag + "_paint", base_col))

    # キャップ：口よりわずかに太い円筒＋上の角R。首との間に細い溝（影で継ぎ目が読める）
    cr, ch, ctop_r = neck + 0.012, 0.30, 0.045
    z0 = zn + 0.038
    cap_prof = [(0.0, z0), (cr - 0.01, z0), (cr, z0 + 0.01), (cr, z0 + ch - ctop_r)] + \
               arc(cr - ctop_r, z0 + ch - ctop_r, ctop_r, 0, math.pi / 2, 8)[1:] + [(0.0, z0 + ch)]
    cap = lathe(tag + "_cap", cap_prof)
    cap.data.materials.append(powder(tag + "_cappaint", base_col, rough=0.40))
    # 差し色：キャップ下端の真鍮の細帯
    band_prof = [(0.0, z0 + 0.012), (cr + 0.002, z0 + 0.012), (cr + 0.004, z0 + 0.018),
                 (cr + 0.004, z0 + 0.030), (cr + 0.002, z0 + 0.036), (0.0, z0 + 0.036)]
    band = lathe(tag + "_band", band_prof)
    band.data.materials.append(principled(tag + "_brass", C_BRASS, rough=0.28, metal=1.0))
    # 持ち手
    st = strap(tag + "_strap", 0.13, 0.034, 0.11, z0 + ch - 0.005)
    st.data.materials.append(powder(tag + "_strappaint", base_col, rough=0.42))

    # 回転の親（原点に置く＝#9）
    root = bpy.data.objects.new(tag, None); scene.collection.objects.link(root)
    root.location = loc
    for o in (body, cap, band, st):
        o.parent = root
    return root, [body, cap, band, st]


front, front_parts = bottle("terra", 0.36, 2.0, C_TERRA, (-0.62, 0.0, 0.0))
back, back_parts = bottle("sand", 0.34, 1.85, C_SAND, (1.05, 2.1, 0.0))

# ------------------------------------------------------------- 舞台：コンクリの天板＋奥の壁（角は立てる）
def plane(name, verts, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0, 1, 2, 3)]); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def concrete():
    m = bpy.data.materials.new("concrete"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.9
    n1.inputs["Detail"].default_value = 8.0; n1.inputs["Roughness"].default_value = 0.62
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 45.0
    n2.inputs["Detail"].default_value = 8.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = tuple(c * 0.70 for c in C_FLOOR[:3]) + (1,)
    ramp.color_ramp.elements[1].position = 0.70; ramp.color_ramp.elements[1].color = tuple(min(1, c * 1.22) for c in C_FLOOR[:3]) + (1,)
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35
    bp.inputs["Distance"].default_value = 0.01
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.62; rr.inputs["To Max"].default_value = 0.80
    nt.links.new(tc.outputs["Object"], n1.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], n2.inputs["Vector"])
    nt.links.new(n1.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(n2.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(n1.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    return m


WALL_Y = 7.0
floor = plane("floor", [(-12, -14, 0), (12, -14, 0), (12, WALL_Y, 0), (-12, WALL_Y, 0)], concrete())
wall = plane("wall", [(-12, WALL_Y, 0), (12, WALL_Y, 0), (12, WALL_Y, 9), (-12, WALL_Y, 9)],
             principled("plaster", C_WALL, rough=0.85))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = hex_to_linear("#CFC9C0")
bg.inputs["Strength"].default_value = 0.08

# ------------------------------------------------------------- 光：左奥の大きな窓1灯＋右手前の弱い起こし
area("window", (-7.0, 2.6, 3.4), 3.6, 15000, (1.0, 0.97, 0.93), target=(0.0, 0.6, 0.9), size_y=3.2)
area("fill", (6.0, -7.0, 2.4), 6.0, 140, (0.96, 0.97, 1.0), target=(0.0, 0.5, 0.9))
# 右の消し板（黒い板）：壁と天板の照り返しが右半身に回るのを切る＝胴に左→右の階調を作る
plane("flag", [(3.2, -4.0, 0.0), (3.2, 2.5, 0.0), (3.2, 2.5, 4.5), (3.2, -4.0, 4.5)],
      principled("flag_black", (0.01, 0.01, 0.01, 1), rough=0.9)).visible_camera = False
bpy.data.objects["flag"].visible_shadow = False
# 右奥の細い縦の反射板（主役の右稜線に帯を立てる）
area("strip", (3.0, 1.4, 2.6), 0.4, 300, (1.0, 0.98, 0.95), target=(-0.62, 0.0, 1.0), size_y=3.0)

# ------------------------------------------------------------- カメラ（低い望遠・天板すれすれ）
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.lens = LOOK["lens"]
cd.dof.use_dof = True
cd.dof.focus_object = front
cd.dof.aperture_fstop = LOOK["fstop"]
scene.camera = cam
CAM0 = Vector((0.9, -21.0, 3.1))
AIM = Vector((1.45, 0.6, 1.10))

# ------------------------------------------------------------- 動き（位相 t で書き毎フレームキー）
# カメラがゆっくり左右に振れ（視差で奥のボトルと壁がずれる）、2本は互い違いに±22°首を振る
def pose(t):
    s = math.sin(2 * math.pi * t)
    cam.location = CAM0 + Vector((0.9 * s, 0.0, 0.10 * math.sin(4 * math.pi * t)))
    cam.rotation_euler = (AIM + Vector((0.25 * s, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    front.rotation_euler = (0, 0, math.radians(-30 + 22 * math.cos(2 * math.pi * t)))
    back.rotation_euler = (0, 0, math.radians(35 + 22 * math.cos(2 * math.pi * t + math.pi * 0.6)))


animated = [cam, front, back]
for f in range(1, N_FRAMES + 2):
    pose((f - 1) / N_FRAMES)
    for o in animated:
        o.keyframe_insert("rotation_euler", frame=f)
    cam.keyframe_insert("location", frame=f)

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
scene.view_settings.look = LOOK["look"]
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

if "phases" in modes:
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

if "glb" in modes:
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in [front, back] + front_parts + back_parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = front
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
