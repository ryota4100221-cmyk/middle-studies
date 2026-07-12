# =============================================================
# monaka design. — MIDDLE STUDY 017 "KAGIANA"
# 黒い縦板に穿たれた鍵穴。板の裏からライム #A5E02E が差す。
# 板がZ軸で回転し、鍵穴がカメラに正対する瞬間に最も光る。
# 裏を向く間は暗く、回ってきて灯る——扉の向こうの光。
# 鍵穴の奥に、光がある。正対して、はじめて差す。
# "Designing the Middle of Your Story."
#
# 実行:
#   Blender --background --factory-startup --python script.py -- <mode...>
#   modes: test | still | anim | glb | blend
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

PLATE_W = 0.74        # 板の半幅(x)
PLATE_D = 0.09        # 板の半奥行(y)＝厚めで裏の光の透けを防ぎ黒を保つ
PLATE_H = 1.0         # 板の半高(z)

KH_CIRC_R = 0.2       # 鍵穴の円の半径
KH_CIRC_Z = 0.22      # 円の中心高さ（板中心から）
KH_SLOT_TOP = 0.08    # スロット上半幅
KH_SLOT_BOT = 0.17    # スロット下半幅（下に広がる）
KH_SLOT_BOTZ = -0.36  # スロット下端（板中心から）

CORE_EMIT = 1.1       # 鍵穴内壁＋裏パネルの発光（自発光で鍵穴が読めるので低めでよい）
CORE_LIGHT_W = 13     # 裏の点光源

CENTER_Z = 1.3
FPS = 24
N_FRAMES = 120        # 5秒 完全ループ
STILL_FRAME = 47      # ヒーロー：正対から更に振れ、板面が光に斜め＝黒が締まる。鍵穴は楕円に


def hex_to_linear(h):
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
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

# 黒い板（マット寄り。金物の面としてわずかな艶）
mat_plate, b = make_principled("plate_black")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = 0.4
b.inputs["Specular IOR Level"].default_value = 0.28

# 発光する裏のライム
mat_core, core_bsdf = make_principled("core_lime")
core_bsdf.inputs["Base Color"].default_value = LIME
core_bsdf.inputs["Emission Color"].default_value = LIME
core_bsdf.inputs["Emission Strength"].default_value = CORE_EMIT
core_bsdf.inputs["Roughness"].default_value = 0.4

# 白い床
mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

# キャプション
mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8

# ---------- 回転リグ（原点。板を中心軸で回す） ----------
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "KagianaRig"

# ---------- 黒い板（鍵穴をブーリアンでくり抜く） ----------
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, CENTER_Z))
plate = bpy.context.active_object
plate.name = "plate"
plate.scale = (PLATE_W, PLATE_D, PLATE_H)
bpy.ops.object.transform_apply(scale=True)
# PITFALL#7-b: transform_apply(scale)はメッシュをworld焼き込み＆location→0。
# 位置は既にCENTER_Zで正しいのでlocationを再設定しない（二重オフセット回避）。
plate.data.materials.append(mat_plate)

# 角丸ベベル（板の縁）
bev = plate.modifiers.new("Bevel", "BEVEL")
bev.width = 0.02
bev.segments = 3
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(40)

# 鍵穴カッター1：円（Y軸に貫通する円柱）
bpy.ops.mesh.primitive_cylinder_add(radius=KH_CIRC_R, depth=0.4, vertices=64,
                                    location=(0, 0, CENTER_Z + KH_CIRC_Z))
cut_c = bpy.context.active_object
cut_c.name = "cut_circle"
cut_c.rotation_euler = (math.radians(90), 0, 0)   # 軸をY方向へ
cut_c.data.materials.append(mat_core)   # 転写で鍵穴の内壁がライムに光る
cut_c.hide_render = True

