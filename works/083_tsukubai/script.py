# =============================================================
# MIDDLE STUDY 083 — TSUKUBAI（蹲踞 / the water only gathers in the middle）
#
#   光の型＝面（#53）  構図の型＝寄り（#57・面×寄りはシリーズ初）  ドメイン＝庭・手水
#
# 茶庭の蹲踞は、ひとつの石の真ん中を刳って水を張ったものだ。
# 石は大きく、縁は低い。立ったままでは水に手が届かない——だから人は蹲う（つくばう）。
# 水は筧（かけい）から落ちてくる。石のどこに落ちても、**水が溜まるのは真ん中だけ**。
# 落ちた一滴は輪になって縁まで行き、縁で消えて、また静かな面に戻る。
#
# 造形：石は1本の断面（刳り→口縁→天端→肩→胴→底）を θ ごとに歪めて回した回転体（boolean 不使用）。
#       肌は `touki`（陶＝石）＋実起伏。筧は節のある竹で、画面の右の外から来る。
#
# 光：面。水面そのものが光る。静的な勾配は平ら（#62①）にして、明るさの模様は波紋にだけ担わせる。
#     波紋は 1ループに2滴＝位相 a=frac(2t) の1周期で閉じる（a=0 と a→1 で振幅0）。
#
# 動き：石の倒れ α(t)（cos）＋ わずかな首振り（sin）＋ 上下の漂い。滴は筧の口で育って落ちる。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = float(os.environ.get("LIME_W", "55"))                     # 随伴のライム光源（#58）

# --- 石 ------------------------------------------------------------
R_S    = 2.10                      # 石の半径（寄り：左右は枠の外）
RB     = 0.56                      # 刳り（水穴）の口縁の半径
Z_W    = -0.11                    # 水面の高さ（天端=0）
NT, NS = 160, 96

# --- 光（面）------------------------------------------------------
B0      = 0.38                     # 静かな水面の明るさ
EDGE_P  = 4.0                      # 平場のべき（#62①：縁の手前まで平ら）
EDGE_K  = 0.85
ES_CORE = 5.4
WHITE_FROM, WHITE_TO = 0.85, 0.45
K_MIX   = 1.6
DROPS   = 2                        # 1ループの滴の数
V_RING  = 1.60                     # 輪の速さ（u/位相）
LAMBDA  = 0.20                     # 波長（u）
SIGMA   = 0.24                     # 波束の幅（u）
AMP0    = 1.00

# --- 筧 ------------------------------------------------------------
SP_R   = 0.105
SP_Z   = 0.40                      # 天端からの高さ（口）
SP_TIP = (0.24, 0.02)               # 口の位置（x,y）＝水面の真ん中の上

# --- 動き --------------------------------------------------------
ALPHA0, DALPHA = 68.0, 5.0         # こちらへの倒れ（度）
GAMMA0, DGAMMA = -4.0, 4.0         # 首振り（度）
BOB    = 0.03
CX, CZ = 0.55, 2.60
STILL_FRAME = 19


# =============================================================
# 純 math
# =============================================================
def smooth(e0, e1, x):
    if e1 == e0:
        return 0.0
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def lerp(a, b, t):
    return a + (b - a) * t


E_OFF = 0.90                       # 刳りは石の中心から手前へずれている（自然石の蹲踞）


def stone_irreg(th):
    """自然石の輪郭の揺らぎ×偏心（外側だけに効かせる）。刳りの中心から見た外周までの距離の比"""
    e = E_OFF
    ecc = (e * math.sin(th) + math.sqrt(R_S * R_S - (e * math.cos(th)) ** 2)) / R_S
    return ecc * (1.0 + 0.055 * math.sin(2 * th + 0.7) + 0.035 * math.sin(3 * th + 2.1) + 0.018 * math.sin(5 * th + 4.0))


# 断面：(r, z, w)  w＝外側の揺らぎを効かせる重み（口縁は円のまま）
PROFILE = [
    (RB - 0.05,  -0.24, 0.0),
    (RB - 0.012, -0.12, 0.0),
    (RB,         -0.03, 0.0),
    (RB + 0.03,   0.0, 0.05),
    (RB + 0.15,   0.010, 0.15),
    (1.10,        0.020, 0.55),
    (1.70,        0.0, 0.90),
    (1.95,       -0.05, 1.0),
    (2.07,       -0.18, 1.0),
    (2.10,       -0.45, 1.0),
    (2.04,       -0.70, 1.0),
    (1.85,       -0.88, 1.0),
    (1.20,       -0.98, 0.9),
    (0.40,       -1.00, 0.6),
    (0.0,        -1.00, 0.0),
]


