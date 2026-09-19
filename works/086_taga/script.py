# =============================================================
# MIDDLE STUDY 086 — TAGA（箍 / what holds the water is the space between）
#
#   光の型＝反復（#53）  構図の型＝端寄せ（#57）  ドメイン＝桶樽・結物（ゆいもの）
#
# 結桶は釘を使わない。膠も使わない。18枚の側板を、竹の箍が2本、外から締めているだけだ。
# **板と板は、くっついていない。締める力が、あいだを塞いでいるだけだ。**
# だから水を留めているのは板ではなく、板と板の**あいだ**のほうだ。
# 箍がゆるんで下へ滑ると、あいだが開いて、中の水が光になって出てくる。
# 18本の縦の筋。どれも同じ高さで切れている——それが水位。
#
# 造形：側板は角度0に1枚だけ作り、Rz(φ_i) で18枚に配る（原点＝桶の軸）。
#       断面は 側面（矧ぎ面）→面取り→外面（わずかに平ら FLATD）→面取り→側面→内面の弧。
#       テーパは真円錐（樽は膨らむが桶は膨らまない＝これが「桶」の骨格）。
#       黒の肌は SUBSURF+DISPLACE ではなく**頂点に直接焼いた木目**（#65：既定の SUBSURF は
#       面取りと矧ぎ面を枕形に丸める）。箍は2.2巻の螺旋帯＝回転対称を破る（#48）。
#
# 光：反復。発光は桶の内壁の円錐だけ。18本の目地を通して**18本の縦の筋**として出る。
#     🔴 #40②：内側の発光面が大きいと行灯になる。だからここでは
#     ①水位より上は ES=0 の純黒の裏当て（#32）②下へ FALL_MIN まで減衰
#     ——光っているのは「桶の中身」であって「桶に入れた電球」ではない。
#     水位は keyframe した Value ノード LEVEL と頂点の h の差から節点で作る。
#     🔴 発光体そのものを上下させると、低い水位のとき桶の底から**外へはみ出す**（解けない）。
#
# 動き：①側板の進行波 φ_i(t)=2πi/18+γ(t)+A·sin(2πt−2π·2i/18)（周に2山）
#       ②一様な膨らみ δ(t) ③ヨー γ(t) ④水位 LEVEL(t) ⑤箍の滑り slip(t)
#       🔴 ①だけでは光の量は動かない——隣り合う目地の和は telescoping で定数
#       （#84「発光面積が一定の作は光の振れが動かない」と同型）。だから②と④を別に足した。
#       確かめ方＝`python3 script.py -- geom`（Blender を起動せず画面で積分する）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = float(os.environ.get("LIME_W", "105"))

# --- 桶（原点＝桶の軸・胴の中心）----------------------------------
N_STAVE = 18
R_TOP, R_BOT = 0.600, 0.520        # 外半径（🔴 比 1.34 は「紙コップ」。結桶は直胴に近い 1.15）
T_WALL = 0.040                     # 肉厚（🔴 0.082 では目地が深い溝になり光が2本しか出ない）
Z_TOP, Z_BOT = 1.00, -1.00         # 胴の高さ 2.00
FLATD = 0.0035                     # 外面のわずかな平ら（🔴 W_SINK より必ず小さく＝#下記）
GAP_A = float(os.environ.get("GAP_A", "0.0500"))   # 目地の基礎角（R=0.55 で弧 0.0275）
WOBB = 0.13                        # 🔴 側板の幅を1枚ずつ変える（等幅＝機械で作った物に見える・#48）
CH_A_F, CH_R = 0.11, 0.016         # 面取り（角度比・半径方向）
NOUT, NIN, NZ = 9, 5, 40   # 🔴 NZ 16 では木目が z 方向に出ない
GRAIN = 0.0050                     # 木目（頂点に焼く。#52 の実ジオメトリ）
WARP = 0.0075                      # 🔴 板の反り。木目は黒では見えないが、反りはシルエットに出る

# --- 側板の幅（1枚ずつ違う）と中心角 ---------------------------------
_raw = [1.0 + WOBB * math.sin(3.7 * i + 1.3) * math.cos(1.9 * i + 0.4) for i in range(N_STAVE)]
_H0 = (2 * math.pi - N_STAVE * GAP_A) / (2 * sum(_raw))
HALFS = [_H0 * r for r in _raw]
PHI0, _acc = [], GAP_A / 2
for _i in range(N_STAVE):
    PHI0.append(_acc + HALFS[_i])
    _acc += 2 * HALFS[_i] + GAP_A
