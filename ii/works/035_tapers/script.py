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

# ------------------------------------------------------------- LOOK（035 TAPERS）
LOOK = dict(
    aspect=(4, 5),
    lens=90,
    fstop=11.0,
    view="Khronos PBR Neutral",
    look="None",
    exposure=-0.35,
    bg=(0.30, 0.31, 0.56),
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


PAPER_HEX = "#6C708C"
PAPER_DARK = "#071632"
GRAD_X, GRAD_Z, GRAD_LO, GRAD_HI = 1.5, 0.6, -0.55, 0.45
GRAD_Y = 1.4
FLOOR_HEX = "#9095B8"
WORLD_STR = 0.02
WAX_ROUGH = 0.40
WAX_SSS = 0.12
KEY_LOC, KEY_SIZE, KEY_E = (0.62, -0.30, 0.52), 0.9, 34
FILL_E = 0.4
WASH_LOC, WASH_TGT, WASH_CONE, WASH_E = (1.6, -0.6, 0.9), (0.55, 0.75, 0.30), 55, 30

# ------------------------------------------------------------- 舞台：藤色の背景紙（左は光が届かず紺に落ちる）
R, W, D, H, WALL_Y = 0.7, 8.0, 3.0, 3.5, 0.75
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 16 * math.pi / 2 for i in range(1, 17)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + WALL_Y - R, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
sweep.data.materials.append(principled("paper", hex_to_linear(PAPER_HEX), rough=0.85))
sweep.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.2
# 塗りのグラデーション：床と右は藤、左上へ行くほど紺（基準の「光の届かない左上」を紙の色で持つ）
_nt = sweep.data.materials[0].node_tree; _pb = _nt.nodes["Principled BSDF"]
_tc = _nt.nodes.new("ShaderNodeTexCoord")
_pn = _nt.nodes.new("ShaderNodeTexNoise"); _pn.inputs["Scale"].default_value = 650; _pn.inputs["Detail"].default_value = 6
_pbmp = _nt.nodes.new("ShaderNodeBump"); _pbmp.inputs["Strength"].default_value = 0.35; _pbmp.inputs["Distance"].default_value = 0.0005
_nt.links.new(_tc.outputs["Object"], _pn.inputs["Vector"]); _nt.links.new(_pn.outputs["Fac"], _pbmp.inputs["Height"])
_nt.links.new(_pbmp.outputs["Normal"], _nt.nodes["Principled BSDF"].inputs["Normal"])
_sep = _nt.nodes.new("ShaderNodeSeparateXYZ"); _nt.links.new(_tc.outputs["Object"], _sep.inputs["Vector"])
_m1 = _nt.nodes.new("ShaderNodeMath"); _m1.operation = 'MULTIPLY_ADD'
_m1.inputs[1].default_value = GRAD_X; _m1.inputs[2].default_value = 0.0
_nt.links.new(_sep.outputs["X"], _m1.inputs[0])
_m2 = _nt.nodes.new("ShaderNodeMath"); _m2.operation = 'MULTIPLY_ADD'
_m2.inputs[1].default_value = -GRAD_Z
_nt.links.new(_sep.outputs["Z"], _m2.inputs[0]); _nt.links.new(_m1.outputs[0], _m2.inputs[2])
_mr = _nt.nodes.new("ShaderNodeMapRange"); _mr.interpolation_type = 'SMOOTHERSTEP'
_mr.inputs["From Min"].default_value = GRAD_LO; _mr.inputs["From Max"].default_value = GRAD_HI
_m3 = _nt.nodes.new("ShaderNodeMath"); _m3.operation = 'MULTIPLY_ADD'
_m3.inputs[1].default_value = -GRAD_Y
_mn = _nt.nodes.new("ShaderNodeMath"); _mn.operation = 'MINIMUM'; _mn.inputs[1].default_value = 0.0
_nt.links.new(_sep.outputs["Y"], _mn.inputs[0]); _nt.links.new(_mn.outputs[0], _m3.inputs[0]); _nt.links.new(_m2.outputs[0], _m3.inputs[2])
_nt.links.new(_m3.outputs[0], _mr.inputs["Value"])
_mix = _nt.nodes.new("ShaderNodeMix"); _mix.data_type = 'RGBA'
_mix.inputs[6].default_value = hex_to_linear(PAPER_DARK); _mix.inputs[7].default_value = hex_to_linear(PAPER_HEX)
_nt.links.new(_mr.outputs["Result"], _mix.inputs[0])
_fl = _nt.nodes.new("ShaderNodeMapRange"); _fl.interpolation_type = 'SMOOTHSTEP'
_fl.inputs["From Min"].default_value = 0.1; _fl.inputs["From Max"].default_value = -0.45
_nt.links.new(_sep.outputs["Y"], _fl.inputs["Value"])
_mix2 = _nt.nodes.new("ShaderNodeMix"); _mix2.data_type = 'RGBA'
_nt.links.new(_fl.outputs["Result"], _mix2.inputs[0]); _nt.links.new(_mix.outputs[2], _mix2.inputs[6])
_mix2.inputs[7].default_value = hex_to_linear(FLOOR_HEX)
_nt.links.new(_mix2.outputs[2], _pb.inputs["Base Color"])

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hex_to_linear("#0B1A3A")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = WORLD_STR


# ------------------------------------------------------------- 被写体：真鍮の台に挿したテーパーキャンドル11本
def lathe(profile, segs=64, z0=0.0):
    """profile=[(r,z)] 下から上。r=0 の点は極に潰す"""
    vs, fs, rings = [], [], []
    for (r, z) in profile:
        if r <= 1e-6:
            rings.append([len(vs)]); vs.append((0, 0, z + z0)); continue
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            ring.append(len(vs)); vs.append((r * math.cos(a), r * math.sin(a), z + z0))
        rings.append(ring)
    for A, B in zip(rings[:-1], rings[1:]):
        if len(A) == 1:
            for k in range(segs):
                fs.append((A[0], B[k], B[(k + 1) % segs]))
        elif len(B) == 1:
            for k in range(segs):
                fs.append((A[k], A[(k + 1) % segs], B[0]))
        else:
            for k in range(segs):
                fs.append((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    return vs, fs


def candle_profile(L, r0=0.0108, r1=0.0098, tip=0.022):
    p = [(0.0, 0.0), (r0 - 0.0012, 0.0), (r0 - 0.0003, 0.0003), (r0, 0.0012)]
    body_top = L - tip
    for i in range(1, 13):
        z = 0.0012 + (body_top - 0.0012) * i / 12
        p.append((r0 + (r1 - r0) * i / 12, z))
    # 鉛筆削りの肩：丸く入って円錐、先は小さく平ら
    for i in range(1, 15):
        s = i / 14
        rr = r1 * (1 - s) ** 1.15 + 0.0026 * s
        if s < 0.18:
            rr = r1 - (r1 - (r1 * (1 - 0.18) ** 1.15 + 0.0026 * 0.18)) * (s / 0.18) ** 2
        p.append((rr, body_top + tip * s))
    p.append((0.0019, L + 0.0004)); p.append((0.0, L + 0.0006))
    return p


def wick_geo(L, segs=12):
    vs, fs = [], []
    pts_ = [(0.0, 0.0, L - 0.002), (0.0002, 0.0, L + 0.0035), (0.0007, 0.0, L + 0.0065), (0.0012, 0.0002, L + 0.0085)]
    rings = []
    for j, (x, y, z) in enumerate(pts_):
        rw = (0.00115, 0.00110, 0.00125, 0.00175)[j]
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            rr = rw * ((1.0 + 0.55 * (k % 3 == 0)) if j == 3 else 1.0)
            zz = z + (0.0012 * ((k * 7) % 5) / 4 if j == 3 else 0)
            ring.append(len(vs)); vs.append((x + rr * math.cos(a), y + rr * math.sin(a), zz))
        rings.append(ring)
    for A, B in zip(rings[:-1], rings[1:]):
        for k in range(segs):
            fs.append((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    top = len(vs); x, y, z = pts_[-1]; vs.append((x + 0.0003, y, z + 0.0006))
    for k in range(segs):
        fs.append((rings[-1][k], rings[-1][(k + 1) % segs], top))
    return vs, fs


def wax(name, hexc):
    m = principled(name, hex_to_linear(hexc), rough=WAX_ROUGH)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Subsurface Weight"].default_value = WAX_SSS
    p.inputs["Subsurface Radius"].default_value = (1.0, 0.7, 0.5)
    p.inputs["Subsurface Scale"].default_value = 0.004
    p.inputs["Specular IOR Level"].default_value = 0.42
    # 蝋の肌：浸し塗りの細かい揺れ（バンプ）
    nt = m.node_tree
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 260
    nz.inputs["Detail"].default_value = 3
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.05
    bp.inputs["Distance"].default_value = 0.0004
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


wick_mat = principled("wick", hex_to_linear("#E6E0D0"), rough=1.0)
_w = wick_mat.node_tree; _wp = _w.nodes["Principled BSDF"]
_wp.inputs["Sheen Weight"].default_value = 1.0; _wp.inputs["Sheen Roughness"].default_value = 0.6
_wp.inputs["Specular IOR Level"].default_value = 0.1
_wn = _w.nodes.new("ShaderNodeTexWave"); _wn.wave_type = 'BANDS'; _wn.bands_direction = 'Z'
_wn.inputs["Scale"].default_value = 900; _wn.inputs["Distortion"].default_value = 8
_wb = _w.nodes.new("ShaderNodeBump"); _wb.inputs["Strength"].default_value = 0.8; _wb.inputs["Distance"].default_value = 0.0004
_w.links.new(_wn.outputs["Fac"], _wb.inputs["Height"]); _w.links.new(_wb.outputs["Normal"], _wp.inputs["Normal"])

HOLDER_R, HOLDER_H = 0.070, 0.030
prof = [(0.0, 0.0), (HOLDER_R - 0.004, 0.0), (HOLDER_R, 0.004), (HOLDER_R + 0.0015, HOLDER_H * 0.55),
        (HOLDER_R, HOLDER_H - 0.003), (HOLDER_R - 0.004, HOLDER_H), (0.0, HOLDER_H)]
vs, fs = lathe(prof, 128)
hm = bpy.data.meshes.new("holder_me"); hm.from_pydata(vs, [], fs); hm.update()
holder = bpy.data.objects.new("holder", hm); scene.collection.objects.link(holder)
for p in hm.polygons:
    p.use_smooth = True
brass = principled("brass", hex_to_linear("#9A7A45"), rough=0.36, metal=1.0)
nt = brass.node_tree; pb = nt.nodes["Principled BSDF"]
nz = nt.nodes.new("ShaderNodeTexWave"); nz.wave_type = 'RINGS'; nz.inputs["Scale"].default_value = 900; nz.inputs["Distortion"].default_value = 2; nz.inputs["Detail"].default_value = 4
mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.02, 0.02, 1)   # 旋盤の挽き目（周方向）
tc = nt.nodes.new("ShaderNodeTexCoord")
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.16; mr.inputs["To Max"].default_value = 0.42
nt.links.new(nz.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], pb.inputs["Roughness"])
_hb = nt.nodes.new("ShaderNodeBump"); _hb.inputs["Strength"].default_value = 0.05; _hb.inputs["Distance"].default_value = 0.00015
nt.links.new(nz.outputs["Fac"], _hb.inputs["Height"]); nt.links.new(_hb.outputs["Normal"], pb.inputs["Normal"])
hm.materials.append(brass)

# 11本：外周8本は外へ開き、中の3本はほぼ立つ（色は基準の組み立て＝寒色の地に暖色を点で）
CANDLES = [
    # (方位deg, 台上の半径, 傾きdeg, 長さ, 色)
    (200, 0.044, 21, 0.300, "#8E1A33"),   # 赤
    (245, 0.046, 16, 0.318, "#1E4A36"),   # 深緑
    (290, 0.044, 19, 0.288, "#E6B8C0"),   # 桃
    (335, 0.046, 23, 0.296, "#E24E1B"),   # 橙
    (20,  0.050, 17, 0.310, "#D8CA7C"),   # 黄
    (65,  0.052, 22, 0.292, "#6A2D88"),   # 紫
    (110, 0.044, 15, 0.322, "#7FA374"),   # 若草
    (155, 0.046, 20, 0.304, "#2D5B9A"),   # 群青
    (90,  0.018, 5,  0.336, "#EAE0C6"),   # アイボリー
    (210, 0.018, 7,  0.328, "#6B1525"),   # ボルドー
    (330, 0.018, 4,  0.344, "#C9B88F"),   # 砂
]
SINK = 0.016
candles, seats, sockets = [], [], []
socket_mat = principled("socket", hex_to_linear("#4A3618"), rough=0.4, metal=1.0)
from mathutils import Matrix
for i, (az, rad, tilt, L, col) in enumerate(CANDLES):
    vs, fs = lathe(candle_profile(L), 48)
    wv, wf = wick_geo(L)
    off = len(vs); vs += wv; fs += [tuple(v + off for v in f) for f in wf]
    cm = bpy.data.meshes.new("c%d_me" % i); cm.from_pydata(vs, [], fs); cm.update()
    cm.materials.append(wax("wax%d" % i, col)); cm.materials.append(wick_mat)
    nwick = len(wf)
    for k, p in enumerate(cm.polygons):
        p.use_smooth = True
        p.material_index = 1 if k >= len(cm.polygons) - nwick else 0
    ob = bpy.data.objects.new("candle%d" % i, cm); scene.collection.objects.link(ob)
    a = math.radians(az)
    base = Vector((rad * math.cos(a), rad * math.sin(a), HOLDER_H - SINK))
    # 外へ傾ける：方位の向きに倒す＝軸 (−sin, cos, 0) まわりに tilt
    axis = Vector((-math.sin(a), math.cos(a), 0))
    from mathutils import Matrix
    rot = Matrix.Rotation(math.radians(tilt), 4, axis).to_euler()
    ob.rotation_mode = 'XYZ'
    ob.location = base; ob.rotation_euler = rot
    ob["wick_spin"] = 0
    seats.append((base.copy(), Vector(rot[:]), L))
    candles.append(ob)
    # 挿し口：天面に暗い座金の輪（蝋燭の足を受ける口金）
    hit = base + Vector(ax_dir := (Matrix.Rotation(math.radians(tilt), 4, axis) @ Vector((0, 0, 1)))) * (SINK / max(0.5, ax_dir.z))
    sv, sf = lathe([(0.0104 / max(0.5, ax_dir.z) ** 0.5, 0.0), (0.0128, 0.0), (0.0138, -0.0008)], 48)
    smh = bpy.data.meshes.new("s%d_me" % i); smh.from_pydata(sv, [], sf); smh.update()
    for p in smh.polygons:
        p.use_smooth = True
    smh.materials.append(socket_mat)
    so = bpy.data.objects.new("socket%d" % i, smh); scene.collection.objects.link(so)
    so.location = (hit.x, hit.y, HOLDER_H + 0.0004)
    sockets.append(so)

parts = [holder] + candles + sockets   # 🔴 被写体は全部ここへ

# ------------------------------------------------------------- 光：右手前の大きな柔光1灯＋背景紙だけを起こすスポット
key = area("key", KEY_LOC, KEY_SIZE, KEY_E, (1.0, 0.97, 0.94), target=(0, 0, 0.17))
fill = area("fill", (-1.3, -1.6, 0.5), 2.0, FILL_E, (0.80, 0.85, 1.0), target=(0, 0, 0.17))
sd = bpy.data.lights.new("wash", 'SPOT'); sd.energy = WASH_E; sd.spot_size = math.radians(WASH_CONE)
sd.spot_blend = 1.0; sd.shadow_soft_size = 0.4; sd.color = (0.92, 0.92, 1.0)
wash = bpy.data.objects.new("wash", sd); scene.collection.objects.link(wash)
wash.location = WASH_LOC
wash.rotation_euler = (Vector(WASH_TGT) - Vector(WASH_LOC)).to_track_quat('-Z', 'Y').to_euler()
# ウォッシュは背景紙だけ（被写体に当てると左右の明暗が消える）
lc = bpy.data.collections.new("paper_only"); lc.objects.link(sweep)
wash.light_linking.receiver_collection = lc
wash.light_linking.blocker_collection = lc
key_light = None
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

# 各カット：sec／cam(t)→(位置, 注視点, レンズ, f値, ピント or None)
TGT = Vector((0.012, 0.0, 0.175))
HERO_CAM = Vector((-0.10, -1.24, 0.42))


def tip_of(i):
    b, r, L = seats[i]
    from mathutils import Euler
    return b + Euler(r).to_matrix() @ Vector((0, 0, L))


def macro_cam(t):
    a, b = tip_of(8), tip_of(10)
    tgt = a.lerp(b, ease(t)) + Vector((0, 0, -0.004))
    loc = tgt + Vector((-0.10 + 0.08 * ease(t), -0.46, 0.015))
    near = (a - loc).length
    far = (b - loc).length
    u = max(0.0, min(1.0, (t - 0.25) / 0.5))
    return loc, tgt, 135, 2.8, near + (far - near) * ease(u)


SHOTS = [
    dict(sec=3.0,   # 物の動き：やや引きの横位置から、1本ずつ上から台へ降りて挿さる
         cam=lambda t: (lerp((0.50, -1.10, 0.20), (0.38, -1.16, 0.23), ease(t)), Vector((0, 0, 0.215)),
                        60, 6.0, None)),
    dict(sec=3.0,   # マクロ：芯の先を横になめ、ピントを手前の芯（アイボリー）から奥の芯（砂）へ送る
         cam=lambda t: macro_cam(t)),
    dict(sec=2.5,   # 押し込み：床すれすれから台の縁へ寄る（真鍮の挽き目と、蝋の根元）
         cam=lambda t: (lerp((0.62, -0.62, 0.035), (0.33, -0.33, 0.045), ease(t)), Vector((0.0, 0.0, 0.105)),
                        50, 3.2, None)),
    dict(sec=3.0,   # 決め：左上から降りながら入って hero の構図で止まる
         cam=lambda t: (lerp((-0.42, -1.25, 0.42), HERO_CAM, ease_out(min(1.0, t / 0.6))), TGT,
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

DROP_ORDER = [8, 9, 10, 3, 0, 5, 6, 1, 4, 7, 2]


def pose(i, t, T):
    from mathutils import Euler
    for k, ob in enumerate(candles):
        b, r, L = seats[k]
        ax = Euler(r).to_matrix() @ Vector((0, 0, 1))
        if i == 0:
            j = DROP_ORDER.index(k)
            s0 = 0.04 + j * 0.055
            u = max(0.0, min(1.0, (t - s0) / 0.30))
            lift = 0.42 * (1 - ease_out(u))
        else:
            lift = 0.0
        ob.location = b + ax * lift
        ob.rotation_euler = r


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
