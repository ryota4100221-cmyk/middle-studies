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

## 7. `transform_apply(scale=True)` が location を 0 に落とす（003で半日溶かした罠）
```python
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,z))
o = bpy.context.active_object
o.scale = (sx, sy, sz)
bpy.ops.object.transform_apply(scale=True)   # ← ここで o.location.z が 0 に化ける
```
**症状**: 生成物が全部 z=0（床）に落ちる。ただし直後に `keyframe_insert(location)` で毎フレーム座標を書き込むオブジェクトは、キーが上書きするので**気づかない**。アニメを打たない固定オブジェクト（003では断層のライム層）だけが床に取り残される。
**回避**: `transform_apply` の直後に `o.location = (0.0, 0.0, z)` を明示再設定する。あるいは scale を transform_apply せず `o.dimensions` / 親スケールで持つ。
**教訓**: 「固定オブジェクトだけ位置がおかしい」時はまず transform_apply を疑う。デバッグは `o.matrix_world.translation` を print して数値で当たりを取ると速い（テストレンダーを何周も回すより桁違いに速い）。

### 7-b. 逆の罠：`--factory-startup` では location=loc 再設定が二重オフセットになる（004で確認）
2026-07-11の004（ANDON）で判明。**`--factory-startup` 付き**で `transform_apply(scale=True)` を呼ぶと、
Blenderは**メッシュ頂点をワールド位置に焼き込み、`location` を 0 に落とす**（=見た目の位置は変わらない）。
この状態は**すでに正しい位置**なので、直後に `o.location = loc` を足すと **loc ぶん二重に上がる**（004では籠が2倍の高さに浮いた）。

```python
bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y,z))
o.scale = (sx, sy, sz)
bpy.ops.object.transform_apply(scale=True)   # ← ここでメッシュがworld焼き込み・location→0（位置は既に正しい）
# o.location = (x,y,z)   # ✗ --factory-startup下ではこれで z が 2z になる
```

**#7と#7-bの使い分け**:
- 固定オブジェクトが**床に落ちた**（z→0）→ #7。`o.location=loc` を足して復旧。
- 固定オブジェクトが**倍の高さに浮いた**（z→2z）→ #7-b。`o.location=loc` を**消す**。
- **確実な見分け方**: 造形直後に `probe` スクリプトで `o.matrix_world.translation.z` と `bound_box` のworld z範囲を print し、`location=loc` の有無で挙動を2秒で確定させてから本レンダーに進む（004ではこれで即断できた）。挙動は起動オプション（`--factory-startup`）やBlenderバージョンで割れるので、**毎回probeで確認**するのが最速かつ確実。

## 9. 回転リグは「原点」に置く。CENTER_Zに置いて matrix_parent_inverse で相殺しない（005で確認）
005（KAWA）で、リグを `empty_add(location=(0,0,CENTER_Z))` に置き、子の `matrix_parent_inverse = rig.matrix_world.inverted()` で相殺しようとしたら、
**メッシュをz≈0で生成したパーツ（皮）と、primitiveのlocationでCENTER_Zに生成したパーツ（餡）が別々の高さに割れた**（皮が床、餡が中空）。
matrix_parent_inverse はリグのオフセットを打ち消すので、生成時の絶対zがそのまま残り、パーツごとに基準がズレる。

**正解（004/005で確立した方式）**:
- リグ（回転用Empty）は必ず**原点 `(0,0,0)`** に置く。
- 全パーツを**ワールドの CENTER_Z に配置**する（メッシュをz≈0で作ったら `o.location=(0,0,CENTER_Z)`、primitiveなら `location=(0,0,CENTER_Z)` で作る）。
- 親子付けは `o.parent = rig` だけ（matrix_parent_inverse は触らない＝既定のidentity）。
- x=y=0 の中心軸上にあるので、リグを世界Z軸まわりに回せばオブジェクトは自分の垂直軸で回転する。

