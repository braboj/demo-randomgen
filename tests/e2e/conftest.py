"""Fixtures for the end-to-end tier.

`live_server` runs the real application in-process on an ephemeral port for the
Playwright UI test. The container test builds and runs the Docker image via
Testcontainers (Podman or Docker backend).

Ryuk (Testcontainers' reaper container) is disabled by default because it does
not run cleanly on rootless Podman; containers are still torn down by the
context managers in the tests.
"""

import os
import threading

import pytest

os.environ.setdefault('TESTCONTAINERS_RYUK_DISABLED', 'true')


@pytest.fixture(scope='session')
def live_server():
    """Serve the app on an ephemeral localhost port for the duration of the session.

    Yields:
        str: The base URL (e.g. ``http://127.0.0.1:53124``).
    """

    from werkzeug.serving import make_server

    from randomgen.app import create_app

    server = make_server('127.0.0.1', 0, create_app(), threaded=True)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{port}'
    finally:
        server.shutdown()
        thread.join(timeout=5)