HALF = _H0

# --- 箍（螺旋帯）--------------------------------------------------
HOOP_Z = (0.80, -0.80)
HOOP_TURNS, HOOP_PITCH, HOOP_H, HOOP_TH = 3.0, 0.062, 0.048, 0.013
# 🔴 2.2巻・帯高 0.086・厚み 0.021 は「成形した樹脂のリング」に見えた。
#    細い帯を3巻きして**巻きのあいだに溝を残す**と、はじめて「竹を巻いた箍」に読める。

# --- 光（内壁の円錐・水位）----------------------------------------
NA_E, NH_E = 180, 72
W_SINK, W_TH = 0.011, 0.020      # 水の面は外面の 11mm 下／厚み 20mm
# 🔴 W_SINK と FLATD（外面中央の凹み）は**連動している**。W_SINK ≤ FLATD だと板の中央で
#    水が外面と同じ高さに出て、白い塗料が板の上へ流れたようににじむ（4周目 W_SINK 0.010／FLATD 0.010）。
#    かといって W_SINK を 0.022 に深くすると目地が深い溝になり、**halo が 59,839 → 6,819 に落ちた**（5周目）。
#    解は「W_SINK を深くする」ではなく「**FLATD を浅くする**」＝0.0035／0.011 で隙 7.3mm。
W_ZBOT = -0.88                   # 水の下端（裾の目地は黒＝底が詰まって見える）
SURF_LO, SURF_HI = -0.010, 0.005   # 水面のにじみ（h 単位）
SURF_BAND = 0.10                   # 水面の白い帯の幅（🔴 0.11 では裾が丸く垂れて「溶けたアイス」に見えた）
DEEP_LO, DEEP_H, DEEP_MIN = 0.30, 0.50, 0.14
# 🔴 #14 の std を「水面を明るくする」方向で稼ごうとしたら**下がった**（31.1→29.6）。
#    白へ飛んだ画素は is_lime（g ≥ r+20）から抜けて母集団から消えるため（#81③ と同型）。
#    std は**暗い側**でしか稼げない。しかも減衰長は「見えている柱の高さ」より短くないと効かない
#    ——DEEP_H 0.70 では柱の下端でもまだ 0.49 までしか落ちていなかった。      # 深さの勾配（🔴 これが無いと std 23.8 のペンキ＝#14）
ES_BASE = float(os.environ.get("ES_BASE", "2.05"))   # 胴（ライムのまま出す明るさ）
ES_CORE = float(os.environ.get("ES_CORE", "3.8"))    # 水面（白へ抜ける）
WHITE_BASE, WHITE_TO = 0.05, 0.88
# 🔴 #81③：halo（150<R<230・G>200・90<B<190）は**純ライムでは作れない**（青が上がらない）。
#    かといって全面を白に飛ばすと #14 に落ちる。だから胴に 22% だけ白を混ぜて halo の帯に入れ、
#    水面の線だけ 85% にする。halo は「線の強さ」ではなく**18本ぶんの面積**で買う（#85②）。
# 🔴 明るさと白抜けを同じ値（深さ）から引くと、胴まで白く飛んで「ライムでない白い筋」になる。
#    3周目で実際にそうなった（#76① の「同じプロファイルから2つ引く」と同型の失敗）。
K_MIX, E_FLOOR = 16.0, 0.12        # 🔴 #85①：裾を 0 に切らないと全面発光になる

# --- 動き --------------------------------------------------------
D0, D1 = 0.004, 0.026              # 半径方向の広がり
AMP_W, K_W = 0.030, 2              # 進行波（周に2山）
GAMMA = 0.19                       # ヨー（rad）
LVL0, LVL1 = 0.35, 0.30            # 水位（h 単位）🔴 満水でも上の箍の下に線が残ること
SLIP = 0.06                        # 箍が下へ滑る量（🔴 大きくすると満水の水位線が箍の裏へ隠れる）
BOB = 0.028

