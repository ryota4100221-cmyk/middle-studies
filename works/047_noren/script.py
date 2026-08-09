# =============================================================
# monaka design. — MIDDLE STUDY 047 "NOREN"（暖簾）
#
# 黒い暖簾が一枚、宙に架かっている。三枚の垂れ布のあいだ——真ん中の隙間——から
# ライムの光が差す。風が来ると布ははらみ、隙間はひらく。布がやわらかいので、
# 光の線もまっすぐではない。たわむ。風が引けば、隙間はまた閉じる。
#
# シリーズ初の**物理シミュレーション（cloth）**。装飾で入れたのではなく、
# この題材は硬いままだと「ただの黒い板」にしかならない（限界テストAで実証）。
# 光の線がたわむのは、それを支えているものが布だからで、45作のどれにも出せなかった線。
#
# 🔴 不変条件「ループが数学的に閉じること」は守る：
#    シムは原理的に閉じないので、末尾 L フレームを先頭へ cos ブレンドして
#    頂点座標を焼き込み、frame N の次が frame 1 に厳密に一致する列を作る。
#    レンダーもglbもこの焼き込み済みシェイプキーから出す（＝シムはビルド時にしか走らない）。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | swing | test | still | anim | blend | glb
# =============================================================
import bpy, bmesh, math, sys, os, time
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))

LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 暖簾（長暖簾） ---
NW, NH = 1.55, 1.62          # 布の幅・丈
NX, NY = 84, 76              # グリッド分割
N_PANEL = 3
SLIT_W = 0.009               # 🔴 切れ目は細く。太いとそれ自体が下駄になり、開閉の相対変化が潰れる
YOKE = 0.22                  # 肩（切れていない帯）
HEM_Z = 0.80                 # 裾の高さ（キャプション帯 z=0.52 とぶつからない下限）
Z_TOP = HEM_Z + NH           # = 2.42
CENTER_Z = HEM_Z + NH * 0.5  # = 1.61
ROD_R = 0.030

FPS = 24
N_FRAMES = 120               # 5秒
BLEND = 16                   # 末尾→先頭のブレンド長（ループを厳密に閉じる）
PREROLL = 44                 # 助走（静止→風の定常状態）
STILL_FRAME = 55             # 見える発光面積が最大の位相（probeの解析積分で確定）

WIND_BASE = 1150.0
CLOTH_MASS = 0.052

def hex_to_linear(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)

LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- マテリアル ----------
def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]

# 布は #17-b（紙・布はマット）。曲面だが漆の艶は乗らない
mat_cloth, p = principled("noren_cloth")
p.inputs["Base Color"].default_value = BLACK
p.inputs["Roughness"].default_value = 0.58   # 黒繻子寄り。マット過ぎると面がハイライトを返さない（#45）
p.inputs["Specular IOR Level"].default_value = 0.22    # 🔴 #45：主材の下限は0.10。割ると黒が光を拾わず「影絵」に退化する

