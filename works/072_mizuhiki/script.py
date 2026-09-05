# =============================================================
# MIDDLE STUDY 072 — MIZUHIKI（水引 / the knot that holds the light）
#
# 水引は、贈り物を結ぶための紙の紐だ。
# 和紙を細くこよって、糊を引いて、まっすぐに伸ばしてある。
# 一本では何の役にも立たない。**結んで初めて、意味になる。**
#
# 五本の水引が、五つの輪を編む。梅結び。
# 端は二本、下へ垂れる。切りっぱなしで、長さも揃っていない。
# 輪はぜんぶ外側にあって、**真ん中には、何も無い。**
# その何も無いところに、光がある。
#
# 引けば輪は深くなり、真ん中は狭くなって、光は小さくなる。
# ゆるめれば輪は浅くなり、真ん中がひらいて、光は戻る。
# 外まわりの大きさは、どちらでも同じだ。
# ——**変わっているのは、真ん中だけ。**
#
# 🔴 光の型＝**芯**（#53：71作で8作。中心の小さな塊、周りは黒）
# 🔴 構図の型＝**天地**（#57：71作で3作。**71作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／
#    #76⑤／#78／#79／#80／#81 に続く15例目）。今日選べたのは
#    光＝隙間／芯／背光 × 構図＝全身／端寄せ／天地。9通りを works.json で数えたら：
#      隙間×全身 18 ／ 隙間×端寄せ 1 ／ 隙間×天地 0
#      芯 ×全身  6 ／ 芯 ×端寄せ 0 ／ 芯 ×天地  0
#      背光×全身  3 ／ 背光×端寄せ 0 ／ 背光×天地 1
#    ・**背光は #74②／#76⑤ より「全身か天地」の二択**で、天地は 065 TORII で既出。→ 落とす。
#    ・隙間(19) と 全身(51) はシリーズの既定であって、もう型ではない。→ 落とす。
#    ・残る空欄は **芯×端寄せ** と **芯×天地**。端寄せは「空いた側を余白として使う」型だが、
#      **芯は被写体の中心に光を置く型**なので、重心を横へ振ると光まで一緒に寄り、
#      余白が「光の無い側」になる。天地なら**光は画面の中心軸に残したまま**、上下の配分だけを主題にできる。
#    → **芯×天地**。71作で一度も無い組み合わせ。
#
# 🔴 天地は「高く浮かせる」側を採る（条件＝重心yが基準63%から12%以上ずれる＝c_y≤51）。
#    ・沈める側（c_y≥75）は #75⑥ のとおりキャプション帯とぶつかる。
#    ・浮かせる側なら **#58 の床帯（画面の62〜80%）が空くので、床のライムが素直に測れる**。
#    ・結び（密）を上に、垂れた端（疎）を下に置くと重心はさらに上がる＝機構と構図が同じ向き。
#    実測 c_y **40.0%**（`compositions.py --verify` 通過）。
#
# 🔴 機構＝**輪の深さ**。KRR(s)=0.85→1.12・K(s)=R_OUT/(KR+KRR) で
#    **外半径 R_OUT=0.680 を定数に固定したまま、内側の開口だけ 0.289→0.215 と閉じる**。
#    受け皿（光）にも同じシェイプキーを入れて一緒に縮ませるので、
#    **真ん中の形が、そのまま光の形**になる。#40⑥ は 0.693（合格 0.75以下・swing 1.44）。
#    🔴 #80⑥：往復は端で必ず静止するので、morph は cos、揺れ（Y軸）と漂い（z）は sin＝
#    位相が π/2 ずれて、どちらかが止まる瞬間にもう一方が最速。
#    シェイプキー2本＋位置・回転のキーだけ＝そのまま glb に乗る（#60）。
#
# 造形＝(2,5) トーラス結びを**平たく潰した**もの＝梅結び。
#    ρ(t)=K(2.6+KRR·cos5t)・偏角 2t・奥行き A·sin5t。奥行きは K に比例させない（紐の太さは変わらない）。
#    交差は 5t=π/2+kπ の10点＝**投影で5箇所**、そこで奥行きの差はちょうど 2A＝上下がきれいに入れ替わる。
#    切る場所は t=4π/5（ρ最大・接線が水平・奥行き0）で、全体を −18°回して**その点を真下の対称軸上**へ。
#    ここで切ると両端は水平に向かい合って出るので、左右の端は下へ曲げながら**互いに入れ替わって**垂れる
#    （実物の水引と同じ）。入れ替わる所で貫通しないよう、左は奥へ +1.4A、右は手前へ −1.4A へ寄せた。
#    🔴 完全な左右対称は図案になる（#75③）ので、**端の長さと開き角を左右で変え**、
#    さらに結びの面を Z まわりに 17°・X まわりに −8° 静的に振った（#74：正対した平たい結びはバッジに読める）。
#    紐の全長 TOT=9.32 は定数で、結びが使った残りが垂れになる。boolean 不使用・object.scale 不使用（#15）。
#
# 🔴🔴🔴 6周かかった。効いた4つ（→ PITFALLS #82）：
#  ① **輪を3つで組むと「顔」に読める。**上に2つ・下に1つ＝耳と口。5つにすると顔の配置が壊れ、
#     しかも実物の水引の結び（梅結び）に一致した。**輪の数は意匠ではなく、読まれ方を決める骨格**。
#  ② 🔴🔴【本命】**「籠に入った光る卵」の犯人は、光っている部分ではなく“光っていない部分の形”だった。**
#     半径固定の円盤を奥に置くと、E が落ちた外周は（#49①の作りでは）黒の Principled に戻るので
#     **不透明な黒い円盤**になり、輪と輪のあいだからそれが見える。**数値には一切出ない**
#     （ライム面積も #40⑥ も #14 も正常）。→ 受け皿の**輪郭を結びの内側の包絡線
#     ρ_in(a)=K(KR−KRR|cos(5a/2)|) にする**と、縁は必ず紐の下に潜る＝#76③「輪郭は持たせない」。
#  ③ **等値線が円でないと、灯りに見えない。**②のあと E を「開口に対する比」で引いたら
#     等値線まで星形になり、**白い星が浮いた「星のバッジ」**になった。
#     → E は**開いた状態の絶対半径で焼き、メッシュごとシェイプキーで縮める**。
#     等値線は円のまま、光は結びと一緒に小さくなる。しかも E は開口の手前で 0 近くまで落ちるので
#     **光と紐のあいだに黒い余白が残る**＝塗りでなく灯りになる（#24 のペンキ化を幾何で外す）。
#  ④ **丸い紐に rough 0.80 を当てると黒が影絵になる**（黒平均12.3／p98 50.8＝#45 不合格）。
#     水引は紐だが素材は**和紙**なので `nuno_usu` が正しく、さらに #45 のとおり
#     **効くのは Specular IOR Level**（0.28→0.38・rough 0.62）で p98 50.8→62.5。
#
# 黒の質感は MATERIALS.md の **`nuno_usu`（薄物・紙）**。#81③ の Sheen 0 ＋ #62③ の Metallic 0.34。
#    DISPLACE は掛けない（#77⑩：半径 0.0105 の紐に strength 0.004 は起伏が半径の 38% になる）。
#
# 【ドメイン】儀礼・水引（シリーズ未踏）。直近10作＝的／躙口／薬研／茶筅／蛸壺／和蝋燭／鳥居／
#    柄鏡／和鋏／紙漉き と別。006 ITO は球に巻きつく1本の糸、033 は縄の「撚り」で、
#    どちらも**結び**ではない（結び目はシリーズ初）。
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
LIME_W = 110.0                     # 随伴のライム光源（#58／#80⑤：シリーズ定数ではない）

