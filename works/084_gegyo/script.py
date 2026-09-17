# =============================================================
# MIDDLE STUDY 084 — GEGYO（懸魚 / hung at the highest middle）
#
#   光の型＝窓（#53）  構図の型＝天地（#57・高く吊る）  ドメイン＝社寺建築・破風飾り
#
# 懸魚（げぎょ）は、破風の二枚の板がいちばん上で出会うところ——屋根の真ん中の、
# いちばん高いところに吊る板だ。棟木の木口を雨から隠すための板で、名は「魚を懸ける」。
# 水に棲むものを屋根に吊って、火を除けた。
# 板には猪目（いのめ）が抜いてある。これも火除けの印。**意匠は彫ったものではなく、抜いたもの。**
# 光っているのは、板の無いところだけだ。
#
# 造形：蕪懸魚（かぶらげぎょ）の外形＋猪目3つ＝2D カーブの内側の閉路（boolean 不使用）。
#       押し出し＋ベベルで肉を持たせ、メッシュに変換。破風板は反り（照り）のある2枚の帯。
#       真ん中に六葉（ろくよう）の金物。
#
# 光：窓。板の裏に発光板（E=1-(r/RG)^GEXP・芯は六葉の裏）。猪目からしか見えない（#87①）。
#
# 動き：縦軸まわりのヨー（sin＝厳密に閉じる）＋わずかな前後の傾き（cos）。
#       斜めから見るほど孔の壁が入口を食う＝光が細る（076 の機構）。
# =============================================================
import math, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
LIME_HEX, BLACK_HEX = "A5E02E", "0A0A0A"

# --- 舞台（シリーズ不変）-----------------------------------------
FPS, N_FRAMES = 24, 120
CAM_LOC = (0.55, -8.3, 1.95)
AIM_X, LOOK_Z = 0.55, 1.95
FRAME_W, FRAME_H = 2.81, 3.52
LIME_W = float(os.environ.get("LIME_W", "105"))

# --- 懸魚（板）：原点 O＝板の胴の中心。X 右・Z 上。厚みは Y ---------
# 半幅の制御点 (z, w)：首→肩→胴→すぼまり→尖り
WIDTH_CP = [(0.56, 0.100), (0.40, 0.135), (0.24, 0.300), (0.06, 0.470),
            (-0.14, 0.530), (-0.36, 0.470), (-0.56, 0.300), (-0.70, 0.100), (-0.76, 0.0)]
EXTRUDE = 0.034
BEVEL   = 0.012
# 猪目 (cx, cz, size, 先の向き[度・下=0・時計回り正])
# 🔴 1周目：左右＋下は「目と口」＝顔（#91 の緑の眼）。2周目：120°おきに3つは「放射能標識」。
#    3周目：縦に2つ、先どうしを向かい合わせ、あいだに六葉＝光は上下から真ん中へ向かう
#    5周目：halo 2524（#88：halo は孔の大きさで買う）。孔を大きくし、先どうしを触れる寸前まで寄せる
#    ＝向い猪目。六葉は首へ（実物でも懸魚を留める釘を隠す金物）
M_Z, M_GAP, S_INOME = -0.15, 0.030, 0.300
BEND = 0.55
INOME = [(0.0, M_Z + M_GAP + 0.78 * S_INOME, S_INOME, 0.0),
         (0.0, M_Z - M_GAP - 0.78 * S_INOME, S_INOME, 180.0)]
ROKUYO = (0.0, 0.40, 0.058)

# --- 破風板 --------------------------------------------------------
AZ     = 0.63                      # 拝み（頂点）の上端
SPAN   = 0.92                      # 片側の水平の長さ
SLOPE  = 27.0                      # 勾配（度）
TERI   = 0.07                      # 照り（端が持ち上がる量）
BH     = 0.140                     # 板の成（せい）
BY0, BY1 = 0.050, 0.115            # 板の奥行き（懸魚の裏から）

# --- 光（裏の発光板）--------------------------------------------
RG      = 0.84
DBACK   = 0.090
GEXP    = 1.25
ES_CORE = 2.8
WHITE_FROM, WHITE_TO = 0.42, 0.85
K_MIX   = 16.0
E_FLOOR = 0.12

# --- 動き --------------------------------------------------------
YAW0, BETA = 13.0, 23.0             # ヨー＝YAW0+BETA·sin（-10°〜+36°）。🔴 8周目：-36°側は漆の板が白い地を映して灰色の板になった
TILT0, DTILT = 4.0, 5.0            # 前傾（度）
BOB    = 0.025
CX, CZ = 0.55, 2.86                # 天地：高く吊る
STILL_FRAME = 64


# =============================================================
# 純 math
# =============================================================
def smooth(e0, e1, x):
    if e1 == e0:
        return 0.0
    v = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return v * v * (3.0 - 2.0 * v)


