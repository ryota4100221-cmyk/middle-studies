# =============================================================
# MIDDLE STUDY 059 — WARIFU（割符 / a tally split in two）
#
# 黒い札が二枚、離れて浮かんでいる。もとは一枚だった——割れ口が噛み合うから、そう分かる。
# 光っているのは札ではない。**割れ口（破面）だけ**が ライム #A5E02E に灯っている。
# その灯りがいちばん強いのは、札のちょうど真ん中の高さ。
# 二枚がゆっくり首を振り、割れ口をそろえてこちらへ開いた一瞬にだけ、光は幅を持つ。
# 向かい合えば、光は輪郭に張りついた一本の線に細る。
# **証しは、どちらの半分にも書かれていない。合わせたときの、あいだにしかない。**
#
# 🔴 光の型＝**稜線**（#53：58作で5作の最少タイ。002 OBI／032 SUZU／053 UKIDAMA）
# 🔴 構図の型＝**対**（#57：58作中51作が「全身」。対は 055 IGATA の1作のみ）
#    🔴 対＝`clusters==2`。**ライムを二つの塊から離して宙に置くと3塊になって落ちる。**
#       だから光は必ず塊の上に載せる——これが稜線を選んだ理由（好みではなく設計上の帰結）。
#    🔴 #67⑤（背光×寄りは原理的に両立しない）と同型の検算を先にやった：
#       **背光×対**も成立しない。背光は「光源が背後」＝あいだに光の島ができ `clusters==3`。
# 【ドメイン】証・割符（シリーズ未踏）。直近10作＝空・凧／運搬・車輪／盤上遊戯／鋳造／
#            植物・果実／漁労／楽器・打／貨幣／玩具・けん玉／武・弓 と別。
#            020 TSUGITE【木工・継手】は「離すと実体（ほぞ）が現れる」＝正負の反転、
#            042 KINTSUGI【工芸・繕い】は「割れを継ぐ」＝どちらも別物。**割符は継がない。**
#            055 IGATA【鋳造】も対だが、あちらは「空洞が主題」でこちらは「破面が主題」。
#
# 機構＝**鏡像のヨー（mirrored yaw）**：δ(t) = D_FAR + (D_NEAR−D_FAR)·a(t)、a(t)=0.5(1−cos2πt)
#   左 φ = −δ ／ 右 φ = π + δ。**二枚が鏡像で首を振る＝片方だけでは成立しない機構。**
#   整数周期で厳密に閉じ、**回転キーだけ**なので glb にそのまま乗る（#60）。
#   🔴 017 KAGIANA・051 ZENI の「回して見せる」と同族であることを隠さない。違いは
#      **基準がカメラでなく相手**であること——δ は「相手の破面に対して何度開いているか」で、
#      対の二体が同じ量だけ、逆向きに開く。
#
# 🔴 割れ線 B(zn) は三角波の和（角がある＝割れは滑らかな曲線ではない）。**二枚は同じ B を共有し、
#    片方が符号を反転して持つ**ので、右を π 回すと厳密に噛み合う相補形になる＝題材が式に入っている。
# 🔴 造形は boolean 不使用。角のある長方形断面（超楕円 p=8）を高さ方向に積み、割れ側の x を B(zn) にするだけ。
#
# ── 10周ぶんの没案と実測（詳細は LOG.md）
#   ・1〜5周：題材は「磐座（二つの立石）」だった。手続き生成した岩は**必ず滑らかな莢**になり、
#     BACKLOG の発想ルール③「スカルプト的な有機形状は避ける」に自分で違反していた。**題材ごと替えた。**
#   ・#40⑥ が 0.963→0.860→0.795 と下がりきらなかった真犯人は、**稜そのもの**。丸められた角の法線は
#     カメラを正面から向くので、首を振っても量が変わらない。**平らな破面だけ**を光らせて 0.627。
#   ・halo の実体は**床のライム溜まり**だった。溜まりを消すと halo 44,532→1,069。
#     #58（床）・#51（halo）・#57（塊の数）は同じ画素を奪い合う（#68④）。
#   ・DISPLACE 0.009 は 480px では1画素も出ず、1600px で**段ボールの縞**になった（#68）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 立石2つ（対）------------------------------------------------
#   xf＝刈り面の局所x（＝割れ面）。vs＝筋を載せる側（-1: 局所−y / +1: 局所+y＝カメラ側）
#   sgn＝首振りの向き（鏡像）。phi0＝基準の向き
STONES = [
    dict(name="hidari", cx=0.307, cy=0.020, z0=1.620, z1=2.770, w=0.800, t=0.070,
         bs=+1.0, vs=-1, sgn=-1.0, phi0=0.0, vwb=0.062, vwf=0.0008),
    dict(name="migi", cx=0.847, cy=-0.010, z0=1.620, z1=2.770, w=0.660, t=0.070,
         bs=-1.0, vs=+1, sgn=+1.0, phi0=math.pi, vwb=0.062, vwf=0.0008),
]
# 首振り：δが小さい＝二つの割れ面が真っ向から向かい合う（筋は輪郭に張りついた一本の線）
#         δが大きい＝そろってこちらへ開く（筋に幅が生まれる＝hero）
D_FAR = math.radians(2.2)
D_NEAR = math.radians(36.0)