def profile_at(s):
    """s∈[0,1] を断面の折れ線の弧長で補間（Catmull-Rom 風に丸める）"""
    P = PROFILE
    L = [0.0]
    for i in range(1, len(P)):
        L.append(L[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    x = s * L[-1]
    for i in range(1, len(P)):
        if x <= L[i] or i == len(P) - 1:
            u = (x - L[i - 1]) / max(1e-9, L[i] - L[i - 1])
            p0 = P[max(i - 2, 0)]; p1 = P[i - 1]; p2 = P[i]; p3 = P[min(i + 1, len(P) - 1)]
            u2, u3 = u * u, u * u * u
            out = []
            for c in range(3):
                out.append(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u
                                  + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u2
                                  + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u3))
            return out
    return list(P[-1])


def wave_of(t):
    """位相 a, 輪の半径 ρ(u), 振幅 A。a=0 と a→1 で A=0 ＝閉じる"""
    a = (DROPS * t) % 1.0
    rho = V_RING * a
    A = AMP0 * math.exp(-0.6 * a) * smooth(0.0, 0.035, a) * (1.0 - smooth(0.66, 0.96, a))
    return a, rho, A


def alpha_of(t):
    return math.radians(ALPHA0 + DALPHA * math.cos(2.0 * math.pi * t))


def gamma_of(t):
    return math.radians(GAMMA0 + DGAMMA * math.sin(2.0 * math.pi * t))


def rot_of(t):
    """世界 = Rz(γ)·Rx(α)"""
    a, g = alpha_of(t), gamma_of(t)
    Rz = ((math.cos(g), -math.sin(g), 0), (math.sin(g), math.cos(g), 0), (0, 0, 1))
    Rx = ((1, 0, 0), (0, math.cos(a), -math.sin(a)), (0, math.sin(a), math.cos(a)))
    return tuple(tuple(sum(Rz[i][k] * Rx[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def center_of(t):
    return (CX, 0.0, CZ + BOB * math.sin(2.0 * math.pi * t))


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

# ---------- マテリアル（MATERIALS.md・#52） ----------
# 蹲踞＝石。`touki`（触ると少しざらつく）
ISHI = dict(rough=0.58, spec=0.26, disp=0.009, dsize=0.10)


def apply_black(p):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = ISHI["rough"]
    p.inputs["Specular IOR Level"].default_value = ISHI["spec"]   # 🔴 0.10 を割らない（#45）


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_body, bp_ = principled("ishi")
apply_black(bp_)
mat_take, kp_ = principled("take")
apply_black(kp_)
kp_.inputs["Roughness"].default_value = 0.52      # 竹：漆の値だと銀のパイプ（#93④）
kp_.inputs["Specular IOR Level"].default_value = 0.22

WAVE_NODES = {}


def glow_material(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')

    def M(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        for idx, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[idx].default_value = x
            else:
                nt.links.new(x, n.inputs[idx])
        return n.outputs[0]

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    u = sep.outputs["X"]

    v_rho = nt.nodes.new("ShaderNodeValue"); v_rho.name = "rho"
    v_amp = nt.nodes.new("ShaderNodeValue"); v_amp.name = "amp"
    WAVE_NODES["rho"], WAVE_NODES["amp"] = v_rho, v_amp

    # 平場：P(u) = 1 − K·u^p
    prof = M('SUBTRACT', 1.0, M('MULTIPLY', EDGE_K, M('POWER', u, EDGE_P)))
    # 波束：A·cos(2π d/λ)·exp(−(d/σ)²)   d = u − ρ
    # 輪の中心は滴の落ちる点（筧の口の真下）
    uv2 = nt.nodes.new("ShaderNodeUVMap"); uv2.uv_map = "xy"
    dv = nt.nodes.new("ShaderNodeVectorMath"); dv.operation = 'DISTANCE'
    nt.links.new(uv2.outputs["UV"], dv.inputs[0])
    dv.inputs[1].default_value = (SP_TIP[0] / (RB - 0.010), SP_TIP[1] / (RB - 0.010), 0.0)
    d = M('SUBTRACT', dv.outputs["Value"], v_rho.outputs[0])
    cosw = M('SUBTRACT', M('COSINE', M('MULTIPLY', d, 2.0 * math.pi / LAMBDA)), 0.45)   # 谷を広く＝波の立つあいだ面が欠ける
    env = M('EXPONENT', M('MULTIPLY', -1.0, M('POWER', M('DIVIDE', d, SIGMA), 2.0)))
    wave = M('MULTIPLY', M('MULTIPLY', cosw, env), v_amp.outputs[0])
    E = M('MAXIMUM', 0.0, M('MULTIPLY', prof, M('ADD', B0, wave)))

    wmr = nt.nodes.new("ShaderNodeMapRange"); wmr.clamp = True
    wmr.inputs["From Min"].default_value = WHITE_FROM
    wmr.inputs["From Max"].default_value = 1.15
    wmr.inputs["To Min"].default_value = 0.0
    wmr.inputs["To Max"].default_value = WHITE_TO
    nt.links.new(E, wmr.inputs["Value"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
    mixc.inputs[6].default_value = LIME
    mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(wmr.outputs["Result"], mixc.inputs[0])

    emi = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mixc.outputs[2], emi.inputs["Color"])
    nt.links.new(M('MULTIPLY', E, ES_CORE), emi.inputs["Strength"])

    blk = nt.nodes.new("ShaderNodeBsdfPrincipled")
    blk.inputs["Base Color"].default_value = BLACK
    blk.inputs["Roughness"].default_value = 0.08       # 水：暗いところは艶の黒
    blk.inputs["Specular IOR Level"].default_value = 0.5

    fac = M('MINIMUM', 1.0, M('MULTIPLY', E, K_MIX))
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fac, mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def drop_material(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Emission Color"].default_value = LIME
    p.inputs["Emission Strength"].default_value = 2.6
    return m


mat_glow = glow_material("mizu")
mat_drop = drop_material("shizuku")


# ---------- 造形（bmesh・実寸。boolean 不使用）----------
def stone_mesh(name):
    bm = bmesh.new()
    rows = []
    for j in range(NS + 1):
        r0, z0, w = profile_at(j / NS)
        ring = []
        for k in range(NT):
            th = 2 * math.pi * k / NT
            f = lerp(1.0, stone_irreg(th), w)
            r = r0 * f
            z = z0 + w * 0.025 * math.sin(3 * th + 1.3) * (1 if z0 > -0.3 else 0.4)
            ring.append(bm.verts.new((r * math.cos(th), r * math.sin(th), z)))
        rows.append(ring)
    for j in range(NS):
        for k in range(NT):
            k2 = (k + 1) % NT
            try:
                bm.faces.new((rows[j][k], rows[j][k2], rows[j + 1][k2], rows[j + 1][k]))
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def water_mesh(name, nr=56, nt=160):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    uvx = bm.loops.layers.uv.new("xy")
    Rw = RB - 0.010
    c = bm.verts.new((0, 0, Z_W))
    rows = []
    umap = {c: 0.0}
    for j in range(1, nr + 1):
        uu = j / nr
        ring = []
        for k in range(nt):
            th = 2 * math.pi * k / nt
            v = bm.verts.new((Rw * uu * math.cos(th), Rw * uu * math.sin(th), Z_W))
            umap[v] = uu
            ring.append(v)
        rows.append(ring)
    for k in range(nt):
        bm.faces.new((c, rows[0][k], rows[0][(k + 1) % nt]))
    for j in range(nr - 1):
        for k in range(nt):
            k2 = (k + 1) % nt
            bm.faces.new((rows[j][k], rows[j][k2], rows[j + 1][k2], rows[j + 1][k]))
    for fc in bm.faces:
        fc.normal_update()
        if fc.normal.z < 0:
            fc.normal_flip()
        for lp in fc.loops:
            lp[uvl].uv = (umap[lp.vert], 0.5)
            lp[uvx].uv = (lp.vert.co.x / Rw, lp.vert.co.y / Rw)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def tube(bm, pts, rad, sides=20, cap=True):
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        a = Vector(pts[min(i + 1, n - 1)]) - Vector(pts[max(i - 1, 0)])
        a.normalize()
        up = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
        uu = a.cross(up); uu.normalize()
        w = a.cross(uu)
        rr = rad(i / (n - 1)) if callable(rad) else rad
        ring = [bm.verts.new(Vector(p) + rr * (math.cos(2 * math.pi * s / sides) * uu
                                               + math.sin(2 * math.pi * s / sides) * w))
                for s in range(sides)]
        rings.append(ring)
    for i in range(n - 1):
        for s in range(sides):
            s2 = (s + 1) % sides
            bm.faces.new((rings[i][s], rings[i][s2], rings[i + 1][s2], rings[i + 1][s]))
    if cap:
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])


def spout_mesh(name):
    """筧：右の外から来る竹。節で少し膨らむ"""
    bm = bmesh.new()
    x0, x1 = 3.4, SP_TIP[0] - 0.03
    pts = []
    N = 140
    for i in range(N + 1):
        s = i / N
        x = lerp(x0, x1, s)
        z = SP_Z + 0.10 * (1 - s) ** 1.5
        pts.append((x, SP_TIP[1] + 0.05 * (1 - s), z))
    nodes = (0.95, 1.95, 2.95)

    def rad(s):
        x = lerp(x0, x1, s)
        bump = sum(math.exp(-((x - nx) / 0.035) ** 2) for nx in nodes)
        return SP_R * (1.0 + 0.16 * bump)
    tube(bm, pts, rad, sides=24, cap=False)
    # 口は斜めに切り、竹の肉の内側に水（ライム）を見せる
    ring_tip = list(bm.verts)[-24:]
    ring_back = list(bm.verts)[:24]
    for v in ring_tip:
        v.co.x += 0.9 * (v.co.z - SP_Z)            # 下の唇が長い＝口が上を向き、中の水が見える
    ctr = sum((v.co for v in ring_tip), Vector()) / 24
    inner = [bm.verts.new(ctr.lerp(v.co, 0.74)) for v in ring_tip]
    for s_ in range(24):
        s2 = (s_ + 1) % 24
        f_ = bm.faces.new((ring_tip[s_], ring_tip[s2], inner[s2], inner[s_]))
    c_ = bm.verts.new(ctr + Vector((0.03, 0, 0)))
    for s_ in range(24):
        f_ = bm.faces.new((inner[s_], inner[(s_ + 1) % 24], c_))
        f_.material_index = 1
    bm.faces.new(ring_back[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def drop_mesh(name):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
    for v in bm.verts:            # 下へ垂れた雫
        if v.co.z > 0:
            v.co.x *= (1 - 0.45 * v.co.z); v.co.y *= (1 - 0.45 * v.co.z); v.co.z *= 1.5
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mats, smooth_ang=1.0):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    for m in mats:
        ob.data.materials.append(m)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=smooth_ang)
    except Exception:
        pass
    return ob


ob_stone = link(stone_mesh("m_ishi"), "ishi", [mat_body], smooth_ang=1.2)
ob_water = link(water_mesh("m_mizu"), "mizu", [mat_glow], smooth_ang=1.2)
ob_spout = link(spout_mesh("m_kakei"), "kakei", [mat_take, mat_drop], smooth_ang=1.0)
ob_drop = link(drop_mesh("m_shizuku"), "shizuku", [mat_drop], smooth_ang=1.2)
parts = [ob_stone, ob_water, ob_spout]

# 石の肌は実ジオメトリ（MATERIALS.md）。発光体には掛けない
tex = bpy.data.textures.new("relief_ishi", 'CLOUDS')
tex.noise_scale = ISHI["dsize"]
sub = ob_stone.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = 2
dmod = ob_stone.modifiers.new("disp", 'DISPLACE')
dmod.texture = tex; dmod.strength = ISHI["disp"]; dmod.mid_level = 0.5
dmod.texture_coords = 'LOCAL'

# --- キーフレーム（毎フレーム）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts + [ob_drop]:
    ob.rotation_mode = 'QUATERNION'
prev = None
TIP_LOCAL = Vector((SP_TIP[0] - 0.02, SP_TIP[1], SP_Z - SP_R * 0.9))
for f, idx in enumerate(FR_):
    t = idx / N_FRAMES
    M3 = rot_of(t)
    Mx = Matrix(((M3[0][0], M3[0][1], M3[0][2]), (M3[1][0], M3[1][1], M3[1][2]), (M3[2][0], M3[2][1], M3[2][2])))
    q = Mx.to_quaternion()
    if prev is not None and q.dot(prev) < 0.0:
        q.negate()
    prev = q.copy()
    C = Vector(center_of(t))
    for ob in parts:
        ob.location = C
        ob.rotation_quaternion = q
        ob.keyframe_insert("location", frame=f + 1)
        ob.keyframe_insert("rotation_quaternion", frame=f + 1)
    # 滴：口で育ち（a 0.45→0.90）、落ちる（0.90→1.0）。a=0 で水面に着く
    a, rho, A = wave_of(t)
    if a < 0.90:
        grow = smooth(0.40, 0.90, a)
        local = TIP_LOCAL + Vector((0, 0, -0.030 * grow))
        sc = 0.034 * grow
    else:
        fall = (a - 0.90) / 0.10
        local = TIP_LOCAL.lerp(Vector((SP_TIP[0], SP_TIP[1], Z_W + 0.01)), fall * fall)
        sc = 0.034 * (1.0 - 0.3 * fall)
    ob_drop.location = C + Mx @ local
    ob_drop.rotation_quaternion = (1, 0, 0, 0)
    ob_drop.scale = (max(sc, 1e-4),) * 3
    for p_ in ("location", "rotation_quaternion", "scale"):
        ob_drop.keyframe_insert(p_, frame=f + 1)
    WAVE_NODES["rho"].outputs[0].default_value = rho
    WAVE_NODES["amp"].outputs[0].default_value = A
    WAVE_NODES["rho"].outputs[0].keyframe_insert("default_value", frame=f + 1)
    WAVE_NODES["amp"].outputs[0].keyframe_insert("default_value", frame=f + 1)
parts = parts + [ob_drop]

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
        caption("MIDDLE STUDY 083 — TSUKUBAI", 0.045, (AIM_X, -1.7, 0.74), "study")]


def area(name, loc, size, energy, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    Lt = bpy.context.active_object; Lt.name = name
    Lt.data.size = size; Lt.data.energy = energy; Lt.data.color = color
    Lt.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return Lt


focus = (CX, 0.0, CZ)
area("key", (-4.0, -3.0, 5.0), 5.0, 1400, (1.0, 0.97, 0.92), focus)
area("rim", (3.5, 4.0, 3.2), 3.0, 420, (0.88, 0.94, 1.0), focus)
area("fill", (0.0, -6.0, 2.0), 6.0, 220, (1.0, 1.0, 1.0), focus)
back = area("back", (0.0, 5.2, 2.2), 4.0, 1800, (1.0, 0.99, 0.96), focus)   # 4灯目（#55/#56）
back.visible_camera = False        # 🔴 #67①

# 🔴 #58③：随伴のライム光源は発光体の外。石の奥・床寄り
for sx, sy, sz, wt in ((-0.30, 8.0, 0.30, LIME_W), (0.30, 11.0, 0.30, LIME_W),
                       (0.80, 14.5, 0.30, LIME_W)):
    bpy.ops.object.light_add(type='POINT', location=(CX + sx, sy, sz))
    lp = bpy.context.active_object
    lp.name = "lime_%+0.2f_%.0f" % (sx, sy)
    lp.data.energy = wt
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
cam.data.dof.focus_distance = 8.3
cam.data.dof.aperture_fstop = 6.0
scene.camera = cam
for tx in caps:
    tx.rotation_euler = cam.rotation_euler

# 🔴 逆光のライトリンクは全ジオメトリ生成後（#56②）。床を受光から外す
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
tH = (STILL_FRAME - 1) / N_FRAMES
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME, " α(hero) %.1f°" % math.degrees(alpha_of(tH)))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 91):
        scene.frame_set(fr); dg.update()
        allx, ally = [], []
        for ob in parts:
            ev = ob.evaluated_get(dg)
            for v in list(ev.data.vertices)[::3]:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                allx.append(c.x); ally.append(c.y)
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        sl = max(0.0, min(x1, 1) - max(x0, 0))
        sh = max(0.0, min(y1, 1) - max(y0, 0))
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  中心x %.1f%%"
              % (fr, x0, x1, y0, y1, sl * 100, sh * 100, edge, (x0 + x1) * 50))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))
    for fr in (1, 19, 61, 91):
        tt = (fr - 1) / N_FRAMES
        aa, rr, AA = wave_of(tt)
        M3 = rot_of(tt)
        nz = Vector((M3[0][2], M3[1][2], M3[2][2]))
        vv = (Vector(CAM_LOC) - Vector(center_of(tt))).normalized()
        print(">> [f%d] a %.2f ρ %.2f A %.2f  水面の向き cos %.2f" % (fr, aa, rr, AA, nz.dot(vv)))
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
    for fr in (1, 31, 43, 49):
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_083.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("ishi_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = ISHI["rough"]
    m_em = bpy.data.materials.new("mizu_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * B0 * 0.5
    ob_stone.data.materials[0] = m_bk
    ob_spout.data.materials[0] = m_bk
    ob_spout.data.materials[1] = m_em
    ob_water.data.materials[0] = m_em
    ob_drop.data.materials[0] = m_em
    for mo in list(ob_stone.modifiers):
        ob_stone.modifiers.remove(mo)          # 容量（#60：8MB以下）
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
