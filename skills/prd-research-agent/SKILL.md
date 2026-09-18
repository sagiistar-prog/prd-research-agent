---
name: prd-research-agent
description: Turn a product brief and supplied research into an evidence-linked PRD, scoped features, testable acceptance criteria and a review backlog. Use for product definition and requirements reviews, including unclear briefs. Does not perform market research or validate demand by itself.
---

# From evidence to a product decision

The user needs an answer to what to build, for whom, and why it belongs in this release. Use the supplied material to reason about their product. The scripts extract literal records, check references and render artifacts; they do not infer domain features or call a model. You are the semantic planning layer.

Paths below are relative to the plugin root, two directories above this skill. Read [the plan contract](../../schemas/plan.schema.json) when producing a full plan. [The fictional worked example](../../examples/team-pulse-plan.json) illustrates the format, not a reusable feature list.

## Work from the actual input

- Preserve the original brief in `requirement_markdown`. Include supplied competitor rows only; they remain unverified input claims. Never replace a user's product with this plugin's own capabilities.
- Read prose for already supplied users, problems, constraints and outcomes. Unclassified fields in the assessment mean the literal parser did not identify a heading, not that the user omitted the information. Ask only for decisions that materially affect the scope; use explicit assumptions for other unknowns.
- Run `python scripts/plugin_run.py --input <input.json>` to get `result.analysis`, its input fingerprint and stable evidence records. Use their exact text for citations. The input schema is [here](../../schemas/input.schema.json).
- For constraints embedded in prose, add a `constraint_responses` entry citing that brief record and explain how every relevant clause is handled. Multiple constraints in one record share one response. The automatic completeness check covers labelled constraint records only; you must read prose for the rest. Do not silently remove or rewrite the source to make validation pass.

## Author the product plan

Build a `schema_version: "1.0"` plan with the assessment's `analysis_id`:

- Define users by their job, and problems by the cost or friction in that job. Tie features to those problems and stories to those users.
- Every objective, user, problem, feature, metric and scope exclusion carries `basis`: exact `{id, quote}` evidence references, named `assumption_ids`, or both. A source can motivate a decision without proving it. Put invented mechanisms, thresholds, projected benefits and priority judgments under explicit assumptions when the supplied record does not establish them. Proposed metric targets use `target_status: "proposed"`; missing baselines stay `null`.
- Choose the smallest useful task loop. State why a feature is `must`, `should` or `could`, and whether it belongs in `mvp` or `later`. Consider cost, uncertainty, alternative workflows and dependencies; list order is not a priority framework. Subfeatures exist only when they explain an actual behavior.
- Write acceptance criteria as observable `given`, `when`, `then` conditions. Include material failures, unavailable evidence and scope boundaries where the task requires them. Avoid criteria such as “accurate”, “clear”, “works well” without a way to judge them.
- Respond to each labelled constraint using its evidence ID. `honored` means the proposed design addresses it, not that implementation or compliance has been proven. Use `needs_decision` or `deferred` if unresolved, with an explanation.
- Include measurable user outcomes and a relevant guardrail, with denominator, event or measurement method. Do not convert a proposed target into observed business results.
- Make rollout stages depend on exit criteria. Do not invent calendar commitments or engineering estimates. Keep user approval, clinical/legal review and external deployment outside structural validation.

Do not enforce a fixed number of features or subfeatures. The schema limits are operational size bounds, not content targets. A brief that lacks enough information can end with the assessment and concrete open questions, without inventing a full PRD.

## Validate and hand off

Save the authored plan separately, then run:

```bash
python scripts/plugin_run.py --input <input.json> --plan <plan.json> --output-dir output/<new-review-name>
```

This checks exact quotes, current input fingerprint, user/problem links, dependencies and cycles, explicit constraint coverage, metric status, and rollout ordering. Fix the actual mismatch; never relabel unsupported claims as supplied evidence to satisfy the checker. A changed brief or competitor record requires reassessment and reconsideration of the plan, not just replacing its hash.

Read the resulting PRD as the product owner: do the citations really support the decisions, do exclusions respect the brief, and can a tester evaluate the criteria? The checker does not establish these semantic facts. Report assumptions and unresolved decisions alongside the artifacts. Do not present `review_ready` as release approval or real customer validation.

The output folder is local, new, and never overwritten. It contains the PRD, versioned result, backlog and review page. Opening or sharing the review page exposes the included brief to whoever receives it; use fictional examples for public portfolio work.
