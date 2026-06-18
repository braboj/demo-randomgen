from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from randomgen.core import RandomGenV1, RandomGenV2
from randomgen.endpoints import RandomGenRestApi
from randomgen.errors import RandomGenError

# Create the Flask application
app = Flask(__name__)
app.rest_api = RandomGenRestApi()


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

    # Parse the query parameter
    quantity = request.args.get('numbers', default=1, type=int)

    # Return the response
    return jsonify(
        app.rest_api
        .randomgen_endpoint(
            randomgen_type=RandomGenV1,
            numbers=quantity
        )
    )


@app.get('/api/v2/randomgen')
def api_v2_randomgen():
    """Route for the /api/v2/randomgen endpoint.

    Returns:
        flask.Response: The response from the randomgen endpoint.

    """

    # Parse the query parameter
    quantity = request.args.get('numbers', default=1, type=int)

    # Return the response
    return jsonify(
        app.rest_api
        .randomgen_endpoint(
            randomgen_type=RandomGenV2,
            numbers=quantity
        )
    )


@app.post('/api/config')
def api_config():
    """Route for the /api/config endpoint.

    Returns:
        flask.Response: The response from the config endpoint.

    """

    # Parse the request body
    numbers = request.json['numbers']
    probabilities = request.json['probabilities']

    # Return the response
    return jsonify(
        app.rest_api.config_endpoint(
            numbers=numbers,
            probabilities=probabilities
        )
    )


@app.post('/api/reset')
def api_reset():
    """Route for the /api/reset endpoint.

    Returns:
        flask.Response: The response from the reset endpoint.

    """

    # Return the response
    return jsonify(
        app.rest_api.reset_endpoint()
    )


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
