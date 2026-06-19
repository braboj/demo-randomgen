---
id: "AD-5"
status: Accepted
date: 2026-06-19
category: api
supersedes: []
superseded_by: []
---

# AD-5 — Versioned API as a stable public contract

## Context

Consumers need predictable, non-breaking evolution. Two generator
implementations exist (see AD-6) and must be exposed without letting a
change to one break clients of the other.

## Decision

Expose two interchangeable generators at `/api/v1` and `/api/v2`. Freeze
each version's behavior — a behavior change MUST be a new version, never a
change to an existing one.

## Alternatives considered

- **Single unversioned endpoint** — rejected; any behavior change would
  break existing consumers.

## Consequences

- `/api/v1` and `/api/v2` differ only in the generator; parameters,
  response shape, and status codes are identical.
- New behavior is added as a new version, never by mutating a shipped one.
