# Development Journal — RandomGen

Continuity log for agent-assisted development. Newest entries at the
bottom. Link to ADRs for decisions and to issues for task tracking — do
not duplicate the data model (it lives in `randomgen/`).

## Architecture overview

- **Service**: Flask REST API built by a `create_app()` factory
  (`src/randomgen/app.py`) that registers a web blueprint and one API blueprint
  per version from the registry (`src/randomgen/blueprints/`,
  `src/randomgen/versions.py`), over a stateless service (`service.py`) and a
  pure-compute random-number generator (`src/randomgen/domain/core.py`). No database. A
  Jinja home-page UI (`templates/` + `static/`) exercises the API.
- **Build/quality**: `pyproject.toml` (PEP 621, src layout); `ruff` +
  `mypy` + tiered `pytest` (unit / integration / e2e).
- **Distribution**: Docker image `braboj/randomgen`; free Render demo via
  `render.yaml`; architecture documented with arc42 under `docs/arc42/`.
- **Quality conventions**: vendored under `docs/solid-ai-templates/`
  (git submodule), referenced from `CLAUDE.md` (hybrid model).

---

### Session 1 — Vendor templates and generate agent context

- Tool: Claude Code (Opus 4.8)
- Added `docs/solid-ai-templates` as a git submodule.
- Added a root `.gitignore` and `.gitattributes`; removed the local
  `.idea/` directory.
- Generated `CLAUDE.md` (hybrid model) from the `stack-flask` template
  dependency chain, plus `docs/ONBOARDING.md`, `docs/PLAYBOOK.md`, and
  this journal.
- Noted divergences from template defaults (flat package layout,
  module-level Flask `app`, `setup.py`, flake8/pytest) in `CLAUDE.md`
  section 2.4.

---

### Session 2 — Modernization (v0.4.0 → v0.8.0)

- Tool: Claude Code (Opus 4.8). Planned as five GitHub milestones
  (v0.4.0–v0.8.0) with issues #70–#89, delivered as five stacked PRs
  #90–#94 (merge in version order). Retired CLAUDE.md §2.4 — the project
  now follows the modern template layout.
