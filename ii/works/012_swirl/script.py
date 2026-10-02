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
    aspect=(16, 9),
    lens=105,
    fstop=1.6,
    view="Standard",
    look="None",
    exposure=0.0,
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


# ------------------------------------------------------------- 舞台（毎回決める）
# 床も壁も無い。カメラに見える地だけ、画面座標の斜めグラデーション（左上の空色→右下の白）。
# 照明・映り込みに使う環境は別に組む（Light Path の Is Camera Ray で分ける）：
#   上半球＝空色、右上奥に暖かい明るい塊（逆光の太陽のまわりの空）、下＝淡い白（雲・地面の照り返し）
SKY_TL, SKY_BR = hex_to_linear("#8FD3FB"), hex_to_linear("#F2F8FE")
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
wn, wl = world.node_tree.nodes, world.node_tree.links
bgn = wn["Background"]
tc = wn.new("ShaderNodeTexCoord")


def sock(node, name, kind, out=False):
    """#103：Mix の同名ソケットは型で引く"""
    return next(s for s in (node.outputs if out else node.inputs) if s.name == name and s.type == kind)


# 画面の地：Window 座標で (x + (1 - y)) / 2
sep = wn.new("ShaderNodeSeparateXYZ"); wl.new(tc.outputs["Window"], sep.inputs[0])
d1 = wn.new("ShaderNodeMath"); d1.operation = 'SUBTRACT'; d1.inputs[0].default_value = 1.0
wl.new(sep.outputs["Y"], d1.inputs[1])
d2 = wn.new("ShaderNodeMath"); d2.operation = 'ADD'
wl.new(sep.outputs["X"], d2.inputs[0]); wl.new(d1.outputs[0], d2.inputs[1])
d3 = wn.new("ShaderNodeMapRange")
d3.inputs["From Min"].default_value, d3.inputs["From Max"].default_value = 0.55, 1.95
wl.new(d2.outputs[0], d3.inputs["Value"])
gr = wn.new("ShaderNodeValToRGB")
gr.color_ramp.elements[0].color = SKY_TL; gr.color_ramp.elements[1].color = SKY_BR
wl.new(d3.outputs["Result"], gr.inputs["Fac"])
cam_bg = wn.new("ShaderNodeBackground"); wl.new(gr.outputs["Color"], cam_bg.inputs["Color"])
cam_bg.inputs["Strength"].default_value = 1.0

# 照明用の空：上下の向き＋太陽側の暖かい塊
gen = tc.outputs["Generated"]


def dotdir(direction):
    dn = wn.new("ShaderNodeVectorMath"); dn.operation = 'DOT_PRODUCT'
    dn.inputs[1].default_value = Vector(direction).normalized()
    nm = wn.new("ShaderNodeVectorMath"); nm.operation = 'NORMALIZE'
    wl.new(gen, nm.inputs[0]); wl.new(nm.outputs["Vector"], dn.inputs[0])
    return dn.outputs["Value"]


def ramp(fac, stops):
    r = wn.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = 'EASE'
    mr = wn.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -1, 1
    wl.new(fac, mr.inputs["Value"]); wl.new(mr.outputs["Result"], r.inputs["Fac"])
    el = r.color_ramp.elements
    el[0].position, el[1].position = stops[0][0], stops[-1][0]
    for st in stops[1:-1]:
        el.new(st[0])
    for e, (p, hx, k) in zip(sorted(el, key=lambda e: e.position), stops):
        c = hex_to_linear(hx); e.color = (c[0] * k, c[1] * k, c[2] * k, 1)
    return r.outputs["Color"]


SUN_DIR = Vector((0.55, 0.75, 0.38)).normalized()     # 右上・奥（カメラは -Y 側から +Y を見る）
sky = ramp(dotdir((0, 0, 1)), [(0.0, "#C9D8E2", 0.9), (0.5, "#BFE3F7", 1.0), (1.0, "#6FB9EC", 1.0)])
warm = ramp(dotdir(SUN_DIR), [(0.0, "#000000", 0.0), (0.70, "#000000", 0.0), (0.90, "#FFB070", 2.2),
                              (1.0, "#FFE2B8", 2.5)])
add = wn.new("ShaderNodeMix"); add.data_type = 'RGBA'; add.blend_type = 'ADD'
add.inputs["Factor"].default_value = 1.0
wl.new(sky, sock(add, "A", 'RGBA')); wl.new(warm, sock(add, "B", 'RGBA'))
env_bg = wn.new("ShaderNodeBackground"); wl.new(sock(add, "Result", 'RGBA', True), env_bg.inputs["Color"])
env_bg.inputs["Strength"].default_value = 1.0

