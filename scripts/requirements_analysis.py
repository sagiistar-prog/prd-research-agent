"""Literal evidence extraction. Product reasoning belongs to the host or author."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPETITOR_COLUMNS = ["name", "positioning", "strengths", "weaknesses", "pricing", "target_user"]
LABELS = {
    "product": ["产品名称", "产品名", "product", "product name"],
    "objective": ["一句话需求", "需求", "背景", "objective", "brief", "goal"],
    "users": ["目标用户", "用户", "users", "target users"],
    "problems": ["当前问题", "问题", "problems", "pain points"],
    "scenarios": ["核心场景", "场景", "scenarios", "use cases"],
    "constraints": ["约束", "限制", "constraints"],
    "metrics": ["成功指标", "指标", "metrics", "success metrics"],
}
ALIASES = {label.casefold(): key for key, labels in LABELS.items() for label in labels}


def assess(brief: str, competitors: list[dict] | None = None) -> dict:
    if not brief.strip():
        raise ValueError("Requirement brief must contain text.")
    competitors = competitors or []
    values = {key: [] for key in LABELS}
    evidence, section, title = [], "context", ""
    for line_number, raw in enumerate(brief.splitlines(), 1):
        text = raw.strip()
        if not text:
            continue
        heading = bool(re.match(r"^#{1,6}\s", text))
        content = re.sub(r"^(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)", "", text).replace("**", "").strip()
        label, separator, value = re.match(r"^([^:：]*)([:：]?)(.*)$", content).groups()
        kind = ALIASES.get(label.strip().casefold())
        if kind:
            section = kind
            if not separator or not value.strip():
                continue
            literal = value.strip()
        else:
            literal = content
            if heading:
                section = "context"
                if not title:
                    title = content
        if section in values:
            values[section].append(literal)
        evidence.append({"id": f"E{len(evidence) + 1:03}", "kind": section,
                         "text": text, "line": line_number, "source": "brief"})
    for index, competitor in enumerate(competitors, 1):
        for field in COMPETITOR_COLUMNS:
            evidence.append({"id": f"C{index:03}-{field}", "kind": "competitor",
                             "text": competitor[field], "line": index, "source": f"competitors.{field}"})
    canonical = json.dumps({"brief": brief, "competitors": competitors}, ensure_ascii=False,
                           sort_keys=True, separators=(",", ":"))
    summary = {"product_name": " / ".join(values["product"]) or title or "未命名需求",
               "one_liner": "\n".join(values["objective"]), "target_users": "\n".join(values["users"]),
               **{k: values[k] for k in ["problems", "scenarios", "constraints", "metrics"]}}
    missing = [key for key in ["users", "problems", "scenarios", "constraints", "metrics"] if not values[key]]
    return {"analysis_id": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "requirement_markdown": brief, "summary": summary, "evidence": evidence,
            "competitors": competitors, "unclassified_fields": missing}


def load_competitors(path: Path | None) -> list[dict]:
    if path is None:
        return []
    if path.stat().st_size > 1_000_000:
        raise ValueError("Competitor CSV exceeds 1 MB.")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or sorted(reader.fieldnames) != sorted(COMPETITOR_COLUMNS):
            raise ValueError("CSV must have each documented competitor column exactly once.")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Competitor CSV row has a different column count.")
            rows.append(row)
            if len(rows) > 30:
                raise ValueError("At most 30 competitor records are supported.")
    validate_input({"requirement_markdown": "CSV validation", "competitors": rows})
    return rows


def validate_input(data: dict) -> None:
    from jsonschema import Draft202012Validator
    schema = json.loads((ROOT / "schemas/input.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(data)


def validate_plan(plan: dict, analysis: dict) -> dict:
    from jsonschema import Draft202012Validator
    schema = json.loads((ROOT / "schemas/plan.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(plan)
    if plan["analysis_id"] != analysis["analysis_id"]:
        raise ValueError("Plan is stale: analysis_id does not match this brief and competitor input.")
    evidence = {entry["id"]: entry for entry in analysis["evidence"]}
    groups = {key: {item["id"]: item for item in plan[key]}
              for key in ["users", "problems", "features", "assumptions", "metrics"]}
    for key, records in groups.items():
        if len(records) != len(plan[key]):
            raise ValueError(f"Duplicate IDs in {key}.")
    def references(ids, allowed, location):
        if len(ids) != len(set(ids)) or any(identifier not in allowed for identifier in ids):
            raise ValueError(f"Unknown or duplicate reference in {location}.")

    def check_basis(basis):
        references(basis["assumption_ids"], groups["assumptions"], "basis.assumption_ids")
        if not basis["evidence_refs"] and not basis["assumption_ids"]:
            raise ValueError("Every decision needs evidence or a stated assumption.")
        for ref in basis["evidence_refs"]:
            if ref["id"] not in evidence or ref["quote"] not in evidence[ref["id"]]["text"]:
                raise ValueError("Evidence quote does not match the referenced input record.")

    check_basis(plan["objective"]["basis"])
    for key in ["users", "problems", "features", "metrics", "out_of_scope"]:
        for item in plan[key]:
            check_basis(item["basis"])
    for problem in plan["problems"]:
        references(problem["user_ids"], groups["users"], "problem.user_ids")
    for feature in plan["features"]:
        references(feature["problem_ids"], groups["problems"], "feature.problem_ids")
        references(feature["dependencies"], groups["features"], "feature.dependencies")
        if feature["scope"] == "mvp" and any(groups["features"][dep]["scope"] != "mvp" for dep in feature["dependencies"]):
            raise ValueError("An MVP feature cannot depend on a later feature.")
        allowed_users = {u for p in feature["problem_ids"] for u in groups["problems"][p]["user_ids"]}
        for story in feature["stories"]:
            references([story["user_id"]], allowed_users, "story.user_id for linked problem")
    visited, visiting = set(), set()
    def visit(identifier):
        if identifier in visiting:
            raise ValueError("Feature dependencies contain a cycle.")
        if identifier in visited:
            return
        visiting.add(identifier)
        for dep in groups["features"][identifier]["dependencies"]:
            visit(dep)
        visiting.remove(identifier)
        visited.add(identifier)
    for identifier in groups["features"]:
        visit(identifier)
    constraint_ids = {e["id"] for e in analysis["evidence"] if e["kind"] == "constraints"}
    addressed = [c["evidence_id"] for c in plan["constraint_responses"]]
    brief_ids = {e["id"] for e in analysis["evidence"] if e["source"] == "brief"}
    if not constraint_ids.issubset(addressed) or not set(addressed).issubset(brief_ids) or len(addressed) != len(set(addressed)):
        raise ValueError("Cover every labelled constraint once; additional prose responses must cite a unique brief record.")
    for constraint in plan["constraint_responses"]:
        references(constraint["feature_ids"], groups["features"], "constraint.feature_ids")
    for metric in plan["metrics"]:
        if (metric["target"] is None) != (metric["target_status"] == "unknown"):
            raise ValueError("A target must have provided/proposed status; an unknown target must be null.")
        if metric["target_status"] == "provided" and not metric["basis"]["evidence_refs"]:
            raise ValueError("A provided metric target needs an input evidence reference.")
        if metric["target_status"] == "provided" and not any(metric["target"] in ref["quote"] for ref in metric["basis"]["evidence_refs"]):
            raise ValueError("Copy a provided target exactly from cited input; otherwise mark it proposed.")
    if not any(m["kind"] == "guardrail" for m in plan["metrics"]):
        raise ValueError("Define at least one guardrail alongside the outcome metric.")
    if not any(m["kind"] == "outcome" for m in plan["metrics"]):
        raise ValueError("Define at least one user outcome metric.")
    release_order = {}
    for index, stage in enumerate(plan["rollout"]):
        references(stage["feature_ids"], groups["features"], "rollout.feature_ids")
        for identifier in stage["feature_ids"]:
            if identifier in release_order:
                raise ValueError("A feature can appear in only one rollout stage.")
            release_order[identifier] = index
    if set(release_order) != set(groups["features"]):
        raise ValueError("Rollout must cover every proposed feature exactly once.")
    for feature in plan["features"]:
        if any(release_order[dep] > release_order[feature["id"]] for dep in feature["dependencies"]):
            raise ValueError("A feature cannot roll out before its dependency.")
    return {"reference_integrity": "passed", "semantic_review": "required",
            "constraint_decisions_pending": sum(c["treatment"] != "honored" for c in plan["constraint_responses"]),
            "assumptions_pending": len(plan["assumptions"]),
            "mvp_feature_ids": [f["id"] for f in plan["features"] if f["scope"] == "mvp"]}
