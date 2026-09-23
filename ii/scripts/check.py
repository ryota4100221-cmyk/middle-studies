#!/usr/bin/env python3
# =============================================================
# MIDDLE STUDIES II — 出す前の機械点検（2026-09-23 新設）
#
#   python3 ii/scripts/check.py hero    <hero.png>              # 露出（白飛び・黒つぶれ）とコントラスト
#   python3 ii/scripts/check.py variety <hero.png> [--id NNN]   # 直近6作との画像距離
#   python3 ii/scripts/check.py look    <look.json> [--id NNN]  # 直近3作とルックの軸が重なっていないか
#   python3 ii/scripts/check.py motion  <loop.mp4>              # 動き量・ループの閉じ・静止率（〜005）
#   python3 ii/scripts/check.py film    <loop.mp4> [hero.png]   # 尺・カット数・止まったカット・決めの構図（006〜）
#   python3 ii/scripts/check.py glb     <model.glb>             # 容量・動き・三角形数
#   python3 ii/scripts/check.py review  <作品フォルダ>            # 自己レビューの周回・testhero・拡大での確認
#   python3 ii/scripts/check.py compose <hero.png> <mask.png>    # 四辺の余白と輪郭の分離（mask は ii/scripts/mask.py）
#   python3 ii/scripts/check.py elapsed <作品フォルダ>            # 開始からの経過分（🔴 自分で数えない）
#   python3 ii/scripts/check.py all     <作品フォルダ>            # 上を全部（公開前に必ずこれを通す）
#   python3 ii/scripts/check.py trend                           # 直近の作品の🔴だけを出す（作品ダイジェストが読む）
#
# 🔴 なぜ在るか：第1期（MIDDLE STUDIES 001〜089）は「ライムが光に見えるか」を測る道具
#    （scripts/measure.py）しか持っていなかった。第2期は色も舞台も毎回変わるので、それは使えない。
#    代わりに**どんな見た目でも成り立つもの**だけを測る＝露出・違い・動き・容量・周回数。
#    良し悪しの審美は測らない（それは基準の作品と並べて目で見る＝SKILL.md 工程4）。
#
# 🔴 数字を添えないガードは静かにオフになる。🔴 が0件でも必ず件数を出す。
# 終了コード：🔴 が1件でもあれば 1。
# =============================================================
import sys, os, json, glob, subprocess, tempfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
II = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.normpath(os.path.join(II, "..", "scripts")))

from PIL import Image  # noqa: E402

WORKS_JSON = os.path.join(II, "works.json")
WORKS_DIR = os.path.join(II, "works")

