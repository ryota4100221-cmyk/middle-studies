# =============================================================
# MIDDLE STUDY 068 — CHASEN（茶筅 / a tea whisk）
#
# 黒い茶筅が一本、画面の左に寄って浮いている。右はぜんぶ余白——そこに茶碗は無い。
#
# 茶筅は、削って作る道具ではない。**割って作る。**
# 一本の竹の先を、十六に割り、それをまた割り、また割る。
# 割ったぶんの半分は外へ、半分は内へ折り返して、外穂と内穂の二重にする。
#
# 光っているのは竹の皮ではない。**内穂**が ライム #A5E02E に灯っている。
# 内穂は、外からはほとんど見えない。外穂の隙間からしか見えない。
# 外穂が締まれば隠れ、ゆるめば現れる。
#
# **そして、根元の一節だけは割らない。**
# 節は竹のいちばん硬いところで、割るのはそこで止める。
# 八十本に割れていても、下半分はまだ一本の竹だ。
# **八十本を一本にしているのは、割らずに残した真ん中——節のほうだ。**
#
# 茶筅は道具のなかでいちばん短命で、穂は使えば折れ、折れたら直せない。
# それでも点前は、湯の中で穂を一本ずつ検めるところから始まる（茶筅通し）。
# **壊れることを前提に作られた真ん中を、使う前に必ず一度、確かめる。**
#
# 🔴 光の型＝**反復**（#53：67作で9作）
# 🔴 構図の型＝**端寄せ**（#57：67作で3作。**67作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／065／066／067 に続く11例目）
#    今日選べたのは 光＝窓／反復／稜線 × 構図＝全身／端寄せ／対。
#    ・いちばん珍しいのは 稜線(6) だが、**いま鳴っているのは halo の △（直近5作が基準期の55%）**で、
#      #51④ の処方は「面で出す・透過させる・内側から出す」＝**線と点は処方の逆**。
#      実測でも 059 WARIFU（稜線）の halo は 9,840＝下限すれすれだった。→ 稜線は今日は取らない。
#    ・窓(7) と 反復(9) のうち、**この題材では窓が原理的に成立しない**——茶筅に孔は無く、
#      孔を作れば別の道具になる。そして #40③「黒い格子＋大きな発光面は必ず行灯になる」は
#      「窓×端寄せ」でいちばん出やすい型（黒い枠＋奥の光る面）。
#    ・→ **反復×端寄せ**。多数の細い光を**個数**で出すので halo を戻す方向に効き、
#      051 ZENI（円盤＋中央の孔）／067 TAKOTSUBO（器と口）とも別の出方になる。
#
# 🔴 機構＝**茶筅通し（穂がゆるむ）**。整数周期・厳密に閉じる。
#    外穂の反り a と巻き c を「締まった姿」→「ゆるんだ姿」へ**形で**補間する（シェイプキー）。
#    #64①：**「開く」を剛体回転で書くと必ず花になる**ので、付け根の角度は動かさず
#    曲率そのものを変える。付け根（s<0.15）は糸で締められているので両姿勢とも平行のまま。
#    **発光の値は1フレームも動かしていない**（#69②／#70④）。変わるのは
#    「外穂が内穂をどれだけ隠しているか」だけ＝#40⑥ は z バッファで幾何積分して測る。
#    首振り ψ=Ψ·sin2πt は「湯の中で回して検める」所作。位置・回転キーとモーフだけで glb に乗る。
#
# 🔴 #34「カメラに正対する細長い発光面は幅方向にも落として芯を残さないとテープになる」
#    ＝内穂の E は**長さ方向 × 幅方向**の積。両端と両縁で厳密に 0（#49① 縁の無い光）。
#
# 🔴 穂は 52＋34＝**86本**＝実物の八十本立と同じ密度。**480×600 では銀の針金にしか見えず**、
#    本数を落として太くしたくなるが、それは #68 の型（テスト解像度で判定してはいけない）。
#    1600×2000 では 52本のほうが「一本の竹を割った縁（ふち）」に見え、36本では**花**に見えた。
#    穂の幅は竹の周を本数で割った値（0.584/52=0.0112）が上限＝根元で隣とほとんど接している。
#
# 造形＝掃引（sweep）だけ。boolean 不使用。object.scale / transform_apply 不使用（#15）。
#    黒の質感は MATERIALS.md の **`urushi`**＝竹の皮は滑らかで艶がある（DISPLACE を掛けない＝
#    厚さ 0.013 の穂に実起伏を入れるとシルエットが崩れる。#52 の掟2）。
#
# 【ドメイン】茶・茶筅。直近10作＝漁労・蛸壺／灯火・和蝋燭／神域・鳥居／鏡・柄鏡／手仕事・和鋏／
#    製紙・紙漉き／古墳・埴輪／炊事・竈／証・割符／空・凧 と別。
#    023 UTSUWA【器・陶／茶道】は**茶碗**＝受ける器で、こちらは**手で動かす道具**。
#    019 AYA【織・布】も細い部材の多数だが、あちらは交差する格子、こちらは一点から出る放射。
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
FRAME_W, FRAME_H = 2.81, 3.52      # y=0 の平面での実効フレーム
LIME_W = 100.0                     # #58③：随伴のライム光源（発光体の外・奥）

