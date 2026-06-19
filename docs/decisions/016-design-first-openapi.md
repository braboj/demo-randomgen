---
id: "AD-16"
status: Accepted
date: 2026-06-19
category: api
supersedes: ["AD-13"]
superseded_by: []
---

# AD-16 — Design-first OpenAPI as the single source of truth

## Context

The API contract was described in two places that could drift apart: a spec
built in Python code (`build_spec()` in `openapi.py`, served at `/openapi.json`
and rendered at `/docs`) and a hand-written `rest_api.md`. Building the spec
from code means the contract is a side effect of the implementation rather than
an agreed artifact, and the prose reference had nothing keeping it in step.

## Decision

1. **The contract is a hand-authored OpenAPI 3.1 document** — `openapi.yaml`,
   bundled in the package — and is the single source of truth (design-first).
2. **The service serves it verbatim** at `/openapi.json`, still rendered as
   ReDoc at `/docs`. The code-building `build_spec()` is removed.
3. **A test pins the contract to the code** — the spec's quantity limits and
   version must equal the live constants (`MAX_NUMBERS`, `DEFAULT_QUANTITY`,
   `__version__`), so the two cannot silently diverge.
4. **Contract tests verify conformance** — the running service is checked
   against the spec in CI.
5. **The prose reference `rest_api.md` is removed** — `/openapi.json` and the
   ReDoc rendering at `/docs` are the human-facing reference. arc42 §3.2 and the
   other docs link to `openapi.yaml` (or `/docs`) directly.

```
   openapi.yaml  (single source of truth, hand-authored)
        |  served verbatim
   /openapi.json  --->  /docs (ReDoc)
        |  verified by
   pin test (limits/version == code)  +  contract tests (CI)
```

## Alternatives considered

- **Keep the code-built spec (AD-13)** — rejected; the contract should be
  designed and agreed, not emitted as a by-product of the code.
- **Hybrid: author the YAML but keep `build_spec()` with a CI diff gate** —
  rejected; two artifacts to keep in lockstep for no gain over serving the YAML.
- **Keep `rest_api.md` as a parallel hand-written contract** — rejected; a
  prose contract with nothing enforcing it is exactly the drift this removes.

## Consequences

- A YAML parser (`pyyaml`) becomes a runtime dependency, and `openapi.yaml`
  ships in the wheel via `package-data`.
- Releases now update the version in `pyproject.toml` and `openapi.yaml`
  together; the pin test catches a miss.
- Changing the API means editing `openapi.yaml` first, then implementing to it
  — see the "change the API contract" procedure in `docs/PLAYBOOK.md`.
