---
name: blender-middle-study
description: >
  Blenderをヘッドレス（コードのみ）で動かして「MIDDLE STUDIES II」の3D作品を1本制作・公開するスキル。
  月・水・金の2:00 JSTにlaunchdルーティンから「daily」引数で起動されるほか、
  「MIDDLE STUDY作って」「今日の分作って」「Blenderで作品」「STUDIES IIの次」などの依頼でも発動する。
  基準の作品を撮る→ルックを決める→シーン生成→基準と並べて6周以上の自己レビュー→本番レンダー→
  機械点検→GitHub Pages公開→Notion記録まで一気通貫。
  Blenderで何かを作る依頼全般でも、まずこのスキルとPITFALLS.mdを参照する。
---

# MIDDLE STUDIES II 制作スキル

> **2026-09-23 に方針を変えた（Ryota決定）。** 第1期（MIDDLE STUDIES 001〜089・毎日）は完結。
> 第1期の正典は `SKILL_I.md` に凍結してある（読むのはBlender技法を引くときだけ・**方針は引き継がない**）。
>
> | | 第1期（〜089） | 第2期 II（090相当〜・番号は001から） |
> |---|---|---|
> | 題材 | 和の道具（BACKLOG.md） | **OBJECT（案件で使える物）と FORM（抽象・グラフィカル）を交互** |
> | 見た目 | 白・黒・ライムの3色／白床／85mm／4灯／キャプション固定 | **全部外した。毎回、基準の作品から決める** |
> | 頻度 | 毎日 | **月・水・金の週3本**（空いた分を1本の周回に回す） |
> | 品質の基準 | 001/002 と並べて違和感がないか | **実在の作品・プロダクト写真と並べて見劣りしないか** |
> | 置き場 | `works/` `works.json` `/` | **`ii/works/` `ii/works.json` `/ii/`** |

## なぜこう変えたか（書き換える前に読む）

- **第1期の最後の10作は、題材が毎日違っても絵は同じだった。** 固定の舞台・固定の光・固定の3色の上では、
  変えられるのが「黒い塊の形」だけになる。画像距離（`ii/scripts/check.py` の式）で測ると
  089 と 087 が 0.062、089 と 050 が 0.056＝3d-daily で「同じ絵」と判定する帯（<0.06）に入っていた。
- **品質の天井は機能ではなく周回数にある**（2026-08-09の限界テスト）。毎日1本では2〜4周しか回せない。
- **題材をAIの頭から出すと、前回の隣に着地する**（2026-08-17 3D Daily事故：18日間同じ絵）。
  だから第2期は**毎回、外にある実在の作品を1件「基準」として撮る**。基準が品質と見た目の両方を外から運んでくる。

## 不変条件（第2期で残したものはこれだけ）

| 項目 | 値 |
|---|---|
| 交互 | **前作が OBJECT なら今回は FORM、FORM なら OBJECT**（`check.py look` が検査） |
| 基準 | **毎回1件、実在の作品を撮って並べる**。基準なしで作らない |
| 納品3点 | `hero.png`（**長辺2560**・256smp・デノイズ）＋ `loop.mp4`（**長辺1080**・24fps・5〜8秒）＋ `model.glb`（動き込み・8MB以下） |
| ループ | **数学的に閉じる**（位相 t∈[0,1) で書き毎フレームキー。イージングのキー2点で済ませない） |
| 自己レビュー | **上限なし・最低6周（うち testhero 2周以上・最後の周は testhero）**。毎周、基準と並べた1枚を Read し、`REVIEW.md` に記録する。止めてよいのは「劣るところを具体的に言えなくなったとき」か、開始から3時間を過ぎたときだけ |
| 公開前点検 | `python3 ii/scripts/check.py all <作品フォルダ>` が **🔴 0件** |
| 画面内の文字 | **入れない**（キャプションはサイトが出す。3D文字は構図を縛るので第1期でやめた） |

