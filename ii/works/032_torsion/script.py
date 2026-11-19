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

# ------------------------------------------------------------- LOOK（032 TORSION）
LOOK = dict(
    aspect=(5, 4),
    lens=16,
    fstop=8.0,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=1.8,
    bg=(0.50, 0.49, 0.47),
)
FPS = 24
# 尺（N_FRAMES）と静止画のフレーム（STILL_FRAME）は、下の「動画」節の SHOTS から決まる

# 納品寸法：長辺で決める（hero 2560 / loop 1080）
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


# ------------------------------------------------------------- 舞台：白い長いギャラリー（床は磨いたコンクリート・天井は浅いヴォールト）
GL_X, GL_Y0, GL_Y1, GL_H = 6.8, -14.0, 52.0, 7.2

def node_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    return m, nt, p

def mesh_obj(name, verts, faces):
    me = bpy.data.meshes.new(name + "_me"); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob

# 床：磨いたコンクリート（淡い灰・むら・わずかな照り）
floor = mesh_obj("floor", [(-GL_X, GL_Y0, 0), (GL_X, GL_Y0, 0), (GL_X, GL_Y1, 0), (-GL_X, GL_Y1, 0)], [(0, 1, 2, 3)])
m, nt, p = node_mat("concrete")
tc = nt.nodes.new("ShaderNodeTexCoord")
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.6; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.62
nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
cr = nt.nodes.new("ShaderNodeValToRGB")
cr.color_ramp.elements[0].position = 0.2; cr.color_ramp.elements[0].color = hex_to_linear("#5A5956")
cr.color_ramp.elements[1].position = 0.8; cr.color_ramp.elements[1].color = hex_to_linear("#8E8D88")
nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
# 目地：x・y の 4.8m ごとに細い線（Brick テクスチャは石ごとに明度が変わって1枚だけ白く浮いた＝使わない）
sx_ = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sx_.inputs["Vector"])
def _joint(out):
    md = nt.nodes.new("ShaderNodeMath"); md.operation = 'PINGPONG'; md.inputs[1].default_value = 2.4
    nt.links.new(out, md.inputs[0])
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.012
    nt.links.new(md.outputs[0], lt.inputs[0]); return lt
