# 地图投影选择规则参考

> 依据 Bojan Šavrič / Bernhard Jenny 的 Projection Wizard (projectionwizard.org) v2.1 的选择逻辑（基于 John P. Snyder 选择指南），本地化整理。原实现（CC BY）见 ProjectionWizard/projectionwizard.github.io。

## 1. 依据范围计算关键量

设范围包围框为 `[lonmin, latmin] × [lonmax, latmax]`（WGS84 经纬度）。所有经度先归一化到 (-180, 180]；若范围跨反经线（Antimeridian），按跨线方式计算经度跨度与中心。

```
中心纬度:  center.lat = (latmax + latmin) / 2
中心经度:  center.lng = 范围中心（跨反经线时按环绕取中心，再归一化）
经度跨度:  dlon = lonmax - lonmin（跨反经线时为 360 - 东西向表观跨度）
比例尺量:  scale = 720 / dlon / (sin(latmax·π/180) - sin(latmin·π/180))
南北比:   ratio = (latmax - latmin) / dlon
             若 latmin > 0，再除以 cos(latmin·π/180)
             若 latmax < 0，再除以 cos(latmax·π/180)
```

尺度分类：
- `scale < 1.5` → **世界（小比例尺）**：等积可选、等角禁用、折衷可选。
- `1.5 ≤ scale < 6` → **半球（中比例尺）**：折衷禁用；若 `|latmax| < 23.43665 且 |latmin| < 23.43665`（范围在热带内）等角可选，否则等角禁用。
- `scale ≥ 6` → **区域及更小（大比例尺）**：等角可选、折衷禁用。

## 2. 世界（scale < 1.5）

| 变形性质 | 首选投影 | PROJ id |
|---|---|---|
| 等积（极点为点） | Mollweide、Hammer | `moll`、`hammer` |
| 等积（极点为线） | Equal Earth、Eckert IV、Wagner IV、Wagner VII | `eqearth`、`eck4`、`wag4`、`wag7` |
| 等距 | 极/斜方位等距、两点等距 | `aeqd`、`tpeqd` |
| 折衷 | Robinson、Natural Earth、Winkel Tripel | `robin`、`natearth`、`wintri` |
| 折衷矩形（不推荐用于多数世界地图） | Patterson、Plate Carrée、Miller I | `patterson`、`latlong`、`mill` |

中央经度取整（worldValues）：scale < 1.15 → 1°；scale < 1.32 → 0.5°；否则 0.1°。

等距世界投影细分：
- 极方位等距 `aeqd`：lat_0 = ±90（可选南北极），lon_0 为中央经线。
- 斜方位等距 `aeqd`：lat_0、lon_0 为地图中心。
- 两点等距 `tpeqd`：+lat_1 +lon_1 +lat_2 +lon_2 两点坐标。

## 3. 半球（1.5 ≤ scale < 6）

**范围在热带内**（|latmax| < 23.43665 且 |latmin| < 23.43665）：
- 标准纬线 latStd：interval = (latmax - latmin)/4；latS1 = center.lat + interval，latS2 = center.lat - interval；若 latS1 与 latS2 同号 → latStd = max(|latmax|, |latmin|)/2；否则 latStd = 0（保留 2 位小数）
- 等积 → 圆柱等积 `cea`（lat_ts = latStd）
- 等角 → Mercator `merc`（lat_ts = latStd）
- 等距 → 等距圆柱 `eqc`（lat_ts = latStd）
- 中央经线保留 2 位小数

**范围在热带外**：
- 等积 → Lambert 方位等积 `laea`
- 等距 → 方位等距 `aeqd`
- 中心纬度：center.lat > 85 → 90；< -85 → -90；否则保留 2 位小数
- 中央经线保留 2 位小数

## 4. 区域及更小区域（scale ≥ 6）

