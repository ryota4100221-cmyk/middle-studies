# =============================================================
# MIDDLE STUDY 057 — KOSHIKI（轂 / 車輪の真ん中 the nave of a wheel）
#
# 黒い車輪が、枠に収まらない大きさで宙にある。輻（や）が十二本、真ん中の轂（こしき）に集まる。
# その轂は、空（うつろ）だ。輪が輪であるのは、真ん中に何も無いからだ。
# 空洞のいちばん奥に、軸の木口がある。そこだけが ライム #A5E02E に光っている。
# 輪が転がって行くと、筒の口が奥の光を斜めに切って、光は細る。
# 真ん中へ戻ってきたときにだけ、光はまた満ちる。
# **輪はまわる。軸はまわらない。光っているのは、まわらない方だ。**
#
# 🔴 光の型＝**芯**（#53：中心の小さな塊。周りは黒。直近は 050 KENDAMA＝7作前）
#    背光を捨てた理由：背光は「光源が被写体の背後にあり、黒は縁だけ光る」＝
#    **輪郭が枠の外に出る「寄り」とは原理的に両立しない**（縁が画面に無い）。
# 🔴 構図の型＝**寄り**（#57：56作中51作が「全身」。寄りは 053 UKIDAMA の1作のみ）
#    輪の外周は左・右・上の3辺で切れ、下の弧だけが画面に残る。
#    edge≥1・長辺78%以上（`compositions.py --verify` で機械検査する）。
# 【ドメイン】運搬・車輪（シリーズ未踏）。直近10作＝盤上遊戯/鋳造/植物・果実/漁労/楽器・打/
#            貨幣/玩具・けん玉/武・弓/農・製粉/商い・暖簾 と別。
#            013 HAGURUMA【道具・構造】は噛み合う歯車2枚＝輻も轂も無く、機構が別物。
#
# 機構＝**転がり（rolling without slipping）＝シリーズ初**。
#   x(t) = X0 + A·sin(2πt)、θ(t) = θ0 + (x(t) − X0)/R_ROLL。
#   転がりの拘束（弧長＝移動距離）がそのまま両者を結ぶので、**位相を合わせる調整値が無い**。
#   整数周期で厳密に閉じ、**位置キーと回転キーだけ**なので glb に乗る（#60）。
#   🔴 軸だけは輪の子にしない＝**位置は追うが回転しない**。これが主題そのもの。
#
# 光の明滅＝**筒による口径食（vignetting through the bore）**。
#   奥の木口（半径 R_AX・y=+AX_Y）を、手前の口（半径 R_BORE・y=−L_NAVE/2）越しに見る。
#   カメラから見た2円の重なりが、そのまま見える発光面。**発光の値を1つも動かさずに光が呼吸する。**
#   #40⑥ は幾何で積分（circ_overlap）＝ min/max 0.73（合格 0.75以下）。
#
# 🔴 造形は全部 lathe（轆轤）と押し出しで、boolean 不使用（#15/#37②）。
# 🔴 輻は**互い違いに前後へ振って轂に挿す**（実物の dish）。これが無いと正対で花に読める（#64①）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 輪（felloe ＋ 輪金）----------------------------------------
R_TYRE_OUT = 2.050             # 輪金の外径＝転がり半径
R_TYRE_IN  = 2.005
R_FEL_OUT  = 2.005             # 木の輪（羽）
R_FEL_IN   = 1.575
WY_FEL     = 0.150             # 輪の半幅（y方向）
WY_TYRE    = 0.150

# --- 輻（spokes）------------------------------------------------
N_SPOKE  = 12
SP_R0, SP_R1 = 0.360, 1.660    # 轂の肩 → 羽の中へ
SP_W0, SP_W1 = 0.098, 0.062    # 接線方向の半幅
SP_D0, SP_D1 = 0.088, 0.066    # y方向の半厚
DISH     = 0.080               # 🔴 轂側で互い違いに前後へ振る（実物の dish）
SP_PHASE = math.radians(13.0)  # 🔴 正対でも鏡映対称にしない（花・アイコン化の回避）

