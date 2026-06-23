"""Unit tests for the container health probe (``randomgen.healthcheck``)."""

from unittest import mock

from randomgen import healthcheck


def _fake_response(status):
    """A ``urlopen`` stand-in usable as a context manager, exposing ``status``."""

    response = mock.MagicMock()
    response.status = status
    response.__enter__.return_value = response
    return response


def test_probe_returns_0_when_service_answers_200():
    """A 200 from /health is reported as healthy (exit 0)."""

    with mock.patch('urllib.request.urlopen', return_value=_fake_response(200)):
        assert healthcheck.probe() == 0


def test_probe_returns_1_on_non_200_status():
    """A non-200 status is reported as unhealthy (exit 1)."""

    with mock.patch('urllib.request.urlopen', return_value=_fake_response(503)):
        assert healthcheck.probe() == 1


def test_probe_returns_1_when_service_unreachable():
    """A refused connection or timeout is reported as unhealthy (exit 1)."""

    with mock.patch('urllib.request.urlopen', side_effect=OSError):
        assert healthcheck.probe() == 1
