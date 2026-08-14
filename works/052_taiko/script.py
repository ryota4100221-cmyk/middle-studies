# =============================================================
# monaka design. — MIDDLE STUDY 052 "TAIKO"（太鼓 / 宮太鼓 a Japanese barrel drum）
#
# 黒い太鼓が宙にある。皮のちょうど真ん中に、ライムの光がある。
# 皮が震えるたび、光は真ん中でふくらみ、輪になって外へ逃げ、また真ん中へ戻る。
# **いちばん低く、いちばん遠くまで届くのは、真ん中を打ったときだけ。**
#
# 【ドメイン】楽器・打／和太鼓（シリーズ未踏）。直近10作（貨幣・銭／玩具・けん玉／武・弓／
#   農・製粉／商い・暖簾／書物・巻子／土木・橋／建築・寺社／虫・生命／工芸・繕い）と別。
#   021 FUE は管、032 SUZU は鳴り物で、どちらも「膜が鳴る」機構ではない。
#
# 【光の型＝面】#53 の8型のうち 51作で3作しか無い最少の型（023 器／028 円相／030 蜂の巣）。
#   直近5作に出ている 隙間／芯／背光 は選べない。**光る面そのものが正面に見える**型を採る。
#
# 【構図＝端寄せ】🔴 #57：51作すべてが「1個の物が丸ごと枠の中央」＝図鑑の構図だった。
#   052 は**シリーズで初めて被写体を枠の中央から外す**。太鼓を画面左（重心 x≒35%）に置き、
#   打面を右の余白へ向ける。カメラ（85mm・(0.55,-8.3,1.95)）は不変条件なので動かさない——
#   動かすのは**被写体をどこに置くか**だけ。
#
# 【機構＝膜の定在波（standing wave on a clamped circular membrane）】シリーズ初の「振動」。
#   円形膜の固有モードは第1種ベッセル関数 J0 で、縁で 0 になる（＝皮は縁で留められている）。
#     w(u,t) = A1·J0(λ1·u)·cos(2πt) + A2·J0(λ2·u)·cos(4πt)      u = r/R（λ1=2.404826, λ2=5.520078）
#   どちらも整数周期なので t=0 と t=1 が厳密に一致＝完全ループ。シェイプキー2枚だけなので
#   glb に morph target としてそのまま乗る（#60 の「動きが入っていない」を構造的に回避）。
#
# 🔴 光は**変位そのもの**。シェーダに時間のキーを1本も打たない——
#   Geometry→Position を Object 空間へ戻し、色属性に焼いた「変位前の z」との差 d を取って
#   ES = ES0·profile(u)·clamp(1 + KD·d/A1) とする。**皮が持ち上がったところが明るい。**
#   （#54 の教訓の一般形＝時間を二重に持つと、いつか片方だけズレる。持ち場を1つにする）
#
# 🔴 #40⑥ は幾何で積分する（#46）。Blender を起動せず --probe-only で解ける。
#
# 実行: Blender --background --factory-startup --python script.py -- <modes>
#   modes: probe | test | testhero | still | phases | anim | blend | glb
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 太鼓（宮太鼓の比から起こす：胴長 ≒ 面径×1.2・胴の腹は面径の1.2倍）------------
# 🔴 比は実物から起こす（#50）。ここで決めるのは比だけで、画面占有は下の実測で詰める。
R_H = 0.550            # 胴の端（＝面）の半径
R_B = 0.760            # 胴の腹（いちばん太いところ）の半径（腹/端 = 1.38）
L = 1.260              # 胴長（2周目：1.32 は寸胴で、光る蓋つきの**カプセル**に読めた）
R_HD = 0.605           # 皮の半径（胴の端より 10% 広い＝耳が鉢を包む）
DOME = 0.045           # 皮の張りの膨らみ
SKIN_TH = 0.020        # 皮の厚み（閉じた薄板にする＝#37②）
UA = 0.860             # 皮のうち「面」の範囲（これより外は耳＝下へ折れる）
SKIRT = 0.170          # 耳の落ち

N_BYOU = 24            # 鋲の数
R_BYOU = 0.027         # 鋲の頭の半径
Z_BYOU = 0.495         # 鋲を打つ高さ（皮の耳の縁）

KAN_R = 0.105          # 環（かん）の輪の半径
KAN_T = 0.015          # 環の太さ
ZA_R = 0.062           # 座金の半径