# --- 筋の光 -----------------------------------------------------
ES_CORE = 3.8
EM_P = 0.75                  # 帯を横断する減衰（ふちが芯・内側へ落ちる）
GZ_P, GZ_E = 1.6, 1.10       # 高さ方向：**札のちょうど真ん中がいちばん明るい**
FAC_LO, FAC_P = 0.90, 1.0    # #65②③：純発光体に法線依存を弱く掛ける
VOFF = 0.004                 # 割れ面からの持ち出し

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
LIME_W = 95.0
FRAME_W, FRAME_H = 2.81, 3.52

NTH, NZR = 20, 26            # 石の格子（粗く取って面を出す・flat shading）
NVZ, NVC = 110, 10             # 筋の格子（縦・帯の横断）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def a_of(t):
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * t))


def delta_of(t):
    return D_FAR + (D_NEAR - D_FAR) * a_of(t)


def tri(u):
    """三角波（−1..1）。角がある＝**割れ線は滑らかな曲線ではない**"""
    return 4.0 * abs(u - math.floor(u + 0.5)) - 1.0


def brk(zn):
    """🔴 割れ線。**二枚は同じ B(zn) を共有する**（片方は符号を反転して持つ＝bs）。
       だから局所では同じ形で組み、右を π 回すと**互いに噛み合う相補形**になる。
       ——合わせたときにだけ本物と分かる、という題材そのものが、この1行に入っている。"""
    return (0.030 * tri(3.2 * zn + 0.13)
            + 0.014 * tri(7.7 * zn + 0.61)
            + 0.022 * tri(1.4 * zn + 0.29))


def end_scale(zn, e=0.045):
    """札の天地を丸めて閉じる"""
    if zn < e:
        u = (e - zn) / e
    elif zn > 1.0 - e:
        u = (zn - (1.0 - e)) / e
    else:
        return 1.0
    return math.sqrt(max(0.0, 1.0 - u * u))


SE_P = 8.0      # 断面の超楕円：角を持った長方形（丸めすぎると「石鹸」になる）
NOL = 720


def sec_geom(S, zn):
    """その高さの断面（中心・半幅・半厚）。割れ側の x が B(zn)"""
    sc = end_scale(zn)
    x1 = S["bs"] * brk(zn)
    x0 = -S["w"]
    cx, hx = 0.5 * (x0 + x1), 0.5 * (x1 - x0)
    return cx, hx * sc, 0.5 * S["t"] * sc


