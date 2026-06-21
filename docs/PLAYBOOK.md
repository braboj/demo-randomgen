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

The OpenAPI contract `src/randomgen/openapi.yaml` is the single source of
truth — edit it first, then implement to match (see ADR-016).

1. Edit the contract: update `src/randomgen/openapi.yaml` — the path,
   parameters, response schemas, and status codes. Keep the quantity limits and
   `info.version` in step with the code constants (a test enforces this).
2. Review it by rendering the spec at `/docs` (ReDoc), in Swagger UI, or via a
   Prism mock, before writing code.
3. Implement to match: add the service logic on `RandomGenRestApi` in
   `src/randomgen/endpoints.py` (and a generator in `src/randomgen/core.py` if
   new generation behavior is needed), then a thin route handler on the `bp`
   Blueprint in `src/randomgen/routing.py`.
4. For a behavior change, expose it under a new version path (`/api/v2/...`) —
   never alter an existing version's contract.
5. Test: add cases in `tests/test_endpoints.py` / `tests/test_routing.py`. The
   pin test (`tests/test_openapi.py`) and the Schemathesis contract test
   (`tests/integration/test_contract.py`) verify the implementation conforms to
   the updated contract.
6. Update the OpenAPI contract (`src/randomgen/openapi.yaml`) and the arc42 docs
   if the surface or architecture changed.

### 2.2 Add a new generator version

1. Implement `RandomGenVN` in `src/randomgen/core.py`.
2. Wire it to a new versioned route in `src/randomgen/routing.py`.
3. Add `tests/test_core.py` cases and a route test.

## 3. Quality

### 3.1 Tests (pytest)

Tests are tiered and auto-marked by directory (`tests/conftest.py`): top-level
`tests/*` are `unit`, `tests/integration/` is `integration`, `tests/e2e/` is
`e2e`. The default run is the fast gate (unit + integration); `e2e` is opt-in.

```bash
pytest                               # fast gate: unit + integration (excludes e2e)
pytest -m unit                       # just the unit tier
pytest tests/test_core.py -k <name>  # a single module / case

# End-to-end tier (real container via Testcontainers on a Podman/Docker
# backend, plus a Playwright browser test). One-time setup, then run:
pip install -e ".[e2e]" && playwright install chromium
pytest -m e2e
```

### 3.2 Lint & type-check (ruff + mypy)

```bash
ruff check .                         # lint (E9/F-series included)
ruff format --check .                # formatting gate (run `ruff format .` to fix)
mypy                                 # static typing (config in pyproject.toml)
```

These are the exact checks `ci.yml` runs in CI alongside
`pytest` (with an 85% coverage gate).

### 3.3 Statistical validation (manual)

`src/randomgen/hypothesis.py` and the `scripts/plot_*.py` helpers can be run
locally to sanity-check that generated distributions match expectations.

### 3.4 Refresh UI snapshots

After a home-page UI change, regenerate the screenshots in
[ui-snapshots.md](reference/ui-snapshots.md):

```bash
pip install -e ".[e2e]" && playwright install chromium  # one-time
python scripts/capture_ui_snapshots.py                   # writes docs/assets/images/ui/*.png
```

## 4. Maintenance

### 4.1 Update dependencies

- Edit `pyproject.toml`: runtime deps under `[project.dependencies]`,
  tooling under `[project.optional-dependencies]` (`test` / `dev`).
  Helper-script deps stay in `scripts/requirements.txt`. Use
  compatible-release pins (`~=`) consistent with the existing entries.

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

```bash
# Bump [project].version in pyproject.toml, then:
git checkout main && git pull
git tag -a v0.4.0 -m "v0.4.0 — <milestone>"
git push origin v0.4.0
```

- **Image + Render deploy**: pushing the tag runs `cd.yml`, which
  builds and pushes `braboj/randomgen:latest` to Docker Hub and then POSTs the
  Render Deploy Hook, so the free web service pulls the new image and redeploys
  (AD-17). To redeploy the current `main` on demand, run the workflow manually
  (Actions → CD → Run workflow).
- **Local image**: `docker build -t braboj/randomgen .` then
  `docker run -p 5000:5000 braboj/randomgen`.
- **One-time setup**: create a Deploy Hook for the Render service and store its
  URL as the `RENDER_DEPLOY_HOOK_URL` GitHub Actions secret; ensure the service
  runs the image (re-sync the `render.yaml` blueprint). Docker Hub credentials
  are the `DOCKER_USERNAME` / `DOCKER_PASSWORD` secrets.
- **Docs**: arc42 architecture docs live as Markdown under `docs/arc42/`
  — no build or publish step; browse them on GitHub.
