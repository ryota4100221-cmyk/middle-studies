# =============================================================
# MIDDLE STUDY 062 — SUKETA（簀桁 / the mould of a papermaker）
#
# 黒い簀桁が、枠に収まらない大きさで宙にある。竹ひごを絹糸で編んだ簀（す）の向こうに、
# 汲んだばかりの紙料（しりょう）が溜まっていて、そこだけが ライム #A5E02E に光っている。
# **光っているのは紙ではない。まだ紙になっていない、水のほうだ。**
# 桁を揺すると竹ひごの影が光を横切り、簀が寝るほど隙間は閉じて、光は細る。
# 紙の縁——耳——は、どれだけ丁寧に漉いても真っ直ぐにならない。
# **それでも人が使うのは、いつも真ん中だけだ。耳は、落とす。**
#
# 🔴 構図の型＝**寄り**（#57：61作中51作が「全身」。寄りは 053／057 の2作のみ）
# 🔴 光の型＝**反復**（#53：61作で8作。014 NENRIN／019 AYA）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71① に続く5例目）
#    今日選べたのは 光＝隙間／反復／背光 × 構図＝全身／寄り／端寄せ。
#    **背光×寄りは #67⑤ で原理的に不成立**（「縁が画面に無いものは、縁で光れない」）ので、
#    最少の 背光（3/61）は寄りと組めない。隙間は 18/61 で最多＝幅が出ない。
#    → **寄り（2/61）を取るなら、光は反復か隙間の二択**。反復を取った。
#    さらに 寄り は `edge>=1 かつ 長辺>=78%` なので、**被写体は枠を越えるしかない**＝
#    「1個の物を丸ごと見せる」道が閉じる。**簀桁は元々1メートル級の道具**なので、
#    枠に収まらないことが誇張ではなく実寸になる（#67⑦「構図は自由度ではなく連立方程式」）。
#
# 🔴 機構＝**揺すり（しごき）**。流し漉きは、汲んだ紙料を桁ごと前後に振って繊維を絡ませる。
#    ① 竹ひごは**丸い**ので、簀が寝ても影の幅 D は変わらず、**隙間のピッチだけ P·cosθ に縮む**。
#       ＝ ルーバー。開口率 1 − D/(P·cosθ) が θ だけで決まる。
#       **発光の値は1フレームも動かしていない**（#69②／#70④）。光量は簀の角度だけが作る。
#    ② 051 ZENI の首振り（方孔が正対で全開）とは別物：あちらは**一つの孔の投影**、
#       こちらは**多数の丸棒の投影ピッチ**で、開口率は cosθ の逆数で効く（＝寝かせるほど急に閉じる）。
#    θ(t) = −(TH_MIN + TH_AMP·0.5(1+cos2πt))／縦揺り dz=DZ·sin2πt／横揺り dx=DX·sin4πt。
#    整数周期で厳密に閉じ、**位置キーと回転キーだけ**なので glb にそのまま乗る（#60）。
#    hero は t=0.5（＝簀がいちばん起きて開口が最大・かつ sin 項が両方 0）＝#70② の型。
#
# 造形＝boolean 不使用。丸棒63本／桁2本／絹糸6本／紙料の面1枚。
#    紙料の勾配は **UV に焼いた実数1つ**（楕円 × 耳のマスク）＝#34/#39。
#    耳は正弦の重ね合わせで揺らす——**まっすぐな縁を持たないことが、紙であることの証拠**。
#
# 【ドメイン】製紙・紙漉き（シリーズ未踏）。直近10作＝古墳・埴輪／炊事・竈／証・割符／空・凧／
#    運搬・車輪／盤上遊戯／鋳造／植物・果実／漁労／楽器・打 と別。
#    046 MAKIMONO【書物・巻子】は**出来上がった紙**が主役で、こちらは**紙になる前の道具と水**。
#    047 NOREN【商い・暖簾】も垂れる布だが、あちらは cloth の風、こちらは剛体の丸棒の格子。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 150.0                      # #58③：随伴のライム光源。発光体の外・#67⑥の遠い床へ

