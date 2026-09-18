"""Render reviewed structures without manufacturing domain decisions."""
from __future__ import annotations

import html
import re


def md(value) -> str:
    text = html.escape(str(value), quote=False)
    return re.sub(r"([\\`*_{}\[\]()|#!>~])", r"\\\1", text).replace("\r", "").replace("\n", "<br>")


def phrase(value) -> str:
    return md(str(value).rstrip("。；;"))


def basis_text(basis: dict) -> str:
    refs = [f"[{md(r['id'])}](#{r['id'].lower()})：{md(r['quote'])}" for r in basis["evidence_refs"]]
    refs += [f"假设 {md(identifier)}" for identifier in basis["assumption_ids"]]
    return "；".join(refs)


def backlog(plan: dict | None) -> list[dict]:
    if not plan:
        return []
    users = {u["id"]: u["name"] for u in plan["users"]}
    return [{"id": f"{f['id']}-S{i}", "feature_id": f["id"], "feature": f["name"],
             "scope": f["scope"], "priority": f["priority"], "user": users[s["user_id"]],
             "want": s["want"], "benefit": s["benefit"], "acceptance": s["acceptance"],
             "dependencies": f["dependencies"], "basis": f["basis"]}
            for f in plan["features"] for i, s in enumerate(f["stories"], 1)]


def render(analysis: dict, plan: dict | None, checks: dict | None) -> str:
    title = plan["product_name"] if plan else analysis["summary"]["product_name"]
    lines = [f"# {md(title)}", "", "状态：待人工评审。引用校验不代表方案已验证。" if plan else "状态：需求资料已整理，产品方案待补充。", ""]
    if not plan:
        lines += ["## 资料梳理", "", "原始输入和竞品资料已建立可引用记录。脚本不按行业关键词套用功能。", "",
                  "## 产品功能总览", "", "产品有哪些功能尚未决定。请由产品负责人或宿主 AI 根据下方输入拟定 product_plan。", "",
                  "## 用户故事与验收标准", "", "待方案明确用户、问题、范围和假设后生成。", "",
                  "## 下一步", "", "1. 读取原始需求，确认用户在什么场景下遇到什么问题。",
                  "2. 按 schemas/plan.schema.json 编写方案，每项判断引用原文或登记假设。",
                  "3. 使用 --plan 重新生成，核对优先级理由、约束响应与验收标准。"]
        if analysis["unclassified_fields"]:
            lines += ["", "未识别到独立字段：" + "、".join(analysis["unclassified_fields"]) + "。信息可能已包含在正文中，请先阅读，不要重复询问。"]
    else:
        lines += ["## 产品目标", "", md(plan["objective"]["statement"]), "", basis_text(plan["objective"]["basis"]), "", "## 用户与问题", ""]
        for user in plan["users"]:
            lines += [f"### {md(user['id'])} {md(user['name'])}", "", md(user["job"]), "", basis_text(user["basis"]), ""]
        for problem in plan["problems"]:
            lines += [f"- {md(problem['id'])}：{md(problem['description'])}（{md(', '.join(problem['user_ids']))}）", "  " + basis_text(problem["basis"])]
        lines += ["", "## 产品功能总览", "", f"{md(title)}产品有" + "、".join(md(f["name"]) for f in plan["features"]) + "功能提案。", "",
                  "| 功能 | 版本范围 | 优先级 | 取舍依据 |", "|---|---|---|---|"]
        for f in plan["features"]:
            lines.append(f"| {md(f['id'])} {md(f['name'])} | {f['scope']} | {f['priority']} | {md(f['priority_rationale'])} |")
        lines += ["", "## 功能范围与验收标准", ""]
        users = {u["id"]: u["name"] for u in plan["users"]}
        for f in plan["features"]:
            lines += [f"### {md(f['id'])} {md(f['name'])}", "", "对应问题：" + md(", ".join(f["problem_ids"])),
                      "", "前置依赖：" + md(", ".join(f["dependencies"]) or "无"), "", "依据：" + basis_text(f["basis"]), ""]
            for sub in f["subfeatures"]:
                lines.append(f"- **{md(sub['name'])}**：{md(sub['description'])}")
            for i, story in enumerate(f["stories"], 1):
                lines += ["", f"**{md(f['id'])}-S{i}** 作为{md(users[story['user_id']])}，我希望{phrase(story['want'])}，以便{phrase(story['benefit'])}。", ""]
                for criterion in story["acceptance"]:
                    lines.append(f"- 给定：{phrase(criterion['given'])}；当：{phrase(criterion['when'])}；则：{phrase(criterion['then'])}。")
        lines += ["", "## 约束响应", ""]
        for c in plan["constraint_responses"]:
            lines.append(f"- [{md(c['evidence_id'])}](#{c['evidence_id'].lower()}) / {md(c['treatment'])}：{phrase(c['implementation'])}。关联功能：{md(', '.join(c['feature_ids']) or '范围约束')}。")
        lines += ["", "## 暂不纳入", ""]
        lines += [f"- {md(o['item'])}：{phrase(o['reason'])}。{basis_text(o['basis'])}" for o in plan["out_of_scope"]] or ["暂无显式排除项。"]
        lines += ["", "## 假设与验证", ""]
        for a in plan["assumptions"]:
            lines += [f"- **{md(a['id'])}** / {md(a['impact'])}：{md(a['claim'])}", "  验证方法：" + md(a["validation"])]
        if not plan["assumptions"]:
            lines.append("未登记假设，评审时仍需核对是否有遗漏。")
        lines += ["", "## 指标与护栏", ""]
        for m in plan["metrics"]:
            lines += [f"### {md(m['name'])} / {m['kind']}", "", md(m["definition"]), "",
                      "基线：" + md(m["baseline"] or "未测量"), "目标：" + md(m["target"] or "待确定") + f"（{m['target_status']}）",
                      "采集方式：" + md(m["collection"]), "", basis_text(m["basis"]), ""]
        lines += ["## 迭代路径", "", "阶段按验收条件推进，日期和投入需另行估算。", ""]
        for stage in plan["rollout"]:
            lines += [f"### {md(stage['name'])}", "", "包含功能：" + md(", ".join(stage["feature_ids"])), ""]
            lines += ["- " + md(criterion) for criterion in stage["exit_criteria"]]
        lines += ["", "## 评审问题", ""]
        lines += ["- " + md(q) for q in plan["open_questions"]] or ["暂无登记，仍需产品负责人确认语义合理性。"]
        lines += ["", f"引用和依赖检查通过。待验证假设 {checks['assumptions_pending']} 项，未决约束 {checks['constraint_decisions_pending']} 项。"]
    lines += ["", "## 输入依据", "", "以下是输入记录，不代表独立完成了用户研究或竞品核验。", ""]
    for e in analysis["evidence"]:
        lines += [f"<a id=\"{e['id'].lower()}\"></a>", f"**{e['id']}** / {md(e['kind'])} / {md(e['source'])} 第 {e['line']} 行", "", md(e["text"]), ""]
    fence = "`" * max(3, max((len(m.group()) + 1 for m in re.finditer(r"`+", analysis["requirement_markdown"])), default=3))
    lines += ["## 原始需求", "", fence + "text", analysis["requirement_markdown"], fence,
              "", "输入指纹：`" + analysis["analysis_id"] + "`", ""]
    return "\n".join(lines)