def outline(S, zn):
    """断面の閉じた折れ線（角のある長方形＝超楕円）"""
    cx, hx, hy = sec_geom(S, zn)
    pts = []
    for i in range(NOL):
        u = 2 * math.pi * i / NOL
        c, sn = math.cos(u), math.sin(u)
        pts.append((cx + hx * (1 if c >= 0 else -1) * abs(c) ** (2.0 / SE_P),
                    hy * (1 if sn >= 0 else -1) * abs(sn) ** (2.0 / SE_P)))
    return pts


def vein_row(S, zn):
    """🔴 筋は「面の上の帯」ではなく **割れ口（破面）の、手前の稜に載る帯**。
       断面の外形線を弧長で歩き、稜を中心に左右へ同じ長さだけ伸ばす。
       帯は破面の厚みぶんを覆い、角で折れて表の面へ少しだけ回り込む
       ＝**どの向きでも輪郭の上の一本**に見える（宣言した「稜線」が絵で保たれる）。
       返すのは [(局所点, 局所外向き法線, s)]（s∈[0,1]・0.5 が稜）"""
    if end_scale(zn) < 0.25:
        return None
    pts = outline(S, zn)
    # 稜の位置は解析的：割れ側(+x)かつカメラ側(vs) の角＝超楕円の u = ∓π/4
    u_c = (-math.pi / 4.0) if S["vs"] < 0 else (math.pi / 4.0)
    ic = int(round((u_c % (2 * math.pi)) / (2 * math.pi) * NOL)) % NOL
    # 🔴 帯を稜の**左右で同じ長さ**にすると、首を振っても表と破面が入れ替わるだけで
    #    見えている発光が動かない（実測 #40⑥ = 0.963＝不合格）。
    #    帯の大半を**破面（割れ口）**に置き、表の面へは稜をまたぐ細い縁だけ回す。
    #    こうすると「破面が見えているか」がそのまま光の量になる。
    hw_b, hw_f = S["vwb"], S["vwf"]
    hw_fwd, hw_bwd = (hw_b, hw_f) if S["vs"] < 0 else (hw_f, hw_b)

    def walk(step, HW):
        out, acc, i = [], 0.0, ic
        while acc < HW:
            j = (i + step) % NOL
            acc += math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
            out.append((j, acc))
            i = j
            if len(out) > NOL // 2:
                break
        return out

    fwd, bwd = walk(+1, hw_fwd), walk(-1, hw_bwd)
    if not fwd or not bwd:
        return None
    seq = [(j, -a) for (j, a) in reversed(bwd)] + [(ic, 0.0)] + [(j, a) for (j, a) in fwd]
    row = []
    for (j, a) in seq:
        P = pts[j]
        Q, O = pts[(j + 1) % NOL], pts[(j - 1) % NOL]
        tx, ty = Q[0] - O[0], Q[1] - O[1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = ty / L, -tx / L
        cx, _, _ = sec_geom(S, zn)
        if nx * (P[0] - cx) + ny * P[1] < 0:
            nx, ny = -nx, -ny
        on_break = (a >= 0) if S["vs"] < 0 else (a <= 0)
        e = cross_e(a, hw_b, hw_f, on_break) * gz(zn)
        row.append(((P[0] + nx * VOFF, P[1] + ny * VOFF), (nx, ny), e))
    return row


def gz(zn):
    """高さ方向：**札のちょうど真ん中がいちばん明るい**（＝タグラインの直訳）"""
    return (1.0 - abs(2.0 * zn - 1.0) ** GZ_P) ** GZ_E


def cross_e(a, hw_b, hw_f, on_break):
    """帯を横断する発光。🔴 稜を芯にした山型にすると、**破面の大半が暗くなって
       首を振っても光の量が動かない**（#40⑥ 0.86＝不合格になった）。
       破面はほぼ一様に光らせ、**縁でだけ 0 に落とす**（#49①）。表の面へ回した縁は速く落とす。"""
    if on_break:
        q = min(1.0, abs(a) / hw_b)
        # 🔴 稜そのもの（丸められた角）を光らせると #40⑥ が動かない——角の法線はカメラを
        #    正面から向くので首を振っても量が変わらない。**平らな破面だけ**を光らせる。
        ramp = min(1.0, max(0.0, (q - 0.14) / 0.10))
        fall = (1.0 - max(0.0, (q - 0.34) / 0.66) ** 2.0) ** 0.85
        return ramp * fall
    q = min(1.0, abs(a) / hw_f)
    return (1.0 - q) ** 0.9


ZN_LO, ZN_HI = 0.045, 0.955


def light_visible(t, want_area=False):
    """🔴 #40⑥ は幾何で積分する（#46/#64②）＝**見えている発光**。
       E × max(0, n̂·v̂) を帯の上で積分する。帯は稜（角）に載っていて外を向いているので、
       石本体による自己遮蔽は起きない（面が背へ回れば n̂·v̂ が先に 0 になる）。"""
    d = delta_of(t)
    C = CAM_LOC
    tot = 0.0
    area = 0.0
    for S in STONES:
        phi = S["phi0"] + S["sgn"] * d
        cp, sp_ = math.cos(phi), math.sin(phi)
        dz = (S["z1"] - S["z0"]) * (ZN_HI - ZN_LO) / NVZ
        for iz in range(NVZ):
            zn = ZN_LO + (ZN_HI - ZN_LO) * (iz + 0.5) / NVZ
            row = vein_row(S, zn)
            if row is None or len(row) < 3:
                continue
            z = S["z0"] + zn * (S["z1"] - S["z0"])
            for k in range(len(row) - 1):
                (lx, ly), (lnx, lny), ek = row[k]
                (mx, my), _, ek2 = row[k + 1]
                seg = math.hypot(mx - lx, my - ly)
                if seg <= 0.0:
                    continue
                X = S["cx"] + lx * cp - ly * sp_
                Y = S["cy"] + lx * sp_ + ly * cp
                nx, ny = lnx * cp - lny * sp_, lnx * sp_ + lny * cp
                vx, vy, vz = C[0] - X, C[1] - Y, C[2] - z
                L = math.sqrt(vx * vx + vy * vy + vz * vz)
                fac = (nx * vx + ny * vy) / L
                if fac <= 0.0:
                    continue
                dA = seg * dz
                tot += 0.5 * (ek + ek2) * fac * dA
                area += fac * dA
    return (tot, area) if want_area else tot


_VS = [light_visible(i / N_FRAMES) for i in range(N_FRAMES)]
_VMAX = max(_VS)
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _VS[i]) + 1


