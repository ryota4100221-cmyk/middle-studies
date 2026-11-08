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

def hex_to_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


# ------------------------------------------------------------- LOOK（毎回決める）
LOOK = dict(
    aspect=(5, 7),
    lens=60,
    fstop=5.6,
    view="Standard",          # 白地の製品写真は Standard＋露出マイナス（PITFALLS [II] 122）
    look="None",
    exposure=-0.2,
    bg=hex_to_linear("#8F8E8C"),
)
SWEEP_Y = 3.5
WORLD_FILL = 0.25
STONE_A, STONE_B, PORE_COL, CORE_COL = "#EAE8E1", "#DDD5C3", "#DDB985", "#8F6F45"
PORE_STRETCH, PORE_SCALE, PORE_T = 3.0, 15.0, 0.625
BAND_SCALE, BAND_T = 3.2, 0.47
DOT_SCALE, DOT_R = 45.0, 0.07
BUMP_S, BUMP_D = 1.0, 0.06
VEIN_X, VEIN_K = 30.0, 0.35
PIN_SCALE, PIN_R = 150.0, 0.17
CAV_SCALE, CAV_T = 5.0, 0.70
STONE_ROUGH = 0.62
RECESS = 0.08
KEY_LOC, KEY_SIZE, KEY_E = (8.0, 0.5, 7.5), 14.0, 1800
BOUNCE_E = 120
WASH_E = 0
KEYF_E = 0
KEYF_SIZE = 14.0
WASH_SPREAD = 180
HERO_TGT, HERO_DIST, HERO_AZ, HERO_EL = (0.05, 0.2, 1.0), 9.6, -8, 26
FPS = 24
# 尺（N_FRAMES）と静止画のフレーム（STILL_FRAME）は、下の「動画」節の SHOTS から決まる

# 納品寸法：長辺で決める（hero 2560 / loop 1080）
def res(long_side):
    a, b = LOOK["aspect"]
    if a >= b:
        return long_side, round(long_side * b / a / 2) * 2
    return round(long_side * a / b / 2) * 2, long_side





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
    L.visible_camera = False      # 光の走りで面光源そのものが写り込むのを止める
    return L


# ------------------------------------------------------------- 舞台：明るい灰白の無限背景紙
R, W, D, H = 7.0, 40.0, 14.0, 20.0
pts = [(-D, 0.0), (0.0, 0.0)] + [(R * math.sin(t), R - R * math.cos(t)) for t in
                                  [i / 16 * math.pi / 2 for i in range(1, 17)]] + [(R, H)]
verts, faces = [], []
for x in (-W / 2, W / 2):
    for (y, z) in pts:
        verts.append((x, y + SWEEP_Y, z))
n = len(pts)
for i in range(n - 1):
    faces.append((i, i + 1, n + i + 1, n + i))
me = bpy.data.meshes.new("sweep_me")
me.from_pydata(verts, [], faces); me.update()
sweep = bpy.data.objects.new("sweep", me); scene.collection.objects.link(sweep)
for p in me.polygons:
    p.use_smooth = True
sweep.data.materials.append(principled("paper", LOOK["bg"], rough=0.8))

world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = WORLD_FILL


