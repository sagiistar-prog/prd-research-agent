# PRD Research Agent


[产品案例与指标](docs/product-case.md) | [能力证据](docs/capability-evidence.json) | [验收与边界](docs/validation.md)

## 面试官 30 秒版

把模糊需求整理成可复核的 PRD 初稿。先让目标用户、约束和待验证假设可见，再讨论功能。跨领域输入不应混入团队健康度的固定结论。

当前可验证能力：**offline_template**。确定性模板草稿；不调用模型，不执行联网调研。 优先级与功能建议需要人工确认，不能作为真实市场结论。

[插件使用与产品取舍](docs/plugin.md) · [输入示例](examples/plugin-input.json) · [输入契约](schemas/input.schema.json) · [维护记录](CHANGELOG.md)

```bash
python -m pip install -r requirements-plugin.txt
python scripts/plugin_run.py --input examples/plugin-input.json
```

## 原有工作流与详细说明


## 面试官 30 秒版

PRD Research Agent 是一个面向产品经理的 AI Agent 项目样例：它从一句简单需求出发，按“澄清需求 → 用户场景 → 市场与竞品 → 功能范围 → 优先级 → 用户故事 → 验收标准 → PRD 初稿”的链路生成结构化产物。项目不是只演示脚本，而是把产品经理的分析方法、文档框架、安全演示、公开仓库审计和可复现 demo 打包成一个独立 GitHub 项目。

Safe Demo 使用完全虚构数据，可离线运行：

```bash
python scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

Windows 兼容命令：

```powershell
py -3 scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

## 项目定位

这个项目用于展示一个产品经理如何把模糊需求推进到开发可读的 PRD 初稿。它强调三件事：

- 需求结构化：把口语化输入拆成目标用户、场景、问题、假设、约束和成功指标。
- 产品判断：结合竞品、版本范围、优先级和风险，说明为什么先做这些功能。
- 交付可执行：输出功能树、子功能、用户故事、验收标准和里程碑，方便研发、设计、测试继续推进。

## 输出格式

生成的 PRD 会使用面向研发沟通的功能树表达，例如：

> TeamPulse 团队健康度助手产品有健康度采集/团队洞察/风险提醒/行动建议/报告导出功能。

每个一级功能下面会继续列出子功能、优先级、用户故事和验收标准。真实业务里可以把这个结构扩展到权限、埋点、非功能需求、上线策略和灰度方案。

## 核心能力

- 需求扩展和结构化
- 需求澄清问题生成
- 用户场景与任务分析
- 市场调研与竞品矩阵
- 功能范围定义
- MoSCoW 优先级判断
- 用户故事和验收标准生成
- PRD 初稿生成
- 面向公开作品集的安全审计

## 项目结构

```text
README.md
AGENTS.md
docs/
skills/prd-research-agent/
scripts/
configs/
examples/
```

## 快速开始

1. 安装 Python 3.10+。
2. 可选安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行 Safe Demo：

```bash
python scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

Windows 兼容命令：

```powershell
py -3 scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

4. 运行作品集审计：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

## 命令说明

```bash
python scripts/generate_prd.py \
  --input examples/sample_requirement.md \
  --competitors examples/sample_competitors.csv \
  --output examples/generated_prd.md \
  --rules configs/prd_rules.yaml \
  --dry-run
```

Windows 兼容命令：

```powershell
py -3 scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

- `--input`：简单需求输入，支持 Markdown。
- `--competitors`：虚构竞品 CSV，用于生成竞品分析。
- `--output`：PRD 初稿输出路径。
- `--rules`：PRD 生成规则配置。
- `--dry-run`：安全演示模式，只使用本地规则和确定性模板，不调用外部服务，仍会写出示例 PRD。

## 安全边界

- 示例数据全部为虚构数据。
- 不包含真实公司、客户、候选人、内部项目或私有路径。
- 审计脚本会检查敏感信息模式、大文件、示例数据风险和 GitHub 公开性。
- 公开展示前建议重新运行 Safe Demo 和审计脚本。

## 文档入口

- [案例研究](docs/case-study.md)
- [工作流程](docs/workflow.md)
- [PRD 方法论](docs/prd-methodology.md)
- [安全演示](docs/safe-demo.md)
- [面试总结](docs/interview-summary.md)

## License

MIT
