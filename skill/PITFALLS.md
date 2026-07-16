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

## 12. 「伸びて千切れる」液滴はメタボール2球ではなく回転体＋シェイプキーで作る（018で確認）
018（SHIZUKU 雫）で、黒い液滴の伸展→ネック→千切れを**メタボール2球**（上下2オブジェクトを同名グループで融合）で作ろうとして破綻した。
- **症状**: 2球はごく近距離でしか融合せず、少し離すと即座に**独立した2つの球**にスナップ分離する（ネック結合レンジが短い）。しかも間に置いた発光ライム球が**裸の緑玉**として宙に浮き、「等サイズの黒2球＋緑の玉」という完全にオフブランドな絵になった。低threshold/高stiffness/travel縮小でも、ドラマチックな長い細ネックは出せない。
- **回避（正解）**: 液滴を**surface of revolution（回転体）としてラーゼ生成**し、ネックを痩せさせる**シェイプキー "stretch"** を1枚足して伸展量svでアニメする。黒メッシュは**繋がったまま**細い糸になるので、ネックに置いた発光ライム球が「痩せた黒糸の断面＝芯」として読める（裸の緑玉にならない）。sv=0.5(1-cos2πt)で完全ループ。ライム球はsvに比例して露出（融合時sv=0で半径0＝球に戻ると芯が消える）。
- **造形メモ**: 回転体プロファイルを対称レモン（r=√sin(πu)）にするとネックの上側が**傘/きのこ状に膨らむ**。頂点(u=0)細・底(u=1)太の**ティアドロップにskew**（例 env=√sin(πu)・skew=0.58+0.62u）し、ネック位置UWを付け根寄り(0.19)に上げると小さなnub＋細ネック＝ちゃんと"雫の垂れ"に読める。頂点/底のポール中心をシェイプ間で頂点数一致させる（両シェイプ同数リング＋2ポール）。
- **教訓**: メタボールは「融合したまま呼吸/回転」（004行灯の核など）には向くが、「伸びて千切れる」トポロジー変化の演出には結合レンジが足りない。連続した細ネックの造形は回転体＋シェイプキーが確実。

## 13. 露出した発光体は Base Color=LIME にすると白飛びする。純発光体として組む（020で確認）
020（TSUGITE）で、黒柱から露出する発光ライムのほぞを `Base Color=LIME + Emission=LIME/2.8` で作ったら**中心が白緑に飛んだ**。
- **正体**: ほぞは柱の外に露出していて **key(1400W) を遮る物が無い**。LIMEの拡散面がキーの白色光をまともに反射し、その白が発光に上乗せされる。001の餡や019の裏面パネルが飛ばないのは、**他のパーツに遮られて直接キーが当たらない**から。
- **回避**: 露出する発光体は**純発光体として組む**。`Base Color` を暗いライム（例 `(0.015,0.030,0.005)`）に落として反射成分を消し、色は emission だけで決める。`Specular IOR Level` も 0.10 程度に。
- **教訓**: 「発光体が周りに遮られているか、裸で露出しているか」でマテリアルの作り方を変える。裸なら純発光体。

## 14. 発光強度は目視でなく**ピクセル値を #A5E02E と数値比較**して決める（020で確立）
020で発光強度を目視スイープしたが、**ES 1.4→2.0 でライム平均が G=239→245 しか動かなかった**＝すでにトーンマップ（PBR Neutral）のショルダーで飽和していて、目視では違いが分からず何周も溶かした。
- **正しい手順**: レンダー後にライム画素の平均を出して `#A5E02E` と直接比べる。低域まで測ると効く範囲が一発で分かる（020: ES 0.85→#A7E329 / 1.05→#AEEC34 / 1.75→#B8F54E）。
```python
from PIL import Image
px = list(Image.open('hero.png').convert('RGB').getdata())
lime = [p for p in px if p[1] > 90 and p[1] > p[2] + 45 and p[1] >= p[0] + 20]
avg = tuple(round(sum(p[i] for p in lime) / len(lime)) for i in range(3))
print("#%02X%02X%02X" % avg)   # ← #A5E02E に寄せる
```
- **シリーズの実測基準**（この数字に寄せる）: 019 AYA `#A2D150`（最良）/ 020 TSUGITE `#ABE92A` / 001 THE FILLING `#C3EC88`（飛び気味）/ 014 NENRIN `#7FA246`（暗め）
- **注意**: 480pxテストと1600px heroで見え方が変わる（480pxでは白飛びを見落とす）。**測るのは hero**。低解像度テストでの目視は構図・造形の判定に使い、色の判定には使わない。
- **教訓**: 色は不変条件（ブランド）なので、主観で粘らず数値で当てる方が速くて確実。ES_BASE を env var で外出しすると数秒でスイープできる。

