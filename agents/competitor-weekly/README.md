# 竞品周报

每周查看中国区 App Store 的竞品更新，与上一份有效快照比较，生成有原文和来源链接的中文周报。

M1 支持豆包、千问、元宝的版本、更新说明、更新日期、评分及评分人数跟踪。小红书模块属于后续 M3。

## 安装

需要 Python 3.11+；运行时仅依赖 PyYAML，联网使用 Python 标准库。进入本目录后执行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 先看效果

```sh
.venv/bin/python run_weekly.py --dry-run
```

读取两周 fixtures，**全程不联网、不调用模型**，即使环境中已配置密钥也不会调用。输出到 `reports/dry-run/2026-W42.md`，不写真实快照。

可直接阅读[完整离线周报示例](reports/examples/dry-run.md)。其中名称、ID、版本、更新说明和评分都是虚构测试数据，不代表真实产品：

| 演示 App | 第二周变化 |
| --- | --- |
| 演示助手甲 | 1.0.0 → 1.1.0；原文写明新增回答收藏功能 |
| 演示助手乙 | 评分 4.2 → 4.3，评分人数 200 → 210 |
| 演示助手丙 | 无变化，一行带过 |

## App 配置与确认

在 `config.yaml` 的 `apps` 中填写显示名、搜索词、已确认的 App ID。新增 App 时先把 `app_id` 设为 `null`，运行：

```sh
.venv/bin/python run_weekly.py --search
```

搜索使用 `country=cn`、`entity=software`，列出名称、开发者、ID、Bundle ID 和商店链接。它不会修改配置。确认候选后，手动写回 `app_id`；若普通运行发现未确认的 ID，也会列候选并停止，避免选错应用。

以下 ID 于 2026-10-13 经 iTunes Search API 查询，并由项目用户确认：

| 显示名 | 搜索返回名称 | App ID | Bundle ID |
| --- | --- | --- | --- |
| 豆包 | 豆包 - 生活工作 AI 助手 | 6459478672 | com.bot.doubao |
| 千问 | 千问 - 阿里AI助手 | 6466733523 | com.aliyun.ios.tongyi |
| 元宝 | 元宝-腾讯全能AI助手 | 6480446430 | com.tencent.hunyuan.app.chat |

