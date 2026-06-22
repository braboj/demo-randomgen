---
id: "AD-26"
status: Accepted
date: 2026-06-22
category: deployment
supersedes: []
superseded_by: []
---

# AD-26 — Rate limiting the generation endpoint

## Context

The generation endpoint is unauthenticated and does real work: it draws up to
the configured maximum number of samples and runs a Chi-Square test per request.
On the free single-instance demo that is a denial-of-service vector — a client
can pin the worker with a tight loop. Nothing throttled it, and the OpenAPI
contract advertised only success and bad-request responses.

## Decision

1. **Flask-Limiter, per application** — the limiter is created inside
   `create_app()` (not as a module-level singleton) and bound with `init_app`.
   The factory builds many applications (a worker per process, one per test);
   a shared instance accumulates a fresh limit registration on every
   `make_api_blueprint` call, double-counting requests. A per-app limiter has
   its own registration set and storage, so counting is correct in every app.
2. **Limit the generation endpoint only** — the limit is applied to each API
   blueprint (whose only route is the generation endpoint). `/health` and the
   browser UI are exempt (`limiter.exempt(web.bp)`); `/docs`, `/openapi.json`,
   and static assets are never throttled.
3. **Configurable limit under a dedicated key** — the value comes from
   `RANDOMGEN_RATELIMIT` (default `60 per minute`), read per request. It is
   intentionally NOT Flask-Limiter's native `RATELIMIT_DEFAULT`, which would
   apply as an app-wide default to every route and double-count the endpoint.
4. **429 through the existing contract** — exceeding the limit raises a Werkzeug
   `TooManyRequests`, which the error boundary already renders as
   `{"error": ...}` with status 429. The contract documents the 429 on both
   generation routes; `openapi.yaml` `info.version` moves 2.0.0 → 2.1.0 (an
   additive change, per AD-21).
5. **In-memory storage by default** — `RANDOMGEN_RATELIMIT_STORAGE_URI` defaults
   to `memory://`. Counters are per worker and reset on restart, so the
   effective limit is the configured value times the worker count. Acceptable
   for the single free-tier instance; the URI is configurable so a shared store
   (e.g. Redis) is a config change, not a code change.

## Alternatives considered

- **App-wide default limits (`RATELIMIT_DEFAULT`)** — rejected; it throttles
  `/docs`, `/openapi.json`, and static assets the home page loads, and
  double-counts the decorated endpoint.
- **Decorating the inner view in the factory** — rejected; the factory's view
  functions share one `__qualname__` across versions, and Flask-Limiter keys
  decorated limits by that name, so each version's limit registers under the
  same key and every request counts once per version.
- **A hand-rolled limiter** — rejected; Flask-Limiter handles window strategies,
  storage backends, and the standard rate-limit response headers.

## Consequences

- New runtime dependency: `flask-limiter`.
- The API contract gains a 429; `info.version` becomes 2.1.0.
- Rate limiting is an operational concern, not routing/contract behaviour, so
  the test suite defaults it off (`RANDOMGEN_RATELIMIT_ENABLED=false` in
  `conftest.py`); the dedicated rate-limit test opts back in.
- The per-worker in-memory storage caveat is documented for operators.
