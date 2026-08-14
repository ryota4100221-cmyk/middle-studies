# =============================================================
# monaka design. — MIDDLE STUDY 042 "KINTSUGI"（金継ぎ / a vessel mended with light）
# 黒い壺が、割れている。破片はもう戻されていて、器のかたちをしている。
# 光っているのは、割れたところだけ——継ぎ目の線が、腹（＝真ん中）でいちばん明るい。
# 継ぎ目はゆっくり息をして、線が太くなり、細くなる。壊れた場所が、いちばん明るい。
#
# 【ドメイン】工芸・繕い／金継ぎ（シリーズ未踏）。直近10作（植物・竹／計量・秤／
#   貝・海／折紙／玩具・独楽／武具・鞘／装身・櫛／調度・屏風／縄・繊維／信仰・鈴）と別領域。
#   023 UTSUWA は【器・陶／茶道】＝碗の中に光が満ちる話。042 は器の**外皮の割れ目**の話で、
#   シルエット（低く広い碗 / 背の高い壺）も主題（満ち引き / 繕い）も別。
#
# 【機構】シリーズ初の「**剛体の破片が軸まわりにわずかに回り、継ぎ目の幅そのものが呼吸する**」。
#   ・器を 6 片に割る：横の割れ（zs(ψ)＝傾いた面で1本）＋縦の割れ（下帯4本・上帯2本）。
#   ・破片 j は器の軸（Z）まわりに θ_j(t) = ROT_A·sin(2πt − ψ_j) だけ回る。
#     **隣り合う θ の差がそのまま継ぎ目の角幅**になる。θ の差は円周を一周すると
#     telescoping で必ず 0 に戻るので、**どの θ_j を選んでも継ぎ目の総和は不変**＝
#     破片は互いに食い込まない。位相を破片の方位 ψ_j にしたので、**開きが器を巡る波**になる。
#   ・sin(2πt) の整数周期＝t=0 と t=1 が厳密一致＝完全ループ。回転キーなので glb に乗る
#     （シェイプキー不要／object.scale・transform_apply 不使用 #15／リグは原点 #9）。
#   ・継ぎ目は 4.3mm（閉）〜25mm（開）。見える発光面積は 47%→100% ＝#40⑥ の意味で
#     機構がそのまま光の量になる（probe で検算）。
#
# 【光】継ぎ目の奥に置いた**継ぎ材のリボン**（内皮のすぐ内側を、割れ線に沿って走る帯）。
#   #29 のとおり「開口と同軸・同形」なので裸の緑棒（#13/#18）にならない。
#   Base＝純黒・Spec 0（#32：随伴光が発光体自身を拡散照明してペンキ化するのを防ぐ）。
#   勾配は #34 の2軸楕円距離。ただし割れ線は z ごとに方位が蛇行するので、
#   **Object 座標では「割れ線を横切る距離」が書けない**。→ 042 では
#   **正規化した2軸座標を UV に焼き込む**（u＝継ぎ目を横切る距離[m]/FU、
#   v＝(z−Z_HOT)/FZ）。材質は sqrt(u²+v²) → POWER → MapRange(ES_CORE→0) の一本で、
#   縦の継ぎ目も横の継ぎ目も同じマテリアルで書ける（横の継ぎ目は u=z方向・v=方位）。
#   FU は**開いたときの継ぎ目の半幅**に取るので、ES は継ぎ目の縁でちょうど 0 に落ちる
#   ＝リボンの外側は完全な黒＝そのまま裏当て（#26②/#28 の緑スピル・白抜けが構造的に出ない）。
#
# 【読み（#16/#33）】#33 の撤退条件を満たす：①細い部材で中心を囲まない（単一の器）
#   ②大きな平円盤を使わない ③solid の塊が主役で光は細い線 ④輪郭が唯一無二
#   （腹の張った壺＋口縁の返し＋平底）。melon（みかんの房）に見えないよう、
#   縦の割れは**方位を不等間隔**に置き、**それぞれ違う振幅・周期で蛇行**させ、
#   さらに**傾いた横の割れ**で上下に切る＝実際の陶片の割れ方に寄せる。
#
# 実行:
#   Blender --background --factory-startup --python monaka_kintsugi.py -- <mode...>
#   modes: probe | bbox | test | testhero | still | anim | blend | glb  （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_kintsugi")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "2.10"))
LOOK_Z = float(os.environ.get("LOOK_Z", "1.72"))
CAM_LOC = (0.55, -8.3, 1.95)

