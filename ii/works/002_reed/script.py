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

# ------------------------------------------------------------- LOOK（毎回決める）
LOOK = dict(
    aspect=(4, 5),
    lens=50,                  # mm（実寸 m で組む＝#101）
    fstop=11.0,
    view=os.environ.get("II_VIEW", "Khronos PBR Neutral"),
    look=os.environ.get("II_LOOKNAME", "None"),
    exposure=float(os.environ.get("II_EXPO", "-0.2")),
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


# ------------------------------------------------------------- 舞台：奥の壁 → 上段 → 下段（実寸 m）
CAUSTICS = os.environ.get("II_CAUSTICS", "1") == "1"
STEP_H = 0.03                      # 上段の高さ
STEP_FRONT = -0.02                  # 上段の前縁の y
WALL_Y = 0.34                       # 奥の壁の y
C_WALL = hex_to_linear(os.environ.get("II_WALL", "#3C70C4"))
C_STEP = hex_to_linear(os.environ.get("II_STEP", "#C4C9DA"))
C_FLOOR = hex_to_linear(os.environ.get("II_FLOOR", "#CDD1DE"))


def box(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0):
    me = bpy.data.meshes.new(name)
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me.from_pydata(v, [], f); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    if bevel:
        bevel_obj(ob, bevel, segments=4)
    ob.data.materials.append(mat)
    return ob


m_wall = principled("wall", C_WALL, rough=0.7)
_nt = m_wall.node_tree
_tc = _nt.nodes.new("ShaderNodeTexCoord"); _sep = _nt.nodes.new("ShaderNodeSeparateXYZ")
_ramp = _nt.nodes.new("ShaderNodeValToRGB")
_nt.links.new(_tc.outputs["Object"], _sep.inputs[0]); _nt.links.new(_sep.outputs["Z"], _ramp.inputs["Fac"])
_ramp.color_ramp.elements[0].position = 0.0
_ramp.color_ramp.elements[0].color = C_WALL                       # 段差の際＝深い青
_ramp.color_ramp.elements[1].position = float(os.environ.get("II_WALL_TOP", "0.6"))
_ramp.color_ramp.elements[1].color = hex_to_linear(os.environ.get("II_WALL_HI", "#AEBCDC"))  # 上＝白く霞む
_nt.links.new(_ramp.outputs["Color"], _nt.nodes["Principled BSDF"].inputs["Base Color"])
m_step = principled("step", C_STEP, rough=0.42)
m_floor = principled("floor", C_FLOOR, rough=0.42)
floor = box("floor", -3, 3, -3, WALL_Y, -0.2, 0.0, m_floor)
step = box("step", -3, 3, STEP_FRONT, WALL_Y, 0.0, STEP_H, m_step, bevel=0.0015)
wall = box("wall", -3, 3, WALL_Y, WALL_Y + 0.1, -0.2, 2.0, m_wall)
# step の影は残す：切ると粒の影が段を素通りして下段に浮く（round 12）
wall.visible_shadow = False          # 🔴 奥上からの太陽を壁が全部さえぎる（II 002 round 1 で全面が日陰になった）
for o in (floor, step, wall):
    o.cycles.is_caustics_receiver = CAUSTICS

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
bgn = world.node_tree.nodes["Background"]
bgn.inputs["Color"].default_value = hex_to_linear(os.environ.get("II_SKY", "#BCC8DE"))
bgn.inputs["Strength"].default_value = float(os.environ.get("II_WORLD", "0.9"))

# ------------------------------------------------------------- 被写体：S字に並ぶガラスの葦（カプセル）
def capsule(name, r, h, seg=48, rings=10):
    """底 z=0 から頂 z=h までのカプセル（閉じた多様体・両端は半球）"""
    prof = []
    for i in range(rings + 1):                       # 下の半球
        a = -math.pi / 2 + (math.pi / 2) * i / rings
        prof.append((r * math.cos(a), r + r * math.sin(a)))
    for i in range(rings + 1):                       # 上の半球
        a = (math.pi / 2) * i / rings
        prof.append((r * math.cos(a), h - r + r * math.sin(a)))
    verts, faces = [], []
    for (pr, pz) in prof:
        for j in range(seg):
            b = 2 * math.pi * j / seg
            verts.append((pr * math.cos(b), pr * math.sin(b), pz))
    n = len(prof)
    for i in range(n - 1):
        for j in range(seg):
            a0, a1 = i * seg + j, i * seg + (j + 1) % seg
            faces.append((a0, a1, a1 + seg, a0 + seg))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)   # 極の重複点を閉じる
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


