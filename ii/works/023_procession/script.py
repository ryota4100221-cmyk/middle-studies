# =============================================================
# MIDDLE STUDIES II 023 — PROCESSION（列）
#   Blender --background --factory-startup --python script.py -- <modes>
#   modes: test / testhero / still / anim / glb / shots
# 基準：Fellow「Stagg EKG Electric Kettle」製品ページ How it works の画像（艶消し黒のケトルが奥へ並ぶ白黒写真）
#   取るもの＝光（曇天の大きく柔らかい上奥の1灯・胴は左が起き右が落ちる）／素材（艶消しの黒い焼付け塗装・コンクリート床・漆喰壁）／
#            構図（1:1・注ぎ口の高さすれすれの望遠で列が消失点へ・手前はぼけて縁を切る）／色（無彩色・明るい灰の地に黒の反復）
#   写さないもの＝円錐の胴・木の取っ手・注ぎ口の S 字。こちらは「肩の丸い円筒の胴＋平らな蓋＋黒い摘み＋
#            低い位置から出て一度だけ折れて斜めに伸びる注ぎ口＋板の取っ手」
# =============================================================
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
modes = set(argv) or {"test"}

LOOK = dict(
    aspect=(1, 1),
    lens=100,
    fstop=20,
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


def grey(v):
    """sRGB の 0〜255 の灰 → linear"""
    c = v / 255
    x = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (x, x, x, 1.0)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ------------------------------------------------------------- 造形の道具
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


def setmat(ob, m):
    ob.data.materials.clear(); ob.data.materials.append(m)


def link(ob):
    scene.collection.objects.link(ob); return ob


def lathe(name, prof, seg=128, close_top=False):
    """prof: [(r, z), …] を z 軸まわりに回す。r=0 の点は極（1点に集める）"""
    bm = bmesh.new()
    rings = []
    for (r, z) in prof:
        if r < 1e-6:
            rings.append([bm.verts.new((0, 0, z))] * seg)
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z))
                          for i in range(seg)])
    for j in range(len(prof) - 1):
        A, B = rings[j], rings[j + 1]
        for i in range(seg):
            i2 = (i + 1) % seg
            vs = [A[i], A[i2], B[i2], B[i]]
            uniq = []
            for v in vs:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                bm.faces.new(uniq)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return link(bpy.data.objects.new(name, me))


def catmull(pts, n_per=10):
    P = [Vector(p) for p in pts]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n_per):
            t = k / n_per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return out


def sweep(name, path, radius_fn, seg=32, flat=1.0, cap_start=False, cap_end=False):
    """path に沿って円（flat<1 で楕円）を押し出す。平行移動フレームで捩れない"""
    bm = bmesh.new()
    rings = []
    n = len(path)
    T0 = (path[1] - path[0]).normalized()
    up = Vector((0, 1, 0)) if abs(T0.y) < 0.9 else Vector((1, 0, 0))
    N = T0.cross(up).normalized()
    prevT = T0
    for i, p in enumerate(path):
        T = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).normalized()
        axis = prevT.cross(T)
        if axis.length > 1e-8:
            ang = prevT.angle(T)
            from mathutils import Matrix
            N = (Matrix.Rotation(ang, 3, axis.normalized()) @ N).normalized()
        prevT = T
        B = T.cross(N).normalized()
        r = radius_fn(i / (n - 1))
        rings.append([bm.verts.new(p + N * (r * math.cos(2 * math.pi * k / seg)) +
                                   B * (r * flat * math.sin(2 * math.pi * k / seg))) for k in range(seg)])
    for j in range(n - 1):
        A, Bb = rings[j], rings[j + 1]
        for k in range(seg):
            k2 = (k + 1) % seg
            bm.faces.new((A[k], A[k2], Bb[k2], Bb[k]))
    if cap_start:
        bm.faces.new(list(reversed(rings[0])))
    if cap_end:
        c = bm.verts.new(path[-1] + (path[-1] - path[-2]).normalized() * radius_fn(1.0) * 0.35)
        for k in range(seg):
            bm.faces.new((rings[-1][k], rings[-1][(k + 1) % seg], c))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return link(bpy.data.objects.new(name, me))


# ------------------------------------------------------------- 材質
def powder(name, v, rough=0.46):
    """艶消しの焼付け塗装：粗さに大きな斑＋細かい梨地のバンプ"""
    m = principled(name, grey(v), rough=rough, spec=0.5)
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0
    nz.inputs["Detail"].default_value = 2.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.04
    bp.inputs["Distance"].default_value = 0.0004
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


