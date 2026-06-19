"""HTTP routes for the RandomGen service, as a Flask blueprint.

Handlers stay thin: they parse and validate query parameters, delegate to the
stateless :class:`RandomGenRestApi` service, and serialize the result. The
blueprint is registered by the application factory in :mod:`randomgen.app`.
"""

from flask import Blueprint, jsonify, render_template, request, url_for

from randomgen import __version__
from randomgen.core import RandomGenV1, RandomGenV2
from randomgen.endpoints import (
    DEFAULT_NUMBERS,
    DEFAULT_PROBABILITIES,
    MAX_NUMBERS,
    RandomGenRestApi,
)
from randomgen.errors import RandomGenDistFormatError, RandomGenQuantityError
from randomgen.openapi import load_spec

# The route blueprint registered by the application factory.
bp = Blueprint('randomgen', __name__)

# The REST API holds no mutable state, so a single shared instance is safe
# across concurrent requests and worker processes.
rest_api = RandomGenRestApi()

# Quantity generated when the `numbers` query parameter is omitted. A large
# default makes the Chi-Square quality report meaningful out of the box.
DEFAULT_QUANTITY = 1000

# The built-in distribution rendered as a ``dist`` string for the home page.
DEFAULT_DIST = ','.join(
    f'{n}:{p}' for n, p in zip(DEFAULT_NUMBERS, DEFAULT_PROBABILITIES, strict=True)
)


def quantity_from_query():
    """Parse the requested quantity from the `numbers` query parameter.

    Returns:
        int: The requested quantity, or ``DEFAULT_QUANTITY`` when omitted.

    Raises:
        RandomGenQuantityError: If `numbers` is present but not an integer.
            Flask's ``type=int`` would silently fall back to the default;
            an explicit, malformed value is a client error and must surface.

    """

    raw = request.args.get('numbers')

    if raw is None:
        return DEFAULT_QUANTITY

    try:
        return int(raw)
    except (TypeError, ValueError):
        raise RandomGenQuantityError() from None


def parse_dist_pairs(raw):
    """Parse the ``dist`` shorthand into parallel value/probability lists.

    The ``dist`` query parameter binds each outcome to its weight as a
    comma-separated list of ``value:probability`` pairs (e.g.
    ``dist=-1:0.01,0:0.3,1:0.58``). Pairing the two together makes a
    misaligned distribution impossible to express, unlike the parallel
    ``value`` / ``probability`` parameters.

    Args:
        raw (str): The raw ``dist`` query value.

    Returns:
        tuple: ``(values, probabilities)`` as parallel lists of floats.

    Raises:
        RandomGenDistFormatError: If any item is missing its ``:`` separator
            or either side is not a number.

    """

    values = []
    probabilities = []

    for item in raw.split(','):
        value, separator, probability = item.partition(':')

        if not separator:
            raise RandomGenDistFormatError()

        try:
            values.append(float(value))
            probabilities.append(float(probability))
        except ValueError:
            raise RandomGenDistFormatError() from None

    return values, probabilities


def distribution_from_query():
    """Parse an optional per-request distribution from the query string.

    Callers may override the built-in distribution in two ways:

    - ``dist`` — a comma-separated list of ``value:probability`` pairs
      (e.g. ``?dist=1:0.5,2:0.5``). Preferred: each value is bound to its
      own weight, so the two cannot be misaligned.
    - repeated ``value`` and ``probability`` parameters (e.g.
      ``?value=1&value=2&probability=0.5&probability=0.5``). Retained for
      backward compatibility.

    ``dist`` takes precedence when present; the repeated parameters are only
    consulted when ``dist`` is absent.

    Returns:
        tuple: ``(values, probabilities)`` as lists, or ``(None, None)`` when
        the caller supplied neither, in which case the default distribution is
        used.

    """

    raw_dist = request.args.get('dist')
    if raw_dist is not None:
        return parse_dist_pairs(raw_dist)

    values = request.args.getlist('value', type=float)
    probabilities = request.args.getlist('probability', type=float)

    if not values and not probabilities:
        return None, None

    return values, probabilities


@bp.route('/')
def hello_world():
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

    return render_template('docs.html', openapi_url=url_for('randomgen.openapi_json'))


@bp.get('/api/v1/randomgen')
def api_v1_randomgen():
    """Route for the /api/v1/randomgen endpoint.

    Returns:
        flask.Response: The response from the randomgen endpoint.

    """

    # Parse the query parameters
    quantity = quantity_from_query()
    values, probabilities = distribution_from_query()

    # Return the response
    return jsonify(
        rest_api.randomgen_endpoint(
            randomgen_type=RandomGenV1,
            quantity=quantity,
            values=values,
            probabilities=probabilities,
        )
    )


@bp.get('/api/v2/randomgen')
def api_v2_randomgen():
    """Route for the /api/v2/randomgen endpoint.

    Returns:
        flask.Response: The response from the randomgen endpoint.

    """

    # Parse the query parameters
    quantity = quantity_from_query()
    values, probabilities = distribution_from_query()

    # Return the response
    return jsonify(
        rest_api.randomgen_endpoint(
            randomgen_type=RandomGenV2,
            quantity=quantity,
            values=values,
            probabilities=probabilities,
        )
    )


@bp.get('/health')
def health():
    """Health check endpoint.

    Returns:
        flask.Response: ``{"status": "ok"}`` with HTTP 200 when the service
        can handle requests. Requires no authentication.

    """

    return jsonify({'status': 'ok'}), 200
