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

## Refinement (2026-06-23)

The `gunicorn.conf.py` introduced by decision 3 was trimmed to its load-bearing
surface: `bind` (gunicorn does not read `$PORT` itself) and `workers` (from
`WEB_CONCURRENCY`). The `threads`, `timeout`, `graceful_timeout`, and `keepalive`
settings were removed — they only restated gunicorn's defaults or exposed env
knobs (`GUNICORN_THREADS`/`GUNICORN_TIMEOUT`/`GUNICORN_LOG_LEVEL`) that a
single-instance demo will never tune. The explicit gunicorn access log was also
dropped, because it duplicated the application's per-request log from decision 1;
gunicorn's own errors still reach stderr by default. The observability intent of
this ADR is unchanged — one log line per request — only the operational
over-specification it carried is gone.

## Coverage review (2026-06-23, #210–#212)

Three spikes asked whether the logging surface — after the access log was
dropped — still tells the operational story: is there a blind spot (#210), does
the request line carry enough (#211), and are business-logic events observable
(#212). The request flow was driven through every response class with logging at
DEBUG to answer empirically. The findings:

- **Coverage holds for what the app handles.** Every handled response — success,
  4xx, 5xx — produces exactly one access line; an unexpected 500 produces exactly
  one traceback (decision 2) followed by one access line. Two gaps were judged
  acceptable rather than closed: a request that exceeds the gunicorn timeout dies
  before `after_request` runs, and requests rejected at the WSGI layer never reach
  the app — but generation is sub-millisecond compute bounded by `MAX_NUMBERS`, so
  a timeout is effectively unreachable, and gunicorn's stderr still records
  process-level failures. Restoring a gunicorn access log to cover them would
  reintroduce the duplication the refinement above removed.
- **The line keeps its format, and gains the client address.** Stdlib text at
  INFO stays (a human reads it directly; structured logging remains the deferred
  option from "Alternatives considered"). The client address was added — standard
  access-log content, one field. A correlation ID and response size were declined
  as overkill for a single replica.
- **One business-logic gap was real and is closed.** Every `400` logged
  identically, so the log could not say *which* rule rejected a request. The error
  boundary now logs the rejection cause at WARNING (the validation message, which
  the client already sent), alongside the unchanged access line. Domain DEBUG
  lines for the default-distribution fallback and the chi-square fairness verdict
  were declined: both already appear in the response body, and adding them is the
  single-replica noise this ADR set out to avoid.
- **Static assets are excluded from the access log.** CSS/JS fetches are
  byproducts of a page view, not traffic worth a line.

Net effect: AD-25's intent — one stdlib-text line per request, minimal — is
unchanged. The line now leads with the client address, validation rejections
carry their cause, and static-asset noise is gone.