CX, CZ = 0.10, 2.24                # 🔴 端寄せ：桶の軸を画面左へ（AIM_X=0.55 から −0.45）
STILL_FRAME = 51   # 🔴 #74①：ヨー0 の f61 は左右対称で右半分が黒い塊。5.4° 振った姿にする


def r_out(z):
    return R_BOT + (R_TOP - R_BOT) * (z - Z_BOT) / (Z_TOP - Z_BOT)


def r_in(z):
    return r_out(z) - T_WALL


def half_eff(z, d, i):
    """側板を δ だけ半径方向へ滑らせると、軸から見た角半幅は縮む（回転ではないので）。"""
    R = r_out(z) - T_WALL / 2
    return math.atan2(R * math.sin(HALFS[i]), R * math.cos(HALFS[i]) + d)


def delta_of(t):
    return D0 + D1 * 0.5 * (1 - math.cos(2 * math.pi * t))


def gamma_of(t):
    return GAMMA * math.sin(2 * math.pi * t)


def phi_of(i, t):
    return (PHI0[i] + gamma_of(t)
            + AMP_W * math.sin(2 * math.pi * t - 2 * math.pi * K_W * i / N_STAVE))


def level_of(t):
    return LVL0 + LVL1 * 0.5 * (1 - math.cos(2 * math.pi * t))


def slip_of(t):
    return SLIP * 0.5 * (1 - math.cos(2 * math.pi * t))


def bob_of(t):
    return BOB * math.sin(2 * math.pi * t)


def emit_E(h, lv):
    """水位 lv（h 単位）の下だけ光る。胴は ES_BASE で一定、水面だけ ES_CORE へ立ち上がる。"""
    d = lv - h
    if d < SURF_LO:
        return 0.0
    gate = 1.0 if d >= SURF_HI else (d - SURF_LO) / (SURF_HI - SURF_LO)
    peak = max(0.0, 1.0 - max(0.0, d) / SURF_BAND)
    deep = 1.0 - min(1.0, max(0.0, (d - DEEP_LO) / (DEEP_H - DEEP_LO))) * (1.0 - DEEP_MIN)
    return gate * deep * (ES_BASE + (ES_CORE - ES_BASE) * peak) / ES_CORE


# =============================================================
# -- geom : Blender を起動せずに「画面に出ている発光面」を積分する（#40⑥）
#           ＋ bbox・長辺占有・重心（カメラは水平・無傾斜なので解析で出せる）
# =============================================================
TAN_H = (FRAME_W / 2) / 8.3
TAN_V = (FRAME_H / 2) / 8.3


def to_screen(p):
    d = p[1] + 8.3
    return (0.5 + 0.5 * (p[0] - AIM_X) / d / TAN_H,
            0.5 + 0.5 * (p[2] - LOOK_Z) / d / TAN_V)


def occluded(px, py, pz, t):
    """水の面（外面の 14mm 下）から視点へ向かう線が、側板の厚みか箍に当たるか。"""
    d = delta_of(t)
    cx, cy = AIM_X - CX, -8.3
    dx, dy, dz = cx - px, cy - py, LOOK_Z - (CZ + pz)
    ln = math.hypot(dx, dy)
    ux, uy, uz = dx / ln, dy / ln, dz / ln
    R_o = r_out(pz) + d
    b = px * ux + py * uy
    c = px * px + py * py - R_o * R_o
    disc = b * b - c
    if disc <= 0:
        return True
    s1 = -b + math.sqrt(disc)
    for k in range(7):
        ss = s1 * k / 6.0
        ang = math.atan2(py + ss * uy, px + ss * ux)
        for i in range(N_STAVE):
            da = (ang - phi_of(i, t) + math.pi) % (2 * math.pi) - math.pi
            if abs(da) <= half_eff(pz, d, i):
                return True
    zc = pz + s1 / 2 * uz
    for zh in HOOP_Z:
        lo = zh - slip_of(t) - (HOOP_PITCH * HOOP_TURNS + HOOP_H) / 2
        if lo <= zc <= lo + HOOP_PITCH * HOOP_TURNS + HOOP_H:
            return True
    return False


