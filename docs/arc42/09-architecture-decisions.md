# 9. Architecture Decisions

The significant architectural decisions are recorded as individual
Architecture Decision Records (ADRs) under
[`docs/decisions/`](../decisions/). This chapter is the **index**: each
row links to the full record. The decisions are consistent with the
constraints in [Chapter 2](02-architecture-constraints.md) and the
strategy in [Chapter 4](04-solution-strategy.md).

When you add an ADR, add a row here (see
[`docs/decisions/README.md`](../decisions/README.md)).

| ID | Decision | Category | Status |
| --- | --- | --- | --- |
| AD-1 | [src layout + application factory + blueprint](../decisions/001-src-layout-app-factory-blueprint.md) | architecture | Accepted |
| AD-2 | [pyproject.toml + ruff/mypy over setup.py + flake8](../decisions/002-pyproject-ruff-mypy.md) | tooling | Accepted |
| AD-3 | [Per-request, stateless distribution](../decisions/003-per-request-stateless-distribution.md) | architecture | Accepted |
| AD-4 | [dist value:probability pairs alongside legacy parameters](../decisions/004-dist-value-probability-pairs.md) | api | Accepted |
| AD-5 | [Versioned API as a stable public contract](../decisions/005-versioned-api-contract.md) | api | Accepted |
| AD-6 | [Two generator implementations behind one interface](../decisions/006-two-generators-one-interface.md) | architecture | Accepted |
| AD-7 | [Chi-Square goodness-of-fit reporting via scipy](../decisions/007-chi-square-goodness-of-fit.md) | architecture | Accepted |
| AD-8 | [gunicorn + hardened Docker image](../decisions/008-gunicorn-hardened-docker.md) | deployment | Accepted |
| AD-9 | [Render free web service for a zero-cost demo](../decisions/009-render-free-demo.md) | deployment | Superseded by AD-17 |
| AD-10 | [arc42 architecture documentation](../decisions/010-arc42-documentation.md) | docs | Accepted |
| AD-11 | [Inline the enforced end-of-session checklist](../decisions/011-inline-end-of-session-checklist.md) | process | Accepted |
| AD-12 | [Dedicated docs/decisions/ folder with arc42 §9 as the index](../decisions/012-dedicated-adr-folder.md) | docs | Accepted |
| AD-13 | [Code-built OpenAPI spec served as interactive docs at /docs](../decisions/013-openapi-docs-endpoint.md) | docs | Superseded by AD-16 |
| AD-14 | [Adopt the solid-ai-templates issue label standard](../decisions/014-adopt-issue-label-standard.md) | process | Accepted |
| AD-15 | [Reorganize the docs/ folder by purpose](../decisions/015-docs-folder-reorganization.md) | docs | Accepted |
| AD-16 | [Design-first OpenAPI as the single source of truth](../decisions/016-design-first-openapi.md) | api | Accepted |
| AD-17 | [Deploy the published image to Render via a deploy hook](../decisions/017-render-image-deploy-hook.md) | deployment | Accepted |