# --- 器（壺） ---
ZH = float(os.environ.get("ZH", "1.00"))       # 半高（全高 2ZH）
WALL = float(os.environ.get("WALL", "0.024"))  # 肉厚
# 輪郭の制御点（正規化 z, 半径[m]）。023 の教訓＝Catmull-Rom で密に取る（低ポリの面取りを消す）
PROFILE = [
    (-1.00, 0.238), (-0.96, 0.270), (-0.90, 0.315), (-0.78, 0.395), (-0.64, 0.478),
    (-0.48, 0.565), (-0.30, 0.640), (-0.12, 0.694), (0.06, 0.700),
    (0.24, 0.668), (0.42, 0.596), (0.58, 0.505), (0.72, 0.395),
    (0.84, 0.290), (0.92, 0.226), (0.965, 0.205), (1.00, 0.252),
]

# --- 割れ（横1本＋縦6本） ---
ZB_N = float(os.environ.get("ZB_N", "0.30"))    # 横の割れの基準高（正規化）
TZ_N = float(os.environ.get("TZ_N", "0.085"))   # 横の割れの傾き（面で割れた＝cos1周期）
PSI_T = float(os.environ.get("PSI_T", "0.90"))
HZ = float(os.environ.get("HZ", "0.013"))       # 横の継ぎ目の幅[m]（固定）
HG = float(os.environ.get("HG", "0.01050"))     # 縦の継ぎ目の**半**角（閉じたときの基準）

# 縦の割れ：(基準方位, 蛇行振幅, 周期係数, 位相)。方位は不等間隔＝みかんの房に見せない
SEAM_L = [(-0.62, 0.19, 1.0, 0.0), (0.05, 0.15, 1.7, 1.1),
          (2.20, 0.22, 1.3, 2.4), (4.05, 0.17, 2.0, 0.7)]
SEAM_U = [(0.30, 0.16, 1.4, 0.4), (3.30, 0.12, 1.1, 2.1)]

ROT_A_L = float(os.environ.get("ROT_A_L", "0.0115"))   # 破片の振れ角[rad]（下帯）
ROT_A_U = float(os.environ.get("ROT_A_U", "0.0080"))   # 同（上帯・2片なので小さく）

# --- 継ぎ材のリボン（＝光） ---
RIB_W = float(os.environ.get("RIB_W", "0.115"))   # 🔴 #51：線が細くhalo 6,850。光は強さでなく面の広さ    # 実体の半幅[m]（裏当てを兼ねる）
RIB_OFF = float(os.environ.get("RIB_OFF", "0.005"))  # 内皮からの引っ込み[m]
FU = float(os.environ.get("FU", "0.0120"))         # 短軸の減衰幅[m]＝開いた継ぎ目の半幅
FZ = float(os.environ.get("FZ", "0.58"))           # 長軸の減衰幅[m]（縦の継ぎ目）
FA = float(os.environ.get("FA", "1.15"))           # 同（横の継ぎ目＝方位[rad]）
Z_HOT = float(os.environ.get("Z_HOT", "0.00"))     # 光の芯の高さ＝器の腹＝真ん中

ES_CORE = float(os.environ.get("ES_CORE", "7.2"))   # 上げすぎると白飛びしてhaloが減る（実測7.0→9.8でhalo低下）   # 🔴 7.0 でも halo 7,636＝下限9,000に届かず   # 🔴 #51：halo 5,763 で下限9,000に届いていなかった
D_POW = float(os.environ.get("D_POW", "1.45"))     # #38④：べきが小さいと暗い裾が中間調を沈める
GLOW_E = float(os.environ.get("GLOW_E", "0.05"))   # 割れ口の側壁を洗うこぼれ光（#22）

