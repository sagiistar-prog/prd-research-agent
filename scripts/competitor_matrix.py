#!/usr/bin/env python3
"""Build a Markdown competitor matrix from a fictional CSV file."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List


REQUIRED_COLUMNS = [
    "name",
    "positioning",
    "strengths",
    "weaknesses",
    "pricing",
    "target_user",
]


def load_competitors(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing competitor columns: {', '.join(missing)}")
        return [{key: (row.get(key) or "").strip() for key in REQUIRED_COLUMNS} for row in reader]


def markdown_table(rows: Iterable[Dict[str, str]]) -> str:
    lines = [
        "| 竞品 | 定位 | 优势 | 短板 | 定价 | 目标用户 |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {name} | {positioning} | {strengths} | {weaknesses} | {pricing} | {target_user} |".format(
                **{key: row.get(key, "").replace("|", "/") for key in REQUIRED_COLUMNS}
            )
        )
    return "\n".join(lines)


def opportunity_notes(rows: List[Dict[str, str]]) -> str:
    if not rows:
        return "暂无竞品数据。"

    weaknesses = [row["weaknesses"] for row in rows if row.get("weaknesses")]
    if not weaknesses:
        return "竞品短板信息不足，建议补充定性访谈或公开资料。"

    notes = [
        "- 机会 1：把周期性信号采集和行动建议连接起来，避免只停留在看板展示。",
        "- 机会 2：把匿名、聚合和可解释规则放进 MVP，提升用户信任。",
        "- 机会 3：优先服务轻量团队，减少复杂配置带来的采用门槛。",
    ]
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
