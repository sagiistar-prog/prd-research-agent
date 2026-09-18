# Case study

The former generator confused its own workflow with the user's product. Version 0.3 separates literal evidence extraction, host-authored product judgment, deterministic validation, and human review.

The complete fictional examples are [TeamPulse input](../examples/plugin-input.json), [TeamPulse plan](../examples/team-pulse-plan.json), [FitCheck input](../examples/fitcheck-input.json), and [FitCheck plan](../examples/fitcheck-plan.json). Their plans are explicit authored fixtures, never hidden keyword-selected answers.

TeamPulse prioritizes the feedback-to-action loop and privacy uncertainty. FitCheck prioritizes local CSV checking and human handling of uncertain compatibility; optional AI summarization is deferred until its value is observed. The examples show decisions and testable proposed behavior. Neither business product is implemented here.

See [the product decision record](product-case.md) for the problem, tradeoffs and proposed value measures, and [acceptance evidence](evidence-review-acceptance.md) for what was actually tested.
