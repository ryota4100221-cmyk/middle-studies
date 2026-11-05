# =============================================================
# MIDDLE STUDIES II 026 DRIFT（2026-11-06）— 雛形から
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

# ------------------------------------------------------------- LOOK（026 DRIFT）
LOOK = dict(
    aspect=(1, 1),
    lens=100,
    fstop=8.0,
    view="Standard",
    look="None",
    exposure=-2.15,
    bg=(0.62, 0.68, 0.68),
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
import random
rng = random.Random(26)

# ------------------------------------------------------------- 壁（正対・y=0 の面、手前が -Y）
WALL = 30.0
me = bpy.data.meshes.new("wall_me")
me.from_pydata([(-WALL, 0, -WALL), (WALL, 0, -WALL), (WALL, 0, WALL), (-WALL, 0, WALL)], [], [(0, 1, 2, 3)])
wall = bpy.data.objects.new("wall", me); scene.collection.objects.link(wall)
wm = bpy.data.materials.new("wall"); wm.use_nodes = True
nt = wm.node_tree; p = nt.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = LOOK["bg"] + (1.0,)
p.inputs["Roughness"].default_value = 0.85
p.inputs["Specular IOR Level"].default_value = 0.05
# 塗り壁のごく弱い凹凸
tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = 900; tx.inputs["Detail"].default_value = 4
bm_ = nt.nodes.new("ShaderNodeBump"); bm_.inputs["Strength"].default_value = 0.04
nt.links.new(tx.outputs["Fac"], bm_.inputs["Height"]); nt.links.new(bm_.outputs["Normal"], p.inputs["Normal"])
wall.data.materials.append(wm)

# ------------------------------------------------------------- ガラス片の配置（自分で起こした「斜めに流れる帯」）
# 回した座標 (s, q)：s が帯の長手。帯の芯は q_c(s) で波打ち、幅は両端で細る＝羽・流れ
ROT = math.radians(32)
SPACING = 0.040
HALF = 0.62


def band(x, z):
    s = x * math.cos(ROT) + z * math.sin(ROT)
    q = -x * math.sin(ROT) + z * math.cos(ROT)
    qc = 0.13 * math.sin(3.4 * s + 0.6) + 0.04 * math.sin(7.1 * s)
    L = 0.80
    if abs(s) >= L:
        return s, q, qc, 0.0
    hw = 0.40 * (1 - (s / L) ** 2) ** 0.6 * (0.85 + 0.15 * math.sin(5.3 * s + 1.2))
    return s, q, qc, hw


fins_v, fins_f, fins_alt, fin_attr = [], [], [], []
pins_v, pins_f = [], []
TURN = math.radians(38)       # 物の動き：シェイプキーで、全片がピンを軸に回る量


def rot_about(v, axis, ang):
    return v.copy() @ Matrix.Rotation(-ang, 3, axis) if False else Matrix.Rotation(ang, 3, axis) @ v


from mathutils import Matrix
# 流れの線（行）：大きく波打つ流線を等間隔に重ね、楕円（縁はゆらぐ）で切る＝風が水面を渡る
ROT = math.radians(14)
GAP = 0.064
STEP = 0.056
RAD = 0.66


def wave(s, j):
    return 0.17 * math.sin(4.1 * s + 0.10 * j + 0.4) + 0.03 * math.sin(9.0 * s + 0.05 * j)


pts = []
for j in range(-14, 15):
    if j in (-5, 4):
        continue
    s = -0.95 + (rng.random() * STEP if j % 2 else STEP * 0.5)
    while s < 0.95:
        q = j * GAP + wave(s, j)
        x = s * math.cos(ROT) - q * math.sin(ROT)
        z = s * math.sin(ROT) + q * math.cos(ROT)
        s2 = s + 0.004
        q2 = j * GAP + wave(s2, j)
        x2 = s2 * math.cos(ROT) - q2 * math.sin(ROT)
        z2 = s2 * math.sin(ROT) + q2 * math.cos(ROT)
        th_row = math.atan2(z2 - z, x2 - x)
        ang = math.atan2(z, x)
        rr = RAD * (1 + 0.06 * math.sin(3 * ang + 0.7) + 0.04 * math.sin(5 * ang - 1.1))
        r = math.hypot(x / 1.0, z / 0.94)
        if r < rr:
            e = r / rr
            k = 1.0 - 0.55 * max(0.0, e - 0.55) / 0.45
            d = max(-1.0, min(1.0, z / RAD))
            pts.append((x, z, x / RAD, d, th_row + (0.0 if j % 2 else math.radians(-68)), k * (1.0 if j % 2 else 0.85), j % 2))
        s += STEP
cx = (max(p[0] for p in pts) + min(p[0] for p in pts)) / 2
cz = (max(p[1] for p in pts) + min(p[1] for p in pts)) / 2
count = 0
for (x, z, s, d, th_row, k, odd) in pts:
        x -= cx; z -= cz
        th = th_row + math.radians(34) + rng.uniform(-0.05, 0.05)     # 羽枝のように行へ斜めに立つ
        LANG = math.atan2(2.6, 2.4)
        dlt = (th - LANG + math.pi / 2) % math.pi - math.pi / 2
        if abs(dlt) < math.radians(22):
            th += math.radians(30) * (1 if dlt >= 0 else -1)
        u = Vector((math.cos(th), 0, math.sin(th)))
        n = Vector((0, -1, 0))
        tilt = math.radians(rng.uniform(-8, 8) + (0 if odd else 12))
        n2 = Matrix.Rotation(tilt, 3, u) @ n
        v = u.cross(n2).normalized()
        w, wt, dd, t = 0.066 * k, 0.046 * k, 0.058 * k, 0.003
        sl = 0.016 * k
        base = Vector((x, 0, z)) + n * 0.0025
        prof = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2 - sl, dd), (w / 2 - sl - wt, dd)]
        loc = []
        for side in (-t / 2, t / 2):
            for (a_, b_) in prof:
                loc.append(u * a_ + n2 * b_ + v * side)
        i0 = len(fins_v)
        for pv in loc:
            fins_v.append(base + pv)
            fins_alt.append(base + Matrix.Rotation(TURN, 3, n) @ pv)
        F = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        for f in F:
            fins_f.append(tuple(i0 + jj for jj in f))
        hue = (0.0 + 0.35 * s + 0.10 * d + rng.uniform(-0.27, 0.27)) % 1.0
        fin_attr.append((hue, rng.random()))
        j0 = len(pins_v); seg = 6
        for yy in (0.0, -0.004):
            for m in range(seg):
                ang = 2 * math.pi * m / seg
                pins_v.append(Vector((x + 0.0006 * math.cos(ang), yy, z + 0.0006 * math.sin(ang))))
        for m in range(seg):
            pins_f.append((j0 + m, j0 + (m + 1) % seg, j0 + seg + (m + 1) % seg, j0 + seg + m))
        count += 1
