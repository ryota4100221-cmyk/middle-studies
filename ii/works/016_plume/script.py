# =============================================================
# MIDDLE STUDIES II 016 — PLUME（羽の車輪）
#
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots   （省略時 test）
#
# 基準：Anthony Howe「Plumage」（風で回るステンレスのキネティック彫刻・日没後の森の前）
# 取るもの：光（曇り空1つ・鏡面の向きで明暗が交互）／素材（磨いた薄板と刃の断面）／
#           構図（4:5 縦・望遠・闇の余白）／色（ほぼ黒の深緑に無彩の金属）
# 造形は自分で起こす：渦の腕に輪の羽を下げた内外2枚の車輪が逆に回る・刃の茎・丸い台
# =============================================================
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

# ------------------------------------------------------------- LOOK
LOOK = dict(
    aspect=(4, 5),
    lens=135,
    fstop=2.8,
    view="AgX",
    look="AgX - Medium High Contrast",
    exposure=0.0,
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
random.seed(16)


def sock(node, name, kind):
    """#103：名前で引くと Float が返ることがある＝型で引く"""
    return next(s for s in node.inputs if s.name == name and s.type == kind)


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


def principled(name, color, rough=0.35, metal=0.0, coat=0.0, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Specular IOR Level"].default_value = spec
    return m


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 2.0), size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy, ld.color, ld.size = energy, color, size
    if size_y:
        ld.shape = 'RECTANGLE'; ld.size_y = size_y
    L = bpy.data.objects.new(name, ld); scene.collection.objects.link(L)
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    L.visible_camera = False
    return L


def mesh_obj(name, verts, faces, smooth=True):
    me = bpy.data.meshes.new(name + "_me")
    me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = smooth
    return ob


# ------------------------------------------------------------- 材質
steel = principled("steel", (0.86, 0.86, 0.88, 1), rough=0.07, metal=1.0)
brushed = principled("brushed", (0.74, 0.76, 0.92, 1), rough=0.24, metal=1.0)
_nt = brushed.node_tree; _p = _nt.nodes["Principled BSDF"]
_tc = _nt.nodes.new("ShaderNodeTexCoord"); _mp = _nt.nodes.new("ShaderNodeMapping")
_mp.inputs["Scale"].default_value = (260, 260, 3)          # 縦（茎の長手≒z）に伸ばした筋
_hn = _nt.nodes.new("ShaderNodeTexNoise"); _hn.inputs["Scale"].default_value = 1.0; _hn.inputs["Detail"].default_value = 2
_hr = _nt.nodes.new("ShaderNodeMapRange"); _hr.inputs["To Min"].default_value = 0.07; _hr.inputs["To Max"].default_value = 0.18
_nt.links.new(_tc.outputs["Object"], _mp.inputs["Vector"]); _nt.links.new(_mp.outputs[0], _hn.inputs["Vector"])
_nt.links.new(_hn.outputs["Fac"], _hr.inputs["Value"]); _nt.links.new(_hr.outputs["Result"], _p.inputs["Roughness"])
concrete = principled("concrete", hex_to_linear("#8E8A90"), rough=0.85, spec=0.2)
_nt = concrete.node_tree; _p = _nt.nodes["Principled BSDF"]
_cn = _nt.nodes.new("ShaderNodeTexNoise"); _cn.inputs["Scale"].default_value = 38.0; _cn.inputs["Detail"].default_value = 12
_cr = _nt.nodes.new("ShaderNodeValToRGB")
_cr.color_ramp.elements[0].color = hex_to_linear("#8A8582"); _cr.color_ramp.elements[1].color = hex_to_linear("#CFC9C4")
_cr.color_ramp.elements[0].position = 0.2; _cr.color_ramp.elements[1].position = 0.8
_nt.links.new(_cn.outputs["Fac"], _cr.inputs["Fac"]); _nt.links.new(_cr.outputs["Color"], _p.inputs["Base Color"])
_cb = _nt.nodes.new("ShaderNodeBump"); _cb.inputs["Strength"].default_value = 0.6; _cb.inputs["Distance"].default_value = 0.004
_nt.links.new(_cn.outputs["Fac"], _cb.inputs["Height"]); _nt.links.new(_cb.outputs["Normal"], _p.inputs["Normal"])

# ------------------------------------------------------------- 舞台：日没後の草地と森
# 地面：暗いオリーブの草地（色むらはノイズで）
gm = bpy.data.materials.new("meadow"); gm.use_nodes = True
nt = gm.node_tree; p = nt.nodes["Principled BSDF"]
p.inputs["Roughness"].default_value = 0.95
p.inputs["Specular IOR Level"].default_value = 0.0     # 寝た角度で空を拾って地平の手前が白むのを止める
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35
nz.inputs["Detail"].default_value = 6
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = hex_to_linear("#3C4026")
ramp.color_ramp.elements[1].color = hex_to_linear("#868448")
gtc = nt.nodes.new("ShaderNodeTexCoord"); gmp = nt.nodes.new("ShaderNodeMapping")
gmp.inputs["Scale"].default_value = (60, 6, 1)          # 草の細い筋（奥行き方向に伸ばす）
gnz = nt.nodes.new("ShaderNodeTexNoise"); gnz.inputs["Scale"].default_value = 1.0; gnz.inputs["Detail"].default_value = 4
gmx = nt.nodes.new("ShaderNodeMath"); gmx.operation = 'MULTIPLY_ADD'
gmx.inputs[1].default_value = 0.55
nt.links.new(gtc.outputs["Object"], gmp.inputs["Vector"]); nt.links.new(gmp.outputs[0], gnz.inputs["Vector"])
nt.links.new(gnz.outputs["Fac"], gmx.inputs[0]); nt.links.new(nz.outputs["Fac"], gmx.inputs[2])
nt.links.new(gmx.outputs[0], ramp.inputs["Fac"])
ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[1].position = 0.95
gbump = nt.nodes.new("ShaderNodeBump"); gbump.inputs["Strength"].default_value = 0.8; gbump.inputs["Distance"].default_value = 0.03
gbn = nt.nodes.new("ShaderNodeTexNoise"); gbn.inputs["Scale"].default_value = 1.0; gbn.inputs["Detail"].default_value = 3
gbm = nt.nodes.new("ShaderNodeMapping"); gbm.inputs["Scale"].default_value = (90, 30, 1)
nt.links.new(gtc.outputs["Object"], gbm.inputs["Vector"]); nt.links.new(gbm.outputs[0], gbn.inputs["Vector"])
nt.links.new(gbn.outputs["Fac"], gbump.inputs["Height"]); nt.links.new(gbump.outputs["Normal"], p.inputs["Normal"])
gsep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(gtc.outputs["Object"], gsep.inputs[0])
gband = nt.nodes.new("ShaderNodeMapRange")       # 局所 y（＝世界 y−20）：手前 −28 → 奥 −5
gband.inputs["From Min"].default_value = -26; gband.inputs["From Max"].default_value = -10
gbr = nt.nodes.new("ShaderNodeValToRGB")
gbr.color_ramp.elements[0].color = (2.3, 2.3, 2.0, 1)
gbr.color_ramp.elements[0].position = 0.0
gbr.color_ramp.elements[1].color = (0.02, 0.025, 0.018, 1)   # 🔴 new() の前に：足すと並べ替わって [1] が中の点を指す
_e = gbr.color_ramp.elements.new(0.35); _e.color = (0.8, 0.78, 0.62, 1)
nt.links.new(gsep.outputs["Y"], gband.inputs["Value"]); nt.links.new(gband.outputs["Result"], gbr.inputs["Fac"])
gmul = nt.nodes.new("ShaderNodeMix"); gmul.data_type = 'RGBA'; gmul.blend_type = 'MULTIPLY'
sock(gmul, "Factor", 'VALUE').default_value = 1.0
nt.links.new(ramp.outputs["Color"], sock(gmul, "A", 'RGBA')); nt.links.new(gbr.outputs["Color"], sock(gmul, "B", 'RGBA'))
nt.links.new(next(o for o in gmul.outputs if o.type == 'RGBA'), p.inputs["Base Color"])
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 20, 0))
ground = bpy.context.object; ground.name = "ground"
ground.data.materials.append(gm)

