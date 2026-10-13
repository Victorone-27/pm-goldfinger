# 项目执行约定

原始任务书为 `TASKS.md`；用户在会话中的最新明确调整优先，任务书不回写。里程碑分别本地提交，交验收报告后等用户回复“通过”；不自动推送或发布。M5 已通过，9 条问题获用户认同 8 条以上；当前进度与检查结果见 `docs/m6-validation.md`，M6 待验收，M3 仍暂缓，M7 未开始。

M5 直接使用 M4/M4.5 已有截图；三组范围为宜家首页浮层、秘塔追问引用、少数派 PRIME 权益。改版说明逐项标注报告标题及问题条目，原型是本地演示，不声称真实改善效果。

M6 交付取代 M5 旧配图版本：三组原型及效果图只用原创中性图形；保留官网截图加日期、来源和“仅用于产品分析”，遮盖无关人像与署名。当前展示图与原始截图哈希分开，索引在 `docs/assets/screenshot-attribution.json`。少数派对比页需保证底部两点说明和展开后的权益依据完整可见。公开发布仍需用户另行确认。

## 浏览器隔离（本项目所有网页工作适用）

仅使用与日常 Google Chrome 不同程序的 Chrome for Testing 或 Chromium，并新建未登录空 profile；禁止用 Google Chrome 另开实例代替。禁止对任何浏览器使用通用应用、窗口、无障碍读取工具，包括只读的窗口发现。只能使用核验过归属的 `127.0.0.1` 调试端口和宿主浏览器能力。

执行前读 `skills/teardown/references/technical-observation.md`，macOS 用其中的 `scripts/isolated_browser.py` 启动、核验和关闭本次程序。无法满足程序隔离、端口核验或清理条件时停止问用户，不切换工具绕行、不连接日常实例。`docs/rea-installation.md` 是宜家试点的历史记录，不是当前浏览器启动方案。

## 运行时与证据

rea 6.4.0 用 `.local/rea/node-v24.21.0-darwin-arm64/bin/node`；不改系统默认 Node 25、shell 配置或 Homebrew 链接。`.local/rea/` 是被忽略的本地运行目录，不能提交浏览器 profile、依赖或缓存。

技术结论使用观察/推断与证据编号；只保存必要脱敏元数据。原始响应、凭据、会话标识和受限正文不进入交付。宿主 CDP 摘要与 rea Evidence 来源分开记录。
