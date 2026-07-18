# =============================================================
# monaka design. — MIDDLE STUDY 024 "OUGI"（扇 / 要とひだ）
# 黒い扇が宙で開いては閉じる。閉じれば一本の黒い骨、
# 開けば骨（ほね）の隙間の奥から、ライム #A5E02E が襞（ひだ）となってひらく。
# 扇の要（かなめ）＝下端のピボットで全ての骨が束ねられ、
# 真ん中——畳まれた襞の「間（ま）」——に、光がある。
#
# 造形: 黒い骨 N=15 枚（bmesh 実寸スラット、局所原点＝要に置き +Z へ伸ばす）を
#       depth(Y) に PITCH_Y でずらして重ねる。閉じると前後に畳まれた一本の束。
#       両端は「親骨（guard）」＝太く硬い黒。
# 光:   骨の隙間に 1 枚ずつ挿し込んだ発光ライムのスラット N-1 枚。黒骨より奥
#       （+LIME_Y）に置き、角度を半インデックスずらして常に「隙間の真後ろ」に来る。
#       閉じ＝黒束＋親骨の陰に完全に隠れて光が消える／開き＝各隙間の奥に発光面が
#       正対して覗く＝襞の光。奥に隠すのでグレージングにならず面で光る（PITFALL #19 回避）。
#       多数の隙間へ分散するので均一暗面上の集中輝点にならない（#11 の Glare 箱回避）。
#       ＝022 HON（剛体パネル＋光を奥に隠す）を放射に組み替え、019 AYA（黒格子の奥の
#       発光面を隙間から覗かせる）と合成した機構。
# アニメ: θ_i(t) = p_i · S(t)、p_i∈[-1,1]（骨）／半インデックスずらし（発光スラット）。
#       S(t) = SMIN + (SMAX-SMIN)·0.5(1-cos2πt) ＝数学的に完全ループ。
#       回転は各骨の局所原点＝要まわりの rotation_euler.y。
#       object.location=(0,y_i,Z_PIV) を置くだけ・object.scale/transform_apply 不使用（#15）、
#       rig empty を使わないので matrix_parent_inverse の罠（#9）も構造的に回避。
#
# 実行:
#   Blender --background --factory-startup --python monaka_ougi.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_ougi")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.55       # 扇の視覚中心（シリーズ共通の画面中心付近）
Z_PIV = 0.66          # 要（かなめ）の高さ＝全ての骨のピボット。扇はここから +Z へ広がる

N_RIBS = 17           # 骨の総数（両端＝親骨）。奇数＝中央の骨が真上を向く。
                      # 骨を太く・多くして黒を主役に、ライムは襞（隙間）の光に絞る（1周目の反省）
RIB_LEN = 1.78        # 骨の長さ（要からの半径）。この先端が扇の弧を描く
RIB_W = 0.068         # 中骨の幅（接線方向 X）。黒い竹の骨。黒を主役にしつつ、光の襞が
                      # r>RIB_W/Δθ で覗く＝細めると光の帯が要側（中央）へ伸びる
RIB_T = 0.011         # 中骨の厚み（法線方向 Y）
GUARD_W = 0.130       # 親骨の幅（太い＝閉じた時に発光スラットの端まで覆う）
GUARD_T = 0.022       # 親骨の厚み
PITCH_Y = 0.012       # 隣り合う骨の depth(Y) ずらし＝閉じた時の束の厚み

# 発光ライムの襞（隙間 1 つにつき 1 枚）
LIME_LEN = 1.62       # 骨より少し短い＝黒い骨先端が扇の弧の縁を作り、光はその内側に
# 隣接発光スラットが角度的に**重なる**幅にして「奥の連続した発光層」を作る＝どの隙間からも
# 白背景が抜けない（1周目は 0.08 で外側の隙間が白く抜けた：太い親骨が斜め視で奥のライムを遮る）。
# 重なり条件 LIME_W > r·Δθ、r=1.5 で 0.12。閉じは黒束＋親骨が覆う（probe で確認）。
LIME_W = 0.120
LIME_T = 0.006
LIME_Y = 0.125        # 全ての黒骨（最大 y=+(N/2)·PITCH_Y ≈ +0.091）より奥に置く

# 開き角。S = 外端の骨の角度（度）。p=±1 の親骨が ±S になる。
# #18：4:5 の実効横は 2.81。開き幅 ≈ 2·RIB_LEN·sin(SMAX)。SMAX=33° → 1.94（69%）。
SMIN = 1.5            # 閉じ（完全に0にせず、束がわずかに扇状に呼吸する）
SMAX = 31.0           # 開き（半開き62°の扇＝ポートレートに収まる「ひらきかけ」／#18 で横65%）

# 扇面を少し起こしてカメラ（斜め上・x=+0.55）に襞を向ける。まず控えめから。
TILT_X = 7.0          # 各骨を要まわりに X 傾け（＋＝上端が奥へ）
ROT_Z = 4.0           # 全体をわずかに Z ひねり＝左右非対称で「撮った写真」に寄せる（010/017）

FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 61      # t≈0.5 ＝ S が SMAX ＝最も開いた瞬間


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