# --- 材質（#17：曲面／#17-c：一様bright env 下は反射率を落とす） ---
SPEC_BLACK = float(os.environ.get("SPEC_BLACK", "0.10"))
ROUGH_BLACK = float(os.environ.get("ROUGH_BLACK", "0.50"))

# --- 姿勢 ---
POSE_YAW = math.radians(float(os.environ.get("POSE_YAW", "3.1")))  # 前面をカメラ光軸へ
SWAY = math.radians(float(os.environ.get("SWAY", "5.0")))
BOB = float(os.environ.get("BOB", "0.045"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.72")),
         float(os.environ.get("CAP_Z2", "0.54")),
         float(os.environ.get("CAP_Z3", "0.42")))

NS_L, NU_L = 64, 22       # 下帯の分割（s＝縦, u＝方位）
NS_U, NU_U = 44, 22
FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)
TAU = 2.0 * math.pi


# ---------- 器の輪郭（Catmull-Rom） ----------
_PZ = [p[0] for p in PROFILE]
_PR = [p[1] for p in PROFILE]


def prof_r(z):
    """z[m] → 外半径[m]。制御点の値に Catmull-Rom（区間内は線形パラメータ）。"""
    zn = max(-1.0, min(1.0, z / ZH))
    m = len(_PZ)
    i = 0
    while i < m - 2 and zn > _PZ[i + 1]:
        i += 1
    u = (zn - _PZ[i]) / (_PZ[i + 1] - _PZ[i])
    p0 = _PR[max(i - 1, 0)]
    p1 = _PR[i]
    p2 = _PR[i + 1]
    p3 = _PR[min(i + 2, m - 1)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * u
                  + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * u * u * u)


def prof_ri(z):
    return prof_r(z) - WALL


def zs(psi):
    """横の割れの中心線 z[m]。傾いた面で割れた＝方位の cos 1周期。"""
    return (ZB_N + TZ_N * math.cos(psi - PSI_T)) * ZH


def seam_psi(sm, s):
    """縦の割れ線の方位。s∈[0,1] は帯の中の高さパラメータ。"""
    return sm[0] + sm[1] * math.sin(sm[2] * math.pi * s + sm[3])


# ---------- 帯（バンド）の定義 ----------
def band_z(band, psi, s):
    if band == "L":
        z0, z1 = -ZH, zs(psi) - HZ * 0.5
    else:
        z0, z1 = zs(psi) + HZ * 0.5, ZH
    return z0 + (z1 - z0) * s


BANDS = {
    "L": dict(seams=SEAM_L, ns=NS_L, nu=NU_L, rot=ROT_A_L),
    "U": dict(seams=SEAM_U, ns=NS_U, nu=NU_U, rot=ROT_A_U),
}


def frag_centers(seams):
    """破片の中心方位（＝回転の位相）。"""
    K = len(seams)
    out = []
    for k in range(K):
        a = seams[k][0]
        b = seams[(k + 1) % K][0]
        if b <= a:
            b += TAU
        out.append(0.5 * (a + b))
    return out


def theta_at(band, j, t):
    b = BANDS[band]
    return b["rot"] * math.sin(TAU * t - frag_centers(b["seams"])[j])


def gap_angle(band, k, t):
    """縦の継ぎ目 k の角幅[rad]＝基準 + 隣り合う破片の回転差。"""
    b = BANDS[band]
    K = len(b["seams"])
    return 2.0 * HG + theta_at(band, k, t) - theta_at(band, (k - 1) % K, t)


# hero＝正面の継ぎ目（下帯 seam#1・基準方位 0.05）がいちばん開いた位相
def _pick_still():
    best, bf = -1e9, 1
    for f in range(1, N_FRAMES + 1):
        g = gap_angle("L", 1, (f - 1) / N_FRAMES)
        if g > best:
            best, bf = g, f
    return bf


STILL_FRAME = int(os.environ.get("STILL_FRAME", str(_pick_still())))


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_tou, b = make_principled("kintsugi_tou")     # 黒陶
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_BLACK
b.inputs["Specular IOR Level"].default_value = SPEC_BLACK
b.inputs["Coat Weight"].default_value = 0.0

