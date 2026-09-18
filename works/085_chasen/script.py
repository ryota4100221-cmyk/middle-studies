# =============================================================
# MIDDLE STUDY 085 — CHASEN（茶筅 / the middle that splitting made）
#
#   光の型＝内包（#53）  構図の型＝全身（#57）  ドメイン＝茶道・点前／茶筅
#
# 茶筅は一本の竹から作る。継がない、足さない。ただ割る。
# 節から先を八十に割って、外へ反らせ、内に短い穂を残し、糸で締める。
# 割る前の竹には内も外も無かった。**割って、はじめて真ん中ができた。**
# 外穂が茶を点て、内穂は茶に触れない。内穂は形を保つためだけに立っている。
# 働いていないものが囲っているところに、光はある。
#
# 造形：外穂34本・内穂12本。断面は竹の割り肌そのまま＝接線方向に平たい短冊
#       （幅 w・厚み th を穂先へ向けて細らせる）。中心線は (r,z) の制御点を
#       catmull で補間し、外穂は反って先で内に巻き、内穂は短く途中で止まる。
#       糸＝外穂を 34 回くぐる螺旋（r に cos(N·θ) を足して内外に潜らせる）。
#       柄は節の膨らみを持つ竹の筒。boolean も object.scale も使わない（#15）。
#
# 光：内包。穂の籠の**内側にだけ**在る細い紡錘（回転体）。
#     🔴 #40②：格子の奥に大きな発光面を置くと必ず行灯になる。だから紡錘は
#     ①穂より細く（内穂の内側に収まる）②発光するのは高さの一帯だけ で、
#     残りは ES=0 の純黒の裏当て（#32）＝開口は「明かり窓」でなく「割れ目」に落ちる。
#     方位は cos(θ-θ0)^PA の非対称な葉（#93③：対称の帯はネオン管、非対称は光）。
#
# 動き：①ヨー ±BETA°（sin＝厳密に閉じる）——軸対称の物なので穂は横へ流れ、
#       **内側の光の葉だけがこちらを向いたり背けたりする**＝光の振れはここで作る。
#       ②穂の開閉（シェイプキー1枚・v=0.5(1-cos2πt)）。締まると穂先が内に寄り持ち上がる。
#       🔴 開閉では光の面積は動かない（放射状の格子の被覆率はスケール不変＝#94 と同型）。
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

# --- 茶筅（原点＝穂の付け根。あとで bbox 中心へ寄せる）-------------
Z_SPLIT = -0.124                    # 割れはじめ＝柄の上端
Z_FOOT = -1.29                      # 柄の下端
R_GRIP = 0.086                      # 柄の半径
R_FOOT = 0.095
Z_FUSHI, D_FUSHI = -0.70, 0.048     # 節（膨らみ）

N_OUT, N_IN = 48, 20
W_OUT, T_OUT = 0.0150, 0.0038   # 🔴 4周目：断面が角材だと「針金」。竹の割り肌は平たい短冊       # 外穂：接線幅／半径方向の厚み（付け根）
W_IN,  T_IN = 0.0132, 0.0036
TAPER_W, TAPER_T = 0.52, 0.46       # 穂先で細る割合

# 外穂の中心線 (r, z)：糸のすぐ上で一気に反り、胴はほぼ直、先は内へ**鉤に巻く**
#   🔴 1周目：先が一点に集まる profile は「バルーン泡立て器」。実物の茶筅の先は
#   一点に集まらず、輪を残したまま内へ折り返す（最後の3点で z が下がる＝鉤）
OUTER_CP = [(0.084, Z_SPLIT), (0.136, -0.034), (0.218, 0.068), (0.288, 0.172),
            (0.340, 0.278), (0.382, 0.388), (0.416, 0.498), (0.444, 0.600),
            (0.462, 0.686), (0.448, 0.744), (0.412, 0.780), (0.372, 0.792),
            (0.344, 0.784)]
# 内穂 (r, z)：短く、途中で止まる（茶に触れない穂）
INNER_CP = [(0.072, Z_SPLIT), (0.104, -0.034), (0.166, 0.062), (0.222, 0.160),
            (0.262, 0.256), (0.286, 0.346), (0.294, 0.420), (0.288, 0.482),
            (0.274, 0.540), (0.256, 0.588), (0.242, 0.616)]

