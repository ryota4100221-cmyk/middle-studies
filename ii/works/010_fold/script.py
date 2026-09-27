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
    lens=50,
    fstop=128.0,
    view="AgX",
    look="AgX - Medium High Contrast",
    exposure=-0.3,
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
# 地は写さない。方向で色が変わる環境（右上＝桃〜クリーム、左上＝明るい青緑、下と奥＝深い青緑〜黒）を
# 鏡に近い艶の面に映し込み、面の向きだけで色を出す（基準に光源は写っていない）。
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
wn, wl = world.node_tree.nodes, world.node_tree.links
bgn = wn["Background"]
tc = wn.new("ShaderNodeTexCoord")
wmap = wn.new("ShaderNodeMapping"); wmap.vector_type = 'VECTOR'   # 光の走り：環境を z 軸まわりに回して映り込みを流す
wl.new(tc.outputs["Generated"], wmap.inputs["Vector"])


def lobe(direction, stops, x=-600):
    """方向ベクトル d との内積（-1..1）→ 色。stops=[(pos, hex, strength)]"""
    dot = wn.new("ShaderNodeVectorMath"); dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = Vector(direction).normalized()
    wl.new(wmap.outputs["Vector"], dot.inputs[0])
    ramp = wn.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = 'LINEAR'
    el = ramp.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    for i, (p, hx, k) in enumerate(stops):
        e = el[0] if i == 0 else el.new(p)
        e.position = p
        c = hex_to_linear(hx)
        e.color = (c[0] * k, c[1] * k, c[2] * k, 0.0 if k == 0 else 1.0)
    mr = wn.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -1, 1
    wl.new(dot.outputs["Value"], mr.inputs["Value"])
    wl.new(mr.outputs["Result"], ramp.inputs["Fac"])
    return ramp.outputs["Color"], ramp.outputs["Alpha"]


ENV = dict(
    base=((-0.25, 0.95, 0.02), [(0.0, "#000000", 0), (0.62, "#000000", 0), (0.78, "#021019", 1),
                              (0.92, "#0A3B55", 1.2), (1.0, "#1B6788", 1.3)]),
    sky=((0.38, 0.85, 0.38), [(0.0, "#000000", 0), (0.955, "#000000", 0), (0.98, "#1F7C9E", 1.2),
                            (0.995, "#B9D8D4", 1.6), (1.0, "#F4E0CA", 1.9)]),
    cool=((0.4, 0.92, 0.0), [(0.0, "#000000", 0), (0.966, "#000000", 0), (0.968, "#5A2A9E", 1.6),
                             (0.970, "#2FA88A", 1.6), (0.972, "#E8962E", 1.9), (0.975, "#E7B7A0", 2.0),
                             (1.0, "#FFF3E6", 3.0)]),
    warm=((0.22, 0.1, 0.97), [(0.0, "#000000", 0), (0.88, "#000000", 0), (0.92, "#3E1030", 1.0),
                              (0.95, "#B85A74", 1.4), (0.96, "#EFA894", 2.1), (1.0, "#FBE0C8", 2.7)]),
)
acc = None
for name, (d, stops) in ENV.items():   # 重ね塗り：base の上に cool、その上に warm（混ぜて濁らせない）
    col, al = lobe(d, stops)
    if name in ("cool", "sky"):   # 稜線（x≈0.33）と斜面（x≈0.27）にだけ当て、上の面の稜（x≈0.43）には当てない
        sx = wn.new("ShaderNodeSeparateXYZ"); wl.new(wmap.outputs["Vector"], sx.inputs[0])
        mk = wn.new("ShaderNodeMapRange"); mk.clamp = True
        mk.inputs["From Min"].default_value, mk.inputs["From Max"].default_value = 0.37, 0.42
        mk.inputs["To Min"].default_value, mk.inputs["To Max"].default_value = 1.0, 0.0
        wl.new(sx.outputs["X"], mk.inputs["Value"])
        ml = wn.new("ShaderNodeMath"); ml.operation = 'MULTIPLY'
        wl.new(al, ml.inputs[0]); wl.new(mk.outputs["Result"], ml.inputs[1]); al = ml.outputs[0]
    if acc is None:
        acc = col
    else:
        mx = wn.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MIX'
        wl.new(al, mx.inputs["Factor"]); wl.new(acc, mx.inputs[6]); wl.new(col, mx.inputs[7])
        acc = mx.outputs[2]
