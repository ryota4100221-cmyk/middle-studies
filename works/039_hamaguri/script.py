# =============================================================
# monaka design. — MIDDLE STUDY 039 "HAMAGURI"（蛤 a clam / 貝合わせ）
# 黒い蛤が宙に浮き、ゆっくり口をひらく。二枚が出会う一線——貝のちょうど真ん中——
# からライム #A5E02E が差し、閉じれば光は消える。
# 蛤は、自分の片割れとしか合わない。合う一枚があることが、その貝の真ん中をつくる。
#
# 【ドメイン】貝・海／二枚貝（シリーズ未踏）。直近10作（折紙・折鶴／玩具・独楽／
#   武具・鞘／装身・櫛／調度・屏風／縄・繊維／信仰・鈴／建築・灯籠／幾何・蜂の巣／
#   植物・松毬）と別領域。38作で「海」に一度も出ていない。
#
# 【機構】二枚の殻は x=0 の合わせ面（commissural plane）に関する**厳密な鏡像**で、
#   背側のヒンジ（＝local Y 軸）まわりに ∓β/2 ずつ回るだけ。実物の二枚貝そのもの。
#     β(t) = B_MIN + (B_MAX−B_MIN)·0.5(1−cos 2πt)   ＝ 整数周期＝完全ループ
#   t=0 で閉じ（光は一条の線）、t=0.5 で最大に開く＝hero（STILL_FRAME=61）。
#
# 【光】合わせ面そのものに置いた発光の板（＝身）。#29 のとおり開口を**面で満たす**。
#   勾配は #34 の2軸だが、ここは**極座標の2軸**にした：
#     r = √((y/LEN)² + (z/HGT)²)   … 殻頂からの正規化距離。r=1 が縁（＝殻のシルエット）
#     d = √( ((r−R_HOT)/FR)² + (y/FY_EM)² ) → MapRange(ES_CORE→0, SMOOTHSTEP)
#   r=1 で ES が厳密に 0 に落ちるので**縁から光がはみ出さない**（#26②/#28 の緑スピル回避）。
#   同時に y でも落とすので、光は「縁に沿って走る帯」ではなく**真ん中がいちばん明るい三日月**に
#   なる（1軸だと #34 の「緑のテープ」）。板は Base＝純黒・Spec=0 なので、
#   光が 0 の領域は完全な黒＝**開口から白背景が抜けるのを止める裏当てを兼ねる**（#32）。
#
# 【読み（#16/#33）】「黒い小石／桃」に転ばないための署名ディテール——
#   ① 成長線（縁へ向かって密になる同心の段。#31-b の「一段細かい階層」）
#   ② 前へ曲がった殻頂（beak・ガウスの滑らかな鼻）③ 前後非対称な輪郭（左右対称の
#   卵形は必ず果実に読める）④ 大きく開く口（＝二枚の板であることの宣言）。
#   #33 の撤退条件（細い部材で中心を囲まない／大きな平円盤を使わない／単一の塊が主役で
#   光は隙間）を満たす。
#
# 【姿勢】YAW は「開口の見えやすさ」と「殻面の見えやすさ」のトレードオフ：
#   開口の画面上の幅 ∝ cos YAW（YAW=0 で最大）／殻の扇の見え ∝ sin YAW。
#   YAW=0 は前面視で細く、YAW=90° は殻面が正対する代わりに開口が奥行き方向で消える。
#   実測：32°＝袋／48°＝黒い桃／**64°＝蛤に読める**／74°＝殻面は綺麗だが二枚目が消える。
#
# 【罠を構造的に回避】object.scale / transform_apply 不使用（#15）。
#   姿勢は**静的な pose Empty に焼き**、子はヒンジの local Y 回転だけ（#9・identity）。
#   glb は必ず最後尾（#30）。
#
# 実行:
#   Blender --background --factory-startup --python monaka_hamaguri.py -- <mode...>
#   modes: probe | test | testhero | still | anim | blend | glb   （glb は #30 で必ず最後尾）
# =============================================================
import bpy
import bmesh
import math
import sys
import os
from mathutils import Vector

# ---------- パラメータ ----------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_hamaguri")
os.makedirs(OUT, exist_ok=True)

LIME_HEX = "A5E02E"
BLACK_HEX = "0A0A0A"

CENTER_Z = float(os.environ.get("CENTER_Z", "2.16"))   # ヒンジ（＝殻頂）の world 高さ
LOOK_Z = float(os.environ.get("LOOK_Z", "1.72"))
CAM_LOC = (0.55, -8.3, 1.95)

