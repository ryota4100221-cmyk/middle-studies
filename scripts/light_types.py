#!/usr/bin/env python3
# =============================================================
# MIDDLE STUDIES — 光の型（PITFALLS #53）
#
#   python3 scripts/light_types.py           # 次作で選べる型 ＋ これまでの分布
#   python3 scripts/light_types.py --check 隙間   # その型を今日選んでよいか（不可なら exit 1）
#
# 🔴 題材のドメイン（玩具／農／建築…）の重複回避とは**別の軸**。
#    ドメインだけ見ていた結果、041〜050 は **10作中8作が「隙間」**になった。
#    ——黒い塊に細い光が1本、を10日続けても、題材が毎日違えば気づけない。
# =============================================================
import json, os, sys, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# 8つの型（＝「光がどう現れるか」。造形でも題材でもない）
TYPES = {
    "内包": "黒い殻の内側が光り、開口や隙間から見える（001 THE FILLING／004 ANDON）",
    "面":   "光る面そのものが正面に見える。円盤・液面・格子越しの面（028 ENSO／030 HACHINOSU）",
    "隙間": "2つの黒の間・割れ目・断面から漏れる細い光（003 DANSOU／042 KINTSUGI）",
    "窓":   "黒に開いた孔の“形”が光る。孔の形が主役（017 KAGIANA／031 TOURO）",
    "反復": "縞・輪・格子として多数現れる（014 NENRIN／019 AYA）",
    "稜線": "縁・赤道・輪郭に沿って走る線（002 OBI／032 SUZU）",
    "芯":   "中心の小さな塊。周りは黒（013 HAGURUMA／050 KENDAMA）",
    "背光": "光源が被写体の背後にあり、黒は縁だけ光る（012 SHOKU／035 KUSHI）",
}

RECENT_BLOCK = 5    # 直近この本数に出た型は選べない
WINDOW = 10         # 直近この本数のうち
WINDOW_MAX = 2      # 同じ型がこの回数を超えて出ていたら選べない


def load():
    with open(os.path.join(ROOT, "works.json")) as f:
        works = json.load(f)
    works.sort(key=lambda w: w["id"])
    return works


def blocked(works):
    recent = [w.get("light_type") for w in works[-RECENT_BLOCK:]]
    window = collections.Counter(w.get("light_type") for w in works[-WINDOW:])
    out = {}
    for t in TYPES:
        if t in recent:
            out[t] = f"直近{RECENT_BLOCK}作に出ている"
        elif window[t] > WINDOW_MAX:
            out[t] = f"直近{WINDOW}作で{window[t]}回出ている（上限{WINDOW_MAX}）"
    return out


def main():
    works = load()
    bad = blocked(works)
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        t = sys.argv[2]
        if t not in TYPES:
            print(f"🔴 「{t}」は定義に無い型。使えるのは: {' / '.join(TYPES)}"); sys.exit(1)
        if t in bad:
            print(f"🔴 「{t}」は今日は選べない（{bad[t]}）"); sys.exit(1)
        print(f"✅ 「{t}」は選んでよい"); return

    print("── 光の型（#53）")
    print(f"直近{WINDOW}作: " + " ".join(f"{w['id']}:{w.get('light_type','?')}" for w in works[-WINDOW:]))
    print("\n✅ 今日選べる型")
    for t, desc in TYPES.items():
        if t not in bad:
            print(f"   {t}  — {desc}")
    print("\n🚫 今日は選べない型")
    for t, why in bad.items():
        print(f"   {t}  — {why}")
    c = collections.Counter(w.get("light_type") for w in works)
    print("\n── 全" + str(len(works)) + "作の分布")
    for t, n in c.most_common():
        print(f"   {t:4} {n:3}  " + "█" * n)


if __name__ == "__main__":
    main()
