# 把 world-atlas land-110m.json 转成紧凑 base36 字符串，供单文件网页内联（window.LAND_ENC）
#
# 用法：
#   curl -sO https://gcore.jsdelivr.net/npm/world-atlas@2/land-110m.json
#   python build_land_data.py land-110m.json land.enc
#   然后把 land.enc 的内容替换 index.html 里 window.LAND_ENC = "..."; 的字符串
#
# 编码格式（前端 decodeLand() 必须与此保持一致）：
#   rings 之间用 "|" 分隔；每个 ring = 4 字符绝对经度 + 4 字符绝对纬度 + 若干 3+3 字符增量
#   单位 1/50 度（0.02°），经度偏移 +9000、纬度偏移 +4500、增量偏移 +23328（3 位 base36 满量程 46656）
#   126 环 / 5123 点 → 约 31KB，绘制误差 ≤0.01°（约 1km，世界级轮廓不可见）
import json, sys

A = "0123456789abcdefghijklmnopqrstuvwxyz"
UNIT = 50.0  # 1/0.02
OFF = 23328

def enc(v, n):
    v = int(v)
    assert 0 <= v < 36 ** n, (v, n)
    s = ""
    for _ in range(n):
        s = A[v % 36] + s
        v //= 36
    return s

t = json.load(open(sys.argv[1]))
sc, tr = t["transform"]["scale"], t["transform"]["translate"]
arcs = []
for a in t["arcs"]:
    x = y = 0
    pts = []
    for dx, dy in a:
        x += dx; y += dy
        pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
    arcs.append(pts)

def ring(idx):
    out = []
    for i in idx:
        seg = arcs[i] if i >= 0 else list(reversed(arcs[~i]))
        if out:
            seg = seg[1:]
        out += seg
    return out

rings = []
for g in t["objects"]["land"]["geometries"]:
    polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
    for poly in polys:
        for r in poly:
            rings.append(ring(r))

def q(v, axis):
    # 量化到 0.02 度，并保证落在合法区间
    k = round(v * UNIT)
    return k

out = []
for r in rings:
    if len(r) < 2:
        continue
    pts = []
    for lon, lat in r:
        p = (q(lon, 0), q(lat, 1))
        pts.append(p)
    if len(pts) < 2:
        continue
    s = enc(pts[0][0] + 9000, 4) + enc(pts[0][1] + 4500, 4)
    prev = pts[0]
    for p in pts[1:]:
        dlon, dlat = p[0] - prev[0], p[1] - prev[1]
        if abs(dlon) > OFF - 1 or abs(dlat) > OFF - 1:
            raise SystemExit("delta 超范围 %s" % ((dlon, dlat),))
        s += enc(dlon + OFF, 3) + enc(dlat + OFF, 3)
        prev = p
    out.append(s)

js = "|".join(out)
print("rings=%d chars=%d" % (len(out), len(js)))
open(sys.argv[2], "w").write(js)
