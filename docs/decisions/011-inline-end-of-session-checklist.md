---
id: "AD-11"
status: Accepted
date: 2026-06-19
category: process
supersedes: []
superseded_by: []
---

# AD-11 — Inline the enforced end-of-session checklist

## Context

The hybrid generation paraphrased `scope.md`'s end-of-session audit into a
lossy four-bullet summary that dropped most steps and the enforcement, so
"wrap up" produced a thin close-out. CLAUDE.md is auto-loaded into the
agent's context; referenced template files are not — so a *procedural*
checklist must be inlined to be reliably executed.

## Decision

Inline the full end-of-session audit — with the "print and execute
sequentially, do not summarize" enforcement — into
[CLAUDE.md](../../CLAUDE.md) §6.3, instead of relying on a soft
`Follow scope.md` reference.

## Alternatives considered

- **Soft `Follow scope.md` reference** — rejected; referenced files are
  not auto-loaded, and the procedure was paraphrased lossily.

## Consequences

- §6.3 carries the full end-of-session checklist verbatim.
- The upstream generation-fidelity defect is tracked as
  `braboj/solid-ai-templates#498`, which proposes a reusable `wrap-up`
  skill/command/hook as the on-demand loader.