查询来源：[豆包](https://itunes.apple.com/search?term=%E8%B1%86%E5%8C%85&country=cn&entity=software&limit=5)、[千问](https://itunes.apple.com/search?term=%E5%8D%83%E9%97%AE&country=cn&entity=software&limit=5)、[元宝](https://itunes.apple.com/search?term=%E5%85%83%E5%AE%9D&country=cn&entity=software&limit=5)。查询结果可能随时间变化。

## 真实运行与比较口径

```sh
# 抓取真实 App Store 数据，不调用模型
.venv/bin/python run_weekly.py --no-llm

# 普通模式：有密钥且存在更新说明变化时才调用模型
.venv/bin/python run_weekly.py
```

也可激活虚拟环境后用 `python run_weekly.py`。从其他目录调用脚本时，默认配置和输出仍以脚本所在目录为准。

- 快照：`data/snapshots/YYYY-MM-DD.json`，日期和采集时间按配置中的 `Asia/Taipei` 记录。
- 周报：`reports/YYYY-Www.md`，使用 ISO 周所属年份，跨年周不会算错。
- 比较用户已确认的**上一份有效快照**，报告注明实际对比日期；不假定间隔恰好七天。同日重跑排除当天快照，保持同一比较基线，覆盖当天快照和本周报告。
- 首次运行或新加入的 App 只建立基线。当前版本的更新说明不被描述为“本周新增功能”。
- 版本、更新说明、更新日期、评分、评分人数的比较全部由代码完成；App 按已确认 ID 匹配。只改变显示名不会被算成版本变化。
- 仅评分或评分人数变化也会报告；全部字段没变化时，周报只有“本周无重要变化”。此时实际对比日期仍保存在快照的 `baseline_date` 中。
- 请求至少间隔 3 秒；网络、HTTP 或 JSON 响应错误重试 2 次。任一 App 获取失败则返回非零状态，保留原有快照与周报，不将失败归为“无变化”。
- 同时启动两个真实任务时，后启动的任务退出，防止覆盖。快照和周报各自原子写入。

真实运行数据和周报已被 `.gitignore` 排除；仓库内的 `reports/examples/` 专门保留可公开示例。

## DeepSeek 解读与降级

密钥只读取环境变量 `DEEPSEEK_API_KEY`，不从配置或文件读取。首次付费调用前需由项目用户确认；本次验收通过无密钥模式完成，不产生模型调用费用。

`config.yaml` 中默认地址为 `https://api.deepseek.com`，模型为 `deepseek-flash`，依据 2026-10-13 查阅的官方文档；模型名称可配置。提示词单独存放在 `prompts/`。

只有更新说明原文相较历史发生变化，才进入模型请求；评分、评分人数与版本号不交给模型计算。首周、仅评分变化、版本变化但说明原文不变时，都不会调用模型。

模型按 JSON 格式返回功能要点和一句话判断，每项附原文证据片段。程序验证证据是否确实出现在对应 App 原文中，并保留完整原文供核对；这能检查引用真实性，不能保证每个语义判断都正确。

没有密钥、指定 `--no-llm`、内容超出输入上限、API 失败、响应不完整或证据无法核验时，都退化为展示原文，周报仍正常生成。模型请求不自动重试，避免重复计费；日志不输出密钥、请求头、模型响应或底层异常正文。

## 每周一定时运行（需要自行安装）

脚本面向 macOS 用户级 launchd，**不会在普通运行时自动安装**。先预览：

```sh
bash schedule/install.sh --preview --no-llm
```

确认后安装，固定跳过模型：

```sh
bash schedule/install.sh --no-llm
```

若已确认启用付费模型，可改为 `bash schedule/install.sh`。launchd 不自动继承当前终端导出的环境变量；若确实需要模型，需先在当前登录会话的 launchd 环境设置已有变量：

```sh
launchctl setenv DEEPSEEK_API_KEY "$DEEPSEEK_API_KEY"
```

这不会把密钥写入 plist，但该环境设置不是跨重启的持久配置；密钥不可用时任务自动退化为原文周报。不要把密钥加入脚本、plist 或仓库文件。

计划时间为**每周一上午 9:00，以 macOS 系统时区为准**；报告日期由 `config.yaml` 的时区决定，建议二者一致。任务只在用户登录会话运行，安装时不立即执行。系统休眠期间错过日历任务会在唤醒后补执行；关机错过的任务需要之后手动运行。

查看与卸载：

```sh
launchctl print "gui/$(id -u)/com.pm-goldfinger.competitor-weekly"
bash schedule/uninstall.sh
```

卸载保留快照、周报和日志。已安装时重复安装会拒绝覆盖；修改计划参数时先卸载再安装。

日志位于 `data/logs/`。虚拟环境必须保留；如使用其他环境，通过 `PM_GOLDFINGER_PYTHON` 指定其 Python 可执行文件的绝对路径。

## 验证

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
env -u DEEPSEEK_API_KEY .venv/bin/python run_weekly.py --dry-run
```

测试覆盖：版本与评分比较、首周基线、无变化、无密钥与 API 失败降级、原文证据核验、仅发送变化的说明、离线模式不联网、同日基线、跨年周编号、限速与重试、抓取失败保留原文件，以及定时任务不写入密钥。

## 官方资料

- [Apple Search API](https://performance-partners.apple.com/search-api)
- [Apple ID Lookup](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/LookupExamples.html)
- [DeepSeek 首次调用、地址与模型名](https://api-docs.deepseek.com/)
- [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/)
- [Apple 定时任务与休眠行为](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)