# ------------------------------------------------------------- 素材：研ぎ出しのトラバーチン
def travertine(name, base_a, base_b, pore_col, core_col, seed=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")

    def mapped(scale, loc=(0, 0, 0)):
        mp = N.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = scale
        mp.inputs["Location"].default_value = loc
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        return mp

    def noise(vec, scale, detail=4.0, rough=0.55):
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = detail
        nz.inputs["Roughness"].default_value = rough
        L.new(vec.outputs["Vector"], nz.inputs["Vector"])
        return nz

    def rng(sock, a, b):
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = a
        mr.inputs["From Max"].default_value = b
        L.new(sock, mr.inputs["Value"])
        return mr.outputs["Result"]

    def math_(op, a, b):
        mt = N.new("ShaderNodeMath"); mt.operation = op
        mt.use_clamp = True
        for k, s in enumerate((a, b)):
            if isinstance(s, float):
                mt.inputs[k].default_value = s
            else:
                L.new(s, mt.inputs[k])
        return mt.outputs[0]

    # 流れの方向＝y（手前→奥）。孔は y に長く、x と z に細い
    long_pores = noise(mapped((PORE_STRETCH, 1.0, PORE_STRETCH), (seed, 0, 0)), PORE_SCALE, 3.0, 0.5)
    band = noise(mapped((1.0, 0.0, 0.25), (seed + 3.1, 0, 0)), BAND_SCALE, 2.0, 0.5)
    p_long = rng(long_pores.outputs["Fac"], PORE_T, PORE_T + 0.05)
    p_band = rng(band.outputs["Fac"], BAND_T, BAND_T + 0.12)
    pores1 = math_('MULTIPLY', p_long, p_band)
    core = math_('MULTIPLY', rng(long_pores.outputs["Fac"], PORE_T + 0.05, PORE_T + 0.09), p_band)
    # まばらな大きい空洞（帯の中だけ）
    cav = noise(mapped((2.5, 1.0, 2.5), (seed + 9.1, 0, 0)), CAV_SCALE, 2.0, 0.45)
    cav1 = math_('MULTIPLY', rng(cav.outputs["Fac"], CAV_T, CAV_T + 0.03), p_band)
    cav2 = math_('MULTIPLY', rng(cav.outputs["Fac"], CAV_T + 0.03, CAV_T + 0.07), p_band)
    cavd = math_('MULTIPLY', rng(cav.outputs["Fac"], CAV_T, CAV_T + 0.14), p_band)
    pores1 = math_('MAXIMUM', pores1, cav1)
    core = math_('MAXIMUM', core, cav2)
    # 地全体に散る小さい孔
    vor = N.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = DOT_SCALE
    L.new(mapped((1.0, 0.45, 1.0), (seed, 0, 0)).outputs["Vector"], vor.inputs["Vector"])
    dots = rng(vor.outputs["Distance"], DOT_R, DOT_R - 0.05)
    dmask = rng(noise(mapped((1, 1, 1), (seed + 7.7, 0, 0)), 9.0).outputs["Fac"], 0.56, 0.64)
    pores2 = math_('MULTIPLY', dots, dmask)
    pores = math_('MAXIMUM', pores1, pores2)
    pin = N.new("ShaderNodeTexVoronoi")
    pin.inputs["Scale"].default_value = PIN_SCALE
    pin.inputs["Randomness"].default_value = 1.0
    L.new(mapped((1.0, 0.7, 1.0), (seed + 2.2, 0, 0)).outputs["Vector"], pin.inputs["Vector"])
    pmask = rng(noise(mapped((1, 1, 1), (seed + 4.4, 0, 0)), 30.0).outputs["Fac"], 0.42, 0.50)
    pins = math_('MULTIPLY', rng(pin.outputs["Distance"], PIN_R, PIN_R - 0.06), pmask)
    pores = math_('MAXIMUM', pores, math_('MULTIPLY', pins, 0.6))
    # 地色：低い周波数のむら＋流れ方向の淡い縞
    mott = noise(mapped((1.0, 0.25, 1.0), (seed + 1.3, 0, 0)), 2.2, 5.0, 0.6)
    mix_base = N.new("ShaderNodeMix"); mix_base.data_type = 'RGBA'
    # 流れ方向の細い筋（y に長く x に極細）と、帯ごとの淡い濃淡
    vein = noise(mapped((VEIN_X, 0.6, VEIN_X), (seed + 5.5, 0, 0)), 1.0, 6.0, 0.6)
    veins = rng(vein.outputs["Fac"], 0.56, 0.66)
    tone = math_('MAXIMUM', rng(mott.outputs["Fac"], 0.35, 0.68), math_('MULTIPLY', veins, VEIN_K))
    L.new(tone, mix_base.inputs[0])
    mix_base.inputs[6].default_value = base_a
    mix_base.inputs[7].default_value = base_b
    mix_p = N.new("ShaderNodeMix"); mix_p.data_type = 'RGBA'
    L.new(pores, mix_p.inputs[0])
    L.new(mix_base.outputs[2], mix_p.inputs[6])
    mix_p.inputs[7].default_value = pore_col
    mix_c = N.new("ShaderNodeMix"); mix_c.data_type = 'RGBA'
    L.new(core, mix_c.inputs[0])
    L.new(mix_p.outputs[2], mix_c.inputs[6])
    mix_c.inputs[7].default_value = core_col
    L.new(mix_c.outputs[2], p.inputs["Base Color"])
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = BUMP_S
    bump.inputs["Distance"].default_value = BUMP_D
    bump.invert = True
    hgt = N.new("ShaderNodeMath"); hgt.operation = 'MAXIMUM'
    L.new(math_('MULTIPLY', pores, 0.6), hgt.inputs[0]); L.new(math_('MULTIPLY', cavd, 1.0), hgt.inputs[1])
    L.new(hgt.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = STONE_ROUGH
    return m


stone = travertine("stone", hex_to_linear(STONE_A), hex_to_linear(STONE_B), hex_to_linear(PORE_COL), hex_to_linear(CORE_COL))
stone2 = travertine("stone2", hex_to_linear(STONE_A), hex_to_linear(STONE_B), hex_to_linear(PORE_COL), hex_to_linear(CORE_COL), seed=11.0)


# ------------------------------------------------------------- 被写体：石の盆＋小さな花器＋枯れ穂
def box(name, size, loc):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    return o


def round_plan(ob, r, seg=12):
    """平面の角（鉛直の稜）だけを丸める"""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    es = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().z) > 0.99]
    bmesh.ops.bevel(bm, geom=es, offset=r, segments=seg, profile=0.5, affect='EDGES', clamp_overlap=True)
    bm.to_mesh(ob.data); bm.free()


