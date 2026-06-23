"""The versioned RandomGen API, as a blueprint factory.

Every API generation shares one contract and differs only by the injected
generator, so a single factory builds them all: :func:`make_api_blueprint`
returns a blueprint mounted under ``/api/<version>`` whose handler stays thin
(parse the query, delegate to the service, serialize JSON). The application
factory registers one blueprint per entry in
:data:`randomgen.versions.API_VERSIONS`.
"""

from flask import Blueprint, jsonify, request

from randomgen.domain.errors import RandomGenDistFormatError, RandomGenQuantityError
from randomgen.service import DEFAULT_QUANTITY, RandomGenService

# The service holds no mutable state, so a single shared instance is safe across
# concurrent requests, every API generation, and worker processes.
service = RandomGenService()


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


def make_api_blueprint(version, generator):
    """Build the API blueprint for one generation.

    Args:
        version (str): The path segment for this generation (e.g. ``"v1"``),
            used both as the blueprint name and the ``/api/<version>`` prefix.
        generator (type): The generator class this generation samples with.
            Captured per call (a function parameter, not a loop variable), so
            each blueprint binds its own generator.

    Returns:
        flask.Blueprint: A blueprint mounted at ``/api/<version>`` whose
        ``/randomgen`` route delegates to the shared service.

    """

    bp = Blueprint(f'api_{version}', __name__, url_prefix=f'/api/{version}')

    @bp.get('/randomgen')
    def randomgen():
        """Generate a sample for this API generation and score its quality.

        Returns:
            flask.Response: The generated numbers plus the Chi-Square report.

        """

        quantity = quantity_from_query()
        values, probabilities = distribution_from_query()

        return jsonify(
            service.generate(
                generator=generator,
                quantity=quantity,
                values=values,
                probabilities=probabilities,
            )
        )

    return bp
