# Playbook — RandomGen

Operational reference for common tasks. See `docs/ONBOARDING.md` for
first-time setup and `CLAUDE.md` for the full rule set.

## 1. Git workflow

```bash
git checkout main && git pull
git checkout -b feat/<scope>          # or fix/, chore/, docs/
# ...make changes, run pytest...
git commit -m "feat: <imperative summary>"
git push -u origin feat/<scope>
gh pr create --fill                   # open a PR; one approval + green CI
```

- One concern per PR. Never commit directly to `main` (protected).
- Never force-push; merge `main` into the branch if it is behind.
- After merge: `git branch -d feat/<scope>` and `git pull` on `main`.

## 2. Domain operations

### 2.1 Add or change an API endpoint (design-first)

The OpenAPI contract `src/randomgen/openapi.yaml` is the single source of truth:
edit it first, then implement to match (AD-16).

1. **Update the contract** (`openapi.yaml`) — the path, parameters, response
   schemas, and status codes. Keep the quantity limits and `info.version` in
   step with the code constants; a test enforces this.
2. **Review it before coding** — render the spec at `/docs` (ReDoc), in Swagger
   UI, or via a Prism mock.
3. **Implement to match**, keeping the route handler thin:
   - business logic → `RandomGenService` in `service.py`;
   - a new generator → `domain/core.py`, only if generation behaviour changes;
   - the thin handler → the relevant blueprint in `blueprints/`.
4. **Version any behaviour change** — expose it under a new path (`/api/v2/...`);
   never alter an existing version's contract.
5. **Test against the contract.** Add cases in `test_service.py` /
   `test_routing.py`. Two drift guards already enforce conformance: the pin test
   (`test_openapi.py`) and the Schemathesis contract test
   (`integration/test_contract.py`).
6. **Sync the arc42 docs** if the surface or architecture changed.

### 2.2 Add a new generator version

1. **Implement** `RandomGenVN` in `domain/core.py`.
2. **Register** it in the `API_VERSIONS` map (`versions.py`) as
   `'vN': RandomGenVN`; the factory builds the `/api/vN` blueprint from it.
3. **Test** — add `test_core.py` cases and a route test.

## 3. Quality

### 3.1 Tests (pytest)

Tests are tiered and auto-marked by directory (`tests/conftest.py`): top-level
`tests/*` are `unit`, `tests/integration/` is `integration`, `tests/e2e/` is
`e2e`. The default run is the fast gate (unit + integration); `e2e` is opt-in.

```bash
pytest                               # fast gate: unit + integration (excludes e2e)
pytest -m unit                       # just the unit tier
pytest tests/test_core.py -k <name>  # a single module / case

# Coverage, the same 85% gate CI enforces (config in pyproject [tool.coverage]):
pytest --cov=randomgen --cov-report=term-missing --cov-fail-under=85

# End-to-end tier (real container via Testcontainers on a Podman/Docker
# backend, plus a Playwright browser test). One-time setup, then run:
pip install -e ".[e2e]" && playwright install chromium
pytest -m e2e
```

The e2e tier needs a container backend; see §3.5 for the local Podman setup.

### 3.2 Lint & type-check (ruff + mypy)

```bash
ruff check .                         # lint (E9/F-series included)
ruff format --check .                # formatting gate (run `ruff format .` to fix)
mypy                                 # static typing (config in pyproject.toml)
```

`ci.yml` runs each of these as its own gate — `lint` (ruff), `typecheck`
(mypy), and `test` (`pytest`, 85% coverage) — plus a `build` gate that packages
and validates the distribution:

```bash
python -m build && twine check dist/*   # build wheel/sdist, validate metadata
```

`e2e`, `secret-scan` (gitleaks), and `codeql.yml` (Python SAST) round out CI; a
`gate` job fans them in — the required check on the branch-protected `main`.

### 3.3 Statistical validation (manual)

`src/randomgen/domain/hypothesis.py` and the `scripts/plot_*.py` helpers can be run
locally to sanity-check that generated distributions match expectations.

### 3.4 Refresh UI snapshots

After a home-page UI change, regenerate the screenshots in
[ui-snapshots.md](reference/ui-snapshots.md):

```bash
pip install -e ".[e2e]" && playwright install chromium  # one-time
python scripts/capture_ui_snapshots.py                   # writes docs/assets/images/ui/*.png
```

### 3.5 Local e2e container backend (Podman)

The e2e tier drives a real container through Testcontainers, so it needs a
Docker-compatible runtime. Podman is the recommended local backend: it is
rootless, runs no always-on daemon, and is the same backend CI uses — which
avoids the Docker Desktop hangs seen on Windows. Testcontainers reaches it over
a Docker-compatible API socket (`DOCKER_HOST`), with Ryuk (the reaper) disabled
because it does not run cleanly on rootless Podman.

Windows (PowerShell):

```powershell
# One-time: install and start the Podman machine.
# (Windows PowerShell chains commands with `;`, not `&&`.)
winget install RedHat.Podman
podman machine init
podman machine start
podman machine list            # confirm it actually started — not "stopped"

# Point Testcontainers at Podman's socket and disable Ryuk, then run e2e
$env:DOCKER_HOST = "npipe:////./pipe/podman-machine-default"
$env:TESTCONTAINERS_RYUK_DISABLED = "true"
pytest -m e2e
```