色・地・床・光・レンズ・判型・ビュー変換・素材は**すべて毎回決める**。決めた値は `works.json` の `look` に書く。

## 題材と基準の取り方

### OBJECT（案件で使える物）
クライアント案件のFV・商品紹介・サービス図解にそのまま置ける物。
プロダクト（家電・文具・化粧品・飲料・食器・家具）、パッケージ、小さな建築・空間、UIの立体化、アイコンの立体化。
**基準の探し先**：メーカー公式の製品ページ（写真の撮り方が一番上手い）／Behance・Dribbble の個別作品ページ
（🔴 検索ページは headless で真っ白に写る。**個別作品の URL か og:image を渡す**）／Awwwards で3Dを使った受賞サイト。
**狙い**：「実写の商品写真と並べても3DCGだと気づかれない」質感と、「案件で使える」構図（余白・置き場）。

### FORM（抽象・グラフィカル）
物ではなく、形・素材・光そのものが主役。ガラス・液体・布・粒子・反復・構造体・タイポ的な形・光の現象。
**基準の探し先**：Behance / ArtStation / Dribbble の抽象3D作品、Awwwards・FWA の3Dサイトの FV、
モーショングラフィックスのスタジオ（作品ページ）。
**狙い**：一目で「強い」画。サイトのFV背景・区切りのビジュアルとして成立するか。

### どちらでも守ること
- 🔴 **基準の URL は `ii/SOURCES.md` に1行足す。同じ URL・直近3作と同じドメインは使わない**（行は消さない）。
- 基準から取るのは **①光の組み方 ②素材の質 ③構図と余白 ④色の組み立て**。
  **形・ロゴ・固有のデザインは写さない**（題材は同じ種類でいいが、造形は自分で起こす）。
- 🔴 **撮った画像は `ii/refs/`（gitignore 済み）に置く。他人の作品を public リポジトリに上げない。**
- スワイプファイルDB・朝刊・トレンド日報に出てきた3Dの作品を基準にしてもよい（外にある実物なら出所は問わない）。

## 実行手順（daily）

0. **曜日の確認**：`TZ=Asia/Tokyo date +%u` が 1・3・5 以外なら何もせず `MIDDLE_OK` だけ出して終わる
   （launchd は月水金にしか起動しないが、手動・キャッチアップ枠で呼ばれたとき用）。
   今日すでに `ii/works.json` の最終行が今日の日付なら、作らずに `MIDDLE_OK` で終わる。
   **引数に `force` があるときは、この工程0の2つの判定を両方とも飛ばして作る**（`II_FORCE=1 zsh scripts/daily.sh` で試作するとき。番号は works.json の続き）。
1. **準備と基準**：`~/projects/middle-studies` で `git pull`。`ii/works.json` の最終行から今回の track（OBJECT/FORM）を決める。
   上の探し先から基準を1件選び、撮る：
   ```bash
   node ii/scripts/ref.mjs "<URL>" ii/refs/NNN.png            # ページなら 1440×900。og:image も表示される
   node ii/scripts/ref.mjs "<og:image の URL>" ii/refs/NNN.png  # 作品画像を直接落とすほうが良いことが多い
   ```
   撮れた画像を **Read で必ず見る**（真っ白・Cookie バナー・ログイン壁なら別の URL で撮り直す）。
   見たうえで、基準から読み取った **光・素材・構図・色** を4行で `REVIEW.md` の冒頭に書く（`基準: <URL>` の行を必ず入れる）。
   🔴 **同じく冒頭に `開始: HH:MM`（JST・`TZ=Asia/Tokyo date +%H:%M` で取った値）を書く。** 工程4の時間の枠はここから数える。
