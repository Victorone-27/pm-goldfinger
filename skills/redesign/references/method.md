# 方法与规范来源

核对日期：2026-10-13。

- [Codex：Build skills](https://learn.chatgpt.com/docs/build-skills)：`SKILL.md` 入口，`name` / `description` 元数据，用户目录 `~/.agents/skills`。
- [Claude Code：Extend Claude with skills](https://code.claude.com/docs/en/skills)：目录内 `SKILL.md`、YAML frontmatter，用户目录 `~/.claude/skills`。
- [abi/screenshot-to-code README](https://github.com/abi/screenshot-to-code)：截图与屏幕状态转为可用 HTML/CSS 等前端产物，再在视觉和交互上迭代。
- [abi/screenshot-to-code LICENSE](https://github.com/abi/screenshot-to-code/blob/main/LICENSE)：本次实际读取为 MIT，`Copyright (c) 2023 Abi Raja`。

本项目只借鉴“先还原、再迭代”的方法，没有复制上游实现、提示词或素材，没有安装其前后端或调用其模型接口。我们的中间产物是有来源的问题判断与可验证改法。上游项目可做品牌素材提取，但本任务按自己的边界用色块代替 logo。

两个宿主均使用现有安装器创建指向仓库的软链接。重新安装已有技能不会覆盖其他来源的同名文件；不靠启动额外模型来验证一个静态模板。
