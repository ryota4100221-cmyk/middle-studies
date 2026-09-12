# =============================================================
# MIDDLE STUDY 079 — HORAGAI（法螺貝 / the road inside the coil）
#
#   光の型＝内包（#53：78作で9作）  構図の型＝寄り（#57：78作で6作）
#   ドメイン＝修験・法具／法螺貝（シリーズ未踏）
#
# 山伏の法螺貝。頂を切り落として吹口を挿し、唇を当てて吹く。
# けれど音は唇にも、殻の外にもない。息は**巻いた殻のなかの道**を何巡りもして、
# それからやっと、広い口へ出てくる。**鳴っているのは、巻かれた真ん中だ。**
# その道は、貝を割るまで誰にも見えない。だから寄って、口のなかだけを見せる。
# 貝はその場で回る。回るのは殻で、真ん中は動かない。
#
# 🔴 型の組み合わせ（#87①：works.json は成功の台帳であって可否の台帳ではない）
#    内包×寄り は 78作で 0。**PITFALLS を「内包」「寄り」で grep して可否を確かめた**：
#      ・#76② に「内包×寄りも成立はするが、開口の面積で頭打ちになる」＝**成立する**（066 は halo を
#        戻す目的だったので芯を採った）。今日は halo は 75%（🔴ではない）＝面積の頭打ちは争点でない。
#      ・#87① の一般則「中央以外の構図を採る日は、光をシルエットの内側に閉じ込められる型から選ぶ」
#        ＝内包はその筆頭（背光が寄り／群／対／端寄せの4方向で潰れているのはこの逆）。
#      ・潰れている組み合わせ：背光×寄り(#67⑤)・稜線×寄り(#76②)。内包は該当しない。
#    直近3作の構図は 端寄せ／対／全身、直近5作の光は 内包(073)…は5作前でちょうど外れる（#53 が許可）。
#
# 🔴 機構＝**その場で回す（巻きの道が回って見える）**。
#    貝を巻きの軸まわりに φ(t)=Δφ(1+cos2πt)/2 で 62°→0°→62° と返す（cos＝厳密に閉じる）。
#    口（開口）は巻きの接線方向を向いているので、**回すほど口はカメラから逃げ、返すほど正対する**。
#    光の量は発光の値を1つも動かさずに**幾何だけ**で作る（#69②／#70④）。
#    🔴 全周回転にはしない——#77⑨：口が一周すると光が出ている時間がループの23%しか無い。
#    ＋ 揺り δ(t)=8°·sin2πt（世界Y）／ζ(t)=6°·sin2πt（世界Z）／bob 0.055·sin2πt。
#    いずれも t=0.5 で 0 ＝ hero は設計どおりの姿。位置キーと回転キーだけ＝glb にそのまま乗る。
#
# 🔴 光は「殻の内側に塗る」のではなく「殻の中に置く」（#77①）。
#    開口から DU_LIGHT ぶん奥に**浅い凹面ディッシュ**を、道の接線に正対させて据える（#77②：
#    球にすると器を倒したとき極が喉に隠れて消える）。奥行き方向の勾配は絞りの中では見えない。
#    口の広さは意匠でなく光学（#77④：d·tanθ < R_MOUTH → θ<47.7°まで芯が見える）。
#
# 造形＝対数螺旋のチューブ1本（boolean 不使用）。
#    中心 C(u)=(rc cos u, rc sin u, -CC(rc-rc0))・rc(u)=RC_END·e^{K(u-U_MAX)}、
#    断面は**縦長の超楕円**で、軸方向の半径 B_AX は「隣の巻きが接する」条件から決まる量＝意匠ではない：
#        B_AX = CC·(G−1)/(1+G) × OVER       ← 1巻きぶんの軸方向の間隔 ÷ 2半径の和
#    径方向の半径は A_RA = B_AX / ASPECT（殻口の縦横比）。
#    肌＝肩の瘤（8個/巻き）と螺旋肋（周方向 7本）を**解析的に実ジオメトリで**入れる（#52）。
#    🔴 MATERIALS.md の add_relief（SUBSURF 3＋DISPLACE）は使わない——この面は既に 420×96 で
#    刻んであるので SUBSURF は要らず、掛けると 64倍で anim が終わらない（掟5）。DISPLACE だけ当てる。
#    黒の質感＝**touki 陶**（貝殻は石灰質でざらつく）。#77⑩ にならい disp は 0.0032/0.20。
#    🔴 陶（rough 0.58）を選んだのは #89① の回避でもある——漆の平らな面はライムの点光源を面ごと映す。
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
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 150.0                      # #58③：随伴のライム光源（発光体の外）