def boolean(target, cutter):
    md = target.modifiers.new("b", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cutter
    md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter)


TW, TD, TH = 3.0, 1.9, 0.22
tray = box("tray", (TW, TD, TH), (0, 0, TH / 2))
round_plan(tray, 0.16, 10)
# くぼみ：左手前に長円の浅い溝（底の縁は丸く）
cut = box("cut", (1.75, 0.82, 0.6), (-0.42, -0.18, TH - RECESS + 0.3))
round_plan(cut, 0.405, 16)
bevel_obj(cut, 0.06, segments=6, angle=30)
boolean(tray, cut)
bevel_obj(tray, 0.014, segments=3, clamp=False, angle=30)
tray.data.materials.clear(); tray.data.materials.append(stone)

VX, VY, VR, VH = 0.92, 0.40, 0.30, 0.95
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=VR, depth=VH, location=(VX, VY, TH + VH / 2))
vase = bpy.context.object; vase.name = "vase"
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.055, depth=1.4, location=(VX, VY, TH + VH))
boolean(vase, bpy.context.object)
bevel_obj(vase, 0.018, segments=3, clamp=False, angle=30)
vase.data.materials.clear(); vase.data.materials.append(stone2)

# 枯れ穂：細い茎＋細長い穂
cu = bpy.data.curves.new("stem_cu", 'CURVE'); cu.dimensions = '3D'
cu.bevel_depth = 0.011; cu.bevel_resolution = 4; cu.use_fill_caps = True
sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
base = Vector((VX, VY, TH + VH - 0.5))
ctrl = [base, base + Vector((-0.05, 0.0, 1.25)), base + Vector((-0.24, 0.02, 2.15))]
for bp, c in zip(sp.bezier_points, ctrl):
    bp.co = c; bp.handle_left_type = bp.handle_right_type = 'AUTO'
