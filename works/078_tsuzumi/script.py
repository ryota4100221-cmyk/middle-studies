# =============================================================
# MIDDLE STUDY 078 — TSUZUMI（鼓 / 小鼓 the grip at the waist）
#
#   光の型＝背光（#53：77作で4作＝8型のうち最少）  構図の型＝全身（直近12作に1作も無い）
#   ドメイン＝楽器・能楽／小鼓
#
# 黒い小鼓がひとつ、宙にある。革が二枚、胴がひとつ、それを調緒（しらべお）が締めている。
# 小鼓は左手で調緒を握って音を変える。握れば革が張って高く、ゆるめれば低く。
# **握っているのは胴のまんなか——いちばん細いところだ。**
# 光は鼓の**うしろ**にある。だから黒は縁だけが灯り、
# 握るほど真ん中のくびれは深くなって、**そこからだけ光がこちらへ抜ける。**
# 音は革で鳴る。けれど音を決めているのは、まんなかの手だ。
#
# 🔴 型の組み合わせ（#87①：works.json は成功の台帳であって可否の台帳ではない）
#    背光が潰れた相手は 寄り／群／対／端寄せ（#67⑤・#71①・#72・#74②）。天地は 065 が通した。
#    全身は背光の本来の型（012／035／051）。直近12作（066〜077）は全身が0作なので、
#    **全身へ戻すこと自体が今日の分布では「外し」になる**。
#    halo は △53%（直近5作 19,118）。#51④ の処方＝面で出す・透過させる → 背光。
#
# 🔴 機構＝**締める（横調べを握る）**。
#    縦調べ12本は革の孔（6つずつ・互い違いに30°）から出て、胴の真ん中で横調べに束ねられる。
#    束ねた半径 RP(t) を s(t)=0.5(1−cos2πt) で開閉する（整数周期＝厳密に閉じる）。
#    シルエットの上下には「革の縁→調緒→束」でできた**V字の切れ込み**があり、
#    RP が小さいほど切れ込みが深く＝**真ん中から抜ける光が増える**。
#    調緒はシェイプキー1枚（開＝基底／締＝shime）なので glb に morph target で乗る。
#    ＋ 首振り ψ(t)=ψ0+Δψ·sin2πt・あおり τ(t)=τ0+Δτ·sin2πt（光の振れを機構だけで出す）
#
# 造形＝胴（轆轤）・革2枚（轆轤）・縦調べ12本＋横調べ3巻＋革の表の渡り3本ずつ（掃引）。boolean 不使用。
#    黒の質感は MATERIALS.md の **urushi（漆＝胴と革の縁）** と **nuno（麻の調緒）**
#    ——掟4の例外「実物がそうである場合」（漆の胴に麻の緒）。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
#   （Blender 無しの幾何プローブ: python3 script.py --probe-only）
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 150.0                      # #58③：随伴のライム光源（発光体の外）

# --- 小鼓（実物：革径 約20cm・全長 約25cm・受けの径 約11cm・棹の径 約4cm。比だけ借りる＝#50）---
RH = 0.56              # 革の半径
TH = 0.085             # 革の厚み（鉄輪を包んだ縁）
LD = 1.40              # 全長（革の表→表）
XI = LD / 2 - TH       # 革の裏（胴の受けが当たる面）
RC = 0.300             # 受け（胴の端の椀）の半径
RW = 0.105             # 棹（胴のくびれ）の半径
U_STEM = 0.30          # 棹がまっすぐな区間（胴の半長に対する比）
BEAD_H, BEAD_W = 0.012, 0.035       # 棹の真ん中の小さな節（まんなかを示す唯一の起伏）
RHOLE = 0.47           # 革の孔の半径位置
NHOLE = 6
RCORD = 0.017          # 調緒の太さ
PLY_A, PLY_PITCH = 0.16, 0.085      # 三つ撚りの起伏（黒の肌は実ジオメトリで作る＝#52）
RP_OPEN, RP_TIGHT = 0.32, 0.155     # 横調べで束ねた半径（開／締）。🔴 0.36 は緩めた相で緒がまっすぐ＝「籠」に読めた
PEX_OPEN, PEX_TIGHT = 1.25, 1.70    # 調緒の曲がり（締めるほど束の近くで急に寄る）
WB, NTURN = 0.11, 3                 # 横調べの幅・巻き数

