# =============================================================
# MIDDLE STUDY 070 — NIJIRIGUCHI（躙口 / the crawl-in entrance of a tea house）
#
# 黒い土壁が、横いっぱいに一枚。左右は画面の外へ出ていて、端は見えない。
# その壁のいちばん下に近いところに、四角い穴がひとつだけ開いている。
# 六十六センチ角。**大人が立って通れない大きさに、わざとしてある。**
#
# 千利休がこの穴を作ったとき、決めたのは寸法ひとつだった。
# 刀は差したままでは入れない。頭を下げなければ入れない。
# 位も、身分も、通り抜けられない。**通れるのは、屈んだ人だけ。**
#
# 壁の仕事は、隔てることだ。窓の仕事は、通すことだ。
# 躙口は、そのどちらでもない。**通す。ただし、姿勢を変えた者だけを。**
# ——だから光は、壁ぜんぶのうち、この穴のかたちの分しか出てこない。
#
# 板戸は、閉じきってもいないし、開ききってもいない。
# 引かれて、また戻る。中では誰かが灯を持って動いている。
# 内と外のあいだにあるのは、扉ではなく、**開いている分量**だ。
#
# 🔴 光の型＝**窓**（#53：69作で7作。孔の“形”が主役）
# 🔴 構図の型＝**寄り**（#57：69作で4作。**69作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／#78／#79 に続く13例目）
#    今日選べたのは 光＝面／隙間／窓 × 構図＝全身／寄り／天地。
#    ・隙間(19) と 全身(51) はシリーズの既定でありもう型ではない。→ 落とす。
#    ・**面 × 天地は #75② で実測済みの不成立**（カメラ軸が完全に水平＝被写体を上げ下げしても
#      面の見え方は 1mm も変わらない＝構図が仕事をしない）。面が残るなら 寄り しかない。
#    ・**窓 × 天地** も同じ理屈の巻き添えを食う（孔の形は高さを変えても変わらない）。
#      #76⑤ の教訓に従い「潰した相手」を明示すると、天地が仕事をするのは
#      **背光**（065 TORII）＝光そのものが余白に広がる型だけ。→ 天地は落とす。
#    ・→ **窓 × 寄り**。窓(7) は 007/017/021/031/044/055/061 の7作あるが、
#      **7作とも「孔のある物体を丸ごと見せて」いる**。躙口は逆で、
#      **孔のまわりを全部見せない**（壁は左右とも枠の外へ出る）。
#      寄って切ることが、そのまま「この穴しか通り道が無い」という主題になる。
#      051 ZENI（丸い板＋真ん中の孔）とは形が近いので**円を1つも使わない**。
#
# 🔴 機構＝**板戸の引きと、中を移る灯**。どちらも整数周期・厳密に閉じる。
#    ・戸：s(t) = S_MID − S_A·cos2πt。t=0 で最も閉じ（孔の 15% だけ残る）、
#      t=0.5 で開ききる。**閉じきらない**——#77② が言うとおり #40⑥ は比なので
#      光が 0 に潰れても「合格」と出る。**下限を絵として持たせておく。**
#    ・灯：発光面そのものを x に ±CORE_A·sin2πt で滑らせる。戸が cos、灯が sin ＝
#      **位相が π/2 ずれるので、どちらかが止まっている瞬間にもう一方が最速**。
#      #59 の「静止率 ≤20%」は往復運動だと端で必ず引っかかるが、これで抜ける。
#    位置キーだけ＝シェイプキー不要でそのまま glb に乗る（#60）。
#
# 🔴 板の合决り（あいじゃくり）は**本物の隙間**にしてある。戸が孔を覆っている間、
#    板と板のあいだから細いライムが3本漏れる。閉じるほど光が減るのではなく、
#    **面から線へ変わる**——これが「窓」を「隙間」に落とさないための担保（hero は開いた側で撮る）。
#
# 造形＝軸に沿った箱と、孔の開いた板だけ。boolean 不使用。object.scale 不使用（#15）。
#    黒の質感は MATERIALS.md の **`touki`**＝土壁も杉板も「触るとざらつく」もの。1作1素材。
#    🔴 #76⑦：SUBSURF は付けず **DISPLACE だけ**（壁も枠も戸も角がある）。
#    🔴 DISPLACE は**土壁だけ**に掛ける。木部に掛けると材が1種類に見える（＝壁も戸も同じ泥）
#    🔴 MATERIALS.md の touki は disp 0.006 / noise 0.10。**壁は 4.66m ある**ので
#       0.10 の粒はレンダー解像度で消える。荒壁の粒として 0.011 / 0.34 に振り直した（#52 掟2の範囲内）
#
# 🔴 #67①：孔が抜けているので **back.visible_camera = False**。
#    さらに back（1800W）は**室内（発光面・柱・上り框）を受光から外す**——
#    外さないと中が白く照らされ、ライムが「点いたパネル」に見える（#76④ の系）。
#
# 【ドメイン】茶室・建築／躙口（シリーズ未踏）。直近10作＝薬研／茶筅／蛸壺／和蝋燭／鳥居／
#    柄鏡／和鋏／紙漉き／埴輪／竈 と別。068 CHASEN は同じ茶でも**道具**、こちらは**建築**。
#    031 TOURO（灯籠の火袋）も「黒に窓」だが、あちらは**光が中にある物体を全身で見せる**作。
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
# 🔴 #58 の「150W」は**被写体の下に床が広く見えている作**の値。この作は壁が床帯の 61% を
#    塞いでいるので、残った 39% に同じ 150W を当てると**床のライムが 79%**（上限 32%）＝舞台が緑になる。
#    実測で 25W まで落として着地。**W数はシリーズ定数ではなく「見えている床の面積」で決まる**
LIME_W = 25.0

