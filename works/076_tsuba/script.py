# =============================================================
# MIDDLE STUDY 076 — TSUBA（鍔 / 透かし the design is the part that was removed）
#
#   光の型＝窓（#53）  構図の型＝端寄せ（#57）  ドメイン＝刀・刀装具／鍔
#
# 鍔は刀の真ん中にある。柄でもなく、身でもない、ただ一枚。
# そして鍔の意匠は、彫ったものではなく **抜いたもの**（透かし）。
# 残った鉄は黒く、**抜かれた空だけが光る**。figure は、無い方だ。
#
# 造形：木瓜形（もっこうがた）の外周 r=R(1+m·cos4θ) と、
#       茎孔（なかごあな・縦の超楕円）＋左右の櫃孔（ひつあな・円）の**合併**でできた
#       ひとつの星形開口。板はこの二つの星形曲線に挟まれた領域＝極座標グリッドで
#       素直に張れる（**boolean 不使用**という掟を守るための骨格）。
#       断面は真ん中（切羽台）と外周（耳）が厚く、あいだが薄い＝実物の鍔の肉取り。
#
# 光：鍔そのものは**完全に黒**（漆レシピ）。ライムは板の裏に置いた発光板だけが持ち、
#     それは開口からしか見えない。＝**光は必ずシルエットの内側に収まる。**
#     🔴 これが 窓×端寄せ が成立する理由。背光は光が余白側へ漏れるので端寄せと組めない
#     （#74②／#67⑤／#71①／#72 の4例）。窓は光を被写体の投影内に閉じ込められる。
#
# 動き：面内の自転（360°＝厳密に閉じる）＋ 縦軸まわりのヨー（cos＝厳密に閉じる）。
#     🔴 光の量を変えている機構は**傾きそのもの**：孔を斜めから見ると、
#        短縮（cos）に加えて**孔自身の壁（肉厚）が入口を食う**ので、開口は二重に狭くなる。
#        ＝「回すと、孔が孔でなくなっていく」。#40⑥/光の振れ はこれで作る（#84 の逆）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52      # y=0 の平面での実効フレーム
LIME_W = 105.0                     # 随伴のライム光源（#58／#80⑤：シリーズ定数ではない）

# --- 鍔の骨格（実物：径 75〜85mm・厚 4〜6mm。すべて R_OUT に対する比）---
R_OUT  = 0.86                      # 外周の基準半径（木瓜の膨らみで最大 1.085 倍）
MOKKO  = 0.022                     # 竪丸形＋木瓜のささやき。🔴 0.15=手裏剣／0.045=丸い菱形に読めた
TATE   = 1.100                     # 縦長率（実物の鍔は縦がわずかに長い）
A_SE, B_SE, N_SE = 0.092, 0.40, 5.0  # 茎孔（縦長の超楕円）半幅／半長／角の立ち
SLOPE  = 0.26                        # 茎の細り：上へ行くほど狭い＝刀身の茎そのものの形
U_SEPPA = 0.30                       # 切羽台（孔のまわりの厚い台）が占める半径の割合
# --- 透かし（四方透かし）：意匠は彫るのではなく抜く。ここが作品の芯 ---
#     🔴 極座標グリッドの「セルを張らない」ことで抜く＝boolean 不使用のまま孔があく。
#        境界がグリッド線に一致するので縁が階段にならない。
SUK_N   = 4                          # 抜きの数（四方）
SUK_TH0 = math.pi / 4                # 最初の抜きの中心角（斜め45°＝上下左右に地を残す）
SUK_HW  = math.radians(27.0)         # 抜きの半角（地を太らせる＝ホイールに読ませない）
SUK_U0, SUK_U1 = 0.34, 0.60          # 抜きが占める半径の帯（u）
T_MAX, T_MIN = 0.078, 0.050
TSUCHI, TS_A, TS_R = 0.0030, 23.0, 5.0   # 鎚目：実ジオメトリの起伏（#52・Bumpでは出ない）        # 肉厚：切羽台と耳が厚く、あいだが薄い
NU, NT = 26, 176                   # 半径方向／周方向の分割

