# =============================================================
# MIDDLE STUDY 061 — HANIWA（円筒埴輪 / cylindrical haniwa）
#
# 黒い筒が、いくつも宙に立っている。人の形でも馬の形でもない。ただの筒だ。
# 円筒埴輪は、古墳のまわりをぐるりと囲んで、何百本も並べられた。**囲うことだけが仕事だった。**
# 筒には透孔（すかしあな）が空いている。焼くときに割れないための穴で、飾りではない。
# **用のために空けた穴だけが、いま光を通している。**
# 輪がゆっくり揺れ、筒がひとつずつ向きを変える。灯るのは、こちらへ穴を向けた一本だけ。
# **囲われていたのは古墳ではなく、一本ずつの真ん中だったのかもしれない。**
#
# 🔴 構図の型＝**群**（#57：60作中51作が「全身」。群は 056 GOISHI の1作のみ）
# 🔴 光の型＝**窓**（#53：60作で6作。017 KAGIANA／031 TOURO）
#
# 🔴🔴 型の組み合わせを先に紙で解いた（#67⑤／#69①／#70⑥ の4例目）
#    群の条件は `clusters>=5`。measure.py の塊マスクは **「暗い画素 ∪ ライム画素」**なので、
#    **共有の光源を宙に置いた瞬間に、それが物どうしを繋いで全部が1塊になる。**
#    ```
#    背光×群 → 光源が背後の共有面 → 物のあいだに光が見える → clusters==1 → 不成立
#    ```
#    （#69① の「背光×対」と同じ形。群では物が増えるぶん、なお繋がりやすい）
#    ゆえに **ライムは各筒の内側に閉じ込めるしかない**。閉じ込めた光の型は 内包 か 窓 の二つで、
#    **内包は直近5作（060 KAMADO）で塞がっている**。→ **窓が一意に決まった**（好みで選んでいない）。
#    004 ANDON・031 TOURO は**灯り**（光ることが目的の道具）で、機構は「奥の発光体が息をする」。
#    こちらは**囲うための無地の筒**で、穴は焼成のための用＝**光は目的ではなく副産物**。
#
# 🔴 機構＝**輪の揺り（sway）＋各筒の自転（spin）**
#    ① 群を保ったまま動き量を出すには、**個体でなく輪ごと動かす**しかない。
#       隣とのクリアランスは 0.085 しかないので、個別に振れば必ずぶつかって塊が融ける
#       （＝群の条件が壊れる）。輪ごと回せば相対位置は不変のまま、画面では 0.39（222px）横に動く。
#    ② 光量は**自転による透孔の向きだけ**で作る。**発光の値は1フレームも動かしていない**
#       （#69②／#70④）。透孔は貫通穴なので見える量は |cos| で効き、位相を π/2 ずつずらして
#       配ると群の合計は 4|cosθ|+3|sinθ| ＝ 3〜5 のあいだで振れる（＝真っ暗な瞬間が無い）。
#    どちらも整数周期で厳密に閉じ、**位置キーと回転キーだけ**なので glb にそのまま乗る（#60）。
#
# 造形＝**boolean 不使用**。円筒面を (θ,z) の格子で張り、**透孔に入る面を最初から作らない**。
#    ——彫るのではなく、**無いところが穴**（型紙と同じ論理）。SOLIDIFY が肉厚と穴の胴を自動で作る。
#
# 【ドメイン】古墳・埴輪（シリーズ未踏）。直近10作＝炊事・竈／証・割符／空・凧／運搬・車輪／
#            盤上遊戯／鋳造／植物・果実／漁労／楽器・打／貨幣 と別。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = 150.0                      # 🔴 #58③：随伴のライム光源。発光体の外・#67⑥の遠い床へ

# --- 輪（囲い）---------------------------------------------------
N_HANI = 7                          # 画面に入る本数（群＝clusters>=5 に対して余裕を2本持たせる）
R_RING = 3.0                        # 輪の半径（浅い弧＝「ぐるりと囲む」の一部だけが見えている）
CX, CY = AIM_X, 3.0                 # 輪の中心。φ=0 が (AIM_X, 0)＝画面の真ん中に来る
ARC = 0.278                         # 隣どうしの弧長（＝画面での隙間 41px。これ以上詰めると塊が融ける）
DPHI = ARC / R_RING                 # 0.095 rad
SWAY = 0.130                        # 輪の揺れ（rad）。横移動 R·SWAY = 0.39 ＝ 222px