# 発光帯：#32 Base純黒で裏当てを兼ね、#34 2軸楕円で縁を厳密に0へ
mat_glow = bpy.data.materials.new("glow"); mat_glow.use_nodes = True
nt = mat_glow.node_tree
gp = nt.nodes["Principled BSDF"]
gp.inputs["Base Color"].default_value = (0, 0, 0, 1)
gp.inputs["Specular IOR Level"].default_value = 0.0
gp.inputs["Emission Color"].default_value = LIME
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
def mnode(op, val=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    if val is not None: n.inputs[1].default_value = val
    return n
dx, dz = mnode('SUBTRACT', 0.5), mnode('SUBTRACT', 0.5)
nt.links.new(sep.outputs["X"], dx.inputs[0]); nt.links.new(sep.outputs["Z"], dz.inputs[0])
sx, sz = mnode('DIVIDE', 0.50), mnode('DIVIDE', 0.50)
nt.links.new(dx.outputs[0], sx.inputs[0]); nt.links.new(dz.outputs[0], sz.inputs[0])
px_, pz_ = mnode('POWER', 2.0), mnode('POWER', 2.0)
nt.links.new(sx.outputs[0], px_.inputs[0]); nt.links.new(sz.outputs[0], pz_.inputs[0])
addn = mnode('ADD')
nt.links.new(px_.outputs[0], addn.inputs[0]); nt.links.new(pz_.outputs[0], addn.inputs[1])
sqn = mnode('SQRT'); nt.links.new(addn.outputs[0], sqn.inputs[0])
pwn = mnode('POWER', 1.45)   # #38④ 暗い裾を締める
nt.links.new(sqn.outputs[0], pwn.inputs[0])
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 1.0
mr.inputs["To Min"].default_value = 4.4;  mr.inputs["To Max"].default_value = 0.0
mr.interpolation_type = 'SMOOTHSTEP'
nt.links.new(pwn.outputs[0], mr.inputs["Value"])
nt.links.new(mr.outputs["Result"], gp.inputs["Emission Strength"])

mat_rod, rp = principled("rod")
rp.inputs["Base Color"].default_value = BLACK
rp.inputs["Roughness"].default_value = 0.40
rp.inputs["Specular IOR Level"].default_value = 0.26    # 竿は塗りの丸棒。#45の下限0.10を割らない

mat_back, bkp = principled("backing")
bkp.inputs["Base Color"].default_value = (0, 0, 0, 1)
bkp.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, fp = principled("floor")
fp.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp.inputs["Roughness"].default_value = 0.42
mat_text, tp = principled("text")
tp.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp.inputs["Roughness"].default_value = 0.6

# ---------- 暖簾メッシュ ----------
x0, x1 = -NW / 2, NW / 2
slit_x = [x0 + (x1 - x0) * k / N_PANEL for k in range(1, N_PANEL)]

bm = bmesh.new()
verts = [[None] * NY for _ in range(NX)]
for i in range(NX):
    x = x0 + (x1 - x0) * i / (NX - 1)
    # 平らな布は平らなまま安定する（限界テストA 1周目）。折り目の種を入れる
    ripple = 0.028 * math.sin(2 * math.pi * 6.0 * (i / (NX - 1)))
    for j in range(NY):
        z = Z_TOP - NH * j / (NY - 1)
        grow = min(1.0, max(0.0, (Z_TOP - z - YOKE) / 0.26))
        verts[i][j] = bm.verts.new((x, ripple * grow, z))
bm.verts.ensure_lookup_table()

def in_slit(xc, zc):
    if zc > Z_TOP - YOKE:
        return False
    return any(abs(xc - s) < SLIT_W / 2 for s in slit_x)

for i in range(NX - 1):
    for j in range(NY - 1):
        xc = (verts[i][j].co.x + verts[i + 1][j].co.x) / 2
        zc = (verts[i][j].co.z + verts[i][j + 1].co.z) / 2
        if in_slit(xc, zc):
            continue
        # 巻き順：法線をカメラ側(-Y)に向ける
        bm.faces.new((verts[i][j], verts[i][j + 1], verts[i + 1][j + 1], verts[i + 1][j]))
bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')

me = bpy.data.meshes.new("noren_sim")
bm.to_mesh(me); bm.free()
sim = bpy.data.objects.new("noren_sim", me)
bpy.context.collection.objects.link(sim)
FACES = [list(pp.vertices) for pp in me.polygons]
NVERT = len(me.vertices)
print(">> mesh verts=%d faces=%d" % (NVERT, len(FACES)))

vg = sim.vertex_groups.new(name="pin")
vg.add([v.index for v in me.vertices if v.co.z > Z_TOP - 0.006], 1.0, 'REPLACE')

mod = sim.modifiers.new("Cloth", 'CLOTH')
cs = mod.settings
def setp(o, k, v):
    try: setattr(o, k, v)
    except Exception as e: print("   !! %s: %s" % (k, e))
setp(cs, "quality", 9)
setp(cs, "mass", CLOTH_MASS)
setp(cs, "tension_stiffness", 24.0)
setp(cs, "compression_stiffness", 24.0)
setp(cs, "shear_stiffness", 8.0)
setp(cs, "bending_stiffness", 0.32)
setp(cs, "air_damping", 1.15)
setp(cs, "tension_damping", 12.0)
setp(cs, "bending_damping", 0.9)
setp(cs, "vertex_group_mass", "pin")
setp(cs, "pin_stiffness", 1.0)
setp(mod.collision_settings, "use_collision", False)
setp(mod.collision_settings, "use_self_collision", False)
SIM_END = PREROLL + N_FRAMES + BLEND
mod.point_cache.frame_start = 1
mod.point_cache.frame_end = SIM_END

# ---------- 風 ----------
# 🔴 風は自分のローカルZにしか吹かない（限界テスト実測：回転0だと 0.000m）
bpy.ops.object.effector_add(type='WIND', location=(0.0, -1.15, CENTER_Z))
wind = bpy.context.active_object; wind.name = "wind"
wind.rotation_euler = (math.radians(90), 0, 0)     # -Y → +Y
wf = wind.field
wf.noise = 0.0; wf.flow = 0.0
# 🔴 一様な風だと3枚が同じに動き、スリットは平行なまま＝光の線が定規で引いたようになる。
#    POINT形状＋球状減衰で風を局所化し、それを左右に走らせる＝突風が横切る。
#    板が順番に遅れて振られるのでスリットが剪断され、光の線がたわむ（この作品の署名）。
wf.shape = 'POINT'
wf.falloff_type = 'SPHERE'
wf.use_max_distance = True
wf.distance_max = 1.75
wf.falloff_power = 1.7
GUST_X = 0.26   # 🔴 大きく走らせると左が開くとき右が閉じ、面積で相殺する（043 MAYU と同じ罠）
for f in range(1, SIM_END + 2):
    t = (f - 1 - PREROLL) / N_FRAMES               # ループ位相（BLEND域も同じ式で連続）
    wf.strength = WIND_BASE * (0.12 + 0.88 * math.sin(2 * math.pi * t))   # ほぼ無風→強風まで振る
    wf.keyframe_insert("strength", frame=f)
    wind.location.x = GUST_X * math.sin(2 * math.pi * t)   # 横に往復＝完全ループ
    wind.keyframe_insert("location", frame=f)

# ---------- シムを回して頂点列を取る ----------
def sim_run():
    t0 = time.time()
    for f in range(1, SIM_END + 1):
        scene.frame_set(f)
    print(">> SIM %d frames  %.1fs (%.3fs/frame)" % (SIM_END, time.time() - t0, (time.time() - t0) / SIM_END))

def coords_at(f):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    ev = sim.evaluated_get(dg); m = ev.to_mesh()
    co = [(v.co.x, v.co.y, v.co.z) for v in m.vertices]
    ev.to_mesh_clear()
    return co

sim_run()
RAW = [coords_at(PREROLL + 1 + i) for i in range(N_FRAMES + BLEND)]

# 🔴 ループを厳密に閉じる：先頭 BLEND フレームに「N フレーム後の姿」を cos で混ぜる
#    out[i<BLEND] = (1-w)·RAW[i+N] + w·RAW[i] , w = 0.5(1-cos(π i/BLEND)) …0→1
#    こうすると out[0] = RAW[N] ＝ out[N-1]=RAW[N-1] の正しい続き＝つなぎ目が消える
SEQ = []
for i in range(N_FRAMES):
    if i < BLEND:
        w = 0.5 * (1 - math.cos(math.pi * i / BLEND))
        a, b = RAW[i + N_FRAMES], RAW[i]
        SEQ.append([(a[k][0] * (1 - w) + b[k][0] * w,
                     a[k][1] * (1 - w) + b[k][1] * w,
                     a[k][2] * (1 - w) + b[k][2] * w) for k in range(NVERT)])
    else:
        SEQ.append(RAW[i])

# ---------- 焼き込み済みオブジェクト（以降シムは使わない） ----------
baked_me = bpy.data.meshes.new("noren")
baked_me.from_pydata(SEQ[0], [], FACES)
baked_me.update()
noren = bpy.data.objects.new("noren", baked_me)
bpy.context.collection.objects.link(noren)
noren.data.materials.append(mat_cloth)
noren.shape_key_add(name="basis", from_mix=False)
KEYS = []
for i in range(N_FRAMES):
    sk = noren.shape_key_add(name="f%03d" % (i + 1), from_mix=False)
    for k, c in enumerate(SEQ[i]):
        sk.data[k].co = c
    KEYS.append(sk)
for i, sk in enumerate(KEYS):
    for j in range(N_FRAMES):
        sk.value = 1.0 if i == j else 0.0
        sk.keyframe_insert("value", frame=j + 1)
bpy.context.view_layer.objects.active = noren
noren.select_set(True); bpy.ops.object.shade_auto_smooth(angle=1.0); noren.select_set(False)

bpy.data.objects.remove(sim, do_unlink=True)
bpy.data.objects.remove(wind, do_unlink=True)

# ---------- 竿・裏当て・発光帯 ----------
bpy.ops.mesh.primitive_cylinder_add(radius=ROD_R, depth=NW + 0.40,
                                    location=(0, 0, Z_TOP + ROD_R * 0.35),
                                    rotation=(0, math.radians(90), 0), vertices=64)
rod = bpy.context.active_object; rod.name = "rod"; rod.data.materials.append(mat_rod)
bpy.ops.object.shade_auto_smooth(angle=0.9)

# 🔴 帯の上下端は「肩」と「裾」に一致させる。中途半端な高さで切ると、
#    2軸グラデが縁の手前でES=0に落ちるため hero に水平の切り口が出る（#16）
GLOW_Z = (HEM_Z + 0.06 + (Z_TOP - YOKE + 0.01)) / 2
GLOW_HALF = ((Z_TOP - YOKE + 0.01) - (HEM_Z + 0.06)) / 2
GLOW_Z_LO, GLOW_Z_HI = GLOW_Z - GLOW_HALF, GLOW_Z + GLOW_HALF   # 🔴 隙間が最も動く高さ（probe実測 z=1.3で30%・1.5で25%）。CENTER_Zではない
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0.28, 1.55),
                                 rotation=(math.radians(90), 0, 0))
