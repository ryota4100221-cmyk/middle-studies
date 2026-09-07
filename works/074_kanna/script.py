# =============================================================
# MIDDLE STUDY 074 — KANNA（鉋 / 刃と木のあいだ where the shaving is born）
#
# 鉋がしていることは、けずることではない。**持ち上げることだ。**
# 刃はほとんど寝ていて（下端から40°）、木の面をこすらない。
# 働いているのはただ一本の線——**刃先が木に触れている、そこだけ**。
# 線には厚みが無い。髪一本ぶんも無い。
# それでも、削り屑が生まれてくるのはそこしかない。
#
# 黒い板が一枚、横切っている。黒い刃が一枚、その上に寝ている。
# 板も刃も枠に収まっていない。見えているのは**ふたつが出会う線**だけだ。
# その線から ライム #A5E02E の屑が立ち上がり、
# 裏金の刃先にぶつかって、巻く。**屑が巻くのは木の性質ではない。当てたからだ。**
#
# 削りが深ければ屑は厚く、ゆるく巻いて、光は面になる。
# 浅ければ屑は薄く、きつく巻いて、光は芯になる。
# **かたちを決めているのは、刃でも木でもない。刃と木のあいだの寸法だけだ。**
#
# 🔴 光の型＝**隙間**（#53：73作で19作。シリーズ最多）
# 🔴 構図の型＝**寄り**（#57：73作で5作。**73作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／
#    #76⑤／#78／#79／#80／#81／#82⑤／#83⑤ に続く17例目）。今日選べたのは
#    光＝隙間／反復／背光 × 構図＝全身／寄り／端寄せ。9通りを works.json で数えたら：
#      隙間×全身 18 ／ 隙間×寄り **0** ／ 隙間×端寄せ 1
#      反復×全身  7 ／ 反復×寄り  1 ／ 反復×端寄せ 1
#      背光×全身  3 ／ 背光×寄り  0 ／ 背光×端寄せ 0
#    ・**背光は #67⑤（寄り）／#69①（対）／#71①（群）／#74②（端寄せ）で4方向とも潰れている**＝
#      実質「全身」専用。今日の3つの構図のうち組めるのは全身だけ＝既定に戻る。→ 落とす。
#    ・反復×寄り は 062 SUKETA、反復×端寄せ は 068 CHASEN。どちらも直近12作の中。→ 落とす。
#    → **隙間×寄り**。73作で一度も無い。**隙間はシリーズ最多（19）なのに、
#      一度も「寄って切った」ことがない**＝19作すべてが「黒い塊を丸ごと置いて、そこに細い線」だった。
#      隙間を主役にする最短の手は、光を強くすることではなく **隙間まで寄ること**。
#    ・寄りの機械条件は `edge>=1 かつ 長辺>=78%`。板を左右の枠から出すので edge>=2・長辺100%。
#      **#51③の「長辺55〜65%」は全身の型のときの話**（正典に明記あり）。
#
# 🔴🔴🔴 **11周を「鉋という道具そのもの」に使って捨てた。** → PITFALLS #84①
#    台（だい）に寄ると、何をしても**箱**になる。台鉋の刃道は「直方体の天面に開いた細長い口」で、
#    寄って撮ると幾何がティッシュ箱／複写機と同一になる（#80① の最悪形）。
#    台を厚くしても薄くしても、口を広げても狭めても、屑を太くしても細くしても抜けられなかった。
#    **直したのは造形ではなく「どの隙間を撮るか」だった**——鉋の隙間は刃道ではない。
#    **刃先が木に触れている線**だ。台を画面から外した瞬間に箱が消え、黒がふたつ（板・刃）になった。
#
# 🔴 機構＝**削り深さがかたちを決める**。ひとつの量から4つが同時に出る：
#    削り深さ u(t) = U0 + UA·0.5(1−cos2πt)（整数周期・位置キーだけ＝そのまま glb に乗る／#60）
#      ① 屑の厚み  ＝ u そのもの（削った層がそのまま屑になる。物理の同一物）
#      ② 巻きの径  Rc = RC0 + RC_K·u （厚い屑はゆるく、薄い屑はきつく巻く）
#      ③ 刃の高さ  刃先は z=−u に沈む（深く削るほど刃は木に食い込む）
#      ④ 見える光  巻きがきついほど**渦が自分で自分を隠す**＝#40⑥ はここで振れる（#78⑦）
#    🔴 #80⑥：u は cos（端で静止する）ので、板の首振りと漂いは **sin** ＝位相が π/2 ずれる。
#
# 🔴 屑は**円錐らせん**（conical helix）。幅方向 v で巻きの径を 1+CONE·v に振ってある。
#    径を一定にすると、幅(1.8) ≫ 径(0.09〜0.23) なので**必ず一様な円筒**になり、
#    「緑のチューブ」「ランプシェード」に読まれた（#84②）。片側を 55% ゆるめて初めて渦になった。
#
# 造形＝凸多面体2つ（板・刃）＋薄板1つ（裏金）＋厚みの無い曲面1つ（屑）。
#    boolean 不使用・object.scale 不使用（#15）。
#    🔴 **板は刃より広く、刃は枠より狭い。** 板は左右の枠から出て「地」になり（隙間の下側の黒）、
#    刃は両端が画面に入って「刃物」に読める（#80①の逆用＝端を見せるべき部材もある）。
#    屑は刃よりさらに狭いので、**渦の口が両端に見える**＝円筒でなく巻き物になる。
#
# 黒の質感は MATERIALS.md から2種。掟4の例外（「実物がそうである場合＝鉄の輪＋布の胴」）に当たる：
#    板＝**`touki`**（陶）／刃と裏金＝**`tetsu`**（鍛えた鋼）。
#    🔴 板は木だが `base` を当てると**平面が環境（0.92のグレー）を映して明るい灰色になる**（#47）。
#    MATERIALS.md に木のレシピは無い。粗さ 0.58 の `touki` が、映り込みを消しつつ
#    #52 の実起伏（SUBSURF＋DISPLACE）を載せられる唯一の選択だった。→ PITFALLS #84③
#
# 【ドメイン】木工・鉋（大工道具）。直近10作＝香道／儀礼・水引／弓術・的／茶室・躙口／医薬・薬研／
#    茶・茶筅／漁労・蛸壺／灯火・和蝋燭／神域・鳥居／鏡・柄鏡 と別。
#    020 TSUGITE【木工・継手】は「離すと実体（ほぞ）が現れる」＝正負の反転で、
#    こちらは**接している線から物が生まれる**＝機構が別。
#    002 OBI（メビウスの帯）とは、帯が閉じた輪でなく**片端が黒へ消える渦**である点で別
#    （#49①：E→0 側は黒へ戻す＝発光板の縁を作らない）。
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
LIME_W = 90.0                      # 随伴のライム光源（#58／#80⑤：シリーズ定数ではない）

