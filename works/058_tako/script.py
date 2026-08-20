# =============================================================
# MIDDLE STUDY 058 — TAKO（凧 / 江戸角凧 a Japanese kite）
#
# 黒い凧が一枚、高いところにいる。こちらから見えているのは裏だ——骨と、糸目と、
# 紙をむこうから透かしてくる ライム #A5E02E の光だけ。絵は、向こう側にある。
# 江戸の凧には尾が無い。振れを止めているのは、面の**真ん中の一点**に集めた糸目だけだ。
# 風が来ると凧は風の方を向く。向いた分だけ、こちらに見せる面は細くなり、
# 反りの手前側の縁が、その光を横から切る。
# **こちらを向くのは、真ん中を通る一瞬だけ。**
#
# 🔴 光の型＝**面**（#53：57作で4作しかない型。定義に「格子越しの面」が含まれる＝骨越しの紙）
# 🔴 構図の型＝**端寄せ**（#57：57作中51作が「全身」。端寄せは 052 TAIKO の1作のみ）
#    凧を左に寄せ、空いた右をそのまま余白（＝これから上がっていく空）にする。
#    edge==0・重心xが中央から12%以上ずれる（`compositions.py --verify` で機械検査）。
# 【ドメイン】空・凧／風（シリーズ未踏）。直近10作＝運搬・車輪／盤上遊戯／鋳造／植物・果実／
#            漁労／楽器・打／貨幣／玩具・けん玉／武・弓／農・製粉 と別。
#            037 KOMA・050 KENDAMA【玩具】は**手の中の身体技**で、こちらは**空に預ける道具**。
#            047 NOREN【商い・暖簾】は垂れ布の隙間＝こちらは張られた一枚の面で機構が別。
#
# 機構＝**風見（weathercocking）**：a(t) = 0.5(1 − cos2πt) の1パラメータで
#   偏角 ψ = YAW0 + PSI·a ／ 流れ x = X_C + D·a ／ バンク roll = −ROLL·a ／ 浮き z = Z_C + ZB·a
#   をすべて結ぶ（**凧は向いた方へ流れる**＝位相を合わせる調整値が1つも無い）。
#   整数周期で厳密に閉じ、**位置キーと回転キーだけ**なので glb にそのまま乗る（#60）。
#
# 🔴 **機構が 051 ZENI の「首振り」と同族であることを隠さない。** 違いは2つ：
#   ① 光の型が別（051＝背光・孔から抜ける／058＝面・紙そのものが光る）
#   ② 光を細らせるのは foreshortening **だけではない**——反り（BOW）で面が
#      カメラ側に凹んでいるので、振れると**手前の縁が中央の光を横から遮る**。
#      #40⑥ の積分は視線方向の1次元zバッファでこの自己遮蔽込みで測る（#44 の「ひとつの機構が2つを動かす」）。
#
# 🔴 造形は押し出しだけで boolean 不使用。紙は反りの解析式そのもの、骨と糸目はその上に載せる。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 凧（panel）------------------------------------------------
HW, HH = 0.780, 1.020          # 紙の半幅・半高（1.56 × 2.04＝江戸角凧の縦横比 1:1.31）
BOW    = 0.300                 # 反り：中央が奥（+Y）・両端が手前（0）＝カメラ側に凹
# --- 骨（bamboo）-----------------------------------------------
RIB_V  = (-0.420, 0.420)                    # 縦骨。**真ん中には通さない**（中央の光を割らないため）
RIB_H  = (-0.970, -0.740, -0.400, 0.400, 0.740, 0.970)   # 横骨6本。
                                            # 🔴 等間隔にすると**キルティングの生地**に見える。
                                            # 真ん中の枡だけを大きく取ると「一枡だけが光っている」が立つ
RIB_HW, RIB_HD = 0.0105, 0.0072             # 骨の半幅・半厚（竹ひごの実寸。
                                            # 🔴 2周目まで 0.023／0.015 で、格子が木箱の枠に見えていた）