CX, CZ = AIM_X, 2.40                # 全身＝画面の中央（キャプション上端 1.09 と上端 3.71 の中点）
PSI0, DPSI = 22.0, 7.0              # 首振り（度）。+ で左の革の表がこちらを向く
TAU0, DTAU = 6.0, 3.0               # あおり（右が上がる）
STILL_FRAME = 61                    # t=0.5 ＝ いちばん締めた瞬間

# --- 光（鼓のうしろ）。065 TORII の型を引き継ぐ（#76）-------------
Y_GLOW = 1.05          # 鼓の奥（奥の革の背は y≈0.78）
RX, RZ = 1.34, 0.84    # 横長 1.6:1（#76③：円い光は惑星になる）。
                       # 🔴 2周目：0.74 では V字の切れ込みの上の角が灰色のまま＝光が「真ん中の卵」に縮んだ
NRF, NAF = 72, 120
ES_CORE = 7.5
WHITE_FROM, WHITE_TO = 0.80, 0.46
K_ALPHA = 11.0                        # #76①：不透明さを発光の強さから切り離す
HAZE_A1, HAZE_F1 = 0.05, 4.5
HAZE_A2, HAZE_F2 = 0.035, 11.0


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def smooth(e0, e1, x):
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def squeeze(t):
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * t))


def pose(t):
    s2 = math.sin(2.0 * math.pi * t)
    return math.radians(PSI0 + DPSI * s2), math.radians(TAU0 + DTAU * s2)


def frame_axes(psi, tau):
    """鼓の軸（ローカルX）と、それに直交する上（ローカルZ）・奥（ローカルY）"""
    ax = (math.cos(tau) * math.cos(psi), math.cos(tau) * math.sin(psi), math.sin(tau))
    d = ax[2]
    up = (-d * ax[0], -d * ax[1], 1.0 - d * ax[2])
    n = math.sqrt(sum(c * c for c in up))
    up = tuple(c / n for c in up)
    ly = (up[1] * ax[2] - up[2] * ax[1], up[2] * ax[0] - up[0] * ax[2],
          up[0] * ax[1] - up[1] * ax[0])
    return ax, ly, up


def body_r(x):
    """胴の半径。棹（まっすぐ）→ 受け（杯のように開く）。v²(3−2v) で杯の S 字"""
    u = abs(x) / XI
    if u <= U_STEM:
        r = RW
    else:
        v = (u - U_STEM) / (1.0 - U_STEM)
        r = RW + (RC - RW) * v * v * (3.0 - 2.0 * v)
    return r + BEAD_H * math.exp(-(x / BEAD_W) ** 2)