# --- 置き場所（#57 端寄せ：枠に接さず・重心xを中央から12%以上ずらす）-------
X0, Y0 = 0.02, 0.0
Z_O    = 2.09                      # 節（穂の付け根）の高さ＝オブジェクト原点
BOB    = 0.030                     # t=0.5（hero）では 0
PSI_A  = 0.62                      # 首振り（湯の中で回して検める）

# --- 竹の寸法（実物比：全長11cm／穂5.5cm／柄5.5cm／外径6cm）-------
R_CULM  = 0.100                    # 柄（竹）の外半径
WALL_T  = 0.0130                   # 竹（柄）の肉厚
T_TINE  = 0.0060                   # 🔴 穂は「平たい削ぎ板」。厚み>幅 の角棒にすると
#                                    どの角度でも稜に環境光が乗って**銀の針金**になる（#67③）
R0_T    = R_CULM - WALL_T * 0.5    # 外穂の中心線が出る半径
R0_IN   = R_CULM - WALL_T * 1.7    # 🔴 内穂は外穂の**内側**から出る（同じ半径だと根元で貫通する）
Z0_T    = 0.035                    # 穂の付け根（節の上）
HAND_L  = 1.060                    # 柄の長さ。実物比 柄6.5cm : 穂4.5cm : 径6cm を守る
#   🔴 5周目まで穂を「長く細い」形にしていて、どう振っても**花**にしかならなかった。
#      茶筅の穂は **半径 ≒ 長さ**（4.5cm の穂が半径 3cm まで開く）＝短くて大きく開く。
#      比を実物から起こしたら（#50「骨格の比だけは実物から起こす」）一発で茶筅に見えた

N_OUT, N_IN = 52, 34
W_OUT, W_IN = 0.0105, 0.0105       # 穂の幅（接線方向）＝厚みの約3倍
L_OUT, L_IN = 1.100, 0.840         # 穂の長さ
BOW_IN      = 0.0035               # 内穂の反り（真横を向いても面が消えない）

# --- 姿勢（a=反り／c=先の巻き）。α(s)=a·sin(π s^1.45) − c·π s^2.2 ------
# 🔴 指数 2.00 は「付け根では開かない」を式に入れるため。糸で締めた所は両姿勢で平行のまま
#    （1.0 未満だと s=0.1 で既に 23° 開き、糸の輪が穂を貫通する）。
#    1.45 では**根元から膨らむ玉ねぎ**になった＝茶筅は「途中から急に開く」壺型
P_A, P_C = 1.70, 16.00
OUT_CLOSED = (0.10, 0.10)          # 締まった姿（乾いた茶筅）
OUT_OPEN   = (0.90, 1.20)          # ゆるんだ姿（湯に浸した茶筅）
#   🔴 c（先の巻き）の**指数**が効く。P_C=2.2 だと穂の上半分がまるごと巻いて
#      **一本ずつが「?」の輪**になり、黒い針金の花輪になった。茶筅の巻きは
#      **先端だけの短い鉤**。P_C=6.0 でもまだ輪が頭の直径の 21% あって「針金の花」だった。
#      P_C=16（s>0.93 で急に巻く）＝輪は直径の 9%＝実物の鉤の比。角度は −216°
IN_CLOSED  = (0.08, 0.05)          # 内穂はほぼ真っ直ぐ
IN_OPEN    = (0.55, 0.90)          # ゆるむと内穂も少し開く（外穂の 1/3 だけ）

