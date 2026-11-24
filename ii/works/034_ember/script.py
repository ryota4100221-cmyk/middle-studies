# =============================================================
# MIDDLE STUDIES II 034 EMBER（燠・FORM）
#   基準：Fred Eversley「untitled (parabolic lens)」（Freeman's lot 24）
#   縦長のカプセル形に注いだ染めた樹脂の板。縁は厚く黒、中心ほど薄く、白い壁の光が琥珀ににじんで透ける。
#   色は厚みだけで出す（Volume Absorption・Beer–Lambert）。影の光線は表面を素通しにして、体積の吸収で色の影を落とす。
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(3, 4),
    lens=55,
    fstop=8.0,
    view="Standard",          # 白地の製品写真は Standard＋露出マイナス（PITFALLS #122）
    look="None",
    exposure=-1.22,
    bg=(0.80, 0.80, 0.80),
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
    L.visible_transmission = False   # 板の向こうで屈折して橙の点に写った
    return L


# ------------------------------------------------------------- 舞台：白の無限背景紙
WALL_Y = 0.45                      # 奥の壁（立ち上がりの始まり）
R, W, D, H = 0.5, 16.0, 2.6, 6.0
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 16 * math.pi / 2 for i in range(1, 17)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + WALL_Y - R, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
sweep.data.materials.append(principled("paper", LOOK["bg"] + (1.0,), rough=0.7))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.02, 0.02, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

# ------------------------------------------------------------- 台
PL_W, PL_D, PL_H = 0.62, 0.30, 0.40
GAP = 0.016          # 台の足元の目地（奥へ 1.4cm 引っ込めた台座）＝下辺に暗い線が出て床から切れる
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, GAP + (PL_H - GAP) / 2))
plinth = bpy.context.object; plinth.name = "plinth"
plinth.scale = (PL_W, PL_D, PL_H - GAP); bpy.ops.object.transform_apply(scale=True)
bevel_obj(plinth, 0.0025, segments=3)
plinth.data.materials.append(principled("plinth", (0.78, 0.79, 0.81, 1), rough=0.6))   # 基準の台は地より一段灰で青み
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, GAP / 2))
foot = bpy.context.object; foot.name = "foot"
foot.scale = (PL_W - 0.028, PL_D - 0.028, GAP); bpy.ops.object.transform_apply(scale=True)
foot.data.materials.append(principled("foot", (0.08, 0.08, 0.085, 1), rough=0.7))

# ------------------------------------------------------------- 被写体：染めた樹脂のカプセル
A = 0.27            # 半幅
S = 0.23            # 直線部の半長（全高 = 2S + 2A = 1.0）
H0, H1, PW = 0.0002, 0.046, 3.2   # 片面の厚み：中心 H0 → 縁 H1・r^PW
CARD_E = 2.5
FLOOR_E = 1000
VSTEP = float(os.environ.get('II_VSTEP', '8'))
ZC = PL_H + S + A - 0.03          # 中心の高さ（下端を台に3cm差し込む）
NU, NR, NE = 256, 56, 14


def outline(u, rho):
    """周の割合 u（0..1）→ 半径 rho のカプセル上の点 (x, z) と外向き法線。直線/半円の割合は rho=A で固定（放射の列をそろえる）"""
    L = 4 * S + 2 * math.pi * A
    s = (u % 1.0) * L
    if s < 2 * S:                      # 右の直線（下→上）
        c = (0.0, -S + s); nrm = (1.0, 0.0)
    elif s < 2 * S + math.pi * A:      # 上の半円
        th = (s - 2 * S) / A; c = (0.0, S); nrm = (math.cos(th), math.sin(th))
    elif s < 4 * S + math.pi * A:      # 左の直線（上→下）
        c = (0.0, S - (s - 2 * S - math.pi * A)); nrm = (-1.0, 0.0)
    else:                              # 下の半円
        th = math.pi + (s - 4 * S - math.pi * A) / A; c = (0.0, -S); nrm = (math.cos(th), math.sin(th))
    return (c[0] + rho * nrm[0], c[1] + rho * nrm[1]), nrm


def relli(x, z):
    return math.sqrt((x / A) ** 2 + (z / (S + A)) ** 2)


def half(r):
    return H0 + (H1 - H0) * r ** PW


