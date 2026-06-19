---
id: "AD-8"
status: Accepted
date: 2026-06-19
category: deployment
supersedes: []
superseded_by: []
---

# AD-8 — gunicorn + hardened Docker image

## Context

The Flask development server is not suitable for production serving. The
demo also needs a reproducible, minimal, least-privilege image that a PaaS
can run with an injected port.

## Decision

Serve via **gunicorn** inside a **non-root, digest-pinned Alpine** image
with a `/health` `HEALTHCHECK`, binding `${PORT:-5000}`.

## Alternatives considered

- **Flask dev server in production** — rejected; not production-grade.
- **A third `webserver.py` entrypoint** — rejected and removed (v0.8.x);
  it was a launch path to keep in sync for no benefit.

## Consequences

- The local Flask dev server (`flask run`) is convenience-only; debug
  stays off everywhere.
- Two launch paths remain: `flask --app "randomgen.app:create_app" run`
  for dev, gunicorn for production.
- The image binds the PaaS-injected `$PORT`.
