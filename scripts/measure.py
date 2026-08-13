#!/usr/bin/env python3
# =============================================================
# MIDDLE STUDIES — hero 実測スクリプト（PITFALLS #14 ＋ #45 ＋ #51）
#
#   python3 scripts/measure.py works/046_makimono/hero.png
#   python3 scripts/measure.py --all          # 全作を並べて時系列で見る
#   python3 scripts/measure.py --trend        # 直近5作 vs 全作の中央値だけを見る
#
# 毎回その場でPILのコードを書き直さない。指標の定義はここだけに置く。
# 🔴 ライムの指標（#14）と黒の指標（#45）は**必ず両方**通す。
#    片方だけ通す運用が「ライムは光っているが黒が影絵」を生んだ（2026-08-10）。
#
# 🔴 **このスクリプトが「合格」と言っても、絵が壊れていないことは保証しない。**
#    実例（#47）：044 に Coat 0.34 を入れたら p98 61.1・std 21.1・平均 28.6 で
#    **全項目合格したまま、黒が鏡面化して基壇にキャプションの文字が映った。**
#    鏡面化・#17 のプラスチック化・#17-b の紙の艶は、どれも数値に出ない。
#    → **Coat や Roughness を触ったら、必ず hero を目視して**
#      「文字・床・環境が黒い面に映り込んでいないか」を確認する。
#
# 🔴 **黒p98 58（BLACK_P98_WARN）は達成目標ではなく、ドリフトの検知器。**
#    カメラに正対したマットな黒面では 50〜56 が物理的に正しい（#47で3レバーを実測して確認）。
#    △が出ても、造形の必然でそうなっているなら現状維持が正解。**△を消しに行って絵を壊さない。**
#
# 🔴🔴 **片側だけの下限は、何作もかけてその方向へ振り切れる（2026-08-13・PITFALLS #51）。**
#    旧 halo の合格ラインは `≥1000` の**片側だけ**で、上限もトレンド判定も無かった。
#    結果：001〜030 の halo 中央値 36,032 に対し **041〜050 は 12,791（1/3）**、
#    050 KENDAMA は **2,828 で「合格」**。ライム面積も 2.0% → 1.0% に半減していた。
#    **1作ずつ見ている限り、この落ち方は絶対に見つからない。**
#    → 下限だけでなく**上限**を置き、さらに**直近5作の中央値が全作中央値の1/3を割ったら🔴**を出す。
#    帯の値は思いつきではなく **001〜030（ドリフト前）の実測分布の P10 / P90** から取っている。
# =============================================================
import sys, os, glob, math, json
from PIL import Image

# --- 合格ライン ------------------------------------------------
LIME_STD_MIN  = 35      # #14 勾配（ペンキ化の検知）
BLACK_P98_MIN = 50      # #45 黒のハイライト＝面が光を拾っているか（不合格ライン）
BLACK_MEAN_LO = 14      # #45 これ未満は「黒が黒い」でなく「影絵」（不合格ライン）
BLACK_P98_WARN = 58     # #45 ここを割ったら要注意（001〜040の健全域は 56〜69）
BLACK_STD_WARN = 12     # #45 陰影の幅。ただし一様に明るい造形では低く出るので警告どまり
BLACK_MEAN_HI = 52      # #17-c 灰色ヴェール側の警告（従来の失敗の方向）

# --- #51 光の量（両側） ---------------------------------------
# 001〜030 の実測分布：halo P10=9,101 / 中央=36,032 / P90=217,369
#                      ライム面積 P10=0.8% / 中央=2.0% / P90=10.3%
HALO_MIN      = 9000    # #51 下限（旧 1000 は低すぎて検知器として機能していなかった）
HALO_HI       = 250000  # #51 上限側の警告（白飛び・画面が緑に沈む。028 ENSO が 410,157）
LIME_AREA_MIN = 0.8     # #51 「真ん中に光がある」の下限。これを割ると光が点景になる
LIME_AREA_HI  = 12.0    # #51 上限側の警告（光が主役でなく地になる）