# --- 結び（淡路結び＝平たく潰した (2,3) トーラス結び）----------------
# ρ = K(KR + KRR·cos3t)。内 (KR−KRR)K ／ 外 (KR+KRR)K
# 🔴 1周目は「結び全体を拡大縮小する」で組んだが、**#40⑥ が 0.994＝光がまったく動かなかった**。
#    内接の開口は (KR−KRR)K − 束の半幅 なので、K だけを ±8% 振っても開口は 0.226→0.271 しか動かない。
#    しかも Λ ∝ K なので、K を大きく振ると**垂れの長さが 0.54→1.12 と2倍に暴れて構図が壊れる**。
#    → **外径 R_OUT を定数に固定して、輪の深さ KRR の方を振る**。
#      K(s) = R_OUT/(KR+KRR(s)) なので外径は動かず、**内側の開口だけが 0.305→0.160 と閉じる**。
#      面積では 0.28 倍＝#40⑥ が素直に入る。垂れの長さは Λ の差ぶんだけ静かに動く。
# 🔴 3周目まで LOBES=3（＝古典的な三つ葉結び）で組んだが、**絵は結び目に読まれなかった**。
#    輪が2つ上・1つ下に並ぶので「耳・鼻・口」＝顔に読める（#33 の型）。
#    実物の水引の結びは輪がもっと多くて密で、**梅結び（五弁）**がいちばん近い。
#    → LOBES=5。交差は 5t=π/2+kπ の10点＝投影で5箇所。輪が細くなり、真ん中の座が小さくなる。
LOBES = 5
KR = 2.6
KRR_OPEN, KRR_SHUT = 0.85, 1.12    # 輪の深さ（浅い＝真ん中が開く／深い＝閉じる）
R_OUT = 0.680                      # 結びの外半径（定数）
K_CUT = 2                          # 切る輪の番号（ρ最大・接線水平・奥行き0 の点を真下へ）
A_DEPTH = 0.019                    # 奥行きの振幅。交差での隙は 2A=0.038 > 紐の直径 0.021
TC = 2.0 * math.pi * K_CUT / LOBES          # 切る位置（ρ最大・接線水平・奥行き0）
ROT0 = 1.5 * math.pi - 2.0 * TC             # 切り口を真下の対称軸へ回す
DELTA = 0.010 * math.pi            # 切り口の開き（両端のあいだ）