def cord_paths(s):
    """縦調べ12本（左の孔→右の孔）＋横調べの巻き＋革の表の掛け。s=0 開／1 締"""
    rp = RP_OPEN + (RP_TIGHT - RP_OPEN) * s
    pex = PEX_OPEN + (PEX_TIGHT - PEX_OPEN) * s
    NS = 72
    paths = []
    step = 2.0 * math.pi / NHOLE
    for k in range(NHOLE):
        a = k * step + math.pi / 2
        for b in (a + step / 2, a - step / 2):          # 右の孔は ±30° 互い違い
            pts = []
            for i in range(NS + 1):
                w = i / NS
                x = -XI - 0.004 + (2 * XI + 0.008) * w
                r = rp + (RHOLE - rp) * abs(2.0 * w - 1.0) ** pex
                th = a + (b - a) * w
                pts.append((x, r * math.cos(th), r * math.sin(th)))
            paths.append(pts)
    # 横調べ：束の外を NTURN 巻き（螺旋）
    rb = rp + 1.9 * RCORD
    NSB = 60 * NTURN
    pts = []
    for i in range(NSB + 1):
        w = i / NSB
        th = 2.0 * math.pi * NTURN * w + 0.4
        pts.append((-WB / 2 + WB * w, rb * math.cos(th), rb * math.sin(th)))
    paths.append(pts)
    # 革の表の渡り：孔から表へ出た緒は、隣の孔へ**まっすぐ**渡って裏へ戻る（1枚に3本）。締めても動かない
    # 🔴 2周目：孔ごとの小さな掛け（弧 0.17rad）は遠目に「棘／鋲」に読めた。渡りは弦で張る
    for sgn, x_out in ((-1.0, -LD / 2), (1.0, LD / 2)):
        off = 0.0 if sgn < 0 else step / 2
        for k in range(0, NHOLE, 2):
            a0 = k * step + math.pi / 2 + off
            a1 = a0 + step
            p0 = (RHOLE * math.cos(a0), RHOLE * math.sin(a0))
            p1 = (RHOLE * math.cos(a1), RHOLE * math.sin(a1))
            pts = []
            for i in range(25):
                w = i / 24
                lift = smooth(0.0, 0.10, w) * smooth(0.0, 0.10, 1.0 - w)
                x = x_out - sgn * 0.02 + sgn * (0.02 + 0.85 * RCORD) * lift
                pts.append((x, p0[0] + (p1[0] - p0[0]) * w, p0[1] + (p1[1] - p0[1]) * w))
            paths.append(pts)
    return paths


# --- 幾何プローブ（#40⑥ を幾何で積分する。Blender を起動しない）---------
def to_world(p, t):
    psi, tau = pose(t)
    ax, ly, up = frame_axes(psi, tau)
    return (CX + ax[0] * p[0] + ly[0] * p[1] + up[0] * p[2],
            ax[1] * p[0] + ly[1] * p[1] + up[1] * p[2],
            CZ + ax[2] * p[0] + ly[2] * p[1] + up[2] * p[2])


def _proj(v):
    s = (Y_GLOW - CAM_LOC[1]) / (v[1] - CAM_LOC[1])
    return (CAM_LOC[0] + s * (v[0] - CAM_LOC[0]), CAM_LOC[2] + s * (v[2] - CAM_LOC[2]))


def _screen(v):
    s = 8.3 / (v[1] - CAM_LOC[1])
    return (0.5 + (v[0] - AIM_X) * s / FRAME_W, 0.5 + (v[2] - LOOK_Z) * s / FRAME_H)


def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    cr = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def field_e(du, dv):
    r = math.hypot(du / RX, dv / RZ)
    if r >= 1.0:
        return 0.0
    return 0.55 * math.exp(-(r / 0.30) ** 2) + 0.45 * (1.0 - r * r) ** 2.8


GLOW_C = _proj((CX, 0.0, CZ))        # 光の中心＝カメラから見て鼓の中心の真後ろ
NGX, NGZ = 100, 64
GX0, GZ0 = GLOW_C[0] - RX, GLOW_C[1] - RZ
_DX, _DZ = 2 * RX / NGX, 2 * RZ / NGZ