def proj_xz(P):
    """被写体面（y=0）に立てた枠での正規化画面座標（透視で 0..1）"""
    C = CAM_LOC
    dy = P[1] - C[1]
    if dy <= 0.05:
        return None
    s = (0.0 - C[1]) / dy
    x = C[0] + s * (P[0] - C[0])
    z = C[2] + s * (P[2] - C[2])
    return ((x - (AIM_X - FRAME_W / 2)) / FRAME_W,
            ((LOOK_Z + FRAME_H / 2) - z) / FRAME_H)


def silhouette(t):
    """札の表面を粗く撒いて、画面上の範囲と「二つの塊が離れているか」を見る"""
    d = delta_of(t)
    boxes = []
    for S in STONES:
        phi = S["phi0"] + S["sgn"] * d
        cp, sp_ = math.cos(phi), math.sin(phi)
        us, vs_ = [], []
        for iz in range(25):
            zn = iz / 24
            z = S["z0"] + zn * (S["z1"] - S["z0"])
            cx, hx, hy = sec_geom(S, zn)
            for it in range(32):
                u = 2 * math.pi * it / 32
                c, sn = math.cos(u), math.sin(u)
                lx = cx + hx * (1 if c >= 0 else -1) * abs(c) ** (2.0 / SE_P)
                ly = hy * (1 if sn >= 0 else -1) * abs(sn) ** (2.0 / SE_P)
                P = (S["cx"] + lx * cp - ly * sp_, S["cy"] + lx * sp_ + ly * cp, z)
                uv = proj_xz(P)
                if uv:
                    us.append(uv[0]); vs_.append(uv[1])
        boxes.append((min(us), max(us), min(vs_), max(vs_)))
    return boxes