jx, jy = _joint(sx_.outputs["X"]), _joint(sx_.outputs["Y"])
jm = nt.nodes.new("ShaderNodeMath"); jm.operation = 'MAXIMUM'
nt.links.new(jx.outputs[0], jm.inputs[0]); nt.links.new(jy.outputs[0], jm.inputs[1])
mj = nt.nodes.new("ShaderNodeMix"); mj.data_type = 'RGBA'; mj.blend_type = 'MULTIPLY'
mj.inputs["B"].default_value = (0.8, 0.8, 0.8, 1)
nt.links.new(jm.outputs[0], mj.inputs["Factor"]); nt.links.new(cr.outputs["Color"], mj.inputs["A"])
ns = nt.nodes.new("ShaderNodeTexNoise"); ns.inputs["Scale"].default_value = 9.0; ns.inputs["Detail"].default_value = 12; ns.inputs["Roughness"].default_value = 0.75
nt.links.new(tc.outputs["Object"], ns.inputs["Vector"])
sk = nt.nodes.new("ShaderNodeMapRange"); sk.inputs["From Min"].default_value = 0.35; sk.inputs["From Max"].default_value = 0.65
sk.inputs["To Min"].default_value = 0.78; sk.inputs["To Max"].default_value = 1.12
nt.links.new(ns.outputs["Fac"], sk.inputs["Value"])
mk = nt.nodes.new("ShaderNodeMix"); mk.data_type = 'RGBA'; mk.blend_type = 'MULTIPLY'; mk.inputs["Factor"].default_value = 1.0
nt.links.new(mj.outputs["Result"], mk.inputs["A"])
cv_ = nt.nodes.new("ShaderNodeCombineXYZ")
for k in ("X", "Y", "Z"): nt.links.new(sk.outputs["Result"], cv_.inputs[k])
nt.links.new(cv_.outputs["Vector"], mk.inputs["B"])
nd = nt.nodes.new("ShaderNodeTexNoise"); nd.inputs["Scale"].default_value = 26.0; nd.inputs["Detail"].default_value = 2
nt.links.new(tc.outputs["Object"], nd.inputs["Vector"])
dd = nt.nodes.new("ShaderNodeMapRange"); dd.inputs["From Min"].default_value = 0.70; dd.inputs["From Max"].default_value = 0.78
nt.links.new(nd.outputs["Fac"], dd.inputs["Value"])
md_ = nt.nodes.new("ShaderNodeMix"); md_.data_type = 'RGBA'; md_.blend_type = 'MULTIPLY'
md_.inputs["B"].default_value = (0.62, 0.62, 0.62, 1)
nt.links.new(dd.outputs["Result"], md_.inputs["Factor"]); nt.links.new(mk.outputs["Result"], md_.inputs["A"])
nt.links.new(md_.outputs["Result"], p.inputs["Base Color"])
rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.45; rr.inputs["To Max"].default_value = 0.7
nt.links.new(nz.outputs["Fac"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
floor.data.materials.append(m)

# 壁と天井（白だが 0.62 に抑える＝白飛びさせない・031 の教訓）
wall_mat = principled("wall", hex_to_linear("#D8D6D2"), rough=0.9)
for sx in (-1, 1):
    w = mesh_obj("wall%d" % sx, [(sx * GL_X, GL_Y0, 0), (sx * GL_X, GL_Y1, 0), (sx * GL_X, GL_Y1, GL_H), (sx * GL_X, GL_Y0, GL_H)], [(0, 1, 2, 3)])
    w.data.materials.append(wall_mat)
for (y, nm) in ((GL_Y1, "back"), (GL_Y0, "front")):
    w = mesh_obj(nm, [(-GL_X, y, 0), (GL_X, y, 0), (GL_X, y, GL_H + 2), (-GL_X, y, GL_H + 2)], [(0, 1, 2, 3)])
    w.data.materials.append(wall_mat)
# ヴォールト天井（x 方向の浅い弧）
cv, cf, NS = [], [], 24
for j, y in enumerate((GL_Y0, GL_Y1)):
    for i in range(NS + 1):
        a = -1 + 2 * i / NS
        cv.append((a * GL_X, y, GL_H + 1.6 * (1 - a * a)))
for i in range(NS):
    cf.append((i, i + 1, NS + 1 + i + 1, NS + 1 + i))
ceil = mesh_obj("ceiling", cv, cf); ceil.data.materials.append(wall_mat)
for pg in ceil.data.polygons:
    pg.use_smooth = True

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

# ------------------------------------------------------------- 被写体：ねじれる鋼板（耐候性鋼）
T_STEEL = 0.04

def corten_mat():
    m, nt, p = node_mat("corten")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.2, 2.2, 0.9)   # 縦に流れる錆の筋
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 3.0; n1.inputs["Detail"].default_value = 10; n1.inputs["Roughness"].default_value = 0.6
    nt.links.new(mp.outputs["Vector"], n1.inputs["Vector"])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.5; n2.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], n2.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMath"); mix.operation = 'MULTIPLY_ADD'; mix.inputs[1].default_value = 0.6
    nt.links.new(n1.outputs["Fac"], mix.inputs[0]); 
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 0.35
    nt.links.new(n2.outputs["Fac"], m2.inputs[0]); nt.links.new(m2.outputs[0], mix.inputs[2])
    cr = nt.nodes.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position = 0.20; el[0].color = hex_to_linear("#45290C")
    el[1].position = 0.85; el[1].color = hex_to_linear("#74491B")
    e = el.new(0.52); e.color = hex_to_linear("#5C3A12")
    nt.links.new(mix.outputs[0], cr.inputs["Fac"])
    gm = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(gm.outputs["Normal"], sep.inputs["Vector"])
    up = nt.nodes.new("ShaderNodeMath"); up.operation = 'GREATER_THAN'; up.inputs[1].default_value = 0.8
    nt.links.new(sep.outputs["Z"], up.inputs[0])
    mt = nt.nodes.new("ShaderNodeMix"); mt.data_type = 'RGBA'
    mt.inputs["B"].default_value = hex_to_linear("#7A6448")
    nt.links.new(up.outputs[0], mt.inputs["Factor"]); nt.links.new(cr.outputs["Color"], mt.inputs["A"])
    # 縦の継ぎ目：板の長さ方向の座標 seam_u（頂点属性）で細い暗い線
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "seam"
    wv = nt.nodes.new("ShaderNodeMath"); wv.operation = 'PINGPONG'; wv.inputs[1].default_value = 0.5
    nt.links.new(at.outputs["Fac"], wv.inputs[0])
    ln = nt.nodes.new("ShaderNodeMath"); ln.operation = 'LESS_THAN'; ln.inputs[1].default_value = 0.004
    nt.links.new(wv.outputs[0], ln.inputs[0])
    ms = nt.nodes.new("ShaderNodeMix"); ms.data_type = 'RGBA'; ms.blend_type = 'MULTIPLY'
    ms.inputs["B"].default_value = (0.70, 0.67, 0.64, 1)
    nt.links.new(ln.outputs[0], ms.inputs["Factor"]); nt.links.new(mt.outputs["Result"], ms.inputs["A"])
    mp2 = nt.nodes.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (16.0, 16.0, 0.25)
    nt.links.new(tc.outputs["Object"], mp2.inputs["Vector"])
    n4 = nt.nodes.new("ShaderNodeTexNoise"); n4.inputs["Scale"].default_value = 2.0; n4.inputs["Detail"].default_value = 3
    nt.links.new(mp2.outputs["Vector"], n4.inputs["Vector"])
    st = nt.nodes.new("ShaderNodeMapRange"); st.inputs["From Min"].default_value = 0.62; st.inputs["From Max"].default_value = 0.75
    nt.links.new(n4.outputs["Fac"], st.inputs["Value"])
    m4 = nt.nodes.new("ShaderNodeMix"); m4.data_type = 'RGBA'; m4.blend_type = 'MULTIPLY'
    m4.inputs["B"].default_value = (0.62, 0.58, 0.55, 1)
    nt.links.new(st.outputs["Result"], m4.inputs["Factor"]); nt.links.new(ms.outputs["Result"], m4.inputs["A"])
    nt.links.new(m4.outputs["Result"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.78
    n3 = nt.nodes.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 60; n3.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], n3.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; bp.inputs["Distance"].default_value = 0.004
    nt.links.new(n3.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m

CORTEN = corten_mat()

def ribbon(name, plan, height, lean, n=420, closed=False):
    """plan(u)->(x,y)・height(u)->m・lean(u)->rad（+ は右手側＝外へ倒れる）。閉じた多様体で作る（solidify を使わない＝#37）"""
    rings = []
    us = [i / n for i in range(n)] if closed else [i / (n - 1) for i in range(n)]
    for u in us:
        e = 1e-4
        p0 = Vector(plan(u) + (0,)); p1 = Vector(plan(u + e) + (0,)); pm = Vector(plan(u - e) + (0,))
        Tg = (p1 - pm).normalized()
        N = Vector((Tg.y, -Tg.x, 0)).normalized()
        th = lean(u)
        D = Vector((0, 0, 1)) * math.cos(th) + N * math.sin(th)
        O = Tg.cross(D).normalized() * (T_STEEL / 2)
        h = height(u)
        rings.append([p0 - O, p0 + D * h - O, p0 + D * h + O, p0 + O])
    verts = [tuple(v) for r in rings for v in r]
    faces = []
    m = len(rings)
    for i in range(m if closed else m - 1):
        a, b = i * 4, ((i + 1) % m) * 4
        for k in range(4):
            faces.append((a + k, a + (k + 1) % 4, b + (k + 1) % 4, b + k))
    if not closed:
        faces.append((3, 2, 1, 0)); L = (m - 1) * 4; faces.append((L, L + 1, L + 2, L + 3))
    ob = mesh_obj(name, verts, faces)
    # 継ぎ目用：弧長(m)/2.6 を頂点属性に（シェーダで小数部が 0 の所に線）
    acc, Ls = 0.0, [0.0]
    for i in range(1, m):
        acc += (rings[i][0] - rings[i - 1][0]).length; Ls.append(acc)
    att = ob.data.attributes.new("seam", 'FLOAT', 'POINT')
    for i in range(m):
        for k in range(4):
            att.data[i * 4 + k].value = Ls[i] / 3.4 + 0.37
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()
    bevel_obj(ob, 0.012, segments=2, clamp=True, angle=40)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
    ob.select_set(False)
    ob.data.materials.append(CORTEN)
    return ob

TAU = 2 * math.pi
# ① 手前の主役：外から内へ1.3周巻き込む渦・倒れが周に沿って内外へねじれる
SP = 1.62 * TAU
def sp_plan(u, c=(0.3, 0.2), R0=4.3):
    ph = u * SP + 0.9
    r = R0 * (1 + 0.13 * math.cos(2 * ph + 0.5)) * (1 - 0.47 * u)
    return (c[0] + r * math.cos(ph), c[1] + r * math.sin(ph) * 0.92)
main = ribbon("spiral", sp_plan, lambda u: 3.2 + 0.3 * math.sin(u * 5.0), lambda u: 0.17 * math.sin(u * SP * 1.0 + 0.4), n=600)

# ② 左奥：開いた漏斗＝外へ倒れながら楕円の向きが回る閉じた輪
def cone_plan(u):
    ph = u * TAU
    return (-3.0 + 1.9 * math.cos(ph), 6.9 + 1.5 * math.sin(ph))
cone = ribbon("funnel", cone_plan, lambda u: 2.9, lambda u: 0.20 + 0.13 * math.sin(2 * u * TAU + 1.0), n=360, closed=True)

# ③ 右奥：並んで蛇行する2枚
def wave(off):
    return lambda u: (2.6 + off + 1.0 * math.sin((u - 0.5) * 5.2), 5.6 + 8.0 * u)
w1 = ribbon("wave_a", wave(0.0), lambda u: 2.9 - 0.3 * u, lambda u: 0.12 * math.sin(u * 6.0), n=360)
w2 = ribbon("wave_b", wave(0.95), lambda u: 2.7 - 0.3 * u, lambda u: 0.12 * math.sin(u * 6.0 + 0.6), n=360)

# ④ 最奥：小さな渦
far = ribbon("spiral_far", lambda u: sp_plan(u, c=(-0.4, 16.5), R0=2.2), lambda u: 2.4, lambda u: -0.12 * math.sin(u * SP * 0.8), n=420)

far2 = ribbon("funnel_far", lambda u: (2.2 + 1.2 * math.cos(u * TAU), 29.0 + 0.9 * math.sin(u * TAU)), lambda u: 2.2, lambda u: -0.18 + 0.1 * math.sin(2 * u * TAU), n=300, closed=True)
parts = [main, cone, w1, w2, far, far2]

# 天井際のスポットのレールと器具（尺度を与える）
rail_mat = principled("rail", hex_to_linear("#2A2A2A"), rough=0.4, metal=0.6)
fix_mat = principled("fixture", hex_to_linear("#E9E8E6"), rough=0.35)
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx * (GL_X - 1.1), (GL_Y0 + GL_Y1) / 2, GL_H + 0.55))
    r = bpy.context.object; r.scale = (0.05, (GL_Y1 - GL_Y0) / 2, 0.04); r.data.materials.append(rail_mat)
    for j in range(int((GL_Y1 - GL_Y0) / 2.2)):
        y = GL_Y0 + 1.0 + j * 2.2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.24, location=(sx * (GL_X - 1.1), y, GL_H + 0.36))
        c = bpy.context.object; c.rotation_euler = (math.radians(-35), sx * math.radians(25), 0)
        c.data.materials.append(fix_mat)

