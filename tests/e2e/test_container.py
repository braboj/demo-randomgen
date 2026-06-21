"""End-to-end test: build and run the real container, hit it over HTTP.

Uses Testcontainers, which drives whatever OCI runtime is available — Podman
(the project default, incl. CI) or Docker — so the same test runs locally on
Windows/macOS/Linux and on GitHub. Marked ``e2e`` automatically by
``tests/conftest.py``; run with ``pytest -m e2e``.
"""

import time
from pathlib import Path

import pytest
import requests

# Skip cleanly (rather than erroring at collection) when the e2e deps are not
# installed — e.g. during the default fast gate.
pytest.importorskip('testcontainers')

from testcontainers.core.container import DockerContainer  # noqa: E402
from testcontainers.core.image import DockerImage  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _wait_for_health(base_url, timeout=90):
    """Poll ``/health`` until the container is ready or the timeout elapses."""

    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            response = requests.get(f'{base_url}/health', timeout=3)
            if response.status_code == 200:
                return
        except requests.RequestException as exc:  # not ready yet
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f'service never became healthy at {base_url}: {last_error}')


@pytest.fixture(scope='module')
def container():
    """Build the image from the repo Dockerfile and run it; yield the container."""

    with (
        DockerImage(path=str(PROJECT_ROOT), tag='randomgen:e2e') as image,
        DockerContainer(str(image)).with_exposed_ports(5000) as running,
    ):
        _wait_for_health(_base_url(running))
        yield running


def _base_url(container):
    """The host-reachable base URL for the running container."""

    return f'http://{container.get_container_host_ip()}:{container.get_exposed_port(5000)}'


def test_health(container):
    """The running container answers the health probe."""

    response = requests.get(f'{_base_url(container)}/health', timeout=5)

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.parametrize('version', ['v1', 'v2'])
def test_generate_over_http(container, version):
    """Both API versions generate and score numbers in the real container."""

    response = requests.get(
        f'{_base_url(container)}/api/{version}/randomgen', params={'numbers': 200}, timeout=10
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body['numbers']) == 200
    assert 'chi_square_test' in body['quality']


def test_invalid_request_returns_json_400(container):
    """The JSON error contract holds end to end through gunicorn."""

    response = requests.get(
        f'{_base_url(container)}/api/v1/randomgen', params={'numbers': 'abc'}, timeout=5
    )

    assert response.status_code == 400
    assert 'error' in response.json()


def test_home_page_and_static_assets_are_served(container):
    """The wheel-packaged UI (template + static assets) is served by the image."""

    base_url = _base_url(container)
    home = requests.get(f'{base_url}/', timeout=5)
    css = requests.get(f'{base_url}/static/css/style.css', timeout=5)
    js = requests.get(f'{base_url}/static/js/app.js', timeout=5)

    assert home.status_code == 200
    assert '<form id="controls"' in home.text
    assert css.status_code == 200
    assert js.status_code == 200


def test_container_process_runs_as_non_root(container):
    """Q11 — the image drops root: commands run as an unprivileged user.

    The Dockerfile declares ``USER appuser``, so a process started in the
    container must not be uid 0. This guards the least-privilege posture against
    an accidental removal of the ``USER`` directive.
    """

    exit_code, output = container.get_wrapped_container().exec_run('id -u')

    assert exit_code == 0
    assert output.decode().strip() != '0'