lp = wn.new("ShaderNodeLightPath")        # カメラに直接写る空は深い藍（映り込みにだけ色の塊を使う）
vis = wn.new("ShaderNodeMix"); vis.data_type = 'RGBA'
vis.inputs[7].default_value = hex_to_linear("#021421")
wl.new(lp.outputs["Is Camera Ray"], vis.inputs["Factor"]); wl.new(acc, vis.inputs[6])
wl.new(vis.outputs[2], bgn.inputs["Color"])
bgn.inputs["Strength"].default_value = 1.0

# ------------------------------------------------------------- 被写体（毎回作る）
# 谷を挟む2枚の大きな面（左の高い斜面・右の低い面）と、上を横切る面。
# 谷の中を、細い帯が何本も平行に這う（カーブの押し出し＝縁が1本ずつ丸く立つ）。
# 谷の筋 c(y) は奥（画面中央）から手前（右下）へ S 字に抜ける。


def crease(y):
    return 0.9 - 0.42 * y + 0.22 * math.sin(1.1 * y + 0.6)


def sig(v):
    return 1 / (1 + math.exp(-max(-40, min(40, v))))


def grid(name, fn, u0, u1, v0, v1, nu, nv, thick=0.04, sub=1):
    verts, faces = [], []
    for j in range(nv + 1):
        v = v0 + (v1 - v0) * j / nv
        for i in range(nu + 1):
            verts.append(fn(u0 + (u1 - u0) * i / nu, v))
    w = nu + 1
    for j in range(nv):
        for i in range(nu):
            faces.append((j * w + i, j * w + i + 1, (j + 1) * w + i + 1, (j + 1) * w + i))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    so = ob.modifiers.new("thick", 'SOLIDIFY'); so.thickness = thick; so.offset = 0; so.use_rim = True
    ss = ob.modifiers.new("round", 'SUBSURF'); ss.levels = ss.render_levels = sub
    return ob


def lacquer(name, hx, rough=0.03, metal=1.0, film=0.0, edge_film=0, ridge_film=0):
    m = principled(name, hex_to_linear(hx), rough=rough, metal=metal)
    p = m.node_tree.nodes["Principled BSDF"]
    if ridge_film and not edge_film and "Thin Film Thickness" in p.inputs:
        # 形の尖り（稜・縁ほど高い）でだけ薄膜を厚く＝稜と縁に細い虹色の縁取り（基準の分散の代わり）
        nt = m.node_tree
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.53, 0.62
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.0, ridge_film
        nt.links.new(geo.outputs["Pointiness"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], p.inputs["Thin Film Thickness"])
        p.inputs["Thin Film IOR"].default_value = 1.45
    if edge_film and "Thin Film Thickness" in p.inputs:
        # 面が視線に対して寝るほど薄膜を厚く＝折れの縁と層の境目にだけ虹色の縁取りが出る（基準の分散の代わり）
        nt = m.node_tree
        lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.55, 1.0
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.0, edge_film
        nt.links.new(lw.outputs["Facing"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], p.inputs["Thin Film Thickness"])
        p.inputs["Thin Film IOR"].default_value = 1.45
    if film and "Thin Film Thickness" in p.inputs:
        p.inputs["Thin Film Thickness"].default_value = film
        p.inputs["Thin Film IOR"].default_value = 1.4
    return m


M_SHEET = lacquer("sheet", "#C9D6DE")
M_BAND = lacquer("band", "#D8DEE4", rough=0.03, edge_film=520)
parts = []

# 左の高い斜面：左で高く、谷へ向かって丸く落ち、谷の中で終わる（u＝谷からの横距離）
SL = dict(top=1.05, w=0.08)
left = grid("left", lambda u, y: (crease(y) + u, y,
                                  SL["top"] * sig(-(u + 0.25) / SL["w"]) + 0.05 * u * u * (u < 0) * 0.2
                                  + 0.0 * max(0.0, y - 1.2) * sig(-(u + 0.6) / 0.3)),
            -7.0, 0.35, -9.0, 9.0, 220, 200)
# 右の低い面：谷から右へゆるく立ち上がって手前に倒れる
right = grid("right", lambda u, y: (crease(y) + u, y,
                                    -0.35 + 0.4 * sig((u - 1.7) / 0.6) + 0.03 * u),
             -0.25, 11.0, -9.0, 9.0, 300, 200)
# 上を横切る面：奥で高く、手前の縁は丸く垂れて谷の上に覆いかぶさる
top = grid("canopy", lambda x, v: (x, 2.4 + 12.0 * v + 0.12 * math.sin(0.55 * x + 0.3),
                                   0.85 + 1.1 * (1.0 - math.exp(-v * 14.0)) - 0.1 * 0.7 * math.log(1 + math.exp(x / 0.7)) - 0.3 * 0.6 * math.log(1 + math.exp(-(x + 1.0) / 0.6))),
           -11.0, 11.0, 0.0, 1.0, 300, 260, thick=0.06)
