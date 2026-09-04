# =============================================================
# MIDDLE STUDY 071 — MATO（的 / 図星 the mark at the centre）
#
# 六つの的が、宙にある。
# 弓道の的は、外から数えて黒・白・黒・白・黒——**いちばん内側が、白い。**
# 霞的という。中心の白を「中白」と呼び、その真ん中の一点を **図星** と呼ぶ。
#
# 図星、という言葉は的から来ている。
# 言い当てられたときに「図星だ」と言うのは、**真ん中に当たった**という意味だ。
# 的の値打ちは、いちばん外の黒い輪ではなく、そこから六つ内側の、いちばん小さい白にある。
#
# 六人立ちの道場には、的が六つ並ぶ。
# けれど射手から見て正面にあるのは、いつでも**自分の的ひとつ**だけだ。
# 隣の的は少しずつ傾いて、輪はつぶれ、真ん中は細くなって、やがて線になる。
# ——**正面から見たときだけ、真ん中が見える。**
#
# そして六つのうち一つは、まだ紙が張られていない。枠だけの的。
# 的は毎回張り替える。**真ん中が無い的には、当てられない。**
#
# 🔴 光の型＝**面**（#53：70作で6作。光る面そのものが正面に見える）
# 🔴 構図の型＝**群**（#57：70作で3作。**70作中51作が「全身」**）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥／#71①／#72／#74②／#75②／
#    #78／#79／#80 に続く14例目）。今日選べたのは 光＝面／隙間／背光 × 構図＝全身／天地／群。
#    ・隙間(19) と 全身(51) はシリーズの既定でありもう型ではない。→ 落とす。
#    ・**背光×群 は #71① で実測済みの不成立**（背後の共有光源が物どうしを繋いで clusters==1）。
#    ・**面×天地 は #75② で実測済みの不成立**（カメラ軸が完全に水平なので、
#      被写体を上げ下げしても「面の見え方」は 1mm も変わらない＝構図が仕事をしない）。
#    ・背光×天地 は 065 TORII で既出（#76④が示した背光の唯一の相方）。
#    ・→ **面×群** が一意に残る。**70作で一度も無い組み合わせ**（下の分布で確認済み）。
#
#    🔴 ただし #71① の理屈をそのまま踏むと死ぬ。あれが禁じているのは
#      「**共有の**光源」であって「光そのもの」ではない。
#      **各個体が自分の面を持つ**なら、光は個体の輪郭の内側に閉じ、塊は繋がらない。
#      → 成立条件は一つだけ：**投影面での個体間の隙間 > Glare のハロー2つ分**。
#        実測で最小の隙間を 0.248（＝1600px で 141px）確保した（下の probe が全ペアを出す）。
#        結果 hero の塊は **6**（compositions.py --verify で確認済み）。
#
# 🔴 機構＝**首振り（yaw）と、上下のわずかな漂い**。どちらも厳密に閉じる。
#    ・θ_i(t) = B_i + TH_MID − TH_A·cos(2πt + φ_i)。面が正対から 59°まで倒れ、
#      **見える発光面積は cos θ に比例して痩せる**＝機構が光を変える（#40⑥）。
#    ・🔴 #71② の裏返し：位相を**散らすと合計が定数になる**ので、ここでは
#      **わざと狭く**（0.13周期＝47°以内）まとめた。群全体が一緒に息をして、
#      ずれは「さざなみ」としてだけ残る。#40⑥ は 0.583（合格 0.75以下）。
#    ・漂いは sin（yaw が cos）＝**位相が π/2 ずれる**ので、どちらかが止まる瞬間に
#      もう一方が最速。#59 の「静止率 ≤20%」は往復運動だと端で引っかかるが、これで抜ける。
#    位置と回転のキーだけ＝シェイプキー不要でそのまま glb に乗る（#60）。
#
# 🔴 #57 の「60°超は必ず銀色」に触らないよう、**θ の最大は 59.0°**で止めてある（＝B_i の最大 +1°）。
# 🔴 #67①：素枠（紙の無い的）が抜けている＋個体のあいだが白く抜けているので
#    **back.visible_camera = False**。さらに back はライトリンクで床を受光から外す（#56）。
#
# 造形＝極座標の円盤と、輪だけの素枠。boolean 不使用。object.scale 不使用（#15）。
#    黒の質感は MATERIALS.md の **`nuno_usu`**＝的紙は和紙＝**光を透かすほど薄い**もの。1作1素材。
#    ただし Sheen は 0.55→0 に落とし、#62③ に従って Metallic を 0→0.34 入れた（下の注を見よ）。
#    面は完全な平面にせず 0.014 の張り出しを持たせ、外周 7% は後ろへ巻き込ませた
#    （#57「カメラに正対する平らな黒い面」への幾何側の担保）。
#
# 🔴 7周かかった。効いた4つを短く：
#    ① **帯の縁の鋸歯**は解像度ではなく補間の形。E を1セルで 0 へ落とすと四角が対角線で折れる
#       → 境目に「幅ゼロ」の行を2本置いて、補間する四角そのものを消す（paper_rows）
#    ② **ボタンに見える犯人は枠だった**。実物の的は紙が枠を包んで前面を覆う＝正面に枠は無い
#       → 部材を1つ消した（#80 と同じ「見せない」判断）
#    ③ **白い輪郭（クロム）は Sheen と丸い縁**。Metallic を入れると `#0a0a0a` は
#       明るいグレー環境を映しても黒いままなので、輪郭だけが消える（#62③）
#    ④ **halo は「明るいライム」では作れない**——青が上がらない。→ 光の作りを
#       「刷りの上に発光」から「**紙を透かす光 × 刷り**」へ変えた（BANDS の注）
#
# 【ドメイン】弓術・的／霞的。直近10作＝躙口／薬研／茶筅／蛸壺／和蝋燭／鳥居／柄鏡／
#    和鋏／紙漉き／埴輪 と別。049 YUMI【武・弓／弓道】は22作前で、しかも**弓＝射る側**。
#    こちらは**射られる側**で、機構も造形も共有していない。
#    028 ENSO も同心の輪だが、あちらは1個の輪を全身で見せる作。
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
LIME_W = 55.0                     # 随伴のライム光源（#58）。床は全面見えている＝#58 の標準側