BLACK = powder("powder_black", 22, rough=0.38)
WHITE = powder("powder_white", 226, rough=0.5)
INNER = principled("inner", grey(8), rough=0.6)

# ------------------------------------------------------------- 舞台：コンクリートの床＋漆喰の壁
WALL_Y = 7.0
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, WALL_Y / 2 - 1, 0))
floor = bpy.context.object; floor.name = "floor"
floor.scale = (30, WALL_Y + 2, 1)
FLOORM = principled("concrete", grey(150), rough=0.8, spec=0.25)
_n = FLOORM.node_tree; _p = _n.nodes["Principled BSDF"]
_tc = _n.nodes.new("ShaderNodeTexCoord")
_geo = _n.nodes.new("ShaderNodeNewGeometry")
_big = _n.nodes.new("ShaderNodeTexNoise"); _big.inputs["Scale"].default_value = 9.0; _big.inputs["Detail"].default_value = 6
_n.links.new(_geo.outputs["Position"], _big.inputs["Vector"])
_fine = _n.nodes.new("ShaderNodeTexNoise"); _fine.inputs["Scale"].default_value = 45; _fine.inputs["Detail"].default_value = 8
_n.links.new(_geo.outputs["Position"], _fine.inputs["Vector"])
_vor = _n.nodes.new("ShaderNodeTexVoronoi"); _vor.inputs["Scale"].default_value = 400
_n.links.new(_geo.outputs["Position"], _vor.inputs["Vector"])
_ramp = _n.nodes.new("ShaderNodeValToRGB")
_ramp.color_ramp.elements[0].position = 0.15; _ramp.color_ramp.elements[0].color = grey(88)
_ramp.color_ramp.elements[1].position = 0.85; _ramp.color_ramp.elements[1].color = grey(132)
_mix = _n.nodes.new("ShaderNodeMath"); _mix.operation = 'MULTIPLY_ADD'
_mix.inputs[1].default_value = 1.0
_n.links.new(_fine.outputs["Fac"], _mix.inputs[0])
_bigw = _n.nodes.new("ShaderNodeMath"); _bigw.operation = 'MULTIPLY_ADD'
_bigw.inputs[1].default_value = 0.3; _bigw.inputs[2].default_value = 0.35
_n.links.new(_big.outputs["Fac"], _bigw.inputs[0])
_n.links.new(_bigw.outputs[0], _mix.inputs[2])
_sub = _n.nodes.new("ShaderNodeMath"); _sub.operation = 'SUBTRACT'; _sub.inputs[1].default_value = 0.50
_n.links.new(_mix.outputs[0], _sub.inputs[0])
_n.links.new(_sub.outputs[0], _ramp.inputs["Fac"])
_sep = _n.nodes.new("ShaderNodeSeparateXYZ"); _n.links.new(_tc.outputs["Object"], _sep.inputs[0])
_dist = _n.nodes.new("ShaderNodeMapRange"); _dist.clamp = True; _dist.interpolation_type = 'SMOOTHSTEP'
_n.links.new(_sep.outputs[1], _dist.inputs["Value"])
_dist.inputs["From Min"].default_value, _dist.inputs["From Max"].default_value = -0.05, 0.5
_dist.inputs["To Min"].default_value, _dist.inputs["To Max"].default_value = 0.85, 1.45
_scr = _n.nodes.new("ShaderNodeTexNoise"); _scr.inputs["Scale"].default_value = 30; _scr.inputs["Detail"].default_value = 2
_scm = _n.nodes.new("ShaderNodeMapping"); _scm.inputs["Scale"].default_value = (22.0, 1.0, 1.0)
_scm.inputs["Rotation"].default_value = (0, 0, 0.35)
_n.links.new(_geo.outputs["Position"], _scm.inputs["Vector"]); _n.links.new(_scm.outputs[0], _scr.inputs["Vector"])
_scrr = _n.nodes.new("ShaderNodeMapRange"); _scrr.clamp = True
_scrr.inputs["From Min"].default_value, _scrr.inputs["From Max"].default_value = 0.62, 0.70
_scrr.inputs["To Min"].default_value, _scrr.inputs["To Max"].default_value = 1.0, 1.08
_n.links.new(_scr.outputs["Fac"], _scrr.inputs["Value"])
_m1 = _n.nodes.new("ShaderNodeVectorMath"); _m1.operation = 'SCALE'
_n.links.new(_ramp.outputs["Color"], _m1.inputs[0]); _n.links.new(_dist.outputs["Result"], _m1.inputs["Scale"])
_m2 = _n.nodes.new("ShaderNodeVectorMath"); _m2.operation = 'SCALE'
_n.links.new(_m1.outputs[0], _m2.inputs[0]); _n.links.new(_scrr.outputs["Result"], _m2.inputs["Scale"])
_vr = _n.nodes.new("ShaderNodeMapRange"); _vr.clamp = True
_vr.inputs["From Min"].default_value, _vr.inputs["From Max"].default_value = 0.0, 0.08
_vr.inputs["To Min"].default_value, _vr.inputs["To Max"].default_value = 1.25, 1.0
_n.links.new(_vor.outputs["Distance"], _vr.inputs["Value"])
_m3 = _n.nodes.new("ShaderNodeVectorMath"); _m3.operation = 'SCALE'
_n.links.new(_m2.outputs[0], _m3.inputs[0]); _n.links.new(_vr.outputs["Result"], _m3.inputs["Scale"])
# こての擦り跡：歪ませた Voronoi の境界を細く切った明るい曲線
_tw = _n.nodes.new("ShaderNodeTexNoise"); _tw.inputs["Scale"].default_value = 6; _tw.inputs["Detail"].default_value = 3
_n.links.new(_geo.outputs["Position"], _tw.inputs["Vector"])
_twm = _n.nodes.new("ShaderNodeVectorMath"); _twm.operation = 'MULTIPLY_ADD'
_twm.inputs[1].default_value = (0.08, 0.08, 0.08)
_n.links.new(_tw.outputs["Color"], _twm.inputs[0]); _n.links.new(_geo.outputs["Position"], _twm.inputs[2])
_tv = _n.nodes.new("ShaderNodeTexVoronoi"); _tv.feature = 'DISTANCE_TO_EDGE'; _tv.inputs["Scale"].default_value = 12
_n.links.new(_twm.outputs[0], _tv.inputs["Vector"])
_tvr = _n.nodes.new("ShaderNodeMapRange"); _tvr.clamp = True
_tvr.inputs["From Min"].default_value, _tvr.inputs["From Max"].default_value = 0.0, 0.07
_tvr.inputs["To Min"].default_value, _tvr.inputs["To Max"].default_value = 1.08, 1.0
_n.links.new(_tv.outputs["Distance"], _tvr.inputs["Value"])
_m4 = _n.nodes.new("ShaderNodeVectorMath"); _m4.operation = 'SCALE'
_n.links.new(_m3.outputs[0], _m4.inputs[0]); _n.links.new(_tvr.outputs["Result"], _m4.inputs["Scale"])
_n.links.new(_m4.outputs[0], _p.inputs["Base Color"])
_fb = _n.nodes.new("ShaderNodeBump"); _fb.inputs["Strength"].default_value = 1.0
_fb.inputs["Distance"].default_value = 0.0006
_hh = _n.nodes.new("ShaderNodeMath"); _hh.operation = 'MULTIPLY_ADD'; _hh.inputs[1].default_value = 0.5
_n.links.new(_scr.outputs["Fac"], _hh.inputs[0]); _n.links.new(_fine.outputs["Fac"], _hh.inputs[2])
_n.links.new(_hh.outputs[0], _fb.inputs["Height"])
_n.links.new(_fb.outputs["Normal"], _p.inputs["Normal"])
setmat(floor, FLOORM)

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, WALL_Y, 3))
wall = bpy.context.object; wall.name = "wall"
wall.scale = (30, 6, 1); wall.rotation_euler = (math.radians(90), 0, 0)
WALLM = principled("plaster", grey(200), rough=0.9, spec=0.3)
_wn = WALLM.node_tree; _wp = _wn.nodes["Principled BSDF"]
_wt = _wn.nodes.new("ShaderNodeNewGeometry")
_wz = _wn.nodes.new("ShaderNodeTexNoise"); _wz.inputs["Scale"].default_value = 3.0; _wz.inputs["Detail"].default_value = 8
_wn.links.new(_wt.outputs["Position"], _wz.inputs["Vector"])
_wr = _wn.nodes.new("ShaderNodeValToRGB")
_wr.color_ramp.elements[0].position = 0.3; _wr.color_ramp.elements[0].color = grey(184)
_wr.color_ramp.elements[1].position = 0.7; _wr.color_ramp.elements[1].color = grey(210)
_wn.links.new(_wz.outputs["Fac"], _wr.inputs["Fac"])
_wn.links.new(_wr.outputs["Color"], _wp.inputs["Base Color"])
setmat(wall, WALLM)

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = grey(200)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12