### 4.1 等距特例（按顺序判定）
1. center.lat > 70 → 极方位等距 `aeqd`（lat_0 = 90）
2. center.lat < -70 → 极方位等距 `aeqd`（lat_0 = -90）
3. ratio > 1.25（南北延伸）→ Cassini `cass`（lon_0 = 中央经线）
4. |center.lat| < 15（近赤道）→ 等距圆柱 `eqc`：范围跨赤道（latmax·latmin ≤ 0）时 latS = max(|latmax|,|latmin|)/2，否则 latS = center.lat
5. 其余 → **双选**：等距圆锥 `eqdc`（lat_0 = center.lat；lat_1 = latmin + Δ/6，lat_2 = latmax − Δ/6，Δ = latmax − latmin）或斜方位等距 `aeqd`（中心 = 范围中心）
6. scale > 260 时附加提示：可检索 EPSG 官方国家投影

### 4.2 等角特例（property == Conformal，按顺序判定）
1. latmin ≥ 84 → 极球面 `stere`（lat_0 = 90，k_0 = 0.994）
2. latmax ≤ −80 → 极球面 `stere`（lat_0 = -90，k_0 = 0.994）
3. dlon ≤ 3 → Transverse Mercator `tmerc`（k_0 = 0.9999，x_0 = 500000）
4. dlon ≤ 6 → Transverse Mercator `tmerc`（k_0 = 0.9996，x_0 = 500000）（仿 UTM）
5. 其余进入 ratio 分支

### 4.3 ratio 分支（等积 / 等角通用，Δ = latmax − latmin）
- **ratio > 1.25（南北延伸）**：
  - 等角 → Transverse Mercator `tmerc`（仅 lon_0）
  - 等积 → 横圆柱等积 `tcea`（仅 lon_0）
- **ratio < 0.8（东西延伸）**：
  - center.lat > 70 → 等角 `stere`（lat_0 = 90）/ 等积 `laea`（lat_0 = 90）
  - center.lat < -70 → 同上（lat_0 = -90）
  - |center.lat| < 15 → 等角 Mercator `merc` / 等积圆柱等积 `cea`（lat_ts：跨赤道时 max(|latmax|,|latmin|)/2，否则 center.lat）
  - 极与赤道之间：
    - 等角 → Lambert 等角圆锥 `lcc`（lat_0 = center.lat，lat_1 = latmin + Δ/6，lat_2 = latmax − Δ/6）；若锥顶点落在极点之外（checkConicOK 检测为不可用）→ 改极球面 `stere`（lat_0 = sign(center.lat)·90）
    - 等积 → Albers 等积圆锥 `aea`（参数同 LCC）；conicTest == 0（扇区不足 180° 环绕极点）→ 斜 Lambert 方位等积 `laea`（中心 = 范围中心）；conicTest < 0 → 极 LAEA（lat_0 = ±90）
- **0.8 ≤ ratio ≤ 1.25（方形）**：
  - center.lat > 75 → 等角极 `stere` / 等积极 `laea`（lat_0 = 90）
  - center.lat < -75 → 同上（lat_0 = -90）
  - |center.lat| < 15 且范围跨赤道（latmax·latmin ≤ 0）→ 等角赤道 `stere` / 等积赤道 `laea`（lat_0 = 0）
  - 其余 → 等角斜 `stere` / 等积斜 `laea`（中心 = 范围中心）

## 5. PROJ 字符串组装（WGS84 基准，米制）

```
aeqd / laea:   +proj=aeqd +lat_0=… +lon_0=… +datum=WGS84 +units=m +no_defs
stere:         +proj=stere +lat_0=… +lon_0=… [+k_0=…] +datum=WGS84 +units=m +no_defs
lcc / aea / eqdc: +proj=lcc +lat_1=… +lat_2=… +lat_0=… +lon_0=… +datum=WGS84 +units=m +no_defs
tmerc:         +proj=tmerc +lon_0=… [+k_0=… +x_0=500000] +datum=WGS84 +units=m +no_defs
merc / cea / eqc: +proj=merc +lon_0=… +lat_ts=… +datum=WGS84 +units=m +no_defs
tcea / cass:   +proj=tcea +lon_0=… +datum=WGS84 +units=m +no_defs
世界投影:       +proj=eqearth +lon_0=… +datum=WGS84 +units=m +no_defs
tpeqd:         +proj=tpeqd +lat_1=… +lon_1=… +lat_2=… +lon_2=… +datum=WGS84 +units=m +no_defs
```

