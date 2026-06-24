---
id: "AD-29"
status: Accepted
date: 2026-06-24
category: security
supersedes: []
superseded_by: []
---

# AD-29 — Supply-chain controls: SCA gate, image/config scan, SBOM, monitored base

## Context

The project's own vendored `devsecops.md` mandates artifact-side supply-chain
controls — dependency scanning on every build, image/IaC scanning, and an SBOM
per release — yet none were present, and the digest-pinned base image
(`python:3.12.2-alpine3.19`, ~2024-03) was stale and unmonitored. The v0.19.0
360 review flagged all four gaps (F22–F25). The published Docker image is the
project's primary distribution artifact, so these controls belong on the
delivery path, not only the source.

The constraint particular to this repo: CD (`cd.yml`) is tag-triggered, so any
job added there cannot be exercised on a pull request before it runs for real on
a release. A scanning step that fails would therefore first surface mid-release.

## Decision

1. **SCA gate in CI.** `ci.yml` gains an `sca` job running `pip-audit` over the
   resolved runtime dependencies, wired into the `gate` fan-in so it is required
   for merge. `pip` and `setuptools` are upgraded first so the audit reports on
   the project's dependencies, not the runner's bundled tooling.

2. **Advisory image + config scan in CD, by construction unable to block a
   release.** A `scan` job runs after `publish` but is **not** a dependency of
   `deploy`, carries `continue-on-error: true`, and runs Trivy with
   `exit-code: '0'`. It scans the published image (`trivy image`) and the
   Dockerfile (`trivy config`) at `HIGH,CRITICAL`. Reporting is the goal;
   an unpatchable upstream-base CVE — or a tooling hiccup in a tag-only job that
   could not be tested on the PR — must never wedge `publish → deploy`.

3. **SBOM as a build artifact, and a Release asset.** The same job emits an
   SPDX SBOM with Syft and uploads it via `actions/upload-artifact`. Once AD-30
   added a GitHub Release per tag, the job also attaches the SBOM to that
   Release (`gh release upload --clobber`), so each version carries a durable
   SBOM beyond the build artifact's run retention. The upload is guarded and
   advisory — a missing Release or SBOM never fails the job, keeping the Release
   record off the scan path (AD-30). `anchore/sbom-action`'s own
   `upload-artifact`/`upload-release-assets` (both default-on) are disabled so
   these two explicit steps are the single source for each, with controlled,
   version-stable names; left on, the action double-emits the SBOM.

4. **Monitored, current base image.** `dependabot.yml` gains the `docker`
   ecosystem so the `FROM` digest is tracked, and the base is bumped to the
   current `python:3.12.13-alpine3.24`, digest-pinned. The e2e job builds the
   Dockerfile, so a base bump is validated on the PR that makes it.

All new CI actions are SHA-pinned (trivy-action, sbom-action, upload-artifact),
matching the AD-20 pinning convention.

## Alternatives considered

- **A blocking image scan** (`exit-code: 1`) — rejected: an Alpine/Python base
  routinely carries CVEs with no available fix, which would block every release
  for issues the project cannot patch. SCA on first-party-chosen dependencies
  (where a fix is actionable via Dependabot) gates; base-image scanning informs.
- **SBOM as a GitHub Release asset** — originally deferred (there was no GitHub
  Release in the CD flow, so the artifact alone satisfied "an SBOM exists per
  release"). AD-30 then added a Release per tag, which unblocked it; implemented
  in decision 3 above (#267) rather than building release-creation machinery
  here just for one asset.
- **Manual base-image bumps only** — rejected: that is exactly how the base went
  ~2 years stale. Dependabot's docker ecosystem keeps the digest fresh; the
  manual bump in this change just resets the clock.

## Consequences

- Merges now require a clean `pip-audit`; a newly-disclosed CVE in a runtime
  dependency turns the `gate` red until the dependency is bumped (which
  Dependabot already proposes) — the intended SCA behaviour.
- The release path gained observability (image/config findings, an SBOM) with
  zero new ways to fail: the `scan` job is advisory and off the `deploy` path.
  The trade-off is that a real, fixable image finding will not stop a release on
  its own — it must be read from the run and acted on deliberately.
- The base image is current and monitored; future drift is a Dependabot PR, not
  a review finding.