# 森：奥の暗い壁（ボケで溶ける）。下の縁だけ茂みで少し起きる
fm = bpy.data.materials.new("forest"); fm.use_nodes = True
nt = fm.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputMaterial")
em = nt.nodes.new("ShaderNodeEmission")
tc = nt.nodes.new("ShaderNodeTexCoord")
nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 0.45
nz2.inputs["Detail"].default_value = 14; nz2.inputs["Roughness"].default_value = 0.78
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
mr = nt.nodes.new("ShaderNodeMapRange")   # 高さ z → 下の茂みほど明るい
mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 3.0
mr.inputs["To Min"].default_value = 1.15; mr.inputs["To Max"].default_value = 0.85
r2 = nt.nodes.new("ShaderNodeValToRGB")
r2.color_ramp.elements[0].position = 0.46
r2.color_ramp.elements[0].color = (0.0056, 0.0080, 0.0058, 1)
r2.color_ramp.elements[1].position = 0.58
r2.color_ramp.elements[1].color = (0.0075, 0.0115, 0.0072, 1)
mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
sock(mul, "Factor", 'VALUE').default_value = 1.0
nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
nt.links.new(tc.outputs["Object"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
nt.links.new(nz2.outputs["Fac"], r2.inputs["Fac"])
nt.links.new(r2.outputs["Color"], sock(mul, "A", 'RGBA'))
nt.links.new(mr.outputs["Result"], sock(mul, "B", 'RGBA'))
nt.links.new(next(s for s in mul.outputs if s.type == 'RGBA'), em.inputs["Color"])
em.inputs["Strength"].default_value = 1.0
nt.links.new(em.outputs[0], out.inputs[0])
verts = [(-60, 16, 0), (60, 16, 0), (60, 16, 30), (-60, 16, 30)]
forest = mesh_obj("forest", verts, [(0, 1, 2, 3)], smooth=False)
forest.data.materials.append(fm)
forest.visible_shadow = False

# 森の手前の茂み：暗い塊を並べて、地平の一直線を崩す（ボケで溶ける）
bm_mat = bpy.data.materials.new("bush"); bm_mat.use_nodes = True
_bp = bm_mat.node_tree.nodes["Principled BSDF"]
_bp.inputs["Base Color"].default_value = hex_to_linear("#070A05"); _bp.inputs["Roughness"].default_value = 0.9
_bp.inputs["Specular IOR Level"].default_value = 0.1
rnd = random.Random(7)
bushes = []
for i in range(0):   # round 10 で撤去（空を受けて森より明るい丘になった）
    x = -30 + 60 * i / 45 + rnd.uniform(-0.8, 0.8)
    r = rnd.uniform(0.8, 2.6)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r, location=(x, 14.5 + rnd.uniform(-1.0, 1.0), r * rnd.uniform(-0.2, 0.35)))
    b = bpy.context.object; b.name = f"bush{i}"
    b.scale = (rnd.uniform(1.0, 1.8), 1.0, rnd.uniform(0.6, 1.1))
    b.data.materials.append(bm_mat)
    bushes.append(b)

# 空：日没後の曇り。天頂が青灰に明るく、地平は森で暗い（金属はこれを映して明暗が交互になる）
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
nt = world.node_tree
bgn = nt.nodes["Background"]
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
rw = nt.nodes.new("ShaderNodeValToRGB")
rw.color_ramp.elements[0].position = 0.02
rw.color_ramp.elements[0].color = (0.004, 0.006, 0.005, 1)
rw.color_ramp.elements[1].position = 0.32
rw.color_ramp.elements[1].color = (0.36, 0.38, 0.80, 1)
rw.color_ramp.elements[1].position = 0.72
_mid = rw.color_ramp.elements.new(0.22); _mid.color = (0.07, 0.085, 0.11, 1)
nt.links.new(tc.outputs["Generated"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], rw.inputs["Fac"])
nt.links.new(rw.outputs["Color"], bgn.inputs["Color"])
bgn.inputs["Strength"].default_value = 1.0

# ------------------------------------------------------------- 被写体
# 台：角の丸い低いコンクリートの楕円盤
def slab(name, a, b, h, nexp=4.0, N=96, bev=0.012):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N
        c, s = math.cos(t), math.sin(t)
        pts.append((a * math.copysign(abs(c) ** (2 / nexp), c), b * math.copysign(abs(s) ** (2 / nexp), s)))
    verts = [(x, y, 0) for x, y in pts] + [(x, y, h) for x, y in pts]
    faces = [tuple(range(N - 1, -1, -1)), tuple(range(N, 2 * N))]
    for i in range(N):
        j = (i + 1) % N
        faces.append((i, j, N + j, N + i))
    ob = mesh_obj(name, verts, faces, smooth=False)
    bevel_obj(ob, bev, segments=3)
    return ob


plinth = slab("plinth", 1.25, 0.55, 0.13, nexp=14.0, bev=0.005)
plinth.location.z = -0.05   # 地面へ少し沈める
plinth.data.materials.append(concrete)

# 茎：幅の広い刃（凸レンズの断面）が S 字に立ち上がる
def stem_center(s):
    x = 0.20 * math.sin(math.pi * s * 0.9) - 0.42 * s ** 2.2
    z = 0.095 + 2.37 * s
    return Vector((x, 0.0, z))


def stem_mesh(n=90, m=24):
    verts, faces = [], []
    for i in range(n + 1):
        s = i / n
        c = stem_center(s)
        tng = (stem_center(min(1, s + 1e-3)) - stem_center(max(0, s - 1e-3))).normalized()
        nrm = Vector((-tng.z, 0, tng.x))            # 画面の中で幅を持つ向き
        w = 0.34 * (1 - s) ** 1.1 + 0.045 * s       # 幅：根元 34cm → 先 4.5cm
        th = 0.22 * (1 - s) + 0.03 * s              # 折れの深さ（V の稜まで）
        flare = 1.0
        for k in range(m):
            a = 2 * math.pi * k / m
            u = math.cos(a)
            # V 字に折れた刃：表は中央の稜へ向けて2枚の平面、裏はほぼ平ら
            v = (1 - abs(u)) * 1.0 if math.sin(a) > 0 else -0.18 * (1 - u * u)
            twist = 0.5 * s                          # 上へ向けてわずかにひねる
            off = nrm * (u * w * 0.5 * flare)
            off = Matrix.Rotation(twist, 3, tng) @ (off + Vector((0, v * th * 0.5, 0)))
            verts.append(tuple(c + off))
    for i in range(n):
        for k in range(m):
            a, b = i * m + k, i * m + (k + 1) % m
            faces.append((a, b, b + m, a + m))
    faces.append(tuple(range(m - 1, -1, -1)))
    faces.append(tuple(range(n * m, n * m + m)))
    return verts, faces


# 座板：刃の根元を受ける鉄の板
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, 0.0, 0.08 + 0.0075))
foot = bpy.context.object; foot.name = "foot"
foot.scale = (0.46, 0.26, 0.015); bpy.ops.object.transform_apply(scale=True)
bevel_obj(foot, 0.003, segments=2)
v, f = stem_mesh()
stem = mesh_obj("stem", v, f)
stem.data.materials.append(brushed)
foot.data.materials.append(brushed)

