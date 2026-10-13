# 演示素材与来源

M6，2026-10-13。以下为当前交付版本；对外展示使用这一版，替代 M5 旧配图版本。HTML 为可编辑源页，PNG 为浏览器实际渲染后导出的效果图。

## 四张工具效果图

均为 **1280 × 800 PNG**，只使用文字、CSS 与原创中性图形，没有第三方商品或房间照片。示例节选经过重新排版，没有虚构运行结果。

| 工具 | 效果图 | 可查看的源页 | 内容依据 |
| --- | --- | --- | --- |
| 产品拆解 | [tool-teardown.png](tool-teardown.png) | [拆解效果图源页](../demos/teardown.html) | [秘塔真实拆解](../../skills/teardown/examples/02-metaso.md)，截图 M2/M3 与技术观察 MT2/MT3；观察限于该次样本 |
| 截图改版 | [tool-redesign.png](tool-redesign.png) | [改版效果图源页](../demos/redesign.html) | [宜家 M5 改版说明](../../skills/redesign/examples/01-ikea/rationale.md)；根据实际方案重排的布局示意，完整交互见下表 |
| 说人话 | [tool-plain-talk.png](tool-plain-talk.png) | [说人话效果图源页](../demos/plain-talk.html) | [用户提供的常见指标示例](../../skills/plain-talk/examples/04-metric.md)；100→112 为比例换算，并非实际人数 |
| 竞品周报 | [tool-competitor-weekly.png](tool-competitor-weekly.png) | [周报效果图源页](../demos/competitor-weekly.html) | [fixtures 离线周报](../../agents/competitor-weekly/reports/examples/dry-run.md)；演示助手甲/乙/丙均为虚构测试数据，不代表真实 App 动态 |

[README 首屏预览](readme-preview.png)由[本地预览页](../demos/readme-preview.html)导出。它展示 README 的标题、介绍和实际四卡内容；不冒充 GitHub 上线截图，宿主排版与屏幕大小会影响首屏范围。

## 三组可点击改版

| 场景 | 对比原型 | 最新效果图 | 本轮变化 |
| --- | --- | --- | --- |
| 宜家首页 | [compare.html](../../skills/redesign/examples/01-ikea/compare.html) | [compare.png](redesign/01-ikea/compare.png) | 卧室、厨房、餐厅照片换成原创 SVG，客厅仍为 CSS 示意 |
| 秘塔追问 | [compare.html](../../skills/redesign/examples/02-metaso/compare.html) | [compare.png](redesign/02-metaso/compare.png) | 已是文字与控件示意，复核没有第三方照片 |
| 少数派 PRIME | [compare.html](../../skills/redesign/examples/03-sspai/compare.html) | [compare.png](redesign/03-sspai/compare.png) | 增高桌面及手机画框，“买之前，先确认这两点”及展开说明完整可见；本来没有商品照片 |

三组共六个 before/after HTML 均可独立离线打开。对比页需要与同目录两个 HTML 一起保留；带编号的问题、报告条目与验证思路见各组 `rationale.md`。所有方案仍是演示草图，不表示线上产品已修改或效果已被业务实验验证。

## 保留的官网截图

`teardown/` 的 18 张 JPG 与 `teardown-technical/` 的 11 张 PNG 是分析证据展示副本，共 29 张。每张底部都标有：

> 截图来源：XX 官网，2026-10-13，仅用于产品分析

来源分别为宜家中国、秘塔 AI 搜索、少数派，以及用于核对秘塔来源的诺贝尔奖官网。URL、采集状态和证据编号见 [M4 来源清单](../../skills/teardown/examples/sources.md)、[宜家试点来源](../rea/ikea-pilot/sources.md)、[M4.5 技术来源](../rea/technical/sources.md)。

其中 10 张遮盖了与产品分析无关的人像、头像、署名或责编信息；匿名会话 URL 已从展示文档移除，项目位置改为仓库根目录相对路径。价格、权益、引用结构、隐私正文等核心证据未改写。诺贝尔奖获奖者姓名是问题与公开来源核查对象，属于必要事实；没有把这些姓名当作用户资料采集。

[screenshot-attribution.json](screenshot-attribution.json)记录每张图的来源条、遮盖坐标、原尺寸、展示尺寸、原始 SHA-256 与当前 SHA-256。**当前加标注文件不是 rea 原始 Evidence 字节**；对应证据索引已同步展示哈希，同时保留 `original_sha256`。经用户授权，发布前已清理全部历史：公开历史只保留加标注及必要遮盖的展示副本。原始截图仅保存在仓库外的私有恢复备份中；`original_sha256` 用于区分原始采集与展示文件，不表示原图仍在公开历史中。

官网截图中的页面、照片、文字与商标归相应权利人；加来源条不代表获得再授权。本项目 MIT 许可适用于自身代码与原创文档，不扩展至第三方素材。原型用色块替代品牌标识，未把第三方照片复用到改版方案或工具效果图中。
