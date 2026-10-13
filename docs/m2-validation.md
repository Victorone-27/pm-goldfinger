# M2 验证记录

日期：2026-10-13。当前记录包含 M2 首次实施及按用户反馈的修订。本轮仅修改「说人话」规则、模板、示例及对应验证记录；安装器和竞品周报实现未变。

## 文件与内容

- `skills/plain-talk/SKILL.md` 包含 `name`、触发描述、适用边界、最多两个输入追问、编号流程、模板引用、自检清单及示例入口。
- 改写细则单独放在 `prompts/rewrite.md`，输出格式在 `templates/output.md`；不调用独立模型接口。
- 五类示例已按用户要求替换为互联网黑话周报、常见指标、订单导出的 PRD 片段、用户真实简历两句、RAG 加向量检索的保险条款方案。
- 两句简历逐字保留，来源明确标为“用户简历”；PRD 标为 Codex 按要求编写的演示需求，其余三项为用户指定的演示输入。
- 老板版只在原文涉及钱或效率时谈相应影响；老板及 HR 版已删除缺少数据的免责说明，口径缺口只放研发版。
- HR 版鼓励把百分比转成日常说法；所有换算都有公式、精确结果和近似或不等关系说明。老板与研发保留原始数字，HR 保留数字含义及样本、试点、测算等限定。

## 本轮修订验证

- Skill Creator 的 `quick_validate.py` 校验通过。
- 9 项精确算术检查通过：75% 正确对应十题平均错 2.5 题，介于两到三之间；94% 对应 0.6 题，小于一；3pp 按每百人折算多 3 人；增长 12% 对应 100 到 112；35% / 41% 对应每百人 35 / 41 人，差为 6 个百分点。
- 五例老板及 HR 版均不超过三句，未出现缺少数据的说明；HR 版去除了缩写和专业术语。程序检查覆盖句数、常见黑话和说明位置，另逐份人工核对语义。
- 简历仍保留 200 题题库、50 名销售试点及 KYC 回收率提升 50%；没有补“人工判定”、没有把回收率改成人数。视频仍为按历史任务测算的 5–7 天到 2–4 天，没有推导固定节省天数。
- 所有 Skill 本地文件引用可解析，Codex / Claude Code 的既有安装链接均指向本轮修订文件。
- 本轮未新增独立模型调用。五类改写在当前会话内按修订规则完成；自然语言自动触发的历史实测记录如下。

## 安装验证

规范来源（当日实际读取）：[Codex](https://learn.chatgpt.com/docs/build-skills)、[Claude Code](https://code.claude.com/docs/en/skills.md)。两种宿主均支持 Skill 目录软链接；本项目使用共同支持的 `name` 和 `description` 字段。

当前用户安装目标为 `~/.agents/skills/plain-talk` 和 `~/.claude/skills/plain-talk`，均指向本仓库 `skills/plain-talk`。占位的 `teardown` 与 `redesign` 被跳过。

安装器 5 项隔离测试在首次 M2 实施时已通过，本轮安装器未改动，未重复运行。覆盖：

1. 预览、取消不写文件。
2. 确认后安装、重复安装与卸载；源文件及其他技能保持不变。
3. 任一目标冲突时，在修改其他目标前停止。
4. 外部来源或已断开的链接不会被移除。
5. 可按宿主或技能限定范围，拒绝安装占位 Skill。

## Codex 发现与自然语言触发（首次版本的实测记录）

本机 Codex CLI 版本：`0.142.4`。

先通过本地 app-server 的 `skills/list` 查询，返回 `name=plain-talk`、`enabled=true`、`scope=user`，路径解析到本仓库的 `SKILL.md`。该查询不发起模型请求。

随后经用户明确授权，执行一次独立 Codex 运行：仅传入下面的自然语言，没有显式指定 Skill 名称或路径。

> 帮我把这段话说成人话：问答正确率从 75% 提升到 94%（200 题测试集，人工判定）。

运行事件证实 Codex 主动读取：

- `skills/plain-talk/SKILL.md`
- `skills/plain-talk/prompts/rewrite.md`
- `skills/plain-talk/templates/output.md`

最终回答给出老板、HR/外行、研发三版。该次输出与验证记录保存在首次实施提交 `c216485`，使用的是修订前的表达规则；当前[五类示例](../skills/plain-talk/examples/README.md)已按用户要求替换，不将旧输出作为修订后效果的证明。

CLI 记录的本次用量：输入 54788 token，其中缓存输入 39808；输出 289 token。这里记录接口用量，不据此推算费用。

## 验证边界

自然语言触发为首次版本在本机 Codex 的一次真实验证；本轮触发描述及安装方式未变，表达规则与示例已变，未另做独立模型触发测试。Claude Code 已验证安装链接和规范兼容性，未执行模型调用。用户可分别用 `$plain-talk` 和 `/plain-talk` 显式调用。

## 复现

从仓库根目录：

```sh
bash scripts/install_skills.sh --dry-run
bash scripts/install_skills.sh
agents/competitor-weekly/.venv/bin/python -m pytest -q scripts/tests
```

然后在 Codex 中输入上述自然语言请求，观察是否加载 Skill 并输出三版。测试安装、卸载的脚本使用临时目录，不动用户其他技能。