bm = bmesh.new()
rings_front, rings_back, rim = [], [], []
# 中心から外形へ放射に刻む（等厚線＝外形の相似形・中心に継ぎ目を作らない）
cF = bm.verts.new((0, -H0, 0)); cB = bm.verts.new((0, H0, 0))
for k in range(1, NR + 1):
    r = (k / NR) ** 0.85
    fr, bk = [], []
    for j in range(NU):
        (xo, zo), _ = outline(j / NU, A)
        x, z = r * xo, r * zo
        q = 0.5 * r + 0.5 * min(1.0, relli(x, z))     # 等厚線を外形の相似と楕円の半々に（芯が角丸の四角にならない）
        fr.append(bm.verts.new((x, -half(q), z)))
        bk.append(bm.verts.new((x, half(q), z)))
    rings_front.append(fr); rings_back.append(bk)
# 縁：半円の小口（y を -H1→+H1 へ回す）
for e in range(1, NE):
    ph = -math.pi / 2 + math.pi * e / NE
    ring = []
    for j in range(NU):
        (x, z), nrm = outline(j / NU, A)
        ring.append(bm.verts.new((x + 0.25 * H1 * math.cos(ph) * nrm[0], H1 * math.sin(ph), z + 0.25 * H1 * math.cos(ph) * nrm[1])))
    rim.append(ring)


def bridge(a, b, flip=False):
    for j in range(NU):
        q = (a[j], a[(j + 1) % NU], b[(j + 1) % NU], b[j])
        bm.faces.new(q[::-1] if flip else q)


for k in range(NR - 1):
    bridge(rings_front[k], rings_front[k + 1], flip=False)
    bridge(rings_back[k], rings_back[k + 1], flip=True)
chain = [rings_front[-1]] + rim + [rings_back[-1]]
for k in range(len(chain) - 1):
    bridge(chain[k], chain[k + 1], flip=False)
for j in range(NU):
    bm.faces.new((cF, rings_front[0][(j + 1) % NU], rings_front[0][j]))
    bm.faces.new((cB, rings_back[0][j], rings_back[0][(j + 1) % NU]))
bm.normal_update()
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
me = bpy.data.meshes.new("lens_me"); bm.to_mesh(me); bm.free()
lens = bpy.data.objects.new("lens", me); scene.collection.objects.link(lens)
for p in me.polygons:
    p.use_smooth = True
lens.location = (0, 0, ZC)

# 材質：表面＝磨いた樹脂（影の光線は素通し）／体積＝琥珀の吸収
ABS = (70.0, 390.0, 1400.0)
NEU, NEU_Q = 220.0, (0.32, 0.85)           # 1m あたりの吸収（R,G,B）
DEN = 800.0
m = bpy.data.materials.new("resin"); m.use_nodes = True
nt = m.node_tree; N = nt.nodes; Lk = nt.links
N.remove(N["Principled BSDF"])
out = N["Material Output"]
glass = N.new("ShaderNodeBsdfPrincipled")
glass.inputs["Base Color"].default_value = (1, 1, 1, 1)
glass.inputs["Roughness"].default_value = 0.015
glass.inputs["Transmission Weight"].default_value = 1.0
glass.inputs["IOR"].default_value = 1.56
tr = N.new("ShaderNodeBsdfTransparent")
tr.inputs["Color"].default_value = (0.74, 0.55, 0.24, 1)   # 影の光線が表と裏で2回通る＝(1, .55, .2) の琥珀
lp = N.new("ShaderNodeLightPath")
mix = N.new("ShaderNodeMixShader")
Lk.new(lp.outputs["Is Shadow Ray"], mix.inputs[0])
Lk.new(glass.outputs[0], mix.inputs[1])
Lk.new(tr.outputs[0], mix.inputs[2])
Lk.new(mix.outputs[0], out.inputs["Surface"])
va = N.new("ShaderNodeVolumeAbsorption")
va.inputs["Color"].default_value = tuple(1 - a / DEN for a in ABS) + (1,)
va.inputs["Density"].default_value = DEN
# 影の光線だけ吸収を弱める＝壁に落ちる影が灰でなく琥珀に染まる（基準の左の影）
lpv = N.new("ShaderNodeLightPath")
dm = N.new("ShaderNodeMath"); dm.operation = 'MULTIPLY_ADD'
Lk.new(lpv.outputs["Is Shadow Ray"], dm.inputs[0]); dm.inputs[1].default_value = -DEN * 0.95; dm.inputs[2].default_value = DEN
Lk.new(dm.outputs[0], va.inputs["Density"])
# 灰の吸収：楕円の距離 0.45→0.8 で効き始める＝尾がえんじに残らず黒へ落ちる（色の吸収だけだと赤が最後まで残る）
tc = N.new("ShaderNodeTexCoord"); sx = N.new("ShaderNodeSeparateXYZ")
Lk.new(tc.outputs["Object"], sx.inputs[0])
def mth(op, a, b=None, c=None):
    n = N.new("ShaderNodeMath"); n.operation = op
    for k, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[k].default_value = v
        else: Lk.new(v, n.inputs[k])
    return n.outputs[0]
