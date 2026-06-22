"""Application factory for the RandomGen Flask service.

The factory builds and configures a :class:`flask.Flask` instance: it registers
the web blueprint, one API blueprint per entry in the version registry, and the
centralized error handler. The service holds no mutable state, so the app can be
created once per process (gunicorn worker) and shared across requests.

Run it via the factory:

- gunicorn: ``gunicorn 'randomgen.app:create_app()'``
- locally:  ``flask --app 'randomgen.app:create_app' run``
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from randomgen.blueprints import api, web
from randomgen.config import Config
from randomgen.errors import RandomGenError
from randomgen.versions import API_VERSIONS


def handle_error(e):
    """Translate exceptions into the JSON ``{"error": ...}`` API contract.

    Domain validation errors (:class:`RandomGenError`) are caused by bad
    client input and map to 400. Flask/Werkzeug HTTP errors keep their own
    status code. Anything else is an unexpected server error and maps to 500.

    Args:
        e (Exception): The exception raised while handling the request.

    Returns:
        flask.Response: A JSON error response with the matching status code.

    """

    # Domain validation errors are caused by bad client input
    if isinstance(e, RandomGenError):
        return jsonify({'error': str(e)}), 400

    # Preserve Flask/Werkzeug HTTP errors (e.g. 404, 405)
    if isinstance(e, HTTPException):
        return jsonify({'error': e.description}), e.code

    # Unexpected failure
    return jsonify({'error': str(e)}), 500


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

    # Browser- and ops-facing routes (home page, OpenAPI docs, health).
    app.register_blueprint(web.bp)

    # One blueprint per API generation, built from the version registry, so
    # adding a generation is a single registry edit with no new route code.
    for version, generator in API_VERSIONS.items():
        app.register_blueprint(api.make_api_blueprint(version, generator))

    # The single API-wide error boundary.
    app.register_error_handler(Exception, handle_error)

    return app
