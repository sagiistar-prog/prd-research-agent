---
name: prd-research-agent
description: Turn a requirement brief into a reviewable PRD with assumptions, constraints, user stories and acceptance criteria. Use for drafting or reviewing product requirements.
---

# PRD Research Agent Skill

Use this skill when a user wants to turn an early product idea into a structured PRD draft.

## Inputs

- A short requirement brief
- Optional competitor notes
- Optional constraints, metrics, or target user details

## Workflow

1. Extract the product name, user segment, problem, scenario, constraints, and success metrics.
2. Ask or generate the most important clarification questions.
3. Convert the requirement into user scenarios and jobs to be done.
4. Summarize competitor positioning and gaps using fictional or approved data only.
5. Build the product feature sentence:

```text
xxx 产品有 xxx/xxx/xxx/xxx/xxx 功能。
```

6. Expand each top-level feature into 3 to 5 subfeatures.
7. Prioritize features with MoSCoW or another explicit framework.
8. Generate user stories and testable acceptance criteria.
9. Call out risks, non-goals, and open questions.

## Safety Rules

- Do not use private company, customer, employee, or account data.
- Do not invent claims about real competitors.
- Use fictional sample data for public demos.
- Keep outputs suitable for a public portfolio repository.

## Output Style

Write in concise product-manager language. Prefer tables and clear decisions over generic prose.

## Versioned plugin interface

Use the repository root as the working directory. For an installed plugin, resolve the root as two directories above this SKILL.md; never assume the user's project contains the bundled scripts.

1. Read `schemas/input.schema.json` before constructing input. Use `examples/plugin-input.json` for an offline demonstration.
2. Install `requirements-plugin.txt` into the user's chosen Python environment when needed.
3. Run `python scripts/plugin_run.py --input examples/plugin-input.json` from the plugin root. For user text, pass a JSON object through stdin; do not interpolate it into a shell command.
4. Parse stdout as one JSON object; exit 0 means success, exit 2 means an input/output/dependency error. Show the error and preserve the input rather than retrying indefinitely.
5. Present the Markdown result and material warnings. When the user asks to save artifacts, add `--output-dir output/<new-run-name>`. This creates files; an existing directory is never overwritten.

The plugin does not grant permission to read unrelated files, publish content, run rendering or access accounts. The original CLI remains available. See `docs/plugin.md` for the capability boundary and the structured error contract.