2. **ルックと題材を決める**：`ii/template.py` を `ii/works/NNN_slug/script.py` にコピーし、`LOOK` と舞台・光・カメラを書き換える。
   同じ値を `works.json` に入れる行の下書き（`look`）を作り、**造形に入る前に照合する**：
   ```bash
   python3 ii/scripts/check.py look /tmp/ii_look.json --id NNN
   ```
   `look` の軸＝`track` `palette_family`（例: warm-neutral / cool-mono / saturated-duo / dark-accent）
   `background`（sweep / void / floor-wall / environment / tabletop …）`lighting`（softbox / hard-sun / rim-only / hdri / practical …）
   `lens`（wide / normal / tele）`aspect`（4:5 / 1:1 / 16:9 …）`material`（主材：glass / metal / plastic / ceramic / fabric / liquid …）。
   **直近3作のどれかと5軸以上一致したら🔴**＝色だけ変えて同じ絵、を造形前に止める。
3. **造形**：雛形の被写体（青い箱とリング）は動作確認用。**これを題材にしない**。
   🔴 **安っぽく見える原因は造形の詰め方3つ**（2026-09-12 FANTAS で実測・`bevel_obj()` に罠を書いてある）：
   ①稜線を立てっぱなしにしない（全パーツに面取り） ②部品を刺したままにしない（同色は面取り→Boolean合体→仕上げ面取り）
   ③roughness を上げすぎない（モノは 0.16〜0.55）。
   形が読めないときは PITFALLS.md と `SKILL_I.md` の技法欄を引く（第1期89作ぶんの造形の罠がある）。