# --- 内穂の光（#49① 両端・両縁で厳密に 0 ／ #34 幅方向にも落とす）------
E_LEN_P, E_LEN_Q = 2.40, 1.55      # 長さ方向：sin(π u^P)^Q。ピークは u≒0.75
#   🔴 ピークを 0.57 に置くと光が付け根まで届き、**光ファイバーのスタンドライト**になった。
#      茶筅の中で光っていてよいのは「穂と穂のあいだ」＝上のほうだけ。根元は黒いまま
E_WID_Q          = 0.50            # 幅方向：sin(π v)^Q
ES_CORE = 18.0
WHITE_FROM, WHITE_TO = 0.66, 0.60  # halo はこの「白→ライム」の帯でしか出ない（#70④）
K_MIX   = 7.0                      # E→0 側は黒い竹へ戻す（発光体の縁を作らない＝#49①）

NS_OUT, NS_IN = 30, 26             # 穂の分割数
STILL_FRAME = 61                   # t=0.5 ＝ 穂がいちばんゆるむ唯一の瞬間


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def jit(i, k, amp):
    """個体差。乱数を使わず決定的に散らす（#70⑤ 等間隔にしない）"""
    return amp * math.sin(k * (i + 1) * 1.0 + k * 0.77)


def alpha(s, a, c):
    return a * math.sin(math.pi * s ** P_A) - c * math.pi * s ** P_C


def curve(a, c, L, r0, z0, ns):
    """子午面の曲線。tangent の角 α を積分して (r, z, α) を ns+1 点返す"""
    sub = 6
    M = ns * sub
    ds = 1.0 / M
    r, z = r0, z0
    pts = [(r0, z0, alpha(0.0, a, c))]
    for k in range(M):
        s = (k + 0.5) * ds
        al = alpha(s, a, c)
        r += L * math.sin(al) * ds
        z += L * math.cos(al) * ds
        if (k + 1) % sub == 0:
            pts.append((r, z, alpha((k + 1) * ds, a, c)))
    return pts


def tines(kind, pose):
    """kind: 'out' / 'in'、pose: 0=締まり 1=ゆるみ。各穂の (phi, pts) を返す"""
    if kind == "out":
        n, L, ns = N_OUT, L_OUT, NS_OUT
        a0, c0 = OUT_CLOSED
        a1, c1 = OUT_OPEN
    else:
        n, L, ns = N_IN, L_IN, NS_IN
        a0, c0 = IN_CLOSED
        a1, c1 = IN_OPEN
    a, c = (a0, c0) if pose == 0 else (a1, c1)
    out = []
    for i in range(n):
        dphi = 2.0 * math.pi / n
        phi = dphi * i + jit(i, 5.3, 0.18 * dphi)
        Li = L * (1.0 + jit(i, 3.1, 0.055))
        # 🔴 内穂は個体差を小さくする。a を 0.06 振ると先が軸を割り、
        #    30本が中心で交差する（プローブの「内穂の最小半径」が検知器）
        # 🔴 巻き c の個体差を大きく取る。揃った鉤は**機械で曲げた針金の輪**に見える。
        #    茶筅は手で癖付けするので、隣どうしで巻きの深さが違う
        ai = a + jit(i, 1.7, (0.10 if kind == "out" else 0.05) * (1.0 + abs(a)))
        ci = c + jit(i, 2.3, 0.150 if kind == "out" else 0.060)
        r0 = R0_T if kind == "out" else R0_IN
        out.append((phi, curve(ai, ci, Li, r0, Z0_T, ns)))
    return out


OUT_P = [tines("out", 0), tines("out", 1)]
IN_P = [tines("in", 0), tines("in", 1)]


def e_len(u):
    return max(0.0, math.sin(math.pi * min(1.0, max(0.0, u)) ** E_LEN_P)) ** E_LEN_Q


