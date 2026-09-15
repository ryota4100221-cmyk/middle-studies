# =============================================================
# MIDDLE STUDY 082 — JANOME（蛇の目傘 / the ring between the centre and the edge）
#
#   光の型＝稜線（#53）  構図の型＝端寄せ（#57・81作で初の組み合わせ）  ドメイン＝雨具・和傘
#
# 蛇の目傘は、黒い傘に輪をひとつだけ入れる。
# 輪があるのは真ん中（ロクロ）でも縁（露先）でもない。そのあいだの、紙がいちばん張っているところ。
#
# 和傘の紙は一枚の平面ではない。ロクロのまわりは浅く、途中から急に落ちる。
# その折れ目が、傘がいちばん力を受けている線で、蛇の目の輪はちょうどそこを走っている。
# **雨はまんなかに降って、縁から落ちる。輪は、そのどちらでもない場所で光っている。**
#
# 造形：傘紙は極座標の格子で張る（boolean 不使用）。断面は2つの勾配の折れ線を softplus で
#       つないだもの＝折れ目 RC が稜線になる。骨（48本）のあいだで紙は内側へ垂れる。
#       裏には親骨・受骨・手元ロクロ、柄には籐巻き。
#
# 光：稜線（折れ目）に沿った帯だけが光る。E は半径だけの関数＝等値線が円（#82③）。
#     混ぜ率を持つので裾は E_FLOOR で 0 に切る（#85①）。
#
# 動き：傘の自転（1ループで骨1本ぶん×整数）＋ こちらへの倒れ α(t)（cos）＋ 上下の漂い（sin）。
#     光の量を変えているのは傘の傾きだけ。**発光の値は1フレームも動かしていない**（#69②）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 150.0                     # 随伴のライム光源（#58）

# --- 傘の骨格 -----------------------------------------------------
N_RIB  = 48                        # 骨の数（和傘の定番）
R      = 0.97                      # 傘の半径
R_HUB  = 0.055                     # 頭ロクロの半径
RC     = 0.43                      # 折れ目＝蛇の目の輪の半径
S1, S2 = 0.20, 0.66                # 内・外の勾配
CW     = 0.018                     # 折れ目の丸み（softplus の幅）
PLEAT  = 0.0025                    # 骨のあいだの垂れ（r 比）
HEM_IN = 0.010                     # 露先のあいだの紙の引き込み
NT, NR = N_RIB * 8, 72

# --- 光（稜線）----------------------------------------------------
RW_IN, RW_OUT = 0.030, 0.105      # 輪の帯の半幅。🔴 対称だと「ネオン管」（3周目）＝折れ目の内は鋭く、外の急斜面へ流れ落ちる
ES_CORE = 3.4
WHITE_FROM, WHITE_TO = 0.93, 0.35
K_MIX   = 3.0
E_FLOOR = 0.06                     # #85①

# --- 柄 ------------------------------------------------------------
SHAFT_TOP, SHAFT_BOT = 0.05, -1.85
RUNNER_Z = -0.40                   # 手元ロクロ
RS       = 0.36                    # 受骨が親骨に掛かる半径

# --- 動き --------------------------------------------------------
ALPHA0, DALPHA = 12.0, 30.0        # こちらへの倒れ（度）
BETA   = -32.0                     # 左への傾き（度）
SPIN_TURNS = 1                     # 1ループの自転（回）
BOB    = 0.035
CX, CZ = -0.10, 2.50
STILL_FRAME = 61


# =============================================================
# 純 math
# =============================================================
def smooth(e0, e1, x):
    if e1 == e0:
        return 0.0
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def softplus(x, w):
    if x / w > 30:
        return x
    return w * math.log1p(math.exp(x / w))


def pleat(th):
    """0（骨の上）..1（骨と骨のまんなか）"""
    return math.sin(N_RIB * th / 2.0) ** 2


def prof_z(r):
    """傘紙の断面：浅い内側と急な外側を折れ目 RC で継ぐ"""
    return -(S1 * r + (S2 - S1) * (softplus(r - RC, CW) - softplus(-RC, CW)))


def canopy_z(r, th):
    return prof_z(r) - PLEAT * max(0.0, r - R_HUB) * pleat(th)


def r_edge(th):
    return R * (1.0 - HEM_IN * pleat(th))


