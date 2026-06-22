"""The unversioned, browser- and ops-facing routes, as a blueprint.

Groups everything that is not part of the versioned API: the home-page UI, the
OpenAPI document and its rendered reference, and the health check. Handlers stay
thin; the application factory registers this blueprint at the site root.
"""

from flask import Blueprint, jsonify, render_template, url_for

from randomgen import __version__
from randomgen.openapi import load_spec
from randomgen.service import (
    DEFAULT_NUMBERS,
    DEFAULT_PROBABILITIES,
    DEFAULT_QUANTITY,
    MAX_NUMBERS,
)

bp = Blueprint('web', __name__)

# The built-in distribution rendered as a ``dist`` string for the home page.
DEFAULT_DIST = ','.join(
    f'{n}:{p}' for n, p in zip(DEFAULT_NUMBERS, DEFAULT_PROBABILITIES, strict=True)
)


@bp.route('/')
def home():
    """Render the home page: a small UI that exercises the API.

    Returns:
        str: The rendered ``index.html`` template, pre-filled with the
        built-in distribution and limits so the page works out of the box.

    """

    return render_template(
        'index.html',
        version=__version__,
        default_quantity=DEFAULT_QUANTITY,
        default_dist=DEFAULT_DIST,
        max_numbers=MAX_NUMBERS,
        config={
            'defaultDist': DEFAULT_DIST,
            'defaultQuantity': DEFAULT_QUANTITY,
            'maxNumbers': MAX_NUMBERS,
            'version': __version__,
        },
    )


@bp.get('/openapi.json')
def openapi_json():
    """Serve the OpenAPI 3.1 specification as JSON.

    Returns:
        flask.Response: The hand-authored OpenAPI contract (``openapi.yaml``),
        served verbatim.

    """

    return jsonify(load_spec())


@bp.get('/docs')
def docs():
    """Render interactive API documentation (ReDoc) over the OpenAPI spec.

    Returns:
        str: The rendered ``docs.html`` page, which loads the specification
        from :func:`openapi_json`.

    """

    return render_template('docs.html', openapi_url=url_for('web.openapi_json'))


@bp.get('/health')
def health():
    """Health check endpoint.

    Returns:
        flask.Response: ``{"status": "ok"}`` with HTTP 200 when the service
        can handle requests. Requires no authentication.

    """

    return jsonify({'status': 'ok'}), 200
