---
id: "AD-6"
status: Accepted
date: 2026-06-19
category: architecture
supersedes: []
superseded_by: []
---

# AD-6 — Two generator implementations behind one interface

## Context

The project is a demonstration as much as a service: it should show more
than one valid way to sample a discrete distribution while keeping client
code decoupled from any single implementation.

## Decision

Define the contract with `RandomGenABC`, and provide two implementations:

1. **`RandomGenV1`** — manual inverse-CDF sampling over `random.random()`.
2. **`RandomGenV2`** — sampling via `random.choices`.

## Alternatives considered

- **A single implementation** — rejected; less instructive and couples
  callers to one sampling strategy ([solution.md](../solution.md) §5).

## Consequences

- V1 measured ~3× faster than V2 in the dev journal.
- V1 needs a floating-point guard so it never returns `None`.
- Callers can compare implementations behind one interface.