# --- #58 光が空間に作用しているか（床に落ちたライム） -------
# 51作の実測：中央値 0.42% / P75 1.53%。強いのは初期作（001=24.5・016=22.4・007=17.5）。
# 🔴 「光っている物」と「光源」は別物。床に何も落ちていない絵は、発光面がただの点いたパネルに見える。
FLOOR_LIME_MIN = 0.3    # #58 下限（現状51作中21作がここを割る＝ほぼ半分が空間に光を出していない）
FLOOR_LIME_HI  = 32.0   # #58 上限の警告（床まで緑に染まると舞台が緑になる。001=24.5 は健全側）

# --- #51 被写体の大きさ（長辺で測る） -------------------------
# 🔴 面積で測らない。001〜030 と 041〜050 で bbox 面積は 37%→26% に落ちるが、
#    **長辺は 54%→55% で変わっていない**＝小さくなったのではなく縦長になっただけ。
#    SKILL.md の「画面の55〜65%」はこの長辺のこと（実測中央値 54〜57 で整合）。
LONG_LO, LONG_HI = 44, 66      # 001〜030 の P10=44 / P90=64（両側とも警告どまり）

CAPTION_TOP = 0.80      # キャプション3行を除外（下20%は測らない）
DARK_CUT    = 70        # これ未満を「黒画素」とみなす

# --- #51 トレンド判定 ------------------------------------------
# 🔴 基準は「全作の中央値」にしてはいけない。**退化した作が基準そのものを引き下げる**ため、
#    実測で直近5作は全作中央値の 98%＝健全に見えた（実際は基準期比 68%）。
#    基準は**ドリフト前の 001〜030（＝帯の値を取ったのと同じ期間）に固定**する。
TREND_N     = 5         # 直近N作
BASE_N      = 30        # 基準期＝001〜030（固定。新作が増えても動かさない）
TREND_ALARM = 0.45      # 基準期中央値のこれを割ったら🔴
TREND_WARN  = 0.70      # ここを割ったら△
# 逆検証（2026-08-13・48ウィンドウ）：0.45 は 035〜047 の実際のドリフトを連続で捕まえ、
# 健全期の誤報は 016〜018（halo 49%）の3ウィンドウだけに収まる。1/3 では 041〜050 の
# halo 中央値（基準比 35%）すら鳴らず、**検知器として機能しなかった**。

# ⚠️ p98 の読み方：黒画素の定義が「輝度 < DARK_CUT」なので、黒が明るくなるほど
#    明るい画素が母集団から抜け、p98 は頭打ち〜わずかに下がることがある。
#    **黒平均が上がっているのに p98 が微減した場合は退行ではない。** 必ず2つを併せて読む。
#    p98 が意味を持つのは「暗い側＝光を拾っていない」の検知（50を割る）であって、
#    明るい側の優劣を比べる物差しではない。

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".measure_cache.json")