NCORD, CD, CR = 5, 0.0225, 0.0105  # 五本・芯間隔・紐の半径。束の半幅 = 2CD+CR = 0.0555
BUNDLE_HW = 2 * CD + CR

TOT = 9.32                         # 紐1本の全長（定数）。結び＋垂れ2本
TAIL_SPLIT = 0.468                 # 左右の分け方（#75③：完全対称を避ける）
TAIL_DIR_L = (-0.055, -0.998)       # 左の端が最後に向かう向き（XZ）
TAIL_DIR_R = (0.10, -0.995)        # 右の端（開き角も左右で変える）
TAIL_BLEND = 0.46                  # 向きが下へ切り替わるまでの弧長
TAIL_Y = 1.40 * A_DEPTH            # 端どうしが入れ替わる所での前後の逃げ

KNOT_C = (AIM_X, 0.0, 2.72)        # 結び目の中心（天地＝高く浮かせる）
# 🔴 #74：正対した平たい結びは「バッジ」に読める（#81② の型）。**面を少し寝かせる**と
#    輪どうしの重なりが左右で不揃いになり、空間に在る物になる。揺れとは別の、静的な傾き。
RX_TILT = math.radians(-8.0)       # 上を奥へ倒す
RZ_TURN = math.radians(17.0)       # 結びの面を横へ振る（垂れは鉛直のまま）
RY_A = math.radians(2.4)           # Y軸まわりの揺れ
BOB = 0.030                        # z の漂い

NK, NT, NR = 432, 96, 10           # 結びの分割／垂れの分割／紐の周の分割

# --- 玉（真ん中の光）------------------------------------------------
# 🔴 #81④：halo は「明るいライム」では 1px も増えない（青が上がらない）。
#    青を 90 まで持ち上げられるのは**白へ抜ける広い勾配**だけなので、
#    ガウスの山ひとつ＋白へ抜く芯、という 071 と同じ作りにした。
#    🔴 ただし 071 は「面」の型なので発光面が被写体いっぱいだった。ここは**芯**なので
#    E が 0 に落ちきる半径（0.42）を**結び目の内側の開口（内接 0.248・最大 0.44）に収める**。
#    ＝光の可視域が被写体の外形（0.74）より外へ出ないこと。出たら定義上それは背光（#76②）。
# 🔴🔴 2周目までは半径固定の円盤を結びの奥へ置いていた。**これが最大の失敗**だった——
#    E が落ちた外周は（#49①の作りでは）黒の Principled に戻るので**不透明な黒い円盤**になり、
#    輪と輪のあいだの隙間からそれが見えて、絵は「籠に入った光る卵」になった。
#    数値には出ない（ライム面積も #40⑥ も正常）。**光の形ではなく、光っていない部分の形が犯人**。
# 🔴 直し方＝**受け皿の輪郭を結びの内側の包絡線そのものにする。**
#    方向 a に対して内側の枝は ρ_in(a) = K(KR − KRR|cos(3a/2)|)（外側の枝は +KRR）。
#    受け皿の縁を ρ_in(a) − 束の半幅 + OVER に置けば、**縁は必ず紐の下に潜る**。
#    さらに結びが閉じると紐は内へ寄るので、縁はいっそう深く隠れる（開いた状態で作れば十分）。
#    ＝#76③「輪郭は隠すのではなく、持たせない」を、持たせずに済ませる唯一の作り方。
LENS_OVER = 0.026                  # 縁を紐の下へ潜らせる深さ
# 🔴 4周目の失敗：E を**絶対半径**で引いたら、光は開口いっぱいまで届いて
#    **縁が紐でぴったり切られた「緑の星」＝シールになった**（#24 のペンキ化の別型）。
#    → E は**開口に対する比 v = r/縁(a,s)** で引く。受け皿にもシェイプキーを入れて
#      結びと一緒に縮ませる＝**真ん中の形が、そのまま光の形**。
# 🔴 5周目の失敗：E を**開口に対する比**で引いたら、等値線まで星形になり
#    **白い星が真ん中に浮いた「星のバッジ」**になった。等値線は円でなければ灯りに見えない。
#    → E は**開いた状態の絶対半径**で引いて UV に焼き、**メッシュごとシェイプキーで縮める**。
#      等値線は円のまま、光は結びと一緒に小さくなる。しかも E は開口の手前で 0 近くまで落ちるので、
#      **光と紐のあいだに黒い余白が残る**＝塗りでなく灯りになる（#24 のペンキ化を幾何で外す）。
GL = 0.190                         # 透過の山（絶対半径・開いた状態で焼く）
HOT_A, HOT_U = 0.26, 0.055         # 白へ抜く芯（絶対半径）
E_PEAK = 1.0 + HOT_A
E_FLOOR = 0.010
ES_CORE = 4.2
WHITE_FROM, WHITE_TO = 0.70, 0.45
K_MIX = 16.0                       # 🔴 #76①：不透明さを発光の強さから切り離す。E≥0.0625 で不透明
LENS_Y, LENS_DOME = 0.075, 0.000   # 受け皿は紐より奥。真ん中だけわずかに手前へ