# --- 貝の寸法（shell-local：ヒンジ＝local Y 軸／腹は -Z／殻はそれぞれ ±X へ膨らむ） ---
# 輪郭は**殻頂が縁の上に載る楕円**（中心 (0,-HGT/2)・半軸 LEN×HGT/2）。
# 1周目は「殻頂を頂点とする扇（＝半楕円のD形）」で作り、hero どころか 480px で
# 「黒い革の袋／瓢箪」に転んだ（#33 の型の失敗）。二枚貝の輪郭は**閉じた卵形**で、
# 殻頂はその上辺に載る一点。ここを変えた瞬間に貝に読めた。
HGT = float(os.environ.get("HGT", "1.00"))    # 殻頂→腹縁（殻高）
LEN = float(os.environ.get("LEN", "0.75"))    # 前後の半長（殻長の半分）
BULG = float(os.environ.get("BULG", "0.26"))  # 片殻の最大の膨らみ
BULG_P = float(os.environ.get("BULG_P", "0.55"))   # 膨らみのピーク位置（s≈0.285＝殻頂寄り）
TH_REL = float(os.environ.get("TH_REL", "0.15"))     # 殻の厚み（膨らみに対する比）
T_SHELL = float(os.environ.get("T_SHELL", "0.030"))  # 身の板厚に流用
T_FLESH = 0.014                                      # 発光板の厚み

# 表面の彫り（#31-b：読みを決めるのは表面の細かい繰り返し。ただし 037 のとおり
# **細かさ**が要る。1周目 GA=0.0115／NG=12＋放射 0.0060 は 480px で「編み籠の網代」に
# 転んだ＝深すぎ・粗すぎ）
NG = int(os.environ.get("NG", "17"))            # 成長線の本数
GA = float(os.environ.get("GA", "0.0032"))      # 成長線の深さ
NR = int(os.environ.get("NR", "18"))            # 放射のうねりの本数
RA = float(os.environ.get("RA", "0.0000"))      # 放射のうねりの深さ（0＝成長線のみ）

# 殻頂の嘴は 0 にした。**殻頂 (0,0) はヒンジ回転の不動点**なので、変位を入れなければ
# 左右の殻の頂点は開いても厳密に一致する。7周目まで嘴で持ち上げていたため、開くたびに
# 頂点が軸から離れて左右にずれ、hero の背に **V 字の欠け** が出ていた（#36① の平面版
# ＝「折れ点を持つ輪郭は割れて見える」の回転版）。輪郭・成長線・前後非対称・開口の
# 4つで貝は読めるので、嘴は捨てる。
UB = float(os.environ.get("UB", "0.0"))         # 殻頂の持ち上がり
UY = float(os.environ.get("UY", "0.0"))       # 殻頂の前への曲がり（prosogyrous）
LIG_Y = float(os.environ.get("LIG_Y", "-0.26"))  # 靭帯の位置（後方＝-y）

NU = int(os.environ.get("NU", "88"))     # 中心→縁の分割（成長線を刻むので多め）
NV = int(os.environ.get("NV", "200"))    # 周方向

# --- 姿勢 ---
# 開口の見えやすさ ∝ cos YAW ／ 殻面（＝貝に読ませる扇）の見えやすさ ∝ sin YAW。
# 32° は開口が広い代わりに殻を前面視で見ることになり「袋」に転んだ（1周目）。
YAW = math.radians(float(os.environ.get("YAW", "64.0")))
PITCH = math.radians(float(os.environ.get("PITCH", "-5.0")))

# --- 運動 ---
B_MIN = math.radians(float(os.environ.get("B_MIN", "4.0")))
B_MAX = math.radians(float(os.environ.get("B_MAX", "38.0")))
BOB = float(os.environ.get("BOB", "0.016"))

# --- 発光（#34 の2軸を極座標で／#32：暗部は純黒＝裏当てを兼ねる） ---
ES_CORE = float(os.environ.get("ES_CORE", "10.5"))
R_HOT = float(os.environ.get("R_HOT", "0.975"))    # 光の帯の位置（s：1.0＝縁）
FR_EM = float(os.environ.get("FR_EM", "0.115"))    # 帯の幅（s=1 で 0 に落ちる）
FY_EM = float(os.environ.get("FY_EM", "0.50"))     # 前後方向の落ち（芯を真ん中に残す）
GLOW_E = float(os.environ.get("GLOW_E", "1.3"))    # 殻の内側を洗うこぼれ光（#22）

