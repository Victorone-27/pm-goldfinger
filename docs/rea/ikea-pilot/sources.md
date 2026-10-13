# 宜家单页试点｜证据附录

日期：2026-10-13。产品页面只访问 `https://www.ikea.cn/cn/zh/`，未登录。官方文档用于核对服务用途，不作为宜家实际启用功能的替代证据。

## 截图

| 编号 | 文件 | 采集时间（UTC+8） | 可支持的判断 |
| --- | --- | --- | --- |
| S1 | [初次首页](../../assets/teardown-technical/ikea-before-cookie.png) | 17:43:22.572 | Cookie 提示、设计服务推广；不是后续隐私选择的截图 |
| S2 | [点击 Cookie 后的首页](../../assets/teardown-technical/ikea-home.png) | 17:54:30.230 | 隐私提示与推广叠加；登录与客服入口 |
| S3 | [向下滚动后的首页](../../assets/teardown-technical/ikea-scrolled.png) | 18:18:23.720 | 房间卡片与持续遮挡；与 E1 的滚动属于同次操作 |

截图尺寸均为 2400 × 1410；原文件 SHA-256、rea 来源 ID 与时间记录在 [screenshots.json](screenshots.json)。保留截图原字节，未裁剪或涂改。图中人物为宜家公开推广素材，不是本机用户或登录账户信息。

## 采集与静态分析

**E1：[inspection-summary.json](inspection-summary.json)。** 来源操作 `inspect_web_page`，来源 ID 为 `ev_6d7b197c95ce98978a7c312697b15adb4a75d71c1bcd4d65e1030775fb86d748`。

- 保留页面地址、捕获窗口、宿主动作时间、必要脚本/资源、5 条图片请求及原结果的范围限制；5,007 个 DOM 节点、1,732 个可访问性节点、26 个脚本、79 个资源。数字来自记录数组/结果字段，不是外层对象键数。
- `prior_activity_available: false`，`completeness.status: policy_filtered`。只按正常浏览中发现的 9 个精确 origin 观察，非允许范围请求被过滤；摘要的 `relevant_origins` 仅列与本文结论相关的 6 个。
- 来源窗口为 `2026-10-13T10:18:16.295Z` 至 `10:18:23.389Z`；滚动为 `10:18:17.797Z`，位于窗口内。先收到启用被动 CDP 的进度，再延后触发一次滚动；最终网络记录确认有 5 条图片请求。
- 原始请求 URL 的 query/fragment 已去除，图片文件标识替换为 `[id]`；不保留 Cookie、请求头、请求体或响应正文。

**E2：[bundle-summary.json](bundle-summary.json)。** 来源操作 `analyze_web_bundle`，来源 ID 为 `ev_5fde849fd909d0e0551507bacf97e3f6a4e32b4d378f2e0d4ed19c63e0c6ce84`。

- 只分析宜家同源脚本：21 个成功、0 个解析失败；未取 source map，未解混淆、未反编译二进制，也未执行脚本文本。
- 主脚本：`https://www.ikea.cn/ikeacn-web-next/CiLYAH80.js`。SHA-256：`ba76e71de40d52d22fee6b2488d831ef5a892a6d492b750867f460c1be53092c`。文本大小 2,446,691 字节，不是网络传输量。
- Vite / Vue 是工具的有界推断，置信度 medium，检测规则分别是 `vite-runtime` / `vue-runtime`；指向同一脚本与哈希。
- 仅摘录两个可解释的静态路径候选：`/event-tracking-service/api/v1/user-events/zipped`（行 698、列 122900）及 `/event-tracking-service/api/v1/user`（行 698、列 123082）。位置按 rea 原输出保留，机制为 `call:P.post`。未主动探测，不把全部字符串候选当成真实接口清单。
- `complete` 只代表所选脚本完成解析，不代表对整站或后端的完整观察。

**摘要保真范围：** E1/E2 JSON 明确标为 `redacted_summary_not_original_evidence`。`source_evidence_id` 只表示来源关系，不是当前摘要的内容哈希，也不能用于宣称脱敏文件等于原始 Evidence。原采集/脚本数据已随临时浏览器目录清除；现在可核对的是摘要、截图及本次验证记录，无法从摘要重建全部原始数据。

## 实际查阅的官方资料

| 编号 | 来源 | 实际核对内容 | 用法限制 |
| --- | --- | --- | --- |
| D1 | [GrowingIO：集成最新 SDK](https://docs.growingio.com/v3/developer-manual/sdkintegrated/web-js-sdk/latest-jssdk) | 正文的安装代码示例包含 `assets.giocdn.com/2.1/gio.js`；正文介绍浏览量、点击量等采集配置 | 用于确认 SDK 归属；未使用文档网站自身的埋点脚本冒充正文，也未由文档推定宜家的数据采集配置 |
| D2 | [极验文档中心](https://docs.geetest.com/index) | 产品说明为网站/应用提供交互安全服务，列出行为验证产品 | 只支持厂商用途线索；未核对 `gt.js` 的具体版本和宜家启用流程 |

两项均于 2026-10-13 实际读取。正文核对摘要保存在 [vendor-docs.json](vendor-docs.json)。

## 运行验证

[安装核验](installation-check.json) · [MCP 握手](mcp-check.json) · [浏览器清理](cleanup.json) · [完整执行记录](../../rea-installation.md)。MCP 记录是按真实配置启动的直接协议调用结果，不能替代 Codex 当前会话的工具重连验证。
