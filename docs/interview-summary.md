# Interview Summary

## 30-Second Pitch

PRD Research Agent is a portfolio-ready AI Agent for product managers. It turns a rough product idea into a structured PRD draft by walking through clarification, user scenarios, competitor analysis, feature scope, prioritization, user stories, and acceptance criteria.

## What It Demonstrates

- Product sense: the output is organized around user problems, not just generated text.
- Execution thinking: the PRD includes scope, trade-offs, risks, and milestones.
- Collaboration readiness: engineering and QA can read the generated user stories and acceptance criteria.
- Safety awareness: the repo includes a Safe Demo and a portfolio audit script.

## How to Demo

Run:

```bash
python scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

Then show:

- `examples/sample_requirement.md`
- `examples/sample_competitors.csv`
- `examples/generated_prd.md`
- `docs/prd-methodology.md`
- `scripts/portfolio_audit.ps1`

## Best Interview Talking Points

- The agent workflow mirrors how a product manager thinks before writing a PRD.
- The generated feature sentence creates an easy shared language: `xxx 产品有 A/B/C/D 功能`.
- The Safe Demo proves the project is reproducible without exposing private information.
- The audit script shows public-repo readiness, which matters for portfolio projects.
