---
name: middle-studies-reel
description: >
  MIDDLE STUDIES REEL（毎晩1本・15秒のモーショングラフィックス）を制作・公開する手順。
  launchd（com.monaka.reel・毎晩23:00＋23:50キャッチアップ）が scripts/reel.sh から起動する。
  「今日のリール」「REEL作って」でも使う。
---

# MIDDLE STUDIES REEL 制作手順

2026-09-29 開始（Ryota指示）。公開先 https://middle.lab.monakadesign.com/reel/

## ブリーフ（毎回これだけ。書き換えない・足さない）

> 君がどれだけすごいモーションデザイナーかを見せる、ダイナミックな15秒のモーショングラフィックス動画を作って。履歴書に添えるショーリールのつもりで。全力でやって。

**このブリーフが唯一の創作上の指示。** 下に書いてあるのは、技術の約束と公開の手順と、
「毎日同じ絵に落ちない」ための歯止めだけ。見た目・題材・構成・色・書体は毎回自分で決める。

## 🔴 無人で走る

これは夜間の自動実行で、人は見ていない。質問しない。止めるときは工程7の通知を送ってから止める。
**レンダー（1分前後）は同期で待つ。バックグラウンドに回してターンを終えない**（終えるとセッションごと死ぬ）。

## 置き場

```
~/projects/middle-studies/reel/
├── index.html            ページ（触らない）
├── works.json            索引（末尾に1件足す）
├── works/NNN_slug/
│   ├── source.html       作品本体（これを書く）
│   ├── reel.mp4          書き出し（gitに入れない＝.gitignore）
│   ├── poster.jpg        render.mjs が作る
│   └── contact.jpg       render.mjs が作る（1秒ごと15枚）
└── scripts/render.mjs / check.py
~/projects/middle-studies-reel/NNN_slug.mp4   配信（別リポ・GitHub Pages）
```

## 工程0：今日の分は済んでいるか

`TZ=Asia/Tokyo date +%F` を今日とする。works.json の末尾の date が今日なら、何もせず `REEL_OK` で終わる。
今日の日付の作品フォルダが works/ にあるのに works.json に載っていなければ、前のセッションの途中＝**そのフォルダから続ける**（番号を新しく取らない）。

## 工程1：前の7本を見る（同じところに着地しないため）

- works.json の直近7件の `title` `concept` `techniques` `look` を読む。
- 直近3本の `contact.jpg` を Read で見る。
- **前の作品の source.html を開かない・コピーしない。** 昨日のコードを土台にすると、変わらない部分が既定で生き残る（3D Daily で18日間同じ絵が出た事故の原因）。
- 読んだうえで、今日は**何を主役にし、何を前作と変えるか**を先に3行で書き出す（主役の技法・構成の型・色と書体）。

## 工程2：作る（source.html）

技術の約束（ここだけは守る。見た目の縛りではない）：

- 1ファイルの HTML。`<canvas>` / SVG / DOM / WebGL どれでもよい。外部ライブラリは cdnjs・jsdelivr・unpkg から読んでよい（GSAP・three.js 等）。フォントは macOS のシステム書体か Google Fonts。
- **`window.__duration = 15` と `window.__seek(t)` を公開する。** `__seek(t)` は時刻 t の絵を描き切る純関数（何度呼んでも同じ絵・呼ぶ順番に依存しない）。Promise を返してもよい（render.mjs が await する）。
- 🔴 **`Math.random()` を使わない**（撮るたびに絵が変わる）。乱数はシード付き PRNG（mulberry32 等）で。`requestAnimationFrame` や経過時間で状態を進めない（GSAP なら timeline を paused で作って `tl.seek(t)`／three.js なら t から姿勢を計算して `renderer.render`）。
- URL に `?render` が付いていないときは自走再生する（ブラウザで開いて見られるように）。
- 1920×1080・60fps・ちょうど15秒・無音（BGM素材は無い）。**15秒でループの戻りが自然になるよう終える**のが望ましい。
- `window.__poster = 秒` で、ポスター（一覧の静止画）に使う1枚を指定する。
- 右下などに作品番号を入れるなら `REEL — NNN`。署名は `Claude`（作者はClaude。Ryota の作品だと書かない）。

