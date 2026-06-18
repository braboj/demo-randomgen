# Development Journal — RandomGen

Continuity log for agent-assisted development. Newest entries at the
bottom. Link to ADRs for decisions and to issues for task tracking — do
not duplicate the data model (it lives in `randomgen/`).

## Architecture overview

- **Service**: Flask REST API (`randomgen/routing.py`) over a pure-compute
  random-number generator (`randomgen/core.py`,
  `randomgen/endpoints.py`). No database.
- **Distribution**: Docker image `braboj/randomgen`; docs published to
  GitHub Pages via MkDocs.
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