TOP = stem_center(1.0)
HUB = Vector((0.18, -0.05, 2.98))
AXIS = Vector((0.62, -0.66, 0.36)).normalized()     # 車輪の軸＝右手前上を向く


def tube(name, pts, r, seg=12, mat=None):
    verts, faces = [], []
    n = len(pts)
    for i, pnt in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(n - 1, i + 1)]
        t = (Vector(b) - Vector(a)).normalized()
        q = t.to_track_quat('Z', 'Y')
        for k in range(seg):
            ang = 2 * math.pi * k / seg
            off = q @ Vector((math.cos(ang) * r, math.sin(ang) * r, 0))
            verts.append(tuple(Vector(pnt) + off))
    for i in range(n - 1):
        for k in range(seg):
            a, b = i * seg + k, i * seg + (k + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    faces.append(tuple(range(seg - 1, -1, -1)))
    faces.append(tuple(range((n - 1) * seg, n * seg)))
    ob = mesh_obj(name, verts, faces)
    if mat:
        ob.data.materials.append(mat)
    return ob


# 茎の先から車輪の軸受けへ：細い棒が弧を描いて回り込む
def bez(p0, p1, p2, p3, t):
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


arc_pts = [bez(TOP, TOP + Vector((-0.10, 0, 0.45)), HUB + Vector((-0.55, 0.10, 0.25)) , HUB - AXIS * 0.18, i / 40)
           for i in range(41)]
arc = tube("arc", arc_pts, 0.016, mat=brushed)

# 軸受け
bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.16, vertices=32, location=HUB - AXIS * 0.06)
hubc = bpy.context.object; hubc.name = "hub"
hubc.rotation_euler = AXIS.to_track_quat('Z', 'Y').to_euler()
bevel_obj(hubc, 0.006, segments=2)
hubc.data.materials.append(brushed)

