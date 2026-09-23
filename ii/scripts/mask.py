# =============================================================
# MIDDLE STUDIES II — 被写体だけのマスクを描く（2026-09-23）
#
#   Blender --background --factory-startup --python ii/scripts/mask.py -- <作品の script.py> <出力 mask.png>
#
# 作品の script.py を「何も描かない」モードで実行して、シーンと `parts` を受け取り、
# 被写体（parts とその子）だけを白・それ以外を透明にして、hero と同じ寸法・同じフレームで描く。
# → check.py compose が「四辺の余白」と「輪郭が地から分かれているか」を測る。
#
# 🔴 なぜ在るか：試作3本の構図の弱点（002 球が右端で窮屈／003 本体の下半分が闇に溶ける）は、
#    自己レビューでも「拡大:」でも拾えなかった。拡大は細部を見る道具で、画面全体の組み方は見ない。
#    被写体がどこまでか、を絵から推測させずにシーンから取る。
#
# 作品側の約束：被写体のオブジェクトを `parts`（または `*_parts`）というリストに入れておくこと。
# =============================================================
import bpy, sys, os, runpy

argv = sys.argv[sys.argv.index("--") + 1:]
script, out = os.path.abspath(argv[0]), os.path.abspath(argv[1])

# script.py は sys.argv の "--" 以降をモードとして読む。存在しないモードを渡して何も描かせない
sys.argv = [sys.argv[0], "--", "__mask_only__"]
cwd = os.getcwd()
os.chdir(os.path.dirname(script))
g = runpy.run_path(script, run_name="__main__")
os.chdir(cwd)

subj = []
for k, v in g.items():
    if (k == "parts" or k.endswith("_parts")) and isinstance(v, (list, tuple)):
        subj += [o for o in v if isinstance(o, bpy.types.Object)]
if not subj:
    sys.exit("🔴 script.py に parts（被写体のリスト）が無い")
names = set()
for o in subj:
    names.add(o.name)
    names.update(c.name for c in o.children_recursive)

scene = bpy.context.scene
scene.frame_set(g.get("STILL_FRAME", 1))
for o in scene.objects:
    if o.type in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
        o.hide_render = o.name not in names

white = bpy.data.materials.new("__mask_white"); white.use_nodes = True
nt = white.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
mo = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(em.outputs[0], mo.inputs[0])
bpy.context.view_layer.material_override = white

if scene.world:
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Strength"].default_value = 0.0
scene.render.film_transparent = True
scene.render.engine = "CYCLES"
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.view_settings.view_transform = "Standard"
if "res" in g:
    scene.render.resolution_x, scene.render.resolution_y = g["res"](2560)
scene.render.resolution_percentage = 100
if scene.camera and scene.camera.data.dof:
    scene.camera.data.dof.use_dof = False   # ボケで輪郭が太らないように
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print(">> mask done", out, len(names), "objects")
