# =============================================================
# MIDDLE STUDY 080 — INRO（印籠 / what it carries is between the tiers）
#
#   光の型＝隙間（#53：79作で20作）  構図の型＝天地（#57：79作で4作）
#   ドメイン＝提げ物・印籠（シリーズ未踏）
#
# 印籠は、帯に提げて持ち歩いた薬入れ。いくつもの段を重ねた漆の小箱で、
# 紐は段の両脇の通し穴を抜けて下でぐるりと回り、上で緒締（おじめ）の玉を通って根付に至る。
# 緒締を緩めると、段は紐に通されたまま**上下にひらく**。
# 中身は箱のどの段にもない。**段と段のあいだにだけ、在る。**
# だから高いところに提げて、下はぜんぶ余白にする——帯から垂れているものだから。
#
# 🔴 型の組み合わせ（#87①：works.json は成功の台帳であって可否の台帳ではない）
#    今日選べたのは 光＝面／隙間／芯 × 構図＝端寄せ／天地／群。
#      ・面×天地＝#75②（カメラ軸が水平なので構図が仕事をしない）／芯×端寄せ＝#82⑤ で不成立
#      ・面×端寄せ(052/058)・面×群(071)・隙間×端寄せ(063)・芯×天地(072) は既出
#      ・未踏で PITFALLS に不成立の記録が無いのは 隙間×天地／隙間×群／芯×群
#    隙間×天地 を検算：天地は重心y だけを見る。隙間の光はシルエットの**内側**（段のあいだ）に
#    閉じ込められるので、重心も塊の数も動かさない（#87① の一般則の側）。→ 成立。
#
# 🔴 機構＝**段がひらく**（緒締を緩めた印籠）。いちばん上の蓋は紐に吊られて動かず、
#    その下の段が順に下がる：各隙間 g_j(t)=G_MIN+(G_MAX−G_MIN)·½(1−cos2π(t−PH·(j−1.5)))。
#    段 k の下がり＝Σ_{j<k} g_j。＋根付を支点にした ヨー（sin）と振り子（sin）。
#    #84④：光の振れは**遮蔽で**作る。発光の値は1つも動かさない。隙間が閉じれば光は段の中に隠れる。
#    位置キーと回転キーだけ＝glb にそのまま乗る。
#
# 🔴 光は隙間に「塗る」のではなく、**段の内側に置いた発光の芯（レンズ形の柱）**。
#    隙間の最大より高く、段の輪郭より INSET だけ細い＝閉じると段の肉の中に隠れる。
#    #49②：隙間を全部光らせない——芯は紐（両脇）より内側で終わり、**端では隙間の向こうの白が抜ける**。
#    #34：カメラに正対する細長い発光面は長軸＋短軸の2軸で落とす。
#
# 黒の質感＝urushi 漆（印籠は漆の塗り物）。紐だけ nuno（実物が 漆＋絹紐＝掟4 の例外）。
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
LIME_W = 150.0

# --- 印籠（実物：幅 6〜7cm・高さ 7〜9cm・厚み 2〜2.5cm・4段＋蓋。比だけ借りる＝#50）---
A_HW = 0.42                          # 半幅（x）
B_HD = 0.15                          # 半厚（y）
SE_P = 2.6                           # 断面の超楕円（2＝楕円）
H_LID = 0.14
H_CASE = 0.245
N_CASE = 4
RE = 0.009                           # 段の上下の縁の丸み
                                     # 🔴 1周目 0.028 は段ごとに丸まって**ホッケーのパック／電池の残量表示**に読めた。
                                     #    印籠は「一つの胴を輪切りにした」もの＝段の縁は立てる
G_MAX, G_MIN = 0.056, 0.002
BAR = 0.075                          # 胴のふくらみ（半幅が上下の端で 1−BAR）
RE_END = 0.075                       # 蓋の天・底の角の丸み
# 🔴 3周目まで：まっすぐな柱を輪切りにしていて、hero は**現代のペンダント照明／スピーカー**だった。
#    印籠の正面は「ひとつの小石を輪切りにした」形——胴がふくらみ、天と底の角が大きく丸い
PH = 0.075                           # 隙間ごとの位相のずれ（上から順にひらく）
                                     # 🔴 4周目：位相を中央対称（j−1.5）にすると hero で4本が同じ幅＝**縞模様**（#75③ の型）。
                                     #    上から順に遅らせ、ひらきが下へ伝わっていく途中を hero にする
