"""Local-development entrypoint.

Builds the app via the factory and serves it with Flask's built-in server.
This is a convenience for local runs only; the Docker image serves the app
with gunicorn. Debug mode stays off here and in the image.
"""

import os

from randomgen.app import create_app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