def visible_lime(t, NTH=900, NH=40):
    """🔴 見えているのは「器の対岸」ではなく**目地の底に来ている水の面**。
       目地は周の 6〜9% しかないので、粗いサンプルでは素通りして 0 と出る
       （最初 NTH=132 で全フレーム 0 になった）。"""
    lv = level_of(t)
    d = delta_of(t)
    sc = 1.0 + d / r_out(0.0)
    tot = 0.0
    for j in range(NH):
        h = (j + 0.5) / NH
        z = Z_BOT + 2.0 * h
        E = emit_E(h, lv)
        if E <= 0.02:
            continue
        R = (r_out(z) - W_SINK) * sc
        dA = (2 * math.pi * R / NTH) * (2.0 / NH)
        for k in range(NTH):
            a = 2 * math.pi * (k + 0.5) / NTH
            px, py = R * math.cos(a), R * math.sin(a)
            vx, vy = (AIM_X - CX) - px, -8.3 - py
            vl = math.hypot(vx, vy)
            cosf = (math.cos(a) * vx + math.sin(a) * vy) / vl
            if cosf <= 0.02:
                continue
            if occluded(px, py, z, t):
                continue
            tot += E * cosf * dA
    return tot


modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]

if "geom" in modes:
    print("── 画面に出ている発光面（#40⑥）と占有（Blender 不使用）")
    vals = []
    for f in range(0, N_FRAMES, 10):
        t = f / N_FRAMES
        v = visible_lime(t)
        vals.append(v)
        print("   f%3d  t %.2f  δ %.4f  水位h %.3f  ヨー %+5.1f°  可視発光 %.5f"
              % (f + 1, t, delta_of(t), level_of(t), math.degrees(gamma_of(t)), v))
    lo, hi = min(vals), max(vals)
    if lo <= 0:
        print("   🔴 可視発光が 0 のフレームがある（目地が塞がっているかサンプルが粗い）")
    else:
        print("   #40⑥ min/max = %.3f   光の振れ（max/min）= %.2f" % (lo / hi, hi / lo))
    # bbox（胴の外形だけで十分。箍は胴より外へ出ない）
    xs, ys = [], []
    t = (STILL_FRAME - 1) / N_FRAMES
    d = delta_of(t)
    for z in (Z_BOT, Z_TOP):
        R = r_out(z) + d
        for k in range(180):
            a = 2 * math.pi * k / 180
            p = (CX + R * math.cos(a), R * math.sin(a), CZ + z + bob_of(t))
            sx, sy = to_screen(p)
            xs.append(sx); ys.append(sy)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print("   bbox x %.3f..%.3f  y %.3f..%.3f  横 %.1f%%  縦 %.1f%%  接触 %d"
          % (x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100,
             (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)))
    cx_s = (x0 + x1) / 2 * 100
    cy_s = (1 - (y0 + y1) / 2) / 0.80 * 100
    print("   重心x %.1f%%（端寄せ＝|x−50|≥12）  重心y %.1f%%（天地＝|y−63|≥12 に**入らない**こと）"
          % (cx_s, cy_s))
    for nm, z in (("tagline", 1.02), ("logo", 0.85), ("study", 0.74)):
        print("   キャプション %-8s 画面の上から %.1f%%" % (nm, (1 - to_screen((AIM_X, -1.7, z))[1]) * 100))
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