# --- 簀桁（ローカル原点＝下桟の上面・画面の x=AIM_X）--------------
PIV_X, PIV_Z = AIM_X, 1.58          # 揺すりの支点＝手が持つ下桟
ROLL = -0.075                       # 面内の傾き（rad）。🔴 水平な桟は「窓に付いたブラインド」に
                                    #    読める（1周目の実測）。**道具は水平に固定されていない**
YAW = -0.42                         # 面の振り（rad）。🔴🔴 3周目までの真犯人はここだった——
                                    #    **カメラに正対した矩形の格子は、何をしても「画面（モニタ）」
                                    #    に読める**（#33 の型の問題の平面版）。振ると竹ひごの投影が
                                    #    消失点へ収束し、平面ではなく**奥行きのある道具**になる。
                                    #    ひごは無限に長い円柱なので、**振っても開口率の式は変わらない**
                                    #    （軸方向の視線成分は遮蔽に効かない）＝機構は保たれる

LX0, LX1 = -2.30, 1.17              # 簀の張られている範囲（x）。左は枠外へ抜ける
LZ0, LZ1 = 0.11, 4.20               # 同（**弧長 s**）。上は反り返って枠外へ抜ける

# 🔴🔴 反り（curl）＝4周目までの真犯人への答え。**矩形の格子は、振っても寄っても
#    「画面（モニタ／ブラインド）」に読める**。効いたのは perspective ではなく
#    **簀が板ではないことを見せる**こと——竹ひごを絹糸で編んだ簀は**しなる**。
#    しなるから紙が剥がれる。板だったら剥がれない。
#    弧長 s の S_CURL から先を曲率 K_CURL の円弧にして、上端を奥へ反らせる。
S_CURL, K_CURL = 1.45, 0.90         # 反りの始まり（弧長）と曲率（1/R）
A_MAX = 1.52                        # 反りの上限角（これ以上は接線方向へ直進）

P_ROD = 0.0400                      # 竹ひごのピッチ。🔴 0.056（63本）ではブラインドの羽根。
                                    #    簀の目は**もっと細かい**——88本にして紙の縞に寄せた
D_ROD = 0.0262                      # 竹ひごの直径（D/P = 0.655）
                                    # 🔴 この比だけが #40⑥ を決める。0.50 では開口率が
                                    #    0.50→0.37 にしか動かず（0.74）機構が光を変えない
NSEG_ROD = 10

KETA_D0, KETA_D1 = -0.26, 0.045     # 桁の奥行き（y）。**簀より手前**＝実物の蓋桁が
                                    #    簀を上から押さえる向き。ひごの木口が隠れる
KETA_S0, KETA_S1 = -0.24, 0.115   # 下桟（z）。🔴 1周目は 0.265 しか無く、しかも SUBSURF に
                                    #    枕形へ丸められて（#65①）**桟でなく影**に見えた
KETA_RX1 = 1.34                     # 桁の右の木口。🔴 右桟（縦の枠）は**外した**——
                                    #    下桟と直交させた瞬間に画面が「額縁／モニタのベゼル」になり、
                                    #    しかも木口が視線とすれすれで**白い帯**を出していた（#67③）
                                    # 🔴 6周目：竹ひごの**木口（蓋）が白い破線**になり、桁の木口も
                                    #    銀色に光った。どちらも rim（右奥・420W）が端面を正面から
                                    #    叩いていたため。金属度でも粗さでも消えない＝**端面を画面の
                                    #    外へ出す**（＝寄りの構図では、端は見せなくていい）

ITO_X = (0.86, 0.20, -0.46, -1.12, -1.78)   # 絹糸（簀を編む糸）の位置
ITO_D = 0.0100
ITO_Y = -0.028                      # ひごより手前