# --- 貝（実物：法螺貝 全長 30〜40cm・殻高 ÷ 殻幅 ≈ 1.8・殻口は殻高の 55%。比だけ借りる＝#50）---
# 🔴🔴 5周かけて分かった骨格の話（→ LOG／PITFALLS）
#    1〜5周目は G=1.16〜1.20（1巻きで16〜20%しか太らない）で組んでいた。
#    すると巻きが**どれも同じ太さの輪**になり、hero では例外なく「黒いゴムホース／ソフトクリーム」に読める。
#    断面を超楕円にしても肋を彫っても直らなかった＝**肌ではなく比の問題**だった。
#    実物から逆算すると、体層（いちばん大きい巻き）が殻高の 58% を占める ⇔ 巻きの高さは等比数列で
#        H = h_body · G/(G−1)   →   h_body/H = (G−1)/G = 0.58   →   **G ≈ 2.4**
#    ＝法螺貝は「1巻きで倍以上に育つ貝」。巻き数も 9.5 ではなく 4〜5 しかない。
#    そして断面は円ではなく**縦長**（殻口が縦 2.1 : 横 1）＝これで細い円錐と太い体層が両立する。
G_TURN = 1.60                       # 1巻きあたりの成長率
                                    # 🔴 6周目に 2.05 まで振ったら、今度は塔が消えて**蓄音機のラッパ**になった。
                                    #    体層の比 (G−1)/G は 1.16→0.14 / 2.05→0.51 / **1.60→0.38** が当たり
N_TURN = 6.0                        # 巻き数
CC = 5.59                            # 円錐の伸び（z の下がり ÷ 半径の増え）
RC_END = 0.52                       # 口の中心半径
WALL = 0.100                        # 肉厚（実物の法螺貝の唇も厚い）
OVER = 1.06                         # 巻きの重なり（1.00＝接するだけ。縫合線を溝でなく筋にする）
                                    # 🔴🔴 重なりは意匠で決められない——**ひとつ前の巻きが、いまの巻きの
                                    #    内腔（lumen）へ何本も刺さる**。口から奥を覗くと、その侵入面が
                                    #    **鋸歯の裂け目**として見える（10周目の hero）。boolean が無いので消せない。
                                    #    条件：侵入量 (OVER−1)·(b+bG) < 2·WALL ＝ 肉厚で飲み込めること。
                                    #    だから OVER を下げるか肉厚を上げる。ここは両方（1.12→1.06／0.045→0.10）
ASPECT = 1.60                       # 断面の縦横比（殻口の縦 ÷ 横）
K = math.log(G_TURN) / (2.0 * math.pi)
U_MAX = 2.0 * math.pi * N_TURN
B_AX = CC * (G_TURN - 1.0) / (1.0 + G_TURN) * OVER    # 断面の**軸方向**半径（隣の巻きと接する条件）
A_RA = B_AX / ASPECT                                  # 断面の**径方向**半径
SHAPE_N = 3.1                       # 断面の超楕円の角（2＝楕円／大きいほど肩が立つ）
NOD_A, NOD_V, NOD_S, NOD_N = 0.18, 0.30, 0.28, 9      # 肩の瘤（振幅・位置v・幅・個/巻き）
CORD_A, CORD_N = 0.045, 9           # 螺旋肋（周方向の本数）
FL_A, FL_U = 0.17, 1.50             # 外唇の朝顔（振幅・効く u の幅）
COL_A = 0.04                        # 軸唇（内側）の立ち上がり
                                    # 🔴 0.16 では口の内側（v≈π）が凹み、**ひとつ前の巻きがそこを突き抜けて**
                                    #    鋸歯の裂け目が出た。内側は触らないのが正解（実物の軸唇は滑らかな胼胝）
NU, NV = 460, 112
MOUTH_L, MOUTH_R = 0.115, 0.62      # 吹口（歌口）の長さ・半径比。hero では枠の外だが glb では回せる

# --- 据え付け（構図＝寄り）--------------------------------------
ALPHA = math.radians(56.0)          # 巻きの軸の傾き（頂が左下・口が右上＝吹いて掲げた向き）
                                    # 🔴 26° では**横長の帯**になり縦4:5の判に合わない（高さ37%）。
                                    #    長い物を縦長の判に入れるときは、傾きが占有そのものを決める
AX0 = (math.cos(ALPHA) , -0.090, math.sin(ALPHA))     # 頂→口の向き（正規化は下で）
P_APER = (1.00, -0.15, 2.85)        # 口の中心を**ここに固定する**（真ん中は動かない）
DPHI = math.radians(56.0)           # 巻き軸まわりの返し
DTILT, ZYAW, BOB = math.radians(8.0), math.radians(6.0), 0.055
STILL_FRAME = 61                    # t=0.5 ＝ 口が正対する（光が最大）

