from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from randomgen.core import RandomGenV1, RandomGenV2
from randomgen.endpoints import RandomGenRestApi
from randomgen.errors import RandomGenError, RandomGenQuantityError

# Create the Flask application
app = Flask(__name__)

# The REST API holds no mutable state, so a single shared instance is safe
# across concurrent requests and worker processes.
app.rest_api = RandomGenRestApi()

# Quantity generated when the `numbers` query parameter is omitted. A large
# default makes the Chi-Square quality report meaningful out of the box.
DEFAULT_QUANTITY = 1000


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
        raise RandomGenQuantityError()


def distribution_from_query():
    """Parse an optional per-request distribution from the query string.

    Callers may override the built-in distribution with repeated ``value``
    and ``probability`` query parameters (e.g. ``?value=1&value=2&
    probability=0.5&probability=0.5``).

    Returns:
        tuple: ``(values, probabilities)`` as lists, or ``(None, None)`` when
        the caller supplied neither, in which case the default distribution is
        used.

    """

    values = request.args.getlist('value', type=float)
    probabilities = request.args.getlist('probability', type=float)

    if not values and not probabilities:
        return None, None

    return values, probabilities


@app.route('/')
def hello_world():
    """Route for the default home page.

    Returns:
        str: The home page message.

    """

    # Return the home page message
    return app.rest_api.home_endpoint()


@app.get('/api/v1/randomgen')
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
        app.rest_api.randomgen_endpoint(
            randomgen_type=RandomGenV1,
            quantity=quantity,
            values=values,
            probabilities=probabilities,
        )
    )


@app.get('/api/v2/randomgen')
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
        app.rest_api.randomgen_endpoint(
            randomgen_type=RandomGenV2,
            quantity=quantity,
            values=values,
            probabilities=probabilities,
        )
    )


@app.get('/health')
def health():
    """Health check endpoint.

    Returns:
        flask.Response: ``{"status": "ok"}`` with HTTP 200 when the service
        can handle requests. Requires no authentication.

    """

    return jsonify({'status': 'ok'}), 200


@app.errorhandler(Exception)
def handle_error(e):
    """Error handler for the application.

    Domain validation errors (RandomGenError) are caused by bad client
    input and map to 400. Flask/Werkzeug HTTP errors keep their own status
    code. Anything else is an unexpected server error and maps to 500.

    Returns:
        flask.Response: The error response.

    """

    # Domain validation errors are caused by bad client input
    if isinstance(e, RandomGenError):
        return jsonify({'error': str(e)}), 400

    # Preserve Flask/Werkzeug HTTP errors (e.g. 404, 405)
    if isinstance(e, HTTPException):
        return jsonify({'error': e.description}), e.code

    # Unexpected failure
    return jsonify({'error': str(e)}), 500


###############################################################################
# FLASK APP
###############################################################################

if __name__ == "__main__":
    app.run(debug=True)
