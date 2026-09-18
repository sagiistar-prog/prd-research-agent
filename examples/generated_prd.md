# TeamPulse 团队健康度助手

状态：需求资料已整理，产品方案待补充。

## 资料梳理

原始输入和竞品资料已建立可引用记录。脚本不按行业关键词套用功能。

## 产品功能总览

产品有哪些功能尚未决定。请由产品负责人或宿主 AI 根据下方输入拟定 product_plan。

## 用户故事与验收标准

待方案明确用户、问题、范围和假设后生成。

## 下一步

1. 读取原始需求，确认用户在什么场景下遇到什么问题。
2. 按 schemas/plan.schema.json 编写方案，每项判断引用原文或登记假设。
3. 使用 --plan 重新生成，核对优先级理由、约束响应与验收标准。

## 输入依据

以下是输入记录，不代表独立完成了用户研究或竞品核验。

<a id="e001"></a>
**E001** / context / brief 第 1 行

\# 示例需求：TeamPulse 团队健康度助手

<a id="e002"></a>
**E002** / product / brief 第 3 行

产品名称：TeamPulse 团队健康度助手

<a id="e003"></a>
**E003** / objective / brief 第 5 行

一句话需求：帮助 20 到 200 人的远程团队每周收集团队健康度信号，发现协作风险，并生成可执行的改进建议。

<a id="e004"></a>
**E004** / users / brief 第 7 行

目标用户：远程团队负责人、项目经理、People Ops 伙伴。

<a id="e005"></a>
**E005** / problems / brief 第 11 行

- 团队负责人通常只能在项目延期后才发现协作问题。

<a id="e006"></a>
**E006** / problems / brief 第 12 行

- 现有问卷工具能收集反馈，但很难自动沉淀趋势和行动建议。

<a id="e007"></a>
**E007** / problems / brief 第 13 行

- 团队成员担心反馈被追溯到个人，因此不愿意说真实问题。

<a id="e008"></a>
**E008** / scenarios / brief 第 17 行

- 每周五自动发起 3 分钟健康度脉冲问卷。

<a id="e009"></a>
**E009** / scenarios / brief 第 18 行

- 周一团队负责人查看趋势、风险主题和建议行动。

<a id="e010"></a>
**E010** / scenarios / brief 第 19 行

- 当某个维度连续两周下降时，系统提醒负责人安排跟进。

<a id="e011"></a>
**E011** / constraints / brief 第 23 行

- MVP 只支持单团队，不做复杂组织架构。

<a id="e012"></a>
**E012** / constraints / brief 第 24 行

- 演示数据必须是虚构数据。

<a id="e013"></a>
**E013** / constraints / brief 第 25 行

- 不要求接入真实聊天工具。

<a id="e014"></a>
**E014** / metrics / brief 第 29 行

- 试用团队首周问卷完成率达到 70%。

<a id="e015"></a>
**E015** / metrics / brief 第 30 行

- 团队负责人每周至少查看一次报告。

<a id="e016"></a>
**E016** / metrics / brief 第 31 行

- 4 周内至少创建 1 条改进行动。

<a id="c001-name"></a>
**C001-name** / competitor / competitors.name 第 1 行

PulseBoard

<a id="c001-positioning"></a>
**C001-positioning** / competitor / competitors.positioning 第 1 行

Lightweight pulse survey for small teams

<a id="c001-strengths"></a>
**C001-strengths** / competitor / competitors.strengths 第 1 行

Simple weekly check-in and trend chart

<a id="c001-weaknesses"></a>
**C001-weaknesses** / competitor / competitors.weaknesses 第 1 行

Limited action planning and weak anonymity controls

<a id="c001-pricing"></a>
**C001-pricing** / competitor / competitors.pricing 第 1 行

Freemium

<a id="c001-target_user"></a>
**C001-target_user** / competitor / competitors.target\_user 第 1 行

Startup team leads

<a id="c002-name"></a>
**C002-name** / competitor / competitors.name 第 2 行

MoodMap

<a id="c002-positioning"></a>
**C002-positioning** / competitor / competitors.positioning 第 2 行

Team mood analytics dashboard

<a id="c002-strengths"></a>
**C002-strengths** / competitor / competitors.strengths 第 2 行

Good visualization and manager alerts

<a id="c002-weaknesses"></a>
**C002-weaknesses** / competitor / competitors.weaknesses 第 2 行

Complex setup for small teams

<a id="c002-pricing"></a>
**C002-pricing** / competitor / competitors.pricing 第 2 行

Per seat

<a id="c002-target_user"></a>
**C002-target_user** / competitor / competitors.target\_user 第 2 行

People Ops teams

<a id="c003-name"></a>
**C003-name** / competitor / competitors.name 第 3 行

ActionLoop

<a id="c003-positioning"></a>
**C003-positioning** / competitor / competitors.positioning 第 3 行

Retrospective and improvement tracker

<a id="c003-strengths"></a>
**C003-strengths** / competitor / competitors.strengths 第 3 行

Strong action follow-up workflow

<a id="c003-weaknesses"></a>
**C003-weaknesses** / competitor / competitors.weaknesses 第 3 行

Does not focus on recurring health signals

<a id="c003-pricing"></a>
**C003-pricing** / competitor / competitors.pricing 第 3 行

Per workspace

<a id="c003-target_user"></a>
**C003-target_user** / competitor / competitors.target\_user 第 3 行

Project managers

<a id="c004-name"></a>
**C004-name** / competitor / competitors.name 第 4 行

QuietSignal

<a id="c004-positioning"></a>
**C004-positioning** / competitor / competitors.positioning 第 4 行

Anonymous feedback inbox

<a id="c004-strengths"></a>
**C004-strengths** / competitor / competitors.strengths 第 4 行

Strong anonymous submission experience

<a id="c004-weaknesses"></a>
**C004-weaknesses** / competitor / competitors.weaknesses 第 4 行

Lacks structured weekly cadence

<a id="c004-pricing"></a>
**C004-pricing** / competitor / competitors.pricing 第 4 行

Flat monthly fee

<a id="c004-target_user"></a>
**C004-target_user** / competitor / competitors.target\_user 第 4 行

Remote-first teams

## 原始需求

```text
# 示例需求：TeamPulse 团队健康度助手

产品名称：TeamPulse 团队健康度助手

一句话需求：帮助 20 到 200 人的远程团队每周收集团队健康度信号，发现协作风险，并生成可执行的改进建议。

目标用户：远程团队负责人、项目经理、People Ops 伙伴。

当前问题：

- 团队负责人通常只能在项目延期后才发现协作问题。
- 现有问卷工具能收集反馈，但很难自动沉淀趋势和行动建议。
- 团队成员担心反馈被追溯到个人，因此不愿意说真实问题。

核心场景：

- 每周五自动发起 3 分钟健康度脉冲问卷。
- 周一团队负责人查看趋势、风险主题和建议行动。
- 当某个维度连续两周下降时，系统提醒负责人安排跟进。

约束：

- MVP 只支持单团队，不做复杂组织架构。
- 演示数据必须是虚构数据。
- 不要求接入真实聊天工具。

成功指标：

- 试用团队首周问卷完成率达到 70%。
- 团队负责人每周至少查看一次报告。
- 4 周内至少创建 1 条改进行动。

```

输入指纹：`6bfc39e9c8b9c86f549f7d835240385366cf7dcbcda4c30bd797b83696dfd63a`