# 鍵穴カッター2：台形スロット（XZの台形をY方向へ押し出し）
def make_slot_cutter():
    bm = bmesh.new()
    zt = CENTER_Z + KH_CIRC_Z + 0.02
    zb = CENTER_Z + KH_SLOT_BOTZ
    wt, wb = KH_SLOT_TOP, KH_SLOT_BOT
    y = 0.2
    # 前面(y=-)と後面(y=+)の台形
    fpts = [(-wt, -y, zt), (wt, -y, zt), (wb, -y, zb), (-wb, -y, zb)]
    bpts = [(-wt, y, zt), (wt, y, zt), (wb, y, zb), (-wb, y, zb)]
    fv = [bm.verts.new(p) for p in fpts]
    bv = [bm.verts.new(p) for p in bpts]
    bm.faces.new(fv)
    bm.faces.new(list(reversed(bv)))
    for k in range(4):
        k2 = (k + 1) % 4
        bm.faces.new([fv[k], fv[k2], bv[k2], bv[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("slot")
    bm.to_mesh(me); bm.free()
    me.materials.append(mat_core)   # 転写で鍵穴スロットの内壁がライムに光る
    o = bpy.data.objects.new("cut_slot", me)
    scene.collection.objects.link(o)
    o.hide_render = True
    return o

cut_s = make_slot_cutter()

for cutter in (cut_c, cut_s):
    m = plate.modifiers.new("cut_" + cutter.name, "BOOLEAN")
    m.operation = 'DIFFERENCE'
    m.solver = 'EXACT'
    m.object = cutter
    try:
        m.material_mode = 'TRANSFER'   # 鍵穴の切断面にカッターのライムを転写
    except Exception:
        pass
    cutter.parent = rig   # カッターも板と一緒に回す＝鍵穴が板に固定される

plate.parent = rig

# ---------- 裏のライムパネル＋点光源（板に追従して回る） ----------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, PLATE_D + 0.13, CENTER_Z))
panel = bpy.context.active_object
panel.name = "panel"
panel.scale = (0.34, 0.44, 1.0)
panel.rotation_euler = (math.radians(90), 0, 0)   # 板の裏に正対
bpy.ops.object.transform_apply(scale=True, rotation=True)
# 7-b同様、transform_apply後はlocation再設定しない（既にworld位置に焼き込み済み）
panel.data.materials.append(mat_core)
panel.visible_shadow = False
panel.parent = rig

bpy.ops.object.light_add(type='POINT', location=(0, PLATE_D + 0.22, CENTER_Z + 0.05))
core_light = bpy.context.active_object
core_light.name = "core_light"
core_light.data.energy = CORE_LIGHT_W
core_light.data.color = (LIME[0], LIME[1], LIME[2])
core_light.data.shadow_soft_size = 0.15
core_light.parent = rig

# ---------- アニメーション（板が1回転・正対で最も光る：完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    a = 2 * math.pi * t + math.pi          # +π：t=0.5で正対
    rig.rotation_euler = (0, 0, a)
    rig.keyframe_insert(data_path="rotation_euler", index=2, frame=f)
    facing = max(0.0, math.cos(a))         # 正対度（0..1）
    core_bsdf.inputs["Emission Strength"].default_value = CORE_EMIT * (0.1 + 0.9 * facing)
    core_bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path="default_value", frame=f)
    core_light.data.energy = CORE_LIGHT_W * (0.08 + 0.92 * facing)
    core_light.data.keyframe_insert(data_path="energy", frame=f)

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
                      0.1, (0.15, -1.35, 0.36), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.35, 0.18), "logo")
study = add_caption("MIDDLE STUDY 017 — KAGIANA", 0.045, (0.15, -1.35, 0.055), "study")

# ---------- ライティング（001〜016と同一＝シリーズの一貫性） ----------
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
bpy.ops.object.camera_add(location=(0.3, -6.3, 1.6))
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.0, 0, CENTER_Z + 0.05))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = plate
cam.data.dof.aperture_fstop = 6.5
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

# ---------- コンポジター（Bloom / Blender 5 新方式） ----------
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
            pass
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

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "monaka_kagiana.blend"))
    print(">> saved .blend")

if "glb" in modes:
    scene.frame_set(STILL_FRAME)
    for o in bpy.data.objects:
        o.select_set(o.name in ("plate", "panel"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "monaka_kagiana.glb"),
        export_format='GLB', use_selection=True,
        export_animations=True, export_yup=True, export_apply=True)
    print(">> exported GLB")

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "test2" in modes:
    scene.frame_set(1)  # 裏向き（暗い）状態を確認
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "test_back.png")
    bpy.ops.render.render(write_still=True)
    print(">> test_back render done")

if "hero480" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 48
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero_check.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero_check render done")

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
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

print(">> ALL DONE")
