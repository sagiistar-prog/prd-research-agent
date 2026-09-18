# 插件契约与使用

根目录 `.codex-plugin/plugin.json` 定义版本 0.3.0 插件，`skills/prd-research-agent/SKILL.md` 是宿主使用入口。Python CLI 可以独立使用；安装为插件后仍由宿主承担语言理解和产品规划，不依赖脚本中的远程模型调用。

## 输入与两种结果

`requirement_markdown` 必填，最多 30000 字符；`competitors` 可选，最多 30 条；`product_plan` 可内嵌，或使用独立 `--plan` 文件，两者不可同时指定。命令行输入文件与独立方案各不超过 1 MB。

没有方案时返回 `phase: needs_plan`，`product_plan` 和 `checks` 为 null，backlog 为空。有合法方案时返回 `phase: review_ready`。两者都是成功结果，顶层 `schema_version` 为 `2.0`，`mode` 为 `evidence_to_prd`。

`analysis.summary` 始终是基于显式标签的原始提取，空字段不等于原文没有信息。`result.summary` 在有方案时取自方案，`summary_source` 为 `product_plan`，否则为 `input_extraction`。所有原文完整保存在 `analysis.requirement_markdown`。

## 方案与引用

[方案 schema](../schemas/plan.schema.json) 版本 1.0，要求目标、角色、问题、功能、约束响应、假设、指标、排除项、评审问题和迭代阶段。产品判断必须有原文引用或登记假设；引用是 `id` 和精确 `quote`。短引文比复制整段更利于评审。

`analysis_id` 绑定原始需求及竞品记录，包括顺序和空白变化。它检测输入改变，不是签名、来源真实性证明或防恶意篡改机制。换输入应重新考虑方案，不能只改哈希。

有标题的约束必须逐条响应；自然段约束可引用任意 brief 记录，一个记录中的多项约束共用一条响应。代码不自动理解隐含约束，完整性须由宿主和评审者检查。`honored` 表示设计响应已给出，不是实施完成。

## 错误和本地文件

非法输入返回 JSON 错误和退出码 2，不返回堆栈或私有输入值。`--output-dir` 只允许仓库 `output/` 下的新目录，不覆盖旧结果。成功写出 result.json、result.md、backlog.json 和 review.html。共享目录或评审页就会共享其中的原始需求，请在公开演示中使用仓库的虚构样例。

从 0.2 迁移时，消费者需要处理新的 phase、summary_source 和可空方案。没有自动从旧模板结果迁移为产品计划的能力。