# --- 光（殻の中に置く浅いディッシュ）-----------------------------
DU_LIGHT = 0.56                     # 口から奥へ（巻き角で）
DISH_OVER = 0.030                   # 皿の縁を壁の下へ潜らせる量（#82②）
R_E_K = 0.62                        # 光が 0 に落ちる絶対半径 ÷ 道の**軸方向**の内寸
                                    # 🔴 2周目 0.76＋広い勾配（GL 0.60）は**緑の卵**になった（#82②／#88④）。
                                    #    #77① の答えは「小さな発光体＋そのまわりの暗がり」——
                                    #    皿を口いっぱいに広げると暗がりが消え、球の陰影に読める
H_DISH_K = 0.30                     # 凹みの深さ ÷ ディッシュ半径
GL, HU, HOT_A, E_FLOOR = 0.50, 0.17, 0.46, 0.010
E_PEAK = 1.0 + HOT_A
ES_CORE = 5.6
WHITE_FROM, WHITE_TO = 0.40, 0.66
K_MIX = 16.0
ND, NA = 34, 96                     # ディッシュの刻み


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def _n(v):
    m = math.sqrt(sum(c * c for c in v))
    return tuple(c / m for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _add(*vs):
    return tuple(sum(c) for c in zip(*vs))


def _mul(v, s):
    return tuple(c * s for c in v)


AX0 = _n(AX0)


def smooth(e0, e1, x):
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def rc(u):
    return RC_END * math.exp(K * (u - U_MAX))


RC0 = rc(0.0)
A_END = A_RA * RC_END               # 口の**径方向**半径
Z_END = B_AX * RC_END               # 口の**軸方向**半径
R_MOUTH = A_END - WALL              # 🔴 口は円ではなく縦長の楕円。遮蔽は楕円で測る
Z_MOUTH = Z_END - WALL
ER_END = (math.cos(U_MAX), math.sin(U_MAX), 0.0)      # 口の面内：径方向
EZ_END = (0.0, 0.0, 1.0)                              # 口の面内：軸方向
N_APER = (-math.sin(U_MAX), math.cos(U_MAX), 0.0)     # 口の面の法線（＝生成円の張る平面）
SHELL_L = CC * (RC_END - RC0)        # 頂から口までの軸長


def center(u):
    r = rc(u)
    return (r * math.cos(u), r * math.sin(u), -CC * (r - RC0))


def tangent(u):
    r = rc(u)
    dr = K * r
    return _n((dr * math.cos(u) - r * math.sin(u), dr * math.sin(u) + r * math.cos(u), -CC * dr))


def shape(v):
    """断面の形（正規化）。円ではなく**縦長の超楕円**。
       貝の巻きは「肩の稜（carina）を持つ縦長の段」であって、丸いチューブではない。
       v=0 が外向き・v=π/2 が頂の側。k は v=0 と v=±π/2 で 1、角（±45°付近）で 1 を超える。"""
    ca, sa = abs(math.cos(v)), abs(math.sin(v))
    return (ca ** SHAPE_N + sa ** SHAPE_N) ** (-1.0 / SHAPE_N)


def relief(u, v):
    """肌（肩の瘤・螺旋肋・外唇の朝顔・軸唇）を**実ジオメトリで**足す倍率（#52：黒に Bump は効かない）"""
    # 🔴 瘤も口の手前で消す。残すと**外唇の縁が波打って「ゴムの口」**になる（実物も唇の縁は滑らか）
    nod = (NOD_A * math.exp(-((v - NOD_V) / NOD_S) ** 2) * (0.5 + 0.5 * math.cos(NOD_N * u))
           * (1.0 - smooth(U_MAX - 1.5, U_MAX - 0.3, u)))
    # 🔴 肋は殻の**外**の彫り。口へ近づくにつれて消す——消さないと内壁に縦溝が残り、
    #    奥の光を見たときに**殻口が多角形のノズル**に見える（1周目の犯人）。実物の貝の内側も滑らか。
    cord = CORD_A * math.cos(CORD_N * v) * (1.0 - smooth(U_MAX - 2.2, U_MAX - 0.4, u))
    sa = smooth(U_MAX - FL_U, U_MAX, u)
    fl = col = 0.0
    if sa > 0.0:
        # 🔴 朝顔は**下外側**へ振る。v-0.15 で開くと頂の側（v≈π/2）まで太り、
        #    最後の巻きが**ひとつ前の巻きを突き抜けて**口の内側に鋸歯の折れ目が出る（9周目の hero）
        c = math.cos(v + 0.34)
        if c > 0.0:
            fl = FL_A * sa ** 1.6 * c ** 1.5                  # 外唇の朝顔
        cv = math.cos(v)
        if cv < 0.0:
            col = -COL_A * sa * cv * cv                       # 軸唇（内側）を立てる
    return 1.0 + nod + cord + fl + col


def half_ra(u, v):
    return A_RA * rc(u) * shape(v) * relief(u, v)


def half_az(u, v):
    return B_AX * rc(u) * shape(v) * relief(u, v)


def surf(u, v):
    cx, cy, cz = center(u)
    hr = half_ra(u, v) * math.cos(v)
    hz = half_az(u, v) * math.sin(v)
    return (cx + hr * math.cos(u), cy + hr * math.sin(u), cz + hz)


# --- 口（開口）：u=U_MAX の生成円。面の法線＝接線 ------------------
C_END = center(U_MAX)
N_END = tangent(U_MAX)

# --- ディッシュ（光）----------------------------------------------
U_LIGHT = U_MAX - DU_LIGHT
C_DISH = center(U_LIGHT)
N_DISH = tangent(U_LIGHT)
_t1 = _n(_cross(N_DISH, (0.0, 0.0, 1.0)))      # 道の**径方向**
_t2 = _n(_cross(N_DISH, _t1))                  # 道の**軸方向**
# 🔴🔴 #82②：発光体の縁は「被写体の内側の包絡線」に一致させる。
#    半径固定の円盤を奥に置くと、E が落ちた外周が**不透明な黒い円盤**として殻の中に残り、
#    明るい芯だけが浮いて「黒い殻に入った光る卵」になる（8周目の hero がまさにこれ）。
#    **どの指標にも出ない**——ライム面積も #40⑥ も std も halo も全部合格していた。
#    皿の輪郭を道の断面（縦長の楕円）そのものにして、縁を壁の下 DISH_OVER だけ潜らせる。
RA_DISH = A_RA * rc(U_LIGHT) - WALL + DISH_OVER       # 皿の径方向の半径
RZ_DISH = B_AX * rc(U_LIGHT) - WALL + DISH_OVER       # 皿の軸方向の半径
R_E = R_E_K * (B_AX * rc(U_LIGHT) - WALL)             # 光が 0 になる**絶対**半径（等値線は円＝#82③）
H_DISH = H_DISH_K * RA_DISH
D_DEPTH = math.sqrt(sum((a - b) ** 2 for a, b in zip(C_DISH, C_END)))   # 口までの距離


def dish_edge(al):
    """皿の縁（道の断面の楕円）までの距離"""
    ca, sa = math.cos(al) / RA_DISH, math.sin(al) / RZ_DISH
    return 1.0 / math.sqrt(ca * ca + sa * sa)


def e_of(rho_n):
    raw = math.exp(-((rho_n / GL) ** 2)) + HOT_A * math.exp(-((rho_n / HU) ** 2))
    return max(0.0, (raw / E_PEAK - E_FLOOR) / (1.0 - E_FLOOR))


def dish_point(w, al):
    """w∈[0,1] が縁まで。凹面（芯が奥・縁が口側）。#77②：ディッシュは θ が変わっても cosθ で痩せるだけ"""
    rho = w * dish_edge(al)
    off = -H_DISH * (1.0 - w * w) ** 1.2
    return _add(C_DISH, _mul(_t1, rho * math.cos(al)), _mul(_t2, rho * math.sin(al)),
                _mul(N_DISH, off))


def dish_normal(w, al):
    """面の法線（N_DISH 側を向く）"""
    if w < 1e-6:
        return N_DISH
    e = dish_edge(al)
    dz = -H_DISH * 1.2 * (1.0 - w * w) ** 0.2 * (-2.0 * w) / e
    rad = _n(_add(_mul(_t1, math.cos(al)), _mul(_t2, math.sin(al))))
    return _n(_add(_mul(N_DISH, 1.0), _mul(rad, -dz)))


# --- 動き --------------------------------------------------------
def phi(t):
    return DPHI * 0.5 * (1.0 + math.cos(2.0 * math.pi * t))


def rock(t):
    s = math.sin(2.0 * math.pi * t)
    return DTILT * s, ZYAW * s, BOB * s


def _rz(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2])


