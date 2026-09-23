# =============================================================
# MIDDLE STUDIES II 006 FULCRUM（2026-09-23）— 雛形から
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

# ------------------------------------------------------------- LOOK（006 FULCRUM）
LOOK = dict(
    aspect=(5, 6),
    lens=58,
    fstop=9.0,
    view="AgX",
    look="AgX - Base Contrast",
    exposure=-0.35,
    bg=None,
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


# ------------------------------------------------------------- 素材の道具
def sock(node, name, kind, out=False):
    """🔴 Mix ノードは同名ソケットを型違いで持つ＝型で引く（PITFALLS [II] 103）"""
    ss = node.outputs if out else node.inputs
    return next(s for s in ss if s.name == name and s.type == kind)


def setp(m, **kw):
    p = m.node_tree.nodes["Principled BSDF"]
    for k, v in kw.items():
        p.inputs[k.replace("_", " ")].default_value = v
    return m


def chips(nt, vec, layers, base_hex, gap=0.06):
    """多角形の欠片を散らす：Voronoi のセル＝欠片。縁までの距離で目地を抜き、セルの乱数で間引く。
    layers＝[(scale, hex, 残す割合)]。戻り値＝Base Color に繋ぐ出力"""
    N, L = nt.nodes, nt.links
    cur = None
    for (sc, hx, keep_ratio) in layers:
        vc = N.new("ShaderNodeTexVoronoi"); vc.feature = 'F1'; vc.inputs["Scale"].default_value = sc
        ve = N.new("ShaderNodeTexVoronoi"); ve.feature = 'DISTANCE_TO_EDGE'; ve.inputs["Scale"].default_value = sc
        for v in (vc, ve):
            v.inputs["Randomness"].default_value = 1.0
            L.new(vec, v.inputs["Vector"])
        sep = N.new("ShaderNodeSeparateColor"); L.new(vc.outputs["Color"], sep.inputs["Color"])
        keep = N.new("ShaderNodeMath"); keep.operation = 'LESS_THAN'; keep.inputs[1].default_value = keep_ratio
        L.new(sep.outputs["Red"], keep.inputs[0])
        # 欠片ごとに目地の太さをばらす＝大きさがばらける
        g = N.new("ShaderNodeMath"); g.operation = 'MULTIPLY_ADD'
        L.new(sep.outputs["Green"], g.inputs[0]); g.inputs[1].default_value = gap * 3.0; g.inputs[2].default_value = gap
        inside = N.new("ShaderNodeMath"); inside.operation = 'GREATER_THAN'
        L.new(ve.outputs["Distance"], inside.inputs[0]); L.new(g.outputs[0], inside.inputs[1])
        fac = N.new("ShaderNodeMath"); fac.operation = 'MULTIPLY'
        L.new(keep.outputs[0], fac.inputs[0]); L.new(inside.outputs[0], fac.inputs[1])
        mx = N.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        L.new(fac.outputs[0], mx.inputs["Factor"])
        if cur is None:
            sock(mx, "A", 'RGBA').default_value = hex_to_linear(base_hex)
        else:
            L.new(cur, sock(mx, "A", 'RGBA'))
        sock(mx, "B", 'RGBA').default_value = hex_to_linear(hx)
        cur = sock(mx, "Result", 'RGBA', out=True)
    return cur


def terrazzo(name):
    """生成りの地に、大小の砕石の欠片（灰・煉瓦・墨・砂）"""
    m = principled(name, hex_to_linear("#E8DCC6"), rough=0.42)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    out = chips(nt, tc.outputs["Object"],
                [(36.0, "#9A958C", 0.22), (54.0, "#B0674E", 0.16), (84.0, "#3A3833", 0.18), (128.0, "#B9A88E", 0.30)],
                "#E8DCC6", gap=0.07)
    nt.links.new(out, nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def prism(name, poly2d, depth, axis='y'):
    """xz 平面の多角形を y 方向に押し出す（axis='z' なら xy 平面を z へ）"""
    bm = bmesh.new()
    vs = []
    for (u, v) in poly2d:
        vs.append(bm.verts.new((u, -depth / 2, v) if axis == 'y' else (u, v, 0)))
    f = bm.faces.new(vs)
    bm.normal_update()
    vec = (0, depth, 0) if axis == 'y' else (0, 0, depth)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)], vec=vec)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


