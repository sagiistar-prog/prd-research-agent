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