# --- 的（六人立ち。実物は全部同じ大きさ＝遠いものが小さく写るのは遠近だけ）----
# 🔴🔴 1周目の造形は「ボタン／スピーカー」にしか見えなかった（#48 の型）。原因は3つとも造形側だった：
#    ① 枠が紙より**外へ膨らんでいた**＝ベゼル ② 見込みが厚すぎてパック（ボタン）
#    ③ 芯が真っ白に飛んで LED。→ **枠を紙より手前へ出し、紙を井戸の底に落とす**。
#    こうすると key の光が枠の内側に**三日月の影**を落とし、「枠に紙が張ってある」が一目で出る。
# 🔴🔴🔴 3周目で分かった真犯人：**枠が紙より外に見えていたこと**。
#    2周目は「枠を手前へ出して紙を井戸の底に落とす」で三日月の影を作ったが、
#    それは絵として**ベゼル**＝ボタンそのものだった。**実物の的は紙が枠を包んで前面を覆う**——
#    正面から枠は1mmも見えない。刷りが縁まで行って、いちばん外の黒い輪の外周が**そのままシルエット**になる。
#    → 紙を R_MATO まで張り、外周 7% で後ろへ巻き込ませた（＝張り込みの折り返し）。
#    「見せない」判断が効いたのは #80 と同じ形。造形を足すのではなく**部材を1つ消した**。
R_MATO  = 0.272                    # 的の半径（実物 36cm 的の比を保った 54cm 判）
TH      = 0.034                    # 的枠の見込み（奥行き）
RIM_R   = 0.0015                   # 素枠の外側の面取り
R_FACE  = R_MATO                   # 🔴 的紙は縁まで張る（枠は紙の裏に隠れる）
HOOP_W  = 0.038                    # 素枠の帯の幅（＝紙の裏にある枠の実寸）
DOME    = 0.014                    # 紙の張り出し（完全な平面を作らない＝#57）
WRAP_U  = 0.93                     # ここから外は紙が後ろへ巻き込む（張り込みの折り返し）
WRAP    = 0.021                    # 巻き込みの深さ