mat_void, b = make_principled("kintsugi_void")   # 内皮・割れ口の側壁＝純黒（#17-c/#32）
b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
b.inputs["Roughness"].default_value = 0.9
b.inputs["Specular IOR Level"].default_value = 0.0
b.inputs["Coat Weight"].default_value = 0.0

mat_seam, seam_bsdf = make_principled("kintsugi_seam")   # 継ぎ材＝光
seam_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
seam_bsdf.inputs["Emission Color"].default_value = LIME
seam_bsdf.inputs["Roughness"].default_value = 0.5
seam_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
def finish(name, bm, mats, smooth=True, weld=True, auto=False):
    me = bpy.data.meshes.new(name)
    if weld:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.verts.index_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    for m in mats:
        o.data.materials.append(m)
    if auto:
        smooth_auto(o)
    return o


def smooth_auto(o, angle=0.60):
    """#6：5.x は shade_auto_smooth（active+selected で呼ぶ）。"""
    try:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_auto_smooth(angle=angle)
    except Exception as e:
        print(">> shade_auto_smooth skipped:", e)


def add_bevel(o, width=0.0016, angle=30):
    """#10：ANGLE 制限で鋭角の辺だけ面取り（割れ口の稜が光を拾って線になる）。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(angle)


def loft(bm, rings, cap=True):
    vs = [[bm.verts.new(tuple(p)) for p in r] for r in rings]
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            bm.faces.new((vs[i][j], vs[i][j2], vs[i + 1][j2], vs[i + 1][j]))
    if cap:
        bm.faces.new(vs[0][::-1])
        bm.faces.new(vs[-1])
    return vs


# ---------- 破片（陶片） ----------
def build_fragment(band, k):
    """帯 band の破片 k＝閉じた多様体（外皮＋内皮＋割れ口の側壁2枚＋上下の切り口の環）。"""
    cfg = BANDS[band]
    seams = cfg["seams"]
    K = len(seams)
    ns, nu = cfg["ns"], cfg["nu"]
    bm = bmesh.new()
    OU = [[None] * (nu + 1) for _ in range(ns + 1)]
    IN = [[None] * (nu + 1) for _ in range(ns + 1)]

    for i in range(ns + 1):
        s = i / ns
        pa = seam_psi(seams[k], s) + HG
        pb = seam_psi(seams[(k + 1) % K], s) - HG
        while pb <= pa:
            pb += TAU
        for j in range(nu + 1):
            psi = pa + (pb - pa) * (j / nu)
            z = band_z(band, psi, s)
            ro = prof_r(z)
            ri = ro - WALL
            sn, cs = math.sin(psi), -math.cos(psi)
            OU[i][j] = bm.verts.new((ro * sn, ro * cs, z))
            IN[i][j] = bm.verts.new((ri * sn, ri * cs, z))

    for i in range(ns):
        for j in range(nu):
            bm.faces.new((OU[i][j], OU[i][j + 1], OU[i + 1][j + 1], OU[i + 1][j]))
            f = bm.faces.new((IN[i][j], IN[i][j + 1], IN[i + 1][j + 1], IN[i + 1][j]))
            f.material_index = 1
        for j in (0, nu):                                   # 割れ口の側壁（純黒）
            f = bm.faces.new((OU[i][j], IN[i][j], IN[i + 1][j], OU[i + 1][j]))
            f.material_index = 1
    for i in (0, ns):                                       # 上下の切り口の環
        for j in range(nu):
            f = bm.faces.new((OU[i][j], OU[i][j + 1], IN[i][j + 1], IN[i][j]))
            f.material_index = 1

    o = finish("shard_%s%d" % (band, k), bm, (mat_tou, mat_void),
               smooth=True, weld=True, auto=True)
    add_bevel(o, 0.0016, 30)
    return o


# ---------- 継ぎ材のリボン（＝光。UV に正規化2軸座標を焼く） ----------
def _strip(name, rows, uvs):
    """rows: [[(x,y,z)...]]（各行の点列）／uvs: 同形の [(u,v)...]。開いた帯を張る。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    V = [[bm.verts.new(p) for p in r] for r in rows]
    U = {}
    for i, r in enumerate(rows):
        for j in range(len(r)):
            U[V[i][j]] = uvs[i][j]
    for i in range(len(rows) - 1):
        for j in range(len(rows[0]) - 1):
            f = bm.faces.new((V[i][j], V[i][j + 1], V[i + 1][j + 1], V[i + 1][j]))
            for lo in f.loops:
                lo[uvl].uv = U[lo.vert]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat_seam)
    return o


