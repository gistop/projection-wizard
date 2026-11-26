---
name: map-projection-wizard
description: 地图投影选择向导。生成一个本地单文件网页，用户通过 2 步操作（① 框定制图范围：上传 GeoJSON/SHP 或在地图上拖拽矩形或手动输入经纬度；② 选择变形性质：等积/等角/等距/折衷）获得推荐投影的名称、参数、PROJ 字符串与 WKT。适用于制图/GIS 场景中的投影选型、投影参数确定、坐标系统设计等需求。网页内置高德矢量/卫星合规底图（免 key，含 GCJ-02 纠偏），底图不可用时可退化为经纬网参考模式。触发词：选投影、投影选择、投影推荐、projection wizard、确定投影参数、投影 PROJ、投影 WKT。
agent_created: true
---

# Map Projection Wizard（地图投影选择向导）

## Overview

生成一个离线可用的单文件网页（Leaflet + 高德合规底图，免 key），用户在页面上 2 步操作即可确定投影名称及参数，页面直接输出推荐的投影名称、参数、PROJ 字符串、WKT1（Esri）与 WKT2（ISO 19162），两套 WKT 都能一键复制或导出为 .prj，并给出投影预览。投影推荐逻辑忠实复刻 Projection Wizard (projectionwizard.org) v2.1 的选择规则（基于 Snyder 投影选择指南）。

## When to Use

- 用户需要为某个制图区域选择合适的地图投影（等积/等角/等距/折衷）
- 用户需要为投影确定标准纬线、中央经线等参数
- 用户需要得到可复制使用的 PROJ 字符串或 WKT
- 触发词：选投影、投影选择、投影推荐、projection wizard、确定投影参数

## 使用流程

1. 将 `assets/template/index.html` 复制到用户指定位置（未指定时复制到当前工作目录，命名为 `projection-wizard.html`）
2. 调用 `present_files` 打开该文件（本地 HTML 直接在预览面板中打开即可运行，全部计算在浏览器本地完成，无需服务器）
3. 告知用户使用方式：
   - **步骤 1（确定范围）**：上传 GeoJSON（.geojson/.json）、SHP（.zip 打包或 .shp+.prj+.dbf 松散文件）自动取包围框；或在地图上点击"⬚ 地图框选"后拖拽矩形
   - **经纬度输入是渐进披露的**：默认收起，只有需要精确数值时才点"▸ 手动输入经纬度"展开（东界数值小于西界即视为跨 180° 经线）。不要再把它默认摊开——面向 GIS 新手时它是纯噪声
   - **矩形画完还能改**：① 在框**内部按住拖动**＝整体平移（宽高不变，贴到 ±180/±90 会停住）；② 拖四角的小方块句柄＝调整大小（对角不动，最小边 0.02° 防塌陷）；③ 鼠标在框上会变成 move 光标。高德底图下句柄与框位置都走 GCJ-02 纠偏。跨 180° 的范围会被拆成两块显示，此时不提供句柄、也不支持整体拖动
   - **步骤 2（选择变形性质）**：一行 4 个紧凑选项（等积/等角/等距/折衷）+ 当前选项的一句话说明；不适用的选项自动变灰禁用（如世界图禁用等角、区域图禁用折衷）。细化说明收在标题后的圆形问号里（悬停/点击/键盘聚焦都能弹出）
   - 结果区以「**3 推荐投影**」开头（与左栏 1/2 同款 step-head，构成 1→2→3 的流程感），给出推荐投影卡片（含首选标记）、参数表与基于 proj4js 的投影预览。**三种文本格式（PROJ / WKT1（Esri） / WKT2（ISO 19162））是单选标签页**（`.fmt-tabs`/`.fmt-pane`，role=tablist），**默认显示 WKT2**（渐进式披露：主流格式直接给，另两种各留一个 tab 按需切换，**不要改回三块全部摊开**）；每张卡的 tab 状态相互独立（事件里用 `tab.closest(".pc-body")` 限定作用范围）。当前标签的问号与操作按钮在代码块上方一行：复制（三格式都有）、下载 .prj（两个 WKT 有，`downloadText()`，Blob + `<a download>`，纯前端不联网），文件名形如 `Albers_CGCS2000_wkt2.prj`
   - **为什么两套 WKT 都要**：**WKT2 已是新数据的主流**——2019 年 OGC 政策指令要求新标准一律用 WKT2（并已启动 WKT1 弃用流程）；ArcGIS Pro 3.6+、GDAL/PROJ 3+、QGIS 3.x、PostGIS 的默认输出都是 WKT2。但 WKT1（Esri）尚未消失：ArcMap、shapefile 的 .prj、GeoTools/FME 等存量生态仍靠它。**两套在 Pro 3.6 里都能读**。默认建议用户拿 WKT2；对方用 ArcMap / Pro≤3.5 / 老第三方工具时给 WKT1
   - **例外**：没有 EPSG 方法码的世界伪圆柱投影（Mollweide、Robinson、Eckert IV、Wagner IV/VII、Natural Earth、Winkel Tripel、Patterson、Hammer、Miller、两点等距、横圆柱等积）在 WKT2 里只有方法名字符串，ArcGIS 可能只当自定义投影。这类情况页面会自动在那张卡的 WKT2 问号里加提示，引导用户改用 ESRI WKT1（`PROJECTION["Robinson"]` 等是 Esri 自己的名字，识别最稳）**结果区没有范围摘要块**（制图范围/中心/类型三行已删——范围在地图上一眼可见，类型与变形信息在选项和卡片里都有，再列一遍是重复）
   - 界面上不再有静态说明段落：所有解释都挂在对应标题后的 `?` 提示里（推荐依据、PROJ/WKT 适用软件、参数含义、大地基准怎么选）。新增说明文字时继续用 `data-tip`，不要往界面上铺段落
