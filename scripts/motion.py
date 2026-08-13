#!/usr/bin/env python3
# =============================================================
# MIDDLE STUDIES — loop.mp4 の実測（PITFALLS #59）
#
#   python3 scripts/motion.py works/051_zeni/loop.mp4
#   python3 scripts/motion.py --all
#
# 🔴 なぜ在るか：51作の品質評価を**すべて hero（静止画）でやってきた**。
#    納品は3点（hero / loop.mp4 / glb）なのに、**動きは一度も測っていない**。
#    「ループが数学的に閉じていること」はシリーズの不変条件なのに、
#    閉じているかどうかを確かめる道具が無かった。
#
# 測るのは4つ。どれも「動きの良し悪し」ではなく**動きが在るか／閉じているか**。
#   動き量      連続フレームの平均差分（中央値）。小さいほど何も起きていない
#   光の振れ    ライム面積の 最大/最小。1.0 に近い＝機構が光を変えていない（#40⑥の絵側の裏取り）
#   ループの閉じ 最終→先頭 の差分 ÷ 動き量。1.0 前後なら閉じている。大きいほど飛ぶ
#   静止率      動き量が中央値の20%未満のフレームの割合。高いほど「止まっている時間」が長い
# =============================================================
import sys, os, glob, subprocess, tempfile, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from measure import is_lime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
N_FRAMES = 24          # 等間隔で抜く枚数（120フレームの loop なら 5フレームおき）
SMALL = (180, 225)     # 差分を測る解像度（ノイズを均すため小さくする）

# --- 帯（基準期001〜030の実測分布から。#51 と同じ取り方） ---
#   動き量   001-030: P10 0.62 / 中央 3.58 / P90 8.38   ← 041-051 の中央は 1.01（基準期の 1/3.5）
#   光の振れ 001-030: P10 1.22 / 中央 3.37 / P90 45.5
#   閉じ     001-030: P10 0.20 / 中央 0.65 / P90 1.10
#   静止率   001-030: P90 9%
MOTION_MIN = 0.62      # 基準期P10。これ未満は「ほぼ動いていない」
MOTION_WARN = 1.5      # 基準期中央値の半分を割ったら△
SWING_MIN = 1.22       # 基準期P10。ライム面積の 最大/最小＝機構が光を変えているか（#40⑥の絵側の裏取り）
CLOSE_MAX = 2.2        # 基準期P90(1.10)の2倍。超えたらループが飛んでいる
CLOSE_WARN = 1.5
STILL_MAX = 0.20       # 基準期P90(9%)の2倍
TREND_N, BASE_N = 5, 30
TREND_ALARM = 0.45


def frames(path, n=N_FRAMES):
    """ffmpeg で等間隔に n 枚抜いて (小さいグレー画像, ライム面積%) の配列にする。"""
    with tempfile.TemporaryDirectory() as td:
        # nb_frames を取って等間隔で抜く（fps 指定だと端数で最終フレームを落とす）
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                              "-show_entries", "stream=nb_frames", "-of", "csv=p=0", path],
                             capture_output=True, text=True).stdout.strip()
        total = int(out) if out.isdigit() else 0
        if total < 4:
            return []
        step = max(1, total // n)
        subprocess.run(["ffmpeg", "-v", "error", "-i", path,
                        "-vf", f"select='not(mod(n\\,{step}))'", "-vsync", "0",
                        os.path.join(td, "f%04d.png")], check=True)
        out = []
        for fp in sorted(glob.glob(os.path.join(td, "*.png")))[:n]:
            im = Image.open(fp).convert("RGB")
            body = im.crop((0, 0, im.size[0], int(im.size[1] * 0.80)))
            px = list(body.getdata())
            lime = sum(1 for p in px if is_lime(p)) / len(px) * 100
            out.append((body.resize(SMALL).convert("L"), lime))
        return out


def diff(a, b):
    pa, pb = list(a.getdata()), list(b.getdata())
    return sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)