STILL_FRAME = 16


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def tau(t):
    return 2.0 * math.pi * t


def morph(t):
    """0＝締まり／1＝ゆるみ。cos なので t=0,0.5 で端（#80⑥ の相手は sin 側）"""
    return 0.5 - 0.5 * math.cos(tau(t))


def krr_of(s_):
    return KRR_OPEN + (KRR_SHUT - KRR_OPEN) * s_


def k_of(s_):
    return R_OUT / (KR + krr_of(s_))


def ry(t):
    return RY_A * math.sin(tau(t))


def bob(t):
    return BOB * math.sin(tau(t))


def knot_pt(t_, s_):
    """平たく潰した (2,3) トーラス結び。+30°回してある。戻り値は (x, y, z)"""
    rho = k_of(s_) * (KR + krr_of(s_) * math.cos(LOBES * t_))
    a = 2.0 * t_ + ROT0
    return (rho * math.cos(a), A_DEPTH * math.sin(LOBES * t_), rho * math.sin(a))


def knot_tan(t_, s_):
    """XZ 平面での接線（正規化）"""
    K, KRR = k_of(s_), krr_of(s_)
    rho = K * (KR + KRR * math.cos(LOBES * t_))
    rp = -LOBES * K * KRR * math.sin(LOBES * t_)
    a = 2.0 * t_ + ROT0
    dx = rp * math.cos(a) - 2.0 * rho * math.sin(a)
    dz = rp * math.sin(a) + 2.0 * rho * math.cos(a)
    n = math.hypot(dx, dz)
    return (dx / n, dz / n)


def knot_len(s_):
    """結びの中心線の弧長（数値積分）"""
    acc, n = 0.0, 3000
    t0, t1 = TC + DELTA, TC + 2.0 * math.pi - DELTA
    prev = knot_pt(t0, s_)
    for i in range(1, n + 1):
        p = knot_pt(t0 + (t1 - t0) * i / n, s_)
        acc += math.dist(p, prev)
        prev = p
    return acc


def tail_lengths(s_):
    rest = TOT - knot_len(s_)
    return rest * TAIL_SPLIT, rest * (1.0 - TAIL_SPLIT)


def _smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


def tail_path(p0, d0, y0, target, length, ytarget, n):
    """端から下へ垂れる紐。向きは d0 → target へ弧長で滑らかに切り替える。
       戻り値は (点, XZ方向) の列（p0 は含まない）"""
    tx, tz = target
    tn = math.hypot(tx, tz)
    tx, tz = tx / tn, tz / tn
    ds = length / n
    x, y, z = p0
    out = []
    for i in range(1, n + 1):
        s = (i - 0.5) * ds
        w = _smooth(s / TAIL_BLEND)
        dx = d0[0] * (1 - w) + tx * w
        dz = d0[1] * (1 - w) + tz * w
        dn = math.hypot(dx, dz)
        dx, dz = dx / dn, dz / dn
        x += dx * ds
        z += dz * ds
        y = y0 + (ytarget - y0) * _smooth((i * ds) / TAIL_BLEND)
        out.append(((x, y, z), (dx, dz)))
    return out


def centerline(s_):
    """紐1本ぶんの道筋（結びの中心＝原点）。戻り値は [(点, XZ方向), ...]。
       左の垂れ（逆順）＋結び＋右の垂れ の順に一本につながっている"""
    t0, t1 = TC + DELTA, TC + 2.0 * math.pi - DELTA
    knot = []
    for i in range(NK + 1):
        t_ = t0 + (t1 - t0) * i / NK
        knot.append((knot_pt(t_, s_), knot_tan(t_, s_)))
    lL, lR = tail_lengths(s_)
    # 端1（t0 側）＝進行方向の逆へ出る
    d_a = (-knot[0][1][0], -knot[0][1][1])
    ta = tail_path(knot[0][0], d_a, knot[0][0][1], TAIL_DIR_L, lL, TAIL_Y, NT)
    # 端2（t1 側）＝進行方向へ出る
    tb = tail_path(knot[-1][0], knot[-1][1], knot[-1][0][1], TAIL_DIR_R, lR, -TAIL_Y, NT)
    # 端1側は逆順にして先頭へ。向きも反転して一本の進行方向に揃える
    head = [(p, (-d[0], -d[1])) for p, d in reversed(ta)]
    return head + knot + tb