RIB_OFF = 0.0090                            # 紙からカメラ側への持ち出し
# --- 唸り（unari／うなり）---------------------------------------------
UN_H  = 0.130                  # 上端から反り上がる高さ（枠の上端まで 0.16 残す）
UN_R  = 0.0098
# --- 糸目（bridle）---------------------------------------------
BR_P   = (0.0, -0.760, 0.235)  # 糸目中（いとめなか）＝**真ん中ではない。少しだけ上**
BR_R   = 0.0038
BR_KNOT = 0.022
# --- 紙の光 -----------------------------------------------------
FX, FZ   = 0.400, 0.360        # 発光の楕円半径（u=1 で ES が厳密に 0＝紙の周縁は完全な黒／#49①）
ES_CORE  = 4.0
EM_BASE  = 0.0
EM_P     = 0.62
FAC_LO, FAC_P = 0.90, 1.0      # #65②③：純発光体に法線依存を弱く掛ける
# --- 舞台 ------------------------------------------------------
X_C, Z_C = 0.090, 2.400        # 凧の中心（🔴 カメラの光軸 AIM_X=0.55 より **左**＝端寄せ）
PITCH  = math.radians(14.0)    # 迎角。🔴 上端を**奥**へ倒す＝下から見上げる凧になる。
                               # 7周目まで −10°（上端が手前）で、空の物でなく吊り下げた灯に読めていた。
YAW0   = math.radians(-8.0)    # 静止時の偏角（key 側へ少し向ける）
PSI    = math.radians(54.0)    # 🔴 片振り（#57③：平らな板は安全な側だけへ振る。両振りは斜入射で銀色に転ぶ）
ROLL_A = math.radians(10.0)    # 向いた方へバンクする
D_X, ZB = 0.300, 0.120         # 流れ・浮き（すべて a(t) に結ばれる）
FPS, N_FRAMES = 24, 120
CAM_LOC  = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
LIME_W = 110.0                 # 随伴のライム光源（#58）。**発光体の外**・**奥**に置く（#64③）
NX, NZ = 100, 80               # 紙の格子
FRAME_W, FRAME_H = 2.81, 3.52  # 被写体面での枠（85mm・8.3m・4:5）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def a_of(t):
    """1つのパラメータ。整数周期で厳密に閉じる"""
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * t))


def pose(t):
    a = a_of(t)
    return dict(a=a, yaw=YAW0 + PSI * a, roll=-ROLL_A * a, pitch=PITCH,
                loc=(X_C + D_X * a, 0.0, Z_C + ZB * a))


def surf(xl, zl):
    """紙の局所座標（反りは x' の放物線。中央が奥・両端が手前）"""
    return (xl, BOW * (1.0 - (xl / HW) ** 2), zl)


def surf_n(xl):
    """法線（カメラ側 −Y を向く）"""
    fp = -2.0 * BOW * xl / (HW * HW)
    n = (fp, -1.0, 0.0)
    L = math.hypot(fp, 1.0)
    return (n[0] / L, n[1] / L, 0.0)


def rot(v, pitch, roll, yaw):
    """Blender の XYZ オイラーと同じ順（R = Rz·Ry·Rx）"""
    x, y, z = v
    cy, sy = math.cos(pitch), math.sin(pitch)          # Rx
    y, z = y * cy - z * sy, y * sy + z * cy
    cr, sr = math.cos(roll), math.sin(roll)            # Ry
    x, z = x * cr + z * sr, -x * sr + z * cr
    cz, sz = math.cos(yaw), math.sin(yaw)              # Rz
    x, y = x * cz - y * sz, x * sz + y * cz
    return (x, y, z)


SE_P = 2.6     # 超楕円の次数（1=菱形／2=楕円／∞=矩形）。枡に沿わせつつ角は丸める
               # 🔴 4.0 まで上げると角の丸い矩形＝**アプリのアイコン**に読める（#57 の警告と同型）


def _u(xl, zl):
    return (abs(xl / FX) ** SE_P + abs(zl / FZ) ** SE_P) ** (1.0 / SE_P)


def emis(xl, zl):
    u = _u(xl, zl)
    if u >= 1.0:
        return 0.0
    return (1.0 - u) ** EM_P


def cam_uv(P):
    """被写体面（y=0）に立てた枠での正規化画面座標。透視で 0..1 に落とす"""
    C = CAM_LOC
    dy = P[1] - C[1]
    if dy <= 0.05:
        return None
    s = (0.0 - C[1]) / dy                                  # y=0 の面へ引き戻す
    x = C[0] + s * (P[0] - C[0])
    z = C[2] + s * (P[2] - C[2])
    return ((x - (AIM_X - FRAME_W / 2)) / FRAME_W,
            ((LOOK_Z + FRAME_H / 2) - z) / FRAME_H)        # v は上から


NS_X, NS_Z = 240, 120


