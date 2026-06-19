# 3. Context and Scope

This section describes the partners RandomGen exchanges data with, and what is
in and out of scope.

## 3.1 Business context

The business context shows who uses RandomGen and what they exchange with it. A
person uses the web page, other programs use the API, and RandomGen itself
depends on no downstream systems.

```mermaid
flowchart LR
    user(["Developer / user<br/>(person)"])
    client["Client application<br/>(another program)"]
    rg["RandomGen"]

    user -->|"requests numbers via the web page"| rg
    rg -->|"shows numbers + fairness report"| user
    client -->|"requests numbers via the API"| rg
    rg -->|"returns numbers + fairness report (JSON)"| client
```

| Communication partner | Input | Output |
|-----------------------|-------|--------|
| Developer / user (person, via the web page) | Picks a quantity and, optionally, a distribution in the browser | The numbers and a Chi-Square fairness report, shown on the page |
| Client application (another program, via the API) | Requests a quantity and, optionally, a distribution | The numbers and a Chi-Square fairness report, as JSON |

## 3.2 Technical context

The technical context shows the runtime channels that connect RandomGen to its
environment, and which data travels over each. Build and deployment are out of
scope here.

```mermaid
flowchart LR
    user(["Developer / user<br/>(person)"])
    client["Client application"]
    platform["Container platform<br/>(Docker / Render)"]
    rg["RandomGen<br/>Flask + gunicorn"]

    user -->|"HTTPS GET (web page and API)"| rg
    client -->|"HTTPS GET (API /api/v1, /api/v2)"| rg
    platform -->|"HTTP GET /health (liveness)"| rg
```

| Channel | Protocol | Notes |
|---------|----------|-------|
| Public HTTP interface | HTTP/1.1, `GET` only | Serves the web page, the JSON API (`/api/v1`, `/api/v2`), and the published API docs. gunicorn on `0.0.0.0:${PORT:-5000}`; JSON via Flask `jsonify`. No TLS in-process (terminated by the platform). |
| Health | HTTP `GET /health` | Called by the container platform — the Docker `HEALTHCHECK` and Render's `healthCheckPath`; the platform also injects `$PORT`. No authentication. |

The full request/response contract — parameters, response shape, and status
codes — is published as an OpenAPI specification at `/openapi.json`, with an
interactive reference at `/docs`.

## 3.3 Scope

**In scope**

- The functional requirements in [Section 1](01-introduction-and-goals.md)
  (§1.1, FR01–FR07).
- A design-first OpenAPI contract as the single source of truth for the API.
- Architecture documentation and decision records.
- A deployable container image and a live demo deployment.
- An automated test suite and CI quality gates.

**Out of scope**

- Persistence, configuration storage, or per-client state (the service is
  stateless).
- Authentication / authorization / rate limiting.
- Cryptographically secure randomness.
- Continuous distributions or non-`GET` mutating operations.
