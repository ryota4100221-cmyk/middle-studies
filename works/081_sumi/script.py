# =============================================================
# MIDDLE STUDY 081 — SUMI（炭 / 備長炭 the core is still burning）
#
#   光の型＝芯（#53）  構図の型＝対（#57・80作で初の組み合わせ）  ドメイン＝燃料・炭焼き／備長炭
#
# 備長炭は、外から見ると冷えている。
# 黒くて、硬くて、叩くと金属の音がする。火が残っているかどうかは、見ただけでは分からない。
#
# だから折る。折れ口のまんなかに、まだ熾（おき）が残っている。
# 炭は外から燃えて、外から消える。**最後まで生きているのは、いつも芯のほうだ。**
#
# 造形：一本の炭を真ん中で折り、二本を離して置いた。折れ口（破面）は極座標の格子で張り、
#       縁は胴の最初の輪と同じ頂点座標で閉じる（boolean 不使用）。
#       破面の起伏は二本で符号を反転して共有する＝**もとは一本だった**ことが式に入っている（059 WARIFU の作法）。
#       備長炭の割れ（放射状）は、破面では外周だけに、胴では縦の溝として**同じ角度**で走る。
#
# 光：破面の芯だけが光る。等値線は円（#82③）。芯は浅くくぼませて黒い縁を立てる（#88④）。
#     🔴 「対」では光を2つのあいだに置けない（#83⑤）。芯は各々の破面の内側に閉じるので対と組める。
#
# 動き：折れ口をこちらへ開く φ(t)（cos・位相をずらす）＋ 各々の軸まわりの自転（整数周期）＋ 上下の漂い（sin）。
#     光の量を変えているのは破面の向きだけ。**発光の値は1フレームも動かしていない**（#69②）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52      # y=0 の平面での実効フレーム
LIME_W = 140.0                     # 随伴のライム光源（#58）

# --- 炭の骨格 -----------------------------------------------------
R0     = 0.235                     # 断面の基準半径
L_L, L_R = 1.12, 0.86              # 左右の長さ（同じにすると鏡像＝図案になる／#75）
CRACKS = (0.35, 1.52, 2.46, 3.71, 4.60, 5.55)   # 割れの角度（rad）。破面と胴で共有
CRK_G  = (1.0, 0.45, 0.8, 0.3, 0.65, 0.5)   # 割れごとの深さ（揃えるとローレット＝つまみに読める）
CRK_W  = 0.035                     # 割れの角度幅
CRK_D  = 0.035                     # 胴の縦溝の深さ（R0比）
FR     = 0.018                     # 破面の起伏の振幅
DIP    = 0.022                     # 芯のくぼみ
SLANT  = 0.30                      # 破面の斜め（dz/dx）
STEP   = 0.030                     # 破面の段
VEIN_SCALE, VEIN_W, VEIN_K = 20.0, 0.050, 0.85   # 熾の割れ目（Voronoi の辺）。🔴 無いと「ケミカルライト」
NT, NRAD = 240, 18                 # 周／破面の半径方向の分割

# --- 光（芯）------------------------------------------------------
RG      = 0.92                     # 芯の半径（R0比）。E はここで 0。🔴 0.66＋K_MIX16 は縁の立った「光る緑のグミ」（1周目）
GEXP    = 2.2                      # E = (1-ρ²)^GEXP
ES_CORE = 4.0
WHITE_FROM, WHITE_TO = 0.80, 0.78
K_MIX   = 5.0                      # #76①。熾は縁が立たない＝黒へ溶ける勾配にする
E_FLOOR = 0.04                     # #85①

# --- 動き --------------------------------------------------------
PHI0, DPHI = 8.0, 44.0            # 折れ口の開き（度）
PH_R       = 0.85                  # 右の位相の遅れ（rad）
BETA_L, BETA_R = 216.0, 32.0       # 胴の向き（xz 平面・度）。一直線から少し折れている
GAP2   = 0.37                      # 折れ口の中心を折れ点からどれだけ離すか
BOB    = 0.035

CX, CZ = 0.55, 2.28
STILL_FRAME = 61


# =============================================================
# 純 math
# =============================================================
def smooth(e0, e1, x):
    if e1 == e0:
        return 0.0
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def crack(th):
    """0..1：割れの角度にいるほど 1"""
    m = 0.0
    for c, g in zip(CRACKS, CRK_G):
        d = math.atan2(math.sin(th - c), math.cos(th - c))
        m = max(m, g * math.exp(-(d / CRK_W) ** 2))
    return m


