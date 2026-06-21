# 11. Risks and Technical Debt

Known risks, limitations, and debt, with the mitigation or rationale for
accepting each.

## 11.1 Risks

| # | Risk | Impact | Mitigation / status |
|---|------|--------|---------------------|
| R1 | **Non-cryptographic randomness.** Sampling uses Python's `random` (Mersenne-Twister). | Misuse for security would be unsafe. | Explicitly out of scope and documented ([Chapter 1](01-introduction-and-goals.md), [Chapter 8](08-crosscutting-concepts.md)). Not a defect — a stated boundary. |
| R2 | **Render free-tier cold start.** Free instances spin down after ~15 min idle and cold-start ~30–60s. | First request after idle is slow. | Accepted for a zero-cost demo; documented in `render.yaml`, README, and [Chapter 7](07-deployment-view.md). |
| R3 | **No rate limiting / auth.** `GET`-only, but a caller can request up to `MAX_NUMBERS` per call repeatedly. | Possible resource use under load. | `MAX_NUMBERS = 10000` caps per-request cost; stateless design scales horizontally. Auth/throttling intentionally out of scope. |
| R4 | **Small-sample fairness.** The Chi-Square verdict is unreliable for tiny samples. | `is_null` may mislead for small `numbers`. | `DEFAULT_QUANTITY = 1000`; the home page and docs note that larger samples are more accurate ([solution.md](../history/solution.md) §8). |
| R5 | **Pinned base image drifts.** The digest-pinned Alpine base will age and accumulate CVEs. | Stale base image over time. | Pinning is deliberate for reproducibility; the pin must be bumped periodically (manual). |
| R6 | **Third-party CI actions.** `deploy_image.yml` uses `mr-smithers-excellent/docker-build-push@v7.0`. | Supply-chain exposure via a non-GitHub action. | Version-pinned; gitleaks scan in CI; secrets scoped to repo secrets. |

## 11.2 Technical debt

Technical debt is tracked as GitHub issues labeled `tech-debt`, so the status
stays live and this section cannot go stale. Each badge shows the ticket's
current state; the
[full live list](https://github.com/braboj/demo-randomgen/issues?q=is%3Aissue+label%3Atech-debt)
is the source of truth.

| # | Debt | Status |
| --- | --- | --- |
| D1 | `solution.md` design journal is partly stale | [![D1](https://img.shields.io/github/issues/detail/state/braboj/demo-randomgen/145)](https://github.com/braboj/demo-randomgen/issues/145) |
| D2 | scipy ships no type stubs | [![D2](https://img.shields.io/github/issues/detail/state/braboj/demo-randomgen/146)](https://github.com/braboj/demo-randomgen/issues/146) |
| D3 | RandomGenV2 ignores the precomputed CDF | [![D3](https://img.shields.io/github/issues/detail/state/braboj/demo-randomgen/147)](https://github.com/braboj/demo-randomgen/issues/147) |
| D4 | `Histogram._counter` initial type inconsistency | [![D4](https://img.shields.io/github/issues/detail/state/braboj/demo-randomgen/148)](https://github.com/braboj/demo-randomgen/issues/148) |