M_RIGHT = lacquer("right", "#1C7EA8", rough=0.5, metal=0.5)
M_TOP = lacquer("top", "#D9B8C2")
for ob, m in ((left, M_SHEET), (right, M_RIGHT), (top, M_TOP)):
    ob.data.materials.append(m); parts.append(ob)

# 谷の中：丸く終わる楕円の舌と、同じ形を少しずつ大きく・低くした板の入れ子＝縁が平行な線として舌を囲む


def lozenge(name, cx, a, b, z0, slope, thick, mat, n=64):
    """(u, y) 平面の楕円（中心 u=cx, y=0.8・半幅 a・半長 b）を、谷の筋 c(y) に沿って曲げ、u 方向に傾ける"""
    verts, faces = [], []
    for j in range(n + 1):
        for i in range(n + 1):
            p, q = -1 + 2 * i / n, -1 + 2 * j / n
            du = p * math.sqrt(max(0.0, 1 - q * q / 2))       # 正方形→円板
            dv = q * math.sqrt(max(0.0, 1 - p * p / 2))
            u, y = cx + a * du, -0.4 + b * dv
            wig = 0.24 * math.sin(2.3 * (y - 0.6))       # 舌だけの S 字のうねり
            verts.append((crease(y) + wig + u, y, z0 - slope * (u - cx) + 0.06 * math.sin(1.3 * y) - 0.14 * du * du))
    w = n + 1
    for j in range(n):
        for i in range(n):
            faces.append((j * w + i, j * w + i + 1, (j + 1) * w + i + 1, (j + 1) * w + i))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    for pg in me.polygons:
        pg.use_smooth = True
    so = ob.modifiers.new("thick", 'SOLIDIFY'); so.thickness = thick; so.offset = 0; so.use_rim = True
    ss = ob.modifiers.new("round", 'SUBSURF'); ss.levels = ss.render_levels = 2
    ob.data.materials.append(mat)
    parts.append(ob)
    return ob


M_TONGUE = lacquer("tongue", "#F0A6A0", rough=0.25, metal=0.0, edge_film=520)
M_TONGUE.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 1.0
M_TONGUE.node_tree.nodes["Principled BSDF"].inputs["Coat Tint"].default_value = hex_to_linear("#FCE6E0")
M_TONGUE.node_tree.nodes["Principled BSDF"].inputs["Coat Roughness"].default_value = 0.03
M_TONGUE.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = hex_to_linear("#F0A6A0")
M_TONGUE.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.3   # 青緑の拡散で灰に濁らせない
lozenge("tongue", 0.65, 0.6, 2.6, 0.5, 0.28, 0.014, M_TONGUE)
for k in range(1, 4):
    lozenge("shell%d" % k, 0.65, 0.6 + 0.07 * k, 2.6 + 0.12 * k, 0.5 - 0.07 * k, 0.28 - 0.02 * k,
            0.01, M_BAND)