ex = mth('POWER', mth('DIVIDE', sx.outputs["X"], A), 2.0)
ez = mth('POWER', mth('DIVIDE', sx.outputs["Z"], S + A), 2.0)
er = mth('SQRT', mth('ADD', ex, ez))
mr = N.new("ShaderNodeMapRange"); mr.interpolation_type = 'SMOOTHSTEP'
mr.inputs["From Min"].default_value = NEU_Q[0]; mr.inputs["From Max"].default_value = NEU_Q[1]
Lk.new(er, mr.inputs["Value"])
shadow_k = mth('MULTIPLY_ADD', lpv.outputs["Is Shadow Ray"], -1.0)
N_ = shadow_k.node; N_.inputs[2].default_value = 1.0
nd = mth('MULTIPLY', mth('MULTIPLY', mr.outputs["Result"], NEU), shadow_k)
vg = N.new("ShaderNodeVolumeAbsorption"); vg.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1)
Lk.new(nd, vg.inputs["Density"])
addv = N.new("ShaderNodeAddShader")
Lk.new(va.outputs[0], addv.inputs[0]); Lk.new(vg.outputs[0], addv.inputs[1])
# 🔴 体積（不均一の灰の吸収）は1080px・24smp で1フレーム84秒＝動画が枠に入らない。厚みは位置で決まっているので、
#    吸収を表面の色に移す：板を抜ける光は表と裏の2回、色 = sqrt(exp(-(σ色 + σ灰·S)·2h)) を掛ける（Beer–Lambert を位置から計算）
if os.environ.get("II_VOLUME") == "1":
    Lk.new(addv.outputs[0], out.inputs["Volume"])
else:
    q = mth('MINIMUM', er, 1.0)
    hq = mth('MULTIPLY_ADD', mth('POWER', q, PW), H1 - H0, H0)          # 片面の厚み h(q)
    L = mth('MULTIPLY', hq, 2.0)                                         # 板を抜ける道のり
    Sg = mr.outputs["Result"]
    chans = []
    for c in range(3):
        sig = mth('MULTIPLY_ADD', Sg, NEU, ABS[c])                       # σ色 + σ灰·S
        chans.append(mth('EXPONENT', mth('MULTIPLY', mth('MULTIPLY', sig, L), -0.5)))  # 1回の界面で sqrt(T)
    cc = N.new("ShaderNodeCombineColor")
    for c in range(3):
        Lk.new(chans[c], cc.inputs[c])
    Lk.new(cc.outputs[0], glass.inputs["Base Color"])
lens.data.materials.append(m)

parts = [lens, plinth, foot]

# ------------------------------------------------------------- 光
KEY_LOC = Vector((4.4, -3.3, 1.75))
key = area("key", KEY_LOC, 2.4, 640, (1.0, 0.98, 0.95), target=(0, 0.2, 0.85))
key.visible_glossy = False
fill = area("fill", (-2.5, -3.0, 1.6), 3.0, 0.0, (1.0, 1.0, 1.0), target=(0, 0, 0.8))
fill.data.specular_factor = 0.0
# 壁を一様に起こす大きな面（被写体からは外す＝PITFALLS #122 のライトリンク）
wash = area("wash", (-0.6, -4.5, 2.4), 7.0, 50, (1.0, 1.0, 1.0), target=(-0.3, WALL_Y, 1.3), size_y=3.0)
wash.data.specular_factor = 0.0
# 壁の左上だけを起こす（受け手は背景紙だけ＝ライトリンク）。基準の壁は左上まで白い
wallc = bpy.data.collections.new("wallonly")
wallc.objects.link(sweep)
tl = area("tl", (-1.6, -0.9, 2.7), 2.4, 75, (1.0, 1.0, 1.0), target=(-0.9, WALL_Y, 1.7))
tl.data.specular_factor = 0.0
tl.light_linking.receiver_collection = wallc
# 手前の床だけを起こす（基準の床は台の前まで白い＝台の下辺が床から切れて読める）
fld = bpy.data.lights.new("floor", 'SPOT'); fld.energy = FLOOR_E; fld.spot_size = math.radians(48); fld.spot_blend = 1.0
fld.shadow_soft_size = 0.6; fld.specular_factor = 0.0
fl = bpy.data.objects.new("floor", fld); scene.collection.objects.link(fl)
fl.location = (0.0, -1.0, 2.6)
fl.rotation_euler = (Vector((-0.35, -1.2, 0)) - fl.location).to_track_quat('-Z', 'Y').to_euler()
fl.light_linking.receiver_collection = wallc
# 板の向こうに、透過の光線にだけ写る白い面を立てる（中の光の明るさはここで決まる）。
# 🔴 壁を後ろから照らす光は、板のまわりの壁にも光の暈を描いた＝仕掛けが見える
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0.22, ZC), rotation=(math.pi / 2, 0, 0))
card = bpy.context.object; card.name = "glowcard"
card.scale = (0.9, 1.3, 1)
cm = bpy.data.materials.new("card"); cm.use_nodes = True
cN = cm.node_tree.nodes; cN.remove(cN["Principled BSDF"])
em = cN.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.97, 0.92, 1); em.inputs["Strength"].default_value = CARD_E
cm.node_tree.links.new(em.outputs[0], cN["Material Output"].inputs["Surface"])
card.data.materials.append(cm)
card.visible_camera = False
card.visible_diffuse = False
card.visible_glossy = False
card.visible_shadow = False
card.visible_volume_scatter = False
cm.cycles.emission_sampling = 'NONE'
subj = bpy.data.collections.new("subj")
subj.objects.link(lens)
wash.light_linking.receiver_collection = subj
wash.light_linking.receiver_collection.collection_objects[0].light_linking.link_state = 'EXCLUDE'
# 正面の面の影も板からは落とさない（板の右奥の壁に琥珀の暈が出て、板が光っているように見えた）
wash.light_linking.blocker_collection = subj
wash.light_linking.blocker_collection.collection_objects[0].light_linking.link_state = 'EXCLUDE'


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


