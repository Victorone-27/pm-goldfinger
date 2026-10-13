# 产品经理金手指 · pm-goldfinger

给产品经理用的开源 AI 工具箱：拆产品、改界面、说人话、追踪竞品变化。

An AI toolkit for product managers, built around traceable examples and practical workflows.

## 当前状态

当前为 M0 仓库骨架，四个工具均在开发中，暂不可安装或运行。

| 工具 | 用途 | 状态 |
| --- | --- | --- |
| [产品拆解](skills/teardown/) | 从公开网页或截图生成有依据的产品分析 | 开发中 · M4 / M4.5 |
| [截图改版](skills/redesign/) | 从体验问题形成改前、改后可点击原型 | 开发中 · M5 |
| [说人话](skills/plain-talk/) | 面向老板、HR 和研发改写，保持事实与口径 | 开发中 · M2 |
| [竞品周报](agents/competitor-weekly/) | 对比 App Store 更新，后续增加小红书口碑变化 | 开发中 · M1 / M3 |

## 设计原则

- 三个 Skill 提供方法、步骤、模板和检查清单，使用 Codex 或 Claude Code 的能力，不单独调用模型接口。
- 竞品周报使用 Python 3.11+，用代码做快照与比较，仅将需要解读的内容交给 DeepSeek；计划支持无密钥时直接输出原文。
- 面向求职作品集：每个工具后续提供真实运行示例和效果图，事实附来源，推断单独标明。

## 目录

```text
skills/                    三个 Skill 的占位说明、模板和示例目录
agents/competitor-weekly/   周报的代码、提示词、测试、定时任务与数据目录
docs/assets/               后续演示效果图
scripts/                   后续 Skill 安装与卸载脚本
TASKS.md                   原始任务书与验收标准
```

空目录用 `.gitkeep` 保留。运行数据和真实周报不提交到 Git；可公开的周报示例预留在 `agents/competitor-weekly/reports/examples/`。

## 开发顺序

M0 仓库骨架 → M1 App Store 周报 → M2 说人话（含 Skill 安装脚本）→ M3 小红书口碑 → M4 产品拆解 → M4.5 技术透视 → M5 截图改版 → M6 演示素材与 README → M7 作品集网页和 BOSS 长图。

每个里程碑单独进行本地提交，按[任务书第 6 节](TASKS.md#6-验收报告格式每个里程碑结束时交给我)交验收报告，确认通过后再开始下一个里程碑。

## 许可证

[MIT](LICENSE)