def e_wid(v):
    return max(0.0, math.sin(math.pi * min(1.0, max(0.0, v)))) ** E_WID_Q


def frame_at(phi, r, z, al):
    """穂の局所フレーム。P=位置／N=面法線（子午面内）／B=幅方向（接線）"""
    cp, sp = math.cos(phi), math.sin(phi)
    P = (r * cp, r * sp, z)
    N = (math.cos(al) * cp, math.cos(al) * sp, -math.sin(al))
    B = (-sp, cp, 0.0)
    return P, N, B


def lerp3(A, B, u):
    return tuple(A[i] + (B[i] - A[i]) * u for i in range(3))


def pose_u(t):
    return 0.5 * (1.0 - math.cos(2.0 * math.pi * t))


def psi_of(t):
    return PSI_A * math.sin(2.0 * math.pi * t)


def world(p, t):
    """局所→ワールド（首振り ψ と上下 bob）"""
    ps = psi_of(t)
    c, s = math.cos(ps), math.sin(ps)
    return (X0 + c * p[0] - s * p[1], Y0 + s * p[0] + c * p[1],
            Z_O + p[2] + BOB * math.sin(2.0 * math.pi * t))


def out_pts(i, t):
    """外穂 i の中心線（ワールド）。シェイプキーと同じ**位置の線形補間**で作る"""
    u = pose_u(t)
    ph0, A = OUT_P[0][i]
    ph1, B = OUT_P[1][i]
    res = []
    for k in range(len(A)):
        r = A[k][0] + (B[k][0] - A[k][0]) * u
        z = A[k][1] + (B[k][1] - A[k][1]) * u
        al = A[k][2] + (B[k][2] - A[k][2]) * u
        P, N, Bv = frame_at(ph0, r, z, al)
        res.append((world(P, t), N, Bv))
    return res


def in_pts(i, t):
    u = pose_u(t)
    ph0, A = IN_P[0][i]
    ph1, B = IN_P[1][i]
    res = []
    for k in range(len(A)):
        r = A[k][0] + (B[k][0] - A[k][0]) * u
        z = A[k][1] + (B[k][1] - A[k][1]) * u
        al = A[k][2] + (B[k][2] - A[k][2]) * u
        P, N, Bv = frame_at(ph0, r, z, al)
        res.append((world(P, t), N, Bv))
    return res


# --- #40⑥ を幾何で積分する（z バッファ）--------------------------
# 発光の値は一切入っていない。変わるのは「外穂が内穂をどれだけ隠しているか」だけ。
GW, GH = 300, 376
CELL_X, CELL_Y = FRAME_W / GW, FRAME_H / GH
SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2


def proj(P):
    """カメラ距離 8.3 の線形近似（シリーズのプローブと同じ）。戻り値 (gx, gy, depth)"""
    m = 8.3 / (8.3 + P[1])
    sx = AIM_X + (P[0] - AIM_X) * m
    sz = LOOK_Z + (P[2] - LOOK_Z) * m
    return ((sx - SX0) / CELL_X, (sz - SZ0) / CELL_Y, P[1])


def zbuf_of(t):
    """外穂＋柄をラスタライズして最近点の depth を持つ格子を返す"""
    zb = [1e9] * (GW * GH)

    def quad(p0, p1, p2, p3):
        xs = [p[0] for p in (p0, p1, p2, p3)]
        ys = [p[1] for p in (p0, p1, p2, p3)]
        d = min(p[2] for p in (p0, p1, p2, p3))
        gx0, gx1 = max(0, int(min(xs))), min(GW - 1, int(max(xs)) + 1)
        gy0, gy1 = max(0, int(min(ys))), min(GH - 1, int(max(ys)) + 1)
        if gx1 < gx0 or gy1 < gy0:
            return
        for gy in range(gy0, gy1 + 1):
            base = gy * GW
            for gx in range(gx0, gx1 + 1):
                if zb[base + gx] > d:
                    zb[base + gx] = d

    for i in range(N_OUT):
        pts = out_pts(i, t)
        for k in range(len(pts) - 1):
            (P0, N0, B0), (P1, N1, B1) = pts[k], pts[k + 1]
            c0 = [proj(tuple(P0[j] + B0[j] * sgn * W_OUT * 0.5 for j in range(3)))
                  for sgn in (-1, 1)]
            c1 = [proj(tuple(P1[j] + B1[j] * sgn * W_OUT * 0.5 for j in range(3)))
                  for sgn in (-1, 1)]
            quad(c0[0], c0[1], c1[1], c1[0])
    # 柄（節から下）は内穂を隠さないが、bbox の計算に要るので別扱い
    return zb