4. **テストレンダーと自己レビュー（上限なし・最低6周・最重要）**：
   ```bash
   Blender --background --factory-startup --python script.py -- test          # 長辺720・48smp
   python3 ii/scripts/sidebyside.py ii/refs/NNN.png _test.png _sbs.png        # 基準と並べる
   ```
   **`_sbs.png` を Read して判定する。自作だけを見ない。** 毎周 `REVIEW.md` に書く：
   ```
   ## round 1
   基準より劣るところ：（具体的に。「光が硬い」ではなく「キーの面積が小さく、ハイライトが点になっている」）
   直すこと：
   ```
   🔴 **周回に上限は無い。止めてよい条件は次の2つだけ**（2026-09-23 改定・Ryota指示）：
   - **(a) 基準と並べて、劣るところを具体的に1つも言えなくなった**（「まだ少し薄い」のような程度の話が残るなら、それを直す周を回す）
     🔴 **「劣る」に数えるのは、形・光・素材・構図・動きの差と、並べて見て別の色に読める色の差だけ。**
     同じ色に読める範囲の調子の差（画面平均の hex でチャンネルあたり ±15 以内が目安）は**劣りではない**。
     それは「許容した差:」の1行で REVIEW.md に書いて、止める。**基準の色を写し取ることは目的ではない**
     （基準から取るのは色の「組み立て」＝何色を何割・どこに置くか）。
     > **なぜ**：II 004 は36周目で「形・光・素材・構図で劣るところは言えなくなった」と判定したのに、
     > 「陰の色味が±10ずれている」も言葉にできる差だとして**さらに11周・約20分を hex の一致合わせに使った**。
     > 絵の強さはほぼ変わらなかった。「言葉にできる差が残れば回す」を字義どおりに取ると、
     > 数字で測れる差は永遠にゼロにならないので、3時間の枠まで複製に寄っていく。
   - **(b) `開始:` から3時間を過ぎた**（残りを本番レンダーと公開に回す。このとき REVIEW.md に「時間切れで止めた・残っている差」を書く）
   - 🔴 **経過時間は自分で数えない。`python3 ii/scripts/check.py elapsed ii/works/NNN_slug` で測る。**
     II 003 は実際54分のところを「開始から約2時間」と書いた。逆向きにずれると、まだ枠があるのに「時間切れ」で止める。
     点検は「時間切れ」と書いてあるのに3時間に届いていなければ🔴を出す。
   > **なぜ上限を外したか**：II 001 は「上限6周」のとおり6周で止め、**27分で完走した**（1周20秒〜1分）。
   > 4時間の枠を使い切らずに、接地の影の薄さと天板の質感という「言葉にできている差」を残したまま出した。
   > 上限は歯止めではなく**天井**として働いていた。
   - **最低6周。4周目以降は `testhero`（長辺1600・128smp）で見る。最後の周は必ず testhero**（点検が🔴を出す）。
   - 3周回しても同じ差が縮まらないときは、ルックではなく**造形か題材を疑う**（パラメータで型は救えない＝#33）。
   - 動きは `phases` の4枚で見る。
   - 🔴 **最終判定の周では、「見劣りしない」と書く箇所ごとに、その部分を拡大して並べて見る**（最低2箇所）：
     ```bash
     python3 ii/scripts/sidebyside.py ii/refs/NNN.png _testhero.png _crop1.png --crop 0.1,0.3,0.5,0.9 0.05,0.2,0.45,0.9
     ```
     見た結果を `拡大: <どこ> — <基準と比べてどうだったか>` の1行で REVIEW.md に書く（点検が2行以上を要求する）。
     > **なぜ**：II 001 は全体図だけで最終判定し、**接地の影が基準よりはっきり弱い**まま出した
     > （拡大すると、基準のポットの底には濃い影が溜まっているのに、ボトルの足元にはほぼ無い）。
     > しかも同じ全体図を見た人間側（セッションのレビュー）は逆に「ボケが弱い」と誤診した——拡大するとボケは効いていた。
     > **縮小した全体図では、ボケ・質感・接地の影・面取りのハイライトの差は、どちら向きにも見誤る。**
     拡大して差が見つかったら、それは (a) を満たしていない＝もう1周回す。
   - 🔴 **最終判定の前に、構図を機械で測る**（拡大は細部を見る道具で、画面全体の組み方は見ない）：
     ```bash
     /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
       --python ii/scripts/mask.py -- ii/works/NNN_slug/script.py ii/works/NNN_slug/mask.png   # 被写体だけを白く抜く（十数秒）
     python3 ii/scripts/check.py compose ii/works/NNN_slug/_testhero.png ii/works/NNN_slug/mask.png
     ```
     見るのは **四辺の余白**（3%未満は窮屈＝切るなら切る、空けるなら空ける）と、**輪郭の辺ごとの明暗差**
     （半分以上の区間で地との差が10未満なら、被写体がどこまでか読めない）。
     > **なぜ**：試作3本の構図の弱点——002 球が右端で窮屈（余白2.4%）／003 本体の下半分が闇に溶ける（下辺100%）——は、
     > 23〜24周の自己レビューでも「拡大:」21件でも拾えなかった。この点検は2つとも拾う。
     🔴なら構図を直す周を回す。**意図して沈めた・透明素材で透けるのが正しい**ときだけ、works.json の
     `compose_note` に辺ごとの理由を書けば通る（`{"上": "ガラスの天端は背景が透けるのが正しい"}`）。
     ⚠️ 被写体は script.py の `parts` から取る。**被写体のオブジェクトは全部 `parts` に入れておく**（雛形どおり）。
5. **本番**：🔴 **daily（launchd・`claude -p`）では、AI は動画（anim）を描かない。** 描くのは `daily.sh`。
   > **なぜ**：「anim は同期で待て」と何度書いても、AI は「完了通知を待ちます」と書いてターンを終え、
   > ヘッドレスではそこでセッションが終わった（第1期 003・062／II 002・005＝試作5本中2本）。005 では anim も道連れで死に、
   > 作り直しに30分かかった。**待つ仕事をAIに持たせないのが唯一の直し方**なので、シェルに移した（2026-09-23）。
   手順（daily）：
   ```bash
   cd ii/works/NNN_slug
   Blender --background --factory-startup --python script.py -- still glb                 # hero.png・model.glb
   Blender --background --factory-startup --python ../../scripts/mask.py -- script.py mask.png   # 本番の hero に対して描き直す
   ```
   `works.json` に行を足し（工程6の形式）、**anim のサンプル数を決めて依頼書を置く**：
   test で1フレームの秒数を測り、`秒/フレーム × フレーム数` が90分を超えないサンプル数にする（既定24・デノイズがあるので16でも粒は出にくい）。
   ```bash
   echo "samples=24" > ii/works/NNN_slug/ANIM_REQUEST
   ```
   ここで**最後の行に `MIDDLE_ANIM_READY` とだけ出して終わる**（点検・公開・Notion はまだやらない）。
   `daily.sh` が anim を描き、フレーム数を確かめてから、**工程6〜7だけを担当する次のセッション**を起動する。
   - 対話セッション（人が見ている）で作るときだけは、自分で anim を描いてよい。そのときは同期で待つ：
     `nohup Blender … -- anim > /tmp/iiNNN_anim.log 2>&1 < /dev/null & disown` → `caffeinate -w $(pgrep -f "script.py -- anim")`
     （600秒で切れたら同じ行をもう一度）。完了は `ffprobe -v error -show_entries stream=nb_frames -of default=nw=1 loop.mp4` で判定。