# --- 轂（nave）--------------------------------------------------
L_NAVE  = 0.50                 # 半長（y = ∓0.50）
R_BORE  = 0.190                # 空洞（＝手前の口。ここが絞りになる）
# 🔴 2周目：口の肉が 0.03 しか無く、光が轂の端いっぱいまで来て**緑のボタン**になった。
#    口のまわりに黒い環（0.10）を残すと、初めて「奥に光がある穴」に読める（#65④ の同型）。
NAVE_PROFILE = [(-0.500, 0.320), (-0.430, 0.345), (-0.300, 0.372), (-0.180, 0.405),
                ( 0.180, 0.405), ( 0.300, 0.372), ( 0.430, 0.345), ( 0.500, 0.320)]
# 🔴 1周目：箍を4本入れたら、轂が**カメラのレンズ鏡胴**に見えた（#48 の「ロータリーノブ」と同型）。
#    同心の輪を積むほど機械になる。実物の車輪も箍は端の2本なので、2本に落とす。
HOOPS = [(-0.400, 0.055, 0.348, 0.370), (0.400, 0.055, 0.348, 0.370)]   # (y, 半幅, r内, r外)

# --- 軸（axle）-------------------------------------------------
AX_Y   = 0.300                 # 木口の y（＝手前の口から 0.80 奥）
R_AX   = 0.178                 # 空洞 0.190 との差 0.012 ＝ 挿さっている隙
AX_END = 1.100                 # 軸の後端

# --- 舞台 ------------------------------------------------------
X0, Z_C = 0.55, 3.10           # 轂の中心（X0 はカメラの光軸に合わせる＝AIM_X）
# 🔴 輪を「寄り」に見せるには、輪の下端がキャプション帯を割ってはいけない（1周目は文字の上に載った）。
#    下端 ≥ 画面下から24%・轂は枠の上寄り＝**見上げる大きな輪**。この制約で R と Z_C は一意に決まる。
LEAN    = math.radians(4.2)     # 🔴 空洞の軸をカメラへ向けて倒す（後述の口径食が hero で片寄らないため）
A_ROLL  = 1.400                # 転がる振幅
R_ROLL  = R_TYRE_OUT
FPS, N_FRAMES = 24, 120
CAM_LOC  = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
LIME_W = 115.0                 # 随伴のライム光源（#58）。**発光体の外**・**奥**に置く（#64③）

# --- 木口の発光 -------------------------------------------------
# 🔴 1周目は ES 17.0＋急な勾配で、木口が**緑の球**になった（芯でなく玉）。
#    奥に沈んだ切り口は「平らで、少しだけ中心が明るい」。強さでなく勾配を寝かせて直す。
ES_CORE  = 5.5
EM_BASE  = 0.58                # 縁で 0 にしない（縁の外は黒い筒の中＝#49 の事故は起きない）
EM_P     = 1.00
FAC_LO, FAC_P = 0.90, 1.0      # #65②③：純発光体に法線依存を弱く掛ける（強いと凹が凸に転ぶ）

SEG = 64                       # 回転体の分割
FRAME_W, FRAME_H = 2.81, 3.52  # 被写体面での枠（85mm・8.3m・4:5）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def x_of(t):
    return X0 + A_ROLL * math.sin(2.0 * math.pi * t)


def theta_of(t):
    """転がりの拘束：回した弧長＝進んだ距離。位相を合わせる調整値は無い"""
    return SP_PHASE + (x_of(t) - X0) / R_ROLL


def circ_overlap(d, R, r):
    """2円の重なり面積（d=中心間距離）"""
    if d >= R + r:
        return 0.0
    if d <= abs(R - r):
        return math.pi * min(R, r) ** 2
    a1 = math.acos((d * d + R * R - r * r) / (2 * d * R))
    a2 = math.acos((d * d + r * r - R * R) / (2 * d * r))
    return (R * R * (a1 - math.sin(2 * a1) / 2) + r * r * (a2 - math.sin(2 * a2) / 2))