def sec_r(th, w=0.0):
    """断面の外周。真円は部品に見えるので低次の歪み＋割れの溝"""
    return R0 * (1.0 + 0.030 * math.sin(3.0 * th + 0.4) + 0.018 * math.sin(5.0 * th + 1.9)
                 + 0.010 * math.sin(2.0 * th + 3.0 * w + 0.6)
                 - CRK_D * crack(th))


def face_h(x, y, sign):
    """破面の高さ（局所 z）。二本で符号を反転して共有＝噛み合う相補形"""
    q, p = x / R0, y / R0
    h = FR * (0.60 * math.sin(2.6 * q + 0.8) + 0.45 * math.sin(2.1 * p + 1.7 * q + 2.1)
              + 0.20 * math.sin(5.3 * p - 4.1 * q) + 0.12 * math.sin(13.0 * q + 11.0 * p + 0.3) * smooth(0.9, 0.3, math.hypot(q, p)))
    # 🔴 折れ口は軸に直交しない＝斜めに裂けて段がつく。平らな直交面は「懐中電灯のレンズ枠」に読めた（3周目）
    h += SLANT * q * R0 + STEP * smooth(-0.12, 0.12, p - 0.35 * q)
    return sign * h


def face_dip(r, th):
    rho = r / (0.62 * R0)
    d = DIP * max(0.0, 1.0 - rho * rho) ** 1.5
    # 割れは外周だけ（芯を横切ると「花／ピザ」に読める＝#82③）
    d += 0.006 * crack(th) * smooth(0.62, 0.85, r / R0)
    return d


def E_of(r):
    rho = r / (RG * R0)
    return max(0.0, 1.0 - rho * rho) ** GEXP


def prof(w):
    """胴の太り：端だけ角を丸めて閉じる"""
    p = 1.0 + 0.015 * math.sin(math.pi * w)
    if w > 0.94:
        u = (w - 0.94) / 0.06
        p *= math.sqrt(max(0.0, 1.0 - u * u))
    return p


def phi_of(t, right):
    ph = PH_R if right else 0.0
    return math.radians(PHI0 + DPHI * (0.5 - 0.5 * math.cos(2.0 * math.pi * t + ph)))