def light_visible(t):
    """🔴 #40⑥ は幾何で積分する（#46/#64②）＝**見えている発光**。
       E(x',z') × max(0, n̂·v̂) を面上で積分し、さらに
       **反りによる自己遮蔽**を視線方向の1次元zバッファで落とす
       （面はカメラ側に凹なので、振れると手前の縁が中央の光を横から切る）。"""
    p = pose(t)
    C = CAM_LOC
    tot = 0.0
    for iz in range(NS_Z):
        zl = -HH + 2 * HH * (iz + 0.5) / NS_Z
        row = []
        for ix in range(NS_X):
            xl = -HW + 2 * HW * (ix + 0.5) / NS_X
            P = rot(surf(xl, zl), p["pitch"], p["roll"], p["yaw"])
            P = (P[0] + p["loc"][0], P[1] + p["loc"][1], P[2] + p["loc"][2])
            n = rot(surf_n(xl), p["pitch"], p["roll"], p["yaw"])
            v = (C[0] - P[0], C[1] - P[1], C[2] - P[2])
            L = math.sqrt(sum(c * c for c in v))
            fac = (n[0] * v[0] + n[1] * v[1] + n[2] * v[2]) / L
            uv = cam_uv(P)
            row.append((uv, L, max(0.0, fac), emis(xl, zl)))
        # 1次元zバッファ（この行のなかで、同じ画面位置に来たものは手前だけが見える）
        buck = {}
        for k, (uv, L, fac, e) in enumerate(row):
            if uv is None:
                continue
            b = int(uv[0] * 2400)
            if b not in buck or L < row[buck[b]][1]:
                buck[b] = k
        vis = set(buck.values())
        for k, (uv, L, fac, e) in enumerate(row):
            if k in vis and e > 0.0:
                tot += e * fac
    return tot * (2 * HW / NS_X) * (2 * HH / NS_Z)


_VS = [light_visible(i / N_FRAMES) for i in range(N_FRAMES)]
_VMAX = max(_VS)
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _VS[i]) + 1

if "--probe-only" in sys.argv:
    p = pose((STILL_FRAME - 1) / N_FRAMES)
    print(">> STILL_FRAME %d (t=%.3f, a=%.3f, ψ=%+.1f°)"
          % (STILL_FRAME, (STILL_FRAME - 1) / N_FRAMES, p["a"], math.degrees(p["yaw"])))
    print(">> #40(6) 見える光 min/max = %.3f  （合格 0.75以下）" % (min(_VS) / _VMAX))
    print(">> ループの閉じ: V(0)=%.6f V(1)=%.6f 差 %.2e   a(0)=%.6f a(1)=%.6f"
          % (_VS[0], light_visible(1.0), abs(_VS[0] - light_visible(1.0)), a_of(0), a_of(1)))
    ell = math.pi * FX * FZ
    print(">> 発光の面積（正対・遮蔽なし） %.4f m² ＝ 枠 %.4f m² の %.2f%%（#51 の帯 0.8〜12.0）"
          % (ell, FRAME_W * FRAME_H, ell / (FRAME_W * FRAME_H) * 100))
    # 投影bbox（紙＋唸り無し・骨は紙の内側なので紙で代表）
    for label, tt in (("hero", (STILL_FRAME - 1) / N_FRAMES), ("a=0", 0.0), ("a=1", 0.5)):
        q = pose(tt)
        us, vs = [], []
        for xl in (-HW, 0.0, HW):
            for zl in (-HH, 0.0, HH):
                P = rot(surf(xl, zl), q["pitch"], q["roll"], q["yaw"])
                P = tuple(P[i] + q["loc"][i] for i in range(3))
                uv = cam_uv(P)
                us.append(uv[0]); vs.append(uv[1])
        # 糸目中も入れる
        P = rot(BR_P, q["pitch"], q["roll"], q["yaw"])
        P = tuple(P[i] + q["loc"][i] for i in range(3))
        uv = cam_uv(P); us.append(uv[0]); vs.append(uv[1])
        print(">> %-4s 画面 x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)  重心x %.1f%%  枠まで 左%.3f 右%.3f 上%.3f"
              % (label, min(us), max(us), (max(us) - min(us)) * 100,
                 min(vs), max(vs), (max(vs) - min(vs)) * 100,
                 (min(us) + max(us)) / 2 * 100, min(us), 1 - max(us), min(vs)))
    print(">> 「端寄せ」＝ edge==0 かつ |重心x−50|≧12 ／ 占有は長辺 55〜65%%")
    for i in range(0, N_FRAMES, 10):
        t = i / N_FRAMES
        q = pose(t)
        print("   t=%.3f  a=%.3f  ψ=%+6.1f°  x=%+.3f  光 %5.1f%%"
              % (t, q["a"], math.degrees(q["yaw"]), q["loc"][0], 100 * _VS[i] / _VMAX))
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
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25, disp=0.004, dsize=0.05),
    # 紙＝**布（薄物）**（MATERIALS.md「光を透かすほど薄いもの＝暖簾・幕・紙」）
    "nuno_usu": dict(rough=0.66, spec=0.28, sheen=0.55, sheen_rough=0.25),
    # 紙（この作専用）＝薄物の値に **金属度**を足したもの。#57②：平らな面を正対させる題材では
    # 鏡面や粗さをいくら振っても白い studio を映して灰色の板になる。metal でだけ黒へ戻る。
    "washi":  dict(rough=0.55, spec=0.34, sheen=0.45, sheen_rough=0.25, metal=0.22,
                   disp=0.0012, dsize=0.040),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
    # 竹の骨＝057 で振り直した木の値（長い直線の稜線が白線にならない側）
    "ki":     dict(rough=0.68, spec=0.32, disp=0.006, dsize=0.10),
    # 竹ひご・唸り＝細い丸みの稜線が studio をそのまま映して白い線になるので metal で断つ
    "take":   dict(rough=0.55, spec=0.34, metal=0.30, disp=0.004, dsize=0.08),
}


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