## 工程3：書き出し

```bash
cd ~/projects/middle-studies/reel
node scripts/render.mjs works/NNN_slug     # 1〜2分。同期で待つ
```

ページのエラーが1件でもあると止まる（exit 3）。直してから撮り直す。

## 工程4：自己レビュー（最低3周・上限なし・開始から2時間で打ち切り）

毎周、`contact.jpg` と、**場面のつなぎ目と一番の見せ場を中心に6枚以上**を `ffmpeg -ss <秒> -frames:v 1` で切り出して Read で見る（縮小図は細部を見誤るので、主張する箇所は等倍で切り出す）。

見ること：
1. **最初の1秒で目を掴むか**（ショーリールは最初の1秒で閉じられる）
2. 止まって見える区間・何も起きていない区間がないか
3. 文字の重なり・はみ出し・画面端での切れ・読めない小ささ（1920幅で本文18px未満は読めない）
4. つなぎが「切り替え」ではなく「つながり」になっているか
5. **前の7本と並べて、今日のものが違って見えるか**

直すことを書き出し → 直す → 撮り直す、を1周とする。**「直すことが言えなくなった」か2時間で止める。**
最後の周で「許容した差：」を1行書いてよい（直さないと決めたこと）。

## 工程5：works.json に1件足す

```json
{
  "id": "NNN", "slug": "kebab-case", "title": "英語の題", "date": "YYYY-MM-DD",
  "concept": "何をどう見せたか（日本語・2〜4文。見どころの秒数を1つ入れてよい）",
  "video": "https://ryota4100221-cmyk.github.io/middle-studies-reel/NNN_slug.mp4",
  "techniques": ["主役の技法を kebab-case で5〜10個"],
  "look": { "palette": ["#hex", "..."], "type": ["書体名"], "structure": "構成の型", "renderer": "canvas2d|svg|dom|webgl|three|gsap" },
  "review_rounds": 3,
  "review": "周ごとに見つけたこと→直したこと。最後に 許容した差：…"
}
```

`sameish`：変化ゲートが近いと言ったのに、それでも出す理由があるときだけ書く（例：同じ技法でも構成が別物）。

## 工程6：点検→公開

```bash
/usr/bin/python3 scripts/check.py NNN          # 🔴0 でなければ公開しない。直して撮り直す
cp works/NNN_slug/reel.mp4 ~/projects/middle-studies-reel/NNN_slug.mp4
cd ~/projects/middle-studies-reel && git add -A && git commit -m "REEL NNN slug" && git push
cd ~/projects/middle-studies && git add reel && git commit -m "REEL NNN slug：一言" && git push
sleep 90   # Pages の反映待ち
/usr/bin/python3 ~/projects/middle-studies/reel/scripts/check.py NNN live   # 4本とも200
```

🔴 **動画を先に push、ページ（works.json）を後に。** 逆だと、動画の無いカードが数分出る。
live が 200 にならなければ 2分待ってもう一度。3回だめなら工程7で止まる。

## 工程7：止まるとき

直せない🔴で止めるときは、`$SLACK_WEBHOOK`（環境変数・#mona-作品）へ1通送ってから終わる：
`🔴 MIDDLE STUDIES REEL（日付）を公開できませんでした — 理由1行 / 作品フォルダ`。
Webhook の URL をファイルに書かない（push が止まる）。

## 完走の証明

最後に、`CHECK NNN: 🔴0 …` の行（local と live の2行）を貼り、**最後の行に `REEL_OK` とだけ書く**。
説明文の中に `REEL_OK` と書かない（シェルは最後の行だけを見る）。
**push と live の確認を実際に済ませていないのに `REEL_OK` と書いてはいけない。**

成功時の Slack 通知はしない（毎朝5:55の作品ダイジェスト #72 が拾う）。
