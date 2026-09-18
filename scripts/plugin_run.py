#!/usr/bin/env python3
"""Versioned, offline JSON interface. No network or model calls."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
MAX_BYTES = 1_000_000

def execute(data: dict) -> dict:
    from requirements_analysis import assess, validate_plan
    from prd_renderer import render, backlog
    analysis = assess(data["requirement_markdown"], data.get("competitors", []))
    plan = data.get("product_plan")
    checks = validate_plan(plan, analysis) if plan is not None else None
    summary = analysis["summary"] if plan is None else {
        "product_name": plan["product_name"], "one_liner": plan["objective"]["statement"],
        "target_users": "、".join(u["name"] for u in plan["users"]),
        "problems": [p["description"] for p in plan["problems"]],
        "scenarios": [s["want"] for f in plan["features"] for s in f["stories"]],
        "constraints": [c["implementation"] for c in plan["constraint_responses"]],
        "metrics": [m["definition"] for m in plan["metrics"]]}
    return {"markdown": render(analysis, plan, checks), "summary": summary,
            "summary_source": "product_plan" if plan is not None else "input_extraction",
            "analysis": analysis, "phase": "review_ready" if plan is not None else "needs_plan",
            "product_plan": plan, "checks": checks, "backlog": backlog(plan)}


def run(data: dict) -> dict:
    from jsonschema import Draft202012Validator
    schema = json.loads((ROOT / "schemas/input.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(data)
    result = {"schema_version": "2.0", "status": "ok", "mode": "evidence_to_prd", "result": execute(data),
              "warnings": ["脚本校验引用与结构；产品判断由宿主 AI 或方案作者完成。", "引用存在不代表推论成立，方案须经产品负责人评审。"]}
    Draft202012Validator(json.loads((ROOT / "schemas/output.schema.json").read_text(encoding="utf-8"))).validate(result)
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description='把模糊需求整理成可复核的 PRD 初稿')
    parser.add_argument("--input", type=Path, help="UTF-8 JSON file. Omit to read stdin.")
    parser.add_argument("--plan", type=Path, help="Separate authored plan; cannot combine with input.product_plan.")
    parser.add_argument("--output-dir", type=Path, help="New directory inside output/. Existing directories are never overwritten.")
    args = parser.parse_args()
    try:
        if args.input and args.input.stat().st_size > MAX_BYTES: raise ValueError("Input exceeds 1 MB")
        raw = args.input.read_text(encoding="utf-8-sig") if args.input else sys.stdin.buffer.read(MAX_BYTES + 1).decode("utf-8-sig")
        if len(raw.encode("utf-8")) > MAX_BYTES: raise ValueError("Input exceeds 1 MB")
        data = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))
        if args.plan:
            if not isinstance(data, dict) or "product_plan" in data:
                raise ValueError("Use either --plan or product_plan, not both.")
            if args.plan.stat().st_size > MAX_BYTES:
                raise ValueError("Plan exceeds 1 MB")
            data["product_plan"] = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        payload = run(data)
        if args.output_dir:
            from review_renderer import render_review
            review = render_review(payload)
            destination = args.output_dir.resolve()
            allowed = (ROOT / "output").resolve()
            if not destination.is_relative_to(allowed) or destination == allowed:
                raise ValueError("Choose a new subdirectory inside output/")
            destination.mkdir(parents=True, exist_ok=False)
            (destination / "result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (destination / "result.md").write_text(payload["result"]["markdown"], encoding="utf-8")
            (destination / "backlog.json").write_text(json.dumps(payload["result"]["backlog"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (destination / "review.html").write_text(review, encoding="utf-8")
        code = 0
    except ImportError:
        payload = {"schema_version":"2.0", "status":"error", "error":{"code":"DEPENDENCY_MISSING", "message":"Install requirements-plugin.txt before running the plugin."}}
        code = 2
    except Exception as exc:
        # Do not echo user text, stack traces or local file paths into the response.
        if type(exc).__name__ == "ValidationError":
            location = ".".join(str(part) for part in exc.absolute_path) or "input"
            message = f"Invalid field: {location}; failed {exc.validator} constraint. See schemas/input.schema.json."
        elif isinstance(exc, (FileExistsError, FileNotFoundError, PermissionError, OSError)):
            message = "Cannot read input or create a fresh output directory. Existing output is preserved."
        elif isinstance(exc, json.JSONDecodeError): message = "Input must be valid UTF-8 JSON."
        else: message = str(exc) if isinstance(exc, ValueError) else "Generation failed; check the documented input contract."
        payload = {"schema_version":"2.0", "status":"error", "error":{"code":"INVALID_INPUT_OR_OUTPUT", "message":message}}
        code = 2
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