数值精度：中央经线与标准纬线按上文规则取整（世界 0.1°–1°；半球/区域 2 位小数；圆锥标准纬线为原始浮点值，输出保留 7 位小数以内）。

## 6. WKT 模板（ESRI WKT1，与 Projection Wizard 输出一致）

```
PROJCS["ProjWiz_Custom_<NAME>",
  GEOGCS["GCS_WGS_1984",
    DATUM["D_WGS_1984",
      SPHEROID["WGS_1984",6378137.0,298.257223563]],
    PRIMEM["Greenwich",0.0],
    UNIT["Degree",0.0174532925199433]],
  PROJECTION["<PROJ_NAME>"],
  PARAMETER["False_Easting",0.0],
  PARAMETER["False_Northing",0.0],
  <其余参数按各投影模板>,
  UNIT["Meter",1.0]]
```

各投影 WKT 映射（PROJECTION 名称与参数顺序）：

| PROJ id | WKT PROJECTION 名 | 参数（顺序） |
|---|---|---|
| aeqd | Azimuthal_Equidistant | Central_Meridian, Latitude_Of_Origin |
| laea | Lambert_Azimuthal_Equal_Area | Central_Meridian, Latitude_Of_Origin |
| stere | Stereographic | Central_Meridian, Scale_Factor, Latitude_Of_Origin |
| aea | Albers | Central_Meridian, Standard_Parallel_1, Standard_Parallel_2, Latitude_Of_Origin |
| eqdc | Equidistant_Conic | Central_Meridian, Standard_Parallel_1, Standard_Parallel_2, Latitude_Of_Origin |
| lcc | Lambert_Conformal_Conic | Central_Meridian, Standard_Parallel_1, Standard_Parallel_2, Latitude_Of_Origin |
| cea | Cylindrical_Equal_Area | Central_Meridian, Standard_Parallel_1 |
| merc | Mercator | Central_Meridian, Standard_Parallel_1 |
| eqc | Equidistant_Cylindrical | Central_Meridian, Standard_Parallel_1 |
| tcea | Transverse_Cylindrical_Equal_Area | Central_Meridian, Scale_Factor, Latitude_Of_Origin |
| tmerc | Transverse_Mercator | Central_Meridian, Scale_Factor, Latitude_Of_Origin |
| cass | Cassini | Central_Meridian, Scale_Factor, Latitude_Of_Origin |
| moll | Mollweide | Central_Meridian |
| hammer | Hammer_Aitoff | Central_Meridian |
| eck4 | Eckert_IV | Central_Meridian |
| eqearth | Equal_Earth | Central_Meridian |
| wag4 | Wagner_IV | Central_Meridian |
| wag7 | Wagner_VII | Central_Meridian |
| robin | Robinson | Central_Meridian |
| natearth | Natural_Earth | Central_Meridian |
| wintri | Winkel_Tripel | Central_Meridian, Standard_Parallel_1=50.467 |
| patterson | Patterson | Central_Meridian |
| latlong | Plate_Carree | Central_Meridian |
| mill | Miller_Cylindrical | Central_Meridian |
| tpeqd | Two_Point_Equidistant | Latitude_Of_1st_Point, Latitude_Of_2nd_Point, Longitude_Of_1st_Point, Longitude_Of_2nd_Point |

数值格式：False_Northing 恒为 0.0；带 x_0 时 False_Easting = x_0；Scale_Factor 默认 1.0（有 k_0 时用 k_0）；经纬度值保留 7 位小数。

## 7. 合规底图（高德为主，天地图为备选）

