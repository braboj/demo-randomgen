# RandomGen UI snapshots

Captured in Chromium (Playwright). The interactive home page lets you pick a
generator (v1/v2), a discrete distribution — or a one-click preset (Uniform,
Skewed, Bimodal, Near-degenerate), added in v0.9.0 — and a sample size, then
renders the Chi-Square verdict and an expected-vs-observed histogram. Every
state below is covered by the Playwright e2e test (`tests/e2e/test_ui.py`).

> Note: the screenshots below were captured at v0.8.0 and do not yet show the
> v0.9.0 preset bar; they will be refreshed.

## Initial state

![Initial state](images/ui/01_initial.png)

## Results — v1 (built-in distribution)

![v1 results](images/ui/02_v1_results.png)

## Results — v2 (custom distribution `1:0.5,2:0.5`)

![v2 custom distribution](images/ui/03_v2_custom.png)

## Error state (malformed `dist`)

![Error state](images/ui/04_error.png)

## Mobile / responsive

![Mobile layout](images/ui/05_mobile.png)