lp = wn.new("ShaderNodeLightPath")
mix = wn.new("ShaderNodeMixShader")
wl.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
wl.new(env_bg.outputs[0], mix.inputs[1]); wl.new(cam_bg.outputs[0], mix.inputs[2])
wl.new(mix.outputs[0], wn["World Output"].inputs["Surface"])

# ------------------------------------------------------------- 被写体（毎回作る）
# 薄いガラスの帯を、傾いた1本の軸のまわりに何十本も巻く。帯ごとに半径・巻き角・幅・ねじれ・軸方向の位置をばらす。
# 帯の長手に沿って細い筋（引っかき）を入れ、異方性の照りで「毛羽立った光沢」を出す。
import random
rng = random.Random(12)
AXIS = Vector((0.78, -0.50, 0.38)).normalized()        # 渦の軸（右上へ倒れ、少しこちらを向く）
E1 = AXIS.cross(Vector((0, 0, 1))).normalized()
E2 = AXIS.cross(E1).normalized()
CENTER = Vector((0, 0, 0))


def glass_mat(name, hx, metal=0.0, aniso=0.85, tint_rough=0.06, trans=None, cut0=0.42):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n, l = nt.nodes, nt.links
    p = n["Principled BSDF"]
    p.inputs["Base Color"].default_value = hex_to_linear(hx)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Transmission Weight"].default_value = (1.0 - metal) if trans is None else trans
    p.inputs["IOR"].default_value = 1.5
    p.inputs["Anisotropic"].default_value = aniso
    uv = n.new("ShaderNodeUVMap")
    tg = n.new("ShaderNodeTangent"); tg.direction_type = 'UV_MAP'
    l.new(tg.outputs["Tangent"], p.inputs["Tangent"])
    # 長手(u)に引き伸ばした筋：u 方向に 4、v 方向に 260
    mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (4.0, 260.0, 1.0)
    l.new(uv.outputs["UV"], mp.inputs["Vector"])
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 3.0
    l.new(mp.outputs["Vector"], nz.inputs["Vector"])
    rr = n.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value, rr.inputs["To Max"].default_value = tint_rough * 0.15, tint_rough * 1.4
    l.new(nz.outputs["Fac"], rr.inputs["Value"]); l.new(rr.outputs["Result"], p.inputs["Roughness"])
    # 繊維：v 方向に細かい筋で抜く（帯が毛羽立った刷毛目の束に見える）
    mp2 = n.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (1.2, 90.0, 1.0)
    l.new(uv.outputs["UV"], mp2.inputs["Vector"])
    nz2 = n.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 1.0; nz2.inputs["Detail"].default_value = 2.0
    l.new(mp2.outputs["Vector"], nz2.inputs["Vector"])
    cut = n.new("ShaderNodeMapRange")
    cut.inputs["From Min"].default_value, cut.inputs["From Max"].default_value = cut0, cut0 + 0.10
    l.new(nz2.outputs["Fac"], cut.inputs["Value"])
    l.new(cut.outputs["Result"], p.inputs["Alpha"])
    bp = n.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.002
    l.new(nz.outputs["Fac"], bp.inputs["Height"]); l.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


M_COPPER = glass_mat("copper", "#F07A2A", metal=0.3)
M_AMBER = glass_mat("amber", "#F2A65E")
M_BLUE = glass_mat("cobalt", "#06338F", metal=0.0, trans=0.0, cut0=0.34, tint_rough=0.02)   # 藍は繊維を詰めて奥の銅を透かさない（透けると藤色に混ざる）
M_BLUE.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.15   # 空の映り込みで藤色に褪せるのを止める
M_CLEAR = glass_mat("clear", "#8FB4CC")


def ribbon(name, r0, dr, a0, span, z0, dz, w, twist0, twist1, nu=180, nv=6, thick=0.006, ax=None, cen=None):
    ax = ax or AXIS
    e1 = ax.cross(Vector((0, 0, 1))).normalized(); e2 = ax.cross(e1).normalized()
    cen = cen if cen is not None else CENTER
    verts, faces, uvs = [], [], []
    for i in range(nu + 1):
        s = i / nu
        th = a0 + span * s
        r = r0 + dr * s
        rad = math.cos(th) * e1 + math.sin(th) * e2
        c = cen + rad * r + ax * (z0 + dz * s)
        ph = twist0 + (twist1 - twist0) * s
        across = math.cos(ph) * ax + math.sin(ph) * rad
        ww = w * math.sin(math.pi * s) ** 0.55
        for j in range(nv + 1):
            t = j / nv - 0.5
            verts.append(c + across * ww * t)
            uvs.append((s * span * r, j / nv))
    for i in range(nu):
        for j in range(nv):
            a = i * (nv + 1) + j
            faces.append((a, a + nv + 1, a + nv + 2, a + 1))
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            uvl.data[li].uv = uvs[me.loops[li].vertex_index]   # 頂点番号は from_pydata の順（#99 の bmesh 罠は無い）
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    so = ob.modifiers.new("thick", 'SOLIDIFY'); so.thickness = thick; so.offset = 0
    return ob


