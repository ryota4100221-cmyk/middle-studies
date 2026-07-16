---
name: blender-middle-study
description: >
  Blenderをヘッドレス（コードのみ）で動かして「MIDDLE STUDIES」連作3D作品を1本制作・公開するスキル。
  毎日2:00 JSTのlaunchdルーティンから「daily」引数で起動されるほか、
  「MIDDLE STUDY作って」「今日の分作って」「Blenderで作品」「003作って」などの依頼でも発動する。
  題材選定→シーン生成→テストレンダー自己レビュー→本番レンダー→GitHub Pages公開→Notion/Slack記録まで一気通貫。
  Blenderで何かを作る依頼全般でも、まずこのスキルのパイプラインとPITFALLS.mdを参照する。
---

# MIDDLE STUDIES 制作スキル

このスキルは **モデルが変わっても001/002と同じ品質を再現するための正典**。手順・数値・落とし穴をすべてここに固定してある。判断に迷ったら「001 THE FILLING / 002 OBI と並べて違和感がないか」で決める。

## シリーズの不変条件（変更禁止）

| 項目 | 値 |
|---|---|
| 色 | 白 / 黒 `#0a0a0a` / ライム `#A5E02E` の3色のみ。**hexはsRGB→linear変換必須** |
| テーマ | 「真ん中に光がある」。外側は黒、中心・隙間・断面にライム |
| 舞台 | 白い床(0.86/rough0.42) + 明るいグレー環境光(0.92×0.55) + 浮遊するオブジェクト |
| ライト | key(-4,-3,5)/size5/1400W/暖白・rim(3.5,4,3.2)/size3/420W/冷白・fill(0,-6,2)/size6/220W |
| カメラ | 85mm・(0.55,-8.3,1.95)付近から・f/6.0 DOF・ポートレート4:5 |
| キャプション | Helvetica・カメラ正対で3行:「Designing the Middle of Your Story.」(0.1) /「monaka design.」(0.06) /「MIDDLE STUDY NNN — 題」(0.045) |
| ビュー変換 | **Khronos PBR Neutral**（AgXはライムが黄土色にくすむ） |
| Bloom | 新コンポジターのGlare(BLOOM)・Threshold1.2・Strength0.35・Size0.55 |
| ループ | **数学的に閉じること**（cos位相 or 360°回転 or 整数周期）。イージングキーフレーム2点は使わず毎フレームキーを打つ |
| 納品3点 | hero.png(1600×2000/96smp) + loop.mp4(720×900/24fps/16smp/5〜6秒) + model.glb(アニメ込み) |

## 実行手順（daily）

1. **準備**: `~/projects/middle-studies` で `git pull`。`BACKLOG.md` から未消化の先頭題材を選ぶ（全消化なら発想ルールに従い新題材を考案しBACKLOGへ追記してから作る）
2. **雛形コピー**: `~/projects/blender-lab/monaka_filling.py`（複数体パーツ＋変形アニメの例）または `monaka_ribbon.py`（bmesh数式生成＋回転ループの例）を土台に、新しい `monaka_<slug>.py` を書く。マテリアル・床・キャプション・ライト・カメラ・レンダー設定・Bloom・出力モード(test/still/anim/glb/blend)のセクションは**そのまま流用**し、造形とアニメーションだけ差し替える
3. **テストレンダー**: `Blender --background --factory-startup --python <script> -- test`（480×600/24smp、約1〜3分）
4. **自己レビュー（必須・最重要）**: test.png を **Readツールで必ず目視**し、下のチェックリストで判定。不合格ならパラメータを直して再テスト。**2〜4周は回るのが正常**（001は4周、002は2周した）
5. **本番**: `-- still glb blend` → `-- anim` を順に実行（M1でスチル約1.5分、アニメ約8〜10分）。**レンダーは必ず同期（フォアグラウンド）で実行し、完了を確認してから次工程へ進む**。バックグラウンド実行にして「完了待ち」でターンを終えてはいけない——ヘッドレス（`claude -p`）ではそこでセッションごと終了し、レンダー子プロセスも巻き添えで死に、公開工程まで到達しない（2026-07-11の003で発生。loop.mp4欠落＋デプロイ未実行のまま exit 0 になった）
6. **公開**: `works/NNN_slug/` に hero.png / loop.mp4 / model.glb / script.py を配置、`works.json` と `LOG.md` と `BACKLOG.md` のチェックを更新、commit & push。続けて **Netlify本番デプロイ**（この定期デプロイは承認済み・例外運用）: `cd ~/projects/middle-studies && netlify deploy --prod --dir .`
7. **記録**: Notion「デザインインプット（自動収集）」DBに1ページ作成
   - data_source: `collection://e7229880-2f1c-456f-873e-f8fe3d6cb36d`
   - 種別: `MIDDLE STUDY`／日付: **必ずJST**（`TZ=Asia/Tokyo date +%F`）
   - 参照URL: `https://middle-studies-monaka.netlify.app/`（**github.com URLは禁止・素のURLを単独で**。GitHub Pages https://ryota4100221-cmyk.github.io/middle-studies/ は副系）
   - 本文: 題・コンセプト・技法メモ（script.pyの冒頭コメントを流用）