# --- 光（裏の発光板。#81④：halo は白へ抜ける広い勾配でしか出ない）-------
RG      = 0.72                     # 発光板の半径（透かし 0.65 より大・外周 0.978 より小＝完全に隠れる）
DBACK   = 0.085                    # 板の裏へ何ぼ下がるか（世界単位）
GEXP    = 1.25                     # E=1-(r/RG)^GEXP  芯が白・縁がライム
ES_CORE = 2.8
WHITE_FROM, WHITE_TO = 0.72, 0.80
K_MIX   = 16.0                     # #76①：不透明さを発光の強さから切り離す
E_FLOOR = 0.12                     # 🔴 #85①：これを引かないと K_MIX が面全体を発光へ転ばせる

# --- 動き --------------------------------------------------------
A_PHASE = -0.10                    # 自転の位相（STILL_FRAME で茎孔が垂直になるように）
BETA    = 42.0                     # ヨーの振幅（度）。cos で 0→BETA→0＝厳密に閉じる

# --- 置き方（端寄せ：画面の左 36% へ寄せ、右を余白として空ける）---
CX, CY, CZ = 0.157, 0.0, 2.16      # 画面 x≒36%（AIM_X から -0.393＝FRAME_W の 14%）
STILL_FRAME = 13                   # t=0.10 → 自転 0°（茎孔が垂直）・ヨー 4°


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def r_out_of(th):
    return R_OUT * (1.0 + MOKKO * math.cos(4.0 * th))


def r_ap_of(th):
    """開口＝茎孔（なかごあな）ひとつ。**上へ行くほど狭い楔**＝刀身の茎の断面そのもの。
       🔴 櫃孔は作らない。円の合併で作ると RHO>C_H（原点を含む）が要るので必ず太り、
          足し込む「耳」で作ると十字（＋）に読める——どちらも2周目に実際に出た。
          半幅 a を θ の関数にすれば、star-shape を保ったまま楔にできる。"""
    ca, sa = abs(math.cos(th)), abs(math.sin(th))
    a = A_SE * (1.0 - SLOPE * math.sin(th))          # 上（sin>0）で狭く、下で広い
    r = 1.0 / (((ca / a) ** N_SE + (sa / B_SE) ** N_SE) ** (1.0 / N_SE))
    return r * R_OUT


def stretch(x, y):
    """縦長率。極座標の r(θ) を保ったまま y だけ伸ばす（星形性は壊れない）"""
    return x, y * TATE


def smooth(e0, e1, x):
    if e1 == e0:
        return 0.0
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def thk_of(u, th=0.0):
    """切羽台（平らな台地）→ 谷 → 耳（縁の返し）。実物の鍔の肉取り。
       🔴 正弦一本だと台地が無く、面が「のっぺりした円盤」に読める（2周目）
       🔴 鎚目を足すのは意匠ではなく **黒に陰影を作るため**（#52／黒std・p98）"""
    if u <= U_SEPPA:
        k = 1.0 - 0.25 * smooth(U_SEPPA * 0.60, U_SEPPA, u)      # 切羽台の台地→肩
    else:
        v = (u - U_SEPPA) / (1.0 - U_SEPPA)
        # 🔴 地は「平ら」でなければ鍔に見えない。耳を長い距離でせり上げると
        #    面が曲面になり、兜／ホイールに読める（6周目に実際に出た）。
        #    耳は**最後の4%だけ**立てる＝縁に細い稜が出て、面は平らのまま。
        k = 0.75 - 0.75 * smooth(0.0, 0.22, v) + 0.55 * smooth(0.955, 1.0, v)
    ts = TSUCHI * math.sin(TS_A * th) * math.sin(TS_R * math.pi * u)
    return (T_MIN + (T_MAX - T_MIN) * k + ts) * R_OUT


def spin_of(t):
    return 2.0 * math.pi * (t + A_PHASE)


def yaw_of(t):
    return math.radians(BETA) * (0.5 - 0.5 * math.cos(2.0 * math.pi * t))