def build_seam_ribbon(band, k, nw=9):
    """縦の継ぎ目のリボン。u＝継ぎ目を横切る距離[m]/FU、v＝(z−Z_HOT)/FZ。"""
    cfg = BANDS[band]
    ns = cfg["ns"]
    rows, uvs = [], []
    for i in range(ns + 1):
        s = i / ns
        # 帯の端から少しだけ内側に入れる（切り口の環の裏に隠す）
        s2 = 0.010 + 0.980 * s
        pc = seam_psi(cfg["seams"][k], s2)
        z = band_z(band, pc, s2)
        r = prof_ri(z) - RIB_OFF
        row, uv = [], []
        for j in range(nw):
            w = -RIB_W + 2.0 * RIB_W * j / (nw - 1)     # 横切る距離[m]
            psi = pc + w / max(r, 1e-4)
            row.append((r * math.sin(psi), -r * math.cos(psi), z))
            uv.append((w / FU, (z - Z_HOT) / FZ))
        rows.append(row)
        uvs.append(uv)
    return _strip("seam_%s%d" % (band, k), rows, uvs)


def build_ring_ribbon(na=192, nw=9):
    """横の継ぎ目のリボン。u＝z方向の距離[m]/FU、v＝正面からの方位[rad]/FA。"""
    rows, uvs = [], []
    for i in range(na + 1):
        psi = -math.pi + TAU * i / na
        z0 = zs(psi)
        row, uv = [], []
        for j in range(nw):
            w = -RIB_W + 2.0 * RIB_W * j / (nw - 1)
            z = z0 + w
            r = prof_ri(z) - RIB_OFF
            row.append((r * math.sin(psi), -r * math.cos(psi), z))
            uv.append((w / FU, psi / FA))
        rows.append(row)
        uvs.append(uv)
    return _strip("seam_ring", rows, uvs)


def build_disc(name, z, r, hz=0.010):
    bm = bmesh.new()
    N = 96
    loop = [(r * math.cos(TAU * i / N), r * math.sin(TAU * i / N)) for i in range(N)]
    loft(bm, [[(x, y, z - hz) for (x, y) in loop],
              [(x, y, z + hz) for (x, y) in loop]], cap=True)
    return finish(name, bm, (mat_void,), smooth=False)


SHARDS = []
for _b in ("L", "U"):
    for _k in range(len(BANDS[_b]["seams"])):
        SHARDS.append((_b, _k, build_fragment(_b, _k)))

RIBBONS = [build_ring_ribbon()]
for _b in ("L", "U"):
    for _k in range(len(BANDS[_b]["seams"])):
        RIBBONS.append(build_seam_ribbon(_b, _k))

# 中を暗く閉じる（#26②/#28：白背景の抜けと緑スピルを構造的に止める）
CAPS = [build_disc("floor_in", -ZH + 0.028, prof_ri(-ZH + 0.02) - 0.004, 0.012),
        build_disc("neck_in", 0.88 * ZH, prof_ri(0.88 * ZH) - 0.004, 0.012)]

PARTS = tuple([o for (_, _, o) in SHARDS] + RIBBONS + CAPS)


# ---------- リグ（#9：原点に置く／matrix_parent_inverse は identity） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig = bpy.context.active_object
rig.name = "kintsugi_pose"
rig.rotation_euler = (0.0, 0.0, POSE_YAW)

for o in PARTS:
    o.parent = rig
    o.location = (0.0, 0.0, 0.0)


# ---------- 発光の勾配（UV に焼いた正規化2軸／d=1 の縁で厳密に 0） ----------
_ct = mat_seam.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["UV"], _sep.inputs["Vector"])


