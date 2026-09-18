# 0.3.0 / 2026-09-18

- 从模板功能生成改为证据整理、宿主规划和可追溯评审。
- 增加计划 JSON 契约、引用与约束检查、依赖和发布次序校验。
- 增加离线评审页、MVP 筛选、来源往返和一致导出。
- 增加 TeamPulse 完整计划与独立汽车售后案例。
- 输出协议升为 2.0；无计划时返回 needs_plan，旧 CLI 仍写资料梳理。

# Maintenance log

## 0.2.0 — 2026-09-17

- Added a versioned Codex plugin manifest with the existing Skill.
- Added validated JSON input/output, a fictional input fixture and an explicit artifact export path.
- Documented the actual offline capability and its limitations.
- Added executable contract and regression checks; see `tests/`.
- Product decision: 先让目标用户、约束和待验证假设可见，再讨论功能。跨领域输入不应混入团队健康度的固定结论。

The version labels a repository iteration, not a hosted product launch or a marketplace release.

## 2026-09-17 Product reliability release

需求到可评审草稿。补齐产品案例、能力证据、指标契约、开源取舍与持续检查。验证范围和未验收项见 docs/validation.md。
