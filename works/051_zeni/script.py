# =============================================================
# monaka design. — MIDDLE STUDY 051 "ZENI"（銭 / a holed coin）
#
# 黒い銭が一枚、宙にある。真ん中は、空いている。
# その四角い空から、ライムの光がまっすぐこちらへ抜けてくる。
# 銭がゆっくり首を振ると、真ん中の光は細くなり、代わりに縁のまわりが明るくなる。
# **真ん中の光は、正面を向いたときにだけ見える。**
#
# 【ドメイン】貨幣・銭（シリーズ未踏）。直近10作（玩具・けん玉／武・弓／農・製粉／商い・暖簾／
#   書物・巻子／土木・橋／建築・寺社／虫・生命／工芸・繕い／植物・竹）と別。
#
# 【光の型＝背光】#53 で新設した8型のうち、50作でわずか2作（012 蝕・035 櫛）しか無い型。
#   041〜050 は10作中8作が「隙間」に収束していた（黒い塊に細い光が1本）。
#   #51 の「光が基準期の1/3まで痩せた」はその結果でしかない——
#   **細い線で出す限り、ライム面積も halo も上がりようがない。**
#   だから 051 は #51④ の処方（面で出す・透過させる）を正面から採る：
#   被写体より大きな発光円盤を真後ろに置き、黒い銭を**逆光のシルエット**として立てる。
#
# 【機構＝首振りによる二重の反転】銭の首振り φ(t) = PHI0 + A·sin(2πt)（整数周期・厳密に閉じる）。
#   正面：真ん中の孔が全開＝**中心の光は最大**／縁のコロナは最小
#   斜め：孔が foreshorten して細り、代わりに**縁の光が増える**
#   ＝ひとつの機構が、中心の光と外周の光を**逆向きに**動かす（#44：機構が光を変える）。
#   回転キーだけなので glb にそのまま乗る（#25c／#30）。
#
# 【造形】方孔円銭。boolean 不使用——**四角（孔）から円（外周）へ張るクアッド格子**で、
#   両面に郭（かく＝縁の盛り上がり）を持つ閉じたソリッドとして一発で組む（#15／#37②）。
#   郭ふたつと四角い孔が「座金でなく銭」を宣言する（#33：型が読みを支配する）。
#
# 🔴 #40⑥ は幾何で積分する（#46）。Blender を起動せず --probe-only で解ける。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 銭（寛永通宝の比から起こす：径24.5mm・厚1.3mm・方孔7mm＝径の0.28）------------
# 🔴 比は実物から起こす（#50）。ここで決めるのは比だけで、画面占有は S で決める。
R_OUT = 0.780          # 外径
T_HALF = 0.046         # 厚みの半分
HH = 0.223             # 方孔の半幅（HH/R_OUT = 0.286＝実物の 7mm/24.5mm）
RIM_H = 0.024          # 郭の高さ（両面とも）
RIM_OUT = 0.90         # 外郭が始まる u（0=孔・1=外周）
RIM_IN = 0.11          # 内郭が終わる u
SQ_ROLL = math.radians(6.0)   # 孔と銘をわずかに傾ける＝鋳物の手仕事／完全な4回対称を崩す（#48）
NSEG, NRAD = 168, 26   # 角度分割・半径分割

# --- 銘（寛永通寳）。上→下→右→左 の順に読む -------------------
USE_KANJI = True
# 🔴 旧字（寬／寶）を使う。鋳造銭の実物も旧字で、かつ AppleMyungjo（明朝系）は
#    新字の「寛」「寳」を持っておらず、**無言で .notdef の□に差し替える**（6周目で発覚）。
KANJI = ["寬", "永", "通", "寶"]          # 上・下・右・左
KANJI_R = 0.500        # 字の中心までの距離
KANJI_SIZE = 0.360
KANJI_EX = 0.015       # 浮き彫りの高さ（黒の肌は実ジオメトリで作る＝#52）
# 🔴 Arial Unicode は和文が**ゴシック**で、鋳造銭の楷書に見えない（5周目）。
#    macOS に和文の明朝は入っていないが、AppleMyungjo（明朝系）は漢字を持っている。
JP_FONT = "/System/Library/Fonts/Supplemental/AppleMyungjo.ttf"
JP_FONT_FALLBACK = "/Library/Fonts/Arial Unicode.ttf"