if "--probe-only" in sys.argv:
    th = (STILL_FRAME - 1) / N_FRAMES
    print(">> STILL_FRAME %d (t=%.3f, a=%.3f, δ=%.1f°)"
          % (STILL_FRAME, th, a_of(th), math.degrees(delta_of(th))))
    print(">> #40(6) 見える光 min/max = %.3f  （合格 0.75以下）" % (min(_VS) / _VMAX))
    print(">> ループの閉じ: V(0)=%.6f V(1)=%.6f 差 %.2e  a(0)=%.6f a(1)=%.6f"
          % (_VS[0], light_visible(1.0), abs(_VS[0] - light_visible(1.0)), a_of(0), a_of(1)))
    _, ar = light_visible(th, want_area=True)
    body = FRAME_W * FRAME_H * 0.80
    print(">> 発光の投影面積 %.4f m² ＝ 上80%%の枠 %.4f m² の %.2f%%（#51 の帯 0.8〜12.0）"
          % (ar, body, ar / body * 100))
    for label, tt in (("hero", th), ("δ小(向かい合う)", 0.0), ("δ大", 0.5)):
        bx = silhouette(tt)
        (l0, r0, t0, b0), (l1, r1, t1, b1) = bx
        L, R = min(l0, l1), max(r0, r1)
        T, B = min(t0, t1), max(b0, b1)
        gap = l1 - r0
        print(">> %-14s 画面 x %.3f..%.3f (長辺%.1f%%)  y %.3f..%.3f (%.1f%%)  重心x %.1f%%"
              % (label, L, R, max(R - L, B - T) * 100, T, B, (B - T) * 100, (L + R) / 2 * 100))
        print("   %-14s あいだ %.3f（=%.0fpx@1600 ／ 6pxグリッドで%.1fセル）  枠まで 左%.3f 右%.3f 上%.3f"
              % ("", gap, gap * 1600, gap * 1600 / 6, L, 1 - R, T))
    # 🔴 #40⑥ が動かないときは「どの面が効いていないか」を見る（灯でなく面で切り分ける＝#67②）
    for lab, tt in (("δ小", 0.0), ("δ大", 0.5)):
        d = delta_of(tt); C = CAM_LOC
        acc = {"破面": 0.0, "表の縁": 0.0}
        for S in STONES:
            phi = S["phi0"] + S["sgn"] * d
            cp, sp_ = math.cos(phi), math.sin(phi)
            dz = (S["z1"] - S["z0"]) * (ZN_HI - ZN_LO) / NVZ
            for iz in range(NVZ):
                zn = ZN_LO + (ZN_HI - ZN_LO) * (iz + 0.5) / NVZ
                row = vein_row(S, zn)
                if not row:
                    continue
                z = S["z0"] + zn * (S["z1"] - S["z0"])
                nb = len(row) // 2
                for k in range(len(row) - 1):
                    (lx, ly), (lnx, lny), ek = row[k]
                    (mx, my), _, ek2 = row[k + 1]
                    seg = math.hypot(mx - lx, my - ly)
                    X = S["cx"] + lx * cp - ly * sp_
                    Y = S["cy"] + lx * sp_ + ly * cp
                    nx, ny = lnx * cp - lny * sp_, lnx * sp_ + lny * cp
                    vx, vy, vz = C[0] - X, C[1] - Y, C[2] - z
                    L = math.sqrt(vx * vx + vy * vy + vz * vz)
                    fac = (nx * vx + ny * vy) / L
                    if fac <= 0:
                        continue
                    on_b = (k >= nb) if S["vs"] < 0 else (k <= nb)
                    acc["破面" if on_b else "表の縁"] += 0.5 * (ek + ek2) * fac * seg * dz
        print(">> %-4s 内訳  破面 %.5f  表の縁 %.5f" % (lab, acc["破面"], acc["表の縁"]))
    print(">> 「対」＝ clusters==2 かつ 最大塊≦72%% ／ 占有は長辺 55〜65%%")
    for i in range(0, N_FRAMES, 10):
        t = i / N_FRAMES
        print("   t=%.3f  a=%.3f  δ=%5.1f°  光 %5.1f%%"
              % (t, a_of(t), math.degrees(delta_of(t)), 100 * _VS[i] / _VMAX))
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
    # 石＝陶（MATERIALS.md「焼き物・石・土・瓦・臼・硯＝触ると少しざらつくもの」）
    "touki":  dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10),
    # 木札（この作専用）＝木に **金属度**を足したもの。#57②：平らな面を正対させる題材は
    # 鏡面や粗さをいくら振っても白い studio を映して灰色の板になる。metal でだけ黒へ戻る
    # （#0a0a0a の金属は反射が地の色で色づく＝白を浴びても黒い・#66④）
    "fuda":   dict(rough=0.66, spec=0.30, metal=0.30, disp=0.0035, dsize=0.10),
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25, disp=0.004, dsize=0.05),
    "nuno_usu": dict(rough=0.66, spec=0.28, sheen=0.55, sheen_rough=0.25),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
    # 注連縄＝厚物の布に **金属度**を足したもの。#68②：細い丸みの稜線は白い studio を
    # そのまま映して白い帯になる。#0a0a0a の金属は白を浴びても黒い（#57②/#66④）
    "nawa":   dict(rough=0.78, spec=0.24, sheen=0.50, sheen_rough=0.25, metal=0.25,
                   disp=0.004, dsize=0.05),
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