def sphere(name, r, loc, seg=128):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    ob = bpy.context.object; ob.name = name
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def box(name, sx, sy, sz, loc):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    ob.location = loc
    return ob

# ------------------------------------------------------------- 舞台：オリーブの無限背景紙
BG_HEX = "#3E4333"
R, W, D, H = 1.6, 16.0, 7.0, 7.0
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 16 * math.pi / 2 for i in range(1, 17)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + 1.6, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
sweep.data.materials.append(principled("paper", hex_to_linear(BG_HEX), rough=0.75))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hex_to_linear("#383C2E")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12

# ------------------------------------------------------------- 被写体：支点に渡した一枚の板と、その上下の物
APEX = Vector((-0.02, 0.0, 0.34))       # 支点の頂
HERO_TILT = math.radians(2.2)           # hero で板が左へ傾いている角（完全な水平にしない）

# 支点：テラゾーの三角柱
wedge = prism("wedge", [(-0.20, 0.0), (0.20, 0.0), (0.0, 0.34)], 0.24)
wedge.location = (APEX.x, 0.0, 0.0)
bevel_obj(wedge, 0.012, segments=4)
wedge.data.materials.append(terrazzo("terrazzo"))

# 板：すりガラス
plank = box("plank", 1.45, 0.17, 0.034, (0, 0, 0))
bevel_obj(plank, 0.005, segments=4)
m_frost = principled("frost", (0.94, 0.95, 0.94, 1), rough=0.20, trans=1.0, ior=1.5)
plank.data.materials.append(m_frost)

# 左：サテンの藤紫の大球（板の上）
ball = sphere("ball", 0.30, (0, 0, 0))
m_ball = principled("satin", hex_to_linear("#6A4A6E"), rough=0.60, metal=0.35)
setp(m_ball, Specular_Tint=(1.0, 0.55, 0.42, 1.0))
ball.data.materials.append(m_ball)

# 右端：翡翠の六角の塊＋金の小球
hexp = [(0.075 * math.cos(math.radians(a + 8)) * (1.0 if k % 2 else 0.9),
         0.075 * math.sin(math.radians(a + 8)) * (1.0 if k % 2 else 0.9)) for k, a in enumerate(range(0, 360, 60))]
hexp = [(1.45 * u, 1.45 * v) for (u, v) in hexp]
jade = prism("jade", hexp, 0.20, axis='z')
bevel_obj(jade, 0.008, segments=4)
m_jade = principled("jade", hex_to_linear("#3C5A40"), rough=0.32)
setp(m_jade, Subsurface_Weight=0.45, Subsurface_Scale=0.008)
m_jade.node_tree.nodes["Principled BSDF"].inputs["Subsurface Radius"].default_value = (0.5, 1.0, 0.6)
# 翡翠の中の欠片（面に沈んだ明るい斑）と、面の微かな凹凸
_N, _L = m_jade.node_tree.nodes, m_jade.node_tree.links
_p = _N["Principled BSDF"]; _tc = _N.new("ShaderNodeTexCoord")
_L.new(chips(m_jade.node_tree, _tc.outputs["Object"], [(150.0, "#324E38", 0.16), (260.0, "#3A5842", 0.14)], "#223C28", gap=0.08),
       _p.inputs["Base Color"])