# --- 発光円盤（真後ろ・被写体より大きい＝背光の本体）------------
RD = 1.00              # 円盤の半径（ここで 0 まで落ちる）
Y_BACK = 0.46          # 銭の面からの奥行き
ES_CORE = 2.5          # 地の発光
GPOW = 1.20            # 勾配のべき（#38④：小さいほど中間調が広い）
# 🔴 #24：勾配が「透明度」だけだと、孔から見える範囲（r<0.31）はほぼ平らな面になり、
#    光でなく**ライムのペンキ板**になる（実測 std 32.4 < 35 で不合格・3周目）。
#    透明度（＝どこまで光が広がるか）と発光の強さ（＝芯の白飛び）を**別の勾配で持つ**。
HOT_R = 0.30           # ホットコアの半径（孔の半幅 0.223 より少し外）
HOT_MUL = 1.5          # 芯で発光を何倍にするか（2.2 は芯が白黄色に飛んだ＝中間調 #D3FD9B）

# --- 首振り ---------------------------------------------------
PHI0 = math.atan2(0.55, 8.3)      # カメラへ正対する yaw（カメラは x=+0.55 にいる）
# 🔴 振り幅を落とすのではなく、**片側だけに振る**（8周目）。
#    平らな板を 60° 超で見ると斜入射のフレネルで、材質に関係なく明るい studio を鏡のように映し、
#    黒い銭が**銀色の板**に転ぶ（metal 0.55→0.80 でも消えなかった＝材質でなく角度の問題）。
#    ただし実測すると **+65.8° は銀色に飛ぶのに −58.2° は黒いまま**＝鏡の向く先が違うだけだった。
#    振り幅を狭めると #40⑥ が 0.742 まで悪化して機構が光を動かさなくなるので、
#    **安全な側（key 側＝負）へ片振りにする**。cos なので t=0/t=1 は厳密に一致＝完全ループ。
AMP = math.radians(62.0)          # 振り幅（片側）

FPS = 24
N_FRAMES = 120
CAM_LOC = (0.55, -8.3, 1.95)
CENTER_Z = 2.10        # 銭の中心（キャプション上端 0.95 とのクリアランスを確保）
LOOK_Z = 1.90
AIM_X = 0.0

# --- 全体倍率：比は上で決め、ここでは**画面占有だけ**を決める（長辺 55〜65%・#51③）---
S = 1.06
R_OUT, T_HALF, HH, RIM_H, KANJI_R, KANJI_SIZE, KANJI_EX, RD, Y_BACK, HOT_R = [
    v * S for v in (R_OUT, T_HALF, HH, RIM_H, KANJI_R, KANJI_SIZE, KANJI_EX, RD, Y_BACK, HOT_R)]


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）。
# 首振り・#40⑥ の遮蔽積分・hero 位相の選択は、シーンを組まずにここで解ける。
# =============================================================
def phi(i):
    """銭の yaw。正面から key 側へ振れて戻る片振り。cos の整数周期＝完全ループ。"""
    return PHI0 - AMP * 0.5 * (1.0 - math.cos(2 * math.pi * (i % N_FRAMES) / N_FRAMES))


def tilt(i):
    """カメラ正対からのズレ（絶対値）。"""
    return abs(phi(i) - PHI0)


def es_at(r):
    """発光円盤のシェーダと同一の式。透明度の勾配 × 芯の勾配（POWER → MapRange SMOOTHSTEP）。"""
    ss = lambda t: t * t * (3.0 - 2.0 * t)
    fac = 1.0 - ss(min(1.0, max(0.0, (r / RD) ** GPOW)))
    hot = 1.0 - ss(min(1.0, max(0.0, r / HOT_R)))
    return fac * ES_CORE * (1.0 + HOT_MUL * hot)


def _coin_frame(p):
    """yaw φ の銭の中心・法線・面内2軸。"""
    c = (0.0, 0.0, CENTER_Z)
    n = (math.sin(p), -math.cos(p), 0.0)          # 正面（-Y 方向）を向く法線
    u = (math.cos(p), math.sin(p), 0.0)           # 面内の水平軸
    v = (0.0, 0.0, 1.0)
    return c, n, u, v