4. 底图默认**高德卫星**（更直观），地图右上角显示当前底图名，悬停/点击展开切换 **经纬网 / 卫星 / 矢量**，在预览面板里也能正常出图（原理见「技术细节·抗 CSP」）。**默认的经纬网参考模式完全离线、无任何外部依赖，是唯一对外可放心宣传的模式**；高德瓦片走公开接口，个人使用与内部演示可用，但对外分发/商用请自行确认高德的使用条款（详见「底图合规要求」）
   - 底图瓦片全部加载失败时（例如本机完全离线）自动回退到经纬网参考模式并 toast 提示，不会留一张空白地图
   - 若用户点名要天地图：需要用户自备 key（tianditu.gov.cn 免费申请，浏览器端应用，测试 key 约 7 天有效），但天地图瓦片需要 key 且配额有限，一般没有必要
5. 页面**没有页脚**：GCJ-02 纠偏说明在地图问号 tip（`EXTENT_TIP`）里，Projection Wizard 署名在「③ 推荐投影」的 tip 里。交付时口头提醒一句即可：底图坐标系是 GCJ-02，页面已自动纠偏，输入框与输出参数始终是 WGS84 真值
6. 用户提到某国/某行业标准（如 GB/T 45792-2025）时：先查 `references/standards/index.md` 有没有卡片；有则按其规则复核页面给出的投影与参数并在回复中说明差异，无则该标准尚未收录，可请用户提供条款或链接后按 `schema.md` 建卡

## 底图合规要求（重要）