# --- 壁（土壁）---------------------------------------------------
PIV_X = 0.55                       # 壁の回転中心（＝カメラの x）
YAW   = math.radians(-7.0)         # 🔴 0°では孔の内法（見込み）が1mmも見えず「印刷した四角」になる
# 🔴 1600×2000 で初めて出た（#68）：壁の左端が枠のすぐ外だと、**左からの key が作る
#    壁の影の端**が床の上にくっきり縦線で出る。壁を左へ2m伸ばして影の端を画面の外へ出す
WX0, WX1 = -3.80, 2.88             # 全長 6.68（フレーム 2.81 より広い＝左右とも枠外へ）
WZ0, WZ1 = 1.34, 6.50              # 🔴 上端はフレームの外（3.71）へ。1周目は 3.02 で上端が見え、
                                   #    上下に横材のある閉じた矩形＝**黒いサイドボード**になった。
                                   #    さらに発光面の光が**壁の上を回り込んで**前面を緑に洗っていた
                                   #    （前面は光源に背を向けているのに緑い＝目視では原因が分からない）
                                   # 🔴🔴 3.71 のすぐ外（4.30）では足りない。**key が壁の上端をかすめて
                                   #    奥の床に届き、床に縦の影の境目**ができる（壁を横へ2m伸ばしても
                                   #    消えない＝原因は横の端ではなく**上の端**だった）。6.50 まで上げて
                                   #    見えている床帯を一様に key の影へ入れる。上端は画面外なので絵は変わらない
TW = 0.150                         # 土壁の厚み（＝孔の見込み）
WY0, WY1 = -TW / 2, TW / 2

# --- 躙口の孔 ----------------------------------------------------
# 🔴 1周目は孔を画面のど真ん中（x=0.55）に置き、板戸が孔の真横に並んで**食器棚の扉**に見えた。
#    孔を右へ 0.40 寄せると、開いた戸は**ほとんど枠の外へ出る**＝hero から戸が消える
HX0, HX1 = 0.59, 1.31              # 幅 0.72（実物 66cm の比）
HZ0, HZ1 = 1.72, 2.42              # 高さ 0.70。敷居は床から 0.38 上

# --- 木部 --------------------------------------------------------
FR_W, FR_SILL, FR_D = 0.072, 0.085, 0.038     # 枠の見付／敷居／壁面からの出
# 🔴 土台（横材）は**取り払った**。前へ出る横材は（a）床に自分の影の帯を作り、
#    （b）壁の下端に「幅木のある家具の台輪」を作る。真壁の柱だけで壁には見える
# 真壁の柱。**これが「家具」を「壁」に変える唯一の部材**（1周目は無かった）
POSTS_W = ((-1.51, -1.39), (-0.28, -0.16))
POSTS_D = 0.032
DW, DH, DT = 0.90, 0.86, 0.042                # 板戸
DZ0 = HZ0 - 0.078
DY1 = WY0 - FR_D - 0.014
DY0 = DY1 - DT
NPLANK, PGAP = 3, 0.009                       # 板3枚・合决りの隙間（本物の隙間＝光が漏れる）
# 🔴 桟（横棧）は付けない。1周目に2本入れたら板戸が**引き出しの前板**に見えた（#72 の系）