back = bpy.context.active_object; back.name = "backing"
for v in back.data.vertices:      # スリットを塞ぐ最小限。大きいと主役の黒板になる
    v.co.x *= 0.72
    v.co.y *= 1.40   # 0.85..2.25＝スリット全高。上が足りないと白抜け、下が出ると黒いタブ(#32-b)
back.data.materials.append(mat_back)

for k, s in enumerate(slit_x):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(s, 0.15, GLOW_Z),
                                     rotation=(math.radians(90), 0, 0))
    g = bpy.context.active_object; g.name = "glow%d" % k
    for v in g.data.vertices:
        v.co.x *= 0.14
        v.co.y *= GLOW_HALF * 2   # 隙間が動く帯。Base純黒なのでこの範囲の裏当ても兼ねる
    g.data.materials.append(mat_glow)

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_floor)

def caption(body, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object; tx.name = name
    tx.data.body = body; tx.data.size = size; tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx

caps = [caption("Designing the Middle of Your Story.", 0.1, (0.15, -1.7, 0.62), "tagline"),
        caption("monaka design.", 0.06, (0.15, -1.7, 0.45), "logo"),
        caption("MIDDLE STUDY 047 — NOREN", 0.045, (0.15, -1.7, 0.34), "study")]   # #20-b 3行目が下端で切れるので底上げ

def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

focus = (0, 0, CENTER_Z)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=(0.55, -8.3, 1.95))
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((0.1, 0, CENTER_Z + 0.05)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = noren
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception:
    scene.view_settings.view_transform = 'AgX'

def setup_bloom():
    ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    ou = ng.nodes.new("NodeGroupOutput")
    try: gl.inputs["Type"].default_value = 'BLOOM'
    except Exception: pass
    gl.inputs["Threshold"].default_value = 1.2
    gl.inputs["Strength"].default_value = 0.35
    try: gl.inputs["Size"].default_value = 0.55
    except Exception: pass
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], ou.inputs["Image"])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True
setup_bloom()

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]
print(">> modes:", modes)

