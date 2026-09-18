#!/usr/bin/env python3
"""Build a Markdown competitor matrix from a fictional CSV file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List
from requirements_analysis import load_competitors
from prd_renderer import md


REQUIRED_COLUMNS = [
    "name",
    "positioning",
    "strengths",
    "weaknesses",
    "pricing",
    "target_user",
]


def markdown_table(rows: Iterable[Dict[str, str]]) -> str:
    lines = [
        "| 竞品 | 定位 | 优势 | 短板 | 定价 | 目标用户 |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {name} | {positioning} | {strengths} | {weaknesses} | {pricing} | {target_user} |".format(
                **{key: md(row.get(key, "")) for key in REQUIRED_COLUMNS}
            )
        )
    return "\n".join(lines)


def opportunity_notes(rows: List[Dict[str, str]]) -> str:
    if not rows:
        return "暂无竞品数据。"

    weaknesses = [row["weaknesses"] for row in rows if row.get("weaknesses")]
    if not weaknesses:
        return "竞品短板信息不足，建议补充定性访谈或公开资料。"

    notes = [f"- 输入样本 {md(row.get('name', '未命名'))} 的短板：{md(row['weaknesses'])}。待验证：该问题是否影响目标用户的核心任务；未独立核实。" for row in rows if row.get("weaknesses")]
    return "\n".join(notes)


def build_matrix(path: Path) -> str:
    competitors = load_competitors(path)
    return "\n\n".join(
        [
            "## 竞品矩阵",
            markdown_table(competitors),
            "## 机会洞察",
            opportunity_notes(competitors),
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Markdown competitor matrix.")
    parser.add_argument("--input", required=True, help="Path to competitor CSV.")
    parser.add_argument("--output", help="Optional Markdown output path. Prints to stdout when omitted.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    content = build_matrix(Path(args.input))

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content + "\n", encoding="utf-8")
        print(f"Generated competitor matrix: {output}")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
