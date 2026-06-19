"""Unit tests for the OpenAPI spec and the /docs + /openapi.json routes."""

from randomgen import __version__
from randomgen.app import create_app
from randomgen.endpoints import MAX_NUMBERS
from randomgen.openapi import build_spec
from randomgen.routing import DEFAULT_QUANTITY


def test_build_spec_reflects_live_constants():
    """The spec embeds the running version and the quantity limits."""

    spec = build_spec(__version__, DEFAULT_QUANTITY, MAX_NUMBERS)

    assert spec['openapi'].startswith('3.1')
    assert spec['info']['version'] == __version__

    params = {p['name']: p for p in spec['paths']['/api/v1/randomgen']['get']['parameters']}
    assert params['numbers']['schema']['default'] == DEFAULT_QUANTITY
    assert params['numbers']['schema']['maximum'] == MAX_NUMBERS


def test_spec_documents_every_api_route():
    """Drift guard: every /api route on the blueprint appears in the spec.

    A new or renamed /api endpoint that is left undocumented fails here.
    """

    spec = build_spec(__version__, DEFAULT_QUANTITY, MAX_NUMBERS)
    documented = set(spec['paths'])

    app = create_app()
    api_rules = {r.rule for r in app.url_map.iter_rules() if r.rule.startswith('/api')}

    assert api_rules, 'expected at least one /api route on the blueprint'
    assert api_rules <= documented


def test_openapi_json_endpoint_returns_spec():
    """GET /openapi.json returns the JSON specification."""

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