XC = A_HW * (1 - BAR) - 0.052        # 紐の通り（両脇の通し穴）。胴のいちばん細い所の内側
CR = 0.0125                          # 紐の半径

# --- 光（段の中の発光の芯）----------------------------------------
INSET_X, INSET_Y = 0.100, 0.030
OVERLAP = 0.035
H_SLAB = G_MAX + 2 * OVERLAP
FX, FZ = 0.78, 0.78                  # 🔴 2周目 0.46 は短い**緑の眼**（#49②）。長い一条にして端を E_FLOOR で黒へ                  # E の2軸の幅（xn＝x/A_S、zn＝(z−中心)/(G_MAX/2)）
HX, HZ, HOT_A = 0.40, 0.42, 0.55
E_PEAK = 1.0 + HOT_A
E_FLOOR = 0.100                      # 🔴 1周目 0.010 は芯の端までライムが残り**緑の錠剤**に読めた。端は黒へ落とす
ES_CORE = 4.6
WHITE_FROM, WHITE_TO = 0.66, 0.70     # 🔴 4周目 0.45 は一条ぜんぶが白く飛んで**ネオン管**（#34）。白は真ん中の芯だけ
K_MIX = 16.0

# --- 上の吊り（緒締・根付）----------------------------------------
Z_NET = 3.49                         # 根付（瓢箪）の括れ＝回転の支点
R_NET, T_NET = 0.100, 0.080
Z_OJ = 3.15                          # 緒締の玉
R_OJ = 0.060
Z_LID_TOP = 2.93                     # 蓋の天（ここは動かない）

# --- 動き ---------------------------------------------------------
YAW0 = math.radians(22.0)            # 厚みを見せる基準の向き
YAW_A = math.radians(20.0)
SWAY_A = math.radians(2.6)
STILL_FRAME = 61                     # t=0.5 ＝ ひらき切り

PIV = (AIM_X, 0.0, Z_NET)


# =============================================================
# 純 math（#31）
# =============================================================
def smooth(e0, e1, x):
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def gap(j, t):
    return G_MIN + (G_MAX - G_MIN) * 0.5 * (1.0 - math.cos(2.0 * math.pi * (t - PH * j)))


def drop(k, t):
    """段 k（0＝蓋）の下がり"""
    return sum(gap(j, t) for j in range(k))


def yaw(t):
    return YAW0 + YAW_A * math.sin(2.0 * math.pi * t)


def sway(t):
    return SWAY_A * math.sin(2.0 * math.pi * t + 0.9)


def piece_top(k):
    """段 k の天の z（リグ座標＝支点からの相対、閉じた状態）"""
    zt = Z_LID_TOP - Z_NET
    if k == 0:
        return zt
    return zt - H_LID - (k - 1) * H_CASE


def piece_h(k):
    return H_LID if k == 0 else H_CASE


H_BODY = H_LID + N_CASE * H_CASE


def half_axes(z):
    """閉じた状態のリグ座標 z での胴の半幅・半厚（ふくらみ）"""
    zt = Z_LID_TOP - Z_NET
    u = ((z - (zt - H_BODY / 2)) / (H_BODY / 2))
    f = 1.0 - BAR * min(1.0, u * u)
    return A_HW * f, B_HD * (0.80 + 0.20 * f / 1.0)


def slab_axes(j):
    zc = piece_top(j) - piece_h(j)
    a, b = half_axes(zc)
    return a - INSET_X, b - INSET_Y


def se_xy(th, a, b):
    c, s = math.cos(th), math.sin(th)
    x = a * math.copysign(abs(c) ** (2.0 / SE_P), c)
    y = b * math.copysign(abs(s) ** (2.0 / SE_P), s)
    return x, y


def e_of(xn, zn):
    # 🔴 3周目：x も 2乗で落とすと等値線が楕円＝**緑の眼**（#49②）。長さ方向は4乗で「一条」にして端だけ落とす
    raw = math.exp(-(xn / FX) ** 4 - (zn / FZ) ** 2) + HOT_A * math.exp(-(xn / HX) ** 2 - (zn / HZ) ** 2)
    return max(0.0, (raw / E_PEAK - E_FLOOR) / (1.0 - E_FLOOR))


def rig_to_world(p, t, dz=0.0):
    """リグ座標 → 世界。R = Ry(sway)·Rz(yaw)"""
    x, y, z = p[0], p[1], p[2] - dz
    ps = yaw(t)
    c, s = math.cos(ps), math.sin(ps)
    x, y = x * c - y * s, x * s + y * c
    sw = sway(t)
    c, s = math.cos(sw), math.sin(sw)
    x, z = x * c + z * s, -x * s + z * c
    return (PIV[0] + x, PIV[1] + y, PIV[2] + z)