def occlusion_grid(t):
    """鼓が光の面のどのセルを隠しているか（凸部品は凸包、調緒はカプセル）"""
    occ = [[False] * NGX for _ in range(NGZ)]

    def fill_hull(h):
        if len(h) < 3:
            return
        xs = [p[0] for p in h]; zs = [p[1] for p in h]
        i0, i1 = max(0, int((min(xs) - GX0) / _DX)), min(NGX - 1, int((max(xs) - GX0) / _DX))
        j0, j1 = max(0, int((min(zs) - GZ0) / _DZ)), min(NGZ - 1, int((max(zs) - GZ0) / _DZ))
        n = len(h)
        for j in range(j0, j1 + 1):
            z = GZ0 + (j + 0.5) * _DZ
            row = occ[j]
            for i in range(i0, i1 + 1):
                if row[i]:
                    continue
                x = GX0 + (i + 0.5) * _DX
                ok = True
                for q in range(n):
                    a, b = h[q], h[(q + 1) % n]
                    if (b[0] - a[0]) * (z - a[1]) - (b[1] - a[1]) * (x - a[0]) < 0.0:
                        ok = False; break
                if ok:
                    row[i] = True

    ring = [2 * math.pi * k / 20 for k in range(20)]
    for x0, x1 in ((-LD / 2, -XI), (XI, LD / 2)):                    # 革（円板＝凸）
        fill_hull(_hull([_proj(to_world((x, RH * math.cos(a), RH * math.sin(a)), t))
                         for x in (x0, x1) for a in ring]))
    NB = 18
    for j in range(NB):                                             # 胴（輪切りの錐台＝凸）
        xa, xb = -XI + 2 * XI * j / NB, -XI + 2 * XI * (j + 1) / NB
        fill_hull(_hull([_proj(to_world((x, body_r(x) * math.cos(a), body_r(x) * math.sin(a)), t))
                         for x in (xa, xb) for a in ring]))
    s = squeeze(t)
    mag = (Y_GLOW - CAM_LOC[1]) / (0.0 - CAM_LOC[1])
    rr = RCORD * mag
    for pth in cord_paths(s):
        pp = [_proj(to_world(p, t)) for p in pth[::3]]
        for (ax_, az_), (bx_, bz_) in zip(pp, pp[1:]):
            i0 = max(0, int((min(ax_, bx_) - rr - GX0) / _DX))
            i1 = min(NGX - 1, int((max(ax_, bx_) + rr - GX0) / _DX))
            j0 = max(0, int((min(az_, bz_) - rr - GZ0) / _DZ))
            j1 = min(NGZ - 1, int((max(az_, bz_) + rr - GZ0) / _DZ))
            dx, dz = bx_ - ax_, bz_ - az_
            L2 = dx * dx + dz * dz + 1e-12
            for j in range(j0, j1 + 1):
                z = GZ0 + (j + 0.5) * _DZ
                for i in range(i0, i1 + 1):
                    x = GX0 + (i + 0.5) * _DX
                    u = max(0.0, min(1.0, ((x - ax_) * dx + (z - az_) * dz) / L2))
                    ex, ez = ax_ + u * dx - x, az_ + u * dz - z
                    if ex * ex + ez * ez < rr * rr:
                        occ[j][i] = True
    return occ


def visible_light(t, thr=0.0):
    occ = occlusion_grid(t)
    tot = 0.0
    for j in range(NGZ):
        z = GZ0 + (j + 0.5) * _DZ
        for i in range(NGX):
            if occ[j][i]:
                continue
            e = field_e(GX0 + (i + 0.5) * _DX - GLOW_C[0], z - GLOW_C[1])
            tot += (e if thr == 0.0 else (1.0 if e > thr else 0.0))
    return tot * _DX * _DZ


def middle_light(t):
    """真ん中（胴の半長の ±35% の幅）から抜ける光だけ"""
    occ = occlusion_grid(t)
    tot = 0.0
    xm = 0.35 * XI * (Y_GLOW - CAM_LOC[1]) / (0.0 - CAM_LOC[1])
    for j in range(NGZ):
        z = GZ0 + (j + 0.5) * _DZ
        for i in range(NGX):
            x = GX0 + (i + 0.5) * _DX
            if occ[j][i] or abs(x - GLOW_C[0]) > xm:
                continue
            tot += field_e(x - GLOW_C[0], z - GLOW_C[1])
    return tot * _DX * _DZ


def silhouette_box(t):
    pts = []
    for x in (-LD / 2, -XI, XI, LD / 2):
        for k in range(24):
            a = 2 * math.pi * k / 24
            pts.append(_screen(to_world((x, RH * math.cos(a), RH * math.sin(a)), t)))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