# --- 帯 ---
# 画像距離は 3d-daily の variety-check と同じ式・同じ閾値（Day001〜048で較正済み）。
# 第2期の実測が10作たまったら、ここを実測で引き直す（→ SKILL.md「帯の引き直し」）。
DIST_FAIL = 0.06       # これ未満は同じ絵 → 🔴
DIST_JUSTIFY = 0.14    # 0.06〜0.14 は works.json の `sameish` に理由が要る（無ければ🔴）
VARIETY_N = 6
# ルックの軸。直近3作のどれかと LOOK_FAIL 軸以上が一致したら🔴（色だけ変えて同じ絵、を止める）
LOOK_AXES = ["track", "palette_family", "background", "lighting", "lens", "aspect", "material"]
LOOK_FAIL = 5
LOOK_N = 3
# 露出（被写体ではなく画面全体で見る。意図した白地・黒地は works.json の look.background で分かる）
CLIP_HI = 2.0          # %。RGB全チャンネル254以上の画素。これを超えたら白飛び
CRUSH_HI = 25.0        # %。輝度3以下の画素。黒地の作品でも25%を超えたら被写体が沈んでいる疑い
CONTRAST_LO = 0.10     # 輝度の標準偏差/255。これ未満は眠い（全面グレー）
# 動き（第1期 motion.py の基準期001〜030の帯を流用。ライムに依存する「光の振れ」だけ外した）
MOTION_MIN = 0.62
CLOSE_MAX = 2.2
STILL_MAX = 0.20
N_FRAMES = 24
# プロダクトフィルム（2026-09-23〜・006から）
FILM_SEC = (9.5, 13.0)    # 尺
FILM_SHOTS = (3, 6)       # カット数
SHOT_MIN_SEC = 1.5        # 1カットの最短
CUT_RATIO, CUT_ABS = 4.0, 8.0   # 隣のフレームとの差が「全体の中央値×4」かつ8以上ならカット
HERO_MATCH = 0.08         # 最終フレームと hero.png の画像距離。これを超えたら「決めの構図で終わっていない」
# glb
SIZE_HI = 8.0          # MB
# 構図（2026-09-23 追加・試作3本で較正）
MARGIN_MIN = 3.0       # %。被写体の外接枠と画面の辺の距離。0.3%未満は「切っている」＝意図した寄りとみなし判定しない
SEP_DL = 8             # 輪郭の内側と外側の色差 ΔE76（Lab）。これ未満の区間は「地に溶けている」＝試作5本で較正
SEP_MERGE_MAX = 0.50   # 1辺のうち溶けている区間の割合の上限
RING_GAP = 4           # 輪郭から帯までの隙間（px・長辺2560換算）
RING = 16              # 帯の外端（px・長辺2560換算）
# 時間
TIME_LIMIT_MIN = 180   # 開始から3時間（SKILL.md 工程4 (b)）
# 自己レビュー
REVIEW_MIN = 6          # 2026-09-23 3→6（II 001 は1周20秒で、6周が27分で終わった＝3周は歯止めにならない）
TESTHERO_MIN = 2        # 長辺1600で細部を見た周
RULES_V2_FROM = "002"
RULES_V3_FROM = "004"
RULES_FILM_FROM = "006"  # 動画をプロダクトフィルム（10〜12秒・3〜4カット）にしたのは 006 から   # 構図（mask.png）と時間の点検は 004 から（001〜003 は試作。遡って🔴にしない）   # 上の2つと「拡大:」は 002 から（001 は旧規則の3周で作って公開済み。遡って🔴にするとダイジェストが毎日鳴る）


def load_works():
    try:
        return json.load(open(WORKS_JSON))
    except Exception:
        return []


def work_dir(w):
    return os.path.join(WORKS_DIR, f"{w['id']}_{w['slug']}")


def prior_works(wid, n):
    """wid より前の作品を新しい順に n 件。wid が None なら全体の末尾 n 件。"""
    ws = load_works()
    if wid:
        ws = [w for w in ws if w["id"] < wid]
    return list(reversed(ws))[:n]


# ---------------------------------------------------------------- hero
def luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def hero(path):
    ng, lines = [], []
    im = Image.open(path).convert("RGB")
    w, h = im.size
    sm = im.resize((min(w, 800), int(h * min(w, 800) / w)))
    px = list(sm.getdata())
    n = len(px)
    clip = sum(1 for r, g, b in px if r >= 254 and g >= 254 and b >= 254) / n * 100
    lum = [luma(*p) for p in px]
    crush = sum(1 for l in lum if l <= 3) / n * 100
    mean = sum(lum) / n
    std = (sum((l - mean) ** 2 for l in lum) / n) ** 0.5 / 255
    lines.append(f"  hero {w}×{h}  白飛び {clip:.2f}%  黒つぶれ {crush:.1f}%  平均輝度 {mean:.0f}  コントラスト {std:.3f}")
    if max(w, h) < 2400:
        ng.append(f"hero の長辺 {max(w, h)}px（2400未満＝第2期の納品寸法に届いていない）")
    if clip > CLIP_HI:
        ng.append(f"白飛び {clip:.2f}%（>{CLIP_HI}%）")
    if crush > CRUSH_HI:
        ng.append(f"黒つぶれ {crush:.1f}%（>{CRUSH_HI}%）")
    if std < CONTRAST_LO:
        ng.append(f"コントラスト {std:.3f}（<{CONTRAST_LO}＝眠い）")
    return ng, lines