# ------------------------------------------------------------- 光：天井の長い天窓＋走る光（3カット目だけ）
sky = area("sky", (0.8, 8, GL_H + 1.4), 5.0, 7000, (1.0, 0.98, 0.95), target=(0, 8, 0))
sky.data.size_y = 36.0
sky2 = area("sky_side", (-4.5, 6, GL_H + 0.5), 2.0, 2200, (0.97, 0.98, 1.0), target=(-1, 6, 0))
sky2.data.size_y = 30.0
spot_d = bpy.data.lights.new("run", 'SPOT'); spot_d.energy = 0; spot_d.spot_size = math.radians(12); spot_d.spot_blend = 0.6
spot_d.shadow_soft_size = 0.3; spot_d.color = (1.0, 0.93, 0.82)
run = bpy.data.objects.new("run", spot_d); scene.collection.objects.link(run)
run.location = (5.5, 2.0, 6.5)
for sx in (-1, 1):   # 壁をかすめる光：壁際の天井から真下へ（round 12・斜めの洗い光は床に四角を落とした）
    ww = area("graze%d" % sx, (sx * (GL_X - 0.35), 14, GL_H + 0.3), 0.5, 6000, (1.0, 0.98, 0.95), target=(sx * (GL_X - 0.35), 14, 0))
    ww.data.size_y = 64.0
    ww.data.spread = math.radians(70)