def glass(name, tint_hex="#F4F7FF", rough=0.0, ior=1.47, shadow_pass=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = hex_to_linear(tint_hex)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Transmission Weight"].default_value = 1.0
    p.inputs["IOR"].default_value = ior
    # 影の光線だけ一部を素通しにする（屈折ガラスの影は MNEE の集光頼みで、リブの多い面では暗く残る＝round 8）
    nt = m.node_tree; out = nt.nodes["Material Output"]
    lp = nt.nodes.new("ShaderNodeLightPath"); mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = shadow_pass if shadow_pass is not None else float(os.environ.get("II_SHADOW_PASS", "0.55"))
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = hex_to_linear("#F2F6FF")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mul.inputs[0]); nt.links.new(mul.outputs[0], mix.inputs[0])
    surf = p.outputs[0]
    disp = float(os.environ.get("II_DISP", "0.018"))
    if disp > 0:
        # 🔴 Blender 5.1 の Principled には Dispersion 入力が無い（round 15）。
        #    R/G/B の Glass BSDF を IOR をずらして足す古典の手で分散（縁の虹）を作る
        tint = hex_to_linear(tint_hex)
        add1 = nt.nodes.new("ShaderNodeAddShader"); add2 = nt.nodes.new("ShaderNodeAddShader")
        gs = []
        for k, (c, di) in enumerate((((1, 0, 0), -disp), ((0, 1, 0), 0.0), ((0, 0, 1), disp))):
            g = nt.nodes.new("ShaderNodeBsdfGlass")
            g.inputs["Color"].default_value = tuple(c[i] * tint[i] for i in range(3)) + (1,)
            g.inputs["Roughness"].default_value = rough
            g.inputs["IOR"].default_value = ior + di
            gs.append(g)
        nt.links.new(gs[0].outputs[0], add1.inputs[0]); nt.links.new(gs[1].outputs[0], add1.inputs[1])
        nt.links.new(add1.outputs[0], add2.inputs[0]); nt.links.new(gs[2].outputs[0], add2.inputs[1])
        # 🔴 分散ガラスを MNEE に見せると、集光が R の1本だけで解かれてピンクに染まった（round 15）。
        #    目で見る経路（カメラ・透過・光沢の光線）だけ分散ガラス、影と MNEE には無分散の Principled を渡す
        see = nt.nodes.new("ShaderNodeMath"); see.operation = 'MAXIMUM'
        see2 = nt.nodes.new("ShaderNodeMath"); see2.operation = 'MAXIMUM'
        nt.links.new(lp.outputs["Is Camera Ray"], see.inputs[0]); nt.links.new(lp.outputs["Is Transmission Ray"], see.inputs[1])
        nt.links.new(see.outputs[0], see2.inputs[0]); nt.links.new(lp.outputs["Is Glossy Ray"], see2.inputs[1])
        fin = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(p.outputs[0], mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2])
        nt.links.new(see2.outputs[0], fin.inputs[0])
        nt.links.new(mix.outputs[0], fin.inputs[1]); nt.links.new(add2.outputs[0], fin.inputs[2])
        nt.links.new(fin.outputs[0], out.inputs["Surface"])
        return m
    nt.links.new(surf, mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


m_glass = glass("glass", os.environ.get("II_TINT", "#EEF3FF"))

# 🔴 round 7：離散の円柱（葦）は焦点距離が半径の1.5倍しかなく、床に届く頃には光が広がり切って
#    「影より少し明るい帯」にしかならなかった（集光が日向を超えない）。
#    → 1枚の板に浅いリブを付けた「型板ガラス」にする。板は光をほぼ全部通すので影が消え、リブが縞の集光を描く
AMP = 0.06
L = 0.30
T = 0.011                                   # 板厚
RIB_P = float(os.environ.get("II_RIB_P", "0.014"))   # リブのピッチ
RIB_R = float(os.environ.get("II_RIB_R", "0.04"))   # リブの曲率半径（大きいほど焦点が遠い）
RIG_LOC = (-0.03, 0.15, STEP_H)
rig = bpy.data.objects.new("rig", None); scene.collection.objects.link(rig)
rig.location = RIG_LOC


def s_curve(x):
    return AMP * math.sin(math.pi * x / (L / 2))


def s_slope(x):
    return AMP * math.pi / (L / 2) * math.cos(math.pi * x / (L / 2))


def height(x):
    u = (0.5 - x / L)                        # 左=1 → 右=0
    return 0.07 + 0.13 * u ** 1.3


def rib(a):
    q = (a % RIB_P) - RIB_P / 2
    return math.sqrt(RIB_R ** 2 - q * q) - math.sqrt(RIB_R ** 2 - (RIB_P / 2) ** 2)


# glb だけ粗くする（1400×48・面取り8分割のままだと 10.3MB で 8MB を超えた）
NX, NZ = (500, 12) if "glb" in modes and len(modes) == 1 else (1400, 48)
xs = [-L / 2 + L * i / (NX - 1) for i in range(NX)]
arc = [0.0]
for i in range(1, NX):
    arc.append(arc[-1] + math.hypot(xs[i] - xs[i - 1], s_curve(xs[i]) - s_curve(xs[i - 1])))
verts, faces = [], []
F = [[0] * (NZ + 1) for _ in range(NX)]
B = [[0] * (NZ + 1) for _ in range(NX)]
for i, x in enumerate(xs):
    tx, ty = 1.0, s_slope(x); ln = math.hypot(tx, ty); tx, ty = tx / ln, ty / ln
    nx, ny = ty, -tx                          # 手前（-y）向きの法線
    cx, cy = x, s_curve(x)
    H = height(x)
    wf = T / 2 + rib(arc[i])
    for j in range(NZ + 1):
        z = H * (1 - (1 - j / NZ) ** 1.0)
        F[i][j] = len(verts); verts.append((cx + nx * wf, cy + ny * wf, z))
        B[i][j] = len(verts); verts.append((cx - nx * T / 2, cy - ny * T / 2, z))
for i in range(NX - 1):
    for j in range(NZ):
        faces.append((F[i][j], F[i + 1][j], F[i + 1][j + 1], F[i][j + 1]))
        faces.append((B[i][j], B[i][j + 1], B[i + 1][j + 1], B[i + 1][j]))
    faces.append((F[i][NZ], F[i + 1][NZ], B[i + 1][NZ], B[i][NZ]))      # 天
    faces.append((F[i][0], B[i][0], B[i + 1][0], F[i + 1][0]))          # 底
for j in range(NZ):                                                    # 両端
    faces.append((F[0][j], F[0][j + 1], B[0][j + 1], B[0][j]))
    faces.append((F[-1][j], B[-1][j], B[-1][j + 1], F[-1][j + 1]))
me = bpy.data.meshes.new("panel_me"); me.from_pydata(verts, [], faces); me.update()
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
panel = bpy.data.objects.new("panel", me); scene.collection.objects.link(panel)
bevel_obj(panel, float(os.environ.get("II_PANEL_BEVEL", "0.0045")), segments=8, angle=40)
panel.data.materials.append(m_glass)
panel.parent = rig
panel.cycles.is_caustics_caster = CAUSTICS
rods = []

# 下段の手前に、小さなガラスの粒（大→小の対角線を受ける）
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(0.18, 0.05, STEP_H + 0.022), segments=256, ring_count=128)
drop = bpy.context.object; drop.name = "drop"
for p in drop.data.polygons:
    p.use_smooth = True