def cord_points(s_, j):
    """j 番目（0..NCORD-1）の紐の中心線。束は XZ 平面内の法線方向へ並べる"""
    off = (j - (NCORD - 1) / 2.0) * CD
    pts = []
    for (x, y, z), (dx, dz) in centerline(s_):
        nx, nz = -dz, dx
        pts.append((x + nx * off, y, z + nz * off))
    return pts


def min_curv_radius(s_):
    """束が内側で潰れないか＝投影の曲率半径が束の半幅を上回るか"""
    pts = [p for p, _ in centerline(s_)]
    best = 9.9
    for i in range(1, len(pts) - 1):
        ax, az = pts[i - 1][0], pts[i - 1][2]
        bx, bz = pts[i][0], pts[i][2]
        cx, cz = pts[i + 1][0], pts[i + 1][2]
        a = math.hypot(bx - ax, bz - az)
        b = math.hypot(cx - bx, cz - bz)
        c = math.hypot(cx - ax, cz - az)
        area = abs((bx - ax) * (cz - az) - (cx - ax) * (bz - az)) / 2.0
        if area > 1e-12:
            best = min(best, a * b * c / (4.0 * area))
    return best


def rho_in(a_raw, s_):
    """方向 a_raw（回す前）で、結びの**内側の枝**までの距離"""
    return k_of(s_) * (KR - krr_of(s_) * abs(math.cos(0.5 * LOBES * a_raw)))


def lens_edge(a_raw, s_):
    """受け皿の縁＝内側包絡線から束の半幅ぶん内へ、さらに OVER だけ潜らせる。
       s_ で縮むので縁は常に紐の下（#76③）"""
    return max(0.030, rho_in(a_raw, s_) - BUNDLE_HW + LENS_OVER)


def e_lens(rho):
    """受け皿の E（0..1）。引数は**開いた状態での絶対半径**。等値線は円"""
    raw = math.exp(-((rho / GL) ** 2)) + HOT_A * math.exp(-((rho / HOT_U) ** 2))
    return max(0.0, (raw / E_PEAK - E_FLOOR) / (1.0 - E_FLOOR))


def _raster(s_, N=380, half=0.52, e_cut=0.14):
    """投影面（XZ）を刻んで、紐で塞がれていない所の玉の面積を数える。
       紐は中心線に沿って円を押し当てて塗る（総当たりだと 560²×3000 で終わらない）。
       戻り値 (開口の面積, ライムとして見える面積, 開口の内接半径)"""
    cell = 2.0 * half / N
    blocked = bytearray(N * N)
    rad = int(math.ceil(CR / cell))
    for j in range(NCORD):
        pts = cord_points(s_, j)
        for i in range(len(pts) - 1):
            x0, z0 = pts[i][0], pts[i][2]
            x1, z1 = pts[i + 1][0], pts[i + 1][2]
            d = math.hypot(x1 - x0, z1 - z0)
            steps = max(1, int(d / (cell * 0.5)) + 1)
            for q in range(steps + 1):
                u = q / steps
                cx, cz = x0 + (x1 - x0) * u, z0 + (z1 - z0) * u
                if math.hypot(cx, cz) > half:
                    continue
                ix = int((cx + half) / cell)
                iz = int((cz + half) / cell)
                for dz in range(-rad, rad + 1):
                    jz = iz + dz
                    if jz < 0 or jz >= N:
                        continue
                    for dx in range(-rad, rad + 1):
                        jx = ix + dx
                        if jx < 0 or jx >= N:
                            continue
                        px = -half + (jx + 0.5) * cell
                        pz = -half + (jz + 0.5) * cell
                        if math.hypot(px - cx, pz - cz) < CR:
                            blocked[jz * N + jx] = 1
    open_a = lime_a = 0.0
    inner = 9.9
    for jz in range(N):
        z = -half + (jz + 0.5) * cell
        for jx in range(N):
            x = -half + (jx + 0.5) * cell
            rho = math.hypot(x, z)
            edge = lens_edge(math.atan2(z, x) - ROT0, s_)
            if rho >= edge:
                continue
            if blocked[jz * N + jx]:
                inner = min(inner, rho)
                continue
            open_a += cell * cell
            # 焼いた UV は開いた状態の半径。閉じるとメッシュごと縮むので比で戻す
            if e_lens(rho * lens_edge(math.atan2(z, x) - ROT0, 0.0) / edge) >= e_cut:
                lime_a += cell * cell
    return open_a, lime_a, inner


