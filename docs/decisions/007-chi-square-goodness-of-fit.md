---
id: "AD-7"
status: Accepted
date: 2026-06-19
category: architecture
supersedes: []
superseded_by: []
---

# AD-7 — Chi-Square goodness-of-fit reporting via scipy

## Context

"Is the output fair?" should be objective and observable rather than a
matter of trust. A correct cumulative distribution and p-value are hard to
hand-roll correctly ([solution.md](../solution.md) §4).

## Decision

Score every sample with a Chi-Square goodness-of-fit test
(`ChiSquareTest`), using `scipy.stats.chi2` for the p-value, and return
the result inline with the generated numbers.

## Alternatives considered

- **Hand-rolled statistic / no reporting** — rejected; error-prone and
  leaves fairness unverifiable by the caller.

## Consequences

- `scipy` is a runtime dependency.
- The explicit expected-category domain ensures never-observed categories
  still contribute to the statistic.
- Larger samples give a more meaningful verdict (`DEFAULT_QUANTITY =
  1000`).