_INS = []      # 内穂のサンプル（i, k, v, weight）
for _k in range(NS_IN):
    _u = (_k + 0.5) / NS_IN
    for _j in range(5):
        _v = (_j + 0.5) / 5.0
        _INS.append((_k, _v, e_len(_u) * e_wid(_v)))


def light_visible(t):
    zb = zbuf_of(t)
    tot = 0.0
    for i in range(N_IN):
        pts = in_pts(i, t)
        for k, v, w in _INS:
            if w <= 0.0:
                continue
            P, N, B = pts[k]
            Q = tuple(P[j] + B[j] * (v - 0.5) * W_IN for j in range(3))
            gx, gy, d = proj(Q)
            gi, gj = int(gx), int(gy)
            if gi < 0 or gj < 0 or gi >= GW or gj >= GH:
                continue
            if zb[gj * GW + gi] < d - 0.006:
                continue
            tot += w
    return tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]

if "--probe-only" in sys.argv:
    print("── 068 CHASEN 幾何プローブ")
    for nm, P in (("締まり", 0), ("ゆるみ", 1)):
        o = OUT_P[P][0][1]
        n = IN_P[P][0][1]
        rmax = max(p[0] for p in o)
        print("   外穂 %s  r 付根%.3f → 最大%.3f → 先%.3f   z 先%.3f   （径 %.3f）"
              % (nm, o[0][0], rmax, o[-1][0], o[-1][1], 2 * rmax))
        print("   内穂 %s  r 付根%.3f → 最大%.3f → 先%.3f   z 先%.3f"
              % (nm, n[0][0], max(p[0] for p in n), n[-1][0], n[-1][1]))
    rmin = min(min(p[0] for p in c) for P in (0, 1) for _, c in IN_P[P])
    print("   🔴 内穂の最小半径 %.4f（軸を割ると反対側の穂と交差する。0.020 以上）" % rmin)

    VS = [light_visible(t) for t in _TS]
    VMAX = max(VS)
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(VS) / VMAX))
    b = max(range(N_FRAMES), key=lambda i: VS[i])
    print("   いちばん明るい frame %d（t=%.3f）  STILL_FRAME=%d" % (b + 1, _TS[b], STILL_FRAME))
    print("   光の曲線 " + " ".join("%.0f" % (100 * VS[i] / VMAX) for i in range(0, N_FRAMES, 6)))
    on = sum(1 for v in VS if v > 0.25 * VMAX) / N_FRAMES * 100
    print("   光が25%%以上ある時間の割合 %.0f%%" % on)
    tot = sum(w for _, _, w in _INS) * N_IN
    print("   🔴 **絶対量** hero で見えている発光 = 全発光の %.1f%%（#77②：#40⑥ は比なので"
          "光が 0 に潰れても合格に見える）" % (100 * VMAX / tot))

    # --- 画面占有（hero t=0.5）
    t = 0.5
    xs, ys = [], []
    for i in range(N_OUT):
        for P, N, B in out_pts(i, t):
            g = proj(P); xs.append(g[0]); ys.append(g[1])
    for zz in (Z_O - HAND_L, Z_O + 0.0):
        for sgn in (-1, 1):
            g = proj((X0 + sgn * R_CULM, Y0, zz)); xs.append(g[0]); ys.append(g[1])
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print("\n   ── 画面占有（t=0.5）")
    print("   bbox x %.1f..%.1f%%  y(下から) %.1f..%.1f%%  → 長辺 %.1f%%（帯 44〜66・目標55〜65）"
          % (x0 / GW * 100, x1 / GW * 100, y0 / GH * 100, y1 / GH * 100,
             max((x1 - x0) / GW, (y1 - y0) / GH) * 100))
    print("   重心x ≒ %.1f%%（端寄せ＝中央から12%%以上。50±12 の外へ）"
          % ((x0 + x1) / 2 / GW * 100))
    print("   重心y（上から）≒ %.1f%%   枠まで 左%.1f%% 右%.1f%% 上%.1f%% 下%.1f%%"
          % (100 - (y0 + y1) / 2 / GH * 100, x0 / GW * 100, 100 - x1 / GW * 100,
             100 - y1 / GH * 100, y0 / GH * 100))
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    print("   被写体の下端 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (SZ0 + y0 * CELL_Y, capz, SZ0 + y0 * CELL_Y - capz))

    # ライム面積の見積り（見えている内穂の面積を画面へ投影）
    la = 0.0
    zb = zbuf_of(0.5)
    for i in range(N_IN):
        pts = in_pts(i, 0.5)
        for k in range(NS_IN):
            P, N, B = pts[k]
            seg = math.dist(pts[k][0], pts[min(k + 1, len(pts) - 1)][0])
            g = proj(P)
            gi, gj = int(g[0]), int(g[1])
            if 0 <= gi < GW and 0 <= gj < GH and zb[gj * GW + gi] >= g[2] - 0.006:
                la += seg * W_IN * 1.6            # 両面＋反りぶん
    print("   見えている内穂の面積 ≒ %.4f ／ 画面 %.2f → ライム面積 ≒ %.2f%%（帯 0.8〜12）"
          % (la, FRAME_W * FRAME_H * 0.8, la / (FRAME_W * FRAME_H * 0.8) * 100))
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
# 竹の皮＝**漆（urushi）**。滑らかで艶がある＝「肌が無いのが肌」。
# 🔴 DISPLACE は掛けない（#52 掟2）。厚さ 0.013 の穂に実起伏を入れるとシルエットが崩れる
# 🔴 竹の皮は艶があるので `urushi` から始めたが、**穂が銀の針金になった**（#67③：
#    すれすれの黒は鏡面でも粗さでも白を映す）。厚さ 0.006 の部材では鏡面を上げてはいけない。
BLACK_RECIPES = {"base": dict(rough=0.36, spec=0.15, coat=0.05, coat_rough=0.10)}
RECIPE = "base"


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p):
    r = BLACK_RECIPES[RECIPE]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Coat Weight"].default_value = r["coat"]
    p.inputs["Coat Roughness"].default_value = r["coat_rough"]


