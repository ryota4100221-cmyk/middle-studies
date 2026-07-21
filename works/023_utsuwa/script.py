# =============================================================
# monaka design. — MIDDLE STUDY 023 "UTSUWA"（器 / うつわ）
# 黒い茶碗が宙に浮く。底からライム #A5E02E の光が液のように満ちて縁まで上がり、
# また退く。外は黒い器、その中（うつろ）に光が満ちる——真ん中に光がある。
# 屋号「最中＝二枚の皮の中に餡」の、器版。
#
# 造形: 器＝bmesh の回転体（surface of revolution）の二重スキン。
#       外プロファイルを回転＝黒い陶。内プロファイルを回転＝発光ライムの凹面。
#       両者を縁のバンドで縫って閉じた多様体に。object.scale/transform_apply を
#       使わず、bmesh でワールド実寸生成＝PITFALL #7/#7-b/#15 を構造的に回避。
#       内壁＝凹面を発光させ、光源を器の奥に隠す（007 KIRITORI・017・022 背表紙と同じ手）
#       ＝pitfall #19（グレージングでLEDテープ化）と #11（暗い大面上の集中輝点で
#       Glare箱）を構造的に回避。
# アニメ: 内腔を水位のように上昇・拡大する発光プール円盤（内壁半径に一致＝液面に読む）
#       ＋随伴する柔らかいライム点光源で内壁を洗う。プールは object.location.z ＋ scale の
#       transform アニメ＝glb にアニメが乗る（材質発光アニメは glb 不可なので幾何で駆動）。
#       level(t) = LMIN + (LMAX-LMIN)·0.5(1-cos2πt) ＝数学的に完全ループ。
#       器は静止し光だけが満ちる（021 FUE「容器静止・光が動く」機構の第2弾）。
#       器を TILT だけカメラ側へ傾け内腔を見せる（017 KAGIANA の板傾けと同じ）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_utsuwa.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_utsuwa")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.58      # 器の中心高さ（シリーズ共通の画面中心）
TILT = 20.0          # 器をカメラ側へ傾ける角度（017 と同じ手）。内腔＝抹茶の面を見せる
SEG = 96             # 回転分割（横方向の滑らかさ）
VSEG = 34            # 縦（プロファイル）方向の分割。制御点を Catmull-Rom で密にして
                     # シルエットの面取り（低ポリのカクつき）を消す

# 器のプロファイル制御点（r, z）。z は器の中心 = 0 で定義（object.location.z=CENTER_Z で
# 持ち上げ、rotation_euler.x=TILT で器の中心を軸に傾ける＝二重オフセットを避ける #9）。
# 器＝抹茶茶碗（chawan：低く広い）。茶道の器として一目で読め、内腔の抹茶＝光が主役になる。
# 深い器を軸ほぼ正面から見ると「水位」は見えない（現実の抹茶と同じ）ので、
# 満ち引きは『内腔が光で満ち、闇へ引く』明滅として読ませる（NENRIN/NAMI同様の静かなループ）。
# 最大幅 2·0.88=1.76 は横（2.81）の 63%＝適正域。
OUTER_CP = [         # 外スキン：底ポール(r=0) → 胴 → 縁。黒い陶。
    (0.00, -0.70),
    (0.24, -0.665),
    (0.50, -0.55),
    (0.72, -0.34),
    (0.86, -0.08),
    (0.88,  0.10),   # 胴の最大径（belly）
    (0.83,  0.34),
    (0.75,  0.55),
    (0.72,  0.70),   # 外縁
]
INNER_CP = [         # 内スキン：内腔の底ポール(r=0) → 内壁 → 内縁。発光ライムの凹面。
    (0.00, -0.50),   # 内腔の底（外底より 0.20 上＝器の厚い底）
    (0.22, -0.47),
    (0.46, -0.36),
    (0.66, -0.16),
    (0.78,  0.06),
    (0.80,  0.28),   # 内腔の最大径
    (0.75,  0.50),
    (0.665, 0.70),   # 内縁（縁の肉厚 0.72-0.665=0.055）
]


def catmull_rom(cps, n_out):
    """制御点を通る滑らかな曲線を n_out 点に再サンプル（端点は複製して外挿）。"""
    pts = [cps[0]] + list(cps) + [cps[-1]]
    out = []
    segs = len(cps) - 1
    for i in range(n_out):
        g = i / (n_out - 1) * segs           # 0..segs
        k = min(int(g), segs - 1)
        u = g - k
        p0, p1, p2, p3 = pts[k], pts[k + 1], pts[k + 2], pts[k + 3]
        c = []
        for d in range(2):
            a0, a1, a2, a3 = p0[d], p1[d], p2[d], p3[d]
            c.append(0.5 * ((2 * a1) + (-a0 + a2) * u +
                            (2 * a0 - 5 * a1 + 4 * a2 - a3) * u * u +
                            (-a0 + 3 * a1 - 3 * a2 + a3) * u * u * u))
        out.append((max(0.0, c[0]), c[1]))
    return out