# --- 材質（#17：曲面／#17-c・037：曲面＋細かい筋は env を線状に拾うので反射率を落とす） ---
SPEC_SHELL = float(os.environ.get("SPEC_SHELL", "0.07"))
ROUGH_SHELL = float(os.environ.get("ROUGH_SHELL", "0.40"))

CAP_Z = (float(os.environ.get("CAP_Z1", "0.66")),
         float(os.environ.get("CAP_Z2", "0.48")),
         float(os.environ.get("CAP_Z3", "0.36")))

FPS = 24
N_FRAMES = 120            # 5.000秒 完全ループ
STILL_FRAME = 61          # t=0.5 ＝ いちばん開いていちばん明るい


def hex_to_linear(h):
    """sRGB hex → Blender linear RGB（PITFALL #4）"""
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def s2l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return tuple(s2l(u) for u in c) + (1.0,)


LIME = hex_to_linear(LIME_HEX)
BLACK = hex_to_linear(BLACK_HEX)


# ---------- 数式 ----------
def beta_at(t01):
    """口の開き。cos の整数周期＝厳密に閉じる。"""
    return B_MIN + (B_MAX - B_MIN) * 0.5 * (1.0 - math.cos(2.0 * math.pi * t01))


def bob_at(t01):
    return BOB * math.cos(2.0 * math.pi * t01)


B_ELL = HGT * 0.5          # 輪郭楕円の縦半軸（中心 z=-B_ELL・殻頂 (0,0) が縁の上に載る）
# 前後非対称（#33 の型）：左右対称の卵形は 480px でも hero でも**果実**に読める。
# 実物の蛤は殻頂が前寄りで、後ろが長く伸びる。上下の接点（殻頂・腹縁）では
# どちらの半楕円も接線が水平なので、半軸だけ前後で変えれば輪郭は滑らかに繋がる。
ASYM = float(os.environ.get("ASYM", "0.18"))
LEN_A = LEN * (1.0 - ASYM)     # 前（+y）＝短い
LEN_P = LEN * (1.0 + ASYM)     # 後（-y）＝長い


def s_of(y, z):
    """(y,z) → 殻頂 (0,0) からの正規化距離 s（s=1 がちょうど縁）。閉形式。
    輪郭楕円 y²/L² + (z+B)²/B² = 1 上の点を s 倍した点が (y,z) ⇔
      s = ( y²·B/L² + z²/B ) / (−2z)        （z<0 なので常に正）
    シェーダ側の勾配もこれと同じ式を使う（#34 の2軸の長軸）。"""
    if z > -1e-9:
        return 0.0
    L = LEN_A if y >= 0.0 else LEN_P
    return ((y * y) * (B_ELL / (L * L)) + (z * z) / B_ELL) / (-2.0 * z)


def disk(u, psi):
    """楕円板の極座標 (u∈[0,1]＝中心からの割合, psi∈[0,2π)) → 合わせ面上の (y, z)。
    psi=0 が腹縁・psi=π が殻頂。**極は楕円の中心ただ1つ**。
    4周目まで使っていた「殻頂を極とする扇」は、殻頂に全列が潰れて極薄スリバーが
    数千個たまり、solidify がそれを **hero で左右に伸びる黒い刃** に押し出していた。
    円盤に張り替えて構造的に解消（#15 の延長＝罠は起こさない書き方にする）。"""
    L = LEN_A if math.sin(psi) >= 0.0 else LEN_P
    y = u * L * math.sin(psi)
    z = -B_ELL - u * B_ELL * math.cos(psi)
    # 殻頂の嘴（beak・前へ曲がる）。ガウスなので折れ点が出ない。
    d = math.hypot(y, z) / (0.30 * HGT)
    g = math.exp(-d * d)
    return y, z, y + UY * LEN * g, z + UB * HGT * g


def bulge_at(u, psi, ripple=True):
    """合わせ面からの膨らみ（片殻・正値）。s=1（縁）で 0＝二枚がぴたりと合う。"""
    y, z, _, _ = disk(u, psi)
    s = min(1.0, s_of(y, z))
    env = math.sin(math.pi * (s ** BULG_P))
    rip = (s ** 0.5) * max(0.0, 1.0 - s ** 3.0)   # 縁へ向かって強くなる成長線
    # 成長線は **env を掛けて** 膨らみに従わせる。5周目までは env とは独立に足していたので
    # 殻頂近く（env→0）で base が負になり max(0,·) でフラットに潰れ、**左右の殻が x=0 で
    # 面を共有**して hero の殻頂に**ギザギザの欠け**が出た（＝coincident face）。
    if not ripple:
        return env * BULG
    return env * (BULG + rip * (GA * math.sin(2.0 * math.pi * NG * (s ** 1.30))
                                + RA * math.cos(psi * NR)))