# --- 局所座標：x＝削り進む向き（+x が刃の後ろ）／y＝刃線／z＝板の上 ---
ALPHA = math.radians(40.0)         # 刃の仕込み勾配（台鉋の標準）
# 板（いた）
ITA_X0, ITA_X1 = -0.55, 1.25       # 手前（カメラ側）／奥
ITA_Y = 3.60                       # 半幅。左右の枠から出る
ITA_T = 0.44                       # 板の厚み
# 刃（は）
HA_L = 2.90                        # 刃道方向の長さ（上は枠の外）
HA_T = 0.130                       # 刃の厚み
HA_BEV = 0.520                     # 刃先の勾配が立ち上がる長さ
HA_Y = 0.95                        # 半幅。🔴 枠より狭い＝両端が画面に入る
# 裏金（うらがね）
URA_A0, URA_A1, URA_T, URA_Y = 0.42, 2.60, 0.075, 0.86

# --- 動き（削り深さ）---------------------------------------------
U0, UA = 0.008, 0.112              # u(t) ∈ [0.008, 0.120] ＝屑の厚みそのもの
                                   # 🔴 [0.012,0.085] では motion.py の光の振れが 1.18＝基準1.22 割れ。
                                   # 振れは発光ではなく**巻きの径の幅**から出るので、削り深さを広げて直す