# ---------------------------------------------------------------- variety
def signature(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((400, 400))
    w, h = im.size
    px = im.load()
    G = 8
    cell = [0.0] * (G * G * 3)
    cnt = [0] * (G * G)
    hist = [0.0] * 16
    for y in range(h):
        gy = min(G - 1, y * G // h)
        for x in range(w):
            gx = min(G - 1, x * G // w)
            r, g, b = px[x, y]
            c = (gy * G + gx) * 3
            cell[c] += r; cell[c + 1] += g; cell[c + 2] += b
            cnt[gy * G + gx] += 1
            hist[min(15, int(luma(r, g, b) / 16))] += 1
    for i in range(G * G):
        k = cnt[i] or 1
        for j in range(3):
            cell[i * 3 + j] /= k * 255
    tot = w * h
    hist = [v / tot for v in hist]
    return cell, hist


def distance(a, b):
    dc = sum(abs(x - y) for x, y in zip(a[0], b[0])) / len(a[0])
    dh = sum(abs(x - y) for x, y in zip(a[1], b[1])) / 2
    return 0.5 * dc + 0.5 * dh


def variety(path, wid=None):
    ng, lines = [], []
    me = signature(path)
    prev = prior_works(wid, VARIETY_N)
    if not prev:
        lines.append("  画像距離: 比較対象なし（第2期の1作目）")
        return ng, lines
    sameish = {}
    for w in load_works():
        if w["id"] == wid and w.get("sameish"):
            sameish = w["sameish"] if isinstance(w["sameish"], dict) else {"*": w["sameish"]}
    ds = []
    for w in prev:
        p = os.path.join(work_dir(w), "hero.png")
        if not os.path.exists(p):
            continue
        d = distance(me, signature(p))
        ds.append((w["id"], d))
        if d < DIST_FAIL:
            ng.append(f"{w['id']} との画像距離 {d:.3f}（<{DIST_FAIL}＝同じ絵）")
        elif d < DIST_JUSTIFY and not (sameish.get(w["id"]) or sameish.get("*")):
            ng.append(f"{w['id']} との画像距離 {d:.3f}（{DIST_FAIL}〜{DIST_JUSTIFY}：works.json の sameish に理由が要る）")
    lines.append("  画像距離: " + "  ".join(f"{i} {d:.3f}" for i, d in ds))
    return ng, lines


# ---------------------------------------------------------------- look
def look(src, wid=None):
    ng, lines = [], []
    lk = json.load(open(src)) if isinstance(src, str) else src
    lk = lk.get("look", lk)
    missing = [a for a in LOOK_AXES if not lk.get(a)]
    if missing:
        ng.append("look に空の軸: " + ", ".join(missing))
    for w in prior_works(wid, LOOK_N):
        o = w.get("look", {})
        same = [a for a in LOOK_AXES if lk.get(a) and lk.get(a) == o.get(a)]
        lines.append(f"  ルック vs {w['id']}: 一致 {len(same)}/{len(LOOK_AXES)} {same}")
        if len(same) >= LOOK_FAIL:
            ng.append(f"{w['id']} とルックが {len(same)} 軸一致（≥{LOOK_FAIL}）：{same}")
    # 交互の規則（OBJECT → FORM → OBJECT …）
    prev = prior_works(wid, 1)
    if prev and lk.get("track") and prev[0].get("look", {}).get("track") == lk.get("track"):
        ng.append(f"track が前作と同じ {lk.get('track')}（OBJECT と FORM を交互に出す）")
    if not lines:
        lines.append("  ルック: 比較対象なし")
    return ng, lines


# ---------------------------------------------------------------- motion
def frames(path, n=N_FRAMES):
    tmp = tempfile.mkdtemp()
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=nb_frames,duration",
                        "-of", "json", path], capture_output=True, text=True)
    st = json.loads(r.stdout or "{}").get("streams", [{}])[0]
    nb = int(st.get("nb_frames", 0) or 0)
    dur = float(st.get("duration", 0) or 0)
    if nb < 2 or dur <= 0:
        return nb, dur, []
    fps = nb / dur
    subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={n / dur:.6f},scale=180:-2",
                    os.path.join(tmp, "f%03d.png")], capture_output=True)
    fs = sorted(glob.glob(os.path.join(tmp, "f*.png")))
    # 最終フレームを別に抜く（ループの閉じを見るため）
    last = os.path.join(tmp, "last.png")
    subprocess.run(["ffmpeg", "-v", "error", "-sseof", f"-{1.5 / fps:.4f}", "-i", path,
                    "-frames:v", "1", "-vf", "scale=180:-2", last], capture_output=True)
    ims = [Image.open(f).convert("L") for f in fs]
    if os.path.exists(last):
        ims.append(Image.open(last).convert("L"))
    return nb, dur, ims


