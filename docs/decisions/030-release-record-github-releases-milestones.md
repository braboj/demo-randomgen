---
id: "AD-30"
status: Accepted
date: 2026-06-24
category: process
supersedes: []
superseded_by: []
---

# AD-30 — Release record: GitHub Releases in CD, milestone-on-purpose

## Context

The repo carried 16 `v*` tags but no GitHub Releases: `cd.yml` published the
image and triggered the Render deploy, yet never created a Release. Milestones
had also drifted across two conventions — early versions each had one, while
recent emergent releases (v0.15.0, v0.16.0, v0.20.0, v0.21.0) were cut from a
rolling `Backlog` milestone and had none. The record read as inconsistent
bookkeeping, though no history was lost. AD-29 had already noted "no GitHub
Release in the current CD flow" as the reason its SBOM is a build artifact
rather than a release asset.

A Release and a milestone serve opposite directions in time. A milestone is
forward-looking — issues planned toward a release, with a burndown. A Release
is backward-looking — what actually shipped at a tag. The drift came from
treating them as the same artifact: an emergent release has nothing to plan, so
no milestone was created, yet its shipped record (a Release) was missing too.

## Decision

1. **CD records a GitHub Release.** `cd.yml` gains a `release` job that runs on
   tag pushes (`if: startsWith(github.ref, 'refs/tags/v')`) and calls
   `gh release create --generate-notes`. It is independent of `publish`/`deploy`
   (a Release records the source at the tag; an artifact hiccup must not erase
   it), idempotent (skips when the Release already exists, so a re-run or a
   manual dispatch is safe), and holds `contents: write` at job scope only.

2. **Existing tags backfilled.** All 16 tags were backfilled as Releases with
   generated notes; v0.8.0's note records that it bundles the v0.4.0–v0.7.0
   milestones, which shipped under that single tag.

3. **Milestone-on-purpose; the Release is the sole shipped record.**
   `Backlog`/`Expedite` stay the default intake, and a version milestone is
   created only for a deliberately-planned, scoped release (e.g. v1.0.0).
   Milestones therefore track *planned* work, never shipped history. The missing
   v0.15/16/20/21 milestones are not backfilled, and the historical per-version
   milestones (the old kata milestones and v0.4.0–v0.19.0) are deleted rather
   than kept: a planning artifact created or retained after a release carries no
   information the Release does not. Deleting a milestone leaves its (now-closed)
   issues intact — it only unsets the association — and each release's issue/PR
   list is preserved in that Release's generated notes. After this change the
   milestone list is just `Backlog`, `Expedite`, and `v1.0.0`.

   **Update (2026-06-24):** the planned-release milestone provision above was
   dropped before it was used. The lone such milestone (`v1.0.0`) is deleted;
   milestones are now intake-only (`Backlog`/`Expedite`), with no per-release or
   planned-release milestones, and release tracking is the tag plus its generated
   notes alone. The milestone list is just `Backlog` and `Expedite`.

## Alternatives considered

- **A milestone per release** — rejected: most recent releases are emergent
  (cut from the review backlog), so the milestone would be created after scope
  was already decided, duplicating the Release with no planning value.
- **Backfill the missing milestones** — rejected for the same reason; empty
  retroactive milestones add ceremony, not record.
- **Forward-only (wire CD, skip the backfill)** — rejected: the repo is a
  portfolio/demo, and a complete Releases page is part of what evaluators read.
- **A third-party release action** (e.g. softprops/action-gh-release) —
  rejected: `gh` is preinstalled on the runner, so one shell step does the job
  with no new SHA-pinned dependency.

## Consequences

- Every future tag self-records a Release with a PR-based changelog; the
  maintainer can enrich the title and notes afterward.
- The AD-29 deferral is now unblocked — a Release exists for an SBOM to attach
  to. That follow-up shipped in #267: the `scan` job attaches the SBOM to the
  tag's Release (see AD-29, decision 3).
- A milestone is intake-only; its presence on an issue means "queued", never
  "shipped in release X". (Per the 2026-06-24 update above, the planned-release
  milestone idea was dropped — see decision 3.)
- The milestone list reads as the convention at a glance — only `Backlog` and
  `Expedite` exist. Shipped history is read from the Releases, not from a wall of
  closed per-version milestones.
