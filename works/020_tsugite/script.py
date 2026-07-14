# =============================================================
# monaka design. — MIDDLE STUDY 020 "TSUGITE"（継手 / 木組みの継ぎ目）
# 黒い角柱が中腹で継がれている。上下の材が離れると、
# 継手の二段ほぞ（tenon）がライム #A5E02E に光って現れる。
# 閉じれば継ぎ目に細い光の線だけが残る。
# 外は黒、真ん中に光がある——柱の芯に、光がある。
#
# 造形: ほぞは「頭（根元の太い段）＋首（先の細い段）」の二段。段はxy両方向に
#       付くので、リグが回ってもどの角度からも段付きプロファイルが読める。
#       上材には素直な角スロットのほぞ穴を boolean DIFFERENCE で彫り、
#       カッターは上材に親付け＝穴が材に固定される（017の教訓）。
#       角柱・ほぞ・カッターは全て bmesh で実寸生成し、object.scale も
#       transform_apply も使わない ＝ PITFALL #7 / #7-b を構造的に回避。
# アニメ: 上材 +d/2 / 下材 -d/2 で対称に開閉＝重心が画面中央に固定される。
#       d(t)=DMIN+(DMAX-DMIN)·0.5(1-cos2πt) を毎フレームキー＝完全ループ。
#       開ききると 頭0.20 全部＋首0.20 が露出し、噛み合いは0.06 残る。
#       リグは原点に置きZ軸を360°回転（PITFALL #9）＝整数周期で閉じる。
#
# 020の教訓: ほぞは柱の外に露出しキーライト(1400W)を遮る物が無いため、
#       Base Color を LIME にすると拡散反射の白が発光に上乗せされて中心が
#       白緑に飛ぶ。Base Color を暗いライムに落とした純発光体にして解消。
#       強度は hero のライム画素平均を #A5E02E と数値比較して決めた（ES_BASE 参照）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_tsugite.py -- <mode...>
#   modes: probe | test | testmid | still | anim | glb | blend
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = 1.60      # 継ぎ目（＝柱の中心）の高さ
W = 0.48             # 角柱の一辺（各材は 0.90/0.48 ≈ 1.9:1 ＝「柱」に読める比）
HH = 0.90            # 上材・下材それぞれの高さ（閉じた柱の全長 = 1.80 / 開くと 2.20）

# 二段ほぞ（頭＝根元の太い段／首＝先の細い段）。抜き出た瞬間に
# 「頭 → 首 → ほぞ穴に消える」段付きプロファイルが出る＝継手として読める。
# 段はxy両方向に付けるので、リグが回っても どの角度からも段が見える。
HEAD_W = 0.27        # 頭の一辺（柱幅0.48の内側に0.105ずつ余白＝黒が額縁になる）
HEAD_H = 0.20        # 頭の高さ（根元 CENTER_Z から上へ）
NECK_W = 0.100       # 首の一辺
NECK_TOP = 0.46      # ほぞ全長（根元からの高さ）
NECK_LAP = 0.02      # 頭と首の重ね（面の一致＝Zファイティングを避ける）

C_PAD = 0.012        # ほぞ穴カッターの隙間（コプラナー回避）
C_DROP = 0.25        # カッターを上材の底面より下へ突き出す量（開口をきれいに）
C_DEPTH = 0.48       # 上材の底面から測ったほぞ穴の深さ（頭が完全に呑まれる深さ）

DMIN = 0.045         # 閉じたときの継ぎ目の隙間（＝細い光の線が残る）
DMAX = 0.40          # 開いたときの隙間（露出＝頭0.20 全部＋首0.20 / 噛み合い0.06残る）

ROT0 = 32.0          # リグの初期角（正対を外して2面に陰影差を作る：010/017の教訓）
                     # 柱もほぞも4回対称なので hero の 32+180=212° は 32° と同じ見え方