def _ry(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c)


def _rzw(v, a):
    return _rz(v, a)


# M0 = [B1 B2 -AX0]：φ=0・揺り0 で「口の法線がカメラを向く」ように組む（導出は冒頭のコメント）
N_AIM = _n(_add(N_DISH, N_END))          # 皿と口の二等分線（上記）


def _basis():
    d = _n(_add(CAM_LOC, _mul(P_APER, -1.0)))
    d = _n(_add(d, _mul(AX0, -_dot(d, AX0))))          # AX0 に直交する成分
    # 🔴 3周目：e を AX0×d で採ると (B1,B2,-AX0) が**左手系＝行列式 −1（鏡映）**になる。
    #    自作の probe は列をそのまま使うので絵が出るが、Blender は
    #    `Matrix.to_quaternion()` を通すので鏡映を表せず、**貝が画面の外に飛ぶ**。
    #    数値も例外も出ない（bbox が負になって初めて分かった）。d×e = B3 になる向きで採る。
    e = _n(_cross(d, AX0))
    # 🔴 揃えるのは「口の法線」ではなく**ディッシュの法線**。
    #    ディッシュは口より DU_LIGHT ぶん手前の巻き角にあるので、口を正対させると
    #    光の面は 35.5° 横を向き、**hero が光の最大にならない**（1周目の probe で t=0.25 の方が明るかった）。
    #    条件：M0·N_DISH の e 成分を 0 にする → ψ = atan2(-Ny, Nx)
    #    🔴 2周目：ディッシュだけを正対させると、**口の法線が 35.5° 横を向く**（道が曲がっている
    #    ぶん、皿の向きと口の向きは DU_LIGHT ぶんズレる）。視線が口へ 67° の斜めで入るので
    #    「皿は正面・でも壁で全部隠れる」になり、#40⑥ が 0.000＝#77③ の穴に落ちた。
    #    **皿の法線と口の法線の二等分線**をカメラへ向けるのが解（どちらも半分だけ譲る）。
    psi = math.atan2(-N_AIM[1], N_AIM[0])
    cp, sp = math.cos(psi), math.sin(psi)
    B1 = _add(_mul(d, cp), _mul(e, sp))
    B2 = _add(_mul(d, -sp), _mul(e, cp))
    return B1, B2, _mul(AX0, -1.0)


