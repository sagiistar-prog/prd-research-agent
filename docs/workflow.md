# Workflow

PRD Research Agent follows a product-management workflow rather than a pure text-generation workflow.

## 1. Input Intake

The agent accepts a short Markdown requirement. It extracts product name, target users, current problems, core scenarios, constraints, and success metrics.

## 2. Requirement Clarification

The agent turns missing information into explicit clarification questions, such as:

- Which user segment is the first MVP segment?
- Which workflow happens weekly, daily, or only on demand?
- Which data must be visible, aggregated, or hidden?
- Which integrations are required now, later, or not at all?

## 3. User Scenario Analysis

The agent maps users to jobs, triggers, pains, expected outcomes, and product moments. This keeps the PRD grounded in behavior rather than feature wish lists.

## 4. Market and Competitor Scan

In Safe Demo mode, the competitor scan uses a local CSV with fictional competitors. A production version could replace this step with a reviewed research source, but public portfolio examples should remain anonymized.

## 5. Functional Scope

The PRD uses a feature-tree structure:

```text
xxx 产品有 A/B/C/D 功能。
A 功能下包含 A1/A2/A3 子功能。
```

This format is easy for product, design, engineering, and QA to discuss together.

## 6. Prioritization

The first version uses MoSCoW:

- Must: required for the MVP promise.
- Should: important, but can wait if timing is tight.
- Could: useful for later differentiation.
- Won't: consciously excluded from the current version.

## 7. Development-Ready Output

The final PRD draft includes user stories, acceptance criteria, risks, open questions, metrics, and milestones.
