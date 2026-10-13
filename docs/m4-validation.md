# M4 验证记录

日期：2026-10-13。M4 已完成，待用户验收。M3 继续暂缓，M4.5 未开始。

## 本次交付

- `skills/teardown/SKILL.md`：替换 M0 占位，包含触发条件、输入、最多两个追问、编号流程、自检清单、边界和真实示例。
- `prompts/analyze.md` 与 `templates/report.md`：分析规则和一页报告模板；仅用宿主能力，不新增模型 API 或依赖。
- [宜家中国](../skills/teardown/examples/01-ikea.md)、[秘塔 AI 搜索](../skills/teardown/examples/02-metaso.md)、[少数派](../skills/teardown/examples/03-sspai.md)：三个经用户确认的不同类型产品；每例 3 个指向具体步骤的 AI 机会点。
- [证据清单](../skills/teardown/examples/sources.md)：15 个证据编号，页面 URL、日期、操作与截图；不把页面生成内容当外部事实。用户未提供目标岗位，三例均省略可选面试部分。
- README 增加安装与用法，更新 M2 通过、M3 暂缓与 M4 待验收状态。安装器本体、M1/M2 实现和原始 TASKS.md 未改。

## 路径与内容核验

| 产品 | 真实核验 | 范围限制 |
| --- | --- | --- |
| 宜家中国 | 首页分类到商品详情；列表选 2人座后结果更新；展开并核对商品/包装尺寸 | 不加购下单、不提供地址；对比仅看到入口 |
| 秘塔 AI 搜索 | 预检已真实提交一问一追问；本轮复核两轮回答并打开官方 PDF 链接 | 不新增问题；API 入口要求登录，停止该分支，未确认定价 |
| 少数派 | 免费文章到关联文章；公开 PRIME 套餐与 FAQ；目录试读、付费章节预览及付费墙 | 不购买、不登录、不访问受限正文 |

逐份人工对照观察与来源完成：

1. 宜家：商品 145 × 71.5 × 71.5 厘米与包装 138 × 74 × 34 厘米分开；没有把页面自动城市当用户地址，也没有说宜家不存在 AI 助手。
2. 秘塔：初答/追问截图分别对应；仅指出本次追问无初答式行内引用，不外推至全站；同标题来源不直接判成重复文档。
3. 少数派：顶栏、PRIME 首屏及套餐卡分别列明；栏目订阅按钮与 PRIME 入会入口区分。普通免费文章、试读、部分预览、单买、年/月会员权益逐项核对，不写成“会员可读全部付费内容”。
4. 九个 AI 机会点均包含具体页面/步骤、依据、改动、小实验和衡量指标/错误护栏。实验人数、任务数是提议，不是历史结果。推断逐项标注，事实与影响假设分开。
5. 截图均已目视检查；仅 DOM 中观察到但截图未覆盖的事实标为【公开资料】。相对文件链接已检查；外链来自实际浏览记录，没有批量重复请求目标站点。

## Skill 与安装验证

规范依据沿用 M2 当日已实际查阅的官方文档：[Codex](https://learn.chatgpt.com/docs/build-skills)、[Claude Code](https://code.claude.com/docs/en/skills.md)。使用双方支持的 `name` / `description` 字段；具体历史记录见 [M2 验证](m2-validation.md)。

- Skill Creator `quick_validate.py`：通过。
- 安装器 pytest：**5 passed**。适配原先把 teardown 当占位的测试，现在默认安装 plain-talk + teardown，仍拒绝 redesign 占位。
- 覆盖预览/取消不写入、两个宿主安装/重复安装/卸载、保留源文件与其他 Skill、冲突时不做部分安装、保护外来链接、限定技能选择。
- 先预览，再执行 `--skill teardown --yes`；核对 `~/.agents/skills/teardown` 与 `~/.claude/skills/teardown` 均软链接至本仓库。
- 本次报告由当前宿主会话按新规则整理；没有运行独立 Codex/Claude 模型触发测试，不声称已验证自然语言自动选中。新会话可用 `$teardown` 或 `/teardown` 显式调用。
- 提交前对 Git 已跟踪及待提交文本扫描常见密钥、私钥、带凭据 URL 和硬编码令牌模式：无匹配；截图目视检查未见用户账户、密钥或私密资料。没有读取用户 API key 或钥匙串。

## 本地复现

在 `.`：

```sh
agents/competitor-weekly/.venv/bin/python -m pytest -q scripts/tests
bash scripts/install_skills.sh --skill teardown --dry-run
```

需要独立使用时，在新会话里对 Codex 说：

> 用 $teardown 拆解宜家中国 https://www.ikea.cn/cn/zh/ ，只看未登录的沙发选购路径，重点分析筛选与购买决策。

## 已知限制与下一步

报告为 2026-10-13 的桌面匿名样本，不覆盖账户内功能、移动端或全部推荐机制。动态价格、权益和匿名会话链接可能改变，因此保留本地截图。秘塔 API 商业定价未验证；卡点与改善效果仍需用户实验。安装已验证，自动触发未独立验证。

等用户回复“通过”后才进入 M4.5：先研究 rea 并交学习笔记，再等确认；本轮未研究/安装 rea，也未推送或发布。