CLOSE_O, CLOSE_I = 0.22, 0.08       # 締まったときに r が縮む率（穂先で最大）
LIFT_O, LIFT_I = 0.034, 0.026       # 締まると穂先が持ち上がる
RAMP_P = 1.7

# --- 糸（外穂をくぐる螺旋）----------------------------------------
ITO_TURNS = 2.55
ITO_Z0, ITO_Z1 = -0.048, 0.044
ITO_AMP = 0.0150                    # 内外に潜る量
ITO_R = 0.0102                      # 糸の太さ

# --- 光（籠の内側の紡錘・回転体）----------------------------------
# 🔴 3周目：籠の中に別の物として浮かぶ紡錘は、何をしても「光る緑のグミ」（#92③）。
#    正しくは**光は物の内側の面**であること＝**内穂がその上に載る**envelope にする。
#    だから GLOW_CP は INNER_CP と同じ線（＝割り残した竹の肉）。樋の谷を内穂の方位に
#    合わせると（cos(N_IN·θ) の谷＝2π(i+0.5)/N_IN）、稜が黒い割れ目のあいだから盛り上がる。
GLOW_CP = [(0.000, -0.152), (0.052, -0.138), (0.070, Z_SPLIT), (0.101, -0.034),
           (0.161, 0.062), (0.215, 0.160), (0.254, 0.256), (0.277, 0.346),
           (0.285, 0.420), (0.264, 0.468), (0.216, 0.498), (0.128, 0.516),
           (0.000, 0.526)]
N_FLUTE, FLUTE = 20, 0.050          # 樋（谷＝内穂の位置）
ZB = 0.240                          # 発光の帯の中心
SZ_DN, SZ_UP = 0.186, 0.206         # 🔴 4周目：上を切ると光の上に黒い兜が載って「莢」に読める
TH0 = -math.pi / 2 - 0.30           # 光の葉の方位（局所）。🔴 カメラ側は θ=-90°（+X から測る）
PA = 2.3                            # 葉の鋭さ
ES_CORE = 3.6
WHITE_FROM, WHITE_TO = 0.30, 0.85   # 🔴 #85②：halo は白へ抜ける“面積”で買う（強さでは買えない）
K_MIX = 16.0
E_FLOOR = 0.12                      # 🔴 #85①：裾を 0 に切らないと全面発光になる

# --- 動き --------------------------------------------------------
YAW0, BETA = 10.0, 44.0
TILT0, DTILT = 14.0, 5.0    # 🔴 #33：リグごと傾けて口をこちらへ向けると「籠」が「器」に転ぶ
BOB = 0.030
CX, CZ = 0.55, 2.26
Z_SHIFT = 0.274                     # bbox 中心を原点へ
STILL_FRAME = 114


# =============================================================
# 純 math（Blender を起動せずに走る）
# =============================================================
def catmull(P, n_per=14):
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for s in range(n_per):
            u = s / n_per; u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u
                                    + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u3) for c in range(2)))
    out.append(P[-1])
    return out


PATH_OUT = catmull(OUTER_CP, 10)
PATH_IN = catmull(INNER_CP, 12)
PATH_GLOW = catmull(GLOW_CP, 10)


def jitter(i, k):
    """穂ごとの手割りの不揃い。決定的（乱数を使わない＝再現する）"""
    return math.sin((i + 1) * 2.3999632297 + k * 1.7)


def tine_line(path, i, n, close, lift, shut, wobble=1.0):
    """穂 i の中心線 [(r, z, s)]。shut=0 開／1 締まる"""
    m = len(path)
    lf = 1.0 + 0.040 * wobble * jitter(i, 0)          # 長さの不揃い
    rf = 1.0 + 0.052 * wobble * jitter(i, 1)          # 反りの不揃い
    out = []
    for k in range(m):
        s = k / (m - 1)
        r, z = path[k]
        r *= 1.0 + (rf - 1.0) * s
        z = z * (1.0 if z <= Z_SPLIT else 1.0) + (lf - 1.0) * s * (z - Z_SPLIT)
        ramp = s ** RAMP_P
        r *= 1.0 - close * ramp * shut
        z += lift * ramp * shut
        out.append((r, z, s))
    return out