def _hit_coin(P, p):
    """P → カメラ の線分が銭に遮られるか。戻り: 0=素通り / 1=銭が遮る / 2=方孔を抜ける。"""
    c, n, u, v = _coin_frame(p)
    d = (CAM_LOC[0] - P[0], CAM_LOC[1] - P[1], CAM_LOC[2] - P[2])
    dn = d[0] * n[0] + d[1] * n[1] + d[2] * n[2]
    if abs(dn) < 1e-9:
        return 0
    w = (c[0] - P[0], c[1] - P[1], c[2] - P[2])
    s = (w[0] * n[0] + w[1] * n[1] + w[2] * n[2]) / dn
    if not (0.0 < s < 1.0):
        return 0
    X = (P[0] + s * d[0], P[1] + s * d[1], P[2] + s * d[2])
    e = (X[0] - c[0], X[1] - c[1], X[2] - c[2])
    a = e[0] * u[0] + e[1] * u[1] + e[2] * u[2]
    b = e[2] * v[2]
    if a * a + b * b > R_OUT * R_OUT:
        return 0
    # 孔は SQ_ROLL だけ傾いている
    ca, sa = math.cos(SQ_ROLL), math.sin(SQ_ROLL)
    aa, bb = a * ca + b * sa, -a * sa + b * ca
    if abs(aa) <= HH and abs(bb) <= HH:
        return 2
    return 1


def glow_split(i, nr=40, nph=96):
    """#40⑥：見える発光量を「孔を抜ける分（＝真ん中の光）」と「縁のまわり（コロナ）」に分けて積む。"""
    p = phi(i)
    hole = corona = 0.0
    for a in range(nr):
        r = RD * (a + 0.5) / nr
        e = es_at(r)
        if e <= 1e-6:
            continue
        dA = (RD / nr) * r * (2 * math.pi / nph)
        for b in range(nph):
            th = 2 * math.pi * (b + 0.5) / nph
            P = (r * math.cos(th), Y_BACK, CENTER_Z + r * math.sin(th))
            h = _hit_coin(P, p)
            if h == 1:
                continue
            if h == 2:
                hole += e * dA
            else:
                corona += e * dA
    return hole, corona


_G = [glow_split(i) for i in range(N_FRAMES)]
_AS = [h + c for (h, c) in _G]
_HS = [h for (h, c) in _G]
_AMAX, _HMAX = max(_AS), max(_HS)

# --- hero 位相（#48-c：単一指標で選ばない）---------------------
#   ① 真ん中の光がほぼ全開（正面）× ② 板でなく「厚みのある一枚」に見えるだけの傾き
#   🔴 傾きは**符号つき**で選ぶ。ライトは不変条件なので動かせない以上、
#      銭の面を key（x=−4）側へ向けないと、正対した黒い面は鏡面を1つも拾わず
#      郭も銘も出ない＝「影絵」になる（#45／2周目で発覚）。
PHI_HERO = math.radians(-16.0)
_SC = [(_HS[i] / _HMAX) * math.exp(-((phi(i) - PHI_HERO) / math.radians(6.0)) ** 2)
       for i in range(N_FRAMES)]
STILL_FRAME = max(range(N_FRAMES), key=lambda i: _SC[i]) + 1


# --- 銭の外形（占有プローブ用）--------------------------------
def coin_extent(i):
    """画面上の見かけの幅・高さ（銭のみ）と、発光円盤まで含めた幅・高さ。"""
    w_coin = 2 * R_OUT * abs(math.cos(phi(i) - PHI0))
    w_coin = max(w_coin, 2 * T_HALF)
    return w_coin, 2 * R_OUT, 2 * RD * (8.3 / (8.3 + Y_BACK)), 2 * RD * (8.3 / (8.3 + Y_BACK))


