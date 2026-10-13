# rea 安装与宜家试点验证记录

> 发布前历史清理：项目位置按仓库根目录作相对路径展示；MCP 片段不可原样作为启动配置，实际安装时解析为绝对位置。原始机器路径不公开。

> M6 展示处理：本页机器路径已替换为占位，使用时需填写实际仓库路径；真实安装配置未修改。

日期：2026-10-13。本文是宜家试点执行时的历史记录，试点效果现已获用户通过。后续浏览器方案已按用户要求改为独立程序 Chrome for Testing，旧启动命令不再使用；当前规则与 M4.5 整体结果见[整体验证记录](m4.5-validation.md)。下文保留当时操作与偏差事实。[试点报告](rea/ikea-pilot/report.md) · [试点证据](rea/ikea-pilot/sources.md)。

## 授权与实际范围

用户已分别批准临时 dry-run 安装，以及正式安装 `rea-agents@6.4.0`、追加已审阅的一个 Codex MCP 项、启动独立未登录浏览器并采集宜家一个公开页面。正式安装前已展示完整成功 dry-run 与配置差异。本次只完成这一范围，未扩展到秘塔、少数派。

## Node 与安装

| 项目 | 实际结果 |
| --- | --- |
| 安装根目录 | `.local/rea` |
| Node 方式 | 官方便携包 `node-v24.21.0-darwin-arm64` 放在项目内，以绝对路径运行；不增加版本管理工具 |
| rea | `app/node_modules/rea-agents`，版本 `6.4.0` |
| 系统默认 Node | 仍为 `v25.8.1`；原 `/opt/homebrew/bin/node` 指向与文件哈希均未改变 |
| shell | `.zshrc` / `.zprofile` 哈希与安装前一致 |
| Git | `/.local/rea/` 已加入忽略，运行时、依赖、缓存与浏览器数据不提交 |

Node 24.21.0 满足 rea 的 `^24.11.0` 范围。Node 存档 SHA-256、rea 发布包 integrity 已校验；正式包与 lockfile 和获批预览一致。[安装核验](rea/ikea-pilot/installation-check.json)保留版本、哈希与检查结果。

正式安装先解压已校验 Node 包，复制预览的 `package.json`、`package-lock.json` 以及 `rea-agents-6.4.0.tgz`，再执行：

```sh
REA_ROOT="$(pwd)/.local/rea"
REA_NODE="$REA_ROOT/node-v24.21.0-darwin-arm64"

# 两个文件均为空；npm 不接受同时把两类配置指定为同一个 /dev/null。
touch "$REA_ROOT/npm-user.npmrc" "$REA_ROOT/npm-global.npmrc"
env PATH="$REA_NODE/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
  "$REA_NODE/bin/node" "$REA_NODE/lib/node_modules/npm/bin/npm-cli.js" \
  ci --prefix "$REA_ROOT/app" \
  --cache "$REA_ROOT/npm-cache" \
  --userconfig "$REA_ROOT/npm-user.npmrc" \
  --globalconfig "$REA_ROOT/npm-global.npmrc" \
  --registry https://registry.npmjs.org \
  --ignore-scripts --omit=dev --omit=optional --no-audit --no-fund
```

安装新增 143 个包，生命周期脚本关闭；网页能力在此安装方式下实测可用。没有全局 npm 安装，没有运行 `setup --yes`，没有额外安装原生逆向工具或 rea 自带 Skill。

## Codex MCP 的实际改动

在 `~/.codex/config.toml` 仅追加以下内容，原配置备份为同目录 `config.toml.rea.backup`。写入前校验原配置未变；写入后解析比较确认原有配置保留、新项与获批文件一致。

```toml
[mcp_servers.rea]
command = ".local/rea/node-v24.21.0-darwin-arm64/bin/node"
args = [".local/rea/app/node_modules/rea-agents/scripts/rea.mjs", "mcp"]
cwd = "."
startup_timeout_sec = 30
tool_timeout_sec = 120
enabled_tools = ["list_browser_targets", "inspect_web_page", "analyze_web_bundle", "observe_web_session", "capture_web_screenshot"]

[mcp_servers.rea.env]
PATH = ".local/rea/node-v24.21.0-darwin-arm64/bin:/usr/bin:/bin:/usr/sbin:/sbin"
```

上游 dry-run 默认将带 shebang 的 `rea.mjs` 作为 command；本配置显式指定 Node 24，避免解析到 Node 25。PATH 仅影响 rea 子进程。

