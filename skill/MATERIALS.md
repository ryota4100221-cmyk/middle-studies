# 黒の質感レシピ（MIDDLE STUDIES 正典・2026-08-13 制定）

> **50作すべてが同じ黒で組まれていた。** 縄（033）も紙（046）も布（047）も石（048）も、
> 数値は少しずつ違うのに **hero では全部おなじプラスチックに見えていた**。
> 色の不変条件（白／黒 `#0a0a0a`／ライム）は**表面を縛っていない**ので、
> **色を1色も増やさずに質感の語彙だけ増やせる。** 実レンダー検証済みの4種を以下に固定する。
>
> 検証スクリプト＝`~/projects/blender-lab/limits/E_black_materials.py`（球＝曲面／立方＝平面／トーラス＝稜線を
> シリーズと同じ照明・カメラ・トーンで同時に撮る）。**値を変えたら必ずこれで撮り直して measure.py に通す。**

---

## 🔴 まず、黒で効かないもの・効くもの（実測で確定）

| 手段 | 黒（`#0a0a0a`）での結果 |
|---|---|
| **Bump（ノイズ→ノーマル）** | 🔴 **まったく見えない。** 強度0.90・スケール14 まで振っても平滑のまま |
| デノイズを切って256サンプル | 🔴 見えたのは起伏でなく**レンダーノイズ** |
| 鏡面を上げた黒に同じ Bump | ⚠️ **見える**。ただし #47 の**映り込み事故**と隣り合わせ |
| **実ジオメトリを動かす（SUBSURF＋DISPLACE）** | ✅ **はっきり見える。これが答え** |

**理由**：黒はアルベドがほぼゼロで**拡散反射に載る情報が無い**。法線を曲げても返る光が無いので、
Bump は原理的に絵に出ない。黒の上で見えるのは**鏡面**か**シルエット（＝実際の面の向き）**だけ。
→ **黒の肌は「マテリアル」ではなく「ジオメトリ」で作る。**

---

## 4つのレシピ（Principled BSDF・Blender 5.1）

| レシピ | Roughness | Specular IOR Level | その他 | 実起伏（DISPLACE） | 実測 黒平均／p98 |
|---|---|---|---|---|---|
| `base`（現行の標準） | 0.36 | 0.15 | Coat 0.05 | なし | 17.9 ／ 61.1 |
| **`urushi` 漆** | 0.30 | 0.34 | Coat 0.05・Coat Rough 0.25 | なし（漆は肌が無いのが肌） | 25.3 ／ 66.1 |
| **`touki` 陶** | 0.58 | 0.26 | — | strength 0.006・noise_scale 0.10 | 28.5 ／ 66.0 |
| **`nuno` 布** | 0.80 | 0.20 | Sheen 0.55・Sheen Rough 0.25 | strength 0.004・noise_scale 0.05 | 24.8 ／ 59.1 |
| **`tetsu` 鉄** | 0.50 | 0.32 | Metallic 0.35 | strength 0.012・noise_scale 0.09 | 22.7 ／ 63.3 |

健全域は 黒平均 14〜52 ／ 黒p98 56〜69（#45）。**4種とも合格。しかも4種とも base より p98 が高い**
＝質感を与えるほど黒は立体になる。

### 選び方（題材の実物の素材で選ぶ。迷ったら base）
- **漆**：塗り物・碗・箱・盆・楽器の胴・鞘。「深く沈んだ艶」がモチーフの本体であるもの
- **陶**：焼き物・石・土・瓦・臼・硯。**触ると少しざらつく**もの
- **布**：暖簾・幕・紐・縄・巻物・紙。**垂れる／たわむ**もの（＋布は**ドレープ＝形**でも語る）
- **鉄**：鋳物・釘・鍵・秤・刃物の地。**硬くて重い**もの

---

## そのまま貼れるコード

```python
BLACK_RECIPES = {
    "base":   dict(rough=0.36, spec=0.15, coat=0.05),
    "urushi": dict(rough=0.30, spec=0.34, coat=0.05, coat_rough=0.25),
    "touki":  dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10),
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25, disp=0.004, dsize=0.05),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
}


def black_material(name, recipe, BLACK):
    """#0a0a0a の主材を作る。recipe は BLACK_RECIPES のキー。"""
    r = BLACK_RECIPES[recipe]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)
    if r.get("sheen"):
        p.inputs["Sheen Weight"].default_value = r["sheen"]
        p.inputs["Sheen Roughness"].default_value = r.get("sheen_rough", 0.3)
        p.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)
    return m, p


def add_relief(objs, recipe):
    """黒の肌は実ジオメトリで作る（Bump は黒では見えない）。**造形が済んだ最後に呼ぶ。**"""
    r = BLACK_RECIPES[recipe]
    if not r.get("disp"):
        return
    tex = bpy.data.textures.new("relief_" + recipe, 'CLOUDS')
    tex.noise_scale = r["dsize"]
    for o in objs:
        sub = o.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 3
        d = o.modifiers.new("disp", 'DISPLACE')
        d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5
```

## 使うときの掟

1. 🔴 **`add_relief` は発光体に掛けない。** 光る面を歪ませると #14 の勾配が壊れる。**黒の主材だけ**。
2. 🔴 **strength を上げるとシルエットが荒れる。** 検証で 0.020 は「粘土」に転んだ。表の値が上限の目安。
3. 🔴 **鏡面を上げる方向（urushi）に振ったら、必ず hero を目視して映り込みを確認する**（#47）。
   平面（板・箱の面）を持つ造形ほど出やすい。**数値には出ない。**
4. **1作に1素材。** 2種以上を混ぜると、質感でなく「部品の寄せ集め」に見える
   （部位で分けるのは、実物がそうである場合＝鉄の輪＋布の胴、のようなときだけ）。
5. **`disp` を入れると SUBSURF が乗るので頂点数が跳ねる。** アニメが重い時は `sub.levels` を先に落とす。
