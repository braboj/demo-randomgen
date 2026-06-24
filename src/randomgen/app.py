"""Application factory for the RandomGen Flask service.

The factory builds and configures a :class:`flask.Flask` instance: it registers
the web blueprint, one API blueprint per entry in the version registry, and the
centralized error handler. The service holds no mutable state, so the app can be
created once per process (gunicorn worker) and shared across requests.

Run it via the factory:

- gunicorn: ``gunicorn 'randomgen.app:create_app()'``
- locally:  ``flask --app 'randomgen.app:create_app' run``
"""

from flask import Flask, current_app, jsonify, request
from flask.json.provider import DefaultJSONProvider
from werkzeug.exceptions import HTTPException

from randomgen.blueprints import api, web
from randomgen.config import Config
from randomgen.domain.errors import RandomGenError
from randomgen.observability import register_logging
from randomgen.versions import API_VERSIONS


class StrictJSONProvider(DefaultJSONProvider):
    """JSON provider that refuses to emit the non-JSON ``NaN``/``Infinity``
    tokens.

    Python's ``json.dumps`` defaults to ``allow_nan=True``, serialising those
    float values as bare tokens that violate RFC 8259 and break a standards-
    compliant ``JSON.parse``. An undefined statistic should already be ``None``
    before it reaches serialisation; this is the defence in depth that turns a
    stray ``NaN`` into a loud 500 rather than a silently invalid 200 body.
    """

    def dumps(self, obj, **kwargs):
        kwargs.setdefault('allow_nan', False)
        return super().dumps(obj, **kwargs)


def handle_error(e):
    """Translate exceptions into the JSON ``{"error": ...}`` API contract.

    Domain validation errors (:class:`RandomGenError`) are caused by bad
    client input and map to 400; the rejection cause is logged at WARNING so
    the access log's bare 400 is explained. Flask/Werkzeug HTTP errors keep
    their own status code. Anything else is an unexpected server error: it is
    logged in full and answered with a generic 500 so internal detail never
    reaches the client.

    Args:
        e (Exception): The exception raised while handling the request.

    Returns:
        flask.Response: A JSON error response with the matching status code.

    """

    # Domain validation errors are caused by bad client input. Log the cause
    # so the access log's bare 400 is explained — which rule rejected the
    # request — without leaking anything the client did not already send.
    if isinstance(e, RandomGenError):
        current_app.logger.warning('Rejected %s %s: %s', request.method, request.path, e)
        return jsonify({'error': str(e)}), 400

    # Preserve Flask/Werkzeug HTTP errors (e.g. 404, 405, 429)
    if isinstance(e, HTTPException):
        return jsonify({'error': e.description}), e.code

    # Unexpected failure: log the detail, return a generic message
    current_app.logger.exception('Unhandled error on %s %s', request.method, request.path)
    return jsonify({'error': 'Internal Server Error'}), 500


def create_app():
    """Create and configure the RandomGen Flask application.

    Returns:
        flask.Flask: The configured application, with the web blueprint, one API
        blueprint per registered version, and the centralized error handler.

    """

    app = Flask(__name__)

    # Serialise with allow_nan=False so an undefined statistic can never reach
    # the client as a non-JSON `NaN`/`Infinity` token (RFC 8259).
    app.json = StrictJSONProvider(app)

    # The service's only configuration surface, read from RANDOMGEN_* env vars
    # at startup (see randomgen.config). Read once here, before anything that
    # consumes app.config.
    app.config.from_object(Config())

    # Configure logging and request-timing hooks (one log line per response).
    register_logging(app)

    # Browser- and ops-facing routes (home page, OpenAPI docs, health).
    app.register_blueprint(web.bp)

    # One blueprint per API generation, built from the version registry, so
    # adding a generation is a single registry edit with no new route code.
    for version, generator in API_VERSIONS.items():
        app.register_blueprint(api.make_api_blueprint(version, generator))

    # The single API-wide error boundary.
    app.register_error_handler(Exception, handle_error)

    return app