_nz = _N.new("ShaderNodeTexNoise"); _nz.inputs["Scale"].default_value = 30.0
_L.new(_tc.outputs["Object"], _nz.inputs["Vector"])
_bp = _N.new("ShaderNodeBump"); _bp.inputs["Strength"].default_value = 0.08
_L.new(_nz.outputs["Fac"], _bp.inputs["Height"]); _L.new(_bp.outputs["Normal"], _p.inputs["Normal"])
jade.data.materials.append(m_jade)

gold = sphere("gold", 0.052, (0, 0, 0), seg=96)
gold.data.materials.append(principled("gold", hex_to_linear("#E9BE78"), rough=0.16, metal=1.0))

# 奥右：煙色の鏡の破片（立てた厚板）
shard = prism("shard", [(-0.14, 0.0), (0.13, 0.0), (0.17, 0.62), (0.10, 1.22), (-0.09, 1.14), (-0.16, 0.46)], 0.035)
shard.location = (0.52, 0.22, 0.0)
shard.rotation_euler = (0, math.radians(-4), math.radians(-18))
bevel_obj(shard, 0.006, segments=3)
shard.data.materials.append(principled("smoke", hex_to_linear("#9A948A"), rough=0.20, metal=1.0))

# 手前左：透明ガラスの立方体
# 薄板のガラスの箱（天が開いた器）：外箱から内箱を Boolean で抜く
cube = box("cube", 0.24, 0.24, 0.24, (-0.55, -0.36, 0.12))
_inner = box("cube_in", 0.23, 0.23, 0.26, (-0.55, -0.36, 0.125 + 0.02))
_bo = cube.modifiers.new("hollow", 'BOOLEAN'); _bo.operation = 'DIFFERENCE'; _bo.object = _inner; _bo.solver = 'EXACT'
bpy.context.view_layer.objects.active = cube
bpy.ops.object.modifier_apply(modifier="hollow")
bpy.data.objects.remove(_inner, do_unlink=True)
cube.data.materials.clear()   # 🔴 Boolean が空スロットを足す（PITFALLS [II] 106）
cube.rotation_euler = (0, 0, math.radians(24))
bevel_obj(cube, 0.0015, segments=2)
cube.data.materials.append(principled("clear", (0.97, 0.98, 0.97, 1), rough=0.02, trans=1.0, ior=1.5))

# 床：ラベンダーの陶球・真珠
lav = sphere("lav", 0.062, (0.30, -0.36, 0.062), seg=96)
lav.data.materials.append(principled("lav", hex_to_linear("#34306A"), rough=0.12, coat=1.0))
pearl = sphere("pearl", 0.040, (0.40, -0.28, 0.040), seg=96)
m_pearl = principled("pearl", hex_to_linear("#EEE6E2"), rough=0.14)
setp(m_pearl, Thin_Film_Thickness=620.0, Thin_Film_IOR=1.6, Coat_Weight=0.4)
pearl.data.materials.append(m_pearl)

# 奥左：真鍮の細い輪（立てた円）
bpy.ops.mesh.primitive_torus_add(major_radius=0.52, minor_radius=0.0065, location=(-0.30, 0.42, 0.52),
                                 rotation=(math.radians(90), 0, math.radians(12)),
                                 major_segments=192, minor_segments=16)
hoop = bpy.context.object; hoop.name = "hoop"
for p in hoop.data.polygons:
    p.use_smooth = True
hoop.data.materials.append(principled("brass", hex_to_linear("#C8A865"), rough=0.22, metal=1.0))

# 奥中央：生成りの陶の柱（細い縦材）
# 縦の溝（フルート）：断面の半径を 24 山で波打たせた押し出し
FL, RC = 24, 0.078
flute = []
for k in range(FL * 8):
    a = 2 * math.pi * k / (FL * 8)
    r = RC - 0.0055 * (0.5 + 0.5 * math.cos(FL * a)) ** 0.6
    flute.append((r * math.cos(a), r * math.sin(a)))
col = prism("column", flute, 1.0, axis='z')
col.location = (-0.08, 0.40, 0.0)
bevel_obj(col, 0.010, segments=4, angle=60)
col.data.materials.append(principled("blush", hex_to_linear("#CDB3A6"), rough=0.40))