mat_ishi = black_material("fuda", "fuda")


def vein_material(name):
    """筋＝黒い石の割れ面のふちに走る一本。勾配は **UV に焼いた E**（#34/#39）。
       ふちで芯・内側へ落ち、**高さの真ん中で最大**（=タグラインの直訳）。"""
    m, p = principled(name)
    set_black(p, "fuda")
    nt = m.node_tree
    p.inputs["Base Color"].default_value = BLACK      # #68⑤：下地に色を置かない
    p.inputs["Emission Color"].default_value = LIME

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    # 🔴 #65②：純発光体は陰影を持たない。法線依存の項が無いと造形が丸ごと消える
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    fcp = mn('POWER', FAC_P); nt.links.new(lw.outputs["Facing"], fcp.inputs[0])
    fcs = mn('MULTIPLY', 1.0 - FAC_LO); nt.links.new(fcp.outputs[0], fcs.inputs[0])
    fca = mn('ADD', FAC_LO); nt.links.new(fcs.outputs[0], fca.inputs[0])

    # 🔴 #24：均一なベタ塗りはペンキに見える。石の目のムラを光そのものに乗せる
    ntx = nt.nodes.new("ShaderNodeTexNoise")
    ntx.inputs["Scale"].default_value = 38.0
    ntx.inputs["Detail"].default_value = 6.0
    ntx.inputs["Roughness"].default_value = 0.60
    nmr = nt.nodes.new("ShaderNodeMapRange"); nmr.clamp = True
    nmr.inputs["From Min"].default_value = 0.34; nmr.inputs["From Max"].default_value = 0.70
    nmr.inputs["To Min"].default_value = 0.55; nmr.inputs["To Max"].default_value = 1.15
    nt.links.new(ntx.outputs["Fac"], nmr.inputs["Value"])

    e1 = mn('MULTIPLY'); nt.links.new(xyz.outputs["X"], e1.inputs[0])
    nt.links.new(fca.outputs[0], e1.inputs[1])
    e0 = mn('MULTIPLY'); nt.links.new(e1.outputs[0], e0.inputs[0])
    nt.links.new(nmr.outputs["Result"], e0.inputs[1])
    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e0.outputs[0], e2.inputs[0])
    nt.links.new(e2.outputs[0], p.inputs["Emission Strength"])
    return m