TGT = Vector((0, 0, 0.80))
HERO_CAM = Vector((0.0, -2.95, 0.86))
SHOTS = [
    dict(sec=3.0,   # スライド：中の距離で、カプセルの前を横に滑る＝中の光が厚みの中で揺れる
         cam=lambda t: (lerp((-0.55, -1.9, ZC + 0.05), (0.45, -1.9, ZC - 0.02), ease(t)),
                        lerp((-0.12, 0, ZC), (0.08, 0, ZC), ease(t)), 75, 5.6, None)),
    dict(sec=2.5,   # マクロ：斜め前の寄りで、縁の輪郭と芯の橙が黒へ落ちる帯を同時に入れ、ピントを縁→芯へ送る
         cam=lambda t: (lerp((0.62, -0.78, ZC + 0.16), (0.60, -0.80, ZC + 0.04), ease(t)),
                        lerp((0.16, 0, ZC + 0.10), (0.15, 0, ZC - 0.01), ease(t)), 120, 2.4,
                        (Vector((0.24, 0, ZC + 0.12)) - lerp((0.62, -0.78, ZC + 0.16), (0.60, -0.80, ZC + 0.04), ease(t))).length * (1 - 0.2 * ease(t)))),
    dict(sec=3.0,   # 回り込み：引きで、斜めから正面へ（板の薄さ→光が開く）
         cam=lambda t: (orbit(TGT, 3.0, 0.95, -62 + 34 * ease(t)), TGT + Vector((0, 0, 0.05)), 50, 8.0, None)),
    dict(sec=3.0,   # 決め：寄りから引いて hero の構図で止まる
         cam=lambda t: (lerp((0.25, -2.75, 0.95), HERO_CAM, ease_out(min(1.0, t / 0.62))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    # 物の動き：板は斜めに向いた所から、決めのカットの頭までにゆっくり正面へ戻る（glb の動きもこれ）
    lens.rotation_euler = (0, 0, math.radians(-16 * (1 - ease(min(1.0, T / 0.74)))))


for i, sh in enumerate(SHOTS):
    for k in range(sh["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh["frames"] - 1)
        T = (f - 1) / max(1, N_FRAMES - 1)
        loc, tgt, lensmm, fstop, focus = sh["cam"](t)
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cd.lens = lensmm
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
scene.cycles.max_bounces = 8
scene.cycles.transmission_bounces = 8
scene.cycles.transparent_max_bounces = 8
scene.cycles.diffuse_bounces = 3
scene.cycles.glossy_bounces = 3
scene.cycles.volume_bounces = 0
# 🔴 灰の吸収は座標から密度を作る＝不均一な体積でレイマーチになり、1080px・24smp で1フレーム84秒かかった。
#    板の厚みは最大9cmなので刻みを粗くしても絵は変わらない
scene.cycles.volume_step_rate = VSTEP
scene.cycles.volume_max_steps = 64
m.cycles.volume_step_rate = VSTEP
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
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
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
