# 0.3 版验收记录

日期：2026-09-18。范围为 PRD 工具、插件技能和本地评审界面，不含案例中业务产品的开发或客户效果。

## 原问题

输入汽车配件发货复核需求时，旧代码仍输出需求澄清、竞品研究、PRD 生成等工具自身模块，并按顺序分配优先级、固定安排四周里程碑。旧的“非 HR”测试只检查不出现 People Ops，没有证明功能服务实际用户任务。

## 实际完成的检查

| 检查 | 结果与范围 |
|---|---|
| Python 契约与行为 | 28 项通过，包括无计划不编造 backlog、跨行业原文保留、精确引用、过期方案、角色关系、循环依赖、MVP 前置条件、自然段约束、指标来源、迭代次序、CSV 异常、HTML 注入和已有目录保护 |
| 显式完整案例 | TeamPulse、FitCheck 的计划均由插件实际校验并生成 Markdown、JSON、backlog 和 HTML；不是关键词选模板 |
| 技能独立试跑 | 新上下文读取真实格式的虚构汽车售后自然段，形成 4 个 MVP 功能、1 个后续候选、22 条拟定业务验收条件和 7 个假设；未执行这 22 条业务产品条件 |
| 浏览器 | 本机实际 Chrome，1440×1000 和 390×844，测试筛选、空搜索、展开、来源往返、下载、空计划和攻击字符串；无页面脚本错误、无横向溢出 |
| 下载一致性 | 浏览器下载的 Markdown 与 result.markdown 逐字一致；backlog 下载与结果结构一致 |
| 自动可访问性 | 两个宽度下四个导航视图，axe-core 的 WCAG 2 A/AA 与 2.1 AA 标签规则均未报告违规；不等于完整可访问性认证 |
| 插件与技能包装 | plugin-creator 校验器、skill-creator 校验器通过 |
| 公开仓库审计 | 必需文件、示例、体积与敏感模式检查通过；修正输入 SHA-256 被误报为电话号码的问题，只排除特定指纹字段和指纹行 |

## 独立测试推动的修复

自然段中的约束最初无法写入 constraint_responses。本轮允许为任意 brief 记录登记约束响应，并继续强制覆盖所有有标签的约束。方案完成后 result.summary 使用方案中的产品名、角色和内容，analysis.summary 保留原始机械提取。渲染器不再重复添加中文句号。

视觉审计发现引用跳转后返回入口不可见。修复将返回按钮移动到当前引用旁；后续浏览器检查在点击前确认其完整位于视口内，Tab 可到达，Enter 返回原控制、滚动位置、MVP 筛选与展开状态。E007、E016 在两种宽度均通过。独立评审对这一修复给出 F1 resolved、针对修复项的 ship，不扩大为重新覆盖所有页面的结论。

Impeccable 检测器仅运行一次。本机缺少 HTML/CSS 解析模块，降级正则结果为空；不据此宣称完整检测通过。最终设计记录见 DESIGN.md。

## 复现

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/build_examples.py --check
python scripts/plugin_run.py --input examples/fitcheck-input.json --plan examples/fitcheck-plan.json --output-dir output/acceptance-fitcheck
npm ci
npx playwright install chromium
npm run test:review
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

浏览器脚本重新生成测试页面，保存 output/browser-check/acceptance.json 和忽略目录中的截图。CI 上传这些浏览器证据。已有 Chrome 可设置 BROWSER_CHANNEL=chrome；PYTHON 可指定独立环境。

未验证：真实 PM 的任务效率、引用对决策的语义支持、行业知识正确性、客户收益、生产多人协作及任意新领域的普遍适用性。没有把这些项目计作通过。
