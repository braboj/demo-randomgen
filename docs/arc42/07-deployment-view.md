# 7. Deployment View

RandomGen is distributed as a single self-contained Docker image. The same
image runs locally, is published to Docker Hub, and is deployed as a free
Render web service. There is no database, no shared storage, and no clustering
to coordinate.

## 7.1 Deployment diagram

```mermaid
flowchart TB
    subgraph build["Build & Publish (CI)"]
        repo["GitHub repo<br/>braboj/randomgen"]
        ci_img["deploy_image.yml<br/>(on version tags)"]
        repo --> ci_img
    end

    dockerhub[("Docker Hub<br/>braboj/randomgen:latest + tag")]
    ci_img -->|build & push| dockerhub

    subgraph image["Docker image (python:3.12.2-alpine3.19, digest-pinned)"]
        gunicorn["gunicorn<br/>bind 0.0.0.0:$PORT (default 5000)"]
        app["randomgen.app:create_app()"]
        gunicorn --> app
        hc["HEALTHCHECK → GET /health"]
    end
    dockerhub -. "image contents" .- image

    subgraph local["Local / any Docker host"]
        d_run["docker run -p 5000:5000"]
    end
    dockerhub -->|docker pull| d_run
    d_run --> image

    subgraph render["Render (free web service, region frankfurt)"]
        r_svc["web service<br/>runtime: image<br/>pulls braboj/randomgen:latest<br/>healthCheckPath: /health"]
    end
    dockerhub -->|pull :latest| render
    ci_img -->|deploy hook POST on tag| render

    client["Client / health probe"] -->|HTTPS / HTTP| render
    client -->|HTTP :5000| local
```

## 7.2 Infrastructure elements

| Element | Details |
|---------|---------|
| **Base image** | `python:3.12.2-alpine3.19`, **pinned by digest** (`@sha256:c7eb5c…`) for reproducibility and integrity. |
| **App install** | `pip install --no-cache-dir .` from `pyproject.toml` (build inputs copied first to keep the layer cached). |
| **User** | Non-root `appuser` (`adduser -D appuser`; `USER appuser`). |
| **Process** | `gunicorn --bind "0.0.0.0:${PORT:-5000}" "randomgen.app:create_app()"` (shell form so `${PORT}` expands at runtime). |
| **Port** | `ENV PORT=5000`, `EXPOSE 5000`; PaaS platforms inject `$PORT`. |
| **Health** | `HEALTHCHECK` every 30s (`timeout 3s`, `start-period 5s`, `retries 3`) hitting `/health` via `python -c urllib.request` (no `curl` in the base image). |

## 7.3 Deployment targets

### Local / any Docker host

```bash
docker pull braboj/randomgen:latest
docker run -p 5000:5000 braboj/randomgen:latest
```

`flask --app "randomgen.app:create_app" run` is a **local-dev convenience
only** (Flask's built-in server, debug off); production always serves via
gunicorn inside the image.

### Docker Hub (`braboj/randomgen`)

[`deploy_image.yml`](../../.github/workflows/deploy_image.yml) builds and pushes
the image on **version tags** (`tags: '*'`), tagging the build and updating
`latest` (`addLatest: true`). Credentials come from the `DOCKER_USERNAME` /
`DOCKER_PASSWORD` repository secrets.

### Render (free web service)

[`render.yaml`](../../render.yaml) is a blueprint: `type: web`, `runtime: image`
running `docker.io/braboj/randomgen:latest`, `plan: free`, `region: frankfurt`,
`healthCheckPath: /health`. Render injects `$PORT`, which the image's gunicorn
`CMD` binds, so no extra configuration is needed.

A release drives the deploy: after [`deploy_image.yml`](../../.github/workflows/deploy_image.yml)
pushes the image, it POSTs a Render Deploy Hook (the `RENDER_DEPLOY_HOOK_URL`
secret) so Render pulls the new `latest` and redeploys (see AD-17).

> **Operational note:** free Render instances **spin down after ~15 minutes of
> inactivity** and **cold-start (~30–60s)** on the next request — expected for a
> zero-cost demo. This is the dominant availability characteristic of the
> hosted demo (see [Chapter 11](11-risks-and-technical-debt.md)).

## 7.4 Scaling notes

Because the service is **stateless**, it scales horizontally by running more
gunicorn workers or more container replicas — no coordination or sticky
sessions are required. The only per-request bound is `MAX_NUMBERS = 10000`,
which caps the CPU/memory cost of a single call.