print(">> fins", count)

me = bpy.data.meshes.new("fins_me")
me.from_pydata([tuple(v) for v in fins_v], [], fins_f); me.update()
fins = bpy.data.objects.new("fins", me); scene.collection.objects.link(fins)
att = me.attributes.new("hue", 'FLOAT', 'FACE'); att2 = me.attributes.new("rnd", 'FLOAT', 'FACE')
for fi in range(len(fins_f)):
    att.data[fi].value = fin_attr[fi // 6][0]; att2.data[fi].value = fin_attr[fi // 6][1]
tipa = me.attributes.new("tip", 'FLOAT', 'POINT')
for vi in range(len(fins_v)):
    tipa.data[vi].value = 1.0 if (vi % 4) >= 2 else 0.0
fins.shape_key_add(name="Basis")
sk = fins.shape_key_add(name="turned")
for i, v in enumerate(fins_alt):
    sk.data[i].co = v
for fi, pl in enumerate(me.polygons):
    pl.material_index = 0 if (fi % 6) < 2 else (2 if (fi % 6) == 4 else 1)
me2 = bpy.data.meshes.new("pins_me")
me2.from_pydata([tuple(v) for v in pins_v], [], pins_f); me2.update()
for pp in me2.polygons:
    pp.use_smooth = True
pins = bpy.data.objects.new("pins", me2); scene.collection.objects.link(pins)

# ------------------------------------------------------------- 材質：ダイクロイック（反射色と透過色が補色・角度で色が回る）
PAL = [(0.00, (0.10, 0.30, 1.00)), (0.20, (0.10, 0.80, 1.00)), (0.29, (0.80, 0.97, 0.92)), (0.38, (1.00, 0.92, 0.35)),
       (0.56, (1.00, 0.45, 0.12)), (0.76, (0.90, 0.08, 0.55)), (0.92, (0.40, 0.18, 1.00)), (1.00, (0.10, 0.30, 1.00))]


def ramp_node(N):
    r = N.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    els[0].position, els[0].color = PAL[0][0], PAL[0][1] + (1,)
    els[1].position, els[1].color = PAL[-1][0], PAL[-1][1] + (1,)
    for pos, col in PAL[1:-1]:     # 🔴 new() は並べ替える（#113）→ 作ってから値を入れない
        e = els.new(pos); e.color = col + (1,)
    return r


gm = bpy.data.materials.new("dichroic"); gm.use_nodes = True
nt = gm.node_tree; N = nt.nodes; Lk = nt.links
N.remove(N["Principled BSDF"]); out = N["Material Output"]
attr = N.new("ShaderNodeAttribute"); attr.attribute_name = "hue"; attr.attribute_type = 'GEOMETRY'
tipn = N.new("ShaderNodeAttribute"); tipn.attribute_name = "tip"; tipn.attribute_type = 'GEOMETRY'
lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
h1 = N.new("ShaderNodeMath"); h1.operation = 'MULTIPLY_ADD'; h1.inputs[1].default_value = 0.26
Lk.new(tipn.outputs["Fac"], h1.inputs[0]); Lk.new(attr.outputs["Fac"], h1.inputs[2])
h2 = N.new("ShaderNodeMath"); h2.operation = 'MULTIPLY_ADD'; h2.inputs[1].default_value = 0.35
Lk.new(lw.outputs["Facing"], h2.inputs[0]); Lk.new(h1.outputs[0], h2.inputs[2])
hT = N.new("ShaderNodeMath"); hT.operation = 'FRACT'; Lk.new(h2.outputs[0], hT.inputs[0])
hR0 = N.new("ShaderNodeMath"); hR0.operation = 'ADD'; hR0.inputs[1].default_value = 0.5; Lk.new(hT.outputs[0], hR0.inputs[0])
hR = N.new("ShaderNodeMath"); hR.operation = 'FRACT'; Lk.new(hR0.outputs[0], hR.inputs[0])
rT = ramp_node(N); Lk.new(hT.outputs[0], rT.inputs["Fac"])
rR = ramp_node(N); Lk.new(hR.outputs[0], rR.inputs["Fac"])
# カメラから見た透過は淡く（白へ寄せる）
paleT = N.new("ShaderNodeMix"); paleT.data_type = 'RGBA'; paleT.inputs["Factor"].default_value = 0.35
Lk.new(rT.outputs["Color"], paleT.inputs[6]); paleT.inputs[7].default_value = (1, 1, 1, 1)
tr = N.new("ShaderNodeBsdfTransparent"); Lk.new(paleT.outputs[2], tr.inputs["Color"])
gl = N.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.03
# 壁（拡散光線）から見た反射は白に寄せる＝列の間に明るい照り返し
wR = N.new("ShaderNodeMix"); wR.data_type = 'RGBA'
lpw = N.new("ShaderNodeLightPath")
wf = N.new("ShaderNodeMath"); wf.operation = 'MULTIPLY'; wf.inputs[1].default_value = 0.5
Lk.new(lpw.outputs["Is Diffuse Ray"], wf.inputs[0]); Lk.new(wf.outputs[0], wR.inputs["Factor"])
Lk.new(rR.outputs["Color"], wR.inputs[6]); wR.inputs[7].default_value = (1, 0.97, 0.85, 1)
boost = N.new("ShaderNodeMix"); boost.data_type = 'RGBA'; boost.blend_type = 'MULTIPLY'
Lk.new(lpw.outputs["Is Diffuse Ray"], boost.inputs["Factor"])
Lk.new(wR.outputs[2], boost.inputs[6]); boost.inputs[7].default_value = (1.6, 1.6, 1.6, 1)
Lk.new(boost.outputs[2], gl.inputs["Color"])
fr = N.new("ShaderNodeLayerWeight"); fr.inputs["Blend"].default_value = 0.25
fac = N.new("ShaderNodeMath"); fac.operation = 'MULTIPLY_ADD'; fac.use_clamp = True
Lk.new(fr.outputs["Fresnel"], fac.inputs[0]); fac.inputs[1].default_value = 0.45; fac.inputs[2].default_value = 0.35
mix = N.new("ShaderNodeMixShader"); # 拡散光線（壁から見たとき）は鏡面を強く＝壁に反射色の集光が落ちる
dif = N.new("ShaderNodeMath"); dif.operation = 'MAXIMUM'
Lk.new(fac.outputs[0], dif.inputs[0])
lp0 = N.new("ShaderNodeLightPath")
dsc = N.new("ShaderNodeMath"); dsc.operation = 'MULTIPLY'; dsc.inputs[1].default_value = 1.0
Lk.new(lp0.outputs["Is Diffuse Ray"], dsc.inputs[0]); Lk.new(dsc.outputs[0], dif.inputs[1])
Lk.new(dif.outputs[0], mix.inputs[0])
Lk.new(tr.outputs[0], mix.inputs[1]); Lk.new(gl.outputs[0], mix.inputs[2])
# 影の光線：鏡面を混ぜず、濃い透過色だけ＝壁に色の光が落ちる
gam = N.new("ShaderNodeGamma"); gam.inputs["Gamma"].default_value = 1.6
Lk.new(rT.outputs["Color"], gam.inputs["Color"])
trS = N.new("ShaderNodeBsdfTransparent"); Lk.new(gam.outputs[0], trS.inputs["Color"])
lp = N.new("ShaderNodeLightPath")
mix2 = N.new("ShaderNodeMixShader"); Lk.new(lp.outputs["Is Shadow Ray"], mix2.inputs[0])
Lk.new(mix.outputs[0], mix2.inputs[1]); Lk.new(trS.outputs[0], mix2.inputs[2])
Lk.new(mix2.outputs[0], out.inputs["Surface"])
fins.data.materials.append(gm)

# 小口：ソーダガラスの緑がかった暗い線
em = bpy.data.materials.new("edge"); em.use_nodes = True
ep = em.node_tree.nodes["Principled BSDF"]
ep.inputs["Base Color"].default_value = hex_to_linear("#4E7468")
ep.inputs["Roughness"].default_value = 0.05
ep.inputs["Transmission Weight"].default_value = 0.0
en = em.node_tree; eo = en.nodes["Material Output"]
etr = en.nodes.new("ShaderNodeBsdfTransparent"); etr.inputs["Color"].default_value = (0.75, 0.9, 0.85, 1)
elp = en.nodes.new("ShaderNodeLightPath"); emx = en.nodes.new("ShaderNodeMixShader")
en.links.new(elp.outputs["Is Shadow Ray"], emx.inputs[0])
en.links.new(ep.outputs[0], emx.inputs[1]); en.links.new(etr.outputs[0], emx.inputs[2])
en.links.new(emx.outputs[0], eo.inputs["Surface"])
fins.data.materials.append(em)
# 先端の小口：カメラと光を向く面に白い照り
lm = bpy.data.materials.new("edge_lit"); lm.use_nodes = True
lp_ = lm.node_tree.nodes["Principled BSDF"]
lp_.inputs["Base Color"].default_value = hex_to_linear("#A9C4BA")
lp_.inputs["Roughness"].default_value = 0.03
lp_.inputs["Specular IOR Level"].default_value = 1.0
fins.data.materials.append(lm)

pm = bpy.data.materials.new("pin"); pm.use_nodes = True
pp = pm.node_tree.nodes["Principled BSDF"]
pp.inputs["Base Color"].default_value = (0.75, 0.75, 0.76, 1); pp.inputs["Metallic"].default_value = 1.0
pp.inputs["Roughness"].default_value = 0.3
pins.data.materials.append(pm)
parts = [fins, pins]

# ------------------------------------------------------------- 光：左上前方の硬めの1灯＋白い環境
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.2

KEY_POS = Vector((2.4, -3.3, 2.6))
ld = bpy.data.lights.new("key", 'AREA'); ld.energy = 1150; ld.size = 1.8; ld.shape = 'DISK'
key_light = bpy.data.objects.new("key", ld); scene.collection.objects.link(key_light)
key_light.location = KEY_POS


def aim(ob, tgt):
    ob.rotation_euler = (Vector(tgt) - ob.location).to_track_quat('-Z', 'Y').to_euler()


aim(key_light, (0, 0, 0))

# ------------------------------------------------------------- カメラ
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cd.dof.use_dof = True
cd.sensor_width = 36
scene.camera = cam

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

# 026：光の走り → 物の動き → マクロ → 決め
HERO_CAM = Vector((0.0, -4.15, 0.0))
TGT = Vector((0.0, 0.0, 0.0))
SHOTS = [
    dict(sec=3.0,   # 光の走り：斜めの中景で止め、キーを右上から左上へ走らせる＝色が片から片へ移る
         cam=lambda t: (lerp((0.9, -2.3, 0.55), (0.75, -2.25, 0.45), ease(t)), Vector((0.12, 0, 0.1)), 85, 5.6, None)),
    dict(sec=3.0,   # 物の動き：壁すれすれの低い角度から、片がピンを軸に一斉に回って落ち着く（片が林のように立つ）
         cam=lambda t: (lerp((-0.92, -0.66, -0.28), (-0.82, -0.68, -0.16), ease(t)), Vector((0.05, 0, 0.02)), 60, 4.0, None)),
    dict(sec=2.8,   # マクロ：帯の芯を150mmでなめ、ピントを送る
         cam=lambda t: (lerp((-0.10, -1.05, 0.30), (0.20, -1.05, 0.42), ease(t)), Vector((0.05 + 0.25 * ease(t), 0, 0.12 + 0.12 * ease(t))),
                        150, 2.8, None)),
    dict(sec=3.0,   # 決め：寄りから引いて正対の hero へ
         cam=lambda t: (lerp((0.10, -3.25, 0.06), HERO_CAM, ease_out(min(1.0, t / 0.62))), lerp((0.04, 0, 0.02), TGT, ease_out(min(1.0, t / 0.62))),
                        LOOK["lens"], LOOK["fstop"], None)),
]
shot_start, N_FRAMES = [], 0
for sh in SHOTS:
    shot_start.append(N_FRAMES + 1)
    sh["frames"] = round(sh["sec"] * FPS)
    N_FRAMES += sh["frames"]
STILL_FRAME = N_FRAMES

skey = fins.data.shape_keys.key_blocks["turned"]


def pose(i, t, T):
    skey.value = 1.0 if i == 0 else (1.0 - ease(t) if i == 1 else 0.0)


def light_path(i, t):
    if i == 0:   # 上を回る弧（正面を通さない）
        a0, a1 = math.radians(140), math.atan2(KEY_POS.z, KEY_POS.x)
        a = a0 + (a1 - a0) * ease(t)
        R_ = math.hypot(KEY_POS.x, KEY_POS.z)
        key_light.location = Vector((R_ * math.cos(a), KEY_POS.y, R_ * math.sin(a)))
    else:
        key_light.location = KEY_POS
    aim(key_light, (0, 0, 0))


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
        skey.keyframe_insert("value", frame=f)
        light_path(i, t)
        key_light.keyframe_insert("location", frame=f)
        key_light.keyframe_insert("rotation_euler", frame=f)
        scene.view_settings.exposure = LOOK["exposure"] + (-0.4 if i == 2 else (-0.25 if i == 1 else 0.0))
        scene.view_settings.keyframe_insert("exposure", frame=f)

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
scene.cycles.caustics_reflective = True
scene.cycles.caustics_refractive = True
scene.cycles.blur_glossy = 0.5
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