- 白名单图源（均有审图号/合规授权）：**高德（默认，免 key）**、腾讯、百度、天地图。当前实现用高德的公开瓦片接口 `webrd0{1-4}`（矢量）/`webst0{1-4}`（卫星，`style=6` 影像 + `style=8` 透明路网注记）
- 默认参考模式：经纬网格 + 赤道/回归线/极圈参考线 + Natural Earth land-110m 陆地轮廓（无国界、无注记的公开自然地理数据）
- 禁止接入 OSM / Mapbox / Google / Bing / ArcGIS Online 等境外图源；中国范围内内容完整，不得裁剪
- 高德瓦片走公开接口，**适合个人使用与内部演示**；对外分发、商用或公开宣传前请自行确认高德的服务条款——**对外宣传口径只讲经纬网参考模式（完全离线合规），不要把"免 key 调高德"当卖点**；要正式发布建议改走高德 JS API 授权或天地图正式 key
- 开源自荐时的口径（重要）：GitHub README 里只描述"内置经纬网参考底图（Natural Earth，公开数据）+ 可选接入高德"，并注明使用第三方瓦片需遵守其条款
- 需要更多合规细节时加载 `geo-map-compliance-guard` skill，图源可用性对照可参考 `basemap-viewer`（底图测试台）skill

## 技术细节