mat_take = black_material("take", "take")      # 竹の骨・唸り
mat_ito = black_material("ito", "nuno")        # 糸目


def washi_material(name):
    """紙＝黒い和紙に、むこうから光が透けている。
       勾配は **UV に焼いた楕円距離**（#34/#39）。u=1 の縁で ES が厳密に 0＝周縁は完全な黒。
       紙の質感（Sheen）は残したまま Emission だけを勾配で動かす。"""
    m, p = principled(name)
    set_black(p, "washi")
    nt = m.node_tree
    # 🔴 1周目の事故：057 の木口（径0.18の小片）に使っていた暗緑の下地をそのまま持ってきたら、
    #    1.56×2.04 の紙**全面が抹茶色**になった。面積が変われば同じ値でも別物になる。黒は黒に戻す。
    p.inputs["Base Color"].default_value = BLACK
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

    # 🔴 #24：均一なベタ塗りはペンキに見える。和紙の**繊維の透けムラ**を光そのものに乗せる
    #    （紙の起伏＝DISPLACE は黒の肌のためのもので、透過のムラはここでしか出せない）
    ntx = nt.nodes.new("ShaderNodeTexNoise")
    ntx.inputs["Scale"].default_value = 46.0
    ntx.inputs["Detail"].default_value = 6.0
    ntx.inputs["Roughness"].default_value = 0.62
    nmr = nt.nodes.new("ShaderNodeMapRange"); nmr.clamp = True
    nmr.inputs["From Min"].default_value = 0.32; nmr.inputs["From Max"].default_value = 0.70
    nmr.inputs["To Min"].default_value = 0.74; nmr.inputs["To Max"].default_value = 1.06
    nt.links.new(ntx.outputs["Fac"], nmr.inputs["Value"])

    e1 = mn('MULTIPLY'); nt.links.new(fra.outputs[0], e1.inputs[0])
    nt.links.new(fca.outputs[0], e1.inputs[1])
    e0 = mn('MULTIPLY'); nt.links.new(e1.outputs[0], e0.inputs[0])
    nt.links.new(nmr.outputs["Result"], e0.inputs[1])
    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e0.outputs[0], e2.inputs[0])
    nt.links.new(e2.outputs[0], p.inputs["Emission Strength"])
    return m


mat_washi = washi_material("washi")

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


def link(me, name, mat, parent):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if not ob.data.materials:
        ob.data.materials.append(mat)
    ob.parent = parent
    if me.get("_smooth"):
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        try:
            bpy.ops.object.shade_auto_smooth(angle=0.35)
        except Exception:
            pass
        ob.select_set(False)
    return ob


