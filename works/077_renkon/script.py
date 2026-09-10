# =============================================================
# MIDDLE STUDY 077 — RENKON（蓮根 / 先を見通す）
#
#   光の型＝反復（#53）  構図の型＝対（#57・76作で初の組み合わせ）  ドメイン＝植物・根菜／蓮根
#
# 蓮根は「先が見通せる」から縁起物になった。
# けれど、その穴は **真ん中で切るまで、誰にも見えない**。
# 節の内側にしまわれていて、外からは黒い泥の塊にしか見えない。
#
# だから2つに切って、切り口どうしを離して置いた。あいだには何も無い。
# **無くなった一枚ぶんの厚みが、この作品の主題**＝ここが真ん中だ。
#
# 造形：断面を極座標で「二段の帯」として張る（rc→h0 ／ h1→rout）。
#       孔は (θ,r) 空間の超楕円で、帯の継ぎ目の1行を**張らないことで開く**（#87②の星形制約を、
#       原点まわりでなく **半径方向に2区間を持たせる**ことで回避した＝boolean 不使用のまま離れた孔があく）。
#       孔の角度の端では h0=h1 に潰れるので、孔の無い角度と**同じ頂点で連続する**。
#
# 光：孔の底（＝節の内側）だけが光る。壁の上半分は黒いまま＝**井戸の底の光**。
#     🔴 「対」で光を2つの物の**あいだ**に置くと塊マスクが繋がって落ちる（#83⑤）。
#        反復は光を各々の輪郭の内側に閉じ込められるので、対と噛み合う唯一の型のひとつ。
#     🔴 **中心の孔だけ浅くしてある**（0.052 / 外周は 0.085）。
#        傾けると外周の孔から順に壁が入口を食って消えていき、**真ん中の光だけが最後まで残る**。
#
# 動き：面外の首振り Φ(t)=50°→86°（cos＝厳密に閉じる）＋ 軸まわりの自転 360°（等速＝端で止まらない／#80⑥）。
#     光の量を変えているのは首振りそのもの：孔を斜めから見ると短縮 cos に加えて
#     **孔自身の壁（深さ）が入口を食う**ので二重に狭くなる（#84 の逆・076と同じ機構）。
#     自転が加わるので、**径方向に長い孔と接線方向に短い孔が入れ替わり**、光る孔の並びが毎フレーム変わる。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52      # y=0 の平面での実効フレーム
LIME_W = 130.0                     # 随伴のライム光源（#58／#80⑤：シリーズ定数ではない）

# --- 蓮根の骨格（実物：径 60〜80mm・節長 100〜150mm。すべて世界単位）---
R0     = 0.345                     # 断面の基準半径
NH     = 8                         # 外周の孔の数（＝外周の膨らみの数。実物は8〜10）
TH0    = math.pi / 2               # 最初の孔の中心角
MLOBE  = 0.016                     # 外周の膨らみ。🔴 0.075→0.050 でも「くしゃくしゃの黒い塊」だった（1〜2周目）。
                                   #    実物の蓮根は**外からは滑らかな筒**で、断面の花弁は外周にほとんど出ない
RC_H   = 0.555                     # 孔の環の半径（R0比）
HR_H   = 0.278                     # 孔の径方向の半径（R0比）＝径方向に長い涙形
DTH    = 0.336                     # 孔の角度半幅（rad）。隣との壁は 0.135rad ぶん残る＝実物どおり薄い
PSE    = 2.35                      # 超楕円の角の立ち（2=楕円は端が尖る／2.6で鈍端になる）
RCEN_H = 0.155                     # 中心孔（R0比）
L      = 0.955                     # 節の長さ
DEPTH   = 0.066                    # 外周の孔の底（＝節の内側）までの深さ
DEPTH_C = 0.040                    # 🔴 中心孔だけ浅い＝真ん中の光が最後まで残る
NT, NA, NB, NZ = 144, 5, 7, 26     # 周／内帯／外帯／軸方向の分割
TAPER  = 0.955                     # 🔴 孔をすぼめる＝孔の内側に黒い縁が立つ。
                                   #    真っ直ぐな孔だと光が縁まで届き、**孔ではなく緑のグミ**に見えた（2周目）