Confirm the pipe path for your machine with
`podman machine inspect --format '{{.ConnectionInfo.PodmanPipe.Path}}'` (Podman
Desktop can also expose `npipe:////./pipe/docker_engine` via its Docker
compatibility setting).

Linux/macOS use the Unix socket, mirroring the CI job
(`.github/workflows/ci.yml`):

```bash
podman system service --time=0 unix:///tmp/podman.sock &
export DOCKER_HOST=unix:///tmp/podman.sock
export TESTCONTAINERS_RYUK_DISABLED=true
pytest -m e2e
```

Docker also works — Testcontainers auto-detects it with no environment set — but
Docker Desktop on Windows has been prone to wedging, so Podman is preferred for
local e2e runs.

If `podman machine start` fails with `ssh error: machine not in running state`
or `\\.\pipe\...: All pipe instances are busy`, the fault is the host's WSL2
layer, not the env vars. Podman runs on WSL2, so a wedged WSL2 — the same fault
that hangs Docker Desktop — blocks it too; switching backends does not help.
Repair the host: `wsl --update` then reboot, confirm virtualization is enabled
(Task Manager → Performance → CPU), and quit Docker Desktop so it stops
contending for the Docker API pipe. The configuration above mirrors CI and is
correct; it only takes effect once the machine reaches a running state.

## 4. Maintenance

### 4.1 Update dependencies

Runtime dependencies live in `pyproject.toml` under `[project.dependencies]`,
tooling under `[project.optional-dependencies]` (the `test` / `dev` extras), and
helper-script dependencies in `scripts/requirements.txt`. Use compatible-release
pins (`~=`) consistent with the existing entries.

### 4.2 Update the templates submodule

```bash
git submodule update --remote docs/solid-ai-templates
git add docs/solid-ai-templates && git commit -m "chore: bump templates"
```

### 4.3 Decisions (ADRs)

Record significant architectural decisions as ADRs under `docs/decisions/`; the
canonical index is [arc42 §9](arc42/09-architecture-decisions.md).

- One decision per file, `NNN-slug.md` (zero-padded). The human id `AD-N`
  matches the file number and appears in the frontmatter `id` and the
  `# AD-N — Title` heading.
- Frontmatter is required (`id`, `status`, `date`, `category`, `supersedes`,
  `superseded_by`) — copy `docs/decisions/TEMPLATE.md` to start.
- `status` is `Proposed` / `Accepted` / `Superseded`; `category` is one of
  `architecture` / `api` / `tooling` / `deployment` / `docs` / `process`.
- ADRs are immutable once accepted: to change a decision, write a new ADR and
  set the old one's `status: Superseded` + `superseded_by`, with a reciprocal
  `supersedes`.

To add one: copy the template to the next free `NNN-slug.md`, fill it in, and
add a row to the [§9 index](arc42/09-architecture-decisions.md). The upstream
convention is `docs/solid-ai-templates/templates/base/core/docs.md`.

## 5. Release and deploy

Releases are tag-driven: pushing a `v*` tag runs `cd.yml`, which publishes the
Docker image and redeploys the Render demo (AD-17).

### 5.1 Cut a release

1. Bump `[project].version` in `pyproject.toml` (SemVer).
2. Reinstall locally — `pip install -e .` — so `__version__` refreshes. It is
   read from the installed package metadata, which an editable install only
   rewrites on reinstall, so the local home page and `/info` would otherwise
   report the old version. Built artifacts (wheel, Docker image, Render) install
   fresh and are always correct, so this only affects a local checkout.
3. Merge the bump to `main` via PR, then tag the release commit and push:

```bash
git checkout main && git pull
git tag -a vX.Y.Z -m "vX.Y.Z — <milestone>"
git push origin vX.Y.Z
```

Pushing the tag publishes `braboj/randomgen:latest` to Docker Hub and POSTs the
Render Deploy Hook. To redeploy the current `main` without a tag, run the
workflow manually (Actions → CD → Run workflow).

### 5.2 Run the image locally

```bash
docker build -t braboj/randomgen .
docker run -p 5000:5000 braboj/randomgen
```

### 5.3 Render deployment (one-time setup)

The CD `deploy` job needs three GitHub Actions secrets, set under the repository
Settings → Secrets and variables → Actions:

| Secret | Purpose |
|--------|---------|
| `DOCKER_USERNAME` | Docker Hub account that owns `braboj/randomgen`. |
| `DOCKER_PASSWORD` | Docker Hub access token (not the account password). |
| `RENDER_DEPLOY_HOOK_URL` | The Render service's Deploy Hook URL; CD POSTs it to trigger a redeploy. |

To wire Render up the first time:

1. Provision the service: in Render, choose New → Blueprint, connect the repo,
   and let it create the free web service from `render.yaml` (it runs the
   published image and uses the `/health` check).
2. Create a Deploy Hook in the service's Settings → Deploy Hook and copy the URL.
3. Store that URL as the `RENDER_DEPLOY_HOOK_URL` secret, and add the two
   `DOCKER_*` secrets so CD can push the image.

After this, every `v*` tag redeploys automatically — no manual step.

### 5.4 Docs

arc42 architecture docs are Markdown under `docs/arc42/` — no build or publish
step; browse them on GitHub.
