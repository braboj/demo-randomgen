---
id: "AD-25"
status: Accepted
date: 2026-06-22
category: deployment
supersedes: []
superseded_by: []
---

# AD-25 — Operational observability: request logging and gunicorn runtime

## Context

The service emitted no application logs at all: a request left no trace, an
unexpected failure produced no diagnostic, and the only signal was the HTTP
response itself. For a service that is meant to demonstrate production
readiness, that is the largest operational gap. Two related shortcomings sit
alongside it: the error boundary returned the raw exception text on a 500,
leaking internal detail to the client; and the container ran gunicorn with
default settings (one worker, no access log, no tunable timeout), so even at the
process level there was nothing to observe.

## Decision

1. **Request logging** — `randomgen.observability.register_logging` configures
   the application logger from `LOG_LEVEL` and registers `before_request` /
   `after_request` hooks that emit one line per response: method, path, status,
   and duration. Because the error boundary returns a response rather than
   re-raising, the hook runs for handled 4xx/5xx responses too, so every request
   produces exactly one access-log line.
2. **Generic 500, logged in full** — the error boundary logs unexpected
   exceptions with `logger.exception` (message plus traceback) and returns a
   generic `{"error": "Internal Server Error"}`. Client-safe messages (domain
   400s and Werkzeug HTTP errors) are unchanged.
3. **Gunicorn runtime config** — a `gunicorn.conf.py` at the repo root, copied
   into the image and auto-discovered, sets workers (from `WEB_CONCURRENCY`,
   default 2), threads, a request timeout, and access/error logs to stdout. The
   Docker entrypoint becomes exec-form `["gunicorn", "randomgen.app:create_app()"]`;
   the config file supplies the bind (reading `$PORT` itself).
4. **Stdlib logging only** — no structured-logging dependency. Logs go to
   stdout/stderr for the container runtime to collect.

## Alternatives considered

- **Structured/JSON logging (structlog, python-json-logger)** — rejected for a
  single-replica demo; it adds a runtime dependency for output a human reads
  directly. The format can change later without touching the call sites.
- **Flask-Talisman / a logging extension** — rejected; the request hooks and the
  generic-500 fix are a few lines of first-party code with no new dependency.

## Consequences

- `create_app()` gains a `register_logging` step; the gunicorn runtime is now
  configuration-as-code rather than implicit defaults (extends AD-8).
- Operators get request-level visibility and tunable concurrency/timeout via
  environment variables; the 500 information leak is closed.
- The end-to-end container tier must be run after this change (the entrypoint
  and serving config changed).