- 单文件实现：**Leaflet 1.9.4（渲染）**、proj4js 2.11（投影计算/预览）、shpjs（SHP 解析，按需懒加载）
- **为什么是 Leaflet 而不是 MapLibre（踩过的坑）**：宿主（WorkBuddy 预览面板 / webview）在部分机器上是软件渲染、**没有 WebGL**，`new maplibregl.Map()` 会直接抛 `Failed to initialize WebGL`，整块地图空白，且异常会中断后面的 `bindUI()/renderResults()`，页面变成半死状态。Leaflet 用 `<img>` 拼瓦片、SVG 画矢量，不需要 WebGL，在同样宿主里正常显示（这也是 `basemap-viewer` 底图测试台能在面板里出图的原因）。**不要再换回 MapLibre**，除非确认宿主都开了 WebGL
- **抗 CSP 设计（改动前先读）**：① leaflet.css 已整段内联进 `<style id="leafletCss">`（宿主 `style-src` 回落 `default-src`，只认 `'unsafe-inline'`，外链 CSS 必被拦）；② Natural Earth land-110m 陆地轮廓改为 base36 内联字符串（`window.LAND_ENC`，首点 4+4 字符绝对坐标、其后 3+3 字符增量、精度 0.02°、126 环 / 31KB），由 `decodeLand()` 在本地解码成 GeoJSON，不再 fetch world-atlas，也顺带支持完全离线；③ **瓦片由 Leaflet 以 `<img>` 加载**，走 `img-src`（允许 `https:`）而不是 `connect-src`，所以宿主禁止 fetch 也能出底图。改动这三处时务必保持「不新增外部 fetch / 不新增外链 CSS」
- **整体拖动实现**：`extLayer` 设 `interactive:true`（否则收不到鼠标事件），在 `map.getContainer()` 上注册**捕获阶段** `mousedown`：目标若是 `path.leaflet-interactive` 就 `L.DomEvent.stop()` 掉并 `map.dragging.disable()`。必须用捕获阶段——Leaflet 的地图拖拽是容器冒泡阶段的监听，冒泡阶段拦不及时（地图会先开始平移）。移动端跟踪挂在 `document` 上而不是 path 上，因为 `refreshExtentLayer()` 每帧会重建 path
- **范围句柄实现**：用 `L.marker` + `L.divIcon`（不引 Leaflet.draw，避免又一个外部依赖；也不用默认 marker 图标，因为 leaflet.css 里的 `images/marker-icon.png` 是相对路径、会 404）。拖角时只改对应的两条边，`deriveExtent()` 重算 scale/ratio/cat，`refreshExtentLayer(temp, skipKey)` 里要**跳过正在拖的那个 marker**，否则 `setLatLng` 会和鼠标抢位置
- **陆地数据格式**：`decodeLand()` 返回的是 **FeatureCollection（每个环一个 Polygon）**，不是单个 MultiPolygon——Leaflet 会把 MultiPolygon 画成一条 path，126 个环共用 nonzero 填充规则会互相抵消，出现"海洋被填、陆地被挖空"的错乱效果
- **GCJ-02 纠偏**：高德瓦片是火星坐标，页面数据与输出是 WGS84，两者在中国境内差 100–600m。原则是**只在边界转换**：显示时 `GCJ.toGcj()`（范围框 `extentFC`、上传图层 `uplDisplayData()`），拖拽输入时 `GCJ.fromGcj()`（`llWgs()`）。内部 `state.extent` 与所有输出永远是 WGS84 真值。经纬网与陆地轮廓不做转换（世界尺度误差不可见）
- **零外部依赖：所有库都内联**（Leaflet 147KB + proj4 91KB + shpjs 248KB，成品约 610KB）。原以为 `script-src` 放行 `https:` 就够，实测在用户侧仍会出现 `Uncaught ReferenceError: L is not defined`——外链脚本在面板里并不可靠（网络/缓存/代理任一环节出错就白屏）。现在断网 + `script-src 'self' 'unsafe-inline'` 的环境下也完整可用（瓦片除外，瓦片必须联网）
- **布局（窄面板优先，改动前先读）**：没有页头、也没有页脚（GCJ-02 说明并进地图问号 tip、Projection Wizard 署名并进③的 tip；`#app` 是单行 grid）。底图切换是贴在地图右上角的 `#mapBar`：按钮 `#baseBtn` **直接显示当前底图名**（"卫星/矢量/经纬网" + 小三角，`#baseBtnText` 由 `applyBasemap()` 同步，**不要换回图标按钮**），`:hover`/`.open`/聚焦展开**竖排下拉** `#baseSeg`，选完 `setBarOpen(false)` 收起——仿百度地图图层切换。下拉动画用 `opacity+translateY` 过渡（`visibility` 单独设 `transition:visibility 0s linear .16s`——收起时延迟隐藏、展开时立即可见；**不要用 `display:none` 切换**，生硬）。**默认底图是卫星**（`state.base:"img"`，HTML 里 `class="on"` 与 footer 初值三处同步）。地图上不要放任何静态说明文字/徽标（曾有「区域（大比例尺）」徽标，已删：结果区摘要里有同样信息）。范围框操作说明是 `addExtentHelpControl()` 加的 **Leaflet 自定义 control**（`.extent-help-ctl`，`position:"topleft"` 排在 zoom 后面 = 缩放按钮正下方的圆框问号），内部 `data-tip` 挂 EXTENT_TIP，`L.DomEvent.disableClickPropagation` 防止点击穿透到地图——**不要改回右下角浮层**（会压住 attribution 版权条）。`#mapStatus` 平时 `hidden`，只在瓦片报错时由 `onTileError()` 显示。说明文字一律用 `data-tip` + 圆形问号，`#tip` 用 fixed 定位（不能用 CSS 伪元素——`#results` 是滚动容器，伪元素会被裁掉）。`@media (max-width:1100px)`（WorkBuddy 右栏就落在这里）切成单列 flex：`#mapWrap` 用 `order:-1` + `position:sticky;top:0` 吸顶、`#main` 成为唯一滚动容器。**不要再给 aside/#results 各自设 `overflow-y:auto`**，嵌套滚动正是旧版「第 2 步要靠滚动条才看得到」的根因
- **启动必须容错**：`initMap()` 包在 try/catch 里，缺库只显示常驻提示条 `showBanner()`，**绝不能让地图异常中断 `bindUI()/renderResults()`**
- 改完这三个库的行为`loadScript()` / `ensureShp()` 仍保留，作为"有人删掉内联块"时的 CDN 兜底
- **proj4js 坑位（务必注意）**：proj4 对原始 PROJ 字符串不设 `x_0/y_0` 默认值，Albers/LAEA/Mollweide/LCC 等不加 `+x_0=0 +y_0=0` 会算出 NaN。页面向用户输出的 PROJ 字符串无需带这两项（PROJ/GDAL 默认为 0），但所有内部 proj4 调用（预览 `makeForward`、圆锥有效性 `conicCheck`）都在副本上显式补 0；`proj4(str)` 返回的是 `{forward, inverse}` 对象，`forward([lon, lat])` 输入单位为度
- **投影预览**：优先用 proj4js 正算；proj4 未实现的投影（`natearth`、`wintri`、`hammer`、`eck4` 等）用 `MANUAL_FWD` 里的球面公式自绘，四者已用 PROJ（pyproj）在 217 个采样点上校验，误差 ≤1e-15·R；其余未实现投影（`wag4`/`wag7`/`patterson`/`tcea`/`tpeqd`）显式提示"暂不支持网页预览"，不误导为加载失败
- 投影范围计算、推荐分支、PROJ/WKT 组装的完整规则见 `references/projection-rules.md`——修改推荐逻辑或扩展投影时必读
- WKT1 为 ESRI 方言（与 Projection Wizard 输出一致）；WKT2 由 `buildWKT2()` 按 ISO 19162 手写生成，方法名/参数名/参数码照 EPSG 名称表与 PROJ 的 WKT2 输出（`WKT2_METHOD` 表），**比例因子必须写 `SCALEUNIT["unity",1]`**（写成 ANGLEUNIT 会被 PROJ 当弧度解析，整个 CRS 就错了）；伪圆柱族没有 EPSG 方法码，只给 METHOD 名。已用 pyproj 3.8 校验：31 个推荐组合里 29 个的 WKT2 与对应 PROJ 字符串在 4 个采样点上偏差 <0.5 m（`hammer`/`patterson` 因 PROJ 自身只支持球面 + `+datum` 无法建管线而跳过变换比对，但 WKT2 能正确解析出方法与参数）

