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
  callers to one sampling strategy ([solution.md](../history/solution.md) §5).

## Consequences

- Callers can compare two sampling strategies behind one interface, with no
  change to client code.
- V1 (inverse-CDF) is explicit and instructive and measured ~3× faster than V2
  in the dev journal, but reimplements standard-library behavior, needs a
  floating-point guard so it never returns `None`, and carries more code to test.
- V2 (`random.choices`) is concise and idiomatic and leans on a battle-tested
  standard-library routine, but is less transparent about how sampling works.