6. **点検と公開**：`works.json` に行を足してから
   ```bash
   python3 ii/scripts/check.py all ii/works/NNN_slug     # 🔴 0件になるまで公開しない
   ```
   （daily では、ここからは `daily.sh` が起動した2つ目のセッションが担当する。anim は描き終わっている）
   🔴が出たら直してから出す。画像距離が 0.06〜0.14 のときは意図があれば `sameish` に理由を書けば通る。
   作品フォルダに置くのは `hero.png` `loop.mp4` `model.glb` `script.py` `REVIEW.md` `mask.png`（本番の hero に対して描き直す）だけ（`_test*.png` `_sbs.png` `_crop*.png` は消す）。
   `ii/SOURCES.md` に行を足し、**commit & push だけで公開完了**（GitHub Pages が `/ii/` を配信）。`netlify deploy` はしない。
7. **記録**：Notion「デザインインプット（自動収集）」DBに1ページ作成
   - data_source: `collection://e7229880-2f1c-456f-873e-f8fe3d6cb36d`
   - 種別: `MIDDLE STUDY`／日付: **必ずJST**（`TZ=Asia/Tokyo date +%F`）
   - タイトル: `MIDDLE STUDIES II NNN — 題`
   - 参照URL: `https://middle.lab.monakadesign.com/ii/`（素のURLを単独で。github.com のリポURLは禁止）
   - 本文: 題・track・コンセプト・基準のURL・基準から取ったもの・REVIEW.md の各周の要点
8. **通知**：**完走したときは Slack に送らない**（毎朝5:55の作品ダイジェストが `ii/works.json` を読んで束ねる）。
   🔴 **途中で諦めたときだけ** ⚠️＋止まった工程・原因・できた所までを1通送る。
   本文を `{"text": "..."}` のJSONに書き、`curl -s -X POST -H 'Content-type: application/json' --data @/tmp/slack_payload.json "$SLACK_WEBHOOK"`。
   🔴 **Webhook URLをこのファイルに書かない**（skill/ は public。`scripts/daily.sh` が環境変数で渡す）。

## works.json の1行（`ii/works.json`）

```json
{
  "id": "001", "slug": "vessel", "title": "VESSEL", "title_ja": "器",
  "date": "2026-09-25", "track": "OBJECT",
  "concept": "1〜2文。何を作り、どこが見どころか",
  "source": {"url": "https://…", "took": "光：… / 素材：… / 構図：… / 色：…"},
  "look": {"track": "OBJECT", "palette_family": "warm-neutral", "background": "sweep",
           "lighting": "softbox", "lens": "tele", "aspect": "4:5", "material": "ceramic"},
  "review_rounds": 4, "loop_seconds": 6,
  "compose_note": {"右": "（任意）構図の点検で🔴の辺を意図として残す理由"},
  "use": "案件でどう使えるか1行（OBJECTのみ・FORMは任意）"
}
```

## 品質チェックリスト（自己レビューの各周で見る）