SHEET_Y = 0.075                     # 紙料の面（ひごの奥）
SX1 = 1.17                          # 紙料の右限（簀の右端 LX1 とは別。簀は枠外へ抜けるが
                                    #    紙は画面の中で耳を見せて終わる）
MIMI = 0.78                         # 耳（紙の縁）の内寄せ。🔴 1周目は 0.30 で、勾配が耳に
                                    #    届く前に 0 になり、**紙の縁が一度も画面に出なかった**
                                    #    ＝「ブラインドの奥の緑のスポット」にしか見えない
MIMI_B = 0.40                       # 耳の内寄せ（下だけ別）。🔴 上下同じにすると
                                    #    紙の下に**死んだ黒い帯**が画面の1/3も空く（7周目の実測）
MIMI_SOFT = 0.170                   # 耳のぼけ幅。**縁として読める硬さ**まで詰める
E_FLOOR = 0.08                      # 耳の内側の下限。楕円だけだと光がスポットに戻る
E_CX, E_CS = -0.20, 0.80            # 勾配の中心（＝画面のほぼ真ん中）
E_A, E_B = 0.94, 0.72               # 楕円の半径。d=1 の縁で厳密に 0（緑スピル無し・#26）
ES_CORE = 7.0
SHEET_NX, SHEET_NZ = 150, 150

# --- 揺すり ------------------------------------------------------
TH_MIN, TH_AMP = 0.052, 0.600       # 簀の寝かし角（rad）。3.0° 〜 37.4°
DZ, DX = 0.075, 0.062               # 縦揺り・横揺り

STILL_FRAME = 61                    # t=0.5（開口最大・sin 項が両方 0＝#70②）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def tilt_of(t):
    """簀の寝かし角。負＝上端が奥へ倒れる"""
    return -(TH_MIN + TH_AMP * 0.5 * (1.0 + math.cos(2.0 * math.pi * t)))


def dz_of(t):
    return DZ * math.sin(2.0 * math.pi * t)


def dx_of(t):
    return DX * math.sin(4.0 * math.pi * t)


def profile(sarc):
    """簀の反り。弧長 sarc → (y, z, 傾き角 a)。s<S_CURL は平ら、以降は曲率 K_CURL の円弧。
       **弧長でパラメータを取る**ので、竹ひごのピッチ P は反っても変わらない
       （＝簀は伸び縮みしない）。開口率の式が反りの上でもそのまま使える理由もこれ。"""
    if sarc <= S_CURL:
        return 0.0, sarc, 0.0
    R = 1.0 / K_CURL
    a = K_CURL * (sarc - S_CURL)
    if a <= A_MAX:
        return R * (1.0 - math.cos(a)), S_CURL + R * math.sin(a), a
    y0 = R * (1.0 - math.cos(A_MAX)); z0 = S_CURL + R * math.sin(A_MAX)
    ex = sarc - S_CURL - A_MAX / K_CURL
    return y0 + ex * math.sin(A_MAX), z0 + ex * math.cos(A_MAX), A_MAX


def mat_point(x, off, sarc):
    """簀の面の上の点。off は面の法線方向のずれ（+ は奥＝紙料の側）"""
    y, z, a = profile(sarc)
    return (x, y + off * math.cos(a), z - off * math.sin(a))


def to_rig(px, py, pz):
    """簀の frame（ひごは X 軸）→ rig の frame。面内の傾き ROLL → 振り YAW の順で焼く"""
    c, s = math.cos(ROLL), math.sin(ROLL)
    rx, rz = px * c + pz * s, -px * s + pz * c
    cy, sy = math.cos(YAW), math.sin(YAW)
    return (rx * cy - py * sy, rx * sy + py * cy, rz)


def rig_to_sheet(vx, vy, vz):
    """rig の frame のベクトル → 簀の frame（遮蔽の計算はこの系でしかできない）"""
    cy, sy = math.cos(-YAW), math.sin(-YAW)
    ax, ay = vx * cy - vy * sy, vx * sy + vy * cy
    c, s = math.cos(-ROLL), math.sin(-ROLL)
    return (ax * c + vz * s, ay, -ax * s + vz * c)


