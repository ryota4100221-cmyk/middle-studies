# =============================================================
# monaka design. — MIDDLE STUDY 021 "FUE"（笛 / 尺八の管）
# 黒い縦笛。前面に指孔が5つ縦一列に並ぶ。
# 管の内腔をライム #A5E02E の「音の粒」が下から上へ駆け上がり、
# 粒が真裏に来た孔だけがライムに光る——音が孔を駆け上がっていく。
# 上端の斜めに削がれた歌口から、光が抜ける。
# 外は黒、真ん中に光がある——管の芯に、音の光がある。
#
# 造形: 外円柱を bmesh で実寸生成。内腔円柱＋指孔カッター5本（Y軸向き＝前面のみ
#       貫通し後壁は残す）＋歌口の斜めボックスを「単一カッター」に合体して
#       boolean DIFFERENCE 一発（重なりは use_self=True で吸収）。
#       object.scale も transform_apply も使わない ＝ PITFALL #7 / #7-b を構造的に回避。
# アニメ: 容器（管）は静止し、光だけが動く——シリーズ初の機構。
#       粒 i の z = Z_LO + frac(i/3 + t)·SPAN で循環＝数学的に完全ループ。
#       両端は envelope で減光し「管の中で」生滅する＝管の外に緑玉が出ない（018の教訓）。
#       粒は管に完全遮蔽され、光は5つの孔へ分散して漏れる
#       ＝集中輝点を作らないので PITFALL #11 のGlare箱・十字は構造的に出ない。
#
# 実行:
#   Blender --background --factory-startup --python monaka_fue.py -- <mode...>
#   modes: probe | test | testmid | still | anim | glb | blend
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector, Matrix

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_fue")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.60      # 管の中心高さ（シリーズ共通の画面中心）
H = 2.10             # 管の全長（外径0.37 に対し 5.7:1 ＝「笛」に読める細長さ）
BOT = CENTER_Z - H / 2   # 0.55（床から浮く＝シリーズの不変条件）
TOP = CENTER_Z + H / 2   # 2.65

# 管は緩いテーパー（下＝管尻が太く、上＝歌口が細い）。ただの円筒は「パイプ」に
# 読めてしまうので、竹の管の膨らみを与えて楽器に寄せる（1周目の教訓）。
# テーパーは「気配」に留める。12%絞ると hero では花瓶／ゴミ箱に読める（4周目の教訓）。
R_BOT = 0.240        # 外半径（下・管尻）
R_TOP = 0.228        # 外半径（上・歌口）／絞り5% ＝ 竹の微かな膨らみだけが残る
RI_BOT = 0.148       # 内半径（下）
RI_TOP = 0.142       # 内半径（上）／肉厚 0.092〜0.086 ＝ 孔に奥行きが出る

HOLE_R = 0.062       # 指孔の半径
# 実物の笛の指孔は等間隔ではなく、歌口から遠いほど間隔が広い（音律）。
# 等間隔だと機械的で「並んだボタン」に読める＝1周目の失敗。非等間隔にして楽器に寄せる。
HOLE_ZS = [0.96, 1.22, 1.46, 1.68, 1.88, 2.06]   # 間隔 0.26/0.24/0.22/0.20/0.18
HOLE_Y = -0.22       # 孔カッターの中心y（前面 -Y のみ貫通し、後壁は残す）
HOLE_DEPTH = 0.64    # y範囲 -0.54..+0.10 ＝ 内腔(±0.15)に届き後壁は無傷

# 歌口は浅く削ぐ。45°/深0.365 では内腔の後壁が三日月の「耳」として飛び出し、
# 笛の管頭でなく栓抜きのフックに読める（heroサイズで発覚＝4周目の教訓）。
CUT_Z = 2.60         # 歌口の斜面が通る高さ
CUT_ANGLE = 30.0     # 前 z=2.47 まで削ぐ（深さ0.18）＝薄いリング状の切り口＝管頭

N_ORBS = 3           # 音の粒の数（孔6個と互いに素＝光が孔を不規則に駆け上がる）
ORB_R = 0.122        # 粒のxy半径（内腔0.138 のぎりぎり内側＝孔を完全に埋める）
ORB_RZ = 0.13        # 粒のz半径。0.19だと孔間隔(0.18〜0.26)を跨いで5孔が同時に
                     # 点いてしまい「音が駆け上がる」ON/OFFが死ぬ＝2周目の教訓。
                     # 短くして1粒=1孔に絞り、点灯/消灯のコントラストを立てる。
Z_LO = 0.72          # 粒の循環下端（管の下端0.55 より内側＝管の中で生まれる）
Z_HI = 2.46          # 粒の循環上端（歌口の奥＝管の中で消える）
FADE = 0.14          # 端のフェード幅（envelope）

ROT0 = -14.0         # 孔の列をわずかに振る（正対の損失は cos14°=0.97 でほぼ無く、
                     # 孔が楕円になって管の丸みが読める：010/017の教訓）