B1, B2, B3 = _basis()


def rot(t):
    """ローカル→世界の回転（列ベクトル3本を返す）"""
    tl, zy, _ = rock(t)
    f = phi(t)
    cf, sf = math.cos(f), math.sin(f)
    # Rz(φ) の列 → M0 で世界へ → 世界Y・世界Z で揺る
    cols = [_add(_mul(B1, cf), _mul(B2, sf)),
            _add(_mul(B1, -sf), _mul(B2, cf)),
            B3]
    return [_rzw(_ry(c, tl), zy) for c in cols]


def to_world(p, t):
    c = rot(t)
    _, _, bz = rock(t)
    base = _add(_mul(c[0], p[0]), _mul(c[1], p[1]), _mul(c[2], p[2]))
    ce = _add(_mul(c[0], C_END[0]), _mul(c[1], C_END[1]), _mul(c[2], C_END[2]))
    return _add(base, (P_APER[0] - ce[0], P_APER[1] - ce[1], P_APER[2] + bz - ce[2]))


def dir_world(v, t):
    c = rot(t)
    return _add(_mul(c[0], v[0]), _mul(c[1], v[1]), _mul(c[2], v[2]))


def _screen(v):
    s = 8.3 / (v[1] - CAM_LOC[1])
    return (0.5 + (v[0] - AIM_X) * s / FRAME_W, 0.5 + (v[2] - LOOK_Z) * s / FRAME_H)


# --- 幾何プローブ（#40⑥ を幾何で積分する。Blender を起動しない）---------
def _dish_samples():
    """(局所位置, 法線, E, dA)"""
    out = []
    for k in range(NA):
        al = 2.0 * math.pi * (k + 0.5) / NA
        ed = dish_edge(al)
        for i in range(ND):
            w0, w1 = i / ND, (i + 1) / ND
            wm = 0.5 * (w0 + w1)
            e = e_of(wm * ed / R_E)
            if e <= 0.0:
                continue
            dA = math.pi * (w1 * w1 - w0 * w0) * ed * ed / NA
            out.append((dish_point(wm, al), dish_normal(wm, al), e, dA))
    return out


DISH = _dish_samples()


def flux(t):
    """口から**見えている**発光（cosθ つき）と、全発光。#77③：比だけでなく絶対量も出す"""
    vis = tot = 0.0
    for p, n, e, dA in DISH:
        pw = to_world(p, t)
        nw = dir_world(n, t)
        w = _n(_add(CAM_LOC, _mul(pw, -1.0)))
        cs = _dot(nw, w)
        if cs <= 0.0:
            continue
        f = e * cs * dA
        tot += f
        # 口を通るか（#77④ の一般形）。🔴 口は円でなく**縦長の楕円**なので楕円で測る
        wl = _wlocal(w, t)
        den = _dot(wl, N_APER)
        if den <= 1e-9:
            continue
        s = _dot(_add(C_END, _mul(p, -1.0)), N_APER) / den
        if s <= 0.0:
            continue
        dq = _add(p, _mul(wl, s), _mul(C_END, -1.0))
        if (_dot(dq, ER_END) / R_MOUTH) ** 2 + (_dot(dq, EZ_END) / Z_MOUTH) ** 2 < 1.0:
            vis += f
    return vis, tot