## 10. 環状/放射メッシュ＋Bevelは「扇状ストリーク」を生む。angle_limitで鋭角のみ面取り（013で確認）
013（HAGURUMA）で、歯車の環状面を内周→外周の1本の長いクアッドで張り、Bevelモジュール（既定=全エッジ）を掛けたら、
**平面上の放射エッジ全部が面取りされ、高解像度レンダーで中心から広がる「扇状ストリーク」**が出た（低解像度テストでは見えず、heroサイズで初めて発覚）。

**回避**:
- Bevelは `bev.limit_method='ANGLE'` ＋ `bev.angle_limit=radians(30)` にして、**鋭角の辺（歯先・縁・穴）だけ**面取り。平面上の放射エッジ（二面角ほぼ0）は除外される。
- 環状面は**半径方向を複数リングに分割**して、内→外の長い1本クアッドを避ける（面が素直になり陰影も安定）。
- bmeshで大量頂点を作った後は `bmesh.ops.remove_doubles` ＋ `recalc_face_normals` で法線の乱れ（これもストリークの原因）を潰す。
- **教訓**: 手続き造形は必ず一度**heroサイズ（1600×2000相当）でテスト**する。480pxテストでは面のアーティファクトが潰れて見えない。

## 11. 均一な暗い面の上の「集中した発光点」はGlare(BLOOM)が箱状＋十字アーティファクトを出す（011で確認）
011（NAMI）で、黒い水面の中心に小さな発光球＋点光源を置いたら、中心に**淡い正方形の箱＋十字（＋）**が出た。
- **消えない対処**（全部ハズレ）：マテリアルをマット化（反射除去）／発光体の`visible_shadow=False`／fillライトの`use_shadow=False`／発光輝度を下げる——どれも効かなかった。
- **正体**：シリーズ不変のコンポジタGlare（Type=BLOOM）はFFT畳み込みなので、**強く集中した輝点の周りに正方形の畳み込みカーネル跡＋streakの十字**を残す。004/007等では核が大きい／背景が忙しく目立たないが、**均一な暗い面（水面・大きな黒盤）の上だと露出する**。
- **効いた対処**：中心の**集中発光オブジェクトを廃止**する。輝点を作らなければFFT箱も十字も出ない。011では「中心の芯」をやめ、最内の生まれたてリング＋`shadow_soft_size`大の柔らかい点光源のみにして解消。
- **教訓**：大きな均一面（水面/黒盤/床）の上に強い輝点を置く構図は避ける。中心の光は「面で」表現するか、リング/エッジなど非集中の形にする。Glare設定は不変なので**造形側で輝点を作らない**のが正解。

## 8. その他の実戦知識
- `--factory-startup` を付けるとユーザー設定に汚染されず再現性が上がる
- レンダー時間目安（M1 8core GPU・適応サンプリング）: 1600×2000/96smp ≈ 80秒、720×900/16smp ≈ 4秒/フレーム
- glTF書き出しはオブジェクトのlocation/rotationキーフレームをそのままアニメとして持っていける: `bpy.ops.export_scene.gltf(export_format='GLB', use_selection=True, export_animations=True)`
- テキストは `bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")`
- メビウス等の非向き付け形状は「180°対称な断面を半ねじりで掃引」すれば閉じたソリッドになる（002 script.py参照）
- **糸/線を「巻き取り→ほどき」で見せたい時は curve の `bevel_factor_end` をアニメする**（006 ITOで確立）。カーブに `bevel_depth` を付けて発光チューブにし、`cu.bevel_factor_end` を cos で 1→0.05→1 にキーフレーム（`cu.keyframe_insert("bevel_factor_end", frame=f)`）すれば、掃引ジオメトリが端から生えては引っ込む＝糸が巻き取られる/ほどける。**headlessでも毎フレーム更新される**。0まで下げると完全消滅するので下限は0.05程度残す。球面スパイラルは `a=π·t`（極角）/ `azi=2π·N·t`（方位）で生成。glTFはbevel_factorアニメを持っていけない（静止ジオメトリのみ）点だけ注意。新造形は**アニメが効くか中間フレームを1枚テストレンダー**して確認してから本番へ（本番アニメは10分かかるので空振り防止）。
- `Material.use_nodes` / `World.use_nodes` はDeprecationWarning（6.0で廃止予定）。今は動くが将来の移行候補