def shadow_clear(m, amount=0.6):
    """ガラスの影を薄く：影の光線にだけ Transparent を混ぜる（PITFALLS [II] 102）"""
    nt = m.node_tree; N, L = nt.nodes, nt.links
    out = N["Material Output"]; p = N["Principled BSDF"]
    lp = N.new("ShaderNodeLightPath"); tr = N.new("ShaderNodeBsdfTransparent")
    mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = amount
    L.new(lp.outputs["Is Shadow Ray"], mul.inputs[0])
    mx = N.new("ShaderNodeMixShader")
    L.new(mul.outputs[0], mx.inputs[0]); L.new(p.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])


shadow_clear(cube.data.materials[0], 0.7)
shadow_clear(m_frost, 0.45)

parts = [wedge, plank, ball, jade, gold, shard, cube, lav, pearl, hoop, col]

# 板に載っている物の、板の座標での置き場（x＝板に沿う距離、z＝板の上面からの高さ）
PT = 0.017   # 板の厚みの半分
ON_PLANK = {
    plank: Vector((0.0, 0.0, 0.0)),
    ball:  Vector((-0.36, 0.0, PT + 0.30)),
    jade:  Vector((0.56, 0.0, PT)),          # jade の原点は底面
    gold:  Vector((0.56, 0.0, PT + 0.20 + 0.052)),
}


def set_tilt(theta):
    """theta＞0 で左が下がる。板は支点の頂で y 軸まわりに回る"""
    from mathutils import Matrix
    Rm = Matrix.Rotation(-theta, 3, 'Y') if False else Matrix.Rotation(theta, 3, 'Y')
    for ob, off in ON_PLANK.items():
        o = Vector(off) + Vector((0, 0, PT))    # 板の中心は頂より PT 上
        ob.location = APEX + Rm @ o
        ob.rotation_euler = (0, theta, 0)


set_tilt(HERO_TILT)

# ------------------------------------------------------------- 光
# キー：左手前の大きな柔らかい面。壁の左下を琥珀に起こす灯り。右から弱い返し
key = area("key", (-2.7, -0.7, 1.9), 1.8, 240, (1.0, 0.72, 0.56), target=(0, 0, 0.45))
wd = bpy.data.lights.new("wash", 'SPOT'); wd.energy = 4400; wd.color = (1.0, 0.66, 0.34)
wd.spot_size = math.radians(62); wd.spot_blend = 1.0; wd.shadow_soft_size = 0.6
wash = bpy.data.objects.new("wash", wd); scene.collection.objects.link(wash)
wash.location = (-0.3, -1.8, 2.6)
wash.rotation_euler = (Vector((-1.8, 1.8, 0.35)) - wash.location).to_track_quat('-Z', 'Y').to_euler()
# 壁の琥珀は壁だけに（ライトリンク：受け手を背景紙だけにする）
wall_only = bpy.data.collections.new("wall_only"); wall_only.objects.link(sweep)
wash.light_linking.receiver_collection = wall_only
# 壁の上半分を暗いオリーブに保つ、ごく弱い面の起こし（壁だけ）
wfill = area("wfill", (0.2, -3.0, 3.0), 5.0, 230, (0.92, 0.96, 0.86), target=(0.0, 1.8, 1.6))
wfill.light_linking.receiver_collection = wall_only
fill = area("fill", (2.8, -2.0, 1.2), 2.0, 60, (0.85, 0.92, 1.0), target=(0, 0, 0.45))
top = area("top", (0.3, -0.6, 3.2), 1.0, 40, (1.0, 0.98, 0.94), target=(0, 0, 0.4))
# 大球の照りを桃〜橙に：大球だけに当たる色の面（ライトリンク）
# キーは大球以外に、大球には同じ位置から桃橙の面を当てる（照りの色だけを替える）
glow = area("glow", (-2.7, -0.7, 1.9), 1.6, 560, (1.0, 0.46, 0.26), target=(0, 0, 0.45))
ball_only = bpy.data.collections.new("ball_only"); ball_only.objects.link(ball)
glow.light_linking.receiver_collection = ball_only
# 大球の陰の側を藤色で持ち上げる（基準の陰は暗く沈まず、くすんだモーヴ）
bfill = area("bfill", (1.6, -2.4, 1.2), 3.0, 80, (0.92, 0.84, 0.94), target=(-0.40, 0, 0.65))
bfill.data.specular_factor = 0.0   # 陰を起こすだけ。照りの2つ目を作らない
bfill.light_linking.receiver_collection = ball_only
not_ball = bpy.data.collections.new("not_ball")
for _o in [o for o in parts if o is not ball] + [sweep]:
    not_ball.objects.link(_o)