if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d  （傾き %.1f°・真ん中の光 %.0f%%・全光量 %.0f%%）"
          % (STILL_FRAME, math.degrees(tilt(STILL_FRAME - 1)),
             100 * _HS[STILL_FRAME - 1] / _HMAX, 100 * _AS[STILL_FRAME - 1] / _AMAX))
    print(">> #40(6) 見える発光量 min/max = %.3f  （合格 0.75以下）" % (min(_AS) / _AMAX))
    print(">> 機構が光を「逆向きに」動かしているか（#44）")
    for i in range(0, N_FRAMES // 4 + 1, 5):
        print("   t=%.3f  傾き %5.1f°   真ん中 %5.0f%%   コロナ %5.0f%%   合計 %5.0f%%"
              % (i / N_FRAMES, math.degrees(tilt(i)), 100 * _HS[i] / _HMAX,
                 100 * _G[i][1] / max(c for (h, c) in _G), 100 * _AS[i] / _AMAX))
    wc, hc, wg, hg = coin_extent(STILL_FRAME - 1)
    print(">> 占有  銭 横%.0f%% 縦%.0f%%  ／ 発光まで含む 横%.0f%% 縦%.0f%%（フレーム 横2.81・縦3.52）"
          % (wc / 2.81 * 100, hc / 3.52 * 100, wg / 2.81 * 100, hg / 3.52 * 100))
    print(">> クリアランス  発光の下端 z=%.3f（キャプション上端 0.95）  銭の下端 z=%.3f"
          % (CENTER_Z - RD, CENTER_Z - R_OUT))
    print(">> 孔の抜け  最大傾き %.0f° で有効開口 %.3f（正面 %.3f・塞がらないこと）"
          % (math.degrees(AMP), 2 * HH * math.cos(AMP) - 2 * T_HALF * math.sin(AMP), 2 * HH))
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
    "touki":  dict(rough=0.58, spec=0.26, disp=0.006, dsize=0.10),
    "nuno":   dict(rough=0.80, spec=0.20, sheen=0.55, sheen_rough=0.25, disp=0.004, dsize=0.05),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
}
RECIPE = "tetsu"        # 銭＝鋳物（鋳造の地肌）
# 🔴 metal 0.35 のままだと、カメラに正対する平らな面が明るいグレー環境（0.92）を面で映して
#    黒平均 50.6＝**灰色の板**になった（3周目実測・健全域 14〜52 の上限すれすれ）。
#    #45 の「Specular を落とす」方向へは振らない（影絵になる）。動かすのは金属度。
# 🔴 ただし向きが逆だった：metal を 0.35→0.18 に**下げたら黒平均は 55.3 に上がった**（4周目）。
#    金属の反射はベースカラーで色が付く＝#0a0a0a の金属はグレー環境を映しても黒いまま。
#    誘電体の鏡面（metal 低）は**白いヴェール**を返す。平らな面を正対させる題材では効き方が逆になる。
#    さらに 0.55 でも、振り切った位相で rim（3.5,4,3.2）の鏡面が**面ごと銀色に光った**（7周目・#47）。
#    誘電体の鏡面は白いので、金属度を上げて「黒い金属＝自分の色で反射する」側へ寄せると消える。
#    🔴 ただし 0.80 まで上げると今度は黒 p98 47＝**影絵**で不合格（#45）。金属度は両側にガードが要る。
#    実測：0.18→平均55.3（灰色の板）／0.55→平均43.7・p98 67.3（合格）／0.80→p98 47.4（影絵）。
BLACK_RECIPES["tetsu"]["metal"] = 0.55


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def black_material(name, recipe):
    r = BLACK_RECIPES[recipe]
    m, p = principled(name)
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]      # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r.get("coat_rough", 0.1)
    return m


mat_coin = black_material("coin", RECIPE)

# 孔の内壁＝純黒（#40④a：窓の内壁が拾う光は緑の環になる）
mat_bore, bo = principled("bore")
bo.inputs["Base Color"].default_value = (0, 0, 0, 1)
bo.inputs["Roughness"].default_value = 0.85
bo.inputs["Specular IOR Level"].default_value = 0.0