def _screen(v):
    s = 8.3 / (v[1] - CAM_LOC[1])
    return (0.5 + (v[0] - AIM_X) * s / FRAME_W, 0.5 + (v[2] - LOOK_Z) * s / FRAME_H)


def slab_flux(t):
    """見えている発光（隙間の高さ × 芯の見かけの幅 × E の平均）。#40⑥ を幾何で"""
    ps = yaw(t)
    tot = 0.0
    for j in range(N_CASE):
        A_S, B_S = slab_axes(j)
        wv = 2.0 * math.sqrt((A_S * math.cos(ps)) ** 2 + (B_S * math.sin(ps)) ** 2)
        g = gap(j, t)
        zz = min(1.0, g / G_MAX)
        # 見えている高さ g のうち E の縦平均（中心から ±zz）
        m = sum(e_of(0.0, zz * (i / 10.0 - 0.5) * 2.0) for i in range(11)) / 11.0
        tot += g * wv * m
    return tot


if "--probe-only" in sys.argv:
    print("── 080 INRO 幾何プローブ")
    H_ALL = H_LID + N_CASE * H_CASE
    print("   印籠 幅 %.2f × 高 %.2f（閉）/%.2f（開）× 厚 %.2f   紐 x=±%.3f  芯の半幅 %s"
          % (2 * A_HW, H_ALL, H_ALL + N_CASE * G_MAX, 2 * B_HD, XC,
             " ".join("%.3f" % slab_axes(j)[0] for j in range(N_CASE))))
    print("   紐と芯の端のすきま %.3f（>0）" % (XC - CR - max(slab_axes(j)[0] for j in range(N_CASE))))
    yh = B_HD * (1 - (XC / A_HW) ** SE_P) ** (1 / SE_P)
    print("   紐の位置での段の半厚 %.3f ＞ 紐の半径 %.3f  %s" % (yh, CR, "OK" if yh > CR + 0.02 else "🔴"))
    fs = [slab_flux(i / 48) for i in range(48)]
    print("   #40⑥ 見える光 min/max = %.3f   max/min = %.1f" % (min(fs) / max(fs), max(fs) / max(min(fs), 1e-9)))
    for t in (0.0, 0.25, 0.5, 0.75):
        print("   t=%.2f  隙間 %s  ヨー %4.1f°  光 %.4f"
              % (t, " ".join("%.3f" % gap(j, t) for j in range(N_CASE)), math.degrees(yaw(t)), slab_flux(t)))
    t = 0.5
    pts = []
    for k in range(N_CASE + 1):
        zt = piece_top(k)
        for zz in (zt, zt - piece_h(k)):
            for i in range(24):
                x, y = se_xy(2 * math.pi * i / 24, A_HW, B_HD)
                pts.append(rig_to_world((x, y, zz), t, drop(k, t)))
    for i in range(24):
        a = 2 * math.pi * i / 24
        pts.append(rig_to_world((R_NET * math.cos(a), 0, R_NET * math.sin(a)), t))
    sc = [_screen(p) for p in pts]
    xs, ys = [p[0] for p in sc], [p[1] for p in sc]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print("   hero 外形 screen x %.3f..%.3f  y %.3f..%.3f  → 幅 %.0f%% 高 %.0f%%（長辺 55〜65%%）"
          % (x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100))
    # 重心（面積の荷重）
    zb = Z_NET + piece_top(N_CASE) - H_CASE - drop(N_CASE, t)
    zt = Z_NET + piece_top(0)
    a_body = 2 * A_HW * (zt - zb)
    a_net = math.pi * R_NET ** 2
    cz = (a_body * 0.5 * (zt + zb) + a_net * Z_NET + 0.012 * Z_OJ) / (a_body + a_net + 0.012)
    print("   ざっくり重心 z=%.3f → c_y≈%.1f%%（天地：51以下）  下の余白 %.2f（キャプション上端 1.09）"
          % (cz, (3.71 - cz) / (0.8 * FRAME_H) * 100, zb - 1.09))
    sys.exit(0)


# =============================================================
# Blender
# =============================================================
import bpy, bmesh                                        # noqa: E402
from mathutils import Vector, Matrix, Quaternion         # noqa: E402


def hex_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    s2l = lambda u: u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME, BLACK = hex_to_linear(LIME_HEX), hex_to_linear(BLACK_HEX)

scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

BLACK_RECIPES = {
    "urushi": dict(rough=0.30, spec=0.34, coat=0.05, coat_rough=0.25),
    "nuno": dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25),
}


def black_material(name, recipe):
    r = BLACK_RECIPES[recipe]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    apply_black(p, recipe)
    return m, p


def apply_black(p, recipe):
    r = BLACK_RECIPES[recipe]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]       # 🔴 0.10 を割らない（#45）
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)
    if r.get("sheen"):
        p.inputs["Sheen Weight"].default_value = r["sheen"]
        p.inputs["Sheen Roughness"].default_value = r.get("sheen_rough", 0.3)
        p.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)


mat_uru, _ = black_material("inro_urushi", "urushi")
mat_himo, _ = black_material("himo_nuno", "nuno")
mat_floor = bpy.data.materials.new("floor"); mat_floor.use_nodes = True
fp_ = mat_floor.node_tree.nodes["Principled BSDF"]
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text = bpy.data.materials.new("text"); mat_text.use_nodes = True
tp_ = mat_text.node_tree.nodes["Principled BSDF"]
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（リグ座標のまま。object.scale 不使用＝#15）----------
NTH = 128


def piece_mesh(k):
    """段 k。超楕円の断面・胴のふくらみ・上下の角の丸み。原点＝支点（段の位置はメッシュに焼く）"""
    zt, h = piece_top(k), piece_h(k)
    rt = RE_END if k == 0 else RE
    rb = RE_END if k == N_CASE else RE
    levels = []
    nr = 10
    for i in range(nr + 1):                                  # 上の丸み
        a = (math.pi / 2) * i / nr
        levels.append((zt - rt * (1 - math.sin(a)), rt * (1 - math.cos(a))))
    nm = 10
    for i in range(1, nm):
        levels.append((zt - rt - (h - rt - rb) * i / nm, 0.0))
    for i in range(nr + 1):                                  # 下の丸み
        a = (math.pi / 2) * i / nr
        levels.append((zt - h + rb * (1 - math.cos(a)), rb * (1 - math.sin(a))))
    bm = bmesh.new()
    rows = []
    for z, d in levels:
        a, b = half_axes(z)
        rows.append([bm.verts.new((*se_xy(2 * math.pi * i / NTH, max(a - d, 1e-4), max(b - d, 1e-4)), z))
                     for i in range(NTH)])
    for r in range(len(rows) - 1):
        for i in range(NTH):
            j = (i + 1) % NTH
            bm.faces.new((rows[r][i], rows[r][j], rows[r + 1][j], rows[r + 1][i]))
    ct = bm.verts.new((0, 0, levels[0][0]))
    cb = bm.verts.new((0, 0, levels[-1][0]))
    for i in range(NTH):
        j = (i + 1) % NTH
        bm.faces.new((ct, rows[0][j], rows[0][i]))
        bm.faces.new((cb, rows[-1][i], rows[-1][j]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("m_dan%d" % k); bm.to_mesh(me); bm.free()
    return me


def slab_mesh(j):
    """隙間 j（段 j と j+1 のあいだ）の発光の芯。側面だけ（上下は段の肉の中）。UV の X に E を焼く"""
    zc = piece_top(j) - piece_h(j) - 0.5 * G_MAX            # 段 j+1 と一緒に動かさず、段 j の下がり＋g/2 で置く
    A_S, B_S = slab_axes(j)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    NZ = 20
    rows, ev = [], []
    for iz in range(NZ + 1):
        zn = -1.0 + 2.0 * iz / NZ
        z = zc + zn * H_SLAB / 2
        zq = zn * (H_SLAB / 2) / (G_MAX / 2)
        r_, e_ = [], []
        for i in range(NTH):
            x, y = se_xy(2 * math.pi * i / NTH, A_S, B_S)
            r_.append(bm.verts.new((x, y, z)))
            e_.append(e_of(x / A_S, zq))
        rows.append(r_); ev.append(e_)
    for r in range(NZ):
        for i in range(NTH):
            j2 = (i + 1) % NTH
            f = bm.faces.new((rows[r][i], rows[r][j2], rows[r + 1][j2], rows[r + 1][i]))
            m = {rows[r][i]: ev[r][i], rows[r][j2]: ev[r][j2],
                 rows[r + 1][j2]: ev[r + 1][j2], rows[r + 1][i]: ev[r + 1][i]}
            for lp in f.loops:
                lp[uvl].uv = (m[lp.vert], 0.5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("m_hikari%d" % j); bm.to_mesh(me); bm.free()
    return me


def catmull(pts, n=10):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in range(n):
            u = s / n
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u * u
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u ** 3) for c in range(3)))
    out.append(pts[-1])
    return out