def screen_y(z, y=0.0):
    """レンダー前に構図を数値で当てる（#16/#18）。-1..+1 が縦フレーム。"""
    dist = y - CAM_LOC[1]
    half = math.tan(math.atan(18.0 / 85.0)) * dist
    cz = CAM_LOC[2] + (LOOK_Z - CAM_LOC[2]) * (dist / (0.0 - CAM_LOC[1]))
    return (z - cz) / half


# ---------- シーン初期化 ----------
scene = bpy.context.scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


# ---------- マテリアル ----------
def make_principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


mat_shell, b = make_principled("hamaguri_shell")
b.inputs["Base Color"].default_value = BLACK
b.inputs["Roughness"].default_value = ROUGH_SHELL
b.inputs["Specular IOR Level"].default_value = SPEC_SHELL
b.inputs["Coat Weight"].default_value = 0.0

# 光＝合わせ面に置いた発光の板（身）。#32：Base は**純黒**（裏当てを兼ねる）
mat_flesh, flesh_bsdf = make_principled("hamaguri_light")
flesh_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
flesh_bsdf.inputs["Emission Color"].default_value = LIME
flesh_bsdf.inputs["Roughness"].default_value = 0.5
flesh_bsdf.inputs["Specular IOR Level"].default_value = 0.0

mat_floor, b = make_principled("floor_white")
b.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
b.inputs["Roughness"].default_value = 0.42
b.inputs["Specular IOR Level"].default_value = 0.4

mat_text, b = make_principled("caption")
b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
b.inputs["Roughness"].default_value = 0.8


# ---------- ジオメトリ・ヘルパ（#15：実寸で頂点を作る／scale・transform_apply 不使用） ----------
def finish(name, bm, mat, smooth=True):
    me = bpy.data.meshes.new(name)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def add_poly(bm, pts):
    vs = [bm.verts.new(tuple(p)) for p in pts]
    bm.faces.new(vs)
    bm.verts.index_update()
    return vs


def add_grid(bm, rows):
    """rows[i] = その行の頂点列（同じ長さ）。四角形で張る。"""
    vs = [[bm.verts.new(tuple(p)) for p in row] for row in rows]
    for i in range(len(rows) - 1):
        for j in range(len(rows[0]) - 1):
            bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    return vs