def catmull(P, n_per=14):
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for s in range(n_per):
            u = s / n_per; u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u
                                    + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u3) for c in range(2)))
    out.append(P[-1])
    return out


HIRE_A, HIRE_N, HIRE_Z0, HIRE_Z1 = 0.060, 3, -0.40, 0.34    # 鰭：側面の波（雲）


def outline():
    side = catmull(WIDTH_CP, n_per=24)          # 上→下（右側）
    side2 = []
    for z, w in side:
        if HIRE_Z0 < z < HIRE_Z1:
            u = (z - HIRE_Z0) / (HIRE_Z1 - HIRE_Z0)
            w += HIRE_A * (0.5 - 0.5 * math.cos(2 * math.pi * HIRE_N * u)) ** 0.7 * math.sin(math.pi * u) ** 0.5   # 谷を尖らせない（7周目：谷に白い横線＝割れ目に見えた）
        side2.append((z, w))
    side = side2
    right = [(w, z) for z, w in side]
    left = [(-w, z) for z, w in reversed(side)][1:-1]
    return right + left                          # (x, z) 閉路


def heart(cx, cz, size, ang_deg, n=84):
    """猪目：先の尖ったハートを縦に伸ばす。先は下（ang=0）"""
    pts = []
    a = math.radians(ang_deg)
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        x /= 32.0
        y = (y + 2.5) / 29.0 * 1.28
        # 猪目＝ハートではない：先を長く、肩を狭く、切れ込みを浅く（4周目・絵文字の ♥ に読めた）
        if y < 0:
            x *= 1.0 / (1.0 - 0.35 * y)
            y *= 1.22
            x += BEND * y * y                        # 先を曲げる：上下で点対称＝二つ巴（6周目・♥♥に読めた）
        else:
            x *= 0.86
            y = y * 0.80 + 0.05 * (1.0 - min(1.0, abs(x) / 0.14)) * (1 if y > 0.3 else 0)
        # 先の向き：下(0°)から ang だけ回す（先が外へ振れる）
        xr = x * math.cos(a) - y * math.sin(a)
        yr = x * math.sin(a) + y * math.cos(a)
        pts.append((cx + size * xr, cz + size * yr))
    for _ in range(5):                              # 切れ込みの尖りを丸める（ベベルが割れる）
        pts = [((pts[i - 1][0] + 2 * pts[i][0] + pts[(i + 1) % n][0]) / 4,
                (pts[i - 1][1] + 2 * pts[i][1] + pts[(i + 1) % n][1]) / 4) for i in range(n)]
    return pts


def ray_poly(poly, th):
    dx, dz = math.cos(th), math.sin(th)
    best = 1e9
    n = len(poly)
    for i in range(n):
        ax, az = poly[i]; bx, bz = poly[(i + 1) % n]
        ex, ez = bx - ax, bz - az
        den = dx * ez - dz * ex
        if abs(den) < 1e-12:
            continue
        s = (ax * ez - az * ex) / den
        u = (ax * dz - az * dx) / den
        if s > 0 and -1e-9 <= u <= 1 + 1e-9:
            best = min(best, s)
    return best


def yaw_of(t):
    return math.radians(YAW0 + BETA * math.sin(2 * math.pi * t))


def tilt_of(t):
    return math.radians(TILT0 + DTILT * math.cos(2 * math.pi * t))