def theta_out(i, shut=0.0):
    return 2 * math.pi * i / N_OUT + 0.30 * (2 * math.pi / N_OUT) * jitter(i, 2)


def theta_in(i, shut=0.0):
    # 🔴 ジッタを入れない：樋の谷（cos(N_IN·θ) の谷）と厳密に合わせるため
    return 2 * math.pi * (i + 0.5) / N_IN


def shut_of(t):
    return 0.5 - 0.5 * math.cos(2 * math.pi * t)


def yaw_of(t):
    return math.radians(YAW0 + BETA * math.sin(2 * math.pi * t))


def tilt_of(t):
    return math.radians(TILT0 + DTILT * math.cos(2 * math.pi * t))


def glow_R(z):
    """紡錘の半径（高さ z）。範囲外は 0"""
    if z <= PATH_GLOW[0][1] or z >= PATH_GLOW[-1][1]:
        return 0.0
    for k in range(len(PATH_GLOW) - 1):
        r0, z0 = PATH_GLOW[k]; r1, z1 = PATH_GLOW[k + 1]
        if z0 <= z <= z1 and z1 > z0:
            u = (z - z0) / (z1 - z0)
            return r0 + (r1 - r0) * u
    return 0.0


def emit_E(th_local, z):
    fz = math.exp(-((z - ZB) / (SZ_DN if z < ZB else SZ_UP)) ** 2)
    c = math.cos(th_local - TH0)
    fa = max(0.0, c) ** PA
    return fz * fa


def tine_r_at(line, z):
    for k in range(len(line) - 1):
        r0, z0, _ = line[k]; r1, z1, _ = line[k + 1]
        if (z0 - z) * (z1 - z) <= 0 and abs(z1 - z0) > 1e-9:
            u = (z - z0) / (z1 - z0)
            return r0 + (r1 - r0) * u, line[k][2]
    return None


def tine_w_at(s, w0, t0):
    return w0 * (1 - TAPER_W * s), t0 * (1 - TAPER_T * s)


def visible_lime(t, NX=90, NZ=90):
    """画面で積分する：紡錘の手前の面のうち、E>E_FLOOR で穂に隠れていない画素の数"""
    sh, ph = shut_of(t), yaw_of(t)
    lines_o = [(tine_line(PATH_OUT, i, N_OUT, CLOSE_O, LIFT_O, sh), theta_out(i) + ph,
                W_OUT, T_OUT) for i in range(N_OUT)]
    lines_i = [(tine_line(PATH_IN, i, N_IN, CLOSE_I, LIFT_I, sh), theta_in(i) + ph,
                W_IN, T_IN) for i in range(N_IN)]
    zlo, zhi = PATH_GLOW[0][1], PATH_GLOW[-1][1]
    rmax = max(r for r, _ in PATH_GLOW)
    hit = 0
    for iz in range(NZ):
        z = zlo + (zhi - zlo) * (iz + 0.5) / NZ
        R = glow_R(z)
        if R <= 1e-6:
            continue
        for ix in range(NX):
            x = -rmax + 2 * rmax * (ix + 0.5) / NX
            if abs(x) >= R:
                continue
            th = -math.acos(max(-1.0, min(1.0, x / R)))       # 手前側（sin<0）
            if emit_E(th - ph, z) <= E_FLOOR:
                continue
            y_s = R * math.sin(th)
            blocked = False
            for lines in (lines_o, lines_i):
                for line, al, w0, t0 in lines:
                    got = tine_r_at(line, z)
                    if got is None:
                        continue
                    r, s = got
                    a = al
                    if math.sin(a) >= 0:
                        continue
                    if r * math.sin(a) >= y_s:                # 紡錘より奥
                        continue
                    w, th_ = tine_w_at(s, w0, t0)
                    half = 0.5 * (w * abs(math.sin(a)) + th_ * abs(math.cos(a)))
                    if abs(x - r * math.cos(a)) < half:
                        blocked = True
                        break
                if blocked:
                    break
            if not blocked:
                hit += 1
    return hit


modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["probe"]

if "geom" in modes:
    print(">> 幾何の検算（Blender を起動しない・#31/#40⑥）")
    rmax = max(r for r, _ in PATH_GLOW)
    print("   紡錘の最大半径 %.3f" % rmax)
    for zc in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70):
        go = tine_r_at(tine_line(PATH_OUT, 0, N_OUT, CLOSE_O, LIFT_O, 1.0, 0.0), zc)
        gi = tine_r_at(tine_line(PATH_IN, 0, N_IN, CLOSE_I, LIFT_I, 1.0, 0.0), zc)
        print("   z %.2f  紡錘 %.3f | 外穂(締) %s | 内穂(締) %s"
              % (zc, glow_R(zc),
                 "%.3f" % go[0] if go else "—", "%.3f" % gi[0] if gi else "—"))
    vals = []
    for f in range(0, N_FRAMES, 4):
        t = f / N_FRAMES
        vals.append((f, visible_lime(t)))
    mx = max(v for _, v in vals); mn = min(v for _, v in vals)
    print("   見える発光画素（相対）")
    for f, v in vals:
        print("     f%3d  yaw %+6.1f°  shut %.2f  %5d  %s"
              % (f + 1, math.degrees(yaw_of(f / N_FRAMES)), shut_of(f / N_FRAMES), v,
                 "#" * int(40 * v / max(1, mx))))
    print("   🔴 光の振れ（最大/最小）= %.2f  （motion.py の下限 1.22）" % (mx / max(1, mn)))
    best = max(vals, key=lambda kv: kv[1])
    print("   最も光るフレーム f%d" % (best[0] + 1))
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

# ---------- マテリアル（MATERIALS.md・#52）----------
#   竹＝漆より少しだけ粗い（割り肌は艶があるが塗りではない）。🔴 Metallic は使わない（#92①）
TAKE = dict(rough=0.44, spec=0.26)
ITO_M = dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25)     # 糸＝布（厚物）


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
    if r.get("sheen"):
        p.inputs["Sheen Weight"].default_value = r["sheen"]
        p.inputs["Sheen Roughness"].default_value = r["sheen_rough"]
        p.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_take, kp_ = principled("take"); apply_black(kp_, TAKE)
mat_ito, ip_ = principled("ito"); apply_black(ip_, ITO_M)


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
    apply_black(blk, TAKE)                                  # 🔴 #32：裏当ては純黒
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


# ---------- 穂（外＋内を1つのメッシュに。シェイプキー1枚で開閉）----------
def tine_coords(shut):
    """全穂の頂点座標を決まった順で返す（基底とシェイプキーで同じ生成器＝#74③）"""
    co = []
    for path, N, th_f, close, lift, w0, t0 in (
            (PATH_OUT, N_OUT, theta_out, CLOSE_O, LIFT_O, W_OUT, T_OUT),
            (PATH_IN, N_IN, theta_in, CLOSE_I, LIFT_I, W_IN, T_IN)):
        for i in range(N):
            a = th_f(i)
            ca, sa = math.cos(a), math.sin(a)
            line = tine_line(path, i, N, close, lift, shut)
            for k, (r, z, s) in enumerate(line):
                if k == 0:
                    dr, dz = line[1][0] - r, line[1][1] - z
                elif k == len(line) - 1:
                    dr, dz = r - line[k - 1][0], z - line[k - 1][1]
                else:
                    dr, dz = line[k + 1][0] - line[k - 1][0], line[k + 1][1] - line[k - 1][1]
                ln = math.hypot(dr, dz) or 1.0
                dr, dz = dr / ln, dz / ln
                w, th_ = tine_w_at(s, w0, t0)
                # 断面：法線 n=(dz,-dr) を半径方向に、接線 (-sa, ca) を幅方向に
                for sgn_t, sgn_w in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
                    rr = r + sgn_t * 0.5 * th_ * dz
                    zz = z - sgn_t * 0.5 * th_ * dr
                    co.append((rr * ca - sgn_w * 0.5 * w * sa,
                               rr * sa + sgn_w * 0.5 * w * ca,
                               zz + Z_SHIFT))
    return co