def add_bevel(o, width=0.0030):
    """#10：ANGLE 制限で鋭角の辺だけ面取り。縁を立たせる。"""
    bev = o.modifiers.new("bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)


# ---------- 造形：片殻／身（どちらも同じ楕円板メッシュ） ----------
def build_disk(name, k, mat, thickness, nu, nv, smooth=True, bevel=False, zk=1.0):
    """k=±1 の殻／k=0 の身（合わせ面の平板）。
    殻は **外面と内面を縁で縫った閉じたレンズ**として作る（開いたシェル＋solidify を
    やめた）。縁で膨らみが 0 に落ちる形に solidify を掛けると、法線が反転する薄い帯で
    リムの壁が捻れ、**殻頂に三角の帆のようなスパイク**が林立した（5〜6周目の hero）。
    閉じた多様体なら solidify 自体が要らないので、罠が構造的に消える（#15 の発想）。
    厚みは膨らみに比例＝縁がナイフエッジ＝実物の貝殻と同じ。"""
    bm = bmesh.new()

    def pt(u, psi, inner):
        _, _, y, z = disk(u, psi)
        if k:
            bl = bulge_at(u, psi, ripple=not inner)
            x = k * bl * ((1.0 - TH_REL) if inner else 1.0)
        else:
            x = (thickness * 0.5) * (-1.0 if inner else 1.0)
        return (x, y, z * zk)

    outer = [[bm.verts.new(pt(i / nu, 2.0 * math.pi * j / nv, False)) for j in range(nv)]
             for i in range(1, nu + 1)]
    inner = [[bm.verts.new(pt(i / nu, 2.0 * math.pi * j / nv, True)) for j in range(nv)]
             for i in range(1, nu)]
    c_out = bm.verts.new(pt(0.0, 0.0, False))
    c_in = bm.verts.new(pt(0.0, 0.0, True))

    def fan(ctr, ring, flip):
        for j in range(nv):
            j2 = (j + 1) % nv
            f = (ctr, ring[j], ring[j2])
            bm.faces.new(f[::-1] if flip else f)

    def band(r0, r1, flip):
        for j in range(nv):
            j2 = (j + 1) % nv
            f = (r0[j], r0[j2], r1[j2], r1[j])
            bm.faces.new(f[::-1] if flip else f)

    fan(c_out, outer[0], False)
    for i in range(len(outer) - 1):
        band(outer[i], outer[i + 1], False)
    band(outer[-1], inner[-1], False)          # 縁（ナイフエッジ）で外面と内面を縫う
    for i in range(len(inner) - 1, 0, -1):
        band(inner[i], inner[i - 1], False)
    fan(c_in, inner[0], True)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish(name, bm, mat, smooth=smooth)
    if bevel:
        add_bevel(o)
    return o


valve_R = build_disk("valve_R", +1, mat_shell, T_SHELL, NU, NV, bevel=True)
valve_L = build_disk("valve_L", -1, mat_shell, T_SHELL, NU, NV, bevel=True)
# 身（＝発光板・裏当て）は殻より **cos(β_max/2) だけ縦に潰す**。
# ヒンジ（local Y 軸）まわりに γ 回した殻の縁は、合わせ面へ投影すると z が cosγ 倍に
# 縮む＝**回さない板の方が必ず大きい**。5周目の hero では板が殻の外に黒いフランジとして
# はみ出し、殻頂で**ギザギザの欠け**に見えた（しかも粗い分割だったので階段状）。
# hero の位相（β_max）でちょうど縁が一致するよう潰し、他の位相では殻の内側に隠れる。
ZK = math.cos(B_MAX * 0.5)
flesh = build_disk("flesh", 0, mat_flesh, T_FLESH, NU, NV, smooth=False, zk=ZK)

# 靭帯（背側の留め具）は 4周目に廃止：殻頂の裏から**刃状に突き出て**hero で
# 「裂け目」に見えた。嘴（beak）だけで二枚貝の背側は読める。#31-c の留め具は
# 縄のように「切り口」がある場合の話で、蛤の背は元々閉じている。
STATIC = [flesh]


# ---------- リグ（#9：姿勢は静的 Empty に焼き、子はヒンジ回転だけ） ----------
bpy.ops.object.empty_add(location=(0.0, 0.0, CENTER_Z))
rig_pose = bpy.context.active_object
rig_pose.name = "hamaguri_pose"
rig_pose.rotation_euler = (PITCH, 0.0, YAW)

for o in (valve_R, valve_L) + tuple(STATIC):
    o.parent = rig_pose
    o.location = (0.0, 0.0, 0.0)      # ヒンジ＝メッシュの原点


# ---------- 発光の勾配（#34 の2軸／極座標版：r=1＝縁で厳密に 0） ----------
_ct = mat_flesh.node_tree
_tc = _ct.nodes.new("ShaderNodeTexCoord")
_sep = _ct.nodes.new("ShaderNodeSeparateXYZ")
_ct.links.new(_tc.outputs["Object"], _sep.inputs["Vector"])


def _m(op, a=None, b=None, val=None):
    n = _ct.nodes.new("ShaderNodeMath")
    n.operation = op
    if a is not None:
        _ct.links.new(a, n.inputs[0])
    if b is not None:
        _ct.links.new(b, n.inputs[1])
    if val is not None:
        n.inputs[1].default_value = val
    return n.outputs[0]


# s ＝ 殻頂 (0,0) からの正規化距離（s=1 がちょうど縁＝殻のシルエット）。
# 輪郭楕円 y²/LEN² + (z+B)²/B² = 1 上の点を s 倍した点が (y,z) ⇔
#   s = ( y²·B/LEN² + z²/B ) / (−2z)     （z<0 なので常に正・閉形式で解ける）
# これで**縁で厳密に ES=0** に落とせる＝緑スピルが構造的に出ない（#26②/#28）。
_y2 = _m('MULTIPLY', _sep.outputs["Y"], _sep.outputs["Y"])
_z2 = _m('MULTIPLY', _sep.outputs["Z"], _sep.outputs["Z"])
_sel = _m('GREATER_THAN', _sep.outputs["Y"], val=0.0)        # 前(+y)なら1
_kA, _kP = (B_ELL * ZK) / (LEN_A * LEN_A), (B_ELL * ZK) / (LEN_P * LEN_P)
_k = _m('ADD', _m('MULTIPLY', _sel, val=_kA - _kP), val=_kP)
_num = _m('ADD', _m('MULTIPLY', _y2, _k),
          _m('MULTIPLY', _z2, val=1.0 / (B_ELL * ZK)))
_r = _m('DIVIDE', _num, _m('MULTIPLY', _sep.outputs["Z"], val=-2.0))
# 軸1：帯の中心 R_HOT からの距離／FR_EM
_u1 = _m('MULTIPLY', _m('ABSOLUTE', _m('SUBTRACT', _r, val=R_HOT)), val=1.0 / FR_EM)
# 軸2：前後方向（#34：短軸を入れないと「緑のテープ」）
_u2 = _m('MULTIPLY', _sep.outputs["Y"], val=1.0 / FY_EM)
_d = _m('SQRT', _m('ADD', _m('MULTIPLY', _u1, _u1), _m('MULTIPLY', _u2, _u2)))

_mr = _ct.nodes.new("ShaderNodeMapRange")
_mr.inputs["From Min"].default_value = 0.0
_mr.inputs["From Max"].default_value = 1.0
_mr.inputs["To Min"].default_value = ES_CORE
_mr.inputs["To Max"].default_value = 0.0      # #32：暗部は完全な黒
_mr.clamp = True
try:
    _mr.interpolation_type = 'SMOOTHSTEP'
except Exception:
    pass
_ct.links.new(_d, _mr.inputs["Value"])
_ct.links.new(_mr.outputs["Result"], flesh_bsdf.inputs["Emission Strength"])

# 殻の内側を洗うこぼれ光（#22：面積で稼ぎ強度で稼がない）
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.0))
glow = bpy.context.active_object
glow.name = "hamaguri_glow"
glow.data.color = (LIME[0], LIME[1], LIME[2])
glow.data.energy = GLOW_E
glow.data.shadow_soft_size = 0.30
glow.parent = rig_pose
glow.location = (0.0, 0.0, -HGT * 0.80)
try:
    glow.visible_camera = False
