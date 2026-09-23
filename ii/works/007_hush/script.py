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

# ------------------------------------------------------------- LOOK（007 HUSH）
# 基準：Renderly UK のヘッドホン（くすんだピンクの単色・右上の大きな柔らかいキー・16:9の極端な寄り）
# 取るのは光・素材・構図・色の組み立てだけ。造形（丸いカップ・一本の支柱・平たいバンド）は自分で起こす。
LOOK = dict(
    aspect=(16, 9),
    lens=100,
    fstop=5.6,
    view="Khronos PBR Neutral",
    look="None",
    exposure=0.0,
    bg="#E4ACAA",
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
    return L


def grid_mesh(name, nu, nv, fn, wrap_u=True, wrap_v=True, uv_scale=(1, 1)):
    """fn(u,v) -> (x,y,z)。u,v は 0→1。UV は (u*su, v*sv) で張る（ニットの目を面に沿わせるため）"""
    vu = nu if wrap_u else nu + 1
    vv = nv if wrap_v else nv + 1
    verts = [fn(i / nu, j / nv) for i in range(vu) for j in range(vv)]
    faces, uvs = [], []
    for i in range(nu if wrap_u else nu):
        for j in range(nv if wrap_v else nv):
            i1, j1 = (i + 1) % vu, (j + 1) % vv
            faces.append((i * vv + j, i1 * vv + j, i1 * vv + j1, i * vv + j1))
            su, sv = uv_scale
            uvs.append([(i / nu * su, j / nv * sv), ((i + 1) / nu * su, j / nv * sv),
                        ((i + 1) / nu * su, (j + 1) / nv * sv), (i / nu * su, (j + 1) / nv * sv)])
    me = bpy.data.meshes.new(name + "_me")
    me.from_pydata(verts, [], faces); me.update()
    uvl = me.uv_layers.new(name="UVMap")
    k = 0
    for p, quad in zip(me.polygons, uvs):
        for li, uv in zip(p.loop_indices, quad):
            uvl.data[li].uv = uv
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


def lathe(name, prof, n=160, zs=1.0):
    """X 軸まわりの回転体。prof=[(x, r)]（端は r=0 で閉じる）。zs で縦に楕円化"""
    def fn(u, v):
        j = min(int(round(v * (len(prof) - 1))), len(prof) - 1)
        x, r = prof[j]
        a = u * 2 * math.pi
        return (x, r * math.sin(a), r * math.cos(a) * zs)
    ob = grid_mesh(name, n, len(prof) - 1, fn, wrap_u=True, wrap_v=False)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=1e-5); bpy.ops.object.mode_set(mode='OBJECT')
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def arc_pts(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


# ------------------------------------------------------------- 素材
PINK = "#D6959C"


def knit_mat(name, base_hex, nu, nv, dark=0.80, bump=0.35):
    """綾目のニット：UV の斜め2方向の sin の積で一目ずつの膨らみを作り、谷を暗く・Sheen で毛羽を乗せる"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    p = N["Principled BSDF"]
    uv = N.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"
    sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(uv.outputs[0], sep.inputs[0])

    def math_node(op, a, b=None, val=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        if isinstance(a, (int, float)):
            n.inputs[0].default_value = a
        else:
            Lk.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, (int, float)):
                n.inputs[1].default_value = b
            else:
                Lk.new(b, n.inputs[1])
        return n.outputs[0]
    # メリヤスの V 目：1目＝左右2本の傾いた脚。u が目の並び（横）、v が段（縦）
    # 🔴 目の列は管の周方向（UV の v）、段は長さ方向（UV の u）＝ V の列が管に沿って走る
    X = math_node('MULTIPLY', sep.outputs[1], float(nv))
    Y = math_node('FRACT', math_node('MULTIPLY', sep.outputs[0], float(nu)))
    fx = math_node('FRACT', X)
    g = math_node('GREATER_THAN', fx, 0.5)                      # 右脚=1
    sgn = math_node('SUBTRACT', 1.0, math_node('MULTIPLY', g, 2.0))
    lx = math_node('FRACT', math_node('MULTIPLY', fx, 2.0))
    d = math_node('ADD', math_node('SUBTRACT', lx, 0.5),
                  math_node('MULTIPLY', math_node('SUBTRACT', Y, 0.5), math_node('MULTIPLY', sgn, 0.55)))
    leg = math_node('MAXIMUM', 0.0, math_node('SUBTRACT', 1.0, math_node('MULTIPLY', math_node('MULTIPLY', d, d), 13.0)))
    along = math_node('POWER', math_node('ABSOLUTE', math_node('SINE', math_node('MULTIPLY', Y, math.pi))), 1.6)
    h0 = math_node('POWER', math_node('MULTIPLY', leg, along), 0.8)
    cellx = math_node('FLOOR', math_node('MULTIPLY', X, 2.0))
    celly = math_node('FLOOR', math_node('MULTIPLY', sep.outputs[0], float(nu)))
    cv = N.new("ShaderNodeCombineXYZ"); Lk.new(cellx, cv.inputs[0]); Lk.new(celly, cv.inputs[1])
    wn_ = N.new("ShaderNodeTexWhiteNoise"); wn_.noise_dimensions = '3D'; Lk.new(cv.outputs[0], wn_.inputs["Vector"])
    h = math_node('MULTIPLY', h0, math_node('ADD', 0.35, math_node('MULTIPLY', wn_.outputs["Value"], 0.9)))
    # 目の不揃い（糸の太さのムラ）
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0
    nz.inputs["Detail"].default_value = 2.0
    tc = N.new("ShaderNodeTexCoord"); Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
    hh = math_node('ADD', math_node('MULTIPLY', h, 0.85), math_node('MULTIPLY', nz.outputs[0], 0.3))
    ramp = N.new("ShaderNodeMix"); ramp.data_type = 'RGBA'
    Lk.new(hh, ramp.inputs["Factor"])
    c = hex_to_linear(base_hex)
    ramp.inputs["A"].default_value = (c[0] * dark * 1.15, c[1] * dark * 0.8, c[2] * dark * 0.85, 1)
    ramp.inputs["B"].default_value = tuple(x * 0.4 + 0.6 * w for x, w in zip(c[:3], (0.97, 0.74, 0.76))) + (1,)
    Lk.new(ramp.outputs["Result"], p.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.004
    Lk.new(hh, bp.inputs["Height"]); Lk.new(bp.outputs[0], p.inputs["Normal"])
    rr = math_node('SUBTRACT', 0.85, math_node('MULTIPLY', hh, 0.3))   # 糸の山ほど照る
    Lk.new(rr, p.inputs["Roughness"])
    p.inputs["Sheen Weight"].default_value = 0.2
    p.inputs["Sheen Roughness"].default_value = 0.4
    p.inputs["Sheen Tint"].default_value = (1.0, 0.86, 0.85, 1)
    return m


def anodized_mat(name, base_hex, rough=0.42):
    """サテンのアルマイト：金属の照りを広くにじませ、細かいブラスト目を bump で"""
    m = principled(name, hex_to_linear(base_hex), rough=rough, metal=0.55)
    nt = m.node_tree; N = nt.nodes
    p = N["Principled BSDF"]
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 650.0; nz.inputs["Detail"].default_value = 1.0; nz.inputs["Roughness"].default_value = 0.8
    tc = N.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8
    nt.links.new(nz.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs[0], p.inputs["Normal"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough - 0.14; mr.inputs["To Max"].default_value = rough + 0.12
    nt.links.new(nz.outputs[0], mr.inputs["Value"]); nt.links.new(mr.outputs[0], p.inputs["Roughness"])
    return m


m_cup = anodized_mat("cup", PINK)
m_chrome = principled("chrome", hex_to_linear("#F2C9C4"), rough=0.08, metal=1.0)
m_mesh = knit_mat("inner", "#D39A98", 120, 120, dark=0.7, bump=0.3)
m_dark = principled("slot", hex_to_linear("#3A2020"), rough=0.5)

# ------------------------------------------------------------- 被写体（寸法は dm：カップ径 ≒ 9.4cm）
C = 0.80        # カップの内面の x（左右対称）
ZS = 1.10       # カップを縦長の楕円に
parts = []


def build_side(sgn):
    s = sgn
    R, D, RC = 0.47, 0.36, 0.24
    prof = [(0.0, 0.0), (0.0, 0.20), (0.0, R - 0.035)]
    prof += [(0.035 - 0.035 * math.cos(t), R - 0.035 + 0.035 * math.sin(t))
             for t in [k / 6 * math.pi / 2 for k in range(1, 7)]]
    prof += [(D - RC, R)]
    prof += [(D - RC + RC * math.sin(t), R - RC + RC * math.cos(t))
             for t in [k / 14 * math.pi / 2 for k in range(1, 15)]]
    # 背面はわずかに膨らむ
    prof += [(D + 0.02 * (1 - (r / (R - RC)) ** 2) ** 1.0 * (1 - (r / (R - RC))) , r) for r in [(R - RC) * (1 - k / 12) for k in range(1, 13)]]
    prof = [(C + x if s > 0 else -(C + x), r) for (x, r) in prof]
    cup = lathe("cup_%s" % ("R" if s > 0 else "L"), prof, n=192, zs=ZS)
    if s < 0:
        for p in cup.data.polygons:
            p.flip()
    cup.data.materials.append(m_cup)
    parts.append(cup)

    # クッション：X 軸まわりのトーラス（断面は角の丸い長方形に近い超楕円）
    cx, RM, hw, hr = C - 0.160, 0.292, 0.178, 0.168

    def cush(u, v):
        a = u * 2 * math.pi; b = v * 2 * math.pi
        cb, sb = math.cos(b), math.sin(b)
        e = 0.62   # 超楕円の指数（<1 で角張る）
        dx = hw * math.copysign(abs(cb) ** e, cb)
        dr = hr * math.copysign(abs(sb) ** e, sb)
        # 外周側（カップ側）へ向かうほど少し膨らみ、顔側は平らに潰れる
        r = RM + dr
        x = cx + dx * (1.0 if dx < 0 else 0.92)
        return ((x if s > 0 else -x), r * math.sin(a), r * math.cos(a) * ZS)
    cu = grid_mesh("cushion_%s" % ("R" if s > 0 else "L"), 256, 72, cush, uv_scale=(1, 1))
    if s < 0:
        for p in cu.data.polygons:
            p.flip()
    cu.data.materials.append(knit_mat("knit_c", "#CE8185", 390, 165, dark=0.26, bump=0.9))
    parts.append(cu)

    # 内側の布（クッションの穴の奥）
    inner = lathe("inner_%s" % ("R" if s > 0 else "L"),
                  [((C - 0.16) * s, 0.0), ((C - 0.16) * s, 0.16), ((C - 0.12) * s, 0.20), ((C - 0.02) * s, 0.24)], n=96, zs=ZS)
    if s > 0:
        for p in inner.data.polygons:
            p.flip()
    inner.data.materials.append(m_mesh)
    parts.append(inner)

    # 支柱：カップ天面の少し背面寄りから真上へ（研磨）。付け根に丸いハブ
    px = (C + 0.13) * s
    top = R * ZS
    bpy.ops.mesh.primitive_cylinder_add(radius=0.040, depth=0.44, location=(px, 0, top + 0.22), vertices=64)
    stem = bpy.context.object; stem.name = "stem"
    bevel_obj(stem, 0.012, segments=4)
    stem.data.materials.append(m_chrome); parts.append(stem)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.05, location=(px, 0, top - 0.035), vertices=96)
    hub = bpy.context.object; hub.name = "hub"
    bevel_obj(hub, 0.018, segments=5)
    hub.data.materials.append(m_cup); parts.append(hub)
    # スリーブ（バンドの端）
    bpy.ops.mesh.primitive_cylinder_add(radius=0.068, depth=0.22, location=(px, 0, top + 0.50), vertices=64)
    sl = bpy.context.object; sl.name = "sleeve"
    bevel_obj(sl, 0.02, segments=5)
    sl.data.materials.append(m_cup); parts.append(sl)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.066, minor_radius=0.010, location=(px, 0, top + 0.607),
                                     major_segments=96, minor_segments=16)
    col = bpy.context.object; col.name = "collar"
    for p in col.data.polygons:
        p.use_smooth = True
    col.data.materials.append(m_chrome); parts.append(col)
    # ボタン（カップの縁・手前上）と小さなスリット（背面）
    # 背面の上寄りに細いスリット（マイク穴）。縁の上に部品を置くと輪郭で割れる（round 23）ので面の中に
    if s > 0:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.0, vertices=48)
        sl2 = bpy.context.object; sl2.name = "slot"
        me2 = sl2.data
        ang = math.radians(float(os.environ.get("II_SLA", "-28")))       # 真上から手前へ倒した角度
        nrm = Vector((0, math.sin(ang), math.cos(ang) * ZS)).normalized()
        tan = Vector((0, math.cos(ang), -math.sin(ang))).normalized()
        xax = Vector((1, 0, 0))
        for v in me2.vertices:
            c0 = v.co.copy()
            v.co = nrm * (c0.z * 0.03) + xax * (c0.x * 0.075) + tan * (c0.y * 0.013)
        bevel_obj(sl2, 0.004, segments=2)
        sl2.location = Vector((C + 0.10, 0, 0)) + Vector((0, math.sin(ang) * R, math.cos(ang) * R * ZS)) - nrm * 0.006
        sl2.data.materials.append(m_dark); parts.append(sl2)
    return top


top = build_side(1)
build_side(-1)

# ヘッドバンド：左右のスリーブを結ぶ弧。断面は平たい角丸（ニット）
BX = C + 0.13
BZ0 = top + 0.74
RB = BX


LEG_F, LEG = 0.10, 0.20      # 両端の直線の脚（u の割合・長さ）＝スリーブへまっすぐ差し込む


def band(u, v):
    b = v * 2 * math.pi
    # 脚の区間はスリーブの太さまですぼめる
    k = min(u, 1 - u) / LEG_F
    sm = 1.0 if k >= 1.6 else max(0.0, (k - 0.3) / 1.3) ** 2 * (3 - 2 * max(0.0, (k - 0.3) / 1.3))
    w = 0.054 + (0.16 - 0.054) * sm
    th = 0.046 + (0.055 - 0.046) * sm
    e = 0.5
    cb, sb = math.cos(b), math.sin(b)
    dy = w * math.copysign(abs(cb) ** e, cb)
    dr = th * math.copysign(abs(sb) ** e, sb)
    if u < LEG_F or u > 1 - LEG_F:
        side = 1 if u < LEG_F else -1
        f = (LEG_F - u) / LEG_F if side > 0 else (u - (1 - LEG_F)) / LEG_F
        return (side * (RB + dr), dy, BZ0 - LEG * f)
    a = math.pi * (u - LEG_F) / (1 - 2 * LEG_F)
    r = RB + dr
    return (r * math.cos(a), dy, BZ0 + r * math.sin(a) * 0.62)


bd = grid_mesh("band", 256, 48, band, wrap_u=False, wrap_v=True, uv_scale=(1, 1))
# 端の管の口に蓋（弧を画に入れると、開いた口の中が黒い輪として写る）
_bm = bmesh.new(); _bm.from_mesh(bd.data)
bmesh.ops.holes_fill(_bm, edges=[e for e in _bm.edges if e.is_boundary], sides=0)
_bm.to_mesh(bd.data); _bm.free()
bd.data.materials.append(knit_mat("knit_b", "#CE8185", 540, 165, dark=0.26, bump=0.9))
parts.append(bd)

# リグ：全体の姿勢（parts は全部この子）
rig = bpy.data.objects.new("rig", None); scene.collection.objects.link(rig)
for o in parts:
    o.parent = rig
RIG_ROT = tuple(math.radians(float(x)) for x in os.environ.get("II_RIG", "0,-28,0").split(","))
rig.rotation_euler = RIG_ROT

# ------------------------------------------------------------- 舞台：地の無い単色（ワールドがそのまま地）
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
wn = world.node_tree.nodes; wl = world.node_tree.links
wbg = wn["Background"]
wbg.inputs["Color"].default_value = hex_to_linear("#E8B2AF")
wbg.inputs["Strength"].default_value = 0.34
# カメラに見える地だけを別に決める（照り返しの量と地の明るさを切り離す）
lp = wn.new("ShaderNodeLightPath")
cam_bg = wn.new("ShaderNodeBackground")
cam_bg.inputs["Color"].default_value = hex_to_linear(LOOK["bg"])  # 地はキーの強さと切り離してある
cam_bg.inputs["Strength"].default_value = 1.0
mix = wn.new("ShaderNodeMixShader")
wl.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
wl.new(wbg.outputs[0], mix.inputs[1]); wl.new(cam_bg.outputs[0], mix.inputs[2])
wl.new(mix.outputs[0], wn["World Output"].inputs[0])

# ------------------------------------------------------------- 光：右上の大きな柔らかいキー＋左の弱い起こし
CUPC = Vector((C + 0.17, 0, 0))
CUSPT = CUPC
key = area("key", (2.6, -3.0, 4.2), 6.0, 2100, (1.0, 0.98, 0.98), target=CUPC)
fill = area("fill", (-3.5, -3.0, 0.6), 3.0, 120, (1.0, 0.9, 0.9), target=(0, 0, 0))
under = area("under", (-2.2, -3.6, -2.4), 5.0, 70, (1.0, 0.92, 0.92), target=(0.0, 0, 1.4))
top_l = area("top", (0.5, 0.8, 4.5), 3.0, 110, (1.0, 0.95, 0.95), target=(0.5, 0, 0.5))

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

# 各カット：sec／cam(t)→(カメラ位置, 注視点, レンズmm, f値, ピント距離 or None)
HERO_AZ, HERO_EL, HERO_D = float(os.environ.get("II_HAZ", "14")), float(os.environ.get("II_HEL", "-24")), float(os.environ.get("II_HD", "6.2"))
HERO_TGT = Vector(tuple(map(float, os.environ.get("II_HT", "0.50,0,0.80").split(","))))


def sph(tgt, az, el, d):
    a, e = math.radians(az), math.radians(el)
    return Vector(tgt) + Vector((d * math.cos(e) * math.sin(a), -d * math.cos(e) * math.cos(a), d * math.sin(e)))


HERO_LOC = sph(HERO_TGT, HERO_AZ, HERO_EL, HERO_D)
RM_ = rig.rotation_euler.to_matrix()


def W(v):                        # リグの中の座標 → ワールド
    return RM_ @ Vector(v)


KEY0 = Vector(key.location)
MID = W((0.0, 0.0, 0.9))                      # 全体の中心
CUSH = W((C - 0.16, -0.46, 0.05))             # 右のクッションの手前の膨らみ
BACK = W((C + 0.30, -0.12, 0.10))             # 右のカップの背面

SHOTS = [
    dict(sec=3.0,   # 回り込み：全体の弧と両方のカップを見せる引き
         cam=lambda t: (sph(MID + Vector((0, 0, -0.25)), 16 - 16 * ease(t), -16 + 12 * ease(t), 12.5), MID + Vector((0, 0, -0.25)), 70, 6.3, None)),
    dict(sec=2.75,  # マクロ：クッションのニットを低くなめる＋ピント送り
         cam=lambda t: (CUSH + W((0.55, -1.55, -0.35 + 0.30 * ease(t))), CUSH + W((0.0, 0.0, 0.10 * ease(t))),
                        135, 2.8, None)),
    dict(sec=2.75,  # 光の走り：カップの背面に照りの帯を走らせる（カメラはわずかに寄るだけ）
         cam=lambda t: (BACK + W((3.1 - 0.25 * ease(t), -0.9, 0.55)), BACK + W((0.0, 0.08, 0.0)), 90, 4.5, None)),
    dict(sec=3.0,   # 決め：下から持ち上がりながら hero に入って止まる
         cam=lambda t: (lerp(sph(HERO_TGT, HERO_AZ - 10, HERO_EL - 8, HERO_D + 1.2), HERO_LOC,
                             ease_out(min(1.0, t / 0.58))), HERO_TGT, LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    pass


def light_path(i, t):
    if i == 2:   # キーを背面の向こうから手前上へ回す＝照りの帯が面を横切る
        key.location = lerp(W((5.0, 1.5, 1.2)), W((1.5, -4.0, 4.5)), ease(t))
        key.rotation_euler = (BACK - key.location).to_track_quat('-Z', 'Y').to_euler()
    else:
        key.location = KEY0
        key.rotation_euler = (CUSPT - KEY0).to_track_quat('-Z', 'Y').to_euler()


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
        for L in (key,):
            L.keyframe_insert("location", frame=f)
            L.keyframe_insert("rotation_euler", frame=f)

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


if "overview" in modes:   # 造形の確認用（全体を斜めから）
    scene.frame_set(STILL_FRAME)
    cam.animation_data_clear(); cd.animation_data_clear()
    cam.location = (2.6, -6.5, 2.2)
    cam.rotation_euler = (Vector((0, 0, 0.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = 50; cd.dof.use_dof = False
    scene.render.resolution_x, scene.render.resolution_y = 960, 540
    scene.cycles.samples = 32
    scene.render.filepath = os.path.join(OUT, "_overview.png")
    bpy.ops.render.render(write_still=True)
    print(">> overview done")

if "probe" in modes:   # 角度の探り撮り（az: -Y から右回り・el: 仰角）
    import itertools
    scene.frame_set(STILL_FRAME)
    cam.animation_data_clear(); cd.animation_data_clear()
    cd.lens = 100; cd.dof.use_dof = False
    scene.render.resolution_x, scene.render.resolution_y = 480, 270
    scene.cycles.samples = 16
    PR = [tuple(map(float, x.split(","))) for x in os.environ.get("II_PROBE", "-40,-20;0,-20;40,-20;-40,15;0,15;40,15").split(";")]
    for k, (az, el) in enumerate(PR):
        tgt = Vector(os.environ.get("II_PT", "%f,0,0.1" % CUPC.x).split(",") and tuple(map(float, os.environ.get("II_PT", "%f,0,0.1" % CUPC.x).split(","))))
        dist = float(os.environ.get("II_PD", "5.0"))
        a, e = math.radians(az), math.radians(el)
        cam.location = tgt + Vector((dist * math.cos(e) * math.sin(a), -dist * math.cos(e) * math.cos(a), dist * math.sin(e)))
        cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = os.path.join(OUT, "_probe_%d.png" % k)
        bpy.ops.render.render(write_still=True)
    print(">> probe done")

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