def _cols(t):
    return rot(t)


def _wlocal(w, t):
    c = rot(t)
    return (_dot(w, c[0]), _dot(w, c[1]), _dot(w, c[2]))      # 直交行列の転置＝逆


def shell_box(t):
    xs, ys = [], []
    for iu in range(0, 61):
        u = U_MAX * iu / 60.0
        for iv in range(24):
            v = 2.0 * math.pi * iv / 24
            sx, sy = _screen(to_world(surf(u, v), t))
            xs.append(sx); ys.append(sy)
    return min(xs), max(xs), min(ys), max(ys)


if "--probe-only" in sys.argv:
    print("── 079 HORAGAI 幾何プローブ")
    _w = 2.0 * (RC_END + A_END)
    _h = SHELL_L + Z_END
    print("   G %.2f × %.1f巻き  断面 径 %.3f × 軸 %.3f（縦横比 %.2f）  軸長 %.3f"
          % (G_TURN, N_TURN, A_RA, B_AX, ASPECT, SHELL_L))
    print("   外形 幅 %.3f × 高 %.3f（H/W %.2f）  体層が殻高の %.0f%%  瘤 %d/巻き  肋 %d本"
          % (_w, _h, _h / _w, 100.0 * (2 * Z_END) / _h, NOD_N, CORD_N))
    print("   皿＝道の断面 %.3f×%.3f（壁の下へ %.3f 潜る）  光が 0 になる半径 %.3f"
          % (RA_DISH, RZ_DISH, DISH_OVER, R_E))
    print("   口までの距離 %.3f  口の内寸 %.3f×%.3f" % (D_DEPTH, 2 * R_MOUTH, 2 * Z_MOUTH))
    _b = B_AX * RC_END
    _intr = (1.0 - 1.0 / OVER) * (_b + _b * G_TURN)
    print("   🔴 前の巻きの内腔への侵入 %.3f ＜ 2·肉厚 %.3f  %s"
          % (_intr, 2 * WALL, "OK" if _intr < 2 * WALL else "🔴 口の奥に鋸歯が出る"))
    print("   #77④ 芯が見える限界 θ < %.1f°（返しは %.0f°）"
          % (math.degrees(math.atan(R_MOUTH / D_DEPTH)), math.degrees(DPHI)))
    ts = [i / 24 for i in range(24)]
    fs = [flux(t) for t in ts]
    vs = [a for a, _ in fs]
    print("   #40⑥ 見える光 min/max = %.3f（合格 0.75以下）  max/min = %.2f"
          % (min(vs) / max(max(vs), 1e-12), max(vs) / max(min(vs), 1e-12)))
    vt = flux(0.5)
    print("   🔴 #77③ 絶対量：hero で 見える光 %.4f ÷ 全発光 %.4f = %.1f%%"
          % (vt[0], vt[1], 100.0 * vt[0] / max(vt[1], 1e-12)))
    thr = 0.25 * max(vs)
    print("   光が出ている時間 %.0f%%（#77⑨：42%%以上）"
          % (100.0 * sum(1 for v in vs if v > thr) / len(vs)))
    for t in (0.0, 0.25, 0.5, 0.75):
        a, b = flux(t)
        print("   t=%.2f  φ=%4.1f°  見える光 %.4f（%.0f%%）" % (t, math.degrees(phi(t)), a,
                                                          100.0 * a / max(b, 1e-12)))
    x0, x1, y0, y1 = shell_box(0.5)
    sw = (min(1.0, x1) - max(0.0, x0)) * 100
    sh = (min(1.0, y1) - max(0.20, y0)) * 100
    edge = (x0 < 0.005) + (x1 > 0.995) + (y1 > 0.995)
    print("   hero 外形 screen x %.3f..%.3f  y %.3f..%.3f" % (x0, x1, y0, y1))
    print("   🔴 長辺 %.1f%%（寄り＝78%%以上）  幅 %.1f%%  高さ %.1f%%  枠への接触 %d辺（寄り＝1以上）"
          % (max(sw, sh), sw, sh, edge))
    ap = _screen(to_world(C_END, 0.5))
    print("   口の中心 screen (%.2f, %.2f)  ＝ 画面の右 %.0f%% / 上 %.0f%%"
          % (ap[0], ap[1], ap[0] * 100, ap[1] * 100))
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

# ---------- マテリアル（MATERIALS.md の実測レシピ・#52） ----------
BLACK_RECIPES = {
    "touki": dict(rough=0.58, spec=0.26, disp=0.0060, dsize=0.11),   # #77⑩ の回転体向け値を貝の寸法で調整
}


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def apply_black(p):
    r = BLACK_RECIPES["touki"]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]       # 🔴 0.10 を割らない（#45）