### 高德（当前实现，免 key）

```
矢量:  https://webrd0{1-4}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}
卫星:  https://webst0{1-4}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}
路网注记（透明，叠卫星）: https://webst0{1-4}.is.autonavi.com/appmaptile?style=8&x={x}&y={y}&z={z}
```

- 全部 **免 key**，EPSG:3857 XYZ，256px 瓦片，实测 `Access-Control-Allow-Origin: *`
- 坐标系是 **GCJ-02**（不是 WGS84）：瓦片里的经纬度已被偏移，与真实 WGS84 差约 100–600m。本页所有数据与输出保持 WGS84，只在绘制/取点边界做转换（见 SKILL.md「GCJ-02 纠偏」）
- 页面用 **Leaflet**：`L.tileLayer(url, { subdomains:["1","2","3","4"], maxZoom:18 })`，瓦片以 `<img>` 加载，天然走 `img-src`，不受宿主 `connect-src` 限制（详见下节）

### 天地图（备选，需 key）

```
https://t{s}.tianditu.gov.cn/DataServer?T={layer}&x={x}&y={y}&l={z}&tk={KEY}
```
- `{s}` 子域 1–7；影像 `img_w` + 中文注记 `cia_w`；矢量 `vec_w` + 注记 `cva_w`；晕渲 `ter_w` + `cta_w`
- 必须携带 `tk=`（tianditu.gov.cn 申请，创建"浏览器端"应用）；仅 https；测试 key 约 7 天有效
- 服务端已配 `Access-Control-Allow-Origin: *`，合法 key 不会被 CORS 拦
- **在预览面板里一定不可用**：瓦片走 fetch，被 `connect-src` 拦死，只能本地打开

### 合规要点

1. 只接白名单图源：高德 / 腾讯 / 百度 / 天地图（均有审图号或合规授权）
2. 底图不可用时退化到"参考模式"：经纬网格 + 赤道/回归线/极圈 + Natural Earth land-110m 陆地轮廓（无国界、无注记）
3. 天地图/高德中国范围内内容完整（含台湾地区、南海诸岛等），不得裁剪或替换为 OSM 等境外底图
4. 高德免 key 瓦片适合内部与演示；对外正式交付建议走 JS API 授权或天地图正式 key

## 附：proj4js 调用注意事项

- proj4 对原始 `+proj=...` 字符串**不设 `x_0`/`y_0` 默认值**：`aea`、`laea`、`moll`、`lcc` 等若不含 `+x_0=0 +y_0=0`，正算结果为 NaN（`eqc`、`stere`、`tmerc`、`merc` 自行兜底不受影响）。页面输出的 PROJ 字符串不必带这两项（PROJ/GDAL 默认 0），但内部调用必须在副本上补齐
- `proj4(str)` 返回 `{ forward(coords), inverse(coords), oProj }` 对象（不可直接调用），`forward([lon, lat])` 输入经纬度单位为**度**
- `checkConicOK` 的等价实现：用 proj4 投影 4 个测试点 `[lon0,-90] [lon0,90] [rel(W),S] [rel(E),N]`，取 y 值判断极点是否落入数据 y 区间（发散点视为 null）；proj4 未就绪时退化为锥常数扇角的几何近似，两者结论一致

### proj4js 未内置的投影（预览兜底）

proj4 2.11 只内置 ~30 个投影，以下引擎会用到的投影**不在其中**：`eck4`、`hammer`、`wag4`、`wag7`、`natearth`、`wintri`、`patterson`、`tcea`、`tpeqd`。

页面用 `MANUAL_FWD`（球面公式）为其中四个提供预览，均以 PROJ（pyproj `+proj=...`）为基准在 217 个采样点（lat −75…75 步长 5、lon 0…180）上校验，最大偏差 ≤1e-15·R：

