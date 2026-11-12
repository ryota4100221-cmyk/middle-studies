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

# ------------------------------------------------------------- LOOK（029 CADDY）
# 基準：Stelton の製品写真（低い日差しが脇の壁に斜めの光の面・鋼の胴に縦の帯・淡いオークの天板・灰褐色の壁）
LOOK = dict(
    aspect=(3, 4),
    lens=50,
    fstop=16.0,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=-0.22,
    bg=None,
)
FPS = 24

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


def sock(node, name, kind, out=False):
    """#103：Mix の同名ソケットは型で引く"""
    ss = node.outputs if out else node.inputs
    return next(s for s in ss if s.name == name and s.type == kind)


def lathe(name, prof, seg=192):
    """(r, z) の断面を z 軸まわりに回す。r=0 の点は極に潰す"""
    bm = bmesh.new()
    rings = []
    for k in range(seg):
        a = 2 * math.pi * k / seg
        ring = []
        for (r, z) in prof:
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    n = len(prof)
    for k in range(seg):
        A, B = rings[k], rings[(k + 1) % seg]
        for i in range(n - 1):
            vs = [A[i], B[i], B[i + 1], A[i + 1]]
            try:
                bm.faces.new(vs)
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


def plane(name, verts, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [tuple(range(len(verts)))]); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob


def flat(name, hexcol, rough=0.85, spec=0.2):
    m = principled(name, hex_to_linear(hexcol), rough=rough)
    m.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = spec
    return m


# ------------------------------------------------------------- 舞台：壁の角＋天板
# 天板の上面 z=0。奥の壁 y=WALL_Y、左に手前へ張り出す脇の壁（x=SIDE_X・+x を向く）
WALL_Y, SIDE_X = 0.95, -0.27
BACK_HEX, SIDE_HEX = "#655C56", "#B4A79C"
wall_m = flat("wall", BACK_HEX, 0.9)
side_m = flat("side", SIDE_HEX, 0.9)
back = plane("backwall", [(SIDE_X - 0.05, WALL_Y, -1.0), (3.0, WALL_Y, -1.0), (3.0, WALL_Y, 2.5), (SIDE_X - 0.05, WALL_Y, 2.5)], wall_m)
side = plane("sidewall", [(SIDE_X, -1.5, -1.0), (SIDE_X, WALL_Y, -1.0), (SIDE_X, WALL_Y, 2.5), (SIDE_X, -1.5, 2.5)], side_m)
# 部屋の残り（鋼に映る「後ろ」と右）。カメラには写らない位置
room_m = flat("room", "#857A72", 0.9)
plane("room_front", [(3.0, -2.4, -1.0), (SIDE_X, -2.4, -1.0), (SIDE_X, -2.4, 2.5), (3.0, -2.4, 2.5)], room_m)
plane("room_right", [(3.0, WALL_Y, -1.0), (3.0, -2.4, -1.0), (3.0, -2.4, 2.5), (3.0, WALL_Y, 2.5)], room_m)
plane("room_ceil", [(SIDE_X, -2.4, 2.5), (3.0, -2.4, 2.5), (3.0, WALL_Y, 2.5), (SIDE_X, WALL_Y, 2.5)], flat("ceil", "#8A7E76", 0.9))
plane("room_floor", [(SIDE_X, WALL_Y, -0.76), (3.0, WALL_Y, -0.76), (3.0, -2.4, -0.76), (SIDE_X, -2.4, -0.76)], flat("floor", "#6E6258", 0.8))
for _n in ("room_front", "room_right", "room_ceil", "room_floor"):
    bpy.data.objects[_n].visible_shadow = False
    bpy.data.objects[_n].visible_diffuse = False   # 照り返しで影が消える（round 14）