# 🔴 配置は「投影面での位置と隙間」から逆算して決めた（#71①の成立条件）。
#    (x, y, z, 素枠か, B_i[deg], φ_i[周], 漂いの位相[周])
MATOS = [
    (-0.0434, -0.95, 2.8799, False, -5.0, 0.000, 0.00),
    ( 0.7526,  0.55, 3.1761, False,  0.0, 0.035, 0.31),
    ( 1.3522,  1.35, 2.4964, True,  -1.0, 0.055, 0.62),   # 🔴 素枠＝紙が張られていない一つ
    (-0.1109, -0.35, 2.0937, False, -3.0, 0.065, 0.14),
    ( 0.6105,  1.75, 1.9379, False,  1.0, 0.100, 0.78),
    ( 1.0723,  0.20, 1.2639, False, -2.0, 0.130, 0.45),
]
TH_MID, TH_A = 29.0, 29.0          # θ ∈ [0°, 58°]＋B_i。
# 🔴 θ の最大は B_i+TH_MID+TH_A ＝ **59.0°**。φ は「いつ倒れるか」しか変えないので
#    最大角には効かない（1周目は B=+4 を入れて 62° になり #57 の 60° を越えていた）
BOB = 0.055                        # 漂いの振幅（sin＝yaw の cos と π/2 ずれる）

# --- 霞的の割り（中心から：中白・一の黒・二の白・二の黒・三の白・三の黒）----
# 🔴🔴🔴 4〜5周目でいちばん高くついた学び：**halo は「明るいライム」では作れない。**
#    measure.py の halo は 150<R<230 かつ G>200 かつ **90<B<190**。実測すると
#    明るい緑の画素 57,156 個の **青の中央値は 37**——帯の下限 90 のはるか下にいた。
#    白の混ぜ方（WHITE_FROM/TO）を上下しても 7,640〜8,800 の間を往復するだけで越えない。
#    **青を上げられるのは「白へ抜ける広い勾配」だけ**で、刷りの硬い輪では勾配が短すぎた。
#
#    → 光の作りを変えた。**的紙は和紙＝光を透かす**（MATERIALS.md の nuno_usu の定義そのもの）。
#      真ん中の裏に光があり、紙を透かして出てくる。刷りの黒はその光を **INK までしか通さない**。
#        E(u) = 透過の山 exp(-(u/GLOW_U)^2) × 刷り（白=1／黒=INK） ＋ 図星の芯
#      こうすると輪の内側から外側まで**連続の勾配**ができ、白→ライムの帯が中白いっぱいに広がる。
#      おまけに #24 の「ペンキ化」——縁のくっきりした均一なベタ塗り——も同時に消える。
BANDS = [(0.00, 0.20, True), (0.20, 0.36, False), (0.36, 0.52, True),
         (0.52, 0.68, False), (0.68, 0.84, True), (0.84, 1.00, False)]
GLOW_U = 0.66                      # 紙を透ける光の広がり（真ん中がいちばん明るい）
INK = 0.04                         # 刷りの黒が通す割合。0.10 では黒い輪が緑に浮いて的が読めない
BAND_TILT = 0.08                   # 帯の中の傾き（内側ほど明るい）。勾配の主役は透過の山の側
HOT_A, HOT_U = 0.46, 0.10          # 図星＝白へ抜く芯
E_PEAK = 1.46                      # raw の最大（1.00 + HOT_A）
E_FLOOR = 0.010
ES_CORE = 4.4                      # 6.0 では中白が白へ飛んで halo の帯を突き抜けた。透過の山にしてから上げ直した
WHITE_FROM, WHITE_TO = 0.55, 0.50
K_MIX = 16.0                       # 三の白（E≒0.10）でも発光へ倒す。9 では黒が混じって g<90 で母集団から抜ける

STILL_FRAME = 26


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def tau(t):
    return 2.0 * math.pi * t