def back_glow(name):
    """背光の本体。Emission と Transparent を勾配で混ぜる。
       🔴 #49①：白い背景の前に置いた「ES=0 の面」は裏当てにならず**黒い板**になる。
       ES を 0 に落とすだけでは縁に黒い輪が出るので、**縁は透明そのものにして消す**。
       円盤は回らないので座標は Object でよい（#35：回るものだけ UV に焼く）。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = LIME
    em.inputs["Strength"].default_value = ES_CORE
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    x2, z2 = mn('POWER', 2.0), mn('POWER', 2.0)
    nt.links.new(sep.outputs["X"], x2.inputs[0]); nt.links.new(sep.outputs["Z"], z2.inputs[0])
    ad = mn('ADD'); nt.links.new(x2.outputs[0], ad.inputs[0]); nt.links.new(z2.outputs[0], ad.inputs[1])
    rr = mn('SQRT'); nt.links.new(ad.outputs[0], rr.inputs[0])
    dv = mn('DIVIDE', RD); nt.links.new(rr.outputs[0], dv.inputs[0])
    pw = mn('POWER', GPOW); nt.links.new(dv.outputs[0], pw.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = 1.0; mr.inputs["To Max"].default_value = 0.0
    mr.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(pw.outputs[0], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mx.inputs["Fac"])

    # 芯（#24）：透明度とは別の勾配で発光の強さを持ち上げる。
    # ここが無いと孔から見える範囲が平らな面になり、光でなくペンキになる。
    hr = nt.nodes.new("ShaderNodeMapRange")
    hr.inputs["From Min"].default_value = 0.0; hr.inputs["From Max"].default_value = HOT_R
    hr.inputs["To Min"].default_value = HOT_MUL; hr.inputs["To Max"].default_value = 0.0
    hr.interpolation_type = 'SMOOTHSTEP'
    hr.clamp = True
    nt.links.new(rr.outputs[0], hr.inputs["Value"])
    ad2 = mn('ADD', 1.0); nt.links.new(hr.outputs["Result"], ad2.inputs[0])
    ml = mn('MULTIPLY', ES_CORE); nt.links.new(ad2.outputs[0], ml.inputs[0])
    nt.links.new(ml.outputs[0], em.inputs["Strength"])
    return m, em


mat_glow, glow_node = back_glow("back_glow")

mat_floor, fp = principled("floor")
fp.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp.inputs["Roughness"].default_value = 0.42
mat_text, tp = principled("text")
tp.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
def sq_pt(th):
    """SQ_ROLL だけ傾いた正方形（半幅 HH）の、角度 th の点。"""
    a = th - SQ_ROLL
    k = HH / max(abs(math.cos(a)), abs(math.sin(a)))
    return (k * math.cos(a) * math.cos(SQ_ROLL) - k * math.sin(a) * math.sin(SQ_ROLL),
            k * math.cos(a) * math.sin(SQ_ROLL) + k * math.sin(a) * math.cos(SQ_ROLL))


def rim_z(u):
    """郭のプロファイル。孔の縁（内郭）と外周（外郭）が盛り上がり、あいだの田は低い。"""
    sm = lambda t: t * t * (3 - 2 * t)
    if u <= RIM_IN - 0.05:
        return RIM_H
    if u < RIM_IN + 0.02:
        return RIM_H * (1.0 - sm((u - (RIM_IN - 0.05)) / 0.07))
    if u < RIM_OUT - 0.02:
        return 0.0
    if u < RIM_OUT + 0.05:
        return RIM_H * sm((u - (RIM_OUT - 0.02)) / 0.07)
    return RIM_H


def build_coin():
    """方孔円銭。四角（孔）→円（外周）へ張るクアッド格子＋両面の郭＋外周壁＋孔の内壁。
       boolean を使わない（#15／#37②：閉じた多様体として一発で作る）。"""
    bm = bmesh.new()
    us = [k / (NRAD - 1) for k in range(NRAD)]
    rings = {}                                    # (side, ui) -> [verts]
    for side in (+1, -1):
        for ui, u in enumerate(us):
            row = []
            for k in range(NSEG):
                th = 2 * math.pi * k / NSEG
                ix, iy = sq_pt(th)
                ox, oy = R_OUT * math.cos(th), R_OUT * math.sin(th)
                x, y = ix + (ox - ix) * u, iy + (oy - iy) * u
                z = side * (T_HALF + rim_z(u))
                row.append(bm.verts.new((x, y, z)))
            rings[(side, ui)] = row
    for side in (+1, -1):
        for ui in range(NRAD - 1):
            A, B = rings[(side, ui)], rings[(side, ui + 1)]
            for k in range(NSEG):
                q = (A[k], A[(k + 1) % NSEG], B[(k + 1) % NSEG], B[k])
                bm.faces.new(q if side > 0 else tuple(reversed(q)))
    # 外周の壁
    A, B = rings[(+1, NRAD - 1)], rings[(-1, NRAD - 1)]
    for k in range(NSEG):
        bm.faces.new((A[k], B[k], B[(k + 1) % NSEG], A[(k + 1) % NSEG]))
    # 孔の内壁（材質スロット1＝純黒）
    A, B = rings[(+1, 0)], rings[(-1, 0)]
    bore = []
    for k in range(NSEG):
        bore.append(bm.faces.new((A[k], A[(k + 1) % NSEG], B[(k + 1) % NSEG], B[k])))
    for f in bore:
        f.material_index = 1
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    sharp = []
    for e in bm.edges:
        try:
            if e.calc_face_angle() > math.radians(35):
                sharp.append(e)
        except Exception:
            pass
    if sharp:                                     # #17：稜線が光を拾わないと黒はプラスチックになる
        bmesh.ops.bevel(bm, geom=sharp, offset=0.0035, segments=2,
                        affect='EDGES', clamp_overlap=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("coin")
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("coin", me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat_coin)
    me.materials.append(mat_bore)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.5)
    except Exception:
        pass
    ob.select_set(False)
    return ob