# 粒の下の集光は縁がギザギザの暗い輪になった（MNEE の取りこぼし・round 20）＝粒だけ影をさらに素通しにして輪を薄める
drop.data.materials.append(glass("glass_drop", os.environ.get("II_TINT", "#EEF3FF"), shadow_pass=float(os.environ.get("II_DROP_PASS", "0.8"))))
drop.cycles.is_caustics_caster = CAUSTICS

parts = [rig, panel, drop]

# ------------------------------------------------------------- 光：奥左上からの太陽1灯（逆光）
# 🔴 太陽（SUN）は MNEE の集光の対象外で、ガラスが黒い棒と同じ影を落とした（round 2）。遠くの小さなスポットで太陽の代わりをする
SUN_EL = math.radians(float(os.environ.get("II_SUN_EL", "36")))
SUN_AZ0 = float(os.environ.get("II_SUN_AZ", "-15"))            # 0=真奥から。負＝左奥
SUN_SWING = float(os.environ.get("II_SUN_SWING", "10"))        # 動き：方位を ±SWING° 振る
SUN_DIST = 4.0
CENTER = Vector((RIG_LOC[0], RIG_LOC[1] - 0.06, 0.05))
sd = bpy.data.lights.new("sun", 'SPOT')
sd.energy = float(os.environ.get("II_SUN", "4500"))
sd.shadow_soft_size = float(os.environ.get("II_SUN_R", "0.035"))
sd.spot_size = math.radians(float(os.environ.get("II_CONE", "7.5"))); sd.spot_blend = float(os.environ.get("II_BLEND", "1.0"))
sd.color = (1.0, 0.975, 0.94)
sd.cycles.is_caustics_light = CAUSTICS
sun = bpy.data.objects.new("sun", sd); scene.collection.objects.link(sun)