def analyse(path):
    fs = frames(path)
    if len(fs) < 4:
        return None
    ds = [diff(fs[i][0], fs[i + 1][0]) for i in range(len(fs) - 1)]
    ds_sorted = sorted(ds)
    med = ds_sorted[len(ds_sorted) // 2]
    limes = [l for _, l in fs]
    # min≈0 ＝どこかの位相で光が完全に消える＝機構として最強。∞として扱う（欠陥ではない）
    swing = (max(limes) / min(limes)) if min(limes) > 0.01 else float("inf")
    close = diff(fs[-1][0], fs[0][0]) / med if med > 0.001 else 999.0
    still = sum(1 for d in ds if d < med * 0.2) / len(ds)
    return dict(motion=med, swing=swing, close=close, still=still, n=len(fs))


def verdict(r):
    ng, warn = [], []
    if r["motion"] < MOTION_MIN:
        ng.append(f"#59 動き量 {r['motion']:.2f}<{MOTION_MIN}（ほぼ動いていない）")
    if r["close"] > CLOSE_MAX:
        ng.append(f"#59 ループの閉じ {r['close']:.1f}>{CLOSE_MAX}（最後から先頭へ飛んでいる）")
    if r["close"] > CLOSE_WARN and r["close"] <= CLOSE_MAX:
        warn.append(f"ループの閉じ {r['close']:.1f}（基準期P90は1.10。継ぎ目が見える可能性）")
    if r["motion"] < MOTION_WARN and r["motion"] >= MOTION_MIN:
        warn.append(f"動き量 {r['motion']:.2f}（基準期中央値3.58の半分未満）")
    if r["swing"] < SWING_MIN:
        warn.append(f"光の振れ {r['swing']:.2f}（機構が光を変えていない＝ただ動いているだけ）")
    if r["still"] > STILL_MAX:
        warn.append(f"静止率 {r['still']*100:.0f}%（止まっている時間が長い）")
    return ng, warn


def main():
    a = sys.argv[1:]
    if a and a[0] == "--all":
        paths = sorted(glob.glob(os.path.join(ROOT, "works", "0*_*", "loop.mp4")))
        print(f"{'work':22}{'動き量':>8}{'光の振れ':>9}{'閉じ':>7}{'静止率':>8}  判定")
        vals, names = [], []
        for p in paths:
            r = analyse(p)
            if not r:
                print(f"{os.path.basename(os.path.dirname(p)):22}  （読めない）"); continue
            ng, warn = verdict(r)
            mark = "NG: " + " / ".join(x.split("（")[0] for x in ng) if ng \
                else ("△ " + " / ".join(x.split("（")[0] for x in warn) if warn else "OK")
            print(f"{os.path.basename(os.path.dirname(p)):22}{r['motion']:8.2f}"
                  f"{('∞' if math.isinf(r['swing']) else '%.2f' % r['swing']):>9}"
                  f"{r['close']:7.1f}{r['still']*100:7.0f}%  {mark}")
            vals.append(r)
            names.append(os.path.basename(os.path.dirname(p)))
        if len(vals) >= BASE_N + TREND_N:
            def med(v):
                v = sorted(v); n = len(v)
                return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
            print(f"\n── 動きのドリフト（#59・直近{TREND_N}作 vs 基準期001〜{BASE_N:03d}）")
            for key, lab in (("motion", "動き量"), ("swing", "光の振れ")):
                b = [x[key] for x in vals[:BASE_N] if not math.isinf(x[key])]
                r5 = [x[key] for x in vals[-TREND_N:] if not math.isinf(x[key])]
                if not b or not r5:
                    continue
                ratio = med(r5) / med(b)
                mark = "🔴" if ratio < TREND_ALARM else ("△" if ratio < 0.7 else "  ")
                print(f"   {mark} {lab:6} 基準期 {med(b):6.2f} → 直近{TREND_N}作 {med(r5):6.2f}（{ratio*100:.0f}%）")
        return

    if not a:
        print("usage: motion.py <loop.mp4> | --all"); sys.exit(2)
    r = analyse(a[0])
    if not r:
        print("🔴 フレームを読めなかった"); sys.exit(2)
    print("── 動き（PITFALLS #59）")
    print(f"   動き量 {r['motion']:.2f}   光の振れ {'∞' if math.isinf(r['swing']) else '%.2f' % r['swing']}   "
          f"ループの閉じ {r['close']:.1f}   静止率 {r['still']*100:.0f}%   （{r['n']}枚で計測）")
    ng, warn = verdict(r)
    if warn:
        print("\n△ 要注意:")
        for x in warn: print("   - " + x)
    if ng:
        print("\n🔴 不合格:")
        for x in ng: print("   - " + x)
        sys.exit(1)
    print("\n✅ 合格")


if __name__ == "__main__":
    main()