def _m(op, a=None, b=None, val=None):
    n = _ct.nodes.new("ShaderNodeMath")
    n.operation = op
    if a is not None:
        _ct.links.new(a, n.inputs[0])
    if b is not None:
        _ct.links.new(b, n.inputs[1])
    if val is not None:
        n.inputs[1].default_value = val
    return n.outputs[0]


_d = _m('SQRT', _m('ADD',
                   _m('MULTIPLY', _sep.outputs["X"], _sep.outputs["X"]),
                   _m('MULTIPLY', _sep.outputs["Y"], _sep.outputs["Y"])))
_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 1.0
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = 0.0      # #32：暗部は完全な黒＝そのまま裏当て
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'
except Exception:
    pass
_ct.links.new(_m('POWER', _d, val=D_POW), _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], seam_bsdf.inputs["Emission Strength"])

# 割れ口の側壁を洗うこぼれ光（#22：面積で稼ぎ強度で稼がない）
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.0))
glow = bpy.context.active_object
glow.name = "kintsugi_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.12
glow.parent = rig
glow.location = (0.0, -0.34, 0.0)
try:
    glow.visible_camera = False
except Exception:
    pass


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    for (bd, kk, o) in SHARDS:
        o.rotation_euler = (0.0, 0.0, theta_at(bd, kk, t))
        o.keyframe_insert(data_path="rotation_euler", frame=f)
    rig.location = (0.0, 0.0, CENTER_Z + BOB * math.sin(TAU * t))
    rig.rotation_euler = (0.0, SWAY * math.sin(TAU * t), POSE_YAW)
    rig.keyframe_insert(data_path="location", frame=f)
    rig.keyframe_insert(data_path="rotation_euler", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, -0.55, CENTER_Z))
focus_null = bpy.context.active_object
focus_null.name = "focus_null"


def add_caption(body_text, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object
    tx.name = name
    tx.data.body = body_text
    tx.data.size = size
    tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, CAP_Z[0]), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, CAP_Z[1]), "logo")
study = add_caption("MIDDLE STUDY 042 — KINTSUGI", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


# ---------- ライティング（001と同一＝シリーズの一貫性） ----------
def add_area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.size = size
    L.data.energy = energy
    L.data.color = color
    direction = Vector(target) - Vector(loc)
    L.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0, 0, CENTER_Z - 0.15)
add_area("key",  (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
add_area("rim",  (3.5, 4.0, 3.2),  3.0, 420, (0.88, 0.94, 1.0), focus)
add_area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
    bg.inputs[1].default_value = 0.55


# ---------- カメラ ----------
bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, LOOK_Z))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus_null
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam

for tx in (tagline, logo, study):
    tx.rotation_euler = cam.rotation_euler


# ---------- レンダー設定 ----------
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = True
    scene.cycles.device = 'GPU'
    print(">> Metal GPU enabled")
except Exception as e:
    print(">> GPU setup failed, using CPU:", e)

scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
    print(">> view: PBR Neutral")
except Exception:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Punchy'
    print(">> view: AgX Punchy")


# ---------- コンポジター（Bloom / PITFALL #3の新方式） ----------
def setup_bloom():
    try:
        ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out='OUTPUT',
                                socket_type='NodeSocketColor')
        rl = ng.nodes.new("CompositorNodeRLayers")
        glare = ng.nodes.new("CompositorNodeGlare")
        out = ng.nodes.new("NodeGroupOutput")
        try:
            glare.inputs["Type"].default_value = 'BLOOM'
        except Exception:
            pass
        glare.inputs["Threshold"].default_value = 1.2
        glare.inputs["Strength"].default_value = 0.35
        try:
            glare.inputs["Size"].default_value = 0.55
        except Exception:
            pass
        ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
        ng.links.new(glare.outputs["Image"], out.inputs["Image"])
        scene.compositing_node_group = ng
        scene.render.use_compositing = True
        print(">> Bloom compositor OK")
    except Exception as e:
        print(">> Bloom setup failed (render continues without):", e)


setup_bloom()