# 羽：輪の羽（外形は涙、内は首の側を厚く残した抜き）。大きさ1の型を1つ作り、使い回す
def petal_mesh(name, L=1.0, W=0.62, N=56, th=0.010):
    outer, inner = [], []
    for i in range(N):
        t = 2 * math.pi * i / N
        e = (1 - math.cos(t)) / 2
        x = L * e
        y = W / 2 * math.sin(t) * e ** 0.85
        outer.append((x, y))
        inner.append((0.36 * L + 0.585 * x, 0.56 * y))
    bow = lambda x, y: 0.9 * y * y + 0.05 * x * x       # 幅方向にわずかに反らす＝1枚の中で映る空がずれて明暗が流れる
    verts = [(x, y, bow(x, y) - th / 2) for x, y in outer] + [(x, y, bow(x, y) - th / 2) for x, y in inner] + \
            [(x, y, bow(x, y) + th / 2) for x, y in outer] + [(x, y, bow(x, y) + th / 2) for x, y in inner]
    O0, I0, O1, I1 = 0, N, 2 * N, 3 * N
    faces = []
    for i in range(N):
        j = (i + 1) % N
        faces.append((O1 + i, O1 + j, I1 + j, I1 + i))      # 表
        faces.append((O0 + j, O0 + i, I0 + i, I0 + j))      # 裏
        faces.append((O0 + i, O0 + j, O1 + j, O1 + i))      # 外の小口
        faces.append((I0 + j, I0 + i, I1 + i, I1 + j))      # 内の小口
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    edges = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > math.radians(50)]
    bmesh.ops.bevel(bm, geom=edges, offset=th * 0.3, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = abs(p.normal.z) < 0.98
    return me


PETAL = petal_mesh("petal_me")
for_glint = []


def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); scene.collection.objects.link(e)
    e.empty_display_size = 0.1
    if parent:
        e.parent = parent
    e.location = loc
    return e


