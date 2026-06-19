---
id: "AD-4"
status: Accepted
date: 2026-06-19
category: api
supersedes: []
superseded_by: []
---

# AD-4 — dist value:probability pairs alongside legacy parameters

## Context

The original API took two parallel lists via repeated `value` and
`probability` parameters. Nothing binds a value to its weight, so a caller
can submit a **misaligned** distribution (mismatched lengths or order).

## Decision

Add a `dist=value:probability,...` parameter that binds each value to its
own weight and takes precedence over the older repeated `value` /
`probability` parameters. The legacy parameters are retained for backward
compatibility.

## Alternatives considered

- **Repeated `value`/`probability` only** — rejected; misalignment
  between the two lists is expressible and easy to get wrong.

## Consequences

- `parse_dist_pairs` raises `RandomGenDistFormatError` on malformed pairs.
- `dist` wins when both forms are present.
- Backward compatibility with the legacy parameters is preserved.