FPS = 24
N_FRAMES = 120       # 5秒 完全ループ
STILL_FRAME = 61     # t=0.5 → 開ききった瞬間


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


# 黒漆の材（平らな面が環境光を拾ってガンメタに転ぶのを防ぐ：010 SOROBANの教訓）
mat_post, b = make_principled("post_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.18
b.inputs["Specular IOR Level"].default_value = 0.32
b.inputs["Coat Weight"].default_value = 0.28
b.inputs["Coat Roughness"].default_value = 0.12

# 二段ほぞ（発光ライム）
# Base Color を LIME のままにすると、拡散面が key(1400W) をまともに反射し、
# 発光に白い反射が上乗せされて中心が白緑に飛ぶ（020で判明）。
# ほぞは柱の外に露出する＝キーを遮るものが無いので、純発光体として組む：
# Base Color を暗いライムに落として反射成分を消し、色は emission だけで決める。
mat_tenon, tenon_bsdf = make_principled("tenon_lime")
tenon_bsdf.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1)
tenon_bsdf.inputs["Emission Color"].default_value = LIME
tenon_bsdf.inputs["Emission Strength"].default_value = 1.7
tenon_bsdf.inputs["Roughness"].default_value = 0.55
tenon_bsdf.inputs["Specular IOR Level"].default_value = 0.10

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


# ---------- ジオメトリ・ヘルパ ----------
# いずれも「メッシュをワールド実寸で作り、object.location は (0,0,0) のまま」。
# object.scale も transform_apply も使わないので PITFALL #7 / #7-b は起こり得ない。

def new_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def box_into(bm, cz, sx, sy, sz):
    """bmesh に 中心(0,0,cz)・寸法(sx,sy,sz) のボックスを1つ足す"""
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=1.0)
    bmesh.ops.scale(tmp, vec=(sx, sy, sz), verts=tmp.verts)
    bmesh.ops.translate(tmp, vec=(0, 0, cz), verts=tmp.verts)
    me = bpy.data.meshes.new("__tmp")
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def make_box(name, cz, sx, sy, sz, mat):
    """中心 (0,0,cz)・寸法 (sx,sy,sz) の実寸ボックス（単一マニフォールド）"""
    bm = bmesh.new()
    box_into(bm, cz, sx, sy, sz)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_object(name, bm, mat)


def make_stepped_tenon(name, z0, mat):
    """二段ほぞ：根元の太い「頭」の上に細い「首」。段はxy両方向に付くので
    リグがどの角度を向いても段付きプロファイルが読める。
    2ボックスは NECK_LAP だけ重ねる＝接する面が内部に隠れZファイティングが出ない。
    （booleanの被演算子ではなく発光ソリッドなので、重なりは見た目に無害）"""
    bm = bmesh.new()
    box_into(bm, z0 + HEAD_H / 2, HEAD_W, HEAD_W, HEAD_H)
    neck_lo = z0 + HEAD_H - NECK_LAP
    neck_h = NECK_TOP - HEAD_H + NECK_LAP
    box_into(bm, neck_lo + neck_h / 2, NECK_W, NECK_W, neck_h)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_object(name, bm, mat)


def add_bevel(o, width=0.010, segs=2):
    """PITFALL #10：全エッジ面取りは平面上に扇状ストリークを生む。鋭角のみに限定。"""
    bev = o.modifiers.new("Bevel", "BEVEL")
    bev.width = width
    bev.segments = segs
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)
    return bev


# ---------- 継手の各パーツ ----------
# 下材：CENTER_Z - HH .. CENTER_Z
lower = make_box("tsugite_lower", CENTER_Z - HH / 2, W, W, HH, mat_post)
add_bevel(lower)
lower.parent = rig

# 上材：CENTER_Z .. CENTER_Z + HH
upper = make_box("tsugite_upper", CENTER_Z + HH / 2, W, W, HH, mat_post)
upper.parent = rig