# --- 定在波 ---------------------------------------------------
LAM1 = 2.404825557695773      # J0 の第1零点＝基本モード（縁で 0）
LAM2 = 5.520078110286311      # 第2零点＝1つ内側に節の輪を持つモード
A1 = 0.044             # 基本モードの振幅
# 🔴 2周目の実測：A2/A1=0.46 では**内側に暗い輪が立つ位相が 120 中 22 しか無く**、
#    しかも hero に選ばれるのは輪の無い t=0（一様な発光の塊＝ただのランプ）だった。
#    0.95 まで上げると輪の立つ位相が 34 に増え、輪の深さも 0.27→0.44 になる。
#    **定在波の節は、この作品で唯一「光が現象である」ことを見せる線**なので、配合で作る。
A2 = 0.042             # 第2モードの振幅（節の輪＝u=0.44 に暗い線が立つ）
# 🔴 光は変位の**向き**ではなく**量**（＝|d|）に結ぶ。
#   符号のまま結ぶと、基本モードが凹む t=0.33〜0.67 が丸ごと 30% の暗いプラトーになり、
#   ループの3分の1が「何も起きていない時間」になった（1周目の probe 実測）。
#   |d| なら、皮がふくらんだときも凹んだときも光る＝**光は、皮が動いた量そのもの**。
#   モードごとに零点の位相が違うので、全域が同時に 0 になる瞬間は無い＝消灯しない。
KA = 1.10              # |d|/A1 に掛ける
BASE = 0.34            # 動いていないところの地の明るさ
ENV_LO, ENV_HI = 0.10, 2.40   # 発光の包絡のクランプ（負にしない／飛ばさない）

# --- 光（面）--------------------------------------------------
# 🔴 5周目：勾配を平らにした（GPOW 4.0）分だけ光が薄くなり、halo が hero 換算で 10,500＝
#    合格ライン 9,000 のすぐ上、中間調も #8BC00E（#A5E02E より暗く緑寄り）に落ちた。
#    輪は**比の谷**なので明るさを上げても消えない。上げるのは地の発光、下げるのは芯の倍率。
ES_CORE = 2.6          # 地の発光（1周目の 3.0 は芯が白く飛んで**輪が1本も読めなかった**）
# 🔴 3周目で分かった一番大事なこと：**静的な勾配が急だと、定在波の節が絵に出ない。**
#    GPOW 1.75 では u=0.44 の節（env 0.38・まわり 0.73＝48%の谷）が、
#    プロファイル側の落ち込み（0.52→0.075）に呑まれて「ただの中心グラデ」に潰れていた。
#    べきを上げると**中心から UG 手前までが平らな高原になり、縁で一気に落ちる**ので、
#    画面のコントラストを作る主役が profile から env（＝皮の動き）へ入れ替わる。
#    ここはシリーズの他作と逆向きの調整で、**光が現象であることを見せるための配分**。
GPOW = 4.00            # 勾配のべき（大きいほど高原が広く、縁が急）
UG = 0.760             # 光が皮を占める範囲（これより外は黒い皮に戻る）
HOT_U = 0.200          # ホットコアの u（#24：透明度と発光の強さを別の勾配で持つ）
HOT_MUL = 0.35         # 芯で発光を何倍にするか

# --- 配置（🔴 #57「端寄せ」）----------------------------------
FPS = 24
N_FRAMES = 120
CAM_LOC = (0.55, -8.3, 1.95)
# 🔴 5周目：-0.39 だと compositions.py --verify が **38.1%** で落ちた（端寄せの条件は 38.0% 以下）。
#    probe の投影bbox の中点は 35.9% で「入っている」ように見えたが、
#    measure の重心は**暗い画素とライム画素の平均**なので、右へ広がるブルームの分だけ中央へ寄る。
#    🔴 bbox の中点と重心は別物。構図の合否は必ず hero を --verify に通して確かめる。
DRUM_X = -0.49         # 🔴 中央から外す。フレーム横 2.81 なので重心は左から約35%
DRUM_Z = 1.95
LOOK_Z = 1.92
AIM_X = 0.0            # キャプションは枠の中央のまま＝被写体だけが左に寄る
# 🔴 1周目は 26.7°（視線となす角 20°）で組んだが、胴の長さが見えず **鍋・バケツ**に読めた。
#    打面を主役にしたまま「胴のある物」に読ませるには、視線となす角が 30°台は要る（#33：型が読みを支配する）。
PSI = math.radians(40.5)   # 胴の首振り（打面を右の余白へ向ける）。視線とのなす角は 34°