# --- 室内 --------------------------------------------------------
EY = 0.62                          # 発光面の y（孔から奥へ 0.545）
EHW = 1.05                         # 発光面の半幅
EZ0, EZ1 = 1.20, 2.90
# 🔴 発光面の下端（1.20）は壁の下端（1.34）より低い＝**壁の下から発光面がはみ出して**
#    床の上に緑の帯と、その左端の縦の段差が出ていた（孔の中では一切分からない）。
#    E の式の基準（EZ0）は動かさず、**メッシュだけ**を壁の内側で切る
EZ_MESH0 = 1.44
CORE_A = 0.30                      # 灯の横移動
EX_C = 0.95                        # 発光面の中心（＝孔の中心）
# 🔴 #75①：発光面は「返しているもの」が描かれていないと必ず「点いたパネル」になる。
#    この2つは装飾ではなく**その唯一の対策**。孔ごしに見えるのは光ではなく「灯のある部屋」
POST = (1.105, 1.180, 0.28, 0.40, 1.30, 2.84)      # 🔴 中央だと「窓の方立」に見える。孔の 71% へ寄せる
KAMACHI = (-0.30, 2.10, 0.09, 0.52, 1.58, 1.86)    # 上り框（室の床。孔の下 20% を占める）

# --- 機構 --------------------------------------------------------
# 🔴 1.56 だと hero で戸が画面の右 16% に残り、**吊戸棚の扉**にしか見えなかった。
#    2.05 まで引くと hero では枠の外へ完全に出る（＝孔だけになる）。移動量も 0.86→1.35 に増える
S_CLOSE, S_OPEN = 0.70, 2.05       # 戸の左端 x（閉＝孔の 15% だけ残る／開＝枠の外へ）
S_MID = 0.5 * (S_CLOSE + S_OPEN)
S_A   = 0.5 * (S_OPEN - S_CLOSE)

# --- 光（#49① 端で厳密に 0 ／ #24 芯→中間→暗部の勾配）-----------
# 🔴🔴 1周目はガウス（U_SIG 0.45／W_SIG 0.26）で作り、**丸い光**になった＝#76③「惑星」。
#    窓の型は「孔の形が主役」なのに、光が孔の形をしていなければ意味が無い。
#    → **平場（super-gaussian・べき6）で孔いっぱいまで一定にし、形は孔が決める**。
#      勾配は平場の中の「傾き（下ほど明るい）」と「小さい芯」だけで作る（#76③ の窓）
# 🔴 2周目の 10.0 でも、白く飛んだ芯が大きすぎて Glare が孔の**外**まで広く洗い、
#    孔の輪郭が溶けた（＝窓の型なのに孔の形が消える）。芯を小さくして強さを落とす
ES_CORE = 6.0
E_FLOOR = 0.060                    # これを引いて 0 に落とす＝発光面の縁を作らない（#49①）
U_PLATE, W_PLATE, W_CTR = 0.62, 0.40, 0.50   # 平場の半幅（べき6）
# 🔴🔴【この作でいちばん高くついた学び】**#14 の std は「暗い側を暗くする」と下がる。**
#    傾きの暗部を 0.34→0.20 と深くしたら std は 34.3→**26.1**まで落ちた。
#    理由：measure.py の is_lime は `g>90` を満たす画素だけを母集団にするので、
#    暗くした画素は**分布を広げるのではなく母集団から抜ける**。残った画素は前より均一になる。
#    ——#45 の p98 と同じ形の罠（母集団が動く指標を、片側だけ動かして読んではいけない）。
#    → std を上げたいときに触るのは**白側（芯の強さ）**。暗部ではない。
HOT_A, HOT_U, HOT_W, HOT_Z = 0.74, 0.13, 0.10, 0.42   # 灯の芯（框のすぐ上に立っている）
E_PEAK = 1.518                     # 上の式の最大値（下で正規化する）
WHITE_FROM, WHITE_TO = 0.86, 0.55  # halo はこの「白→ライム」の帯でしか出ない（#70④）
K_MIX = 7.0

STILL_FRAME = 51                   # t≒0.417 ＝ 戸が孔から外れ、灯は右寄り（左右対称を避ける）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def tau(t):
    return 2.0 * math.pi * t


def slide(t):
    """板戸の左端 x（壁の局所座標）。t=0 で最も閉じ、t=0.5 で開ききる"""
    return S_MID - S_A * math.cos(tau(t))


def core(t):
    """室内の灯の x（ワールド）。戸が cos なので灯は sin ＝位相が π/2 ずれる"""
    return EX_C + CORE_A * math.sin(tau(t))


def e_local(xl, zl):
    """発光面の E。xl∈[-EHW,EHW]（面の中心から）／zl∈[EZ0,EZ1]（ワールド z）
       平場（形は孔が決める）× 傾き（下ほど明るい）＋ 芯（白へ抜く小さな点）"""
    u = xl / EHW
    w = (zl - EZ0) / (EZ1 - EZ0)
    plate = (math.exp(-(abs(u) / U_PLATE) ** 6)
             * math.exp(-(abs(w - W_CTR) / W_PLATE) ** 6))
    tilt = 0.52 + 0.48 * (1.0 - w)     # 🔴 平場は形を作るが勾配を消す。傾きで戻す（#24）
    hot = HOT_A * math.exp(-((u / HOT_U) ** 2) - (((w - HOT_Z) / HOT_W) ** 2))
    raw = plate * (tilt + hot) / E_PEAK
    return max(0.0, (raw - E_FLOOR) / (1.0 - E_FLOOR))