# ---------- 検算ヘルパ ----------
def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = (18.0 / 85.0) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


def lit_len(t, n=400):
    """**カメラから見える**発光の面積[cm²]。#40⑥ の検算。
    継ぎ目の角幅の総和は telescoping で常に一定（＝破片は食い込まない）ので、
    絵として効くのは「正面の継ぎ目がどれだけ開くか」。射影 cos で重みを付けて測る。"""
    area = 0.0
    for bd in ("L", "U"):
        cfg = BANDS[bd]
        for k in range(len(cfg["seams"])):
            g = gap_angle(bd, k, t)
            for i in range(n):
                s = (i + 0.5) / n
                pc = seam_psi(cfg["seams"][k], s)
                vis = math.cos(pc)                    # 正面 ψ=0 が最大・裏は見えない
                if vis <= 0.0:
                    continue
                z = band_z(bd, pc, s)
                dz = abs(band_z(bd, pc, min(1.0, s + 1.0 / n)) - z)
                r = prof_r(z)
                w = min(r * g, 2.0 * FU * math.sqrt(max(0.0, 1.0 - ((z - Z_HOT) / FZ) ** 2)))
                area += max(0.0, w) * dz * vis
    for i in range(n):                       # 横の継ぎ目（幅は不変・見える範囲だけ）
        psi = -math.pi + TAU * (i + 0.5) / n
        if math.cos(psi) <= 0.0 or abs(psi / FA) >= 1.0:
            continue
        area += min(HZ, 2.0 * FU) * prof_r(zs(psi)) * TAU / n * math.cos(psi)
    return area * 1e4


# ---------- 出力モード ----------

# ---------- #58 光を空間に出す（2026-08-14 の作り直しで追加） ----------
# 床にライムが1つも落ちていない絵は「光っている物」でなく「点いているパネル」に見える。
# 効くのは発光の強さでもバウンス数でもなく**随伴のライム光源のW数**（4.5W→150Wで床0.03%→4.68%）。
# 🔴 発光体の中に置くと発光体自身が遮って1ルクスも出ないので、被写体の下端の外に置く。
def _add_lime_spill(energy=300.0):
    xs, zs, ys = [], [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.lower().startswith(("floor", "plane", "text")):
            continue
        if max(o.dimensions) > 8:      # 床の巨大プレーンを除く
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            xs.append(w.x); ys.append(w.y); zs.append(w.z)
    if not zs:
        return None
    cx, cy, zmin = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)
    # 🔴 浮いている作は真下へ。床に接している作は真下だと**床の下に潜って1ルクスも出ない**ので、
    #    カメラ側(-Y)へ逃がして床すれすれに置く（031 TOURO で踏んだ）
    # 🔴 被写体の真下に置くと、床の光が画面の測定帯（62〜80%）より下に落ちて見えない。
    #    手前(-Y)の床を照らす位置にすると、光の溜まりがそのまま絵に入る（031で実測 0.00%→0.39%）。
    loc = (cx, cy - 0.62, min(0.42, max(0.16, zmin - 0.10)))
    bpy.ops.object.light_add(type='POINT', location=loc)
    L = bpy.context.active_object; L.name = "lime_spill"
    L.data.energy = energy; L.data.color = LIME[:3]
    L.data.shadow_soft_size = 0.30
    L.visible_camera = False
    print(">> lime_spill %.2f,%.2f,%.2f  (zmin %.2f, %.0fW)" % (loc[0], loc[1], loc[2], zmin, energy))
    return L


_add_lime_spill()

modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "probe" in modes:
    print(">> STILL_FRAME=%d  破片 %d 片 / 継ぎ目 %d 本"
          % (STILL_FRAME, len(SHARDS), len(RIBBONS)))
    dg = bpy.context.evaluated_depsgraph_get()
    for f in (1, 31, STILL_FRAME, 91):
        scene.frame_set(f)
        dg.update()
        xs, zs_, ys = [], [], []
        for o in PARTS:
            ob = o.evaluated_get(dg)
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                xs.append(w.x)
                zs_.append(w.z)
                ys.append(w.y)
        print(f">> f{f} 横 {min(xs):+.2f}..{max(xs):+.2f} "
              f"({max(xs)-min(xs):.2f}/2.81={(max(xs)-min(xs))/2.81*100:.0f}%)  "
              f"縦 {min(zs_):.2f}..{max(zs_):.2f} "
              f"({max(zs_)-min(zs_):.2f}/3.52={(max(zs_)-min(zs_))/3.52*100:.0f}%)")
        print(f"   screen 縦 {screen_y(min(zs_)):+.3f}..{screen_y(max(zs_)):+.3f} "
              f"{'OK' if abs(screen_y(min(zs_))) < 0.97 and abs(screen_y(max(zs_))) < 0.97 else 'WARN 切れる'}")
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    print(">> 継ぎ目の幅[mm]（腹 r=%.3f の高さで）" % prof_r(0.0))
    ts = STILL_FRAME - 1
    for bd in ("L", "U"):
        for k in range(len(BANDS[bd]["seams"])):
            gmin = min(gap_angle(bd, k, (f - 1) / N_FRAMES) for f in range(1, N_FRAMES + 1))
            gmax = max(gap_angle(bd, k, (f - 1) / N_FRAMES) for f in range(1, N_FRAMES + 1))
            gh = gap_angle(bd, k, ts / N_FRAMES)
            print("   %s%d ψ0=%+.2f  閉 %5.1f / hero %5.1f / 開 %5.1f  %s"
                  % (bd, k, BANDS[bd]["seams"][k][0], 1000 * prof_r(0.0) * gmin,
                     1000 * prof_r(0.0) * gh, 1000 * prof_r(0.0) * gmax,
                     "WARN 食い込み" if gmin <= 0.0 else ""))
    print(">> #40③ 光の半幅 %.4f m vs 開いた継ぎ目の半幅 %.4f m : %s"
          % (FU, 0.5 * prof_r(0.0) * max(gap_angle("L", 1, (f - 1) / N_FRAMES)
                                         for f in range(1, N_FRAMES + 1)),
             "OK" if FU <= 0.5 * prof_r(0.0) * max(
                 gap_angle("L", 1, (f - 1) / N_FRAMES)
                 for f in range(1, N_FRAMES + 1)) else "WARN 光が開口より太い"))
    print(">> リボンの実体半幅 %.3f m ≥ 開口の半幅 → 裏当てOK" % RIB_W)
    a_h = lit_len((STILL_FRAME - 1) / N_FRAMES)
    for f in (1, 31, STILL_FRAME, 91):
        a = lit_len((f - 1) / N_FRAMES)
        print("   f%-4d 見える発光面積 %6.2f cm² (%3.0f%%)" % (f, a, a / a_h * 100))
    print(">> loop: θ=A·sin(2πt−ψ) 整数周期＝t=0とt=1が厳密一致 / %df %.3fs"
          % (N_FRAMES, N_FRAMES / FPS))

if "bbox" in modes:
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME)
    dg.update()
    for o in PARTS:
        ob = o.evaluated_get(dg)
        ws = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        print(">> %-12s x %+.3f..%+.3f  y %+.3f..%+.3f  z %+.3f..%+.3f  verts=%d"
              % (o.name, min(w.x for w in ws), max(w.x for w in ws),
                 min(w.y for w in ws), max(w.y for w in ws),
                 min(w.z for w in ws), max(w.z for w in ws), len(ob.data.vertices)))

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "kintsugi.blend"))
    print(">> saved .blend")

if "test" in modes:
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "testhero" in modes:
    # PITFALL #16：480pxでは「何に見えるか」が見えない。造形が固まったら hero で目視。
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test_hero") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> hero-size test done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero still done")

if "anim" in modes:
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'   # PITFALL #2
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

# 🔴 PITFALL #30：glb は Emission を定数へ潰す副作用があるので必ず最後尾に置く。
if "glb" in modes:
    try:
        for lk in list(seam_bsdf.inputs["Emission Strength"].links):
            mat_seam.node_tree.links.remove(lk)
        seam_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> seam emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {rig.name} | {o.name for o in PARTS}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "kintsugi.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
