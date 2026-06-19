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

### 2.1 Add or change an API endpoint

1. Add the endpoint logic as a method on `RandomGenRestApi` in
   `src/randomgen/endpoints.py` (and a generator in `src/randomgen/core.py`
   if new generation behavior is needed).
2. Add a thin route handler on the `bp` Blueprint in
   `src/randomgen/routing.py` that parses input, calls the service method,
   and returns `jsonify(...)`.
3. For a behavior change, expose it under a new version path
   (`/api/v2/...`) — never alter an existing version's contract.
4. Add tests in `tests/test_endpoints.py` and `tests/test_routing.py`.
5. Update `docs/reference/rest_api.md` if the public API surface changed, and the
   arc42 docs under `docs/arc42/` if the architecture changed.

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

These are the exact checks `test_application.yml` runs in CI alongside
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

### 4.3 Decisions

- Record significant architectural decisions as ADRs under
  `docs/decisions/` (`NNN-slug.md`). Copy `docs/decisions/TEMPLATE.md`,
  fill it in, then add a row to the
  [arc42 §9 index](arc42/09-architecture-decisions.md). See
  `docs/decisions/README.md` for the conventions (and
  `docs/solid-ai-templates/templates/base/core/docs.md` upstream).

## 5. Release and deploy

```bash
# Bump [project].version in pyproject.toml, then:
git checkout main && git pull
git tag -a v0.4.0 -m "v0.4.0 — <milestone>"
git push origin v0.4.0
```

- **Image + Render deploy**: pushing the tag runs `deploy_image.yml`, which
  builds and pushes `braboj/randomgen:latest` to Docker Hub and then POSTs the
  Render Deploy Hook, so the free web service pulls the new image and redeploys
  (AD-17). To redeploy the current `main` on demand, run the workflow manually
  (Actions → Deploy Image → Run workflow).
- **Local image**: `docker build -t braboj/randomgen .` then
  `docker run -p 5000:5000 braboj/randomgen`.
- **One-time setup**: create a Deploy Hook for the Render service and store its
  URL as the `RENDER_DEPLOY_HOOK_URL` GitHub Actions secret; ensure the service
  runs the image (re-sync the `render.yaml` blueprint). Docker Hub credentials
  are the `DOCKER_USERNAME` / `DOCKER_PASSWORD` secrets.
- **Docs**: arc42 architecture docs live as Markdown under `docs/arc42/`
  — no build or publish step; browse them on GitHub.