def visible_light(t):
    """#40⑥ を幾何で数える＝紐に塞がれずに見える『光っている面』の面積"""
    return _raster(morph(t))[1]


def proj(x, y, z):
    m = 8.3 / (8.3 + y)
    return (AIM_X + (x - AIM_X) * m, LOOK_Z + (z - LOOK_Z) * m, m)


_TS = [i / N_FRAMES for i in range(N_FRAMES)]

if "--probe-only" in sys.argv:
    print("── 072 MIZUHIKI 幾何プローブ")
    print("   外半径 %.3f（定数）＋束の半幅 %.4f ＝ %.3f" % (R_OUT, BUNDLE_HW, R_OUT + BUNDLE_HW))
    print("   紐 半径%.4f（直径 %.0fpx@1600）／芯間隔%.4f／五本の幅 %.0fpx"
          % (CR, 2 * CR / FRAME_W * 1600, CD, 2 * BUNDLE_HW / FRAME_W * 1600))
    for nm, s_ in (("開", 0.0), ("閉", 1.0)):
        lL, lR = tail_lengths(s_)
        print("   %s KRR=%.2f K=%.4f 内接の開口 %.4f 結びの弧長 %.3f 垂れ 左%.3f 右%.3f 曲率半径の最小 %.4f（>%.4f）"
              % (nm, krr_of(s_), k_of(s_), (KR - krr_of(s_)) * k_of(s_) - BUNDLE_HW,
                 knot_len(s_), lL, lR, min_curv_radius(s_), BUNDLE_HW))
    print("   奥行き 2A=%.4f > 紐の直径 %.4f（交差が貫通しないこと）" % (2 * A_DEPTH, 2 * CR))

    print("\n   ── 光（#40⑥ / #51 / #76②）")
    oa_o, la_o, in_o = _raster(0.0)
    oa_s, la_s, in_s = _raster(1.0)
    print("   開 開口%.4f ライム%.4f 内接%.3f ／ 閉 開口%.4f ライム%.4f 内接%.3f"
          % (oa_o, la_o, in_o, oa_s, la_s, in_s))
    print("   🔴 見える光 min/max = %.3f （合格 0.75以下）" % (la_s / la_o))
    body = FRAME_W * FRAME_H * 0.8
    print("   ライム面積 ≒ %.2f%%（帯 0.8〜12）／光の可視域 0.30 < 被写体の外形 %.3f なら芯（#76②）"
          % (la_o / body * 100, R_OUT + BUNDLE_HW))

    th = (STILL_FRAME - 1) / N_FRAMES
    sh = morph(th)
    print("\n   ── 画面（hero frame %d・t=%.3f・s=%.3f）" % (STILL_FRAME, th, sh))
    xs, zs, zsum, wsum = [], [], 0.0, 0.0
    for j in range(NCORD):
        for (x, y, z) in cord_points(sh, j):
            px, pz, _ = proj(KNOT_C[0] + x, KNOT_C[1] + y, KNOT_C[2] + z + bob(th))
            xs.append(px); zs.append(pz); zsum += pz; wsum += 1.0
    x0, x1 = min(xs) - CR, max(xs) + CR
    z0, z1 = min(zs) - CR, max(zs) + CR
    SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2
    print("   bbox x %.1f..%.1f%%  z(下から) %.1f..%.1f%%"
          % ((x0 - SX0) / FRAME_W * 100, (x1 - SX0) / FRAME_W * 100,
             (z0 - SZ0) / FRAME_H * 100, (z1 - SZ0) / FRAME_H * 100))
    print("   🔴 長辺 %.1f%%（帯 55〜65）  幅 %.1f%%  高さ %.1f%%"
          % (max((x1 - x0) / FRAME_W, (z1 - z0) / FRAME_H) * 100,
             (x1 - x0) / FRAME_W * 100, (z1 - z0) / FRAME_H * 100))
    print("   上の余白 %.3f（正なら edge=0）／左 %.3f ／右 %.3f"
          % (SZ0 + FRAME_H - z1, x0 - SX0, SX0 + FRAME_W - x1))
    top = SZ0 + FRAME_H
    print("   🔴 重心 y（上から・分母は上80%%）≒ %.1f%%（天地は ≤51 か ≥75）"
          % ((top - zsum / wsum) / (FRAME_H * 0.8) * 100))
    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    print("   垂れの下端 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (z0, capz, z0 - capz))

    print("\n   ── 機構")
    vs = [visible_light(_TS[i]) for i in range(0, N_FRAMES, N_FRAMES // 12)]
    vmax = max(vs)
    print("   光の曲線 " + " ".join("%.0f" % (100 * v / vmax) for v in vs))
    print("   hero の光は最大の %.0f%%（揺れ %.2f° の %.0f%%）"
          % (100 * visible_light(th) / vmax, math.degrees(ry(th)),
             100 * abs(math.sin(tau(th)))))
    lL, lR = tail_lengths(sh)
    print("   hero の垂れ 左%.3f 右%.3f（開 %.3f/%.3f → 閉 %.3f/%.3f）"
          % (lL, lR, *tail_lengths(0.0), *tail_lengths(1.0)))
    print("   紐の全長 %.3f（定数）＝結び %.3f ＋ 垂れ %.3f" % (TOT, knot_len(sh), lL + lR))
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
# 🔴 水引は「紐」だが、素材は**和紙**（こよりに糊を引き、絹を巻いたもの）＝`nuno_usu`（薄物・紙）。
#    最初 `nuno`（布・厚物：縄・紐・帯）で組んだが、**黒平均12.3／p98 50.8 で #45 に落ちた**
#    ——rough 0.80 は丸い紐の上で鏡面の芯を消してしまい、黒が影絵になる。
#    `nuno_usu`（rough0.66／spec0.28）＋ #81③ の Sheen 0 ＋ #62③ の Metallic 0.34 は 071 で実証済み。
# DISPLACE は掛けない（#77⑩：紐の半径 0.0105 に対して strength 0.004 は大きすぎる）
BLACK_RECIPES = {"nuno_usu": dict(rough=0.62, spec=0.38, metal=0.34, sheen=0.0, sheen_rough=0.25)}
RECIPE = "nuno_usu"


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p):
    r = BLACK_RECIPES[RECIPE]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r["metal"]
    p.inputs["Sheen Weight"].default_value = r["sheen"]
    p.inputs["Sheen Roughness"].default_value = r["sheen_rough"]
    p.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)


mat_body, bp_ = principled("nuno")
apply_black(bp_)
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


mat_glow = glow_material("tama")


# ---------- 造形（bmesh・実寸）----------
def frames(pts):
    """回転最小フレーム（parallel transport）。ねじれを出さない"""
    n = len(pts)
    T = []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        v = Vector(b) - Vector(a)
        T.append(v.normalized())
    up = Vector((0.0, 1.0, 0.0))
    u = (up - T[0] * up.dot(T[0]))
    if u.length < 1e-6:
        u = Vector((1.0, 0.0, 0.0)) - T[0] * T[0].x
    u.normalize()
    U = [u]
    for i in range(1, n):
        prev = U[-1]
        w = prev - T[i] * prev.dot(T[i])
        if w.length < 1e-9:
            w = Vector((0.0, 1.0, 0.0)) - T[i] * T[i].y
        U.append(w.normalized())
    return T, U


def tube_verts(pts):
    """紐1本ぶんの頂点（リング順）。トポロジは点数で決まるので K が変わっても同じ"""
    T, U = frames(pts)
    vs = []
    for i, p in enumerate(pts):
        V = T[i].cross(U[i]).normalized()
        for k in range(NR):
            a = 2.0 * math.pi * k / NR
            o = U[i] * (CR * math.cos(a)) + V * (CR * math.sin(a))
            vs.append((p[0] + o.x, p[1] + o.y, p[2] + o.z))
    return vs


def all_verts(s_):
    vs = []
    for j in range(NCORD):
        vs.extend(tube_verts(cord_points(s_, j)))
    return vs


def build_cords():
    """basis＝開（s=0）。faces は点数だけで決まるので s が変わってもトポロジは同じ"""
    npts = NT + (NK + 1) + NT
    bm = bmesh.new()
    vs = all_verts(0.0)
    bvs = [bm.verts.new(v) for v in vs]
    bm.verts.ensure_lookup_table()
    for j in range(NCORD):
        base = j * npts * NR
        for i in range(npts - 1):
            for k in range(NR):
                k2 = (k + 1) % NR
                bm.faces.new((bvs[base + i * NR + k], bvs[base + i * NR + k2],
                              bvs[base + (i + 1) * NR + k2], bvs[base + (i + 1) * NR + k]))
        bm.faces.new([bvs[base + k] for k in range(NR - 1, -1, -1)])
        bm.faces.new([bvs[base + (npts - 1) * NR + k] for k in range(NR)])
    me = bpy.data.meshes.new("mizuhiki")
    bm.to_mesh(me); bm.free()
    return me


LENS_NAA, LENS_NBB = 168, 72


def lens_verts(s_):
    """受け皿の頂点（リング順）。トポロジは s_ に依らない＝シェイプキーに乗る"""
    vs = []
    for ib in range(LENS_NBB + 1):
        w = (ib / LENS_NBB) ** 0.85
        for ia in range(LENS_NAA):
            a_raw = 2.0 * math.pi * ia / LENS_NAA
            r = w * lens_edge(a_raw, s_)
            a = a_raw + ROT0
            yy = LENS_Y - LENS_DOME * (1.0 - w * w)
            vs.append((r * math.cos(a), yy, r * math.sin(a)))
    return vs


def build_lens():
    """受け皿＝真ん中の光。縁は結びの内側の包絡線に沿うので、輪郭は常に紐の下（#76③）。
       UV の X に E を入れる。E は**開口に対する比**なので、シェイプキーで縮んでも模様は保たれる"""
    NAA, NBB = LENS_NAA, LENS_NBB
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    vs = lens_verts(0.0)
    rows = [[bm.verts.new(vs[ib * NAA + ia]) for ia in range(NAA)] for ib in range(NBB + 1)]
    ev = [[e_lens(((ib / NBB) ** 0.85) * lens_edge(2.0 * math.pi * ia / NAA, 0.0))
           for ia in range(NAA)] for ib in range(NBB + 1)]
    for ib in range(1, NBB):
        for ia in range(NAA):
            ja = (ia + 1) % NAA
            f = bm.faces.new((rows[ib][ia], rows[ib][ja], rows[ib + 1][ja], rows[ib + 1][ia]))
            for lp in f.loops:
                if lp.vert is rows[ib][ia]:
                    e = ev[ib][ia]
                elif lp.vert is rows[ib][ja]:
                    e = ev[ib][ja]
                elif lp.vert is rows[ib + 1][ja]:
                    e = ev[ib + 1][ja]
                else:
                    e = ev[ib + 1][ia]
                lp[uvl].uv = (e, 0.5)
    for ia in range(NAA):
        ja = (ia + 1) % NAA
        f = bm.faces.new((rows[0][ia], rows[1][ja], rows[1][ia]))
        for lp in f.loops:
            lp[uvl].uv = (ev[0][ia] if lp.vert is rows[0][ia]
                          else (ev[1][ja] if lp.vert is rows[1][ja] else ev[1][ia]), 0.5)
    me = bpy.data.meshes.new("tama")
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth=0.9):
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


