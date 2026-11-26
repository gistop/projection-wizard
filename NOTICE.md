# NOTICE — 第三方来源与署名要求

本项目的**推荐逻辑**并非原创，而是对既有研究成果的工程化重实现。分发、修改、再发布时请保留本文件与 README 中的署名。

## 1. Projection Wizard（推荐引擎的算法来源）

- **项目**：Projection Wizard v2.1
- **作者**：Bojan Šavrič、Bernhard Jenny
- **站点**：https://projectionwizard.org
- **源码**：https://github.com/ProjectionWizard/projectionwizard.github.io
- **许可**：Creative Commons Attribution（CC BY）
- **本项目做了什么**：按其在 `outputFormat.js` 等文件中体现的选择规则（尺度分类阈值 `scale`、南北比对 `ratio`、各变形性质下的推荐分支、锥顶点有效性检查），用 JavaScript 重新实现为单文件离线页面，并补充 PROJ/WKT 输出、WKT2（ISO 19162）生成与 .prj 导出。**未复制其源代码**，行为一致性以几何规则为准。

**署名要求**：任何公开分发需在 README 与应用界面内保留 "基于 Projection Wizard（projectionwizard.org，CC BY）的离线重实现" 的说明。本页界面内的署名位于「③ 推荐投影」标题后的问号提示中。

## 2. 投影选择方法论

- John P. Snyder, *Map Projections: A Working Manual*, USGS Professional Paper 1395, 1987.（公有领域，美国政府出版物）

## 3. 地理数据与代码库

| 组件 | 版本 | 许可 | 用途 |
|---|---|---|---|
| Leaflet | 1.9.4 | BSD-2-Clause | 地图渲染（内联进单文件） |
| proj4js | 2.11 | MIT | 投影正算与预览 |
| shpjs | 3.x | MIT | SHP/ZIP 解析（懒加载） |
| Natural Earth land-110m | — | Public Domain | 经纬网参考模式的陆地轮廓（base36 内联编码） |

以上均以源码内联方式打包进 `dist/projection-wizard.html`，原始许可证见各自仓库。

## 4. 底图瓦片

- 页面内置**经纬网参考模式**（Natural Earth + 自绘经纬网），完全离线、无外部请求，可自由分发。
- **高德地图瓦片**为可选项，走其公开瓦片接口。瓦片版权归高德（© 高德地图 autonavi.com），页面内已保留 attribution。**对外分发或商用前请自行确认高德的服务条款**；本仓库不以「直连高德公开瓦片」作为卖点或技术承诺。

## 5. 国家标准卡片

`references/standards/` 下的卡片仅摘录与投影相关的**条款要点与出处指针**（标准号、条款号、检索日期），**不包含标准原文**。引用时请注明标准号与条款号；标准正文请通过正规渠道获取。