def theta(i, t):
    """i 番目の的の首振り角[rad]"""
    _, _, _, _, b, ph, _ = MATOS[i]
    return math.radians(b + TH_MID - TH_A * math.cos(tau(t) + tau(ph)))


def bob(i, t):
    """i 番目の的の漂い（z への足し込み）"""
    return BOB * math.sin(tau(t) + tau(MATOS[i][6]))


def e_in(u, band):
    """的紙の E。**透過の山 × 刷り ＋ 図星の芯**。
       band を引数で渡すのは、帯の境目を「幅ゼロ」にするため（paper_rows の説明を見よ）"""
    a, b, white = band
    raw = math.exp(-((u / GLOW_U) ** 2)) * ((1.0 - BAND_TILT * (u - a) / (b - a))
                                            if white else INK)
    if a == 0.0:                                   # 図星の芯は中白にだけ
        raw += HOT_A * math.exp(-((u / HOT_U) ** 2))
    return max(0.0, (raw / E_PEAK - E_FLOOR) / (1.0 - E_FLOOR))


def e_local(u):
    """u だけから引く版（幾何の積分と probe 用）"""
    if u >= 1.0:
        return 0.0
    for band in BANDS:
        if band[0] <= u < band[1]:
            return e_in(u, band)
    return 0.0



def proj(x, y, z):
    """ワールド → 画面（y=0 平面の実寸）。カメラ軸は完全に +Y（#75②）"""
    m = 8.3 / (8.3 + y)
    return (AIM_X + (x - AIM_X) * m, LOOK_Z + (z - LOOK_Z) * m, m)


# 的紙のうちライムが占める面積の比（幾何で積分＝レンダーの画素で測らない・#46）
def _lime_share():
    N = 4000
    s = 0.0
    for k in range(N):
        u = (k + 0.5) / N
        if e_local(u) > 0.02:
            s += 2.0 * u / N
    return s


LIME_SHARE = _lime_share()


def visible_light(t):
    """#40⑥ を幾何で積分する。見える発光 ＝ Σ_i (投影面積) × cos θ_i。
       的紙は平らなので、正対からの傾きはそのまま cos で効く（素枠は 0）。"""
    tot = 0.0
    for i, (x, y, z, hoop, _, _, _) in enumerate(MATOS):
        if hoop:
            continue
        m = 8.3 / (8.3 + y)
        tot += (math.pi * R_FACE ** 2 * LIME_SHARE) * m * m * max(0.0, math.cos(theta(i, t)))
    return tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]

