# 开源复用与选择

本项目在真正需要可靠性的边界复用成熟组件，界面采用原生 HTML 语义和少量 JavaScript，保持评审页可离线分享。

| 项目 | 采用方式 | 选择原因与边界 |
|---|---|---|
| [python-jsonschema](https://github.com/python-jsonschema/jsonschema) | Python 运行依赖，MIT | 实际执行 Draft 2020-12 输入、计划与结果契约；结构检查不做语义评判 |
| [Playwright](https://github.com/microsoft/playwright) | 开发验收，Apache-2.0 | 在真实浏览器检查筛选、来源往返、下载和窄屏；不是产品运行依赖 |
| [axe-core](https://github.com/dequelabs/axe-core) | 开发验收，MPL-2.0 | 对四个评审视图执行自动可访问性规则；不能替代人工和读屏器测试 |
| [Impeccable](https://impeccable.style) | 设计工作流，未打包进产品 | 检查留白、层级、状态和响应式；本机机械检测器依赖不全，不能声称其完整检查通过 |

上游项目页面于 2026-09-18 核对。实际 Node 开发依赖锁定在 package-lock.json，Python 的支持范围在 requirements-plugin.txt。没有复制参考图素材，也没有将其他作品集仓库的数据库或模型依赖标成这个项目已接入。

为何不引入 React 和大型组件库：当前任务是读取一个已生成方案、查依据并导出，没有跨设备编辑和协作状态。原生 details、button、select 与独立文档足以完成任务。若未来需要在线协作，再以真实需求决定架构。