# 二段ほぞ（発光）：下材の肩 CENTER_Z から上へ NECK_TOP。下材に追従させる。
tenon = make_stepped_tenon("tsugite_tenon", CENTER_Z, mat_tenon)
add_bevel(tenon, width=0.007)
tenon.parent = lower

# ほぞ穴カッター：頭が完全に呑まれる角穴（実際の ほぞ穴 と同じく素直な角スロット）。
# 上材に追従＝穴は上材に固定される（017の教訓：カッターを親付けしないと穴がズレる）。
cutter = make_box("tsugite_cutter", CENTER_Z - C_DROP + (C_DROP + C_DEPTH) / 2,
                  HEAD_W + C_PAD * 2, HEAD_W + C_PAD * 2, C_DROP + C_DEPTH,
                  mat_post)
cutter.hide_render = True
cutter.parent = upper

# 上材にほぞ穴を彫る（Boolean → Bevel の順。穴の縁も面取りされる）
bo = upper.modifiers.new("mortise", "BOOLEAN")
bo.operation = 'DIFFERENCE'
bo.solver = 'EXACT'
bo.object = cutter
add_bevel(upper)


# ---------- アニメーション（完全ループ） ----------
def opening(t01):
    """0..1 → 0..1、cosベースなので数学的に閉じる"""
    return 0.5 * (1 - math.cos(2 * math.pi * t01))


scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

es = tenon_bsdf.inputs["Emission Strength"]
# 020の決め方: hero のライム画素平均を #A5E02E と数値比較して決定（目視より速く確実）。
# ES 1.4→2.0 ではトーンマップのショルダーで飽和し G=239→245 しか動かない＝効かない。
# 低域を測って base 0.75→#A7E329 / 0.95→#AEEC34 を確認し、色の正確さと発光感の
# 両立点として 0.85 を採用（hero時 ES=1.15）。
ES_BASE = float(os.environ.get("ES_BASE", "0.85"))

for f in range(1, N_FRAMES + 1):
    t01 = (f - 1) / N_FRAMES
    u = opening(t01)
    d = DMIN + (DMAX - DMIN) * u          # 継ぎ目の隙間＝露出するほぞの長さ

    upper.location.z = d / 2              # 上材は上へ
    upper.keyframe_insert(data_path="location", index=2, frame=f)
    lower.location.z = -d / 2             # 下材は下へ（＝重心は動かない）
    lower.keyframe_insert(data_path="location", index=2, frame=f)

    rig.rotation_euler.z = math.radians(ROT0 + 360.0 * t01)   # 1周＝整数周期
    rig.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

    es.default_value = ES_BASE + 0.30 * u  # 開くほど芯が強く灯る（白飛び回避で控えめ）
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
study = add_caption("MIDDLE STUDY 020 — TSUGITE", 0.045, (0.15, -1.3, 0.06), "study")


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
look = Vector((0.1, 0, 1.48))   # キャプション3行が入る高さに固定（019と同じ画角）
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = tenon
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
    deps = bpy.context.evaluated_depsgraph_get()
    for o in (lower, upper, tenon, cutter):
        oe = o.evaluated_get(deps)
        zs = [(oe.matrix_world @ Vector(c)).z for c in oe.bound_box]
        print(f">> {o.name:16s} loc.z={o.location.z:+.3f} "
              f"world_z={min(zs):.3f}..{max(zs):.3f}")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_tsugite.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("tsugite_lower", "tsugite_upper", "tsugite_tenon"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "tsugite.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_apply=True,      # ほぞ穴（Boolean）を焼き込んで書き出す
        export_yup=True,
    )
    print(">> exported GLB")

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "testmid" in modes:
    # 閉じかけ（噛み合い）の検証用：ほぞ穴がちゃんと機能しているか
    scene.frame_set(1)
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_closed.png")
    bpy.ops.render.render(write_still=True)
    print(">> closed-state test render done")

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
