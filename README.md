# MIDDLE STUDIES

**monaka design.** の連作3Dスタディ。*"Designing the Middle of Your Story."* の「真ん中」を、毎日ひとつ違うかたちで研究する。

- 🖼 ギャラリー: https://middle-studies-monaka.netlify.app/ （副系: https://ryota4100221-cmyk.github.io/middle-studies/ ）
- 制作: Blender 5.1 ヘッドレス（GUIなし・全工程Pythonコード）
- 色は3つだけ: 白 / 黒 `#0a0a0a` / ライム `#A5E02E`

## 構成

```
works/NNN_slug/
├── hero.png    1600×2000 スチル
├── loop.mp4    完全ループ動画（数学的にシームレス）
├── model.glb   アニメーション込みWebアセット（R3F/Framerで再利用可）
└── script.py   シーン全体を再生成するBlender Pythonスクリプト
works.json      ギャラリー索引
BACKLOG.md      題材ストックと発想ルール
LOG.md          完了ログ
```

## 運用

毎日 2:00 JST、ローカルMacのlaunchdがClaude Code（スキル `blender-middle-study`）を起動して1作品を生成・push、Netlifyへ本番デプロイする。制作パイプラインの正典はスキル側にある。

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