# --- 光（孔の底の発光面。#81④：halo は白へ抜ける広い勾配でしか出ない）-------
EW      = 0.40                     # 壁の底＝孔の縁での E（ここから内側で白へ抜ける）
GEXP    = 1.30                     # E = EW+(1-EW)(1-ρ^GEXP)
WEXP    = 1.45                     # 壁は E = EW·(z/depth)^WEXP（縁は 0＝黒のまま／#49①）
ES_CORE = 4.0
WHITE_FROM, WHITE_TO = 0.82, 0.78
K_MIX   = 16.0                     # #76①：不透明さを発光の強さから切り離す
E_FLOOR = 0.12                     # 🔴 #85①：これを引かないと K_MIX が面全体を発光へ転ばせる

# --- 動き --------------------------------------------------------
PHI0, DPHI = 40.0, 48.0            # 首振り（度）。cos で PHI0→PHI0+DPHI→PHI0＝厳密に閉じる
YAW_U, YAW_D = 30.0, -24.0         # 🔴 胴を真後ろでなく斜め後ろへ逃がす（1周目は胴が切り口の真裏に隠れ、
                                   #    「8枚の花びら」にしか読めなかった）。上下で角度を変え鏡像にしない
PH_U, PH_D = 0.18, 1.32            # 自転の初期位相（上下で違えて鏡像に見せない）

# --- 置き方（対：上下に離し、あいだを主題にする）---
CX, CY, CZ = 0.66, 0.0, 2.32       # 🔴 中央から右へ 0.11・上へ 0.16 ずらしてある。意匠ではなく
                                   #    **床に落ちた影を画面の外へ出すため**（#88①＝対の3つ目の塊は影だった）
ZOFF    = 0.480                    # 切り口の中心を CZ から上下へどれだけ離すか
STILL_FRAME = 23                   # t=22/120 → Φ≒54.2°（胴が筒として読める角度）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
RC   = RC_H * R0
HR   = HR_H * R0
RCEN = RCEN_H * R0


def smooth(e0, e1, x):
    if e1 == e0:
        return 0.0
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def sec_rout(th):
    """外周。膨らみ＋低次の歪み＝土の中で育った根の輪郭（真円は「部品」に見える）"""
    return R0 * (1.0 + MLOBE * math.cos(NH * (th - TH0))
                 + 0.008 * math.sin(3.0 * th + 0.7))


# 🔴 孔は8つとも同じ寸法にしない。完全な回転対称は「花／マンダラ」に読める（1周目の犯人の半分）
HJIT = ((1.00, 1.00, 1.000), (0.88, 1.04, 0.978), (1.09, 0.96, 1.026), (0.94, 1.02, 0.992),
        (1.05, 0.97, 1.018), (0.90, 1.05, 0.982), (1.03, 0.98, 1.008), (0.96, 1.03, 0.996))


def hole_band(th):
    """(h0,h1)＝孔の内側／外側の半径。孔に当たらない角度では h0==h1==RC に潰れる。
       🔴 この「潰れる」が骨格の芯：孔のある角度と無い角度が**同じ行数**で繋がる。"""
    for i in range(NH):
        jh, jd, jr = HJIT[i]
        thi = TH0 + 2.0 * math.pi * i / NH
        dth, rc, hr = DTH * jd, RC * jr, HR * jh
        d = math.atan2(math.sin(th - thi), math.cos(th - thi))
        if abs(d) < dth:
            s = abs(d) / dth
            H = hr * max(0.0, 1.0 - s ** PSE) ** (1.0 / PSE)
            return rc - H, rc + H
    return RC, RC


def sec_radii(th):
    """断面の格子：rc→h0（NA+1行）／ h1→rout（NB+1行）。index NA と NA+1 が孔の縁"""
    h0, h1 = hole_band(th)
    ro = sec_rout(th)
    rs = [RCEN + (h0 - RCEN) * (i / NA) for i in range(NA + 1)]
    rs += [h1 + (ro - h1) * (i / NB) for i in range(NB + 1)]
    return rs


def prof(w):
    """軸方向の太り：胴が膨らみ → 節でくびれ → 襟 → 端はドームで閉じる"""
    if w >= 1.0:
        return 0.0
    p = 1.0 + 0.060 * math.sin(math.pi * min(w / 0.68, 1.0))
    p -= 0.17 * smooth(0.60, 0.88, w)
    p -= 0.055 * math.exp(-((w - 0.80) / 0.038) ** 2)      # 節の溝（ここで根が継がれていた）
    if w > 0.86:
        u = (w - 0.86) / 0.14
        p *= math.sqrt(max(0.0, 1.0 - u * u))
    return p


def relief(th, w):
    """黒の肌は実ジオメトリで作る（#52）。縦の筋＝蓮根の皮。w=0（切り口）では 0"""
    return (0.009 * math.sin(17.0 * th + 1.7) * math.sin(math.pi * w) ** 0.6
            + 0.005 * math.sin(3.0 * math.pi * w) * math.sin(math.pi * w))