# --- 筒（円筒埴輪）----------------------------------------------
R0 = 0.103                          # 胴の半径（径 0.206。H/D≒4〜5 の実物比）
WALL = 0.027                        # 肉厚（SOLIDIFY）。🔴 0.018 では透孔が**平らな緑のシール**に
                                    # 見えた。奥行きは芯を遠ざけるのではなく**穴の胴**で作る（#24）
RH = 0.047                          # 透孔の半径（径 0.094＝胴径の 46%）
# 4種の高さ・据わり・自転位相を mod 4 で配る（#70⑤：等高・等角・等間隔は必ずベタになる）
HH = [0.86, 1.02, 0.74, 0.94]
ZB = [1.46, 1.38, 1.54, 1.42]       # 底のz（浮遊）
NLEV = [4, 4, 4, 4]                 # 透孔の段数
# 🔴 実物の埴輪列は無地の円筒ばかりではなく、**朝顔形埴輪**（口が朝顔のように開くもの）を
#    一定間隔で混ぜて立てる。1周目・2周目は全部を同じ筒にしたので、
#    絵が「黒い管に緑の点」＝竹か電池にしか見えなかった。**口を開いた2本が入ると列が埴輪になる。**
FLARE = [0.0, 1.38, 0.0, 0.0]       # 口の開き（R0 倍）。0 は無地の円筒埴輪
LEVHI = [0.84, 0.62, 0.84, 0.84]    # 透孔の最上段（朝顔形は口の下で止める）
PHASE = [0.0, 0.26, 0.13, 0.39]     # 自転の位相差（rad）。🔴 π/2 ずつ等間隔に配ると
                                    # 群の合計が定数になり #40⑥ が 0.896 で落ちる（1周目の実測）
ALT = math.radians(48)              # 段ごとに透孔の向きを振る。実物は90°だが、90°では
                                    # 偶数段と奇数段が完全に補い合って**光量が定数になる**（下記）

RC = 0.049                          # 内側の発光体（芯）の半径
                                    # 🔴 RC >= RH が**絶対条件**。下回ると向かい合う2つの透孔が
                                    #    一直線に抜けて、穴に**背景の白がそのまま貼りつく**
                                    #    （2周目に上3本の天の穴が白い座薬みたいになった＝#67① の透過版）
ES_CORE = 8.4

NTH, NZ = 104, 112                  # (θ,z) 格子。🔴 64×76 では透孔が**角丸の四角**に見えた
                                    # （半径あたり 4.3 セルしか無い）。セル 0.0060×0.0080 で円に戻る
LEV_LO = 0.18                       # 透孔の最下段（高さに対する比）
BANDS = (0.29, 0.51, 0.73)          # 突帯（タガ）の位置
BAND_W, BAND_H = 0.014, 0.042       # 突帯の幅（比）と張り出し（R0 比）
                                    # 🔴 1周目は 0.030/0.115 で、節のある**竹**にしか見えなかった。
                                    #    実物の突帯は粘土を貼った薄い箍で、胴は膨らまない

STILL_FRAME = 117                   # probe で確定（明るさ0.93 かつ 揺れがほぼ中央）


# =============================================================
# ここから下は Blender に依存しない純 math（#31 の規律）
# =============================================================
def sway_of(t):
    return SWAY * math.sin(2.0 * math.pi * t)


def spin_of(j, t):
    """自転。1周（2π）で厳密に閉じる＝DISPLACE のクレイ肌も同じ姿に戻る"""
    return 2.0 * math.pi * t + PHASE[j % 4]


def phi_of(j, t):
    """輪の上での角。φ=0 が画面の真ん中"""
    return (j - (N_HANI - 1) * 0.5) * DPHI + sway_of(t)


def base_of(j, t):
    p = phi_of(j, t)
    return (CX + R_RING * math.sin(p), CY - R_RING * math.cos(p), ZB[j % 4])


def lev_u(idx, lev):
    n = NLEV[idx]
    return LEV_LO if n == 1 else LEV_LO + (LEVHI[idx] - LEV_LO) * lev / (n - 1)


