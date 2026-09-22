#!/usr/bin/env python3
# MIDDLE STUDIES II — 基準と自作を同じ高さで並べる（2026-09-23）
#
#   python3 ii/scripts/sidebyside.py <基準.png> <test.png> <出力.png>
#
# 🔴 自己レビューは必ずこの1枚を Read して行う。自作だけを見ると、何周回しても
#    「前の周よりは良い」しか判定できない（第1期が89作かけて学んだこと）。
import sys
from PIL import Image, ImageDraw, ImageStat

ref, mine, out = sys.argv[1:4]
H = 1100
ims = []
for p in (ref, mine):
    im = Image.open(p).convert("RGB")
    # 🔴 空の撮影を弾く（2026-09-23 実測：Behance の検索ページは headless で真っ白に写った）。
    #    白紙と並べても「見劣りしない」と判定できてしまう＝基準が無いのと同じ。
    st = ImageStat.Stat(im.convert("L").resize((200, 200)))
    if st.stddev[0] < 4:
        sys.exit(f"🔴 {p} がほぼ一色（輝度std {st.stddev[0]:.1f}）＝撮れていない。og:image か作品画像のURLを直接渡して撮り直す")
    ims.append(im.resize((round(im.width * H / im.height), H)))
gap = 24
W = sum(i.width for i in ims) + gap * 3
canvas = Image.new("RGB", (W, H + gap * 2 + 28), (24, 24, 24))
x = gap
d = ImageDraw.Draw(canvas)
for lab, im in zip(("REFERENCE", "MINE"), ims):
    canvas.paste(im, (x, gap + 28))
    d.text((x, gap), lab, fill=(200, 200, 200))
    x += im.width + gap
canvas.save(out)
print(">> saved", out, canvas.size)