- **v0.4.0 (#90)** — src layout (`src/randomgen/`), a `create_app()`
  factory with a route Blueprint, `pyproject.toml` replacing
  `setup.py`/`requirements*.txt`, `ruff` and `mypy` replacing flake8,
  Dockerfile/CI updated, and `$PORT` honored.
- **v0.5.0 (#91)** — `render.yaml` blueprint for a free Render web-service
  demo (cold-starts after idle).
- **v0.6.0 (#92)** — arc42 architecture docs under `docs/arc42/` (12
  sections + Mermaid diagrams); removed MkDocs and the Pages workflow.
- **v0.7.0 (#93)** — single Jinja home-page UI + CSS/JS exercising the API
  (served via `render_template`; assets packaged in the wheel).
- **v0.8.0 (#94)** — tiered tests (unit / integration / e2e), Testcontainers
  e2e on a **Podman** backend, Playwright browser e2e, and a CI `e2e` job.
  The Playwright test caught a real CSS bug (`[hidden]` overridden).

#### Ship & operate (post-merge)

- Merged all five PRs into `main` in version order. #91/#93 show CLOSED (not
  MERGED): a GitHub mergeability-computation race during the back-to-back
  stack merge blocked their direct merge, but because the branches were
  stacked their commits landed via #92/#94. Verified `main` green
  (ruff 0.15 + mypy 2.1, 175 unit+integration tests; CI `e2e` job passed).
- Tagged **`v0.8.0`** → `deploy_image.yml` published the image to Docker Hub.
- Connected the Render Blueprint; live demo at
  <https://randomgen-llyc.onrender.com/> (smoke-tested: health, both API
  versions, error contract, UI + static assets).
- Merged the Dependabot dev-tooling bump (#95: ruff 0.14→0.15, mypy 1.18→2.1,
  setuptools build req) after confirming the gates pass on `main`.
- Deleted all feature branches; `image_deployment.yml` confirmed as a long-
  renamed legacy (now `deploy_image.yml`) — no action needed.

---

### Session 3 — Documentation & session-protocol cleanup

- Tool: Claude Code (Opus 4.8). One theme: tighten the docs and the
  agent session protocol after the v0.8.0 ship. No code/behavior change;
  all PRs are docs/chore.
- **Journal catch-up (#97)** — recorded the post-merge "ship & operate"
  steps (tag, Docker Hub publish, Render demo, Dependabot #95) that closed
  out session 2.
- **Session protocol (#98)** — inlined the full enforced end-of-session
  checklist into [CLAUDE.md](../CLAUDE.md) §6.3 (14 items, "print and
  execute sequentially, do not summarize"), replacing a lossy 4-bullet
  paraphrase of `scope.md`. Recorded as **AD-11**; the upstream
  generation-fidelity defect is filed as `solid-ai-templates#498`
  (proposes a reusable `wrap-up` loader).
- **Drop CONTRIBUTING.md (#99, #100)** — removed the redundant
  `CONTRIBUTING.md`, folded a one-line Contributing pointer to CLAUDE.md
  into the README, and dropped its stale reference from
  [solution.md](history/solution.md). Single source of contribution rules =
  CLAUDE.md.
- **Remove `webserver.py` entrypoint (#101)** — deleted the legacy
  `webserver.py` launcher and dead scripts; docs now use
  `flask --app "randomgen.app:create_app" run` for dev (gunicorn in prod).
  Refinement of **AD-8** (no third launch path to keep in sync).
- **Issue cleanup** — closed the session-2 modernization issues (#75–#89)
  that did not auto-close because of the #91/#93 stacked-PR merge race.
- **Key decisions.** AD-11 (inline the enforced checklist); AD-8 amended
  for the `webserver.py` removal. Procedural rules the agent must execute
  belong *inlined* in CLAUDE.md, never paraphrased — referenced template
  files are not auto-loaded into context.

---

### Session 4 — Issue triage, label standard, and v0.9.0

- Tool: Claude Code (Opus 4.8). Filed a backlog (#103–#110), adopted the
  solid-ai-templates issue-label standard, then planned, built, and shipped
  the **v0.9.0** milestone (ADR folder, `/docs` OpenAPI endpoint, GUI presets).
- **Backlog + labels** — filed issues #103–#110; adopted the 12-label
  type/priority/triage scheme from `platform/github.md` + its ADR-002 (created
  the labels with Atlassian colours, retired GitHub's defaults, kept the
  Dependabot/CI labels) and added `Backlog`/`Expedite`/`v0.9.0` milestones.
  Recorded the convention in [CLAUDE.md](../CLAUDE.md) §2.1 (#111) and as
  **AD-14**. Logged the upstream `task`/`epic` colour mismatch (github.md vs
  the submodule CLAUDE.md §2.2) on #110.
- **#104 (PR #112)** — created `docs/decisions/` (README + TEMPLATE); migrated
  AD-1…AD-11 out of arc42 §9 into individual `NNN-slug.md` files (kept the
  `AD-N` ids); reduced arc42 §9 to an index. Recorded as **AD-12**.
- **#108 (PR #113)** — interactive `/docs` API reference (ReDoc) from a
  code-built OpenAPI 3.1 spec (`openapi.py`, served at `/openapi.json`), with a
  drift-guard test asserting every `/api` route is documented. Recorded as
  **AD-13** (chose this over a flask-smorest MethodView + marshmallow refactor).
- **#105 (PR #114)** — one-click home-page preset distributions (Uniform/
  Skewed/Bimodal/Near-degenerate) + a Playwright e2e.
- **Release v0.9.0 (PR #115)** — bumped the version, tagged `v0.9.0` →
  `deploy_image.yml` published the image to Docker Hub (Render auto-redeploys);
  closed the v0.9.0 milestone.
- **Doc sync (PR #116, #117)** — a post-release audit found stale
  module/endpoint enumerations; updated CLAUDE.md §1.2, arc42 §3/§5, and
  rest_api.md, refreshed the UI snapshots, and added a reproducible
  `scripts/capture_ui_snapshots.py` (PLAYBOOK §3.4). Also corrected a stale
  `home_endpoint()` reference in arc42 §5.
- **Filed #118** — flaky `TestRestApiRouting` (webserver-fixture startup race),
  surfaced as an intermittent CI `build` failure on #117 and confirmed flaky by
  a clean re-run with no code change.
- **Key decisions.** AD-12 (dedicated `docs/decisions/` folder, arc42 §9 as the
  index); AD-13 (code-built OpenAPI spec served at `/docs`); AD-14 (adopt the
  solid-ai-templates issue-label standard).

---

### Session 5 — Docs deep-clean, design-first API, deploy fix

- Tool: Claude Code (Opus 4.8). Reorganized `docs/`, started a plain-language
  pass over the arc42 docs, moved the API to a design-first OpenAPI contract,
  and fixed automatic deployment to Render.
- **Docs reorg (PR #121, AD-15)** — grouped `docs/` by purpose: `reference/`
  (rest_api, ui-snapshots), `history/` (problem, solution), and a single
  `assets/` image tree (folded the second `images/` tree in). Repointed every
  inbound link; closed #120.
- **arc42 §1–§3 readability (PR #122, open)** — plain-language rewrite for a
  non-technical reader: requirement ids `R#` → `FR01–FR07` in shall-form
  (IEEE 29148); quality goals `QG01–QG06` with ISO 25010 names; §2 constraints
  restated forward (no reverse-engineered code citations); §3 business and
  technical context as black-box diagrams distinguishing the user (web page)
  from client apps (API). Added a demo-oriented `QG06 Usability` and an
  evaluator stakeholder. The plain-language conventions are saved as agent
  memory.
- **Design-first OpenAPI (PR #124, open, AD-16 supersedes AD-13)** — a
  hand-authored `src/randomgen/openapi.yaml` is the single source of truth,
  served verbatim at `/openapi.json` (dropped `build_spec()`; added `pyyaml`).
  A pin test ties the spec's version and quantity limits to the code constants;
  Schemathesis contract tests verify the running app conforms to the spec.
- **Render auto-deploy (PR #126, AD-17 supersedes AD-9)** — the demo was stuck
  at v0.8.0 because nothing triggered a Render deploy. `render.yaml` now runs
  the published `braboj/randomgen:latest` image and `deploy_image.yml` POSTs a
  Render Deploy Hook (`RENDER_DEPLOY_HOOK_URL`) after each push. Validated
  end-to-end (workflow → image → hook → Render deploy `dep-d8qnaop…`); the demo
  is back on v0.9.0 at the same URL. Closed #125.
- **Upstream** — filed solid-ai-templates#500 (spike: dev-journal filename
  casing, a possible `SESSIONS.md` rename, and a required-contents schema).
- **Key decisions.** AD-15 (reorganize `docs/` by purpose); AD-16 (design-first
  OpenAPI as the single source of truth, supersedes AD-13); AD-17 (deploy the
  published image to Render via a deploy hook, supersedes AD-9).
- **Next.** Merge PR #122 and #124 (the latter needs a one-line arc42 §9 merge
  now that AD-17 landed); continue the arc42 readability pass (§4–§12); export
  the §3.1 draw.io diagram to a rendered image and swap it into the doc; the
  P1 license reconciliation (#107) is still open.

---

### Session 6 — Land the design-first API + arc42 §1–§3; retire rest_api.md

- Tool: Claude Code (Opus 4.8). Merged the two PRs left open at session 5,
  fixed a CI break, finished the §3 pass, and retired the hand-written REST
  reference. All three open PRs (#122, #124, #127) landed; no PRs remain open.
- **Design-first OpenAPI (PR #124, AD-16)** — merged. The e2e job was red: the
  new Schemathesis contract test (`tests/integration/test_contract.py`) imports
  `schemathesis`, which the `e2e` extra does not install, and `pytest -m e2e`
  collects every module before deselecting. Fixed by guarding the import with
  `pytest.importorskip` plus a scoped ruff `E402` per-file-ignore for the
  post-guard imports; merged `main` in and resolved the arc42 §9 conflict.
  Closed #123.
- **arc42 §1–§3 + retire rest_api.md (PR #122, squash-merge)** — merged.
  Finished §3: §3.3 scope reframed from a re-list of FR01–FR07 to the project's
  *deliverables*, kept high-level (file paths, tool names like ReDoc, and
  Docker Hub/Render pushed to §7/§9); dropped `scipy` from the §3.2 channel
  table (in-process library, not an external partner); broadened the API channel
  to cover the web page and docs, not just JSON. Retired
  `docs/reference/rest_api.md`: deleted it and repointed every live reference
  (arc42 §3.2/§6/§8, the arc42 README, `CLAUDE.md`, `PLAYBOOK.md`) at the
  OpenAPI spec; de-linked the historical AD-10 mention; amended AD-16 decision
  #5 ("becomes a short human intro" → "is removed").
- **Session 5 wrap-up (PR #127)** — merged (the dev-journal entry).
- **Key decisions.** No new ADR. The rest_api.md retirement is a continuation
  of AD-16, recorded by amending its decision #5 in place; the arc42 §3
  authoring rules (scope = deliverables; technical-context channels = external
  partners only; keep §3 high-level) are documentation style, saved to agent
  memory [[arc42-writing-conventions]].
- **Upstream.** Recorded two reusable conventions on the lessons-learned spike
  #110: the `importorskip` + scoped-ruff-ignore pattern for optional-dependency
  test modules (→ `core/testing.md`), and the arc42 §3 authoring rules
  (→ `core/docs.md`).
- **Next.** P1 license reconciliation (#107); flaky `TestRestApiRouting` (#118);
  continue the arc42 readability pass (§4–§12) and export/swap the §3.1 draw.io
  diagram into a rendered image; backlog spikes #103/#106/#109/#110.

### Session 7 — arc42 readability overhaul (§2–§7), one PR per chapter

- Tool: Claude Code (Opus 4.8). Reconciled the license, then refactored arc42
  §2–§7 for readability and accuracy, grounded throughout in the canonical
  DokChess arc42 example. Seven chapter PRs landed (#129, #132, #134, #135,
  #136, #137, #138); no chapter PRs remain open.
- **License → MIT (PR #129)** — replaced the Unlicense `LICENSE` text with the
  MIT text (`pyproject.toml` already declared MIT). Closed #107. Filed #130 to
  modernize the PEP-639 license metadata later.
- **arc42 §4–§6 readability + terminology (PRs #132, #134)** — a readability
  pass on Solution Strategy / Building Blocks / Runtime (closed #131), then
  standardized "Chapter N" over "Section N" across all 12 docs (numbered
  sub-parts stay "Section N.M").
- **Chapter 2 ↔ 4 realignment (PR #135)** — the substantive one. Applied the
  DokChess rule that §2 holds *givens* (language, platform, environment,
  process, conventions) while technology *selections* are §4 decisions: moved
  scipy/gunicorn (T03/T04) and non-root/pinned-base (S02/S03) out of §2 into §4;
  kept Flask and no-persistence as constraints; added the missing givens
  (OSS-only deps, zero-cost free-tier budget, plain-HTTP/TLS-at-edge); trimmed
  §2.2 to process/tooling. Rendered §4.1/§4.2 as tables and replaced the §4.2
  decomposition (a §5 duplicate) with an FR01–FR07 → approach table.
- **Chapter 5 rebuild (PR #136)** — replaced the nine-module dump with four
  coarse building blocks (HTTP Adapter, Domain Logic, API contract, Errors),
  each with a whitebox diagram and a subcomponent table.
- **Chapter 6 (PR #137)** — fixed the §6.1 mermaid that would not render (a `;`
  that mermaid treats as a statement separator, and a bare `<` in an HTML note),
  then split the one diagram into a happy path and an error path.
- **Chapter 7 (PR #138)** — split the busy diagram into a runtime-topology and a
  release-and-deploy diagram, applied the deployment lens (process vs artifact
  vs communication path), and retitled §7.3 "Infrastructure elements" →
  "Container image" (it described the Dockerfile, not infrastructure nodes).
- **Cross-cutting.** Removed every inline ADR citation from the chapters (§9 is
  the sole ADR index) and the cross-chapter links from §4/§5; lightened prose
  and diagrams; minimized bold/italic and inline-code density throughout.
- **Key decisions.** No new ADR — all readability / documentation-structure, no
  architecture change. The conventions are saved to agent memory
  ([[arc42-writing-conventions]], [[doc-formatting-style]]): the §2-vs-§4
  constraint/decision boundary, "chapters never cite ADRs", and the
  minimize-emphasis / minimize-inline-code rules.
- **Upstream.** The arc42 conventions above are reusable — recorded on the
  lessons-learned spike #110 (→ `core/docs.md`).
- **Next.** Continue the readability pass into §8–§12 (crosscutting, decisions
  index, quality, risks, glossary); flaky `TestRestApiRouting` (#118, P2);
  backlog spikes #103/#133/#130/#106/#109/#110.

### Session 8 — arc42 readability §7–§12; debt as tickets; folder READMEs removed

Finished the arc42 readability pass through the remaining chapters and acted on
two reader-driven cleanups (technical debt, folder READMEs). All merged into
`main` on `braboj/demo-randomgen`.

- **§7 Deployment (PR #141)** — added §7.1 Environments (local dev → CI gate →
  production; the single-environment topology stated as a deliberate choice for a
  stateless, zero-cost demo), and reframed §7.3 as the full CI/CD pipeline
  showing both triggers (push/PR → quality gate; tag → release).
- **§8 Crosscutting (PR #142)** — de-bold pass; new §8.1 Sampling model (domain)
  concept; every section reworked to one shape (generic prose + implementation
  table); §8.4 Werkzeug `HTTPException` row clarified with a matching glossary
  entry; enriched AD-6 with the per-generator trade-offs.
- **§9 & §10 (PR #144)** — de-bold "index"/second-person in §9; de-bold the §10
  quality-tree column and the secondary scenario emphases, keeping the Q-labels
  and Verified-by traceability.
- **§11 & §12 (PR #149)** — §11.2 technical debt replaced with a live index of
  GitHub issues labeled `tech-debt` (shields.io status badges) — **AD-18**;
  relocated the §11.3 "correctness safeguards (not debt)" list into a new §8.6
  (renumber §8.6–8.9 → 8.7–8.10); glossary de-monospaced to bold + normal text.
- **Folder READMEs removed** — `docs/arc42/README.md` (PR #150; the folder now
  shows the chapters directly) and `docs/decisions/README.md` (PR #151; the ADR
  conventions relocated to PLAYBOOK §4.3, §9 repointed) — **AD-19** (refines
  AD-12's folder layout; its core folder + §9-index decision stands).
- **Issues filed.** #143 (tests for uncovered §10 scenarios, P3); #145–#148
  (tech-debt items D1–D4, P3/P4) + the new `tech-debt` label.
- **Key decisions.** AD-18 (debt as labeled issues, §11.2 indexes them), AD-19
  (drop the ADR-folder README, conventions → PLAYBOOK); AD-6 enriched. New
  conventions saved to [[doc-formatting-style]]: the §8 "generic prose +
  implementation table" section shape, and glossary = bold terms + normal text
  (no inline code).
- **Next.** File the CI/CD workflow-rename ticket (`test_application.yml` /
  `deploy_image.yml` → `ci.yml` / `cd.yml`, still unfiled); #143 tests; #118
  flaky `TestRestApiRouting` (P2); backlog spikes #103/#133/#130/#106/#109/#110.

### Session 9 — Plan & ship v0.10.0 (code hardening); CI/CD pipeline overhaul

Planned the v0.10.0 milestone "Code hardening & debt paydown", shipped all six
of its work items, then overhauled the CI/CD pipeline. Eight PRs merged
(#154, #155, #156, #157, #158, #160, #162, #164); milestone v0.10.0 closed at
0 open. The release tag itself is not yet cut — `pyproject` is still `0.9.0`.

- **Planning.** Created milestone #11, scoped six items, filed the unfiled
  workflow-rename ticket (#153), and retitled the four `Tech debt:` issues to
  conventional-commit prefixes (#145 `docs:`, #146 `chore:`, #147/#148
  `refactor:`) — the `tech-debt` label already carries the category.
- **#118 flaky test (PR #154).** Converted `TestRestApiRouting` from the
  threaded real-socket `webserver` fixture to the in-process Flask
  `test_client()` (the home-page tests already used it), removing the connection
  race and the hardcoded port. Net −116/+29.
- **#143 §10 coverage (PR #155).** Closed the arc42 §10 gaps: Q5 (bound is
  served), Q6 (concurrent disjoint distributions stay isolated), Q10 (v1/v2
  response-schema snapshot), Q11 (e2e asserts the container runs non-root; the
  fixture now yields the container). Q8 (thin handlers) left as a documented
  review-only concern. Verified locally; Q11 confirmed on CI's Podman e2e job
  (local Docker was down).
- **#130 license metadata (PR #156).** `license = { text = "MIT" }` →
  `license = "MIT"` + `license-files = ["LICENSE"]` (PEP 639 SPDX); `python -m
  build` clean, LICENSE bundled in wheel + sdist.
- **#147 + #148 tech debt (PR #157).** Moved the precomputed CDF
  (`calc_cdf` + `_cumulative_probabilities`) out of the shared base into
  RandomGenV1 (the only consumer); `Histogram._counter` initialized as
  `Counter()`. No behavior change.
- **#153 workflow rename (PR #158).** `test_application.yml` → `ci.yml`,
  `deploy_image.yml` → `cd.yml`; repointed the live references and left the
  historical records (dev-journal, ADR-017) on the old names. Found `main` was
  not actually branch-protected.
- **CI/CD overhaul — AD-20.** Restructured `ci.yml` into one gate per job
  (`lint`/`typecheck`/`test`/`build`/`e2e`/`secret-scan`, PR #160), added the
  missing build gate (`python -m build` + `twine check`); split `cd.yml` into
  `publish` + `deploy` with `deploy` gated on `publish` (PR #162); added CodeQL
  Python SAST and a `gate` fan-in aggregator (PR #164). SHA-pinned every action,
  added pip caching + a CI concurrency group, renamed display names to CI/CD.
  Prompted by a comparison against `Imbra-Ltd/wuseria`'s pipelines (CodeQL +
  gate were the two relevant gaps; Lighthouse/Pages/link-checking were
  static-site-specific).
- **Branch protection.** Enabled on `main`: required checks `gate` +
  `Analyze (python)`, no required reviews (solo maintainer), non-strict,
  `enforce_admins` off — making the "main is protected" convention real.
- **arc42 §7 refresh (PR #166).** Rewrote the deployment view for the new
  pipeline: §7.1 lists the build + CodeQL gates and the protected-branch required
  checks; §7.3 redrew the diagram for the six-job fan-out into `gate`, CodeQL,
  and the cd `publish → deploy` split; §7.5 reflects the `v*` trigger.
- **Upstream contributions.** Grounded the lessons-learned candidates (#110)
  against the actual templates and filed two on `solid-ai-templates`: #510
  (SHA-pin actions) and #511 (Python build gate). CodeQL-as-workflow was already
  covered upstream, so dropped.
- **Released v0.10.0 (PR #167 + tag).** Bumped to 0.10.0, tagged `v0.10.0` →
  `cd.yml` published the image to Docker Hub (`latest` + `v0.10.0`) and triggered
  the Render redeploy; the demo serves 0.10.0. Milestone #11 closed. First
  release to ship through the new branch protection.
- **Single-sourced the version (#168 → PR #169), then decoupled the contract
  version (#170 → PR #171, AD-21).** First made `pyproject` the single source by
  injecting `__version__` into the served OpenAPI spec; then, on the observation
  that `info.version` is the *contract* version (distinct from the package
  version per the OpenAPI spec), reverted the injection and hand-set
  `openapi.yaml` `info.version` to `2.0.0` — the API generation (major = highest
  `/api/vN`), maintained independently. The drift guard keeps the limit pins and
  drops the version cross-pin.
- **Key decisions.** AD-20 (CI/CD pipeline — one gate per job, SAST, enforced
  branch protection); AD-21 (OpenAPI `info.version` is the contract version,
  decoupled from the package version, `2.0.0`). New feedback saved to agent
  memory ([[ci-job-srp]]): CI workflows follow SOLID single-responsibility, one
  gate per job.
- **Next.** Backlog spikes #103 (src multi-version restructure, P2), #133, #106,
  #109; #145 (stale solution.md); the §3.1 draw.io diagram still wants a
  rendered-image export. The 2.0.0 contract version goes live on the next deploy.

### Session 10 — v0.11.0 Showcase UI/UX (dark mode, sliders, CSV) via a UX bake-off

Planned and built the "v0.11.0 — Showcase UI/UX" milestone on the existing
single-page **vanilla** front-end (no build step, no new dependency, no API
change). Six PRs merged (#174, #176, #177, #178, #179, #180); the release tag is
not yet cut (`pyproject` unchanged) — the features sit on `main`.

- **Front-end stack — kept vanilla (spike #173).** Opened a spike weighing
  htmx vs TypeScript vs typed-build-free JS (JSDoc + `tsc --checkJs`) and drafted
  AD-22 recommending the last. The maintainer rejected every stack change; AD-22
  was closed unmerged (**no ADR recorded, by request**) and #173 closed
  "keep the current vanilla JS".
- **#174 Normal preset (Expedite).** A fifth distribution preset — the symmetric
  binomial B(4, 0.5), the textbook discrete bell.
- **#176 dark mode.** A `:root[data-theme="dark"]` token block (only colours
  change) + a sliding toggle switch (`role="switch"`, inline-SVG sun/moon), a
  no-flash head script, and `localStorage` persistence; hard-coded `#fff` control
  surfaces reworked to `var(--surface)`.
- **#177 footer API-docs link.** Built an on-page "Call the API" snippet panel
  (curl/Python, live), then scrapped it as clutter in favour of a single footer
  link to `/docs`.
- **#178 CSV download.** A results button that saves the generated sample as a
  one-column CSV from the response already in hand (no extra request).
- **#179 distribution weight sliders — via a graded UX bake-off.** Built three
  editor variants (live-preview-only / weight-sliders / full add-remove builder),
  graded each on the dev server (8 / 9 / 9), and shipped the sliders — tied top
  UX at the lowest effort. Also gave the distribution field its own full-width
  row to de-clutter the form.
- **#180 e2e + snapshots.** Four new Playwright tests (theme toggle, sliders, CSV
  download, footer link); regenerated the UI screenshots (now showing the sliders
  and toggle), added a dark-theme shot, refreshed `ui-snapshots.md` to v0.11.0,
  updated the README Features bullet.
- **Rejected (firm minimal bar):** the snippet panel, a plain-language Chi-Square
  explainer, advertising the Render URL in snippets (free-tier cold-start would
  confuse users), and bake-off variants A & C.
- **Key decisions.** Front-end stays vanilla/no-build (#173 settled; no ADR by
  request). The interactive distribution editor was selected by a **graded UX
  bake-off** (build N variants → grade UX → pick best-per-effort) rather than
  decided up front — a reusable method flagged as a deferred upstream candidate.
- **Next.** Cut the v0.11.0 release tag (the UI features are on `main`,
  unreleased). Deferred UI idea: a shareable permalink. Backlog spikes
  #103/#133/#106/#109; #145 (stale solution.md).

### Session 11 — v0.12.0 API package structure (registry + blueprint factory) from the structural spikes

Took the two structural spikes (#103, #133) end to end — decision → ADRs →
implementation → release — as the first step toward a 1.0 contract. Five PRs
merged (#184, #187, #188, #189, #190).

- **Reframing finding (drove everything).** `/api/v1` and `/api/v2` are parallel
  implementations of **one** contract (AD-5/AD-21) — identical params,
  validation, and response shape, differing only by the injected generator. So
  #103's premise ("the split mixes version-specific logic") did not hold: there
  is no version-specific endpoint logic, only generator selection. A per-version
  directory tree would duplicate byte-identical handlers and imply a divergence
  that does not exist.
- **AD-22 / AD-23 (#184).** Recorded the two decisions (spikes #103, #133 closed).
  AD-22: keep the flat, role-named package; add a version registry + a blueprint
  factory; document the **escalation trigger** (a version graduates to its own
  module only when its *contract* diverges). AD-23: rename the misnamed service
  module/class. Don't-fake-architecture-in-a-demo — the per-version layout is a
  documented design, not contrived running code.
- **#185 rename.** `endpoints.py` → `service.py`, `RandomGenRestApi` →
  `RandomGenService` (`git mv`, history preserved); internal name, no contract
  change.
- **#186 registry + blueprint factory.** `versions.py`
  (`API_VERSIONS = {'v1': RandomGenV1, 'v2': RandomGenV2}`) + `blueprints/web.py`
  (UI/docs/health) + `blueprints/api.py` (`make_api_blueprint`); `app.py` loops
  the registry; `routing.py` deleted. Blueprints no longer import `core` — version
  selection flows through the registry, resolving the #133 route→core coupling.
  Adding a version is now a one-line registry edit.
- **#189 service method naming.** `randomgen_endpoint` → `generate`,
  `generate_random_numbers` → `_draw_and_score` (made private), `validate_distribution`
  kept. The same "endpoint" misnomer fixed one level down.
- **Generator-injection design debate.** Weighed per-call `generate(generator, …)`
  vs constructor injection vs a `set_generator` setter through the Strategy lens.
  Ruled out the setter (shared mutable state on the singleton → concurrency
  hazard; the strategy is a per-version constant we never swap). Scored per-call
  vs constructor injection **67–67**; kept per-call (Strategy-as-parameter) on the
  cost/reversibility tiebreaker. Constructor injection left as a documented,
  low-cost future option.
- **Milestones.** Closed the stale `v0.11.0` milestone; created and completed
  `v0.12.0 — API package structure` (#185, #186).
- **#190 release.** Bumped `pyproject` 0.11.0 → 0.12.0 and tagged `v0.12.0`
  (CD → Docker Hub + Render). No contract change, so `openapi.yaml` `info.version`
  stays `2.0.0`.
- **Key decisions.** AD-22 (layout: registry + factory, reject the per-version
  tree as premature generalization), AD-23 (rename). Per-call generator injection
  retained over constructor injection (tie-break).
- **Next.** Remaining backlog spikes #106 (Flask audit), #109 (showcase
  assessment), #110 (upstream to solid-ai-templates); #182 permalink; #145 (stale
  solution.md). Toward a v1.0 contract.

### Session 12 — Spikes resolved + v0.13.0 (Observability & serving), with a mid-flight scope correction

Closed the three reflective spikes, then planned and shipped v0.13.0 — and
course-corrected its scope mid-build when the planned features ran past the
documented boundary.

- **Spikes #106 / #109 / #110 (resolved).** #106 mapped the Flask surface:
  strong on structure (factory, blueprint-factory + registry, explicit
  validation, centralized errors, hardened WSGI), thin on the cross-cutting
  operational layer. #109 (done after the others) judged the showcase: the
  AI-assisted-dev rigor is the standout, the one real engineering hole was
  *zero logging*. #110 inventoried upstreaming: filed `solid-ai-templates`
  #513 (arc42 writing conventions), #514 (graded UX bake-off), #515 (naming
  rule), and caught that the pre-existing #512 already covered the AD-22
  layout guidance (narrowed #515 to dedup). Audits posted as issue comments;
  spikes closed.
- **#197 refactor.** Reworked the request-generator build in `service.py` from
  a single fluent chain to explicit builder statements — settled after weighing
  the one-line chain, a `# fmt: skip` wrapped chain, and a project-wide
  line-length drop (measured: 14 files + ~10 manual E501 fixes — not worth it).
- **v0.13.0 plan.** Planned "operational hardening" from the #106/#109 gaps —
  observability, security headers/CORS, rate limiting, gunicorn config — using
  Flask extensions. Landed PR #198 (config foundation, AD-24) and PR #199
  (observability + gunicorn + generic-500, AD-25).
- **Scope correction (the lesson).** Rate limiting (#194) is **explicitly out of
  scope** per arc42 §3.3 ("Authentication / authorization / rate limiting"), and
  CORS/security headers (#193) sit next to the same exclusion. The audit had
  recommended them for "demonstration value" without reconciling against §3.3.
  Honored the documented scope: closed PR #200 (rate limiting) unmerged, closed
  #193/#194 as out of scope, and trimmed the dead CORS/rate-limit config keys the
  foundation had shipped forward-looking (PR #201; AD-24 revised to LOG_LEVEL).
- **Implementation notes (from the dropped rate-limiter, kept for the record).**
  Flask-Limiter keys decorated limits by the view's `__qualname__`, which the
  blueprint factory shares across versions (double-counting); and a module-level
  limiter singleton accumulates registrations across `create_app()` calls. The
  fix was a per-app limiter applied to each blueprint — useful if rate limiting
  is ever brought into scope deliberately.
- **#190-style release.** Bumped `pyproject` 0.12.0 → 0.13.0; `openapi.yaml`
  `info.version` stays `2.0.0` (no contract change — the 429 went away with rate
  limiting). Milestone "v0.13.0 — Observability & serving" completed.
- **Key decisions.** AD-24 (env-driven config, now log level only), AD-25
  (request logging + gunicorn runtime + generic-500). Scope is enforced by the
  documented §3.3 boundary, not by feature-audit enthusiasm — an audit
  recommendation must reconcile against scope before it becomes work.
- **Post-release: rate limiting / CORS stay out of scope, tracked deferred.**
  Decided not to backlog #193/#194 — "Backlog" means accepted work, which would
  contradict §3.3. Kept them closed with a "reopen only via an ADR amending §3.3"
  note in the issues + memory ([[scope-vs-audit]]); the design is preserved in
  closed PR #200. The deferred framing lives in the journal/issues/memory, not in
  arc42 §3.3 (chapters carry no decision references).
- **Post-release: triaged the GitHub Discussions (Ideas).** Of 5 ideas: filed
  #203 (shrink the image via a multi-stage build, in scope / QG04) and #204
  (`GET /api/info` — additive GET, flagged as net-new contract surface needing a
  new FR + `info.version` bump). Closed 3 with disposition: #25 deploy-to-cloud
  (resolved — already on Render), #29 persistent storage and #26 in-process TLS
  (out of scope per §3.3 / §3.2). Same scope discipline as the v0.13.0 rescope.
- **Next.** #182 permalink; #196 (surface the "how it was built" story in the
  README, from #109); #203 (image size); #204 (`/api/info`, needs scope nod);
  #145 (stale solution.md); #146 (scipy stubs); land the upstream
  `solid-ai-templates` issues #513/#514/#515. Toward a v1.0 contract.

### Session 13 — v0.14.0 scoping (de-scoped to cleanup), solution.md overhaul, gunicorn trim, Pages teardown

Planned v0.14.0 as "tech-debt cleanup," then pared it back after an
over-engineering pass: two of the three candidates were not worth doing, so the
release theme was re-pointed at the showcase work and the cleanup shipped as
standalone docs/chore changes.

- **v0.14.0 plan → over-engineering audit.** Candidates were #203 (multi-stage
  Docker), #145 (stale solution.md), #146 (scipy stubs). Reassessed each against
  the demo's purpose before building.
- **#203 closed (measured, not worth it).** The image is ~95% scipy/numpy, which
  must stay regardless; scipy ships `musllinux` wheels so nothing compiles, and
  the standard venv-multistage on a `python:3.12-alpine` final stage reclaims
  ~0 MB (the base still ships pip/setuptools). Closed with the math rather than
  cargo-culting a best practice. Lesson: **measure before optimizing.**
- **#146 closed (accepted limitation).** scipy is the only untyped import in
  `src`; no maintained `types-scipy` to adopt. Revisit if it ships stubs.
- **#145 → PR #206 (solution.md overhaul).** Reconciled the stale refs inline
  (no `/api/v1/config`; response uses `is_null`, no `version`; port 5000) and
  added a two-part structure: Part I (kata) + a short, bulleted Part II
  (post-tag productionization, no ADR citations). Fixed a real bug — §6 had the
  generators swapped (V1 is `random.random` over the cumulative dist, V2 is
  `random.choices`; contradicted `core.py`) — plus typos, and reconciled the
  MkDocs/Pages mentions after the teardown below. Iterated on voice/density per
  review.
- **gunicorn config trim → PR #207.** From a config-review consult: trimmed
  `gunicorn.conf.py` to its load-bearing surface (`bind` for `$PORT`, `workers`
  from `WEB_CONCURRENCY`); the rest restated gunicorn defaults or exposed knobs
  no single-instance demo will tune. Dropped the gunicorn access log, which
  double-logged with the app's per-request log (`observability.py`). Synced docs
  and added a dated refinement note to AD-25 (intent unchanged).
- **#208 filed.** Local e2e was blocked — the Docker engine wedged
  (`docker version` hung >150s while Desktop ran). Task to evaluate rootless
  Podman vs a Docker recovery runbook; CI e2e is unaffected.
- **GitHub Pages teardown (completes ADR-010).** Pages was still enabled, serving
  the stale 2024 MkDocs site at `braboj.me/demo-randomgen`; the code side
  (`mkdocs.yml` + the Pages workflow) was removed long ago. Disabled Pages and
  deleted the 30 `github-pages` deployments + the `github-pages` environment via
  the API. Custom-domain note: only the project path went away; the main
  `braboj.me` site (separate repo) is untouched. Settings-only — no commit.
- **Key decisions.** A feature/debt recommendation must reconcile against both
  the documented scope ([[scope-vs-audit]]) **and** its measured payoff before it
  becomes work — "best practice" alone (multi-stage Docker) does not justify it.
  v0.14.0 settled as a tech-debt/cleanup release.
- **v0.14.0 release (tech debt & cleanup).** Bundled the session's cleanup — PRs
  #206 (solution.md), #207 (gunicorn trim), #209 (this journal) merged — and
  bumped `pyproject` 0.13.0 → 0.14.0; `openapi.yaml` `info.version` stays `2.0.0`
  (no contract change). No open tech-debt remains (arc42 §11.2 D1–D4 all closed).
  Tag `v0.14.0` → CD publishes the image and redeploys Render.
- **Scope changes.** Dropped the shareable-permalink feature (#182, closed) — the
  in-page demo config is enough. Filed three logging-sufficiency spikes: #210
  (coverage after the gunicorn access-log removal), #211 (request-line content),
  #212 (business-logic observability).
- **Next.** #196 (README "how it was built" story); #204 (`/api/info`, needs a
  scope nod); #208 (local e2e backend / Podman); resolve the logging spikes
  #210/#211/#212; land the upstream `solid-ai-templates` #513/#514/#515. Toward a
  v1.0 contract.

### Session 14 — v0.15.0 Observability (logging coverage review, #210–#212)

Resolved the three logging spikes filed last session as one coverage review of
AD-25, then released v0.15.0. The discipline that paid off: a spike's deliverable
is a *decision*, so the app was driven through every response class (success /
4xx / 404 / 500) with logging at DEBUG to answer each question empirically
*before* writing any code — which kept the add-list small.

- **Findings → a deliberately small add-list (PR #214).** The one real gap was
  that every `400` logged identically — the log could not say which rule rejected
  a request (#212). Closed by logging the validation cause at WARNING in the error
  boundary (the single choke point all domain 400s flow through). Alongside it:
  the access line now leads with the client address (#211), and static-asset
  fetches are dropped as page-view byproducts (#210).
- **Reviewed and declined (recorded, not silently skipped).** Worker-timeout /
  pre-Flask blind spots — generation is sub-ms compute bounded by `MAX_NUMBERS`,
  and a restored gunicorn access log would re-introduce the duplication PR #207
  removed. Structured logging / correlation ID / response size — overkill for a
  single replica (AD-25 holds). Domain DEBUG lines (fallback marker, fairness
  verdict) — already in the response body, noise otherwise. All recorded in AD-25
  (`Coverage review`) + arc42 §8.10.
- **Invariants confirmed empirically.** Every handled response → exactly one
  access line; an unexpected 500 → exactly one traceback + one access line (no
  duplication across the error boundary and the request hook).
- **Issue auto-close gotcha.** `Closes #210, #211, #212` closed only #210 —
  GitHub needs the keyword before *each* number. Closed #211/#212 by hand. Use
  `Closes #a, closes #b, closes #c` next time.
- **v0.15.0 release.** Bumped `pyproject` 0.14.0 → 0.15.0; `openapi.yaml`
  `info.version` stays `2.0.0` — observability is internal, no contract change.
  Tag `v0.15.0` → CD publishes the image and redeploys Render.
- **Next.** #196 (README story); #204 (`/api/info`, needs a scope nod); #208
  (local e2e / Podman); upstream `solid-ai-templates` #513/#514/#515. Toward a
  v1.0 contract.

### Session 15 — v0.16.0 Service metadata (the `/info` endpoint, #204)

Implemented the `/info` endpoint that the prior sessions had deferred pending a
scope nod, then released it as v0.16.0 — the first contract bump since the v2
generation split.

- **The #204 reversal (a decision worth recording).** The agent first agreed to
  close #204 on YAGNI — the version is already on the home page. Pushed to
  actually evaluate rather than comply, the call flipped: for a *portfolio* demo
  ([[project-demo-purpose]]) a service-metadata endpoint is a recognized REST
  convention, and there was a real gap — the **release** version (`__version__`)
  was only ever rendered as HTML, never machine-readable (the home page shows the
  package version; `/openapi.json` carries the *contract* version, distinct by
  AD-21). That gap, not "demo value" hand-waving, justified the work against
  [[scope-vs-audit]]. Closed-then-reopened, implemented design-first.
- **`GET /info` (PR #216).** Returns `{name, version, api:{version, generations}}`
  — release version, contract version, and the served generations from the
  `API_VERSIONS` registry. No new state/deps: it aggregates `__version__`, the
  OpenAPI `info` block, and the registry. Placed at the **root** next to
  `/health`, following the convention that ops/discovery routes are unversioned
  (only generation endpoints live under `/api/vN`). Design-first: documented in
  `openapi.yaml` with an `Info` schema and `info.version` bumped 2.0.0 → 2.1.0
  (additive, AD-21); added FR08 to arc42 §1.1; tests at all three tiers.
- **Editable-install version staleness (found via `/info`).** Locally the
  endpoint reported `0.12.0` while `pyproject` was `0.15.0`. Root cause:
  `__version__` reads the installed `.dist-info` (`importlib.metadata`), which an
  editable install only rewrites on `pip install -e .`. Built artifacts (wheel,
  Docker, Render) install fresh and are always correct — only a local editable
  checkout drifts. The home page has the same behaviour. Kept the mechanism
  (correct for artifacts; `setuptools-scm` / runtime pyproject reads are worse),
  documented the reinstall in PLAYBOOK §5, and filed it upstream as a reusable
  gotcha for `python-lib.md` (`solid-ai-templates` #518).
- **v0.16.0 release (Service metadata — `/info`).** Bumped `pyproject` 0.15.0 →
  0.16.0; `openapi.yaml` `info.version` is now `2.1.0` (additive contract growth).
  Tag `v0.16.0` → CD publishes the image and redeploys Render. First exercise of
  the new PLAYBOOK version-refresh note.
- **Next.** #196 (README "how it was built" story); #208 (local e2e / Podman);
  land the upstream `solid-ai-templates` #513/#514/#515/#518. Toward a v1.0
  contract.

### Session 16 — v0.17.0 Readability & v0.19.0 Clean-layer structure

Two releases plus a deep package-structure decision. v0.17.0 polished the
project's surface (docs + the Dockerfile); v0.19.0 grouped the domain logic into
a subpackage with a clean-architecture ADR. (The v0.18.0 milestone — the local
Podman e2e backend — was satisfied by a runbook and folded into v0.19.0 rather
than tagged on its own.)

- **v0.17.0 "Readability & polish."** README overhaul (#196/#219): dropped the
  inaccurate "aimed at developers" lede and the per-module structure listing,
  terse feature bullets, a by-audience config table — grounded in the base-readme
  template. PLAYBOOK restructure + the missing Render-setup section listing the
  three GitHub secrets (#221/#223). Dockerfile `HEALTHCHECK` extracted from a
  dense inline `python -c` one-liner into `randomgen.healthcheck`, run as
  `python -m randomgen.healthcheck`, with unit tests (#222/#224). Released v0.17.0
  (#225), verified live.
- **#208 local Podman e2e (PR #226).** A runbook (PLAYBOOK §3.5 + ONBOARDING)
  grounded in the working CI e2e config (`DOCKER_HOST` → the Podman socket +
  `TESTCONTAINERS_RYUK_DISABLED`). CI-grounded, but the Windows pipe path and
  "does it cure the wedge" are empirical on the maintainer's machine — that
  boundary was surfaced, not papered over.
- **PLAYBOOK §2 readability (#227).** Follow-up to #221: §2.1's dense run-on steps
  rewritten with bold-lead imperatives + sub-bullets.
- **The package-structure decision (#220 → AD-26).** Extracted `domain/` (core,
  histogram, hypothesis, errors) — the one seam with enough cohesive,
  framework-free substance to fold. Kept the presentation layer as the existing
  `blueprints/` package; **rejected** an `api/` umbrella (collides with
  `blueprints/api.py` → `randomgen.api.blueprints.api`; and `openapi.yaml` is
  package-data no CI job exercises, so a move could break packaging silently) and
  the full `domain/application/api/infrastructure` quartet (three of four layers
  hold 0–2 files = ceremony). Conforms to the Clean Architecture Dependency Rule
  (presentation → application → domain), ports-and-adapters deliberately omitted
  — no external resources to decouple (stateless pure compute, §3.3). A
  persistence/`models` layer stays a documented escalation trigger.
- **Reference-driven, not cargo-culted.** Weighed two Flask-DDD references + a
  search-result layout (`app/` + `models/` + `migrations/` + per-version
  `api/v1`,`api/v2`). All are tuned for the modal CRUD-over-DB app with diverging
  versions — RandomGen is neither, and per-version folders would *reverse* AD-22.
  Took the principles, not the literal folders. AD-26 cites Martin's *Clean
  Architecture* and the cosmicpython book (which covers when *not* to apply the
  full pattern).
- **Key decision: proportional layering.** Group what has substance; leave thin
  shells flat. The `domain/`-only asymmetry is the senior signal, not a textbook
  quartet with hollow folders → extends [[scope-vs-audit]] to architecture.
- **v0.19.0 release (Clean-layer package structure).** Ships the `domain/`
  refactor (#228, AD-26) plus the v0.18.0 runbook (#226) and §2 readability
  (#227). Bumped `pyproject` 0.17.0 → 0.19.0; `info.version` stays `2.1.0` (no
  contract change). Tag `v0.19.0` → CD.
- **Podman runbook live-verified — the real #208 cause.** Drove a full Podman
  setup on the maintainer's Windows machine: `podman machine start` will not boot
  (`ssh error: machine not in running state`) with Docker-API pipe contention,
  and the Docker daemon also wedges — both runtimes ride the same WSL2, so a
  broken WSL2 (not a Podman-vs-Docker choice) is the actual blocker. #208 reopened
  and reframed as a host WSL2 repair; runbook corrected in PR #231 (PowerShell
  `;` not `&&`, confirm the machine is Running, WSL2 troubleshooting note). The
  runbook *config* is verified equivalent to the green CI e2e job.
- **Next.** Repair the host WSL2 and confirm #208 with `pytest -m e2e`; land the
  upstream `solid-ai-templates` #513/#514/#515/#518. Toward a v1.0 contract.

### Session 17 — v0.19.0 360 review (multi-agent audit → backlog)

Ran a whole-project 360-degree review of v0.19.0 before turning toward v1.0,
persisted it, and converted the actionable findings into a triaged backlog. No
source was changed — read-only assessment plus its paperwork.

- **The review (multi-agent, read-only).** Adapted the `base-360` template:
  for a stateless backend the four stakeholder lenses collapse into the
  engineer's, so the single Quality perspective was re-projected into ten code
  dimensions (architecture, API contract, container, dependencies,
  correctness, code quality, security, tests, CI/CD, docs). 48 agents — 10
  parallel dimension reviewers reading actual `file:line`, 37 per-finding
  skeptics (refute-by-default), 1 synthesiser. 37 findings raised → 33 survived
  → 29 reported. Overall grade **A−**.
- **Headline P1 (#233).** A valid single-category distribution (`dist=5:1.0`)
  gives `df=0` → `NaN` p_value, serialised as the bare token `NaN` in a 200 —
  not legal JSON (RFC 8259) and a `type: number` contract violation, with zero
  test coverage. Reproduced live through the Flask test client before being
  featured. The one material defect; everything else is low/info hygiene.
- **Backlog.** 10 issues filed from an empty backlog (#233–#242), one type +
  one priority label each: P1 #233; P2 #235/#237/#238; P3 #234/#236/#239/
  #240/#241; P4 #242. Each maps back to the report's finding IDs.
- **Scope held.** Every recommendation was reconciled against arc42 §3.3 first;
  the deliberate exclusions (auth, rate limiting/CORS, crypto-RNG, persistence,
  TLS) were recorded as scope-excluded, not raised as gaps — applying the
  scope-vs-audit rule.
- **Persistence + decision (#243, AD-27).** Both the findings report
  (`2026-06-24-360-review.md`) and a reconstructed orchestration plan
  (`2026-06-24-360-plan.md`) live under a new `docs/review/` directory. The new
  directory triggered an ADR: AD-27 records persisting 360s as dated
  report+plan files there, diverging from `base-360`'s single-file
  `docs/360-audit.md` score-table model (which can't hold a `file:line`
  findings report). `CLAUDE.md` §1.2 tree and the arc42 §9 index updated.
- **Local e2e / #208 — live host investigation, closed completed.** The
  Session 16 blocker is gone: the host WSL2 is repaired (WSL 2.7.8.0, kernel
  6.18 — a `wsl --update` since). Podman now builds + runs containers, the
  Docker API works over the npipe for Testcontainers (`docker-py ping = True`,
  podman 5.8.3), and `pytest -m e2e` gets **9/15 pass** (was 0). The remaining
  failures are host/tooling, not repo-actionable — CI e2e is green on Linux
  every PR. Two distinct host blockers, both reproduced live: (1) Podman's
  gvproxy port-forwarding on Windows doesn't deliver the app's published port
  to localhost — `nginx` internal :80 → HTTP 200, but gunicorn/python/nginx on
  :5000 and the app on :8080 all → instant empty reply (likely an
  IPv4-vs-gvproxy-relay quirk); (2) Docker Desktop is locked out of
  `\\.\pipe\docker_engine` (`Access is denied`) by a stale, elevated Podman
  `win-sshproxy` that survives `podman machine stop` / `wsl --shutdown` and
  needs elevation or a reboot to clear. Both confirm the original "Docker-API
  pipe contention / both runtimes on one WSL2" finding. Repo deliverables were
  already done (runbook #226, WSL2 fix #231); #208 closed **completed** —
  local e2e is host maintenance (reboot, run one runtime, Docker Desktop
  preferred). Did **not** contort the app (no dual-stack gunicorn bind) for a
  local quirk → [[scope-vs-audit]].
- **Next.** Work the #233–#242 backlog toward v1.0, starting with the P1 #233
  (`NaN` guard + `allow_nan=False` + regression test on v1/v2). Still pending
  from Session 16: the upstream `solid-ai-templates` items.