def to_world(px, py, pz, t):
    """簀の frame（支点原点・ひごは X）→ 世界"""
    px, py, pz = to_rig(px, py, pz)
    th = tilt_of(t)
    c, s = math.cos(th), math.sin(th)
    y = py * c - pz * s
    z = py * s + pz * c
    return (PIV_X + px + dx_of(t), y, PIV_Z + z + dz_of(t))


def sheet_e(x, z):
    """紙料の発光スカラー（0..1）＝ 楕円の勾配 × 耳のマスク。z は**弧長 s**（＝簀の上の座標）。
       耳は正弦の重ね合わせで揺れる——**まっすぐな縁を持たないのが紙**"""
    d = math.sqrt(((x - E_CX) / E_A) ** 2 + ((z - E_CS) / E_B) ** 2)
    e = max(0.0, 1.0 - d)
    # 🔴 2周目は振幅の合計が 0.25 あって、耳が**大きな瘤**になり紙でなく染みに見えた。
    #    実物の耳の揺れは数ミリ——**「まっすぐではない」と分かる最小の量**でいい
    inset = (MIMI + 0.068 * math.sin(3.30 * x + 1.10)
             + 0.048 * math.sin(5.10 * z + 0.40)
             + 0.034 * math.sin(8.30 * x - 2.20)
             + 0.025 * math.sin(11.9 * z + 2.90)
             + 0.018 * math.sin(17.3 * x + 0.75))
    dm = min(x - LX0, SX1 - x, (z - LZ0) + (MIMI - MIMI_B), LZ1 - z) - inset
    m = max(0.0, min(1.0, dm / MIMI_SOFT))
    return (E_FLOOR + (1.0 - E_FLOOR) * e) * m


def light_visible(t):
    """🔴 #40⑥ は幾何で積分する（#46/#64②）＝**見えている発光**。
       丸棒のルーバーなので、面の寄与 = 発光スカラー × 面積 × max(0, n̂·v̂) × 開口率。
       開口率は**ひごに直交する (y,z) 面内での視線の傾き φ** だけで決まる：1 − D/(P·cosφ)。
       ——円柱は軸方向に無限なので、**軸に沿った視線成分は遮蔽に一切効かない**。
       だから YAW（振り）をいくら足しても機構は変わらない。
       **発光の値は一切入っていない。**"""
    C = CAM_LOC
    th = tilt_of(t)
    c, s = math.cos(th), math.sin(th)
    NX, NZ = 46, 60
    dx_c = (LX1 - LX0) / NX
    dz_c = (LZ1 - LZ0) / NZ
    cell = dx_c * dz_c
    tot = 0.0
    for i in range(NX):
        x = LX0 + (i + 0.5) * dx_c
        for j in range(NZ):
            z = LZ0 + (j + 0.5) * dz_c
            E = sheet_e(x, z)
            if E <= 1e-4:
                continue
            mp = mat_point(x, SHEET_Y, z)
            P = to_world(mp[0], mp[1], mp[2], t)
            aa = profile(z)[2]
            Ny, Nz = -math.cos(aa), math.sin(aa)      # 面の法線（カメラ側）
            v = (C[0] - P[0], C[1] - P[1], C[2] - P[2])
            L = math.sqrt(sum(q * q for q in v))
            v = tuple(q / L for q in v)
            # 世界 → rig（X 軸まわり −th）→ 簀の frame（−YAW → −ROLL）
            ry = v[1] * c + v[2] * s
            rz = -v[1] * s + v[2] * c
            _, ly, lz = rig_to_sheet(v[0], ry, rz)
            face = ly * Ny + lz * Nz        # 反りで法線が場所ごとに変わる
            if face <= 0.0:
                continue
            perp = math.hypot(ly, lz)
            cosf = face / perp if perp > 1e-9 else 1.0
            if cosf <= 1e-6:
                continue
            op = 1.0 - D_ROD / (P_ROD * cosf)
            if op <= 0.0:
                continue
            tot += E * cell * face * op
    return tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]