## 署名与许可（对外分发必读）

- **推荐逻辑来源**：忠实复刻 Bojan Šavrič / Bernhard Jenny 的 [Projection Wizard](https://projectionwizard.org) v2.1 选择规则（基于 John P. Snyder《Map Projections: A Working Manual》的投影选择指南），原实现以 **CC BY** 发布。**任何对外分发（GitHub、博客、课程）必须在 README 与页面内保留署名**，页面内的署名在「③ 推荐投影」问号 tip（`projectionwizard.org，CC BY；本页为离线重实现`）
- **代码许可**：本仓库代码 MIT；文档与规则卡片 CC BY 4.0（见仓库 `LICENSE` / `NOTICE.md`）
- **第三方数据**：Natural Earth land-110m（公有领域）、Leaflet 1.9.4（BSD-2）、proj4js 2.11（MIT）、shpjs（MIT）、高德瓦片（© 高德，页内已保留 attribution）
- **国标卡片**：只摘录投影相关条款 + 出处指针，不放标准原文 PDF；引用时注明标准号与条款号

## Resources

### assets/template/index.html
单文件投影选择器网页模板。使用时整体复制到交付位置，不要拆分；如需定制（增删投影、改默认范围、换语言），直接编辑副本。

### references/standards/
投影相关标准的知识库：`index.md`（总表 + 待收录清单 + 冲突裁决顺序）、`schema.md`（卡片字段与填写规范）、`_template.md`（空白卡）、已收录标准的规则卡（如 `cn-GBT45792-2025.md`）。
**这里放"规则"，不放原文 PDF**：一张卡只摘投影相关条款 + 出处指针（标准号/条款/URL/检索日期）。用户提供标准资料时，按 `schema.md` 建卡并更新 `index.md`。
注意：页面本身只实现几何启发式（Projection Wizard 逻辑）；标准优先级高于它，命中标准时以卡片规则为准，参数（带号、x_0、k、双标准纬线）常需人工改。

### references/projection-rules.md
投影选择规则参考：范围计算公式（scale/ratio）、尺度分类阈值、各变形性质下的推荐分支、PROJ 参数格式、WKT 参数映射表、合规底图要点与抗 CSP 约束。修改推荐引擎或核对规则时加载。