def phi_of(t):
    return math.radians(PHI0 + DPHI * (0.5 - 0.5 * math.cos(2.0 * math.pi * t)))


def _mul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3))
                 for i in range(3))


def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return ((1.0, 0.0, 0.0), (0.0, c, -s), (0.0, s, c))


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))


def rot3(t, upper):
    """上：Rz(YAW_U)·Rx(-Φ)·Rz(+2πt)  下：Rz(YAW_D)·Rx(π+Φ)·Rz(-2πt)
       切り口の法線 y 成分は -cos(YAW)·sinΦ＝カメラ側。ヨーで胴が横へ逃げるので**筒として読める**。"""
    ph = phi_of(t)
    if upper:
        return _mul(_rz(math.radians(YAW_U)), _mul(_rx(-ph), _rz(2.0 * math.pi * t + PH_U)))
    return _mul(_rz(math.radians(YAW_D)), _mul(_rx(math.pi + ph), _rz(-2.0 * math.pi * t + PH_D)))


def apply3(M, v):
    return tuple(sum(M[i][k] * v[k] for k in range(3)) for i in range(3))


def in_outer_holes(px, py):
    r = math.hypot(px, py)
    if r < 1e-9:
        return False
    th = math.atan2(py, px)
    h0, h1 = hole_band(th)
    return h1 > h0 and h0 < r < h1


def in_center_hole(px, py):
    return px * px + py * py < RCEN * RCEN


def visible_light(t, n=110):
    """#40⑥ を**幾何で積分する**（レンダーのライム画素は Bloom で薄まる＝#47④）。
       孔の底の点 (px,py) が見えるのは、視線が切り口の開口も抜けるときだけ
       ＝短縮 cos に加えて **壁が入口を食う** ぶんが効く。中心孔は浅いので別に積む。"""
    tot = 0.0
    for upper in (True, False):
        M = rot3(t, upper)
        C = (CX, CY, CZ + (ZOFF if upper else -ZOFF))
        w = (CAM_LOC[0] - C[0], CAM_LOC[1] - C[1], CAM_LOC[2] - C[2])
        Lw = math.sqrt(sum(c * c for c in w))
        w = tuple(c / Lw for c in w)
        d = tuple(sum(M[k][i] * w[k] for k in range(3)) for i in range(3))   # Mᵀ·w
        if abs(d[2]) < 1e-6:
            continue
        cosang = abs(d[2])
        lim = R0 * 1.10
        cell = (2 * lim / n) ** 2
        for depth, fn in ((DEPTH, in_outer_holes), (DEPTH_C, in_center_hole)):
            # 孔の底は z=+depth。視線を切り口（z=0）へ戻すと (px,py) は -shift だけずれる
            sx, sy = -d[0] / d[2] * depth, -d[1] / d[2] * depth
            hit = 0
            for i in range(n):
                py = -lim + 2 * lim * (i + 0.5) / n
                for j in range(n):
                    px = -lim + 2 * lim * (j + 0.5) / n
                    if fn(px, py) and fn(px + sx, py + sy):
                        hit += 1
            tot += hit * cell * cosang
    return tot


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
# 蓮根＝切ると少しざらつく実。`touki`（陶）。実起伏は DISPLACE ではなくメッシュに直に入れてある
# 🔴 表の 0.58／0.26 をそのまま当てたら、胴に**白い鏡面の筋**が縦に走り、
#    ①黒がプラスチックに見え ②その筋が明るすぎて塊マスクを断ち切り、節の側だけが
#    **3つ目の塊**になって `--verify 対` が落ちた（5周目）。粗くして鏡面で相殺する（MATERIALS.md 薄物の作法）
TOUKI = dict(rough=0.68, spec=0.30)