def rot_of(t):
    """世界 = Rz(yaw)·Rx(tilt)"""
    a, g = tilt_of(t), yaw_of(t)
    Rz = ((math.cos(g), -math.sin(g), 0), (math.sin(g), math.cos(g), 0), (0, 0, 1))
    Rx = ((1, 0, 0), (0, math.cos(a), -math.sin(a)), (0, math.sin(a), math.cos(a)))
    return tuple(tuple(sum(Rz[i][k] * Rx[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def center_of(t):
    return (CX, 0.0, CZ + BOB * math.sin(2 * math.pi * t))


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

# ---------- マテリアル（MATERIALS.md・#52・#87③）----------
URUSHI = dict(rough=0.28, spec=0.28, coat=0.02, coat_rough=0.25)     # 懸魚＝塗りの板
HAFU   = dict(rough=0.46, spec=0.26)                                  # 破風板＝古い塗りの木
TETSU  = dict(rough=0.50, spec=0.32, metal=0.35)                      # 六葉＝金物


def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"]


def apply_black(p, r):
    p.inputs["Base Color"].default_value = BLACK
    p.inputs["Roughness"].default_value = r["rough"]
    p.inputs["Specular IOR Level"].default_value = r["spec"]   # 🔴 0.10 を割らない（#45）
    p.inputs["Metallic"].default_value = r.get("metal", 0.0)
    if r.get("coat"):
        p.inputs["Coat Weight"].default_value = r["coat"]
        p.inputs["Coat Roughness"].default_value = r["coat_rough"]


mat_floor, fp_ = principled("floor")
fp_.inputs["Base Color"].default_value = (0.86, 0.86, 0.86, 1)
fp_.inputs["Roughness"].default_value = 0.42
mat_text, tp_ = principled("text")
tp_.inputs["Base Color"].default_value = (0.06, 0.06, 0.06, 1)
tp_.inputs["Roughness"].default_value = 0.6
mat_gegyo, gp_ = principled("gegyo"); apply_black(gp_, URUSHI)
mat_hafu, hp_ = principled("hafu"); apply_black(hp_, HAFU)
mat_kana, kp_ = principled("rokuyo"); apply_black(kp_, TETSU)


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
    apply_black(blk, URUSHI)
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


mat_glow = glow_material("hikari")

ROT_X90 = Matrix.Rotation(math.radians(90.0), 4, 'X')   # 曲線の XY → 世界の XZ（前面が -Y＝カメラ側）


def curve_mesh(name, loops, extrude, bevel, bevel_res=3):
    """2D カーブ（内側の閉路＝孔）→ 押し出し＋ベベル → メッシュ。boolean 不使用"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = bevel_res
    cu.resolution_u = 1
    for poly in loops:
        sp = cu.splines.new('POLY')
        sp.points.add(len(poly) - 1)
        for i, (x, z) in enumerate(poly):
            sp.points[i].co = (x, z, 0.0, 1.0)
        sp.use_cyclic_u = True
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    me.transform(ROT_X90)
    me.update()
    return me


def glow_mesh(name, poly, NT=160, NR=22):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("grad")
    emap = {}
    gx, gz = 0.0, M_Z                             # 芯＝二つの猪目の先が向かい合う点
    hub = bm.verts.new((gx, DBACK, gz)); emap[hub] = 1.0
    shifted = [(x - gx, z - gz) for x, z in poly]
    Rth = [RG * ray_poly(shifted, 2 * math.pi * k / NT) for k in range(NT)]
    rings = []
    for i in range(1, NR + 1):
        u = i / NR
        ring = []
        for k in range(NT):
            th = 2 * math.pi * k / NT
            v = bm.verts.new((gx + Rth[k] * u * math.cos(th), DBACK, gz + Rth[k] * u * math.sin(th)))
            emap[v] = max(0.0, 1.0 - u ** GEXP)
            ring.append(v)
        rings.append(ring)
    for k in range(NT):
        bm.faces.new((hub, rings[0][(k + 1) % NT], rings[0][k]))
    for i in range(NR - 1):
        for k in range(NT):
            k2 = (k + 1) % NT
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    bm.normal_update()
    for f in bm.faces:
        if f.normal.y > 0:
            f.normal_flip()
        for lp in f.loops:
            lp[uvl].uv = (emap[lp.vert], 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def hafu_mesh(name, N=48):
    """破風板：拝みから左右へ。照りで端が持ち上がる。断面は中心線に直交"""
    bm = bmesh.new()
    L = SPAN / math.cos(math.radians(SLOPE))
    for side in (1, -1):
        secs = []
        for i in range(N + 1):
            s = i / N
            x = side * SPAN * s
            z = AZ - SPAN * s * math.tan(math.radians(SLOPE)) + TERI * s * s
            dzds = -SPAN * math.tan(math.radians(SLOPE)) + 2 * TERI * s
            tx, tz = side * SPAN, dzds
            ln = math.hypot(tx, tz); tx, tz = tx / ln, tz / ln
            nx, nz = -tz * side, tx * side            # 下向きの法線
            if nz > 0:
                nx, nz = -nx, -nz
            bx, bz = x + BH * nx, z + BH * nz
            secs.append([bm.verts.new((x, BY0, z)), bm.verts.new((bx, BY0, bz)),
                         bm.verts.new((bx, BY1, bz)), bm.verts.new((x, BY1, z))])
        for i in range(N):
            a, b = secs[i], secs[i + 1]
            for j in range(4):
                j2 = (j + 1) % 4
                bm.faces.new((a[j], a[j2], b[j2], b[j]))
        bm.faces.new(secs[0])
        bm.faces.new(secs[-1][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def rokuyo_loops():
    cx, cz, r = ROKUYO
    n = 144
    petal = [(cx + r * (1 + 0.20 * math.cos(6 * 2 * math.pi * i / n)) * math.cos(2 * math.pi * i / n),
              cz + r * (1 + 0.20 * math.cos(6 * 2 * math.pi * i / n)) * math.sin(2 * math.pi * i / n))
             for i in range(n)]
    return [petal]


def link(me, name, mats, smooth_ang=0.6):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.clear()
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


OUT_POLY = outline()
HOLES = [heart(*h) for h in INOME]
ob_gegyo = link(curve_mesh("m_gegyo", [OUT_POLY] + HOLES, EXTRUDE, BEVEL), "gegyo", [mat_gegyo])
ob_glow = link(glow_mesh("m_hikari", OUT_POLY), "hikari", [mat_glow])
ob_hafu = link(hafu_mesh("m_hafu"), "hafu", [mat_hafu], smooth_ang=0.5)
bv = ob_hafu.modifiers.new("bevel", 'BEVEL'); bv.width = 0.008; bv.segments = 2
ob_roku = link(curve_mesh("m_rokuyo", rokuyo_loops(), 0.016, 0.008), "rokuyo", [mat_kana])
for v in ob_roku.data.vertices:
    v.co.y -= EXTRUDE + BEVEL + 0.012          # 板の前面に載せる
# 六葉の真ん中の座（丸い鋲）
bm_ = bmesh.new()
bmesh.ops.create_uvsphere(bm_, u_segments=24, v_segments=12, radius=0.030)
for v in bm_.verts:
    v.co.y *= 0.6
    v.co += Vector((ROKUYO[0], -(EXTRUDE + BEVEL + 0.045), ROKUYO[1]))
me_ = bpy.data.meshes.new("m_byo"); bm_.to_mesh(me_); bm_.free()
ob_byo = link(me_, "byo", [mat_kana], smooth_ang=1.2)
parts = [ob_gegyo, ob_glow, ob_hafu, ob_roku, ob_byo]

# --- キーフレーム（毎フレーム）----
FR_ = list(range(N_FRAMES)) + [N_FRAMES]
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for ob in parts:
    ob.rotation_mode = 'QUATERNION'
prev = None
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
        caption("MIDDLE STUDY 084 — GEGYO", 0.045, (AIM_X, -1.7, 0.74), "study")]


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
back.visible_camera = False        # 🔴 #67①：板と破風のあいだは抜けている

# 🔴 #58③：随伴のライム光源は発光体の外。板の裏・床寄り
for sx, sy, sz, wt in ((-0.36, 2.2, 0.26, LIME_W), (0.10, 4.6, 0.26, LIME_W),
                       (0.62, 7.8, 0.26, LIME_W)):
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
print(">> modes:", modes, " STILL_FRAME:", STILL_FRAME, " yaw(hero) %.1f°" % math.degrees(yaw_of(tH)))

if "probe" in modes:
    from bpy_extras.object_utils import world_to_camera_view
    scene.render.resolution_x, scene.render.resolution_y = 1600, 2000
    dg = bpy.context.evaluated_depsgraph_get()
    for fr in (STILL_FRAME, 1, 31, 61, 91):
        scene.frame_set(fr); dg.update()
        allx, ally = [], []
        for ob in parts:
            ev = ob.evaluated_get(dg)
            for v in list(ev.data.vertices)[::2]:
                c = world_to_camera_view(scene, cam, ev.matrix_world @ v.co)
                allx.append(c.x); ally.append(c.y)
        x0, x1, y0, y1 = min(allx), max(allx), min(ally), max(ally)
        sl = max(0.0, min(x1, 1) - max(x0, 0))
        sh = max(0.0, min(y1, 1) - max(y0, 0))
        edge = (x0 <= 0) + (x1 >= 1) + (y0 <= 0) + (y1 >= 1)
        print(">> [f%d] bbox x %.3f..%.3f y %.3f..%.3f  横 %.1f%% 縦 %.1f%%  接触 %d  中心y(上から) %.1f%%"
              % (fr, x0, x1, y0, y1, sl * 100, sh * 100, edge, (1 - (y0 + y1) / 2) * 100))
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "_084.blend"))

# 🔴 glb は必ず最後（#25c：Emission ノード網は GLB で NaN を吐く＝定数に潰す）
if "glb" in modes:
    m_bk = bpy.data.materials.new("gegyo_glb"); m_bk.use_nodes = True
    pi = m_bk.node_tree.nodes["Principled BSDF"]
    pi.inputs["Base Color"].default_value = BLACK
    pi.inputs["Roughness"].default_value = URUSHI["rough"]
    m_em = bpy.data.materials.new("hikari_glb"); m_em.use_nodes = True
    pe = m_em.node_tree.nodes["Principled BSDF"]
    pe.inputs["Base Color"].default_value = BLACK
    pe.inputs["Emission Color"].default_value = LIME
    pe.inputs["Emission Strength"].default_value = ES_CORE * 0.34
    for ob in (ob_gegyo, ob_hafu, ob_roku, ob_byo):
        ob.data.materials[0] = m_bk
    ob_glow.data.materials[0] = m_em
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