# --- 全体倍率：比は上で決め、ここでは**画面占有だけ**を決める（長辺 55〜65%・#51③）---
# 🔴 面積で測らない。長辺で測る（#51③）。probe の投影bboxで実測して詰めた（2周目・首を振った分だけ横に伸びるので縮めた）
S = 0.99
R_H, R_B, L, R_HD, DOME, SKIN_TH, SKIRT, R_BYOU, Z_BYOU, KAN_R, KAN_T, ZA_R, A1, A2 = [
    v * S for v in (R_H, R_B, L, R_HD, DOME, SKIN_TH, SKIRT, R_BYOU, Z_BYOU,
                    KAN_R, KAN_T, ZA_R, A1, A2)]

# 随伴のライム光源（#58：床に光を落とすのはこのW数だけ。**発光体の外**に置く）
LIME_W = 150.0


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）。
# 定在波・#40⑥ の発光積分・hero 位相の選択は、シーンを組まずにここで解ける。
# =============================================================
def j0(x):
    """第1種ベッセル関数 J0（べき級数）。x ≤ 6 なら倍精度で十分収束する。"""
    s, term = 1.0, 1.0
    q = -(x * x) / 4.0
    for k in range(1, 40):
        term *= q / (k * k)
        s += term
        if abs(term) < 1e-16:
            break
    return s