def E_of(r):
    e = math.exp(-((r - RC) / (RW_IN if r < RC else RW_OUT)) ** 2)
    return max(0.0, (e - E_FLOOR) / (1.0 - E_FLOOR))


def alpha_of(t):
    return math.radians(ALPHA0 + DALPHA * (0.5 - 0.5 * math.cos(2.0 * math.pi * t)))


def spin_of(t):
    return 2.0 * math.pi * SPIN_TURNS * t


def rot_of(t):
    """世界 = Ry(β)·Rx(α)·Rz(spin)。行列（3x3・行優先）"""
    a, b, s = alpha_of(t), math.radians(BETA), spin_of(t)
    Rz = ((math.cos(s), -math.sin(s), 0), (math.sin(s), math.cos(s), 0), (0, 0, 1))
    Rx = ((1, 0, 0), (0, math.cos(a), -math.sin(a)), (0, math.sin(a), math.cos(a)))
    Ry = ((math.cos(b), 0, math.sin(b)), (0, 1, 0), (-math.sin(b), 0, math.cos(b)))
    mul = lambda A, B: tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    return mul(Ry, mul(Rx, Rz))


def center_of(t):
    return (CX, 0.0, CZ + BOB * math.sin(2.0 * math.pi * t))


def visible_light(t):
    """#40⑥：輪の面積 × 輪の面の法線と視線の cos（外・内の勾配の平均で近似）"""
    M = rot_of(t)
    C = center_of(t)
    v = [CAM_LOC[i] - C[i] for i in range(3)]
    L = math.sqrt(sum(c * c for c in v)); v = [c / L for c in v]
    tot = 0.0
    for k in range(72):
        th = 2 * math.pi * k / 72
        for sl in (S1, S2):
            n = (sl * math.cos(th), sl * math.sin(th), 1.0)
            nl = math.sqrt(sum(c * c for c in n)); n = [c / nl for c in n]
            nw = [sum(M[i][j] * n[j] for j in range(3)) for i in range(3)]
            tot += max(0.0, sum(nw[i] * v[i] for i in range(3)))
    return tot / 144.0


# =============================================================
# ここから Blender
# =============================================================
import bpy, bmesh                                        # noqa: E402
from mathutils import Vector, Matrix                     # noqa: E402


def hex_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- マテリアル（MATERIALS.md・#52） ----------
# 蛇の目傘＝渋紙に油と漆。深く沈んだ艶＝`urushi`（漆）
KAMI = dict(rough=0.34, spec=0.30, coat=0.05, coat_rough=0.25)


def apply_black(p):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = KAMI["rough"]
    p.inputs["Specular IOR Level"].default_value = KAMI["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Coat Weight"].default_value = KAMI["coat"]
    p.inputs["Coat Roughness"].default_value = KAMI["coat_rough"]


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_body, bp_ = principled("hone")
apply_black(bp_)
# 骨と柄は竹。漆の値のままだと細い円柱が鏡面で「銀のパイプ」に読める（3周目）
bp_.inputs["Roughness"].default_value = 0.58
bp_.inputs["Specular IOR Level"].default_value = 0.20
bp_.inputs["Coat Weight"].default_value = 0.0


def glow_material(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    E = sep.outputs["X"]

    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = WHITE_FROM
    wmr.inputs["From Max"].default_value = 1.0
    wmr.inputs["To Min"].default_value = 0.0
    wmr.inputs["To Max"].default_value = WHITE_TO
    nt.links.new(E, wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])

    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    es.inputs[1].default_value = ES_CORE
    nt.links.new(E, es.inputs[0])

    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])

    blk = nt.nodes.new("ShaderNodeBsdfPrincipled")
    apply_black(blk)

    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_MIX
    nt.links.new(E, a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])

    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a1.outputs[0], mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("janome")