FPS = 24
N_FRAMES = 120       # 5秒 完全ループ
STILL_FRAME = 54     # 粒3つが孔1・3・6の真裏に最もよく揃う＝3孔同時点灯
                     # （全120フレームを数値スコアで探索して決定。14/54/94が同点＝3回対称）


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4：この変換なしだと別の色になる）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)

# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


# 黒漆の管（平らな面・丸い面が環境光を拾ってガンメタに転ぶのを防ぐ：010 SOROBANの教訓）
mat_tube, b = make_principled("tube_black")
b.inputs["Base Color"].default_value = BLACK
# 丸い管は平面（010 SOROBAN）以上に環境光を拾い、縦に走る鋭いハイライトで
# 「黒いプラスチックのパイプ」に転ぶ（heroサイズで発覚）。ラフネスを上げて
# ハイライトを縦に散らし、クリアコートの照りをほぼ落として黒漆＝竹の管に寄せる。
b.inputs["Roughness"].default_value = 0.34
b.inputs["Specular IOR Level"].default_value = 0.30
b.inputs["Coat Weight"].default_value = 0.08
b.inputs["Coat Roughness"].default_value = 0.20

# 音の粒（発光ライム）
# 粒は管に遮蔽されるので key(1400W) の白は乗りにくいが、歌口・下端開口から
# 露出する瞬間があるため、020の教訓に従い純発光体として組む：
# Base Color を暗いライムに落として反射成分を消し、色は emission だけで決める。
orb_mats = []
for i in range(N_ORBS):
    m, bsdf = make_principled(f"orb_lime_{i}")
    bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
    bsdf.inputs["Emission Color"].default_value = LIME
    bsdf.inputs["Emission Strength"].default_value = 2.6
    bsdf.inputs["Roughness"].default_value = 0.55
    bsdf.inputs["Specular IOR Level"].default_value = 0.10
    orb_mats.append((m, bsdf))

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- 彫刻の親（PITFALL #9：リグは必ず原点に置く） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "Sculpture"
rig.rotation_euler.z = math.radians(ROT0)


# ---------- ジオメトリ・ヘルパ（PITFALL #15） ----------
# いずれも「メッシュをワールド実寸で作り、object.location は (0,0,0) のまま」。
# bmesh.ops の scale/rotate/translate は頂点を動かすだけでオブジェクト変換に
# 触れないので、transform_apply が要らない ＝ #7 / #7-b が起こり得ない。

def new_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def _merge(bm, tmp):
    """一時bmeshの中身を bm に取り込む"""
    me = bpy.data.meshes.new("__tmp")
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def cyl_into(bm, r0, r1, z0, z1, segments=64):
    """bm に 中心軸=Z・下半径r0/上半径r1・z0..z1 のテーパー円柱を1本足す"""
    tmp = bmesh.new()
    bmesh.ops.create_cone(tmp, cap_ends=True, segments=segments,
                          radius1=r0, radius2=r1, depth=(z1 - z0))
    bmesh.ops.translate(tmp, vec=(0, 0, (z0 + z1) / 2), verts=tmp.verts)
    _merge(bm, tmp)


def hole_into(bm, z):
    """bm に Y軸向きの指孔カッターを1本足す（前面のみ貫通・後壁は残す）"""
    tmp = bmesh.new()
    bmesh.ops.create_cone(tmp, cap_ends=True, segments=32,
                          radius1=HOLE_R, radius2=HOLE_R, depth=HOLE_DEPTH)
    # 既定のZ軸向き → X軸まわり90°回転でY軸向きへ
    bmesh.ops.rotate(tmp, cent=(0, 0, 0),
                     matrix=Matrix.Rotation(math.radians(90), 3, 'X'),
                     verts=tmp.verts)
    bmesh.ops.translate(tmp, vec=(0, HOLE_Y, z), verts=tmp.verts)
    _merge(bm, tmp)


def mouth_into(bm):
    """bm に 歌口（管頭の斜め削ぎ）のカッターを足す。
    下面がちょうど原点を通る箱を作ってから X軸まわりに回すので、
    回転後の斜面は z = y·tan(θ) + CUT_Z（前が低く後ろが高い＝尺八の管頭）。"""
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=1.0)
    bmesh.ops.scale(tmp, vec=(2.0, 2.0, 2.0), verts=tmp.verts)
    bmesh.ops.translate(tmp, vec=(0, 0, 1.0), verts=tmp.verts)   # 下面を z=0 に
    bmesh.ops.rotate(tmp, cent=(0, 0, 0),
                     matrix=Matrix.Rotation(math.radians(CUT_ANGLE), 3, 'X'),
                     verts=tmp.verts)
    bmesh.ops.translate(tmp, vec=(0, 0, CUT_Z), verts=tmp.verts)
    _merge(bm, tmp)


def add_bevel(o, width=0.008, segs=2):
    """PITFALL #10：全エッジ面取りは平面上に扇状ストリークを生む。鋭角のみに限定。"""
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = width
    bev.segments = segs
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)
    return bev