_VS = [light_visible(t) for t in _TS]
_VMAX = max(_VS)

if "--probe-only" in sys.argv:
    half_w = FRAME_W * 0.5
    print("── 062 SUKETA 幾何プローブ")
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    best = max(range(N_FRAMES), key=lambda i: _VS[i])
    print("   いちばん明るいフレーム = %d（t=%.3f）  STILL_FRAME=%d"
          % (best + 1, _TS[best], STILL_FRAME))
    for t in (0.0, 0.25, 0.5, 0.75):
        th = tilt_of(t)
        cosf = math.cos(th)
        op = 1.0 - D_ROD / (P_ROD * cosf)
        # 画面の上端・下端に来るローカル z（近似：y=0 面での換算）
        pts = [to_world(LX1, SHEET_Y, LZ0, t), to_world(LX1, SHEET_Y, LZ1, t)]
        print("   t=%.2f  簀の寝かし %5.1f°  開口率 %.3f  光 %5.1f%%  "
              "右桟の下端 z=%.2f 上端 z=%.2f"
              % (t, math.degrees(-th), op, 100 * light_visible(t) / _VMAX,
                 pts[0][2], pts[1][2]))
    print("   竹ひご %d本 / 隙間 %.1fpx / ひご %.1fpx（1600幅換算）"
          % (int((LZ1 - LZ0) / P_ROD),
             (P_ROD - D_ROD) / (2 * half_w) * 1600, D_ROD / (2 * half_w) * 1600))
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
    "base": dict(rough=0.36, spec=0.15, coat=0.05),
    # 簀＝使い込んだ竹ひご、桁＝檜。艶のある塗り物寄り（urushi）を土台に、
    # 🔴 #67③：丸棒はシルエットの全周が視線とすれすれ＝誘電体では鏡面を下げても白を映す。
    #    #0a0a0a の金属は白を浴びても黒いままなので、金属度を混ぜて逃がす。
    "take": dict(rough=0.38, spec=0.28, metal=0.20, coat=0.04, coat_rough=0.22),
    # 桁＝檜の角材。🔴 #67③：木口（小口）が視線とすれすれで**白い楔**を出していた。
    #    誘電体では鏡面を下げても粗さを上げても消えないので、金属度で逃がす
    "hinoki": dict(rough=0.52, spec=0.20, metal=0.55),
    # 🔴🔴 木口（小口）だけ別スロット（#67③ の型を、金属でなく**艶消し**で解いた版）。
    #    竹ひごの蓋と桁の端面は**カメラに正対する平らな黒い面**で、rim（右奥420W）を
    #    正面から受けて**白い破線／銀の楔**になる。すれすれではないので金属は効かない——
    #    効くのは鏡面を下限（0.10・#45）まで落として粗さで散らすこと。
    "kuchi": dict(rough=0.88, spec=0.10),
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
    return p


def black_material(name, recipe):
    m, p = principled(name)
    set_black(p, recipe)
    return m


mat_take = black_material("suketa_take", "take")
mat_keta = black_material("suketa_keta", "hinoki")
mat_kuchi = black_material("suketa_kuchi", "kuchi")


