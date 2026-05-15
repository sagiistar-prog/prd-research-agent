# PRD Methodology

This project treats PRD writing as a chain of product decisions.

## PRD Shape

The preferred format is:

```text
xxx 产品有 xxx/xxx/xxx/xxx/xxx 功能。
每个功能下面列出子功能、用户故事、验收标准和优先级。
```

This structure creates a shared map for product managers, designers, engineers, and testers.

## Required Questions

Before writing the PRD, the agent asks:

- Who has the problem first?
- What event triggers the need?
- What does the user do today?
- What would make the user trust the product?
- What is inside the MVP, and what is intentionally excluded?
- How will the team know whether the release worked?

## Feature Tree

Each top-level feature should be:

- Outcome-based, not implementation-based.
- Small enough to discuss in one product review.
- Clear enough for engineering decomposition.
- Testable through acceptance criteria.

## Prioritization

The demo uses MoSCoW because it is readable in interviews and works well for early scoping. In production, the scoring layer could be replaced with RICE, opportunity scoring, Kano, or a revenue-weighted model.

## Acceptance Criteria

Acceptance criteria use a Gherkin-like style:

```text
Given a specific state
When the user takes an action
Then the product produces an observable result
```

The point is not ceremony. The point is to remove ambiguity before development starts.
