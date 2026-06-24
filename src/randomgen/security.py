"""Security response headers for the RandomGen service.

A single ``after_request`` hook stamps a small, fixed set of hardening headers
on every response: MIME-sniffing and clickjacking protection plus a baseline
Content-Security-Policy. The policy is deliberately permissive enough to keep
the served UI working — the home page ships inline ``<script>`` blocks and the
``/docs`` page renders ReDoc from its CDN — so it constrains the origin set and
blocks framing/plugins/base-URI hijacking rather than attempting a strict,
nonce-based lockdown. HSTS is intentionally omitted: TLS is terminated by the
deployment platform, which owns that header (see arc42 §3.3). See ADR-028.
"""

# ReDoc (served on /docs) loads its bundle from this CDN, fetches the
# same-origin spec, injects its own styles, and spins up a blob web worker; the
# policy below allows exactly that and no more.
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "img-src 'self' data: blob: https://cdn.redoc.ly; "
    "font-src 'self' data: https://fonts.gstatic.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.redocly.com; "
    "worker-src 'self' blob:; "
    "connect-src 'self'"
)

SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Content-Security-Policy': CONTENT_SECURITY_POLICY,
}


def register_security_headers(app):
    """Attach the security-header ``after_request`` hook to the app.

    Uses ``setdefault`` so a route that deliberately sets its own value for one
    of these headers is never overridden.

    Args:
        app (flask.Flask): The application to harden.

    Returns:
        flask.Flask: The same application, for chaining.

    """

    @app.after_request
    def _set_security_headers(response):
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response

    return app