OUTER = catmull_rom(OUTER_CP, VSEG)
INNER = catmull_rom(INNER_CP, VSEG)

# 光のプール（液面）。level は器ローカル z。LMIN=空（底すれすれ）／LMAX=満（縁下）。
LMIN = -0.44
LMAX =  0.60

FPS = 24
N_FRAMES = 120       # 5秒 完全ループ
STILL_FRAME = 61     # t=0.5 ＝ level が LMAX ＝最も満ちた瞬間


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4：この変換なしだと別の色になる）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


def inner_radius_at(zc):
    """内スキンプロファイルを線形補間して、高さ zc（ローカル）での内腔半径を返す。
    プール円盤をこの半径に一致させて『液面が壁に接している』に読ませる。"""
    pts = INNER
    if zc <= pts[0][1]:
        return pts[0][0]
    if zc >= pts[-1][1]:
        return pts[-1][0]
    for k in range(len(pts) - 1):
        r0, z0 = pts[k]
        r1, z1 = pts[k + 1]
        if z0 <= zc <= z1:
            u = (zc - z0) / (z1 - z0) if z1 != z0 else 0.0
            return r0 + (r1 - r0) * u
    return pts[-1][0]


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


# 器の外＝黒い陶。曲面なので #17 の曲面レシピ寄り（丸面は環境光を縦ストリークに拾い
# プラスチック化する）。ただし陶なのでツヤは控えめのマット寄りに（#17-b の素材判断）。
mat_body, b = make_principled("body_ceramic")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.44
b.inputs["Specular IOR Level"].default_value = 0.28
b.inputs["Coat Weight"].default_value = 0.05
b.inputs["Coat Roughness"].default_value = 0.30

# 内壁＝発光ライムの凹面。凹面は内腔の点光源＋プールに向くので面で光る（#19）。
# 常時ほのかに灯し「中はライム」を保証（満ち引きの主役はプール円盤）。
# 020 の教訓に従い純発光体：Base Color を暗いライムに落とし色は emission だけで決める（#13）。
mat_inner, inner_bsdf = make_principled("inner_lime")
inner_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
inner_bsdf.inputs["Emission Color"].default_value = LIME
inner_bsdf.inputs["Roughness"].default_value = 0.55
inner_bsdf.inputs["Specular IOR Level"].default_value = 0.10

# 光のプール（液面円盤）。満ちると縁近くまで上がり key(1400W) を浴びうるので純発光体（#13）。
mat_pool, pool_bsdf = make_principled("pool_lime")
pool_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
pool_bsdf.inputs["Emission Color"].default_value = LIME
pool_bsdf.inputs["Roughness"].default_value = 0.5
pool_bsdf.inputs["Specular IOR Level"].default_value = 0.10

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（PITFALL #15：object.scale/transform_apply を使わない） ----------
def new_object(name, bm, mats):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    for m in mats:
        o.data.materials.append(m)
    return o


def build_ring(bm, r, z):
    """r≈0 ならポール（単一頂点）、そうでなければ SEG 個のリング。"""
    if r < 1e-4:
        return [bm.verts.new((0.0, 0.0, z))]
    vs = []
    for k in range(SEG):
        a = 2 * math.pi * k / SEG
        vs.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
    return vs


def stitch(bm, rA, rB, faces_out):
    """2つのリング（またはポール）を面で繋ぐ。ポールは三角扇。"""
    if len(rA) == 1 and len(rB) == 1:
        return
    if len(rA) == 1:
        for k in range(SEG):
            faces_out.append(bm.faces.new((rA[0], rB[k], rB[(k + 1) % SEG])))
    elif len(rB) == 1:
        for k in range(SEG):
            faces_out.append(bm.faces.new((rA[k], rA[(k + 1) % SEG], rB[0])))
    else:
        for k in range(SEG):
            faces_out.append(bm.faces.new(
                (rA[k], rA[(k + 1) % SEG], rB[(k + 1) % SEG], rB[k])))