# ---------- マテリアル（MATERIALS.md・#52。掟4の例外＝実物が2素材）----------
SUGI = dict(rough=0.78, spec=0.13)   # 側板＝杉（🔴 rough 0.60/spec 0.22 では曲面が環境を映して「黒いプラスチックのゴミ箱」・#17／#47）
TAKE = dict(rough=0.54, spec=0.20)   # 箍＝竹


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p, r):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r["coat_rough"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_sugi, sp_ = principled("sugi"); apply_black(sp_, SUGI)
mat_take, kp_ = principled("take"); apply_black(kp_, TAKE)

val_level = None


def glow_material(name):
    """h（UV.x）と keyframe する LEVEL の差から水位を作る。水位より上は純黒（#32）。"""
    global val_level
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    val_level = nt.nodes.new("ShaderNodeValue"); val_level.name = "LEVEL"
    val_level.outputs[0].default_value = LVL0
    d = nt.nodes.new("ShaderNodeMath"); d.operation = 'SUBTRACT'
    nt.links.new(val_level.outputs[0], d.inputs[0])
    nt.links.new(sep.outputs["X"], d.inputs[1])
    gate = nt.nodes.new("ShaderNodeMapRange"); gate.clamp = True
    gate.inputs["From Min"].default_value = SURF_LO
    gate.inputs["From Max"].default_value = SURF_HI
    gate.inputs["To Min"].default_value = 0.0
    gate.inputs["To Max"].default_value = 1.0
    nt.links.new(d.outputs[0], gate.inputs["Value"])
    peak = nt.nodes.new("ShaderNodeMapRange"); peak.clamp = True
    peak.inputs["From Min"].default_value = 0.0
    peak.inputs["From Max"].default_value = SURF_BAND
    peak.inputs["To Min"].default_value = 1.0
    peak.inputs["To Max"].default_value = 0.0
    nt.links.new(d.outputs[0], peak.inputs["Value"])
    # 明るさ＝(ES_BASE + (ES_CORE−ES_BASE)·peak) · gate
    sm = nt.nodes.new("ShaderNodeMath"); sm.operation = 'MULTIPLY_ADD'
    sm.inputs[1].default_value = (ES_CORE - ES_BASE) / ES_CORE
    sm.inputs[2].default_value = ES_BASE / ES_CORE
    nt.links.new(peak.outputs["Result"], sm.inputs[0])
    deep = nt.nodes.new("ShaderNodeMapRange"); deep.clamp = True
    deep.inputs["From Min"].default_value = DEEP_LO
    deep.inputs["From Max"].default_value = DEEP_H
    deep.inputs["To Min"].default_value = 1.0
    deep.inputs["To Max"].default_value = DEEP_MIN
    nt.links.new(d.outputs[0], deep.inputs["Value"])
    Ed = nt.nodes.new("ShaderNodeMath"); Ed.operation = 'MULTIPLY'
    nt.links.new(deep.outputs["Result"], Ed.inputs[0])
    nt.links.new(sm.outputs[0], Ed.inputs[1])
    Em = nt.nodes.new("ShaderNodeMath"); Em.operation = 'MULTIPLY'
    nt.links.new(gate.outputs["Result"], Em.inputs[0])
    nt.links.new(Ed.outputs[0], Em.inputs[1])
    E = Em.outputs[0]

    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = 0.0
    wmr.inputs["From Max"].default_value = 1.0
    wmr.inputs["To Min"].default_value = WHITE_BASE
    wmr.inputs["To Max"].default_value = WHITE_TO
    nt.links.new(peak.outputs["Result"], wmr.inputs["Value"])
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
    apply_black(blk, SUGI)                                  # 🔴 #32：裏当ては純黒
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = E_FLOOR
    nt.links.new(gate.outputs["Result"], sub.inputs[0])
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


mat_glow = glow_material("mizu")


# ---------- 側板（角度0に1枚。Rz で18枚に配る）----------
def section(z, i):
    """断面：矧ぎ面→面取り→外面→面取り→矧ぎ面→内面の弧（閉じた多角形）"""
    Ro, Ri = r_out(z), r_in(z)
    hf = HALFS[i]
    ca = CH_A_F * hf
    pts = [(-hf, Ri), (-hf, Ro - CH_R)]
    for k in range(NOUT + 1):
        a = -(hf - ca) + 2 * (hf - ca) * k / NOUT
        pts.append((a, Ro - FLATD * (1 - (a / hf) ** 2)))
    pts += [(hf, Ro - CH_R), (hf, Ri)]
    for k in range(1, NIN):
        pts.append((hf - 2 * hf * k / NIN, Ri))
    return pts


def stave_mesh(name, i):
    NS = len(section(0.0, i))
    verts, faces = [], []
    for j in range(NZ + 1):
        z = Z_BOT + (Z_TOP - Z_BOT) * j / NZ
        for k, (a, r) in enumerate(section(z, i)):
            g = GRAIN * (0.45 * math.sin(38.0 * a + 5.1 * i) * math.sin(6.5 * z + 1.7 + i)
                         + 0.32 * math.sin(77.0 * a - 1.1 + 2.0 * i) * math.sin(19.0 * z + 0.4)
                         + 0.23 * math.sin(131.0 * a + 0.7 * i) * math.sin(44.0 * z + 1.1 * i))
            rr = r + g + WARP * math.sin(2.6 * z + 2.3 * i) * math.sin(1.1 * i + 0.6)
            verts.append((rr * math.cos(a), rr * math.sin(a), z))
    for j in range(NZ):
        for k in range(NS):
            k2 = (k + 1) % NS
            faces.append((j * NS + k, j * NS + k2, (j + 1) * NS + k2, (j + 1) * NS + k))
    faces.append(tuple(range(NS - 1, -1, -1)))                      # 底の小口
    faces.append(tuple(range(NZ * NS, NZ * NS + NS)))               # 上の小口
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    return me


# ---------- 箍（2.2巻の螺旋帯）----------
def hoop_mesh(name, z_c, NU=220):
    span = HOOP_PITCH * HOOP_TURNS
    z0 = z_c - (span + HOOP_H) / 2 + HOOP_H / 2
    verts, faces = [], []
    for k in range(NU + 1):
        u = k / NU
        th = 2 * math.pi * HOOP_TURNS * u
        z = z0 + span * u
        Ri = r_out(z) + 0.0015
        for (dr, dz) in ((0, -HOOP_H / 2), (HOOP_TH, -HOOP_H / 2),
                         (HOOP_TH, HOOP_H / 2), (0, HOOP_H / 2)):
            R = Ri + dr
            verts.append((R * math.cos(th), R * math.sin(th), z + dz))
    for k in range(NU):
        for s in range(4):
            s2 = (s + 1) % 4
            faces.append((k * 4 + s, k * 4 + s2, (k + 1) * 4 + s2, (k + 1) * 4 + s))
    faces.append((3, 2, 1, 0))
    faces.append((NU * 4 + 0, NU * 4 + 1, NU * 4 + 2, NU * 4 + 3))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    return me


# ---------- 水（目地の底に来る円錐シェル・UV.x = h）----------
def water_mesh(name):
    verts, faces, uvs = [], [], []
    for j in range(NH_E + 1):
        z = W_ZBOT + (Z_TOP - W_ZBOT) * j / NH_E
        h = (z - Z_BOT) / 2.0
        for lay, dr in enumerate((W_SINK, W_SINK + W_TH)):
            R = r_out(z) - dr
            for k in range(NA_E):
                a = 2 * math.pi * k / NA_E
                verts.append((R * math.cos(a), R * math.sin(a), z))
    row = 2 * NA_E

    def vid(j, lay, k):
        return j * row + lay * NA_E + (k % NA_E)

    hh = [(W_ZBOT + (Z_TOP - W_ZBOT) * j / NH_E - Z_BOT) / 2.0 for j in range(NH_E + 1)]
    for j in range(NH_E):
        h0, h1 = hh[j], hh[j + 1]
        for k in range(NA_E):
            faces.append((vid(j, 0, k), vid(j, 0, k + 1), vid(j + 1, 0, k + 1), vid(j + 1, 0, k)))
            uvs += [(h0, .5), (h0, .5), (h1, .5), (h1, .5)]
            faces.append((vid(j, 1, k + 1), vid(j, 1, k), vid(j + 1, 1, k), vid(j + 1, 1, k + 1)))
            uvs += [(h0, .5), (h0, .5), (h1, .5), (h1, .5)]
    for j, nz in ((0, True), (NH_E, False)):
        h = hh[j]
        for k in range(NA_E):
            q = (vid(j, 1, k), vid(j, 1, k + 1), vid(j, 0, k + 1), vid(j, 0, k))
            faces.append(q if nz else q[::-1])
            uvs += [(h, .5)] * 4
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    lay = me.uv_layers.new(name="grad")
    for i, uv in enumerate(uvs):
        lay.data[i].uv = uv
    return me


# ---------- 底板 ----------
def base_mesh(name, z=-0.955, th=0.075, NA=64):   # 🔴 -0.90 だと裾の目地から**背景が透ける**
    R = r_in(z) - 0.002
    verts, faces = [], []
    for zz in (z - th / 2, z + th / 2):
        for k in range(NA):
            a = 2 * math.pi * k / NA
            verts.append((R * math.cos(a), R * math.sin(a), zz))
    for k in range(NA):
        k2 = (k + 1) % NA
        faces.append((k, k2, NA + k2, NA + k))
    faces.append(tuple(range(NA - 1, -1, -1)))
    faces.append(tuple(range(NA, 2 * NA)))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    return me


def link(me, name, mats, smooth_ang=0.7):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.clear()
    for m in mats:
        ob.data.materials.append(m)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_ang)
    except Exception:
        pass
    return ob