def sheet_material(name):
    """紙料の光。勾配は **UV 'grad' の U に焼いた実数1つ**（#34/#39）。
       ノイズは「地合（じあい）」＝繊維の絡みむら。**紙が均くなるのは真ん中だけ**。
       🔴 #70④：halo は**芯を白へ抜く**ことでしか出ない（ライムは B がほぼ無い）。"""
    m, p = principled(name)
    set_black(p, "base")
    nt = m.node_tree
    p.inputs["Base Color"].default_value = BLACK            # #68⑤：下地に色を置かない
    p.inputs["Roughness"].default_value = 0.62

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    # 地合（繊維のむら）。2オクターブを重ねて、細かい筋と大きな溜まりを両方出す
    ntx = nt.nodes.new("ShaderNodeTexNoise")
    ntx.inputs["Scale"].default_value = 11.0
    ntx.inputs["Detail"].default_value = 7.0
    ntx.inputs["Roughness"].default_value = 0.62
    nmr = nt.nodes.new("ShaderNodeMapRange"); nmr.clamp = True
    nmr.inputs["From Min"].default_value = 0.30; nmr.inputs["From Max"].default_value = 0.74
    nmr.inputs["To Min"].default_value = 0.72; nmr.inputs["To Max"].default_value = 1.18
    nt.links.new(ntx.outputs["Fac"], nmr.inputs["Value"])

    e0 = mn('MULTIPLY'); nt.links.new(xyz.outputs["X"], e0.inputs[0])
    nt.links.new(nmr.outputs["Result"], e0.inputs[1])

    # 芯だけ白へ抜く（#70④：#24 のペンキ化と #51 の halo が同じ1手で解ける）
    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = 0.72; wmr.inputs["From Max"].default_value = 1.15
    wmr.inputs["To Min"].default_value = 0.0; wmr.inputs["To Max"].default_value = 0.52
    nt.links.new(e0.outputs[0], wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])
    nt.links.new(mixc.outputs[2], p.inputs["Emission Color"])

    e2 = mn('MULTIPLY', ES_CORE); nt.links.new(e0.outputs[0], e2.inputs[0])
    nt.links.new(e2.outputs[0], p.inputs["Emission Strength"])
    return m


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
def link(me, name, mat, parent=None, smooth=0.35):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if not ob.data.materials:
        ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def RV(bm, x, y, z):
    """簀の frame の実寸 → rig の frame（面内の傾きと振りをここで焼く）"""
    return bm.verts.new(to_rig(x, y, z))


def tube_x(bm, x0, x1, sarc, r, nseg):
    """X 軸に沿った竹ひご（両端に蓋）。断面は**面の法線と接線**の張る円"""
    y0, z0, a = profile(sarc)
    ny, nz = math.cos(a), -math.sin(a)          # 面の法線（奥向き）
    ty, tz = math.sin(a), math.cos(a)           # 面の接線（弧長方向）
    rings = []
    for x in (x0, x1):
        ring = []
        for k in range(nseg):
            th = 2 * math.pi * k / nseg
            cy = y0 + r * (ny * math.cos(th) + ty * math.sin(th))
            cz = z0 + r * (nz * math.cos(th) + tz * math.sin(th))
            ring.append(RV(bm, x, cy, cz))
        rings.append(ring)
    for k in range(nseg):
        bm.faces.new((rings[0][k], rings[0][(k + 1) % nseg],
                      rings[1][(k + 1) % nseg], rings[1][k]))
    for i, sgn in ((0, 0), (1, 1)):
        c = RV(bm, x0 if i == 0 else x1, y0, z0)
        for k in range(nseg):
            a, b = rings[i][k], rings[i][(k + 1) % nseg]
            f = bm.faces.new((c, b, a) if sgn else (c, a, b))
            f.material_index = 1                     # 木口＝艶消しスロット


def thread_s(bm, s0, s1, xc, off, r, nseg, nstep=90):
    """絹糸。反った簀の上を弧長に沿って走る"""
    rings = []
    for j in range(nstep + 1):
        sa = s0 + (s1 - s0) * j / nstep
        y0, z0, a = profile(sa)
        ny, nz = math.cos(a), -math.sin(a)
        ring = []
        for k in range(nseg):
            th = 2 * math.pi * k / nseg
            cy = y0 + off * ny + r * (ny * math.cos(th) + math.sin(th) * 0.0)
            cz = z0 + off * nz + r * (nz * math.cos(th))
            ring.append(RV(bm, xc + r * math.sin(th), cy, cz))
        rings.append(ring)
    for j in range(nstep):
        for k in range(nseg):
            bm.faces.new((rings[j][k], rings[j][(k + 1) % nseg],
                          rings[j + 1][(k + 1) % nseg], rings[j + 1][k]))


