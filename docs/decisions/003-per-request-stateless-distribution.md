---
id: "AD-3"
status: Accepted
date: 2026-06-19
category: architecture
supersedes: []
superseded_by: []
---

# AD-3 — Per-request, stateless distribution

## Context

An early design held the distribution in server-side configuration
(a `/api/v1/config` endpoint). Server-side state complicates horizontal
scaling and forces persistence and a configuration lifecycle the service
does not otherwise need.

## Decision

Hold no configuration server-side. The distribution defaults to a built-in
one and is overridable **per request** (`dist` pairs, or repeated
`value`/`probability` parameters).

## Alternatives considered

- **Server-side config endpoint (`/api/v1/config`)** — rejected; adds
  shared mutable state and persistence. Replaced by per-request
  parameters.

## Consequences

- A shared, stateless `RandomGenRestApi`; no shared mutable state across
  workers.
- The service is trivially horizontally scalable with no config endpoint
  or persistence.
