# Agent Instructions

This repository is a standalone portfolio project for PRD Research Agent.

## Boundaries

- Work only inside this repository when modifying files.
- Use fictional and anonymized examples only.
- Do not add private company content, real customer data, personal messages, credentials, or local absolute paths.
- Keep generated examples deterministic enough for portfolio review.
- Prefer clear product reasoning over large technical abstractions.

## Safe Demo

The required demo command is:

```bash
python scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

The `--dry-run` flag means offline deterministic generation. It must not call external APIs, but it must still write `examples/generated_prd.md`.

## Quality Bar

- README must start with an interviewer-friendly 30-second summary.
- Examples must stay fictional.
- PRD output should include feature tree, subfeatures, user stories, acceptance criteria, and prioritization.
- Run `powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1` before publishing.