except Exception:
    pass


# ---------- アニメーション（毎フレームキー #1 ／完全ループ） ----------
scene.frame_start = 1
scene.frame_end = N_FRAMES
scene.render.fps = FPS

for f in range(1, N_FRAMES + 1):
    t = (f - 1) / N_FRAMES
    bt = beta_at(t)
    valve_R.rotation_euler = (0.0, -bt * 0.5, 0.0)
    valve_R.keyframe_insert(data_path="rotation_euler", frame=f)
    valve_L.rotation_euler = (0.0, bt * 0.5, 0.0)
    valve_L.keyframe_insert(data_path="rotation_euler", frame=f)
    rig_pose.location = (0.0, 0.0, CENTER_Z + bob_at(t))
    rig_pose.keyframe_insert(data_path="location", frame=f)


# ---------- 床・キャプション ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat_floor)

bpy.ops.object.empty_add(location=(0, 0, CENTER_Z - HGT * 0.5))
focus_null = bpy.context.active_object
focus_null.name = "focus_null"


def add_caption(body_text, size, loc, name):
    bpy.ops.object.text_add(location=loc)
    tx = bpy.context.active_object
    tx.name = name
    tx.data.body = body_text
    tx.data.size = size
    tx.data.align_x = 'CENTER'
    try:
        tx.data.font = bpy.data.fonts.load("/System/Library/Fonts/Helvetica.ttc")
    except Exception:
        pass
    tx.data.materials.append(mat_text)
    return tx


# #20-b：キャプションは y=-1.3（カメラ寄り）で z が大きな px 間隔に拡大。
tagline = add_caption("Designing the Middle of Your Story.",
                      0.1, (0.15, -1.3, CAP_Z[0]), "tagline")
logo = add_caption("monaka design.", 0.06, (0.15, -1.3, CAP_Z[1]), "logo")
study = add_caption("MIDDLE STUDY 039 — HAMAGURI", 0.045, (0.15, -1.3, CAP_Z[2]), "study")


# ---------- ライティング（001と同一＝シリーズの一貫性） ----------
def add_area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.size = size
    L.data.energy = energy
    L.data.color = color
    direction = Vector(target) - Vector(loc)
    L.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return L