def rot3(t):
    """M = Rz(yaw) · Rx(+90°) · Rz(spin)。板は XY 平面で作る（法線 +Z）。
       Rx(+90°) で法線は -Y＝カメラ側を向く。純 math の 3x3（Blender 非依存）"""
    a, b = spin_of(t), yaw_of(t)
    ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    # Rz(a)
    Ra = ((ca, -sa, 0.0), (sa, ca, 0.0), (0.0, 0.0, 1.0))
    # Rx(90°)
    Rx = ((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0))
    # Rz(b)
    Rb = ((cb, -sb, 0.0), (sb, cb, 0.0), (0.0, 0.0, 1.0))
    def mul(A, B):
        return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3))
                     for i in range(3))
    return mul(Rb, mul(Rx, Ra))


def apply3(M, v):
    return tuple(sum(M[i][k] * v[k] for k in range(3)) for i in range(3))


def is_suk(u, th):
    """u,θ が透かしの帯に入っているか"""
    if not (SUK_U0 <= u <= SUK_U1):
        return False
    for i in range(SUK_N):
        th0 = SUK_TH0 + 2.0 * math.pi * i / SUK_N
        d = abs(math.atan2(math.sin(th - th0), math.cos(th - th0)))
        if d <= SUK_HW:
            return True
    return False


def inside_ap(px, py):
    """光が抜けてくる面＝茎孔 ∪ 透かし（縦長を戻してから極座標で測る）"""
    qy = py / TATE
    th = math.atan2(qy, px)
    r = math.hypot(px, qy)
    ra = r_ap_of(th)
    if r <= ra:
        return True
    ro = r_out_of(th)
    return is_suk((r - ra) / max(ro - ra, 1e-9), th)


def visible_light(t, n=90):
    """#40⑥ を**幾何で積分する**（レンダーのライム画素は Bloom で薄まる＝#47④）。
       孔は肉厚 T の角柱。裏面の点 (px,py) が見えるのは、視線が入口（表面の開口）も
       抜けるときだけ＝短縮 cos に加えて**壁が入口を食う**ぶんが効く。"""
    M = rot3(t)
    C = (CX, CY, CZ)
    # 視線（板の中心 → カメラ）。板ローカルへ落とす（M は直交なので転置＝逆）
    w = (CAM_LOC[0] - C[0], CAM_LOC[1] - C[1], CAM_LOC[2] - C[2])
    L = math.sqrt(sum(c * c for c in w))
    w = tuple(c / L for c in w)
    d = tuple(sum(M[k][i] * w[k] for k in range(3)) for i in range(3))   # Mᵀ·w
    cosang = abs(d[2])
    if cosang < 1e-6:
        return 0.0
    T = thk_of(0.0)                       # 開口まわりの肉厚（切羽台）
    sx, sy = d[0] / d[2] * T, d[1] / d[2] * T
    lim = SUK_U1 * R_OUT * TATE * 1.35
    hit = tot = 0
    for i in range(n):
        py = -lim + 2 * lim * (i + 0.5) / n
        for j in range(n):
            px = -lim + 2 * lim * (j + 0.5) / n
            if not inside_ap(px, py):
                continue
            tot += 1
            if inside_ap(px + sx, py + sy):   # 入口も抜けるか
                hit += 1
    if tot == 0:
        return 0.0
    cell = (2 * lim / n) ** 2
    return tot * cell * (hit / tot) * cosang


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
# 鍔は鉄地。tetsu 系は黒が沈みすぎるので、漆レシピの艶で「拾う黒」にする（#45）
URUSHI = dict(rough=0.28, spec=0.28, coat=0.02, coat_rough=0.25)