def apply_black(p):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = TOUKI["rough"]
    p.inputs["Specular IOR Level"].default_value = TOUKI["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = 0.0


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_body, bp_ = principled("renkon")
apply_black(bp_)


def glow_material(name):
    """E→0 側は黒（陶）へ戻す＝発光面の縁を作らない（#49①）。
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

THS = [2.0 * math.pi * k / NT for k in range(NT)]
RADII = [sec_radii(th) for th in THS]
NROW = NA + NB + 2


# ---------- 造形（bmesh・実寸。boolean 不使用・object.scale 不使用）----------
def body_mesh(name):
    """切り口（孔あき環）＋ 外周の胴 ＋ 端のドーム。孔の壁は発光側が持つ"""
    bm = bmesh.new()
    rows = []
    for j in range(NROW):
        rows.append([bm.verts.new((RADII[k][j] * math.cos(THS[k]),
                                   RADII[k][j] * math.sin(THS[k]), 0.0))
                     for k in range(NT)])
    # 切り口。🔴 j==NA の1行を張らないことで孔が開く（孔の無い角度では h0==h1 で潰れて連続）
    for j in range(NROW - 1):
        if j == NA:
            continue
        for k in range(NT):
            k2 = (k + 1) % NT
            bm.faces.new((rows[j][k], rows[j][k2], rows[j + 1][k2], rows[j + 1][k]))
    # 中心孔の底までの壁は発光側。切り口の内縁（rows[0]）はそこに接する
    # 胴（外周）
    outer = [rows[NROW - 1]]
    for jz in range(1, NZ + 1):
        w = jz / NZ
        p = prof(w)
        if p <= 1e-6:
            break
        ring = []
        for k in range(NT):
            r = sec_rout(THS[k]) * p * (1.0 + relief(THS[k], w))
            ring.append(bm.verts.new((r * math.cos(THS[k]), r * math.sin(THS[k]), L * w)))
        outer.append(ring)
    for a in range(len(outer) - 1):
        for k in range(NT):
            k2 = (k + 1) % NT
            bm.faces.new((outer[a][k], outer[a + 1][k], outer[a + 1][k2], outer[a][k2]))
    apex = bm.verts.new((0.0, 0.0, L))
    for k in range(NT):
        bm.faces.new((outer[-1][k], apex, outer[-1][(k + 1) % NT]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def glow_mesh(name):
    """孔の壁（上は黒・底で光る）＋ 孔の底の発光面。境界は body と同じ関数・同じ θ 標本"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    emap = {}

    def wall_and_plug(loop_xy, depth):
        """loop_xy＝切り口での閉じた境界（順序つき）。すぼまる壁を掘り、底を張る"""
        NW = 6
        M = len(loop_xy)
        cx = sum(x for x, _ in loop_xy) / M
        cy = sum(y for _, y in loop_xy) / M
        rings = []
        for a in range(NW + 1):
            z = depth * a / NW
            e = EW * (a / NW) ** WEXP
            sc = 1.0 - (1.0 - TAPER) * (a / NW)
            ring = []
            for (x, y) in loop_xy:
                v = bm.verts.new((cx + (x - cx) * sc, cy + (y - cy) * sc, z))
                emap[v] = e; ring.append(v)
            rings.append(ring)
        for a in range(NW):
            for k in range(M):
                k2 = (k + 1) % M
                bm.faces.new((rings[a][k], rings[a][k2], rings[a + 1][k2], rings[a + 1][k]))
        # 底：境界点を中心へ相似縮小（超楕円も円も相似で内側に収まる）
        NR = 6
        plug = [rings[NW]]
        for b in range(1, NR):
            rho = 1.0 - b / NR
            ring = []
            for (x, y) in loop_xy:
                v = bm.verts.new((cx + (x - cx) * TAPER * rho,
                                  cy + (y - cy) * TAPER * rho, depth))
                emap[v] = EW + (1.0 - EW) * (1.0 - rho ** GEXP)
                ring.append(v)
            plug.append(ring)
        hub = bm.verts.new((cx, cy, depth)); emap[hub] = 1.0
        for b in range(len(plug) - 1):
            for k in range(M):
                k2 = (k + 1) % M
                bm.faces.new((plug[b][k], plug[b + 1][k], plug[b + 1][k2], plug[b][k2]))
        for k in range(M):
            bm.faces.new((plug[-1][k], hub, plug[-1][(k + 1) % M]))

    # 外周の孔：body と同じ θ 標本で境界を作る（＝縁に隙間が出ない）
    for i in range(NH):
        thi = TH0 + 2.0 * math.pi * i / NH
        ks = [k for k in range(NT)
              if abs(math.atan2(math.sin(THS[k] - thi), math.cos(THS[k] - thi))) < DTH]
        ks.sort(key=lambda k: math.atan2(math.sin(THS[k] - thi), math.cos(THS[k] - thi)))
        outer_side = [(RADII[k][NA + 1] * math.cos(THS[k]),
                       RADII[k][NA + 1] * math.sin(THS[k])) for k in ks]
        inner_side = [(RADII[k][NA] * math.cos(THS[k]),
                       RADII[k][NA] * math.sin(THS[k])) for k in reversed(ks)]
        wall_and_plug(outer_side + inner_side, DEPTH)
    # 中心孔（body の内縁 rows[0] と同じ半径・同じ θ 標本）
    wall_and_plug([(RCEN * math.cos(th), RCEN * math.sin(th)) for th in THS], DEPTH_C)

    bm.normal_update()
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = (emap[lp.vert], 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth_ang=1.0):
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
    return ob


me_body, me_glow = body_mesh("m_renkon"), glow_mesh("m_hikari")
ob_bu = link(me_body, "renkon_up", mat_body, smooth_ang=0.62)
ob_bd = link(me_body.copy(), "renkon_dn", mat_body, smooth_ang=0.62)
ob_gu = link(me_glow, "hikari_up", mat_glow, smooth_ang=0.55)
ob_gd = link(me_glow.copy(), "hikari_dn", mat_glow, smooth_ang=0.55)
parts = [ob_bu, ob_gu, ob_bd, ob_gd]
bodies = [ob_bu, ob_bd]

# --- キーフレーム（毎フレーム打つ＝イージング不使用。回転は四元数＝glbで素直に閉じる）----
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev = {}
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    for upper, obs in ((True, (ob_bu, ob_gu)), (False, (ob_bd, ob_gd))):
        M3 = rot3(t, upper)
        M = Matrix(((M3[0][0], M3[0][1], M3[0][2], 0.0),
                    (M3[1][0], M3[1][1], M3[1][2], 0.0),
                    (M3[2][0], M3[2][1], M3[2][2], 0.0),
                    (0.0, 0.0, 0.0, 1.0)))
        q = M.to_quaternion()
        if upper in prev and q.dot(prev[upper]) < 0.0:      # 🔴 符号を揃える（二重被覆）
            q.negate()
        prev[upper] = q.copy()
        for ob in obs:
            ob.location = (CX, CY, CZ + (ZOFF if upper else -ZOFF))
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
        caption("MIDDLE STUDY 077 — RENKON", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：被写体は2つに割れていて**あいだが素通し**＝面光源が地に直接写ると白い帯になる
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。あいだの奥・床寄りに置いて空間へ光を出す
for sx, sy, sz, wt in ((-0.30, 2.0, 0.30, LIME_W), (0.14, 4.2, 0.30, LIME_W),
                       (0.58, 7.2, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(CX + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = wt
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
cam.data.dof.focus_distance = 8.3
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
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME,
      " Φ(hero) = %.1f°" % math.degrees(phi_of((STILL_FRAME - 1) / N_FRAMES)))

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
        if ob in bodies:
            allx += xs; ally += ys
    x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
    sl = max(0.0, min(x1, 1) - max(x0, 0))
    sh = max(0.0, min(y1, 1) - max(y0, 0))
    edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
    print(">> 全体 bbox x %.3f..%.3f y %.3f..%.3f" % (x0, x1, y0, y1))
    print(">> 🔴 長辺 %.1f%%（55〜65%%）  枠への接触 %d辺" % (max(sl, sh) * 100, edge))
    # 対：上下の塊のあいだが画面で何%空いているか
    up = ob_bu.evaluated_get(dg); dn = ob_bd.evaluated_get(dg)
    uy = [world_to_camera_view(scene, cam, up.matrix_world @ v.co).y for v in up.data.vertices]
    dy = [world_to_camera_view(scene, cam, dn.matrix_world @ v.co).y for v in dn.data.vertices]
    print(">> 🔴 あいだ %.1f%%（上の下端 %.1f%% − 下の上端 %.1f%%）"
          % ((min(uy) - max(dy)) * 100, min(uy) * 100, max(dy) * 100))
    print(">> 重心x（幾何）%.1f%%  重心y %.1f%%" % ((x0 + x1) / 2 * 100, (y0 + y1) / 2 * 100))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))
    vs = [visible_light(i / 24.0) for i in range(24)]
    print(">> 🔴 #40⑥ 見える発光面積 max/min = %.3f（光の振れの下限 1.22 に効く）"
          % (max(vs) / max(min(vs), 1e-9)))
    print(">>    内訳 max %.5f  min %.5f  hero %.5f"
          % (max(vs), min(vs), visible_light((STILL_FRAME - 1) / N_FRAMES)))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_077.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("renkon_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = TOUKI["rough"]
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.34
    for o in bodies:
        o.data.materials[0] = m_bk
    for o in (ob_gu, ob_gd):
        o.data.materials[0] = m_em
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