# 車輪の座：軸に沿ったローカル座標（Z＝軸）
seat = empty("seat")
seat.location = HUB
seat.rotation_euler = AXIS.to_track_quat('Z', 'Y').to_euler()


def wheel(name, K, r0, r1, n_petal, size0, size1, curl, cup, sign, z0, hoop=True):
    """渦の腕に、葉のように羽を下げる（羽の長手は腕から外へ、接線と放射の間）"""
    root = empty(name, seat, (0, 0, z0))
    for j in range(K):
        ph0 = 2 * math.pi * j / K + 0.3 * sign
        def P(r):
            u = (r - r0) / (r1 - r0)
            ph = ph0 + sign * curl * u ** 0.9
            return Vector((r * math.cos(ph), r * math.sin(ph), cup * u ** 2))
        pts = [P(r0 + (r1 - r0) * i / 30) for i in range(31)]
        arm = tube(f"{name}_arm{j}", pts, 0.006, seg=10, mat=steel); arm.parent = root
        base_f = 22 * math.sin(1.7 * j + 0.6) + 8 * random.uniform(-1, 1)   # 正面を挟んで±30°
        for k in range(n_petal):
            u = (k + 1) / n_petal
            r = r0 + (r1 - r0) * (0.10 + 0.90 * u)
            a = P(min(r, r1 - 0.011))
            tng = (P(min(r, r1 - 0.011) + 0.01) - a).normalized()
            rad = Vector((a.x, a.y, 0)).normalized()
            sz = size0 + (size1 - size0) * u ** 1.2
            dirv = (rad * 0.75 + tng * 0.65 * sign + Vector((0, 0, 0.14))).normalized()
            ob = bpy.data.objects.new(f"{name}_p{j}_{k}", PETAL)
            scene.collection.objects.link(ob)
            ob.parent = root
            side = dirv.cross(Vector((0, 0, 1))).normalized()
            nrm = dirv.cross(side).normalized()
            feather = math.radians(base_f + 3 * k + 5 * random.uniform(-1, 1))   # 腕の中では段々にひねる
            q = Matrix.Rotation(feather, 3, dirv)
            side, nrm = q @ side, q @ nrm
            M = Matrix((dirv, side, nrm)).transposed()
            ob.matrix_basis = Matrix.Translation(a - dirv * 0.03 * sz) @ M.to_4x4() @ Matrix.Scale(sz, 4)
            for_glint.append(ob)
    ring_pts = [Vector((r0 * math.cos(2 * math.pi * i / 64), r0 * math.sin(2 * math.pi * i / 64), 0)) for i in range(65)]
    if hoop:
        rg = tube(f"{name}_hoop", ring_pts, 0.009, seg=10, mat=steel); rg.parent = root
    return root


