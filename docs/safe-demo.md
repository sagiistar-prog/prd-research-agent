# 离线演示

仓库示例全部为虚构资料，不含真实用户反馈或业务结果。安装 Python 依赖后，演示无需网络或模型密钥。

保留原命令：

```bash
python scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

它写出资料梳理。要生成完整 PRD，显式加 `--plan examples/team-pulse-plan.json`。交互版本使用 README 中的 plugin_run 命令，输出到新的 output 子目录。

不要将“成功生成”解释为已经验证商业价值。真实产品的实现与本地 PRD 工具的技术验收是两件不同的工作。