def box(bm, x0, x1, y0, y1, z0, z1):
    vs = {}
    for i, x in enumerate((x0, x1)):
        for j, y in enumerate((y0, y1)):
            for k, z in enumerate((z0, z1)):
                vs[(i, j, k)] = RV(bm, x, y, z)
    q = [((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)),
         ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)),
         ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)),
         ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
         ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)),
         ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1))]
    for f in q:
        bm.faces.new([vs[i] for i in f])


def _mark_east(bm):
    """いちばん +x 側の面（＝画面に出る木口）を艶消しスロットへ"""
    fx = max(bm.faces, key=lambda f: f.calc_center_median().x)
    fx.material_index = 1


def su_mesh():
    """簀＝竹ひごの列。**丸いから、寝かせると隙間だけが閉じる**（ルーバー）"""
    bm = bmesh.new()
    n = int((LZ1 - LZ0) / P_ROD)
    for i in range(n):
        tube_x(bm, LX0, LX1, LZ0 + (i + 0.5) * P_ROD, D_ROD * 0.5, NSEG_ROD)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("su"); bm.to_mesh(me); bm.free()
    return me


def ito_mesh():
    """簀を編む絹糸。**丸棒だけでは簾になる**——糸が渡って初めて簀に読める"""
    bm = bmesh.new()
    for x in ITO_X:
        thread_s(bm, LZ0 - 0.02, LZ1 + 0.02, x, ITO_Y, ITO_D * 0.5, 8)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("ito"); bm.to_mesh(me); bm.free()
    return me


def keta_mesh():
    """桁（下桟だけ）。**簀より手前**にあって、ひごの木口を押さえている。
       🔴 縦の右桟は外した——下桟と直交した瞬間に画面が「額縁／モニタのベゼル」になり、
          しかも木口が視線とすれすれで白い帯を出していた（#67③・4周目の実測）"""
    bm = bmesh.new()
    box(bm, LX0 - 0.14, KETA_RX1, KETA_D0, KETA_D1, KETA_S0, KETA_S1)     # 下桟
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _mark_east(bm)
    me = bpy.data.meshes.new("keta"); bm.to_mesh(me); bm.free()
    return me


def sheet_mesh():
    """紙料の面。UV 'grad' の U に sheet_e（楕円 × 耳）を焼く。
       U=0 の領域は純黒の裏当てになる——**その黒は簀と桁の奥**なので #49① に触れない"""
    bm = bmesh.new()
    grid, gsxz = [], []
    for j in range(SHEET_NZ + 1):
        z = LZ0 + (LZ1 - LZ0) * j / SHEET_NZ
        gsxz.append([(LX0 + (LX1 - LX0) * i / SHEET_NX, z) for i in range(SHEET_NX + 1)])
        grid.append([RV(bm, *mat_point(LX0 + (LX1 - LX0) * i / SHEET_NX, SHEET_Y, z))
                     for i in range(SHEET_NX + 1)])
    for j in range(SHEET_NZ):
        for i in range(SHEET_NX):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.verts.index_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                       # 法線をカメラ側（−Y）へ
        if f.normal.y > 0:
            f.normal_flip()
    uvl = bm.loops.layers.uv.new("grad")
    vmap = {}                                       # 頂点 → (x, 弧長 s)。格子を作った時に控える
    for j in range(SHEET_NZ + 1):
        for i in range(SHEET_NX + 1):
            vmap[grid[j][i].index] = gsxz[j][i]
    for f in bm.faces:
        for lp in f.loops:
            sx, sz = vmap[lp.vert.index]
            lp[uvl].uv = (sheet_e(sx, sz), 0.5)
    me = bpy.data.meshes.new("sheet"); bm.to_mesh(me); bm.free()
    return me