parts = []
N_RIB = 140
LAYERS = [((AXIS + Vector(v) * 0.35).normalized(), z) for v, z in
          [((0, 0, 0), 0.0), ((0.3, 0.2, -0.4), -0.32), ((-0.4, 0.1, 0.3), 0.30), ((0.1, -0.4, 0.2), -0.55), ((-0.2, 0.3, -0.1), 0.52)]]
for k in range(N_RIB):
    q = rng.random()
    if q < 0.42:
        mat = M_COPPER
    elif q < 0.62:
        mat = M_AMBER
    elif q < 0.86:
        mat = M_BLUE
    else:
        mat = M_CLEAR
    r0 = 0.9 * rng.random() ** 0.8 + 0.08
    layer = LAYERS[k % len(LAYERS)]            # 軸方向にずれた5枚の層＝円盤が何層も重なる
    ax = (layer[0] + Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))) * 0.06).normalized()
    cen = AXIS * layer[1] + Vector((rng.gauss(0, 0.04), rng.gauss(0, 0.04), rng.gauss(0, 0.04)))
    wmul = 1.7 if mat is M_BLUE else 1.0
    ob = ribbon("rib%02d" % k, r0, rng.uniform(-0.25, 0.3), rng.uniform(0, 2 * math.pi),
                rng.uniform(1.6, 4.2), rng.uniform(-0.12, 0.12), rng.uniform(-0.1, 0.1),
                rng.uniform(0.06, 0.34) * wmul, math.pi / 2 + rng.uniform(-0.35, 0.35), math.pi / 2 + rng.uniform(-0.6, 0.6), ax=ax, cen=cen)
    ob.data.materials.append(mat)
    ob["spin"] = rng.uniform(0.6, 1.4)
    parts.append(ob)
body = parts[0]

# ------------------------------------------------------------- 光（毎回組む）
# 右上・奥からの暖かい逆光（太陽）＋環境の空。光源は画面に写さない。
sun_d = bpy.data.lights.new("sun", 'SUN'); sun_d.energy = 8.0; sun_d.color = (1.0, 0.78, 0.55)
sun_d.angle = math.radians(2.0)
sun = bpy.data.objects.new("sun", sun_d); scene.collection.objects.link(sun)
sun.rotation_euler = (-SUN_DIR).to_track_quat('-Z', 'Y').to_euler()

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
# 🔴 下は動作確認用の仮置き。**毎回、基準と題材に合わせて組み直す**。
TGT = Vector((0, 0, 0))
HERO_T = Vector((-0.04, 0, 0.0))                     # 注視点を左へ＝塊は画面の中央やや右
HERO_C = Vector((-0.12, -17.5, 0.8))
SHOTS = [
    dict(sec=2.8,   # マクロ：右の縁の刷毛目と照りを外からなめる＋ピント送り
         cam=lambda t: (lerp((2.1, -5.6, 1.1), (1.5, -5.8, 0.6), ease(t)), Vector((0.95, 0, 0.35)),
                        150, 2.0, 5.2 + 0.5 * ease(t))),
    dict(sec=3.0,   # 回り込み：渦を横から、軸の傾きが見える側へ
         cam=lambda t: (orbit(TGT, 9.5, 2.4 - 1.2 * ease(t), 62 - 34 * ease(t)), TGT, 70, 2.8, None)),
    dict(sec=2.7,   # 物の動き：下から見上げ、帯がほどけるように回る（pose が速くなる）
         cam=lambda t: (lerp((-3.2, -8.6, -3.0), (-2.6, -8.9, -2.6), ease(t)), Vector((0.1, 0, 0.1)), 85, 2.4, None)),
    dict(sec=3.0,   # 決め：寄りながら入って hero の構図で止まる
         cam=lambda t: (lerp(HERO_C + Vector((1.1, 3.2, -0.25)), HERO_C, ease_out(min(1.0, t / 0.62))), HERO_T,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES        # 最後のフレーム＝決めのカットが止まったところ＝hero

from mathutils import Quaternion


def pose(i, t, T):
    """帯ごとに渦の軸まわりに回る。速さは帯ごとに違い、決めの終わりで止まる"""
    a = ease_out(T) * 1.6
    for o in parts:
        o.rotation_euler = Quaternion(AXIS, -a * o["spin"]).to_euler('XYZ')


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