def place_sun(az_deg):
    az = math.radians(az_deg)
    Lsrc = Vector((math.sin(az) * math.cos(SUN_EL), math.cos(az) * math.cos(SUN_EL), math.sin(SUN_EL)))
    sun.location = CENTER + Lsrc * SUN_DIST
    sun.rotation_euler = (-Lsrc).to_track_quat('-Z', 'Y').to_euler()


place_sun(SUN_AZ0)

# 映り込み用の白い面（カメラには写さない）：縁とリブの稜線に白いハイライトを作る
card = area("card", (0.55, -0.35, 0.45), 0.6, float(os.environ.get("II_CARD", "30")), (0.96, 0.97, 1.0), target=(0.0, 0.15, 0.08), shape='DISK')   # 四角いと粒に窓が写る（round 20）
card.visible_camera = False
card.data.cycles.is_caustics_light = False
# 🔴 面光は壁と床まで洗って全体を霞ませた（round 9）＝ライトリンクでガラスにだけ当てる
_glass_col = bpy.data.collections.new("glass_only")
for _o in (panel, drop):
    _glass_col.objects.link(_o)
card.light_linking.receiver_collection = _glass_col
# 段の前面の起こし（step だけに当てる）：濃い一本線を明るい「折れ目」にする（round 13）
fill = area("fill", (0.1, -0.9, 0.12), 1.2, float(os.environ.get("II_FILL", "6")), (0.9, 0.93, 1.0), target=(0.1, 0.0, 0.015))
fill.visible_camera = False
_step_col = bpy.data.collections.new("step_only"); _step_col.objects.link(step)
fill.light_linking.receiver_collection = _step_col

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.lens = LOOK["lens"]
CAM = Vector((float(os.environ.get("II_CX", "0.33")), float(os.environ.get("II_CY", "-0.44")),
              float(os.environ.get("II_CZ", "0.30"))))
AIM = Vector((float(os.environ.get("II_AX", "0.035")), 0.04, float(os.environ.get("II_AZ", "0.07"))))
cam.location = CAM
cam.rotation_euler = (AIM - CAM).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True
cd.dof.focus_distance = (Vector((0.07, 0.04, 0.08)) - CAM).length   # 衝立と粒の中間
cd.dof.aperture_fstop = LOOK["fstop"]
scene.camera = cam
# ------------------------------------------------------------- 動画＝プロダクトフィルム（2026-09-23 に作り直し）
# 旧：6秒・1カットの振り子ループ。→ 光の走り（中）／回り込み（引き）／マクロ（寄り）／決め（hero）の4カット・11.5秒
# 物の動き（光の方位の振り子・衝立の首振り）は旧版を全体の進み T に移し、決めのカットで hero の位相（t=0）に戻して止める。
def ease(t):                  # 加減速（sine in-out）
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out(t):              # 動きながら入って止まる
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def orbit(center, radius, height, deg):   # 被写体まわりの弧（deg=0 が正面 -Y）
    r = math.radians(deg)
    return Vector((center[0] + radius * math.sin(r), center[1] - radius * math.cos(r), height))