def lum(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def is_lime(p):
    return p[1] > 90 and p[1] > p[2] + 45 and p[1] >= p[0] + 20


def _clusters(body, W, bh, step=6):
    """#57 被写体が画面の中でいくつの塊に分かれているか（対・群の判定用）。
       1/6 に間引いたグリッドで4近傍の連結成分を数える。小さすぎる粒（ノイズ）は捨てる。"""
    gw, gh = W // step, bh // step
    grid = [[False] * gw for _ in range(gh)]
    for gy in range(gh):
        row = grid[gy]
        base = gy * step * W
        for gx in range(gw):
            p = body[base + gx * step]
            row[gx] = is_lime(p) or lum(p) < DARK_CUT
    # 🔴 膨張してから数える。ブルームのハロー（淡い黄白）は「ライムでも黒でもない」ので
    #    素のマスクだと1つの物が途中で切れる（001 THE FILLING が6塊と出た）。
    for _ in range(1):
        grow = [row[:] for row in grid]
        for gy in range(gh):
            for gx in range(gw):
                if grid[gy][gx]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < gw and 0 <= ny < gh and grid[ny][nx]:
                        grow[gy][gx] = True
                        break
        grid = grow
    seen = [[False] * gw for _ in range(gh)]
    sizes = []
    for gy in range(gh):
        for gx in range(gw):
            if not grid[gy][gx] or seen[gy][gx]:
                continue
            stack = [(gx, gy)]; seen[gy][gx] = True; n = 0
            while stack:
                x, y = stack.pop(); n += 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < gw and 0 <= ny < gh and grid[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True; stack.append((nx, ny))
            sizes.append(n)
    total = sum(sizes)
    if not total:
        return 0, 0.0
    keep = [s for s in sizes if s >= max(6, total * 0.02)]   # 2%未満の粒は数えない
    return len(keep), max(sizes) / total * 100


def measure(path):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    px = list(im.getdata())
    bh = int(H * CAPTION_TOP)
    body = list(im.crop((0, 0, W, bh)).getdata())

    # --- ライム（#14）: 画像全体で測る ---
    lime = [p for p in px if is_lime(p)]
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

    # --- ライム面積（#51）: キャプションを除いた上80%に対する割合 ---
    lime_body = [i for i, p in enumerate(body) if is_lime(p)]
    lime_area = len(lime_body) / len(body) * 100

    # --- 被写体の長辺（#51）: 黒画素 ∪ ライム画素の 1〜99 パーセンタイル矩形 ---
    #     外れ値（床の粒・ブルームの飛び）で矩形が伸びないよう両端1%を捨てる。
    subj = sorted(set(lime_body + [i for i, p in enumerate(body) if lum(p) < DARK_CUT]))
    if subj:
        xs = sorted(i % W for i in subj)
        ys = sorted(i // W for i in subj)
        trim = lambda v: (v[int(len(v) * 0.01)], v[int(len(v) * 0.99)])
        x0, x1 = trim(xs)
        y0, y1 = trim(ys)
        s_w, s_h = (x1 - x0) / W * 100, (y1 - y0) / H * 100
        # --- 構図（#57）: 重心・枠への接触・塊の数 ---
        # 🔴 下端は数えない。body は上80%で切っているので、下端＝キャプション帯であって画面の端ではない。
        c_x = sum(xs) / len(xs) / W * 100
        c_y = sum(ys) / len(ys) / bh * 100
        edge = ((min(xs) < W * 0.005) + (max(xs) > W * 0.995) + (min(ys) < bh * 0.005))
    else:
        s_w = s_h = c_x = c_y = 0.0
        edge = 0
    clusters, big_share = _clusters(body, W, bh)

    # --- 光の作用（#58）: 被写体の下の床に、ライムの照り返しが落ちているか ---
    # 発光体の外に光が出ていない作は「光っている物」でなく「点いている面」に見える。
    # 被写体の下端からキャプション帯までを床とみなし、緑に寄った明るい画素の割合を測る。
    # 🔴 帯は固定（画面の62〜80%＝床が写る帯）。被写体のbboxの下だけを見る作り方は、
    #    被写体が下まで伸びている作で帯が消えて**一律0%になり、検知器として死ぬ**（最初そう作って失敗した）。
    #    分母は「被写体でない画素」だけ。発光そのもの（is_lime）と白飛びは数えない。
    fl = [body[i] for i in range(int(bh * 0.62) * W, bh * W, 3)]
    ground = [p for p in fl if not is_lime(p) and lum(p) >= DARK_CUT and lum(p) < 250]
    # 帯の大半が被写体で埋まっている（＝#57「寄り」の型など）ときは測れない → -1（判定を飛ばす）
    floor_lime = (sum(1 for p in ground if p[1] > p[0] + 4 and p[1] > p[2] + 8)
                  / len(ground) * 100) if len(ground) > len(fl) * 0.15 else -1.0

    # --- 黒（#45）: キャプションを除いた上80%で測る ---
    dark = [lum(p) for p in body
            if lum(p) < DARK_CUT and not (p[1] > p[0] + 18 and p[1] > p[2] + 18)]
    base = dict(lime_mid=avg, lime_std=std, halo=halo, lime_area=lime_area,
                s_w=s_w, s_h=s_h, s_long=max(s_w, s_h),
                c_x=c_x, c_y=c_y, edge=edge, clusters=clusters, big_share=big_share,
                floor_lime=floor_lime)
    if len(dark) < 300:
        base.update(b_area=0.0, b_mean=0.0, b_std=0.0, b_p98=0.0)
        return base
    dark.sort()
    bm = sum(dark) / len(dark)
    bs = math.sqrt(sum((d - bm) ** 2 for d in dark) / len(dark))
    base.update(b_area=len(dark) / len(body) * 100, b_mean=bm, b_std=bs,
                b_p98=dark[int(len(dark) * 0.98)])
    return base


# --- キャッシュ（--all / --trend を毎回50枚読み直さないため） -----
def measure_cached(path):
    try:
        with open(CACHE) as f:
            cache = json.load(f)
    except Exception:
        cache = {}
    st = os.stat(path)
    key = os.path.relpath(path, ROOT)
    sig = [int(st.st_mtime), st.st_size]
    hit = cache.get(key)
    if hit and hit.get("sig") == sig:
        return hit["r"]
    r = measure(path)
    r["lime_mid"] = list(r["lime_mid"])
    cache[key] = {"sig": sig, "r": r}
    try:
        with open(CACHE, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass
    return r


def all_paths():
    return sorted(glob.glob(os.path.join(ROOT, "works", "0*_*", "hero.png")))


def verdict(r):
    """(不合格, 要注意) を返す。不合格が1つでもあれば作り直し。"""
    ng, warn = [], []
    if r["lime_std"] < LIME_STD_MIN:  ng.append(f"#14 ライムstd {r['lime_std']:.0f}<{LIME_STD_MIN}（ペンキ化）")
    if r["halo"] < HALO_MIN:          ng.append(f"#51 halo {r['halo']}<{HALO_MIN}（光が滲んでいない＝点景化）")
    if r["lime_area"] < LIME_AREA_MIN: ng.append(f"#51 ライム面積 {r['lime_area']:.2f}%<{LIME_AREA_MIN}%（光が主役でない）")
    if 0 <= r.get("floor_lime", -1) < FLOOR_LIME_MIN:
        ng.append(f"#58 床のライム {r['floor_lime']:.2f}%<{FLOOR_LIME_MIN}%（光が空間に出ていない）")
    if r["b_p98"] < BLACK_P98_MIN:    ng.append(f"#45 黒p98 {r['b_p98']:.0f}<{BLACK_P98_MIN}（黒が光を拾っていない＝影絵）")
    if r["b_mean"] < BLACK_MEAN_LO:   ng.append(f"#45 黒平均 {r['b_mean']:.0f}<{BLACK_MEAN_LO}（沈めすぎ）")
    if r.get("floor_lime", -1) > FLOOR_LIME_HI:
        warn.append(f"床のライム {r['floor_lime']:.0f}%（>{FLOOR_LIME_HI}%：舞台まで緑に染まっている）")
    if r["halo"] > HALO_HI:
        warn.append(f"halo {r['halo']}（>{HALO_HI}：白飛び側）")
    if r["lime_area"] > LIME_AREA_HI:
        warn.append(f"ライム面積 {r['lime_area']:.1f}%（>{LIME_AREA_HI}%：光が地になっている）")
    if not (LONG_LO <= r["s_long"] <= LONG_HI):
        warn.append(f"長辺 {r['s_long']:.0f}%（健全域 {LONG_LO}〜{LONG_HI}%＝SKILL.mdの55〜65%。"
                    f"ただし#57の「寄り」の型では枠から出るのが正しいので、この△は無視してよい）")
    if BLACK_P98_MIN <= r["b_p98"] < BLACK_P98_WARN:
        warn.append(f"黒p98 {r['b_p98']:.0f}（健全域56〜69の下端）")
    if r["b_std"] < BLACK_STD_WARN:
        warn.append(f"黒std {r['b_std']:.0f}（陰影が薄い。一様に明るい造形なら可）")
    if r["b_mean"] > BLACK_MEAN_HI:
        warn.append(f"黒平均 {r['b_mean']:.0f}（#17-c の灰色ヴェール側）")
    return ng, warn


def median(v):
    v = sorted(v)
    n = len(v)
    return 0.0 if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)


def trend(quiet=False):
    """#51 直近TREND_N作の中央値が、基準期（001〜BASE_N）の中央値に対して落ちていないか。
       戻り値は🔴行のリスト（空なら健全）。"""
    paths = all_paths()
    if len(paths) < BASE_N + TREND_N:
        return []
    rs = [measure_cached(p) for p in paths]
    alarms, lines = [], []
    for key, label, fmt in [("halo", "halo", "{:.0f}"),
                            ("lime_area", "ライム面積%", "{:.2f}"),
                            ("s_long", "長辺%", "{:.0f}")]:
        basem = median([r[key] for r in rs[:BASE_N]])
        recm = median([r[key] for r in rs[-TREND_N:]])
        ratio = recm / basem if basem else 1.0
        mark = "🔴" if ratio < TREND_ALARM else ("△" if ratio < TREND_WARN else "  ")
        lines.append(f"   {mark} {label:12} 基準期001〜{BASE_N:03d} {fmt.format(basem):>9} → "
                     f"直近{TREND_N}作 {fmt.format(recm):>9}（{ratio*100:.0f}%）")
        if ratio < TREND_ALARM:
            alarms.append(f"{label} が基準期の {ratio*100:.0f}% まで落ちている")
    if not quiet:
        print(f"\n── シリーズのドリフト（#51・直近{TREND_N}作 vs 基準期001〜{BASE_N:03d}）")
        for l in lines:
            print(l)
        if alarms:
            print("   🔴 1作ずつ見ていても見つからない退化が起きている。"
                  "帯の下限に触れていなくても、次作は基準期へ戻す方向で作る。")
    return alarms


def main():
    args = sys.argv[1:]

    if args and args[0] == "--trend":
        trend()
        return

    if args and args[0] == "--all":
        paths = all_paths()
        print(f"{'work':22}{'黒面積%':>8}{'黒平均':>7}{'黒std':>7}{'黒p98':>7}"
              f"{'ライムstd':>9}{'ライム面積%':>11}{'halo':>8}{'長辺%':>7}  判定")
        for p in paths:
            r = measure_cached(p)
            ng, warn = verdict(r)
            mark = "NG: " + " / ".join(x.split("（")[0] for x in ng) if ng \
                else ("△ " + " / ".join(x.split("（")[0] for x in warn) if warn else "OK")
            print(f"{os.path.basename(os.path.dirname(p)):22}"
                  f"{r['b_area']:8.1f}{r['b_mean']:7.1f}{r['b_std']:7.1f}{r['b_p98']:7.1f}"
                  f"{r['lime_std']:9.1f}{r['lime_area']:11.2f}{r['halo']:8d}{r['s_long']:7.0f}  {mark}")
        trend()
        return

    if not args:
        print("usage: measure.py <hero.png> | --all | --trend"); sys.exit(2)

    r = measure(args[0])
    print("── ライム（PITFALLS #14 ＋ #51）")
    print("   中間調 #%02X%02X%02X   std %.1f   halo %d   面積 %.2f%%"
          % (*r["lime_mid"], r["lime_std"], r["halo"], r["lime_area"]))
    print("── 黒（PITFALLS #45）")
    print("   面積 %.1f%%   平均 %.1f   std %.1f   p98 %.1f" % (r["b_area"], r["b_mean"], r["b_std"], r["b_p98"]))
    print("── 光の作用（PITFALLS #58）")
    print("   床のライム %s" % ("測れない（帯が被写体で埋まっている）" if r["floor_lime"] < 0
                                 else "%.2f%%" % r["floor_lime"]))
    print("── 被写体（PITFALLS #51）")
    print("   長辺 %.0f%%（幅 %.0f%% / 高さ %.0f%%）" % (r["s_long"], r["s_w"], r["s_h"]))
    ng, warn = verdict(r)
    if warn:
        print("\n△ 要注意:")
        for x in warn: print("   - " + x)
    if ng:
        print("\n🔴 不合格（作り直し）:")
        for x in ng: print("   - " + x)
        print("\n   黒が不合格のときは造形でなく Specular IOR Level を疑う（PITFALLS #45）。")
        print("   主材の下限は 0.10。0.02〜0.05 まで落とすと黒は影絵になる。")
        print("   光が不合格のときは**造形を作り直す前に光の出し方を変える**（PITFALLS #51）。")
        print("   細い線で出していないか＝面で出す・透過させる・内側から出す。2周で入らなければ題材を替える。")
        print("   床のライムが不合格のときは**随伴のライム光源のW数**（#58）。4.5W では床に届かない＝150W前後。")
        print("   🔴 その光源は発光体の**外**に置く。中に置くと発光体自身が遮って1ルクスも出ない。")
        trend()
        sys.exit(1)
    trend()
    print("\n✅ 合格")


if __name__ == "__main__":
    main()