def build_vessel():
    bm = bmesh.new()
    outer_rings = [build_ring(bm, r, z) for (r, z) in OUTER]
    inner_rings = [build_ring(bm, r, z) for (r, z) in INNER]
    bm.verts.ensure_lookup_table()

    body_faces, inner_faces, rim_faces = [], [], []
    for k in range(len(outer_rings) - 1):
        stitch(bm, outer_rings[k], outer_rings[k + 1], body_faces)
    for k in range(len(inner_rings) - 1):
        stitch(bm, inner_rings[k], inner_rings[k + 1], inner_faces)
    # 縁のバンド（外縁リング ↔ 内縁リング）＝二枚のスキンを縫って閉じる
    stitch(bm, outer_rings[-1], inner_rings[-1], rim_faces)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    inner_set = set(inner_faces)
    for f in bm.faces:
        f.material_index = 1 if f in inner_set else 0   # 0=黒陶(外+縁) / 1=発光ライム(内)

    o = new_object("utsuwa_body", bm, [mat_body, mat_inner])
    o.location = (0.0, 0.0, CENTER_Z)
    o.rotation_euler = (math.radians(TILT), 0.0, 0.0)   # 器の中心を軸に傾ける
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_auto_smooth(angle=0.6)          # PITFALL #6
    o.select_set(False)
    return o


vessel = build_vessel()


# ---------- 光のプール（液面円盤・器の子） ----------
# ローカル z=0 の平円盤として作り、object.location.z（水位）と scale（内腔半径）で
# アニメする。器の子にして TILT を継承＝液面は器の軸に垂直（容器と一緒に傾く）。
def build_pool():
    bm = bmesh.new()
    ring = [bm.verts.new((math.cos(2 * math.pi * k / SEG),
                          math.sin(2 * math.pi * k / SEG), 0.0)) for k in range(SEG)]
    cen = bm.verts.new((0.0, 0.0, 0.0))
    for k in range(SEG):
        bm.faces.new((cen, ring[k], ring[(k + 1) % SEG]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object("utsuwa_pool", bm, [mat_pool])
    o.parent = vessel                    # 親の parent_inverse は既定 identity のまま（#9）
    return o


pool = build_pool()


# ---------- 内腔を洗う点光源（プールに随伴して上昇） ----------
LIGHT_E = float(os.environ.get("LIGHT_E", "64"))  # 2026-07-21引き上げ：内壁を洗う光を強化
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.05))
pool_light = bpy.context.active_object
pool_light.name = "pool_light"
pool_light.data.energy = LIGHT_E
pool_light.data.color = (0.72, 0.90, 0.32)   # ライム寄りの光で内壁をライムに洗う
pool_light.data.shadow_soft_size = 0.45
pool_light.parent = pool                      # プールと一緒に上昇・下降


# ---------- アニメーション（完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

# PITFALL #14：発光強度は目視でなく hero のライム画素平均を #A5E02E と数値比較して決める。
# 020 の実測カーブ（0.85→#A7E329 / 1.05→#AEEC34 / 1.75→#B8F54E）に本作も概ね乗る想定で、
# プールは exposed 気味なので中域から。内壁は常時ほのかに（満ち引きの主役はプール）。
# hero実測でスイープ： 0.80→#9FD92B / 0.95→#A8E42F（目標 #A5E02E に一致・白飛び0%） / 1.6→#B6F04F（浅い）。
ES_POOL = float(os.environ.get("ES_POOL", "2.6"))  # 2026-07-21引き上げ（#24ペンキ化是正・#14改訂）
# 内壁は自発光させない（＝ ES_INNER 相当は 0）。器の内側の光は「プール＋随伴点光源」だけが
# 作る。こうすると空＝プールが底で小さく暗く沈み内壁は闇／満＝プールが縁まで上がり内腔全体が
# ライムに満ちる、という明滅の落差が生まれる（深い器では水位は見えないので落差で満ち引きを読ませる）。
inner_bsdf.inputs["Emission Strength"].default_value = 0.0
# 抹茶が空でも消えないよう、プール発光は満ち引きで 0 まで落とさず下限を残す（種火）。
POOL_LO = 0.30           # 空のときの発光倍率（満ち=1.0）
LIGHT_LO = 8.0           # 空のときの点光源エネルギー（満ち=LIGHT_E）

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    u = 0.5 * (1 - math.cos(2 * math.pi * t01))     # 0(空)→1(満)→0(空)
    level = LMIN + (LMAX - LMIN) * u
    r = inner_radius_at(level) * 0.97               # 液面を内壁に接させる
    pool.location = (0.0, 0.0, level)
    pool.scale = (r, r, 1.0)
    pool.keyframe_insert(data_path="location", index=2, frame=f)
    pool.keyframe_insert(data_path="scale", frame=f)
    # 発光の満ち引き（明滅）。プール発光と壁を洗う点光源を u で強めて「光が満ちる」を作る。
    pool_bsdf.inputs["Emission Strength"].default_value = ES_POOL * (POOL_LO + (1 - POOL_LO) * u)
    pool_bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
    pool_light.data.energy = LIGHT_LO + (LIGHT_E - LIGHT_LO) * u
    pool_light.data.keyframe_insert("energy", frame=f)