# ---------- 造形（bmesh・実寸。boolean 不使用）----------
def canopy_mesh(name):
    """傘紙：頭ロクロの縁 → 露先。E は半径だけで焼く（等値線が円）。
       面は E の平均で material_index を分ける（glb で輪だけを発光にするため）"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    emap = {}
    THS = [2.0 * math.pi * k / NT for k in range(NT)]
    rows = []
    for j in range(NR + 1):
        f = j / NR
        ring = []
        for th in THS:
            r = R_HUB + (r_edge(th) - R_HUB) * f
            v = bm.verts.new((r * math.cos(th), r * math.sin(th), canopy_z(r, th)))
            emap[v] = E_of(r)
            ring.append(v)
        rows.append(ring)
    for j in range(NR):
        for k in range(NT):
            k2 = (k + 1) % NT
            face = bm.faces.new((rows[j][k], rows[j][k2], rows[j + 1][k2], rows[j + 1][k]))
    for fc in bm.faces:
        fc.normal_update()
    if sum(fc.normal.z for fc in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    for fc in bm.faces:
        es = [emap[lp.vert] for lp in fc.loops]
        fc.material_index = 1 if sum(es) / len(es) > 0.02 else 0
        for lp in fc.loops:
            lp[uvl].uv = (emap[lp.vert], 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def tube(bm, pts, rad, sides=6, cap=True):
    """折れ線 pts に沿った細い管（骨・柄）"""
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        a = Vector(pts[min(i + 1, n - 1)]) - Vector(pts[max(i - 1, 0)])
        a.normalize()
        up = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
        u = a.cross(up); u.normalize()
        w = a.cross(u)
        rr = rad(i / (n - 1)) if callable(rad) else rad
        ring = []
        for s in range(sides):
            ph = 2 * math.pi * s / sides
            ring.append(bm.verts.new(Vector(p) + rr * (math.cos(ph) * u + math.sin(ph) * w)))
        rings.append(ring)
    for i in range(n - 1):
        for s in range(sides):
            s2 = (s + 1) % sides
            bm.faces.new((rings[i][s], rings[i][s2], rings[i + 1][s2], rings[i + 1][s]))
    if cap:
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])


def cylinder(bm, z0, z1, rad_fn, n_z=24, sides=24):
    """z 軸の回転体。rad_fn(z, th)"""
    rings = []
    for i in range(n_z + 1):
        z = z0 + (z1 - z0) * i / n_z
        rings.append([bm.verts.new((rad_fn(z, 2 * math.pi * s / sides) * math.cos(2 * math.pi * s / sides),
                                    rad_fn(z, 2 * math.pi * s / sides) * math.sin(2 * math.pi * s / sides), z))
                      for s in range(sides)])
    for i in range(n_z):
        for s in range(sides):
            s2 = (s + 1) % sides
            bm.faces.new((rings[i][s], rings[i][s2], rings[i + 1][s2], rings[i + 1][s]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])


def frame_mesh(name):
    """裏の骨・ロクロ・柄"""
    bm = bmesh.new()
    for k in range(N_RIB):
        th = 2 * math.pi * k / N_RIB
        c, s = math.cos(th), math.sin(th)
        # 親骨：紙の裏を露先まで
        pts = []
        for i in range(21):
            r = R_HUB + (R * 0.995 - R_HUB) * i / 20
            pts.append((r * c, r * s, prof_z(r) - 0.009))
        tube(bm, pts, lambda u: 0.0065 * (1.0 - 0.35 * u), sides=4)
        # 受骨：手元ロクロ → 親骨の RS
        p0 = Vector((0.030 * c, 0.030 * s, RUNNER_Z))
        p1 = Vector((RS * c, RS * s, prof_z(RS) - 0.016))
        tube(bm, [tuple(p0.lerp(p1, i / 6)) for i in range(7)], 0.0048, sides=4)
    # 頭ロクロ（紙の上に出る頭）
    cylinder(bm, prof_z(R_HUB) - 0.02, SHAFT_TOP,
             lambda z, th: R_HUB * (1.0 - 0.45 * smooth(0.0, SHAFT_TOP, z)), n_z=8)
    # 手元ロクロ
    cylinder(bm, RUNNER_Z - 0.05, RUNNER_Z + 0.03, lambda z, th: 0.036, n_z=4)
    # 柄：竹＋手元の籐巻き
    def shaft_r(z, th):
        r = 0.020
        if z < SHAFT_BOT + 0.40:
            r = 0.027 * (1.0 + 0.10 * math.sin(90.0 * z + th) ** 8)
        return r
    cylinder(bm, SHAFT_BOT, prof_z(R_HUB), shaft_r, n_z=140, sides=16)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mats, smooth_ang=1.0):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    for m in mats:
        ob.data.materials.append(m)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_ang)
    except Exception:
        pass
    return ob


ob_can = link(canopy_mesh("m_kasa"), "kasa", [mat_glow, mat_glow], smooth_ang=0.9)
ob_frm = link(frame_mesh("m_hone"), "hone", [mat_body], smooth_ang=0.9)
parts = [ob_can, ob_frm]

# --- キーフレーム（毎フレーム・四元数）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev = None
for f, idx in enumerate(FR_):
    t = idx / N_FRAMES
    M3 = rot_of(t)
    M = Matrix(((M3[0][0], M3[0][1], M3[0][2], 0.0),
                (M3[1][0], M3[1][1], M3[1][2], 0.0),
                (M3[2][0], M3[2][1], M3[2][2], 0.0),
                (0.0, 0.0, 0.0, 1.0)))
    q = M.to_quaternion()
    if prev is not None and q.dot(prev) < 0.0:
        q.negate()
    prev = q.copy()
    for ob in parts:
        ob.location = center_of(t)
        ob.rotation_quaternion = q
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_quaternion", frame=f + 1)

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor_obj = bpy.context.active_object
floor_obj.name = "floor"
floor_obj.data.materials.append(mat_floor)


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


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 1.02), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.85), "logo"),
        caption("MIDDLE STUDY 082 — JANOME", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = (CX, 0.0, CZ)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：骨のあいだ・傘の下が素通し

# 🔴 #58③：随伴のライム光源は発光体の外。傘の奥・床寄り
for sx, sy, sz, wt in ((-0.30, 2.0, 0.30, LIME_W), (0.30, 4.2, 0.30, LIME_W),
                       (0.80, 7.2, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(CX + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = wt
    lp.data.shadow_soft_size = 2.60
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0

world_d = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world_d; world_d.use_nodes = True
bgn = world_d.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 8.3
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは全ジオメトリ生成後（#56②）。床を受光から外す
lit = bpy.data.collections.new("lit_by_back")
bpy.context.scene.collection.children.link(lit)
for o in parts:
    lit.objects.link(o)
back.light_linking.receiver_collection = lit

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
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception:
    scene.view_settings.view_transform = 'AgX'


def setup_glare():
    """🔴 #54：try で包まない。2026-08-13 Ryota決定＝Streaks 続投。"""
    ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new("CompositorNodeRLayers")
    glr = ng.nodes.new("CompositorNodeGlare")
    ou = ng.nodes.new("NodeGroupOutput")
    glr.inputs["Type"].default_value = 'Streaks'
    glr.inputs["Threshold"].default_value = 1.2
    glr.inputs["Strength"].default_value = 0.35
    glr.inputs["Size"].default_value = 0.55
    ng.links.new(rl.outputs["Image"], glr.inputs["Image"])
    ng.links.new(glr.outputs["Image"], ou.inputs["Image"])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True


