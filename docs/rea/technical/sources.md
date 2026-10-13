# M4.5 技术透视｜秘塔与少数派证据

日期：2026-10-13，时区 UTC+8。浏览器为项目内 **Chrome for Testing 155.0.8059.39**，全新未登录 profile，独立于日常 Google Chrome；全部操作经过核验的 `127.0.0.1:61328`。采集已结束，进程、端口和 profile 已清理。

本附录区分 **rea 观察**与**宿主 CDP 元数据**。前者支持脚本、资源和窗口内请求等；后者补充正常操作前启用的网络记录、持续接收数据的时间和长度。没有使用通用应用、窗口或无障碍读取工具，没有登录、购买或探测未触发的接口。

## MT1

秘塔[首页](https://metaso.cn/)，rea 截图与短窗口采集：

- [首页截图](../../assets/teardown-technical/metaso-technical-home.png)，18:47:09；保留“登录/注册”状态与公开功能入口。
- [metaso-rea.json](metaso-rea.json) 的 `home`：来源 ID `ev_e504463e7857111814ce30f9d4e9c78a6b102d5c7bbb5b64a393835dabdc3ab9`。窗口 18:47:07.723–18:47:09.146；配置观察 1000 ms，实际还含采集处理时间。
- 原采集计数：141 个脚本、131 个资源、0 条窗口内请求。摘要只保留支持结论的脚本/资源，因此保留数组长度不等于原采集计数。0 条请求不代表页面加载时没有请求。
- 可核对脚本：`res.wx.qq.com/connect/zh_CN/htmledition/js/wxLogin.js`、`o.alicdn.com/captcha-frontend/aliyunFP/fp.min.js`、`static-1.metaso.cn/_next/static/chunks/main-app-56a5f76b4d05b4e6.js`。只确认已加载；登录/验证码用途为基于路径的推断，未实际触发验证。

## MT2

初问输入：“2025年诺贝尔物理学奖授予了谁？请提供诺贝尔奖官网来源。”首页选“深入”，18:48:55.987 提交，未登录。

- [初答截图](../../assets/teardown-technical/metaso-technical-answer.png)，18:49:44；有段落、引用编号与来源侧栏。截图仅用于核对产品输出形态，不将回答内容当作本研究事实。
- rea [metaso-session.json](metaso-session.json)：来源 ID 与窗口在文件中；18:48:55.239–18:49:20.243 覆盖本次提交，记录首页到 `/chat/[session]` 的同文档导航。会话标识已替换。
- 宿主 [metaso-stream.json](metaso-stream.json) 的 `records[0]`：`POST https://metaso.cn/api/search/chat`，Fetch，200，HTTP/2，`text/event-stream`；39 次非空 `Network.dataReceived`，首末时间 116194.889779 → 116206.041727（CDP 单调时钟），跨度 11.151948 秒。
- 分批数据长度/时间保留在 `chunks`；正文只引用约 11.152 秒。不是 token 数、不是 SSE 消息数量，也不是从按下回车到完成回答的总耗时。

## MT3

追问输入：“请只依据上述官方来源，用普通人能听懂的话解释获奖发现，并保留出处。”18:50:42.554 提交，仍未登录。

- [追问截图](../../assets/teardown-technical/metaso-technical-followup.png)，18:51:07；产品实际提供第二轮解释。
- rea [metaso-rea.json](metaso-rea.json) 的 `followup`：来源 ID `ev_ff9cd0557276b43c38319551a9b4783b0bbe06f559826b781c8acf671abbe7e8`。18:50:41.806–18:51:06.930，25 秒配置窗口覆盖提交与回答过程；108 个脚本、142 个资源、9 条请求。
- rea 与宿主都记录到 `POST https://metaso.cn/api/search/chat`，200 / `text/event-stream`。宿主 `metaso-stream.json` 的 `records[1]` 有 26 次非空数据事件，首末时间 116301.448638 → 116307.174955，跨度 5.726317 秒。
- 同窗还采到 `POST https://metaso.cn/admin/user/event_report`，200 / JSON；只记录实际请求路径，不保留字段值，不主动调用这个接口。

**初问与追问的共同限制：**两次流在 CDP 中均以 `net::ERR_ABORTED` 结束，没有 `loadingFinished`；页面都有可见回答，但未核实连接终止原因。不将该信号直接解释为服务故障，也不写成“请求正常结束”。Fetch 接收 `text/event-stream` 时，本次未收到 EventSource 专用消息事件；因此使用 MIME 与持续数据时序作证，不声称解析了 SSE 帧或逐 token 协议。可见正文长度采样仅是界面变化的补充，没有保存采样正文。服务端内部调用及模型厂商不可见。

## ST1

少数派[首页](https://sspai.com/)及打开的[免费《派评》](https://sspai.com/post/115934)。

- [首页截图](../../assets/teardown-technical/sspai-technical-home.png)，18:52:55；全局 PRIME 与公开内容入口可见。
- rea [sspai-rea.json](sspai-rea.json) 的 `home`：来源 ID `ev_b24e1b3312cdee7ef648392d1be3022d567d369cce501cdc7daa92570661c05f`，27 个脚本、76 个资源、0 条短窗口内请求。
- 宿主 [sspai-network.json](sspai-network.json) 的 `home` 阶段，在导航前启用网络事件，实际记录 `www.googletagmanager.com/gtag/js`、`hm.baidu.com/hm.js`、`hm.baidu.com/hm.gif`，首次响应均 200。
- 从首页链接打开免费文章的新页，正文、文末与关联阅读可见；该新页加载前未另附加网络记录器，不声称完整采集了它的初始请求。原 M4 的阅读截图与产品结论仍有效，本次不复制整篇文章。

## ST2

从首页 PRIME 进入[会员介绍](https://sspai.com/prime/explore)，展开“年付和月付会员有什么区别？”FAQ。

- [PRIME 首屏](../../assets/teardown-technical/sspai-technical-prime.png)与[FAQ 入口](../../assets/teardown-technical/sspai-technical-faq.png)，18:54:07。FAQ 截图在展开动画期间捕获，尚未呈现答案，不能用它证明答案文字；点击后实际读取的可见 DOM 摘录在 [page-observations.json](page-observations.json)，明确月付不享有会员栏目畅读。首屏与套餐区入会入口也在 DOM 中复核，原 M4 的[展开 FAQ 截图](../../assets/teardown/sspai-prime-faq.jpg)继续作为已展开样式证据。
- rea `sspai-rea.json` 的 `prime`：来源 ID `ev_fd42b90e6c3a1d5807e3a5c668f3e59785921d968d3b8c927dc90a5bf31a675b`，24 个脚本、81 个资源、1 条短窗口请求。资源中含 Google tag 等脚本。
- 宿主 `sspai-network.json` 的 `prime` 阶段记录 `GET https://sspai.com/api/v2/member/single/info/get`，200 / JSON，以及 `POST https://www.google-analytics.com/g/collect`，204 / `text/plain`。
- 仅由接口名称与页面状态关联用途，未读取响应正文中的会员字段。统计请求的参数和 payload 不保留，无法据此列出真实埋点事件方案。

## ST3

直接复核原 M4 的[栏目目录](https://sspai.com/series/422/list)，再沿页面提供的链接打开[付费文章预览](https://sspai.com/post/113073)。没有点订阅、登录或尝试读取付费墙之后的正文。

- [目录截图](../../assets/teardown-technical/sspai-technical-directory.png)，18:55:10：免费试读、¥59、年付会员免费可见；“全部内容（付费后可读）”在当前视口下方，本次通过同页可见 DOM 核对，摘录见 [page-observations.json](page-observations.json)，不能把该标题算作新截图直接所见。
- [付费墙截图](../../assets/teardown-technical/sspai-technical-paywall.png)，18:56:23：顶部 PRIME、“订阅栏目查看完整内容”、栏目单订与年付权益提示并列。
- rea `sspai-rea.json` 的 `paid_preview`：来源 ID `ev_743b1775ed280e6d7b78906d5532cd4eba43bea045a6ba459bc90d7a409ac719`；32 个脚本、51 个资源、0 条短窗口请求。脚本包含 `res.wx.qq.com/open/js/jweixin-1.4.0.js`。这不是微信支付已接入的证据。
- 宿主 `sspai-network.json` 的 `paid-preview` 阶段：`GET https://sspai.com/api/v1/article/info/get`、`GET https://sspai.com/api/v1/series/info/get` 均 200 / JSON；Google Analytics 的 `/g/collect` 返回 204；百度 `/hm.gif` 返回 200。
- API 的 query/fragment 已移除，未读响应正文、未枚举文章或调用发现的接口；不能由可见付费墙推断权限校验只在前端或已经由服务端安全实现。

## D1

[Google 官方：Set up the Google tag with gtag.js](https://developers.google.com/tag-platform/gtagjs)，2026-10-13 实际查阅。用于核对 Google tag 名称及用途，配合实际 Google Analytics 请求；不由通用文档推定少数派的事件或归因配置。

## D2

[百度统计](https://tongji.baidu.com/)，2026-10-13 实际查阅公开落地页，产品自述为“一站式智能数据分析与应用平台”。页面跳转到公开登录落地页，没有登录；不保存其跳转查询参数。结合 `hm.baidu.com` 请求提出统计接入推断，未进入控制台核实配置。

## 脱敏与验证范围

- 所有 rea 文件均标记 `redacted_summary_not_original_evidence`；`source_evidence_id` 是来源，不是摘要的内容哈希。筛选后的数组只含相关条目，计数保留原采集口径。原始结果未另作公开保存，无法由摘要重建全部 Evidence。
- 宿主记录明确标为 `host_cdp_metadata_summary`，没有借用 rea Evidence ID。只保留正常浏览实际出现的必要元数据，去掉查询值、fragment 与会话标识；没有凭据、请求/响应正文、受限文章内容或日常 Chrome 数据。
- [screenshots.json](screenshots.json)包含 8 张截图的原始 SHA-256、M6 标注展示版 SHA-256、rea 来源 ID 与时间。M6 增加来源条，必要时遮盖无关署名；rea 来源 ID 仍指向原始采集，不能把展示副本当作原始 Evidence。截图不包括浏览器地址栏和 profile 信息。处理范围见[素材索引](../../assets/screenshot-attribution.json)。
- 运行环境与清理见 [browser-install.json](browser-install.json)、[isolation-check.json](isolation-check.json)、[browser-cleanup.json](browser-cleanup.json)。Chrome for Testing 官方包为 ad-hoc 签名，`codesign` 应用资源封装验证未通过；原始 ZIP CRC 校验通过，未补签、未修改浏览器安全设置。没有把本地 SHA-256 称作上游发布校验值。
- [mcp-check.json](mcp-check.json)记录实际配置的 MCP 协议调用，当前 Codex 会话原生工具重连仍未验证。