RC0, RC_K = 0.075, 1.80            # 巻きの径 ＝ RC0 + RC_K·u
LF = 0.95                          # 屑の自由長（一定。伸びるのではなく巻きが変わる）
BSPIR = 0.45                       # 渦の広がり（1周で重ならないだけ与える）
CONE = 0.55                        # 🔴 幅方向の径の振れ。0 にすると必ず円筒になる（#84②）
WK = 1.80                          # 屑の幅（刃 1.90 よりわずかに狭い）
N_IN, N_OUT, N_V = 10, 104, 16     # 刃の上／自由ぶん／幅方向の分割
YAW_A, BOB_A = math.radians(4.5), 0.030    # 🔴 #80⑥ 首振りと漂いは sin（u は cos）

# --- 光（#81④：halo は白へ抜ける広い勾配でしか出ない）-------------
E_TOP = 1.10                       # 芯（＝刃と木が触れている線）の値
GLOW_S = 1.05                      # 線からの減衰長。ここが halo の勾配の幅そのもの
E_FLOOR = 0.010
ES_CORE = 1.7
WHITE_FROM, WHITE_TO = 0.44, 0.62
K_MIX = 16.0                       # #76①：不透明さを発光の強さから切り離す

# --- 置き方 ------------------------------------------------------
PIVOT = (0.42, 0.50, 2.05)         # 刃先の線（局所原点）の世界座標
ROT = (math.radians(9.04), math.radians(-26.76), math.radians(54.14))   # XYZ euler

STILL_FRAME = 61                   # t=0.5 ＝いちばん深く削っている（屑が厚く、巻きがゆるい）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
SA, CA = math.sin(ALPHA), math.cos(ALPHA)
D_BED = (CA, 0.0, SA)              # 刃の面を上る単位ベクトル
M_BED = (SA, 0.0, -CA)             # 刃の身の側
F_BED = (-SA, 0.0, CA)             # 屑の側（刃の表へ）


def tau(t):
    return 2.0 * math.pi * t


def u_of(t):
    """削り深さ＝屑の厚み。cos＝端で静止する（対になる sin をあとで足す）"""
    return U0 + UA * 0.5 * (1.0 - math.cos(tau(t)))


def rc_of(t):
    return RC0 + RC_K * u_of(t)


def yaw_of(t):
    return YAW_A * math.sin(tau(t))


def bob_of(t):
    return BOB_A * math.sin(tau(t))