# ------------------------------------------------------------- ケトル（自作）
# 胴：肩の丸い円筒（わずかに上へ細る）・底は一段絞る・天は蓋の座
BODY_H = 0.205
BODY_PROF = [
    (0.0, 0.004), (0.052, 0.004), (0.0575, 0.006), (0.0598, 0.010), (0.0610, 0.016),
    (0.0610, 0.030), (0.0600, 0.100), (0.0585, 0.160), (0.0570, BODY_H - 0.020),
    (0.0556, BODY_H - 0.012), (0.0535, BODY_H - 0.0060), (0.0505, BODY_H - 0.0025), (0.0470, BODY_H - 0.0005), (0.0440, BODY_H),
    (0.0432, BODY_H), (0.0430, BODY_H - 0.0012),   # 蓋の座の溝
    (0.0422, BODY_H - 0.0012), (0.0420, BODY_H),
    (0.0, BODY_H),
]
LZ = BODY_H - 0.0004
LID_PROF = [(r, z + LZ) for (r, z) in [
    (0.0, 0.0045), (0.0380, 0.0045), (0.0400, 0.0038), (0.0412, 0.0024), (0.0416, 0.0008), (0.0416, -0.0004),
    (0.0, -0.0004)]]
KNOB_PROF = [(r, z + LZ + 0.0045) for (r, z) in [
    (0.0, 0.0245), (0.0100, 0.0245), (0.0118, 0.0239), (0.0128, 0.0227), (0.0130, 0.0210),
    (0.0118, 0.0085), (0.0085, 0.0035), (0.0075, 0.0), (0.0, 0.0)]]
