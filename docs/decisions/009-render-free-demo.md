---
id: "AD-9"
status: Accepted
date: 2026-06-19
category: deployment
supersedes: []
superseded_by: []
---

# AD-9 — Render free web service for a zero-cost demo

## Context

The project benefits from a public, always-available demo, but the demo
must cost nothing to host.

## Decision

Provide a `render.yaml` blueprint that deploys the existing Docker image
as a **free Render web service** (auto-deploy on commit, `/health` check).

## Alternatives considered

- **A paid always-on instance** — rejected; unnecessary cost for a demo.

## Consequences

- Free instances cold-start after ~15 minutes idle — acceptable for a demo
  (see [arc42 §11](../arc42/11-risks-and-technical-debt.md)).
- The demo deploys straight from the Dockerfile with no separate build.