focus = (0, 0, CENTER_Z - HGT * 0.5)
add_area("key",  (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
add_area("rim",  (3.5, 4.0, 3.2),  3.0, 420, (0.88, 0.94, 1.0), focus)
add_area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)

world = bpy.data.worlds.new("studio") if scene.world is None else scene.world
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1)
    bg.inputs[1].default_value = 0.55


# ---------- カメラ ----------
bpy.ops.object.camera_add(location=CAM_LOC)
cam = bpy.context.active_object
cam.name = "hero_cam"
cam.data.lens = 85
look = Vector((0.1, 0, LOOK_Z))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus_null
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam

for tx in (tagline, logo, study):
    tx.rotation_euler = cam.rotation_euler


# ---------- レンダー設定 ----------
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for dev in prefs.devices:
        dev.use = True
    scene.cycles.device = 'GPU'
    print(">> Metal GPU enabled")
except Exception as e:
    print(">> GPU setup failed, using CPU:", e)

scene.cycles.use_denoising = True
try:
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
    print(">> view: PBR Neutral")
except Exception:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Punchy'
    print(">> view: AgX Punchy")


# ---------- コンポジター（Bloom / PITFALL #3の新方式） ----------
def setup_bloom():
    try:
        ng = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out='OUTPUT',
                                socket_type='NodeSocketColor')
        rl = ng.nodes.new("CompositorNodeRLayers")
        glare = ng.nodes.new("CompositorNodeGlare")
        out = ng.nodes.new("NodeGroupOutput")
        try:
            glare.inputs["Type"].default_value = 'BLOOM'
        except Exception:
            pass
        glare.inputs["Threshold"].default_value = 1.2
        glare.inputs["Strength"].default_value = 0.35
        try:
            glare.inputs["Size"].default_value = 0.55
        except Exception:
            pass
        ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
        ng.links.new(glare.outputs["Image"], out.inputs["Image"])
        scene.compositing_node_group = ng
        scene.render.use_compositing = True
        print(">> Bloom compositor OK")
    except Exception as e:
        print(">> Bloom setup failed (render continues without):", e)


setup_bloom()


# ---------- 出力モード ----------
modes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test"]
print(">> modes:", modes)

