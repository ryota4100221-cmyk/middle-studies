# =============================================================
# monaka design. — MIDDLE STUDY 022 "HON"（本 / 綴じ目）
# 黒い本が宙に立ち、こちらへ向かって開く。
# 開くと綴じ目（ノド）の奥にライム #A5E02E が灯り、
# 閉じるとページ束が光を完全に遮蔽して、光は消える。
# 外は黒、真ん中に光がある——本の真ん中に、光がある。
#
# シリーズのタグライン "Designing the Middle of Your Story." を
# 文字どおり立体化した題材。物語の真ん中＝綴じ目。
#
# 造形: ページ＝bmesh の薄い実寸パネル24枚（両端2枚は一回り大きい厚表紙）。
#       法線方向に PITCH ずつオフセットして積み、綴じ軸＝ワールドZ軸に置く。
#       object.scale も transform_apply も使わない ＝ PITCHFALL #7 / #7-b を構造的に回避。
# アニメ: object.rotation_euler.z だけでページを振る。
#       φ_i = A(t)·(sign(s)·(1-K) + s·K)  （s＝正規化した綴じ位置 -1..+1）
#       各半束は剛体的に開きつつ、K=0.28 の内部扇で「束」に見せる。
#       A(t) = AMIN + (AMAX-AMIN)·0.5(1-cos2πt) ＝数学的に完全ループ。
#       光は綴じ軸上の細いライム棒（純発光体）。開くとV字の谷に現れ、
#       閉じるとページ束の裏に隠れて消える＝「閉じた本に光はない」。
#
# 実行:
#   Blender --background --factory-startup --python monaka_hon.py -- <mode...>
#   modes: probe | test | testhero | still | anim | glb | blend
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_hon")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.62      # 本の中心高さ（シリーズ共通の画面中心）

N_LEAVES = 24        # ページ総数（両端の2枚＝表紙）
# 4:5ポートレートの実効フレームは 縦3.52 × 横2.81（85mm・距離8.3・sensor_fit=AUTOで
# 36mmが長辺＝縦に載る）。開いた本の横幅 ≈ 2·(SPINE_R+PAGE_W)·sin(AMAX) が
# 支配的なので、ページ幅と開き角の両方で横を殺さないと画面からはみ出す。
PAGE_W = 1.22        # ページの幅（綴じ目からの半径方向）。PAGE_H との比 1.52 ＝実本の判型。
                     # 幅を削って縦長にすると「本」でなく「黒い板」に読める（1周目の失敗）
PAGE_H = 1.85        # ページの高さ（縦置き＝4:5ポートレートに最適）
THICK = 0.016        # 中身ページの厚み
PITCH = 0.018        # ページの積みピッチ。THICKとの差＝隙間 0.002（hero で 1.1px）。
                     # 0.012/0.019（隙間が厚みの58%）では小口がヒートシンクのフィンに読め、
                     # 0.016/0.021（31%）でもまだ隙間の奥が見えてグリルに読めた（5・6周目）。
                     # 実本の小口はほぼ密＝細い線が並ぶだけ。隙間は「見える」と紙をやめる。

COVER_T = 0.030      # 表紙の厚み（中身の2.5倍＝「厚表紙」に読ませる）
COVER_DW = 0.035     # 表紙のはみ出し（幅）。実本の表紙は中身より一回り大きい
COVER_DH = 0.050     # 表紙のはみ出し（高さ）

SPINE_R = 0.095      # 綴じ軸からページ内縁までの距離（＝ノドの幅）。見開きの
                     # スリット幅 = 2·SPINE_R·sin(A·(1-K)) を決める＝光の見え方の主役