def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm3(a):
    n = math.sqrt(dot3(a, a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def cross3(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def rot_xyz(v, rx, ry, rz):
    """Blender の XYZ euler と同じ順（R = Rz·Ry·Rx）"""
    x, y, z = v
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return (x, y, z)


def to_world(p, t):
    v = rot_xyz(p, ROT[0], ROT[1], ROT[2] + yaw_of(t))
    return (PIVOT[0] + v[0], PIVOT[1] + v[1], PIVOT[2] + bob_of(t) + v[2])


def to_local_dir(d, t):
    d = rot_xyz(d, 0, 0, -(ROT[2] + yaw_of(t)))
    d = rot_xyz(d, 0, -ROT[1], 0)
    return rot_xyz(d, -ROT[0], 0, 0)


def blade_thick(a):
    """刃先で 0、HA_BEV で HA_T。屑は刃先そのものから生まれる"""
    return HA_T * min(1.0, max(0.0, a) / HA_BEV)


def kuzu_curve(t, v):
    """屑の芯線（幅位置 v ∈ [−1,1]）。刃の表を URA_A0 まで上り、
       裏金の刃先にぶつかって前（−x）へ巻く。弧長は v によらず一定＝UV が不変（#43-e）"""
    u = u_of(t)
    rc = rc_of(t) * (1.0 + CONE * v)
    off = 0.5 * u + 0.004
    pts = []
    for i in range(N_IN + 1):
        a = URA_A0 * i / N_IN
        pts.append((a * D_BED[0] + off * F_BED[0] - u,
                    0.0,
                    a * D_BED[2] + off * F_BED[2]))
    p = list(pts[-1])
    phi = 0.0
    ds = LF / N_OUT
    for i in range(1, N_OUT + 1):
        r = rc * (1.0 + BSPIR * phi)
        phi += ds / r
        c, s_ = math.cos(-phi), math.sin(-phi)
        dx = D_BED[0] * c + D_BED[2] * s_
        dz = -D_BED[0] * s_ + D_BED[2] * c
        p[0] += dx * ds
        p[2] += dz * ds
        pts.append(tuple(p))
    return pts


S_OF = [URA_A0 * i / N_IN for i in range(N_IN + 1)] + \
       [URA_A0 + LF * i / N_OUT for i in range(1, N_OUT + 1)]


def e_of(s):
    """🔴 芯は**刃と木が触れている線**（s=0）。そこから屑に沿って白→ライム→黒へ落ちる。
       #49①：E→0 側を黒へ戻すので発光板の縁ができない。
       #81④：halo はこの「白へ抜ける広い勾配」でしか出ない"""
    return max(E_FLOOR, min(1.55, E_TOP * math.exp(-(s / GLOW_S) ** 2)))


def kuzu_verts(t):
    """幅方向 v ごとに別の径で巻く＝円錐らせん。厚みの無い曲面（屑は薄い）"""
    grid = []
    for j in range(N_V + 1):
        v = 2.0 * j / N_V - 1.0
        y = v * WK / 2
        grid.append([(p[0], y, p[2]) for p in kuzu_curve(t, v)])
    vs = []
    for i in range(len(S_OF)):
        for j in range(N_V + 1):
            vs.append(grid[j][i])
    return vs


def kuzu_uvs():
    return [(e_of(s), 0.5) for s in S_OF for _ in range(N_V + 1)]


# --- 凸多面体（板・刃・裏金）。probe の遮蔽と Blender の造形が同じ定義を使う ---
def half(nx, ny, nz, d):
    """内側は n·p <= d"""
    return (nx, ny, nz, d)


def solids(t):
    u = u_of(t)
    ita = [half(0, 0, 1, 0.0), half(0, 0, -1, ITA_T),
           half(1, 0, 0, ITA_X1), half(-1, 0, 0, -ITA_X0),
           half(0, 1, 0, ITA_Y), half(0, -1, 0, ITA_Y)]
    o = (-u, 0.0, -u)                # 刃は削り深さだけ沈む
    d0 = dot3(F_BED, o)
    ha = [half(*F_BED, d0), half(*M_BED, -d0 + HA_T),
          half(*D_BED, dot3(D_BED, o) + HA_L),
          half(-D_BED[0], -D_BED[1], -D_BED[2], -dot3(D_BED, o)),
          half(0, 1, 0, HA_Y), half(0, -1, 0, HA_Y)]
    ura = [half(*F_BED, d0 + URA_T), half(*M_BED, -d0),
           half(*D_BED, dot3(D_BED, o) + URA_A1),
           half(-D_BED[0], -D_BED[1], -D_BED[2], -(dot3(D_BED, o) + URA_A0)),
           half(0, 1, 0, URA_Y), half(0, -1, 0, URA_Y)]
    return [ita, ha, ura]


def ray_hits(p, dirv, planes, eps=1e-4):
    t0, t1 = eps, 1e9
    for (nx, ny, nz, d) in planes:
        den = nx * dirv[0] + ny * dirv[1] + nz * dirv[2]
        num = d - (nx * p[0] + ny * p[1] + nz * p[2])
        if abs(den) < 1e-12:
            if num < 0:
                return False
            continue
        tt = num / den
        if den > 0:
            t1 = min(t1, tt)
        else:
            t0 = max(t0, tt)
        if t0 > t1:
            return False
    return t1 > t0


def proj(x, y, z):
    m = 8.3 / (8.3 + y)
    return (AIM_X + (x - AIM_X) * m, LOOK_Z + (z - LOOK_Z) * m, m)


def visible_light(t):
    """#40⑥ 見えている発光量。🔴 渦は**自分で自分を隠す**（きつく巻くほど内側が見えない）ので、
       解析的な遮蔽（板・刃・裏金）だけでは振れが測れない。#78⑦ のとおり **z バッファ**で数える"""
    GW, GH = 240, 300
    sd = solids(t)
    zb = {}
    for j in range(0, N_V + 1, 2):
        v = 2.0 * j / N_V - 1.0
        y = v * WK / 2
        curve = kuzu_curve(t, v)
        for i, c in enumerate(curve):
            e = e_of(S_OF[i])
            if e < 0.02:
                continue
            q = (c[0], y, c[2])
            w = to_world(q, t)
            dw = norm3((CAM_LOC[0] - w[0], CAM_LOC[1] - w[1], CAM_LOC[2] - w[2]))
            dl = to_local_dir(dw, t)
            if any(ray_hits(q, dl, s) for s in sd):
                continue
            if i + 1 < len(curve):
                tg = norm3((curve[i + 1][0] - c[0], 0.0, curve[i + 1][2] - c[2]))
            else:
                tg = (1.0, 0.0, 0.0)
            nrm = norm3(cross3(tg, (0.0, 1.0, 0.0)))
            sx, sz, m = proj(*w)
            gx = int((sx - (AIM_X - FRAME_W / 2)) / FRAME_W * GW)
            gy = int((sz - (LOOK_Z - FRAME_H / 2)) / FRAME_H * GH)
            if not (0 <= gx < GW and 0 <= gy < GH):
                continue
            cell = zb.get((gx, gy))
            if cell is None or w[1] < cell[0]:
                zb[(gx, gy)] = (w[1], e * abs(dot3(nrm, dl)))
    return sum(c[1] for c in zb.values())


if "--probe-only" in sys.argv:
    print("── 074 KANNA 幾何プローブ")
    print("   板 幅%.2f 厚み%.2f 奥行%.2f ／ 刃 勾配%.0f° 厚み%.3f 幅%.2f ／ 屑 幅%.2f"
          % (2 * ITA_Y, ITA_T, ITA_X1 - ITA_X0, math.degrees(ALPHA), HA_T, 2 * HA_Y, WK))
    print("   削り深さ u %.3f〜%.3f ／ 巻きの径 %.3f〜%.3f（幅方向に ±%.0f%%）"
          % (u_of(0.0), u_of(0.5), rc_of(0.0), rc_of(0.5), CONE * 100))

    def turns(rc):
        b = BSPIR * 0.5
        return ((-1 + math.sqrt(1 + 4 * b * LF / rc)) / (2 * b)) / (2 * math.pi)
    print("   屑の全長 %.3f（刃の上 %.2f＋自由 %.2f）／ 渦 %.2f周（薄い）〜%.2f周（厚い）"
          % (URA_A0 + LF, URA_A0, LF, turns(rc_of(0.0)), turns(rc_of(0.5))))

    print("\n   ── 見える光（#40⑥ / #59）")
    vs = [visible_light(x / 24) for x in range(24)]
    vmax = max(vs)
    print("   " + " ".join("%3.0f" % (100 * v / vmax) for v in vs))
    print("   🔴 見える光 min/max = %.3f （合格 0.75以下）" % (min(vs) / vmax))
    th = (STILL_FRAME - 1) / N_FRAMES
    print("   hero(t=%.3f) は最大の %.0f%%" % (th, 100 * visible_light(th) / vmax))

    print("\n   ── 画面（hero frame %d）" % STILL_FRAME)
    pts = {"ita": [], "ha": [], "kuzu": []}
    for xx in (ITA_X0, ITA_X1):
        for yy in (-ITA_Y, ITA_Y):
            for zz in (0.0, -ITA_T):
                pts["ita"].append(to_world((xx, yy, zz), th))
    u = u_of(th)
    for a in (0.0, HA_L):
        for yy in (-HA_Y, HA_Y):
            for k in (0.0, HA_T):
                pts["ha"].append(to_world((a * D_BED[0] + k * M_BED[0] - u, yy,
                                           a * D_BED[2] + k * M_BED[2] - u), th))
    for p in kuzu_verts(th):
        pts["kuzu"].append(to_world(p, th))

    SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2
    box = {}
    for k, ps in pts.items():
        xs = [proj(*p)[0] for p in ps]
        zs = [proj(*p)[1] for p in ps]
        box[k] = (min(xs), max(xs), min(zs), max(zs))
        print("   %-5s x %6.1f..%6.1f%%  z %6.1f..%6.1f%%"
              % (k, (box[k][0] - SX0) / FRAME_W * 100, (box[k][1] - SX0) / FRAME_W * 100,
                 (box[k][2] - SZ0) / FRAME_H * 100, (box[k][3] - SZ0) / FRAME_H * 100))
    x0 = min(b[0] for b in box.values()); x1 = max(b[1] for b in box.values())
    z0 = min(b[2] for b in box.values()); z1 = max(b[3] for b in box.values())
    sl = max(min(x1, SX0 + FRAME_W) - max(x0, SX0), 0) / FRAME_W
    sh = max(min(z1, SZ0 + FRAME_H) - max(z0, SZ0), 0) / FRAME_H
    edge = ((x0 <= SX0) + (x1 >= SX0 + FRAME_W)
            + (z0 <= SZ0) + (z1 >= SZ0 + FRAME_H))
    print("   🔴 長辺 %.1f%%（寄り＝78%%以上）  幅 %.1f%%  高さ %.1f%%  枠への接触 %d辺（寄り＝1以上）"
          % (max(sl, sh) * 100, sl * 100, sh * 100, edge))
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    # 🔴 枠の外の角まで数えると余白を誤診する。**画面内に入っている板の下端**だけを測る
    lows = []
    for i in range(241):
        yy = -ITA_Y + 2 * ITA_Y * i / 240
        px, pz, _ = proj(*to_world((ITA_X0, yy, -ITA_T), th))
        if SX0 <= px <= SX0 + FRAME_W:
            lows.append(pz)
    lo = min(lows) if lows else box["ita"][2]
    print("   画面内の板の下端 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (lo, capz, lo - capz))
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
    "touki": dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10),
    "tetsu": dict(rough=0.50, spec=0.32, metal=0.35, disp=0.005, dsize=0.09),
}


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p, recipe="touki"):
    r = BLACK_RECIPES[recipe]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)