key.light_linking.receiver_collection = not_ball
top.light_linking.receiver_collection = not_ball
fill.light_linking.receiver_collection = not_ball   # 右の返しの照りが大球の中央に2つ目の照りを作っていた
for L_ in (key, fill, top):
    L_.data.cycles.max_bounces = 16
key.data.spread = math.radians(70)
top.data.spread = math.radians(50)

# ------------------------------------------------------------- カメラ
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

# 各カット：sec（秒）／cam(t)→(カメラ位置, 注視点, レンズmm, f値, ピント距離 or None=注視点まで)
#           ／pose(t)→物の動き（任意）。t はそのカットの中で 0→1。
# ------------------------------------------------------------- フィルム（006）
# 板が揺れて、静まる。最後に hero で釣り合って止まる
HERO_CAM = Vector((0.16, -4.45, 1.06))
HERO_TGT = Vector((0.08, 0.0, 0.64))
TGT = HERO_TGT
SHOTS = [
    dict(sec=3.0,   # マクロ：金の小球と翡翠の縁をなめる（ピント送り）
         cam=lambda t: (lerp((1.05, -1.25, 0.72), (0.80, -1.30, 0.62), ease(t)), Vector((0.62, 0, 0.52)),
                        120, 2.8, 1.40 + 0.12 * ease(t))),
    dict(sec=3.0,   # 回り込み（低い広角）：床すれすれから支点を見上げ、揺れる板を壁の前に抜く
         cam=lambda t: (orbit(Vector((APEX.x, 0, 0)), 1.55, 0.16, 34 - 24 * ease(t)), Vector((APEX.x + 0.05, 0, 0.42)),
                        32, 5.6, None)),
    dict(sec=2.5,   # スライド：大球・柱・輪の前を横に滑る（中）
         cam=lambda t: (lerp((-1.05, -2.0, 0.95), (-0.15, -2.1, 0.80), ease(t)), lerp((-0.55, 0.1, 0.62), (-0.10, 0.2, 0.60), ease(t)),
                        75, 4.5, None)),
    dict(sec=3.0,   # 決め：引きながら入り hero で止まる
         cam=lambda t: (lerp((0.55, -3.8, 0.75), HERO_CAM, ease_out(min(1.0, t / 0.6))),
                        lerp((0.05, 0.0, 0.45), HERO_TGT, ease_out(min(1.0, t / 0.6))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES
SETTLE = (shot_start[3] + round(SHOTS[3]["frames"] * 0.6) - 1) / (N_FRAMES - 1)   # この T で板が静まる


def tilt_at(T):
    """減衰する揺れ。SETTLE で hero の角にぴたりと止まる（包絡を (1-u)^2 で 0 に落とす）"""
    if T >= SETTLE:
        return HERO_TILT
    u = T / SETTLE
    env = (1 - u) ** 2
    return HERO_TILT + math.radians(7.0) * env * math.cos(2 * math.pi * 2.6 * u)


def pose(i, t, T):
    set_tilt(tilt_at(T))


key_light = None


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