mat_suji = vein_material("suji")

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


def stone_mesh(S):
    """割符の片割れ＝角のある長方形断面を高さ方向に積んだ板。**割れ側の x が B(zn)** で、
       そこだけが上下に蛇行する。boolean 不使用・押し出しだけ。"""
    bm = bmesh.new()
    NSEC = 56
    rings = []
    for iz in range(NZR + 1):
        zn = iz / NZR
        z = S["z0"] + zn * (S["z1"] - S["z0"])
        cx, hx, hy = sec_geom(S, zn)
        row = []
        for it in range(NSEC):
            u = 2 * math.pi * it / NSEC
            c, sn = math.cos(u), math.sin(u)
            row.append(bm.verts.new((cx + hx * (1 if c >= 0 else -1) * abs(c) ** (2.0 / SE_P),
                                     hy * (1 if sn >= 0 else -1) * abs(sn) ** (2.0 / SE_P), z)))
        rings.append(row)
    for iz in range(NZR):
        A, B = rings[iz], rings[iz + 1]
        for it in range(NSEC):
            j = (it + 1) % NSEC
            try:
                bm.faces.new([A[it], A[j], B[j], B[it]])
            except ValueError:
                pass
    return finish_mesh(bm, S["name"], bevel=0.0022, angle=30, smooth=True)