setup_glare()

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]
tH = (STILL_FRAME - 1) / N_FRAMES
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME, " α(hero) %.1f°" % math.degrees(alpha_of(tH)))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 91):
        scene.frame_set(fr); dg.update()
        allx, ally = [], []
        for ob in parts:
            ev = ob.evaluated_get(dg)
            for v in list(ev.data.vertices)[::3]:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                allx.append(c.x); ally.append(c.y)
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        sl = max(0.0, min(x1, 1) - max(x0, 0))
        sh = max(0.0, min(y1, 1) - max(y0, 0))
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  中心x %.1f%%"
              % (fr, x0, x1, y0, y1, sl * 100, sh * 100, edge, (x0 + x1) * 50))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))
    vs = [visible_light(i / 48.0) for i in range(48)]
    print(">> 🔴 #40⑥ 見える輪 max/min = %.3f   max %.4f min %.4f hero %.4f"
          % (max(vs) / max(min(vs), 1e-9), max(vs), min(vs), visible_light(tH)))
    print(">> 面数 %d" % sum(len(o.evaluated_get(dg).data.polygons)
                            for o in bpy.data.objects if o.type == 'MESH'))

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 480, 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test done")

if "testhero" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_testhero.png")
    bpy.ops.render.render(write_still=True)
    print(">> testhero done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero done")

if "phases" in modes:
    for fr in (1, 31, 61, 91):
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_082.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("kami_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = KAMI["rough"]
    m_em = bpy.data.materials.new("janome_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.34
    ob_can.data.materials[0] = m_bk
    ob_can.data.materials[1] = m_em
    ob_frm.data.materials[0] = m_bk
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True,
                                  export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
