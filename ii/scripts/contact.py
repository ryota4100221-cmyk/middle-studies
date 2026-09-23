#!/usr/bin/env python3
# MIDDLE STUDIES II — 動画のカットを1枚に並べる（2026-09-23）
#
#   python3 ii/scripts/contact.py <作品フォルダ> [出力.png]
#
# script.py の `-- shots` が書いた _shot_<カット>_<0=頭 1=中 2=終わり>.png を、
# 1カット1行で並べる。🔴 動画の自己レビューは必ずこの1枚を Read して行う（静止画の hero だけ見ても動画は分からない）。
import sys, os, glob, re
from PIL import Image, ImageDraw

d = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(d, "_contact.png")
fs = glob.glob(os.path.join(d, "_shot_*_*.png"))
if not fs:
    sys.exit("🔴 _shot_*.png が無い（script.py -- shots を回していない）")
grid = {}
for f in fs:
    i, j = map(int, re.findall(r"_shot_(\d+)_(\d+)\.png$", f)[0])
    grid.setdefault(i, {})[j] = Image.open(f).convert("RGB")
w, h = next(iter(next(iter(grid.values())).values())).size
pad, lab = 12, 22
W = pad + 3 * (w + pad)
H = pad + len(grid) * (h + lab + pad)
c = Image.new("RGB", (W, H), (22, 22, 22))
dr = ImageDraw.Draw(c)
for r, i in enumerate(sorted(grid)):
    y = pad + r * (h + lab + pad)
    for j, name in enumerate(("in", "mid", "out")):
        x = pad + j * (w + pad)
        dr.text((x, y), f"SHOT {i + 1}  {name}", fill=(200, 200, 200))
        if j in grid[i]:
            c.paste(grid[i][j], (x, y + lab))
c.save(out)
print(">> saved", out, c.size)