if "--probe-only" in sys.argv:
    print("── 071 MATO 幾何プローブ")
    print("   的 半径%.3f（直径%.3f）／枠の見込み%.3f／紙の半径%.3f／張り出し%.3f"
          % (R_MATO, 2 * R_MATO, TH, R_FACE, DOME))
    print("   霞的の割り " + " ".join("%s%.2f-%.2f" % ("白" if w else "黒", a, c)
                                      for a, c, w in BANDS))
    print("   E の段 " + " ".join("%.2f" % e_local(u) for u in
                                 (0.0, 0.10, 0.19, 0.28, 0.37, 0.51, 0.60, 0.69, 0.83, 0.92)))
    print("   ライムが的紙に占める比 %.3f（幾何で積分）" % LIME_SHARE)

    print("\n   ── 投影（#71① の成立条件：個体が繋がらないこと）")
    P = []
    for i, (x, y, z, hoop, b, ph, bp) in enumerate(MATOS):
        px, pz, m = proj(x, y, z)
        P.append((px, pz, R_MATO * m, hoop))
        print("   %d %s 投影(%.3f, %.3f) 半径%.3f  m=%.4f  B=%+.1f° φ=%.3f"
              % (i + 1, "素枠" if hoop else "的  ", px, pz, R_MATO * m, m, b, ph))
    gmin = 9.0
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            d = math.hypot(P[i][0] - P[j][0], P[i][1] - P[j][1]) - P[i][2] - P[j][2]
            gmin = min(gmin, d)
    print("   🔴 個体間の最小の隙間 %.3f（＝1600px で %.0fpx。ハロー2つ分より広いこと）"
          % (gmin, gmin / FRAME_W * 1600))

    print("\n   ── 機構（#40⑥）")
    step = max(1, N_FRAMES // 24)
    VS = {i: visible_light(_TS[i]) for i in range(0, N_FRAMES, step)}
    vs = [VS[i] for i in sorted(VS)]
    vmax, vmin = max(vs), min(vs)
    print("   見える光 min/max = %.3f （合格 0.75以下）" % (vmin / vmax))
    print("   光の曲線 " + " ".join("%.0f" % (100 * v / vmax) for v in vs))
    b = max(VS, key=lambda i: VS[i])
    print("   いちばん明るい frame %d（t=%.3f）  STILL_FRAME=%d（t=%.3f・光は最大の %.0f%%）"
          % (b + 1, _TS[b], STILL_FRAME, (STILL_FRAME - 1) / N_FRAMES,
             100 * visible_light((STILL_FRAME - 1) / N_FRAMES) / vmax))
    th = [math.degrees(theta(i, (STILL_FRAME - 1) / N_FRAMES)) for i in range(len(MATOS))]
    print("   hero の θ " + " ".join("%.1f°" % v for v in th))
    thmax = max(math.degrees(theta(i, tt)) for i in range(len(MATOS)) for tt in _TS)
    print("   θ の最大 %.1f°（#57 の 60° を割らないこと）" % thmax)

    t = (STILL_FRAME - 1) / N_FRAMES
    print("\n   ── 画面占有（hero t=%.3f）" % t)
    print("   ライム面積 ≒ %.2f%%（帯 0.8〜12）"
          % (visible_light(t) / (FRAME_W * FRAME_H * 0.8) * 100))

    SX0, SZ0 = AIM_X - FRAME_W / 2, LOOK_Z - FRAME_H / 2
    gx0 = min(p[0] - p[2] for p in P); gx1 = max(p[0] + p[2] for p in P)
    gz0 = min(p[1] - p[2] for p in P); gz1 = max(p[1] + p[2] for p in P)
    print("   群 bbox x %.1f..%.1f%%  y(下から) %.1f..%.1f%%"
          % ((gx0 - SX0) / FRAME_W * 100, (gx1 - SX0) / FRAME_W * 100,
             (gz0 - SZ0) / FRAME_H * 100, (gz1 - SZ0) / FRAME_H * 100))
    print("   長辺 %.1f%%（帯 44〜66・群は横に広がるので上振れは警告どまり）"
          % (max((gx1 - gx0) / FRAME_W, (gz1 - gz0) / FRAME_H) * 100))

    capz = LOOK_Z + (1.02 + 0.075 - LOOK_Z) * (8.3 / (8.3 - 1.7))
    print("   いちばん下の的 z=%.3f ／ キャプション上端 z=%.3f → 余白 %.3f（正なら重ならない）"
          % (gz0 - BOB, capz, gz0 - BOB - capz))
    zb_hi = SZ0 + FRAME_H - 0.62 * (FRAME_H * 0.8)
    zb_lo = SZ0 + FRAME_H - 1.00 * (FRAME_H * 0.8)
    occ = sum(max(0.0, min(p[1] + p[2], zb_hi) - max(p[1] - p[2], zb_lo)) * 2 * p[2]
              for p in P) / ((zb_hi - zb_lo) * FRAME_W)
    print("   #58 床帯 z %.3f..%.3f のうち的で塞がれている割合 ≒%.0f%%（85%%未満なら測れる）"
          % (zb_lo, zb_hi, occ * 100))
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
# 的紙は和紙、枠は竹。**光を透かすほど薄い**もの＝`nuno_usu`（暖簾・幕・巻物・紙）。1作1素材（掟4）
# 🔴 MATERIALS.md の nuno_usu（rough0.66／spec0.28／Sheen0.55）をそのまま当てると、
#    **円い縁が back(1800W) と rim を擦れ角で拾って白い輪郭になる**＝クロムのボタン（1〜3周目）。
#    Sheen は擦れ角で効くので、輪や巻き込みのある形では効きすぎる。→ 0 に落とす。
# 🔴 #62③ のとおり **Metallic を入れる**（0 → 0.34）。`#0a0a0a` の金属は
#    明るいグレー環境（world 0.92）を映しても**黒いまま**なので、白い輪郭だけが消える。
#    Coat は元から入れていない（#62③：Coat は常に誘電体の白い層＝ヴェールの本体）
BLACK_RECIPES = {"nuno_usu": dict(rough=0.66, spec=0.28, metal=0.34,
                                  sheen=0.0, sheen_rough=0.25)}
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


mat_body, bp_ = principled("nuno_usu")
apply_black(bp_)
mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6


def glow_material(name):
    """E→0 側は**的紙の黒そのもの**へ戻す（発光板の縁を作らない・#49①）。
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


mat_glow = glow_material("zuboshi")


# ---------- 造形（bmesh・実寸。局所座標＝面の法線は -Y）----------
NA = 144         # 円周の分割（96 では帯の縁が低解像度でモアレになった）
NB = 5           # 帯ひとつあたりの半径方向の分割
NRIM = 3         # 枠の外側の分割
U_EPS = 5e-4     # 帯の境目に置く「幅ゼロに近い」段差（下記）

Y0 = -TH / 2                       # 的の前面の基準


def y_paper(u):
    """的紙の断面。中心はわずかに張り出し、外周 7% で後ろへ巻き込む（＝縁が丸いのは紙のせい）"""
    y = Y0 - DOME * (1.0 - u * u)
    if u > WRAP_U:
        y += WRAP * ((u - WRAP_U) / (1.0 - WRAP_U)) ** 2
    return y


def paper_rows():
    """的紙の断面 [(y, r, E), ...] を半径の小さい順に。

    🔴🔴 2周目でいちばん高くついた学び：**E を「1セルで 0 へ落とす」と、帯の縁が鋸歯になる。**
    四角形は描画時に三角形2枚に割られるので、四隅の UV が違う四角は
    **対角線に沿って折れる**＝円周の分割数ぶんのギザギザが縁に並ぶ（144本の櫛が見えた）。
    解像度でも分割数でも消えない（原因が量子化ではなく補間の形だから）。

    → 帯の境目に**同じ位置の行を2本**置き（半径差 1e-3·R_FACE ＝ 1600px で 0.13px）、
      **補間する四角そのものを消す**。各帯は自分の値のまま端まで行き、
      次の帯は次の値で始まる＝霞的の刷り分けと同じ、幅ゼロの境目になる。
    （#49① の「発光面の縁を作らない」は**発光板**の話。ここでの硬い縁は題材そのもの＝的の刷り）
    """
    rows = []
    for band in BANDS:
        a, b = band[0], band[1]
        for k in range(NB + 1):
            u = (a + U_EPS) + ((b - U_EPS) - (a + U_EPS)) * k / NB
            rows.append((y_paper(u), R_FACE * u, e_in(u, band)))
    return rows


def rim_profile():
    """素枠の外側の断面。(y, r, 0) を 手前の面 → 後ろの面 で返す"""
    out = []
    for k in range(NRIM + 1):
        v = k / NRIM
        out.append((Y0 + TH * v, R_MATO - RIM_R * (2 * v - 1) ** 2, 0.0))
    return out


def polar(bm, uvl, rows, close_center):
    """rows = [(y, r, E)] を半径の小さい順に。円周方向に NA 分割して面を張り、
       E を UV に焼く（#39：面の並び順ではなく**行の値**から引く）。
       🔴 glb はノード網を持てない（#25c）。発光する面だけスロット1に分ける（#60）"""
    verts = []
    for (yy, rr, _e) in rows:
        verts.append([bm.verts.new((rr * math.cos(2 * math.pi * a / NA), yy,
                                    rr * math.sin(2 * math.pi * a / NA))) for a in range(NA)])
    def paint(f, es):
        for lp, e in zip(f.loops, es):
            lp[uvl].uv = (e, 0.5)
        f.material_index = 1 if max(es) > 0.02 else 0
    for i in range(len(rows) - 1):
        e0, e1 = rows[i][2], rows[i + 1][2]
        for a in range(NA):
            b = (a + 1) % NA
            f = bm.faces.new((verts[i][a], verts[i + 1][a], verts[i + 1][b], verts[i][b]))
            paint(f, (e0, e1, e1, e0))
    if close_center:
        c = bm.verts.new((0.0, rows[0][0], 0.0))
        ec = rows[0][2]
        for a in range(NA):
            b = (a + 1) % NA
            paint(bm.faces.new((c, verts[0][a], verts[0][b])), (ec, ec, ec))


def new_bm():
    bm = bmesh.new()
    return bm, bm.loops.layers.uv.new("grad")


def finish(bm, name):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)   # 継ぎ目を溶接＝閉じた立体（#37②）
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def build_mato():
    """紙の張られた的＝浅い枠の井戸の底に的紙。枠は紙より手前へ出る（三日月の影）"""
    bm, uvl = new_bm()
    rows = paper_rows()
    polar(bm, uvl, rows, close_center=True)                                          # 的紙（縁まで）
    polar(bm, uvl, [(rows[-1][0], R_MATO, 0.0), (TH / 2, R_MATO, 0.0)], False)       # 巻き込みの続き
    polar(bm, uvl, [(TH / 2, R_MATO * u, 0.0) for u in (0.0, 0.34, 0.67, 1.0)], True)  # 後（閉じる）
    return finish(bm, "mato")