def diff(a, b):
    pa, pb = list(a.getdata()), list(b.getdata())
    return sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)


def motion(path):
    ng, lines = [], []
    nb, dur, ims = frames(path)
    if len(ims) < 4:
        ng.append(f"loop.mp4 が読めない（nb_frames={nb}）")
        return ng, lines
    seq, last = ims[:-1], ims[-1]
    ds = [diff(seq[i], seq[i + 1]) for i in range(len(seq) - 1)]
    med = sorted(ds)[len(ds) // 2]
    around = (ds[0] + ds[-1]) / 2 or 1e-6
    close = diff(last, seq[0]) / around
    still = sum(1 for d in ds if d < med * 0.2) / len(ds)
    lines.append(f"  loop {nb}f/{dur:.1f}s  動き量 {med:.2f}  閉じ {close:.2f}  静止率 {still * 100:.0f}%")
    if dur < 5.0 or dur > 8.5:
        ng.append(f"尺 {dur:.1f}s（5〜8秒）")
    if med < MOTION_MIN:
        ng.append(f"動き量 {med:.2f}（<{MOTION_MIN}＝ほぼ動いていない）")
    if close > CLOSE_MAX:
        ng.append(f"ループの閉じ {close:.2f}（>{CLOSE_MAX}＝継ぎ目で飛ぶ）")
    if still > STILL_MAX:
        ng.append(f"静止率 {still * 100:.0f}%（>{STILL_MAX * 100:.0f}%）")
    return ng, lines


def film(path, hero_path=None):
    """プロダクトフィルムの点検：尺・カット数・止まったカット・決めの構図（006〜）"""
    ng, lines = [], []
    tmp = tempfile.mkdtemp()
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=nb_frames,duration",
                        "-of", "json", path], capture_output=True, text=True)
    st = json.loads(r.stdout or "{}").get("streams", [{}])[0]
    nb, dur = int(st.get("nb_frames", 0) or 0), float(st.get("duration", 0) or 0)
    if nb < 24:
        return [f"loop.mp4 が読めない（nb_frames={nb}）"], lines
    subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=180:-2", os.path.join(tmp, "f%04d.png")],
                   capture_output=True)
    fs = sorted(glob.glob(os.path.join(tmp, "f*.png")))
    ims = [Image.open(f).convert("L") for f in fs]
    ds = [diff(ims[i], ims[i + 1]) for i in range(len(ims) - 1)]
    med = sorted(ds)[len(ds) // 2] or 1e-6
    cuts = [i + 1 for i, d in enumerate(ds) if d > max(CUT_ABS, med * CUT_RATIO)]
    bounds = [0] + cuts + [len(ims)]
    shots = [(bounds[k], bounds[k + 1]) for k in range(len(bounds) - 1)]
    fps = nb / dur if dur else 24
    lines.append(f"  film {nb}f/{dur:.1f}s  カット {len(shots)}  "
                 + "  ".join(f"#{k + 1} {(b - a) / fps:.1f}s" for k, (a, b) in enumerate(shots)))
    if not (FILM_SEC[0] <= dur <= FILM_SEC[1]):
        ng.append(f"尺 {dur:.1f}s（{FILM_SEC[0]}〜{FILM_SEC[1]}秒）")
    if not (FILM_SHOTS[0] <= len(shots) <= FILM_SHOTS[1]):
        ng.append(f"カット {len(shots)}（{FILM_SHOTS[0]}〜{FILM_SHOTS[1]}）")
    for k, (a, b) in enumerate(shots):
        if (b - a) / fps < SHOT_MIN_SEC:
            ng.append(f"カット{k + 1} が {(b - a) / fps:.1f}秒（<{SHOT_MIN_SEC}秒＝一瞬で読めない）")
        inner = ds[a:max(a, b - 1)]
        if k < len(shots) - 1:
            mv = max(inner) if inner else 0
        else:   # 決めのカットは最後に止まってよい。前半で動いていればよい
            mv = max(inner[:max(1, len(inner) // 2)]) if inner else 0
        if mv < MOTION_MIN:
            ng.append(f"カット{k + 1} が止まっている（動きの最大 {mv:.2f}<{MOTION_MIN}）")
    if hero_path and os.path.exists(hero_path):
        dh = distance(signature(fs[-1]), signature(hero_path))
        lines.append(f"  最終フレームと hero の距離 {dh:.3f}")
        if dh > HERO_MATCH:
            ng.append(f"最後が hero の構図で終わっていない（距離 {dh:.3f}>{HERO_MATCH}）")
    return ng, lines


# ---------------------------------------------------------------- glb
def glb(path):
    from model import read_glb  # 第1期の読み取り器をそのまま使う
    ng, lines = [], []
    js, _ = read_glb(path)
    if not js:
        return [f"glb が読めない: {path}"], lines
    mb = os.path.getsize(path) / 1048576
    anim = bool(js.get("animations")) or any("targets" in p for m in js.get("meshes", []) for p in m.get("primitives", []))
    lines.append(f"  glb {mb:.1f}MB  動き {'あり' if anim else 'なし'}  マテリアル {len(js.get('materials', []))}")
    if mb > SIZE_HI:
        ng.append(f"glb {mb:.1f}MB（>{SIZE_HI}MB）")
    if not anim:
        ng.append("glb に動きが乗っていない")
    return ng, lines


# ---------------------------------------------------------------- compose
def _lab(rgb):
    """sRGB(0-255) → CIE Lab（D65）"""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)

def compose(hero_path, mask_path, note=None):
    """被写体マスク（ii/scripts/mask.py）から、四辺の余白と輪郭の分離を測る。
    note＝works.json の compose_note（{"上": "理由"} など）。理由のある辺は🔴にしない
    （透明素材・意図して沈めた脇役など。sameish と同じく「必ず分離させろ」の片側ゲートにしない）。"""
    note = note or {}
    from PIL import ImageFilter, ImageChops
    ng, lines = [], []
    if not os.path.exists(mask_path):
        return [f"mask.png が無い（Blender で ii/scripts/mask.py を回していない）"], lines
    hero_im = Image.open(hero_path).convert("RGB")
    m = Image.open(mask_path).getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    if m.size != hero_im.size:
        # 🔴 手順どおり testhero（長辺1600）に対して回すと、mask（長辺2560）と寸法が必ず違う（2026-09-23 004で発覚）。
        #    縦横比が同じなら mask を合わせる。違うなら判型を変えた後の古い mask なので描き直させる
        if abs(m.size[0] / m.size[1] - hero_im.size[0] / hero_im.size[1]) > 0.01:
            return [f"mask {m.size} と hero {hero_im.size} の縦横比が違う（判型を変えたなら mask を描き直す）"], lines
        m = m.resize(hero_im.size, Image.BILINEAR).point(lambda v: 255 if v >= 128 else 0)
    W, H = m.size
    bb = m.getbbox()
    if not bb:
        return ["mask が空（parts が画面に写っていない）"], lines
    x0, y0, x1, y1 = bb
    mg = {"上": y0 / H * 100, "下": (H - y1) / H * 100, "左": x0 / W * 100, "右": (W - x1) / W * 100}
    lines.append("  余白 " + "  ".join(f"{k} {v:.1f}%" for k, v in mg.items()))
    for k, v in mg.items():
        if 0.3 <= v < MARGIN_MIN and not note.get(k):
            ng.append(f"{k}の余白 {v:.1f}%（<{MARGIN_MIN}%＝辺に寄りすぎて窮屈。切るなら切る、空けるなら空ける）")
    # 輪郭の帯：境目から GAP〜RING だけ離した内側・外側の帯（長辺2560換算）。
    # 🔴 境目に接した帯で測ると、縮小とボケで両側の画素が混ざり明暗差が消える（較正時に001で誤検知した）
    sc = 1280 / max(W, H)
    size = (max(1, round(W * sc)), max(1, round(H * sc)))
    ms = m.resize(size, Image.BILINEAR).point(lambda v: 255 if v >= 128 else 0)
    g_ = max(1, round(RING_GAP * 1280 / 2560)); r_ = max(g_ + 1, round(RING * 1280 / 2560))
    er = lambda im, n: im.filter(ImageFilter.MinFilter(2 * n + 1))
    di = lambda im, n: im.filter(ImageFilter.MaxFilter(2 * n + 1))
    inner = ImageChops.subtract(er(ms, g_), er(ms, r_))
    outer = ImageChops.subtract(di(ms, r_), di(ms, g_))
    L = hero_im.resize(size, Image.BOX).load()   # RGB
    I, O = inner.load(), outer.load()
    cx, cy = (x0 + x1) / 2 * sc, (y0 + y1) / 2 * sc
    hw, hh = max(1, (x1 - x0) / 2 * sc), max(1, (y1 - y0) / 2 * sc)
    SEG = 8
    acc = {s: [[[0, 0, 0], 0, [0, 0, 0], 0] for _ in range(SEG)] for s in ("上", "下", "左", "右")}  # [RGBin, nin, RGBout, nout]
    for y in range(size[1]):
        for x in range(size[0]):
            wi, wo = I[x, y] / 255, O[x, y] / 255
            if not wi and not wo:
                continue
            dx, dy = (x - cx) / hw, (y - cy) / hh
            if abs(dx) >= abs(dy):
                side, t = ("右" if dx > 0 else "左"), (dy + 1) / 2
            else:
                side, t = ("下" if dy > 0 else "上"), (dx + 1) / 2
            seg = min(SEG - 1, max(0, int(t * SEG)))
            a = acc[side][seg]
            if wi >= 0.2:
                px_ = L[x, y]
                for c in range(3):
                    a[0][c] += px_[c] * wi
                a[1] += wi
            if wo >= 0.2:
                px_ = L[x, y]
                for c in range(3):
                    a[2][c] += px_[c] * wo
                a[3] += wo
    for side in ("上", "下", "左", "右"):
        if mg[side] < 0.3:
            lines.append(f"  輪郭 {side}: 画面の辺で切っている（判定しない）")
            continue
        # 🔴 明るさの差ではなく Lab の色差（ΔE76）で見る（2026-09-23 005：パステルのマグと明るい天板は
        #    明るさが近いが色相で分かれて読める。明るさだけでは「溶けている」と誤判定した）
        dls = []
        for a in acc[side]:
            if a[1] > 0.5 and a[3] > 0.5:
                li = _lab([v / a[1] for v in a[0]]); lo = _lab([v / a[3] for v in a[2]])
                dls.append(sum((p - q) ** 2 for p, q in zip(li, lo)) ** 0.5)
        if not dls:
            continue
        merged = sum(1 for d in dls if d < SEP_DL) / len(dls)
        lines.append(f"  輪郭 {side}: 色差ΔE 中央 {sorted(dls)[len(dls) // 2]:.0f}  溶けた区間 {merged * 100:.0f}%")
        if merged > SEP_MERGE_MAX and note.get(side):
            lines.append(f"    └ 理由あり（compose_note）：{note[side]}")
        elif merged > SEP_MERGE_MAX:
            ng.append(f"輪郭の{side}辺が地に溶けている（{merged * 100:.0f}%の区間で色差ΔE<{SEP_DL}）＝被写体がどこまでか読めない")
    return ng, lines


# ---------------------------------------------------------------- elapsed
def started_at(d):
    """REVIEW.md の `開始: HH:MM` と作品の日付から開始時刻（JST）を返す。"""
    import datetime as dt
    p = os.path.join(d, "REVIEW.md")
    if not os.path.exists(p):
        return None
    m = re.search(r"^開始[:：]\s*(\d{1,2}):(\d{2})", open(p, encoding="utf-8").read(), re.M)
    if not m:
        return None
    jst = dt.timezone(dt.timedelta(hours=9))
    base = dt.datetime.fromtimestamp(os.path.getctime(p), jst)
    st = base.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
    if st > base:            # 日付をまたいだ（23:50 開始 → 00:10 作成 など）
        st -= dt.timedelta(days=1)
    return st


def elapsed(d):
    """🔴 経過時間は自分で数えない。これで測る（II 003 が54分を「約2時間」と書いた）。"""
    import datetime as dt
    st = started_at(d)
    if not st:
        return ["REVIEW.md に `開始: HH:MM` が無い"], []
    now = dt.datetime.now(st.tzinfo)
    mins = (now - st).total_seconds() / 60
    left = TIME_LIMIT_MIN - mins
    return [], [f"  開始 {st:%H:%M}  経過 {mins:.0f}分  3時間の枠まで残り {left:.0f}分" + ("（枠を過ぎた＝工程4 (b)）" if left <= 0 else "")]


# ---------------------------------------------------------------- review
def review(d):
    ng, lines = [], []
    p = os.path.join(d, "REVIEW.md")
    if not os.path.exists(p):
        return ["REVIEW.md が無い（自己レビューの記録が無い）"], lines
    txt = open(p, encoding="utf-8").read()
    rounds = re.findall(r"^##\s*round\s*(\d+)", txt, re.M | re.I)
    has_ref = bool(re.search(r"^基準[:：]\s*\S+", txt, re.M))
    heads = re.findall(r"^##\s*round\s*\d+.*$", txt, re.M | re.I)
    hero_rounds = sum(1 for h in heads if "testhero" in h.lower())
    crop_lines = len(re.findall(r"^拡大[:：]", txt, re.M))
    lines.append(f"  自己レビュー {len(rounds)}周（うちtesthero {hero_rounds}周）  拡大での確認 {crop_lines}件  基準の記載 {'あり' if has_ref else 'なし'}")
    wid = os.path.basename(os.path.abspath(d)).split("_")[0]
    if wid < RULES_V2_FROM:
        if len(rounds) < 3:
            ng.append(f"自己レビュー {len(rounds)}周（<3・旧規則）")
        if not has_ref:
            ng.append("REVIEW.md に「基準: <URL>」の行が無い")
        return ng, lines
    if len(rounds) < REVIEW_MIN:
        ng.append(f"自己レビュー {len(rounds)}周（<{REVIEW_MIN}）")
    if hero_rounds < TESTHERO_MIN:
        ng.append(f"testhero の周 {hero_rounds}（<{TESTHERO_MIN}）＝細部を見ずに止めている")
    if heads and "testhero" not in heads[-1].lower():
        ng.append("最後の周が testhero ではない（最終判定は長辺1600で見る）")
    # 時間切れの申告が本当か（REVIEW.md を最後に書いた時刻で測る）
    st = started_at(d)
    if st:
        import datetime as dt
        last = dt.datetime.fromtimestamp(os.path.getmtime(p), st.tzinfo)
        mins = (last - st).total_seconds() / 60
        lines.append(f"  レビューにかけた時間 {mins:.0f}分（開始 {st:%H:%M} → 最終記入 {last:%H:%M}）")
        if re.search(r"時間切れ", txt) and mins < TIME_LIMIT_MIN - 10:
            ng.append(f"「時間切れ」と書いているが、実際は {mins:.0f}分（3時間に届いていない）＝経過時間を数え違えて早く止めた")
    elif wid >= RULES_V3_FROM:
        ng.append("REVIEW.md に `開始: HH:MM` が無い")
    film_rounds = len(re.findall(r"^##\s*film\s*round\s*\d+", txt, re.M | re.I))
    if wid >= RULES_FILM_FROM:
        lines.append(f"  動画のレビュー {film_rounds}周")
        if film_rounds < 2:
            ng.append(f"動画のレビュー（## film round）{film_rounds}周（<2）＝カットを並べて見ていない")
        # 🔴 最後の動画レビューに「直すこと」が残っていたら、直した画を誰も見ていない（2026-09-23 006：
        #    film round 2 で2カット目の向きを直したが、描き直さずに anim へ進んだ）。確かめる周を1つ挟ませる
        last_film = re.split(r"^##\s*film\s*round\s*\d+.*$", txt, flags=re.M | re.I)[-1] if film_rounds else ""
        last_film = re.split(r"^##\s", last_film, flags=re.M)[0]
        if film_rounds and re.search(r"直すこと[:：]", last_film) and wid > "006":
            ng.append("最後の動画レビューに「直すこと」が残っている＝直したカットを描き直して見ていない（もう1周 shots→contact を回す）")
    if crop_lines < 2:
        ng.append(f"「拡大:」の行が {crop_lines} 件（<2）＝見劣りしないと書いた箇所を拡大して確かめていない")
    if not has_ref:
        ng.append("REVIEW.md に「基準: <URL>」の行が無い（何と並べて判定したか分からない）")
    return ng, lines


# ---------------------------------------------------------------- all / trend
def all_checks(d):
    d = os.path.abspath(d)
    wid = os.path.basename(d).split("_")[0]
    me = next((w for w in load_works() if w["id"] == wid), None)
    ng, lines = [], []
    def run(fn, *a):
        n, l = fn(*a); ng.extend(n); lines.extend(l)
    for f, fn in (("hero.png", hero), ("loop.mp4", motion), ("model.glb", glb)):
        p = os.path.join(d, f)
        if not os.path.exists(p):
            ng.append(f"{f} が無い")
        elif f == "loop.mp4" and (wid >= RULES_FILM_FROM or (me or {}).get("film")):   # 001〜005 は作り直した後（works.json に film がある）
            run(film, p, os.path.join(d, "hero.png"))
        else:
            run(fn, p)
    if os.path.exists(os.path.join(d, "hero.png")):
        run(variety, os.path.join(d, "hero.png"), wid)
    if me:
        run(look, me, wid)
    else:
        ng.append(f"works.json に {wid} の行が無い（look を照合できない）")
    run(review, d)
    mp = os.path.join(d, "mask.png")
    if os.path.exists(mp):
        run(compose, os.path.join(d, "hero.png"), mp, (me or {}).get("compose_note"))
    elif wid >= RULES_V3_FROM:
        ng.append("mask.png が無い（Blender --python ii/scripts/mask.py -- script.py mask.png を回していない）")
    return ng, lines


def trend():
    out = []
    for w in list(reversed(load_works()))[:3]:
        d = work_dir(w)
        if not os.path.isdir(d):
            continue
        ng, _ = all_checks(d)
        for n in ng:
            out.append(f"🔴 II {w['id']} {w['title']}: {n}")
    return out


def report(ng, lines, label):
    for l in lines:
        print(l)
    print(f"{label}: 🔴 {len(ng)}件")
    for n in ng:
        print(f"  🔴 {n}")
    return 1 if ng else 0


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__ or open(__file__).read().split("# ===")[1]); return 2
    cmd = a[0]
    wid = a[a.index("--id") + 1] if "--id" in a else None
    if cmd == "trend":
        for l in trend():
            print(l)
        return 0
    fn = {"hero": hero, "motion": motion, "glb": glb, "review": review, "all": all_checks}.get(cmd)
    if fn:
        return report(*fn(a[1]), cmd)
    if cmd == "film":
        return report(*film(a[1], a[2] if len(a) > 2 and not a[2].startswith("--") else None), cmd)
    if cmd == "elapsed":
        return report(*elapsed(a[1]), cmd)
    if cmd == "compose":
        return report(*compose(a[1], a[2]), cmd)
    if cmd == "variety":
        return report(*variety(a[1], wid), cmd)
    if cmd == "look":
        return report(*look(a[1], wid), cmd)
    print(f"unknown: {cmd}"); return 2


if __name__ == "__main__":
    sys.exit(main())
