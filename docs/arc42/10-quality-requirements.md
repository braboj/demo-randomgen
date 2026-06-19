# 10. Quality Requirements

This section refines the quality goals from
[Section 1](01-introduction-and-goals.md) into a quality tree and concrete,
testable scenarios.

## 10.1 Quality tree

| Quality attribute | Refinement |
|-------------------|------------|
| **Functional correctness** | Statistical fairness; Chi-Square reporting accuracy; input validation. |
| **Reliability** | Predictable failure; bounded work per request; no shared mutable state. |
| **Maintainability** | Clear decomposition; lint/type gates; high test coverage. |
| **Portability** | Single image runs locally, on Docker Hub, and on Render. |
| **Compatibility** | Stable, versioned public API. |
| **Security** | Non-root, digest-pinned, no secrets, debug off. |
| **Performance** | Reasonable latency within the `MAX_NUMBERS` bound. |

## 10.2 Quality scenarios

### Correctness

- **Q1 — Fair sampling.** Given the default distribution and a large sample
  (e.g. `numbers=1000`), the observed histogram approximates the expected one
  and the Chi-Square test reports `is_null = true` at α = 0.05 the large
  majority of the time. *Verified by:* `tests/test_hypothesis.py`,
  `tests/test_core.py`.
- **Q2 — Zero-observation categories count.** A category with probability > 0
  that is never drawn still contributes to the Chi-Square statistic (explicit
  expected-category domain). *Verified by:* `ChiSquareTest.calc()` logic +
  `tests/test_hypothesis.py`.
- **Q3 — Both versions agree on contract.** `/api/v1` and `/api/v2` accept the
  same parameters and return the same response shape and status codes.
  *Verified by:* `tests/test_routing.py`.

### Reliability / robustness

- **Q4 — Predictable bad input.** `?numbers=abc`, a quantity outside
  `1..10000`, a length mismatch, a negative weight, or weights not summing to 1
  return **HTTP 400** with `{"error": ...}` — never a 500 or a crashed worker.
  *Verified by:* `app.handle_error` + `tests/test_routing.py`,
  `tests/test_endpoints.py`.
- **Q5 — Bounded work.** `MAX_NUMBERS = 10000` caps the cost of one request.
- **Q6 — Concurrency safety.** Stateless service + per-request generator means
  concurrent requests/workers never corrupt shared state.

### Maintainability

- **Q7 — Gates green.** `ruff check` + `ruff format --check` + `mypy` pass, and
  `pytest` meets the **≥ 85% coverage** gate. *Enforced by:*
  [`test_application.yml`](../../.github/workflows/test_application.yml).
- **Q8 — Thin handlers.** No business logic in `routing.py`; the service and
  core remain Flask-independent.

### Portability / compatibility

- **Q9 — Runs anywhere Docker runs.** `docker run -p 5000:5000
  braboj/randomgen` serves the API; the same image deploys on Render via
  `render.yaml`.
- **Q10 — API stability.** Existing `/api/v1` and `/api/v2` behavior never
  changes; new behavior is a new version.

### Security

- **Q11 — Least privilege & integrity.** Container runs as non-root `appuser`
  on a digest-pinned base image; CI gitleaks scan finds no secrets; debug is
  off in the image and in the local `flask run`.

### Performance

- **Q12 — Reasonable latency.** Within `MAX_NUMBERS`, generation is fast
  (V1 ≈ 3× faster than V2 per [solution.md](../solution.md) §10); the dominant
  hosted-demo latency is the Render free-tier cold start, not generation
  ([Section 11](11-risks-and-technical-debt.md)).