cords = link(build_cords(), "mizuhiki", mat_body)
cords.location = KNOT_C
cords.rotation_mode = 'XYZ'
lens = link(build_lens(), "tama", mat_glow, smooth=1.2)
lens.location = KNOT_C
lens.rotation_mode = 'XYZ'

# シェイプキー（basis＝締まり／key＝ゆるみ）。トポロジは同じ
cords.shape_key_add(name="Basis", from_mix=False)
sk = cords.shape_key_add(name="shut", from_mix=False)
for i, v in enumerate(all_verts(1.0)):
    sk.data[i].co = v
sk.value = 0.0
lens.shape_key_add(name="Basis", from_mix=False)
skl = lens.shape_key_add(name="shut", from_mix=False)
for i, v in enumerate(lens_verts(1.0)):
    skl.data[i].co = v
skl.value = 0.0

parts = [cords, lens]

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    for ob in parts:
        ob.location = (KNOT_C[0], KNOT_C[1], KNOT_C[2] + bob(t))
        ob.rotation_euler = (RX_TILT, ry(t), RZ_TURN)
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_euler", frame=f + 1)
    sk.value = skl.value = morph(t)
    sk.keyframe_insert("value", frame=f + 1)
    skl.keyframe_insert("value", frame=f + 1)

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
        caption("MIDDLE STUDY 072 — MIZUHIKI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, KNOT_C[2])
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：結び目は輪と輪のあいだが全部抜けている＝面光源が素通しで写る
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。結び目の下、床すれすれに置いて床帯へ届かせる
for sx, sy, sz, w in ((-0.70, 3.2, 0.26, LIME_W), (0.30, 6.0, 0.26, LIME_W),
                      (1.10, 10.0, 0.26, LIME_W)):
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
cam.data.dof.focus_distance = math.hypot(8.3, KNOT_C[2] - LOOK_Z)
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
    gx0 = gy0 = 9.0; gx1 = gy1 = -9.0
    for ob in parts:
        ev = ob.evaluated_get(dg)
        xs, ys = [], []
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
        print(">> %-10s x %.3f..%.3f  y %.3f..%.3f" % (ob.name, min(xs), max(xs),
                                                       min(ys), max(ys)))
        if ob is cords:
            gx0, gx1 = min(xs), max(xs); gy0, gy1 = min(ys), max(ys)
    print(">> 紐 bbox x %.3f..%.3f  y %.3f..%.3f  → 長辺 %.1f%%"
          % (gx0, gx1, gy0, gy1, max(gx1 - gx0, gy1 - gy0) * 100))
    print(">> 枠まで 左%.3f 右%.3f 上%.3f 下%.3f（すべて正なら edge=0）"
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_072.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("tama_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    lens.data.materials[0] = m_em
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