if "--probe-only" in sys.argv:
    print("── 078 TSUZUMI 幾何プローブ")
    ts = [i / 24 for i in range(24)]
    vs = [visible_light(t) for t in ts]
    ms = [middle_light(t) for t in ts]
    ar = [visible_light(t, thr=0.06) for t in ts]
    print("   #40⑥ 見える光 min/max = %.3f（合格 0.75以下）  max/min = %.2f"
          % (min(vs) / max(vs), max(vs) / min(vs)))
    print("   ライム面積（E>0.06）max/min = %.2f（motion 光の振れ 1.22 以上）" % (max(ar) / min(ar)))
    print("   真ん中から抜ける光 max/min = %.2f" % (max(ms) / max(min(ms), 1e-9)))
    for t in (0.0, 0.25, 0.5, 0.75):
        print("   t=%.2f  s=%.2f  見える光 %.3f  真ん中 %.4f" % (t, squeeze(t), visible_light(t),
                                                            middle_light(t)))
    x0, x1, y0, y1 = silhouette_box(0.5)
    print("   hero の革の外形 bbox  x %.3f..%.3f  y %.3f..%.3f → 幅 %.1f%% 高 %.1f%%"
          % (x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100))
    print("   重心x ≈ %.1f%%" % ((x0 + x1) * 50))
    sys.exit(0)


# =============================================================
# ここから Blender
# =============================================================
import bpy, bmesh                                        # noqa: E402
from mathutils import Vector, Matrix                     # noqa: E402


def hex_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------- マテリアル（MATERIALS.md の実測レシピ・#52） ----------
BLACK_RECIPES = {
    "urushi": dict(rough=0.30, spec=0.34, coat=0.05, coat_rough=0.25),
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25),
}


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def black_material(name, recipe):
    m, p = principled(name)
    r = BLACK_RECIPES[recipe]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)
    if r.get("sheen"):
        p.inputs["Sheen Weight"].default_value = r["sheen"]
        p.inputs["Sheen Roughness"].default_value = r.get("sheen_rough", 0.3)
        p.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)
    return m


mat_body = black_material("tsuzumi_urushi", "urushi")
mat_cord = black_material("shirabe_nuno", "nuno")
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（ローカル座標：軸＝X。object.scale / transform_apply 不使用＝#15）----------
def mk_mesh(name, verts, faces):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return me


def lathe(profile, na=96):
    """profile＝[(x, r)]。r=0 の点は軸上の1頂点に畳む（閉じたソリッド）"""
    verts, faces, rows = [], [], []
    for x, r in profile:
        if r <= 1e-9:
            rows.append([len(verts)] * na); verts.append((x, 0.0, 0.0))
        else:
            rows.append(list(range(len(verts), len(verts) + na)))
            for k in range(na):
                a = 2 * math.pi * k / na
                verts.append((x, r * math.cos(a), r * math.sin(a)))
    for j in range(len(rows) - 1):
        for k in range(na):
            k2 = (k + 1) % na
            q = [rows[j][k], rows[j][k2], rows[j + 1][k2], rows[j + 1][k]]
            q2 = []
            for v in q:
                if v not in q2:
                    q2.append(v)
            if len(q2) >= 3:
                faces.append(q2)
    return verts, faces


def body_profile():
    prof = [(-XI, 0.0)]
    N = 90
    for i in range(N + 1):
        x = -XI + 2 * XI * i / N
        prof.append((x, body_r(x)))
    prof.append((XI, 0.0))
    return prof


def head_profile(sgn):
    """革：表は平ら、縁は鉄輪を包んだ丸み、表の外周に一段高い縁（漆の帯）"""
    xo, xi = sgn * LD / 2, sgn * XI
    rr = TH / 2
    xm = (xo + xi) / 2
    xs = xo - sgn * 0.008                      # 革の面は縁の帯より一段沈む
    prof = [(xs, 0.0), (xs, 0.735 * RH), (xo, 0.755 * RH)]
    # 🔴 1周目：縁の丸みを「裏→表」の順に張って輪郭が自己交差し、左の革の表が抜けて光が透けた
    for k in range(0, 13):                     # 表（a=0）→ 外周 → 裏（a=π）
        a = math.pi * k / 12
        prof.append((xm + sgn * rr * math.cos(a), RH - rr + rr * math.sin(a)))
    prof += [(xi, 0.0)]
    return prof