def vein_mesh(S):
    """筋＝割れ面と丸みが出会う**稜**に載る帯。UV.x に E を焼く（#39）。"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    rows, meta = [], []
    NC = None
    for iz in range(NVZ + 1):
        zn = ZN_LO + (ZN_HI - ZN_LO) * iz / NVZ
        row = vein_row(S, zn)
        if row is None or len(row) < 3:
            rows.append(None); meta.append(None); continue
        z = S["z0"] + zn * (S["z1"] - S["z0"])
        # 行ごとに点数が違うと格子が張れないので、帯を NVC+1 点に取り直す
        vs_, ms_ = [], []
        for ic in range(NVC + 1):
            j = min(len(row) - 1, int(round(ic / NVC * (len(row) - 1))))
            (px, py), _, e = row[j]
            vs_.append(bm.verts.new((px, py, z)))
            ms_.append(e)
        rows.append(vs_); meta.append(ms_)
    look = {}
    for r, m in zip(rows, meta):
        if r:
            for v, mm in zip(r, m):
                look[v] = mm
    for iz in range(NVZ):
        A, B = rows[iz], rows[iz + 1]
        if A is None or B is None:
            continue
        for ic in range(NVC):
            try:
                bm.faces.new([A[ic], A[ic + 1], B[ic + 1], B[ic]])
            except ValueError:
                continue
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if sum(f.normal.x for f in bm.faces) < 0:      # 法線を外向き（局所+x側）へ揃える
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    for f in bm.faces:
        for lp in f.loops:
            e = look.get(lp.vert, 0.0)
            lp[uvl].uv = (max(0.0, min(1.0, e)), 0.5)
    me = bpy.data.meshes.new(S["name"] + "_suji"); bm.to_mesh(me); bm.free()
    me["_smooth"] = True
    return me


# ---------- 配置 ----------
roots, parts, veins = [], [], []
for S in STONES:
    root = bpy.data.objects.new(S["name"] + "_root", None)
    bpy.context.collection.objects.link(root)
    root.location = (S["cx"], S["cy"], 0.0)
    roots.append(root)
    ob = link(stone_mesh(S), S["name"], mat_ishi, root)
    vn = link(vein_mesh(S), S["name"] + "_suji", mat_suji, root)
    parts += [ob, vn]
    veins.append(vn)

# 🔴 黒の肌は実ジオメトリ（#52）。**発光体には掛けない**（MATERIALS.md 掟1）
for ob in parts:
    if ob.name.endswith("_suji"):
        continue
    rec = "fuda"
    r = BLACK_RECIPES[rec]
    tex = bpy.data.textures.new("relief_" + ob.name, 'CLOUDS'); tex.noise_scale = r["dsize"]
    sub = ob.modifiers.new("sub", 'SUBSURF')
    sub.levels = sub.render_levels = 2
    sub.subdivision_type = 'SIMPLE'            # 🔴 #65①：既定のCatmull-Clarkは面を枕に丸める
    d = ob.modifiers.new("disp", 'DISPLACE')
    d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    d = delta_of(i / N_FRAMES)
    for S, root in zip(STONES, roots):
        root.rotation_euler = (0.0, 0.0, S["phi0"] + S["sgn"] * d)
        root.keyframe_insert("rotation_euler", frame=f + 1)

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
        caption("MIDDLE STUDY 059 — WARIFU", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0.52, 0.0, 2.25)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：**被写体に抜けがある作では逆光をカメラから隠す**。
#    この作は「対」＝二つの塊のあいだが素通しで、そこは画面の 0.645m（=367px）ある。
#    4×4・1800W の面光源は被写体面へ換算すると半径1.23＝あいだにそのまま写り込む。
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③/#67⑥：**奥**（画面62〜80%の帯に届く位置）へ
limelamps = []
for sx, sy in ((-0.90, 22.0), (0.45, 30.0), (1.90, 40.0)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, 0.30))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = LIME_W
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
cam.data.dof.focus_object = veins[0]
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
vein_names = {v.name for v in veins}
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name not in vein_names:
        lit_by_lime.objects.link(o)
for lp in limelamps:
    lp.light_linking.receiver_collection = lit_by_lime

# 🔴 破面は**自分の表の面を洗ってしまう**（右の札が緑のグラデを被った＝#24 のペンキ側）。
#    各々の破面から「自分自身」だけを外すと、**二枚は互いの光でしか照らされない**
#    ——あいだを通してしか触れていない、という題材そのものが照明になる。
for i, vn in enumerate(veins):
    c = bpy.data.collections.new("lit_by_" + vn.name)
    bpy.context.scene.collection.children.link(c)
    own = {STONES[i]["name"], vn.name}
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name not in own:
            c.objects.link(o)
    vn.light_linking.receiver_collection = c

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
    allxs, allys = [], []
    boxes = []
    for root, S in zip(roots, STONES):
        xs, ys = [], []
        for o in bpy.data.objects:
            if o.type != 'MESH' or not o.name.startswith(S["name"]):
                continue
            ev = o.evaluated_get(dg)
            for v in ev.data.vertices:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                xs.append(c.x); ys.append(c.y)
        boxes.append((min(xs), max(xs), min(ys), max(ys)))
        allxs += xs; allys += ys
    x0, x1, y0, y1 = min(allxs), max(allxs), min(allys), max(allys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 占有  長辺 %.1f%%（帯 55〜65%%）  重心x %.1f%%" % (max((x1 - x0), (y1 - y0)) * 100,
                                                            (x0 + x1) / 2 * 100))
    gap = boxes[1][0] - boxes[0][1]
    print(">> あいだ %.4f（=%.0fpx@1600 ／ measure の6pxグリッドで %.1fセル・膨張1で潰れない下限=3）"
          % (gap, gap * 1600, gap * 1600 / 6))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_059.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    for vn in veins:
        m_em = bpy.data.materials.new(vn.name + "_glb"); m_em.use_nodes = True
        pe = m_em.node_tree.nodes["Principled BSDF"]
        pe.inputs["Base Color"].default_value = BLACK
        pe.inputs["Emission Color"].default_value = LIME
        pe.inputs["Emission Strength"].default_value = ES_CORE * 0.55
        vn.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts} | {r.name for r in roots}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = veins[0]
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