def tine_mesh(name):
    bm = bmesh.new()
    co = tine_coords(0.0)
    verts = [bm.verts.new(c) for c in co]
    bm.verts.ensure_lookup_table()
    p = 0
    for path, N in ((PATH_OUT, N_OUT), (PATH_IN, N_IN)):
        m = len(path)
        for _ in range(N):
            base = p
            for k in range(m - 1):
                a = [verts[base + 4 * k + j] for j in range(4)]
                b = [verts[base + 4 * (k + 1) + j] for j in range(4)]
                for j in range(4):
                    j2 = (j + 1) % 4
                    bm.faces.new((a[j], a[j2], b[j2], b[j]))
            bm.faces.new([verts[base + j] for j in range(4)][::-1])
            bm.faces.new([verts[base + 4 * (m - 1) + j] for j in range(4)])
            p += 4 * m
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def handle_mesh(name, NZ=64, NA=28):
    """柄：節の膨らみを持つ竹の筒。上端は割れはじめ"""
    bm = bmesh.new()
    rings = []
    for i in range(NZ + 1):
        u = i / NZ
        z = Z_FOOT + (Z_SPLIT - Z_FOOT) * u
        r = R_FOOT + (R_GRIP - R_FOOT) * u
        d = (z - Z_FUSHI) / D_FUSHI
        r *= (1.0 + 0.085 * math.exp(-d * d) + 0.020 * math.exp(-((z - Z_SPLIT) / 0.055) ** 2)
              + 0.011 * math.sin(6.2 * z + 0.8))      # 竹は真っ直ぐではない（つるりとした円柱＝ゴムの握り）
        ring = [bm.verts.new((r * math.cos(2 * math.pi * k / NA),
                              r * math.sin(2 * math.pi * k / NA), z + Z_SHIFT))
                for k in range(NA)]
        rings.append(ring)
    for i in range(NZ):
        for k in range(NA):
            k2 = (k + 1) % NA
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    # 底：面取りしてから塞ぐ（ブラント端は機械部品＝#21）
    cb = [bm.verts.new((v.co.x * 0.86, v.co.y * 0.86, Z_FOOT - 0.016 + Z_SHIFT)) for v in rings[0]]
    for k in range(NA):
        k2 = (k + 1) % NA
        bm.faces.new((rings[0][k2], rings[0][k], cb[k], cb[k2]))
    bm.faces.new(cb[::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def ito_mesh(name, NS=520, NA=8):
    """糸：外穂を 34 回くぐる螺旋（r に cos(N·θ) を足して内外へ潜る）"""
    bm = bmesh.new()
    rings = []
    for i in range(NS + 1):
        u = i / NS
        a = 2 * math.pi * ITO_TURNS * u
        z = ITO_Z0 + (ITO_Z1 - ITO_Z0) * u
        got = tine_r_at(tine_line(PATH_OUT, 0, N_OUT, CLOSE_O, LIFT_O, 0.0, 0.0), z)
        rbase = got[0] if got else 0.13
        r = rbase + ITO_AMP * math.cos(N_OUT * a)
        env = min(1.0, 6.0 * min(u, 1 - u))                 # 両端を細らせる（#21）
        c, s = math.cos(a), math.sin(a)
        ring = []
        for k in range(NA):
            b = 2 * math.pi * k / NA
            rr = r + ITO_R * env * math.cos(b)
            zz = z + ITO_R * env * math.sin(b)
            ring.append(bm.verts.new((rr * c, rr * s, zz + Z_SHIFT)))
        rings.append(ring)
    for i in range(NS):
        for k in range(NA):
            k2 = (k + 1) % NA
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def glow_mesh(name, NA=112):
    """籠の内側の紡錘。E＝高さの帯（非対称）×方位の葉（cos^PA）を UV に焼く"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    emap = {}
    prof = [(r, z) for r, z in PATH_GLOW]
    rings, tops = [], []
    for r, z in prof:
        if r <= 1e-6:
            v = bm.verts.new((0.0, 0.0, z + Z_SHIFT))
            emap[v] = emit_E(TH0, z)
            tops.append(v); rings.append(None)
            continue
        ring = []
        for k in range(NA):
            th = 2 * math.pi * k / NA
            rr = r * (1.0 + FLUTE * math.cos(N_FLUTE * th))
            v = bm.verts.new((rr * math.cos(th), rr * math.sin(th), z + Z_SHIFT))
            emap[v] = emit_E(th, z)
            ring.append(v)
        rings.append(ring); tops.append(None)
    for i in range(len(prof) - 1):
        a, b = rings[i], rings[i + 1]
        if a is None and b is not None:
            for k in range(NA):
                bm.faces.new((tops[i], b[k], b[(k + 1) % NA]))
        elif a is not None and b is None:
            for k in range(NA):
                bm.faces.new((a[(k + 1) % NA], a[k], tops[i + 1]))
        elif a is not None and b is not None:
            for k in range(NA):
                k2 = (k + 1) % NA
                bm.faces.new((a[k], a[k2], b[k2], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = (emap[lp.vert], 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
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


ob_ho = link(tine_mesh("m_ho"), "ho", [mat_take], smooth_ang=0.6)
ob_e = link(handle_mesh("m_e"), "e", [mat_take], smooth_ang=1.0)
ob_ito = link(ito_mesh("m_ito"), "ito", [mat_ito], smooth_ang=1.2)
ob_glow = link(glow_mesh("m_hikari"), "hikari", [mat_glow], smooth_ang=1.2)
parts = [ob_ho, ob_e, ob_ito, ob_glow]

# --- 開閉のシェイプキー（🔴 #43：bevel / remove_doubles は使えない）----
ob_ho.shape_key_add(name="Basis", from_mix=False)
sk_shut = ob_ho.shape_key_add(name="shut", from_mix=False)
for i, c in enumerate(tine_coords(1.0)):
    sk_shut.data[i].co = c

# --- キーフレーム（毎フレーム）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev = None
for f, idx in enumerate(FR_):
    t = idx / N_FRAMES
    g, a = yaw_of(t), tilt_of(t)
    Rz = Matrix.Rotation(g, 4, 'Z')
    Rx = Matrix.Rotation(a, 4, 'X')
    q = (Rz @ Rx).to_quaternion()
    if prev is not None and q.dot(prev) < 0.0:
        q.negate()
    prev = q.copy()
    C = Vector((CX, 0.0, CZ + BOB * math.sin(2 * math.pi * t)))
    for ob in parts:
        ob.location = C
        ob.rotation_quaternion = q
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_quaternion", frame=f + 1)
    sk_shut.value = shut_of(t)
    sk_shut.keyframe_insert("value", frame=f + 1)

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
        caption("MIDDLE STUDY 085 — CHASEN", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
back.visible_camera = False        # 🔴 #67①：穂のあいだは抜けている

# 🔴 #58③：随伴のライム光源は発光体の外。籠の裏・床寄り
for sx, sy, sz, wt in ((-0.36, 2.2, 0.26, LIME_W), (0.10, 4.6, 0.26, LIME_W),
                       (0.62, 7.8, 0.26, LIME_W)):
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
      " yaw %.1f°  shut %.2f" % (math.degrees(yaw_of(tH)), shut_of(tH)))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 61, 91):
        scene.frame_set(fr); dg.update()
        allx, ally = [], []
        for ob in parts:
            ev = ob.evaluated_get(dg)
            for v in list(ev.data.vertices)[::3]:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                allx.append(c.x); ally.append(c.y)
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        sl = max(0.0, min(x1, 1) - max(x0, 0))
        sh = max(0.0, min(y1, 1) - max(y0, 0))
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  中心y(上から) %.1f%%"
              % (fr, x0, x1, y0, y1, sl * 100, sh * 100, edge, (1 - (y0 + y1) / 2) * 100))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_085.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("take_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = TAKE["rough"]
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.34
    for ob in (ob_ho, ob_e, ob_ito):
        ob.data.materials[0] = m_bk
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