8. **通知**: Slack Bot「mona」のIncoming Webhook経由で **#mona-日報** チャンネルへ1通。**成功でも失敗でも必ず送る**。失敗時は⚠️＋止まった工程・原因・できた所まで。URLは装飾せず素のまま単独行
   - 手順: 本文を `{"text": "<本文>"}` 形式のJSONファイル（改行は `\n`、書式はSlack mrkdwn）に書き、`curl -s -X POST -H 'Content-type: application/json' --data @/tmp/slack_payload.json "$SLACK_WEBHOOK"` を実行、レスポンス `ok` を確認
   - 🔴 **Webhook URLをこのファイルに書かない。** `scripts/daily.sh` が環境変数 `SLACK_WEBHOOK` で渡す。**このskill/ は public リポジトリにハードリンクでミラーされる**ため、直書きすると GitHub の Push Protection が push を拒否し、**毎晩のルーティンが公開まで到達できなくなる**（2026-07-15に直書きして実際に停止。7/16に解消）
   - Webhookが2回失敗した時のみ従来のSlack DM `D0AR1NB6N73` にフォールバック

## 品質チェックリスト（テストレンダー目視時）

- [ ] 黒が黒く見えるか（ライム被りで抹茶色になっていないか → 発光を下げ白ライトを上げる。001の教訓）
- [ ] ライムが `#A5E02E` らしい鮮やかさか（白飛びして白黄色になっていないか → Emission Strength 2.5〜3.5目安）
- [ ] 余白があるか（オブジェクトは画面の55〜65%。フレームいっぱいはNG。001/002とも初回は寄りすぎた）
- [ ] キャプション3行がオブジェクトと重ならず読めるか
- [ ] シルエットが一目で読めるか（「開いて光が見える」等のコンセプトが1秒で伝わるか。歪んだ塊に見えたら造形からやり直し）
- [ ] 発光がLEDテープのように飛んでいないか（Bloom Strengthは0.35固定、発光側を調整）

## 技術の正典

- Blender: `/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python <script> -- <modes>`
- **Blender 5.x APIの落とし穴は `PITFALLS.md`（このスキルと同じフォルダ）を必ず先に読む**。ハマったら新しい発見をそこに追記すること
- 完成スクリプト実例: `~/projects/blender-lab/monaka_filling.py` / `monaka_ribbon.py`（コメント込みで読めば構造がわかる）
- リポ: `~/projects/middle-studies`（GitHub: ryota4100221-cmyk/middle-studies・public・Pages有効）

## 人間（Ryota）との分担

- スキルが全自動でやってよい: 制作・公開・Notion/Slack記録（インフラは構築済み・[[project_intake_flow]]の自動実行原則）
- Ryotaがやる: X投稿などの対外発信、シリーズ方針の変更、不変条件の変更