def bore_visible(t):
    """#40⑥ は幾何で積分する（#46/#64②）＝**見えている発光面**。
       空洞の軸 u（LEAN で倒れている）上に、手前の口（半径 R_BORE）と奥の木口（半径 R_AX）がある。
       木口をカメラから口の平面へ中心投影し、2円の重なりを取る＝そのまま見える発光面。
       🔴 発光の値は1つも動かさない。**動くのは輪だけで、光はその結果として呼吸する。**"""
    xh = x_of(t)
    H = (xh, 0.0, Z_C)
    u = (0.0, -math.cos(LEAN), -math.sin(LEAN))          # 空洞の軸（カメラ側が正）
    P_lip = tuple(H[i] + u[i] * L_NAVE for i in range(3))
    P_ax = tuple(H[i] - u[i] * AX_Y for i in range(3))
    C = CAM_LOC
    dot = lambda a, b: sum(a[i] * b[i] for i in range(3))
    sub = lambda a, b: tuple(a[i] - b[i] for i in range(3))
    s = dot(sub(P_lip, C), u) / dot(sub(P_ax, C), u)      # 木口を口の平面へ縮める率
    P = tuple(C[i] + s * (P_ax[i] - C[i]) for i in range(3))
    d = math.dist(P, P_lip)
    return circ_overlap(d, R_BORE, s * R_AX) / (s * s)    # 木口の面に戻す


_VS = [bore_visible(i / N_FRAMES) for i in range(N_FRAMES)]
_VMAX = max(_VS)
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _VS[i]) + 1

if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d (t=%.3f)" % (STILL_FRAME, (STILL_FRAME - 1) / N_FRAMES))
    print(">> #40(6) 見える光 min/max = %.3f  （合格 0.75以下）" % (min(_VS) / _VMAX))
    print(">> ループの閉じ: V(0)=%.6f V(1)=%.6f  差 %.2e"
          % (_VS[0], bore_visible(1.0), abs(_VS[0] - bore_visible(1.0))))
    print(">> 転がりの閉じ: x(0)=%.4f x(1)=%.4f  θ(0)=%.4f θ(1)=%.4f"
          % (x_of(0), x_of(1), theta_of(0), theta_of(1)))
    print(">> 回転の振れ ±%.1f°（輻の間隔 %.1f°）"
          % (math.degrees(A_ROLL / R_ROLL), 360.0 / N_SPOKE))
    print(">> 発光面 全開 %.4f m² ＝ 枠 %.4f m² の %.2f%%（#51 の帯 0.8〜12.0）"
          % (_VMAX, FRAME_W * FRAME_H, _VMAX / (FRAME_W * FRAME_H) * 100))
    # 枠（被写体面）に対する輪の当たり
    fx0, fx1 = AIM_X - FRAME_W / 2, AIM_X + FRAME_W / 2
    fz0, fz1 = LOOK_Z - FRAME_H / 2, LOOK_Z + FRAME_H / 2
    print(">> 枠 x %.2f..%.2f  z %.2f..%.2f" % (fx0, fx1, fz0, fz1))
    print(">> 輪 z %.2f..%.2f （下端が枠内＝%s／上端は切れる＝%s）"
          % (Z_C - R_ROLL, Z_C + R_ROLL, Z_C - R_ROLL > fz0, Z_C + R_ROLL > fz1))
    hh = min(fz1, Z_C + R_ROLL) - (Z_C - R_ROLL)
    print(">> 見える縦の広がり %.2f ＝ 枠の %.1f%%（「寄り」は 78%% 以上）" % (hh, hh / FRAME_H * 100))
    for i in range(0, N_FRAMES, 10):
        t = i / N_FRAMES
        print("   t=%.3f  x=%+.3f  θ=%+6.1f°  光 %5.1f%%"
              % (t, x_of(t), math.degrees(theta_of(t)), 100 * _VS[i] / _VMAX))
    sys.exit(0)