def build_hoop():
    """素枠＝紙の張られていない的。紙の裏にあるはずの枠だけが在る。閉じた立体にする"""
    bm, uvl = new_bm()
    ri = R_MATO - HOOP_W
    polar(bm, uvl, [(Y0, ri, 0.0), (Y0, R_MATO - RIM_R, 0.0)], False)                # 前の輪
    polar(bm, uvl, rim_profile(), False)                                             # 外の縁
    polar(bm, uvl, [(TH / 2, ri, 0.0), (TH / 2, R_MATO - RIM_R, 0.0)], False)        # 後の輪
    polar(bm, uvl, [(Y0, ri, 0.0), ((Y0 + TH / 2) / 2, ri * 0.99, 0.0),
                    (TH / 2, ri, 0.0)], False)                                       # 内壁
    return finish(bm, "suwaku")


def link(me, name, glow=False, smooth=0.60):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat_body)          # slot 0 ＝ 黒（紙・枠）
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


parts = []
for i, (x, y, z, hoop, b, ph, bp) in enumerate(MATOS):
    if hoop:
        ob = link(build_hoop(), "suwaku_%d" % (i + 1))
    else:
        ob = link(build_mato(), "mato_%d" % (i + 1), glow=True)
    ob.rotation_mode = 'XYZ'
    ob.location = (x, y, z)
    parts.append(ob)

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, idx in enumerate(FR):
    t = idx / N_FRAMES
    for i, ob in enumerate(parts):
        x, y, z = MATOS[i][0], MATOS[i][1], MATOS[i][2]
        ob.location = (x, y, z + bob(i, t))
        ob.rotation_euler = (0.0, 0.0, theta(i, t))
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
        caption("MIDDLE STUDY 071 — MATO", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
# 🔴 #67①：素枠が抜けている＋個体のあいだが白く抜けている＝面光源が素通しで写る
back.visible_camera = False

# 🔴 #58③：随伴のライム光源は**発光体の外**。的の奥、床すれすれに置いて床帯へ届かせる
for sx, sy, sz, w in ((-0.85, 6.5, 0.28, LIME_W), (0.35, 10.0, 0.28, LIME_W),
                      (1.45, 15.0, 0.28, LIME_W)):
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
cam.data.dof.focus_distance = 8.55     # 群の重心（y≒+0.25）
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
        gx0 = min(gx0, min(xs)); gx1 = max(gx1, max(xs))
        gy0 = min(gy0, min(ys)); gy1 = max(gy1, max(ys))
    print(">> 群 bbox x %.3f..%.3f  y %.3f..%.3f  → 長辺 %.1f%%"
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_071.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_em = bpy.data.materials.new("zuboshi_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.40
    for ob in parts:
        if len(ob.data.materials) > 1:
            ob.data.materials[1] = m_em
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
