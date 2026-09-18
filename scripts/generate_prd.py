#!/usr/bin/env python3
"""Assess a brief, or validate and render an explicitly authored product plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from requirements_analysis import assess, load_competitors, validate_input, validate_plan
from prd_renderer import render


def requirement_summary(markdown: str) -> dict:
    return assess(markdown)["summary"]


def build_prd(markdown: str, competitors: list[dict], rules=None, dry_run=True, plan=None) -> str:
    validate_input({"requirement_markdown": markdown, "competitors": competitors})
    analysis = assess(markdown, competitors)
    return render(analysis, plan, validate_plan(plan, analysis) if plan is not None else None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--competitors", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan", type=Path, help="Explicit product plan conforming to schemas/plan.schema.json")
    parser.add_argument("--rules", type=Path, help="Compatibility option; no domain templates are loaded")
    parser.add_argument("--dry-run", action="store_true", help="Offline execution; still writes the output")
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 120_000:
            raise ValueError("Brief exceeds 120 KB.")
        text = args.input.read_text(encoding="utf-8-sig")
        competitors = load_competitors(args.competitors)
        if args.plan and args.plan.stat().st_size > 1_000_000:
            raise ValueError("Plan exceeds 1 MB.")
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig")) if args.plan else None
        content = build_prd(text, competitors, plan=plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    except Exception:
        parser.exit(2, "Could not generate PRD. Check the brief, CSV and plan contracts. Existing output was not changed.\n")
    print("Written: review draft." if plan else "Written: input assessment. Add --plan to render an authored product proposal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