def tube(bm, path, r, nr=10):
    prev = None
    rows = []
    for i, p in enumerate(path):
        a = path[max(0, i - 1)]; b = path[min(len(path) - 1, i + 1)]
        tng = Vector(b) - Vector(a); tng.normalize()
        ref = Vector((0, 1, 0)) if abs(tng.y) < 0.9 else Vector((1, 0, 0))
        n1 = tng.cross(ref); n1.normalize()
        n2 = tng.cross(n1)
        rows.append([bm.verts.new(Vector(p) + (n1 * math.cos(2 * math.pi * q / nr) + n2 * math.sin(2 * math.pi * q / nr)) * r)
                     for q in range(nr)])
    for i in range(len(rows) - 1):
        for q in range(nr):
            q2 = (q + 1) % nr
            bm.faces.new((rows[i][q], rows[i][q2], rows[i + 1][q2], rows[i + 1][q]))


def cord_stub_mesh(k):
    """段 k に付く紐：段の中から下の段の中まで（隙間で見える区間）。いちばん下の段は下を回る輪"""
    zb = piece_top(k) - piece_h(k)
    bm = bmesh.new()
    if k < N_CASE:
        for sx in (-1, 1):
            tube(bm, [(sx * XC, 0, zb + 0.03), (sx * XC, 0, zb - G_MAX - 0.03)], CR)
    else:
        dip = 0.026
        pts = [(-XC, 0, zb + 0.03), (-XC, 0, zb - dip * 0.35), (-XC * 0.80, 0, zb - dip),
               (0, 0, zb - dip * 1.05), (XC * 0.80, 0, zb - dip), (XC, 0, zb - dip * 0.35), (XC, 0, zb + 0.03)]
        tube(bm, catmull(pts, 8), CR)
    me = bpy.data.meshes.new("m_himo%d" % k); bm.to_mesh(me); bm.free()
    return me


def cord_top_mesh():
    """蓋の上：両脇から緒締へ寄り、二本撚りのまま根付へ"""
    zt = piece_top(0)
    zo = Z_OJ - Z_NET
    bm = bmesh.new()
    for sx in (-1, 1):
        # 🔴 1周目は蓋のすぐ上で水平に寄せて**バケツの持ち手**に読めた。通し穴から斜めに立ち上げる
        pts = [(sx * XC, 0, zt - 0.03), (sx * XC, 0, zt + 0.015), (sx * XC * 0.62, 0, zt + 0.10),
               (sx * 0.035, 0, zo - R_OJ * 1.4), (sx * 0.010, 0, zo - R_OJ * 0.5)]
        tube(bm, catmull(pts, 10), CR)
        pts2 = [(sx * 0.010, 0, zo + R_OJ * 0.5), (sx * 0.013, 0, zo + R_OJ * 1.5),
                (sx * 0.012, 0, -0.02)]
        tube(bm, catmull(pts2, 8), CR * 0.95)
    me = bpy.data.meshes.new("m_himo_ue"); bm.to_mesh(me); bm.free()
    return me


def lathe(profile, axis_center, axis='z', na=64, name="m"):
    """profile=[(r, h)]。軸方向 h・半径 r"""
    bm = bmesh.new()
    rows = []
    for r, h in profile:
        row = []
        for i in range(na):
            a = 2 * math.pi * i / na
            if axis == 'z':
                v = (axis_center[0] + r * math.cos(a), axis_center[1] + r * math.sin(a), axis_center[2] + h)
            else:   # y 軸
                v = (axis_center[0] + r * math.cos(a), axis_center[1] + h, axis_center[2] + r * math.sin(a))
            row.append(bm.verts.new(v))
        rows.append(row)
    for i in range(len(rows) - 1):
        for q in range(na):
            q2 = (q + 1) % na
            try:
                bm.faces.new((rows[i][q], rows[i][q2], rows[i + 1][q2], rows[i + 1][q]))
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return me


def ojime_mesh():
    prof = []
    n = 24
    for i in range(n + 1):
        a = -math.pi / 2 + math.pi * i / n
        r = max(1e-5, R_OJ * math.cos(a))
        prof.append((r, R_OJ * 0.92 * math.sin(a)))
    return lathe(prof, (0, 0, Z_OJ - Z_NET), 'z', 48, "m_ojime")