if "probe" in modes:
    # #16/#18：レンダーで目視する前に構図と幾何を数値で当てる。
    dg = bpy.context.evaluated_depsgraph_get()
    for f in (1, STILL_FRAME, N_FRAMES // 4 + 1):
        scene.frame_set(f)
        dg.update()
        xs, zs, ys = [], [], []
        for o in (valve_R, valve_L, flesh):
            ob = o.evaluated_get(dg)
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                xs.append(w.x)
                zs.append(w.z)
                ys.append(w.y)
        t = (f - 1) / N_FRAMES
        bt = beta_at(t)
        gap = 2.0 * HGT * math.sin(bt * 0.5)
        print(f">> f{f} β={math.degrees(bt):.1f}° 腹縁の開き={gap:.3f}m "
              f"(画面上 {gap * math.cos(YAW):.3f}m) "
              f"横 {min(xs):+.2f}..{max(xs):+.2f} ({max(xs)-min(xs):.2f}/2.81="
              f"{(max(xs)-min(xs))/2.81*100:.0f}%)  "
              f"縦 {min(zs):.2f}..{max(zs):.2f} ({max(zs)-min(zs):.2f}/3.52="
              f"{(max(zs)-min(zs))/3.52*100:.0f}%)  奥行 {min(ys):+.2f}..{max(ys):+.2f}")
        print(f"   screen 縦 {screen_y(min(zs)):+.3f}..{screen_y(max(zs)):+.3f} "
              f"{'OK' if abs(screen_y(min(zs))) < 0.97 and abs(screen_y(max(zs))) < 0.97 else 'WARN 切れる'}")
    scene.frame_set(STILL_FRAME)
    for i, cz in enumerate(CAP_Z):
        print(f">> caption{i + 1} z={cz:.2f} → screen {screen_y(cz, -1.3):+.3f} "
              f"({'OK' if abs(screen_y(cz, -1.3)) < 0.98 else 'WARN 枠外'})")
    # 発光の勾配：縁（r=1）と殻頂（r=0）で ES が 0 に落ちるか＝スピルしないか
    def es(r, y):
        d = math.hypot(abs(r - R_HOT) / FR_EM, y / FY_EM)
        x = min(1.0, max(0.0, d))
        return ES_CORE * (1.0 - (x * x * (3 - 2 * x)))
    print(f">> 勾配 r={R_HOT}±{FR_EM} ／ y falloff {FY_EM}")
    for (r, y, tag) in ((R_HOT, 0.0, "芯"), (1.0, 0.0, "縁(=シルエット)"),
                        (0.72, 0.0, "内側"), (R_HOT, LEN * 0.85, "前後端")):
        print(f"   r={r:.2f} y={y:+.2f} ({tag}) → ES {es(r, y):.2f}")
    print("   " + ("OK（縁で 0＝緑スピルなし・芯が真ん中に残る #34/#28）"
                   if es(1.0, 0.0) < 0.01 and es(R_HOT, LEN * 0.85) < 0.6 else "WARN"))
    # 見える帯の幅：視線は合わせ面と YAW の角をなすので、開口 Δ から内へ Δ/tan(YAW)
    dlt = HGT * math.sin(B_MAX * 0.5)
    reach = dlt / math.tan(YAW)
    print(f">> 開口 Δ={dlt:.3f}m → 板が見える帯の幅 ≈ {reach:.3f}m "
          f"(= r で {reach / HGT:.3f}) 芯は縁から {(1 - R_HOT) * HGT:.3f}m 内側 "
          f"{'OK（芯が帯の中）' if (1 - R_HOT) * HGT < reach else 'WARN 芯が殻に隠れる'}")
    print(f">> loop: β=B_MIN+(B_MAX-B_MIN)·0.5(1-cos2πt) ＝整数周期＝t=0とt=1が厳密一致 / "
          f"{N_FRAMES}f {N_FRAMES / FPS:.3f}s")


if "bbox" in modes:
    dg = bpy.context.evaluated_depsgraph_get()
    scene.frame_set(STILL_FRAME)
    dg.update()
    for o in (valve_R, valve_L, flesh):
        ob = o.evaluated_get(dg)
        ws = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        print(">> %-9s x %+.3f..%+.3f  y %+.3f..%+.3f  z %+.3f..%+.3f  verts=%d"
              % (o.name, min(w.x for w in ws), max(w.x for w in ws),
                 min(w.y for w in ws), max(w.y for w in ws),
                 min(w.z for w in ws), max(w.z for w in ws), len(ob.data.vertices)))
        # 最も外側の頂点（world x 最小/最大）のローカル座標を出す
        vs = [(ob.matrix_world @ v.co, v.co) for v in ob.data.vertices]
        for tag, key in (("x-min", lambda t: t[0].x), ("x-max", lambda t: -t[0].x)):
            w, l = min(vs, key=key)
            print("     %s world(%+.3f,%+.3f,%+.3f) local(%+.4f,%+.4f,%+.4f)"
                  % (tag, w.x, w.y, w.z, l.x, l.y, l.z))

if "blend" in modes:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hamaguri.blend"))
    print(">> saved .blend")

if "test" in modes:
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.cycles.samples = 24
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> test render done")

if "testhero" in modes:
    # PITFALL #16：480pxでは「何に見えるか」が見えない。造形が固まったら hero で目視。
    scene.frame_set(int(os.environ.get("TESTFRAME", STILL_FRAME)))
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, os.environ.get("TESTNAME", "test_hero") + ".png")
    bpy.ops.render.render(write_still=True)
    print(">> hero-size test done")

if "still" in modes:
    scene.frame_set(STILL_FRAME)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 2000
    scene.cycles.samples = 96
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(OUT, "hero.png")
    bpy.ops.render.render(write_still=True)
    print(">> hero still done")

if "anim" in modes:
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.cycles.samples = 16
    scene.render.image_settings.media_type = 'VIDEO'   # PITFALL #2
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = os.path.join(OUT, "monaka_loop.mp4")
    bpy.ops.render.render(animation=True)
    print(">> loop animation done")

# 🔴 PITFALL #30：glb は Emission を定数へ潰す副作用があるので必ず最後尾に置く。
if "glb" in modes:
    try:
        for lk in list(flesh_bsdf.inputs["Emission Strength"].links):
            mat_flesh.node_tree.links.remove(lk)
        flesh_bsdf.inputs["Emission Strength"].default_value = 3.0
    except Exception as e:
        print(">> light emission simplify skipped:", e)
    scene.frame_set(STILL_FRAME)
    keep = {valve_R.name, valve_L.name, rig_pose.name} | {o.name for o in STATIC}
    for o in bpy.data.objects:
        o.select_set(o.name in keep)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, "hamaguri.glb"),
        export_format='GLB',
        use_selection=True,
        export_animations=True,
        export_yup=True,
    )
    print(">> exported GLB")


print(">> ALL DONE")