mat_shell, sp_ = principled("kai_touki")
apply_black(sp_)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（ローカル座標のまま。object.scale 不使用＝#15）----------
def shell_mesh():
    """対数螺旋のチューブ。面の巻きは ∂u×∂v＝+er（外向き）"""
    bm = bmesh.new()
    rows = []
    for iu in range(NU + 1):
        u = U_MAX * iu / NU
        rows.append([bm.verts.new(surf(u, 2.0 * math.pi * iv / NV)) for iv in range(NV)])
    for iu in range(NU):
        for iv in range(NV):
            j = (iv + 1) % NV
            bm.faces.new((rows[iu][iv], rows[iu + 1][iv], rows[iu + 1][j], rows[iu][j]))
    # 頂（u=0）は吹口を挿すために切り落とされている＝平らに塞ぐ
    cap = bm.verts.new(center(0.0))
    for iv in range(NV):
        j = (iv + 1) % NV
        bm.faces.new((cap, rows[0][j], rows[0][iv]))
    me = bpy.data.meshes.new("m_kai"); bm.to_mesh(me); bm.free()
    return me


def mouthpiece_mesh():
    """歌口（吹口）。頂の切り口に挿した短い筒＋座。hero では枠の外だが glb では回せる"""
    t0 = tangent(0.0)
    c0 = center(0.0)
    e1 = _n(_cross(t0, (0.0, 0.0, 1.0)))
    e2 = _n(_cross(t0, e1))
    r0 = A_RA * RC0 * MOUTH_R
    prof = [(-0.012, 0.0), (-0.012, r0 * 1.35), (0.010, r0 * 1.35),
            (0.010, r0), (MOUTH_L, r0 * 0.88), (MOUTH_L, r0 * 0.60), (MOUTH_L, 0.0)]
    bm = bmesh.new()
    na = 32
    rows = []
    for s, r in prof:
        if r <= 1e-9:
            v = bm.verts.new(_add(c0, _mul(t0, -s)))
            rows.append([v] * na)
        else:
            row = []
            for k in range(na):
                a = 2.0 * math.pi * k / na
                row.append(bm.verts.new(_add(c0, _mul(t0, -s),
                                             _mul(e1, r * math.cos(a)), _mul(e2, r * math.sin(a)))))
            rows.append(row)
    for j in range(len(rows) - 1):
        for k in range(na):
            k2 = (k + 1) % na
            q = [rows[j][k], rows[j][k2], rows[j + 1][k2], rows[j + 1][k]]
            q2 = []
            for x in q:
                if x not in q2:
                    q2.append(x)
            if len(q2) >= 3:
                try:
                    bm.faces.new(q2)
                except ValueError:
                    pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("m_utaguchi"); bm.to_mesh(me); bm.free()
    return me


def dish_mesh():
    """発光ディッシュ。UV の X に E を焼く。縁は E=0（発光板の縁を作らない・#49①）"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    cen = bm.verts.new(dish_point(0.0, 0.0))
    ALS = [2.0 * math.pi * k / NA for k in range(NA)]
    rings, evs = [], []
    for ib in range(1, ND + 1):
        w = (ib / ND) ** 0.9
        rings.append([bm.verts.new(dish_point(w, a)) for a in ALS])
        evs.append([e_of(w * dish_edge(a) / R_E) for a in ALS])   # 🔴 等値線は**絶対半径**の円（#82③）
    e0 = e_of(0.0)

    def setuv(f, m):
        for lp in f.loops:
            lp[uvl].uv = (m[lp.vert], 0.5)

    for k in range(NA):
        k2 = (k + 1) % NA
        f = bm.faces.new((cen, rings[0][k], rings[0][k2]))
        setuv(f, {cen: e0, rings[0][k]: evs[0][k], rings[0][k2]: evs[0][k2]})
    for ib in range(ND - 1):
        for k in range(NA):
            k2 = (k + 1) % NA
            f = bm.faces.new((rings[ib][k], rings[ib][k2], rings[ib + 1][k2], rings[ib + 1][k]))
            setuv(f, {rings[ib][k]: evs[ib][k], rings[ib][k2]: evs[ib][k2],
                      rings[ib + 1][k2]: evs[ib + 1][k2], rings[ib + 1][k]: evs[ib + 1][k]})
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.dot(Vector(N_DISH)) < 0.0:
            f.normal_flip()
    me = bpy.data.meshes.new("m_hikari"); bm.to_mesh(me); bm.free()
    return me


def glow_material(name):
    """E→0 側は黒へ戻す。芯だけ白へ抜く＝halo はこの「白→ライム」の帯でしか出ない（#81④）"""
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


mat_glow = glow_material("hikari")


def link(me, name, mat, smooth_ang=0.9):
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
    ob.select_set(False)
    return ob