def netsuke_mesh():
    """瓢箪の根付：z 軸の回転体（原点＝括れ）。🔴 1周目の饅頭根付は正面を向いた円盤で**吸盤**に読めた"""
    prof = [(1e-5, -0.215)]
    n = 60
    for i in range(1, n):
        h = -0.215 + 0.37 * i / n
        lo = 0.100 * math.sqrt(max(0.0, 1 - ((h + 0.105) / 0.110) ** 2))
        up = 0.066 * math.sqrt(max(0.0, 1 - ((h - 0.070) / 0.075) ** 2))
        r = max(lo, up, 0.030)
        prof.append((r, h))
    prof += [(0.012, 0.155), (0.012, 0.185), (1e-5, 0.188)]
    return lathe(prof, (0, 0, 0), 'z', 64, "m_netsuke")


def link(me, name, mat, ang=0.9):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=ang)
    except Exception:
        pass
    ob.select_set(False)
    return ob


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
    es = nt.nodes.new("ShaderNodeMath"); es.operation = 'MULTIPLY'
    es.inputs[1].default_value = ES_CORE
    nt.links.new(E, es.inputs[0])
    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(es.outputs[0], emi.inputs["Strength"])
    blk = nt.nodes.new("ShaderNodeBsdfPrincipled")
    apply_black(blk, "urushi")
    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_MIX
    nt.links.new(E, a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a1.outputs[0], mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("hikari")

# (object, 下がりの段番号 k)。蓋・上の紐・緒締・根付は k=0（下がらない）
rig = []
dan = []
for k in range(N_CASE + 1):
    ob = link(piece_mesh(k), "dan%d" % k, mat_uru, 0.9)
    dan.append(ob); rig.append((ob, k))
    rig.append((link(cord_stub_mesh(k), "himo%d" % k, mat_himo, 1.2), k))
slabs = []
for j in range(N_CASE):
    ob = link(slab_mesh(j), "hikari%d" % j, mat_glow, 1.2)
    slabs.append(ob); rig.append((ob, ("half", j)))
ob_top = link(cord_top_mesh(), "himo_ue", mat_himo, 1.2); rig.append((ob_top, 0))
ob_oj = link(ojime_mesh(), "ojime", mat_uru, 1.2); rig.append((ob_oj, 0))
ob_net = link(netsuke_mesh(), "netsuke", mat_uru, 1.2); rig.append((ob_net, 0))


def dz_of(tag, t):
    if isinstance(tag, tuple):
        j = tag[1]
        return drop(j, t) + 0.5 * (gap(j, t) - G_MAX)      # 隙間の真ん中に置く（メッシュは G_MAX/2 で焼いてある）
    return drop(tag, t)


# --- キーフレーム（毎フレーム・リニア）--------------------------------
FR = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob, _ in rig:
    ob.rotation_mode = 'QUATERNION'
prev = None
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    q = Quaternion((0, 1, 0), sway(t)) @ Quaternion((0, 0, 1), yaw(t))
    if prev is not None and q.dot(prev) < 0.0:
        q.negate()
    prev = q.copy()
    for ob, tag in rig:
        off = q @ Vector((0, 0, -dz_of(tag, t)))
        ob.location = Vector(PIV) + off
        ob.rotation_quaternion = q
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_quaternion", frame=f + 1)

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
        caption("MIDDLE STUDY 080 — INRO", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = (AIM_X, 0.0, 2.45)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 620, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：隙間の端から背景が抜ける

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

# 🔴 逆光のライトリンクは全ジオメトリ生成後（#56②）。床だけ受光から外す
lit = bpy.data.collections.new("lit_by_back")
bpy.context.scene.collection.children.link(lit)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not floor_obj:
        lit.objects.link(o)
back.light_linking.receiver_collection = lit

lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o not in slabs:
        lit_by_lime.objects.link(o)
for lp in limelamps:
    lp.light_linking.receiver_collection = lit_by_lime

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
    for o, _ in rig:
        if o in slabs:
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f  y %.3f..%.3f  幅 %.1f%% 高 %.1f%%" % (x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_080.blend"))

# 🔴 glb は必ず最後（#25c／#30）
if "glb" in modes:
    m_bk = bpy.data.materials.new("urushi_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = 0.30
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    for o, _ in rig:
        o.data.materials[0] = m_em if o in slabs else m_bk
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o, _ in rig}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = dan[0]
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
