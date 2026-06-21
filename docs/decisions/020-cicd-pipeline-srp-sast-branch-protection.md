---
id: "AD-20"
status: Accepted
date: 2026-06-21
category: process
supersedes: []
superseded_by: []
---

# AD-20 — CI/CD pipeline: one gate per job, SAST, and enforced branch protection

## Context

The CI/CD workflows had grown organically. A single `build` job bundled install,
lint, format, type-check, test, and coverage, so a failure did not say which gate
broke and the job conflated several responsibilities. Delivery bundled the image
push and the Render hook in one job. The files were named after early purposes
(`test_application.yml`, `deploy_image.yml`) and every action was pinned to a
mutable tag. Two documented gate categories were missing: there was no build
verification and no static security analysis (SAST), although the quality-gates
model lists both as required. `main` was described as protected but no rule
enforced it, so a passing CI run did not actually block a merge.

## Decision

1. **One gate per job** — `ci.yml` fans out into `lint`, `typecheck`, `test`,
   `build`, `e2e`, and `secret-scan`; each MUST fail fast and report
   independently.
2. **Add the missing gates** — a `build` gate runs `python -m build` plus
   `twine check`, and CodeQL SAST runs in its own `codeql.yml` for Python (the
   elevated `security-events: write` permission stays scoped to that workflow).
3. **Single fan-in gate** — a `gate` job aggregates the six `ci.yml` gates so
   branch protection can require one context; a skipped or cancelled gate MUST
   NOT count as a pass.
4. **Split delivery** — `cd.yml` separates `publish` (build and push the image)
   from `deploy` (trigger the Render redeploy), with `deploy` gated on a
   successful `publish` (artifact promotion).
5. **Pin actions by SHA** — every action MUST be pinned to a commit SHA with a
   trailing version comment; Dependabot keeps the pins current.
6. **Rename and enforce** — the workflows are `ci.yml` / `cd.yml` (display names
   `CI` / `CD`), and branch protection on `main` requires the `gate` and CodeQL
   checks. Reviews are not required (the project has a single maintainer);
   `enforce_admins` stays off so a stuck check cannot lock the maintainer out.

## Alternatives considered

- **Keep the single bundled `build` job** — rejected; it hides which gate failed
  and violates one-responsibility-per-job.
- **CodeQL default setup instead of a workflow file** — rejected;
  pipeline-as-code keeps the definition in-repo, reviewed, and SHA-pinned.
- **Require pull-request reviews / `enforce_admins`** — deferred; both would
  block the solo maintainer's self-merge flow. They can be enabled later.

## Consequences

- CI reports six independent gates plus `gate` and CodeQL; `gate` is the single
  required status context, with CodeQL required alongside it.
- The build and SAST gates catch packaging and security regressions before
  merge (the build gate would have caught the PEP 639 license-metadata issue).
- The "main is protected" convention is now actually enforced; every PR — the
  release bump included — waits on green CI before the merge button unlocks.
- Live doc references were repointed (README badges, PLAYBOOK, arc42 §7/§10/§11/
  §12); arc42 §10 Q5/Q6/Q10/Q11 verified-by pointers reference the new tests.
- The single-responsibility-in-CI guidance is recorded in agent memory.