def _norm(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def frame_of(t, right):
    """局所（破面 z=0・胴は +z）→ 世界。列 = (e_x, e_y, e_z)。
       e_z＝胴の向き d を y（奥）へ φ だけ倒したもの＝破面の法線 −e_z がカメラ側を向く。
       e_x = d×ŷ は折りの蝶番で φ に依らない。右手系は e_x×e_y=e_z で確認済み（#90⑦）"""
    b = math.radians(BETA_R if right else BETA_L)
    d = (math.cos(b), 0.0, math.sin(b))
    a = (-d[2], 0.0, d[0])
    ph = phi_of(t, right)
    ez = (math.cos(ph) * d[0], math.sin(ph), math.cos(ph) * d[2])
    ex = a
    ey = _cross(ez, ex)
    spin = 2.0 * math.pi * t * (1.0 if right else -1.0) + (1.3 if right else 0.2)
    c, s = math.cos(spin), math.sin(spin)
    ex2 = tuple(c * ex[i] + s * ey[i] for i in range(3))
    ey2 = tuple(-s * ex[i] + c * ey[i] for i in range(3))
    M = tuple(tuple((ex2[i], ey2[i], ez[i])[j] for j in range(3)) for i in range(3))
    return M, d


def center_of(t, right):
    b = math.radians(BETA_R if right else BETA_L)
    bob = BOB * math.sin(2.0 * math.pi * t + (1.1 if right else 0.0))
    return (CX + GAP2 * math.cos(b), 0.0, CZ + GAP2 * math.sin(b) + bob)


def visible_light(t):
    """#40⑥：芯の面積 × 破面の法線と視線の cos（正の側だけ）"""
    A = math.pi * (RG * R0) ** 2
    tot = 0.0
    for right in (False, True):
        M, _ = frame_of(t, right)
        n = (-M[0][2], -M[1][2], -M[2][2])
        C = center_of(t, right)
        v = _norm((CAM_LOC[0] - C[0], CAM_LOC[1] - C[1], CAM_LOC[2] - C[2]))
        tot += A * max(0.0, sum(n[i] * v[i] for i in range(3)))
    return tot


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
# 備長炭＝硬くて重く、叩くと金属の音がする。銀色の艶がある＝`tetsu`（鉄）
SUMI = dict(rough=0.62, spec=0.28, metal=0.0)


def apply_black(p):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = SUMI["rough"]
    p.inputs["Specular IOR Level"].default_value = SUMI["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = SUMI["metal"]


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_body, bp_ = principled("sumi")
apply_black(bp_)


def glow_material(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')

    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "grad"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    E0 = sep.outputs["X"]
    # 熾の割れ目：オブジェクト座標の Voronoi の辺で E を削る（等値線の円は保ったまま肌だけ割る／#82③）
    tco = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs["Scale"].default_value = VEIN_SCALE
    nt.links.new(tco.outputs["Object"], vor.inputs["Vector"])
    vmr = nt.nodes.new("ShaderNodeMapRange"); vmr.clamp = True
    vmr.inputs["From Min"].default_value = 0.0
    vmr.inputs["From Max"].default_value = VEIN_W
    vmr.inputs["To Min"].default_value = 1.0 - VEIN_K
    vmr.inputs["To Max"].default_value = 1.0
    nt.links.new(vor.outputs["Distance"], vmr.inputs["Value"])
    emul = nt.nodes.new("ShaderNodeMath"); emul.operation = 'MULTIPLY'
    nt.links.new(E0, emul.inputs[0]); nt.links.new(vmr.outputs["Result"], emul.inputs[1])
    E = emul.outputs[0]

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

    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'
    sub.inputs[1].default_value = E_FLOOR
    nt.links.new(E, sub.inputs[0])
    a0 = nt.nodes.new("ShaderNodeMath"); a0.operation = 'MULTIPLY'
    a0.inputs[1].default_value = K_MIX
    nt.links.new(sub.outputs[0], a0.inputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = 'MINIMUM'
    a1.inputs[1].default_value = 1.0
    nt.links.new(a0.outputs[0], a1.inputs[0])
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MAXIMUM'
    a2.inputs[1].default_value = 0.0
    nt.links.new(a1.outputs[0], a2.inputs[0])

    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mix.inputs[0])
    nt.links.new(blk.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


mat_glow = glow_material("oki")

THS = [2.0 * math.pi * k / NT for k in range(NT)]


def rim_z(th, sign):
    r = sec_r(th)
    x, y = r * math.cos(th), r * math.sin(th)
    return face_h(x, y, sign) + face_dip(r, th)


# ---------- 造形（bmesh・実寸。boolean 不使用）----------
def body_mesh(name, L, sign):
    """胴：破面の縁（z=rim_z）から端の丸みまで。縁は破面と同じ座標"""
    bm = bmesh.new()
    ws = [i / 30 * 0.90 for i in range(31)] + [0.90 + 0.10 * (i / 10) for i in range(1, 10)]
    rings = []
    for w in ws:
        blend = 1.0 - smooth(0.0, 0.10, w)
        ring = []
        for th in THS:
            r = sec_r(th, w) * prof(w)
            # 胴の肌：縦の細かな筋（窯の中で縮んだ痕）＋節
            r *= 1.0 + (0.0045 * math.sin(29.0 * th + 7.0 * w + 0.9 * math.sin(5.0 * th))
                         + 0.0030 * math.sin(47.0 * th - 3.0 * w + 2.0)) * smooth(0.0, 0.08, w)
            r *= 1.0 - 0.012 * math.exp(-((w - 0.47) / 0.04) ** 2)
            z = L * w + rim_z(th, sign) * blend
            ring.append(bm.verts.new((r * math.cos(th), r * math.sin(th), z)))
        rings.append(ring)
    for a in range(len(rings) - 1):
        for k in range(NT):
            k2 = (k + 1) % NT
            bm.faces.new((rings[a][k], rings[a + 1][k], rings[a + 1][k2], rings[a][k2]))
    apex = bm.verts.new((0.0, 0.0, L))
    for k in range(NT):
        bm.faces.new((rings[-1][k], apex, rings[-1][(k + 1) % NT]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def face_mesh(name, sign):
    """破面：中心の hub → 縁（sec_r）。E は絶対半径で焼く＝等値線が円（#82③）"""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    emap = {}
    rows = []
    for j in range(1, NRAD + 1):
        fj = j / NRAD
        ring = []
        for th in THS:
            r = sec_r(th) * fj
            x, y = r * math.cos(th), r * math.sin(th)
            z = face_h(x, y, sign) + face_dip(r, th)
            v = bm.verts.new((x, y, z)); emap[v] = E_of(r); ring.append(v)
        rows.append(ring)
    hub = bm.verts.new((0.0, 0.0, face_h(0.0, 0.0, sign) + face_dip(0.0, 0.0)))
    emap[hub] = 1.0
    for k in range(NT):
        bm.faces.new((hub, rows[0][(k + 1) % NT], rows[0][k]))
    for j in range(NRAD - 1):
        for k in range(NT):
            k2 = (k + 1) % NT
            bm.faces.new((rows[j][k], rows[j][k2], rows[j + 1][k2], rows[j + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    # 法線は −z（胴の外）を向くこと
    if sum(f.normal.z for f in bm.faces) > 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    for f in bm.faces:
        for lp in f.loops:
            lp[uvl].uv = (emap[lp.vert], 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def link(me, name, mat, smooth_ang=1.0):
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
    return ob


ob_bl = link(body_mesh("m_sumi_l", L_L, +1.0), "sumi_L", mat_body, smooth_ang=0.70)
ob_br = link(body_mesh("m_sumi_r", L_R, -1.0), "sumi_R", mat_body, smooth_ang=0.70)
ob_fl = link(face_mesh("m_oki_l", +1.0), "oki_L", mat_glow, smooth_ang=0.70)
ob_fr = link(face_mesh("m_oki_r", -1.0), "oki_R", mat_glow, smooth_ang=0.70)
parts = [ob_bl, ob_fl, ob_br, ob_fr]
bodies = [ob_bl, ob_br]

# --- キーフレーム（毎フレーム・四元数）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev = {}
for f, idx in enumerate(FR_):
    t = idx / N_FRAMES
    for right, obs in ((False, (ob_bl, ob_fl)), (True, (ob_br, ob_fr))):
        M3, _ = frame_of(t, right)
        M = Matrix(((M3[0][0], M3[0][1], M3[0][2], 0.0),
                    (M3[1][0], M3[1][1], M3[1][2], 0.0),
                    (M3[2][0], M3[2][1], M3[2][2], 0.0),
                    (0.0, 0.0, 0.0, 1.0)))
        q = M.to_quaternion()
        if right in prev and q.dot(prev[right]) < 0.0:
            q.negate()
        prev[right] = q.copy()
        for ob in obs:
            ob.location = center_of(t, right)
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
        caption("MIDDLE STUDY 081 — SUMI", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
back.visible_camera = False        # 🔴 #67①：二本のあいだが素通し

# 🔴 #58③：随伴のライム光源は発光体の外。あいだの奥・床寄り
for sx, sy, sz, wt in ((-0.30, 2.0, 0.30, LIME_W), (0.14, 4.2, 0.30, LIME_W),
                       (0.58, 7.2, 0.30, LIME_W)):
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
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME,
      " φ(hero) L %.1f° R %.1f°" % (math.degrees(phi_of(tH, False)), math.degrees(phi_of(tH, True))))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 91):
        scene.frame_set(fr); dg.update()
        allx, ally, per = [], [], {}
        for ob in parts:
            ev = ob.evaluated_get(dg)
            xs, ys = [], []
            for v in ev.data.vertices:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                xs.append(c.x); ys.append(c.y)
            per[ob.name] = (min(xs), max(xs), min(ys), max(ys))
            allx += xs; ally += ys
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        sl = max(0.0, min(x1, 1) - max(x0, 0))
        sh = max(0.0, min(y1, 1) - max(y0, 0))
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d"
              % (fr, x0, x1, y0, y1, sl * 100, sh * 100, edge))
        l = per["sumi_L"]; r = per["sumi_R"]
        print(">>       L x %.3f..%.3f y %.3f..%.3f / R x %.3f..%.3f y %.3f..%.3f"
              % (l + r))
        print(">>       あいだ（L右端→R左端）%.1f%%" % ((r[0] - l[1]) * 100))
    for tx in caps:
        c = world_to_camera_view(scene, cam, tx.location)
        print(">> キャプション %-8s 画面の上から %.1f%%" % (tx.name, (1 - c.y) * 100))
    vs = [visible_light(i / 48.0) for i in range(48)]
    print(">> 🔴 #40⑥ 見える芯 max/min = %.3f   max %.5f min %.5f hero %.5f"
          % (max(vs) / max(min(vs), 1e-9), max(vs), min(vs), visible_light(tH)))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_081.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("sumi_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = SUMI["rough"]
    pi.inputs["Metallic"].default_value = SUMI["metal"]
    m_em = bpy.data.materials.new("oki_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.34
    for o in bodies:
        o.data.materials[0] = m_bk
    for o in (ob_fl, ob_fr):
        o.data.materials[0] = m_em
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