SPOUT_PTS = [(-0.048, 0, 0.034), (-0.072, 0, 0.031), (-0.092, 0, 0.034), (-0.106, 0, 0.046),
             (-0.116, 0, 0.066), (-0.132, 0, 0.108), (-0.150, 0, 0.152), (-0.168, 0, 0.190),
             (-0.184, 0, 0.212), (-0.199, 0, 0.222), (-0.214, 0, 0.2225), (-0.224, 0, 0.2195)]
HANDLE_PTS = [(0.044, 0, 0.186), (0.074, 0, 0.192), (0.098, 0, 0.184), (0.110, 0, 0.160),
              (0.114, 0, 0.128), (0.112, 0, 0.098), (0.100, 0, 0.078), (0.080, 0, 0.071), (0.056, 0, 0.073)]


def make_kettle(tag, x, y, yaw=0.0, mat=None):
    mat = mat or BLACK
    root = link(bpy.data.objects.new(tag + "_root", None))
    root.location = (x, y, 0); root.rotation_euler = (0, 0, math.radians(yaw))
    objs = []
    body = lathe(tag + "_body", BODY_PROF)
    lid = lathe(tag + "_lid", LID_PROF, seg=96)
    knob = lathe(tag + "_knob", KNOB_PROF, seg=64)
    spout = sweep(tag + "_spout", catmull(SPOUT_PTS, 12),
                  lambda u: 0.0062 - 0.0020 * u - 0.0012 * max(0.0, (u - 0.9) / 0.1), seg=28, cap_end=True)
    # 注ぎ口の根元の座（胴に溶接した肉）
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.013, location=(-0.058, 0, 0.034))
    boss = bpy.context.object; boss.name = tag + "_boss"; boss.scale = (0.55, 1.0, 1.0)
    for p in boss.data.polygons:
        p.use_smooth = True
    handle = sweep(tag + "_handle", catmull(HANDLE_PTS, 10), lambda u: 0.0075, seg=24, flat=0.45)
    for o in (body, lid, knob, spout, boss, handle):
        setmat(o, mat); o.parent = root; objs.append(o)
    return root, objs


ROW_N, ROW_GAP = 14, float(os.environ.get("II_GAP", "0.30"))
YAW_STEP = float(os.environ.get("II_YAW", "-10"))
WHITE_IDX = {int(x) for x in os.environ.get("II_W", "3").split(",")}
kettles, parts = [], []
for i in range(int(os.environ.get("II_START", "1")), ROW_N):
    r, objs = make_kettle("k%02d" % i, 0.0, i * ROW_GAP, yaw=YAW_STEP * (i - 1), mat=WHITE if i in WHITE_IDX else BLACK)
    kettles.append(r); parts += objs

