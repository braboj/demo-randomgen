---
id: "AD-17"
status: Accepted
date: 2026-06-19
category: deployment
supersedes: ["AD-9"]
superseded_by: []
---

# AD-17 — Deploy the published image to Render via a deploy hook

## Context

The free Render demo was configured to build the image from the repository
Dockerfile and auto-deploy on commit (AD-9). In practice the demo lagged the
released code — it kept serving an older version — because the commit-based
auto-deploy did not fire reliably, and nothing in CI made a deploy an explicit,
observable step. Separately, the release workflow already builds and pushes the
image to Docker Hub, so Render was rebuilding the same artifact a second time.

## Decision

1. **Render runs the published image** — `render.yaml` uses `runtime: image`
   with `docker.io/braboj/randomgen:latest`, the artifact built and pushed by
   `deploy_image.yml`. Render no longer rebuilds from the Dockerfile.
2. **A release triggers the deploy** — after pushing the image (on a version
   tag, or a manual `workflow_dispatch`), `deploy_image.yml` POSTs a Render
   Deploy Hook, so Render pulls the new image and redeploys.
3. **The deploy hook URL is a secret** — `RENDER_DEPLOY_HOOK_URL`; the CI step
   is skipped (and the workflow still succeeds) when it is absent.

```
   git tag vX.Y.Z
        |
   deploy_image.yml: build + push braboj/randomgen:latest
        |
   POST $RENDER_DEPLOY_HOOK_URL
        |
   Render pulls :latest and redeploys  --->  /health
```

## Alternatives considered

- **Keep building from the repo on commit (AD-9)** — rejected; it deployed
  unreliably and rebuilt an artifact CI already produces.
- **Deploy on every green `main` commit** — rejected; redeploys on docs-only
  commits and is noisier than release-driven deploys for a demo.
- **Pin Render to an immutable digest per release** — deferred; `:latest` plus
  a deploy on each release is enough for a zero-cost demo.

## Consequences

- A one-time setup is required: create a Render Deploy Hook for the service and
  store its URL as the `RENDER_DEPLOY_HOOK_URL` GitHub Actions secret; re-sync
  the blueprint so the service runs the image rather than building from the repo.
- Releasing is the single deploy trigger; re-running `deploy_image.yml`
  manually (`workflow_dispatch`) deploys the current `main` build on demand.
- The release procedure in `docs/PLAYBOOK.md` section 5 documents the flow.
