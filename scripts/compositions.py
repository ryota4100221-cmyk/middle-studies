#!/usr/bin/env python3
# =============================================================
# MIDDLE STUDIES — 構図の型（PITFALLS #57）
#
#   python3 scripts/compositions.py                       # 次作で選べる型 ＋ これまでの分布
#   python3 scripts/compositions.py --check 寄り           # その型を今日選んでよいか
#   python3 scripts/compositions.py --verify <hero.png> 寄り  # 宣言した型と絵が合っているか
#
# 🔴 なぜ在るか（2026-08-13 実測）：
#    51作すべて、被写体の重心が画面の中央±8%（中央値46.6%）で、
#    **枠に接した作は 0/51**。つまり「1個の物が正面から丸ごと枠の中央に収まっている」を51回。
#    これは作品の構図ではなく**図鑑・物撮りの構図**で、051 ZENI が
#    「アプリアイコンに見える」のは造形ではなくこれが原因。
#
# 🔴 カメラ（85mm・(0.55,-8.3,1.95)）はシリーズの不変条件なので動かさない。
#    **被写体をどこに置き、どこで切るかは縛られていない。** 変えるのはそこだけ。
# =============================================================
import json, os, sys, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 型の定義と、heroの実測がその型であることの条件（宣言だけ変えて絵が同じ、を防ぐ）
TYPES = {
    "全身": dict(
        desc="1個の物が丸ごと枠に収まり、中央にいる（001〜051の既定）",
        cond=lambda r: r["edge"] == 0 and abs(r["c_x"] - 50) < 10,
        why="枠に接さず（edge=0）・重心xが中央±10%以内"),
    "寄り": dict(
        desc="寄って枠で切る。物の全体を見せない＝一部が画面の外へ出る",
        cond=lambda r: r["edge"] >= 1 and r["s_long"] >= 78,
        why="枠に1辺以上接し（edge≥1）・長辺78%以上"),
    "端寄せ": dict(
        desc="被写体を左右どちらかに寄せ、空いた側を余白として使う",
        cond=lambda r: r["edge"] == 0 and abs(r["c_x"] - 50) >= 12,
        why="枠に接さず・重心xが中央から12%以上ずれている"),
    "天地": dict(
        desc="高く浮かせる／低く沈める。上下の余白の配分そのものを主題にする",
        cond=lambda r: r["edge"] == 0 and abs(r["c_y"] - 63) >= 12,
        why="枠に接さず・重心yが基準63%から12%以上ずれている（基準＝51作の中央値62.7%）"),
    "対": dict(
        desc="2つの塊を離して置き、**その間**を主題にする（シリーズの主題そのもの）",
        cond=lambda r: r["clusters"] == 2 and r["big_share"] <= 72,
        why="塊がちょうど2つ・大きい方が全体の72%以下（＝どちらかが添え物になっていない）"),
    "群": dict(
        desc="小さいものが多数。1個の物としてではなく分布として見せる",
        cond=lambda r: r["clusters"] >= 5,
        why="塊が5つ以上"),
}

RECENT_BLOCK = 3    # 直近この本数に出た型は選べない


def load():
    with open(os.path.join(ROOT, "works.json")) as f:
        works = json.load(f)
    works.sort(key=lambda w: w["id"])
    return works


def blocked(works):
    recent = [w.get("comp_type") for w in works[-RECENT_BLOCK:]]
    return {t: f"直近{RECENT_BLOCK}作に出ている" for t in TYPES if t in recent}


def verify(path, t):
    from measure import measure
    r = measure(path)
    print(f"── 構図の実測（#57）")
    print(f"   重心 x {r['c_x']:.1f}% / y {r['c_y']:.1f}%   枠への接触 {r['edge']}辺   "
          f"塊 {r['clusters']}   最大塊 {r['big_share']:.0f}%   長辺 {r['s_long']:.0f}%")
    if t not in TYPES:
        print(f"🔴 「{t}」は定義に無い型"); return 1
    ok = TYPES[t]["cond"](r)
    print(f"   宣言＝「{t}」の条件：{TYPES[t]['why']}")
    if ok:
        print(f"\n✅ 絵は宣言どおり「{t}」になっている")
        return 0
    print(f"\n🔴 宣言は「{t}」だが、**絵は そうなっていない**。"
          f"\n   構図は言葉ではなく配置で決まる。被写体の位置・スケールを直すか、宣言を実物に合わせる。")
    for other, d in TYPES.items():
        if other != t and d["cond"](r):
            print(f"   （いまの絵は「{other}」の条件を満たしている）")
    return 1


def main():
    a = sys.argv[1:]
    works = load()
    bad = blocked(works)

    if len(a) >= 3 and a[0] == "--verify":
        sys.exit(verify(a[1], a[2]))

    if len(a) >= 2 and a[0] == "--check":
        t = a[1]
        if t not in TYPES:
            print(f"🔴 「{t}」は定義に無い型。使えるのは: {' / '.join(TYPES)}"); sys.exit(1)
        if t in bad:
            print(f"🔴 「{t}」は今日は選べない（{bad[t]}）"); sys.exit(1)
        print(f"✅ 「{t}」は選んでよい"); return

    print("── 構図の型（#57）")
    print(f"直近{RECENT_BLOCK}作: " + " ".join(
        f"{w['id']}:{w.get('comp_type', '?')}" for w in works[-RECENT_BLOCK:]))
    print("\n✅ 今日選べる型")
    for t, d in TYPES.items():
        if t not in bad:
            print(f"   {t:4} — {d['desc']}")
    if bad:
        print("\n🚫 今日は選べない型")
        for t, why in bad.items():
            print(f"   {t:4} — {why}")
    c = collections.Counter(w.get("comp_type") for w in works)
    print(f"\n── 全{len(works)}作の分布")
    for t, n in c.most_common():
        print(f"   {str(t):5} {n:3}  " + "█" * min(n, 60))


if __name__ == "__main__":
    main()