## 15. object.scale / transform_apply を最初から使わなければ #7/#7-b は起こらない（020で確立）
#7 と #7-b は「どっちに転ぶか毎回probeで確認」が必要で消耗する。020では**そもそも両方使わない**書き方にして罠を構造的に消した。
- bmesh でメッシュを**ワールド実寸**で作り、`object.location` は `(0,0,0)` のまま置く。`bmesh.ops.create_cube(size=1)` → `bmesh.ops.scale` → `bmesh.ops.translate` は**メッシュ頂点を動かすだけ**でオブジェクト変換には触れないので、transform_apply が要らない。
- アニメはその上に `o.location.z` のキーを**差分として**乗せればよい（メッシュのオフセット＋location で合成される）。
- boolean のカッターも同じ作りにして被演算子に `parent` するだけで、穴が材にぴったり固定される（親のparent_inverseは既定のidentityのまま触らない＝#9とも整合）。
- ベベル幅が非一様スケールで歪む問題も同時に消える（object.scaleが1のまま）。
- **教訓**: 新規スクリプトはこの方式を既定にする。primitive_*_add＋scale＋transform_apply は罠が多い。

## 16. 480pxでは「造形の意味的な破綻」が見えない。シルエットの"読み"はheroサイズで判定する（021で確認）
#10 は「面のアーティファクトが潰れて見えない」話だったが、021（FUE 笛）で**もっと重い失敗**が同じ原因で起きた。
480pxテストを3周回して「笛に読める」と合格を出した造形が、heroサイズにした瞬間に**3つ同時に別物へ転んだ**：
- **歌口の45°削ぎ** → 内腔の後壁が三日月の「耳」として飛び出し、笛の管頭ではなく**栓抜きのフック**に見えた（480pxでは単なる「斜めの口」に見えていた）
- **テーパー12%（下0.245→上0.215）** → **花瓶／ゴミ箱**に見えた（480pxでは気づかない絞り量）
- **丸い管の縦ハイライト** → **黒いプラスチックのパイプ**に見えた（後述 #17）

**教訓**: 480pxテストで判定してよいのは**構図・余白・明暗のバランス**まで。「**何に見えるか**」＝シルエットの意味は解像度が上がると変わる。
造形が固まった時点で**必ず一度 heroサイズ（1600×2000/96smp、M1で約30秒）を目視**してから本番へ。480pxを何周回しても意味的破綻は出てこない。
（021では 480px×3周 → heroで3つ露出 → 修正 → heroで再確認、の順で4周目に収束した）

## 17. 丸い面は平面より環境光を拾う。ラフネス0.20+コート0.28の「黒漆」レシピは筒/球には効かない（021で確認）
010 SOROBAN で確立した黒漆レシピ（ラフ0.20 / スペキュラ0.32 / コート0.28）は**平らな枠・桁**用。
021 の丸い管に同じ値を当てたら、明るい環境光（0.92×0.55）が丸面に**縦一本の鋭い白ストリーク**として映り込み、**黒いプラスチックのパイプ**に転んだ。
平面はハイライトが面ごとに均一に乗るが、曲面は環境の映り込みが線状に集中するため、同じ値でも樹脂に見える。
- **回避（021の採用値）**: ラフネス **0.34** / スペキュラ 0.30 / コート **0.08** / コートラフ 0.20。ハイライトを縦に散らし、クリアコートの照りを落とす。
- **使い分け**: 平面主体（枠・板・角柱）→ ラフ0.20・コート0.28（010/020）。曲面主体（管・球・チューブ）→ ラフ0.34・コート0.08（021）。019 AYAの丸チューブが0.34で黒を保てていたのとも整合。

## 8. その他の実戦知識
- `--factory-startup` を付けるとユーザー設定に汚染されず再現性が上がる
- レンダー時間目安（M1 8core GPU・適応サンプリング）: 1600×2000/96smp ≈ 80秒、720×900/16smp ≈ 4秒/フレーム
- glTF書き出しはオブジェクトのlocation/rotationキーフレームをそのままアニメとして持っていける: `bpy.ops.export_scene.gltf(export_format='GLB', use_selection=True, export_animations=True)`
- テキストは `bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")`
- メビウス等の非向き付け形状は「180°対称な断面を半ねじりで掃引」すれば閉じたソリッドになる（002 script.py参照）
- **糸/線を「巻き取り→ほどき」で見せたい時は curve の `bevel_factor_end` をアニメする**（006 ITOで確立）。カーブに `bevel_depth` を付けて発光チューブにし、`cu.bevel_factor_end` を cos で 1→0.05→1 にキーフレーム（`cu.keyframe_insert("bevel_factor_end", frame=f)`）すれば、掃引ジオメトリが端から生えては引っ込む＝糸が巻き取られる/ほどける。**headlessでも毎フレーム更新される**。0まで下げると完全消滅するので下限は0.05程度残す。球面スパイラルは `a=π·t`（極角）/ `azi=2π·N·t`（方位）で生成。glTFはbevel_factorアニメを持っていけない（静止ジオメトリのみ）点だけ注意。新造形は**アニメが効くか中間フレームを1枚テストレンダー**して確認してから本番へ（本番アニメは10分かかるので空振り防止）。
- `Material.use_nodes` / `World.use_nodes` はDeprecationWarning（6.0で廃止予定）。今は動くが将来の移行候補
