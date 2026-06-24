"""Unit tests for the OpenAPI contract and the /docs + /openapi.json routes.

The contract is the hand-authored ``openapi.yaml`` (the single source of truth);
these tests pin it to the live code constants and confirm it is served.
"""

from randomgen import __version__
from randomgen.app import create_app
from randomgen.openapi import load_spec
from randomgen.service import DEFAULT_QUANTITY, MAX_NUMBERS, MIN_NUMBERS


def test_spec_is_openapi_31():
    """The bundled contract parses and declares OpenAPI 3.1."""

    spec = load_spec()

    assert spec['openapi'].startswith('3.1')
    assert spec['info']['title'] == 'RandomGen API'


def test_spec_pins_live_limits():
    """Drift guard: the contract's quantity limits match the live code constants.

    The limits are hand-authored in the YAML, so this stops them diverging from
    the constants the service enforces. ``info.version`` is the contract's own
    version (AD-21), independent of the package version, so it is not pinned
    here — only confirmed present, as OpenAPI requires it.
    """

    spec = load_spec()
    numbers = spec['components']['parameters']['Numbers']['schema']

    assert numbers['default'] == DEFAULT_QUANTITY
    assert numbers['minimum'] == MIN_NUMBERS
    assert numbers['maximum'] == MAX_NUMBERS
    assert isinstance(spec['info']['version'], str) and spec['info']['version']


def test_spec_documents_every_api_route():
    """Drift guard: every /api route on the blueprint appears in the contract.

    A new or renamed /api endpoint that is left undocumented fails here.
    """

    documented = set(load_spec()['paths'])

    app = create_app()
    api_rules = {r.rule for r in app.url_map.iter_rules() if r.rule.startswith('/api')}

    assert api_rules, 'expected at least one /api route on the blueprint'
    assert api_rules <= documented


def test_api_operations_document_error_statuses():
    """Drift guard: every /api operation documents its real error statuses.

    ``handle_error`` can answer an /api request with 400 (bad input), 405
    (wrong method), or 500 (server error); the contract must surface each so
    generated clients model them. Each error response resolves — through the
    shared ``components/responses`` — to the ``Error`` envelope schema. (404 is
    a global unknown-path concern, not reachable for a documented operation, so
    it is intentionally not attached per-operation.)
    """

    spec = load_spec()
    expected_statuses = {'400', '405', '500'}

    api_ops = [
        op
        for path, item in spec['paths'].items()
        if path.startswith('/api')
        for op in item.values()
    ]
    assert api_ops, 'expected at least one /api operation in the contract'

    for op in api_ops:
        responses = op['responses']
        assert expected_statuses <= set(responses)
        for status in expected_statuses:
            ref = responses[status]['$ref']
            component = ref.rsplit('/', 1)[1]
            schema = spec['components']['responses'][component]
            assert (
                schema['content']['application/json']['schema']['$ref']
                == '#/components/schemas/Error'
            )


def test_spec_declares_servers():
    """The contract declares a servers block so /docs shows a base URL."""

    servers = load_spec()['servers']

    assert servers, 'expected at least one server entry'
    assert all('url' in server for server in servers)
    # The relative origin is always valid wherever the document is served.
    assert any(server['url'] == '/' for server in servers)


def test_spec_documents_info_endpoint():
    """The contract documents /info and its Info schema."""

    spec = load_spec()

    assert '/info' in spec['paths']
    assert 'Info' in spec['components']['schemas']


def test_info_endpoint_reflects_live_sources():
    """Drift guard: GET /info reports the live package and contract versions.

    The two versions are deliberately distinct (AD-21): the top-level version is
    the package release, the nested one is the contract version. Pinning both to
    their sources stops the endpoint silently reporting a stale value.
    """

    spec = load_spec()
    body = create_app().test_client().get('/info').get_json()

    assert body['name'] == spec['info']['title']
    assert body['version'] == __version__
    assert body['api']['version'] == spec['info']['version']


def test_openapi_json_endpoint_returns_spec():
    """GET /openapi.json serves the contract as JSON."""

    client = create_app().test_client()
    response = client.get('/openapi.json')

    assert response.status_code == 200
    assert response.is_json
    body = response.get_json()
    assert body['info']['title'] == 'RandomGen API'
    assert '/api/v1/randomgen' in body['paths']
    assert '/api/v2/randomgen' in body['paths']


def test_docs_endpoint_renders_redoc():
    """GET /docs renders the ReDoc page pointing at the spec URL."""

    client = create_app().test_client()
    response = client.get('/docs')
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'text/html' in response.content_type
    assert '<redoc' in body
    # Jinja injected the spec URL; no literal placeholder is left behind.
    assert '/openapi.json' in body
    assert 'openapi_url' not in body