def wrot(x, y):
    """壁の局所 (x,y) → ワールド（PIV_X, y=0 まわりに YAW）"""
    c, s = math.cos(YAW), math.sin(YAW)
    dx = x - PIV_X
    return (PIV_X + dx * c - y * s, dx * s + y * c)


def proj(x, y, z):
    """ワールド → 画面（y=0 平面の実寸）。カメラ軸は完全に +Y（#75②）"""
    m = 8.3 / (8.3 + y)
    return (AIM_X + (x - AIM_X) * m, LOOK_Z + (z - LOOK_Z) * m)


def quad_wall(x0, x1, y, z0, z1):
    """壁の局所矩形（y 一定）を画面の四角形へ"""
    out = []
    for (a, b) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
        wx, wy = wrot(a, y)
        out.append(proj(wx, wy, b))
    return out


def inside(q, p):
    """凸四角形の内外（頂点は順回り）"""
    sgn = 0
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        c = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if c > 1e-12:
            if sgn < 0:
                return False
            sgn = 1
        elif c < -1e-12:
            if sgn > 0:
                return False
            sgn = -1
    return True


GN = 190          # 孔のなかを刻む格子（画面空間）


def visible_light(t, want_area=False):
    """#40⑥ を幾何で積分する。
       見える発光＝（前面の孔）∩（背面の孔）− 戸 − 柱 − 框 を通して見える発光面の E の総和。
       矩形のトンネルなので、前面の孔と背面の孔の**共通部分**が抜けている領域そのもの。"""
    qf = quad_wall(HX0, HX1, WY0, HZ0, HZ1)
    qb = quad_wall(HX0, HX1, WY1, HZ0, HZ1)
    s = slide(t)
    qd = quad_wall(s, s + DW, DY0, DZ0, DZ0 + DH)
    # 板の隙間（合决り）＝戸の中の抜け。板 NPLANK 枚のあいだ
    pw = (DW - PGAP * (NPLANK - 1)) / NPLANK
    qgaps = [quad_wall(s + pw * (k + 1) + PGAP * k, s + pw * (k + 1) + PGAP * (k + 1),
                       DY0, DZ0, DZ0 + DH) for k in range(NPLANK - 1)]
    qpost = [proj(x, POST[2], z) for (x, z) in
             ((POST[0], POST[4]), (POST[1], POST[4]), (POST[1], POST[5]), (POST[0], POST[5]))]
    qkam = [proj(x, KAMACHI[2], z) for (x, z) in
            ((KAMACHI[0], KAMACHI[4]), (KAMACHI[1], KAMACHI[4]),
             (KAMACHI[1], KAMACHI[5]), (KAMACHI[0], KAMACHI[5]))]

    xs = [p[0] for p in qf] + [p[0] for p in qb]
    zs = [p[1] for p in qf] + [p[1] for p in qb]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    dx, dz = (x1 - x0) / GN, (z1 - z0) / GN
    cx = core(t)
    tot = 0.0
    area = 0.0
    for i in range(GN):
        px = x0 + (i + 0.5) * dx
        for j in range(GN):
            pz = z0 + (j + 0.5) * dz
            p = (px, pz)
            if not (inside(qf, p) and inside(qb, p)):
                continue
            if inside(qd, p) and not any(inside(g, p) for g in qgaps):
                continue
            if inside(qpost, p) or inside(qkam, p):
                continue
            # 画面上の点 → 発光面（y=EY）の当たり
            m = 8.3 / (8.3 + EY)
            wx = AIM_X + (px - AIM_X) / m
            wz = LOOK_Z + (pz - LOOK_Z) / m
            e = e_local(wx - cx, wz)
            if e > 0.02:
                tot += e * dx * dz
                area += dx * dz
    return (tot, area) if want_area else tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]