mat_ki, kp_ = principled("ita_touki")
apply_black(kp_, "touki")
mat_ha, hp_ = principled("ha_tetsu")
apply_black(hp_, "tetsu")
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は黒へ戻す（発光板の縁を作らない・#49①）。芯だけ白へ抜く＝halo は
       この「白→ライム」の帯でしか出ない（#81④）"""
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
    apply_black(blk, "touki")

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


mat_glow = glow_material("kuzu")


# ---------- 造形（bmesh・実寸。boolean 不使用）----------
def prism(section, y0, y1, name):
    """x–z 断面の凸多角形を y 方向に押し出した角柱"""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y0, z)) for (x, z) in section]
    hi = [bm.verts.new((x, y1, z)) for (x, z) in section]
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    n = len(section)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=0.5):
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
    ob.rotation_mode = 'XYZ'
    return ob


ita = link(prism([(ITA_X0, -ITA_T), (ITA_X1, -ITA_T), (ITA_X1, 0.0), (ITA_X0, 0.0)],
                 -ITA_Y, ITA_Y, "ita"), "ita", mat_ki)


def blade_mesh(name, a0, a1, k0_of, k1_of, hy, nseg=20):
    """刃道方向に loft する楔。k0/k1 は刃道法線 M_BED 方向の内外"""
    bm = bmesh.new()
    rings = []
    for i in range(nseg + 1):
        a = a0 + (a1 - a0) * i / nseg
        k0, k1 = k0_of(a), k1_of(a)
        base = (a * D_BED[0], a * D_BED[2])
        ring = []
        for (sy, kk) in ((-1, k0), (1, k0), (1, k1), (-1, k1)):
            ring.append(bm.verts.new((base[0] + M_BED[0] * kk, sy * hy,
                                      base[1] + M_BED[2] * kk)))
        rings.append(ring)
    for A, B in zip(rings, rings[1:]):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((A[i], A[j], B[j], B[i]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


ha = link(blade_mesh("ha", 0.0, HA_L, lambda a: 0.0, blade_thick, HA_Y), "ha", mat_ha)
ura = link(blade_mesh("ura", URA_A0, URA_A1,
                      lambda a: -URA_T, lambda a: 0.0, URA_Y), "ura", mat_ha)


def build_kuzu():
    """毎フレームの形をシェイプキーに焼く（#43-e）"""
    nV = N_V + 1
    faces = []
    for i in range(len(S_OF) - 1):
        for j in range(nV - 1):
            a = i * nV + j
            faces.append((a, a + 1, a + nV + 1, a + nV))
    frames = [kuzu_verts(i / N_FRAMES) for i in range(N_FRAMES + 1)]
    me = bpy.data.meshes.new("kuzu")
    me.from_pydata(frames[0], [], faces); me.update()
    ob = bpy.data.objects.new("kuzu", me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat_glow)
    lay = me.uv_layers.new(name="grad")
    uvs = kuzu_uvs()
    for poly in me.polygons:
        for li in poly.loop_indices:
            lay.data[li].uv = uvs[me.loops[li].vertex_index]
    ob.shape_key_add(name="basis", from_mix=False)
    keys = []
    for f, vs in enumerate(frames):
        sk = ob.shape_key_add(name="f%03d" % f, from_mix=False)
        sk.slider_min, sk.slider_max = 0.0, 1.0
        for vi, co in enumerate(vs):
            sk.data[vi].co = co
        keys.append(sk)
    for f, sk in enumerate(keys):
        for d in (-1, 0, 1):
            fr = f + d
            if 0 <= fr < len(frames):
                sk.value = 1.0 if d == 0 else 0.0
                sk.keyframe_insert("value", frame=fr + 1)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=1.2)
    except Exception:
        pass
    ob.select_set(False)
    ob.rotation_mode = 'XYZ'
    return ob


kuzu = build_kuzu()
parts = [ita, ha, ura, kuzu]

# --- 面取りと黒の肌（#52／#80①：黒の稜線は Bevel で作る。add_relief は最後に）---
bv = ita.modifiers.new("bev", 'BEVEL')
bv.width = 0.012; bv.segments = 2; bv.limit_method = 'ANGLE'; bv.angle_limit = 0.52
for ob in (ha, ura):
    bv = ob.modifiers.new("bev", 'BEVEL')
    bv.width = 0.004; bv.segments = 2; bv.limit_method = 'ANGLE'; bv.angle_limit = 0.52
tex_ki = bpy.data.textures.new("relief_touki", 'CLOUDS')
tex_ki.noise_scale = BLACK_RECIPES["touki"]["dsize"]
sub = ita.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 3
d = ita.modifiers.new("disp", 'DISPLACE')
d.texture = tex_ki; d.strength = BLACK_RECIPES["touki"]["disp"]; d.mid_level = 0.5
tex_ha = bpy.data.textures.new("relief_tetsu", 'CLOUDS')
tex_ha.noise_scale = BLACK_RECIPES["tetsu"]["dsize"]
for ob in (ha, ura):
    sub = ob.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 1
    d = ob.modifiers.new("disp", 'DISPLACE')
    d.texture = tex_ha; d.strength = BLACK_RECIPES["tetsu"]["disp"]; d.mid_level = 0.5


# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    rot = (ROT[0], ROT[1], ROT[2] + yaw_of(t))
    loc = (PIVOT[0], PIVOT[1], PIVOT[2] + bob_of(t))
    u = u_of(t)
    dive = rot_xyz((-u, 0.0, -u), *rot)          # 刃は削り深さだけ沈む
    for ob in parts:
        if ob in (ha, ura):
            ob.location = (loc[0] + dive[0], loc[1] + dive[1], loc[2] + dive[2])
        else:
            ob.location = loc
        ob.rotation_euler = rot
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)

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
        caption("MIDDLE STUDY 074 — KANNA", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, 1.95)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：屑の渦の内側が抜けているので面光源をカメラから隠す
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。渦の下・手前に置いて空間へ光を出す
for sx, sy, sz, w in ((-0.35, 2.6, 0.26, LIME_W), (0.55, 5.4, 0.26, LIME_W),
                      (1.35, 9.0, 0.26, LIME_W)):
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
cam.data.dof.focus_distance = math.hypot(8.3 + PIVOT[1], PIVOT[2] - LOOK_Z)
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
        allx += xs; ally += ys
        print(">> %-5s x %6.3f..%6.3f  y %6.3f..%6.3f" % (ob.name, min(xs), max(xs),
                                                          min(ys), max(ys)))
    x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
    sl = max(0.0, min(x1, 1) - max(x0, 0))
    sh = max(0.0, min(y1, 1) - max(y0, 0))
    edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
    print(">> 全体 bbox x %.3f..%.3f y %.3f..%.3f" % (x0, x1, y0, y1))
    print(">> 🔴 長辺 %.1f%%（寄り＝78%%以上）  枠への接触 %d辺（寄り＝1以上）"
          % (max(sl, sh) * 100, edge))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_074.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("kuzu_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    kuzu.data.materials[0] = m_em
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