# 背（ハードカバーの背表紙）。中身と表紙を1冊に繋ぐ構造で、これが無いと
# 「黒い板が2枚浮いている」絵になる（5周目・heroで発覚）＝本に読ませる決定打。
# 後方の170°だけを覆う中空の半円筒シェル。ページは -Y から±26°の範囲しか
# 振らないので、95°〜265°に置けば決して当たらない。
# **光は、この背の内側（凹面）そのもの**。軸上に発光する棒を置くと、どう細くしても
# heroでは「裸の緑棒」に読める（2・5周目で2回失敗／018と同じ罠）。凹面を発光させれば
# 光源は本の奥に隠れ、見開きのスリットからだけ覗く＝「本の真ん中が光っている」。
# 007 KIRITORI（くり抜いた空洞の内壁だけが光る）・017（内壁をマテリアル転写で発光）と同じ手。
SPINE_RI = 0.175     # 背の内半径（凹面＝発光ライム）
SPINE_RO = 0.205     # 背の外半径（凸面＝黒。閉じた本ではページ束の陰に完全に隠れる）
                     # ＝束の半幅(12·PITCH=0.216)より内側であること。はみ出すと閉じても光が漏れる
SPINE_A0 = 95.0      # 背の張り出し角（-Y方向を0°として後方へ）
SPINE_A1 = 265.0

# 開き角。A=0 で全ページが -Y（カメラ方向）を向いた「閉じた本」。
AMIN = 4.0           # 閉じ（完全に0にせず、小口がわずかに扇状に開く＝本の呼吸）
AMAX = 26.0          # 開き（見開き52°＝手に持って読む本の角度）。76°では横2.04＝
                     # フレーム幅2.81の73%で表紙が切れた（1周目のテストで発覚）

# 半束の内部扇。剛体パネルは扇状に開くと必ず互いを貫通するので、Kには幾何の上限がある。
# 外縁 r=SPINE_R+PAGE_W での隣接ページのクリアランス： PITCH - THICK - r·Δφ ≥ 0。
# 扇は「半束の中」で配るので隙間は半束あたり 11 個（23個ではない＝最初の見積りの誤り）。
# 隙間を 0.002 まで詰めた分、許される Δφ も減る： Δφ ≤ 0.002/1.31 = 0.087° → K ≤ 0.037。
# K=0.03 なら半束で 0.8° の扇＝実本の見開き（半束はほぼ平行）と同じ控えめさ。
# ＝「紙に見せる（隙間を詰める）」ことと「扇を効かせる」ことはトレードオフ。紙を取る。
# （実本のページは撓んで扇状に開くが、ここは剛体パネルなので幾何が上限を決める）
K_FAN = 0.03

# 本をわずかに振る（閉じでは小口が斜めに見え、開きでは左右非対称になって
# 「撮った写真」に寄る：010/017の教訓）。**符号が効く**：カメラは x=+0.55 から
# x=+0.1 を見ているのでフレームは右に余裕があり、左は詰まっている。-10° だと
# 左の表紙がカメラ側へ振り出て遠近で1.14倍に拡大し、フレーム左で切れた（2周目）。
# +10° で右へ振ると、空いている右の余白を使って収まる。
ROT0 = +10.0

FPS = 24
N_FRAMES = 120       # 5秒 完全ループ
STILL_FRAME = 61     # t=0.5 ＝ A が AMAX ＝最も開いた瞬間


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


