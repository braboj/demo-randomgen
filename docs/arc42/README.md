# RandomGen — Architecture Documentation (arc42)

This is the architecture documentation for **RandomGen**, a small Flask 3.x
REST API (Python 3.12+) that draws random numbers from a configurable
**discrete distribution** and reports goodness-of-fit with a **Chi-Square
test** (via `scipy`). The service is stateless, pure-compute, and ships as a
hardened Docker image served by gunicorn. It is structured following the
[arc42](https://arc42.org) template — one document per chapter.

For the user-facing overview and quick start, see the project
[README](../../README.md). For project conventions and guard-rails, see
[CLAUDE.md](../../CLAUDE.md). For the original task and the design journal, see
[problem.md](../history/problem.md) and [solution.md](../history/solution.md). The HTTP
contract is defined by the [OpenAPI document](../../src/randomgen/openapi.yaml)
(served at `/openapi.json`, rendered at `/docs`).

## Table of contents

1. [Introduction and Goals](01-introduction-and-goals.md)
2. [Architecture Constraints](02-architecture-constraints.md)
3. [Context and Scope](03-context-and-scope.md)
4. [Solution Strategy](04-solution-strategy.md)
5. [Building Block View](05-building-block-view.md)
6. [Runtime View](06-runtime-view.md)
7. [Deployment View](07-deployment-view.md)
8. [Crosscutting Concepts](08-crosscutting-concepts.md)
9. [Architecture Decisions](09-architecture-decisions.md)
10. [Quality Requirements](10-quality-requirements.md)
11. [Risks and Technical Debt](11-risks-and-technical-debt.md)
12. [Glossary](12-glossary.md)