# =============================================================
# ここから Blender
# =============================================================
import bpy, bmesh                                        # noqa: E402
from mathutils import Vector                             # noqa: E402


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
    "base":   dict(rough=0.36, spec=0.15, coat=0.05),
    "urushi": dict(rough=0.30, spec=0.34, coat=0.05, coat_rough=0.25),
    "touki":  dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10),
    # 🔴 車輪の木＝`touki` を**この形に合わせて振り直した値**（MATERIALS.md「レシピの値は
    #    その形で検証した値でしかない」／#62③）。羽の内縁と輻の小口が長い直線の稜線なので、
    #    0.58 のままだと**白い環境を映した一本の白線**になり、芯より目立つ。
    #    粗さを上げて稜線のハイライトを散らし、沈む黒は鏡面で戻す（nuno_usu と同じ手当て）。
    "ki":     dict(rough=0.68, spec=0.32, disp=0.006, dsize=0.10),
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25, disp=0.004, dsize=0.05),
    "nuno_usu": dict(rough=0.66, spec=0.28, sheen=0.55, sheen_rough=0.25),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
    # 空洞の内壁。**筒の中は見えることが仕事だが、緑に染まってはいけない**。
    # #57②/#66④：#0a0a0a の金属は反射がベースカラーで色づく＝ライムを浴びても黒いまま。
    "bore":   dict(rough=0.62, spec=0.24, metal=0.85),
    # 🔴 羽（felloe）の**内壁**専用。3周目の最大の事故＝ここが白い帯に光っていた。
    #    誘電体の黒は、視線とすれすれの面では Fresnel が 1 に漸近するので
    #    **鏡面値を下げても粗さを上げても白い床を映す**（#47 の映り込みの、曲面版）。
    #    #57②/#66④：#0a0a0a の**金属**は反射がベースカラーで色づく＝白を浴びても黒いまま。
    "rim_in": dict(rough=0.70, spec=0.20, metal=0.95),
}
# 車輪は実物が **木（羽・輻・轂）＋ 鉄（輪金・箍）** なので2素材で正しい（MATERIALS.md 掟4の例外）
WOOD_R, IRON_R = "ki", "tetsu"


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def set_black(p, recipe):
    r = BLACK_RECIPES[recipe]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)
    if r.get("sheen"):
        p.inputs["Sheen Weight"].default_value = r["sheen"]
        p.inputs["Sheen Roughness"].default_value = r.get("sheen_rough", 0.25)
    return p


def black_material(name, recipe):
    m, p = principled(name)
    set_black(p, recipe)
    return m


mat_wood = black_material("wood", WOOD_R)
mat_iron = black_material("iron", IRON_R)
mat_bore = black_material("bore", "bore")
mat_rimin = black_material("rim_in", "rim_in")


