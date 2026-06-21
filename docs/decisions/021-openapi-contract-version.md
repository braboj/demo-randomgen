---
id: "AD-21"
status: Accepted
date: 2026-06-21
category: api
supersedes: []
superseded_by: []
---

# AD-21 — OpenAPI info.version is the contract version, decoupled from the package version

## Context

The served OpenAPI document's `info.version` had been hand-copied to match the
package version, and a later change injected `__version__` into it at serve time
so a release would not have to edit the version in two files. But the OpenAPI
specification defines `info.version` as the version of the API document, which is
distinct from the implementation version. Tying it to the package version
conflates the two and churns the contract version on package patches that do not
touch the contract. The API is already versioned by path (`/api/v1`, `/api/v2`),
so the contract has its own cadence.

## Decision

1. **The contract version is independent.** `openapi.yaml` `info.version` is the
   version of the API contract, maintained by hand in the YAML and decoupled from
   the package version in `pyproject.toml`. `load_spec()` MUST NOT overwrite it.
2. **Scheme.** major = the highest `/api/vN` generation served (`2.0.0` today,
   since `/api/v2` exists); minor = an additive change to the documented surface
   (a new endpoint or optional parameter, e.g. `/health`); patch = clarifications
   or fixes with no surface change. The next major (`3.0.0`) lands with
   `/api/v3`.
3. **Drift guard.** The contract test pins the documented quantity limits to the
   code constants and asserts every `/api` route is documented; it no longer pins
   `info.version` to the package version (only that the required field is
   present).

## Alternatives considered

- **Inject the package version** (the prior approach) — rejected; it conflates
  the contract and implementation versions and moves the contract version on
  package patches that do not change the contract.
- **Strict document semver from `1.0.0`** — rejected as less intuitive here:
  readers expect the document version to track the visible `/api/vN` generation.
  This makes `2.0.0` a house convention (major mirrors the path generation), not
  the default additive-vs-breaking reading — `/api/v2` is a parallel
  implementation of the same contract as v1, not a breaking successor.

## Consequences

- A routine release edits only `pyproject.toml` (plus the tag); `info.version`
  changes only when the contract does.
- The served `/openapi.json` reports `2.0.0` while the package is at `0.10.0` —
  intended, and explained here.
- `openapi.py` no longer imports `__version__`; the drift-guard test drops the
  version assertion (the limit pins and route coverage stay).