ob_kai = link(shell_mesh(), "kai", mat_shell, 1.0)
ob_uta = link(mouthpiece_mesh(), "utaguchi", mat_shell, 0.9)
ob_hi = link(dish_mesh(), "hikari", mat_glow, 1.2)
parts = [ob_kai, ob_uta, ob_hi]

# --- 肉厚（口の唇が厚く見えるのは SOLIDIFY の rim。内壁＝道の壁もこれで生まれる）
sld = ob_kai.modifiers.new("atsumi", 'SOLIDIFY')
sld.thickness = WALL
sld.offset = -1.0
sld.use_rim = True
sld.use_rim_only = False

# --- 黒の肌（#52）。🔴 SUBSURF は掛けない＝面は既に 420×96 で刻んである（掟5）
_r = BLACK_RECIPES["touki"]
tex_relief = bpy.data.textures.new("relief_touki", 'CLOUDS')
tex_relief.noise_scale = _r["dsize"]
for o in (ob_kai, ob_uta):
    d = o.modifiers.new("hada", 'DISPLACE')
    d.texture = tex_relief; d.strength = _r["disp"]; d.mid_level = 0.5

# --- キーフレーム（毎フレーム打つ＝イージング不使用。回転は四元数）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev = None
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    c = rot(t)
    M = Matrix(((c[0][0], c[1][0], c[2][0], 0.0),
                (c[0][1], c[1][1], c[2][1], 0.0),
                (c[0][2], c[1][2], c[2][2], 0.0),
                (0.0, 0.0, 0.0, 1.0)))
    q = M.to_quaternion()
    if prev is not None and q.dot(prev) < 0.0:
        q.negate()
    prev = q.copy()
    ce = _add(_mul(c[0], C_END[0]), _mul(c[1], C_END[1]), _mul(c[2], C_END[2]))
    _, _, bz = rock(t)
    loc = (P_APER[0] - ce[0], P_APER[1] - ce[1], P_APER[2] + bz - ce[2])
    for ob in parts:
        ob.location = loc
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
        caption("MIDDLE STUDY 079 — HORAGAI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = P_APER
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①：寄りで枠が空く＝面光源が素通しで写る側に賭けない

limelamps = []
for sx, sy, sz, w in ((-0.85, 12.0, 0.30, LIME_W), (0.30, 24.0, 0.30, LIME_W),
                      (1.60, 38.0, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(AIM_X + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = w
    lp.data.shadow_soft_size = 2.60
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    lp.data.specular_factor = 0.0
    limelamps.append(lp)

# #76①：暗いライムが作れるのは黒の上だけ＝唇と肩の瘤をうしろからライムで舐める
# 🔴 陶（rough 0.58）なので #89① の「面ごと映る」は出ない前提。test で必ず目視する
rimlamps = []
for lx, ly, lz, w in ((P_APER[0] + 0.55, 0.95, P_APER[2] + 0.55, 210.0),
                      (P_APER[0] - 1.35, 0.85, P_APER[2] - 0.75, 180.0)):
    bpy.ops.object.light_add(type='POINT', location=(lx, ly, lz))
    lp = bpy.context.active_object
    lp.name = "rim_%+0.2f" % lx
    lp.data.energy = w
    lp.data.shadow_soft_size = 0.80
    lp.data.color = LIME[:3]
    lp.visible_camera = False
    rimlamps.append(lp)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
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

lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not ob_hi:
        lit_by_lime.objects.link(o)
for lp in limelamps:
    lp.light_linking.receiver_collection = lit_by_lime

lit_by_rim = bpy.data.collections.new("lit_by_rim")
bpy.context.scene.collection.children.link(lit_by_rim)
for o in (ob_kai, ob_uta):
    lit_by_rim.objects.link(o)
for lp in rimlamps:
    lp.light_linking.receiver_collection = lit_by_rim

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
    xs, ys = [], []
    for o in (ob_kai, ob_uta):
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sw = (min(1.0, x1) - max(0.0, x0)) * 100
    sh = (min(1.0, y1) - max(0.20, y0)) * 100
    edge = (x0 < 0.005) + (x1 > 0.995) + (y1 > 0.995)
    print(">> 貝の投影bbox  x %.3f..%.3f  y %.3f..%.3f" % (x0, x1, y0, y1))
    print(">> 🔴 長辺 %.1f%%（寄り＝78%%以上）  幅 %.1f%%  高さ %.1f%%  枠への接触 %d辺（寄り＝1以上）"
          % (max(sw, sh), sw, sh, edge))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_079.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("kai_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = 0.58
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    ob_kai.data.materials[0] = m_bk
    ob_uta.data.materials[0] = m_bk
    ob_hi.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = ob_kai
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