def kiguchi_material(name):
    """木口＝軸の切り口に溜まった光。勾配は **UV に焼いた半径**（#34/#39）。
       u = r/R_AX：中心が芯・縁で EM_BASE。縁の外は黒い筒の内壁なので #49 の事故は起きない。
       🔴 #65②③：純発光体は法線依存の項が無いと形が消えるが、強いと凹が凸に転ぶ。弱く掛ける。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)
    p.inputs["Roughness"].default_value = 0.55
    p.inputs["Specular IOR Level"].default_value = 0.10
    p.inputs["Emission Color"].default_value = LIME

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    fr = nt.nodes.new("ShaderNodeMapRange")
    fr.interpolation_type = 'SMOOTHSTEP'; fr.clamp = True
    fr.inputs["From Min"].default_value = 0.0; fr.inputs["From Max"].default_value = 1.0
    fr.inputs["To Min"].default_value = 1.0; fr.inputs["To Max"].default_value = 0.0
    nt.links.new(xyz.outputs["X"], fr.inputs["Value"])
    frp = mn('POWER', EM_P); nt.links.new(fr.outputs["Result"], frp.inputs[0])
    frs = mn('MULTIPLY', 1.0 - EM_BASE); nt.links.new(frp.outputs[0], frs.inputs[0])
    fra = mn('ADD', EM_BASE); nt.links.new(frs.outputs[0], fra.inputs[0])

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    fcp = mn('POWER', FAC_P); nt.links.new(lw.outputs["Facing"], fcp.inputs[0])
    fcs = mn('MULTIPLY', 1.0 - FAC_LO); nt.links.new(fcp.outputs[0], fcs.inputs[0])
    fca = mn('ADD', FAC_LO); nt.links.new(fcs.outputs[0], fca.inputs[0])

    e1 = mn('MULTIPLY'); nt.links.new(fra.outputs[0], e1.inputs[0])
    nt.links.new(fca.outputs[0], e1.inputs[1])
    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e1.outputs[0], e2.inputs[0])
    nt.links.new(e2.outputs[0], p.inputs["Emission Strength"])
    return m


mat_kiguchi = kiguchi_material("kiguchi")

mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
def finish_mesh(bm, name, bevel=0.0018, angle=32, smooth=True):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    sharp = []
    for e in bm.edges:
        try:
            if e.calc_face_angle() > math.radians(angle):
                sharp.append(e)
        except Exception:
            pass
    if sharp and bevel > 0:                       # #17：稜線が光を拾わないと黒はプラスチックになる
        bmesh.ops.bevel(bm, geom=sharp, offset=bevel, segments=2,
                        affect='EDGES', clamp_overlap=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me["_smooth"] = smooth
    return me


def link(me, name, mat, parent, mat2=None):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if not ob.data.materials:
        ob.data.materials.append(mat)
        if mat2 is not None:
            ob.data.materials.append(mat2)
    ob.parent = parent
    if me.get("_smooth"):
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        try:
            bpy.ops.object.shade_auto_smooth(angle=0.35)
        except Exception:
            pass
        ob.select_set(False)
    return ob


def ring_verts(bm, y, r, seg=SEG):
    return [bm.verts.new((r * math.cos(2 * math.pi * s / seg), y,
                          r * math.sin(2 * math.pi * s / seg))) for s in range(seg)]


def bridge(bm, a, b, seg=SEG, store=None):
    for s in range(seg):
        f = bm.faces.new([a[s], a[(s + 1) % seg], b[(s + 1) % seg], b[s]])
        if store is not None:
            store.append(f)


def annulus_ring(bm, rings, store=None):
    """(y, r) の並びを順に橋渡しして閉じた回転体の帯にする"""
    for a, b in zip(rings, rings[1:]):
        bridge(bm, a, b, store=store)


def band_mesh(name, y_half, r_in, r_out, split_inner=False):
    """矩形断面の輪（羽・輪金・箍）。4面を巻いた閉じた輪。
       split_inner=True で**内壁だけ**をマテリアル1に分ける（白い床の映り込み対策）。
       🔴 断面の頂点は4つ。最初と最後に同じ点を重ねて書くと**二重頂点で稜線に裂け目**ができ、
          そこが白い一本線に光る（5周目に実際に踏んだ）。巻き戻して閉じる。"""
    bm = bmesh.new()
    quad = [(-y_half, r_out), (y_half, r_out), (y_half, r_in), (-y_half, r_in)]
    rings = [ring_verts(bm, y, r) for y, r in quad]
    faces = [[] for _ in range(4)]
    for k in range(4):
        bridge(bm, rings[k], rings[(k + 1) % 4], store=faces[k])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if split_inner:
        inner = set(id(f) for f in faces[2])
        for f in bm.faces:
            f.material_index = 1 if id(f) in inner else 0
    return finish_mesh(bm, name, bevel=0.0022, smooth=False)


def spokes_mesh():
    """輻12本。轂側の y 中心を互い違いに ±DISH へ振る（実物の dish）＝正対でも平らな花にしない。"""
    bm = bmesh.new()
    NR = 5
    for k in range(N_SPOKE):
        ang = SP_PHASE_LOCAL + 2 * math.pi * k / N_SPOKE
        ca, sa = math.cos(ang), math.sin(ang)
        dsh = DISH if k % 2 == 0 else -DISH
        rings = []
        for j in range(NR + 1):
            u = j / NR
            r = SP_R0 + (SP_R1 - SP_R0) * u
            w = SP_W0 + (SP_W1 - SP_W0) * u
            d = SP_D0 + (SP_D1 - SP_D0) * u
            yc = dsh * (1.0 - u) ** 1.4                 # 轂側で振れ、羽では 0 に戻る
            vs = []
            for (dw, dy) in ((-w, -d), (w, -d), (w, d), (-w, d)):
                x = r * ca - dw * sa
                z = r * sa + dw * ca
                vs.append(bm.verts.new((x, yc + dy, z)))
            rings.append(vs)
        for a, b in zip(rings, rings[1:]):
            for s in range(4):
                bm.faces.new([a[s], a[(s + 1) % 4], b[(s + 1) % 4], b[s]])
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])
    return finish_mesh(bm, "spokes", bevel=0.004, smooth=False)


def nave_mesh():
    """轂＝外は樽・中は貫通した空洞。スロット 0=木 / 1=空洞の内壁。"""
    bm = bmesh.new()
    outer, bore, ends = [], [], []
    o_rings = [ring_verts(bm, y, r) for y, r in NAVE_PROFILE]
    annulus_ring(bm, o_rings, store=outer)
    b_rings = [ring_verts(bm, y, R_BORE) for y in
               (-L_NAVE, -0.25, 0.0, 0.25, L_NAVE)]
    annulus_ring(bm, b_rings, store=bore)
    # 端の輪（口の縁）
    for oi, bi, flip in ((0, 0, True), (-1, -1, False)):
        a, b = o_rings[oi], b_rings[bi]
        for s in range(SEG):
            f = bm.faces.new([a[s], a[(s + 1) % SEG], b[(s + 1) % SEG], b[s]])
            ends.append(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ids = set(id(f) for f in bore)
    for f in bm.faces:
        f.material_index = 1 if id(f) in ids else 0
    me = bpy.data.meshes.new("nave"); bm.to_mesh(me); bm.free()
    me["_smooth"] = True
    return me


def axle_mesh():
    """軸＝丸棒。スロット 0=木 / 1=木口（発光）。UV.x に r/R_AX を焼く（#39）。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    side = []
    s_rings = [ring_verts(bm, y, R_AX) for y in (AX_Y, AX_Y + 0.35, AX_END)]
    annulus_ring(bm, s_rings, store=side)
    # 木口（手前・−Y を向く面）。中心から放射に張る
    face = []
    NRR = 12
    rings = [s_rings[0]]
    for k in range(NRR - 1, 0, -1):
        rings.append(ring_verts(bm, AX_Y, R_AX * k / NRR))
    cen = bm.verts.new((0.0, AX_Y, 0.0))
    for a, b in zip(rings, rings[1:]):
        for s in range(SEG):
            face.append(bm.faces.new([a[s], a[(s + 1) % SEG], b[(s + 1) % SEG], b[s]]))
    for s in range(SEG):
        face.append(bm.faces.new([rings[-1][s], rings[-1][(s + 1) % SEG], cen]))
    # 後端の蓋
    face_back = bm.faces.new(s_rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    fid = set(id(f) for f in face)
    for f in bm.faces:
        f.material_index = 1 if id(f) in fid else 0
        for lp in f.loops:
            q = lp.vert.co
            lp[uvl].uv = (min(1.0, math.hypot(q.x, q.z) / R_AX), 0.5)
    me = bpy.data.meshes.new("axle"); bm.to_mesh(me); bm.free()
    me["_smooth"] = True
    return me


# ---------- 配置 ----------
SP_PHASE_LOCAL = 0.0           # 位相は親の回転で与える（輻の並びはローカルでは 0 起点）

tilt = bpy.data.objects.new("tilt", None)       # 倒し（空洞の軸をカメラへ向ける）
bpy.context.collection.objects.link(tilt)
tilt.rotation_euler = (LEAN, 0.0, 0.0)
wheel = bpy.data.objects.new("wheel", None)     # まわる方
bpy.context.collection.objects.link(wheel)
wheel.parent = tilt
axle_pivot = bpy.data.objects.new("axle_pivot", None)   # 🔴 まわらない方
bpy.context.collection.objects.link(axle_pivot)
axle_pivot.parent = tilt

parts = []
parts.append(link(band_mesh("felloe", WY_FEL, R_FEL_IN, R_FEL_OUT, split_inner=True),
                  "felloe", mat_wood, wheel, mat_rimin))
parts.append(link(band_mesh("tyre", WY_TYRE, R_TYRE_IN, R_TYRE_OUT), "tyre", mat_iron, wheel))
parts.append(link(spokes_mesh(), "spokes", mat_wood, wheel))
parts.append(link(nave_mesh(), "nave", mat_wood, wheel, mat_bore))
for i, (y, hw, ri, ro) in enumerate(HOOPS):
    ob = link(band_mesh("hoop%d" % i, hw, ri, ro), "hoop%d" % i, mat_iron, wheel)
    ob.location = (0.0, y, 0.0)
    parts.append(ob)
axle_ob = link(axle_mesh(), "axle", mat_wood, axle_pivot, mat_kiguchi)
parts.append(axle_ob)

# 🔴 黒の肌は実ジオメトリ（#52）。**箱状の部品なので SIMPLE**（#65①：Catmull-Clark は角を枕にする）
for objs, rec in ((["felloe", "spokes", "nave"], WOOD_R), (["tyre"] + ["hoop%d" % i for i in range(len(HOOPS))], IRON_R)):
    r = BLACK_RECIPES[rec]
    if not r.get("disp"):
        continue
    tex = bpy.data.textures.new("relief_" + rec, 'CLOUDS')
    tex.noise_scale = r["dsize"]
    for nm in objs:
        o = bpy.data.objects[nm]
        sub = o.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 2
        sub.subdivision_type = 'SIMPLE'
        d = o.modifiers.new("disp", 'DISPLACE')
        d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    x = x_of(t)
    tilt.location = (x, 0.0, Z_C)
    tilt.keyframe_insert("location", frame=f + 1)
    wheel.rotation_euler = (0.0, theta_of(t), 0.0)   # 倒した軸まわりに転がる
    wheel.keyframe_insert("rotation_euler", frame=f + 1)
    axle_pivot.rotation_euler = (0.0, 0.0, 0.0)      # 🔴 位置は追うが、まわらない
    axle_pivot.keyframe_insert("rotation_euler", frame=f + 1)

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
        caption("MIDDLE STUDY 057 — KOSHIKI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, Z_C)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴🔴 1周目の最大の事故：**逆光そのものが画面に写っていた**。
#    4×4・1800W の面光源は被写体面へ換算すると半径1.23＝輪の内側とほぼ同寸で、
#    輻の隙間から**カメラが光源を直視**し、羽の内側に白い輪ができていた（黒が黒くない元凶）。
#    50作の被写体は塞がっていたので誰も踏まなかった。**抜けのある造形では必ず外す。**
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③：**奥**に置く（手前だとキャプションが染まる）。
#    画面に写る床は y≥1.1 の遠い側だけ（カメラが水平なので手前の床は枠の下に外れる）＝そこを狙う。
limelamps = []
for sx, sy in ((-1.6, 8.0), (0.0, 11.0), (1.6, 14.5)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, 0.30))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = LIME_W
    lp.data.shadow_soft_size = 0.60
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
cam.data.dof.focus_object = axle_ob
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

# 🔴 #63③：ライムの随伴光源は「誰に当てるか」でなく「誰から外すか」で書く（外すものを最小に）。
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != "axle":
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
    print(">> #40(6) 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, ys = [], []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name == "floor":
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 占有  長辺 %.1f%%（「寄り」は 78%% 以上・枠で切れて当然）"
          % (max((x1 - x0), (y1 - y0)) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外へ出ている＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))

if "diag4" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 400, 500
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    fp_.inputs["Base Color"].default_value = (0.9, 0.0, 0.0, 1)   # 床を赤に
    scene.render.filepath = os.path.join(OUT, "_diag4_floorred.png"); bpy.ops.render.render(write_still=True)
    fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
    fp_.inputs["Roughness"].default_value = 1.0                    # 床の艶だけ消す
    scene.render.filepath = os.path.join(OUT, "_diag4_floormatte.png"); bpy.ops.render.render(write_still=True)
    fp_.inputs["Roughness"].default_value = 0.42
    print(">> diag4 done")

if "diag3" in modes:
    # 🔴 物ごとに隠して撮る＝どの面が白いのかを一意に決める
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 300, 375
    scene.cycles.samples = 16
    scene.render.image_settings.file_format = 'PNG'
    for nm in ("felloe", "tyre", "spokes", "nave", "axle", "floor", "hoop0"):
        o = bpy.data.objects[nm]
        o.hide_render = True
        scene.render.filepath = os.path.join(OUT, "_diag3_%s.png" % nm)
        bpy.ops.render.render(write_still=True)
        o.hide_render = False
    print(">> diag3 done")

if "diag2" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 300, 375
    scene.cycles.samples = 16
    scene.render.image_settings.file_format = 'PNG'
    # a: 地（床・環境）を消す → 白い弧が残れば「物」、消えれば「地」
    fp_.inputs["Base Color"].default_value = (0, 0, 0, 1)
    bgn.inputs[1].default_value = 0.0
    scene.render.filepath = os.path.join(OUT, "_diag2_a.png"); bpy.ops.render.render(write_still=True)
    fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
    bgn.inputs[1].default_value = 0.55
    # b: 木の主材を赤に → 白い弧が赤くなれば felloe/spoke、白のままなら別の物
    for pp in (bpy.data.materials["wood"].node_tree.nodes["Principled BSDF"],):
        pp.inputs["Base Color"].default_value = (0.8, 0.0, 0.0, 1)
    scene.render.filepath = os.path.join(OUT, "_diag2_b.png"); bpy.ops.render.render(write_still=True)
    print(">> diag2 done")

if "diag" in modes:
    # 🔴 「白い輪」の犯人を推測で決めない。灯を1つずつ落として撮る（#16）
    import itertools
    lights = {n: bpy.data.objects[n] for n in ("key", "rim", "fill", "back")}
    lights.update({lp.name: lp for lp in limelamps})
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x, scene.render.resolution_y = 300, 375
    scene.cycles.samples = 16
    scene.render.image_settings.file_format = 'PNG'
    for off in ("none", "key", "rim", "fill", "back", "lime"):
        keep = {}
        for n, L in lights.items():
            keep[n] = L.data.energy
            if off == n or (off == "lime" and n.startswith("lime")):
                L.data.energy = 0.0
        bgn.inputs[1].default_value = 0.0 if off == "world" else 0.55
        scene.render.filepath = os.path.join(OUT, "_diag_%s.png" % off)
        bpy.ops.render.render(write_still=True)
        for n, L in lights.items():
            L.data.energy = keep[n]
    print(">> diag done")

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_057.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("kiguchi_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = (0.015, 0.030, 0.005, 1.0)
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.75
    axle_ob.data.materials[1] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {wheel.name, axle_pivot.name, tilt.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = axle_ob
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
