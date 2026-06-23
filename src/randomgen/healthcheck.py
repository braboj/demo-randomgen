"""Container liveness probe for the Docker ``HEALTHCHECK``.

Run as ``python -m randomgen.healthcheck``: it requests ``/health`` on the local
service and exits ``0`` when the service answers ``200``, non-zero otherwise.

Kept as a module rather than an inline ``python -c`` one-liner in the Dockerfile
so it stays readable and unit-testable, and Python-based because the slim base
image ships no ``curl`` or ``wget``.
"""

import os
import sys
import urllib.request

# The service's listen port; Render and other PaaS inject $PORT (default 5000).
PORT = os.environ.get('PORT', '5000')
HEALTH_URL = f'http://localhost:{PORT}/health'

# Bounded so the probe can never outlast the Docker HEALTHCHECK --timeout.
REQUEST_TIMEOUT_SECONDS = 3


def probe() -> int:
    """Request ``/health`` and return a process exit code (``0`` = healthy).

    Returns:
        int: ``0`` when the service answers HTTP 200; ``1`` otherwise — a refused
        connection, a timeout, or a non-200 status (``urlopen`` raises
        ``HTTPError``, a subclass of ``OSError``, for 4xx/5xx).

    """

    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return 0 if response.status == 200 else 1
    except OSError:
        return 1


if __name__ == '__main__':
    sys.exit(probe())
