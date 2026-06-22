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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException

from randomgen.blueprints import api, web
from randomgen.config import Config
from randomgen.errors import RandomGenError
from randomgen.observability import register_logging
from randomgen.versions import API_VERSIONS


def handle_error(e):
    """Translate exceptions into the JSON ``{"error": ...}`` API contract.

    Domain validation errors (:class:`RandomGenError`) are caused by bad
    client input and map to 400. Flask/Werkzeug HTTP errors keep their own
    status code. Anything else is an unexpected server error: it is logged in
    full and answered with a generic 500 so internal detail never reaches the
    client.

    Args:
        e (Exception): The exception raised while handling the request.

    Returns:
        flask.Response: A JSON error response with the matching status code.

    """

    # Domain validation errors are caused by bad client input
    if isinstance(e, RandomGenError):
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

    # The service's only configuration surface, read from RANDOMGEN_* env vars
    # at startup (see randomgen.config). Read once here, before anything that
    # consumes app.config.
    app.config.from_object(Config())

    # Configure logging and request-timing hooks (one log line per response).
    register_logging(app)

    # The rate limiter is created per application (not as a module singleton) so
    # the factory can build many apps — gunicorn workers, every test — without
    # limit registrations accumulating on a shared instance. It reads its
    # storage/headers/enabled flags from the RATELIMIT_* config above.
    limiter = Limiter(key_func=get_remote_address)
    limiter.init_app(app)

    # Browser- and ops-facing routes (home page, OpenAPI docs, health).
    app.register_blueprint(web.bp)

    # Health checks and the browser UI are never throttled.
    limiter.exempt(web.bp)

    # One blueprint per API generation, built from the version registry, so
    # adding a generation is a single registry edit with no new route code. The
    # limit is applied to each blueprint (its only route is the generation
    # endpoint); the value defers to RANDOMGEN_RATELIMIT, read per request.
    for version, generator in API_VERSIONS.items():
        bp = api.make_api_blueprint(version, generator)
        limiter.limit(lambda: current_app.config['RANDOMGEN_RATELIMIT'])(bp)
        app.register_blueprint(bp)

    # The single API-wide error boundary.
    app.register_error_handler(Exception, handle_error)

    return app
