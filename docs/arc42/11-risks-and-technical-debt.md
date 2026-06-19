# 11. Risks and Technical Debt

Known risks, limitations, and debt, with the mitigation or rationale for
accepting each.

## 11.1 Risks

| # | Risk | Impact | Mitigation / status |
|---|------|--------|---------------------|
| R1 | **Non-cryptographic randomness.** Sampling uses Python's `random` (Mersenne-Twister). | Misuse for security would be unsafe. | Explicitly out of scope and documented ([Section 1](01-introduction-and-goals.md), [Section 8](08-crosscutting-concepts.md)). Not a defect — a stated boundary. |
| R2 | **Render free-tier cold start.** Free instances spin down after ~15 min idle and cold-start ~30–60s. | First request after idle is slow. | Accepted for a zero-cost demo; documented in `render.yaml`, README, and [Section 7](07-deployment-view.md). |
| R3 | **No rate limiting / auth.** `GET`-only, but a caller can request up to `MAX_NUMBERS` per call repeatedly. | Possible resource use under load. | `MAX_NUMBERS = 10000` caps per-request cost; stateless design scales horizontally. Auth/throttling intentionally out of scope. |
| R4 | **Small-sample fairness.** The Chi-Square verdict is unreliable for tiny samples. | `is_null` may mislead for small `numbers`. | `DEFAULT_QUANTITY = 1000`; the home page and docs note that larger samples are more accurate ([solution.md](../history/solution.md) §8). |
| R5 | **Pinned base image drifts.** The digest-pinned Alpine base will age and accumulate CVEs. | Stale base image over time. | Pinning is deliberate for reproducibility; the pin must be bumped periodically (manual). |
| R6 | **Third-party CI actions.** `deploy_image.yml` uses `mr-smithers-excellent/docker-build-push@v7.0`. | Supply-chain exposure via a non-GitHub action. | Version-pinned; gitleaks scan in CI; secrets scoped to repo secrets. |

## 11.2 Technical debt

| # | Debt | Notes |
|---|------|-------|
| D1 | **`solution.md` journal is partly stale.** It references a planned `/api/v1/config` endpoint, a `version` field and `is_fair` key in the response, and port 8080 — none of which match the shipped code (per-request distribution, `is_null`, port 5000, no `version` field). It is a historical journal, not a current spec. |
| D2 | **scipy has no type stubs.** mypy runs with `ignore_missing_imports`, so calls into `scipy` are unchecked. |
| D3 | **V2 ignores the precomputed CDF.** `validate()` computes `_cumulative_probabilities`, which `RandomGenV2.next_num()` never uses (it calls `random.choices`). Minor wasted work, harmless. |
| D4 | **`Histogram._counter` initial type.** Initialized to `0` in `__init__` and later reassigned to a `Counter`; cosmetic inconsistency, no functional effect. |

## 11.3 Notable correctness safeguards (not debt)

- **V1 floating-point guard.** `RandomGenV1.next_num()` falls back to the last
  number when `random.random()` exceeds the final cumulative probability
  (which can be marginally below 1.0), preventing an implicit `None`.
- **Rounded probability sum.** `round(sum(probabilities), 3) == 1` tolerates
  floating-point error in weight validation.
- **`zip(..., strict=...)` usage.** Length mismatches in the Chi-Square domain
  are caught explicitly (`RandomGenMismatchError`) rather than silently
  truncated.