if not PETAL.materials:
    PETAL.materials.append(steel)
inner = wheel("inner", 8, 0.07, 0.62, 5, 0.18, 0.28, 1.0, 0.16, +1, 0.06, hoop=False)
outer = wheel("outer", 12, 0.55, 1.18, 7, 0.22, 0.36, 0.7, 0.08, -1, -0.04)
# 軸受けまわり：車輪ごとのボス板＋座金＋軸の頭（中心に「組んだ物」の密度を作る）
def disc(name, parent, r, h, z, seg=48, bev=0.003):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=seg, location=(0, 0, 0))
    d = bpy.context.object; d.name = name
    bevel_obj(d, bev, segments=2)
    d.data.materials.append(brushed); d.parent = parent; d.location = (0, 0, z)
    return d
disc("inner_boss", inner, 0.085, 0.022, 0.0)
disc("inner_washer", inner, 0.055, 0.03, 0.025)
disc("outer_boss", outer, 0.11, 0.018, 0.0)
disc("cap", seat, 0.032, 0.06, 0.10)
disc("bearing", seat, 0.06, 0.12, -0.10)
# 外の輪を内へつなぐ細いスポーク
spk = []
for j in range(4):
    a = 2 * math.pi * j / 4 + 0.4
    spk.append(tube(f"spoke{j}", [Vector((0.05 * math.cos(a), 0.05 * math.sin(a), 0)),
                                   Vector((0.55 * math.cos(a), 0.55 * math.sin(a), -0.04))], 0.006, seg=8, mat=steel))
    spk[-1].parent = outer

