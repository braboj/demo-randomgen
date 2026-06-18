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
   `randomgen/endpoints.py` (and a generator in `randomgen/core.py` if
   new generation behavior is needed).
2. Add a thin route handler in `randomgen/routing.py` that parses input,
   calls the service method, and returns `jsonify(...)`.
3. For a behavior change, expose it under a new version path
   (`/api/v2/...`) — never alter an existing version's contract.
4. Add tests in `tests/test_endpoints.py` and `tests/test_routing.py`.
5. Update `docs/rest_api.md` and the MkDocs nav if the public API
   surface changed.

### 2.2 Add a new generator version

1. Implement `RandomGenVN` in `randomgen/core.py`.
2. Wire it to a new versioned route in `randomgen/routing.py`.
3. Add `tests/test_core.py` cases and a route test.

## 3. Quality

### 3.1 Tests (pytest)

```bash
pytest                               # full suite
pytest tests/test_core.py -k <name>  # a single module / case
```

### 3.2 Linting (flake8)

```bash
flake8 . --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

These are the exact checks `test_application.yml` runs in CI; the first
fails the build on syntax/undefined-name errors.

### 3.3 Statistical validation (manual)

`randomgen/hypothesis.py` and the `scripts/plot_*.py` helpers can be run
locally to sanity-check that generated distributions match expectations.

## 4. Maintenance

### 4.1 Update dependencies

- Edit `requirements.txt` (runtime), `tests/requirements.txt` (tests),
  or `scripts/requirements.txt` (helper scripts). Use compatible-release
  pins (`~=`) consistent with the existing entries.

### 4.2 Update the templates submodule

```bash
git submodule update --remote docs/solid-ai-templates
git add docs/solid-ai-templates && git commit -m "chore: bump templates"
```

### 4.3 Decisions

- Record significant architectural decisions as ADRs under
  `docs/decisions/` (`NNN-slug.md`) — see
  `docs/solid-ai-templates/templates/base/core/docs.md`.

## 5. Release and deploy

```bash
# Bump VERSION in setup.py, then:
git checkout main && git pull
git tag -a v0.2.0 -m "v0.2.0 — <milestone>"
git push origin v0.2.0
```

- **Docker image**: `deploy_image.yml` builds and publishes
  `braboj/randomgen`. Build locally with `docker build -t
  braboj/randomgen .` and run with `docker run -p 5000:5000
  braboj/randomgen`.
- **Docs site**: `deploy_pages.yml` builds the MkDocs site and deploys
  it to GitHub Pages. Preview locally with `mkdocs serve`.
