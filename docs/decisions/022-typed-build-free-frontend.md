---
id: "AD-22"
status: Proposed
date: 2026-06-21
category: frontend
supersedes: []
superseded_by: []
---

# AD-22 — Typed, build-free front-end for the demo UI

## Context

The single-page demo UI is roughly 190 lines of ES5 (an IIFE using `var`)
that calls the public JSON API (`GET /api/vN/randomgen`) and renders the
result client-side, so the page exercises the contract it documents. A
showcase milestone will add interactive features — a distribution builder
with a live preview, dark mode, an API-snippet panel, shareable permalinks,
and a Chi-Square explainer with a raw-sample download. The stack those
features are built on is a foundational choice and was deferred to a spike.

The decision is constrained by what the repository already is. The package
builds with setuptools and ships the Jinja templates and static assets in
the wheel as-is via `package-data`; there is no Node toolchain and no bundler.
CI is six Python gates fanning into one required `gate` context. The home
page is fully self-contained, while the `/docs` page already loads ReDoc from
a CDN, so "offline-friendly" today means the home page only. The UI's purpose
is to demonstrate the JSON API, not to be a second, parallel interface.

## Decision

1. **UI stays a client of the JSON API** — the demo MUST keep calling
   `GET /api/vN/randomgen` and rendering client-side. It MUST NOT move to
   server-rendered HTML fragments, so the page continues to exercise the
   public contract it documents.
2. **Modern ES modules, no build step** — replace the ES5 IIFE/`var` code
   with ES-module JavaScript using `const`/`let` and `async`/`await`. The
   `.js` MUST ship unchanged through the existing wheel `package-data`; no
   bundler, no compiled artifact, no CDN dependency for the home page.
3. **Types via JSDoc, checked by `tsc`** — annotate the code with JSDoc types,
   model the API response after `openapi.yaml`, and verify with
   `tsc --noEmit --checkJs`. This adopts TypeScript's type system and the
   contract-typed payoff without authoring `.ts` or emitting build output.
4. **One `frontend` CI gate** — a single Node job runs the `tsc` check and
   fans into `gate`. It MUST NOT touch packaging: the `build` gate stays
   pure-Python and the wheel ships the same `.js`.

## Alternatives considered

- **Full TypeScript with a build step** — rejected; setuptools runs no Node,
  so it forces either committed compiled artifacts or a custom build hook that
  couples the wheel to a Node toolchain, for ~250 lines of glue. JSDoc plus
  `tsc --checkJs` gives the same type safety with no emit and no packaging
  change.
- **htmx with server-rendered fragments** — rejected; it re-architects the UI
  onto new `/ui/*` HTML routes, so the page stops exercising the JSON API it
  exists to demonstrate, and the interactive features still need a client-side
  JS shim. Distinctive for Flask, but it works against the "API is the product"
  framing and expands scope.
- **Modernized vanilla JS without types** — rejected as the end state (it is
  the first step of this decision); it leaves the contract untyped and forgoes
  the main craft signal for a negligible saving over the type gate.
- **JSDoc checked in the editor only, no CI gate** — a lighter variant that
  keeps the repo Node-free; rejected as the default because an unenforced type
  check silently rots. MAY be adopted if a Node CI job is later judged not
  worth its weight.

## Consequences

- `ci.yml` gains a `frontend` gate (Node + `tsc --noEmit --checkJs`) wired into
  the `gate` fan-in; a `package.json` and a `tsconfig.json` (`checkJs`,
  `strict`) land at the repo root. The wheel build, `package-data`, and offline
  behavior are unchanged.
- The showcase milestone gated by this spike is built on this stack; its
  feature set becomes follow-up issues once this ADR is accepted.
- CLAUDE.md (§2.3) and the PLAYBOOK gain a one-line pointer to the typed-JS
  gate; the dev-toolchain docs note that Node is needed only for the front-end
  type check, not for building or shipping the package.
- Status is Proposed: this records the spike's recommendation. Acceptance
  (merge and flip to Accepted) authorizes creating the milestone issues.
