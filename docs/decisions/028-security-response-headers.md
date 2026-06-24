---
id: "AD-28"
status: Accepted
date: 2026-06-24
category: security
supersedes: []
superseded_by: []
---

# AD-28 — HTTP security response headers and a baseline CSP

## Context

The service served full HTML (the home page and the ReDoc `/docs` page) and
JSON with no security response headers: no MIME-sniffing protection, no
clickjacking protection, and no Content-Security-Policy. The project's own
`security.md` calls for these, and the v0.19.0 360 review flagged their absence
(F13). They sit inside the documented scope — distinct from the arc42 §3.3
exclusions of authentication, authorization, and rate limiting.

A strict, nonce-based CSP is not a clean fit for this UI: the home page ships two
small inline `<script>` blocks, and `/docs` renders ReDoc from its CDN, which
injects its own styles, spins up a blob web worker, and pulls a logo from a
second Redocly origin. Locking those down with nonces would mean templating a
per-request nonce through both pages for marginal benefit on a stateless demo.

## Decision

1. A single `after_request` hook (`randomgen.security.register_security_headers`)
   stamps three headers on every response, using `setdefault` so a route may
   override any one:

   | Header | Value |
   | --- | --- |
   | `X-Content-Type-Options` | `nosniff` |
   | `X-Frame-Options` | `DENY` |
   | `Content-Security-Policy` | baseline policy below |

2. The CSP constrains the origin set and blocks framing, plugins, and base-URI
   hijacking, while staying permissive enough to keep the served UI working:
   `default-src 'self'`; `frame-ancestors 'none'`; `object-src 'none'`;
   `base-uri 'self'`; `script-src` adds `'unsafe-inline' 'unsafe-eval'` and the
   ReDoc CDN; `style-src`/`img-src`/`font-src`/`worker-src`/`connect-src` allow
   exactly what the home page and ReDoc need and no more.

3. `nosniff` requires correct MIME types. Python's `mimetypes` consults the OS
   registry, which on Windows maps `.js` to `text/plain`; served that way the
   browser refuses to execute the script. `create_app` registers
   `text/javascript` / `text/css` so static serving is correct and deterministic
   across platforms.

4. HSTS is intentionally omitted. TLS is terminated by the deployment platform
   (Render), which owns that header — consistent with the arc42 §3.3 boundary
   that puts transport security at the platform layer.

## Alternatives considered

- A strict nonce/hash CSP — rejected as disproportionate: per-request nonces
  threaded through both HTML pages, for little gain on a stateless demo whose
  pages load no third-party scripts beyond the pinned ReDoc bundle.
- flask-talisman — rejected; the hook is a few lines of first-party code with no
  new runtime dependency, matching the AD-25 rationale for declining it for
  logging.
- A per-route policy (tight for the app, relaxed for `/docs`) — rejected as
  over-engineering for a demo; one permissive-enough policy covers both.

## Consequences

- The permissive `script-src` (`'unsafe-inline' 'unsafe-eval'`) means the CSP is
  a baseline, not a hard lockdown; it raises the bar (MIME sniffing, clickjacking,
  arbitrary external origins, plugins) without claiming script-injection
  immunity. Tightening it later is a self-contained change to one constant.
- `create_app` now also fixes static MIME types — a latent cross-platform bug
  that `nosniff` surfaced (the home-page JS would not run on Windows otherwise).
- The end-to-end UI tier exercises the home page under the live policy; `/docs`
  (ReDoc) is verified to render with no CSP violations.