coin = build_coin()

# --- 銘（浮き彫り）。黒の上で読めるのは実ジオメトリだけ（#52）-------------
kanji_objs = []
MIN_GLYPH_VERTS = 48      # 🔴 .notdef の□は 8〜16 頂点。実際の漢字は数百ある


def build_kanji(path):
    """1書体で銘4字を組む。1字でも .notdef なら**全部捨てて False を返す**。
       🔴 フォントに無い字は例外を出さず、**無言で□に差し替わる**（6周目・AppleMyungjo の寛／寳）。
       #54 と同じ構造の事故＝失敗が沈黙するので、頂点数で明示的に検算する。"""
    try:
        font = bpy.data.fonts.load(path)
    except Exception as e:
        print(">> ⚠️ 和文フォントの読み込みに失敗:", path, e)
        return [], False
    pos = [(0.0, KANJI_R), (0.0, -KANJI_R), (KANJI_R, 0.0), (-KANJI_R, 0.0)]
    made, ok = [], True
    for ch, (px, py) in zip(KANJI, pos):
        bpy.ops.object.text_add(location=(0, 0, 0))
        tx = bpy.context.active_object
        tx.name = "kanji_" + ch
        tx.data.body = ch
        tx.data.font = font
        tx.data.size = KANJI_SIZE
        tx.data.align_x = 'CENTER'
        tx.data.align_y = 'CENTER'
        tx.data.extrude = KANJI_EX * 0.5
        tx.data.bevel_depth = 0.0018
        tx.data.materials.append(mat_coin)
        bpy.ops.object.convert(target='MESH')
        tx = bpy.context.active_object
        nv = len(tx.data.vertices)
        if nv < MIN_GLYPH_VERTS:
            print(">> ⚠️ グリフが無い（□に差し替わった）: %s  頂点 %d  in %s"
                  % (ch, nv, os.path.basename(path)))
            ok = False
        c, s = math.cos(SQ_ROLL), math.sin(SQ_ROLL)
        tx.location = (px * c - py * s, px * s + py * c, T_HALF + KANJI_EX * 0.5)
        tx.rotation_euler = (0.0, 0.0, SQ_ROLL)
        made.append(tx)
    if not ok:
        for o in made:
            bpy.data.objects.remove(o, do_unlink=True)
        return [], False
    print(">> 銘の書体:", os.path.basename(path))
    return made, True


if USE_KANJI:
    for _p in (JP_FONT, JP_FONT_FALLBACK):
        kanji_objs, _ok = build_kanji(_p)
        if _ok:
            break
    print(">> 銘 %d 字を配置" % len(kanji_objs))

# --- 黒の肌は実ジオメトリで作る（#52）。🔴 Catmull-Clark は郭の稜線を丸めるので SIMPLE ---
_r = BLACK_RECIPES[RECIPE]
tex = bpy.data.textures.new("relief_" + RECIPE, 'CLOUDS')
tex.noise_scale = 0.04
sub = coin.modifiers.new("sub", 'SUBSURF')
sub.subdivision_type = 'SIMPLE'
sub.levels = sub.render_levels = 1
dsp = coin.modifiers.new("disp", 'DISPLACE')
dsp.texture = tex
dsp.strength = 0.0016                             # 🔴 表の 0.012 は「鋳肌」でなく「アスファルト」になった（1周目）
dsp.mid_level = 0.5

