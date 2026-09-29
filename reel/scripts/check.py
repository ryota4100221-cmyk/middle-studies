#!/usr/bin/python3
"""MIDDLE STUDIES REEL の機械点検。🔴が1件でもあれば公開しない。

  /usr/bin/python3 reel/scripts/check.py <id>        # 公開前（ローカルの作品フォルダ）
  /usr/bin/python3 reel/scripts/check.py <id> live   # 公開後（配信URLが200か）

最後の行に必ず件数を出す（数字を添えないガードは静かにオフになる）：
  CHECK <id>: 🔴0 ⚠️1 ✅14
"""
import json, os, re, subprocess, sys, urllib.request

import numpy as np
from PIL import Image

HOME = os.path.expanduser("~")
REEL = os.path.join(HOME, "projects/middle-studies/reel")
MEDIA = os.path.join(HOME, "projects/middle-studies-reel")
MEDIA_URL = "https://ryota4100221-cmyk.github.io/middle-studies-reel/"
PAGE_URL = "https://middle.lab.monakadesign.com/reel/"
REQUIRED = ["id", "slug", "title", "date", "concept", "video", "techniques", "look", "review_rounds", "review"]

red, warn, ok = [], [], []


def R(m): red.append(m); print("🔴", m)
def Wn(m): warn.append(m); print("⚠️", m)
def O(m): ok.append(m); print("✅", m)


def signature(path):
    """コンタクトシート（15枚）の画像距離用の特徴：8×8平均色＋16bin輝度ヒスト"""
    im = Image.open(path).convert("RGB")
    small = np.asarray(im.resize((40, 24), Image.BILINEAR), dtype=np.float32) / 255
    lum = np.asarray(im.convert("L"), dtype=np.float32) / 255
    hist = np.histogram(lum, bins=16, range=(0, 1))[0].astype(np.float32)
    return small, hist / hist.sum()