def hole_world(j, t, lev, side):
    """透孔の（中心の世界座標, 外向き法線）。side=0 外向き / 1 内向き（貫通穴）"""
    x, y, z0 = base_of(j, t)
    H = HH[j % 4]
    u = lev_u(j % 4, lev)
    zc = z0 + H * u
    beta = phi_of(j, t) + spin_of(j, t) + ALT * (lev % 2) + (math.pi if side else 0.0)
    nx, ny = math.sin(beta), -math.cos(beta)
    r = R0 * radius_at(u, FLARE[j % 4])
    return (x + nx * r, y + ny * r, zc), (nx, ny, 0.0)


def radius_at(u, fl=0.0):
    """胴の輪郭（比）。実物は下から上へわずかに開き、口縁だけが外へ反る。
       🔴 裾を膨らませない——膨らませると竹の根元になる（1周目の失敗）。
       fl>0 は**朝顔形**：首でいったん締めてから、口が二次曲線で開く"""
    if fl > 0.0:
        if u < 0.66:
            return 0.962 + 0.030 * (u / 0.66)
        if u < 0.74:
            return 0.992 - 0.062 * (u - 0.66) / 0.08          # 首
        s2 = (u - 0.74) / 0.26
        return 0.930 + (fl - 0.930) * s2 ** 1.9
    if u < 0.88:
        return 0.962 + 0.038 * (u / 0.88)
    return 1.0 + 0.058 * (u - 0.88) / 0.12


def _vig(cos_t, rh, T):
    """穴の胴（厚み T）による口径食＝2円の重なり。cos_t は面法線と視線の内積"""
    if cos_t <= 1e-6:
        return 0.0
    sin_t = math.sqrt(max(0.0, 1.0 - cos_t * cos_t))
    d = T * sin_t / cos_t
    if d >= 2 * rh:
        return 0.0
    a = 2 * rh * rh * math.acos(d / (2 * rh)) - (d / 2) * math.sqrt(max(0.0, 4 * rh * rh - d * d))
    return a / (math.pi * rh * rh)


def light_visible(t):
    """🔴 #40⑥ は幾何で積分する（#46/#64②）＝**見えている発光**。
       透孔は貫通穴なので、外向き・内向きの両方が「その向きに開いた窓」になる。
       見える量 = 穴の面積 × max(0, n̂·v̂) × 口径食。**発光の値は一切入っていない。**"""
    C = CAM_LOC
    tot = 0.0
    for j in range(N_HANI):
        for lev in range(NLEV[j % 4]):
            for side in (0, 1):
                P, N = hole_world(j, t, lev, side)
                v = (C[0] - P[0], C[1] - P[1], C[2] - P[2])
                L = math.sqrt(sum(c * c for c in v))
                v = tuple(c / L for c in v)
                ct = sum(N[k] * v[k] for k in range(3))
                if ct <= 0:
                    continue
                tot += math.pi * RH * RH * ct * _vig(ct, RH, WALL)
    return tot


_TS = [i / N_FRAMES for i in range(N_FRAMES)]
_VS = [light_visible(t) for t in _TS]
_VMAX = max(_VS)

if "--probe-only" in sys.argv:
    print("── 061 HANIWA 幾何プローブ")
    print("   #40⑥ 見える光 min/max = %.3f （合格 0.75以下）" % (min(_VS) / _VMAX))
    best = max(range(N_FRAMES), key=lambda i: _VS[i])
    print("   いちばん明るいフレーム = %d（t=%.3f）" % (best + 1, _TS[best]))
    # 画面上の並び（bbox と隙間）
    for t in (0.0, _TS[best], 0.25):
        xs = []
        for j in range(N_HANI):
            x, y, z0 = base_of(j, t)
            d = y - CAM_LOC[1]
            xs.append(((x - CAM_LOC[0]) / d, R0 / d))
        span = (max(c + w for c, w in xs) - min(c - w for c, w in xs))
        half = 18.0 / 85.0 * 0.8            # 画面半幅の tan（4:5 ポートレート）
        gaps = [(xs[i + 1][0] - xs[i][0]) - (xs[i][1] + xs[i + 1][1]) for i in range(N_HANI - 1)]
        print("   t=%.3f  横占有 %.1f%%（帯 44〜66）  最小の隙間 %.0f px  光 %5.1f%%"
              % (t, span / (2 * half) * 100, min(gaps) / half * 800, 100 * light_visible(t) / _VMAX))
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
    "base":  dict(rough=0.36, spec=0.15, coat=0.05),
    # 埴輪＝素焼きの土器 → **陶**（焼き物・石・土・瓦・臼）
    # 🔴 #67③/#57②：誘電体の黒は**視線とすれすれの面で白を映す**。筒はシルエットの全周が
    #    すれすれなので、素の陶だと灰色のゴムに転ぶ。#0a0a0a の金属は白を浴びても黒い
    # 🔴 disp 0.010 は**シルエットが波打って**素焼きでなく溶けたゴムに見えた。
    #    肌は残して輪郭は乱さない量が 0.0055
    "touki": dict(rough=0.58, spec=0.26, metal=0.18, disp=0.0055, dsize=0.055),
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