# ページ＝黒い紙。PITFALL #17 は「平面ならラフ0.20＋コート0.28の黒漆」と言うが、
# それは枠・角柱・板の話で、**紙に当てると死ぬ**：24枚の平行なページに漆の艶を乗せたら
# 小口が機械加工アルミのヒートシンクに読めた（5周目・heroで発覚）。紙はマット。
# ＝ #17 の使い分けに「紙・布」の第3項を足す。
mat_page, b = make_principled("page_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.58
b.inputs["Specular IOR Level"].default_value = 0.22
b.inputs["Coat Weight"].default_value = 0.0

# 表紙＝クロス装の板。紙より硬く、わずかに照る。中身と質感を変えることで
# 「表紙／中身」の階層が生まれ、本に読める（全部同じ質感だと板の束になる）。
mat_cover, b = make_principled("cover_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.34
b.inputs["Specular IOR Level"].default_value = 0.30
b.inputs["Coat Weight"].default_value = 0.12
b.inputs["Coat Roughness"].default_value = 0.22

# 綴じ目の光（背の凹面に貼る発光ライム）
# 開いた瞬間、凹面は見開きのスリット越しに key(1400W) を浴びうる。
# 020の教訓に従い純発光体として組む：Base Color を暗いライムに落として
# 拡散反射の白が発光に上乗せされるのを防ぎ、色は emission だけで決める。
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


# ---------- 彫刻の親（PITFALL #9：リグは必ず原点に置く） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "Sculpture"
rig.rotation_euler.z = math.radians(ROT0)


# ---------- ジオメトリ・ヘルパ（PITFALL #15） ----------
# メッシュをワールド実寸で作り、object.location は (0,0,0) のまま。
# bmesh.ops の scale/translate は頂点を動かすだけでオブジェクト変換に触れないので
# transform_apply が要らない ＝ #7 / #7-b が起こり得ない。

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


def make_leaf(name, w, h, thick, xoff, bevel_w, mat):
    """綴じ軸から -Y 方向へ伸びる1枚。xoff ＝ 束の中での積み位置（法線方向）。
    オブジェクト原点は綴じ軸(0,0,0)なので、rotation_euler.z がそのまま開き角になる。"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(thick, w, h), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(xoff, -(SPINE_R + w / 2), CENTER_Z), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_object(name, bm, mat)
    add_bevel(o, bevel_w)
    o.parent = rig
    return o


# ---------- ページ束 ----------
leaves = []
half = (N_LEAVES - 1) / 2.0
for i in range(N_LEAVES):
    xoff = (i - half) * PITCH
    is_cover = (i == 0 or i == N_LEAVES - 1)
    if is_cover:
        o = make_leaf(f"hon_cover_{i}", PAGE_W + COVER_DW, PAGE_H + COVER_DH,
                      COVER_T, xoff, 0.006, mat_cover)
    else:
        o = make_leaf(f"hon_page_{i:02d}", PAGE_W, PAGE_H, THICK, xoff, 0.003, mat_page)
    leaves.append(o)


# ---------- 背表紙（中空の半円筒シェル／凹面だけが発光ライム） ----------
# 面ごとにマテリアルを塗り分けたいので、boolean ではなく bmesh で直に張る
# （017 はマテリアル転写で内壁を発光させたが、直に張れば転写の当たり外れが無い）。
SPINE_H = PAGE_H + COVER_DH
SPINE_SEG = 64


def build_spine():
    bm = bmesh.new()
    zb = CENTER_Z - SPINE_H / 2
    zt = CENTER_Z + SPINE_H / 2

    def v(r, a_deg, z):
        a = math.radians(a_deg)
        # -Y方向を0°として後方へ回る（ページの角度定義と同じ座標系）
        return bm.verts.new((r * math.sin(a), -r * math.cos(a), z))

    ob, ot, ib, it = [], [], [], []
    for j in range(SPINE_SEG):
        a = SPINE_A0 + (SPINE_A1 - SPINE_A0) * j / (SPINE_SEG - 1)
        ob.append(v(SPINE_RO, a, zb))
        ot.append(v(SPINE_RO, a, zt))
        ib.append(v(SPINE_RI, a, zb))
        it.append(v(SPINE_RI, a, zt))
    bm.verts.ensure_lookup_table()

    lime_faces = []
    for j in range(SPINE_SEG - 1):
        bm.faces.new((ob[j], ob[j + 1], ot[j + 1], ot[j]))          # 外（凸）＝黒
        lime_faces.append(bm.faces.new((ib[j], it[j], it[j + 1], ib[j + 1])))  # 内（凹）＝発光
        bm.faces.new((ot[j], ot[j + 1], it[j + 1], it[j]))          # 天
        bm.faces.new((ob[j], ib[j], ib[j + 1], ob[j + 1]))          # 地
    bm.faces.new((ob[0], ot[0], it[0], ib[0]))                      # 木口（左）
    bm.faces.new((ob[-1], ib[-1], it[-1], ot[-1]))                  # 木口（右）

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lime_set = set(lime_faces)
    for f in bm.faces:
        f.material_index = 1 if f in lime_set else 0

    me = bpy.data.meshes.new("hon_spine")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("hon_spine", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat_cover)   # slot 0 ＝ 黒
    o.data.materials.append(mat_core)    # slot 1 ＝ 発光ライム
    o.parent = rig
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_auto_smooth(angle=0.6)   # PITFALL #6
    o.select_set(False)
    return o


spine = build_spine()


# ---------- アニメーション（完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

# PITFALL #14：色は目視で粘らず hero のライム画素平均を #A5E02E と数値比較して決める。
# hero実測でスイープ： 2.0 → #B9F454（明るく浅い。020の ES1.75→#B8F54E とほぼ同じ位置）。
# 020の実測カーブ（0.85→#A7E329 / 1.05→#AEEC34 / 1.75→#B8F54E）に本作もよく乗るので、
# 目標 #A5E02E に当たる 0.9 付近を採る。凹面は本の奥にあり key を遮る物が無いため、
# 露出したほぞ（020）と同じ桁になる＝「遮蔽されているか露出しているか」で桁が決まる。
ES_BASE = float(os.environ.get("ES_BASE", "1.3"))
core_bsdf.inputs["Emission Strength"].default_value = ES_BASE

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    A = AMIN + (AMAX - AMIN) * 0.5 * (1 - math.cos(2 * math.pi * t01))
    for i, o in enumerate(leaves):
        s = (i - half) / half                      # -1（表表紙）..+1（裏表紙）
        sgn = -1.0 if s < 0 else 1.0
        phi = A * (sgn * (1.0 - K_FAN) + s * K_FAN)
        o.rotation_euler.z = math.radians(phi)
        o.keyframe_insert(data_path="rotation_euler", index=2, frame=f)
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
                      0.1, (0.15, -1.7, 0.36), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.7, 0.18), "logo")
study = add_caption("MIDDLE STUDY 022 — HON", 0.045, (0.15, -1.7, 0.06), "study")


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

# 綴じ目に「点光源を足さない」ことがこの作品の答え（3・4周目に2回失敗して確定）。
# 011 NAMI・014 NENRIN では柔らかい点光源が効いたが、本作の幾何では原理的に効かない：
# 光源を綴じ軸に置くと、ページは光線に対してほぼ平行（グレージング入射）なので面が
# 洗えず、光源のすぐ隣（0.07）だけが逆二乗で強く光る＝離散したホットスポットになる。
#   3灯 → 見開きに光の玉が3つ＝「本の中に豆電球が3つ入っている」
#   9灯 → 粒が繋がらず＝「LEDテープ」（品質チェックリストの禁則そのもの）
# 綴じ目の光の棒は、それ自体が連続した線光源として既にページを照らしている。
# 足すべきはライトではなく、棒の Emission Strength だけ。

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
look = Vector((0.1, 0, 1.48))   # キャプション3行が入る高さに固定（019〜021と同じ画角）
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = spine
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
    for o in [leaves[0], leaves[N_LEAVES // 2 - 1], leaves[N_LEAVES // 2],
              leaves[-1], spine]:
        oe = o.evaluated_get(deps)
        cs = [oe.matrix_world @ Vector(c) for c in oe.bound_box]
        print(f">> {o.name:14s} rotz={math.degrees(o.rotation_euler.z):+6.2f}° "
              f"x={min(c.x for c in cs):+.3f}..{max(c.x for c in cs):+.3f} "
              f"y={min(c.y for c in cs):+.3f}..{max(c.y for c in cs):+.3f} "
              f"z={min(c.z for c in cs):+.3f}..{max(c.z for c in cs):+.3f}")
    # 隣接ページが貫通しないかの幾何チェック（K_FAN の上限＝交差半径 > ページ外縁）
    dphi = math.radians(AMAX * K_FAN / (half - 0.5))
    r_out = SPINE_R + PAGE_W
    print(f">> adjacent d-phi={math.degrees(dphi):.3f}° "
          f"clearance_at_outer_edge={PITCH - THICK - r_out * dphi:+.4f} (must be > 0)")
    for nm, A in (("closed", AMIN), ("open", AMAX)):
        slit = 2 * SPINE_R * math.sin(math.radians(A * (1 - K_FAN)))
        print(f">> slit({nm:6s} A={A:4.1f}°) = {slit:.4f} "
              f"= {slit / 2.81 * 1600:5.1f}px @hero")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_hon.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    keep = {o.name for o in leaves} | {"hon_spine"}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "hon.glb"),
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
