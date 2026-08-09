#!/usr/bin/env python3
# =============================================================
# MIDDLE STUDIES — hero 実測スクリプト（PITFALLS #14 ＋ #45）
#
#   python3 scripts/measure.py works/046_makimono/hero.png
#   python3 scripts/measure.py --all          # 全作を並べて時系列で見る
#
# 毎回その場でPILのコードを書き直さない。指標の定義はここだけに置く。
# 🔴 ライムの指標（#14）と黒の指標（#45）は**必ず両方**通す。
#    片方だけ通す運用が「ライムは光っているが黒が影絵」を生んだ（2026-08-10）。
# =============================================================
import sys, os, glob, math
from PIL import Image

# --- 合格ライン ------------------------------------------------
LIME_STD_MIN  = 35      # #14 勾配（ペンキ化の検知）
LIME_HALO_MIN = 1000    # #14 ハロー
BLACK_P98_MIN = 50      # #45 黒のハイライト＝面が光を拾っているか（不合格ライン）
BLACK_MEAN_LO = 14      # #45 これ未満は「黒が黒い」でなく「影絵」（不合格ライン）
BLACK_P98_WARN = 58     # #45 ここを割ったら要注意（001〜040の健全域は 56〜69）
BLACK_STD_WARN = 12     # #45 陰影の幅。ただし一様に明るい造形では低く出るので警告どまり
BLACK_MEAN_HI = 52      # #17-c 灰色ヴェール側の警告（従来の失敗の方向）

CAPTION_TOP = 0.80      # キャプション3行を除外（下20%は測らない）


def lum(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def measure(path):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    px = list(im.getdata())
    body = list(im.crop((0, 0, W, int(H * CAPTION_TOP))).getdata())

    # --- ライム（#14）: 画像全体で測る ---
    lime = [p for p in px if p[1] > 90 and p[1] > p[2] + 45 and p[1] >= p[0] + 20]
    if lime:
        ls = sorted((lum(p), p) for p in lime)
        mid = [p for _, p in ls[len(ls) // 5: len(ls) * 4 // 5]]
        avg = tuple(round(sum(p[i] for p in mid) / len(mid)) for i in range(3))
        m = sum(l for l, _ in ls) / len(ls)
        std = math.sqrt(sum((l - m) ** 2 for l, _ in ls) / len(ls))
    else:
        avg, std = (0, 0, 0), 0.0
    halo = sum(1 for p in px if 150 < p[0] < 230 and p[1] > 200
               and 90 < p[2] < 190 and p[1] > p[2] + 30)

    # --- 黒（#45）: キャプションを除いた上80%で測る ---
    dark = [lum(p) for p in body
            if lum(p) < 70 and not (p[1] > p[0] + 18 and p[1] > p[2] + 18)]
    if len(dark) < 300:
        return dict(lime_mid=avg, lime_std=std, halo=halo,
                    b_area=0.0, b_mean=0.0, b_std=0.0, b_p98=0.0)
    dark.sort()
    bm = sum(dark) / len(dark)
    bs = math.sqrt(sum((d - bm) ** 2 for d in dark) / len(dark))
    return dict(lime_mid=avg, lime_std=std, halo=halo,
                b_area=len(dark) / len(body) * 100,
                b_mean=bm, b_std=bs, b_p98=dark[int(len(dark) * 0.98)])


def verdict(r):
    """(不合格, 要注意) を返す。不合格が1つでもあれば作り直し。"""
    ng, warn = [], []
    if r["lime_std"] < LIME_STD_MIN:  ng.append(f"#14 ライムstd {r['lime_std']:.0f}<{LIME_STD_MIN}（ペンキ化）")
    if r["halo"] < LIME_HALO_MIN:     ng.append(f"#14 halo {r['halo']}<{LIME_HALO_MIN}（ブルーム死）")
    if r["b_p98"] < BLACK_P98_MIN:    ng.append(f"#45 黒p98 {r['b_p98']:.0f}<{BLACK_P98_MIN}（黒が光を拾っていない＝影絵）")
    if r["b_mean"] < BLACK_MEAN_LO:   ng.append(f"#45 黒平均 {r['b_mean']:.0f}<{BLACK_MEAN_LO}（沈めすぎ）")
    if BLACK_P98_MIN <= r["b_p98"] < BLACK_P98_WARN:
        warn.append(f"黒p98 {r['b_p98']:.0f}（健全域56〜69の下端）")
    if r["b_std"] < BLACK_STD_WARN:
        warn.append(f"黒std {r['b_std']:.0f}（陰影が薄い。一様に明るい造形なら可）")
    if r["b_mean"] > BLACK_MEAN_HI:
        warn.append(f"黒平均 {r['b_mean']:.0f}（#17-c の灰色ヴェール側）")
    return ng, warn


def main():
    args = sys.argv[1:]
    if args and args[0] == "--all":
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "works")
        paths = sorted(glob.glob(os.path.join(root, "0*_*", "hero.png")))
        print(f"{'work':22}{'黒面積%':>8}{'黒平均':>7}{'黒std':>7}{'黒p98':>7}"
              f"{'ライムstd':>9}{'halo':>8}  判定")
        for p in paths:
            r = measure(p)
            ng, warn = verdict(r)
            mark = "NG: " + " / ".join(x.split("（")[0] for x in ng) if ng \
                else ("△ " + " / ".join(x.split("（")[0] for x in warn) if warn else "OK")
            print(f"{os.path.basename(os.path.dirname(p)):22}"
                  f"{r['b_area']:8.1f}{r['b_mean']:7.1f}{r['b_std']:7.1f}{r['b_p98']:7.1f}"
                  f"{r['lime_std']:9.1f}{r['halo']:8d}  {mark}")
        return

    if not args:
        print("usage: measure.py <hero.png> | --all"); sys.exit(2)

    r = measure(args[0])
    print("── ライム（PITFALLS #14）")
    print("   中間調 #%02X%02X%02X   std %.1f   halo %d" % (*r["lime_mid"], r["lime_std"], r["halo"]))
    print("── 黒（PITFALLS #45）")
    print("   面積 %.1f%%   平均 %.1f   std %.1f   p98 %.1f" % (r["b_area"], r["b_mean"], r["b_std"], r["b_p98"]))
    ng, warn = verdict(r)
    if warn:
        print("\n△ 要注意:")
        for x in warn: print("   - " + x)
    if ng:
        print("\n🔴 不合格（作り直し）:")
        for x in ng: print("   - " + x)
        print("\n   黒が不合格のときは造形でなく Specular IOR Level を疑う（PITFALLS #45）。")
        print("   主材の下限は 0.10。0.02〜0.05 まで落とすと黒は影絵になる。")
        sys.exit(1)
    print("\n✅ 合格")


if __name__ == "__main__":
    main()
