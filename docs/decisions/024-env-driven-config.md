---
id: "AD-24"
status: Accepted
date: 2026-06-22
category: architecture
supersedes: []
superseded_by: []
---

# AD-24 — Env-driven application configuration

## Context

Until now the application read no configuration: `create_app()` took no
arguments, the app held no `app.config`, and the only runtime knob was the
listen port, expanded by the shell in the Docker entrypoint. The observability
work needs one setting that must vary by environment without a rebuild — the
logging verbosity — and more operational settings may follow. A small
configuration surface is needed, and the service has none.

The distribution to sample from is already per-request and the service holds no
mutable state across requests. Any configuration must preserve that property: it
may parameterize how a worker starts, but must not become shared mutable state
that requests read and write.

## Decision

1. **Single `Config` object** — a `randomgen.config.Config` class reads its
   values from `RANDOMGEN_*` environment variables in `__init__` and is applied
   with `app.config.from_object(Config())` as the first step of `create_app()`,
   before anything that consumes `app.config`. It currently exposes one value,
   the log level, and is the one place new operational settings are added.
2. **Read at application-creation time** — `Config` is instantiated per
   `create_app()` call, so the environment is read when the worker (or a test)
   builds the app, not at import. This keeps the configuration testable: a test
   sets the environment, then calls `create_app()`.
3. **Configuration is read-only startup state** — values are fixed for the life
   of a worker and MUST NOT be mutated while serving a request. This does not
   conflict with per-request statelessness: it parameterizes how a worker
   starts, not what a request stores.

## Alternatives considered

- **`app.config.from_prefixed_env()`** — rejected as the source of truth; it
  reads the environment but provides no defaults or documented surface, and
  layering it on top of the class would create two competing conventions.
- **Module-level constants read at import** — rejected; the values would freeze
  at first import, so tests could not override the environment per case without
  reimporting the module.

## Consequences

- `create_app()` gains a configuration step; `randomgen.config` is the one place
  that names every environment variable and its default.
- The observability layer reads `LOG_LEVEL` from `app.config` rather than
  hard-coding it.
- The surface starts minimal (logging verbosity) and grows as operational
  settings are added, without changing how configuration is read or applied.