| projId | 公式要点 |
|---|---|
| `wintri` | Aitoff 分量与 **plate carrée**（x=λ, y=φ）取平均；注意等距圆柱分量**不乘** cos φ₁（曾误用 φ·cos50.467 导致纬向压缩） |
| `natearth` | Šavrič–Patterson–Jenny 多项式：x=λ(0.8707−0.131979φ²−0.013791φ⁴+0.003971φ¹⁰−0.001529φ¹²)，y=φ(1.007226+0.015085φ²−0.044475φ⁶+0.028874φ⁸−0.005916φ¹⁰) |
| `hammer` | z=√(1+cosφ·cos(λ/2))，x=2√2·cosφ·sin(λ/2)/z，y=√2·sinφ/z |
| `eck4` | 牛顿迭代解 θ+sinθcosθ+2sinθ=(2+π/2)sinφ，x=0.4222382·λ(1+cosθ)，y=1.3265004·sinθ |

其余 `wag4`/`wag7`/`patterson`/`tcea`/`tpeqd` 显示"暂不支持网页预览"提示（PROJ/WKT 照常可用）。

### 预览绘制注意

- `extentRingPts` 的四条边必须按 南→东（自南向北）→北（自东向西）→西（**自北向南**）闭合；西边若反向会让范围框出现一条竖直线伪影（圆锥投影下因边界是直线不易察觉，曲线边界投影会暴露）
- 世界范围（W=−180, E=180）时，经度相对中央经线的差值必须保留 ±180 两侧（不能把 +180 折回 −180），否则东边界塌陷、图形只剩半边

## 附：运行环境与抗 CSP 约束（改动页面时必读）

宿主（WorkBuddy 预览面板、企业微信 webview 等）会给页面注入内容安全策略，典型响应头为：

```
default-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:;
script-src  'self' 'unsafe-inline' 'unsafe-eval' blob: data: https: ...;
connect-src 'self' http://127.0.0.1:* https://*.map.qq.com ...;   ← 不含 jsdelivr / autonavi / tianditu
img-src     'self' data: blob: https:;
```

推论与页面必须遵守的几条：

1. **外链 CSS 一定被拦**（`style-src` 未设置 → 回落 `default-src`，其中没有 `https:`）。leaflet.css 已整段内联在 `<style id="leafletCss">`，不要再改回 `<link>`。
2. **任何 `fetch`/`XHR` 到非白名单域名一定被拦**（`connect-src`）。Land 轮廓因此改为内联 base36（`window.LAND_ENC` + `decodeLand()`），不要改回 fetch world-atlas。
3. **栅格瓦片用 `<img>` 加载，天然绕开 `connect-src`**：Leaflet 的 `L.tileLayer` 就是拼 `<img src>`，而 `img-src` 允许 `https:`；换成 MapLibre 则必踩坑——它的 raster source 内部用 fetch（被拦），要另写 `addProtocol` + `createImageBitmap` 才行，而且 MapLibre 还需要 WebGL（部分宿主没有），所以本项目直接用 Leaflet
   - 若确实要迁回 MapLibre：`maplibregl.addProtocol("amap", ...)` 内用 `<img crossorigin="anonymous">` 取图（高德回 `ACAO: *`）→ `createImageBitmap(img)` → `resolve({data: bm})`（4.7 支持 ImageBitmap 作为协议返回值），`tiles` 里写 `amap://` 前缀；同时确认宿主有 WebGL
4. **Leaflet 的坑**：`L.geoJSON` 收到 MultiPolygon 会渲染成**一条 path**，多环共用 nonzero 填充规则会互相抵消（表现为海洋被填、陆地挖空）。陆地数据必须给成 FeatureCollection、每环一个 Polygon
5. **覆盖层 z-index**：Leaflet 的 pane 到 700、control 到 800，页面上自绘的提示条/状态条要用 `z-index:1000` 才不被地图盖住
6. **容器尺寸**：面板宽度变化时必须 `map.invalidateSize()`（已用 ResizeObserver 监听 `#mapWrap`），否则瓦片错位或空白