up = area("uplight", (0, 18, GL_H + 0.2), 4.0, 1800, (1.0, 0.98, 0.96), target=(0, 18, GL_H + 5))   # 天井を下から照らす間接
up.data.size_y = 64.0
area("endwash", (0, GL_Y1 - 6, 5.0), 6.0, 1500, (1.0, 0.98, 0.95), target=(0, GL_Y1, 4.0))
key_light = None

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
cd.clip_end = 200
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

# 各カット：sec（秒）／cam(t)→(カメラ位置, 注視点, レンズmm, f値, ピント距離 or None=注視点まで)
#           ／pose(t)→物の動き（任意）。t はそのカットの中で 0→1。
# 🔴 下は動作確認用の仮置き。**毎回、基準と題材に合わせて組み直す**。
HERO_LOC, HERO_TGT = Vector((0.4, -3.3, 7.3)), Vector((0.0, 5.6, 0.0))
SHOTS = [
    dict(sec=3.0,   # スライド：渦の外・左の壁際の低い目線で、外面に沿って奥の漏斗へ滑る
         cam=lambda t: (lerp((-5.7, -3.6, 1.3), (-5.5, -0.8, 1.5), ease(t)), lerp((-1.6, 4.0, 1.6), (-2.2, 6.0, 1.5), ease(t)),
                        24, 5.6, None)),
    dict(sec=2.6,   # マクロ：手前の巻きの上端の小口を、高い所から 135mm で横へなめる（下に渦の中の床がぼける）
         cam=lambda t: (lerp((0.0, -6.0, 6.2), (1.4, -6.0, 6.2), ease(t)), lerp((0.15, -2.15, 3.45), (1.6, -2.05, 3.42), ease(t)),
                        135, 2.8, None)),
    dict(sec=2.6,   # 光の走り：内側の巻きの上から漏斗の全体と床を見下ろし、斜めの光が面を横切る
         cam=lambda t: (lerp((0.4, 1.6, 5.2), (0.1, 1.9, 5.1), ease(t)), Vector((-2.6, 7.0, 1.2)),
                        32, 6.0, None)),
    dict(sec=3.0,   # 決め：高く引きながら入って hero の構図で止まる
         cam=lambda t: (lerp(HERO_LOC + Vector((-1.6, 3.0, -2.2)), HERO_LOC, ease_out(min(1.0, t / 0.6))),
                        lerp(HERO_TGT + Vector((-0.8, 1.0, 0.4)), HERO_TGT, ease_out(min(1.0, t / 0.6))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    """物は動かさない（彫刻）。動きはカメラと光で見せる"""
    pass


def light_path(i, t):
    if i == 2:
        spot_d.energy = 40000 * math.sin(math.pi * min(1.0, t * 1.1)) ** 0.5
        run.location = lerp((2.0, 4.0, 6.2), (2.0, 12.5, 6.2), ease(t))
    else:
        spot_d.energy = 0
        run.location = (2.0, 4.0, 6.2)
    run.rotation_euler = (Vector((-3.3, 6.9 + (run.location.y - 6.9) * 0.6, 1.2)) - run.location).to_track_quat('-Z', 'Y').to_euler()
    for pth in ("location", "rotation_euler"):
        run.keyframe_insert(pth, frame=f)
    spot_d.keyframe_insert("energy", frame=f)


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
        if key_light:
            key_light.keyframe_insert("location", frame=f)

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