staves = [link(stave_mesh("m_ita_%02d" % i, i), "ita_%02d" % i, [mat_sugi], 0.50)
          for i in range(N_STAVE)]
hoops = [link(hoop_mesh("m_taga_%d" % n, z), "taga_%d" % n, [mat_take], 0.60)
         for n, z in enumerate(HOOP_Z)]
ob_water = link(water_mesh("m_mizu"), "mizu", [mat_glow], 1.30)
ob_base = link(base_mesh("m_soko"), "soko", [mat_sugi], 0.50)
body = hoops + [ob_water, ob_base]
parts = staves + body

# --- キーフレーム（毎フレーム・剛体だけ）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
R_REF = r_out(0.0)
for f, idx in enumerate(FR_):
    t = idx / N_FRAMES
    d, g, sl, bb = delta_of(t), gamma_of(t), slip_of(t), bob_of(t)
    s = 1.0 + d / R_REF
    for i, ob in enumerate(staves):
        p = phi_of(i, t)
        ob.location = (CX + d * math.cos(p), d * math.sin(p), CZ + bb)
        ob.rotation_euler = (0.0, 0.0, p)
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)
    for ob in hoops:
        ob.location = (CX, 0.0, CZ + bb - sl)
        ob.rotation_euler = (0.0, 0.0, g)
        ob.scale = (s, s, 1.0)
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)
        ob.keyframe_insert("scale", frame=f + 1)
    for ob in (ob_water, ob_base):
        ob.location = (CX, 0.0, CZ + bb)
        ob.rotation_euler = (0.0, 0.0, g)
        ob.scale = (s, s, 1.0)          # 🔴 水も側板と一緒に広がる（目地の底に居続ける）
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)
        ob.keyframe_insert("scale", frame=f + 1)
    val_level.outputs[0].default_value = level_of(t)
    val_level.outputs[0].keyframe_insert("default_value", frame=f + 1)

