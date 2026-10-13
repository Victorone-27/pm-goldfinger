# 产品经理金手指 · pm-goldfinger

给产品经理用的开源 AI 工具箱：拆产品、改界面、说人话、追踪竞品变化。

An AI toolkit for product managers, built around traceable examples and practical workflows.

## 当前状态

M0、M1 已通过。M2「说人话」已实现，待验收；产品拆解和截图改版仍在开发中。

| 工具 | 用途 | 状态 |
| --- | --- | --- |
| [产品拆解](skills/teardown/) | 从公开网页或截图生成有依据的产品分析 | 开发中 · M4 / M4.5 |
| [截图改版](skills/redesign/) | 从体验问题形成改前、改后可点击原型 | 开发中 · M5 |
| [说人话](skills/plain-talk/) | 面向老板、HR 和研发改写，保持事实与口径 | M2 待验收 |
| [竞品周报](agents/competitor-weekly/) | 对比 App Store 更新，后续增加小红书口碑变化 | M1 已通过；M3 未开始 |

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

## 安装「说人话」

需要 Python 3.11+，安装器只使用标准库。下载仓库后，在仓库根目录运行：

```sh
bash scripts/install_skills.sh
```

脚本先打印计划，输入 `y` 后才会创建链接；默认安装到 Codex 的 `~/.agents/skills` 和 Claude Code 的 `~/.claude/skills`。当前只安装已完成的 `plain-talk`，跳过产品拆解和截图改版的占位文件。通过软链接引用本仓库，请保留仓库位置；更新 Skill 文件后宿主会读取新内容。

按宿主安装、预览和卸载：

```sh
bash scripts/install_skills.sh --target codex --dry-run
bash scripts/install_skills.sh --target codex
bash scripts/install_skills.sh --target claude
bash scripts/install_skills.sh --uninstall
```

重复安装不会重复创建；已有同名文件或其他来源的链接时拒绝覆盖。卸载只删除指向本仓库的链接，保留源文件及其他技能。`--skill plain-talk` 可限定技能；`--yes` 用于已确认的自动化操作，仍先打印计划。

安装后对 Codex 说：

> 帮我把这段话说成人话：问答正确率从 75% 提升到 94%（200 题测试集，人工判定）。

默认输出老板、HR/外行、研发三版；没有收入或效率证据时不补收益，数字和测试口径保留。示例输入来自任务书，不是本项目的真实业务成绩。查看[五类完整示例](skills/plain-talk/examples/README.md)。

也可在 Codex 显式使用 `$plain-talk`，在 Claude Code 使用 `/plain-talk`。自动选择取决于宿主对请求的判断；新安装后若当前会话未刷新技能列表，重新打开会话。安装目录与字段依据 2026-10-13 查阅的 [Codex 官方规范](https://learn.chatgpt.com/docs/build-skills)及 [Claude Code 官方规范](https://code.claude.com/docs/en/skills)。

## 开发顺序

M0 仓库骨架 → M1 App Store 周报 → M2 说人话（含 Skill 安装脚本）→ M3 小红书口碑 → M4 产品拆解 → M4.5 技术透视 → M5 截图改版 → M6 演示素材与 README → M7 作品集网页和 BOSS 长图。

每个里程碑单独进行本地提交，按[任务书第 6 节](TASKS.md#6-验收报告格式每个里程碑结束时交给我)交验收报告，确认通过后再开始下一个里程碑。

## 许可证

[MIT](LICENSE)