mat_clay = black_material("haniwa_clay", "touki")


def core_material(name):
    """筒の中の光。勾配は **UV に焼いた**（#34/#39）＝**筒の真ん中がいちばん明るい**。
       両端で 0 に落ちるので、開いた口から芯の小口が覗いても光の帯にならない。
       #65②：純発光体は法線依存の項が無いと形が消える → LayerWeight を掛ける。
       🔴 #70④：halo は**芯を白へ抜く**ことでしか出ない（ライムは B がほぼ無い）。"""
    m, p = principled(name)
    set_black(p, "base")
    nt = m.node_tree
    p.inputs["Base Color"].default_value = BLACK            # #68⑤：下地に色を置かない

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], xyz.inputs["Vector"])

    def mn(op, val=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if val is not None:
            n.inputs[1].default_value = val
        return n

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    # 🔴 #24：芯が均一に光ると、透孔は**緑のシール**になる。芯の面が視線から外れるほど
    #    暗くなる項を強く掛けると、穴の中に「奥が丸い」勾配が出る
    fcs = mn('MULTIPLY', 0.62); nt.links.new(lw.outputs["Facing"], fcs.inputs[0])
    fca = mn('ADD', 0.38); nt.links.new(fcs.outputs[0], fca.inputs[0])

    ntx = nt.nodes.new("ShaderNodeTexNoise")
    ntx.inputs["Scale"].default_value = 22.0
    ntx.inputs["Detail"].default_value = 6.0
    ntx.inputs["Roughness"].default_value = 0.58
    nmr = nt.nodes.new("ShaderNodeMapRange"); nmr.clamp = True
    nmr.inputs["From Min"].default_value = 0.32; nmr.inputs["From Max"].default_value = 0.72
    nmr.inputs["To Min"].default_value = 0.52; nmr.inputs["To Max"].default_value = 1.30
    nt.links.new(ntx.outputs["Fac"], nmr.inputs["Value"])

    e1 = mn('MULTIPLY'); nt.links.new(xyz.outputs["X"], e1.inputs[0])
    nt.links.new(fca.outputs[0], e1.inputs[1])
    e0 = mn('MULTIPLY'); nt.links.new(e1.outputs[0], e0.inputs[0])
    nt.links.new(nmr.outputs["Result"], e0.inputs[1])

    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = 0.50; wmr.inputs["From Max"].default_value = 1.10
    wmr.inputs["To Min"].default_value = 0.0; wmr.inputs["To Max"].default_value = 0.80
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
def link(me, name, mat, parent=None):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if not ob.data.materials:
        ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=0.35)
    except Exception:
        pass
    ob.select_set(False)
    return ob


def wall_r(u, fl=0.0):
    """胴の半径（実寸）。突帯（タガ）の張り出しを含む"""
    r = R0 * radius_at(u, fl)
    for b in BANDS:
        if fl > 0.0 and b > 0.60:
            continue
        d = abs(u - b)
        if d < BAND_W:
            # 🔴 コサインの山にすると**竹の節**になる。実物の突帯は粘土を貼った薄い箍で、
            #    頂が平らで肩がストンと落ちる。胴そのものは膨らまない
            r += R0 * BAND_H * (1.0 if d < BAND_W * 0.55 else (BAND_W - d) / (BAND_W * 0.45))
    return r


def hole_list(idx, H):
    """透孔の中心を (角, 高さ) で並べる。段ごとに ALT だけ向きを振る"""
    hs = []
    for lev in range(NLEV[idx]):
        uc = lev_u(idx, lev)
        a0 = ALT * (lev % 2)
        for a in (a0, a0 + math.pi):
            hs.append((a % (2 * math.pi), uc * H))
    return hs