# 🔴 Blender 5.x の Action は slotted なので `.fcurves` は無い（AttributeError）。
#    補間は keyframe_insert の前に置いた keyframe_new_interpolation_type='LINEAR' が効く。

# ---------- 床・キャプション・ライト・カメラ（シリーズ不変） ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor_obj = bpy.context.active_object
floor_obj.name = "floor"
floor_obj.data.materials.append(mat_floor)


def caption(body_s, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object; tx.name = name
    tx.data.body = body_s; tx.data.size = size; tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 1.02), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.85), "logo"),
        caption("MIDDLE STUDY 086 — TAGA", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
back.visible_camera = False        # 🔴 #67①：18本の目地は抜けている

# 🔴 #58③：随伴のライム光源は発光体の外。桶の裏・床寄り
for sx, sy, sz, wt in ((-0.36, 2.2, 0.28, LIME_W), (0.10, 4.6, 0.28, LIME_W),
                       (0.62, 7.8, 0.28, LIME_W)):
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

# 🔴 逆光のライトリンクは全ジオメトリ生成後（#56②）。床を受光から外す
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

tH = (STILL_FRAME - 1) / N_FRAMES
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME,
      " δ %.4f  水位h %.3f  ヨー %+.1f°" % (delta_of(tH), level_of(tH), math.degrees(gamma_of(tH))))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 91):
        scene.frame_set(fr); dg.update()
        allx, ally = [], []
        for ob in parts:
            ev = ob.evaluated_get(dg)
            for v in list(ev.data.vertices)[::5]:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                allx.append(c.x); ally.append(c.y)
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  "
              "重心x %.1f%%  中心y(上から) %.1f%%  LEVEL %.3f"
              % (fr, x0, x1, y0, y1, (x1 - x0) * 100, (y1 - y0) * 100, edge,
                 (x0 + x1) / 2 * 100, (1 - (y0 + y1) / 2) * 100,
                 val_level.outputs[0].default_value))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_086.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("sugi_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = SUGI["rough"]
    m_em = bpy.data.materials.new("mizu_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_BASE * 0.80
    for ob in staves + hoops + [ob_base]:
        ob.data.materials[0] = m_bk
    ob_water.data.materials[0] = m_em
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
