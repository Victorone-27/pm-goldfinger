# 产品经理金手指 · pm-goldfinger

给产品经理用的开源 AI 工具箱：拆产品、改界面、说人话、追踪竞品变化。

An AI toolkit for product managers, built around traceable examples and practical workflows.

## 当前状态

M0、M1、M2、M4 已通过。产品拆解已补充“30 秒速读”；三例为宜家中国、秘塔 AI 搜索、少数派。M3 小红书口碑暂缓，等用户准备账号；当前进入 M4.5 第一步 rea 研究，接入与截图改版尚未开始。

| 工具 | 用途 | 状态 |
| --- | --- | --- |
| [产品拆解](skills/teardown/) | 从公开网页或截图生成有依据的产品分析 | M4 已通过 · 含 30 秒速读；M4.5 研究中 |
| [截图改版](skills/redesign/) | 从体验问题形成改前、改后可点击原型 | 开发中 · M5 |
| [说人话](skills/plain-talk/) | 面向老板、HR 和研发改写，保持事实与口径 | M2 已通过 |
| [竞品周报](agents/competitor-weekly/) | 对比 App Store 更新，后续增加小红书口碑变化 | M1 已通过；M3 暂缓，等用户准备账号 |

## 设计原则

- 三个 Skill 提供方法、步骤、模板和检查清单，使用 Codex 或 Claude Code 的能力，不单独调用模型接口。
- 竞品周报使用 Python 3.11+，用代码做快照与比较，仅将需要解读的内容交给 DeepSeek；无密钥时直接输出原文。
- 面向求职作品集：每个工具后续提供真实运行示例和效果图，事实附来源，推断单独标明。

## 目录

```text
skills/                    Skill 流程、模板和示例；未完成工具保留占位
agents/competitor-weekly/   周报的代码、提示词、测试、定时任务与数据目录
docs/assets/               后续演示效果图
scripts/                   Skill 安装与卸载脚本
TASKS.md                   原始任务书与验收标准
```

空目录用 `.gitkeep` 保留。运行数据和真实周报不提交到 Git；可公开的周报示例预留在 `agents/competitor-weekly/reports/examples/`。

## 安装 Skill

需要 Python 3.11+，安装器只使用标准库。下载仓库后，在仓库根目录运行：

```sh
bash scripts/install_skills.sh
```

脚本先打印计划，输入 `y` 后才会创建链接；默认安装到 Codex 的 `~/.agents/skills` 和 Claude Code 的 `~/.claude/skills`。当前安装已完成的 `plain-talk` 和 `teardown`，跳过截图改版的占位文件。通过软链接引用本仓库，请保留仓库位置；更新 Skill 文件后宿主会读取新内容。

按宿主安装、预览和卸载：

```sh
bash scripts/install_skills.sh --target codex --dry-run
bash scripts/install_skills.sh --target codex
bash scripts/install_skills.sh --target claude
bash scripts/install_skills.sh --uninstall
```

重复安装不会重复创建；已有同名文件或其他来源的链接时拒绝覆盖。卸载只删除指向本仓库的链接，保留源文件及其他技能。`--skill plain-talk` 或 `--skill teardown` 可限定技能；`--yes` 用于已确认的自动化操作，仍先打印计划。

安装后对 Codex 说：

> 帮我把这段话说成人话：问答正确率从 75% 提升到 94%（200 题测试集，人工判定）。

默认输出老板、HR/外行、研发三版；没有收入或效率证据时不补收益，数字和测试口径保留。示例输入来自任务书，不是本项目的真实业务成绩。查看[五类完整示例](skills/plain-talk/examples/README.md)。

也可在 Codex 显式使用 `$plain-talk`，在 Claude Code 使用 `/plain-talk`。自动选择取决于宿主对请求的判断；新安装后若当前会话未刷新技能列表，重新打开会话。安装目录与字段依据 2026-10-13 查阅的 [Codex 官方规范](https://learn.chatgpt.com/docs/build-skills)及 [Claude Code 官方规范](https://code.claude.com/docs/en/skills)。

## 使用「产品拆解」

安装后对 Codex 说：

> 拆解宜家中国 https://www.ikea.cn/cn/zh/ ，只看未登录的沙发选购路径，重点分析筛选和购买决策。

也可用 `$teardown`（Codex）或 `/teardown`（Claude Code）显式调用。网页由宿主实际浏览并截图；App 需要提供截图或录屏。输出先给“30 秒速读”（最好的一点、最大的问题、先改什么），再给一页摘要，含功能地图、核心路径、商业模式、3 个具体 AI 机会点；提供目标岗位时再加面试准备。速读不带来源标记，下方正文每条结论区分截图、公开资料与推断。

真实示例：[宜家中国](skills/teardown/examples/01-ikea.md) · [秘塔 AI 搜索](skills/teardown/examples/02-metaso.md) · [少数派](skills/teardown/examples/03-sspai.md)；[逐项证据与截图](skills/teardown/examples/sources.md)。少数派单列 PRIME 入口与免费/付费边界。功能使用宿主能力，不新增模型 API、账号或依赖；遇核心登录阻塞就停下说明。

[流程与自检](skills/teardown/SKILL.md) · [M4 验证记录](docs/m4-validation.md)。这里的建议是待验证的方案，不是已取得的产品效果。

## 开发顺序

当前顺序：M0 仓库骨架 → M1 App Store 周报 → M2 说人话（含 Skill 安装脚本）→ M4 产品拆解 → M4.5 技术透视 → M5 截图改版 → M6 演示素材与 README → M7 作品集网页和 BOSS 长图。M3 小红书口碑暂缓，等用户准备好账号后再安排；原始 TASKS.md 保留不改。

每个里程碑单独进行本地提交，按[任务书第 6 节](TASKS.md#6-验收报告格式每个里程碑结束时交给我)交验收报告，确认通过后再开始下一个里程碑。

## 许可证

[MIT](LICENSE)