mat_body, bp_ = principled("take")
apply_black(bp_)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は**竹の黒そのもの**へ戻す（発光板の縁を作らない・#49①）。
       芯だけ白へ抜く＝halo はこの「白→ライム」の帯でしか出ない（#70④）"""
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


mat_glow = glow_material("uchiho")


# ---------- 造形（bmesh・実寸。局所座標で作り、object に位置と回転を与える）----
def local(phi, r, z, al, dn, dv, w):
    """穂の断面上の1点。dn=法線方向オフセット、dv=幅方向(−0.5..0.5)"""
    cp, sp = math.cos(phi), math.sin(phi)
    ca, sa = math.cos(al), math.sin(al)
    return (r * cp + ca * cp * dn - sp * dv * w,
            r * sp + ca * sp * dn + cp * dv * w,
            z - sa * dn)


def outer_mesh(pose):
    """外穂 N_OUT 本。断面は 10 点の閉じた環（外側5点＋内側5点）＝厚みのある竹の板"""
    bm = bmesh.new()
    for phi, pts in OUT_P[pose]:
        rings = []
        for (r, z, al) in pts:
            ring = []
            for sgn in (0.5, -0.5):                     # 外面 → 内面
                vs = range(5) if sgn > 0 else range(4, -1, -1)
                for j in vs:
                    v = j / 4.0 - 0.5
                    ring.append(bm.verts.new(local(phi, r, z, al,
                                                   sgn * T_TINE, v, W_OUT)))
            rings.append(ring)
        M = len(rings[0])
        for k in range(len(rings) - 1):
            for j in range(M):
                j2 = (j + 1) % M
                bm.faces.new((rings[k][j], rings[k][j2],
                              rings[k + 1][j2], rings[k + 1][j]))
        for ring, flip in ((rings[0], True), (rings[-1], False)):
            f = bm.faces.new(ring[::-1] if flip else ring)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("soto_%d" % pose); bm.to_mesh(me); bm.free()
    return me


