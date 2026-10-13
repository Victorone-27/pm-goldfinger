# M2 验证记录

日期：2026-10-13。范围：「说人话」Skill、五类示例及 Skill 安装器；未修改竞品周报实现。

## 文件与内容

- `skills/plain-talk/SKILL.md` 包含 `name`、触发描述、适用边界、最多两个输入追问、编号流程、模板引用、自检清单及示例入口。
- 改写细则单独放在 `prompts/rewrite.md`，输出格式在 `templates/output.md`；不调用独立模型接口。
- 五类示例分别为真实周报句子、任务书需求、按已实现功能整理的简历句子、任务书指定指标和已实现技术方案。每份标明输入、来源与事实范围。
- 已逐份检查三版数字与原文一致，老板及 HR 版不超过三句；HR 版用普通词语替换专业表达，没有编造收入、工时、个人功劳或真实业务效果。
- 指标示例使用实际 Codex 触发运行的三版输出。75%、94%、200 题、人工判定均保留；“同题同条件”被列为缺少信息，没有私自补齐。

## 安装验证

规范来源（当日实际读取）：[Codex](https://learn.chatgpt.com/docs/build-skills)、[Claude Code](https://code.claude.com/docs/en/skills.md)。两种宿主均支持 Skill 目录软链接；本项目使用共同支持的 `name` 和 `description` 字段。

当前用户安装目标为 `~/.agents/skills/plain-talk` 和 `~/.claude/skills/plain-talk`，均指向本仓库 `skills/plain-talk`。占位的 `teardown` 与 `redesign` 被跳过。

安装器 5 项隔离测试通过，覆盖：

1. 预览、取消不写文件。
2. 确认后安装、重复安装与卸载；源文件及其他技能保持不变。
3. 任一目标冲突时，在修改其他目标前停止。
4. 外部来源或已断开的链接不会被移除。
5. 可按宿主或技能限定范围，拒绝安装占位 Skill。

Skill Creator 的 `quick_validate.py` 校验通过；所有本地文档引用可解析。

## Codex 发现与自然语言触发

本机 Codex CLI 版本：`0.142.4`。

先通过本地 app-server 的 `skills/list` 查询，返回 `name=plain-talk`、`enabled=true`、`scope=user`，路径解析到本仓库的 `SKILL.md`。该查询不发起模型请求。

随后经用户明确授权，执行一次独立 Codex 运行：仅传入下面的自然语言，没有显式指定 Skill 名称或路径。

> 帮我把这段话说成人话：问答正确率从 75% 提升到 94%（200 题测试集，人工判定）。

运行事件证实 Codex 主动读取：

- `skills/plain-talk/SKILL.md`
- `skills/plain-talk/prompts/rewrite.md`
- `skills/plain-talk/templates/output.md`

最终回答给出老板、HR/外行、研发三版，正文已收入[指标示例](../skills/plain-talk/examples/04-metric.md)。检查结果：数字与来源状态准确；老板版说明未提供成本或效率数据；HR 版用做题批卷解释；研发版保留样本量、人工判定并指出比较条件缺口。

CLI 记录的本次用量：输入 54788 token，其中缓存输入 39808；输出 289 token。这里记录接口用量，不据此推算费用。

## 验证边界

自然语言触发是对本机 Codex 的一次真实验证，不保证所有宿主、模型和所有措辞都必然触发。Claude Code 已验证安装链接和规范兼容性，未另行执行模型调用。用户可分别用 `$plain-talk` 和 `/plain-talk` 显式调用。

## 复现

从仓库根目录：

```sh
bash scripts/install_skills.sh --dry-run
bash scripts/install_skills.sh
agents/competitor-weekly/.venv/bin/python -m pytest -q scripts/tests
```

然后在 Codex 中输入上述自然语言请求，观察是否加载 Skill 并输出三版。测试安装、卸载的脚本使用临时目录，不动用户其他技能。