def oak_material():
    m = bpy.data.materials.new("oak"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.62
    p.inputs["Specular IOR Level"].default_value = 0.35
    tc = N.new("ShaderNodeTexCoord")
    oi = N.new("ShaderNodeObjectInfo")
    off = N.new("ShaderNodeVectorMath"); off.operation = 'SCALE'
    L.new(oi.outputs["Random"], off.inputs["Scale"])
    comb = N.new("ShaderNodeCombineXYZ")
    comb.inputs[0].default_value = 3.1; comb.inputs[1].default_value = 7.3; comb.inputs[2].default_value = 1.7
    L.new(comb.outputs[0], off.inputs[0])
    add = N.new("ShaderNodeVectorMath"); add.operation = 'ADD'
    L.new(tc.outputs["Object"], add.inputs[0]); L.new(off.outputs[0], add.inputs[1])
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (12.0, 160.0, 160.0)
    L.new(add.outputs[0], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 3.0
    L.new(mp.outputs[0], nz.inputs["Vector"])
    warp = N.new("ShaderNodeVectorMath"); warp.operation = 'MULTIPLY_ADD'
    L.new(nz.outputs["Color"], warp.inputs[0]); warp.inputs[1].default_value = (0.0, 2.5, 0.0)
    L.new(mp.outputs[0], warp.inputs[2])
    wave = N.new("ShaderNodeTexWave"); wave.wave_type = 'BANDS'; wave.bands_direction = 'Y'
    wave.wave_profile = 'SAW'
    wave.inputs["Scale"].default_value = 0.9
    wave.inputs["Distortion"].default_value = 8.0
    wave.inputs["Detail"].default_value = 6.0
    L.new(warp.outputs[0], wave.inputs["Vector"])
    grain = N.new("ShaderNodeTexNoise"); grain.inputs["Scale"].default_value = 1.0
    grain.inputs["Detail"].default_value = 2.0
    gmp = N.new("ShaderNodeMapping"); gmp.inputs["Scale"].default_value = (40.0, 700.0, 700.0)
    L.new(add.outputs[0], gmp.inputs["Vector"]); L.new(gmp.outputs[0], grain.inputs["Vector"])
    blot = N.new("ShaderNodeTexNoise"); blot.inputs["Scale"].default_value = 3.0
    L.new(add.outputs[0], blot.inputs["Vector"])
    s1 = N.new("ShaderNodeMath"); s1.operation = 'MULTIPLY_ADD'
    L.new(wave.outputs["Fac"], s1.inputs[0]); s1.inputs[1].default_value = 0.25
    L.new(grain.outputs["Fac"], s1.inputs[2])
    s2 = N.new("ShaderNodeMath"); s2.operation = 'MULTIPLY_ADD'
    L.new(blot.outputs["Fac"], s2.inputs[0]); s2.inputs[1].default_value = 0.4
    L.new(s1.outputs[0], s2.inputs[2])
    sc = N.new("ShaderNodeMapRange")
    sc.inputs["From Min"].default_value = 0.45; sc.inputs["From Max"].default_value = 1.35
    L.new(s2.outputs[0], sc.inputs["Value"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hex_to_linear(OAK_DARK)
    ramp.color_ramp.elements[1].color = hex_to_linear(OAK_LIGHT)
    L.new(sc.outputs[0], ramp.inputs["Fac"])
    # 導管：長手に引き伸ばした Voronoi の縁（#106）
    ln = N.new("ShaderNodeTexVoronoi"); ln.feature = 'DISTANCE_TO_EDGE'
    lmp = N.new("ShaderNodeMapping"); lmp.inputs["Scale"].default_value = (15.0, 400.0, 400.0)
    L.new(warp.outputs[0], lmp.inputs["Vector"]); L.new(lmp.outputs[0], ln.inputs["Vector"])
    lr = N.new("ShaderNodeMapRange")
    lr.inputs["From Min"].default_value = 0.04; lr.inputs["From Max"].default_value = 0.0
    lr.inputs["To Max"].default_value = 0.8
    L.new(ln.outputs["Distance"], lr.inputs["Value"])
    lmix = N.new("ShaderNodeMix"); lmix.data_type = 'RGBA'; lmix.blend_type = 'MULTIPLY'
    L.new(lr.outputs[0], lmix.inputs["Factor"])
    L.new(ramp.outputs["Color"], sock(lmix, "A", 'RGBA'))
    sock(lmix, "B", 'RGBA').default_value = hex_to_linear("#A08668")
    L.new(sock(lmix, "Result", 'RGBA', out=True), p.inputs["Base Color"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.06
    bump.inputs["Distance"].default_value = 0.0003
    L.new(s1.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


OAK_LIGHT, OAK_DARK = "#CDBDA0", "#8E7860"
oak = oak_material()
# 天板：板目は左右（x）に流れる。継ぎ目は手前と奥に2本
PLANKS = [(-1.6, -0.16), (-0.16, 0.24), (0.24, 0.62)]
TH = 0.035
tabletop = []
for i, (y0, y1) in enumerate(PLANKS):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.6, (y0 + y1) / 2, -TH / 2))
    pl = bpy.context.object; pl.name = "plank%d" % i
    pl.scale = (2.2, (y1 - y0) - 0.006, TH); bpy.ops.object.transform_apply(scale=True)
    bevel_obj(pl, 0.0025, segments=3)
    pl.data.materials.append(oak)
    tabletop.append(pl)

plane("under", [(-0.6, -1.7, -0.04), (1.8, -1.7, -0.04), (1.8, 0.7, -0.04), (-0.6, 0.7, -0.04)], flat("under", "#2A2420"))   # 継ぎ目の溝を暗く
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hex_to_linear("#9A8A7E")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.18

# ------------------------------------------------------------- 被写体：ステンレスの茶筒＋小さなタンブラー（自作の造形）
def steel_material(name, rough=0.09, aniso=0.0):
    m = principled(name, (0.55, 0.55, 0.56, 1.0), rough=rough, metal=1.0)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Anisotropic"].default_value = aniso
    if aniso > 0:
        tg = m.node_tree.nodes.new("ShaderNodeCombineXYZ"); tg.inputs[2].default_value = 1.0   # 縦の接線＝映り込みが縦に伸びる
        m.node_tree.links.new(tg.outputs[0], p.inputs["Tangent"])
        # 縦のヘアライン：縦に引き伸ばしたノイズで粗さと凹凸をわずかに揺らす
        nt = m.node_tree
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2600.0, 2600.0, 4.0)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 2.0
        nt.links.new(mp.outputs[0], nz.inputs["Vector"])
        rr = nt.nodes.new("ShaderNodeMapRange")
        rr.inputs["To Min"].default_value = rough * 0.7; rr.inputs["To Max"].default_value = rough * 1.5
        nt.links.new(nz.outputs["Fac"], rr.inputs["Value"]); nt.links.new(rr.outputs[0], p.inputs["Roughness"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.04; bp.inputs["Distance"].default_value = 0.00005
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


steel = steel_material("steel", 0.08, 0.7)
steel_in = steel_material("steel_in", 0.18)
black = principled("acetal", hex_to_linear("#141414"), rough=0.42)
black.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.4

CX, CY = 0.03, 0.08            # 茶筒の位置
R, HB = 0.046, 0.168           # 胴の半径・胴の高さ
LH, LR = 0.044, 0.0472         # 蓋の高さ・半径（胴より1.2mm大きい）
body = lathe("caddy_body", [(0.0, 0.0), (R - 0.0035, 0.0), (R - 0.0012, 0.0006), (R - 0.0001, 0.0024),
                             (R, 0.004), (R, HB - LH + 0.004), (R - 0.0015, HB - LH + 0.006), (0.0, HB - LH + 0.006)])
body.data.materials.append(steel)
lid_bot, lid_top = HB - LH, HB
lid = lathe("caddy_lid", [(R + 0.0002, lid_bot + 0.0015), (R + 0.0006, lid_bot + 0.0003), (R + 0.0014, lid_bot),
                           (LR - 0.0006, lid_bot + 0.0002), (LR, lid_bot + 0.001), (LR, lid_top - 0.0028),
                           (LR - 0.0006, lid_top - 0.0008), (LR - 0.0024, lid_top), (0.0, lid_top)])
lid.data.materials.append(steel)
knob = lathe("caddy_knob", [(0.0, 0.0), (0.0135, 0.0), (0.0142, 0.0007), (0.0142, 0.0068),
                             (0.0133, 0.0082), (0.0115, 0.0088), (0.0, 0.0088)])
knob.location = (0, 0, lid_top - 0.0002)
knob.parent = lid
knob.data.materials.append(black)
for o in (body, lid):
    o.location = (CX, CY, 0)
lid.location = (CX, CY, 0)

TX, TY = -0.125, 0.02        # タンブラー
TR, TH2 = 0.029, 0.058
tumbler = lathe("tumbler", [(0.0, 0.0), (TR - 0.003, 0.0), (TR - 0.0008, 0.0008), (TR, 0.003), (TR, TH2 - 0.0012),
                             (TR - 0.0005, TH2), (TR - 0.0012, TH2), (TR - 0.0016, TH2 - 0.0012),
                             (TR - 0.0016, 0.006), (TR - 0.004, 0.0045), (0.0, 0.0045)])
tumbler.data.materials.append(steel)
tumbler.location = (TX, TY, 0)

parts = [body, lid, knob, tumbler]

# ------------------------------------------------------------- 光
subj_col = bpy.data.collections.new("subj"); scene.collection.children.link(subj_col)
for o in parts:
    subj_col.objects.link(o)
side_col = bpy.data.collections.new("side_only"); scene.collection.children.link(side_col)
side_col.objects.link(side)

# ① 日差し：右手前の低い太陽。脇の壁だけに当て、窓枠の影で斜めの縁を切る
SUN_DIR = Vector((-1.0, 0.35, -0.42)).normalized()     # 光の進む向き
sun_d = bpy.data.lights.new("sun", 'SUN'); sun_d.energy = 23.0; sun_d.angle = math.radians(4.0)
sun_d.color = (1.0, 0.95, 0.9)
sun = bpy.data.objects.new("sun", sun_d); scene.collection.objects.link(sun)
sun.rotation_euler = SUN_DIR.to_track_quat('-Z', 'Y').to_euler()
sun.light_linking.receiver_collection = side_col

# 窓枠：壁から 0.35 離した不可視の板。光の面は「下が明るく・上は斜めに切れる・奥は縦に切れる」
blk_m = flat("blocker", "#000000")
def blocker(name, verts):
    ob = plane(name, verts, blk_m)
    ob.visible_camera = False; ob.visible_glossy = False; ob.visible_diffuse = False
    ob.visible_transmission = False; ob.visible_volume_scatter = False
    return ob
BX = SIDE_X + 0.35
# 斜めの上端：手前（y=-0.7）で高く、奥（y=0.3）で低い線より上を塞ぐ
blk_top = blocker("blk_top", [(BX, -1.4, 1.25), (BX, 1.2, 0.05), (BX, 1.2, 2.6), (BX, -1.4, 2.6)])
# 奥の縦の縁：y > 0.18 を塞ぐ
blk_back = blocker("blk_back", [(BX, 0.62, -1.0), (BX, 1.2, -1.0), (BX, 1.2, 2.6), (BX, 0.62, 2.6)])
block_col = bpy.data.collections.new("blockers"); scene.collection.children.link(block_col)
for o in (blk_top, blk_back):
    block_col.objects.link(o)

# ② 天井側の大きな柔光（被写体と天板を起こす）
key = area("key", (0.9, 0.0, 0.9), 0.4, 42, (1.0, 0.98, 0.95), target=(0.0, 0.1, 0.0))
# ③ 奥の壁を少し起こす（下ほど明るい＝基準の右下が明るい）
wash = area("wash", (0.45, 0.0, -0.35), 1.2, 30, (1.0, 0.92, 0.85), target=(0.3, WALL_Y, 0.25))
wall_col = bpy.data.collections.new("wall_only"); scene.collection.children.link(wall_col)
wall_col.objects.link(back)
wall_col.objects.link(side)
wash.light_linking.receiver_collection = wall_col
# 部屋の照り返しを切った分、奥の壁を正面上から柔らかく起こす（壁だけ）
wallfill = area("wallfill", (0.3, -0.9, 0.5), 2.0, 45, (1.0, 0.97, 0.94), target=(0.3, WALL_Y, 0.3))
wallfill.light_linking.receiver_collection = wall_col
# 窓枠の板は日差し以外の影を落とさない
cast_col = bpy.data.collections.new("casters"); scene.collection.children.link(cast_col)
for o in list(parts) + tabletop + [back, side]:
    cast_col.objects.link(o)
for L_ in (key, wash, wallfill):
    L_.light_linking.blocker_collection = cast_col
# キーは天板と被写体だけ（壁まで照らすと壁が 160 に上がった＝round 14）
key_col = bpy.data.collections.new("key_recv"); scene.collection.children.link(key_col)
for o in list(parts) + tabletop:
    key_col.objects.link(o)
key.light_linking.receiver_collection = key_col

# 鋼に映る縦の帯：右の白い板（カメラには写らない・鏡面にだけ映る）と、左手前の暗い板
def card(name, loc, w, h, strength, color=(1, 1, 1)):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = color + (1,)
    em.inputs["Strength"].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0])
    ob = plane(name, [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], m)
    ob.location = loc
    to = Vector((CX, CY, loc[2])) - Vector(loc)   # 板は垂直に立て、法線(−y)を被写体へ
    ob.rotation_euler = to.to_track_quat('-Y', 'Z').to_euler()
    ob.visible_camera = False; ob.visible_shadow = False; ob.visible_diffuse = False
    return ob

# 帯の板は茶筒を囲む輪の上に置く（遠いと胴の上だけに映り、横の境目ができる＝round 11）
CARD_SPECS = (("c_b1", -25, 0.10, 1.6), ("c_d1", 15, 0.06, 0.25), ("c_b2", 45, 0.12, 1.8),
              ("c_d2", -60, 0.10, 0.25), ("c_b3", 62, 0.06, 1.6), ("c_d3", 82, 0.14, 0.15), ("c_d4", 102, 0.20, 0.12), ("c_d5", 128, 0.20, 0.10), ("c_d6", 152, 0.20, 0.10))
_A0 = math.atan2(-0.68 - CY, -0.05 - CX)
cards = []
for nm, phi, w, st in CARD_SPECS:
    a = _A0 + math.radians(phi)   # xy の角度（atan2(y, x)）・φ>0 がカメラから見て右
    loc = (CX + 0.22 * math.cos(a), CY + 0.22 * math.sin(a), 0.375)
    cards.append(card(nm, loc, w, 0.75, st))


def place_cards(off_deg):
    """帯の板の輪を回す（光の走り）。off=0 が hero の並び"""
    for ob, (nm, phi, w, st) in zip(cards, CARD_SPECS):
        a = _A0 + math.radians(phi + off_deg)
        ob.location = (CX + 0.22 * math.cos(a), CY + 0.22 * math.sin(a), 0.375)
        to = Vector((CX, CY, 0.375)) - Vector(ob.location)
        ob.rotation_euler = to.to_track_quat('-Y', 'Z').to_euler()


# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam


# ------------------------------------------------------------- 動画＝プロダクトフィルム
def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


HERO_LOC = Vector((-0.05, -0.68, 0.24))
HERO_TGT = Vector((-0.03, 0.05, 0.24))
HERO_SHIFT = -0.08        # 縦線を垂直に保ったまま構図を下げる（あおり補正）
def surf_focus(loc, z=0.1):   # 円柱をなめるピントは「軸までの距離 − 半径」（#122）
    return (Vector((CX, CY, z)) - Vector(loc)).length - R


def macro_cam(t):    # 蓋の合わせ目を左から右へなめる
    a = math.radians(-118 + 34 * ease(t))
    tgt = Vector((CX + R * math.cos(a), CY + R * math.sin(a), HB - LH + 0.002))
    d = Vector((math.cos(a + math.radians(8)), math.sin(a + math.radians(8)), 0.0))
    loc = tgt + d * 0.36 + Vector((0, 0, 0.035))
    return loc, tgt, 120, 9.0, (tgt - loc).length


SHOTS = [
    dict(sec=3.0, name="光の走り",   # 中の寄り：帯の板の輪が回り、明暗の帯が胴を横切る
         cam=lambda t: (lerp((0.42, -0.36, 0.11), (0.38, -0.40, 0.12), ease(t)), Vector((-0.02, 0.22, 0.13)), 60, 8.0,
                        surf_focus(lerp((0.42, -0.36, 0.11), (0.38, -0.40, 0.12), ease(t))))),
    dict(sec=2.9, name="マクロ", cam=macro_cam),
    dict(sec=2.8, name="物の動き",   # 蓋が持ち上がる：左手前の低い位置から
         cam=lambda t: (lerp((-0.24, -0.42, 0.13), (-0.21, -0.40, 0.145), ease(t)), Vector((CX, CY, 0.15)), 85, 9.0,
                        surf_focus(lerp((-0.24, -0.42, 0.13), (-0.21, -0.40, 0.145), ease(t)), 0.15))),
    dict(sec=3.3, name="決め",       # 右奥から寄りながら入って hero で止まる
         cam=lambda t: (lerp(HERO_LOC + Vector((0.07, 0.12, 0.02)), HERO_LOC, ease_out(min(1.0, t / 0.62))), HERO_TGT,
                        LOOK["lens"], LOOK["fstop"], None, HERO_SHIFT)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    if i == 2:      # 蓋がすっと持ち上がる（少しだけ回る）
        u = ease(min(1.0, t / 0.85))
        lid.location = (CX, CY, 0.042 * u)
        lid.rotation_euler = (0, 0, math.radians(18 * u))
    else:
        lid.location = (CX, CY, 0)
        lid.rotation_euler = (0, 0, 0)


def light_path(i, t):
    place_cards(-60 * ease(t) + 30 if i == 0 else 0.0)
    for ob in cards:
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", frame=f)


for i, sh in enumerate(SHOTS):
    for k in range(sh["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh["frames"] - 1)
        T = (f - 1) / max(1, N_FRAMES - 1)
        r_ = sh["cam"](t)
        loc, tgt, lens, fstop, focus = r_[:5]
        cd.shift_y = r_[5] if len(r_) > 5 else 0.0
        cd.keyframe_insert("shift_y", frame=f)
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        cd.lens = lens
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus if focus else (Vector((CX - 0.05, CY - 0.06, 0.1)) - Vector(loc)).length
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
        sun.keyframe_insert("rotation_euler", frame=f)

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