def seq_step(i, j):
    d = [math.dist(p, q) for p, q in zip(SEQ[i], SEQ[j])]
    return sum(d) / len(d)

if "probe" in modes:
    # ループの判定は「継ぎ目の跳び」を通常の1フレーム移動量と比べること。
    # 同じなら継ぎ目は存在しない（ブレンド設計上、末尾の次が先頭の実際の続きになる）
    steps = [seq_step(i, i + 1) for i in range(N_FRAMES - 1)]
    wrap = seq_step(N_FRAMES - 1, 0)
    print(">> LOOP  継ぎ目の跳び %.5fm ／ 通常1フレーム 平均%.5fm 最大%.5fm → 比 %.2f"
          % (wrap, sum(steps) / len(steps), max(steps), wrap / (sum(steps) / len(steps))))

    # 「線のたわみ」＝スリットの縁が垂直からどれだけ外れるか（この作品の署名）
    bend = 0.0
    for s in slit_x:
        edge = [c for c in SEQ[STILL_FRAME - 1]
                if abs(c[0] - s) < 0.045 and c[2] < Z_TOP - YOKE]
        if edge:
            mx = sum(c[0] for c in edge) / len(edge)
            bend = max(bend, max(abs(c[0] - mx) for c in edge))
    print(">> BEND   スリット縁の垂直からのずれ 最大 %.4fm（0.03以上で絵として見える）" % bend)

    # 🔴 隙間は「どの高さで」開くのか。光をそこに置かないと機構が光を変えない（#40⑥）
    print(">> GAP   高さ別のスリット幅（全120フレームの min→max）")
    for zt in (2.10, 1.90, 1.70, 1.50, 1.30, 1.10, 0.95):
        gs = []
        for fr in range(0, N_FRAMES, 6):
            c = SEQ[fr]
            tot = 0.0
            for s in slit_x:
                left = [p[0] for p in c if abs(p[2] - zt) < 0.03 and s - 0.30 < p[0] < s]
                right = [p[0] for p in c if abs(p[2] - zt) < 0.03 and s < p[0] < s + 0.30]
                if left and right:
                    tot += max(right) * 0 + (min(right) - max(left))
            gs.append(tot / len(slit_x))
        if gs:
            print("   z=%.2f  %.4f → %.4f m   （変化 %.0f%%）"
                  % (zt, min(gs), max(gs), (max(gs) / max(min(gs), 1e-6) - 1) * 100))

    # 🔴 #40⑥ は「見える発光面積」で判定する。レンダーで8枚撮るのは粗い＆遅いので、
    #    シム結果から解析的に積分する（全120フレーム・帯の縦グラデで重み付け）
    BAND_W, BAND_Z0, BAND_Z1 = 0.14, GLOW_Z_LO, GLOW_Z_HI
    def visible_area(c):
        tot = 0.0
        zs = [BAND_Z0 + (BAND_Z1 - BAND_Z0) * i / 24 for i in range(25)]
        for zt in zs:
            wz = max(0.0, 1.0 - abs(zt - (BAND_Z0 + BAND_Z1) / 2) / ((BAND_Z1 - BAND_Z0) / 2))
            for s in slit_x:
                left = [p[0] for p in c if abs(p[2] - zt) < 0.028 and s - 0.30 < p[0] < s]
                right = [p[0] for p in c if abs(p[2] - zt) < 0.028 and s < p[0] < s + 0.30]
                if left and right:
                    tot += min(max(min(right) - max(left), 0.0), BAND_W) * wz
        return tot
    vs = [visible_area(SEQ[i]) for i in range(0, N_FRAMES, 3)]
    print(">> #40⑥ 見える発光面積  min/max = %.2f  （合格 0.75以下）" % (min(vs) / max(vs)))
    print("   最小 frame %d ／ 最大 frame %d"
          % (vs.index(min(vs)) * 3 + 1, vs.index(max(vs)) * 3 + 1))

    # 板ごとのはらみ＝突風が横切っているか
    for k, (lo, hi) in enumerate(((-NW / 2, slit_x[0]), (slit_x[0], slit_x[1]), (slit_x[1], NW / 2))):
        ys = [abs(c[1]) for c in SEQ[STILL_FRAME - 1] if lo < c[0] < hi]
        print("   panel%d max|y|=%.4f" % (k, max(ys) if ys else 0))
    ys = [abs(c[1]) for c in SEQ[STILL_FRAME - 1]]
    print(">> BILLOW(still) max|y|=%.4fm" % max(ys))
    zs = [c[2] for c in SEQ[STILL_FRAME - 1]]
    xs = [c[0] for c in SEQ[STILL_FRAME - 1]]
    print(">> BBOX  x %.3f..%.3f (%.3f)  z %.3f..%.3f (%.3f)  ／ フレーム 横2.81・縦3.52"
          % (min(xs), max(xs), max(xs) - min(xs), min(zs), max(zs), max(zs) - min(zs)))
    print(">> 占有  横%.0f%%  縦%.0f%%" % ((max(xs)-min(xs))/2.81*100, (Z_TOP+ROD_R-min(zs))/3.52*100))