def hole_near(hs, th, z):
    """いちばん近い透孔までの距離（**弧長で測る**。角度で測ると穴が縦長に潰れる）"""
    best = (1e9, 0.0, 0.0)
    for (a, zc) in hs:
        da = (th - a + math.pi) % (2 * math.pi) - math.pi
        d = math.hypot(da * R0, z - zc)
        if d < best[0]:
            best = (d, a, zc)
    return best


def haniwa_mesh(idx):
    """**穴は掘るのではなく、面を作らないことで生まれる**（boolean 不使用）。
       🔴 ただし格子のセル単位で切ると穴は**角丸の四角**になる（1周目の実測）。
          境界にある頂点だけを、正確な円の上へ滑らせてから面を張る。"""
    H, fl = HH[idx], FLARE[idx]
    hs = hole_list(idx, H)
    cell = max(2 * math.pi * R0 / NTH, H / NZ)
    P = [[(2 * math.pi * it / NTH, jz / NZ * H) for it in range(NTH)] for jz in range(NZ + 1)]
    cut = [[hole_near(hs, 2 * math.pi * (it + 0.5) / NTH, (jz + 0.5) / NZ * H)[0] < RH
            for it in range(NTH)] for jz in range(NZ)]
    for jz in range(NZ + 1):
        for it in range(NTH):
            nb = [cut[jz + dz][(it + dt) % NTH]
                  for dz in (-1, 0) for dt in (-1, 0) if 0 <= jz + dz < NZ]
            if not nb or all(nb) or not any(nb):     # 境界の頂点だけを動かす
                continue
            th, z = P[jz][it]
            d, a, zc = hole_near(hs, th, z)
            if d < 1e-9 or abs(d - RH) > 1.3 * cell:
                continue
            da = (th - a + math.pi) % (2 * math.pi) - math.pi
            k = RH / d
            P[jz][it] = (a + da * k, zc + (z - zc) * k)
    bm = bmesh.new()
    grid = []
    for jz in range(NZ + 1):
        row = []
        for it in range(NTH):
            th, z = P[jz][it]
            r = wall_r(z / H, fl)
            row.append(bm.verts.new((r * math.sin(th), -r * math.cos(th), z)))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for jz in range(NZ):
        for it in range(NTH):
            if cut[jz][it]:
                continue
            a = grid[jz][it]; b = grid[jz][(it + 1) % NTH]
            c = grid[jz + 1][(it + 1) % NTH]; d = grid[jz + 1][it]
            bm.faces.new((a, b, c, d))
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("haniwa_%d" % idx)
    bm.to_mesh(me); bm.free()
    return me