# ------------------------------------------------------------- 光：曇天の大きな上奥の1灯＋左の起こし
def area(name, loc, size, energy, target, size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    if size_y:
        ld.shape = 'RECTANGLE'; ld.size, ld.size_y = size, size_y
    else:
        ld.size = size
    L = link(bpy.data.objects.new(name, ld)); L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


key = area("key", (-0.8, 5.0, 3.0), 3.0, 400, (0, 2.0, 0.2), size_y=4.0)
wash = area("wash", (-0.5, 2.0, 2.6), 4.0, 900, (0, WALL_Y, 1.4), size_y=2.0)
fill = area("fill", (-3.0, 0.5, 1.6), 2.0, 40, (0, 1.0, 0.1))
front = area("front", (-0.40, -0.06, 0.22), 0.5, float(os.environ.get("II_FE", "3")), (0.0, 0.0, 0.11))
front.data.use_shadow = False
for L in (key, fill, wash, front):
    L.visible_camera = False

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = link(bpy.data.objects.new("cam", cd))
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam

_hc = [float(v) for v in os.environ.get("II_CAM", "-0.11,-0.40,0.13,0.04").split(",")]
HERO = dict(loc=Vector(_hc[:3]), tgt=Vector((_hc[3], 2.5, 0.125)), lens=LOOK["lens"],
            fstop=LOOK["fstop"], focus=float(os.environ.get("II_FOC", "1.30")))


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


# 1 マクロ：黒の2台目の蓋の摘みから白の3台目の摘みへピント送り（列はまだ同じ向き）
# 2 物の動き：注ぎ口の側の斜め上から、列が手前から奥へ1台ずつ向きを変えて扇に開く
# 3 スライド：床すれすれを横へ滑り、開いた扇を低く見る
# 4 決め：引きから押し込んで hero で止まる
PRE_YAW = 30.0


def macro_cam(t):
    """白（列の3台目・y=0.9）が +30° を向いたときの注ぎ口の先と根元を計算し、先→根元へピントを送る"""
    c, sn = math.cos(math.radians(PRE_YAW)), math.sin(math.radians(PRE_YAW))
    def w(px, pz):
        return Vector((px * c, 0.9 + px * sn, pz))
    tip, mid = w(-0.222, 0.2195), w(-0.150, 0.150)
    cam_p = lerp(tip + Vector((-0.12, -0.20, 0.05)), tip + Vector((-0.10, -0.17, 0.04)), ease(t))
    tgt = tip.lerp(mid, 0.35)
    f0, f1 = (tip - cam_p).length, (mid - cam_p).length
    return cam_p, tgt, 100, 4.0, f0 + (f1 - f0) * ease(min(1.0, max(0.0, (t - 0.15) / 0.7)))


SHOTS = [
    dict(sec=2.8, cam=lambda t: macro_cam(t), name="マクロ"),
    dict(sec=3.2, cam=lambda t: (lerp((-1.25, 0.10, 0.55), (-1.10, 0.35, 0.50), ease(t)), Vector((0.0, 1.45, 0.10)),
                                 60, 8.0, None), name="物の動き"),
    dict(sec=2.6, cam=lambda t: (lerp((-0.75, -0.35, 1.55), (-0.35, -0.45, 1.55), ease(t)), Vector((0.0, 1.5, 0.0)),
                                 70, 11.0, None), name="スライド"),
    dict(sec=3.0, cam=lambda t: (lerp(HERO["loc"] + Vector((-0.06, -0.30, 0.03)), HERO["loc"], ease_out(min(1.0, t / 0.6))),
                                 lerp(HERO["tgt"] + Vector((-0.10, 0, 0)), HERO["tgt"], ease_out(min(1.0, t / 0.6))),
                                 HERO["lens"], HERO["fstop"], HERO["focus"]), name="決め"),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    """列が手前から奥へ1台ずつ回って扇に開く（カット2）。前は揃った列、後は開いた扇＝hero"""
    for k, r in enumerate(kettles):
        if i == 0:
            sk = 0.0
        elif i == 1:
            sk = ease((t - 0.05 - 0.045 * k) / 0.32)
        else:
            sk = 1.0
        r.rotation_euler = (0, 0, math.radians(PRE_YAW + (YAW_STEP * k - PRE_YAW) * sk))


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
        for o in kettles:
            o.keyframe_insert("rotation_euler", frame=f)
            o.keyframe_insert("location", frame=f)
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
    still(os.path.join(OUT, os.environ.get("II_TESTNAME", "_test.png")), int(os.environ.get("II_TL", "720")), 48)
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
    names = {o.name for o in parts} | {o.name for o in kettles}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
