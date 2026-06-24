"""Integration tests: the full request path through the real wiring.

These exercise the application as assembled by ``create_app()`` — factory,
blueprint, error handler, service, generators, histogram, and Chi-Square test
— with no mocks, asserting the public HTTP contract end to end. They use
Flask's ``test_client`` (in-process, no socket) and are marked ``integration``
automatically by ``tests/conftest.py``.
"""

from concurrent.futures import ThreadPoolExecutor

import pytest

from randomgen import __version__
from randomgen.app import create_app
from randomgen.openapi import load_spec
from randomgen.service import MAX_NUMBERS


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


def test_info_returns_service_metadata(client):
    """The /info endpoint exposes service identity and both versions.

    This is the one place the package release version is machine-readable; the
    home page only renders it as HTML.
    """

    response = client.get('/info')

    assert response.status_code == 200
    assert response.get_json() == {
        'name': 'RandomGen API',
        'version': __version__,
        'api': {
            'version': load_spec()['info']['version'],
            'generations': ['v1', 'v2'],
        },
    }


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


@pytest.mark.parametrize('version', ['v1', 'v2'])
def test_single_category_distribution_returns_valid_json_null_quality(client, version):
    """Regression (#233): a single-category distribution is valid generation
    input but its goodness-of-fit test is undefined (df = 0). The response must
    stay a 200 with RFC-8259-valid JSON — no bare `NaN` token — and report the
    undefined statistic as JSON null rather than a wrong verdict."""

    response = client.get(f'/api/{version}/randomgen?numbers=10&dist=5:1.0')

    assert response.status_code == 200
    # The bare `NaN` token (the bug) is not valid JSON; the body must not carry it.
    assert 'NaN' not in response.get_data(as_text=True)

    body = response.get_json()
    assert set(body['numbers']) == {5.0}
    chi = body['quality']['chi_square_test']
    assert chi['df'] == 0
    assert chi['p_value'] is None
    assert chi['is_null'] is None
    assert body['quality']['expected_histogram'] == {'5.0': 1.0}


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


def test_strict_json_provider_rejects_nan():
    """Defence in depth (#233): the app's JSON provider serialises with
    allow_nan=False, so a stray NaN raises instead of emitting the non-JSON
    `NaN` token. This backstops the domain fix at the serialisation boundary."""

    app = create_app()

    with pytest.raises(ValueError):
        app.json.dumps({'value': float('nan')})


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


def test_request_at_max_numbers_bound_is_served(client):
    """Q5 — a request exactly at MAX_NUMBERS is served; one above is rejected.

    The over-bound rejection is covered elsewhere; this pins the served side of
    the boundary so the cap cannot silently shrink.
    """

    at_bound = client.get(f'/api/v1/randomgen?numbers={MAX_NUMBERS}')

    assert at_bound.status_code == 200
    assert len(at_bound.get_json()['numbers']) == MAX_NUMBERS

    over_bound = client.get(f'/api/v1/randomgen?numbers={MAX_NUMBERS + 1}')

    assert over_bound.status_code == 400
    assert 'error' in over_bound.get_json()


def test_concurrent_requests_keep_distributions_isolated():
    """Q6 — concurrent requests with disjoint distributions never bleed together.

    The service keeps no per-request state on the shared ``service`` singleton
    or the module-level generators; each request builds its own generator. This
    drives many requests in parallel, each with a distinct, disjoint two-outcome
    distribution, and asserts every response stays within its own outcomes — any
    shared-state corruption would surface as a foreign value.
    """

    app = create_app()

    def fetch(worker):
        # A two-outcome distribution whose values are disjoint from every other
        # worker's, so cross-contamination is impossible to mistake for noise.
        base = 100 * worker
        dist = f'{base}:0.5,{base + 1}:0.5'
        response = app.test_client().get(f'/api/v1/randomgen?numbers=200&dist={dist}')
        assert response.status_code == 200
        return worker, base, response.get_json()['numbers']

    workers = range(1, 13)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch, workers))

    for worker, base, numbers in results:
        assert len(numbers) == 200
        assert set(numbers) <= {float(base), float(base + 1)}, (
            f'worker {worker} saw values outside its own distribution'
        )


def _response_signature(body):
    """Reduce a JSON value to a structural signature: keys recursively, leaf types.

    Numeric leaves collapse to ``'number'`` (so an int/float change is not a false
    positive) and a list to its set of element signatures, leaving the response
    *shape* — the public contract — as the thing under test.
    """

    if isinstance(body, dict):
        return {key: _response_signature(value) for key, value in sorted(body.items())}
    if isinstance(body, list):
        return ['list', sorted({_leaf_type(item) for item in body})]
    return _leaf_type(body)


def _leaf_type(value):
    """Name a JSON leaf's type, collapsing int/float to ``'number'``."""

    if isinstance(value, bool):  # bool is an int subclass — check it first
        return 'bool'
    if isinstance(value, (int, float)):
        return 'number'
    return type(value).__name__


def test_api_versions_share_a_stable_response_schema(client):
    """Q10 — v1 and v2 return the identical, pinned response schema.

    A behaviour snapshot independent of the OpenAPI spec: it pins the exact
    top-level structure and field types of the success response and asserts the
    two versions stay structurally identical. An accidental shape change in
    either version — or a divergence between them — fails CI. A balanced
    two-outcome distribution fixes the histogram keys and guarantees both
    categories are observed.
    """

    query = 'numbers=400&dist=1:0.5,2:0.5'
    v1 = _response_signature(client.get(f'/api/v1/randomgen?{query}').get_json())
    v2 = _response_signature(client.get(f'/api/v2/randomgen?{query}').get_json())

    assert v1 == v2

    expected = {
        'numbers': ['list', ['number']],
        'quality': {
            'chi_square_test': {
                'chi_square': 'number',
                'df': 'number',
                'is_null': 'bool',
                'p_value': 'number',
            },
            'expected_histogram': {'1.0': 'number', '2.0': 'number'},
            'observed_histogram': {'1.0': 'number', '2.0': 'number'},
        },
    }
    assert v1 == expected