stem = bpy.data.objects.new("stem", cu); scene.collection.objects.link(stem)
stem_mat = principled("stem", hex_to_linear("#3A2E25"), rough=0.5)
stem.data.materials.append(stem_mat)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0, location=ctrl[-1] + Vector((-0.035, 0, 0.17)))
head = bpy.context.object; head.name = "head"
head.scale = (0.034, 0.034, 0.20); head.rotation_euler = (0, math.radians(-12), 0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
for p in head.data.polygons:
    p.use_smooth = True
head.data.materials.append(principled("head", hex_to_linear("#5A4634"), rough=0.6))
# 穂と茎は花器の口を支点に揺れる
pivot = bpy.data.objects.new("pivot", None); scene.collection.objects.link(pivot)
pivot.location = (VX, VY, TH + VH)
bpy.context.view_layer.update()
for o in (stem, head):
    mw = o.matrix_world.copy(); o.parent = pivot; o.matrix_world = mw
parts = [tray, vase, stem, head]

# ------------------------------------------------------------- 光：右上前方の大きく柔らかい1灯
KEY_HOME = Vector(KEY_LOC)
key = area("key", KEY_HOME, KEY_SIZE, KEY_E, (1.0, 0.99, 0.975), target=(0, 0, 0.3))
bounce = area("bounce", (-6, -4, 3), 6.0, BOUNCE_E, (1, 1, 1), target=(0, 0, 0.3))
# 壁だけを洗う光（被写体には当てない＝PITFALLS [II] 122）
wash = area("wash", (0, -25, 1.2), 30.0, WASH_E, (1, 1, 1), target=(0, SWEEP_Y, 3.0))
wash.data.spread = math.radians(WASH_SPREAD)
wcoll = bpy.data.collections.new("wash_recv")
wcoll.objects.link(sweep)
wash.light_linking.receiver_collection = wcoll
# 石を照らすキーは被写体だけ、床の影は同じ位置の弱い光（受け手＝背景紙だけ）が落とす
pcoll = bpy.data.collections.new("key_recv")
for o in parts:
    pcoll.objects.link(o)
# （027 round 6〜）キーは石も床も照らす＝紙の反射率で地を落とす
key_floor = area("key_floor", KEY_HOME, KEYF_SIZE, KEYF_E, (1, 1, 1), target=(0, 0, 0.3))
key_floor.light_linking.receiver_collection = wcoll

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


def sph(target, dist, az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector(target) + Vector((dist * math.cos(e) * math.sin(a), -dist * math.cos(e) * math.cos(a), dist * math.sin(e)))


HERO_T = Vector(HERO_TGT)
HERO_C = sph(HERO_T, HERO_DIST, HERO_AZ, HERO_EL)
SHOTS = [
    dict(sec=2.8,   # 押し込み：花器の口から穂の頭へ、寄りながら上がる
         cam=lambda t: (lerp(sph((VX, VY, 1.2), 6.8, 30, 8), sph((VX - 0.2, VY, 2.9), 3.4, 22, 4), ease(t)),
                        lerp((VX, VY, 1.2), (VX - 0.2, VY, 2.95), ease(t)), 85, 2.8, None)),
    dict(sec=3.0,   # マクロ：盆の小口を左から右へなめる＋ピント送り
         cam=lambda t: (lerp((-1.3, -2.25, 0.36), (-0.2, -2.15, 0.30), ease(t)), lerp((-0.75, -0.95, 0.14), (0.35, -0.95, 0.12), ease(t)),
                        135, 2.2, None)),
    dict(sec=2.7,   # 光の走り：真上寄りから溝を見て、光が回る
         cam=lambda t: (lerp((-0.55, -2.4, 3.6), (-0.30, -2.3, 3.7), ease(t)), Vector((-0.35, -0.15, 0.15)), 70, 5.0, None)),
    dict(sec=3.5,   # 決め：寄りから引きながら回り込んで止まる
         cam=lambda t: (lerp(sph(HERO_T, HERO_DIST * 0.8, HERO_AZ - 14, HERO_EL + 5), HERO_C, ease_out(min(1.0, t / 0.6))),
                        HERO_T, LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES


def pose(i, t, T):
    # 穂がかすかに揺れて、決めで止まる
    damp = 1.0 if i < 3 else (1 - ease(min(1.0, t / 0.6)))
    pivot.rotation_euler = (math.radians(1.2 * math.sin(T * 2 * math.pi * 1.6)) * damp, math.radians(2.0 * math.sin(T * 2 * math.pi * 1.1 + 0.7)) * damp, 0)
    for o in (stem, head):
        pass


key_light = key


def light_path(i, t):
    if i == 2:
        key.location = lerp(Vector((-8.0, 4.0, 5.0)), Vector((8.0, 4.0, 5.0)), ease(t))
    else:
        key.location = KEY_HOME
    # 🔴 大きい面光源は向きごと動かす（向きを固定して動かすと板が盆と床を貫いて画面が白く飛ぶ）
    key.rotation_euler = (Vector((0, 0, 0.3)) - key.location).to_track_quat('-Z', 'Y').to_euler()
    fr = shot_start[i] + round(t * (SHOTS[i]["frames"] - 1))
    key.keyframe_insert("rotation_euler", frame=fr)
    # 真後ろに来た瞬間の照り返しで飛ばないよう、光の走りの中盤だけ光量を絞る
    key.data.energy = KEY_E * ((1 - 0.72 * math.sin(math.pi * t)) if i == 2 else 1.0)
    key.data.keyframe_insert("energy", frame=fr)
    key_floor.location = key.location
    key_floor.keyframe_insert("location", frame=shot_start[i] + round(t * (SHOTS[i]["frames"] - 1)))


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
        pivot.keyframe_insert("rotation_euler", frame=f)
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
    names = {o.name for o in parts} | {"pivot"}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"), export_format='GLB',
                              use_selection=True, export_animations=True, export_yup=True)
    print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
