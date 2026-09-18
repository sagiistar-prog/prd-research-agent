# TeamPulse 团队健康度助手

状态：待人工评审。引用校验不代表方案已验证。

## 产品目标

让远程团队负责人从每周反馈中发现协作阻碍，并留下能在下一次复盘验证的改进行动。

[E003](#e003)：一句话需求：帮助 20 到 200 人的远程团队每周收集团队健康度信号，发现协作风险，并生成可执行的改进建议。；[E005](#e005)：- 团队负责人通常只能在项目延期后才发现协作问题。；[E006](#e006)：- 现有问卷工具能收集反馈，但很难自动沉淀趋势和行动建议。

## 用户与问题

### U1 远程团队负责人

周一阅读团队层面的变化，选出一个需要跟进的问题。

[E004](#e004)：目标用户：远程团队负责人、项目经理、People Ops 伙伴。；[E009](#e009)：- 周一团队负责人查看趋势、风险主题和建议行动。

### U2 团队成员

在短问卷中表达协作阻碍，同时知道哪些数据会被负责人看见。

[E007](#e007)：- 团队成员担心反馈被追溯到个人，因此不愿意说真实问题。；[E008](#e008)：- 每周五自动发起 3 分钟健康度脉冲问卷。

- P1：负责人发现协作阻碍太晚，已有反馈也难以转成下一步行动。（U1）
  [E005](#e005)：- 团队负责人通常只能在项目延期后才发现协作问题。；[E006](#e006)：- 现有问卷工具能收集反馈，但很难自动沉淀趋势和行动建议。
- P2：成员担心回答被追溯，反馈可能失真。（U2）
  [E007](#e007)：- 团队成员担心反馈被追溯到个人，因此不愿意说真实问题。

## 产品功能总览

TeamPulse 团队健康度助手产品有每周反馈采集、团队趋势与风险复核、改进行动跟进、连续下降提醒功能提案。

| 功能 | 版本范围 | 优先级 | 取舍依据 |
|---|---|---|---|
| F1 每周反馈采集 | mvp | must | 没有可信输入就没有趋势；先降低填写和隐私理解成本，再考虑复杂分析。 |
| F2 团队趋势与风险复核 | mvp | must | 负责人需要判断变化是否值得行动；按人数阈值抑制展示先于更细颗粒度洞察。 |
| F3 改进行动跟进 | mvp | must | 趋势必须连接下一步；先让人选择行动，避免把生成建议当成团队共识。 |
| F4 连续下降提醒 | later | should | 自动提醒需要稳定的可比数据，先验证周报是否被使用，再评估提醒噪声。 |

## 功能范围与验收标准

### F1 每周反馈采集

对应问题：P2

前置依赖：无

依据：[E007](#e007)：- 团队成员担心反馈被追溯到个人，因此不愿意说真实问题。；[E008](#e008)：- 每周五自动发起 3 分钟健康度脉冲问卷。；假设 A1

- **填写前说明**：明确数据用途、保留期和可见范围，默认不收集姓名、部门细分或自由文本。
- **单团队问卷**：团队负责人设置一个周五开放的问卷，成员可跳过问题并在提交前检查。

**F1-S1** 作为团队成员，我希望用不超过三分钟的问卷提交反馈，以便表达问题并理解可见范围。

- 给定：单团队本周问卷开放；当：成员填写并提交一次；则：显示收到反馈；公开页面和负责人页面都不返回个人回答。
- 给定：必答项未完成；当：成员点击提交；则：明确指出缺项，已填答案保留且允许退出。
### F2 团队趋势与风险复核

对应问题：P1

前置依赖：F1

依据：[E009](#e009)：- 周一团队负责人查看趋势、风险主题和建议行动。；[E011](#e011)：- MVP 只支持单团队，不做复杂组织架构。；[E007](#e007)：- 团队成员担心反馈被追溯到个人，因此不愿意说真实问题。；假设 A1

- **聚合报告**：只展示满足阈值的团队周度维度分布和可比周趋势，无逐人详情。
- **复核入口**：负责人将某个维度标记为需要讨论；只记录团队问题，不推断个人状态。

**F2-S1** 作为远程团队负责人，我希望看到有足够样本支持的周度变化，以便在项目延期前发现需要讨论的阻碍。

- 给定：本周仅有四份有效回答；当：负责人打开报告；则：不返回维度分布，仅说明样本不足；导出与接口采用相同抑制规则。
- 给定：本周和上周各有至少五份有效回答；当：负责人比较趋势；则：展示两周样本量与维度分布，并说明它们是聚合反馈而非个人绩效。
### F3 改进行动跟进

对应问题：P1

前置依赖：F2

依据：[E006](#e006)：- 现有问卷工具能收集反馈，但很难自动沉淀趋势和行动建议。；[E016](#e016)：- 4 周内至少创建 1 条改进行动。

- **行动记录**：从报告创建一条行动，写清责任角色、检查条件与复盘节点。
- **复盘记录**：负责人记录已做什么、观察到什么，允许结论为无改善。

**F3-S1** 作为远程团队负责人，我希望从一个反馈主题建立可复盘的行动，以便验证是否减少了具体协作阻碍。

- 给定：负责人已标记一个团队问题；当：保存包含责任角色与复盘条件的行动；则：报告保留行动链接和待复盘状态。
- 给定：行动尚未填写复盘条件；当：点击保存；则：提示补充验收依据，不自动宣称问题已解决。
### F4 连续下降提醒

对应问题：P1

前置依赖：F2

依据：[E010](#e010)：- 当某个维度连续两周下降时，系统提醒负责人安排跟进。；假设 A2

- **下降规则**：只对连续三周可比样本中的连续两次下降生成站内候选提醒。
- **去重与关闭**：同一维度同一周最多一条提醒，负责人可标记无需跟进并说明原因。

**F4-S1** 作为远程团队负责人，我希望在连续下降时收到可复核的提醒，以便减少遗漏但避免被无效警报打扰。

- 给定：某维度连续三周均满足样本阈值且连续两次下降；当：执行规则检查两次；则：只产生一条带三周聚合依据的站内提醒。
- 给定：任一周样本不足；当：执行规则检查；则：不产生下降提醒，保留数据不足状态。

## 约束响应

- [E011](#e011) / honored：仅单团队数据域；组织树和跨团队比较列入排除项。关联功能：F1, F2。
- [E012](#e012) / honored：本文件为虚构方案演练，不包含真实问卷或真实使用效果。关联功能：范围约束。
- [E013](#e013) / honored：使用站内入口和可复制链接，暂不实现聊天工具接入。关联功能：F1, F4。

## 暂不纳入

- 复杂组织架构和跨团队排名：首版只证明一个团队的反馈到行动闭环，也避免额外细分带来的隐私风险。[E011](#e011)：- MVP 只支持单团队，不做复杂组织架构。
- 真实聊天工具接入：当前约束不要求，先验证主要工作流。[E013](#e013)：- 不要求接入真实聊天工具。
- AI 自动执行团队行动：建议可能误判团队情境，先由负责人选择和复盘。[E006](#e006)：- 现有问卷工具能收集反馈，但很难自动沉淀趋势和行动建议。；假设 A2

## 假设与验证

- **A1** / high：五份有效回答作为最小聚合阈值是待测试设计，不能保证完全匿名；首版不提供自由文本和组织细分。
  验证方法：用不同团队规模的虚构回答检查小样本和差分重识别风险；再由隐私负责人审阅阈值、留存和访问规则。
- **A2** / medium：三周数据中的连续两次下降值得形成候选提醒。
  验证方法：在历史模拟数据中统计提醒量和重复量，试用时由负责人逐条标记是否有行动价值。

## 指标与护栏

### 首周问卷完成率 / outcome

首周提交有效问卷的人数 / 首周受邀参与人数。

基线：未测量
目标：达到 70%（provided）
采集方式：以受邀总数和去重后的提交数计算，仅保存团队级汇总。

[E014](#e014)：- 试用团队首周问卷完成率达到 70%。

### 行动创建 / outcome

团队试用四周内从报告创建的改进行动数，不作为改善效果的替代指标。

基线：未测量
目标：4 周内至少创建 1 条改进行动。（provided）
采集方式：记录 action\_created 事件，复盘另行记录是否改善。

[E016](#e016)：- 4 周内至少创建 1 条改进行动。

### 小样本泄露 / guardrail

未达到最小样本量的报告、导出或接口返回了维度分布的次数。

基线：未测量
目标：验收样例中为 0（proposed）
采集方式：用四人、五人和缺失周的虚构样例覆盖页面、接口与导出。

[E007](#e007)：- 团队成员担心反馈被追溯到个人，因此不愿意说真实问题。；假设 A1

## 迭代路径

阶段按验收条件推进，日期和投入需另行估算。

### 先验证反馈到行动

包含功能：F1, F2, F3

- 虚构四人和五人样本的权限、抑制与导出验收通过。
- 负责人能够从报告创建行动，并记录一次无改善的复盘。
- 试用前明确受邀人数、去重机制与数据留存规则。
### 再验证提醒价值

包含功能：F4

- 已有三周可比较数据。
- 提醒去重和样本不足用例通过，试用负责人能标记每条提醒的行动价值。

## 评审问题

- 谁负责创建和维护受邀人数，如何降低重复回答而不向负责人暴露身份？
- 在更换成员或组织调整后，哪些周度数据仍可比较？
- 问卷答案的保留期限、删除方式和访问权限由谁审核？

引用和依赖检查通过。待验证假设 2 项，未决约束 0 项。

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
