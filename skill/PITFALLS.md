# Blender 5.x ヘッドレスAPIの落とし穴（実戦で踏んだものだけ）

> 2026-07-10、Blender 5.1.1（macOS/M1）で001・002を制作した際に実際に踏んだ罠。
> 新しい罠を踏んだら**このファイルに追記**する。ここが最新の正典。

## 1. `action.fcurves` 直アクセス廃止（slotted actions化）
```python
# ✗ 5.xでAttributeError
for fc in obj.animation_data.action.fcurves: ...
```
**回避**: 補間設定に頼らず**毎フレーム `keyframe_insert` で値を打つ**。ループ動画は元々全フレーム打つ方が確実（cosで値を計算すれば補間の歪みもゼロ）。

## 2. 動画出力は `media_type` を先に切り替える
```python
# ✗ TypeError: enum "FFMPEG" not found
scene.render.image_settings.file_format = 'FFMPEG'
# ○ 先にVIDEOへ切り替えるとFFMPEGがenumに現れる
scene.render.image_settings.media_type = 'VIDEO'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'; scene.render.ffmpeg.codec = 'H264'
```

## 3. コンポジターは `scene.node_tree` 廃止 → node_group方式
```python
ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
rl = ng.nodes.new("CompositorNodeRLayers")
glare = ng.nodes.new("CompositorNodeGlare")
out = ng.nodes.new("NodeGroupOutput")
glare.inputs["Type"].default_value = 'BLOOM'   # ← Glareは全パラメータがinputソケット化
glare.inputs["Threshold"].default_value = 1.2
ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
ng.links.new(glare.outputs["Image"], out.inputs["Image"])
scene.compositing_node_group = ng
scene.render.use_compositing = True
```
`glare.glare_type` のような旧プロパティは存在しない。

## 4. 色の落とし穴2つ
- **hex→linear変換必須**: `#A5E02E` をそのまま `(0.647, 0.878, 0.180)` で入れると別の色になる。`((c+0.055)/1.055)**2.4` でlinear化
- **ビュー変換はKhronos PBR Neutral**: デフォルトのAgXは高輝度のライムを黄土色〜白に転ばせる。ブランドカラーの正確さが要る絵ではPBR Neutral一択（001で比較検証済み）

## 5. Metal GPU有効化（毎回必要・セッション限り）
```python
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.get_devices()
for dev in prefs.devices: dev.use = True
scene.cycles.device = 'GPU'
```

## 6. スムーズシェーディング
`bpy.ops.object.shade_auto_smooth(angle=0.6)` が5.xの正解（旧auto_smoothプロパティは廃止）。ops なのでオブジェクトがactive+selectedの状態で呼ぶこと。

## 7. その他の実戦知識
- `--factory-startup` を付けるとユーザー設定に汚染されず再現性が上がる
- レンダー時間目安（M1 8core GPU・適応サンプリング）: 1600×2000/96smp ≈ 80秒、720×900/16smp ≈ 4秒/フレーム
- glTF書き出しはオブジェクトのlocation/rotationキーフレームをそのままアニメとして持っていける: `bpy.ops.export_scene.gltf(export_format='GLB', use_selection=True, export_animations=True)`
- テキストは `bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")`
- メビウス等の非向き付け形状は「180°対称な断面を半ねじりで掃引」すれば閉じたソリッドになる（002 script.py参照）
- `Material.use_nodes` / `World.use_nodes` はDeprecationWarning（6.0で廃止予定）。今は動くが将来の移行候補