# 毎フレーム打っているので補間設定は不要（PITFALL #1）


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)


def add_caption(body, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object
    tx.name = name
    tx.data.body = body
    tx.data.size = size
    tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.7, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.7, 0.34), "logo")
study = add_caption("MIDDLE STUDY 023 — UTSUWA", 0.045, (0.15, -1.7, 0.22), "study")


# ---------- ライティング（001と同一セットアップ＝シリーズの一貫性） ----------
def add_area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.size = size
    L.data.energy = energy
    L.data.color = color
    direction = Vector(target) - Vector(loc)
    L.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0, 0, CENTER_Z)
add_area("key",  (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
add_area("rim",  (3.5, 4.0, 3.2),  3.0, 420, (0.88, 0.94, 1.0), focus)
add_area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
    bg.inputs[1].default_value = 0.55


# ---------- カメラ ----------
bpy.ops.object.camera_add(location=(0.55, -8.3, 1.95))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, 1.48))   # キャプション3行が入る高さに固定（019〜022と同じ画角）
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = vessel
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam

for tx in (tagline, logo, study):
    tx.rotation_euler = cam.rotation_euler


# ---------- レンダー設定 ----------
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = True
    scene.cycles.device = 'GPU'
    print(">> Metal GPU enabled")
except Exception as e:
    print(">> GPU setup failed, using CPU:", e)

scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
    print(">> view: PBR Neutral")
except Exception:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Punchy'
    print(">> view: AgX Punchy")


# ---------- コンポジター（Bloom / PITFALL #3の新方式） ----------
def setup_bloom():
    try:
        ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out='OUTPUT',
                                socket_type='NodeSocketColor')
        rl = ng.nodes.new("CompositorNodeRLayers")
        glare = ng.nodes.new("CompositorNodeGlare")
        out = ng.nodes.new("NodeGroupOutput")
        try:
            glare.inputs["Type"].default_value = 'BLOOM'
        except Exception:
            glare.inputs["Type"].default_value = 'Bloom'
        glare.inputs["Threshold"].default_value = 1.2
        glare.inputs["Strength"].default_value = 0.35
        try:
            glare.inputs["Size"].default_value = 0.55
        except Exception:
            pass
        ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
        ng.links.new(glare.outputs["Image"], out.inputs["Image"])
        scene.compositing_node_group = ng
        scene.render.use_compositing = True
        print(">> Bloom compositor OK")
    except Exception as e:
        print(">> Bloom setup failed (render continues without):", e)


setup_bloom()


# ---------- 出力モード ----------
modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "probe" in modes:
    # PITFALL #7/#7-b/#18：造形直後にworld座標を数値で確認（テストレンダーより桁違いに速い）
    scene.frame_set(STILL_FRAME)
    deps = bpy.context.evaluated_depsgraph_get()
    for o in [vessel, pool]:
        oe = o.evaluated_get(deps)
        cs = [oe.matrix_world @ Vector(c) for c in oe.bound_box]
        print(f">> {o.name:13s} x={min(c.x for c in cs):+.3f}..{max(c.x for c in cs):+.3f} "
              f"y={min(c.y for c in cs):+.3f}..{max(c.y for c in cs):+.3f} "
              f"z={min(c.z for c in cs):+.3f}..{max(c.z for c in cs):+.3f}")
    w_body = max(abs(c.x) for c in [vessel.evaluated_get(deps).matrix_world @ Vector(c)
                                    for c in vessel.evaluated_get(deps).bound_box])
    print(f">> body half-width={w_body:.3f}  frame-width-budget=1.405 (2.81/2)  "
          f"fill={w_body / 1.405 * 100:.0f}%")
    for nm, lv in (("empty", LMIN), ("full", LMAX)):
        print(f">> pool({nm:5s} lv={lv:+.2f}) inner_r={inner_radius_at(lv):.3f}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_utsuwa.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    keep = {"utsuwa_body", "utsuwa_pool"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "utsuwa.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_apply=True,
        export_yup=True,
    )
    print(">> exported GLB")

if "test" in modes:
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "testhero" in modes:
    # PITFALL #16：480pxでは「何に見えるか」＝造形の意味的破綻が見えない。heroで一度見る。
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test_hero") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> hero-size test done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero still done")

if "anim" in modes:
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'   # PITFALL #2
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