def core_mesh(idx):
    """筒の中の芯。UV 'grad' の U に **1-|2zn-1|**（＝真ん中で1・両端で0）を焼く"""
    H = HH[idx]
    z0, z1 = 0.06, H - 0.06   # 🔴 透孔の上端より高く・下端より低く（抜けを塞ぐ）
    NS, NR = 40, 26
    bm = bmesh.new()
    rings = []
    for jz in range(NR + 1):
        zn = jz / NR
        z = z0 + (z1 - z0) * zn
        rings.append([bm.verts.new((RC * math.sin(2 * math.pi * i / NS),
                                    -RC * math.cos(2 * math.pi * i / NS), z))
                      for i in range(NS)])
    cap0 = bm.verts.new((0, 0, z0)); cap1 = bm.verts.new((0, 0, z1))
    for jz in range(NR):
        for i in range(NS):
            bm.faces.new((rings[jz][i], rings[jz][(i + 1) % NS],
                          rings[jz + 1][(i + 1) % NS], rings[jz + 1][i]))
    for i in range(NS):
        bm.faces.new((cap0, rings[0][(i + 1) % NS], rings[0][i]))
        bm.faces.new((cap1, rings[NR][i], rings[NR][(i + 1) % NS]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bm.loops.layers.uv.new("grad")
    for f in bm.faces:
        for lp in f.loops:
            zn = (lp.vert.co.z - z0) / (z1 - z0)
            lp[uvl].uv = (1.0 - abs(2.0 * zn - 1.0), 0.5)
    me = bpy.data.meshes.new("core_%d" % idx)
    bm.to_mesh(me); bm.free()
    return me


# ---------- 配置 ----------
ring = bpy.data.objects.new("ring", None)         # 輪の中心（ここを回すと群ごと動く）
bpy.context.collection.objects.link(ring)
ring.location = (CX, CY, 0.0)

hanis, cores, roots = [], [], []
for j in range(N_HANI):
    idx = j % 4
    root = bpy.data.objects.new("root_%d" % j, None)   # 輪の上の1本ぶんの座（自転はここ）
    bpy.context.collection.objects.link(root)
    root.parent = ring
    p0 = (j - (N_HANI - 1) * 0.5) * DPHI
    root.location = (R_RING * math.sin(p0), -R_RING * math.cos(p0), ZB[idx])
    root.rotation_euler = (0.0, 0.0, p0)
    ob = link(haniwa_mesh(idx), "haniwa_%d" % j, mat_clay, parent=root)
    cm = core_material("core_mat_%d" % j)
    co = link(core_mesh(idx), "core_%d" % j, cm, parent=root)
    hanis.append(ob); cores.append(co); roots.append(root)

# 🔴 黒の肌は実ジオメトリ（#52）。**発光体には掛けない**（MATERIALS.md 掟1）
#    格子が既に細かい（セル 0.010×0.012）ので SUBSURF は要らない。DISPLACE を直に掛ける。
for ob in hanis:
    r = BLACK_RECIPES["touki"]
    tex = bpy.data.textures.new("relief_" + ob.name, 'CLOUDS'); tex.noise_scale = r["dsize"]
    d = ob.modifiers.new("disp", 'DISPLACE')
    d.texture = tex; d.strength = r["disp"]; d.mid_level = 0.5
    sol = ob.modifiers.new("sol", 'SOLIDIFY')     # 肉厚と**透孔の胴**がここで自動的に生まれる
    sol.thickness = WALL; sol.offset = -1.0; sol.use_rim = True
    bev = ob.modifiers.new("bev", 'BEVEL')        # #17：稜線が光を拾わないと黒はプラスチックになる
    bev.width = 0.0016; bev.segments = 2
    bev.limit_method = 'ANGLE'; bev.angle_limit = math.radians(30)

# --- キーフレーム（毎フレーム打つ＝イージング不使用）----------
FR = list(range(N_FRAMES)) + [N_FRAMES]          # 末尾に t=1 を打つ＝glb でループが閉じる
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f, i in enumerate(FR):
    t = i / N_FRAMES
    ring.rotation_euler = (0.0, 0.0, sway_of(t))
    ring.keyframe_insert("rotation_euler", frame=f + 1)
    for j, ob in enumerate(hanis):
        p0 = (j - (N_HANI - 1) * 0.5) * DPHI
        roots[j].rotation_euler = (0.0, 0.0, p0 + spin_of(j, t))
        roots[j].keyframe_insert("rotation_euler", frame=f + 1)

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
        caption("MIDDLE STUDY 061 — HANIWA", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
# 🔴 #67①：抜け（筒のあいだ・透孔）がある造形では逆光がそのままカメラに写る
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
core_names = {o.name for o in cores}
lit_by_lime = bpy.data.collections.new("lit_by_lime")
bpy.context.scene.collection.children.link(lit_by_lime)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name not in core_names:
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
    print(">> 占有  長辺 %.1f%%（帯 55〜65%%）  重心x %.1f%%  重心y(上から) %.1f%%"
          % (max((x1 - x0), (y1 - y0)) * 100, (x0 + x1) / 2 * 100,
             (1 - (y0 + y1) / 2) / 0.80 * 100))
    print(">> 枠まで  左%.3f 右%.3f 上%.3f 下%.3f （負なら枠外＝edge）"
          % (x0, 1 - x1, 1 - y1, y0))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_061.blend"))

# 🔴 glb は必ず最後（#25c：複雑な Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    for co in cores:
        m_em = bpy.data.materials.new(co.name + "_glb"); m_em.use_nodes = True
        pe = m_em.node_tree.nodes["Principled BSDF"]
        pe.inputs["Base Color"].default_value = BLACK
        pe.inputs["Emission Color"].default_value = LIME
        pe.inputs["Emission Strength"].default_value = ES_CORE * 0.45
        co.data.materials[0] = m_em
    scene.frame_end = N_FRAMES + 1
    names = {ring.name} | {o.name for o in roots} | {o.name for o in hanis} | core_names
    for o in bpy.data.objects:
        o.select_set(o.name in names)
    bpy.context.view_layer.objects.active = hanis[0]
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