def paper_mesh():
    """紙＝反りの解析式そのもの。UV.x に楕円距離 u を焼く（#39）。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    grid = []
    for iz in range(NZ + 1):
        zl = -HH + 2 * HH * iz / NZ
        row = [bm.verts.new(surf(-HW + 2 * HW * ix / NX, zl)) for ix in range(NX + 1)]
        grid.append(row)
    for iz in range(NZ):
        for ix in range(NX):
            bm.faces.new([grid[iz][ix], grid[iz][ix + 1],
                          grid[iz + 1][ix + 1], grid[iz + 1][ix]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # 🔴 法線をカメラ側（−Y）へ揃える。裏返っていると黒一色なので「作り忘れ」に見える（#57①）
    if sum(f.normal.y for f in bm.faces) > 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    for f in bm.faces:
        for lp in f.loops:
            q = lp.vert.co
            lp[uvl].uv = (min(1.0, _u(q.x, q.z)), 0.5)
    me = bpy.data.meshes.new("paper"); bm.to_mesh(me); bm.free()
    me["_smooth"] = True
    return me


def _bar(bm, pts, hw, hd, nrm):
    """pts に沿った角断面の棒。nrm＝断面の「幅」方向の単位ベクトル"""
    rings = []
    for i, P in enumerate(pts):
        if i == 0:
            T = tuple(pts[1][k] - pts[0][k] for k in range(3))
        elif i == len(pts) - 1:
            T = tuple(pts[-1][k] - pts[-2][k] for k in range(3))
        else:
            T = tuple(pts[i + 1][k] - pts[i - 1][k] for k in range(3))
        L = math.sqrt(sum(c * c for c in T)) or 1.0
        T = tuple(c / L for c in T)
        W = (T[1] * nrm[2] - T[2] * nrm[1], T[2] * nrm[0] - T[0] * nrm[2],
             T[0] * nrm[1] - T[1] * nrm[0])
        LW = math.sqrt(sum(c * c for c in W)) or 1.0
        W = tuple(c / LW for c in W)
        vs = []
        for sw, sd in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(tuple(P[k] + sw * hw * W[k] + sd * hd * nrm[k]
                                         for k in range(3))))
        rings.append(vs)
    for a, b in zip(rings, rings[1:]):
        for s in range(4):
            bm.faces.new([a[s], a[(s + 1) % 4], b[(s + 1) % 4], b[s]])
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])


def ribs_mesh():
    """骨＝縦2本・横4本。紙の反りに載せ、カメラ側（−Y）へ RIB_OFF 持ち出す。
       🔴 真ん中（x'=0・z'=0）には1本も通さない＝中央の光を割らない。"""
    bm = bmesh.new()
    N = 40
    for xv in RIB_V:                                   # 縦骨（反りに沿って z' 方向へ走る）
        pts = []
        for i in range(N + 1):
            zl = -HH + 2 * HH * i / N
            x, y, z = surf(xv, zl)
            n = surf_n(xv)
            pts.append((x + n[0] * RIB_OFF, y + n[1] * RIB_OFF, z))
        _bar(bm, pts, RIB_HW, RIB_HD, (0.0, -1.0, 0.0))
    for zh in RIB_H:                                   # 横骨（反りそのものを描く）
        pts = []
        for i in range(N + 1):
            xl = -HW + 2 * HW * i / N
            x, y, z = surf(xl, zh)
            n = surf_n(xl)
            pts.append((x + n[0] * RIB_OFF, y + n[1] * RIB_OFF, z))
        _bar(bm, pts, RIB_HW, RIB_HD, (0.0, -1.0, 0.0))
    return finish_mesh(bm, "ribs", bevel=0.0022, smooth=False)


# 🔴 4点糸目（実物どおり）。3周目まで8本にしていたら、細い線が扇に束なって
#    **面から出ている光がプロジェクタの光線に見えた**——光の型が「面」から「芯」に転ぶ。
BRIDLE_PTS = [(xv, zh) for zh in (RIB_H[0], RIB_H[-1]) for xv in RIB_V]


def unari_mesh():
    """唸り＝上端に渡した弓。両端を天の骨の端に結び、真ん中がいちばん高い。"""
    bm = bmesh.new()
    N = 36
    pts = []
    for i in range(N + 1):
        u = i / N
        xl = -HW * 0.94 + 2 * HW * 0.94 * u
        x, y, z = surf(xl, HH)
        n = surf_n(xl)
        pts.append((x + n[0] * RIB_OFF, y + n[1] * RIB_OFF,
                    z + UN_H * math.sin(math.pi * u)))
    _bar(bm, pts, UN_R, UN_R, (0.0, -1.0, 0.0))
    return finish_mesh(bm, "unari", bevel=0.0018, smooth=True)


def bridle_mesh():
    """糸目10本。骨の交点から**一点**へ集める。江戸の凧に尾が無いのはこれが在るからだ。"""
    bm = bmesh.new()
    SEG = 8
    for (xv, zh) in BRIDLE_PTS:
        x, y, z = surf(xv, zh)
        n = surf_n(xv)
        A = (x + n[0] * (RIB_OFF + RIB_HD), y + n[1] * (RIB_OFF + RIB_HD), z)
        pts = [tuple(A[k] + (BR_P[k] - A[k]) * (i / 6) for k in range(3)) for i in range(7)]
        rings = []
        for i, P in enumerate(pts):
            T = tuple(BR_P[k] - A[k] for k in range(3))
            L = math.sqrt(sum(c * c for c in T)) or 1.0
            T = tuple(c / L for c in T)
            up = (0.0, 0.0, 1.0) if abs(T[2]) < 0.9 else (1.0, 0.0, 0.0)
            U = (T[1] * up[2] - T[2] * up[1], T[2] * up[0] - T[0] * up[2],
                 T[0] * up[1] - T[1] * up[0])
            LU = math.sqrt(sum(c * c for c in U)) or 1.0
            U = tuple(c / LU for c in U)
            V = (T[1] * U[2] - T[2] * U[1], T[2] * U[0] - T[0] * U[2],
                 T[0] * U[1] - T[1] * U[0])
            vs = []
            for s in range(SEG):
                ang = 2 * math.pi * s / SEG
                vs.append(bm.verts.new(tuple(
                    P[k] + BR_R * (math.cos(ang) * U[k] + math.sin(ang) * V[k])
                    for k in range(3))))
            rings.append(vs)
        for a, b in zip(rings, rings[1:]):
            for s in range(SEG):
                bm.faces.new([a[s], a[(s + 1) % SEG], b[(s + 1) % SEG], b[s]])
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])
    # 糸目中の結び目
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=BR_KNOT,
                               matrix=__import__("mathutils").Matrix.Translation(BR_P))
    return finish_mesh(bm, "bridle", bevel=0.0, smooth=True)


# ---------- 配置 ----------
kite = bpy.data.objects.new("kite", None)
bpy.context.collection.objects.link(kite)

parts = []
paper_ob = link(paper_mesh(), "paper", mat_washi, kite)
parts.append(paper_ob)
parts.append(link(ribs_mesh(), "ribs", mat_take, kite))
parts.append(link(bridle_mesh(), "bridle", mat_ito, kite))
parts.append(link(unari_mesh(), "unari", mat_take, kite))

# 🔴 黒の肌は実ジオメトリ（#52）。骨は箱状なので SUBSURF は SIMPLE（#65①）
for nm, rec in (("ribs", "take"), ("unari", "take"), ("paper", "washi")):
    r = BLACK_RECIPES[rec]
    tex = bpy.data.textures.new("relief_" + rec, 'CLOUDS'); tex.noise_scale = r["dsize"]
    o = bpy.data.objects[nm]
    sub = o.modifiers.new("sub", 'SUBSURF')
    sub.levels = sub.render_levels = 2 if nm == "ribs" else 1
    sub.subdivision_type = 'SIMPLE'
    d = o.modifiers.new("disp", 'DISPLACE')
    d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    p = pose(i / N_FRAMES)
    kite.location = p["loc"]
    kite.rotation_euler = (p["pitch"], p["roll"], p["yaw"])
    kite.keyframe_insert("location", frame=f + 1)
    kite.keyframe_insert("rotation_euler", frame=f + 1)

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
        caption("MIDDLE STUDY 058 — TAKO", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (X_C, 0.0, Z_C)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：**被写体に抜けがある作では逆光をカメラから隠す**。
#    凧の周りも糸目の内側も素通しなので、4×4・1800W の面光源が画面にそのまま写る。
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③：**奥**に置く（手前だとキャプションが染まる）
limelamps = []
for sx, sy in ((-0.70, 16.0), (0.35, 20.0), (1.55, 26.0)):
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
cam.data.dof.focus_object = paper_ob
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

# 🔴 #63③：ライムの随伴光源は「誰から外すか」で書く（外すものを最小に）
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != "paper":
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
    print(">> 占有  長辺 %.1f%%（帯 55〜65%%）  重心x %.1f%%（端寄せ＝中央から12%%以上）"
          % (max((x1 - x0), (y1 - y0)) * 100, (x0 + x1) / 2 * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))

if "diag" in modes:
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_058.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("washi_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.55
    paper_ob.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {kite.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = paper_ob
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