def apply_black(p):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = URUSHI["rough"]
    p.inputs["Specular IOR Level"].default_value = URUSHI["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = 0.0
    p.inputs["Coat Weight"].default_value = URUSHI["coat"]
    p.inputs["Coat Roughness"].default_value = URUSHI["coat_rough"]


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_iron, ip_ = principled("tetsu")
apply_black(ip_)


def glow_material(name):
    """E→0 側は黒（漆）へ戻す＝発光板の縁を作らない（#49①）。
       芯だけ白へ抜く＝halo はこの「白→ライム」の帯でしか出ない（#81④）"""
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
    apply_black(blk)

    # 🔴 #85①：E から E_FLOOR を引いてから K_MIX を掛ける。裾を切らないと面が全部光る
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = E_FLOOR
    nt.links.new(E, sub.inputs[0])
    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_MIX
    nt.links.new(sub.outputs[0], a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MAXIMUM'
    a2.inputs[1].default_value = 0.0
    nt.links.new(a1.outputs[0], a2.inputs[0])

    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("hikari")


# ---------- 造形（bmesh・実寸。boolean 不使用・object.scale 不使用）----------
def tsuba_mesh(name):
    """二つの星形曲線（開口・外周）に挟まれた領域を極座標グリッドで張る"""
    bm = bmesh.new()
    ths = [2 * math.pi * k / NT for k in range(NT)]
    ra = [r_ap_of(th) for th in ths]
    ro = [r_out_of(th) for th in ths]
    top, bot = [], []
    for i in range(NU + 1):
        u = i / NU
        rt, rb = [], []
        for k in range(NT):
            h = thk_of(u, ths[k]) * 0.5
            r = ra[k] + (ro[k] - ra[k]) * u
            x, y = stretch(r * math.cos(ths[k]), r * math.sin(ths[k]))
            rt.append(bm.verts.new((x, y, h)))
            rb.append(bm.verts.new((x, y, -h)))
        top.append(rt); bot.append(rb)
    # 🔴 透かし＝セルを張らない。境界がグリッド線に一致するので縁が階段にならない
    thm = [2 * math.pi * (k + 0.5) / NT for k in range(NT)]
    holed = [[is_suk((i + 0.5) / NU, thm[k]) for k in range(NT)] for i in range(NU)]

    def is_hole(i, k):
        return 0 <= i < NU and holed[i][k % NT]

    for i in range(NU):
        for k in range(NT):
            if holed[i][k]:
                continue
            k2 = (k + 1) % NT
            bm.faces.new((top[i][k], top[i][k2], top[i + 1][k2], top[i + 1][k]))
            bm.faces.new((bot[i][k], bot[i + 1][k], bot[i + 1][k2], bot[i][k2]))
    for k in range(NT):                       # 内壁（茎孔）と外壁（耳）
        k2 = (k + 1) % NT
        bm.faces.new((top[0][k], bot[0][k], bot[0][k2], top[0][k2]))
        bm.faces.new((top[NU][k], top[NU][k2], bot[NU][k2], bot[NU][k]))
    for i in range(NU):                       # 透かしの内壁（4辺ぶん）
        for k in range(NT):
            if not holed[i][k]:
                continue
            k2 = (k + 1) % NT
            if not is_hole(i - 1, k):         # 内側の縁
                bm.faces.new((top[i][k], bot[i][k], bot[i][k2], top[i][k2]))
            if not is_hole(i + 1, k):         # 外側の縁
                bm.faces.new((top[i + 1][k], top[i + 1][k2], bot[i + 1][k2], bot[i + 1][k]))
            if not is_hole(i, k - 1):         # 周方向の縁（手前）
                bm.faces.new((top[i][k], top[i + 1][k], bot[i + 1][k], bot[i][k]))
            if not is_hole(i, k + 1):         # 周方向の縁（奥）
                bm.faces.new((top[i][k2], bot[i][k2], bot[i + 1][k2], top[i + 1][k2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def glow_mesh(name):
    """裏の発光板。E=1-(r/RG)^GEXP＝芯が白・縁がライム（#81④の広い勾配）"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    emap = {}
    R = RG * R_OUT
    NR = 22
    hub = bm.verts.new((0.0, 0.0, 0.0)); emap[hub] = 1.0
    rings = []
    for i in range(1, NR + 1):
        u = i / NR
        ring = []
        for k in range(NT):
            th = 2 * math.pi * k / NT
            gx, gy = stretch(R * u * math.cos(th), R * u * math.sin(th))
            v = bm.verts.new((gx, gy, 0.0))
            emap[v] = max(0.0, 1.0 - u ** GEXP)
            ring.append(v)
        rings.append(ring)
    for k in range(NT):
        bm.faces.new((hub, rings[0][k], rings[0][(k + 1) % NT]))
    for i in range(NR - 1):
        for k in range(NT):
            k2 = (k + 1) % NT
            bm.faces.new((rings[i][k], rings[i + 1][k], rings[i + 1][k2], rings[i][k2]))
    bm.normal_update()
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = (emap[lp.vert], 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=1.0):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    return ob


ob_tsuba = link(tsuba_mesh("m_tsuba"), "tsuba", mat_iron, smooth=0.52)
ob_glow = link(glow_mesh("m_hikari"), "hikari", mat_glow)
# 🔴 孔の下の内壁に小さな白い三角（発光板の白い芯の映り込み）が出る。
#    `ob_glow.visible_glossy = False` で消そうとしたら**逆に増え**（51→345画素）、
#    さらにライムstd が 37.1→32.7 と #14 を割った＝映り込みが消えた面に
#    明るい環境光が入れ替わりで映るため。**材質でも ray visibility でも直らない。**
#    実物の透かし鍔も、逆光では抜きの切り口が光る。ここは直さず残す（10周目の判断）。
parts = [ob_tsuba, ob_glow]

# --- キーフレーム（毎フレーム打つ＝イージング不使用。回転は四元数＝glbで素直に閉じる）----
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev_q = None
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    M3 = rot3(t)
    M = Matrix(((M3[0][0], M3[0][1], M3[0][2], 0.0),
                (M3[1][0], M3[1][1], M3[1][2], 0.0),
                (M3[2][0], M3[2][1], M3[2][2], 0.0),
                (0.0, 0.0, 0.0, 1.0)))
    q = M.to_quaternion()
    if prev_q is not None and q.dot(prev_q) < 0.0:      # 🔴 符号を揃える（二重被覆）
        q.negate()
    prev_q = q.copy()
    back = apply3(M3, (0.0, 0.0, -DBACK))
    ob_tsuba.location = (CX, CY, CZ)
    ob_glow.location = (CX + back[0], CY + back[1], CZ + back[2])
    for ob in parts:
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
        caption("MIDDLE STUDY 076 — TSUBA", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (CX, 0.0, CZ)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：被写体は板1枚で背景を塞がない＝面光源が地に直接写ると白い帯になる
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。板の裏・下に置いて空間へ光を出す
for sx, sy, sz, w in ((-0.36, 2.2, 0.26, LIME_W), (0.10, 4.6, 0.26, LIME_W),
                      (0.62, 7.8, 0.26, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(CX + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = w
    lp.data.shadow_soft_size = 2.60
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0

world_d = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world_d; world_d.use_nodes = True
bgn = world_d.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 8.3 + 0.55
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは**全ジオメトリ生成後**に置く（#56②）。床を受光から外す
lit = bpy.data.collections.new("lit_by_back")
bpy.context.scene.collection.children.link(lit)
for o in parts:
    lit.objects.link(o)
back.light_linking.receiver_collection = lit

scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
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
    allx, ally = [], []
    for ob in parts:
        ev = ob.evaluated_get(dg)
        xs, ys = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
        print(">> %-12s x %6.3f..%6.3f  y %6.3f..%6.3f" % (ob.name, min(xs), max(xs),
                                                           min(ys), max(ys)))
        if ob is ob_tsuba:                    # 🔴 占有・重心は「見える物」＝鍔で測る
            allx += xs; ally += ys
    x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
    sl = max(0.0, min(x1, 1) - max(x0, 0))
    sh = max(0.0, min(y1, 1) - max(y0, 0))
    edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
    print(">> 全体 bbox x %.3f..%.3f y %.3f..%.3f" % (x0, x1, y0, y1))
    print(">> 🔴 長辺 %.1f%%（55〜65%%）  枠への接触 %d辺" % (max(sl, sh) * 100, edge))
    print(">> 🔴 重心x（幾何）%.1f%%（端寄せ＝|x-50|>=12）" % ((x0 + x1) / 2 * 100))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))
    vs = [visible_light(i / 24.0) for i in range(24)]
    print(">> 🔴 #40⑥ 見える発光面積 max/min = %.3f（光の振れの下限 1.22 に効く）"
          % (max(vs) / max(min(vs), 1e-9)))
    print(">>    内訳 max %.5f  min %.5f" % (max(vs), min(vs)))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_076.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_ir = bpy.data.materials.new("tsuba_glb"); m_ir.use_nodes = True
    pi = m_ir.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = URUSHI["rough"]
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.34
    ob_tsuba.data.materials[0] = m_ir
    ob_glow.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True,
                                  export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