def ss(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def es_profile(u):
    """静的な半径方向の発光プロファイル（芯が白く、外へ落ちる）。"""
    g = 1.0 - ss((u / UG) ** GPOW) if u < UG else 0.0
    hot = 1.0 - ss(u / HOT_U)
    return g * (1.0 + HOT_MUL * hot)


def gmask(u):
    """皮のどこまでが「光る面」か（外は黒い皮へ戻る）。MixShader の Fac。"""
    return 1.0 - ss((u / UG) ** GPOW) if u < UG else 0.0


def disp(u, i):
    """変位 w(u,t)。両モードとも整数周期＝t=0 と t=1 が厳密一致。"""
    t = (i % N_FRAMES) / N_FRAMES
    return (A1 * j0(LAM1 * u) * math.cos(2 * math.pi * t)
            + A2 * j0(LAM2 * u) * math.cos(4 * math.pi * t))


def env(u, i):
    """シェーダと同一の包絡（光＝皮が動いた量）。"""
    return min(ENV_HI, max(ENV_LO, BASE + KA * abs(disp(u, i)) / A1))


def light(i, n=240):
    """#40⑥：見える発光量。皮の面で積分する（幾何で測る＝#46）。"""
    s = 0.0
    for k in range(n):
        u = (k + 0.5) / n
        s += es_profile(u) * gmask(u) * env(u, i) * u
    return s * (1.0 / n)


_LS = [light(i) for i in range(N_FRAMES)]
_LMAX = max(_LS)

# --- hero 位相（#48-c：単一指標で選ばない）---------------------
# 🔴 2周目の失敗：「明るさ × 半径方向の標準偏差」で選ぶと**必ず t=0（一様な山）**が勝った。
#    標準偏差は中心→外への当たり前の落ち方でも大きくなるので、**輪の有無を1ミリも測っていない**。
#    hero に要るのは光の量ではなく「これは定在波だ」と1秒で分かる線＝**内側に立つ本物の極小**。
def ring_dip(i, n=120):
    """env の内側の極小（＝節の輪）の深さ。輪が無ければ 0。"""
    us = [(k + 0.5) / n * UG for k in range(n)]
    ev = [env(u, i) for u in us]
    best = 0.0
    for k in range(4, n - 4):
        if ev[k] < ev[k - 3] and ev[k] < ev[k + 3] and 0.10 < us[k] < 0.58:
            best = max(best, min(max(ev[:k]), max(ev[k:])) - ev[k])
    return best


#   ③ ただし**真ん中が明るい位相**を選ぶ（シリーズの主題は「真ん中に光がある」）。
#      節が中心に来る位相＝t=0.5 は絵として強いが、主題としては「真ん中から光が抜けた」瞬間。
_SC = [(_LS[i] / _LMAX) * ring_dip(i) * env(0.0, i) for i in range(N_FRAMES)]
STILL_FRAME = (max(range(N_FRAMES), key=lambda i: _SC[i]) + 1) if max(_SC) > 0 else 1


def barrel_r(z):
    """胴の外形。端で R_H、腹で R_B の膨らみ。
       🔴 素の cos だと端で壁が 20° 内へ倒れていて、回転楕円体＝**卵**に読めた（3周目）。
       べきを 1 **未満**にしたら腹が平らに広がって、もっと卵になった（4周目・向きが逆だった）。
       正しくは **1 より大きく**する：cos^p (p>1) は零点で微分も 0 になるので、
       **胴の壁が端の面に直角で当たる＝肩が立つ**。腹だけが局所的に張り出す「刳り抜き胴」になる。"""
    return R_H + (R_B - R_H) * math.cos(math.pi * z / L) ** 1.90


if "--probe-only" in sys.argv:
    print(">> STILL_FRAME %d" % STILL_FRAME)
    print(">> #40(6) 見える発光量 min/max = %.3f  （合格 0.75以下）" % (min(_LS) / _LMAX))
    print(">> 定在波（皮の変位・単位 mm）")
    for i in range(0, N_FRAMES, 10):
        print("   t=%.3f  中心 %+6.1f  u=.44 %+6.1f  u=.70 %+6.1f   光量 %5.0f%%  芯の明るさ %.2f"
              % (i / N_FRAMES, 1000 * disp(0.0, i), 1000 * disp(0.4357, i), 1000 * disp(0.70, i),
                 100 * _LS[i] / _LMAX, env(0.0, i)))
    print(">> 縁で 0 か（皮は縁で留まっている）: w(1.0)=%.6f  J0(λ1)=%.2e  J0(λ2)=%.2e"
          % (disp(1.0, 7), j0(LAM1), j0(LAM2)))
    print(">> ループの閉じ: w(0,f=0)=%.6f  w(0,f=120)=%.6f" % (disp(0.0, 0), disp(0.0, 120)))
    print(">> 胴の外形  端 %.3f  腹 %.3f  胴長 %.3f  皮 %.3f" % (R_H, R_B, L, R_HD))
    print(">> 鋲の座  z=%.3f で胴の半径 %.3f" % (Z_BYOU, barrel_r(Z_BYOU)))
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
    "nuno_usu": dict(rough=0.66, spec=0.28, sheen=0.55, sheen_rough=0.25),
    "tetsu":  dict(rough=0.50, spec=0.32, metal=0.35, disp=0.012, dsize=0.09),
}
# 胴＝漆（塗り物の胴。MATERIALS.md「深く沈んだ艶がモチーフの本体であるもの」）
# 皮＝布（厚物）。鋲と環＝鉄。**色は1色も増えない。質感の語彙だけ増やす**
RECIPE_BODY, RECIPE_SKIN, RECIPE_IRON = "urushi", "nuno", "tetsu"
# 🔴 2周目：MATERIALS.md の urushi をそのまま当てたら、胴が**銀色のカプセル**になった（黒平均44・
#    数値は健全域なのに絵は銀）。レシピは径0.3程度の球・立方で測った値で、ここは**径1.4の大きな曲面**
#    ＝明るい環境（0.92）を面で返す量が桁で違う（#55 と同じ「前提の差」）。効いたのは2つ：
#    ① **Coat を落とす**。Coat は Metallic で黒くならない**常に誘電体の白い層**で、
#       大きな曲面ではそれが白いヴェールの本体になる。
#    ② **金属度を入れる**（#57②：#0a0a0a の金属はグレー環境を映しても黒いまま／誘電体の鏡面は白い）。
BLACK_RECIPES["urushi"] = dict(rough=0.34, spec=0.30, coat=0.0, metal=0.42)


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


mat_body = black_material("body", RECIPE_BODY)
mat_iron = black_material("iron", RECIPE_IRON)


