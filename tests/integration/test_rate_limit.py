"""Integration tests for rate limiting the generation endpoint."""

import pytest

from randomgen.app import create_app


@pytest.fixture
def client(monkeypatch):
    """A client whose app limits the generation endpoint to 2 requests/minute.

    Each app gets its own limiter with fresh storage, so this test's counter is
    naturally isolated from requests other tests made.
    """

    monkeypatch.setenv('RANDOMGEN_RATELIMIT', '2 per minute')
    monkeypatch.setenv('RANDOMGEN_RATELIMIT_ENABLED', 'true')
    return create_app().test_client()


class TestRateLimiting:
    def test_generation_endpoint_throttles_after_limit(self, client):
        assert client.get('/api/v1/randomgen').status_code == 200
        assert client.get('/api/v1/randomgen').status_code == 200

        third = client.get('/api/v1/randomgen')

        assert third.status_code == 429
        assert 'error' in third.get_json()
        assert 'Retry-After' in third.headers

    def test_health_is_never_throttled(self, client):
        # Far more than the limit; the liveness probe must never be rejected.
        for _ in range(5):
            assert client.get('/health').status_code == 200