# 中骨＝黒い竹骨。世界は一様に明るいグレー（env 0.92・シリーズ不変）なので、**鏡面反射は
# 一様な灰色ヴェールになる**（roughness では消せない＝均一な env はどうボかしても同じ灰）。
# 漆（低ラフ＋コート）は逆にヴェールを濃くした（1周目 #313130→2周目 #424241 と悪化）。
# ＝**鏡面反射率そのもの（Specular IOR Level・Coat）を落とす**のが正解：正対面は暗く沈み、
# フレネルで縁だけ明るく立つ＝黒いスラットが縁の光でかたちを持つ。key(1400W) の鋭い
# ハイライトは低反射率でも env ヴェールより明るく出るので、面の陰影＝立体感は保たれる。
mat_rib, b = make_principled("rib_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.35
b.inputs["Specular IOR Level"].default_value = 0.10
b.inputs["Coat Weight"].default_value = 0.0

# 親骨・要＝硬い塗りの黒。中骨よりわずかに反射率を上げて「親骨／中骨」の階層を作る（#17-b）。
mat_guard, b = make_principled("guard_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.30
b.inputs["Specular IOR Level"].default_value = 0.16
b.inputs["Coat Weight"].default_value = 0.05
b.inputs["Coat Roughness"].default_value = 0.20

# 襞の光（隙間の奥の発光ライム）。開いた瞬間、隙間越しに key(1400W) を浴びうる。
# #13/#20 に従い純発光体として組む：Base Color を暗いライムに落として拡散反射の白が
# 発光に上乗せされるのを防ぎ、色は emission だけで決める。
mat_core, core_bsdf = make_principled("core_lime")
core_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Roughness"].default_value = 0.55
core_bsdf.inputs["Specular IOR Level"].default_value = 0.10

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（PITFALL #15） ----------
# メッシュを「局所原点＝要(0,0,0)から +Z へ伸ばす実寸スラット」で作り、object.location に
# 要のワールド位置 (0, y_i, Z_PIV) を置く。object.scale も transform_apply も使わない
# ＝ #7 / #7-b が起こり得ない。回転は object.rotation_euler.y（＝要まわりの扇の開き）。
# rig empty を使わないので #9 の matrix_parent_inverse の罠も構造的に無い。

def new_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def add_bevel(o, width, segs=2):
    """PITFALL #10：全エッジ面取りは平面上に扇状ストリークを生む。鋭角のみに限定。"""
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = width
    bev.segments = segs
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)
    return bev


def make_slat(name, w, t, length, y_depth, bevel_w, mat):
    """要(局所原点)から +Z へ length 伸びる 1 枚。幅 w(X)・厚み t(Y)。
    object.location=(0, y_depth, Z_PIV) を置くだけ＝要がワールド上の回転中心になる。"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, t, length), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, length / 2.0), verts=bm.verts)  # 下端＝局所原点(要)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat)
    add_bevel(o, bevel_w)
    o.location = (0.0, y_depth, Z_PIV)
    o.rotation_euler = (math.radians(TILT_X), 0.0, math.radians(ROT_Z))
    return o


# ---------- 骨（黒） ----------
ribs = []
c = (N_RIBS - 1) / 2.0
for i in range(N_RIBS):
    y_i = (i - c) * PITCH_Y
    is_guard = (i == 0 or i == N_RIBS - 1)
    if is_guard:
        o = make_slat(f"ougi_guard_{i}", GUARD_W, GUARD_T, RIB_LEN, y_i, 0.006, mat_guard)
    else:
        o = make_slat(f"ougi_rib_{i:02d}", RIB_W, RIB_T, RIB_LEN, y_i, 0.003, mat_rib)
    ribs.append(o)

# ---------- 襞の発光ライム（隙間 1 つにつき 1 枚。全て黒骨より奥） ----------
limes = []
for j in range(N_RIBS - 1):
    o = make_slat(f"ougi_lime_{j:02d}", LIME_W, LIME_T, LIME_LEN, LIME_Y, 0.002, mat_core)
    limes.append(o)


# ---------- 要（かなめ）の鋲＝ピボットを締める小さな黒い鋲 ----------
# 17枚の骨と親骨が要に集まる根元は、開き時に太い親骨の底が交差して雑然とする（hero で発覚）。
# 小さな黒い鋲で throat を締めると「1点で束ねられた扇」に読める。静止・非アニメ。
def build_rivet():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.185, 0.30, 0.185), verts=bm.verts)  # x, y(depth), z
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object("ougi_rivet", bm, mat_guard)
    add_bevel(o, 0.055)
    o.location = (0.0, 0.0, Z_PIV)
    o.rotation_euler = (math.radians(TILT_X), 0.0, math.radians(ROT_Z))
    return o


rivet = build_rivet()


# ---------- アニメーション（完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

# PITFALL #14：色は目視で粘らず hero のライム画素平均を #A5E02E と数値比較して決める。
# 発光面は隙間の奥にあり開き時だけ key を浴びる＝半遮蔽。HON の凹面（ES1.3→#AEEC2C）と
# 同域を狙って 1.15 から。still 後に #14 の測定でスイープする。
ES_BASE = float(os.environ.get("ES_BASE", "1.15"))
core_bsdf.inputs["Emission Strength"].default_value = ES_BASE


def S_of(t01):
    return SMIN + (SMAX - SMIN) * 0.5 * (1 - math.cos(2 * math.pi * t01))


for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    S = S_of(t01)
    for i, o in enumerate(ribs):
        p = (i - c) / c                                  # -1（前の親骨）..+1（後の親骨）
        o.rotation_euler.y = math.radians(p * S)
        o.keyframe_insert(data_path="rotation_euler", index=1, frame=f)
    for j, o in enumerate(limes):
        p = ((j + 0.5) - c) / c                           # 常に骨 j と j+1 の「間」の角度
        o.rotation_euler.y = math.radians(p * S)
        o.keyframe_insert(data_path="rotation_euler", index=1, frame=f)
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


# #20-b：キャプションは y=-1.7（カメラに近い）で z が大きな px 間隔に拡大するので、
# hon 流用の 0.36/0.18/0.06 では 3行目（STUDY）がフレーム外に落ちた（bottom-crop で確認）。
# 023 で確立した 0.52/0.34/0.22 へ持ち上げる（要 z=0.62 とも干渉しない）。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.7, 0.52), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.7, 0.34), "logo")
study = add_caption("MIDDLE STUDY 024 — OUGI", 0.045, (0.15, -1.7, 0.22), "study")


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

# 襞の光に「点光源を足さない」——022 HON と同じ判断。発光面は隙間の奥で正対しており
# それ自体が面光源としてすでに読める。軸/隙間に点光源を置くと放射面をグレージングで
# 洗えず「豆電球／LEDテープ」に転ぶ（#19）。足すべきはライトでなく Emission Strength だけ。

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
look = Vector((0.1, 0, 1.48))   # キャプション3行が入る高さに固定（019〜023と同じ画角）
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = ribs[N_RIBS // 2]   # 中央の骨に合焦
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
    # #7/#7-b：造形直後にworld座標を数値で確認（テストレンダーより桁違いに速い）。
    # さらに「閉じで発光スラットが黒束＋親骨に隠れるか」「開きの隙間幅」「開き横幅」を数値で当てる。
    def world_x_range(o, deps):
        oe = o.evaluated_get(deps)
        cs = [oe.matrix_world @ Vector(cc) for cc in oe.bound_box]
        return (min(c.x for c in cs), max(c.x for c in cs),
                min(c.y for c in cs), max(c.y for c in cs),
                min(c.z for c in cs), max(c.z for c in cs))

    for nm, fr in (("closed", 1), ("open", STILL_FRAME)):
        scene.frame_set(fr)
        deps = bpy.context.evaluated_depsgraph_get()
        # 黒骨の union X 幅と、発光スラットの union X 幅
        bx0 = min(world_x_range(o, deps)[0] for o in ribs)
        bx1 = max(world_x_range(o, deps)[1] for o in ribs)
        lx0 = min(world_x_range(o, deps)[0] for o in limes)
        lx1 = max(world_x_range(o, deps)[1] for o in limes)
        S = S_of((fr - 1) / N_FRAMES)
        dth = math.radians(2 * S / (N_RIBS - 1))            # 隣接骨の角度差
        gap = RIB_LEN * dth - RIB_W                          # 開き時の骨エッジ間の隙間（先端）
        persp = 8.3 / (8.3 - 0.0)                            # 扇は y≈0 ＝ 遠近ほぼ等倍
        print(f">> [{nm:6s}] S={S:5.2f}° black_x={bx0:+.3f}..{bx1:+.3f} "
              f"lime_x={lx0:+.3f}..{lx1:+.3f}  frame_w={ (bx1-bx0)*persp:.3f}/2.81 "
              f"({(bx1-bx0)*persp/2.81*100:.0f}%)  gap@tip={gap:+.4f} "
              f"(lime_w={LIME_W} must exceed)")
        # 閉じで発光が隠れるか：黒 union が lime union を包むか
        if nm == "closed":
            covered = (bx0 <= lx0 and bx1 >= lx1)
            print(f">>   closed: black covers lime? {covered}  "
                  f"(black[{bx0:+.3f},{bx1:+.3f}] vs lime[{lx0:+.3f},{lx1:+.3f}])")
    # z 範囲（キャプション z=0.36 と要 z=0.66 の干渉チェック用）
    scene.frame_set(STILL_FRAME)
    deps = bpy.context.evaluated_depsgraph_get()
    zr = [world_x_range(o, deps)[4:] for o in ribs]
    print(f">> open fan z-range = {min(z[0] for z in zr):+.3f}..{max(z[1] for z in zr):+.3f}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_ougi.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    keep = {o.name for o in ribs} | {o.name for o in limes} | {"ougi_rivet"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "ougi.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_apply=True,      # Bevel を焼き込んで書き出す
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
    # PITFALL #16：480pxでは「何に見えるか」＝造形の意味的破綻が見えない。
    # 造形が固まったら必ず一度 heroサイズで目視してから本番へ。
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