def inner_mesh(pose):
    """内穂 N_IN 本。厚みの無い反った帯（＝竹の壁の一片）。E を UV 'grad' の U に焼く"""
    bm = bmesh.new()
    for phi, pts in IN_P[pose]:
        rings = []
        for (r, z, al) in pts:
            ring = []
            for j in range(5):
                v = j / 4.0
                dn = BOW_IN * (1.0 - (2.0 * v - 1.0) ** 2)
                ring.append(bm.verts.new(local(phi, r, z, al, dn, v - 0.5, W_IN)))
            rings.append(ring)
        for k in range(len(rings) - 1):
            for j in range(4):
                bm.faces.new((rings[k][j], rings[k][j + 1],
                              rings[k + 1][j + 1], rings[k + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bm.loops.layers.uv.new("grad")
    # UV は面の並び順ではなく **頂点 index** から引き直す（#39 の規律）。
    # ここでは仮に 0 を入れ、リンク後に mesh 側で焼く
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = (0.0, 0.5)
    me = bpy.data.meshes.new("uchi_%d" % pose); bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=1.15):
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
    ob.select_set(False)
    return ob


# --- 外穂（シェイプキーで「締まり→ゆるみ」を形として持つ・#64①）---
me_out = outer_mesh(0)
ob_out = link(me_out, "sotoho", mat_body)
co_open = []
bm = bmesh.new(); bm.from_mesh(outer_mesh(1)); bm.verts.ensure_lookup_table()
co_open = [v.co.copy() for v in bm.verts]; bm.free()
ob_out.shape_key_add(name="Basis", from_mix=False)
kb_out = ob_out.shape_key_add(name="yurumu", from_mix=False)
for i, co in enumerate(co_open):
    kb_out.data[i].co = co

# --- 内穂（発光）。UV の U に E＝長さ×幅 を焼く ---
me_in = inner_mesh(0)
ob_in = link(me_in, "uchiho", mat_glow, smooth=1.2)
bm = bmesh.new(); bm.from_mesh(inner_mesh(1)); bm.verts.ensure_lookup_table()
co_in_open = [v.co.copy() for v in bm.verts]; bm.free()
ob_in.shape_key_add(name="Basis", from_mix=False)
kb_in = ob_in.shape_key_add(name="yurumu", from_mix=False)
for i, co in enumerate(co_in_open):
    kb_in.data[i].co = co

# 🔴 UV は「頂点が何番目の断面・何列目か」から引く。頂点は
#    穂 → 断面 → 幅(5) の順に作ってあるので index から一意に戻せる（#39）
NS_IN_PTS = len(IN_P[0][0][1])
uvl = me_in.uv_layers["grad"]
for poly in me_in.polygons:
    for li in poly.loop_indices:
        vi = me_in.loops[li].vertex_index
        r = vi % (NS_IN_PTS * 5)
        k = r // 5
        j = r % 5
        u = (k + 0.0) / (NS_IN_PTS - 1)
        v = j / 4.0
        uvl.data[li].uv = (e_len(u) * e_wid(v), 0.5)


# --- 柄（節・中空の口）------------------------------------------
def handle_mesh():
    """柄＝節から下の、まだ割っていない一本の竹。上端は中空（＝暗いトンネル・#71④）"""
    PROF = [(-HAND_L + 0.004, 0.052), (-HAND_L + 0.016, 0.080), (-HAND_L + 0.034, 0.092),
            (-0.72, 0.096), (-0.665, 0.101), (-0.640, 0.112), (-0.615, 0.101),
            (-0.560, 0.097),                    # 🔴 柄の途中にもう一節。無いと**黒い懐中電灯**
            (-0.30, 0.099), (-0.080, 0.100), (-0.036, 0.105),
            (0.000, 0.117), (0.026, 0.106), (Z0_T, R_CULM),
            (Z0_T, R_CULM - WALL_T), (Z0_T - 0.20, R_CULM - WALL_T),
            (Z0_T - 0.235, 0.055)]
    NPHI = 72
    bm = bmesh.new()
    rings = []
    for k in range(NPHI):
        ph = 2.0 * math.pi * k / NPHI
        c, s_ = math.cos(ph), math.sin(ph)
        rings.append([bm.verts.new((r * c, r * s_, z)) for z, r in PROF])
    for k in range(NPHI):
        k2 = (k + 1) % NPHI
        for j in range(len(PROF) - 1):
            if abs(PROF[j][0] - PROF[j + 1][0]) < 1e-9 and abs(PROF[j][1] - PROF[j + 1][1]) < 1e-9:
                continue
            bm.faces.new((rings[k][j], rings[k][j + 1], rings[k2][j + 1], rings[k2][j]))
    bot = bm.verts.new((0.0, 0.0, -HAND_L - 0.004))
    top = bm.verts.new((0.0, 0.0, Z0_T - 0.250))
    for k in range(NPHI):
        k2 = (k + 1) % NPHI
        bm.faces.new((bot, rings[k2][0], rings[k][0]))
        bm.faces.new((top, rings[k][-1], rings[k2][-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("e"); bm.to_mesh(me); bm.free()
    return me


ob_handle = link(handle_mesh(), "handle", mat_body)


def thread_mesh():
    """糸＝穂を締めている輪。節と糸だけが、割れた竹を一本にしている"""
    NA, NB, R, TR = 96, 12, 0.1055, 0.0068
    bm = bmesh.new()
    rings = []
    for a in range(NA):
        pa = 2.0 * math.pi * a / NA
        ca, sa = math.cos(pa), math.sin(pa)
        rings.append([bm.verts.new(((R + TR * math.cos(2.0 * math.pi * b / NB)) * ca,
                                    (R + TR * math.cos(2.0 * math.pi * b / NB)) * sa,
                                    0.125 + TR * math.sin(2.0 * math.pi * b / NB)))
                      for b in range(NB)])
    for a in range(NA):
        a2 = (a + 1) % NA
        for b in range(NB):
            b2 = (b + 1) % NB
            bm.faces.new((rings[a][b], rings[a][b2], rings[a2][b2], rings[a2][b]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("ito"); bm.to_mesh(me); bm.free()
    return me


ob_thread = link(thread_mesh(), "ito", mat_body)

parts = [ob_handle, ob_thread, ob_out, ob_in]

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    loc = (X0, Y0, Z_O + BOB * math.sin(2.0 * math.pi * t))
    rot = (0.0, 0.0, psi_of(t))
    for ob in parts:
        ob.location = loc
        ob.rotation_euler = rot
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)
    u = pose_u(t)
    for kb in (kb_out, kb_in):
        kb.value = u
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
        caption("MIDDLE STUDY 068 — CHASEN", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, LOOK_Z + 0.30)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：穂は抜けだらけ＝面光源が穂のあいだから素通しで写る

# 🔴 #58③：随伴のライム光源は**発光体の外**。#64③/#67⑥：**奥**（画面62〜80%の帯に届く位置）へ
for sx, sy, sz, w in ((-0.90, 12.0, 0.30, LIME_W), (0.35, 24.0, 0.30, LIME_W),
                      (1.65, 38.0, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
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
    gx0 = gy0 = 9.0; gx1 = gy1 = -9.0
    for ob in parts:
        ev = ob.evaluated_get(dg)
        xs, ys = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
        print(">> %-8s x %.3f..%.3f  y %.3f..%.3f" % (ob.name, min(xs), max(xs),
                                                      min(ys), max(ys)))
        gx0 = min(gx0, min(xs)); gx1 = max(gx1, max(xs))
        gy0 = min(gy0, min(ys)); gy1 = max(gy1, max(ys))
    print(">> bbox x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)  長辺 %.1f%%（帯 44〜66）"
          % (gx0, gx1, (gx1 - gx0) * 100, gy0, gy1, (gy1 - gy0) * 100,
             max(gx1 - gx0, gy1 - gy0) * 100))
    print(">> 重心x ≒ %.1f%%（端寄せ＝50±12 の外）  枠まで 左%.3f 右%.3f 上%.3f 下%.3f"
          % ((gx0 + gx1) / 2 * 100, gx0, 1 - gx1, 1 - gy1, gy0))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_068.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("uchiho_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    ob_in.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = parts[0]
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