if "--probe-only" in sys.argv:
    print("── 070 NIJIRIGUCHI 幾何プローブ")
    print("   壁 幅%.2f×高さ%.2f 厚み%.3f（フレーム幅 %.2f ＝左右とも枠外へ %.2f）"
          % (WX1 - WX0, WZ1 - WZ0, TW, FRAME_W, (WX1 - WX0 - FRAME_W) / 2))
    print("   孔 %.2f×%.2f（実物 66×63cm の比 %.3f ／ この孔 %.3f）"
          % (HX1 - HX0, HZ1 - HZ0, 63 / 66, (HZ1 - HZ0) / (HX1 - HX0)))
    print("   戸 幅%.2f 移動 %.2f→%.2f（%.2f）  閉じたとき孔の %.0f%% が残る"
          % (DW, S_CLOSE, S_OPEN, S_OPEN - S_CLOSE, (S_CLOSE - HX0) / (HX1 - HX0) * 100))

    step = max(1, N_FRAMES // 24)
    VS = {i: visible_light(_TS[i]) for i in range(0, N_FRAMES, step)}
    vs = [VS[i] for i in sorted(VS)]
    vmax = max(vs)
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(vs) / vmax))
    b = max(VS, key=lambda i: VS[i])
    print("   いちばん明るい frame %d（t=%.3f）  STILL_FRAME=%d" % (b + 1, _TS[b], STILL_FRAME))
    print("   光の曲線 " + " ".join("%.0f" % (100 * v / vmax) for v in vs))

    t = (STILL_FRAME - 1) / N_FRAMES
    tot, la = visible_light(t, want_area=True)
    print("\n   ── 画面占有（hero t=%.3f）" % t)
    print("   ライム面積 ≒ %.2f%%（帯 0.8〜12）"
          % (la / (FRAME_W * FRAME_H * 0.8) * 100))

    # 構図（#57）：被写体＝壁。左右とも枠外へ出ているか／長辺／重心
    SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2
    pts = []
    for (a, bz) in ((WX0, WZ0), (WX1, WZ0), (WX1, WZ1), (WX0, WZ1)):
        for yy in (WY0, WY1):
            wx, wy = wrot(a, yy)
            pts.append(proj(wx, wy, bz))
    gx0, gx1 = min(p[0] for p in pts), max(p[0] for p in pts)
    gz0, gz1 = min(p[1] for p in pts), max(p[1] for p in pts)
    sw = (min(gx1, SX0 + FRAME_W) - max(gx0, SX0)) / FRAME_W * 100
    sh = (min(gz1, SZ0 + FRAME_H) - max(gz0, SZ0)) / FRAME_H * 100
    print("   壁 画面 x %.1f..%.1f%%  y(下から) %.1f..%.1f%%"
          % ((gx0 - SX0) / FRAME_W * 100, (gx1 - SX0) / FRAME_W * 100,
             (gz0 - SZ0) / FRAME_H * 100, (gz1 - SZ0) / FRAME_H * 100))
    print("   🔴 寄り（edge≥1 かつ 長辺≥78）：見えている長辺 %.1f%%  左右の枠接触 %s"
          % (max(sw, sh), "あり" if (gx0 < SX0 and gx1 > SX0 + FRAME_W) else "🔴なし"))
    cy = 100 - ((gz0 + gz1) / 2 - SZ0) / (FRAME_H * 0.8) * 100
    print("   重心y（上から・body基準）≒ %.1f%%（天地の条件 |y−63|≥12 ＝寄りなら関係なし）" % cy)
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    print("   壁の下端 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (gz0, capz, gz0 - capz))
    # #58 の床帯（body の 62〜80%）に白い床が残っているか
    zb_hi = SZ0 + FRAME_H - 0.62 * (FRAME_H * 0.8)
    zb_lo = SZ0 + FRAME_H - 1.00 * (FRAME_H * 0.8)
    free = (min(gz0, zb_hi) - zb_lo) / (zb_hi - zb_lo) * 100
    print("   #58 床帯 z %.3f..%.3f のうち壁で塞がれていない割合 %.0f%%（15%%超なら測れる）"
          % (zb_lo, zb_hi, free))
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
# 土壁も杉板も `touki`＝焼き物・石・土の側。**触ると少しざらつく**もの。1作1素材（掟4）
# 🔴 MATERIALS.md の touki は rough0.58／spec0.26／disp0.006・noise0.10。**プリミティブで採った値**。
#    4.66m の壁に当てたら（a）左半分が輝度 80 まで上がって**黒でなく灰色の樹脂板**になり、
#    （b）0.10 の粒はレンダー解像度で完全に消えて**平滑な板**になった。
#    → 粗さを上げて鏡面を下げ（大面積の広い鏡面ローブを殺す）、起伏は**桁で1つ上げる**。
#    掟2 の 0.020 上限は小さい造形の話。荒壁の粒は実寸で 1〜3cm ある。
# 🔴🔴 さらに 1600×2000 で発覚：**この面積の平面は spec 0.20 でも灰色になる**。
#    黒く見えない原因は色でも粗さでもなく「大面積が環境光の半球ぜんぶを鏡面で拾う」こと。
#    #45 の下限 0.10 ぎりぎりまで落として初めて黒に戻った（黒の情報は起伏が持っている）
# 🔴🔴🔴 spec 0.12 まで落としたら **黒p98 44＝#45 不合格（影絵）**。0.20 では灰色。
#    どちらも「面が平らすぎる」ことの裏表で、鏡面の1本のつまみでは両立しない。
#    → MATERIALS.md の答えのとおり **黒の情報はジオメトリが持つ**。起伏を 0.042→0.060 に上げ、
#      粒を細かく（0.26→0.20）して**小さな面が key を拾う点**を増やすと、
#      平均は上げずに p98 だけ戻る。鏡面は 0.16 で中を取る
BLACK_RECIPES = {"touki": dict(rough=0.62, spec=0.16, metal=0.0, disp=0.055, dsize=0.14)}
RECIPE = "touki"


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p):
    r = BLACK_RECIPES[RECIPE]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r["metal"]