# ---------- 配置 ----------
rig = bpy.data.objects.new("suketa", None)      # 揺すりはここ1つ（＝手）
bpy.context.collection.objects.link(rig)
rig.location = (PIV_X, 0.0, PIV_Z)

ob_su = link(su_mesh(), "su", mat_take, parent=rig)
ob_su.data.materials.append(mat_kuchi)          # スロット1＝木口
# 🔴 絹糸（簀を編む糸）は**外した**。1600×2000 で初めて見えた欠陥（#68 の型）——
#    ①縦に走る太い曲線が**ブラインドの操作コード**そのものに見える
#    ②視線とすれすれの糸が**白い破線**になる（#67③ の細物版）
#    実物の絹糸は紙料の下でほとんど見えない。**見えない物を描くと、別の物に見える。**
ob_keta = link(keta_mesh(), "keta", mat_keta, parent=rig, smooth=0.20)
ob_keta.data.materials.append(mat_kuchi)        # スロット1＝木口
mat_sheet = sheet_material("shiryou")
ob_sheet = link(sheet_mesh(), "sheet", mat_sheet, parent=rig)

# 🔴 黒の肌は実ジオメトリ（#52）。**発光体には掛けない**（MATERIALS.md 掟1）
#    ひごと糸は細すぎて DISPLACE がシルエットを食うので、桁（大きな平面）だけに入れる
#    🔴 #65①：既定の Catmull-Clark は**直方体を枕形に丸める**。1周目の下桟は
#       レンズ形の影にしか見えなかった。**'SIMPLE' で割るだけにする**
sub = ob_keta.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 4
sub.subdivision_type = 'SIMPLE'
tex = bpy.data.textures.new("relief_keta", 'CLOUDS'); tex.noise_scale = 0.075
dsp = ob_keta.modifiers.new("disp", 'DISPLACE')
dsp.texture = tex; dsp.strength = 0.0030; dsp.mid_level = 0.5
for ob, w in ((ob_keta, 0.0045), (ob_su, 0.0012)):
    bev = ob.modifiers.new("bev", 'BEVEL')      # #17：稜線が光を拾わないと黒はプラスチックになる
    bev.width = w; bev.segments = 2
    bev.limit_method = 'ANGLE'; bev.angle_limit = math.radians(30)

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    rig.rotation_euler = (tilt_of(t), 0.0, 0.0)
    rig.location = (PIV_X + dx_of(t), 0.0, PIV_Z + dz_of(t))
    rig.keyframe_insert("rotation_euler", frame=f + 1)
    rig.keyframe_insert("location", frame=f + 1)

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
        caption("MIDDLE STUDY 062 — SUKETA", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (AIM_X, 0.0, 1.90)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
# 🔴 #67①：抜け（ひごのあいだ）がある造形では逆光がそのままカメラに写る
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
cam.data.dof.focus_distance = 8.32
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
    if o.type == 'MESH' and o is not ob_sheet:
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
        if o.type != 'MESH' or o is floor_obj:
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
    # 桁の右端・下端が画面のどこに来るか（＝寄りの構図を決める2条件・#67⑦）
    for nm, p in (("桁の木口", (KETA_RX1, KETA_D1, KETA_S1)),
                  ("下桟の下端", (0.0, KETA_D1, KETA_S0)),
                  ("反りの始まり", (0.0, 0.0, S_CURL)),
                  ("耳の下端(右)", (0.7, SHEET_Y, LZ0 + MIMI))):
        w = to_world(p[0], p[1], p[2], 0.5)
        c = world_to_camera_view(scene, cam, Vector(w))
        print(">> %-10s  画面 x %.1f%%  上から %.1f%%" % (nm, c.x * 100, (1 - c.y) * 100))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_062.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("shiryou_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.42
    ob_sheet.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {rig.name, ob_su.name, ob_keta.name, ob_sheet.name}
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = ob_su
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