用真实配置的 command/args/env 创建 MCP stdio 客户端，完成 initialize、工具列表、页面观察与截图调用。服务返回 `rea 6.4.0`、170 个工具，获批的 5 个工具全部存在，stderr 为零字节。[mcp-check.json](rea/ikea-pilot/mcp-check.json)记录握手，E1 与 S3 来自实际 MCP 调用；bundle 分析与前两张截图通过同一安装的 CLI 完成。

`enabled_tools` 限制的是 Codex 开放给模型的工具；rea 服务自身仍声明全量工具。**当前聊天的原生 MCP 列表尚未重新连接验证**，所以这里的“通过”是实际协议调用通过，不是声称宿主当前已加载。后续使用时仍需核对 Codex 重连后的工具列表。

## 独立浏览器与操作

为试点新建空的 profile，未复制日常 Chrome 数据、未登录账号。首次独立启动在端口 19222 后退出，原因未确认；改用 macOS 的新实例启动方式，另建空 profile、改用事先确认空闲的 19223，最终使用 PID 47802（Chrome 155.0.8059.40）。

成功启动参数如下，`<新建空目录>` 为当次的 `.local/rea/browser-runs/ikea-20261013-173626-open`：

```sh
open -na 'Google Chrome' --args \
  --user-data-dir='<新建空目录>' \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=19223 \
  --no-first-run --no-default-browser-check \
  --disable-sync --disable-extensions \
  --disable-features=OptimizationGuideModelDownloading \
  about:blank
```

启动后用 `lsof` 和进程参数核对：监听仅 `127.0.0.1:19223`，PID 对应本次独立 profile；rea/CDP 只使用该端点。宿主负责正常导航、点击 Cookie 提示及滚动，rea 负责观察。未登录、未购物、未预约、未提交表单；新出现的隐私选择没有点击。

**偏差记录：** 在识别窗口时，通用 Chrome 应用选择器误读了日常 Chrome 当前窗口的无障碍内容，随后一次全局状态查询返回了日常浏览器元数据及鉴权错误。没有在该窗口进行页面操作，rea/CDP 也没有连接该实例；误读内容未纳入报告、截图或项目证据。发现后已告知用户，停止使用通用选择器，后续只通过核验过的独立端口操作。因此不能将本次执行描述为“全程未读取日常 Chrome”，该项偏差交用户判断。

## 有效与无效的观察

- 静止页面的初次观察为零条请求：只能说明连接后窗口没有采到，不用于证明网页没有网络活动。
- 一次尝试在观察期间刷新返回 `target_changed`，这次不作为成功采集证据。
- 最终使用同页滚动：7000 ms 观察窗口内记录一次向下滚动，成功捕获 5 条图片请求，全部 `200` / `image/webp`。页面结构、脚本、资源与请求分别计数。
- 脚本静态分析仅限同源选定脚本，不取 source map、不解混淆；两条 tracking 路径仅为字符串候选，没有主动探测。
- 未运行模型 API；本次技术结论由宿主基于实测与官方资料整理。

## 清理与验证结果

只向本次独立 PID 发送终止信号；确认端口不再监听、该 profile 无残留进程后，删除两个试点 profile 及其中的 cookies、日志、原始采集与脚本文本。没有用 `killall`，没有关闭日常 Chrome。19222、19223 均已关闭。[cleanup.json](rea/ikea-pilot/cleanup.json)

保留脱敏摘要、三张经目视检查的公开页面截图、截图哈希及运行验证；摘要不冒充原始 Evidence。完成正式安装后，临时预览 runner、便携 Node 副本、缓存与重复解包等已清理；正式运行目录与已审阅的 dry-run 交付保留。

复核覆盖：默认与独立 Node 版本、包版本及获批文件哈希、MCP 增量、shell 未变、截图哈希、浏览器关闭、文档链接、敏感凭据模式检查和 `git diff --check`。本次没有修改周报或说人话逻辑，未重复跑其无关测试。

## 版权与下一步

rea 上游：[morluto/rea](https://github.com/morluto/rea)，MIT，`Copyright (c) 2026 morluto`。本次调用已安装依赖并参考观察与证据方法，没有复制 rea 实现到本项目；依赖原 LICENSE 保留，README 已致谢。

待用户确认宜家效果后，继续验证宿主原生 MCP 连接，再按同样证据标准扩展秘塔与少数派，并更新 teardown 的流程与模板。核心路径要求登录时，仍按已有要求停止该产品并说明。
