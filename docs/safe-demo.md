# Safe Demo

Safe Demo proves the project can run without private data or external services.

## Command

```bash
python scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

Windows 兼容命令：

```powershell
py -3 scripts/generate_prd.py --input examples/sample_requirement.md --competitors examples/sample_competitors.csv --output examples/generated_prd.md --rules configs/prd_rules.yaml --dry-run
```

## Expected Result

The command writes:

```text
examples/generated_prd.md
```

The generated PRD should include:

- Requirement summary
- Clarification questions
- User scenarios
- Competitor matrix
- Feature overview sentence
- Feature tree with subfeatures
- Prioritization
- User stories
- Acceptance criteria
- Risks and milestones

## Why `--dry-run` Still Writes a File

In this project, dry-run means safe offline generation. It disables external calls and uses deterministic local logic, but it still writes the demo artifact so interviewers can reproduce the result with one command.

## Audit

Run the audit after generating the PRD:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

The audit checks required files, common sensitive-info patterns, large files, generated demo output, and GitHub visibility when a remote repository is configured.