def tube(paths):
    """調緒＝三つ撚りのチューブ（撚りの起伏は実ジオメトリ）。頂点の並びは状態に依らない"""
    NR = 10
    verts, faces = [], []
    for pts in paths:
        n = len(pts)
        base = len(verts)
        # 平行移動フレーム
        T = []
        for i in range(n):
            a = pts[max(0, i - 1)]; b = pts[min(n - 1, i + 1)]
            d = Vector(b) - Vector(a); T.append(d.normalized())
        ref = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((0, 1, 0))
        Nv = (ref - T[0] * ref.dot(T[0])).normalized()
        arc = 0.0
        for i in range(n):
            if i > 0:
                Nv = (Nv - T[i] * Nv.dot(T[i])).normalized()
                arc += (Vector(pts[i]) - Vector(pts[i - 1])).length
            Bv = T[i].cross(Nv)
            for k in range(NR):
                a = 2 * math.pi * k / NR
                r = RCORD * (1.0 + PLY_A * math.cos(3 * a - 2 * math.pi * arc / PLY_PITCH))
                off = Nv * (r * math.cos(a)) + Bv * (r * math.sin(a))
                verts.append(tuple(Vector(pts[i]) + off))
        for i in range(n - 1):
            for k in range(NR):
                k2 = (k + 1) % NR
                faces.append([base + i * NR + k, base + i * NR + k2,
                              base + (i + 1) * NR + k2, base + (i + 1) * NR + k])
        for i, rev in ((0, True), (n - 1, False)):
            c = len(verts); verts.append(pts[i])
            for k in range(NR):
                k2 = (k + 1) % NR
                f = [c, base + i * NR + k, base + i * NR + k2]
                faces.append(f[::-1] if rev else f)
    return verts, faces


def link(me, name, mat, smooth_ang=0.9):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_ang)
    except Exception:
        pass
    ob.select_set(False)
    return ob


ob_body = link(mk_mesh("m_dou", *lathe(body_profile())), "dou", mat_body, 1.2)
ob_hl = link(mk_mesh("m_kawa_l", *lathe(head_profile(-1.0), 128)), "kawa_hidari", mat_body, 0.9)
ob_hr = link(mk_mesh("m_kawa_r", *lathe(head_profile(+1.0), 128)), "kawa_migi", mat_body, 0.9)
v0, f0 = tube(cord_paths(0.0))
v1, _ = tube(cord_paths(1.0))
ob_cord = link(mk_mesh("m_shirabe", v0, f0), "shirabe", mat_cord, 1.2)
ob_cord.shape_key_add(name="Basis", from_mix=False)
kb = ob_cord.shape_key_add(name="shime", from_mix=False)
for i, co in enumerate(v1):
    kb.data[i].co = co
parts = [ob_body, ob_hl, ob_hr, ob_cord]