def skin_material(name):
    """皮。外は黒い革、内は発光。
       🔴 光は**変位そのもの**：Geometry→Position を Object 空間に戻し、
          色属性に焼いた「変位前の z」との差を取る。シェーダに時間のキーを打たない。
       色属性 wave = (R:静的プロファイル, G:変位前のz, B:u, A:革↔発光の混合)。"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')

    leather = nt.nodes.new("ShaderNodeBsdfPrincipled")
    set_black(leather, RECIPE_SKIN)

    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = LIME

    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(leather.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])

    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "wave"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])
    nt.links.new(attr.outputs["Alpha"], mx.inputs["Fac"])       # A＝革↔発光

    # いまの位置（変形後）をオブジェクト空間へ戻す
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    vt = nt.nodes.new("ShaderNodeVectorTransform")
    vt.vector_type = 'POINT'; vt.convert_from = 'WORLD'; vt.convert_to = 'OBJECT'
    nt.links.new(geo.outputs["Position"], vt.inputs["Vector"])
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(vt.outputs["Vector"], xyz.inputs["Vector"])

    def mn(op, val=None, clamp=False):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        if val is not None:
            n.inputs[1].default_value = val
        return n

    d = mn('SUBTRACT')                                          # d = z(いま) − z(変位前)
    nt.links.new(xyz.outputs["Z"], d.inputs[0])
    nt.links.new(sep.outputs["Green"], d.inputs[1])
    ab = mn('ABSOLUTE'); nt.links.new(d.outputs[0], ab.inputs[0])   # 🔴 向きでなく量
    k = mn('MULTIPLY', KA / A1); nt.links.new(ab.outputs[0], k.inputs[0])
    one = mn('ADD', BASE); nt.links.new(k.outputs[0], one.inputs[0])
    cl = nt.nodes.new("ShaderNodeClamp")
    cl.inputs["Min"].default_value = ENV_LO; cl.inputs["Max"].default_value = ENV_HI
    nt.links.new(one.outputs[0], cl.inputs["Value"])
    pr = mn('MULTIPLY')                                         # × 静的プロファイル
    nt.links.new(sep.outputs["Red"], pr.inputs[0])
    nt.links.new(cl.outputs[0], pr.inputs[1])
    es = mn('MULTIPLY', ES_CORE); nt.links.new(pr.outputs[0], es.inputs[0])
    nt.links.new(es.outputs[0], em.inputs["Strength"])
    return m


mat_skin = skin_material("skin")

mat_floor, fp = principled("floor")
fp.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp.inputs["Roughness"].default_value = 0.42
mat_text, tp = principled("text")
tp.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp.inputs["Roughness"].default_value = 0.6


# ---------- 造形（bmesh・ローカル実寸。object.scale / transform_apply 不使用＝#15） ----------
NSEG = 112


def lathe(profile, name, mat, close_bottom=True):
    """(r, z) の輪郭を Z 軸まわりに回して閉じたソリッドにする。r=0 の点は極として1頂点に潰す。"""
    bm = bmesh.new()
    rings, poles = [], []
    for (r, z) in profile:
        if r < 1e-6:
            v = bm.verts.new((0.0, 0.0, z)); rings.append(None); poles.append(v)
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / NSEG),
                                        r * math.sin(2 * math.pi * k / NSEG), z))
                          for k in range(NSEG)])
            poles.append(None)
    for i in range(len(profile) - 1):
        A, B = rings[i], rings[i + 1]
        if A is None and B is None:
            continue
        if A is None:
            p = poles[i]
            for k in range(NSEG):
                bm.faces.new((p, B[(k + 1) % NSEG], B[k]))
        elif B is None:
            p = poles[i + 1]
            for k in range(NSEG):
                bm.faces.new((p, A[k], A[(k + 1) % NSEG]))
        else:
            for k in range(NSEG):
                bm.faces.new((A[k], A[(k + 1) % NSEG], B[(k + 1) % NSEG], B[k]))
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
        bmesh.ops.bevel(bm, geom=sharp, offset=0.006, segments=2,
                        affect='EDGES', clamp_overlap=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        pass
    ob.select_set(False)
    return ob


# --- 胴（くり抜きの実体。空洞を作らない＝#41-b／#37②）----------
prof = [(0.0, -L / 2)]
NB_ = 40
for k in range(NB_ + 1):
    z = -L / 2 + L * k / NB_
    prof.append((barrel_r(z), z))
prof.append((0.0, L / 2))
barrel = lathe(prof, "barrel", mat_body)

# --- 皮（閉じた薄板。面＝ドーム、耳＝下へ折れて鉢を包む）--------
ZTOP = L / 2 + 0.014
NA_, NS_ = 34, 12


def skin_profile():
    """(r, z, u) の並び。u は「面としての半径比」で、光と変位はこれで決まる。"""
    pts = []
    for k in range(NA_ + 1):
        u = UA * k / NA_
        pts.append((R_HD * u, ZTOP + DOME * (1.0 - (u / UA) ** 2), u / 1.0))
    for k in range(1, NS_ + 1):
        a = (math.pi / 2) * k / NS_
        u = UA + (1.0 - UA) * math.sin(a)
        pts.append((R_HD * u, ZTOP - SKIRT * (1.0 - math.cos(a)), u))
    return pts


def build_skin():
    """上面と下面を持つ閉じた薄板。変位は上下おなじだけ動かす＝厚みが変わらない膜。"""
    pts = skin_profile()
    bm = bmesh.new()
    top, bot = [], []
    pole_t = bm.verts.new((0.0, 0.0, pts[0][1]))
    pole_b = bm.verts.new((0.0, 0.0, pts[0][1] - SKIN_TH))
    uv_of = {pole_t: 0.0, pole_b: 0.0}
    zb_of = {pole_t: pts[0][1], pole_b: pts[0][1] - SKIN_TH}
    for (r, z, u) in pts[1:]:
        rt = [bm.verts.new((r * math.cos(2 * math.pi * k / NSEG),
                            r * math.sin(2 * math.pi * k / NSEG), z)) for k in range(NSEG)]
        rb = [bm.verts.new((r * math.cos(2 * math.pi * k / NSEG),
                            r * math.sin(2 * math.pi * k / NSEG), z - SKIN_TH)) for k in range(NSEG)]
        for v in rt:
            uv_of[v] = u; zb_of[v] = z
        for v in rb:
            uv_of[v] = u; zb_of[v] = z - SKIN_TH
        top.append(rt); bot.append(rb)
    for k in range(NSEG):
        bm.faces.new((pole_t, top[0][(k + 1) % NSEG], top[0][k]))
        bm.faces.new((pole_b, bot[0][k], bot[0][(k + 1) % NSEG]))
    for i in range(len(top) - 1):
        A, B = top[i], top[i + 1]
        C, D = bot[i], bot[i + 1]
        for k in range(NSEG):
            bm.faces.new((A[k], A[(k + 1) % NSEG], B[(k + 1) % NSEG], B[k]))
            bm.faces.new((C[k], D[k], D[(k + 1) % NSEG], C[(k + 1) % NSEG]))
    A, C = top[-1], bot[-1]                       # 縁を閉じる
    for k in range(NSEG):
        bm.faces.new((A[k], C[k], C[(k + 1) % NSEG], A[(k + 1) % NSEG]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("skin")
    keep = [(uv_of[v], zb_of[v]) for v in bm.verts]       # 頂点順のまま持ち出す
    bm.verts.index_update()
    order = {v.index: i for i, v in enumerate(bm.verts)}
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("skin", me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat_skin)
    return ob, keep, order


skin, SK, _ORD = build_skin()
# 色属性 wave＝(静的プロファイル, 変位前のz, u, 革↔発光の混合)
ca = skin.data.color_attributes.new(name="wave", type='FLOAT_COLOR', domain='POINT')
for i, (u, zb) in enumerate(SK):
    ca.data[i].color = (es_profile(u), zb, u, gmask(u))

# --- シェイプキー2枚＝2つの固有モード（glb に morph target で乗る＝#60）----
skin.shape_key_add(name="Basis", from_mix=False)
kb1 = skin.shape_key_add(name="mode1", from_mix=False)
kb2 = skin.shape_key_add(name="mode2", from_mix=False)
for i, (u, zb) in enumerate(SK):
    kb1.data[i].co.z += A1 * j0(LAM1 * min(u, 1.0))
    kb2.data[i].co.z += A2 * j0(LAM2 * min(u, 1.0))
for kb in (kb1, kb2):
    kb.slider_min = -1.0
    kb.slider_max = 1.0

# --- 鋲（皮の耳を胴に打ち留める・黒の肌は実ジオメトリで作る＝#52）----
# 🔴 2周目：鋲も皮も手前の面にしか無いと、太鼓ではなく「光る蓋のついたカプセル」に読めた。
#    太鼓は**両端に皮が張ってある物**なので、向こうの縁と鋲も出す（見えるのは輪郭だけでよい／#33）。
byou = []
for side in (+1, -1):
    zb_ = side * Z_BYOU
    rb_ = barrel_r(zb_) + 0.010
    for k in range(N_BYOU):
        th = 2 * math.pi * k / N_BYOU
        bpy.ops.mesh.primitive_uv_sphere_add(radius=R_BYOU, segments=18, ring_count=10,
                                             location=(rb_ * math.cos(th), rb_ * math.sin(th), zb_))
        b = bpy.context.active_object
        b.name = "byou_%s%02d" % ("n" if side > 0 else "f", k)
        b.data.materials.append(mat_iron)
        try:
            bpy.ops.object.shade_auto_smooth(angle=0.6)
        except Exception:
            pass
        b.select_set(False)
        byou.append(b)

# 向こう側の皮の縁（耳）。手前の皮と同じ張り出しを輪郭にだけ出す
mat_leather = black_material("leather", RECIPE_SKIN)
bpy.ops.mesh.primitive_torus_add(major_radius=R_HD - SKIN_TH, minor_radius=SKIN_TH * 1.15,
                                 major_segments=NSEG, minor_segments=12,
                                 location=(0.0, 0.0, -(L / 2 + 0.012)))
far_lip = bpy.context.active_object
far_lip.name = "far_lip"
far_lip.data.materials.append(mat_leather)
try:
    bpy.ops.object.shade_auto_smooth(angle=0.6)
except Exception:
    pass
far_lip.select_set(False)
byou.append(far_lip)

# --- 環（かん）と座金。🔴 回転対称を破って初めて「太鼓」に読める（#33／048 の教訓）----
kan = []
for sgn in (-1, +1):
    rz_ = barrel_r(0.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=ZA_R, depth=0.030, vertices=28,
                                        location=(sgn * (rz_ + 0.004), 0.0, 0.0),
                                        rotation=(0.0, math.pi / 2, 0.0))
    za = bpy.context.active_object; za.name = "za_%d" % sgn
    za.data.materials.append(mat_iron); za.select_set(False)
    bpy.ops.mesh.primitive_torus_add(major_radius=KAN_R, minor_radius=KAN_T,
                                     major_segments=44, minor_segments=12,
                                     location=(sgn * (rz_ + 0.020), -KAN_R * 0.82, 0.0))
    kn = bpy.context.active_object; kn.name = "kan_%d" % sgn
    kn.data.materials.append(mat_iron)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.6)
    except Exception:
        pass
    kn.select_set(False)
    kan += [za, kn]

# --- リグ：胴・皮・鋲・環をまとめて立て、打面を右の余白へ向ける ----------
# 🔴 #57①：Rx(+π/2) がローカル +Z を **−Y（カメラ側）** へ送る。−π/2 だと作り込みが丸ごと裏に回る。
rig = bpy.data.objects.new("rig", None)
bpy.context.collection.objects.link(rig)
rig.location = (DRUM_X, 0.0, DRUM_Z)
rig.rotation_euler = (math.pi / 2, 0.0, PSI)
parts = [barrel, skin] + byou + kan
for o in parts:
    o.parent = rig

# --- 定在波のキー（毎フレーム打つ＝イージング不使用・#25c）----------
FR = list(range(N_FRAMES)) + [0]                  # 末尾に折り返し＝glb でループが閉じる
# 🔴 Blender 5.x の Action はスロット制で `action.fcurves` が無い（1周目で AttributeError）。
#    打った後に直すのではなく、**打つ前に既定の補間を LINEAR にする**（版に依存しない）。
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = (i % N_FRAMES) / N_FRAMES
    kb1.value = math.cos(2 * math.pi * t)
    kb2.value = math.cos(4 * math.pi * t)
    kb1.keyframe_insert("value", frame=f + 1)
    kb2.keyframe_insert("value", frame=f + 1)

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
        caption("MIDDLE STUDY 052 — TAIKO", 0.045, (AIM_X, -1.7, 0.57), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.size = size; L.data.energy = energy; L.data.color = color
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (DRUM_X, 0, DRUM_Z)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）

# 🔴 #58：床にライムを落とせるのは随伴のライム光源の**W数**だけ（発光の強さでもバウンス数でもない）。
#    ③ **発光体の中に置かない**。皮の面より手前・下に出す。
head_c = (DRUM_X + (L / 2) * math.sin(PSI), -(L / 2) * math.cos(PSI), DRUM_Z)
bpy.ops.object.light_add(type='POINT', location=(head_c[0] - 0.10, head_c[1] - 0.62, head_c[2] - 0.66))
limelamp = bpy.context.active_object
limelamp.name = "lime"
limelamp.data.energy = LIME_W
limelamp.data.shadow_soft_size = 0.28
limelamp.data.color = LIME[:3]
limelamp.visible_camera = False

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world; world.use_nodes = True
bgn = world.node_tree.nodes.get("Background")
bgn.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
bgn.inputs[1].default_value = 0.55

bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object; cam.name = "hero_cam"; cam.data.lens = 85
cam.rotation_euler = (Vector((AIM_X, 0, LOOK_Z)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = skin
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
    # 🔴 既定は 1920×1080（横）。判型を先に入れないと縦の占有が丸ごと嘘になる（1周目で実測）
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    print(">> #40(6) 見える発光量 min/max = %.3f （合格 0.75以下）" % (min(_LS) / _LMAX))
    # 🔴 面の向きを検算する（#57①：黒一色では「裏返っている」ように見えない）
    n_world = (rig.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    to_cam = (Vector(CAM_LOC) - Vector((DRUM_X, 0, DRUM_Z))).normalized()
    print(">> 打面の法線 %s  カメラ方向とのなす角 %.1f°（90未満＝カメラを向いている）"
          % (tuple(round(v, 3) for v in n_world), math.degrees(math.acos(n_world.dot(to_cam)))))
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME); dg.update()
    xs, ys = [], []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name == "floor":
            continue
        ev = o.evaluated_get(dg)
        for v in ev.data.vertices:
            c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
            xs.append(c.x); ys.append(c.y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(">> 投影bbox  x %.3f..%.3f (%.1f%%)  y %.3f..%.3f (%.1f%%)"
          % (x0, x1, (x1 - x0) * 100, y0, y1, (y1 - y0) * 100))
    print(">> 構図  重心x %.1f%%（端寄せ＝中央から12%%以上／edge=0）  枠まで 左%.3f 右%.3f 上%.3f 下%.3f"
          % ((x0 + x1) / 2 * 100, x0, 1 - x1, 1 - y1, y0))
    print(">> 占有  長辺 %.1f%%（合格 55〜65）" % (max((x1 - x0), (y1 - y0)) * 100))
    # 🔴 シェイプキーが**実際に評価されているか**を機械で見る（3周目：位相を変えても
    #    ライム面積が 3.35%→2.89% しか動かず、絵からは「効いていない」としか分からなかった）
    for fr in (1, 31, 61, 91):
        scene.frame_set(fr); dg.update()
        ev = skin.evaluated_get(dg)
        z0 = ev.data.vertices[0].co.z
        print(">> f%3d  kb1=%+.3f kb2=%+.3f  皮の中心 z=%.4f  変位=%+.4f（純math %+.4f）"
              % (fr, kb1.value, kb2.value, z0, z0 - SK[0][1], disp(0.0, fr - 1)))
    print(">> キャプション上端 z=0.95 と 被写体下端のクリアランス（world）")

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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_052.blend"))

# 🔴 glb は必ず最後（#30：Emission を定数へ潰すので、レンダーの前に置かない）
if "glb" in modes:
    m2, p2 = principled("skin_flat")
    set_black(p2, RECIPE_SKIN)
    p2.inputs["Emission Color"].default_value = LIME
    p2.inputs["Emission Strength"].default_value = 2.6
    skin.data.materials.clear()
    skin.data.materials.append(m2)
    scene.frame_end = N_FRAMES + 1
    names = {o.name for o in parts}
    for o in bpy.data.objects:
        o.select_set(o.name in names or o is rig)
    bpy.context.view_layer.objects.active = barrel
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "model.glb"),
                                  export_format='GLB', use_selection=True,
                                  export_animations=True, export_morph=True, export_yup=True)
        print(">> GLB %.1fMB" % (os.path.getsize(os.path.join(OUT, "model.glb")) / 1e6))
    except Exception as e:
        print(">> GLB FAILED:", e)
    scene.frame_end = N_FRAMES

print(">> ALL DONE")
