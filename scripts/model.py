#!/usr/bin/env python3
# =============================================================
# MIDDLE STUDIES — model.glb の実測（PITFALLS #60）
#
#   python3 scripts/model.py works/051_zeni/model.glb
#   python3 scripts/model.py --all
#
# 🔴 なぜ在るか：納品は3点（hero / loop.mp4 / model.glb）。
#    hero は #14/#45/#51/#57/#58 で、loop は #59 で測るようにしたが、
#    **glb だけ一度も測っていない**。しかも glb は
#      ・R3F（[[project_monaka_gl]]）にそのまま乗る素材
#      ・Emission を定数に潰して書き出している（#30）
#      ・開いた殻を作らない（#37②）という不変条件がある
#    という、**壊れても hero では絶対に気づけない**場所。
#
# 外部ライブラリを使わず GLB を直接読む（JSONチャンク＋BINチャンク）。
#   容量        MB。#43-e で morph target が重い問題が実在した
#   三角形      primitive の indices から
#   開いた辺%   1回しか使われない辺の割合。**閉じた立体なら 0%**。板・帯は正当に増える
#   発光        materials に emissiveFactor が入っているか（ライムが glb に乗っているか）
#   動き        animations か morph target があるか（loop が glb に乗っているか）
#   寸法        POSITION accessor の min/max（ワールド実寸）
# =============================================================
import sys, os, glob, json, struct

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

SIZE_HI = 8.0        # MB。#43-e で 10.2MB を 5MB級に落とした経緯があるので上限を置く
OPEN_EDGE_HI = 12.0  # %。閉じた立体なら0。板・帯でも12%を超えたら殻が開いている疑い
TRI_MAX = 600000     # これを超えたら辺の検査は重いので飛ばす


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"glTF":
        return None, None
    n = struct.unpack("<I", data[12:16])[0]
    js = json.loads(data[20:20 + n])
    bin_chunk = b""
    off = 20 + n
    while off < len(data):
        clen, ctype = struct.unpack("<II", data[off:off + 8])
        if ctype == 0x004E4942:      # BIN
            bin_chunk = data[off + 8: off + 8 + clen]
        off += 8 + clen + (-clen % 4)
    return js, bin_chunk


COMP = {5121: ("B", 1), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}


def accessor_ints(js, binc, idx):
    acc = js["accessors"][idx]
    bv = js["bufferViews"][acc["bufferView"]]
    fmt, size = COMP[acc["componentType"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    cnt = acc["count"]
    return struct.unpack_from("<%d%s" % (cnt, fmt), binc, start)


def analyse(path):
    js, binc = read_glb(path)
    if not js:
        return None
    tris = 0
    open_edges = total_edges = 0
    heavy = False
    for mesh in js.get("meshes", []):
        for prim in mesh.get("primitives", []):
            if "indices" not in prim:
                continue
            idx = accessor_ints(js, binc, prim["indices"])
            tris += len(idx) // 3
    if tris and tris <= TRI_MAX:
        edges = {}
        for mesh in js.get("meshes", []):
            for prim in mesh.get("primitives", []):
                if "indices" not in prim:
                    continue
                idx = accessor_ints(js, binc, prim["indices"])
                for i in range(0, len(idx) - 2, 3):
                    a, b, c = idx[i], idx[i + 1], idx[i + 2]
                    for e in ((a, b), (b, c), (c, a)):
                        k = (min(e), max(e))
                        edges[k] = edges.get(k, 0) + 1
        total_edges = len(edges)
        open_edges = sum(1 for v in edges.values() if v == 1)
    else:
        heavy = True

    emissive = any(any(x > 0.01 for x in m.get("emissiveFactor", [0, 0, 0]))
                   for m in js.get("materials", []))
    morph = any("targets" in p for m in js.get("meshes", []) for p in m.get("primitives", []))
    anim = bool(js.get("animations"))

    lo = [1e9] * 3; hi = [-1e9] * 3
    for mesh in js.get("meshes", []):
        for prim in mesh.get("primitives", []):
            a = js["accessors"][prim["attributes"]["POSITION"]]
            if "min" in a and "max" in a:
                lo = [min(lo[i], a["min"][i]) for i in range(3)]
                hi = [max(hi[i], a["max"][i]) for i in range(3)]
    size = [round(hi[i] - lo[i], 2) for i in range(3)] if hi[0] > -1e8 else [0, 0, 0]

    return dict(mb=os.path.getsize(path) / 1048576, tris=tris,
                open_pct=(open_edges / total_edges * 100) if total_edges else -1.0,
                heavy=heavy, emissive=emissive, morph=morph, anim=anim, size=size,
                mats=len(js.get("materials", [])))


def verdict(r):
    ng, warn = [], []
    if not r["emissive"]:
        ng.append("#60 発光が乗っていない（glbを開いた人にライムが伝わらない・#30）")
    if not (r["morph"] or r["anim"]):
        ng.append("#60 動きが乗っていない（loopがglbに入っていない）")
    if r["open_pct"] > OPEN_EDGE_HI:
        warn.append(f"開いた辺 {r['open_pct']:.0f}%（>{OPEN_EDGE_HI}%：殻が開いている疑い・#37②）")
    if r["mb"] > SIZE_HI:
        warn.append(f"容量 {r['mb']:.1f}MB（>{SIZE_HI}MB・#43-e）")
    return ng, warn


def main():
    a = sys.argv[1:]
    if a and a[0] == "--all":
        print(f"{'work':22}{'MB':>7}{'三角形':>10}{'開いた辺%':>10}{'発光':>5}{'動き':>5}  判定")
        for p in sorted(glob.glob(os.path.join(ROOT, "works", "0*_*", "model.glb"))):
            r = analyse(p)
            name = os.path.basename(os.path.dirname(p))
            if not r:
                print(f"{name:22}  （読めない）"); continue
            ng, warn = verdict(r)
            mark = "NG: " + " / ".join(x.split("（")[0] for x in ng) if ng \
                else ("△ " + " / ".join(x.split("（")[0] for x in warn) if warn else "OK")
            oe = "—（重い）" if r["heavy"] else f"{r['open_pct']:.1f}"
            print(f"{name:22}{r['mb']:7.1f}{r['tris']:10,d}{oe:>10}"
                  f"{('○' if r['emissive'] else '×'):>5}{('○' if (r['morph'] or r['anim']) else '×'):>5}  {mark}")
        return

    if not a:
        print("usage: model.py <model.glb> | --all"); sys.exit(2)
    r = analyse(a[0])
    if not r:
        print("🔴 GLBとして読めない"); sys.exit(2)
    print("── モデル（PITFALLS #60）")
    print(f"   容量 {r['mb']:.1f}MB   三角形 {r['tris']:,}   マテリアル {r['mats']}")
    print(f"   開いた辺 {'—（三角形が多すぎるので未検査）' if r['heavy'] else '%.1f%%' % r['open_pct']}")
    print(f"   発光 {'○' if r['emissive'] else '×'}   "
          f"動き {'morph' if r['morph'] else ''}{'/anim' if r['anim'] else ''}{'×' if not (r['morph'] or r['anim']) else ''}")
    print(f"   寸法 {r['size'][0]} × {r['size'][1]} × {r['size'][2]}")
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
