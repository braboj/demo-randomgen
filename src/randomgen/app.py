"""Application factory for the RandomGen Flask service.

The factory builds and configures a :class:`flask.Flask` instance: it
registers the route blueprint and the centralized error handler. The service
holds no mutable state, so the app can be created once per process (gunicorn
worker) and shared across requests.

Run it via the factory:

- gunicorn: ``gunicorn 'randomgen.app:create_app()'``
- locally:  ``flask --app 'randomgen.app:create_app' run``
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from randomgen.errors import RandomGenError
from randomgen.routing import bp


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
        flask.Flask: The configured application, with the route blueprint and
        the centralized error handler registered.

    """

    app = Flask(__name__)

    # Register the routes and the single API-wide error boundary.
    app.register_blueprint(bp)
    app.register_error_handler(Exception, handle_error)

    return app