FOCUS_HERO = Vector((0.07, 0.04, 0.08))      # hero のピント（衝立と粒の中間）
DROP = Vector(drop.location)
SHOTS = [
    dict(sec=3.0, kind="光の走り",   # 中：上段の集光の床を低く見下ろし、光が振れて V 字の線が床を流れる。カメラは横にわずかに滑る
         cam=lambda t: (lerp((-0.16, -0.30, 0.20), (-0.08, -0.31, 0.19), ease(t)),
                        lerp((-0.06, 0.02, 0.03), (0.00, 0.02, 0.03), ease(t)), 70, 8.0, None)),
    dict(sec=2.5, kind="回り込み",   # 引き：左前の高みから弧を描き、S 字の衝立の全体と段差を見せる
         cam=lambda t: (orbit(CENTER, 0.70, 0.50, -34 + 22 * ease(t)), CENTER + Vector((0.02, 0, 0.0)), 50, 11.0, None)),
    dict(sec=3.0, kind="マクロ",     # 寄り：粒と真下の白い焦点を見下ろし、ピントを焦点から粒へ送る
         cam=lambda t: (lerp(DROP + Vector((-0.11, -0.27, 0.13)), DROP + Vector((-0.05, -0.29, 0.12)), ease(t)),
                        DROP + Vector((0.0, -0.025, -0.015)), 120, 5.6,
                        (DROP - Vector((0.0, 0.03, 0.02)) - (DROP + Vector((-0.08, -0.28, 0.125)))).length * (1 - ease(t))
                        + (DROP - (DROP + Vector((-0.08, -0.28, 0.125)))).length * ease(t))),
    dict(sec=3.0, kind="決め",       # 右から寄りながら入り、hero の構図で止まる
         cam=lambda t: (lerp(CAM + Vector((0.10, -0.06, 0.05)), CAM, ease_out(min(1.0, t / 0.6))),
                        lerp(AIM + Vector((0.03, 0, -0.01)), AIM, ease_out(min(1.0, t / 0.6))),
                        LOOK["lens"], LOOK["fstop"], "hero")),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
SECONDS = N_FRAMES / FPS
STILL_FRAME = N_FRAMES        # 最後のフレーム＝決めのカットが止まったところ＝hero
SETTLE = (shot_start[-1] + round(SHOTS[-1]["frames"] * 0.6) - 1) / (N_FRAMES - 1)   # この T で動きが hero の位相に戻って止まる


def pose(T):
    """旧版の振り子（位相 u で1往復）。u=0 と u=1 が hero の位相＝決めで止まる"""
    u = ease(min(1.0, T / SETTLE))
    place_sun(SUN_AZ0 + SUN_SWING * math.sin(2 * math.pi * u))
    rig.rotation_euler = (0, 0, math.radians(5) * math.sin(2 * math.pi * u + 0.8))


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
        if focus == "hero":
            focus = (FOCUS_HERO - Vector(loc)).length
        cd.dof.focus_distance = focus if focus else (Vector(tgt) - Vector(loc)).length
        for path in ("location", "rotation_euler"):
            cam.keyframe_insert(path, frame=f)
        cd.keyframe_insert("lens", frame=f)
        cd.dof.keyframe_insert("aperture_fstop", frame=f)
        cd.dof.keyframe_insert("focus_distance", frame=f)
        pose(T)
        rig.keyframe_insert("rotation_euler", frame=f)
        sun.keyframe_insert("location", frame=f)
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
    still(os.path.join(OUT, "_testhero.png"), 1600, int(os.environ.get("II_TH_SAMPLES", "128")))
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
