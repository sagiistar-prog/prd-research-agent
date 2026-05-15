#!/usr/bin/env python3
"""Generate a deterministic PRD draft from a short requirement brief."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import textwrap
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


COMPETITOR_COLUMNS = [
    "name",
    "positioning",
    "strengths",
    "weaknesses",
    "pricing",
    "target_user",
]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8-sig")


def strip_quotes(value: str) -> str:
    return value.strip().strip('"').strip("'")


def parse_simple_yaml(text: str) -> Dict[str, object]:
    """Small fallback parser for the simple config shape used by this demo."""

    result: Dict[str, object] = {}
    current_list: str | None = None

    for raw_line in text.splitlines():
        line_without_comment = raw_line.split("#", 1)[0].rstrip()
        if not line_without_comment.strip():
            continue

        if not raw_line.startswith((" ", "\t")) and ":" in line_without_comment:
            key, value = line_without_comment.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not value:
                result[key] = []
                current_list = key
            elif value.startswith("[") and value.endswith("]"):
                result[key] = [strip_quotes(item) for item in value[1:-1].split(",") if item.strip()]
                current_list = None
            else:
                result[key] = strip_quotes(value)
                current_list = None
            continue

        if current_list and line_without_comment.lstrip().startswith("- "):
            item = strip_quotes(line_without_comment.lstrip()[2:])
            if isinstance(result.get(current_list), list):
                result[current_list].append(item)  # type: ignore[union-attr]

    return result


def load_rules(path: Path | None) -> Dict[str, object]:
    if not path:
        return {}

    text = read_text(path)
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        return parse_simple_yaml(text)


def extract_label(markdown: str, labels: Sequence[str]) -> str:
    for label in labels:
        pattern = rf"^{re.escape(label)}\s*[:：]\s*(.+?)\s*$"
        match = re.search(pattern, markdown, flags=re.MULTILINE)
        if match:
            return match.group(1).strip()
    return ""


def collect_bullets_after(markdown: str, heading: str) -> List[str]:
    pattern = rf"^{re.escape(heading)}\s*[:：]?\s*$"
    match = re.search(pattern, markdown, flags=re.MULTILINE)
    if not match:
        return []

    tail = markdown[match.end() :].splitlines()
    bullets: List[str] = []
    for line in tail:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^[#A-Za-z0-9\u4e00-\u9fff].*[:：]\s*$", stripped) and bullets:
            break
        if stripped.startswith(("- ", "* ")):
            bullets.append(stripped[2:].strip())
        elif bullets:
            break
    return bullets


def first_heading(markdown: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def infer_product_name(markdown: str) -> str:
    explicit = extract_label(markdown, ["产品名称", "产品名", "Product"])
    if explicit:
        return explicit

    heading = first_heading(markdown)
    if "：" in heading:
        return heading.split("：", 1)[1].strip()
    if ":" in heading:
        return heading.split(":", 1)[1].strip()
    return heading or "示例产品"


def requirement_summary(markdown: str) -> Dict[str, object]:
    return {
        "product_name": infer_product_name(markdown),
        "one_liner": extract_label(markdown, ["一句话需求", "需求", "背景"]),
        "target_users": extract_label(markdown, ["目标用户", "用户"]),
        "problems": collect_bullets_after(markdown, "当前问题"),
        "scenarios": collect_bullets_after(markdown, "核心场景"),
        "constraints": collect_bullets_after(markdown, "约束"),
        "metrics": collect_bullets_after(markdown, "成功指标"),
    }


def load_competitors(path: Path | None) -> List[Dict[str, str]]:
    if not path:
        return []
    if not path.exists():
        raise FileNotFoundError(f"Competitor file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in COMPETITOR_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing competitor columns: {', '.join(missing)}")
        return [{key: (row.get(key) or "").strip() for key in COMPETITOR_COLUMNS} for row in reader]


def detect_domain(summary: Dict[str, object]) -> str:
    text = " ".join(
        [
            str(summary.get("product_name", "")),
            str(summary.get("one_liner", "")),
            " ".join(summary.get("problems", []) or []),
            " ".join(summary.get("scenarios", []) or []),
        ]
    )
    if any(keyword in text for keyword in ["健康度", "远程团队", "团队", "协作"]):
        return "team_health"
    return "generic_product"


def feature_tree(summary: Dict[str, object], rules: Dict[str, object]) -> Dict[str, List[str]]:
    domain = detect_domain(summary)
    if domain == "team_health":
        return {
            "健康度采集": ["脉冲问卷模板", "每周自动发起", "匿名回答保护", "完成率监控"],
            "团队洞察": ["维度趋势图", "主题聚类摘要", "团队分组筛选", "历史对比"],
            "风险提醒": ["连续下降识别", "阈值提醒", "风险原因解释", "负责人待办"],
            "行动建议": ["建议库匹配", "行动项创建", "跟进状态更新", "复盘记录"],
            "报告导出": ["Markdown 周报", "关键指标摘要", "风险与行动清单", "分享权限控制"],
        }

    configured = rules.get("default_function_modules")
    if isinstance(configured, list) and configured:
        return {
            str(name): ["输入解析", "结构化摘要", "人工确认点", "输出记录"]
            for name in configured[:6]
        }

    return {
        "需求澄清": ["背景提取", "问题拆解", "假设识别", "待确认问题"],
        "用户场景": ["用户分层", "任务路径", "痛点分析", "期望结果"],
        "功能定义": ["功能树", "子功能", "非目标", "依赖项"],
        "优先级判断": ["MVP 标记", "取舍说明", "风险提示", "版本建议"],
        "PRD 生成": ["用户故事", "验收标准", "指标", "里程碑"],
    }


def markdown_list(items: Iterable[str], fallback: str = "暂无明确输入，建议补充。") -> str:
    values = [item for item in items if item]
    if not values:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in values)


def competitor_table(competitors: List[Dict[str, str]]) -> str:
    if not competitors:
        return "未提供竞品数据；建议补充 3 到 5 个竞品进行定位对比。"

    lines = [
        "| 竞品 | 定位 | 优势 | 短板 | 定价 | 目标用户 |",
        "|---|---|---|---|---|---|",
    ]
    for row in competitors:
        clean = {key: row.get(key, "").replace("|", "/") for key in COMPETITOR_COLUMNS}
        lines.append(
            "| {name} | {positioning} | {strengths} | {weaknesses} | {pricing} | {target_user} |".format(
                **clean
            )
        )
    return "\n".join(lines)


def competitor_insights(competitors: List[Dict[str, str]]) -> str:
    if not competitors:
        return "- 需要补充竞品样本后再判断差异化机会。"

    return "\n".join(
        [
            "- 多数竞品只覆盖反馈收集或看板展示，机会在于把信号、解释和行动闭环连起来。",
            "- 小团队采用门槛敏感，因此 MVP 应减少配置复杂度。",
            "- 匿名和聚合规则会直接影响反馈真实性，应作为基础能力而不是后置增强。",
        ]
    )


def clarification_questions(summary: Dict[str, object]) -> List[str]:
    product_name = summary["product_name"]
    return [
        f"{product_name} 的首个付费或试用用户是团队负责人、People Ops，还是项目经理？",
        "匿名反馈的最小展示人数是多少，低于阈值时是否隐藏结果？",
        "MVP 是否需要支持自定义问卷维度，还是先使用固定模板？",
        "风险提醒应通过产品内通知、邮件，还是后续再接入协作工具？",
        "成功指标的观察周期是首周、四周，还是一个季度？",
    ]


def priority_rows(features: Dict[str, List[str]]) -> str:
    rows = [
        "| 功能 | 优先级 | 判断理由 | MVP 处理 |",
        "|---|---|---|---|",
    ]
    labels = ["Must", "Must", "Must", "Should", "Could", "Could"]
    reasons = [
        "直接支撑核心价值闭环",
        "帮助用户理解问题并形成信任",
        "让风险在延期前被发现",
        "把洞察转成可执行改进",
        "提升传播和复盘效率",
        "增强长期可配置性",
    ]
    for index, name in enumerate(features):
        label = labels[index] if index < len(labels) else "Could"
        reason = reasons[index] if index < len(reasons) else "增强完整体验"
        treatment = "纳入 MVP" if label in {"Must", "Should"} else "放入后续版本评估"
        rows.append(f"| {name} | {label} | {reason} | {treatment} |")
    rows.append("| 复杂组织架构 | Won't | 会显著增加配置和权限复杂度 | 当前版本不做 |")
    return "\n".join(rows)


def user_stories(features: Dict[str, List[str]], summary: Dict[str, object]) -> str:
    target_users = summary.get("target_users") or "目标用户"
    lines: List[str] = []
    for index, (feature, subfeatures) in enumerate(features.items(), start=1):
        first_subfeature = subfeatures[0] if subfeatures else "核心能力"
        lines.extend(
            [
                f"### Story {index}: {feature}",
                "",
                f"作为{target_users}，我希望使用{feature}，以便在关键场景中更快完成判断和行动。",
                "",
                "验收标准：",
                "",
                f"- Given 用户已进入产品并具备访问权限，When 用户使用{first_subfeature}，Then 系统应展示清晰的结果和下一步动作。",
                f"- Given 输入数据不足，When 用户查看{feature}，Then 系统应提示缺失信息并给出补充建议。",
                f"- Given 用户完成{feature}相关操作，When 页面刷新或重新打开，Then 系统应保留最新状态。",
                "",
            ]
        )
    return "\n".join(lines).strip()


def scenario_table(summary: Dict[str, object]) -> str:
    scenarios = summary.get("scenarios", []) or []
    if not scenarios:
        scenarios = ["用户提交需求", "负责人查看分析", "团队确认 MVP 范围"]

    rows = [
        "| 场景 | 触发 | 用户目标 | 产品机会 |",
        "|---|---|---|---|",
    ]
    for scenario in scenarios:
        rows.append(f"| {scenario} | 固定周期或风险信号出现 | 快速理解状态并决定下一步 | 提供结构化洞察、提醒和行动建议 |")
    return "\n".join(rows)


def build_prd(
    requirement_markdown: str,
    competitors: List[Dict[str, str]],
    rules: Dict[str, object],
    dry_run: bool,
) -> str:
    summary = requirement_summary(requirement_markdown)
    product_name = str(summary["product_name"])
    features = feature_tree(summary, rules)
    feature_names = list(features.keys())
    feature_sentence = f"{product_name}产品有{'/'.join(feature_names)}功能。"
    generated_on = dt.date.today().isoformat()
    mode = "Safe Demo / dry-run / offline deterministic" if dry_run else "local generation"

    feature_sections = []
    for name, subfeatures in features.items():
        feature_sections.append(
            "\n".join(
                [
                    f"### {name}",
                    "",
                    markdown_list(subfeatures, fallback="待补充子功能。"),
                ]
            )
        )

    content = f"""
    # {product_name} PRD 初稿

    > 生成模式：{mode}
    > 生成日期：{generated_on}

    ## 1. 需求摘要

    - 产品名称：{product_name}
    - 一句话需求：{summary.get("one_liner") or "暂无明确一句话需求，建议补充。"}
    - 目标用户：{summary.get("target_users") or "暂无明确目标用户，建议补充。"}

    当前问题：

    {markdown_list(summary.get("problems", []) or [])}

    成功指标：

    {markdown_list(summary.get("metrics", []) or [])}

    ## 2. 需求澄清问题

    {markdown_list(clarification_questions(summary))}

    ## 3. 用户与场景

    {scenario_table(summary)}

    ## 4. 市场与竞品分析

    {competitor_table(competitors)}

    机会洞察：

    {competitor_insights(competitors)}

    ## 5. 产品功能总览

    {feature_sentence}

    ## 6. 功能范围与子功能

    {chr(10).join(feature_sections)}

    ## 7. 优先级与版本范围

    {priority_rows(features)}

    ## 8. 用户故事与验收标准

    {user_stories(features, summary)}

    ## 9. 数据与风控

    - 匿名反馈必须以团队聚合方式展示，避免个人可识别信息进入公开 demo。
    - 当样本量不足时，系统应隐藏趋势判断并提示继续收集。
    - 风险提醒需要解释原因，避免让用户把分数误读成个人评价。
    - 当前版本不接入真实账号、聊天记录或私有系统。

    ## 10. 里程碑

    | 阶段 | 目标 | 交付物 |
    |---|---|---|
    | Week 1 | 验证问题和首个用户场景 | 访谈提纲、需求澄清清单 |
    | Week 2 | 完成 MVP 范围和原型 | 功能树、低保真流程、指标定义 |
    | Week 3 | 进入开发准备 | 用户故事、验收标准、埋点草案 |
    | Week 4 | 小范围试用 | 试用报告、问题清单、下版建议 |

    ## 11. 非目标

    - 不做复杂组织架构。
    - 不做个人绩效评分。
    - 不接入真实聊天工具。
    - 不输出未经确认的真实市场结论。

    ## 12. 后续开放问题

    - 是否需要团队负责人和成员看到不同的信息层级？
    - 是否允许管理员自定义健康度维度？
    - 风险提醒的频率和打扰阈值如何设置？
    - 报告导出的主要使用场景是周会、复盘，还是向上汇报？
    """

    return textwrap.dedent(content).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a PRD draft from a requirement brief.")
    parser.add_argument("--input", required=True, help="Path to requirement Markdown.")
    parser.add_argument("--competitors", help="Path to fictional competitor CSV.")
    parser.add_argument("--output", required=True, help="Path to generated PRD Markdown.")
    parser.add_argument("--rules", help="Path to PRD rules YAML.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use safe offline deterministic generation. Still writes the output file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    rules_path = Path(args.rules) if args.rules else None
    competitors_path = Path(args.competitors) if args.competitors else None

    requirement_markdown = read_text(input_path)
    rules = load_rules(rules_path)
    competitors = load_competitors(competitors_path)
    prd = build_prd(requirement_markdown, competitors, rules, dry_run=args.dry_run)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prd, encoding="utf-8")

    if args.dry_run:
        print("Safe Demo dry-run complete: no external services were called.")
    print(f"Generated PRD: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