body = parts[0]

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True   # 決めは f/128＝実質パンフォーカス。マクロだけ浅く
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
TGT = Vector((0.8, 1.6, 0.4))
ROLL = math.radians(10)   # 稜線を対角にする傾き
HERO_CAM = Vector((-0.2, -4.9, 2.9))
_ry = 0.2                                  # 舌の左の入れ子の縁の束（舌の式から出す：左端 u=0.65−0.6 の少し外）
RIMS = Vector((crease(_ry) + 0.24 * math.sin(2.3 * (_ry - 0.6)) + 0.0, _ry, 0.5 + 0.28 * 0.62 - 0.14 - 0.1))
RIDGE = Vector((-0.1, 1.2, 0.9))          # 斜面の稜
M0, M1 = Vector((0.35, -0.95, 1.55)), Vector((0.62, -1.05, 1.45))
SHOTS = [
    dict(sec=3.0, roll=math.radians(-6),   # マクロ：入れ子の縁の束を長いレンズでなめ、ピントを手前の縁→奥の縁へ送る
         cam=lambda t: (M0.lerp(M1, ease(t)), RIMS, 120, 4.0,
                        (RIMS - M0.lerp(M1, ease(t))).length - 0.12 + 0.3 * ease(t))),
    dict(sec=3.0, roll=math.radians(18),   # 光の走り：稜と上の面の寄り。カメラはほぼ止め、環境を回して映り込みを流す
         cam=lambda t: (lerp((-1.9, -2.2, 2.05), (-1.75, -2.25, 2.0), ease(t)), RIDGE, 70, 128.0, None)),
    dict(sec=2.5, roll=math.radians(4),    # 押し込み：高い引きから谷へまっすぐ寄る
         cam=lambda t: (lerp((1.3, -8.8, 6.6), (1.0, -7.4, 5.4), ease(t)), Vector((0.7, 1.4, 0.1)), 35, 128.0, None)),
    dict(sec=3.0,                          # 決め：左上から入って hero の構図で止まる
         cam=lambda t: (lerp((-1.3, -5.6, 3.5), HERO_CAM, ease_out(min(1.0, t / 0.6))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES        # 最後のフレーム＝決めのカットが止まったところ＝hero


FLOATERS = [o for o in parts if o.name.startswith(("tongue", "shell"))]


def pose(i, t, T):
    """物の動き：決めの手前まで、舌と入れ子が層ごとに少しずれて浮き沈みする。決めの間は 0（hero と一致）"""
    g = (T * (N_FRAMES - 1)) / max(1, shot_start[-1] - 1)   # 0→1 が決めの頭まで
    for n, o in enumerate(FLOATERS):
        o.location = (0, 0, 0.035 * math.sin(math.pi * min(1.0, g)) * (1 - 0.18 * n)) if g < 1 else (0, 0, 0)


key_light = None


def light_path(i, t):
    """光の走り：2カット目だけ環境を z 軸まわりに −8°→+10° 回す。ほかは 0（hero と同じ映り込み）"""
    ang = math.radians(-8 + 18 * ease(t)) if i == 1 else 0.0
    wmap.inputs["Rotation"].default_value = (0, 0, ang)


for i, sh in enumerate(SHOTS):
    for k in range(sh["frames"]):
        f = shot_start[i] + k
        t = k / max(1, sh["frames"] - 1)
        T = (f - 1) / max(1, N_FRAMES - 1)
        loc, tgt, lens, fstop, focus = sh["cam"](t)
        cam.location = loc
        q = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y')
        from mathutils import Quaternion
        q = q @ Quaternion((0, 0, 1), sh.get("roll", ROLL))
        cam.rotation_euler = q.to_euler()
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
        wmap.inputs["Rotation"].keyframe_insert("default_value", frame=f)
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
# 色収差：明暗の境目の両側に細い橙と青紫の縁（基準の縁取り）。PITFALLS #3 のノードグループ方式
DISPERSION = 0.0
cng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
cng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
c_rl = cng.nodes.new("CompositorNodeRLayers")
c_ld = cng.nodes.new("CompositorNodeLensdist")
c_ld.inputs["Dispersion"].default_value = DISPERSION
c_ld.inputs["Fit"].default_value = True
c_out = cng.nodes.new("NodeGroupOutput")
cng.links.new(c_rl.outputs["Image"], c_ld.inputs["Image"])
cng.links.new(c_ld.outputs["Image"], c_out.inputs["Image"])
scene.compositing_node_group = cng
scene.render.use_compositing = True
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


for nm in os.environ.get("II_HIDE", "").split(","):   # 診断用：指定の面を描かない
    if nm and bpy.data.objects.get(nm):
        bpy.data.objects[nm].hide_render = True

if "dirmap" in modes:   # 診断：画面の各点が映している環境の方向（RGB＝方向*0.5+0.5）
    for l in list(wn):
        if l.type not in ('OUTPUT_WORLD', 'BACKGROUND', 'TEX_COORD'):
            wn.remove(l)
    vm = wn.new("ShaderNodeVectorMath"); vm.operation = 'MULTIPLY_ADD'
    vm.inputs[1].default_value = (0.5, 0.5, 0.5); vm.inputs[2].default_value = (0.5, 0.5, 0.5)
    wl.new(tc.outputs["Generated"], vm.inputs[0]); wl.new(vm.outputs[0], bgn.inputs["Color"])
    for m in bpy.data.materials:
        p = m.node_tree.nodes.get("Principled BSDF")
        if p:
            p.inputs["Base Color"].default_value = (1, 1, 1, 1); p.inputs["Roughness"].default_value = 0.0
            if "Thin Film Thickness" in p.inputs:
                p.inputs["Thin Film Thickness"].default_value = 0
    scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0; scene.cycles.use_denoising = False
    scene.render.image_settings.color_depth = '16'
    still(os.path.join(OUT, "_dir.png"), 480, 16)

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
                              use_selection=True, export_animations=True, export_yup=True,
                              export_apply=True, export_draco_mesh_compression_enable=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