機械で見るもの（`check.py all`）：白飛び≤2%・黒つぶれ≤25%・コントラスト≥0.10・hero長辺≥2400／
直近6作との画像距離≥0.06（0.06〜0.14は理由が要る）／直近3作とルック5軸以上一致しない・track交互／
動き量≥0.62・ループの閉じ≤2.2・静止率≤20%・尺5〜8秒／glb 8MB以下・動きあり／
自己レビュー6周以上・testhero 2周以上・最後の周が testhero・「拡大:」2行以上・基準の記載あり／
「時間切れ」の申告が実時間と合う／四辺の余白≥3%・輪郭の各辺で溶けた区間≤50%（理由は compose_note）。

目で見るもの（`_sbs.png` で基準と並べて）：
- [ ] **並べて見劣りしないか**。劣るなら、どこが劣るかを1つに絞って言葉にできるか（言えないうちは直せない）
- [ ] 稜線にハイライトが乗っているか（面取りが無いと粘土に見える）
- [ ] 素材が素材に見えるか（プラスチックとセラミックと塗装金属の区別がつくか＝roughness と coat と IOR）
- [ ] 接地しているか／浮いているなら浮いている理由が絵にあるか（影が無い浮遊は合成に見える）
- [ ] 光に向きがあるか（全方向から均等に照らすと模型写真になる）
- [ ] シルエットが1秒で読めるか
- [ ] OBJECT なら：案件のFVに置いたとき、コピーを載せる余白があるか
- [ ] FORM なら：サムネイル（幅300px）に縮めても強いか
- [ ] 動き：ループの継ぎ目が見えないか（`phases` の4枚と最初・最後のフレーム）

## 帯の引き直し

`check.py` の閾値は第1期と 3d-daily の実測を流用した仮置き。**II が10作たまったら**
`python3 ii/scripts/check.py hero` / `motion` を全作に掛けて分布を取り、`check.py` 冒頭の帯を実測で引き直す
（そのとき AUTOMATION_ROADMAP.md にも一行残す）。

## 技術の正典

- Blender: `/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python <script> -- <modes>`（5.1）
- **Blender 5.x API の落とし穴は `PITFALLS.md` を必ず先に読む**。ライム・白床・4灯に固有の項（#24 #45 #51 #56 #58 など）は
  第2期では前提が違うので読み飛ばしてよい。**API・レンダー・書き出し・待ち方の罠は全部そのまま効く。**
  新しく踏んだ罠は PITFALLS.md に追記する（見出しに `[II]` を付ける）。
- 雛形: `ii/template.py`（2026-09-23 に Blender 5.1.1 で test/glb の完走を確認済み）
- 道具: `ii/scripts/check.py`（点検）／`ref.mjs`（基準を撮る）／`sidebyside.py`（並べる）／`mask.py`（被写体マスク）
- リポ: `~/projects/middle-studies`（GitHub: ryota4100221-cmyk/middle-studies・public・Pages有効）

## 人間（Ryota）との分担

- スキルが全自動でやってよい: 制作・公開・Notion記録
- Ryotaがやる: X投稿などの対外発信、シリーズ方針の変更、不変条件の変更、**案件への転用の判断**

---

## 完走の証明

全工程（本番レンダー・点検🔴0件・GitHub Pages公開・Notion記録）を終えたら、**最後の行に `MIDDLE_OK` とだけ出力する**。
（daily の1つ目のセッションは工程5で `MIDDLE_ANIM_READY` を出して終わる。`MIDDLE_OK` を出すのは公開まで終えた2つ目のセッション）
（工程0で「今日は制作日ではない／今日の分は済んでいる」と判定して終えたときも `MIDDLE_OK`）

🔴 **push や Notion 記録を実際に済ませていないのに `MIDDLE_OK` と書いてはいけない。**
シェルの終了コードは「AIが完走したか」を何も保証しない。証拠が無い場合、`scripts/daily.sh` はログ横に
`INCOMPLETE-<日付>` という印を置き、毎朝のローカル日次点検がそれを拾って通知する。
