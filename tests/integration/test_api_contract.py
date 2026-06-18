"""Integration tests: the full request path through the real wiring.

These exercise the application as assembled by ``create_app()`` — factory,
blueprint, error handler, service, generators, histogram, and Chi-Square test
— with no mocks, asserting the public HTTP contract end to end. They use
Flask's ``test_client`` (in-process, no socket) and are marked ``integration``
automatically by ``tests/conftest.py``.
"""

import pytest

from randomgen.app import create_app


@pytest.fixture
def client():
    """A test client over a freshly built application."""

    return create_app().test_client()


def test_home_page_serves_html(client):
    """The home route returns the rendered UI."""

    response = client.get('/')

    assert response.status_code == 200
    assert 'text/html' in response.content_type
    assert '<form id="controls"' in response.get_data(as_text=True)


def test_health_returns_ok(client):
    """The health endpoint is a plain liveness probe."""

    response = client.get('/health')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


@pytest.mark.parametrize('version', ['v1', 'v2'])
def test_default_distribution_response_shape(client, version):
    """A default request returns the full numbers + quality contract."""

    response = client.get(f'/api/{version}/randomgen?numbers=500')

    assert response.status_code == 200
    body = response.get_json()

    assert len(body['numbers']) == 500
    quality = body['quality']
    assert set(quality) == {
        'chi_square_test',
        'expected_histogram',
        'observed_histogram',
    }
    chi = quality['chi_square_test']
    assert set(chi) == {'is_null', 'chi_square', 'p_value', 'df'}
    assert isinstance(chi['is_null'], bool)
    # Expected histogram mirrors the built-in distribution.
    assert quality['expected_histogram'] == {
        '-1': 0.01,
        '0': 0.3,
        '1': 0.58,
        '2': 0.1,
        '3': 0.01,
    }


@pytest.mark.parametrize('version', ['v1', 'v2'])
def test_custom_distribution_via_dist_pairs(client, version):
    """A per-request `dist` distribution is sampled and scored."""

    response = client.get(f'/api/{version}/randomgen?numbers=400&dist=1:0.25,2:0.75')

    assert response.status_code == 200
    body = response.get_json()
    assert set(body['numbers']) <= {1.0, 2.0}
    assert body['quality']['expected_histogram'] == {'1.0': 0.25, '2.0': 0.75}


def test_custom_distribution_via_repeated_params(client):
    """The legacy repeated value/probability parameters still work."""

    response = client.get(
        '/api/v1/randomgen?numbers=300'
        '&value=1&value=2&value=3'
        '&probability=0.2&probability=0.2&probability=0.6'
    )

    assert response.status_code == 200
    assert set(response.get_json()['numbers']) <= {1.0, 2.0, 3.0}


@pytest.mark.parametrize(
    ('query', 'fragment'),
    [
        ('numbers=abc', 'integer'),  # non-integer quantity
        ('numbers=0', None),  # below the minimum
        ('numbers=10001', None),  # above MAX_NUMBERS
        ('numbers=10&dist=1:0.5,2', None),  # malformed dist pair
        ('numbers=10&value=1&value=2&probability=0.5', None),  # length mismatch
        ('numbers=10&value=1&value=2&probability=0.2&probability=0.2', None),  # sum != 1
    ],
)
def test_invalid_requests_return_json_400(client, query, fragment):
    """Bad input yields a 400 with the JSON error contract."""

    response = client.get(f'/api/v1/randomgen?{query}')

    assert response.status_code == 400
    body = response.get_json()
    assert 'error' in body
    if fragment:
        assert fragment in body['error']


def test_unknown_path_returns_json_404(client):
    """An unknown path is handled by the JSON error boundary, not HTML."""

    response = client.get('/api/v1/does-not-exist')

    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_wrong_method_returns_json_405(client):
    """POST to a GET-only endpoint returns a JSON 405."""

    response = client.post('/api/v1/randomgen')

    assert response.status_code == 405
    assert 'error' in response.get_json()