# ---------- 光（鼓のうしろ）。065 と同じ組み方 ------------------
def glow_mesh():
    bm = bmesh.new()
    ctr = bm.verts.new((0.0, 0.0, 0.0))
    rings = []
    for j in range(1, NRF + 1):
        rho = j / NRF
        rings.append([bm.verts.new((rho * RX * math.cos(2 * math.pi * k / NAF), 0.0,
                                    rho * RZ * math.sin(2 * math.pi * k / NAF)))
                      for k in range(NAF)])
    for k in range(NAF):
        bm.faces.new((ctr, rings[0][k], rings[0][(k + 1) % NAF]))
    for j in range(NRF - 1):
        for k in range(NAF):
            k2 = (k + 1) % NAF
            bm.faces.new((rings[j][k], rings[j][k2], rings[j + 1][k2], rings[j + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.y > 0:
            f.normal_flip()
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (field_e(co.x, co.z), 0.5)
    me = bpy.data.meshes.new("hikari"); bm.to_mesh(me); bm.free()
    return me


def glow_material(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    E = sep.outputs["X"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    gsep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], gsep.inputs["Vector"])

    def band(freq, amp, phase):
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = 2.0 * math.pi * freq
        nt.links.new(gsep.outputs["Z"], mul.inputs[0])
        add = nt.nodes.new("ShaderNodeMath"); add.operation = 'ADD'
        add.inputs[1].default_value = phase
        nt.links.new(mul.outputs[0], add.inputs[0])
        sn = nt.nodes.new("ShaderNodeMath"); sn.operation = 'SINE'
        nt.links.new(add.outputs[0], sn.inputs[0])
        ma = nt.nodes.new("ShaderNodeMath"); ma.operation = 'MULTIPLY_ADD'
        ma.inputs[1].default_value = 0.5 * amp
        ma.inputs[2].default_value = 0.5 * amp
        nt.links.new(sn.outputs[0], ma.inputs[0])
        return ma.outputs[0]

    b1, b2 = band(HAZE_F1, HAZE_A1, 0.0), band(HAZE_F2, HAZE_A2, 1.7)
    bsum = nt.nodes.new("ShaderNodeMath"); bsum.operation = 'ADD'
    nt.links.new(b1, bsum.inputs[0]); nt.links.new(b2, bsum.inputs[1])
    haze = nt.nodes.new("ShaderNodeMath"); haze.operation = 'SUBTRACT'
    haze.inputs[0].default_value = 1.0
    nt.links.new(bsum.outputs[0], haze.inputs[1])
    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = WHITE_FROM
    wmr.inputs["From Max"].default_value = 1.0
    wmr.inputs["To Min"].default_value = 0.0
    wmr.inputs["To Max"].default_value = WHITE_TO
    nt.links.new(E, wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])
    es0 = nt.nodes.new("ShaderNodeMath"); es0.operation = 'MULTIPLY'
    es0.inputs[1].default_value = ES_CORE
    nt.links.new(E, es0.inputs[0])
    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    nt.links.new(es0.outputs[0], es.inputs[0]); nt.links.new(haze.outputs[0], es.inputs[1])
    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_ALPHA
    nt.links.new(E, a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MULTIPLY'
    nt.links.new(a1.outputs[0], a2.inputs[0]); nt.links.new(haze.outputs[0], a2.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("hikari")
glow = bpy.data.objects.new("hikari", glow_mesh())
bpy.context.collection.objects.link(glow)
glow.data.materials.append(mat_glow)
glow.location = (GLOW_C[0], Y_GLOW, GLOW_C[1])
glow.visible_shadow = False

# --- キーフレーム（毎フレーム打つ＝イージング不使用。回転は四元数）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev = None
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    ax, ly, up = frame_axes(*pose(t))
    M = Matrix(((ax[0], ly[0], up[0], 0.0), (ax[1], ly[1], up[1], 0.0),
                (ax[2], ly[2], up[2], 0.0), (0.0, 0.0, 0.0, 1.0)))
    q = M.to_quaternion()
    if prev is not None and q.dot(prev) < 0.0:
        q.negate()
    prev = q.copy()
    for ob in parts:
        ob.location = (CX, 0.0, CZ)
        ob.rotation_quaternion = q
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_quaternion", frame=f + 1)
    kb.value = squeeze(t)
    kb.keyframe_insert("value", frame=f + 1)

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor_obj = bpy.context.active_object
floor_obj.name = "floor"
floor_obj.data.materials.append(mat_floor)


def caption(body, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object; tx.name = name
    tx.data.body = body; tx.data.size = size; tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 1.02), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.85), "logo"),
        caption("MIDDLE STUDY 078 — TSUZUMI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = (CX, 0.0, CZ)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
# 🔴 #76④：背光の作では白い逆光がライムの回り込みを上書きする＝ライムの随伴光より弱く（1800→620W）
back = area("back", (0.0, 5.2, 2.2), 4.0, 620, (1.0, 0.99, 0.96), focus)
back.visible_camera = False        # 🔴 #67①：調緒は抜けだらけ＝逆光がそのままカメラに写る

limelamps = []
for sx, sy, sz, w in ((-0.85, 12.0, 0.30, LIME_W), (0.30, 24.0, 0.30, LIME_W),
                      (1.60, 38.0, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = w
    lp.data.shadow_soft_size = 2.60
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0
    limelamps.append(lp)

# #76①：暗いライムが作れるのは黒の上だけ＝革の縁と調緒をうしろからライムで舐める
rimlamps = []
for sx, sy, sz, w in ((-1.05, 1.05, CZ + 0.10, 230.0), (1.05, 1.05, CZ + 0.10, 230.0),
                      (0.00, 1.35, CZ + 0.85, 200.0)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "rim_%+0.2f" % sx
    lp.data.energy = w
    lp.data.shadow_soft_size = 0.80
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    rimlamps.append(lp)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 8.30
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは**全ジオメトリ生成後**に置く（#56②）。床だけ受光から外す
lit = bpy.data.collections.new("lit_by_back")
bpy.context.scene.collection.children.link(lit)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not floor_obj:
        lit.objects.link(o)
back.light_linking.receiver_collection = lit

lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not glow:
        lit_by_lime.objects.link(o)
for lp in limelamps:
    lp.light_linking.receiver_collection = lit_by_lime

# 🔴 2周目：革（漆の平らな面）まで受光させると、ライムの点光源が**面全体に映って革がライムの板になる**
#    （光の面を消しても革は緑のまま＝映り込みだと切り分けた）。舐めるのは麻の調緒と胴だけ
lit_by_rim = bpy.data.collections.new("lit_by_rim")
bpy.context.scene.collection.children.link(lit_by_rim)
for o in (ob_cord, ob_body):
    lit_by_rim.objects.link(o)
for lp in rimlamps:
    lp.light_linking.receiver_collection = lit_by_rim

scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print(">> GPU failed:", e)
scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
except Exception:
    scene.view_settings.view_transform = 'AgX'


def setup_glare():
    """🔴 #54：try で包まない。2026-08-13 Ryota決定＝Streaks 続投。"""
    ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new("CompositorNodeRLayers")
    glr = ng.nodes.new("CompositorNodeGlare")
    ou = ng.nodes.new("NodeGroupOutput")
    glr.inputs["Type"].default_value = 'Streaks'
    glr.inputs["Threshold"].default_value = 1.2
    glr.inputs["Strength"].default_value = 0.35
    glr.inputs["Size"].default_value = 0.55
    ng.links.new(rl.outputs["Image"], glr.inputs["Image"])
    ng.links.new(glr.outputs["Image"], ou.inputs["Image"])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True


setup_glare()

scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME)

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, ys = [], []
    for o in parts:
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 鼓の投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 🔴 長辺 %.1f%%（55〜65%%）  重心x %.1f%%" % (max(x1 - x0, y1 - y0) * 100,
                                                    (x0 + x1) * 50))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))
    print(">> 面数 %d" % sum(len(o.evaluated_get(dg).data.polygons)
                            for o in bpy.data.objects if o.type == 'MESH'))

if "test" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 480, 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_test.png")
    bpy.ops.render.render(write_still=True)
    print(">> test done")

if "testhero" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "_testhero.png")
    bpy.ops.render.render(write_still=True)
    print(">> testhero done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero done")

if "phases" in modes:
    for fr in (1, 31, 61, 91):
        scene.frame_set(fr)
        scene.render.resolution_x, scene.render.resolution_y = 480, 600
        scene.cycles.samples = 24
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(OUT, "_phase_%03d.png" % fr)
        bpy.ops.render.render(write_still=True)
    print(">> phases done")

if "anim" in modes:
    scene.render.resolution_x, scene.render.resolution_y = 720, 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> anim done")

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_078.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("tsuzumi_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = 0.34
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    for o in parts:
        o.data.materials[0] = m_bk
    glow.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {glow.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = ob_body
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True,
                                  export_morph_animation=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