if "swing" in modes:
    # #40⑥ 機構が光を変えているか＝見える発光面積の振れを実測する
    scene.render.resolution_x, scene.render.resolution_y = 320, 400
    scene.cycles.samples = 16
    scene.render.image_settings.file_format = 'PNG'
    for i in range(8):
        f = 1 + round(i * N_FRAMES / 8)
        scene.frame_set(f)
        scene.render.filepath = os.path.join(OUT, "_swing_%02d.png" % f)
        bpy.ops.render.render(write_still=True)
    print(">> swing frames rendered")

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 480, 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero done")

if "phases" in modes:
    # #35 ループものは still 以外の位相も撮る（材質側の破綻は1枚では出ない）
    for fr in (1, 25, 97):
        scene.frame_set(fr)
        scene.render.resolution_x, scene.render.resolution_y = 800, 1000
        scene.cycles.samples = 48
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(OUT, "_phase_%03d.png" % fr)
        bpy.ops.render.render(write_still=True)
    print(">> phases done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = 720, 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> anim done")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_047.blend"))

# 🔴 glb は必ず最後（#30：材質の単純化をレンダーの前に置かない）
if "glb" in modes:
    # morph target は重い（#43-e：24キーで10.2MB）。10キーに間引いて 5MB 級に収める
    STEP = 12
    keep = [i for i in range(0, N_FRAMES, STEP)]
    exp_me = bpy.data.meshes.new("noren_exp")
    exp_me.from_pydata(SEQ[0], [], FACES); exp_me.update()
    eo = bpy.data.objects.new("noren_exp", exp_me)
    bpy.context.collection.objects.link(eo)
    eo.data.materials.append(mat_cloth)
    eo.shape_key_add(name="basis", from_mix=False)
    sks = []
    for i in keep:
        sk = eo.shape_key_add(name="f%03d" % (i + 1), from_mix=False)
        for k, c in enumerate(SEQ[i]):
            sk.data[k].co = c
        sks.append((i, sk))
    for i, sk in sks:
        for j, _ in sks:
            sk.value = 1.0 if i == j else 0.0
            sk.keyframe_insert("value", frame=j + 1)
        sk.value = 1.0 if i == keep[0] else 0.0     # 折り返し（最終→先頭）
        sk.keyframe_insert("value", frame=N_FRAMES + 1)
    for o in bpy.data.objects:
        o.select_set(o.name == "noren_exp")
    bpy.context.view_layer.objects.active = eo
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True,
                                  export_yup=True)
        print(">> GLB %d morph targets  %.1fMB"
              % (len(sks), os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)

print(">> ALL DONE")