parts = [plinth, foot, stem, arc, hubc, seat]   # 🔴 被写体（子の羽・腕は seat の子として拾われる）
anim_objs = [inner, outer]

# ------------------------------------------------------------- 光
# 空そのもの（World）が主。足すのは、空の明るい側（左上奥）を代わりに持つ大きな面と、手前の弱い起こしだけ
key = area("skyglow", (-6.0, 4.0, 9.0), 8.0, 500, (0.58, 0.66, 1.0), target=(0, 0, 2.2))
glint = area("glint", (-7.0, -12.0, 7.5), 3.2, 16000, (1.0, 0.97, 0.92), target=(0.2, 0, 3.0))
# 照りの点は金属にだけ（#107 のライトリンク）。草・台・茂みを洗わない
metal_rcv = bpy.data.collections.new("metal_rcv")
for o in [stem, arc, hubc] + list(seat.children_recursive):
    if o.type == 'MESH':
        metal_rcv.objects.link(o)
glint.light_linking.receiver_collection = metal_rcv
fill = area("front", (3.0, -12.0, 3.0), 5.0, 160, (0.60, 0.66, 1.0), target=(0, 0, 2.0))

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


TGT = Vector((0.15, 0, 2.05))
HERO_CAM = Vector((1.9, -19.5, 1.25))
SHOTS = [
    dict(sec=2.5,   # スライド：刃の茎を根元から上へなめる（稜の明暗が流れる）
         cam=lambda t: (lerp((-0.9, -6.2, 0.35), (-0.6, -6.2, 2.1), ease(t)),
                        lerp((-0.05, 0, 0.45), (-0.25, 0, 2.25), ease(t)), 120, 2.8, None)),
    dict(sec=3.0,   # マクロ：回る羽の縁を浅いピントで（ピントを手前の羽→奥の羽へ送る）
         cam=lambda t: (lerp((2.2, -3.9, 3.55), (1.7, -4.1, 3.35), ease(t)), HUB + Vector((0.22, -0.12, 0.04)),
                        150, 1.8, 4.05 + 0.5 * ease(t))),
    dict(sec=3.0,   # 回り込み：頭を左下から仰いで弧を描く
         cam=lambda t: (orbit(Vector((0.1, 0, 2.7)), 8.0, 1.9 + 0.4 * ease(t), -48 + 32 * ease(t)),
                        Vector((0.1, 0, 2.7)), 100, 2.8, None)),
    dict(sec=3.0,   # 決め：引きながら入って hero の構図で止まる
         cam=lambda t: (lerp(HERO_CAM + Vector((0.9, 3.0, 0.3)), HERO_CAM, ease_out(min(1.0, t / 0.6))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

SPIN_IN, SPIN_OUT = 26.0, -15.0   # 度/秒（逆回り）


def pose(i, t, T, f):
    sec = (f - 1) / FPS
    inner.rotation_euler = (0, 0, math.radians(SPIN_IN * sec))
    outer.rotation_euler = (0, 0, math.radians(SPIN_OUT * sec))


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
        pose(i, t, T, f)
        for o in anim_objs:
            o.keyframe_insert("rotation_euler", frame=f)

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
scene.cycles.max_bounces = 10
scene.cycles.glossy_bounces = 8
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


def film_grain(path, sigma=3.0 / 255, seed=16):
    """写真の粒を後から乗せる（#104）"""
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

if "shots" in modes:
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
    names = set()
    for o in parts:
        names.add(o.name); names.update(c.name for c in o.children_recursive)
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