mat_body, bp_ = principled("touki")
apply_black(bp_)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は**土壁の黒そのもの**へ戻す（発光板の縁を作らない・#49①）。
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


mat_glow = glow_material("akari")


# ---------- 造形（bmesh・実寸。局所座標で作り、object に位置と回転を与える）----
def seg(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


def add_box(bm, x0, x1, y0, y1, z0, z1, nx=1, ny=1, nz=1):
    """軸に沿った箱。面の向きは最後に recalc_face_normals で揃える"""
    XS, YS, ZS = seg(x0, x1, nx), seg(y0, y1, ny), seg(z0, z1, nz)
    V = {}

    def v(a, b, c):
        k = (round(a, 6), round(b, 6), round(c, 6))
        if k not in V:
            V[k] = bm.verts.new((a, b, c))
        return V[k]

    def grid(fixed, axis):
        if axis == 'y':                                   # y 一定の面（前後）
            for i in range(len(XS) - 1):
                for j in range(len(ZS) - 1):
                    bm.faces.new((v(XS[i], fixed, ZS[j]), v(XS[i + 1], fixed, ZS[j]),
                                  v(XS[i + 1], fixed, ZS[j + 1]), v(XS[i], fixed, ZS[j + 1])))
        elif axis == 'x':                                 # x 一定の面（左右）
            for i in range(len(YS) - 1):
                for j in range(len(ZS) - 1):
                    bm.faces.new((v(fixed, YS[i], ZS[j]), v(fixed, YS[i + 1], ZS[j]),
                                  v(fixed, YS[i + 1], ZS[j + 1]), v(fixed, YS[i], ZS[j + 1])))
        else:                                             # z 一定の面（上下）
            for i in range(len(XS) - 1):
                for j in range(len(YS) - 1):
                    bm.faces.new((v(XS[i], YS[j], fixed), v(XS[i + 1], YS[j], fixed),
                                  v(XS[i + 1], YS[j + 1], fixed), v(XS[i], YS[j + 1], fixed)))

    grid(y0, 'y'); grid(y1, 'y')
    grid(x0, 'x'); grid(x1, 'x')
    grid(z0, 'z'); grid(z1, 'z')


def build_wall():
    """孔の開いた土壁。格子線を孔の縁にぴったり合わせるので boolean が要らない"""
    XS = seg(WX0, HX0, 96)[:-1] + seg(HX0, HX1, 24)[:-1] + seg(HX1, WX1, 34)
    ZS = seg(WZ0, HZ0, 13)[:-1] + seg(HZ0, HZ1, 24)[:-1] + seg(HZ1, WZ1, 58)
    bm = bmesh.new()
    F = [[bm.verts.new((x, WY0, z)) for z in ZS] for x in XS]
    B = [[bm.verts.new((x, WY1, z)) for z in ZS] for x in XS]
    eps = 1e-7

    def in_hole(i, j):
        return (XS[i] >= HX0 - eps and XS[i + 1] <= HX1 + eps
                and ZS[j] >= HZ0 - eps and ZS[j + 1] <= HZ1 + eps)

    for i in range(len(XS) - 1):
        for j in range(len(ZS) - 1):
            if in_hole(i, j):
                continue
            bm.faces.new((F[i][j], F[i + 1][j], F[i + 1][j + 1], F[i][j + 1]))
            bm.faces.new((B[i][j], B[i + 1][j], B[i + 1][j + 1], B[i][j + 1]))
    # 孔の見込み（4面）
    ih0, ih1 = XS.index(min(XS, key=lambda v: abs(v - HX0))), XS.index(min(XS, key=lambda v: abs(v - HX1)))
    jh0, jh1 = ZS.index(min(ZS, key=lambda v: abs(v - HZ0))), ZS.index(min(ZS, key=lambda v: abs(v - HZ1)))
    for i in range(ih0, ih1):
        for (j, ) in ((jh0, ), (jh1, )):
            bm.faces.new((F[i][j], F[i + 1][j], B[i + 1][j], B[i][j]))
    for j in range(jh0, jh1):
        for (i, ) in ((ih0, ), (ih1, )):
            bm.faces.new((F[i][j], F[i][j + 1], B[i][j + 1], B[i][j]))
    # 外周（4面）
    for i in range(len(XS) - 1):
        for j in (0, len(ZS) - 1):
            bm.faces.new((F[i][j], F[i + 1][j], B[i + 1][j], B[i][j]))
    for j in range(len(ZS) - 1):
        for i in (0, len(XS) - 1):
            bm.faces.new((F[i][j], F[i][j + 1], B[i][j + 1], B[i][j]))
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("kabe"); bm.to_mesh(me); bm.free()
    return me


def build_timber():
    """木部＝上下の横材（桁・土台）＋ 躙口の枠（敷居・鴨居・方立）"""
    bm = bmesh.new()
    for px0, px1 in POSTS_W:                                                      # 真壁の柱
        add_box(bm, px0, px1, WY0 - POSTS_D, WY0 + 0.02, WZ0, WZ1, nx=2, nz=60)
    fy0, fy1 = WY0 - FR_D, WY0 + 0.055
    add_box(bm, HX0 - FR_W, HX1 + FR_W, fy0, fy1, HZ0 - FR_SILL, HZ0 + 0.020, nx=26, nz=4)   # 敷居
    add_box(bm, HX0 - FR_W, HX1 + FR_W, fy0, fy1, HZ1 - 0.020, HZ1 + FR_W, nx=26, nz=3)      # 鴨居
    # 🔴 方立を敷居・鴨居と同じ z 範囲で作ると、**前面が同一平面で重なって z-fighting**し、
    #    枠の四隅に結晶のような破片が出る（480×600 では出ない・#68 の型）。突き付けにする
    for x0, x1 in ((HX0 - FR_W, HX0 + 0.020), (HX1 - 0.020, HX1 + FR_W)):                    # 方立
        add_box(bm, x0, x1, fy0 - 0.002, fy1, HZ0 + 0.018, HZ1 - 0.018, nx=3, nz=24)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("kizai"); bm.to_mesh(me); bm.free()
    return me


def build_door():
    """板戸＝板 NPLANK 枚（合决りの隙間は本物の抜け）＋ 桟2本。
       局所座標：左端 x=0 を基準にし、object.location で滑らせる"""
    bm = bmesh.new()
    pw = (DW - PGAP * (NPLANK - 1)) / NPLANK
    for k in range(NPLANK):
        x0 = k * (pw + PGAP)
        add_box(bm, x0, x0 + pw, DY0, DY1, DZ0, DZ0 + DH, nx=8, nz=22)
    add_box(bm, DW - 0.145, DW - 0.105, DY0 - 0.011, DY0,                     # 引手
            DZ0 + 0.43, DZ0 + 0.57, nx=1, nz=4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("itado"); bm.to_mesh(me); bm.free()
    return me


def build_room():
    """室内＝柱と上り框。**発光面を平板に見せないためだけに在る**（#75① の系）"""
    bm = bmesh.new()
    add_box(bm, *POST[0:2], *POST[2:4], *POST[4:6], nx=2, nz=30)
    add_box(bm, *KAMACHI[0:2], *KAMACHI[2:4], *KAMACHI[4:6], nx=40, nz=3)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("shitsunai"); bm.to_mesh(me); bm.free()
    return me


def build_emitter():
    """室の灯。y=EY の縦の面。E は頂点位置から baked（#39）"""
    NX, NZ = 96, 84
    XS, ZS = seg(-EHW, EHW, NX), seg(EZ_MESH0, EZ1, NZ)
    bm = bmesh.new()
    V = [[bm.verts.new((x, 0.0, z - 0.5 * (EZ0 + EZ1))) for z in ZS] for x in XS]
    for i in range(NX):
        for j in range(NZ):
            bm.faces.new((V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("akari"); bm.to_mesh(me); bm.free()
    return me


def link(me, name, glow=False, smooth=0.52):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat_body)          # slot 0 ＝ 黒（土）
    if glow:
        ob.data.materials.append(mat_glow)      # slot 1 ＝ 発光（UV 勾配）
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


ob_wall = link(build_wall(), "kabe")
ob_tim = link(build_timber(), "kizai")
ob_door = link(build_door(), "itado")
ob_room = link(build_room(), "shitsunai")
ob_emit = link(build_emitter(), "akari", glow=True)

# 発光面の UV（E）を焼く。🔴 面の並び順ではなく**頂点の位置**から引く（#39）
uvl = ob_emit.data.uv_layers.new(name="grad")
ZC = 0.5 * (EZ0 + EZ1)
for poly in ob_emit.data.polygons:
    emax = 0.0
    for li in poly.loop_indices:
        co = ob_emit.data.vertices[ob_emit.data.loops[li].vertex_index].co
        e = e_local(co.x, co.z + ZC)
        uvl.data[li].uv = (e, 0.5)
        emax = max(emax, e)
    # 🔴 glb はノード網を持てない（#25c）。発光する面だけスロット1に分ける（#60）
    poly.material_index = 1 if emax > 0.02 else 0

# 🔴 黒の肌は実ジオメトリ（#52）。SUBSURF は付けず DISPLACE だけ（#76⑦）。
#    掛けるのは**土壁だけ**——木部に掛けると壁と戸が同じ材に見える
_r = BLACK_RECIPES[RECIPE]
tex_relief = bpy.data.textures.new("relief_touki", 'CLOUDS')
tex_relief.noise_scale = _r["dsize"]
d = ob_wall.modifiers.new("disp", 'DISPLACE')
d.texture = tex_relief; d.strength = _r["disp"]; d.mid_level = 0.5

# --- 位置と姿勢 --------------------------------------------------
CY, SY = math.cos(YAW), math.sin(YAW)
for ob in (ob_wall, ob_tim, ob_door):
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0.0, 0.0, YAW)
for ob in (ob_wall, ob_tim):
    ob.location = (PIV_X, 0.0, 0.0)


def door_loc(t):
    """局所 x に slide(t) だけ滑らせる＝ワールドでは壁の向きに沿って動く"""
    s = slide(t)
    return (PIV_X + s * CY, s * SY, 0.0)


# 🔴 mesh は局所座標（PIV_X 基準ではなく素の x）で作ってあるので、原点差を引く
for ob in (ob_wall, ob_tim):
    ob.data.transform(__import__("mathutils").Matrix.Translation((-PIV_X, 0, 0)))
ob_door.data.transform(__import__("mathutils").Matrix.Translation((-PIV_X, 0, 0)))
ob_emit.location = (EX_C, EY, ZC)

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    ob_door.location = door_loc(t)
    ob_emit.location = (core(t), EY, ZC)
    ob_door.keyframe_insert("location", frame=f + 1)
    ob_emit.keyframe_insert("location", frame=f + 1)

parts = [ob_wall, ob_tim, ob_door, ob_room, ob_emit]

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
        caption("MIDDLE STUDY 070 — NIJIRIGUCHI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, LOOK_Z + 0.10)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：孔が抜けている＝面光源が素通しで写る

# 🔴 #58③：随伴のライム光源は**発光体の外**。壁の下端より奥（画面 62〜80% の帯に届く位置）へ
for sx, sy, sz, w in ((-0.80, 8.5, 0.30, LIME_W), (0.30, 12.0, 0.30, LIME_W),
                      (1.55, 17.0, 0.30, LIME_W)):
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
cam.data.dof.focus_distance = 8.30     # 壁は y≒0
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは**全ジオメトリ生成後**に置く（#56②）。
#    床だけでなく**室内（発光面・柱・框）も外す**——中が白く照らされると光が点いたパネルになる
lit = bpy.data.collections.new("lit_by_back")
bpy.context.scene.collection.children.link(lit)
for o in (ob_wall, ob_tim, ob_door):
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
    gx0 = gy0 = 9.0; gx1 = gy1 = -9.0
    for ob in parts:
        ev = ob.evaluated_get(dg)
        xs, ys = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
        print(">> %-10s x %.3f..%.3f  y %.3f..%.3f" % (ob.name, min(xs), max(xs),
                                                       min(ys), max(ys)))
        if ob is not ob_emit and ob is not ob_room:
            gx0 = min(gx0, min(xs)); gx1 = max(gx1, max(xs))
            gy0 = min(gy0, min(ys)); gy1 = max(gy1, max(ys))
    print(">> 壁+木部 bbox x %.3f..%.3f  y %.3f..%.3f  → 見えている長辺 %.1f%%（寄り＝78以上）"
          % (gx0, gx1, gy0, gy1,
             max(min(gx1, 1) - max(gx0, 0), min(gy1, 1) - max(gy0, 0)) * 100))
    print(">> 枠まで 左%.3f 右%.3f 上%.3f 下%.3f（左右が負なら枠外へ出ている＝edge≥2）"
          % (gx0, 1 - gx1, 1 - gy1, gy0))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_070.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("akari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    ob_emit.data.materials[1] = m_em
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