# ---------- 笛の管 ----------
bm = bmesh.new()
cyl_into(bm, R_BOT, R_TOP, BOT, TOP)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
tube = new_object("fue_tube", bm, mat_tube)
tube.parent = rig

# カッター：内腔＋指孔5本＋歌口 を単一メッシュに合体。
# 互いに重なる（内腔と孔が交差する）が、boolean の use_self=True が
# 自己交差を解決して union として扱うので1回の DIFFERENCE で彫れる。
bmc = bmesh.new()
cyl_into(bmc, RI_BOT, RI_TOP, BOT - 0.15, TOP + 0.30)   # 内腔（上下とも貫通＝両端開口の筒）
for z in HOLE_ZS:
    hole_into(bmc, z)
mouth_into(bmc)
bmesh.ops.recalc_face_normals(bmc, faces=bmc.faces)
cutter = new_object("fue_cutter", bmc, mat_tube)
cutter.hide_render = True
cutter.parent = tube      # 管に追従＝孔が管に固定される（017の教訓）

bo = tube.modifiers.new("bore", "BOOLEAN")
bo.operation = 'DIFFERENCE'
bo.solver = 'EXACT'
bo.use_self = True        # 重なり合うカッター群を union として解決
bo.object = cutter
add_bevel(tube)


# ---------- 音の粒（内腔を駆け上がるライムの光） ----------
def make_orb(name, mat):
    b_ = bmesh.new()
    bmesh.ops.create_uvsphere(b_, u_segments=32, v_segments=16, radius=1.0)
    bmesh.ops.scale(b_, vec=(ORB_R, ORB_R, ORB_RZ), verts=b_.verts)
    bmesh.ops.recalc_face_normals(b_, faces=b_.faces)
    o = new_object(name, b_, mat)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_auto_smooth(angle=0.6)   # PITFALL #6
    o.select_set(False)
    return o


orbs = [make_orb(f"fue_orb_{i}", orb_mats[i][0]) for i in range(N_ORBS)]
for o in orbs:
    o.parent = rig


# ---------- アニメーション（完全ループ） ----------
def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def envelope(u):
    """粒が管の中で生まれ、管の中で消えるための端フェード。
    中央 72% はフル発光なので、孔の前を通る粒は常に最大で光る。"""
    return smoothstep(0.0, FADE, u) * smoothstep(0.0, FADE, 1.0 - u)


scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

# PITFALL #14：色は目視で粘らず hero のライム画素平均を #A5E02E と数値比較して決める。
# 020（露出したほぞ）は 0.85 だったが、本作の粒は管に遮蔽され孔越しにしか見えないので
# 桁が違う。hero を実測してスイープ：
#   2.6 → #ACE24B（白飛び26.9% ＝ NG） / 2.2 → #A6DD40（白飛び0%）
#   1.8 → #9FD632 / 1.4 → #96CD21（暗い）
# 2.2 が目標 #A5E02E に対し R=166/G=221（目標165/224）でほぼ一致＋白飛びゼロ＝採用。
ES_BASE = float(os.environ.get("ES_BASE", "2.2"))

SPAN = Z_HI - Z_LO
for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    for i, o in enumerate(orbs):
        u = ((i / N_ORBS) + t01) % 1.0        # frac ＝ 数学的に閉じる
        o.location.z = Z_LO + u * SPAN
        o.keyframe_insert(data_path="location", index=2, frame=f)
        es = orb_mats[i][1].inputs["Emission Strength"]
        es.default_value = ES_BASE * envelope(u)
        es.keyframe_insert(data_path="default_value", frame=f)
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
                      0.1, (0.15, -1.3, 0.36), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, 0.18), "logo")
study = add_caption("MIDDLE STUDY 021 — FUE", 0.045, (0.15, -1.3, 0.06), "study")


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
look = Vector((0.1, 0, 1.48))   # キャプション3行が入る高さに固定（019/020と同じ画角）
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = tube
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
    # PITFALL #7 / #7-b：造形直後にworld座標を数値で確認（テストレンダーより桁違いに速い）
    scene.frame_set(STILL_FRAME)
    deps = bpy.context.evaluated_depsgraph_get()
    for o in [tube, cutter] + orbs:
        oe = o.evaluated_get(deps)
        zs = [(oe.matrix_world @ Vector(c)).z for c in oe.bound_box]
        ys = [(oe.matrix_world @ Vector(c)).y for c in oe.bound_box]
        print(f">> {o.name:14s} loc.z={o.location.z:+.3f} "
              f"world_z={min(zs):.3f}..{max(zs):.3f} "
              f"world_y={min(ys):.3f}..{max(ys):.3f} "
              f"verts={len(oe.data.vertices)}")
    print(">> hole z:", HOLE_ZS)
    print(">> orb  z:", [round(o.location.z, 3) for o in orbs])

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_fue.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    keep = {"fue_tube"} | {o.name for o in orbs}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "fue.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_apply=True,      # 内腔・指孔（Boolean）を焼き込んで書き出す
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
    # PITFALL #10：造形のアーティファクトは480pxでは潰れて見えない。heroサイズで一度確認。
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_hero.png")
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