# --- リグ：銭と銘をまとめて首を振らせる（親を付けてから動かす＝matrix_parent_inverse 不使用・#16）---
rig = bpy.data.objects.new("rig", None)
bpy.context.collection.objects.link(rig)
rig.location = (0.0, 0.0, CENTER_Z)
for o in [coin] + kanji_objs:
    o.parent = rig
FR = list(range(N_FRAMES)) + [0]                  # 末尾に折り返し＝glb でループが閉じる
for f, i in enumerate(FR):
    # XYZ順＝Rz(φ)·Rx(+90°)：立ててから振る。
    # 🔴 Rx(−90°) だと法線が +Y＝**カメラと反対**を向き、銘と郭が裏側に回って消える（2周目で発覚）。
    # しかも黒一色なので「文字が無い」ではなく「文字を作り忘れた」ようにしか見えない。
    rig.rotation_euler = (math.pi / 2, 0.0, phi(i))
    rig.keyframe_insert("rotation_euler", frame=f + 1)

# --- 発光円盤（背光の本体）------------------------------------
bm = bmesh.new()
cen = bm.verts.new((0.0, 0.0, 0.0))
ring = [bm.verts.new((RD * math.cos(2 * math.pi * k / 128), 0.0,
                      RD * math.sin(2 * math.pi * k / 128))) for k in range(128)]
for k in range(128):
    bm.faces.new((cen, ring[k], ring[(k + 1) % 128]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("glow"); bm.to_mesh(me); bm.free()
glow = bpy.data.objects.new("glow", me)
bpy.context.collection.objects.link(glow)
glow.location = (0.0, Y_BACK, CENTER_Z)
glow.data.materials.append(mat_glow)
glow.visible_shadow = False                       # 白い床に影を落とさない

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


caps = [caption("Designing the Middle of Your Story.", 0.1, (AIM_X, -1.7, 0.85), "tagline"),
        caption("monaka design.", 0.06, (AIM_X, -1.7, 0.68), "logo"),
        caption("MIDDLE STUDY 051 — ZENI", 0.045, (AIM_X, -1.7, 0.57), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0, 0, CENTER_Z)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = coin
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
back.light_linking.receiver_collection = lit      # 🔴 データでなくオブジェクト側にある

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
    """🔴 #54：try で包まない。50作は 'BLOOM' の TypeError を握りつぶして既定の Streaks で出ていた。
       2026-08-13 Ryota決定＝Streaks 続投（これが MIDDLE STUDIES の光）。"""
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
    print(">> #40(6) 見える発光量 min/max = %.3f （合格 0.75以下）" % (min(_AS) / _AMAX))
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, zs = [], []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name in ("floor", "glow"):
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            w = ev.matrix_world @ v.co
            xs.append(w.x); zs.append(w.z)
    print(">> BBOX(銭)  x %.3f..%.3f (%.3f)  z %.3f..%.3f (%.3f)" %
          (min(xs), max(xs), max(xs) - min(xs), min(zs), max(zs), max(zs) - min(zs)))
    print(">> 占有(銭)  横%.0f%%  縦%.0f%%   キャプション上端 0.95 とのクリアランス %.3f" %
          ((max(xs) - min(xs)) / 2.81 * 100, (max(zs) - min(zs)) / 3.52 * 100, min(zs) - 0.95))

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_051.blend"))

# 🔴 glb は必ず最後（#30：Emission を定数へ潰すので、レンダーの前に置かない）
if "glb" in modes:
    m2, p2 = principled("glow_flat")
    p2.inputs["Base Color"].default_value = (0, 0, 0, 1)
    p2.inputs["Emission Color"].default_value = LIME
    p2.inputs["Emission Strength"].default_value = 2.6
    glow.data.materials.clear()
    glow.data.materials.append(m2)
    scene.frame_end = N_FRAMES + 1
    names = {"coin", "glow"} | {o.name for o in kanji_objs}
    for o in bpy.data.objects:
        o.select_set(o.name in names or o is rig)
    bpy.context.view_layer.objects.active = coin
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