def distance(a, b):
    return float(np.abs(a[0] - b[0]).mean() + np.abs(a[1] - b[1]).sum() * 0.5)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    wid, mode = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "local")
    works = json.load(open(os.path.join(REEL, "works.json")))
    idx = next((i for i, w in enumerate(works) if w.get("id") == wid), None)
    if idx is None:
        R(f"works.json に id {wid} が無い"); return finish(wid)
    w = works[idx]
    d = os.path.join(REEL, "works", f"{w['id']}_{w['slug']}")
    name = f"{w['id']}_{w['slug']}.mp4"

    if mode == "live":
        for url in (MEDIA_URL + name, PAGE_URL, PAGE_URL + "works.json",
                    PAGE_URL + f"works/{w['id']}_{w['slug']}/poster.jpg"):
            try:
                code = urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20).status
            except Exception as e:
                code = getattr(e, "code", str(e))
            (O if code == 200 else R)(f"live {code} {url}")
        return finish(wid)

    # --- works.json の記入 ---
    miss = [k for k in REQUIRED if not w.get(k)]
    (R if miss else O)(f"works.json 必須項目 {'欠け: ' + ', '.join(miss) if miss else 'そろっている'}")
    if w.get("video") != MEDIA_URL + name:
        R(f"video のURLが配信先と違う（{w.get('video')} ≠ {MEDIA_URL + name}）")
    if not re.fullmatch(r"\d{3}", w["id"]) or int(w["id"]) != idx + 1:
        R(f"id が連番でない（{w['id']} / {idx + 1}番目）")
    if (w.get("review_rounds") or 0) < 3:
        R(f"自己レビューが {w.get('review_rounds')} 周（最低3周）")
    else:
        O(f"自己レビュー {w['review_rounds']} 周")

    # --- ファイル ---
    missing = [f for f in ("source.html", "reel.mp4", "poster.jpg", "contact.jpg") if not os.path.exists(os.path.join(d, f))]
    (R if missing else O)(f"ファイル {'欠け: ' + ', '.join(missing) if missing else '4点そろっている'}")
    if missing:
        return finish(wid)

    # --- 決定論（同じ t で同じ絵） ---
    src = open(os.path.join(d, "source.html"), encoding="utf-8").read()
    if "Math.random(" in src:
        R("source.html が Math.random() を使っている（撮るたびに絵が変わる）。シード付きPRNGにする")
    if not re.search(r"__seek", src) or not re.search(r"__duration", src):
        R("__seek / __duration が無い")
    for m in re.finditer(r"(Date\.now|new Date\()", src):
        Wn("source.html が Date を使っている（時刻依存の絵になっていないか確認）"); break

    # --- 書き出しの仕様 ---
    mp4 = os.path.join(d, "reel.mp4")
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                    "stream=width,height,r_frame_rate,nb_frames:format=duration,size",
                                    "-of", "json", mp4], capture_output=True, text=True).stdout)
    s, fmt = pr["streams"][0], pr["format"]
    spec = (s["width"], s["height"], s["r_frame_rate"], int(s["nb_frames"]))
    (O if spec == (1920, 1080, "60/1", 900) else R)(f"仕様 {spec[0]}×{spec[1]} {spec[2]} {spec[3]}f（要 1920×1080 60/1 900f）")
    dur = float(fmt["duration"])
    (O if abs(dur - 15) < 0.03 else R)(f"尺 {dur:.3f}s")
    mb = int(fmt["size"]) / 1e6
    (O if mb <= 8 else R)(f"容量 {mb:.2f}MB（上限8MB）")

    # --- 止まっている／真っ黒な区間 ---
    log = subprocess.run(["ffmpeg", "-v", "info", "-i", mp4, "-vf",
                          "freezedetect=n=0.0008:d=1.2,blackdetect=d=1.0:pix_th=0.06",
                          "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    fr = re.findall(r"freeze_duration: ([\d.]+)", log)
    bl = re.findall(r"black_duration:([\d.]+)", log)
    longest = max([float(x) for x in fr] or [0])
    (R if longest >= 1.2 else O)(f"静止区間 最長 {longest:.2f}s（1.2s以上は🔴＝15秒のリールで1秒以上止めない）")
    (R if bl else O)(f"真っ黒な区間 {len(bl)}件" + (f"（{', '.join(bl)}s）" if bl else ""))

    # --- 前の作品と違うか（変化ゲート） ---
    me = signature(os.path.join(d, "contact.jpg"))
    prev = works[max(0, idx - 7):idx]
    dists = []
    for p in prev:
        c = os.path.join(REEL, "works", f"{p['id']}_{p['slug']}", "contact.jpg")
        if os.path.exists(c):
            dists.append((distance(me, signature(c)), p["id"]))
    if dists:
        dmin, pid = min(dists)
        if dmin < 0.06:
            R(f"画像距離 {dmin:.3f}（vs {pid}）＝ほぼ同じ絵。0.06未満は🔴")
        elif dmin < 0.14 and not w.get("sameish"):
            R(f"画像距離 {dmin:.3f}（vs {pid}）＝近い。works.json に sameish（近くても出す理由）を書けば通す")
        else:
            O(f"画像距離 最小 {dmin:.3f}（vs {pid}・直近{len(dists)}本）")
        mine = set(w.get("techniques", []))
        for p in prev:
            other = set(p.get("techniques", []))
            if mine and other:
                j = len(mine & other) / len(mine | other)
                if j >= 0.6 and not w.get("sameish"):
                    R(f"techniques が {p['id']} と {j:.0%} 重複（60%以上は🔴・sameish で理由を書けば通す）")
        pal = [p.get("look", {}).get("palette", []) for p in prev[-3:]]
        if any(sorted(x) == sorted(w.get("look", {}).get("palette", [])) for x in pal):
            R("palette が直近3本のどれかと完全一致")
    else:
        O("変化ゲート：比べる前作なし（1本目）")

    # --- 配信先の容量 ---
    try:
        size = sum(os.path.getsize(os.path.join(MEDIA, f)) for f in os.listdir(MEDIA) if f.endswith(".mp4")) / 1e6
        size += mb if not os.path.exists(os.path.join(MEDIA, name)) else 0
        (R if size > 800 else Wn if size > 600 else O)(f"配信リポの動画 合計 {size:.0f}MB（GitHub Pages 上限1GB・800MB超で🔴）")
    except FileNotFoundError:
        R(f"配信リポ {MEDIA} が無い")
    return finish(wid)


def finish(wid):
    print(f"CHECK {wid}: 🔴{len(red)} ⚠️{len(warn)} ✅{len(ok)}")
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
