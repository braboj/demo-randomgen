"""Unit tests for the OpenAPI contract and the /docs + /openapi.json routes.

The contract is the hand-authored ``openapi.yaml`` (the single source of truth);
these tests pin it to the live code constants and confirm it is served.
"""

from randomgen import __version__
from randomgen.app import create_app
from randomgen.endpoints import MAX_NUMBERS
from randomgen.openapi import load_spec
from randomgen.routing import DEFAULT_QUANTITY


def test_spec_is_openapi_31():
    """The bundled contract parses and declares OpenAPI 3.1."""

    spec = load_spec()

    assert spec['openapi'].startswith('3.1')
    assert spec['info']['title'] == 'RandomGen API'


def test_spec_pins_live_constants():
    """Drift guard: the served contract's limits and version match the code.

    The limits are hand-authored in the YAML, so this stops them diverging from
    the constants the service enforces; the version is injected by ``load_spec``
    from the installed package, so the served spec always matches the release.
    """

    spec = load_spec()
    numbers = spec['components']['parameters']['Numbers']['schema']

    assert spec['info']['version'] == __version__
    assert numbers['default'] == DEFAULT_QUANTITY
    assert numbers['maximum'] == MAX_NUMBERS


def test_spec_documents_every_api_route():
    """Drift guard: every /api route on the blueprint appears in the contract.

    A new or renamed /api endpoint that is left undocumented fails here.
    """

    documented = set(load_spec()['paths'])

    app = create_app()
    api_rules = {r.rule for r in app.url_map.iter_rules() if r.rule.startswith('/api')}

    assert api_rules, 'expected at least one /api route on the blueprint'
    assert api_rules <= documented


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
